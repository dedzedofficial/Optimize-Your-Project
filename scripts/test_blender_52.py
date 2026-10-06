"""Run the core Blender suite on 5.2 with the removed Action.fcurves assertion replaced.

Blender 5.0 removed the legacy Action.fcurves API. The core suite still runs all
other tests; this wrapper replaces only that API-specific test with the modern
slotted-Action/channelbag equivalent.
"""
import runpy
import sys
import unittest
from pathlib import Path

import bpy

repo_root = Path(__file__).resolve().parents[1]

_original_get_names = unittest.TestLoader.getTestCaseNames


def _modern_names(loader, test_case_class):
    names = _original_get_names(loader, test_case_class)
    return [name for name in names if name != "test_remesh_copies_shape_key_action"]


unittest.TestLoader.getTestCaseNames = _modern_names
try:
    runpy.run_path(str(repo_root / "scripts" / "test_blender.py"), run_name="__main__")
finally:
    unittest.TestLoader.getTestCaseNames = _original_get_names

sys.path.insert(0, str(repo_root / "Blender"))
import vr_optimizer_blender as addon
from vr_optimizer_blender import deform_transfer


class Blender52ActionTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)
        bpy.context.scene.fishhwb_triangle_target = 200
        bpy.context.scene.fishhwb_apply_modifiers = True
        bpy.context.scene.fishhwb_create_collision_proxy = False
        bpy.context.scene.fishhwb_language = "EN"
        bpy.context.scene.fishhwb_last_result = ""

    def simple_mesh(self, name="AnimatedShape"):
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(
            [
                (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
                (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1),
            ],
            [],
            [
                (0, 1, 2, 3), (4, 7, 6, 5),
                (0, 4, 5, 1), (1, 5, 6, 2),
                (2, 6, 7, 3), (4, 0, 3, 7),
            ],
        )
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        return obj

    def test_remesh_copies_slotted_shape_key_action(self):
        source = self.simple_mesh()
        source.shape_key_add(name="Basis")
        key = source.shape_key_add(name="Smile")
        for item in key.data:
            item.co.z += 0.2
        key.value = 0.1
        key.keyframe_insert("value", frame=1)
        key.value = 0.8
        key.keyframe_insert("value", frame=10)

        original_animation = source.data.shape_keys.animation_data
        original_action = original_animation.action
        original_curves = deform_transfer._action_fcurves(original_animation)
        self.assertEqual(len(original_curves), 1)

        self.assertEqual(bpy.ops.fishhwb.one_click_remesh(), {"FINISHED"})
        output = bpy.context.active_object
        copied_animation = output.data.shape_keys.animation_data
        copied_action = copied_animation.action
        copied_curves = deform_transfer._action_fcurves(copied_animation)

        self.assertIsNot(copied_action, original_action)
        self.assertEqual(len(copied_curves), 1)
        self.assertEqual(copied_curves[0].data_path, original_curves[0].data_path)
        self.assertEqual(len(copied_curves[0].keyframe_points), 2)
        self.assertIsNotNone(getattr(copied_animation, "action_slot", None))
        self.assertIn("Changed: 1", bpy.context.scene.fishhwb_last_result)


addon.register()
try:
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(Blender52ActionTests)
    )
finally:
    addon.unregister()

if not result.wasSuccessful():
    raise RuntimeError("Blender 5.2 slotted Action regression checks failed")
