"""Blender bridge for conservative triangle-pair preview (not retopology).

Fail closed for unsupported mesh data. Never mutate the original mesh/object.
Requires Blender's bpy runtime; callers must inspect the resulting preview.
"""
from .validated_pair_preview import validated_pair_preview


def create_blender_pair_preview(source, *, minimum_dot=0.75):
    """Return (new_object, report), leaving source untouched.

    This first bridge supports triangle-only meshes without shape keys, custom
    split normals, non-UV corner attributes or modifiers. Unsupported cases
    raise before creating a new object. No implicit destructive fallback.
    """
    import bpy

    if source.type != 'MESH':
        raise ValueError("Expected a mesh object")
    mesh = source.data
    if any(len(p.vertices) != 3 for p in mesh.polygons):
        raise ValueError("Triangle-only input required for this preview")
    if mesh.shape_keys is not None:
        raise ValueError("Shape keys require an explicit transfer implementation")
    if getattr(mesh, "has_custom_normals", False):
        raise ValueError("Custom normals require an explicit transfer implementation")
    if source.modifiers:
        raise ValueError("Modifiers require an explicit preservation implementation")
    # Blender's corner-domain attributes include normals, colors and arbitrary
    # user data. Do not discard any such data silently.
    supported = {layer.name for layer in mesh.uv_layers}
    for attr in mesh.attributes:
        if attr.domain == 'CORNER' and attr.name not in supported and not attr.is_internal:
            raise ValueError("Unsupported corner attribute: " + attr.name)

    vertices = [tuple(v.co) for v in mesh.vertices]
    faces = [tuple(p.vertices) for p in mesh.polygons]
    materials = [p.material_index for p in mesh.polygons]
    corners = []
    for poly in mesh.polygons:
        corners.append(tuple(
            tuple(tuple(layer.data[loop_index].uv) for layer in mesh.uv_layers)
            for loop_index in poly.loop_indices
        ))
    result = validated_pair_preview(
        vertices, faces, materials=materials,
        corner_signatures=corners, minimum_dot=minimum_dot)

    new_mesh = bpy.data.meshes.new(mesh.name + "_PairPreview")
    new_object = None
    try:
        new_mesh.from_pydata(vertices, [], result["faces"])
        new_mesh.update()
        for material in mesh.materials:
            new_mesh.materials.append(material)
        for poly, material_index in zip(new_mesh.polygons, result["materials"]):
            poly.material_index = material_index
        for layer_index, layer in enumerate(mesh.uv_layers):
            target = new_mesh.uv_layers.new(name=layer.name)
            for poly, signatures in zip(new_mesh.polygons, result["corners"]):
                for loop_index, signature in zip(poly.loop_indices, signatures):
                    target.data[loop_index].uv = signature[layer_index]

        new_object = bpy.data.objects.new(source.name + "_PairPreview", new_mesh)
        new_object.matrix_world = source.matrix_world.copy()
        # Copy vertex groups by index: unchanged vertex order and positions.
        for group in source.vertex_groups:
            new_object.vertex_groups.new(name=group.name)
        for vertex in mesh.vertices:
            for assignment in vertex.groups:
                new_object.vertex_groups[assignment.group].add(
                    [vertex.index], assignment.weight, 'REPLACE')
        # Linking is the last operation so a failure cannot leave a scene object.
        collections = list(source.users_collection)
        if not collections:
            raise ValueError("Source must belong to a collection")
        collections[0].objects.link(new_object)
        return new_object, result
    except Exception:
        if new_object is not None:
            bpy.data.objects.remove(new_object, do_unlink=True)
        else:
            bpy.data.meshes.remove(new_mesh)
        raise
