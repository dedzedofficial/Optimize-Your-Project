"""Run with Blender --background --factory-startup --python-exit-code 1 --python scripts/test_blender.py."""
import sys
import unittest
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Blender'))
import vr_optimizer_blender as addon


def snapshot(mesh):
    return (
        tuple(tuple(v.co) for v in mesh.vertices),
        tuple(tuple(e.vertices) for e in mesh.edges),
        tuple((tuple(p.vertices), p.material_index) for p in mesh.polygons),
        tuple(tuple(tuple(v.uv) for v in uv.data) for uv in mesh.uv_layers),
        tuple(m.name if m else None for m in mesh.materials),
    )


class CleanupTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)

    def mesh(self, name='Prop', vertices=None, edges=(), faces=None):
        data = bpy.data.meshes.new(name)
        data.from_pydata(vertices or [(0, 0, 0), (1, 0, 0), (0, 1, 0)], edges,
                         [(0, 1, 2)] if faces is None else faces)
        data.update()
        obj = bpy.data.objects.new(name, data)
        bpy.context.collection.objects.link(obj)
        addon._select_only(bpy.context, obj)
        return obj

    def clean(self):
        self.assertEqual(bpy.ops.fishhwb.clean_selected_mesh(), {'FINISHED'})
        return bpy.context.active_object

    def test_cleanup_source_uv_materials_and_idempotence(self):
        source = self.mesh(vertices=[(0,0,0),(1,0,0),(0,1,0),(0,0,0),(1,1,0),
                                    (4,0,0),(5,0,0),(8,8,8)],
                           edges=[(5,6)], faces=[(0,1,2),(3,2,4)])
        for name in ('UnusedBefore', 'Used', 'UnusedAfter'):
            source.data.materials.append(bpy.data.materials.new(name))
        for face in source.data.polygons:
            face.material_index = 1
        uv = source.data.uv_layers.new(name='UVMap')
        for i, loop in enumerate(uv.data):
            loop.uv = (i / 10, i / 20)
        shared = bpy.data.objects.new('SharedMeshUser', source.data)
        bpy.context.collection.objects.link(shared)
        before = snapshot(source.data)
        cleaned = self.clean()
        self.assertEqual(before, snapshot(shared.data))
        self.assertIsNot(cleaned.data, source.data)
        self.assertEqual(before, snapshot(source.data))
        self.assertEqual(cleaned.name, 'Prop_Clean')
        self.assertEqual(len(cleaned.data.vertices), 4)
        self.assertEqual(len(cleaned.data.polygons), 2)
        self.assertEqual([m.name for m in cleaned.data.materials], ['Used'])
        self.assertTrue(all(p.material_index == 0 for p in cleaned.data.polygons))
        self.assertEqual(before[3], snapshot(cleaned.data)[3])
        self.assertIn('Changed: 1', bpy.context.scene.fishhwb_last_result)
        self.assertIn('exact duplicates merged: 1', bpy.context.scene.fishhwb_last_result)
        clean_before = snapshot(cleaned.data)
        twice = self.clean()
        self.assertEqual(clean_before, snapshot(twice.data))
        self.assertIn('Unchanged: 1', bpy.context.scene.fishhwb_last_result)
        addon._select_only(bpy.context, source)
        self.assertEqual(self.clean().name, 'Prop_Clean_001')
        self.assertEqual(bpy.context.mode, 'OBJECT')

    def test_valid_isolated_faces_and_nearby_vertices_survive(self):
        source = self.mesh(vertices=[(0,0,0),(1,0,0),(0,1,0),
                                    (0,0,0.00001),(1,0,0.00001),(0,1,0.00001)],
                           faces=[(0,2,1),(3,4,5)])
        before = snapshot(source.data)
        cleaned = self.clean()
        self.assertEqual(before, snapshot(cleaned.data))
        self.assertIn('Unchanged: 1', bpy.context.scene.fishhwb_last_result)

    def test_zero_area_and_wire_geometry(self):
        self.mesh(vertices=[(0,0,0),(1,0,0),(2,0,0),(0,1,0)], faces=[(0,1,2),(0,1,3)])
        cleaned = self.clean()
        self.assertEqual(len(cleaned.data.polygons), 1)
        self.assertIn('Zero-area faces removed: 1', bpy.context.scene.fishhwb_last_result)
        self.mesh(name='Wire', edges=[(0,1)], faces=[])
        self.assertEqual(len(self.clean().data.vertices), 0)

    def test_closed_component_normals(self):
        bpy.ops.mesh.primitive_cube_add()
        source = bpy.context.active_object
        source.data.polygons[0].flip()
        before = snapshot(source.data)
        cleaned = self.clean()
        self.assertEqual(before, snapshot(source.data))
        self.assertTrue(all(p.center.dot(p.normal) > 0 for p in cleaned.data.polygons))
        self.assertIn('Faces reoriented: 1', bpy.context.scene.fishhwb_last_result)

    def test_unsupported_inputs_create_nothing(self):
        for kind in ('shape_keys', 'vertex_group', 'armature', 'modifier', 'custom_normals', 'empty'):
            with self.subTest(kind=kind):
                source = self.mesh(name=kind)
                if kind == 'shape_keys': source.shape_key_add(name='Basis')
                elif kind == 'vertex_group': source.vertex_groups.new(name='Weights')
                elif kind == 'armature': source.modifiers.new('Rig', 'ARMATURE')
                elif kind == 'modifier': source.modifiers.new('Subsurf', 'SUBSURF')
                elif kind == 'custom_normals': source.data.normals_split_custom_set([(0,0,1)] * len(source.data.loops))
                else: source.data.clear_geometry()
                before = snapshot(source.data)
                objects, meshes = len(bpy.data.objects), len(bpy.data.meshes)
                self.assertEqual(bpy.ops.fishhwb.clean_selected_mesh(), {'CANCELLED'})
                self.assertEqual((objects,meshes), (len(bpy.data.objects),len(bpy.data.meshes)))
                self.assertEqual(before, snapshot(source.data))
                self.assertEqual(bpy.context.active_object, source)
                self.assertIn('Unsupported: 1', bpy.context.scene.fishhwb_last_result)

    def test_failure_rolls_back_copy_and_selection(self):
        other = self.mesh(name='Other')
        source = self.mesh()
        other.select_set(True)
        before = snapshot(source.data)
        objects, meshes = len(bpy.data.objects), len(bpy.data.meshes)
        original = addon._clean_mesh
        def fail(mesh):
            mesh.clear_geometry()
            raise RuntimeError('Injected cleanup failure')
        addon._clean_mesh = fail
        try:
            self.assertEqual(bpy.ops.fishhwb.clean_selected_mesh(), {'CANCELLED'})
        finally:
            addon._clean_mesh = original
        self.assertEqual((objects,meshes), (len(bpy.data.objects),len(bpy.data.meshes)))
        self.assertEqual(set(bpy.context.selected_objects), {source,other})
        self.assertEqual(bpy.context.active_object, source)
        self.assertEqual(before, snapshot(source.data))
        self.assertIn('Failed: 1', bpy.context.scene.fishhwb_last_result)

    def test_existing_merge_changes_duplicate_geometry(self):
        source = self.mesh(vertices=[(0,0,0),(1,0,0),(0,1,0),(0,0,0),(1,1,0)],
                           faces=[(0,1,2),(3,2,4)])
        before = snapshot(source.data)
        self.assertEqual(bpy.ops.fishhwb.merge_vertices(), {'FINISHED'})
        self.assertEqual(len(bpy.context.active_object.data.vertices), 4)
        self.assertEqual(before, snapshot(source.data))
        self.assertIn('Changed: 1', bpy.context.scene.fishhwb_last_result)

    def test_existing_merge_and_remesh_preserve_source(self):
        bpy.ops.mesh.primitive_cube_add()
        source = bpy.context.active_object
        before = snapshot(source.data)
        self.assertEqual(bpy.ops.fishhwb.merge_vertices(), {'FINISHED'})
        self.assertIsNot(source.data, bpy.context.active_object.data)
        self.assertIn('Unchanged: 1', bpy.context.scene.fishhwb_last_result)
        addon._select_only(bpy.context, source)
        self.assertEqual(bpy.ops.fishhwb.one_click_remesh(), {'FINISHED'})
        self.assertIsNot(source.data, bpy.context.active_object.data)
        self.assertGreater(len(bpy.context.active_object.data.polygons), 0)
        self.assertEqual(before, snapshot(source.data))


    def test_batch_cleanup_preserves_all_sources(self):
        first = self.mesh(name='BatchA', vertices=[(0,0,0),(1,0,0),(0,1,0),(0,0,0)],
                          faces=[(0,1,2),(3,1,2)])
        first_before = snapshot(first.data)
        second = self.mesh(name='BatchB')
        second_before = snapshot(second.data)
        first.select_set(True)
        second.select_set(True)
        bpy.context.view_layer.objects.active = first

        self.assertEqual(bpy.ops.fishhwb.clean_selected_meshes(), {'FINISHED'})
        names = {obj.name for obj in bpy.context.selected_objects}
        self.assertIn('BatchA_Clean', names)
        self.assertIn('BatchB_Clean', names)
        self.assertEqual(first_before, snapshot(first.data))
        self.assertEqual(second_before, snapshot(second.data))
        self.assertIn('Changed: 1', bpy.context.scene.fishhwb_last_result)
        self.assertIn('Unchanged: 1', bpy.context.scene.fishhwb_last_result)

    def test_game_ready_copy_preserves_source(self):
        source = self.mesh(
            name='GameReady',
            vertices=[(0,0,0),(1,0,0),(0,1,0),(0,0,0),(1,1,0)],
            faces=[(0,1,2),(3,2,4)])
        source.data.materials.append(bpy.data.materials.new('Used'))
        source.data.materials.append(bpy.data.materials.new('Unused'))
        for face in source.data.polygons:
            face.material_index = 0
        source.rotation_euler = (0.2, 0.3, 0.4)
        source.scale = (2.0, 1.5, 0.5)
        before = snapshot(source.data)
        before_rotation = tuple(source.rotation_euler)
        before_scale = tuple(source.scale)
        bpy.context.scene.fishhwb_apply_modifiers = True

        self.assertEqual(bpy.ops.fishhwb.create_game_ready_copy(), {'FINISHED'})
        output = bpy.context.active_object
        self.assertEqual(output.name, 'GameReady_GameReady')
        self.assertEqual(before, snapshot(source.data))
        self.assertEqual(before_rotation, tuple(source.rotation_euler))
        self.assertEqual(before_scale, tuple(source.scale))
        self.assertEqual(len(output.data.vertices), 4)
        self.assertEqual(len(output.data.materials), 1)
        self.assertIs(output.data.materials[0], source.data.materials[0])
        self.assertTrue(all(abs(v - 1.0) < 1e-5 for v in output.scale))
        self.assertTrue(all(abs(v) < 1e-5 for v in output.rotation_euler))
        self.assertIn('Changed: 1', bpy.context.scene.fishhwb_last_result)
        self.assertIn('Original object preserved', bpy.context.scene.fishhwb_last_result)

    def test_language_switch_and_heavy_mesh_review(self):
        bpy.context.scene.fishhwb_language = 'JA'
        self.assertEqual(addon.tr(bpy.context, 'language'), '言語')
        self.assertEqual(addon.tr(bpy.context, 'game_ready'), 'ゲーム用コピーを作成')
        heavy = self.mesh(name='Heavy')
        bpy.context.scene.fishhwb_heavy_triangles = 1
        self.assertEqual(bpy.ops.fishhwb.show_heavy_meshes(), {'FINISHED'})
        self.assertEqual(bpy.context.active_object, heavy)
        self.assertIn('Found 1 meshes', bpy.context.scene.fishhwb_last_result)


addon.register()
try:
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CleanupTests))
finally:
    addon.unregister()
if not result.wasSuccessful():
    raise RuntimeError('Blender regression checks failed')
