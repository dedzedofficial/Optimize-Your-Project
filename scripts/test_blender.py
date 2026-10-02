"""Run with Blender --background --factory-startup --python-exit-code 1 --python scripts/test_blender.py."""
import importlib.util
import sys
import unittest
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Blender"))
import vr_optimizer_blender as addon


def snapshot(mesh):
    return (
        tuple(tuple(vertex.co) for vertex in mesh.vertices),
        tuple(tuple(polygon.vertices) for polygon in mesh.polygons),
    )


class RemeshLodTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)

        for collection in list(bpy.data.collections):
            if collection.users == 0:
                bpy.data.collections.remove(collection)

        bpy.context.scene.fishhwb_apply_modifiers = True
        bpy.context.scene.fishhwb_language = "EN"
        bpy.context.scene.fishhwb_last_result = ""

    def simple_mesh(self, name="Prop"):
        data = bpy.data.meshes.new(name)
        data.from_pydata(
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
        data.update()
        obj = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(obj)
        addon._select_only(bpy.context, obj)
        return obj

    def dense_mesh(self, name="Dense"):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1.0)
        obj = bpy.context.active_object
        obj.name = name
        obj.data.name = name
        return obj

    def test_language_switch(self):
        bpy.context.scene.fishhwb_language = "JA"
        self.assertEqual(addon.tr(bpy.context, "language"), "言語")
        self.assertEqual(addon.tr(bpy.context, "remesh"), "ワンクリックリメッシュ")
        self.assertEqual(addon.tr(bpy.context, "lod_title"), "LOD 生成")

    def test_one_click_remesh_preserves_source(self):
        source = self.simple_mesh("RemeshSource")
        before = snapshot(source.data)

        self.assertEqual(bpy.ops.fishhwb.one_click_remesh(), {"FINISHED"})
        output = bpy.context.active_object

        self.assertTrue(output.name.startswith("RemeshSource_Remesh"))
        self.assertIsNot(output.data, source.data)
        self.assertGreater(addon.triangle_count(output.data), 0)
        self.assertEqual(before, snapshot(source.data))
        self.assertIn("Changed: 1", bpy.context.scene.fishhwb_last_result)
        self.assertIn("Original object preserved", bpy.context.scene.fishhwb_last_result)

    def test_remesh_rejects_shape_keys(self):
        source = self.simple_mesh("ShapeKeySource")
        source.shape_key_add(name="Basis")
        before = snapshot(source.data)
        count_before = len(bpy.data.objects)

        self.assertEqual(bpy.ops.fishhwb.one_click_remesh(), {"CANCELLED"})
        self.assertEqual(count_before, len(bpy.data.objects))
        self.assertEqual(before, snapshot(source.data))
        self.assertEqual(bpy.context.active_object, source)
        self.assertIn("Unsupported: 1", bpy.context.scene.fishhwb_last_result)

    def test_active_lod_generation_preserves_source(self):
        source = self.dense_mesh("LODSource")
        before = snapshot(source.data)
        source_count = addon.triangle_count(source.data)

        self.assertEqual(bpy.ops.fishhwb.create_lods(), {"FINISHED"})
        lod0 = bpy.context.active_object

        self.assertTrue(lod0.name.startswith("LODSource_LOD0"))
        self.assertEqual(before, snapshot(source.data))
        self.assertEqual(source_count, addon.triangle_count(lod0.data))

        collection = next(
            collection
            for collection in bpy.data.collections
            if collection.name.startswith("LODSource_LODs")
        )
        created = {obj.get("fishhwb_lod_level"): obj for obj in collection.objects}
        self.assertEqual(set(created), {0, 1, 2})

        lod1_count = addon.triangle_count(created[1].data)
        lod2_count = addon.triangle_count(created[2].data)
        self.assertLessEqual(lod1_count, max(1, int(source_count * 0.66)))
        self.assertLessEqual(lod2_count, max(1, int(source_count * 0.33)))
        self.assertIn("Changed: 1", bpy.context.scene.fishhwb_last_result)
        self.assertIn("Original object preserved", bpy.context.scene.fishhwb_last_result)

    def test_lod_modifier_guard(self):
        source = self.dense_mesh("ModifierSource")
        source.modifiers.new("Subdivision", "SUBSURF")
        bpy.context.scene.fishhwb_apply_modifiers = False
        before = snapshot(source.data)
        count_before = len(bpy.data.objects)

        self.assertEqual(bpy.ops.fishhwb.create_lods(), {"CANCELLED"})
        self.assertEqual(count_before, len(bpy.data.objects))
        self.assertEqual(before, snapshot(source.data))
        self.assertEqual(bpy.context.active_object, source)
        self.assertIn("Unsupported: 1", bpy.context.scene.fishhwb_last_result)

    def test_batch_lod_generation(self):
        first = self.dense_mesh("BatchA")
        second = self.dense_mesh("BatchB")
        first_before = snapshot(first.data)
        second_before = snapshot(second.data)

        first.select_set(True)
        second.select_set(True)
        bpy.context.view_layer.objects.active = first

        self.assertEqual(bpy.ops.fishhwb.create_lods_selected(), {"FINISHED"})
        self.assertEqual(first_before, snapshot(first.data))
        self.assertEqual(second_before, snapshot(second.data))
        self.assertIn("Changed: 2", bpy.context.scene.fishhwb_last_result)

        lod0_names = {obj.name for obj in bpy.context.selected_objects}
        self.assertTrue(any(name.startswith("BatchA_LOD0") for name in lod0_names))
        self.assertTrue(any(name.startswith("BatchB_LOD0") for name in lod0_names))


addon.register()
try:
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(RemeshLodTests)
    )
finally:
    addon.unregister()

if not result.wasSuccessful():
    raise RuntimeError("Blender Remesh/LOD regression checks failed")

# Verify the repository-root Blender extension proxy still registers the focused add-on.
repo_root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "optimize_your_project",
    repo_root / "__init__.py",
    submodule_search_locations=[str(repo_root)],
)
extension = importlib.util.module_from_spec(spec)
sys.modules["optimize_your_project"] = extension
spec.loader.exec_module(extension)
extension.register()
try:
    if not hasattr(bpy.types.Scene, "fishhwb_language"):
        raise RuntimeError("Blender extension proxy did not register the add-on")
    if not hasattr(bpy.types.Scene, "fishhwb_apply_modifiers"):
        raise RuntimeError("Blender extension proxy did not register LOD settings")
finally:
    extension.unregister()
