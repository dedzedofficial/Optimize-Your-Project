"""Blender regression: a seam in ANY UV map must prevent unsafe pairing."""
import bpy
from vr_optimizer_blender.blender_pair_preview import create_blender_pair_preview


def run_case(split_second_layer):
    mesh = bpy.data.meshes.new("pair-multi-uv-source")
    mesh.from_pydata([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],
                     [], [(0, 1, 2), (0, 2, 3)])
    mesh.update()
    source = bpy.data.objects.new("pair-multi-uv-source", mesh)
    bpy.context.scene.collection.objects.link(source)
    first = mesh.uv_layers.new(name="Base")
    second = mesh.uv_layers.new(name="Detail")
    for polygon in mesh.polygons:
        for index in polygon.loop_indices:
            vertex = mesh.loops[index].vertex_index
            coordinate = mesh.vertices[vertex].co
            first.data[index].uv = (coordinate.x, coordinate.y)
            second.data[index].uv = (coordinate.x * 0.5, coordinate.y * 0.5)
            if split_second_layer and polygon.index == 1:
                second.data[index].uv.x += 0.2
    mesh.uv_layers.active_index = 1
    second.active_render = True
    first.active_render = False
    original_faces = tuple(tuple(p.vertices) for p in mesh.polygons)
    original_uv = tuple(
        tuple(tuple(layer.data[i].uv) for i in range(len(mesh.loops)))
        for layer in mesh.uv_layers
    )
    result, report = create_blender_pair_preview(source)
    expected = 0 if split_second_layer else 1
    assert report["quad_joins"] == expected, report
    assert len(result.data.polygons) == 2 - expected
    assert [layer.name for layer in result.data.uv_layers] == ["Base", "Detail"]
    assert result.data.uv_layers.active_index == 1
    assert [layer.active_render for layer in result.data.uv_layers] == [False, True]
    assert tuple(tuple(p.vertices) for p in mesh.polygons) == original_faces
    assert tuple(
        tuple(tuple(layer.data[i].uv) for i in range(len(mesh.loops)))
        for layer in mesh.uv_layers
    ) == original_uv
    assert result.data is not mesh
    if not split_second_layer:
        for layer_index in range(2):
            src_by_vertex = {
                mesh.loops[i].vertex_index: tuple(mesh.uv_layers[layer_index].data[i].uv)
                for i in range(len(mesh.loops))
            }
            for loop in result.data.loops:
                actual = result.data.uv_layers[layer_index].data[loop.index].uv
                expected_uv = src_by_vertex[loop.vertex_index]
                assert max(abs(a-b) for a,b in zip(actual, expected_uv)) < 1e-6
    bpy.data.objects.remove(result, do_unlink=True)
    bpy.data.objects.remove(source, do_unlink=True)
    bpy.data.meshes.remove(mesh)


run_case(False)
run_case(True)
print("Multiple UV maps: continuous join and secondary-layer seam rejection passed")
