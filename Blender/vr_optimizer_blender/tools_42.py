# SPDX-License-Identifier: GPL-3.0-or-later
"""Blender 4.2+ focused optimization actions."""

import hashlib
import math
import struct

import bpy

MIN_BLENDER_VERSION = (4, 2, 0)
LIGHTMAP_UV_NAME = "LightmapUV"

_TRANSLATIONS = {
    "panel": {
        "EN": "BLENDER 4.2+ TOOLS",
        "JA": "BLENDER 4.2+ ツール",
        "ZH": "BLENDER 4.2+ 工具",
        "KO": "BLENDER 4.2+ 도구",
    },
    "desc": {
        "EN": "Static-mesh jobs for modern Blender projects.",
        "JA": "最新 Blender 向けの静的メッシュ最適化です。",
        "ZH": "面向现代 Blender 项目的静态网格优化。",
        "KO": "최신 Blender 프로젝트용 정적 메시 최적화입니다.",
    },
    "lightmap": {
        "EN": "GENERATE LIGHTMAP UV",
        "JA": "ライトマップ UV を生成",
        "ZH": "生成光照贴图 UV",
        "KO": "라이트맵 UV 생성",
    },
    "lightmap_help": {
        "EN": "Adds a protected second UV channel without changing geometry.",
        "JA": "ジオメトリを変更せず、2 番目の UV チャンネルを追加します。",
        "ZH": "不修改几何体，添加第二个 UV 通道。",
        "KO": "지오메트리를 변경하지 않고 두 번째 UV 채널을 추가합니다.",
    },
    "link": {
        "EN": "LINK IDENTICAL MESH DATA",
        "JA": "同一メッシュデータをリンク",
        "ZH": "链接相同网格数据",
        "KO": "동일 메시 데이터 연결",
    },
    "link_help": {
        "EN": "Selected exact static duplicates share one mesh datablock.",
        "JA": "選択した完全一致の静的複製でメッシュデータを共有します。",
        "ZH": "让所选完全相同的静态副本共享一个网格数据块。",
        "KO": "선택한 완전히 동일한 정적 복제본이 하나의 메시 데이터를 공유합니다.",
    },
    "strip_collider": {
        "EN": "STRIP COLLIDER RENDER DATA",
        "JA": "コライダーの描画データを削除",
        "ZH": "移除碰撞代理渲染数据",
        "KO": "콜라이더 렌더 데이터 제거",
    },
    "strip_collider_help": {
        "EN": "Remove materials, UVs and color data from generated collider proxies.",
        "JA": "生成したコライダー代理からマテリアル、UV、カラーデータを削除します。",
        "ZH": "从生成的碰撞代理中移除材质、UV 和颜色数据。",
        "KO": "생성된 콜라이더 프록시에서 머티리얼, UV 및 색상 데이터를 제거합니다.",
    },
}


def _tr(context, key):
    lang = getattr(context.scene, "fishhwb_language", "EN") if context and context.scene else "EN"
    values = _TRANSLATIONS.get(key, {})
    return values.get(lang, values.get("EN", key))


def _report(operator, context, label, changed=0, unchanged=0, unsupported=0, failed=0, detail=""):
    message = (
        f"{label}: Changed: {changed} | Unchanged: {unchanged} | "
        f"Unsupported: {unsupported} | Failed: {failed}. {detail}"
    ).strip()
    context.scene.fishhwb_last_result = message
    level = {"ERROR"} if failed else ({"WARNING"} if unsupported and not changed else {"INFO"})
    operator.report(level, message)


def _selected_meshes(context):
    return [obj for obj in context.selected_objects if obj and obj.type == "MESH" and obj.data]


def _lightmap_reason(obj):
    if obj.library or obj.data.library:
        return "Linked library meshes require a local copy."
    if obj.data.shape_keys or any(mod.type == "ARMATURE" for mod in obj.modifiers):
        return "Lightmap UV generation is limited to static meshes."
    layers = obj.data.uv_layers
    if len(layers) == 0:
        return "A primary UV map is required before creating LightmapUV."
    if LIGHTMAP_UV_NAME in layers:
        index = list(layers).index(layers[LIGHTMAP_UV_NAME])
        if index == 1:
            return None
        return "Existing LightmapUV is not the second UV channel; preserved for manual review."
    if len(layers) > 1:
        return "Existing secondary UV channels were found; no channel was replaced automatically."
    if len(obj.data.polygons) == 0:
        return "The mesh has no faces to unwrap."
    return None


def _project_axes(normal):
    axis = max(range(3), key=lambda index: abs(normal[index]))
    if axis == 0:
        return 1, 2
    if axis == 1:
        return 0, 2
    return 0, 1


def _pack_lightmap_face_atlas(mesh, layer):
    """Create non-overlapping per-face UV islands without context-dependent UV operators."""
    faces = list(mesh.polygons)
    if not faces:
        raise ValueError("The mesh has no faces to unwrap.")

    grid = max(1, int(math.ceil(math.sqrt(len(faces)))))
    cell = 1.0 / grid
    pad = cell * 0.08
    inner = max(cell - pad * 2.0, cell * 0.5)
    epsilon = 1.0e-12

    for face_number, face in enumerate(faces):
        axis_u, axis_v = _project_axes(face.normal)
        coords = []
        for loop_index in face.loop_indices:
            co = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            coords.append((co[axis_u], co[axis_v]))

        min_u = min(value[0] for value in coords)
        max_u = max(value[0] for value in coords)
        min_v = min(value[1] for value in coords)
        max_v = max(value[1] for value in coords)
        size_u = max_u - min_u
        size_v = max_v - min_v

        cell_x = face_number % grid
        cell_y = face_number // grid
        origin_u = cell_x * cell + pad
        origin_v = cell_y * cell + pad

        for loop_index, (value_u, value_v) in zip(face.loop_indices, coords):
            local_u = 0.5 if size_u <= epsilon else (value_u - min_u) / size_u
            local_v = 0.5 if size_v <= epsilon else (value_v - min_v) / size_v
            layer.data[loop_index].uv = (
                origin_u + local_u * inner,
                origin_v + local_v * inner,
            )


def _generate_lightmap_uv(obj, context):
    layers = obj.data.uv_layers
    if LIGHTMAP_UV_NAME in layers and list(layers).index(layers[LIGHTMAP_UV_NAME]) == 1:
        return False

    original_index = layers.active_index
    created = layers.new(name=LIGHTMAP_UV_NAME, do_init=False)
    layers.active = created

    try:
        _pack_lightmap_face_atlas(obj.data, created)
        uv_values = [tuple(item.uv) for item in created.data]
        if not uv_values or not all(math.isfinite(value) for uv in uv_values for value in uv):
            raise RuntimeError("Generated LightmapUV contains invalid coordinates.")
        if min(value for uv in uv_values for value in uv) < -0.0001 or max(value for uv in uv_values for value in uv) > 1.0001:
            raise RuntimeError("Generated LightmapUV escaped the 0-1 UV range.")

        obj.data["fishhwb_lightmap_uv"] = LIGHTMAP_UV_NAME
        obj.data.update()
        return True
    except Exception:
        if created.name in layers:
            layers.remove(created)
        raise
    finally:
        if len(layers):
            layers.active_index = min(original_index, len(layers) - 1)


def _mesh_signature(mesh):
    digest = hashlib.sha256()
    digest.update(struct.pack("<III", len(mesh.vertices), len(mesh.edges), len(mesh.polygons)))

    for vertex in mesh.vertices:
        digest.update(struct.pack("<3f", *vertex.co))
    for edge in mesh.edges:
        digest.update(struct.pack("<2I", *edge.vertices))
    for face in mesh.polygons:
        digest.update(repr((tuple(face.vertices), face.material_index, face.use_smooth)).encode("utf-8"))

    for layer in mesh.uv_layers:
        digest.update(("uv:" + layer.name).encode("utf-8"))
        for item in layer.data:
            digest.update(struct.pack("<2f", *item.uv))

    for attribute in sorted(mesh.attributes, key=lambda item: item.name):
        digest.update(repr((attribute.name, attribute.domain, attribute.data_type)).encode("utf-8"))
        for item in attribute.data:
            captured = False
            for field in ("value", "vector", "color", "uv"):
                if not hasattr(item, field):
                    continue
                value = getattr(item, field)
                if hasattr(value, "__len__") and not isinstance(value, (str, bytes)):
                    value = tuple(value)
                digest.update(repr(value).encode("utf-8"))
                captured = True
                break
            if not captured:
                digest.update(repr(item).encode("utf-8"))

    digest.update(repr(tuple(material.name_full if material else "" for material in mesh.materials)).encode("utf-8"))
    return digest.hexdigest()


def _link_reason(obj):
    if obj.library or obj.data.library:
        return "Linked library meshes are not relinked."
    if obj.modifiers:
        return "Objects with modifiers are skipped so evaluated geometry is not guessed."
    if obj.data.shape_keys:
        return "Shape-key meshes are skipped because sharing would also share deformation data."
    if any(slot.link != "DATA" for slot in obj.material_slots):
        return "Objects with object-level material overrides are skipped."
    return None


def _strip_collider_render_data(obj):
    if not obj.get("fishhwb_collision_proxy"):
        return None
    if obj.library or obj.data.library:
        raise ValueError("Linked collider proxies require a local copy.")

    mesh = obj.data
    changed = False
    if len(mesh.materials):
        mesh.materials.clear()
        changed = True
    while len(mesh.uv_layers):
        mesh.uv_layers.remove(mesh.uv_layers[-1])
        changed = True
    color_attributes = getattr(mesh, "color_attributes", None)
    if color_attributes is not None:
        for attribute in list(color_attributes):
            color_attributes.remove(attribute)
            changed = True
    if changed:
        mesh["fishhwb_collider_render_data_stripped"] = True
        mesh.update()
    return changed


class FISHHWB_OT_generate_lightmap_uv(bpy.types.Operator):
    bl_idname = "fishhwb.generate_lightmap_uv"
    bl_label = "Generate Lightmap UV"
    bl_description = "Create a non-overlapping second LightmapUV channel for selected supported static meshes"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT" and bool(_selected_meshes(context))

    def execute(self, context):
        changed = unchanged = unsupported = failed = 0
        for obj in _selected_meshes(context):
            reason = _lightmap_reason(obj)
            if reason:
                if LIGHTMAP_UV_NAME in obj.data.uv_layers and list(obj.data.uv_layers).index(obj.data.uv_layers[LIGHTMAP_UV_NAME]) == 1:
                    unchanged += 1
                else:
                    unsupported += 1
                continue
            try:
                if _generate_lightmap_uv(obj, context):
                    changed += 1
                else:
                    unchanged += 1
            except Exception:
                failed += 1

        _report(
            self, context, "Lightmap UV", changed, unchanged, unsupported, failed,
            "Creates LightmapUV only as the second UV channel; existing secondary UVs are preserved.",
        )
        return {"FINISHED"} if changed or unchanged else {"CANCELLED"}


class FISHHWB_OT_link_identical_mesh_data(bpy.types.Operator):
    bl_idname = "fishhwb.link_identical_mesh_data"
    bl_label = "Link Identical Mesh Data"
    bl_description = "Make exact selected static mesh duplicates share one mesh datablock without changing object transforms"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT" and len(_selected_meshes(context)) >= 2

    def execute(self, context):
        supported = []
        unsupported = 0
        for obj in _selected_meshes(context):
            if _link_reason(obj):
                unsupported += 1
            else:
                supported.append(obj)

        groups = {}
        for obj in supported:
            groups.setdefault(_mesh_signature(obj.data), []).append(obj)

        active = context.view_layer.objects.active
        changed = unchanged = 0
        linked_groups = 0
        for group in groups.values():
            if len(group) < 2:
                unchanged += len(group)
                continue
            canonical = active if active in group else group[0]
            group_changed = 0
            for obj in group:
                if obj is canonical or obj.data is canonical.data:
                    unchanged += 1
                    continue
                obj.data = canonical.data
                obj["fishhwb_linked_mesh_source"] = canonical.name_full
                changed += 1
                group_changed += 1
            if group_changed:
                linked_groups += 1

        _report(
            self, context, "Identical mesh data", changed, unchanged, unsupported, 0,
            f"Linked {changed} object(s) across {linked_groups} exact duplicate group(s). Zero-user old mesh datablocks remain available for Undo and later orphan cleanup.",
        )
        return {"FINISHED"} if changed or unchanged else {"CANCELLED"}


class FISHHWB_OT_strip_collider_render_data(bpy.types.Operator):
    bl_idname = "fishhwb.strip_collider_render_data"
    bl_label = "Strip Collider Render Data"
    bl_description = "Remove materials, UV layers and color attributes from selected generated collision proxies while preserving geometry"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT" and bool(_selected_meshes(context))

    def execute(self, context):
        changed = unchanged = unsupported = failed = 0
        for obj in _selected_meshes(context):
            if not obj.get("fishhwb_collision_proxy"):
                unsupported += 1
                continue
            try:
                result = _strip_collider_render_data(obj)
                if result:
                    changed += 1
                else:
                    unchanged += 1
            except Exception:
                failed += 1

        _report(
            self, context, "Collider render data", changed, unchanged, unsupported, failed,
            "Generated collider geometry is preserved; only render-only materials, UVs and color attributes are removed.",
        )
        return {"FINISHED"} if changed or unchanged else {"CANCELLED"}


class FISHHWB_PT_optimizer_42(bpy.types.Panel):
    bl_label = "Blender 4.2+ Tools"
    bl_idname = "FISHHWB_PT_optimizer_42"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FISHHWB"
    bl_parent_id = "FISHHWB_PT_optimizer"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.label(text=_tr(context, "panel"))
        layout.label(text=_tr(context, "desc"))

        lightmap = layout.box()
        lightmap.label(text=_tr(context, "lightmap_help"))
        row = lightmap.row()
        row.scale_y = 1.25
        row.operator("fishhwb.generate_lightmap_uv", text=_tr(context, "lightmap"))

        linking = layout.box()
        linking.label(text=_tr(context, "link_help"))
        row = linking.row()
        row.scale_y = 1.25
        row.operator("fishhwb.link_identical_mesh_data", text=_tr(context, "link"))

        collider = layout.box()
        collider.label(text=_tr(context, "strip_collider_help"))
        row = collider.row()
        row.scale_y = 1.25
        row.operator("fishhwb.strip_collider_render_data", text=_tr(context, "strip_collider"))


classes = (
    FISHHWB_OT_generate_lightmap_uv,
    FISHHWB_OT_link_identical_mesh_data,
    FISHHWB_OT_strip_collider_render_data,
    FISHHWB_PT_optimizer_42,
)


def register():
    if bpy.app.version < MIN_BLENDER_VERSION:
        raise RuntimeError("Optimize Your Project Blender tools require Blender 4.2 or newer.")
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if hasattr(bpy.types, cls.__name__):
            bpy.utils.unregister_class(cls)
