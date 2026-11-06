"""Blender bridge for conservative triangle-pair preview (not retopology).

Fail closed for unsupported mesh data. Never mutate the original mesh/object.
Requires Blender's bpy runtime; callers must inspect the resulting preview.
"""
from .validated_pair_preview import validated_pair_preview


def create_blender_pair_preview(source, *, minimum_dot=0.75):
    """Return (new_object, report), leaving source untouched.

    This bridge supports triangle-only face topology and preserves loose edges,
    but rejects unsupported normals, attributes and modifiers. Unsupported cases
    raise before creating a new object. No implicit destructive fallback.
    """
    import bpy

    if source.type != 'MESH':
        raise ValueError("Expected a mesh object")
    mesh = source.data
    # This preview copies geometry and a narrow set of explicit properties,
    # not arbitrary datablock/object metadata or animation bindings.
    # Reject such sources rather than producing an apparently equivalent mesh.
    if mesh.keys():
        raise ValueError("Mesh custom properties require explicit transfer")
    if mesh.animation_data is not None:
        raise ValueError("Mesh animation data require explicit transfer")
    if source.keys():
        raise ValueError("Object custom properties require explicit transfer")
    if source.animation_data is not None:
        raise ValueError("Object animation data require explicit transfer")
    if source.constraints:
        raise ValueError("Object constraints require explicit transfer")
    if any(len(p.vertices) != 3 for p in mesh.polygons):
        raise ValueError("Triangle-only input required for this preview")
    if getattr(mesh, "has_custom_normals", False):
        raise ValueError("Custom normals require an explicit transfer implementation")
    # Shape-key animation and ID properties are not represented by the
    # coordinate-only transfer below. Reject them before allocating output.
    keys = mesh.shape_keys
    if keys is not None:
        if not keys.use_relative:
            raise ValueError("Absolute shape keys require explicit timing transfer")
        if keys.animation_data is not None:
            raise ValueError("Animated shape keys require explicit action/driver transfer")
        if keys.keys():
            raise ValueError("Shape-key custom properties require explicit transfer")
        # ShapeKey blocks do not implement IDProperties in Blender 4.2-5.2.
        # Their RNA settings are copied below; only the Key datablock has
        # supported IDProperties to check.
    if source.parent is not None:
        raise ValueError("Parented objects require explicit transform and rig preservation")
    if source.modifiers:
        raise ValueError("Modifiers require an explicit preservation implementation")
    # Blender's corner-domain attributes include normals, colors and arbitrary
    # user data. Do not discard any such data silently.
    supported = {layer.name for layer in mesh.uv_layers}
    # Blender exposes built-in topology fields in mesh.attributes. All other
    # user-defined attributes must be transferred explicitly, not dropped.
    builtins = {"position", "material_index", "sharp_face", "sharp_edge", ".edge_verts", ".corner_vert", ".corner_edge"}
    for attr in mesh.attributes:
        if attr.name in builtins or attr.is_internal:
            continue
        if attr.domain == 'CORNER' and attr.name in supported:
            continue
        raise ValueError("Unsupported mesh attribute: " + attr.name +
                         " (" + attr.domain + ")")
    # Some Blender versions expose authored split normals through the native
    # custom_normal attribute instead of has_custom_normals.
    if mesh.attributes.get("custom_normal") is not None:
        raise ValueError("Custom normals require an explicit transfer implementation")

    if any(p.use_smooth for p in mesh.polygons):
        raise ValueError("Smooth shading requires explicit normal preservation")
    if any(e.use_edge_sharp for e in mesh.edges):
        raise ValueError("Sharp edges require explicit edge attribute transfer")

    # Preserve explicit edges not referenced by any face. Their endpoints keep
    # their original indices because the preview never reindexes vertices.
    face_edges = {mesh.loops[loop_index].edge_index
                  for poly in mesh.polygons for loop_index in poly.loop_indices}
    loose_edges = [edge.index for edge in mesh.edges if edge.index not in face_edges]
    loose_edge_pairs = [tuple(mesh.edges[index].vertices) for index in loose_edges]

    vertices = [tuple(v.co) for v in mesh.vertices]
    faces = [tuple(p.vertices) for p in mesh.polygons]
    materials = [p.material_index for p in mesh.polygons]
    corners = []
    for poly in mesh.polygons:
        corners.append(tuple(
            tuple((tuple(layer.data[loop_index].uv),
                   bool(layer.data[loop_index].pin_uv),
                   bool(getattr(layer.data[loop_index], 'select', False)),
                   bool(getattr(layer.data[loop_index], 'select_edge', False)))
                  for layer in mesh.uv_layers)
            for loop_index in poly.loop_indices
        ))
    result = validated_pair_preview(
        vertices, faces, materials=materials,
        corner_signatures=corners, minimum_dot=minimum_dot)

    new_mesh = bpy.data.meshes.new(mesh.name + "_PairPreview")
    new_object = None
    try:
        new_mesh.from_pydata(vertices, loose_edge_pairs, result["faces"])
        new_mesh.update()
        for material in mesh.materials:
            new_mesh.materials.append(material)
        for poly, material_index in zip(new_mesh.polygons, result["materials"]):
            poly.material_index = material_index
        for layer_index, layer in enumerate(mesh.uv_layers):
            target = new_mesh.uv_layers.new(name=layer.name)
            for poly, signatures in zip(new_mesh.polygons, result["corners"]):
                for loop_index, signature in zip(poly.loop_indices, signatures):
                    uv, pinned, selected, edge_selected = signature[layer_index]
                    target.data[loop_index].uv = uv
                    target.data[loop_index].pin_uv = pinned
                    if hasattr(target.data[loop_index], 'select'):
                        target.data[loop_index].select = selected
                    if hasattr(target.data[loop_index], 'select_edge'):
                        target.data[loop_index].select_edge = edge_selected
        if mesh.uv_layers:
            new_mesh.uv_layers.active_index = mesh.uv_layers.active_index
            for source_layer, target_layer in zip(mesh.uv_layers, new_mesh.uv_layers):
                target_layer.active_render = source_layer.active_render

        new_object = bpy.data.objects.new(source.name + "_PairPreview", new_mesh)
        new_object.matrix_world = source.matrix_world.copy()
        # Preserve relative shape-key coordinates on the unchanged vertex indices.
        if mesh.shape_keys is not None:
            keys = mesh.shape_keys
            if not keys.use_relative:
                raise ValueError("Absolute shape keys require explicit timing transfer")
            for key in keys.key_blocks:
                target = new_object.shape_key_add(name=key.name, from_mix=False)
                for index, point in enumerate(key.data):
                    target.data[index].co = point.co
                target.value = key.value
                target.slider_min = key.slider_min
                target.slider_max = key.slider_max
                target.mute = key.mute
                target.vertex_group = key.vertex_group
                target.interpolation = key.interpolation
            output_keys = new_object.data.shape_keys.key_blocks
            for key, target in zip(keys.key_blocks, output_keys):
                target.relative_key = output_keys[key.relative_key.name]
        # Copy vertex groups by index: unchanged vertex order and positions.
        for group in source.vertex_groups:
            new_group = new_object.vertex_groups.new(name=group.name)
            new_group.lock_weight = group.lock_weight
        for vertex in mesh.vertices:
            for assignment in vertex.groups:
                new_object.vertex_groups[assignment.group].add(
                    [vertex.index], assignment.weight, 'REPLACE')
        # Linking is the last operation so a failure cannot leave a scene object.
        collections = list(source.users_collection)
        if not collections:
            raise ValueError("Source must belong to a collection")
        for collection in collections:
            collection.objects.link(new_object)
        return new_object, result
    except Exception:
        if new_object is not None:
            bpy.data.objects.remove(new_object, do_unlink=True)
        # Remove the orphan mesh as well as the object on any failure.
        if new_mesh.users == 0:
            bpy.data.meshes.remove(new_mesh)
        raise
