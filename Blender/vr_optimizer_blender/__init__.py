# SPDX-License-Identifier: GPL-3.0-or-later
bl_info = {
    "name": "Optimize Your Project for Blender",
    "author": "FISHHWB | Ded Zed",
    "version": (0, 7, 55),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > FISHHWB",
    "description": "Remesh with deformation transfer and static-mesh LOD tools",
    "category": "Mesh",
}

from pathlib import Path
import hashlib
import json
import struct
import uuid
from . import deform_transfer

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
    'reset_history': {
        'EN': 'Reset history', 'JA': '履歴をリセット',
        'ZH': '重置历史', 'KO': '기록 초기화',
    },
    'protect_detail': {
        'EN': 'Protect detail', 'JA': 'ディテールを保護',
        'ZH': '保护细节', 'KO': '디테일 보호',
    },
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
        'EN': 'Select a mesh for Remesh; static meshes for LOD.',
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
        'EN': 'Reduce triangles while retaining the surface, UVs and materials.',
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


def _action_report(operator, context, detail, changed=0, unsupported=0, failed=0, unchanged=0):
    parts = [
        f"Changed: {changed}",
        f"Unchanged: {unchanged}",
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
    keys = mesh.shape_keys if mesh else None
    owned_action = keys.animation_data.action if keys and keys.animation_data and keys.animation_data.action and keys.animation_data.action.get("fishhwb_owned_transfer") else None
    bpy.data.objects.remove(obj, do_unlink=True)
    if mesh and mesh.users == 0:
        bpy.data.meshes.remove(mesh)
    if owned_action and owned_action.users == 0:
        bpy.data.actions.remove(owned_action)


def _static_mesh_reason(source, allow_deformation=False):
    if not source or source.type != 'MESH' or not source.data:
        return "Select a mesh object."
    if source.fishhwb_protect_detail:
        return "Detail protection enabled. Original geometry will not be optimized."
    if source.library or source.data.library:
        return 'Linked library meshes require a local copy before optimization.'
    if allow_deformation:
        reason = deform_transfer.unsupported_reason(source)
        if reason:
            return reason
    else:
        if source.data.shape_keys or source.vertex_groups or any(m.type == 'ARMATURE' for m in source.modifiers):
            return 'LOD remains static-mesh only. Remesh supports guarded deformation transfer.'
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

    policy = 'lod-v0755:' + str(apply_modifiers)
    cached = _cached_outputs(source, context, 'lod', policy)
    source['fishhwb_lod_reused'] = bool(cached)
    if cached:
        return cached[0].users_collection[0], cached
    collection = bpy.data.collections.new(source.name + "_LODs")
    context.scene.collection.children.link(collection)
    collection["fishhwb_generated_lod"] = True
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

        _remember_outputs(source, context, "lod", policy, created)
        return collection, created
    except Exception:
        for obj in list(created):
            _remove_object_and_mesh(obj)
        if collection.name in bpy.data.collections:
            bpy.data.collections.remove(collection)
        raise


def _object_signature(obj, context):
    mesh = obj.data.copy() if deform_transfer.has_deformation(obj) else _evaluated_mesh_copy(obj, context)
    try:
        digest = hashlib.sha256()
        digest.update(repr(tuple(tuple(row) for row in obj.matrix_world)).encode())
        for vertex in mesh.vertices:
            digest.update(struct.pack('<3f', *vertex.co))
        for edge in mesh.edges:
            digest.update(struct.pack('<2I', *edge.vertices))
        for face in mesh.polygons:
            digest.update(repr((tuple(face.vertices), face.material_index, face.use_smooth)).encode())
        for layer in mesh.uv_layers:
            digest.update(layer.name.encode())
            for item in layer.data:
                digest.update(struct.pack('<2f', *item.uv))
        for attribute in mesh.attributes:
            if attribute.name.startswith('.') or attribute.data_type == 'STRING':
                continue
            digest.update(repr((attribute.name, attribute.domain, attribute.data_type)).encode())
            for item in attribute.data:
                for field in ('value', 'vector', 'color', 'uv'):
                    if hasattr(item, field):
                        value = getattr(item, field)
                        digest.update(repr(tuple(value) if hasattr(value, '__len__') else value).encode())
                        break
        digest.update(repr(tuple(material.name_full if material else '' for material in mesh.materials)).encode())
        digest.update(deform_transfer.signature(obj))
        return digest.hexdigest()
    finally:
        bpy.data.meshes.remove(mesh)


def _resolve_source(obj, job):
    if not obj or obj.get('fishhwb_generated_job') != job:
        return obj
    output_id = obj.get('fishhwb_output_id')
    if output_id:
        for candidate in bpy.data.objects:
            raw = candidate.get('fishhwb_' + job + '_history')
            if not raw:
                continue
            try:
                record = json.loads(raw)
                if record.get('owner') == candidate.name_full and any(item.get('id') == output_id for item in record['outputs']):
                    return candidate
            except (ValueError, KeyError, TypeError):
                continue
    return obj


def _cached_outputs(source, context, job, policy):
    if source.get('fishhwb_generated_job') == job:
        raise ValueError("Select the original source for this action; this object is already its generated output.")
    raw = source.get('fishhwb_' + job + '_history')
    if not raw:
        return None
    try:
        record = json.loads(raw)
    except (ValueError, TypeError):
        return None
    if record.get('owner') != source.name_full:
        return None
    outputs = [_history_object(item) for item in record['outputs']]
    for obj, item in zip(outputs, record['outputs']):
        if obj and obj.fishhwb_protect_detail:
            raise ValueError('Generated output is protected; preserved. Reset source history to create a fresh set.')
        if obj and _object_signature(obj, context) != item['signature']:
            raise ValueError("Generated output has manual edits; preserved. Clear source history to explicitly create new outputs.")
    if all(outputs) and record['source'] == _object_signature(source, context) and record['policy'] == policy:
        return outputs
    return None


def _history_object(item):
    if not item.get('id'):
        return None
    return next((obj for obj in bpy.data.objects if obj.get('fishhwb_output_id') == item.get('id')), None)


def _remember_outputs(source, context, job, policy, outputs):
    key = 'fishhwb_' + job + '_history'
    raw = source.get(key)
    try:
        previous = json.loads(raw) if raw else None
    except (ValueError, TypeError):
        previous = None
    if previous and previous.get('owner') != source.name_full:
        previous = None
    for output in outputs:
        for old_job in ('remesh', 'lod'):
            old_key = 'fishhwb_' + old_job + '_history'
            if old_key in output:
                del output[old_key]
        output['fishhwb_generated_job'] = job
        output['fishhwb_output_id'] = uuid.uuid4().hex
    record = json.dumps({
        'owner': source.name_full, 'source': _object_signature(source, context), 'policy': policy,
        'outputs': [{'id': obj['fishhwb_output_id'], 'signature': _object_signature(obj, context)} for obj in outputs],
    })
    # Replace only verified, untouched generated outputs after the replacement has succeeded.
    if previous:
        for item in previous['outputs']:
            old = _history_object(item)
            if old and old not in outputs and not old.fishhwb_protect_detail and _object_signature(old, context) == item['signature']:
                collections = list(old.users_collection)
                _remove_object_and_mesh(old)
                for collection in collections:
                    if collection.get('fishhwb_generated_lod') and not collection.objects:
                        bpy.data.collections.remove(collection)
    source[key] = record


class FISHHWB_OT_reset_history(bpy.types.Operator):
    bl_idname = "fishhwb.reset_optimization_history"
    bl_label = "Reset Optimization History"
    bl_description = "Preserve current outputs and allow the original source to create a fresh set next time"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        source = context.active_object
        if not source or source.type != 'MESH':
            return {'CANCELLED'}
        for job in ('remesh', 'lod'):
            key = 'fishhwb_' + job + '_history'
            if key in source:
                del source[key]
        _action_report(self, context, "History reset. Existing outputs preserved; the next action creates fresh copies.")
        return {'FINISHED'}



class FISHHWB_OT_one_click_remesh(bpy.types.Operator):
    bl_idname = "fishhwb.one_click_remesh"
    bl_label = "One-Click Remesh"
    bl_description = "Create a surface-preserving reduced copy with UVs and materials"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (
            context.mode == 'OBJECT'
            and context.active_object is not None
            and context.active_object.type == 'MESH'
        )

    def execute(self, context):
        source = _resolve_source(context.active_object, 'remesh')
        reason = _static_mesh_reason(source, allow_deformation=True)
        if reason:
            _action_report(self, context, reason, unsupported=1)
            return {'CANCELLED'}

        original_selection = list(context.selected_objects)
        original_active = context.view_layer.objects.active
        copy = None

        try:
            policy = 'remesh-surface-v0755:' + str(context.scene.fishhwb_triangle_target)
            try:
                cached = _cached_outputs(source, context, 'remesh', policy)
            except ValueError as exc:
                _action_report(self, context, str(exc), unsupported=1)
                return {'CANCELLED'}
            if cached:
                _select_only(context, cached[0])
                _action_report(self, context, "Unchanged source/settings: existing remesh reused.", unchanged=1)
                return {'FINISHED'}
            copy = _copy_mesh_object(source, context, "_Remesh")
            transfer_deformation = deform_transfer.has_deformation(source)
            if transfer_deformation:
                deform_transfer.prepare_neutral_copy(source, copy, context)
            before = triangle_count(copy.data)

            # Voxel reconstruction discards UV loops and merges nearby clothing,
            # hair and facial surfaces. Retain the existing surface instead.
            # Evaluate existing static modifiers once, even below the budget.
            if copy.modifiers:
                result = _evaluated_mesh_copy(copy, context)
                old_mesh = copy.data
                copy.modifiers.clear()
                copy.data = result
                if old_mesh.users == 0:
                    bpy.data.meshes.remove(old_mesh)
            uv_names = {layer.name for layer in copy.data.uv_layers}
            after = _reduce_copy_to_limit(copy, context.scene.fishhwb_triangle_target, context)
            if after < 1:
                raise ValueError("The optimized surface contains no triangles.")
            if not uv_names.issubset({layer.name for layer in copy.data.uv_layers}):
                raise ValueError("Surface reduction lost a UV layer; output discarded.")
            copy.data.name = copy.name
            transfer_detail = ""
            if transfer_deformation:
                groups, shapes, distance = deform_transfer.transfer(source, copy)
                transfer_detail = f" Transferred {groups} weight groups, {shapes} relative blendshapes and armature bindings; max surface projection distance {distance:.5g} local units. Test deformation before replacing the source."
            _remember_outputs(source, context, "remesh", policy, [copy])
            _select_only(context, copy)
            _action_report(
                self,
                context,
                f"Surface-preserving copy created: {before:,} -> {after:,} triangles. UVs and material assignments retained. Original object preserved." + transfer_detail,
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
        source = _resolve_source(context.active_object, 'lod')
        original_selection = list(context.selected_objects)
        original_active = context.view_layer.objects.active

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
                f"LOD set from {base:,} triangles: LOD1 {lod1:,}, LOD2 {lod2:,}. Original object preserved.",
                changed=0 if source.get("fishhwb_lod_reused") else 1,
                unchanged=1 if source.get("fishhwb_lod_reused") else 0,
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
        sources = list(dict.fromkeys(_resolve_source(obj, 'lod') for obj in context.selected_objects if obj.type == 'MESH'))
        original_selection = list(context.selected_objects)
        original_active = context.view_layer.objects.active
        outputs = []
        changed = 0
        unchanged = 0
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
                if source.get("fishhwb_lod_reused"):
                    unchanged += 1
                else:
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
            f"LOD sets: {changed} created, {unchanged} reused across {len(sources)} sources. Originals preserved.",
            changed=changed,
            unchanged=unchanged,
            unsupported=unsupported,
            failed=failed,
        )
        return {'FINISHED'} if changed or unchanged else {'CANCELLED'}


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
            selected.prop(obj, 'fishhwb_protect_detail', text=tr(context, 'protect_detail'))
            if obj.get('fishhwb_remesh_history') or obj.get('fishhwb_lod_history'):
                selected.operator('fishhwb.reset_optimization_history', text=tr(context, 'reset_history'), icon='FILE_REFRESH')
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
    FISHHWB_OT_reset_history,
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

    bpy.types.Object.fishhwb_protect_detail = BoolProperty(
        name="Protect detail", default=False,
        description="Skip this object's Remesh and LOD actions to preserve important geometry",
    )
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

    if hasattr(bpy.types.Object, "fishhwb_protect_detail"):
        del bpy.types.Object.fishhwb_protect_detail
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
