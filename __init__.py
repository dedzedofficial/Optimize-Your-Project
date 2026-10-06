# SPDX-License-Identifier: GPL-3.0-or-later
"""Blender 4.2+ extension entry point for Optimize Your Project."""

import textwrap
import bpy

from .Blender import vr_optimizer_blender as _addon
from .Blender.vr_optimizer_blender import tools_42 as _tools42

bl_info = dict(_addon.bl_info)
bl_info.update({
    "version": (0, 7, 65),
    "blender": (4, 2, 0),
    "description": "Readable one-panel Remesh, LOD, lightmap, collider and static-mesh optimization tools",
})

_addon.bl_info.update(bl_info)
_addon._TRANSLATIONS["subtitle"].update({
    "EN": "Blender v0.7.65: Quick Optimize",
    "JA": "Blender v0.7.65: クイック最適化",
    "ZH": "Blender v0.7.65：快速优化",
    "KO": "Blender v0.7.65: 빠른 최적화",
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
        brand.template_icon(icon_value=_addon._brand_preview["logo"].icon_id, scale=2.4)
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

    quick = layout.box()
    quick.label(text="QUICK OPTIMIZE", icon="TOOL_SETTINGS")
    _wrapped(quick, "All supported mesh optimization actions are grouped here. Source meshes are preserved by Remesh and LOD workflows.", context)

    remesh = quick.box()
    remesh.label(text=_addon.tr(context, "remesh_title"), icon="MOD_REMESH")
    _wrapped(remesh, _addon.tr(context, "remesh_desc"), context)
    remesh.prop(context.scene, "fishhwb_triangle_target", text=_addon.tr(context, "triangle_target"), slider=True)
    row = remesh.row()
    row.scale_y = 1.45
    row.operator("fishhwb.one_click_remesh", text=_addon.tr(context, "remesh"), icon="MOD_REMESH")

    lod = quick.box()
    lod.label(text=_addon.tr(context, "lod_title"), icon="MOD_DECIM")
    _wrapped(lod, _addon.tr(context, "lod_desc"), context)
    lod.prop(context.scene, "fishhwb_apply_modifiers", text=_addon.tr(context, "apply_modifiers"))
    lod.prop(context.scene, "fishhwb_create_collision_proxy", text=_addon.tr(context, "collision_proxy"))
    row = lod.row()
    row.scale_y = 1.45
    row.operator(
        "fishhwb.create_lods_selected" if len(selected_meshes) > 1 else "fishhwb.create_lods",
        text=_addon.tr(context, "create_lods"), icon="MOD_DECIM",
    )

    modern = quick.box()
    modern.label(text="BLENDER 4.2+ MESH TOOLS", icon="MESH_GRID")
    _wrapped(modern, _tools42._tr(context, "lightmap_help"), context)
    row = modern.row()
    row.scale_y = 1.3
    row.operator("fishhwb.generate_lightmap_uv", text=_tools42._tr(context, "lightmap"), icon="UV")
    _wrapped(modern, _tools42._tr(context, "link_help"), context)
    row = modern.row()
    row.scale_y = 1.3
    row.operator("fishhwb.link_identical_mesh_data", text=_tools42._tr(context, "link"), icon="LINKED")
    _wrapped(modern, _tools42._tr(context, "strip_collider_help"), context)
    row = modern.row()
    row.scale_y = 1.3
    row.operator("fishhwb.strip_collider_render_data", text=_tools42._tr(context, "strip_collider"), icon="TRASH")

    if context.scene.fishhwb_last_result:
        result = layout.box()
        result.label(text=_addon.tr(context, "last_result"), icon="INFO")
        for line in context.scene.fishhwb_last_result.splitlines():
            _wrapped(result, line, context)


# Replace the older stacked panel with the compact 0.7.65 layout.
_addon.FISHHWB_PT_optimizer.draw = _draw_core_765

# The modern tools remain registered as operators, but their separate child panel is
# intentionally omitted because 0.7.65 exposes them in the main Quick Optimize area.
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
