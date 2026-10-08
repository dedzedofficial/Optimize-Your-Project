# SPDX-License-Identifier: GPL-3.0-or-later
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
                # Do not round-trip deformation-sensitive meshes through BMesh. Even a
                # topology-preserving BMesh write can disturb authored correspondence.
                mesh.update()
                deformation_safe += 1
                unchanged += 1
                continue

            before = (len(mesh.vertices), len(mesh.edges), len(mesh.polygons))
            bm = None
            try:
                bm = bmesh.new()
                bm.from_mesh(mesh)
                bm.verts.ensure_lookup_table()
                bm.edges.ensure_lookup_table()
                bm.faces.ensure_lookup_table()

                if bm.verts:
                    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.00001)
                if bm.edges:
                    bmesh.ops.dissolve_degenerate(bm, dist=0.00001, edges=list(bm.edges))
                loose = [v for v in bm.verts if not v.link_edges and not v.link_faces]
                if loose:
                    bmesh.ops.delete(bm, geom=loose, context='VERTS')
                if bm.faces:
                    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))

                bm.to_mesh(mesh)
                mesh.validate(verbose=False, clean_customdata=False)
                mesh.update()

                after = (len(mesh.vertices), len(mesh.edges), len(mesh.polygons))
                if after != before:
                    changed += 1
                else:
                    unchanged += 1
            except Exception:
                failed += 1
            finally:
                if bm is not None:
                    bm.free()

        _action_report(
            self,
            context,
            "Safe cleanup completed. Static meshes can merge duplicate vertices, dissolve degenerate geometry, remove loose vertices and recalculate normals. "
            f"{deformation_safe} deformation-sensitive mesh(es) were left topology-untouched so shape keys, weights and armature vertex correspondence remain authored.",
            changed=changed,
            unchanged=unchanged,
            unsupported=unsupported,
            failed=failed,
        )
        return {'FINISHED'} if changed or unchanged else {'CANCELLED'}


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

        context.scene.fishhwb_last_result += " v0.8 preservation validation passed for UVs, materials, vertex groups and shape keys."
        return result

    guarded_execute._fishhwb_v08_guard = True
    addon.FISHHWB_OT_one_click_remesh.execute = guarded_execute


classes = (FISHHWB_OT_clean_mesh,)


def register(addon):
    install_remesh_guard(addon)
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
