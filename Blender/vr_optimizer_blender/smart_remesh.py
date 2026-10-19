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
    unsupported = [
        item.name for item in mesh.attributes
        if not item.is_internal and item.name not in builtin and item.name not in uvs
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
    for face in output_mesh.polygons:
        tri, _, _ = sample(face.center)
        face.material_index = neutral_mesh.polygons[tri.polygon_index].material_index
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
        'Repair small gaps, reconstruct and retopologize a private mesh, '
        'aim for the triangle limit, and project compatible UVs, vertex groups, '
        'relative shape keys and armature modifiers')
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (
            context.mode == 'OBJECT' and context.active_object is not None
            and context.active_object.type == 'MESH'
        )

    def execute(self, context):
        source = context.active_object
        previous_selection = list(context.selected_objects)
        previous_active = source
        output = None
        neutral = None
        try:
            reason = _static_mesh_reason(source, allow_deformation=True)
            if reason:
                raise ValueError(reason)
            reason = deform_transfer.unsupported_reason(source)
            if reason:
                raise ValueError(reason)
            reason = _custom_data_reason(source.data)
            if reason:
                raise ValueError(reason)

            target = int(context.scene.fishhwb_triangle_target)
            if target > 500000:
                raise ValueError(
                    'Smart Remesh is limited to 500,000 target triangles for '
                    'safe operation. Reduce the triangle limit first.')
            deforming = deform_transfer.has_deformation(source)
            before = triangle_count(source.data)
            output = _copy_mesh_object(source, context, '_SmartRemesh')
            for key in (
                    'fishhwb_remesh_history', 'fishhwb_lod_history',
                    'fishhwb_output_id', 'fishhwb_generated_job',
                    'fishhwb_source_deformation_sensitive'):
                if key in output:
                    del output[key]

            if deforming:
                keys = output.data.shape_keys
                if keys:
                    basis = [item.co.copy() for item in keys.key_blocks[0].data]
                    output.shape_key_clear()
                    for vert, co in zip(output.data.vertices, basis):
                        vert.co = co
                output.modifiers.clear()
            else:
                if output.modifiers:
                    evaluated = _evaluated_mesh_copy(output, context)
                    old = output.data
                    output.modifiers.clear()
                    output.data = evaluated
                    if old.users == 0:
                        bpy.data.meshes.remove(old)

            # Attribute source is independent of cleanup and reconstruction.
            neutral = output.data.copy()
            _v08._repair_static_mesh(output.data, fill_holes=True)
            quadriflow, actual = _retopology_geometry(output, context, target)
            groups, shapes = _project_details(
                source, output, neutral, deforming, context)
            output['fishhwb_generated_job'] = 'smart_remesh'
            output['fishhwb_retopology_status'] = (
                'QUADRIFLOW' if quadriflow else 'VOXEL_QUADS')
            output['fishhwb_triangle_target'] = target
            _select_only(context, output)
            method = 'QuadriFlow' if quadriflow else 'voxel quad topology'
            _action_report(
                self, context,
                f'Smart Remesh: {before:,} -> {actual:,} triangles '
                f'(target {target:,}); repaired and rebuilt with {method}. '
                f'Projected {len(neutral.uv_layers)} UV layers, '
                f'{groups} vertex groups and {shapes} blendshapes. '
                'Compatible armature bindings restored; source untouched. '
                'Inspect UV seams, deformation and small details before export.',
                changed=1)
            return {'FINISHED'}
        except Exception as exc:
            if output is not None:
                _remove_object_and_mesh(output)
            for obj in list(context.selected_objects):
                obj.select_set(False)
            for obj in previous_selection:
                if obj.name in bpy.data.objects:
                    obj.select_set(True)
            if previous_active and previous_active.name in bpy.data.objects:
                context.view_layer.objects.active = previous_active
            _action_report(
                self, context,
                'Smart Remesh not applied: ' + str(exc) + '. Source preserved.',
                unsupported=1)
            return {'CANCELLED'}
        finally:
            if neutral is not None and neutral.users == 0:
                bpy.data.meshes.remove(neutral)


classes = (FISHHWB_OT_smart_remesh,)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
