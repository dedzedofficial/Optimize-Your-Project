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
        scene.fishhwb_remesh_method = 'SURFACE'

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

    def test_smart_diagnoses_under_target_instead_of_silent_no_changes(self):
        source = self.cube()
        bpy.context.scene.fishhwb_triangle_target = 10000
        result = bpy.ops.fishhwb.smart_optimize(
            'EXEC_DEFAULT', clean_geometry=False, remesh=True,
            lods=False, atlas=False, lightmap=False)
        self.assertEqual(result, {'CANCELLED'})
        message = bpy.context.scene.fishhwb_last_result
        self.assertIn('12 triangles already within 10,000 target', message)
        self.assertIn('0 optimized', message)
        self.assertIs(bpy.context.active_object, source)

    def test_smart_rebuilds_under_triangle_target_when_opted_in(self):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0)
        source = bpy.context.active_object
        source.name = 'BelowTargetStatic'
        first_count = len(source.data.polygons)
        bpy.context.scene.fishhwb_triangle_target = 10000
        bpy.context.scene.fishhwb_remesh_method = 'REBUILD'
        self.assertEqual(bpy.ops.fishhwb.smart_optimize(
            'EXEC_DEFAULT', clean_geometry=False, remesh=True,
            lods=False, atlas=False, lightmap=False), {'FINISHED'})
        output = bpy.context.active_object
        self.assertIsNot(output, source)
        self.assertEqual(len(source.data.polygons), first_count)
        self.assertIn('remesh / retopology', bpy.context.scene.fishhwb_last_result)
        self.assertEqual(output.get('fishhwb_remesh_method_used'), 'REBUILD')

    def test_smart_rebuild_existing_remesh_preserves_old_result(self):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0)
        source = bpy.context.active_object
        source.name = 'Body.001'
        bpy.context.scene.fishhwb_triangle_target = 120
        self.assertEqual(bpy.ops.fishhwb.one_click_remesh(), {'FINISHED'})
        previous = bpy.context.active_object
        self.assertIsNot(previous, source)
        original_count = len(source.data.polygons)
        previous_coords = [tuple(vertex.co) for vertex in previous.data.vertices]
        bpy.context.scene.fishhwb_triangle_target = 10000
        bpy.context.scene.fishhwb_remesh_method = 'REBUILD'
        self.assertEqual(bpy.ops.fishhwb.smart_optimize(
            'EXEC_DEFAULT', clean_geometry=False, remesh=True,
            lods=False, atlas=False, lightmap=False), {'FINISHED'})
        new_result = bpy.context.active_object
        self.assertIsNot(new_result, previous)
        self.assertIsNot(new_result, source)
        self.assertIn(source.name, bpy.data.objects)
        self.assertIn(previous.name, bpy.data.objects)
        self.assertEqual(len(source.data.polygons), original_count)
        self.assertEqual(previous_coords,
                         [tuple(vertex.co) for vertex in previous.data.vertices])
        self.assertEqual(new_result.get('fishhwb_remesh_method_used'), 'REBUILD')
        self.assertNotIn('fishhwb_output_id', new_result)
        self.assertFalse(any('_SmartRebuildInput' in obj.name
                             for obj in bpy.data.objects))

    def test_smart_explains_rigged_retopology_skip(self):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0)
        source = bpy.context.active_object
        source.shape_key_add(name='Basis')
        source.shape_key_add(name='Smile')
        bpy.context.scene.fishhwb_triangle_target = 10000
        bpy.context.scene.fishhwb_remesh_method = 'REBUILD'
        self.assertEqual(bpy.ops.fishhwb.smart_optimize(
            'EXEC_DEFAULT', clean_geometry=False, remesh=True,
            lods=False, atlas=False, lightmap=False), {'CANCELLED'})
        self.assertIn('rigged/shape-key mesh cannot be rebuilt',
                      bpy.context.scene.fishhwb_last_result)

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
        proxies = [ob for ob in lod0.users_collection[0].objects
                   if ob.get('fishhwb_collision_proxy')]
        if proxies:
            self.assertEqual(len(proxies), 1)
            self.assertLessEqual(triangle_count(proxies[0].data), 60)
        else:
            self.assertTrue(lod0.users_collection[0].get('fishhwb_collision_warning'),
                            "An impossible collider budget must be reported.")
        self.assertEqual(len(source.data.polygons), before)

    def test_pbr_atlas_bakes_multi_material_scalar_channels(self):
        obj = self.cube()
        obj.name = "AtlasSource"
        m1 = bpy.data.materials.new("Atlas_A")
        m2 = bpy.data.materials.new("Atlas_B")
        for mat in (m1, m2):
            mat.use_nodes = True
        m1.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value = 0.2
        m2.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value = 0.8
        m2.node_tree.nodes.get('Principled BSDF').inputs['Metallic'].default_value = 0.4
        m2.node_tree.nodes.get('Principled BSDF').inputs['Alpha'].default_value = 0.5
        obj.data.materials.append(m1)
        obj.data.materials.append(m2)
        for index, poly in enumerate(obj.data.polygons):
            poly.material_index = index % 2
        bpy.context.scene.fishhwb_atlas_size = '1024'
        result = bpy.ops.fishhwb.merge_textures()
        self.assertEqual(result, {'FINISHED'})
        output = bpy.context.active_object
        self.assertIsNot(output, obj)
        self.assertEqual(len(obj.data.materials), 2)
        self.assertEqual(len(output.data.materials), 1)
        self.assertIn('Roughness', output.get('fishhwb_pbr_atlas_channels', ''))
        self.assertIn('Metallic', output.get('fishhwb_pbr_atlas_channels', ''))
        self.assertIn('Alpha', output.get('fishhwb_pbr_atlas_channels', ''))
        self.assertIn('AtlasUV', output.data.uv_layers)

    def test_remesh_rebuild_repairs_and_retops_on_copy(self):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0)
        source = bpy.context.active_object
        source.name = "RebuildSource"
        source_faces = len(source.data.polygons)
        source_coords = [tuple(vertex.co) for vertex in source.data.vertices]
        bpy.context.scene.fishhwb_remesh_method = 'REBUILD'
        bpy.context.scene.fishhwb_triangle_target = 100
        self.assertEqual(bpy.ops.fishhwb.one_click_remesh(), {'FINISHED'})
        result = bpy.context.active_object
        self.assertIsNot(source, result)
        self.assertEqual(len(source.data.polygons), source_faces)
        self.assertEqual(source_coords,
                         [tuple(vertex.co) for vertex in source.data.vertices])
        self.assertLessEqual(
            sum(max(0, len(poly.vertices)-2) for poly in result.data.polygons), 100)
        self.assertEqual(result.get('fishhwb_remesh_method_used'), 'REBUILD')
        self.assertIn(result.get('fishhwb_retopology_status'),
                      {'QUADRIFLOW', 'VOXEL_QUADS'})

    def test_remesh_rebuild_protects_rigged_shape_key_workflow(self):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0)
        source = bpy.context.active_object
        source.shape_key_add(name='Basis')
        key = source.shape_key_add(name='Smile')
        key.data[0].co.x += 0.1
        bpy.context.scene.fishhwb_remesh_method = 'REBUILD'
        bpy.context.scene.fishhwb_triangle_target = 100
        self.assertEqual(bpy.ops.fishhwb.one_click_remesh(), {'FINISHED'})
        result = bpy.context.active_object
        self.assertIsNot(result, source)
        self.assertEqual(result.get('fishhwb_remesh_method_used'), 'SURFACE')
        self.assertIsNotNone(result.data.shape_keys)
        self.assertIn('Smile', result.data.shape_keys.key_blocks)

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
