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
vertex_parent_mesh = bpy.data.meshes.new("vertex-parent-mesh")
vertex_parent_mesh.from_pydata([(0, 0, 0)], [], [])
vertex_parent_obj = bpy.data.objects.new("vertex-parent", vertex_parent_mesh)
bpy.context.scene.collection.objects.link(vertex_parent_obj)
obj.parent = vertex_parent_obj
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
# Two successful previews exist (initial and parented). Rejections add none.
assert len([o for o in bpy.data.objects if o.name.startswith("source_PairPreview")]) == 2

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

# A BONE-parented mesh must fail closed: copying ordinary OBJECT parenting
# would lose the bone attachment even when the parent armature is retained.
armature_data = bpy.data.armatures.new("pair-preview-parent-armature")
armature_object = bpy.data.objects.new("pair-preview-parent-armature", armature_data)
bpy.context.scene.collection.objects.link(armature_object)
loose_obj.parent = armature_object
loose_obj.parent_type = 'BONE'
loose_obj.parent_bone = "MissingBone"
original_parent = loose_obj.parent
original_parent_type = loose_obj.parent_type
original_parent_bone = loose_obj.parent_bone
expect_metadata_rejection(loose_obj, "Bone/vertex parenting")
assert loose_obj.parent is original_parent
assert loose_obj.parent_type == original_parent_type
assert loose_obj.parent_bone == original_parent_bone
loose_obj.parent_type = 'OBJECT'
loose_obj.parent = None
print("Bone parenting fails closed without changing source hierarchy")

# Shape-key vertex-group references and relative-key dependencies must map
# to the independent preview rather than be lost during face reconstruction.
smile = mesh.shape_keys.key_blocks["Smile"]
smile.vertex_group = "Bone"
extra_key = obj.shape_key_add(name="SmileDetail")
extra_key.relative_key = smile
extra_key.data[1].co.z += 0.125
dependent_preview, _ = create_blender_pair_preview(obj)
preview_keys = dependent_preview.data.shape_keys.key_blocks
assert preview_keys["Smile"].vertex_group == "Bone"
assert preview_keys["SmileDetail"].relative_key.name == preview_keys["Smile"].name
assert abs(preview_keys["SmileDetail"].data[1].co.z - extra_key.data[1].co.z) < 1e-6
assert preview_keys["SmileDetail"] is not extra_key
assert mesh.shape_keys.key_blocks["SmileDetail"].relative_key.name == smile.name
print("Shape-key relative dependencies and vertex-group references preserved")

# Verify exact sparse skin-weight correspondence across multiple groups.
# The preview must not invent assignments for unweighted vertices or normalize
# intentional partial weights; vertex indices are deliberately unchanged.
weight_mesh = bpy.data.meshes.new("weight-correspondence-source")
weight_mesh.from_pydata([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
                         (2, 0, 0)], [], [(0, 1, 2), (0, 2, 3)])
weight_mesh.update()
weight_obj = bpy.data.objects.new("weight-correspondence-source", weight_mesh)
bpy.context.scene.collection.objects.link(weight_obj)
left = weight_obj.vertex_groups.new(name="Left")
right = weight_obj.vertex_groups.new(name="Right")
unused = weight_obj.vertex_groups.new(name="Unused")
left.add([0], 0.25, 'REPLACE')
right.add([0], 0.65, 'REPLACE')
left.add([1, 2], 1.0, 'REPLACE')
right.add([3], 0.4, 'REPLACE')
unused.lock_weight = True

def skin_snapshot(mesh_object):
    return tuple(tuple(sorted((mesh_object.vertex_groups[a.group].name,
                               round(a.weight, 7)) for a in v.groups))
                 for v in mesh_object.data.vertices)

weights_before = skin_snapshot(weight_obj)
weight_preview, weight_report = create_blender_pair_preview(weight_obj)
assert weight_report["quad_joins"] == 1
assert skin_snapshot(weight_obj) == weights_before
assert skin_snapshot(weight_preview) == weights_before
assert [g.name for g in weight_preview.vertex_groups] == ["Left", "Right", "Unused"]
assert weight_preview.vertex_groups["Unused"].lock_weight
assert not weight_preview.data.vertices[4].groups
# The output must be independent, including subsequent weight edits.
weight_preview.vertex_groups["Left"].add([0], 0.9, 'REPLACE')
assert skin_snapshot(weight_obj) == weights_before
assert skin_snapshot(weight_preview) != weights_before
print("Sparse multi-group skin-weight correspondence and isolation passed")


# Attribute discontinuities across a shared edge must block pairing.
# These are synthetic meshes, not a claim of deformation-aware retopology.
def seam_case(*, split_uv=False, split_material=False):
    seam_mesh = bpy.data.meshes.new("seam-test-mesh")
    seam_mesh.from_pydata([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],
                          [], [(0, 1, 2), (0, 2, 3)])
    seam_mesh.update()
    seam_obj = bpy.data.objects.new("seam-test-source", seam_mesh)
    bpy.context.scene.collection.objects.link(seam_obj)
    layer = seam_mesh.uv_layers.new(name="UVMap")
    for poly in seam_mesh.polygons:
        for loop_index in poly.loop_indices:
            vi = seam_mesh.loops[loop_index].vertex_index
            layer.data[loop_index].uv = seam_mesh.vertices[vi].co.xy
            if split_uv and poly.index == 1:
                layer.data[loop_index].uv.x += 0.125
    if split_material:
        seam_mesh.materials.append(bpy.data.materials.new("seam-mat-a"))
        seam_mesh.materials.append(bpy.data.materials.new("seam-mat-b"))
        seam_mesh.polygons[1].material_index = 1
    original_faces = tuple(tuple(poly.vertices) for poly in seam_mesh.polygons)
    original_uv = tuple(tuple(layer.data[li].uv) for li in range(len(seam_mesh.loops)))
    result_obj, result = create_blender_pair_preview(seam_obj)
    assert tuple(tuple(poly.vertices) for poly in seam_mesh.polygons) == original_faces
    assert tuple(tuple(layer.data[li].uv) for li in range(len(seam_mesh.loops))) == original_uv
    expected_joins = 0 if (split_uv or split_material) else 1
    assert result["quad_joins"] == expected_joins
    assert len(result_obj.data.polygons) == 2 - expected_joins
    assert result_obj.data is not seam_mesh
    return result

seam_case()
seam_case(split_uv=True)
seam_case(split_material=True)
print("UV seam and material boundary pairing guards passed")


# A single supported Armature modifier is transferred without touching the
# source rig, skin assignments or mesh. Unsupported envelope mode fails closed.
rig_data = bpy.data.armatures.new("pair-preview-deformation-rig")
rig_obj = bpy.data.objects.new("pair-preview-deformation-rig", rig_data)
bpy.context.scene.collection.objects.link(rig_obj)
rig_modifier = weight_obj.modifiers.new("Skin", 'ARMATURE')
rig_modifier.object = rig_obj
rig_modifier.use_deform_preserve_volume = True
rig_weights_before = skin_snapshot(weight_obj)
rigged_preview, rigged_report = create_blender_pair_preview(weight_obj)
assert rigged_report["quad_joins"] == 1
assert rigged_preview.data is not weight_obj.data
assert skin_snapshot(weight_obj) == rig_weights_before
assert skin_snapshot(rigged_preview) == rig_weights_before
assert len(rigged_preview.modifiers) == 1
assert rigged_preview.modifiers[0].type == 'ARMATURE'
assert rigged_preview.modifiers[0].object.name == rig_obj.name
assert rigged_preview.modifiers[0].use_deform_preserve_volume
assert rig_modifier.object.name == rig_obj.name
rig_modifier.use_bone_envelopes = True
rig_objects_before = set(bpy.data.objects.keys())
rig_meshes_before = set(bpy.data.meshes.keys())
try:
    create_blender_pair_preview(weight_obj)
except ValueError as exc:
    assert "Armature modifier settings" in str(exc), str(exc)
else:
    raise AssertionError("Envelope deformation must fail closed")
assert set(bpy.data.objects.keys()) == rig_objects_before
assert set(bpy.data.meshes.keys()) == rig_meshes_before
assert skin_snapshot(weight_obj) == rig_weights_before
rig_modifier.use_bone_envelopes = False
# A vertex-group mask changes the deformation semantics and must be rejected
# before any preview datablocks are allocated.
rig_modifier.vertex_group = weight_obj.vertex_groups[0].name
mask_objects_before = set(bpy.data.objects.keys())
mask_meshes_before = set(bpy.data.meshes.keys())
try:
    create_blender_pair_preview(weight_obj)
except ValueError as exc:
    assert "Armature modifier settings" in str(exc), str(exc)
else:
    raise AssertionError("Masked Armature deformation must fail closed")
assert set(bpy.data.objects.keys()) == mask_objects_before
assert set(bpy.data.meshes.keys()) == mask_meshes_before
rig_modifier.vertex_group = ""
weight_obj.modifiers.remove(rig_modifier)
assert create_blender_pair_preview(weight_obj)[1]["quad_joins"] == 1
print("Single Armature modifier transfer, unsupported settings and source isolation passed")

# Exercise weighted-pose correspondence in the existing Blender CI entrypoint.
import runpy
runpy.run_path(str(Path(__file__).with_name('test_blender_pair_pose.py')), run_name='__main__')

# Compare evaluated Blender Armature deformation on actual posed bones.
runpy.run_path(str(Path(__file__).with_name('test_blender_pair_armature_pose.py')), run_name='__main__')
