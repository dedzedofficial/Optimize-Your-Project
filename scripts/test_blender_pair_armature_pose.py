"""Actual Blender Armature evaluated-mesh parity for conservative face pairing.

This test intentionally checks a topology-only preview: identical vertex indices
and coordinates, not remeshing or reconstructed edge flow.
"""
import math
import bpy
from mathutils import Matrix
from vr_optimizer_blender.blender_pair_preview import create_blender_pair_preview

# Imported by the existing Blender smoke entrypoint.
arm_data = bpy.data.armatures.new("pose-parity-rig")
arm_obj = bpy.data.objects.new("pose-parity-rig", arm_data)
bpy.context.scene.collection.objects.link(arm_obj)
bpy.ops.object.select_all(action='DESELECT')
arm_obj.select_set(True)
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='EDIT')
for name, head, tail in (
    ("Root", (0, 0, 0), (0, 1, 0)),
    ("Tip", (0, 1, 0), (0, 2, 0)),
):
    bone = arm_data.edit_bones.new(name)
    bone.head, bone.tail = head, tail
bpy.ops.object.mode_set(mode='OBJECT')

pose_mesh = bpy.data.meshes.new("pose-parity-source")
pose_mesh.from_pydata(
    [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],
    [], [(0, 1, 2), (0, 2, 3)]
)
pose_mesh.update()
pose_obj = bpy.data.objects.new("pose-parity-source", pose_mesh)
bpy.context.scene.collection.objects.link(pose_obj)
root_group = pose_obj.vertex_groups.new(name="Root")
tip_group = pose_obj.vertex_groups.new(name="Tip")
root_group.add([0, 1], 1.0, 'REPLACE')
root_group.add([2, 3], 0.35, 'REPLACE')
tip_group.add([2, 3], 0.65, 'REPLACE')
basis = pose_obj.shape_key_add(name="Basis")
flex = pose_obj.shape_key_add(name="Flex")
flex.data[2].co.z += 0.3
flex.data[3].co.x -= 0.15
modifier = pose_obj.modifiers.new("Skin", 'ARMATURE')
modifier.object = arm_obj
modifier.use_vertex_groups = True
modifier.use_bone_envelopes = False

source_faces = tuple(tuple(p.vertices) for p in pose_mesh.polygons)
preview, report = create_blender_pair_preview(pose_obj)
assert report["quad_joins"] == 1
assert preview.data is not pose_mesh
assert tuple(tuple(p.vertices) for p in pose_mesh.polygons) == source_faces
assert len(preview.modifiers) == 1
assert [key.name for key in preview.data.shape_keys.key_blocks] == ["Basis", "Flex"]
assert preview.modifiers[0].object.name == arm_obj.name

def evaluated_positions(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    evaluated_mesh = evaluated.to_mesh()
    try:
        return tuple(tuple(obj.matrix_world @ v.co) for v in evaluated_mesh.vertices)
    finally:
        evaluated.to_mesh_clear()

pose_cases = (
    (0.0, 0.0),
    (math.radians(30), math.radians(-20)),
    (math.radians(-35), math.radians(40)),
)
max_error = 0.0
# A parity test that only compares two inert objects can pass even if the rig
# or shape keys never deform. Require independently observable movement.
reference_positions = None
posed_positions = None
flexed_positions = None
try:
    for flex_value in (0.0, 0.8):
      pose_mesh.shape_keys.key_blocks["Flex"].value = flex_value
      preview.data.shape_keys.key_blocks["Flex"].value = flex_value
      for root_angle, tip_angle in pose_cases:
          arm_obj.pose.bones["Root"].rotation_mode = 'XYZ'
          arm_obj.pose.bones["Tip"].rotation_mode = 'XYZ'
          arm_obj.pose.bones["Root"].rotation_euler.z = root_angle
          arm_obj.pose.bones["Tip"].rotation_euler.z = tip_angle
          bpy.context.view_layer.update()
          original = evaluated_positions(pose_obj)
          if flex_value == 0.0 and root_angle == 0.0 and tip_angle == 0.0:
              reference_positions = original
          elif flex_value == 0.0 and posed_positions is None:
              posed_positions = original
          elif flex_value > 0.0 and root_angle == 0.0 and tip_angle == 0.0:
              flexed_positions = original
          result = evaluated_positions(preview)
          assert len(original) == len(result) == 4
          for a, b in zip(original, result):
              error = max(abs(x-y) for x, y in zip(a, b))
              max_error = max(max_error, error)
              assert error <= 1e-5, (root_angle, tip_angle, error)
finally:
    pose_mesh.shape_keys.key_blocks["Flex"].value = 0.0
    preview.data.shape_keys.key_blocks["Flex"].value = 0.0
    for bone in arm_obj.pose.bones:
        bone.rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()

assert reference_positions is not None and posed_positions is not None and flexed_positions is not None

def largest_displacement(a, b):
    return max(max(abs(x - y) for x, y in zip(v1, v2))
               for v1, v2 in zip(a, b))

pose_displacement = largest_displacement(reference_positions, posed_positions)
shape_displacement = largest_displacement(reference_positions, flexed_positions)
assert pose_displacement > 1e-3, ("Armature did not deform the mesh", pose_displacement)
assert shape_displacement > 1e-3, ("Shape key did not deform the mesh", shape_displacement)
assert tuple(tuple(p.vertices) for p in pose_mesh.polygons) == source_faces
print("Pose displacement:", pose_displacement, "shape-key displacement:", shape_displacement)
print("Actual Blender Armature pose parity passed: 6 pose/shape-key combinations, 4 vertices, max error", max_error)
