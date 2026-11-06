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
for li in range(len(mesh.loops)):
    vertex_index = mesh.loops[li].vertex_index
    uv.data[li].pin_uv = vertex_index == 1
    if hasattr(uv.data[li], 'select'):
        uv.data[li].select = vertex_index == 2
    if hasattr(uv.data[li], 'select_edge'):
        uv.data[li].select_edge = vertex_index == 3
group = obj.vertex_groups.new(name="Bone")
group.add([0, 1], 0.75, 'REPLACE')
before = tuple(tuple(p.vertices) for p in mesh.polygons)
preview, report = create_blender_pair_preview(obj)
assert preview is not obj and preview.data is not mesh
assert tuple(tuple(p.vertices) for p in mesh.polygons) == before
assert len(mesh.polygons) == 2 and len(preview.data.polygons) == 1
assert report["quad_joins"] == 1
assert len(preview.data.uv_layers) == 1
assert preview.data.uv_layers.active_index == mesh.uv_layers.active_index
assert preview.data.uv_layers[0].active_render == mesh.uv_layers[0].active_render
for poly in preview.data.polygons:
    for li in poly.loop_indices:
        vi = preview.data.loops[li].vertex_index
        loop_uv = preview.data.uv_layers[0].data[li]
        assert bool(loop_uv.pin_uv) == (vi == 1)
        if hasattr(loop_uv, 'select'):
            assert bool(loop_uv.select) == (vi == 2)
        if hasattr(loop_uv, 'select_edge'):
            assert bool(loop_uv.select_edge) == (vi == 3)
assert len(preview.vertex_groups) == 1
assert abs(preview.data.uv_layers[0].data[0].uv.x) < 1e-6
assert abs(preview.vertex_groups[0].weight(0) - 0.75) < 1e-6
parent = bpy.data.objects.new("rig-placeholder", None)
bpy.context.scene.collection.objects.link(parent)
parent.location = (3.0, -2.0, 1.0)
obj.parent = parent
obj.matrix_parent_inverse = parent.matrix_world.inverted()
obj.location = (0.25, 0.5, -0.75)
parent_preview, parent_report = create_blender_pair_preview(obj)
assert parent_report["quad_joins"] == 1
assert parent_preview.parent is parent
assert parent_preview.parent_type == obj.parent_type
for left, right in zip(parent_preview.matrix_parent_inverse, obj.matrix_parent_inverse):
    assert max(abs(a - b) for a, b in zip(left, right)) < 1e-6
for left, right in zip(parent_preview.matrix_basis, obj.matrix_basis):
    assert max(abs(a - b) for a, b in zip(left, right)) < 1e-6
for left, right in zip(parent_preview.matrix_world, obj.matrix_world):
    assert max(abs(a - b) for a, b in zip(left, right)) < 1e-6
assert parent_preview.data is not mesh
assert obj.parent is parent
# Vertex parenting is not equivalent to object parenting: the source can
# follow a deforming vertex, so it must fail before preview allocation.
obj.parent = parent
obj.parent_type = 'VERTEX'
obj.parent_vertices = (0, 0, 0)
old_objects = set(bpy.data.objects.keys())
old_meshes = set(bpy.data.meshes.keys())
try:
    create_blender_pair_preview(obj)
except ValueError as exc:
    assert "Bone/vertex parenting" in str(exc)
else:
    raise AssertionError("Expected vertex-parent rejection")
assert set(bpy.data.objects.keys()) == old_objects
assert set(bpy.data.meshes.keys()) == old_meshes
obj.parent_type = 'OBJECT'
obj.parent = None
obj.location = (0, 0, 0)
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

# A late failure after mesh/object allocation must not leak either datablock.
existing_objects = set(bpy.data.objects.keys())
existing_meshes = set(bpy.data.meshes.keys())
obj.users_collection[0].objects.unlink(obj)
try:
    create_blender_pair_preview(obj)
except ValueError as exc:
    assert "collection" in str(exc)
else:
    raise AssertionError("Expected missing collection rejection")
finally:
    bpy.context.scene.collection.objects.link(obj)
assert set(bpy.data.objects.keys()) == existing_objects
assert set(bpy.data.meshes.keys()) == existing_meshes

# Collection preflight must run before topology validation and allocation.
# Even a non-triangle unlinked source should fail on collection membership.
obj.users_collection[0].objects.unlink(obj)
mesh.polygons[0].use_smooth = True
try:
    expect_collection_error = False
    try:
        create_blender_pair_preview(obj)
    except ValueError as exc:
        expect_collection_error = "collection" in str(exc)
    assert expect_collection_error
    assert set(bpy.data.objects.keys()) == existing_objects
    assert set(bpy.data.meshes.keys()) == existing_meshes
finally:
    mesh.polygons[0].use_smooth = False
    bpy.context.scene.collection.objects.link(obj)

# Relative shape keys and group lock settings are point-domain and must survive.
group.lock_weight = True
basis = obj.shape_key_add(name="Basis")
smile = obj.shape_key_add(name="Smile")
smile.data[0].co.z = 0.25
smile.value = 0.6
smile.slider_max = 2.0
shape_preview, _ = create_blender_pair_preview(obj)
assert shape_preview.data.shape_keys is not mesh.shape_keys
assert [k.name for k in shape_preview.data.shape_keys.key_blocks] == ["Basis", "Smile"]
assert abs(shape_preview.data.shape_keys.key_blocks["Smile"].data[0].co.z - 0.25) < 1e-6
assert abs(shape_preview.data.shape_keys.key_blocks["Smile"].value - 0.6) < 1e-6
assert shape_preview.vertex_groups["Bone"].lock_weight
assert abs(mesh.shape_keys.key_blocks["Smile"].data[0].co.z - 0.25) < 1e-6

# Shape-key metadata must not silently disappear from a new preview.
def expect_shape_key_rejection(message):
    old_objects = set(bpy.data.objects.keys())
    old_meshes = set(bpy.data.meshes.keys())
    try:
        create_blender_pair_preview(obj)
    except ValueError as exc:
        assert message in str(exc), str(exc)
    else:
        raise AssertionError("Expected rejection: " + message)
    assert set(bpy.data.objects.keys()) == old_objects
    assert set(bpy.data.meshes.keys()) == old_meshes

mesh.shape_keys["test_payload"] = 1
expect_shape_key_rejection("Shape-key custom properties")
del mesh.shape_keys["test_payload"]
mesh.shape_keys.animation_data_create()
expect_shape_key_rejection("Animated shape keys")
mesh.shape_keys.animation_data_clear()

# A standalone edge must survive reconstruction without modifying the source.
loose_mesh = bpy.data.meshes.new("loose_edge_source")
loose_mesh.from_pydata([(0, 0, 0), (1, 0, 0), (1, 1, 0),
                        (0, 1, 0), (2, 0, 0), (3, 0, 0)],
                       [(4, 5)], [(0, 1, 2), (0, 2, 3)])
loose_mesh.update()
loose_obj = bpy.data.objects.new("loose_edge_source", loose_mesh)
bpy.context.scene.collection.objects.link(loose_obj)
source_edges = {tuple(sorted(edge.vertices)) for edge in loose_mesh.edges}
loose_preview, loose_report = create_blender_pair_preview(loose_obj)
output_edges = {tuple(sorted(edge.vertices)) for edge in loose_preview.data.edges}
assert (4, 5) in output_edges
assert output_edges == source_edges - {(0, 2)}
assert len(loose_mesh.edges) == 6
assert loose_report["quad_joins"] == 1
assert len(loose_preview.data.vertices) == len(loose_mesh.vertices)
print("Loose edge preservation passed")

# Metadata that cannot be copied must be rejected before allocating objects.
def expect_metadata_rejection(source, expected):
    old_objects = set(bpy.data.objects.keys())
    old_meshes = set(bpy.data.meshes.keys())
    try:
        create_blender_pair_preview(source)
    except ValueError as exc:
        assert expected in str(exc), str(exc)
    else:
        raise AssertionError("Expected metadata rejection: " + expected)
    assert set(bpy.data.objects.keys()) == old_objects
    assert set(bpy.data.meshes.keys()) == old_meshes

loose_mesh["author_tag"] = "keep"
expect_metadata_rejection(loose_obj, "Mesh custom properties")
del loose_mesh["author_tag"]
loose_obj["author_tag"] = "keep"
expect_metadata_rejection(loose_obj, "Object custom properties")
del loose_obj["author_tag"]
loose_obj.animation_data_create()
expect_metadata_rejection(loose_obj, "Object animation data")
loose_obj.animation_data_clear()
loose_mesh.animation_data_create()
expect_metadata_rejection(loose_obj, "Mesh animation data")
loose_mesh.animation_data_clear()
constraint = loose_obj.constraints.new('LIMIT_LOCATION')
expect_metadata_rejection(loose_obj, "Object constraints")
loose_obj.constraints.remove(constraint)
assert create_blender_pair_preview(loose_obj)[1]["quad_joins"] == 1
print("Metadata rejection and recovery passed")

# Multi-collection membership must be preserved, not reduced to the first.
secondary = bpy.data.collections.new("pair-preview-secondary")
bpy.context.scene.collection.children.link(secondary)
secondary.objects.link(loose_obj)
membership_before = {collection.name for collection in loose_obj.users_collection}
multi_preview, multi_report = create_blender_pair_preview(loose_obj)
assert multi_report["quad_joins"] == 1
assert {collection.name for collection in multi_preview.users_collection} == membership_before
assert {collection.name for collection in loose_obj.users_collection} == membership_before
assert multi_preview.data is not loose_mesh
print("Multiple collection memberships preserved")

# Object-linked material overrides must retain their effective material and
# link mode independently of the mesh's shared material slots.
material = bpy.data.materials.new("pair-preview-mesh-material")
override = bpy.data.materials.new("pair-preview-object-override")
loose_mesh.materials.append(material)
loose_obj.material_slots[0].link = 'OBJECT'
loose_obj.material_slots[0].material = override
override_preview, override_report = create_blender_pair_preview(loose_obj)
assert override_report["quad_joins"] == 1
assert override_preview.material_slots[0].link == 'OBJECT'
assert override_preview.material_slots[0].material is override
assert override_preview.data.materials[0] is material
assert loose_obj.material_slots[0].link == 'OBJECT'
assert loose_obj.material_slots[0].material is override
# Mutating the new object's override must not change the original.
override_preview.material_slots[0].material = material
assert loose_obj.material_slots[0].material is override
loose_obj.material_slots[0].link = 'DATA'
data_preview, _ = create_blender_pair_preview(loose_obj)
assert data_preview.material_slots[0].link == 'DATA'
assert data_preview.material_slots[0].material is material
print("Object-linked and mesh-linked material preservation passed")
