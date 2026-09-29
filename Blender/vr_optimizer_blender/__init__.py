bl_info = {
    "name": "Optimize Your Project for Blender",
    "author": "FISHHWB | Ded Zed",
    "version": (0, 7, 5),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > FISHHWB",
    "description": "Mesh reduction, joining, Base Color atlases and static LOD copies",
    "category": "Mesh",
}

import bpy
import bmesh
import math
from pathlib import Path
import bpy.utils.previews
from array import array
from bpy.props import BoolProperty, FloatProperty, IntProperty

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


class FISHHWB_PT_tri_limit(bpy.types.Panel):
    bl_label = "Optimize Your Project"
    bl_idname = "FISHHWB_PT_tri_limit"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'FISHHWB'

    def draw(self, context):
        layout = self.layout
        if _brand_preview and "logo" in _brand_preview:
            layout.template_icon(icon_value=_brand_preview["logo"].icon_id, scale=4)
        obj = context.active_object
        if obj and obj.type == 'MESH':
            layout.label(text=f"Source: {obj.name}")
            layout.label(text=f"Base triangles: {triangle_count(obj.data):,}")
        else:
            layout.label(text="Select a mesh object", icon='INFO')
        layout.prop(context.scene, 'fishhwb_tri_limit')
        layout.prop(context.scene, 'fishhwb_apply_modifiers')
        layout.operator('fishhwb.tri_limit', icon='MOD_DECIM')
        layout.separator()
        layout.label(text="Join selected mesh objects")
        layout.prop(context.scene, 'fishhwb_merge_distance')
        layout.prop(context.scene, 'fishhwb_make_atlas')
        if context.scene.fishhwb_make_atlas:
            layout.prop(context.scene, 'fishhwb_atlas_size')
            layout.prop(context.scene, 'fishhwb_atlas_padding')
        layout.operator('fishhwb.join_merge', icon='AUTOMERGE_ON')
        layout.separator()
        layout.label(text="Static Mesh LODs")
        layout.label(text="LOD0 100%  /  LOD1 66%  /  LOD2 33%")
        layout.operator('fishhwb.create_lods', icon='MOD_DECIM')


classes = (FISHHWB_OT_tri_limit, FISHHWB_OT_join_merge,
           FISHHWB_OT_create_lods, FISHHWB_PT_tri_limit)


def register():
    global _brand_preview
    _brand_preview = bpy.utils.previews.new()
    _brand_preview.load("logo", str(Path(__file__).with_name("optimize-your-project-logo.png")), 'IMAGE')
    for cls in classes:
        bpy.utils.register_class(cls)
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


def unregister():
    global _brand_preview
    if _brand_preview is not None:
        bpy.utils.previews.remove(_brand_preview)
        _brand_preview = None
    del bpy.types.Scene.fishhwb_tri_limit
    del bpy.types.Scene.fishhwb_apply_modifiers
    del bpy.types.Scene.fishhwb_merge_distance
    del bpy.types.Scene.fishhwb_make_atlas
    del bpy.types.Scene.fishhwb_atlas_size
    del bpy.types.Scene.fishhwb_atlas_padding
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
