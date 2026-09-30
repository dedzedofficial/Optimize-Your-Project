bl_info = {
    "name": "Optimize Your Project for Blender",
    "author": "FISHHWB | Ded Zed",
    "version": (0, 7, 1),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > FISHHWB",
    "description": "One-click mesh cleanup, remesh and vertex merging with optional mesh reduction, joining and LOD tools",
    "category": "Mesh",
}

import bpy
import bmesh
import math
from pathlib import Path
import bpy.utils.previews
from array import array
from bpy.props import BoolProperty, FloatProperty, IntProperty, StringProperty

_brand_preview = None


def triangle_count(mesh):
    mesh.calc_loop_triangles()
    return len(mesh.loop_triangles)


def evaluated_count(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        return triangle_count(mesh)
    finally:
        evaluated.to_mesh_clear()


class FISHHWB_OT_tri_limit(bpy.types.Operator):
    bl_idname = "fishhwb.tri_limit"
    bl_label = "Create Reduced Copy"
    bl_description = "Duplicate the active mesh and reduce its triangle count"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        source = context.active_object
        limit = context.scene.fishhwb_tri_limit
        before = triangle_count(source.data)
        if before == 0:
            self.report({'ERROR'}, "The source mesh has no triangles")
            return {'CANCELLED'}

        copy = source.copy()
        copy.data = source.data.copy()
        copy.name = source.name + "_TriLimit"
        context.collection.objects.link(copy)
        copy.matrix_world = source.matrix_world.copy()

        # Apply existing modifiers to the copy only, when requested.
        if context.scene.fishhwb_apply_modifiers:
            depsgraph = context.evaluated_depsgraph_get()
            evaluated = copy.evaluated_get(depsgraph)
            try:
                result = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)
            except Exception as exc:
                bpy.data.objects.remove(copy, do_unlink=True)
                self.report({'ERROR'}, "Could not evaluate modifiers: " + str(exc))
                return {'CANCELLED'}
            old_mesh = copy.data
            copy.modifiers.clear()
            copy.data = result
            if old_mesh.users == 0:
                bpy.data.meshes.remove(old_mesh)

        before = triangle_count(copy.data)
        if before > limit:
            modifier = copy.modifiers.new("Triangle Limit", 'DECIMATE')
            modifier.decimate_type = 'COLLAPSE'
            modifier.use_collapse_triangulate = True
            depsgraph = context.evaluated_depsgraph_get()
            low, high = 0.0, 1.0
            best_ratio = None
            best_count = -1
            for i in range(24):
                ratio = (low + high) * 0.5
                modifier.ratio = ratio
                context.view_layer.update()
                count = evaluated_count(copy, depsgraph)
                if count <= limit:
                    if count > best_count:
                        best_count, best_ratio = count, ratio
                    low = ratio
                else:
                    high = ratio
            if best_ratio is None or best_count == 0:
                bpy.data.objects.remove(copy, do_unlink=True)
                self.report({'ERROR'}, "This mesh cannot retain any triangles at that limit")
                return {'CANCELLED'}
            modifier.ratio = best_ratio
            context.view_layer.update()
            evaluated = copy.evaluated_get(depsgraph)
            result = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)
            final_count = triangle_count(result)
            if final_count > limit:
                bpy.data.meshes.remove(result)
                bpy.data.objects.remove(copy, do_unlink=True)
                self.report({'ERROR'}, "Could not satisfy the requested limit")
                return {'CANCELLED'}
            old_mesh = copy.data
            copy.modifiers.remove(modifier)
            copy.data = result
            if old_mesh.users == 0:
                bpy.data.meshes.remove(old_mesh)
        else:
            final_count = before

        for obj in context.selected_objects:
            obj.select_set(False)
        copy.select_set(True)
        context.view_layer.objects.active = copy
        self.report({'INFO'}, f"Created {copy.name}: {final_count:,} triangles (limit {limit:,})")
        return {'FINISHED'}


def reduce_copy_to_limit(obj, target, context):
    """Replace only this object's mesh with an evaluated Decimate result."""
    if triangle_count(obj.data) <= target:
        return triangle_count(obj.data)
    modifier = obj.modifiers.new("LOD Triangle Limit", 'DECIMATE')
    modifier.decimate_type = 'COLLAPSE'
    modifier.use_collapse_triangulate = True
    depsgraph = context.evaluated_depsgraph_get()
    low, high = 0.0, 1.0
    best_ratio, best_count = None, -1
    for _ in range(24):
        ratio = (low + high) * 0.5
        modifier.ratio = ratio
        context.view_layer.update()
        count = evaluated_count(obj, depsgraph)
        if count <= target:
            if count > best_count:
                best_ratio, best_count = ratio, count
            low = ratio
        else:
            high = ratio
    if best_ratio is None or best_count < 1:
        raise ValueError("Unable to preserve a triangle within this LOD limit")
    modifier.ratio = best_ratio
    context.view_layer.update()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(
        evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)
    count = triangle_count(mesh)
    if count < 1 or count > target:
        bpy.data.meshes.remove(mesh)
        raise ValueError("The evaluated LOD did not meet its triangle target")
    old_mesh = obj.data
    obj.modifiers.remove(modifier)
    obj.data = mesh
    if old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)
    return count


class FISHHWB_OT_create_lods(bpy.types.Operator):
    bl_idname = "fishhwb.create_lods"
    bl_label = "Create LOD0 / LOD1 / LOD2"
    bl_description = "Create static mesh copies at 100%, up to 66%, and up to 33% of the original triangle count"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        source = context.active_object
        if source.data.shape_keys or source.vertex_groups or any(m.type == 'ARMATURE' for m in source.modifiers):
            self.report({'ERROR'}, "LOD copies currently support static meshes without shape keys, vertex groups or armature modifiers")
            return {'CANCELLED'}
        original_selection = list(context.selected_objects)
        made = []
        collection = bpy.data.collections.new(source.name + "_LODs")
        context.scene.collection.children.link(collection)
        try:
            base = source.copy()
            base.data = source.data.copy()
            collection.objects.link(base)
            made.append(base)
            base.matrix_world = source.matrix_world.copy()
            base.name = source.name + "_LOD0"
            if context.scene.fishhwb_apply_modifiers:
                depsgraph = context.evaluated_depsgraph_get()
                evaluated = base.evaluated_get(depsgraph)
                mesh = bpy.data.meshes.new_from_object(
                    evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)
                old_mesh = base.data
                base.modifiers.clear()
                base.data = mesh
                if old_mesh.users == 0:
                    bpy.data.meshes.remove(old_mesh)
            elif base.modifiers:
                raise ValueError("Enable Apply Existing Modifiers to make measurable LOD meshes")
            count = triangle_count(base.data)
            if count < 1:
                raise ValueError("The selected object has no triangles")
            base['fishhwb_lod_level'] = 0
            for level, fraction in ((1, 0.66), (2, 0.33)):
                copy = base.copy()
                copy.data = base.data.copy()
                collection.objects.link(copy)
                made.append(copy)
                copy.matrix_world = source.matrix_world.copy()
                copy.name = source.name + f"_LOD{level}"
                target = max(1, int(count * fraction))
                actual = reduce_copy_to_limit(copy, target, context)
                copy['fishhwb_lod_level'] = level
                copy['fishhwb_triangle_target'] = target
                copy.hide_set(True)
            for obj in context.selected_objects:
                obj.select_set(False)
            base.select_set(True)
            context.view_layer.objects.active = base
            self.report({'INFO'},
                f"LODs created from {count:,} triangles: LOD1 {triangle_count(made[1].data):,}, LOD2 {triangle_count(made[2].data):,}")
            return {'FINISHED'}
        except Exception as exc:
            for copy in made:
                mesh = copy.data
                bpy.data.objects.remove(copy, do_unlink=True)
                if mesh and mesh.users == 0:
                    bpy.data.meshes.remove(mesh)
            bpy.data.collections.remove(collection)
            for obj in context.selected_objects:
                obj.select_set(False)
            for obj in original_selection:
                obj.select_set(True)
            context.view_layer.objects.active = source
            self.report({'ERROR'}, "LOD generation failed: " + str(exc))
            return {'CANCELLED'}


def base_color_image(material):
    if not material or not material.use_nodes:
        raise ValueError("Atlas requires node-based materials with direct image Base Color")
    outputs = [n for n in material.node_tree.nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output]
    if not outputs or not outputs[0].inputs['Surface'].is_linked:
        raise ValueError(f"{material.name} has no active surface output")
    shader = outputs[0].inputs['Surface'].links[0].from_node
    if shader.type != 'BSDF_PRINCIPLED':
        raise ValueError(f"{material.name} needs a Principled BSDF")
    color = shader.inputs.get('Base Color')
    if not color or len(color.links) != 1 or color.links[0].from_node.type != 'TEX_IMAGE':
        raise ValueError(f"{material.name} needs an image directly linked to Base Color")
    node = color.links[0].from_node
    if node.inputs['Vector'].is_linked:
        raise ValueError(f"{material.name} uses mapped texture coordinates; atlas skipped")
    image = node.image
    if not image or image.source != 'FILE' or image.size[0] == 0 or image.size[1] == 0:
        raise ValueError(f"{material.name} needs a loaded single-file image")
    if image.tiles and len(image.tiles) > 1:
        raise ValueError(f"{material.name} uses UDIM tiles; atlas skipped")
    if any(inp.is_linked for inp in shader.inputs if inp != color):
        raise ValueError(f"{material.name} uses additional shader maps; baking is needed")
    return image


def build_atlas(obj, material_images, size, padding):
    images = list(dict.fromkeys(material_images.values()))
    cols = math.ceil(math.sqrt(len(images)))
    rows = math.ceil(len(images) / cols)
    tile = min((size - (cols + 1) * padding) // cols,
               (size - (rows + 1) * padding) // rows)
    if tile < 2:
        raise ValueError("Atlas too small for the number of images and padding")
    uv_layer = obj.data.uv_layers.get("FISHHWB_Atlas_UV")
    if not uv_layer:
        raise ValueError("Joined mesh lost its active UV map")
    obj.data.uv_layers.active_index = obj.data.uv_layers.find(uv_layer.name)

    pixels = array('f', [0.0]) * (size * size * 4)
    placements = {}
    for i, image in enumerate(images):
        scaled = image.copy()
        try:
            scaled.scale(tile, tile)
            source_pixels = array('f', scaled.pixels[:])
            x = padding + (i % cols) * (tile + padding)
            y = padding + (i // cols) * (tile + padding)
            for line in range(tile):
                start = ((y + line) * size + x) * 4
                src = line * tile * 4
                pixels[start:start + tile * 4] = source_pixels[src:src + tile * 4]
            placements[image] = (x, y)
        finally:
            bpy.data.images.remove(scaled)

    # Do not rewrite material assignments or UVs until every image was copied.
    atlas = bpy.data.images.new(obj.name + "_BaseColor_Atlas", width=size, height=size, alpha=True)
    atlas.pixels[:] = pixels
    atlas.update()
    atlas_material = bpy.data.materials.new(obj.name + "_Atlas")
    atlas_material.use_nodes = True
    atlas_material.blend_method = 'BLEND'
    nodes = atlas_material.node_tree.nodes
    bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
    tex = nodes.new('ShaderNodeTexImage')
    tex.image = atlas
    atlas_material.node_tree.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    atlas_material.node_tree.links.new(tex.outputs['Alpha'], bsdf.inputs['Alpha'])

    original_slots = [slot.material for slot in obj.material_slots]
    for face in obj.data.polygons:
        material = original_slots[face.material_index]
        image = material_images.get(material)
        if image is None:
            raise ValueError(f"Joined material {material.name if material else '<empty>'} changed unexpectedly")
        x, y = placements[image]
        for index in face.loop_indices:
            uv = uv_layer.data[index].uv
            uv.x = (x + min(1.0, max(0.0, uv.x)) * (tile - 1) + 0.5) / size
            uv.y = (y + min(1.0, max(0.0, uv.y)) * (tile - 1) + 0.5) / size
        face.material_index = 0
    obj.data.materials.clear()
    obj.data.materials.append(atlas_material)


class FISHHWB_OT_join_merge(bpy.types.Operator):
    bl_idname = "fishhwb.join_merge"
    bl_label = "Join Selected and Merge Vertices"
    bl_description = "Create one new mesh from selected meshes and weld nearby vertices"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and len([o for o in context.selected_objects if o.type == 'MESH']) >= 2

    def execute(self, context):
        sources = [o for o in context.selected_objects if o.type == 'MESH']
        if any(o.data.shape_keys for o in sources):
            self.report({'ERROR'}, "Shape keys are not supported by vertex merging; remove them from copies first")
            return {'CANCELLED'}

        make_atlas = context.scene.fishhwb_make_atlas
        material_images = {}
        if make_atlas:
            try:
                for source in sources:
                    if not source.data.uv_layers.active:
                        raise ValueError(f"{source.name} has no active UV map")
                    for poly in source.data.polygons:
                        material = source.material_slots[poly.material_index].material
                        if material not in material_images:
                            material_images[material] = base_color_image(material)
                        for index in poly.loop_indices:
                            uv = source.data.uv_layers.active.data[index].uv
                            if not (-0.00001 <= uv.x <= 1.00001 and -0.00001 <= uv.y <= 1.00001):
                                raise ValueError(f"{source.name} has tiled UVs outside 0–1; atlas skipped")
                if not material_images:
                    raise ValueError("No textured faces found")
                if len(set(material_images.values())) > 64:
                    raise ValueError("Atlas supports up to 64 distinct images")
            except (ValueError, IndexError, AttributeError) as exc:
                self.report({'ERROR'}, str(exc))
                return {'CANCELLED'}

        original_active = context.view_layer.objects.active
        original_selection = list(context.selected_objects)
        copies = []
        try:
            for source in sources:
                copy = source.copy()
                copy.data = source.data.copy()
                context.collection.objects.link(copy)
                copies.append(copy)
                copy.matrix_world = source.matrix_world.copy()
                if make_atlas:
                    # Give each active UV map a common name so Blender's Join combines it.
                    uv = copy.data.uv_layers.active
                    uv.name = "FISHHWB_Atlas_UV"
                    copy.data.uv_layers.active_index = copy.data.uv_layers.find(uv.name)

                if context.scene.fishhwb_apply_modifiers:
                    depsgraph = context.evaluated_depsgraph_get()
                    evaluated = copy.evaluated_get(depsgraph)
                    mesh = bpy.data.meshes.new_from_object(
                        evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)
                    old_mesh = copy.data
                    copy.modifiers.clear()
                    copy.data = mesh
                    if old_mesh.users == 0:
                        bpy.data.meshes.remove(old_mesh)

            for obj in context.selected_objects:
                obj.select_set(False)
            for obj in copies:
                obj.select_set(True)
            joined = copies[0]
            context.view_layer.objects.active = joined
            result = bpy.ops.object.join()
            if 'FINISHED' not in result:
                raise RuntimeError("Blender could not join the selected meshes")
            joined.name = "Joined_TriLimit"
            joined.data.name = joined.name

            before = len(joined.data.vertices)
            bm = bmesh.new()
            try:
                bm.from_mesh(joined.data)
                bmesh.ops.remove_doubles(
                    bm, verts=list(bm.verts), dist=context.scene.fishhwb_merge_distance)
                bm.to_mesh(joined.data)
            finally:
                bm.free()
            joined.data.update()
            if make_atlas:
                build_atlas(joined, material_images, context.scene.fishhwb_atlas_size,
                            context.scene.fishhwb_atlas_padding)
            joined.select_set(True)
            context.view_layer.objects.active = joined
            self.report({'INFO'},
                f"Joined {len(sources)} meshes: {before - len(joined.data.vertices):,} vertices merged")
            return {'FINISHED'}
        except Exception as exc:
            for copy in copies:
                if copy.name in bpy.data.objects:
                    mesh = copy.data
                    bpy.data.objects.remove(copy, do_unlink=True)
                    if mesh and mesh.users == 0:
                        bpy.data.meshes.remove(mesh)
            for obj in context.selected_objects:
                obj.select_set(False)
            for obj in original_selection:
                obj.select_set(True)
            context.view_layer.objects.active = original_active
            self.report({'ERROR'}, "Join failed: " + str(exc))
            return {'CANCELLED'}



def _copy_mesh_object(source, context, suffix):
    copy = source.copy()
    mesh = None
    try:
        mesh = source.data.copy()
        copy.data = mesh
        base = source.name + suffix
        name, number = base, 1
        while name in bpy.data.objects:
            name = f"{base}_{number:03d}"
            number += 1
        copy.name = name
        mesh.name = name
        context.collection.objects.link(copy)
        copy.matrix_world = source.matrix_world.copy()
        return copy
    except Exception:
        bpy.data.objects.remove(copy, do_unlink=True)
        if mesh is not None and mesh.users == 0:
            bpy.data.meshes.remove(mesh)
        raise


def _action_report(operator, context, detail, changed=0, unchanged=0,
                   skipped=0, unsupported=0, failed=0):
    counts = (f"Changed: {changed} | Unchanged: {unchanged} | Skipped: {skipped} | "
              f"Unsupported: {unsupported} | Failed: {failed}")
    context.scene.fishhwb_last_result = counts + "\n" + detail
    operator.report({'WARNING'} if failed or unsupported else {'INFO'}, counts + ". " + detail)


def _cleanup_unsupported(source):
    if source.data.shape_keys:
        return "Shape keys depend on the original topology."
    if source.vertex_groups or source.find_armature():
        return "Rigged meshes and vertex groups depend on the original topology."
    if source.modifiers:
        return "Apply modifiers to a separate static copy before cleanup."
    if source.data.has_custom_normals:
        return "Custom split normals need a dedicated shading workflow."
    if source.library or source.data.library or source.override_library or source.data.override_library:
        return "Linked or overridden meshes must be made local before cleanup."
    if any(not math.isfinite(value) for vertex in source.data.vertices for value in vertex.co):
        return "Mesh coordinates contain non-finite values."
    if not source.data.vertices:
        return "The mesh has no vertices."
    return None


def _clean_mesh(mesh):
    """Clean only the caller-owned mesh. Keep open surfaces and their winding."""
    stats = dict(vertices=0, loose_edges=0, duplicates=0, zero_faces=0,
                 material_slots=0, normals=0)
    before_vertices = len(mesh.vertices)
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        # Exact coordinates only: no proximity threshold can erase thin details.
        targets, coordinates = {}, {}
        for vertex in bm.verts:
            key = tuple(vertex.co)
            if key in coordinates:
                targets[vertex] = coordinates[key]
            else:
                coordinates[key] = vertex
        count = len(bm.verts)
        if targets:
            bmesh.ops.weld_verts(bm, targetmap=targets)
        stats['duplicates'] = count - len(bm.verts)

        zero_faces = [face for face in bm.faces if face.calc_area() == 0.0]
        stats['zero_faces'] = len(zero_faces)
        if zero_faces:
            bmesh.ops.delete(bm, geom=zero_faces, context='FACES_ONLY')
        loose_edges = [edge for edge in bm.edges if not edge.link_faces]
        stats['loose_edges'] = len(loose_edges)
        if loose_edges:
            bmesh.ops.delete(bm, geom=loose_edges, context='EDGES')
        loose_verts = [vertex for vertex in bm.verts if not vertex.link_edges]
        if loose_verts:
            bmesh.ops.delete(bm, geom=loose_verts, context='VERTS')

        # Only closed manifold components have a meaningful outside direction.
        bm.normal_update()
        remaining = set(bm.faces)
        while remaining:
            seed = remaining.pop()
            component, pending = [seed], [seed]
            while pending:
                face = pending.pop()
                for edge in face.edges:
                    for neighbor in edge.link_faces:
                        if neighbor in remaining:
                            remaining.remove(neighbor)
                            pending.append(neighbor)
                            component.append(neighbor)
            if all(edge.is_manifold for face in component for edge in face.edges):
                normals = [(face, face.normal.copy()) for face in component]
                bmesh.ops.recalc_face_normals(bm, faces=component)
                bm.normal_update()
                stats['normals'] += sum(face.normal.dot(normal) < 0.0 for face, normal in normals)
        bm.to_mesh(mesh)
    finally:
        bm.free()
    mesh.update()
    stats['vertices'] = before_vertices - len(mesh.vertices)
    used = {face.material_index for face in mesh.polygons}
    # Removing in descending order lets Blender remap face indices correctly.
    for index in reversed(range(len(mesh.materials))):
        if index not in used:
            mesh.materials.pop(index=index)
            stats['material_slots'] += 1
    return stats


class FISHHWB_OT_clean_selected_mesh(bpy.types.Operator):
    bl_idname = "fishhwb.clean_selected_mesh"
    bl_label = "Clean Selected Mesh"
    bl_description = "Clean the active static mesh on a new copy; preserve the original"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.mode == 'OBJECT' and context.active_object is not None
                and context.active_object.type == 'MESH'
                and context.active_object.select_get())

    def execute(self, context):
        source = context.active_object
        reason = _cleanup_unsupported(source)
        if reason:
            _action_report(self, context, reason, unsupported=1)
            return {'CANCELLED'}
        selection = list(context.selected_objects)
        copy = None
        try:
            copy = _copy_mesh_object(source, context, "_Clean")
            stats = _clean_mesh(copy.data)
            _select_only(context, copy)
            changed = any(stats.values())
            detail = (f"{copy.name}: Vertices removed: {stats['vertices']:,} "
                      f"(exact duplicates merged: {stats['duplicates']:,}); "
                      f"Loose edges removed: {stats['loose_edges']:,}; "
                      f"Zero-area faces removed: {stats['zero_faces']:,}; "
                      f"Unused material slots removed: {stats['material_slots']:,}; "
                      f"Faces reoriented: {stats['normals']:,}. Original object preserved.")
            _action_report(self, context, detail, changed=int(changed), unchanged=int(not changed))
            return {'FINISHED'}
        except Exception as exc:
            if copy is not None:
                mesh = copy.data
                bpy.data.objects.remove(copy, do_unlink=True)
                if mesh.users == 0:
                    bpy.data.meshes.remove(mesh)
            for item in context.selected_objects:
                item.select_set(False)
            for item in selection:
                item.select_set(True)
            context.view_layer.objects.active = source
            _action_report(self, context, "Mesh cleanup failed: " + str(exc), failed=1)
            return {'CANCELLED'}


def _select_only(context, obj):
    for item in context.selected_objects:
        item.select_set(False)
    obj.select_set(True)
    context.view_layer.objects.active = obj


class FISHHWB_OT_one_click_remesh(bpy.types.Operator):
    bl_idname = "fishhwb.one_click_remesh"
    bl_label = "One-Click Remesh"
    bl_description = "Create a safe remeshed copy using an automatic voxel size"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        source = context.active_object
        if source.data.shape_keys or source.vertex_groups or any(m.type == 'ARMATURE' for m in source.modifiers):
            _action_report(self, context, "One-Click Remesh supports static meshes without rigs or shape keys.", unsupported=1)
            return {'CANCELLED'}

        copy = None
        original_selection = list(context.selected_objects)
        original_active = source

        try:
            copy = _copy_mesh_object(source, context, "_Remesh")
            before = triangle_count(copy.data)
            if before < 1:
                raise ValueError("The selected mesh has no triangles")

            max_dimension = max(abs(v) for v in copy.dimensions)
            if max_dimension <= 0:
                raise ValueError("The selected mesh has no usable size")

            modifier = copy.modifiers.new("One Click Remesh", 'REMESH')
            try:
                modifier.mode = 'VOXEL'
            except (TypeError, ValueError):
                modifier.mode = 'SMOOTH'

            if hasattr(modifier, "voxel_size"):
                modifier.voxel_size = max(max_dimension / 96.0, 0.0001)
            if hasattr(modifier, "octree_depth"):
                modifier.octree_depth = 6
            if hasattr(modifier, "use_smooth_shade"):
                modifier.use_smooth_shade = True

            depsgraph = context.evaluated_depsgraph_get()
            context.view_layer.update()
            evaluated = copy.evaluated_get(depsgraph)
            result = bpy.data.meshes.new_from_object(
                evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)

            after = triangle_count(result)
            if after < 1:
                bpy.data.meshes.remove(result)
                raise ValueError("Remesh produced no triangles")

            old_mesh = copy.data
            copy.modifiers.clear()
            copy.data = result
            if old_mesh.users == 0:
                bpy.data.meshes.remove(old_mesh)

            _select_only(context, copy)
            _action_report(self, context, f"Remeshed copy created: {before:,} -> {after:,} triangles. Original object preserved.", changed=1)
            return {'FINISHED'}
        except Exception as exc:
            if copy is not None:
                mesh = copy.data
                bpy.data.objects.remove(copy, do_unlink=True)
                if mesh.users == 0:
                    bpy.data.meshes.remove(mesh)
            for item in context.selected_objects:
                item.select_set(False)
            for item in original_selection:
                if item and item.name in bpy.data.objects:
                    item.select_set(True)
            context.view_layer.objects.active = original_active
            _action_report(self, context, "Remesh failed: " + str(exc), failed=1)
            return {'CANCELLED'}


class FISHHWB_OT_merge_vertices(bpy.types.Operator):
    bl_idname = "fishhwb.merge_vertices"
    bl_label = "Merge Duplicate Vertices"
    bl_description = "Create a copy and merge nearby duplicate vertices using the Merge Distance"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        source = context.active_object
        if source.data.shape_keys:
            _action_report(self, context, "Shape keys depend on the original topology.", unsupported=1)
            return {'CANCELLED'}

        copy = None
        original_selection = list(context.selected_objects)
        try:
            copy = _copy_mesh_object(source, context, "_Merged")
            before = len(copy.data.vertices)
            bm = bmesh.new()
            try:
                bm.from_mesh(copy.data)
                bmesh.ops.remove_doubles(
                    bm,
                    verts=list(bm.verts),
                    dist=max(context.scene.fishhwb_merge_distance, 0.0))
                bm.to_mesh(copy.data)
            finally:
                bm.free()

            copy.data.update()
            after = len(copy.data.vertices)
            _select_only(context, copy)
            _action_report(self, context, f"Merged {before - after:,} vertices on {copy.name}. Original object preserved.", changed=int(before != after), unchanged=int(before == after))
            return {'FINISHED'}
        except Exception as exc:
            if copy is not None:
                mesh = copy.data
                bpy.data.objects.remove(copy, do_unlink=True)
                if mesh.users == 0:
                    bpy.data.meshes.remove(mesh)
            for item in context.selected_objects:
                item.select_set(False)
            for item in original_selection:
                item.select_set(True)
            context.view_layer.objects.active = source
            _action_report(self, context, "Vertex merge failed: " + str(exc), failed=1)
            return {'CANCELLED'}


class FISHHWB_PT_tri_limit(bpy.types.Panel):
    bl_label = "Optimize Your Project"
    bl_idname = "FISHHWB_PT_tri_limit"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'FISHHWB'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        brand = layout.box()
        if _brand_preview and "logo" in _brand_preview:
            brand.template_icon(icon_value=_brand_preview["logo"].icon_id, scale=3)
        brand.label(text="OPTIMIZE YOUR PROJECT", icon='TOOL_SETTINGS')
        brand.label(text="Free one-click tools for developers")
        brand.label(text="v0.7.1 • Blender")

        obj = context.active_object
        selected = layout.box()
        selected.label(text="CURRENT SELECTION", icon='MESH_DATA')
        if obj and obj.type == 'MESH':
            selected.label(text=obj.name)
            stats = selected.row(align=True)
            stats.label(text=f"Triangles: {triangle_count(obj.data):,}")
            stats.label(text=f"Vertices: {len(obj.data.vertices):,}")
        else:
            selected.label(text="Select one mesh object to begin", icon='INFO')

        quick = layout.box()
        quick.label(text="ONE-CLICK CLEANUP", icon='MODIFIER')
        quick.label(text="Fast, safe actions that create new copies.")
        quick.separator()

        clean = quick.row()
        clean.scale_y = 1.45
        clean.operator('fishhwb.clean_selected_mesh', text="CLEAN SELECTED MESH", icon='BRUSH_DATA')
        quick.label(text="Clean mesh clutter on a new static copy.")
        quick.separator()

        remesh = quick.row()
        remesh.scale_y = 1.45
        remesh.operator('fishhwb.one_click_remesh', text="ONE-CLICK REMESH", icon='MOD_REMESH')

        quick.separator()
        quick.label(text="Merge nearby duplicate vertices")
        quick.prop(context.scene, 'fishhwb_merge_distance')
        merge = quick.row()
        merge.scale_y = 1.45
        merge.operator('fishhwb.merge_vertices', text="MERGE DUPLICATE VERTICES", icon='AUTOMERGE_ON')

        tools = layout.box()
        tools.label(text="MORE TOOLS", icon='PREFERENCES')
        tools.prop(
            context.scene,
            'fishhwb_show_advanced',
            text="Show Advanced Mesh Tools",
            toggle=True)

        if context.scene.fishhwb_show_advanced:
            advanced = tools.column(align=False)
            advanced.separator()
            advanced.label(text="Triangle Reduction", icon='MOD_DECIM')
            advanced.prop(context.scene, 'fishhwb_tri_limit')
            advanced.prop(context.scene, 'fishhwb_apply_modifiers')
            row = advanced.row()
            row.scale_y = 1.2
            row.operator('fishhwb.tri_limit', text="CREATE REDUCED COPY", icon='MOD_DECIM')

            advanced.separator()
            advanced.label(text="Join + Atlas", icon='AUTOMERGE_ON')
            advanced.prop(context.scene, 'fishhwb_make_atlas')
            if context.scene.fishhwb_make_atlas:
                advanced.prop(context.scene, 'fishhwb_atlas_size')
                advanced.prop(context.scene, 'fishhwb_atlas_padding')
            row = advanced.row()
            row.scale_y = 1.2
            row.operator('fishhwb.join_merge', text="JOIN SELECTED MESHES", icon='AUTOMERGE_ON')

            advanced.separator()
            advanced.label(text="Static Mesh LODs", icon='MOD_DECIM')
            row = advanced.row()
            row.scale_y = 1.2
            row.operator('fishhwb.create_lods', text="CREATE LOD0 / LOD1 / LOD2", icon='MOD_DECIM')

        if context.scene.fishhwb_last_result:
            result = layout.box()
            result.label(text="LAST RESULT", icon='INFO')
            # Wrap long reports to fit narrow sidebar panels.
            import textwrap
            width = max(24, int(context.region.width / (7 * context.preferences.system.ui_scale)))
            for line in context.scene.fishhwb_last_result.splitlines():
                for wrapped in textwrap.wrap(line, width=width):
                    result.label(text=wrapped)

        support = layout.box()
        support.label(text="FREE FOR DEVELOPERS", icon='HEART')
        support.label(text="Built to save time, reduce busywork,")
        support.label(text="and help newer creators learn.")
        support.separator()
        support.label(text="If this tool helps you, optional Patreon")
        support.label(text="support funds new tools, testing,")
        support.label(text="documentation and future integrations.")
        support.label(text="The project stays free either way.")

        donate = support.row()
        donate.scale_y = 1.35
        donate.operator(
            "wm.url_open",
            text="SUPPORT DEVELOPMENT ON PATREON",
            icon='URL').url = "https://www.patreon.com/cw/DedZed"

        links = layout.row(align=True)
        links.operator("wm.url_open", text="GitHub", icon='URL').url = "https://github.com/dedzedofficial/Optimize-Your-Project"
        links.operator("wm.url_open", text="Website", icon='URL').url = "https://fishhwb.github.io/"


classes = (FISHHWB_OT_clean_selected_mesh, FISHHWB_OT_tri_limit, FISHHWB_OT_join_merge, FISHHWB_OT_one_click_remesh,
           FISHHWB_OT_merge_vertices, FISHHWB_OT_create_lods, FISHHWB_PT_tri_limit)


def register():
    global _brand_preview
    _brand_preview = bpy.utils.previews.new()
    _brand_preview.load("logo", str(Path(__file__).with_name("optimize-your-project-logo.png")), 'IMAGE')
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.fishhwb_last_result = StringProperty(options={'SKIP_SAVE'})
    bpy.types.Scene.fishhwb_tri_limit = IntProperty(name="Triangle Limit", default=1000, min=1)
    bpy.types.Scene.fishhwb_apply_modifiers = BoolProperty(name="Apply Existing Modifiers", default=True,
        description="Include existing modifiers in the new copy before decimation")
    bpy.types.Scene.fishhwb_make_atlas = BoolProperty(
        name="Merge Base Color Textures + UVs", default=False,
        description="Pack supported image textures into one atlas and remap UVs on the joined copy")
    bpy.types.Scene.fishhwb_atlas_size = IntProperty(
        name="Atlas Size", default=1024, min=256, max=4096)
    bpy.types.Scene.fishhwb_atlas_padding = IntProperty(
        name="Padding (Pixels)", default=4, min=0, max=32)
    bpy.types.Scene.fishhwb_merge_distance = FloatProperty(
        name="Merge Distance", default=0.0001, min=0.0, precision=5, subtype='DISTANCE',
        description="World-space proximity used to merge vertices after joining")
    bpy.types.Scene.fishhwb_show_advanced = BoolProperty(
        name="Show Advanced Mesh Tools", default=False,
        description="Reveal the optional triangle reduction, joining, atlas and LOD tools")


def unregister():
    global _brand_preview
    if _brand_preview is not None:
        bpy.utils.previews.remove(_brand_preview)
        _brand_preview = None
    del bpy.types.Scene.fishhwb_last_result
    del bpy.types.Scene.fishhwb_tri_limit
    del bpy.types.Scene.fishhwb_apply_modifiers
    del bpy.types.Scene.fishhwb_merge_distance
    del bpy.types.Scene.fishhwb_make_atlas
    del bpy.types.Scene.fishhwb_atlas_size
    del bpy.types.Scene.fishhwb_atlas_padding
    del bpy.types.Scene.fishhwb_show_advanced
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
