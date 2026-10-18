# SPDX-License-Identifier: GPL-3.0-or-later
import math
import bmesh
import bpy


def _action_report(operator, context, detail, changed=0, unsupported=0, failed=0, unchanged=0):
    parts = [
        f"Changed: {changed}",
        f"Unchanged: {unchanged}",
        f"Unsupported: {unsupported}",
        f"Failed: {failed}",
    ]
    message = " | ".join(parts) + ". " + detail
    context.scene.fishhwb_last_result = message
    operator.report({'ERROR'} if failed else ({'WARNING'} if unsupported and not changed else {'INFO'}), message)


def _has_deformation(obj):
    mesh = obj.data
    return bool(
        mesh.shape_keys
        or obj.vertex_groups
        or any(mod.type == 'ARMATURE' for mod in obj.modifiers)
    )


def _mesh_diagonal(mesh):
    if not mesh.vertices:
        return 0.0
    xs = [v.co.x for v in mesh.vertices]
    ys = [v.co.y for v in mesh.vertices]
    zs = [v.co.z for v in mesh.vertices]
    return math.sqrt(
        (max(xs) - min(xs)) ** 2
        + (max(ys) - min(ys)) ** 2
        + (max(zs) - min(zs)) ** 2
    )


def _small_hole_edges(bm, diagonal):
    """Only fill closed, tiny boundary loops; leave intentional openings alone."""
    remaining = {edge for edge in bm.edges if edge.is_boundary}
    fill_edges = []
    while remaining:
        first = remaining.pop()
        component = {first}
        pending = [first]
        while pending:
            edge = pending.pop()
            for vert in edge.verts:
                for other in vert.link_edges:
                    if other in remaining:
                        remaining.remove(other)
                        component.add(other)
                        pending.append(other)
        vertices = {vert for edge in component for vert in edge.verts}
        perimeter = sum(edge.calc_length() for edge in component)
        if (3 <= len(component) <= 8 and len(vertices) == len(component)
                and all(sum(1 for edge in vert.link_edges if edge in component) == 2
                        for vert in vertices)
                and perimeter < max(1.0e-5, diagonal * 0.35)):
            fill_edges.extend(component)
    return fill_edges


def _repair_static_mesh(mesh, fill_holes=True):
    """Repair obvious cracks and broken topology without touching another object."""
    before = (len(mesh.vertices), len(mesh.edges), len(mesh.polygons))
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        diagonal = max(_mesh_diagonal(mesh), 0.001)
        weld_distance = max(1.0e-6, diagonal * 1.0e-5)

        if bm.verts:
            bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=weld_distance)
        if bm.edges:
            bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=weld_distance)

        loose_edges = [e for e in bm.edges if not e.link_faces]
        loose_verts = [v for v in bm.verts if not v.link_edges and not v.link_faces]
        if loose_edges:
            bmesh.ops.delete(bm, geom=loose_edges, context='EDGES')
        if loose_verts:
            bmesh.ops.delete(bm, geom=loose_verts, context='VERTS')

        if fill_holes:
            tiny_holes = _small_hole_edges(bm, diagonal)
            if tiny_holes:
                bmesh.ops.holes_fill(bm, edges=tiny_holes, sides=8)

        if bm.faces:
            bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))

        bm.to_mesh(mesh)
        mesh.validate(verbose=False, clean_customdata=False)
        mesh.update()
    finally:
        bm.free()

    after = (len(mesh.vertices), len(mesh.edges), len(mesh.polygons))
    return before != after


def _activate_only(context, obj):
    if context.mode != 'OBJECT':
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass
    for item in list(context.selected_objects):
        item.select_set(False)
    obj.select_set(True)
    context.view_layer.objects.active = obj


def _voxel_rebuild(obj, context, target):
    """Best-effort manifold rebuild and quad retopology for the Remesh output copy."""
    mesh = obj.data
    if _has_deformation(obj) or not mesh.vertices:
        return False

    diagonal = _mesh_diagonal(mesh)
    if diagonal <= 0.0:
        return False

    target = max(128, int(target))
    cells = max(48.0, min(320.0, math.sqrt(target) * 1.8))
    voxel_size = max(0.0001, diagonal / cells)

    original_selection = list(context.selected_objects)
    original_active = context.view_layer.objects.active
    backup_mesh = mesh.copy()
    required_uvs = {layer.name for layer in mesh.uv_layers}
    try:
        _activate_only(context, obj)
        mesh.remesh_voxel_size = voxel_size
        mesh.remesh_voxel_adaptivity = 0.0
        if hasattr(mesh, "use_remesh_fix_poles"):
            mesh.use_remesh_fix_poles = True
        if hasattr(mesh, "use_remesh_preserve_volume"):
            mesh.use_remesh_preserve_volume = True
        if hasattr(mesh, "use_remesh_preserve_attributes"):
            mesh.use_remesh_preserve_attributes = True

        result = bpy.ops.object.voxel_remesh()
        if 'FINISHED' not in result or len(obj.data.polygons) < 1:
            raise RuntimeError("Voxel remesh produced no usable surface.")

        try:
            bpy.ops.object.quadriflow_remesh(
                use_mesh_symmetry=False,
                use_preserve_sharp=True,
                use_preserve_boundary=False,
                preserve_attributes=True,
                smooth_normals=True,
                mode='FACES',
                target_faces=max(4, target // 2),
                seed=0,
            )
        except Exception:
            pass

        output_uvs = {layer.name for layer in obj.data.uv_layers}
        if required_uvs and not required_uvs.issubset(output_uvs):
            raise RuntimeError("Rebuild could not preserve the source UV layers.")
        return True
    except Exception:
        failed_mesh = obj.data
        obj.data = backup_mesh
        backup_mesh = None
        if failed_mesh.users == 0:
            bpy.data.meshes.remove(failed_mesh)
        return False
    finally:
        if backup_mesh is not None and backup_mesh.users == 0:
            bpy.data.meshes.remove(backup_mesh)
        for item in list(context.selected_objects):
            item.select_set(False)
        for item in original_selection:
            if item and item.name in bpy.data.objects:
                item.select_set(True)
        context.view_layer.objects.active = original_active


def install_smart_reducer(addon):
    """Upgrade the existing Remesh and LOD buttons without adding UI controls."""
    original_reduce = addon._reduce_copy_to_limit
    if getattr(original_reduce, '_fishhwb_v09_smart', False):
        return

    def smart_reduce(obj, target, context):
        is_remesh = obj.name.endswith("_Remesh") or obj.get("fishhwb_generated_job") == "remesh"

        if is_remesh and not _has_deformation(obj):
            _repair_static_mesh(obj.data, fill_holes=True)
            # Open boundaries may be deliberate: never voxel-close them by default.
            check = bmesh.new()
            try:
                check.from_mesh(obj.data)
                closed_but_broken = (
                    not any(edge.is_boundary for edge in check.edges)
                    and any(not edge.is_manifold for edge in check.edges)
                )
            finally:
                check.free()
            if closed_but_broken:
                _voxel_rebuild(obj, context, target)
                _repair_static_mesh(obj.data, fill_holes=False)

        return original_reduce(obj, target, context)

    smart_reduce._fishhwb_v09_smart = True
    addon._reduce_copy_to_limit = smart_reduce


class FISHHWB_OT_clean_mesh(bpy.types.Operator):
    bl_idname = "fishhwb.clean_mesh"
    bl_label = "Clean Mesh"
    bl_description = "Safely clean duplicate, loose and degenerate geometry on static meshes while preserving deformation-sensitive meshes"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and any(obj.type == 'MESH' for obj in context.selected_objects)

    def execute(self, context):
        changed = 0
        unchanged = 0
        unsupported = 0
        failed = 0
        deformation_safe = 0

        for obj in [item for item in context.selected_objects if item.type == 'MESH']:
            if obj.library or obj.data.library or obj.get('fishhwb_protect_detail'):
                unsupported += 1
                continue

            mesh = obj.data
            if _has_deformation(obj):
                mesh.update()
                deformation_safe += 1
                unchanged += 1
                continue

            try:
                if _repair_static_mesh(mesh, fill_holes=False):
                    changed += 1
                else:
                    unchanged += 1
            except Exception:
                failed += 1

        _action_report(
            self,
            context,
            "Safe cleanup completed. Static meshes merge duplicate vertices, dissolve degenerate geometry, remove loose geometry and recalculate normals. "
            f"{deformation_safe} deformation-sensitive mesh(es) were left topology-untouched so shape keys, weights and armature vertex correspondence remain authored.",
            changed=changed,
            unchanged=unchanged,
            unsupported=unsupported,
            failed=failed,
        )
        return {'FINISHED'} if changed or unchanged else {'CANCELLED'}


def _ensure_atlas_uv(obj, context):
    mesh = obj.data
    original_uv = mesh.uv_layers.active.name if mesh.uv_layers.active else None
    # Preserve the sampling UV for input textures when the bake target changes.
    if original_uv:
        for slot in obj.material_slots:
            mat = slot.material
            if not mat or not mat.use_nodes or not mat.node_tree:
                continue
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            for tex in list(nodes):
                if tex.type == 'TEX_IMAGE' and tex.inputs.get('Vector') and not tex.inputs['Vector'].is_linked:
                    uv_node = nodes.new('ShaderNodeUVMap')
                    uv_node.uv_map = original_uv
                    links.new(uv_node.outputs['UV'], tex.inputs['Vector'])
    atlas = mesh.uv_layers.get("AtlasUV")
    if atlas is None:
        atlas = mesh.uv_layers.new(name="AtlasUV")
    mesh.uv_layers.active = atlas
    atlas.active_render = True

    _activate_only(context, obj)
    bpy.ops.object.mode_set(mode='EDIT')
    try:
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(
            angle_limit=math.radians(66.0),
            island_margin=0.02,
            area_weight=0.0,
            correct_aspect=True,
            scale_to_bounds=True,
        )
    finally:
        bpy.ops.object.mode_set(mode='OBJECT')
    return atlas


def _bake_material_atlas(obj, context, size=2048):
    materials = [slot.material for slot in obj.material_slots if slot.material]
    if not materials:
        raise ValueError("The selected mesh has no materials to merge.")

    image = bpy.data.images.new(
        name=obj.name + "_Atlas",
        width=size,
        height=size,
        alpha=True,
        float_buffer=False,
    )
    image.generated_color = (0.0, 0.0, 0.0, 0.0)

    temp_nodes = []
    try:
        for material in materials:
            material.use_nodes = True
            nodes = material.node_tree.nodes
            node = nodes.new("ShaderNodeTexImage")
            node.name = "FISHHWB_TEMP_ATLAS"
            node.label = "Temporary Optimize Your Project bake target"
            node.image = image
            nodes.active = node
            node.select = True
            temp_nodes.append((material, node))

        scene = context.scene
        previous_engine = scene.render.engine
        previous_margin = scene.render.bake.margin
        previous_samples = scene.cycles.samples
        try:
            # Color/texture bakes do not benefit from costly high render samples.
            scene.cycles.samples = min(previous_samples, 16)
            scene.render.engine = 'CYCLES'
            _activate_only(context, obj)
            scene.render.bake.margin = 16
            bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, use_clear=True)
        finally:
            scene.render.bake.margin = previous_margin
            scene.render.engine = previous_engine
            scene.cycles.samples = previous_samples

        atlas_material = bpy.data.materials.new(name=obj.name + "_Atlas")
        atlas_material.use_nodes = True
        nodes = atlas_material.node_tree.nodes
        links = atlas_material.node_tree.links
        bsdf = nodes.get("Principled BSDF")
        tex = nodes.new("ShaderNodeTexImage")
        tex.image = image
        tex.interpolation = 'Linear'
        if bsdf:
            links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
            links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
        obj.data.materials.clear()
        obj.data.materials.append(atlas_material)
        for poly in obj.data.polygons:
            poly.material_index = 0

        image.pack()
        obj["fishhwb_texture_atlas"] = image.name
        obj["fishhwb_texture_atlas_size"] = size
        return image, atlas_material
    finally:
        for material, node in temp_nodes:
            try:
                material.node_tree.nodes.remove(node)
            except Exception:
                pass


class FISHHWB_OT_merge_textures(bpy.types.Operator):
    bl_idname = "fishhwb.merge_textures"
    bl_label = "Merge Textures"
    bl_description = "Create a copy with one packed texture atlas, repaired UVs and one material"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (
            context.mode == 'OBJECT'
            and context.active_object is not None
            and context.active_object.type == 'MESH'
        )

    def execute(self, context):
        source = context.active_object
        if source.library or source.data.library:
            _action_report(self, context, "Linked library meshes require a local copy before texture merging.", unsupported=1)
            return {'CANCELLED'}
        if source.get('fishhwb_protect_detail'):
            _action_report(self, context, "Detail protection enabled. Original and generated texture data were left untouched.", unsupported=1)
            return {'CANCELLED'}

        original_selection = list(context.selected_objects)
        original_active = context.view_layer.objects.active
        output = None
        try:
            output = source.copy()
            output.data = source.data.copy()
            output.name = source.name + "_Atlas"
            output.matrix_world = source.matrix_world.copy()
            context.collection.objects.link(output)

            # Work on private material copies so baking setup never mutates the source.
            for slot in output.material_slots:
                if slot.material:
                    slot.material = slot.material.copy()

            _ensure_atlas_uv(output, context)
            atlas_size = int(getattr(context.scene, "fishhwb_atlas_size", "2048"))
            image, material = _bake_material_atlas(output, context, atlas_size)
            output.data.name = output.name
            output["fishhwb_generated_job"] = "texture_atlas"

            _activate_only(context, output)
            _action_report(
                self,
                context,
                f"Texture merge created {output.name}: packed {atlas_size}x{atlas_size} atlas ({image.name}), one material ({material.name}) and rebuilt AtlasUV. Original preserved.",
                changed=1,
            )
            return {'FINISHED'}
        except Exception as exc:
            if output and output.name in bpy.data.objects:
                mesh = output.data
                bpy.data.objects.remove(output, do_unlink=True)
                if mesh and mesh.users == 0:
                    bpy.data.meshes.remove(mesh)
            for item in list(context.selected_objects):
                item.select_set(False)
            for item in original_selection:
                if item and item.name in bpy.data.objects:
                    item.select_set(True)
            context.view_layer.objects.active = original_active
            _action_report(self, context, "Texture merge failed: " + str(exc), failed=1)
            return {'CANCELLED'}


def _draw_merge_button(self, context):
    layout = self.layout
    box = layout.box()
    if hasattr(context.scene, "fishhwb_atlas_size"):
        box.prop(context.scene, "fishhwb_atlas_size", text="Atlas Resolution")
    row = box.row()
    row.scale_y = 1.35
    row.operator("fishhwb.merge_textures", text="MERGE TEXTURES", icon="TEXTURE")


def install_remesh_guard(addon):
    original_execute = addon.FISHHWB_OT_one_click_remesh.execute
    if getattr(original_execute, '_fishhwb_v08_guard', False):
        return

    def guarded_execute(self, context):
        source = addon._resolve_source(context.active_object, 'remesh') if context.active_object else None
        if not source or source.type != 'MESH':
            return original_execute(self, context)

        source_uvs = {layer.name for layer in source.data.uv_layers}
        source_materials = tuple(slot.material.name_full if slot.material else '' for slot in source.material_slots)
        source_groups = {group.name for group in source.vertex_groups}
        source_shapes = set(source.data.shape_keys.key_blocks.keys()) if source.data.shape_keys else set()

        result = original_execute(self, context)
        output = context.active_object
        if 'FINISHED' not in result or not output or output is source or output.type != 'MESH':
            return result

        output_uvs = {layer.name for layer in output.data.uv_layers}
        output_materials = tuple(slot.material.name_full if slot.material else '' for slot in output.material_slots)
        output_groups = {group.name for group in output.vertex_groups}
        output_shapes = set(output.data.shape_keys.key_blocks.keys()) if output.data.shape_keys else set()

        problems = []
        if not source_uvs.issubset(output_uvs):
            problems.append('UV maps')
        if source_materials and output_materials != source_materials:
            problems.append('material slots')
        if source_groups and not source_groups.issubset(output_groups):
            problems.append('vertex groups')
        if source_shapes and not source_shapes.issubset(output_shapes):
            problems.append('shape keys')

        if problems:
            try:
                addon._remove_object_and_mesh(output)
                addon._select_only(context, source)
            except Exception:
                pass
            _action_report(
                self,
                context,
                "Remesh output rejected because preservation validation failed for: "
                + ", ".join(problems)
                + ". Original object kept unchanged.",
                failed=1,
            )
            return {'CANCELLED'}

        context.scene.fishhwb_last_result += (
            " Smart repair/rebuild completed and preservation validation passed for "
            "UVs, materials, vertex groups and shape keys."
        )
        return result

    guarded_execute._fishhwb_v08_guard = True
    addon.FISHHWB_OT_one_click_remesh.execute = guarded_execute


classes = (
    FISHHWB_OT_clean_mesh,
    FISHHWB_OT_merge_textures,
)


def register(addon):
    install_smart_reducer(addon)
    install_remesh_guard(addon)
    for cls in classes:
        bpy.utils.register_class(cls)
    try:
        addon.FISHHWB_PT_optimizer.append(_draw_merge_button)
    except Exception:
        pass


def unregister():
    try:
        for panel in (getattr(bpy.types, "FISHHWB_PT_optimizer", None),):
            if panel:
                panel.remove(_draw_merge_button)
    except Exception:
        pass
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
