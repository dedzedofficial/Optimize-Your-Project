"""Fail-closed checks for data-only triangle-pair previews.

This module does not validate Blender UVs, weights, shape keys, or animation.
"""
from collections import Counter


def validate_preview(source_faces, output_faces, provenance):
    """Verify face coverage, unchanged boundary edges, and triangle budget.

    Vertex indices are deliberately preserved; callers must additionally
    compare vertex coordinates and all Blender data layers.
    """
    if len(output_faces) != len(provenance):
        raise ValueError("Preview provenance length mismatch")
    seen = []
    for output, group in zip(output_faces, provenance):
        if not isinstance(group, (tuple, list)) or len(group) not in (1, 2):
            raise ValueError("Invalid source face group")
        if any(type(i) is not int or not 0 <= i < len(source_faces)
               for i in group):
            raise ValueError("Invalid source face index")
        if len(set(group)) != len(group):
            raise ValueError("Duplicate source face")
        seen.extend(group)
        if len(group) == 1:
            if tuple(output) != tuple(source_faces[group[0]]):
                raise ValueError("Unpaired face changed")
        else:
            if any(len(source_faces[i]) != 3 for i in group) or len(output) != 4:
                raise ValueError("Only two triangles may form a quad")
            if len(set(output)) != 4:
                raise ValueError("Invalid quad")
            if set(output) != set(source_faces[group[0]]) | set(source_faces[group[1]]):
                raise ValueError("Quad vertex correspondence changed")
    if sorted(seen) != list(range(len(source_faces))):
        raise ValueError("Source faces lost or duplicated")

    def boundary(faces):
        edges = Counter()
        for face in faces:
            if len(face) < 3 or len(set(face)) != len(face):
                raise ValueError("Invalid polygon")
            for a, b in zip(face, face[1:] + face[:1]):
                if type(a) is not int or type(b) is not int or a < 0 or b < 0:
                    raise ValueError("Invalid vertex index")
                edges[tuple(sorted((a, b)))] += 1
        return Counter({e: n for e, n in edges.items() if n != 2})

    if boundary(source_faces) != boundary(output_faces):
        raise ValueError("Boundary or nonmanifold incidence changed")
    if sum(len(f) - 2 for f in source_faces) != sum(len(f) - 2 for f in output_faces):
        raise ValueError("Triangle-equivalent budget changed")
    return True
