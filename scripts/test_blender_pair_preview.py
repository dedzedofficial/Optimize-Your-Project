"""Blender runtime smoke test for fail-closed, non-destructive pair preview."""
import sys
from pathlib import Path
import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Blender"))
from vr_optimizer_blender.blender_pair_preview import create_blender_pair_preview

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
mesh = bpy.data.meshes.new("source")
mesh.from_pydata([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)], [],
                 [(0, 1, 2), (0, 2, 3)])
mesh.update()
obj = bpy.data.objects.new("source", mesh)
bpy.context.scene.collection.objects.link(obj)
uv = mesh.uv_layers.new(name="UVMap")
for poly in mesh.polygons:
    for li in poly.loop_indices:
        uv.data[li].uv = mesh.vertices[mesh.loops[li].vertex_index].co.xy
group = obj.vertex_groups.new(name="Bone")
group.add([0, 1], 0.75, 'REPLACE')
before = tuple(tuple(p.vertices) for p in mesh.polygons)
preview, report = create_blender_pair_preview(obj)
assert preview is not obj and preview.data is not mesh
assert tuple(tuple(p.vertices) for p in mesh.polygons) == before
assert len(mesh.polygons) == 2 and len(preview.data.polygons) == 1
assert report["quad_joins"] == 1
assert len(preview.data.uv_layers) == 1
assert len(preview.vertex_groups) == 1
assert abs(preview.data.uv_layers[0].data[0].uv.x) < 1e-6
assert abs(preview.vertex_groups[0].weight(0) - 0.75) < 1e-6
obj.parent = bpy.data.objects.new("rig-placeholder", None)
try:
    create_blender_pair_preview(obj)
except ValueError as exc:
    assert "Parented" in str(exc)
else:
    raise AssertionError("Expected fail-closed parent rejection")
assert len([o for o in bpy.data.objects if o.name.startswith("source_PairPreview")]) == 1
print("Blender pair preview smoke test passed")

# User-defined POINT attributes must not disappear on the output.
obj.parent = None
extra = mesh.attributes.new(name="vertex_payload", type='FLOAT', domain='POINT')
extra.data[0].value = 0.42
try:
    create_blender_pair_preview(obj)
except ValueError as exc:
    assert "vertex_payload" in str(exc)
else:
    raise AssertionError("Expected unsupported point attribute rejection")
mesh.attributes.remove(extra)

# Face smoothing changes loop normals; reject until explicitly transferred.
mesh.polygons[0].use_smooth = True
try:
    create_blender_pair_preview(obj)
except ValueError as exc:
    assert "Smooth shading" in str(exc)
else:
    raise AssertionError("Expected smooth shading rejection")
mesh.polygons[0].use_smooth = False
assert len([o for o in bpy.data.objects if o.name.startswith("source_PairPreview")]) == 1
