# SPDX-License-Identifier: GPL-3.0-or-later
"""Simple one-click topology rebuild with guarded UV, rig and shape-key reprojection.

The input object is never changed. Retopology is attempted regardless of whether
the source is below its requested triangle budget or was already remeshed.
"""
import math

import bmesh
import bpy
from mathutils.bvhtree import BVHTree

from . import deform_transfer
from .smart_budget import allocate_triangle_budgets
from . import v08_tools as _v08
from . import (
    _copy_mesh_object, _remove_object_and_mesh, _select_only, _evaluated_mesh_copy,
    _static_mesh_reason, triangle_count, _action_report,
)


def _custom_data_reason(mesh):
    builtin = {
        'position', 'material_index', 'sharp_face', 'sharp_edge',
        'crease_edge', 'crease_vert', 'bevel_weight_edge', 'bevel_weight_vert',
        '.position', '.edge_verts', '.corner_vert', '.corner_edge',
        '.material_index', '.select_vert', '.select_edge', '.select_poly',
        '.hide_vert', '.hide_edge', '.hide_poly',
    }
    uvs = {layer.name for layer in mesh.uv_layers}
    custom_normal = mesh.attributes.get('custom_normal')
    if custom_normal is not None and not (
            (custom_normal.data_type == 'FLOAT_VECTOR'
             and custom_normal.domain in {'POINT', 'CORNER'})
            or (custom_normal.data_type == 'INT16_2D'
                and custom_normal.domain == 'CORNER')):
        return (
            "Cannot preserve custom_normal: expected a FLOAT_VECTOR attribute "
            "on POINT/CORNER or Blender's native INT16_2D on CORNER, got "
            + custom_normal.data_type + " on " + custom_normal.domain
        )
    unsupported = [
        item.name for item in mesh.attributes
        if not item.is_internal and item.name not in builtin and item.name not in uvs
        and item.name != 'custom_normal'
    ]
    if mesh.color_attributes:
        unsupported.extend(item.name for item in mesh.color_attributes)
    if unsupported:
        return 'Cannot safely reproject custom mesh attributes: ' + ', '.join(sorted(set(unsupported))[:8])
    return None


def _triangle_samples(mesh):
    """Construct local-space BVH and immutable per-triangle source data."""
    mesh.calc_loop_triangles()
    tris = list(mesh.loop_triangles)
    if not tris:
        raise ValueError('No source triangles available to transfer detail.')
    positions = [v.co.copy() for v in mesh.vertices]
    tree = BVHTree.FromPolygons(
        positions, [tuple(tri.vertices) for tri in tris], all_triangles=True)
    if tree is None:
        raise ValueError('Could not build the nearest-surface correspondence index.')

    def sample(pos):
        nearest, _normal, index, distance = tree.find_nearest(pos)
        if nearest is None or index is None:
            raise ValueError('A rebuilt vertex could not be mapped back onto the original surface.')
        tri = tris[index]
        a, b, c = (positions[i] for i in tri.vertices)
        u = b - a
        v = c - a
        w = nearest - a
        aa, ab, bb = u.dot(u), u.dot(v), v.dot(v)
        aw, bw = w.dot(u), w.dot(v)
        denominator = aa * bb - ab * ab
        if abs(denominator) < 1.0e-14:
            bary = (1.0, 0.0, 0.0)
        else:
            y = (bb * aw - ab * bw) / denominator
            z = (aa * bw - ab * aw) / denominator
            bary = (1.0 - y - z, y, z)
        return tri, bary, distance

    return sample



def _geometry_facts(mesh):
    """Count disconnected face islands and unsafe open/nonmanifold boundaries."""
    if not mesh.polygons:
        raise ValueError("A selected mesh has no usable polygons.")
    parents = list(range(len(mesh.vertices)))

    def find(i):
        while parents[i] != i:
            parents[i] = parents[parents[i]]
            i = parents[i]
        return i

    for polygon in mesh.polygons:
        indices = list(polygon.vertices)
        first = find(indices[0])
        for index in indices[1:]:
            parents[find(index)] = first

    islands = len({find(face.vertices[0]) for face in mesh.polygons})
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        unsafe_edges = sum(1 for edge in bm.edges if not edge.is_manifold)
    finally:
        bm.free()
    positions = [vertex.co for vertex in mesh.vertices]
    bounds = tuple(
        (min(p[axis] for p in positions), max(p[axis] for p in positions))
        for axis in range(3)
    )
    return islands, unsafe_edges, bounds


def _verify_result(mesh, reference, ceiling, expected_islands, source_bounds):
    """Reject damaged reconstruction before a result can be marked successful."""
    actual = triangle_count(mesh)
    if actual < 1 or actual > ceiling:
        raise ValueError(
            f"Output exceeds its assigned triangle limit "
            f"({actual:,} / {ceiling:,}) or contains no usable triangles.")
    islands, _edges, bounds = _geometry_facts(mesh)
    if islands != expected_islands:
        raise ValueError(
            f"Retopology changed disconnected components "
            f"({expected_islands} -> {islands}). Original retained.")
    diagonal = math.sqrt(sum(
        (high - low) ** 2 for low, high in source_bounds))
    tolerance = max(1.0e-5, diagonal * 0.08)
    if any(abs(a - b) > tolerance
           for old_axis, new_axis in zip(source_bounds, bounds)
           for a, b in zip(old_axis, new_axis)):
        raise ValueError(
            "Retopology changed the model bounds beyond the safety tolerance. "
            "The source is preserved; raise the budget or use manual retopology.")
    return actual


def _collect_meshes(context):
    """Respect the explicit operation scope without modifying hidden sources."""
    scope = getattr(context.scene, 'fishhwb_remesh_scope', 'ACTIVE')
    active = context.active_object
    if scope == 'SELECTED':
        candidates = list(context.selected_objects)
    elif scope == 'HIERARCHY':
        candidates = [active, *active.children_recursive] if active else []
    else:
        candidates = [active] if active else []
    return sorted(
        (obj for obj in dict.fromkeys(candidates)
         if obj is not None and obj.type == 'MESH'),
        key=lambda obj: obj.name_full,
    )


def _restore_selection(context, selected, active):
    for obj in list(context.selected_objects):
        obj.select_set(False)
    for obj in selected:
        if obj.name in bpy.data.objects:
            obj.select_set(True)
    if active is not None and active.name in bpy.data.objects:
        context.view_layer.objects.active = active


def _retopology_geometry(output, context, target):
    """Voxel weld/rebuild + optional QuadriFlow, with guarded budget refinement."""
    source_mesh = output.data
    if len(source_mesh.vertices) < 3 or len(source_mesh.polygons) == 0:
        raise ValueError('The mesh has no usable faces.')
    xs = [v.co.x for v in source_mesh.vertices]
    ys = [v.co.y for v in source_mesh.vertices]
    zs = [v.co.z for v in source_mesh.vertices]
    diagonal = math.sqrt(
        (max(xs)-min(xs))**2 + (max(ys)-min(ys))**2 + (max(zs)-min(zs))**2)
    if diagonal < 1e-6:
        raise ValueError('Mesh bounds are degenerate.')
    cells = max(48.0, min(220.0, math.sqrt(max(64, target)) * 1.65))
    source_mesh.remesh_voxel_size = max(1e-5, diagonal/cells)
    source_mesh.remesh_voxel_adaptivity = 0.0
    if hasattr(source_mesh, 'use_remesh_preserve_volume'):
        source_mesh.use_remesh_preserve_volume = True
    _v08._activate_only(context, output)
    if 'FINISHED' not in bpy.ops.object.voxel_remesh():
        raise ValueError('Voxel reconstruction was unavailable for this geometry.')
    if not output.data.polygons:
        raise ValueError('Reconstruction produced no faces.')

    quadriflow = False
    try:
        result = bpy.ops.object.quadriflow_remesh(
            use_mesh_symmetry=False,
            use_preserve_sharp=True,
            use_preserve_boundary=False,
            preserve_attributes=True,
            smooth_normals=True,
            mode='FACES',
            target_faces=max(4, target // 2),
            seed=0,
        )
        quadriflow = 'FINISHED' in result
    except Exception:
        pass
    if not output.data.polygons:
        raise ValueError('Retopology produced no usable surface.')

    actual = triangle_count(output.data)
    if actual > target:
        from . import _reduce_copy_to_limit
        # Reduce only newly constructed topology, before any attribute transfer.
        actual = _reduce_copy_to_limit(output, target, context)
    elif actual < int(target * 0.60) and target > actual * 2:
        # An increase in budget is useful for subsequent sculpt work, but
        # never invent detail or imply a subdivided mesh is more accurate.
        for _ in range(2):
            if actual >= target * 0.65:
                break
            bm = bmesh.new()
            try:
                bm.from_mesh(output.data)
                bmesh.ops.subdivide_edges(
                    bm, edges=list(bm.edges), cuts=1, use_grid_fill=True)
                bm.to_mesh(output.data)
            finally:
                bm.free()
            output.data.update()
            actual = triangle_count(output.data)
            if actual > target:
                from . import _reduce_copy_to_limit
                actual = _reduce_copy_to_limit(output, target, context)
                break
    return quadriflow, actual


def _reproject_custom_normals(source_mesh, target_mesh, sample, vertex_matches):
    """Transfer decoded corner normals, not Blender's encoded INT16_2D storage.

    Blender's native `custom_normal` is a CORNER/INT16_2D spherical encoding
    relative to a split normal's corner fan. These integers are NOT normal XY
    components. Decode them through Mesh.corner_normals and install the new
    corner normals through Mesh.normals_split_custom_set so Blender correctly
    encodes them for the *new* topology.
    """
    original = source_mesh.attributes.get('custom_normal')
    # Blender 4.2 stores custom split normals in a legacy mesh layer.
    # Blender 4.4+ exposes that layer as CORNER/INT16_2D.
    if original is None and not source_mesh.has_custom_normals:
        return False
    encoded = (original is None or (
        original.data_type == 'INT16_2D' and original.domain == 'CORNER'))
    vector_attr = (original is not None
                   and original.data_type == 'FLOAT_VECTOR'
                   and original.domain in {'POINT', 'CORNER'})
    if not (encoded or vector_attr):
        raise ValueError('Unsupported custom_normal domain or storage type.')

    # Blender's native packed normals must be read through the evaluated
    # per-corner vectors rather than .value (which contains two short ints).
    native_corner_vectors = None
    if encoded:
        native_corner_vectors = [
            item.vector.copy() for item in source_mesh.corner_normals
        ]
        if len(native_corner_vectors) != len(source_mesh.loops):
            raise ValueError('Unable to decode every custom split normal.')

    def weighted_vector(tri, weights):
        if encoded:
            vectors = [native_corner_vectors[index] for index in tri.loops]
        elif original.domain == 'POINT':
            vectors = [original.data[index].vector for index in tri.vertices]
        else:
            vectors = [original.data[index].vector for index in tri.loops]
        result = sum(
            (vec * weight for vec, weight in zip(vectors, weights)),
            vectors[0] * 0.0,
        )
        if result.length_squared > 1.0e-12:
            result.normalize()
        else:
            result = vectors[0].normalized()
        return result

    previous = target_mesh.attributes.get('custom_normal')
    if previous is not None:
        target_mesh.attributes.remove(previous)

    if encoded:
        # Every destination loop gets a real 3D custom split normal. Let
        # Blender encode it in the correct tangent frame of the rebuilt mesh.
        normals = [None] * len(target_mesh.loops)
        for face in target_mesh.polygons:
            for loop_index in face.loop_indices:
                vertex = target_mesh.vertices[target_mesh.loops[loop_index].vertex_index]
                query = vertex.co.lerp(face.center, 0.001)
                tri, weights, _distance = sample(query)
                vec = weighted_vector(tri, weights)
                normals[loop_index] = (vec.x, vec.y, vec.z)
        if any(item is None for item in normals):
            raise ValueError('One or more custom normals could not be projected.')
        target_mesh.normals_split_custom_set(normals)
        target_mesh.update()
        if not target_mesh.has_custom_normals:
            raise ValueError('Blender did not retain the transferred custom normals.')
    else:
        target = target_mesh.attributes.new(
            name='custom_normal', type='FLOAT_VECTOR', domain=original.domain)
        if original.domain == 'POINT':
            if len(target.data) != len(vertex_matches):
                raise ValueError('Custom normals could not be matched to every output vertex.')
            for element, (tri, weights, _distance) in zip(target.data, vertex_matches):
                element.vector = weighted_vector(tri, weights)
        else:
            for face in target_mesh.polygons:
                for loop_index in face.loop_indices:
                    vertex = target_mesh.vertices[target_mesh.loops[loop_index].vertex_index]
                    query = vertex.co.lerp(face.center, 0.001)
                    tri, weights, _distance = sample(query)
                    target.data[loop_index].vector = weighted_vector(tri, weights)
        if len(target.data) != (
                len(target_mesh.vertices) if original.domain == 'POINT'
                else len(target_mesh.loops)):
            raise ValueError('Custom normal data count differs from remeshed topology.')
    return True


def _project_details(source, output, neutral_mesh, deforming, context):
    """Project material/UV/weight and relative key data by nearest triangle."""
    sample = _triangle_samples(neutral_mesh)
    output_mesh = output.data
    source_materials = list(neutral_mesh.materials)
    source_uvs = [layer.name for layer in neutral_mesh.uv_layers]
    output_mesh.materials.clear()
    for material in source_materials:
        output_mesh.materials.append(material)
    for name in source_uvs:
        if name not in output_mesh.uv_layers:
            output_mesh.uv_layers.new(name=name)

    # Build correspondence separately for vertices and corners. Mapping a loop
    # from its vertex position can be ambiguous at UV seams: warn users to
    # visually inspect them; the original mesh/UVs remain intact.
    vertex_matches = [sample(vertex.co) for vertex in output_mesh.vertices]
    custom_normals_preserved = _reproject_custom_normals(
        neutral_mesh, output_mesh, sample, vertex_matches)
    for face in output_mesh.polygons:
        tri, _, _ = sample(face.center)
        face.material_index = neutral_mesh.polygons[tri.polygon_index].material_index
        face.use_smooth = neutral_mesh.polygons[tri.polygon_index].use_smooth
        for loop_idx in face.loop_indices:
            if not source_uvs:
                continue
            pos = output_mesh.vertices[output_mesh.loops[loop_idx].vertex_index].co
            src_tri, weights, _ = sample(pos)
            for name in source_uvs:
                src = neutral_mesh.uv_layers[name]
                dst = output_mesh.uv_layers[name]
                uv = src.data[src_tri.loops[0]].uv * weights[0]
                uv += src.data[src_tri.loops[1]].uv * weights[1]
                uv += src.data[src_tri.loops[2]].uv * weights[2]
                dst.data[loop_idx].uv = uv

    if deforming:
        src_keys = source.data.shape_keys
        basis = ([item.co for item in src_keys.key_blocks[0].data]
                 if src_keys else [v.co for v in source.data.vertices])
        for grp in list(output.vertex_groups):
            output.vertex_groups.remove(grp)
        copied_groups = []
        for old in source.vertex_groups:
            copied = output.vertex_groups.new(name=old.name)
            copied.lock_weight = old.lock_weight
            copied_groups.append(copied)
        offsets = []
        if src_keys:
            for key in list(src_keys.key_blocks)[1:]:
                offsets.append([
                    key.data[i].co - basis[i] for i in range(len(basis))
                ])
        for vertex, (tri, weights, _dist) in zip(output_mesh.vertices, vertex_matches):
            group_weights = {}
            for src_index, w in zip(tri.vertices, weights):
                for group in source.data.vertices[src_index].groups:
                    group_weights[group.group] = (
                        group_weights.get(group.group, 0.0) + w * group.weight)
            for group_index, value in group_weights.items():
                if value > 1e-7:
                    copied_groups[group_index].add(
                        [vertex.index], max(0.0, min(1.0, value)), 'REPLACE')
        attr_names = []
        for offsets_for_key in offsets:
            attr = output_mesh.attributes.new(
                name='fishhwb_shape_reproject', type='FLOAT_VECTOR', domain='POINT')
            attr_names.append(attr.name)
            data = []
            for tri, weights, _distance in vertex_matches:
                vector = sum(
                    (offsets_for_key[idx] * w
                     for idx, w in zip(tri.vertices, weights)),
                    offsets_for_key[tri.vertices[0]] * 0.0)
                data.extend((vector.x, vector.y, vector.z))
            attr.data.foreach_set('vector', data)
        groups, shapes = deform_transfer.transfer(source, output, attr_names)
    else:
        groups, shapes = 0, 0
    if custom_normals_preserved:
        source_attr = neutral_mesh.attributes.get('custom_normal')
        new_attr = output_mesh.attributes.get('custom_normal')
        if source_attr is None or source_attr.data_type == 'INT16_2D':
            if not output_mesh.has_custom_normals:
                raise ValueError('Blender-native split normals were not preserved.')
            # Blender 4.2 stores them in a legacy custom-data layer,
            # not a visible generic mesh attribute.
            if source_attr is not None and (
                    new_attr is None or new_attr.domain != 'CORNER'
                    or new_attr.data_type != 'INT16_2D'):
                raise ValueError('Retopology did not retain encoded split normals.')
        elif (new_attr is None or new_attr.domain != source_attr.domain
              or new_attr.data_type != source_attr.data_type):
            raise ValueError('Authored custom normals were not transferred.')
    if set(source_uvs) != {layer.name for layer in output_mesh.uv_layers}:
        raise ValueError('Rebuilt output did not preserve UV layer names.')
    if tuple(source_materials) != tuple(output_mesh.materials):
        raise ValueError('Rebuilt output did not preserve material slots.')
    if deforming:
        if set(g.name for g in source.vertex_groups) != set(g.name for g in output.vertex_groups):
            raise ValueError('Some vertex groups could not be transferred.')
        source_key_names = (
            set(source.data.shape_keys.key_blocks.keys())
            if source.data.shape_keys else set())
        target_key_names = (
            set(output.data.shape_keys.key_blocks.keys())
            if output.data.shape_keys else set())
        if source_key_names != target_key_names:
            raise ValueError('Some blendshapes could not be transferred.')
    return groups, shapes


class FISHHWB_OT_smart_remesh(bpy.types.Operator):
    bl_idname = 'fishhwb.smart_remesh'
    bl_label = 'Smart Remesh'
    bl_description = (
        'Prepare the active mesh, selected meshes or model hierarchy under '
        'one strict triangle budget. Originals are never modified')
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.mode == 'OBJECT' and
                bool(_collect_meshes(context)))

    def execute(self, context):
        originals = list(context.selected_objects)
        original_active = context.active_object
        generated = []
        try:
            sources = _collect_meshes(context)
            if not sources:
                raise ValueError('Select one or more mesh objects.')
            target = int(context.scene.fishhwb_triangle_target)
            if target > 500000:
                raise ValueError(
                    'Smart Remesh is limited to 500,000 output triangles. '
                    'Reduce the triangle limit first.')

            # Preflight every source before creating any output. A protected,
            # linked or unsupported child must never disappear silently.
            source_facts = []
            for source in sources:
                reason = (_static_mesh_reason(source, allow_deformation=True)
                          or deform_transfer.unsupported_reason(source)
                          or _custom_data_reason(source.data))
                if reason:
                    raise ValueError(source.name + ': ' + reason)
                evaluated = None
                try:
                    if (source.modifiers
                            and not deform_transfer.has_deformation(source)):
                        evaluated = _evaluated_mesh_copy(source, context)
                    data = evaluated or source.data
                    islands, _boundary, _bounds = _geometry_facts(data)
                    source_facts.append((triangle_count(data), islands))
                finally:
                    if evaluated is not None and evaluated.users == 0:
                        bpy.data.meshes.remove(evaluated)

            ceilings = allocate_triangle_budgets(source_facts, target)
            total_before = sum(count for count, _ in source_facts)
            total_after = 0
            methods = []
            used_fallback = []
            normals_reprojected = 0

            for source, ceiling in zip(sources, ceilings):
                output = _copy_mesh_object(source, context, '_SmartRemesh')
                generated.append(output)
                for key in (
                        'fishhwb_remesh_history', 'fishhwb_lod_history',
                        'fishhwb_output_id', 'fishhwb_generated_job',
                        'fishhwb_source_deformation_sensitive'):
                    if key in output:
                        del output[key]

                deforming = deform_transfer.has_deformation(source)
                neutral = None
                try:
                    # Static modifier results are evaluated only on a private
                    # copy. Rigged sources retain their unposed Basis.
                    if not deforming and output.modifiers:
                        evaluated = _evaluated_mesh_copy(output, context)
                        old = output.data
                        output.modifiers.clear()
                        output.data = evaluated
                        if old.users == 0:
                            bpy.data.meshes.remove(old)

                    islands, unsafe_edges, bounds = _geometry_facts(output.data)
                    # Voxel welding can erase open sheets or merge separate
                    # islands. Retain surface topology in those cases instead.
                    safe_rebuild = islands == 1 and unsafe_edges == 0
                    if not safe_rebuild:
                        if deforming:
                            if triangle_count(output.data) > ceiling:
                                raise ValueError(
                                    source.name + ': open or disconnected rigged '
                                    'mesh cannot safely meet this triangle budget. '
                                    'Source and shape keys preserved.')
                            actual = triangle_count(output.data)
                            method = 'DEFORMATION_PRESERVED'
                        else:
                            from . import _reduce_copy_to_limit
                            actual = _reduce_copy_to_limit(
                                output, ceiling, context)
                            method = 'SURFACE_PRESERVED'
                        used_fallback.append(source.name)
                        groups = len(source.vertex_groups)
                        shapes = (len(source.data.shape_keys.key_blocks) - 1
                                  if source.data.shape_keys else 0)
                    else:
                        if deforming:
                            keys = output.data.shape_keys
                            if keys:
                                basis = [item.co.copy()
                                         for item in keys.key_blocks[0].data]
                                output.shape_key_clear()
                                for vert, co in zip(output.data.vertices, basis):
                                    vert.co = co
                            output.modifiers.clear()
                        neutral = output.data.copy()
                        _v08._repair_static_mesh(output.data, fill_holes=True)
                        quadriflow, actual = _retopology_geometry(
                            output, context, ceiling)
                        groups, shapes = _project_details(
                            source, output, neutral, deforming, context)
                        if (neutral.attributes.get('custom_normal')
                                or neutral.has_custom_normals):
                            normals_reprojected += 1
                        method = ('QUADRIFLOW' if quadriflow
                                  else 'VOXEL_QUADS')

                    actual = _verify_result(
                        output.data, source.data, ceiling, islands, bounds)
                    output['fishhwb_generated_job'] = 'smart_remesh'
                    output['fishhwb_retopology_status'] = method
                    output['fishhwb_triangle_target'] = ceiling
                    output['fishhwb_smart_remesh_scope'] = getattr(
                        context.scene, 'fishhwb_remesh_scope', 'ACTIVE')
                    total_after += actual
                    methods.append(method)
                finally:
                    if neutral is not None and neutral.users == 0:
                        bpy.data.meshes.remove(neutral)

            if total_after > target:
                raise ValueError(
                    'Combined model exceeds its global triangle limit '
                    f'({total_after:,} > {target:,}); nothing was accepted.')
            _restore_selection(context, generated, generated[0])
            fallback = (
                ' Surface-preserving fallback used for: '
                + ', '.join(used_fallback[:6])
                + ('.' if len(used_fallback) <= 6 else ', and others.')
                if used_fallback else ''
            )
            _action_report(
                self, context,
                f'Smart Remesh: {len(generated)} mesh(es), '
                f'{total_before:,} -> {total_after:,} triangles '
                f'(global maximum {target:,}). '
                f'Methods: {", ".join(sorted(set(methods)))}. '
                'Component counts, output bounds and per-mesh budgets verified. '
                + ('Authored custom_normal data reprojected. '
                   if normals_reprojected else '')
                + 'Originals untouched. Review UV seams, shading and rigging '
                'before export.' + fallback,
                changed=len(generated))
            return {'FINISHED'}
        except Exception as exc:
            for output in reversed(generated):
                _remove_object_and_mesh(output)
            _restore_selection(context, originals, original_active)
            _action_report(
                self, context,
                'Smart Remesh not applied: ' + str(exc)
                + '. All original sources preserved.',
                unsupported=1)
            return {'CANCELLED'}


classes = (FISHHWB_OT_smart_remesh,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
