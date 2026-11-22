# SPDX-License-Identifier: GPL-3.0-or-later
"""Project-open update orchestration via Blender's native Extensions manager.

Only installed extensions from already configured online repositories are
eligible. Never modify Blender files, manually installed add-ons or asset libraries.
"""
import time

import bpy
from bpy.app.handlers import persistent

_addon_id = None
_status = "Automatic extension updates have not run yet."
_next_check = 0.0
_sync_started_at = 0.0
_sync_pending = False


def status():
    return _status


def _allowed():
    if bpy.app.background or not bpy.app.online_access:
        return False
    addon = bpy.context.preferences.addons.get(_addon_id)
    return bool(addon and addon.preferences.auto_update_extensions)


def _schedule(seconds=8.0):
    if not _allowed() or bpy.app.timers.is_registered(_sync_repositories):
        return
    if time.monotonic() < _next_check:
        return
    bpy.app.timers.register(_sync_repositories, first_interval=seconds)


def _sync_repositories():
    global _status, _sync_pending, _sync_started_at, _next_check
    if not _allowed():
        _status = "Automatic updates skipped: offline or disabled."
        return None

    # Prevent repeated downloads when someone switches .blend files frequently.
    try:
        if not bpy.ops.extensions.repo_sync_all.poll():
            _status = "Extension repository sync unavailable; use Preferences > Extensions."
            return None
        result = bpy.ops.extensions.repo_sync_all('INVOKE_DEFAULT', use_active_only=False)
        if 'CANCELLED' in result:
            _status = "Extension repository sync was cancelled."
            return None
        _next_check = time.monotonic() + 6 * 3600
        _status = "Checking configured online extension repositories..."
        _sync_started_at = time.monotonic()
        _sync_pending = True
        if not bpy.app.timers.is_registered(_upgrade_when_ready):
            bpy.app.timers.register(_upgrade_when_ready, first_interval=5.0)
    except (RuntimeError, AttributeError, TypeError) as error:
        _status = "Extension update check unavailable: " + str(error)
    return None


def _upgrade_when_ready():
    global _status, _sync_pending
    if not _sync_pending or not _allowed():
        _sync_pending = False
        return None
    # Blender advertises the number of upgradeable extensions after syncing.
    # Do not start the upgrade while repository synchronization is still active.
    wm = bpy.context.window_manager
    count = getattr(wm, "extensions_updates", None) if wm else None
    elapsed = time.monotonic() - _sync_started_at
    # Blender can use negative update counts as a repository-check-in-progress
    # sentinel. Never start upgrading while that scan is still running.
    if isinstance(count, int) and count < 0:
        if elapsed < 120.0:
            return 3.0
        _status = "Extension repository check timed out. No upgrades attempted."
        _sync_pending = False
        return None
    if count == 0 and elapsed < 12.0:
        return 3.0
    if count == 0:
        _status = "Extension check finished; no updates were reported."
        _sync_pending = False
        return None
    if count is None and elapsed < 12.0:
        return 3.0
    _sync_pending = False
    try:
        if not bpy.ops.extensions.package_upgrade_all.poll():
            _status = "Updates may be available; open Preferences > Extensions to install them."
            return None
        result = bpy.ops.extensions.package_upgrade_all('INVOKE_DEFAULT', use_active_only=False)
        _status = ((str(count) + " Blender extension update(s) queued; review Preferences > Extensions."
                   if isinstance(count, int) and count > 0 else
                   "Blender extension upgrades requested; review Preferences > Extensions.")
                   if 'CANCELLED' not in result else
                   "Blender extension updates were cancelled.")
    except (RuntimeError, AttributeError, TypeError) as error:
        _status = "Automatic extension upgrade unavailable: " + str(error)
    return None


@persistent
def _after_project_loaded(_unused):
    _schedule()


def register(addon_id):
    global _addon_id
    _addon_id = addon_id
    if _after_project_loaded not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_after_project_loaded)
    _schedule()


def unregister():
    global _sync_pending, _addon_id
    if _after_project_loaded in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_after_project_loaded)
    for callback in (_sync_repositories, _upgrade_when_ready):
        if bpy.app.timers.is_registered(callback):
            bpy.app.timers.unregister(callback)
    _sync_pending = False
    _addon_id = None
