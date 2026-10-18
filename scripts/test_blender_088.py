"""Blender 4.2+ smoke/regression tests for 0.8.8 Smart Optimize workflows."""
import importlib.util
from pathlib import Path
import sys
import unittest

import bpy

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "optimize_your_project_v088", ROOT / "__init__.py",
    submodule_search_locations=[str(ROOT)])
extension = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = extension
spec.loader.exec_module(extension)


class SmartOptimize088Tests(unittest.TestCase):
    def setUp(self):
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        scene = bpy.context.scene
        scene.fishhwb_lod1_percent = 66
        scene.fishhwb_lod2_percent = 33
        scene.fishhwb_collision_target = 500
        scene.fishhwb_create_collision_proxy = False
        scene.fishhwb_triangle_target = 10000

    def cube(self):
        bpy.ops.mesh.primitive_cube_add()
        return bpy.context.active_object

    def test_version_and_operator_registered(self):
        self.assertEqual(extension.bl_info["version"], (0, 8, 8))
        obj = self.cube()
        self.assertTrue(bpy.ops.fishhwb.smart_optimize.poll())
        self.assertIsNotNone(obj)

    def test_smart_unchanged_leaves_object_untouched(self):
        obj = self.cube()
        before = [(tuple(v.co)) for v in obj.data.vertices]
        result = bpy.ops.fishhwb.smart_optimize(
            'EXEC_DEFAULT', clean_geometry=False, remesh=False,
            lods=False, atlas=False, lightmap=False)
        self.assertEqual(result, {'CANCELLED'})
        self.assertEqual(before, [(tuple(v.co)) for v in obj.data.vertices])

    def test_smart_lightmap_uses_separate_copy(self):
        obj = self.cube()
        obj.name = "OriginalCube"
        source_uvs = [uv.name for uv in obj.data.uv_layers]
        self.assertTrue(source_uvs, "Default cube should have a UV layer.")
        result = bpy.ops.fishhwb.smart_optimize(
            'EXEC_DEFAULT', clean_geometry=False, remesh=False,
            lods=False, atlas=False, lightmap=True)
        self.assertEqual(result, {'FINISHED'})
        self.assertEqual(source_uvs, [uv.name for uv in obj.data.uv_layers])
        copy = bpy.context.active_object
        self.assertIsNot(copy, obj)
        self.assertIn('LightmapUV', copy.data.uv_layers)
        self.assertNotIn('LightmapUV', obj.data.uv_layers)

    def test_lod_and_collider_independent_targets(self):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16)
        source = bpy.context.active_object
        before = len(source.data.polygons)
        scene = bpy.context.scene
        scene.fishhwb_lod1_percent = 75
        scene.fishhwb_lod2_percent = 25
        scene.fishhwb_collision_target = 60
        scene.fishhwb_create_collision_proxy = True
        self.assertEqual(bpy.ops.fishhwb.create_lods(), {'FINISHED'})
        lod0 = bpy.context.active_object
        meshes = {ob.get('fishhwb_lod_level'): ob for ob in lod0.users_collection[0].objects
                  if ob.get('fishhwb_lod_level') is not None}
        self.assertEqual(set(meshes), {0, 1, 2})
        from optimize_your_project_v088.Blender.vr_optimizer_blender import triangle_count
        base = triangle_count(meshes[0].data)
        self.assertLessEqual(triangle_count(meshes[1].data), int(base * 0.75))
        self.assertLessEqual(triangle_count(meshes[2].data), int(base * 0.25))
        collider = next(ob for ob in lod0.users_collection[0].objects
                        if ob.get('fishhwb_collision_proxy'))
        self.assertLessEqual(triangle_count(collider.data), 60)
        self.assertEqual(len(source.data.polygons), before)

    def test_remesh_keeps_large_open_boundary(self):
        from optimize_your_project_v088.Blender.vr_optimizer_blender import v08_tools
        bpy.ops.mesh.primitive_plane_add(size=4)
        plane = bpy.context.active_object
        previous = len(plane.data.polygons)
        v08_tools._repair_static_mesh(plane.data, fill_holes=True)
        self.assertEqual(len(plane.data.polygons), previous)


extension.register()
try:
    outcome = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(SmartOptimize088Tests))
finally:
    extension.unregister()

if not outcome.wasSuccessful():
    raise RuntimeError("Blender 0.8.8 regression suite failed.")
