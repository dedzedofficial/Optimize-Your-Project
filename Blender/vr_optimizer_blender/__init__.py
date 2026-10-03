# SPDX-License-Identifier: GPL-3.0-or-later
bl_info = {
    "name": "Optimize Your Project for Blender",
    "author": "FISHHWB | Ded Zed",
    "version": (0, 7, 55),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > FISHHWB",
    "description": "Focused one-click Remesh and LOD tools for static Blender meshes",
    "category": "Mesh",
}

from pathlib import Path

import bpy
import bpy.utils.previews
from bpy.props import BoolProperty, EnumProperty, StringProperty, IntProperty


_brand_preview = None

LANGUAGE_ITEMS = (
    ('EN', 'English', 'English'),
    ('JA', '日本語', 'Japanese'),
    ('ZH', '简体中文', 'Chinese (Simplified)'),
    ('KO', '한국어', 'Korean'),
)

_TRANSLATIONS = {
    'triangle_target': {
        'EN': 'Triangle target', 'JA': '三角形の上限',
        'ZH': '三角面目标', 'KO': '삼각형 목표',
    },
    'language': {
        'EN': 'Language',
        'JA': '言語',
        'ZH': '语言',
        'KO': '언어',
    },
    'title': {
        'EN': 'OPTIMIZE YOUR PROJECT',
        'JA': 'プロジェクトを最適化',
        'ZH': '优化你的项目',
        'KO': '프로젝트 최적화',
    },
    'subtitle': {
        'EN': 'Blender v0.7.55: Remesh + LOD only',
        'JA': 'Blender v0.7.55: リメッシュ + LOD のみ',
        'ZH': 'Blender v0.7.55：仅重网格 + LOD',
        'KO': 'Blender v0.7.55: 리메시 + LOD 전용',
    },
    'selection': {
        'EN': 'CURRENT SELECTION',
        'JA': '現在の選択',
        'ZH': '当前选择',
        'KO': '현재 선택',
    },
    'select_mesh': {
        'EN': 'Select one or more static mesh objects.',
        'JA': '1つ以上の静的メッシュを選択してください。',
        'ZH': '请选择一个或多个静态网格对象。',
        'KO': '하나 이상의 정적 메시 오브젝트를 선택하세요.',
    },
    'remesh_title': {
        'EN': 'REMESH',
        'JA': 'リメッシュ',
        'ZH': '重网格',
        'KO': '리메시',
    },
    'remesh_desc': {
        'EN': 'Create a separate automatically remeshed copy.',
        'JA': '自動リメッシュした別コピーを作成します。',
        'ZH': '创建一个单独的自动重网格副本。',
        'KO': '자동 리메시된 별도 복사본을 만듭니다.',
    },
    'remesh': {
        'EN': 'ONE-CLICK REMESH',
        'JA': 'ワンクリックリメッシュ',
        'ZH': '一键重网格',
        'KO': '원클릭 리메시',
    },
    'lod_title': {
        'EN': 'LOD GENERATION',
        'JA': 'LOD 生成',
        'ZH': 'LOD 生成',
        'KO': 'LOD 생성',
    },
    'lod_desc': {
        'EN': 'Create LOD0, LOD1 and LOD2 copies while preserving the source.',
        'JA': '元データを保持したまま LOD0、LOD1、LOD2 を作成します。',
        'ZH': '保留源对象并创建 LOD0、LOD1 和 LOD2 副本。',
        'KO': '원본을 유지하면서 LOD0, LOD1, LOD2 복사본을 만듭니다.',
    },
    'apply_modifiers': {
        'EN': 'Apply Existing Modifiers',
        'JA': '既存モディファイアを適用',
        'ZH': '应用现有修改器',
        'KO': '기존 모디파이어 적용',
    },
    'create_lods': {
        'EN': 'CREATE LOD0 / LOD1 / LOD2',
        'JA': 'LOD0 / LOD1 / LOD2 を作成',
        'ZH': '创建 LOD0 / LOD1 / LOD2',
        'KO': 'LOD0 / LOD1 / LOD2 생성',
    },
    'batch_lods': {
        'EN': 'CREATE LODS FOR SELECTION',
        'JA': '選択メッシュの LOD を作成',
        'ZH': '为所选网格创建 LOD',
        'KO': '선택 메시 LOD 생성',
    },
    'last_result': {
        'EN': 'LAST RESULT',
        'JA': '最後の結果',
        'ZH': '上次结果',
        'KO': '마지막 결과',
    },
}


def tr(context, key):
    lang = getattr(context.scene, 'fishhwb_language', 'EN') if context and context.scene else 'EN'
    values = _TRANSLATIONS.get(key, {})
    return values.get(lang, values.get('EN', key))


def triangle_count(mesh):
    mesh.calc_loop_triangles()
    return len(mesh.loop_triangles)


def _action_report(operator, context, detail, changed=0, unsupported=0, failed=0):
    parts = [
        f"Changed: {changed}",
        f"Unsupported: {unsupported}",
        f"Failed: {failed}",
    ]
    message = " | ".join(parts) + ". " + detail
    context.scene.fishhwb_last_result = message
    level = {'ERROR'} if failed else ({'WARNING'} if unsupported and not changed else {'INFO'})
    operator.report(level, message)


def _select_only(context, obj):
    for item in list(context.selected_objects):
        item.select_set(False)
    obj.select_set(True)
    context.view_layer.objects.active = obj


def _copy_mesh_object(source, context, suffix):
    copy = source.copy()
    copy.data = source.data.copy()
    copy.name = source.name + suffix
    context.collection.objects.link(copy)
    copy.matrix_world = source.matrix_world.copy()
    return copy


def _remove_object_and_mesh(obj):
    if obj is None or obj.name not in bpy.data.objects:
        return
    mesh = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    if mesh and mesh.users == 0:
        bpy.data.meshes.remove(mesh)


def _static_mesh_reason(source):
    if not source or source.type != 'MESH' or not source.data:
        return "Select a mesh object."
    if source.data.shape_keys:
        return "Shape keys are not supported because Remesh and LOD generation change topology."
    if source.vertex_groups:
        return "Vertex-group meshes are not supported because topology reduction can invalidate weights."
    if any(modifier.type == 'ARMATURE' for modifier in source.modifiers):
        return "Armature-driven meshes are not supported. Use a separate static copy."
    if triangle_count(source.data) < 1:
        return "The selected mesh has no triangles."
    return None


def _evaluated_mesh_copy(obj, context):
    depsgraph = context.evaluated_depsgraph_get()
    context.view_layer.update()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(
        evaluated,
        preserve_all_data_layers=True,
        depsgraph=depsgraph,
    )
    if mesh is None:
        raise RuntimeError("Blender could not evaluate the mesh.")
    return mesh


def _reduce_copy_to_limit(obj, target, context):
    before = triangle_count(obj.data)
    if before <= target:
        return before

    modifier = obj.modifiers.new("LOD Triangle Limit", 'DECIMATE')
    modifier.decimate_type = 'COLLAPSE'
    modifier.use_collapse_triangulate = True

    depsgraph = context.evaluated_depsgraph_get()
    low = 0.0
    high = 1.0
    best_ratio = None
    best_count = -1

    for _ in range(24):
        ratio = (low + high) * 0.5
        modifier.ratio = ratio
        context.view_layer.update()

        evaluated = obj.evaluated_get(depsgraph)
        evaluated_mesh = evaluated.to_mesh()
        try:
            count = triangle_count(evaluated_mesh)
        finally:
            evaluated.to_mesh_clear()

        if count <= target:
            if count > best_count:
                best_ratio = ratio
                best_count = count
            low = ratio
        else:
            high = ratio

    if best_ratio is None or best_count < 1:
        obj.modifiers.remove(modifier)
        raise ValueError("Unable to create a usable LOD within the triangle target.")

    modifier.ratio = best_ratio
    context.view_layer.update()
    result = _evaluated_mesh_copy(obj, context)
    count = triangle_count(result)

    if count < 1 or count > target:
        bpy.data.meshes.remove(result)
        obj.modifiers.remove(modifier)
        raise ValueError("The generated LOD did not meet its triangle target.")

    old_mesh = obj.data
    obj.modifiers.remove(modifier)
    obj.data = result
    if old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)

    return count


def _create_lod_set(source, context, apply_modifiers):
    reason = _static_mesh_reason(source)
    if reason:
        raise ValueError(reason)
    if source.modifiers and not apply_modifiers:
        raise ValueError("Enable Apply Existing Modifiers or use a mesh with no modifiers.")

    collection = bpy.data.collections.new(source.name + "_LODs")
    context.scene.collection.children.link(collection)
    created = []

    try:
        lod0 = source.copy()
        lod0.data = source.data.copy()
        lod0.name = source.name + "_LOD0"
        lod0.matrix_world = source.matrix_world.copy()
        collection.objects.link(lod0)
        created.append(lod0)

        if lod0.modifiers:
            evaluated_mesh = _evaluated_mesh_copy(lod0, context)
            old_mesh = lod0.data
            lod0.modifiers.clear()
            lod0.data = evaluated_mesh
            if old_mesh.users == 0:
                bpy.data.meshes.remove(old_mesh)

        base_count = triangle_count(lod0.data)
        if base_count < 1:
            raise ValueError("The selected mesh has no usable triangles.")

        lod0['fishhwb_lod_level'] = 0
        lod0['fishhwb_triangle_target'] = base_count

        for level, fraction in ((1, 0.66), (2, 0.33)):
            copy = lod0.copy()
            copy.data = lod0.data.copy()
            copy.name = source.name + f"_LOD{level}"
            copy.matrix_world = source.matrix_world.copy()
            collection.objects.link(copy)
            created.append(copy)

            target = max(1, int(base_count * fraction))
            actual = _reduce_copy_to_limit(copy, target, context)
            copy['fishhwb_lod_level'] = level
            copy['fishhwb_triangle_target'] = target
            copy['fishhwb_triangle_result'] = actual
            copy.hide_set(True)

        return collection, created
    except Exception:
        for obj in list(created):
            _remove_object_and_mesh(obj)
        if collection.name in bpy.data.collections:
            bpy.data.collections.remove(collection)
        raise


class FISHHWB_OT_one_click_remesh(bpy.types.Operator):
    bl_idname = "fishhwb.one_click_remesh"
    bl_label = "One-Click Remesh"
    bl_description = "Create a separate remeshed copy using an automatic voxel size"
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
        reason = _static_mesh_reason(source)
        if reason:
            _action_report(self, context, reason, unsupported=1)
            return {'CANCELLED'}

        original_selection = list(context.selected_objects)
        original_active = source
        copy = None

        try:
            copy = _copy_mesh_object(source, context, "_Remesh")
            before = triangle_count(copy.data)

            max_dimension = max(abs(value) for value in copy.dimensions)
            if max_dimension <= 0:
                raise ValueError("The selected mesh has no usable size.")

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

            result = _evaluated_mesh_copy(copy, context)
            after = triangle_count(result)
            if after < 1:
                bpy.data.meshes.remove(result)
                raise ValueError("Remesh produced no triangles.")

            old_mesh = copy.data
            copy.modifiers.clear()
            copy.data = result
            copy.data.name = copy.name
            if old_mesh.users == 0:
                bpy.data.meshes.remove(old_mesh)

            after = _reduce_copy_to_limit(copy, context.scene.fishhwb_triangle_target, context)
            _select_only(context, copy)
            _action_report(
                self,
                context,
                f"Remeshed copy created: {before:,} -> {after:,} triangles. Original object preserved.",
                changed=1,
            )
            return {'FINISHED'}
        except Exception as exc:
            _remove_object_and_mesh(copy)
            for item in list(context.selected_objects):
                item.select_set(False)
            for item in original_selection:
                if item and item.name in bpy.data.objects:
                    item.select_set(True)
            context.view_layer.objects.active = original_active
            _action_report(self, context, "Remesh failed: " + str(exc), failed=1)
            return {'CANCELLED'}


class FISHHWB_OT_create_lods(bpy.types.Operator):
    bl_idname = "fishhwb.create_lods"
    bl_label = "Create LOD0 / LOD1 / LOD2"
    bl_description = "Create LOD copies for the active static mesh while preserving the original"
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
        original_selection = list(context.selected_objects)
        original_active = source

        try:
            _, created = _create_lod_set(
                source,
                context,
                context.scene.fishhwb_apply_modifiers,
            )
            _select_only(context, created[0])
            base = triangle_count(created[0].data)
            lod1 = triangle_count(created[1].data)
            lod2 = triangle_count(created[2].data)
            _action_report(
                self,
                context,
                f"LOD set created from {base:,} triangles: LOD1 {lod1:,}, LOD2 {lod2:,}. Original object preserved.",
                changed=1,
            )
            return {'FINISHED'}
        except ValueError as exc:
            for item in list(context.selected_objects):
                item.select_set(False)
            for item in original_selection:
                if item and item.name in bpy.data.objects:
                    item.select_set(True)
            context.view_layer.objects.active = original_active
            _action_report(self, context, str(exc), unsupported=1)
            return {'CANCELLED'}
        except Exception as exc:
            for item in list(context.selected_objects):
                item.select_set(False)
            for item in original_selection:
                if item and item.name in bpy.data.objects:
                    item.select_set(True)
            context.view_layer.objects.active = original_active
            _action_report(self, context, "LOD generation failed: " + str(exc), failed=1)
            return {'CANCELLED'}


class FISHHWB_OT_create_lods_selected(bpy.types.Operator):
    bl_idname = "fishhwb.create_lods_selected"
    bl_label = "Create LODs for Selection"
    bl_description = "Create LOD0, LOD1 and LOD2 for each supported selected static mesh"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (
            context.mode == 'OBJECT'
            and any(obj.type == 'MESH' for obj in context.selected_objects)
        )

    def execute(self, context):
        sources = [obj for obj in context.selected_objects if obj.type == 'MESH']
        original_selection = list(context.selected_objects)
        original_active = context.view_layer.objects.active
        outputs = []
        changed = 0
        unsupported = 0
        failed = 0

        for source in sources:
            try:
                _, created = _create_lod_set(
                    source,
                    context,
                    context.scene.fishhwb_apply_modifiers,
                )
                outputs.append(created[0])
                changed += 1
            except ValueError:
                unsupported += 1
            except Exception:
                failed += 1

        for item in list(context.selected_objects):
            item.select_set(False)

        if outputs:
            for item in outputs:
                if item and item.name in bpy.data.objects:
                    item.select_set(True)
            context.view_layer.objects.active = outputs[0]
        else:
            for item in original_selection:
                if item and item.name in bpy.data.objects:
                    item.select_set(True)
            context.view_layer.objects.active = original_active

        _action_report(
            self,
            context,
            f"Created LOD sets for {changed} of {len(sources)} selected meshes. Originals preserved.",
            changed=changed,
            unsupported=unsupported,
            failed=failed,
        )
        return {'FINISHED'} if changed else {'CANCELLED'}


class FISHHWB_PT_optimizer(bpy.types.Panel):
    bl_label = "Optimize Your Project"
    bl_idname = "FISHHWB_PT_optimizer"
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
        brand.label(text=tr(context, 'title'))
        brand.label(text=tr(context, 'subtitle'))
        brand.prop(context.scene, 'fishhwb_language', text=tr(context, 'language'))

        obj = context.active_object
        selected_meshes = [item for item in context.selected_objects if item.type == 'MESH']

        selected = layout.box()
        selected.label(text=tr(context, 'selection'), icon='MESH_DATA')
        if obj and obj.type == 'MESH':
            selected.label(text=obj.name)
            stats = selected.row(align=True)
            stats.label(text=f"Triangles: {triangle_count(obj.data):,}")
            stats.label(text=f"Vertices: {len(obj.data.vertices):,}")
            if len(selected_meshes) > 1:
                selected.label(text=f"{len(selected_meshes)} mesh objects selected")
        else:
            selected.label(text=tr(context, 'select_mesh'), icon='INFO')

        remesh = layout.box()
        remesh.label(text=tr(context, 'remesh_title'), icon='MOD_REMESH')
        remesh.label(text=tr(context, 'remesh_desc'))
        remesh.prop(context.scene, 'fishhwb_triangle_target', text=tr(context, 'triangle_target'), slider=True)
        row = remesh.row()
        row.scale_y = 1.4
        row.operator('fishhwb.one_click_remesh', text=tr(context, 'remesh'), icon='MOD_REMESH')

        lod = layout.box()
        lod.label(text=tr(context, 'lod_title'), icon='MOD_DECIM')
        lod.label(text=tr(context, 'lod_desc'))
        lod.prop(context.scene, 'fishhwb_apply_modifiers', text=tr(context, 'apply_modifiers'))

        active_lod = lod.row()
        active_lod.scale_y = 1.35
        active_lod.operator(
            'fishhwb.create_lods_selected' if len(selected_meshes) > 1 else 'fishhwb.create_lods',
            text=tr(context, 'create_lods'), icon='MOD_DECIM',
        )

        if context.scene.fishhwb_last_result:
            result = layout.box()
            result.label(text=tr(context, 'last_result'), icon='INFO')
            import textwrap
            width = max(
                24,
                int(context.region.width / (7 * context.preferences.system.ui_scale)),
            )
            for line in context.scene.fishhwb_last_result.splitlines():
                for wrapped in textwrap.wrap(line, width=width):
                    result.label(text=wrapped)


classes = (
    FISHHWB_OT_one_click_remesh,
    FISHHWB_OT_create_lods,
    FISHHWB_OT_create_lods_selected,
    FISHHWB_PT_optimizer,
)


def register():
    global _brand_preview
    _brand_preview = bpy.utils.previews.new()
    _brand_preview.load(
        "logo",
        str(Path(__file__).with_name("optimize-your-project-logo.png")),
        'IMAGE',
    )

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.fishhwb_triangle_target = IntProperty(
        name="Triangle target", default=10000, min=4, max=10000000,
        soft_min=100, soft_max=100000,
        description="Maximum triangle budget for the remeshed copy; preserves the original",
    )
    bpy.types.Scene.fishhwb_last_result = StringProperty(options={'SKIP_SAVE'})
    bpy.types.Scene.fishhwb_language = EnumProperty(
        name="Language",
        items=LANGUAGE_ITEMS,
        default='EN',
        description="Interface language for Optimize Your Project",
    )
    bpy.types.Scene.fishhwb_apply_modifiers = BoolProperty(
        name="Apply Existing Modifiers",
        default=True,
        description="Apply existing non-armature modifiers to generated LOD0 before making LOD1 and LOD2",
    )


def unregister():
    global _brand_preview

    if hasattr(bpy.types.Scene, "fishhwb_triangle_target"):
        del bpy.types.Scene.fishhwb_triangle_target
    if hasattr(bpy.types.Scene, "fishhwb_last_result"):
        del bpy.types.Scene.fishhwb_last_result
    if hasattr(bpy.types.Scene, "fishhwb_language"):
        del bpy.types.Scene.fishhwb_language
    if hasattr(bpy.types.Scene, "fishhwb_apply_modifiers"):
        del bpy.types.Scene.fishhwb_apply_modifiers

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    if _brand_preview is not None:
        bpy.utils.previews.remove(_brand_preview)
        _brand_preview = None


if __name__ == '__main__':
    register()
