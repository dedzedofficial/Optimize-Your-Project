"""Blender Git-install entry point for Optimize Your Project.

Clone this repository into a Blender add-ons directory using the folder name
"optimize_your_project". Blender will load this proxy and forward registration
to the maintained add-on under Blender/vr_optimizer_blender.
"""

from .Blender.vr_optimizer_blender import bl_info
from .Blender import vr_optimizer_blender as _addon


def register():
    _addon.register()


def unregister():
    _addon.unregister()
