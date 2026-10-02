"""Blender 4.2+ extension entry point for Optimize Your Project.

The repository ZIP is installable as a Blender extension. This proxy forwards
registration to the maintained add-on under Blender/vr_optimizer_blender.
"""

from .Blender.vr_optimizer_blender import bl_info
from .Blender import vr_optimizer_blender as _addon


def register():
    _addon.register()


def unregister():
    _addon.unregister()
