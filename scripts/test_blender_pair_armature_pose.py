"""Actual Blender Armature evaluated-mesh parity for conservative face pairing.

This test intentionally checks a topology-only preview: identical vertex indices
and coordinates, not remeshing or reconstructed edge flow.
"""
import math
import bpy
from mathutils import Matrix

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
try:
    for root_angle, tip_angle in pose_cases:
        arm_obj.pose.bones["Root"].rotation_mode = 'XYZ'
        arm_obj.pose.bones["Tip"].rotation_mode = 'XYZ'
        arm_obj.pose.bones["Root"].rotation_euler.z = root_angle
        arm_obj.pose.bones["Tip"].rotation_euler.z = tip_angle
        bpy.context.view_layer.update()
        original = evaluated_positions(pose_obj)
        result = evaluated_positions(preview)
        assert len(original) == len(result) == 4
        for a, b in zip(original, result):
            error = max(abs(x-y) for x, y in zip(a, b))
            max_error = max(max_error, error)
            assert error <= 1e-5, (root_angle, tip_angle, error)
finally:
    for bone in arm_obj.pose.bones:
        bone.rotation_euler = (0, 0, 0)
    bpy.context.view_layer.update()

assert tuple(tuple(p.vertices) for p in pose_mesh.polygons) == source_faces
print("Actual Blender Armature pose parity passed: 3 poses, 4 vertices, max error", max_error)
