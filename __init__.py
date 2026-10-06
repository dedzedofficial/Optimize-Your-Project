# SPDX-License-Identifier: GPL-3.0-or-later
"""Blender 4.2+ extension entry point for Optimize Your Project."""

import textwrap
import bpy

from .Blender import vr_optimizer_blender as _addon
from .Blender.vr_optimizer_blender import tools_42 as _tools42

bl_info = dict(_addon.bl_info)
bl_info.update({
    "version": (0, 7, 66),
    "blender": (4, 2, 0),
    "description": "Readable one-panel Remesh, LOD, lightmap, collider and static-mesh optimization tools",
})

_addon.bl_info.update(bl_info)
_addon._TRANSLATIONS["subtitle"].update({
    "EN": "Blender v0.7.66: Primary Actions",
    "JA": "Blender v0.7.66: 主要アクション",
    "ZH": "Blender v0.7.66：主要操作",
    "KO": "Blender v0.7.66: 주요 작업",
})


def _wrapped(layout, text, context, icon=None):
    width = max(28, int(context.region.width / (7 * max(context.preferences.system.ui_scale, 0.5))))
    lines = textwrap.wrap(text, width=width) or [text]
    for index, line in enumerate(lines):
        if icon and index == 0:
            layout.label(text=line, icon=icon)
        else:
            layout.label(text=line)


def _draw_core_765(self, context):
    layout = self.layout
    layout.use_property_split = False
    layout.use_property_decorate = False

    brand = layout.box()
    if _addon._brand_preview and "logo" in _addon._brand_preview:
        brand.template_icon(icon_value=_addon._brand_preview["logo"].icon_id, scale=2.2)
    brand.label(text=_addon.tr(context, "title"))
    brand.label(text=_addon.tr(context, "subtitle"))
    brand.prop(context.scene, "fishhwb_language", text=_addon.tr(context, "language"))

    obj = context.active_object
    selected_meshes = [item for item in context.selected_objects if item.type == "MESH"]

    selected = layout.box()
    selected.label(text=_addon.tr(context, "selection"), icon="MESH_DATA")
    if obj and obj.type == "MESH":
        selected.label(text=obj.name)
        stats = selected.row(align=True)
        stats.label(text=f"Triangles: {_addon.triangle_count(obj.data):,}")
        stats.label(text=f"Vertices: {len(obj.data.vertices):,}")
        selected.prop(obj, "fishhwb_protect_detail", text=_addon.tr(context, "protect_detail"))
        if obj.get("fishhwb_remesh_history") or obj.get("fishhwb_lod_history"):
            selected.operator("fishhwb.reset_optimization_history", text=_addon.tr(context, "reset_history"), icon="FILE_REFRESH")
        if len(selected_meshes) > 1:
            selected.label(text=f"{len(selected_meshes)} mesh objects selected")
    else:
        _wrapped(selected, _addon.tr(context, "select_mesh"), context, "INFO")

    primary = layout.box()
    primary.label(text="PRIMARY ACTIONS", icon="TOOL_SETTINGS")

    remesh = primary.box()
    remesh.prop(context.scene, "fishhwb_triangle_target", text=_addon.tr(context, "triangle_target"), slider=True)
    row = remesh.row()
    row.scale_y = 1.5
    row.operator("fishhwb.one_click_remesh", text="REMESH TO TRIANGLE TARGET", icon="MOD_REMESH")

    lod = primary.box()
    lod.prop(context.scene, "fishhwb_apply_modifiers", text=_addon.tr(context, "apply_modifiers"))
    lod.prop(context.scene, "fishhwb_create_collision_proxy", text=_addon.tr(context, "collision_proxy"))
    row = lod.row()
    row.scale_y = 1.5
    row.operator(
        "fishhwb.create_lods_selected" if len(selected_meshes) > 1 else "fishhwb.create_lods",
        text="CREATE LOD0 / LOD1 / LOD2", icon="MOD_DECIM",
    )

    row = primary.row()
    row.scale_y = 1.4
    row.operator("fishhwb.generate_lightmap_uv", text="GENERATE LIGHTMAP UV", icon="UV")

    row = primary.row()
    row.scale_y = 1.4
    row.operator("fishhwb.link_identical_mesh_data", text="LINK IDENTICAL MESH DATA", icon="LINKED")

    row = primary.row()
    row.scale_y = 1.4
    row.operator("fishhwb.strip_collider_render_data", text="STRIP COLLIDER RENDER DATA", icon="TRASH")

    if context.scene.fishhwb_last_result:
        result = layout.box()
        result.label(text=_addon.tr(context, "last_result"), icon="INFO")
        for line in context.scene.fishhwb_last_result.splitlines():
            _wrapped(result, line, context)


# Replace the older stacked panel with the button-first 0.7.66 layout.
_addon.FISHHWB_PT_optimizer.draw = _draw_core_765

# Modern 4.2+ tools remain registered as operators and are surfaced as direct
# primary buttons in the main panel instead of a separate child panel.
_tools42.classes = tuple(
    cls for cls in _tools42.classes
    if cls is not _tools42.FISHHWB_PT_optimizer_42
)


def register():
    if bpy.app.version < (4, 2, 0):
        raise RuntimeError("Optimize Your Project for Blender requires Blender 4.2 or newer.")
    _addon.register()
    try:
        _tools42.register()
    except Exception:
        _addon.unregister()
        raise


def unregister():
    _tools42.unregister()
    _addon.unregister()
