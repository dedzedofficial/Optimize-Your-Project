"""Blender 4.2+ regression checks for modern extension-only tools."""
import importlib.util
import sys
import unittest
from pathlib import Path

import bpy

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root / "Blender"))
import vr_optimizer_blender as addon
from vr_optimizer_blender import tools_42


def snapshot(mesh):
    return (
        tuple(tuple(vertex.co) for vertex in mesh.vertices),
        tuple(tuple(poly.vertices) for poly in mesh.polygons),
    )


class Blender42ToolsTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)
        for mesh in list(bpy.data.meshes):
            if mesh.users == 0:
                bpy.data.meshes.remove(mesh)
        bpy.context.scene.fishhwb_last_result = ""
        bpy.context.scene.fishhwb_language = "EN"

    def cube(self, name="Cube", with_uv=True):
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
        if with_uv:
            uv = mesh.uv_layers.new(name="UVMap")
            for loop in mesh.loops:
                co = mesh.vertices[loop.vertex_index].co
                uv.data[loop.index].uv = ((co.x + 1.0) * 0.5, (co.y + 1.0) * 0.5)
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        for selected in list(bpy.context.selected_objects):
            selected.select_set(False)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        return obj

    def test_requires_blender_42_or_newer(self):
        self.assertGreaterEqual(bpy.app.version, tools_42.MIN_BLENDER_VERSION)
        self.assertEqual(tools_42.MIN_BLENDER_VERSION, (4, 2, 0))

    def test_generate_lightmap_uv_creates_second_channel_only(self):
        source = self.cube("LightmapSource")
        before = snapshot(source.data)
        primary_before = tuple(tuple(item.uv) for item in source.data.uv_layers[0].data)

        self.assertEqual(bpy.ops.fishhwb.generate_lightmap_uv(), {"FINISHED"})
        self.assertEqual([layer.name for layer in source.data.uv_layers], ["UVMap", "LightmapUV"])
        self.assertEqual(before, snapshot(source.data))
        self.assertEqual(primary_before, tuple(tuple(item.uv) for item in source.data.uv_layers[0].data))

        generated = tuple(tuple(item.uv) for item in source.data.uv_layers["LightmapUV"].data)
        self.assertTrue(generated)
        self.assertGreater(len(set(generated)), 1)
        for uv in generated:
            self.assertGreaterEqual(min(uv), -0.0001)
            self.assertLessEqual(max(uv), 1.0001)

        face_bounds = []
        layer = source.data.uv_layers["LightmapUV"]
        for face in source.data.polygons:
            coords = [layer.data[index].uv for index in face.loop_indices]
            face_bounds.append((
                min(value.x for value in coords), max(value.x for value in coords),
                min(value.y for value in coords), max(value.y for value in coords),
            ))
        for index, first in enumerate(face_bounds):
            for second in face_bounds[index + 1:]:
                overlap_x = min(first[1], second[1]) > max(first[0], second[0])
                overlap_y = min(first[3], second[3]) > max(first[2], second[2])
                self.assertFalse(overlap_x and overlap_y)

        self.assertEqual(bpy.ops.fishhwb.generate_lightmap_uv(), {"FINISHED"})
        self.assertEqual(len(source.data.uv_layers), 2)
        self.assertIn("Unchanged: 1", bpy.context.scene.fishhwb_last_result)

    def test_lightmap_uv_preserves_existing_secondary_channel(self):
        source = self.cube("ExistingSecondary")
        source.data.uv_layers.new(name="DetailUV")
        before = [layer.name for layer in source.data.uv_layers]
        self.assertEqual(bpy.ops.fishhwb.generate_lightmap_uv(), {"CANCELLED"})
        self.assertEqual(before, [layer.name for layer in source.data.uv_layers])
        self.assertNotIn("LightmapUV", source.data.uv_layers)
        self.assertIn("Unsupported: 1", bpy.context.scene.fishhwb_last_result)

    def test_lightmap_uv_requires_primary_uv(self):
        source = self.cube("NoUV", with_uv=False)
        before = snapshot(source.data)
        self.assertEqual(bpy.ops.fishhwb.generate_lightmap_uv(), {"CANCELLED"})
        self.assertEqual(before, snapshot(source.data))
        self.assertEqual(len(source.data.uv_layers), 0)

    def test_link_identical_mesh_data_preserves_object_transforms(self):
        first = self.cube("InstanceA")
        second = first.copy()
        second.data = first.data.copy()
        second.name = "InstanceB"
        second.location = (3.0, 2.0, 1.0)
        bpy.context.collection.objects.link(second)
        first.select_set(True)
        second.select_set(True)
        bpy.context.view_layer.objects.active = first
        bpy.context.view_layer.update()

        first_snapshot = snapshot(first.data)
        second_transform = second.matrix_world.copy()
        self.assertIsNot(first.data, second.data)
        self.assertEqual(bpy.ops.fishhwb.link_identical_mesh_data(), {"FINISHED"})
        bpy.context.view_layer.update()
        self.assertIs(first.data, second.data)
        self.assertEqual(first_snapshot, snapshot(second.data))
        self.assertEqual(second_transform, second.matrix_world)
        self.assertEqual(second.get("fishhwb_linked_mesh_source"), first.name_full)
        self.assertIn("Changed: 1", bpy.context.scene.fishhwb_last_result)

    def test_linking_skips_nonidentical_meshes(self):
        first = self.cube("DifferentA")
        second = self.cube("DifferentB")
        second.data.vertices[0].co.x += 0.25
        second.data.update()
        first.select_set(True)
        second.select_set(True)
        bpy.context.view_layer.objects.active = first
        data_a = first.data
        data_b = second.data
        self.assertEqual(bpy.ops.fishhwb.link_identical_mesh_data(), {"FINISHED"})
        self.assertIs(first.data, data_a)
        self.assertIs(second.data, data_b)
        self.assertIsNot(first.data, second.data)
        self.assertIn("Changed: 0", bpy.context.scene.fishhwb_last_result)

    def test_linking_skips_modifiers_and_shape_keys(self):
        first = self.cube("GuardA")
        second = self.cube("GuardB")
        first.modifiers.new("Mirror", "MIRROR")
        second.shape_key_add(name="Basis")
        first.select_set(True)
        second.select_set(True)
        bpy.context.view_layer.objects.active = first
        self.assertEqual(bpy.ops.fishhwb.link_identical_mesh_data(), {"CANCELLED"})
        self.assertIn("Unsupported: 2", bpy.context.scene.fishhwb_last_result)

    def test_strip_collider_render_data_preserves_geometry(self):
        collider = self.cube("ColliderProxy")
        collider["fishhwb_collision_proxy"] = True
        collider.data.materials.append(bpy.data.materials.new("ColliderMaterial"))
        collider.data.color_attributes.new(name="Color", type="FLOAT_COLOR", domain="CORNER")
        before = snapshot(collider.data)

        self.assertEqual(bpy.ops.fishhwb.strip_collider_render_data(), {"FINISHED"})
        self.assertEqual(before, snapshot(collider.data))
        self.assertEqual(len(collider.data.materials), 0)
        self.assertEqual(len(collider.data.uv_layers), 0)
        self.assertEqual(len(collider.data.color_attributes), 0)
        self.assertTrue(collider.data.get("fishhwb_collider_render_data_stripped"))
        self.assertIn("Changed: 1", bpy.context.scene.fishhwb_last_result)

        self.assertEqual(bpy.ops.fishhwb.strip_collider_render_data(), {"FINISHED"})
        self.assertIn("Unchanged: 1", bpy.context.scene.fishhwb_last_result)

    def test_strip_collider_render_data_rejects_normal_mesh(self):
        source = self.cube("NormalMesh")
        before_uv = len(source.data.uv_layers)
        self.assertEqual(bpy.ops.fishhwb.strip_collider_render_data(), {"CANCELLED"})
        self.assertEqual(len(source.data.uv_layers), before_uv)
        self.assertIn("Unsupported: 1", bpy.context.scene.fishhwb_last_result)


addon.register()
tools_42.register()
try:
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(Blender42ToolsTests)
    )
finally:
    tools_42.unregister()
    addon.unregister()

if not result.wasSuccessful():
    raise RuntimeError("Blender 4.2+ optimization regression checks failed")

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
    if not hasattr(bpy.types, "FISHHWB_PT_optimizer"):
        raise RuntimeError("Optimize Your Project main panel was not registered")
    if hasattr(bpy.types, "FISHHWB_PT_optimizer_42"):
        raise RuntimeError("The old separate Blender 4.2+ child panel should not be registered in 0.8.0")
    if extension.bl_info["version"] != (0, 8, 0):
        raise RuntimeError("Blender extension runtime version is not 0.8.0")
    if extension.bl_info["blender"] != (4, 2, 0):
        raise RuntimeError("Blender extension minimum runtime is not 4.2")
finally:
    extension.unregister()
