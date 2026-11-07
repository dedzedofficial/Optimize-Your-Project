"""Synthetic weighted-pose correspondence test for conservative pair preview.

This tests linear-blend deformation of unchanged vertices, NOT Blender armature
modifier support or genuine flow-aware retopology. No private FBX is needed.
Run with blender --background --python scripts/test_blender_pair_pose.py
"""
import sys
from pathlib import Path
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Blender"))
from vr_optimizer_blender.blender_pair_preview import create_blender_pair_preview


mesh = bpy.data.meshes.new("pose-source")
mesh.from_pydata(
    [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (2, 0, 0)],
    [], [(0, 1, 2), (0, 2, 3)])
mesh.update()
source = bpy.data.objects.new("pose-source", mesh)
bpy.context.scene.collection.objects.link(source)
left = source.vertex_groups.new(name="Left")
right = source.vertex_groups.new(name="Right")
left.add([0, 1, 2], 0.7, "REPLACE")
right.add([0, 1, 2], 0.3, "REPLACE")
right.add([3], 1.0, "REPLACE")
# Vertex 4 is intentionally unweighted, and must stay unweighted.
original_faces = tuple(tuple(p.vertices) for p in mesh.polygons)
preview, report = create_blender_pair_preview(source)
assert report["quad_joins"] == 1
assert len(preview.data.polygons) == 1
assert tuple(tuple(p.vertices) for p in mesh.polygons) == original_faces
assert preview.data is not mesh


def weights(obj, index):
    return {obj.vertex_groups[a.group].name: a.weight
            for a in obj.data.vertices[index].groups}


def deform(obj, transforms):
    positions = []
    for vertex in obj.data.vertices:
        influence = weights(obj, vertex.index)
        original = vertex.co.copy()
        if not influence:
            positions.append(original)
            continue
        # Preserve partial weights without implicit normalization.
        total = sum(influence.values())
        result = original * (1.0 - total)
        for name, weight in influence.items():
            result += (transforms[name] @ original) * weight
        positions.append(result)
    return positions


poses = (
    {"Left": Matrix.Identity(4), "Right": Matrix.Identity(4)},
    {"Left": Matrix.Translation((0.2, 0.0, 0.1)),
     "Right": Matrix.Translation((0.0, -0.4, 0.3))},
    {"Left": Matrix.Rotation(0.45, 4, "Z"),
     "Right": Matrix.Rotation(-0.65, 4, "X")},
)
for pose in poses:
    source_positions = deform(source, pose)
    preview_positions = deform(preview, pose)
    assert len(source_positions) == len(preview_positions)
    for original, result in zip(source_positions, preview_positions):
        assert (original - result).length < 1e-6
assert not weights(source, 4)
assert not weights(preview, 4)
print("Synthetic weighted-pose correspondence passed: 3 poses, 5 vertices")
