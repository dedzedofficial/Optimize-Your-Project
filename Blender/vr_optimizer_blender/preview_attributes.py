"""Fail-closed material and loop-attribute checks for indexed face previews.

These checks compare caller-supplied data only. They do not prove Blender
custom-normal, UV, shape-key, or rig preservation.
"""


def validate_preview_attributes(source_faces, output_faces, provenance, *,
                                source_materials, output_materials,
                                source_corners, output_corners):
    """Validate exact per-face material and per-vertex corner correspondence.

    Each corner signature must contain every protected loop attribute the
    caller intends to preserve (for example all UV layers, split normals,
    colors). No interpolation or implicit data transfer is performed.
    """
    ns, no = len(source_faces), len(output_faces)
    if (len(provenance) != no or len(source_materials) != ns
            or len(source_corners) != ns or len(output_materials) != no
            or len(output_corners) != no):
        raise ValueError("Face or attribute layer count mismatch")
    seen = set()
    for face, group, material, corners in zip(
            output_faces, provenance, output_materials, output_corners):
        if (not isinstance(group, (tuple, list)) or len(group) not in (1, 2)
                or any(type(i) is not int or not 0 <= i < ns for i in group)
                or len(set(group)) != len(group)):
            raise ValueError("Invalid provenance")
        if len(face) < 3 or len(set(face)) != len(face):
            raise ValueError("Invalid output face")
        if not isinstance(corners, (tuple, list)) or len(corners) != len(face):
            raise ValueError("Invalid output corner layer")
        expected = {}
        for index in group:
            if index in seen:
                raise ValueError("Source face reused")
            seen.add(index)
            src_face = source_faces[index]
            src_corners = source_corners[index]
            if (len(src_face) < 3 or len(set(src_face)) != len(src_face)
                    or not isinstance(src_corners, (tuple, list))
                    or len(src_corners) != len(src_face)):
                raise ValueError("Invalid source corner layer")
            if source_materials[index] != material:
                raise ValueError("Material assignment changed")
            for vertex, signature in zip(src_face, src_corners):
                if vertex in expected and expected[vertex] != signature:
                    raise ValueError("Incompatible source corner signatures")
                expected[vertex] = signature
        if set(face) != set(expected):
            raise ValueError("Output vertex correspondence changed")
        for vertex, signature in zip(face, corners):
            if signature != expected[vertex]:
                raise ValueError("Loop attribute correspondence changed")
    if len(seen) != ns:
        raise ValueError("Source faces lost")
    return True
