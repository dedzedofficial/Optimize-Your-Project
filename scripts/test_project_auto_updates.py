"""Blender-free tests for extension updater lifecycle and safety gates."""
import importlib.util
from pathlib import Path
import sys
import time
import types
import unittest
from unittest.mock import MagicMock


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Blender" / "vr_optimizer_blender" / "auto_updates.py"


def load_updater(online=True, enabled=True, count=2):
    mock_bpy = types.ModuleType("bpy")
    app = types.ModuleType("bpy.app")
    handlers = types.ModuleType("bpy.app.handlers")
    handlers.load_post = []
    handlers.persistent = lambda callback: callback

    registered = {}
    timers = types.SimpleNamespace(
        is_registered=lambda callback: callback in registered,
        register=lambda callback, first_interval: registered.update({callback: first_interval}),
        unregister=lambda callback: registered.pop(callback),
    )
    app.background = False
    app.online_access = online
    app.handlers = handlers
    app.timers = timers

    extensions = types.SimpleNamespace(
        repo_sync_all=MagicMock(return_value={"RUNNING_MODAL"}),
        package_upgrade_all=MagicMock(return_value={"RUNNING_MODAL"}),
    )
    extensions.repo_sync_all.poll = MagicMock(return_value=True)
    extensions.package_upgrade_all.poll = MagicMock(return_value=True)
    mock_bpy.app = app
    mock_bpy.ops = types.SimpleNamespace(extensions=extensions)

    preferences = types.SimpleNamespace(auto_update_extensions=enabled)
    mock_bpy.context = types.SimpleNamespace(
        preferences=types.SimpleNamespace(
            addons={"test.optimize_your_project": types.SimpleNamespace(preferences=preferences)}
        ),
        window_manager=types.SimpleNamespace(extensions_updates=count),
    )

    previous = {name: sys.modules.get(name) for name in ("bpy", "bpy.app", "bpy.app.handlers")}
    sys.modules["bpy"] = mock_bpy
    sys.modules["bpy.app"] = app
    sys.modules["bpy.app.handlers"] = handlers
    try:
        spec = importlib.util.spec_from_file_location("test_oyp_auto_updates", SOURCE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        for name, original in previous.items():
            if original is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = original
    return module, mock_bpy, registered, preferences


class ProjectAutoUpdateTests(unittest.TestCase):
    def test_default_enabled_schedules_once_and_load_handler_is_registered(self):
        updater, blender, queued, _ = load_updater()
        updater.register("test.optimize_your_project")
        self.assertIn(updater._sync_repositories, queued)
        self.assertIn(updater._after_project_loaded, blender.app.handlers.load_post)
        updater._after_project_loaded(None)
        self.assertEqual(1, len(queued))
        updater.unregister()
        self.assertFalse(queued)
        self.assertEqual([], blender.app.handlers.load_post)

    def test_offline_prevents_network_actions(self):
        updater, blender, queued, _ = load_updater(online=False)
        updater.register("test.optimize_your_project")
        self.assertFalse(queued)
        self.assertEqual(0, blender.ops.extensions.repo_sync_all.call_count)

    def test_disabled_prevents_network_actions(self):
        updater, blender, queued, _ = load_updater(enabled=False)
        updater.register("test.optimize_your_project")
        self.assertFalse(queued)
        self.assertEqual(0, blender.ops.extensions.package_upgrade_all.call_count)

    def test_sync_then_native_upgrade_when_updates_present(self):
        updater, blender, queued, _ = load_updater(count=2)
        updater.register("test.optimize_your_project")
        self.assertIsNone(updater._sync_repositories())
        blender.ops.extensions.repo_sync_all.assert_called_once_with(
            "INVOKE_DEFAULT", use_active_only=False)
        self.assertIn(updater._upgrade_when_ready, queued)
        self.assertIsNone(updater._upgrade_when_ready())
        blender.ops.extensions.package_upgrade_all.assert_called_once_with(
            "INVOKE_DEFAULT", use_active_only=False)
        self.assertIn("queued", updater.status())

    def test_no_updates_does_not_invoke_upgrade(self):
        updater, blender, _, _ = load_updater(count=0)
        updater.register("test.optimize_your_project")
        updater._sync_repositories()
        updater._sync_started_at = time.monotonic() - 50
        self.assertIsNone(updater._upgrade_when_ready())
        self.assertEqual(0, blender.ops.extensions.package_upgrade_all.call_count)
        self.assertIn("no updates", updater.status())

    def test_sync_unavailable_fails_closed(self):
        updater, blender, _, _ = load_updater()
        updater.register("test.optimize_your_project")
        blender.ops.extensions.repo_sync_all.poll.return_value = False
        updater._sync_repositories()
        self.assertEqual(0, blender.ops.extensions.repo_sync_all.call_count)
        self.assertIn("unavailable", updater.status())


if __name__ == "__main__":
    unittest.main()
