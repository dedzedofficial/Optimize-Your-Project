# SPDX-License-Identifier: GPL-3.0-or-later
"""Blender 4.2+ extension entry point for Optimize Your Project.

The modern Blender Extensions package is the supported Blender distribution.
Registration forwards to the established Remesh/LOD core and then adds the
4.2+ static-mesh optimization tools.
"""

import bpy

from .Blender import vr_optimizer_blender as _addon
from .Blender.vr_optimizer_blender import tools_42 as _tools42

bl_info = dict(_addon.bl_info)
bl_info.update({
    "version": (0, 7, 61),
    "blender": (4, 2, 0),
    "description": "Remesh, LOD, collision proxy, lightmap UV and static-mesh instancing tools",
})

# The 4.2+ extension entry point owns the current Blender release metadata.
_addon.bl_info.update(bl_info)
_addon._TRANSLATIONS["subtitle"].update({
    "EN": "Blender v0.7.61: Remesh + LOD + 4.2+ Tools",
    "JA": "Blender v0.7.61: リメッシュ + LOD + 4.2+ ツール",
    "ZH": "Blender v0.7.61：重网格 + LOD + 4.2+ 工具",
    "KO": "Blender v0.7.61: 리메시 + LOD + 4.2+ 도구",
})


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
