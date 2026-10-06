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

        bpy.context.scene.fishhwb_triangle_target = 10000
        bpy.context.scene.fishhwb_apply_modifiers = True
        bpy.context.scene.fishhwb_create_collision_proxy = False
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

    def textured_layers(self):
        vertices, faces = [], []
        n = 8
        for sheet in range(2):
            base = len(vertices)
            vertices.extend((x / n, y / n, sheet * 0.01)
                            for y in range(n + 1) for x in range(n + 1))
            for y in range(n):
                for x in range(n):
                    a = base + y * (n + 1) + x
                    faces.append((a, a + 1, a + n + 2, a + n + 1))
        mesh = bpy.data.meshes.new("TexturedSheets")
        mesh.from_pydata(vertices, [], faces)
        for name in ("Skin", "Coat"):
            material = bpy.data.materials.new(name)
            material.use_nodes = True
            mesh.materials.append(material)
        uv = mesh.uv_layers.new(name="UVMap")
        secondary = mesh.uv_layers.new(name="DetailUV")
        for face in mesh.polygons:
            sheet = face.index // (n * n)
            face.material_index = sheet
            for loop_index in face.loop_indices:
                co = mesh.vertices[mesh.loops[loop_index].vertex_index].co
                uv.data[loop_index].uv = (co.x + sheet * 2, co.y)
                secondary.data[loop_index].uv = (co.x * 0.5, co.y * 0.5)
        obj = bpy.data.objects.new("TexturedSheets", mesh)
        bpy.context.collection.objects.link(obj)
        addon._select_only(bpy.context, obj)
        return obj

    def test_remesh_preserves_uv_materials_and_close_surfaces(self):
        source = self.textured_layers()
        original = snapshot(source.data)
        original_uv = tuple(tuple(item.uv) for item in source.data.uv_layers[0].data)
        bpy.context.scene.fishhwb_triangle_target = 100
        self.assertEqual(bpy.ops.fishhwb.one_click_remesh(), {"FINISHED"})
        output = bpy.context.active_object
        self.assertLessEqual(addon.triangle_count(output.data), 100)
        self.assertEqual(list(output.data.materials), list(source.data.materials))
        self.assertEqual(set(f.material_index for f in output.data.polygons), {0, 1})
        self.assertEqual(set(l.name for l in output.data.uv_layers), {"UVMap", "DetailUV"})
        for face in output.data.polygons:
            for index in face.loop_indices:
                co = output.data.vertices[output.data.loops[index].vertex_index].co
                self.assertAlmostEqual(co.z, face.material_index * 0.01, places=5)
                uv = output.data.uv_layers["UVMap"].data[index].uv
                self.assertAlmostEqual(uv.x, co.x + face.material_index * 2, places=4)
                self.assertAlmostEqual(uv.y, co.y, places=4)
                detail = output.data.uv_layers["DetailUV"].data[index].uv
                self.assertAlmostEqual(detail.x, co.x * 0.5, places=4)
                self.assertAlmostEqual(detail.y, co.y * 0.5, places=4)
        self.assertEqual(original, snapshot(source.data))
        self.assertEqual(original_uv, tuple(tuple(item.uv) for item in source.data.uv_layers[0].data))

    def test_remesh_below_budget_keeps_surface_and_uv_exactly(self):
        source = self.textured_layers()
        original = snapshot(source.data)
        original_uv = tuple(tuple(item.uv) for item in source.data.uv_layers[0].data)
        self.assertEqual(bpy.ops.fishhwb.one_click_remesh(), {"FINISHED"})
        output = bpy.context.active_object
        self.assertEqual(original, snapshot(output.data))
        self.assertEqual(original_uv, tuple(tuple(item.uv) for item in output.data.uv_layers[0].data))

    def test_blendshapes_follow_coincident_surfaces_without_cross_transfer(self):
        for budget in (10000, 100):
            source = self.textured_layers()
            for vertex in source.data.vertices:
                vertex.co.z = 0
            source.shape_key_add(name="Basis")
            expression = source.shape_key_add(name="Expression")
            for i, point in enumerate(expression.data):
                point.co.z += 0.2 if i < 81 else -0.3
            bpy.context.scene.fishhwb_triangle_target = budget
            self.assertEqual(bpy.ops.fishhwb.one_click_remesh(), {"FINISHED"})
            output = bpy.context.active_object
            key = output.data.shape_keys.key_blocks["Expression"]
            for face in output.data.polygons:
                expected = 0.2 if face.material_index == 0 else -0.3
                for index in face.vertices:
                    self.assertAlmostEqual(key.data[index].co.z, expected, places=5)
            self.assertFalse(any(a.name.startswith("fishhwb_shape_") for a in output.data.attributes))

    def test_language_switch(self):
        bpy.context.scene.fishhwb_language = "JA"
        self.assertEqual(addon.tr(bpy.context, "language"), "言語")
        self.assertEqual(addon.tr(bpy.context, "remesh"), "ワンクリックリメッシュ")
        self.assertEqual(addon.tr(bpy.context, "lod_title"), "LOD 生成")
        self.assertEqual(addon.tr(bpy.context, "collision_proxy"), "LOD2 からコライダー代理を作成")

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

    def test_remesh_rejects_absolute_shape_keys(self):
        source = self.simple_mesh("ShapeKeySource")
        source.shape_key_add(name="Basis")
        source.data.shape_keys.use_relative = False
        before = snapshot(source.data)
        count_before = len(bpy.data.objects)
        self.assertEqual(bpy.ops.fishhwb.one_click_remesh(), {"CANCELLED"})
        self.assertEqual(count_before, len(bpy.data.objects))
        self.assertEqual(before, snapshot(source.data))
        self.assertEqual(bpy.context.active_object, source)
        self.assertIn("Unsupported: 1", bpy.context.scene.fishhwb_last_result)

    def test_remesh_transfers_relative_shapes_and_weights(self):
        source = self.dense_mesh("DeformSource")
        source.shape_key_add(name="Basis")
        smile = source.shape_key_add(name="Smile")
        for vertex in smile.data:
            vertex.co.z += 0.2
        smile.value = 0.7
        jaw = source.shape_key_add(name="Jaw")
        for base, shaped in zip(smile.data, jaw.data):
            shaped.co = base.co.copy()
            shaped.co.y += 0.1
        jaw.relative_key = smile
        left = source.vertex_groups.new(name="Left")
        right = source.vertex_groups.new(name="Right")
        for vertex in source.data.vertices:
            weight = (vertex.co.x + 1.0) / 2.0
            left.add([vertex.index], weight, 'REPLACE')
            right.add([vertex.index], 1.0 - weight, 'REPLACE')
        left.lock_weight = True
        before = snapshot(source.data)
        original_shape = tuple(tuple(v.co) for v in smile.data)
        bpy.context.scene.fishhwb_triangle_target = 200
        self.assertEqual(bpy.ops.fishhwb.one_click_remesh(), {"FINISHED"})
        output = bpy.context.active_object
        self.assertLessEqual(addon.triangle_count(output.data), 200)
        self.assertEqual(before, snapshot(source.data))
        self.assertEqual(original_shape, tuple(tuple(v.co) for v in smile.data))
        self.assertAlmostEqual(smile.value, 0.7, places=5)
        blocks = output.data.shape_keys.key_blocks
        self.assertEqual([block.name for block in blocks], ["Basis", "Smile", "Jaw"])
        self.assertEqual(blocks["Jaw"].relative_key, blocks["Smile"])
        for smile_point, jaw_point in zip(blocks["Smile"].data, blocks["Jaw"].data):
            self.assertAlmostEqual(jaw_point.co.y - smile_point.co.y, 0.1, places=5)
        for base, shaped in zip(blocks[0].data, blocks[1].data):
            self.assertAlmostEqual(shaped.co.z - base.co.z, 0.2, places=5)
        for vertex in output.data.vertices:
            self.assertAlmostEqual(sum(weight.weight for weight in vertex.groups), 1.0, places=5)
        self.assertEqual([group.name for group in output.vertex_groups], ["Left", "Right"])
        self.assertTrue(output.vertex_groups["Left"].lock_weight)
        self.assertEqual(bpy.ops.fishhwb.one_click_remesh(), {"FINISHED"})
        self.assertIn("Unchanged: 1", bpy.context.scene.fishhwb_last_result)

    def test_remesh_keeps_armature_and_does_not_bake_pose(self):
        bpy.ops.object.armature_add()
        rig = bpy.context.active_object
        rig.pose.bones[0].location.x = 2.0
        source = self.simple_mesh("RiggedSource")
        group = source.vertex_groups.new(name=rig.data.bones[0].name)
        group.add(list(range(len(source.data.vertices))), 1.0, 'REPLACE')
        modifier = source.modifiers.new("Rig", 'ARMATURE')
        modifier.object = rig
        modifier.use_deform_preserve_volume = True
        source.shape_key_add(name="Basis")
        smile = source.shape_key_add(name="Smile")
        for item in smile.data:
            item.co.z += 0.2
        curve = smile.driver_add('value')
        rig['SmileControl'] = 0.5
        variable = curve.driver.variables.new()
        variable.name = 'strength'
        variable.type = 'SINGLE_PROP'
        variable.targets[0].id = rig
        variable.targets[0].data_path = '["SmileControl"]'
        curve.driver.expression = 'strength'
        before = snapshot(source.data)
        bpy.context.scene.fishhwb_triangle_target = 200
        self.assertEqual(bpy.ops.fishhwb.one_click_remesh(), {"FINISHED"})
        output = bpy.context.active_object
        self.assertEqual(before, snapshot(source.data))
        self.assertEqual(rig.pose.bones[0].location.x, 2.0)
        self.assertEqual(output.modifiers[0].object, rig)
        self.assertTrue(output.modifiers[0].use_deform_preserve_volume)
        self.assertLess(max(v.co.x for v in output.data.vertices), 1.2)
        self.assertGreater(min(v.co.x for v in output.data.vertices), -1.2)
        self.assertEqual(output.data.shape_keys.animation_data.drivers[0].driver.expression, 'strength')
        self.assertEqual(output.data.shape_keys.animation_data.drivers[0].driver.variables[0].targets[0].id, rig)
        self.assertEqual(source.modifiers[0].object, rig)

    def test_remesh_copies_shape_key_action(self):
        source = self.simple_mesh("AnimatedShape")
        source.shape_key_add(name="Basis")
        key = source.shape_key_add(name="Smile")
        for item in key.data:
            item.co.z += 0.2
        key.value = 0.1
        key.keyframe_insert('value', frame=1)
        key.value = 0.8
        key.keyframe_insert('value', frame=10)
        action = source.data.shape_keys.animation_data.action
        bpy.context.scene.fishhwb_triangle_target = 200
        self.assertEqual(bpy.ops.fishhwb.one_click_remesh(), {"FINISHED"})
        copied = bpy.context.active_object.data.shape_keys.animation_data.action
        self.assertIsNot(copied, action)
        self.assertEqual(len(copied.fcurves[0].keyframe_points), 2)
        self.assertEqual(copied.fcurves[0].data_path, action.fcurves[0].data_path)
        self.assertEqual(source.data.shape_keys.animation_data.action, action)

    def test_remesh_rejects_unsupported_deformation_modifier_stack(self):
        source = self.simple_mesh("ModifierShape")
        source.shape_key_add(name="Basis")
        source.shape_key_add(name="Smile")
        source.modifiers.new("Mirror", 'MIRROR')
        before = snapshot(source.data)
        count = len(bpy.data.objects)
        self.assertEqual(bpy.ops.fishhwb.one_click_remesh(), {"CANCELLED"})
        self.assertEqual(before, snapshot(source.data))
        self.assertEqual(count, len(bpy.data.objects))

    def test_lod_still_rejects_deformation_mesh(self):
        source = self.simple_mesh("LODShapeSource")
        source.shape_key_add(name="Basis")
        source.shape_key_add(name="Smile")
        count = len(bpy.data.objects)
        self.assertEqual(bpy.ops.fishhwb.create_lods(), {"CANCELLED"})
        self.assertEqual(count, len(bpy.data.objects))

    def test_active_lod_generation_preserves_source(self):
        source = self.dense_mesh("LODSource")
        before = snapshot(source.data)
        source_count = addon.triangle_count(source.data)
        self.assertEqual(bpy.ops.fishhwb.create_lods(), {"FINISHED"})
        lod0 = bpy.context.active_object
        self.assertTrue(lod0.name.startswith("LODSource_LOD0"))
        self.assertEqual(before, snapshot(source.data))
        self.assertEqual(source_count, addon.triangle_count(lod0.data))
        collection = next(collection for collection in bpy.data.collections if collection.name.startswith("LODSource_LODs"))
        created = {obj.get("fishhwb_lod_level"): obj for obj in collection.objects}
        self.assertEqual(set(created), {0, 1, 2})
        lod1_count = addon.triangle_count(created[1].data)
        lod2_count = addon.triangle_count(created[2].data)
        self.assertLessEqual(lod1_count, max(1, int(source_count * 0.66)))
        self.assertLessEqual(lod2_count, max(1, int(source_count * 0.33)))
        self.assertIn("Changed: 1", bpy.context.scene.fishhwb_last_result)
        self.assertIn("Original object preserved", bpy.context.scene.fishhwb_last_result)

    def test_optional_collision_proxy_reuses_lod2_and_preserves_source(self):
        source = self.dense_mesh("ColliderSource")
        before = snapshot(source.data)
        bpy.context.scene.fishhwb_create_collision_proxy = True
        self.assertEqual(bpy.ops.fishhwb.create_lods(), {"FINISHED"})
        collection = next(collection for collection in bpy.data.collections if collection.name.startswith("ColliderSource_LODs"))
        proxy = next(obj for obj in collection.objects if obj.get("fishhwb_collision_proxy"))
        lod2 = next(obj for obj in collection.objects if obj.get("fishhwb_lod_level") == 2)
        self.assertTrue(proxy.name.startswith("ColliderSource_COLLIDER"))
        self.assertIsNot(proxy.data, lod2.data)
        self.assertEqual(snapshot(proxy.data), snapshot(lod2.data))
        self.assertEqual(addon.triangle_count(proxy.data), addon.triangle_count(lod2.data))
        self.assertTrue(proxy.hide_render)
        self.assertEqual(proxy.display_type, 'WIRE')
        self.assertEqual(before, snapshot(source.data))
        self.assertIn("Collision proxy created from LOD2", bpy.context.scene.fishhwb_last_result)
        count = len(bpy.data.objects)
        addon._select_only(bpy.context, source)
        self.assertEqual(bpy.ops.fishhwb.create_lods(), {"FINISHED"})
        self.assertEqual(count, len(bpy.data.objects))
        self.assertIn("Unchanged: 1", bpy.context.scene.fishhwb_last_result)

    def test_repeat_from_selected_generated_output_reuses_source(self):
        self.simple_mesh("RepeatSource")
        self.assertEqual(bpy.ops.fishhwb.one_click_remesh(), {"FINISHED"})
        output = bpy.context.active_object
        count = len(bpy.data.objects)
        self.assertEqual(bpy.ops.fishhwb.one_click_remesh(), {"FINISHED"})
        self.assertEqual(output, bpy.context.active_object)
        self.assertEqual(count, len(bpy.data.objects))
        self.assertIn("Unchanged: 1", bpy.context.scene.fishhwb_last_result)

    def test_unchanged_remesh_reuses_output(self):
        source = self.simple_mesh("CachedRemesh")
        self.assertEqual(bpy.ops.fishhwb.one_click_remesh(), {"FINISHED"})
        output = bpy.context.active_object
        count = len(bpy.data.objects)
        addon._select_only(bpy.context, source)
        self.assertEqual(bpy.ops.fishhwb.one_click_remesh(), {"FINISHED"})
        self.assertEqual(count, len(bpy.data.objects))
        self.assertEqual(output, bpy.context.active_object)
        self.assertIn("Unchanged: 1", bpy.context.scene.fishhwb_last_result)

    def test_changed_lod_source_replaces_only_owned_outputs(self):
        source = self.dense_mesh("ChangedLOD")
        self.assertEqual(bpy.ops.fishhwb.create_lods(), {"FINISHED"})
        count = len(bpy.data.objects)
        source.data.vertices[0].co.x += 0.1
        source.data.update()
        addon._select_only(bpy.context, source)
        self.assertEqual(bpy.ops.fishhwb.create_lods(), {"FINISHED"})
        self.assertEqual(count, len(bpy.data.objects))
        self.assertIn("Changed: 1", bpy.context.scene.fishhwb_last_result)

    def test_unchanged_lod_reuses_outputs_after_rename(self):
        source = self.dense_mesh("CachedLOD")
        self.assertEqual(bpy.ops.fishhwb.create_lods(), {"FINISHED"})
        output = bpy.context.active_object
        output.name = "RenamedLOD"
        count = len(bpy.data.objects)
        addon._select_only(bpy.context, source)
        self.assertEqual(bpy.ops.fishhwb.create_lods(), {"FINISHED"})
        self.assertEqual(count, len(bpy.data.objects))
        self.assertIn("Unchanged: 1", bpy.context.scene.fishhwb_last_result)

    def test_manual_lod_output_edits_are_preserved(self):
        source = self.dense_mesh("ManualLOD")
        self.assertEqual(bpy.ops.fishhwb.create_lods(), {"FINISHED"})
        output = bpy.context.active_object
        output.data.vertices[0].co.x += 0.2
        output.data.update()
        edited = snapshot(output.data)
        count = len(bpy.data.objects)
        addon._select_only(bpy.context, source)
        self.assertEqual(bpy.ops.fishhwb.create_lods(), {"CANCELLED"})
        self.assertEqual(edited, snapshot(output.data))
        self.assertEqual(count, len(bpy.data.objects))
        self.assertEqual(bpy.ops.fishhwb.reset_optimization_history(), {"FINISHED"})
        self.assertEqual(bpy.ops.fishhwb.create_lods(), {"FINISHED"})
        self.assertEqual(edited, snapshot(output.data))

    def test_detail_protection_blocks_topology_changes(self):
        source = self.dense_mesh("Protected")
        source.fishhwb_protect_detail = True
        before = snapshot(source.data)
        count = len(bpy.data.objects)
        self.assertEqual(bpy.ops.fishhwb.one_click_remesh(), {"CANCELLED"})
        self.assertEqual(bpy.ops.fishhwb.create_lods(), {"CANCELLED"})
        self.assertEqual(before, snapshot(source.data))
        self.assertEqual(count, len(bpy.data.objects))

    def test_remesh_triangle_budget_preserves_source(self):
        source = self.dense_mesh("BudgetSource")
        before = snapshot(source.data)
        bpy.context.scene.fishhwb_triangle_target = 200
        self.assertEqual(bpy.ops.fishhwb.one_click_remesh(), {"FINISHED"})
        output = bpy.context.active_object
        self.assertIsNot(output, source)
        self.assertGreater(addon.triangle_count(output.data), 0)
        self.assertLessEqual(addon.triangle_count(output.data), 200)
        self.assertEqual(before, snapshot(source.data))

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
    if not hasattr(bpy.types.Scene, "fishhwb_create_collision_proxy"):
        raise RuntimeError("Blender extension proxy did not register collision proxy settings")
finally:
    extension.unregister()
