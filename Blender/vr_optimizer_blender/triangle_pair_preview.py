"""Conservative triangle pairing for a non-destructive topology-cleanup preview.

This is NOT quad retopology: existing vertices and triangle geometry stay intact.
Caller must validate UV/corner normals, material assignment and rig attributes.
"""
from collections import defaultdict
import math


def propose_pairs(vertices, faces, *, materials=None, corner_signatures=None,
                  protected_edges=(), minimum_dot=0.75):
    """Return deterministic disjoint triangle pairs, never modifying input.

    corner_signatures: optional per-face tuple of per-corner hashable values,
    such as (UV, split normal, color). Both ends of a shared edge must match.
    Faces must be triangles with valid, distinct vertex indices.
    """
    if not math.isfinite(minimum_dot) or not -1 <= minimum_dot <= 1:
        raise ValueError("Invalid coplanarity threshold")
    n = len(vertices)
    for vertex in vertices:
        if (len(vertex) != 3 or
                any(not isinstance(c, (int, float)) or
                    isinstance(c, bool) or not math.isfinite(c)
                    for c in vertex)):
            raise ValueError("Expected finite 3D vertex coordinates")
    protected = set()
    for edge in protected_edges:
        if (len(edge) != 2 or
                any(type(v) is not int or not 0 <= v < n for v in edge)
                or edge[0] == edge[1]):
            raise ValueError("Invalid protected edge")
        protected.add(tuple(sorted(edge)))
    if materials is not None and len(materials) != len(faces):
        raise ValueError("Material count mismatch")
    if corner_signatures is not None and len(corner_signatures) != len(faces):
        raise ValueError("Corner signature count mismatch")
    edges = defaultdict(list)
    for fi, face in enumerate(faces):
        if len(face) != 3 or len(set(face)) != 3 or any(
                type(v) is not int or not 0 <= v < n for v in face):
            raise ValueError("Expected valid indexed triangles")
        if corner_signatures is not None and len(corner_signatures[fi]) != 3:
            raise ValueError("Invalid corner signatures")
        for a, b in zip(face, face[1:] + face[:1]):
            edges[tuple(sorted((a, b)))].append(fi)

    def normal(face):
        a, b, c = (vertices[i] for i in face)
        u = [b[k] - a[k] for k in range(3)]
        v = [c[k] - a[k] for k in range(3)]
        cross = (u[1]*v[2]-u[2]*v[1],
                 u[2]*v[0]-u[0]*v[2],
                 u[0]*v[1]-u[1]*v[0])
        length = math.sqrt(sum(x*x for x in cross))
        return tuple(x/length for x in cross) if length > 1e-12 else None

    normals = [normal(f) for f in faces]
    choices = []
    for edge, adjacent in edges.items():
        if len(adjacent) != 2 or edge in protected:
            continue
        i, j = adjacent
        if materials is not None and materials[i] != materials[j]:
            continue
        if normals[i] is None or normals[j] is None:
            continue
        dot = sum(a*b for a, b in zip(normals[i], normals[j]))
        if dot < minimum_dot:
            continue
        # Opposite winding on the shared edge is mandatory.
        def direction(face):
            return next((1 if (a, b) == edge else -1)
                        for a, b in zip(face, face[1:] + face[:1])
                        if tuple(sorted((a, b))) == edge)
        if direction(faces[i]) == direction(faces[j]):
            continue
        if corner_signatures is not None:
            def sig(fi, v):
                return corner_signatures[fi][faces[fi].index(v)]
            if any(sig(i, v) != sig(j, v) for v in edge):
                continue
        # A duplicate vertex across the two faces is a folded or duplicate face.
        if len(set(faces[i]) | set(faces[j])) != 4:
            continue
        # Check that the four outer vertices form a strictly convex loop.
        # Coplanarity alone is insufficient: concave pairs create poor quads,
        # and a collapsed corner can corrupt downstream triangulation.
        first = faces[i]
        second = faces[j]
        boundary = []
        for face in (first, second):
            for u, v in zip(face, face[1:] + face[:1]):
                if tuple(sorted((u, v))) != edge:
                    boundary.append((u, v))
        successors = {u: v for u, v in boundary}
        if len(successors) != 4:
            continue
        loop = [boundary[0][0]]
        for _ in range(4):
            loop.append(successors.get(loop[-1]))
        if loop[-1] != loop[0] or len(set(loop[:-1])) != 4:
            continue
        winding = []
        for k in range(4):
            p0 = vertices[loop[k]]
            p1 = vertices[loop[(k + 1) % 4]]
            p2 = vertices[loop[(k + 2) % 4]]
            u = [p1[d] - p0[d] for d in range(3)]
            v = [p2[d] - p1[d] for d in range(3)]
            cross = (u[1]*v[2]-u[2]*v[1],
                     u[2]*v[0]-u[0]*v[2],
                     u[0]*v[1]-u[1]*v[0])
            winding.append(sum(cross[d] * normals[i][d] for d in range(3)))
        if min(winding) <= 1e-10:
            continue
        choices.append((-dot, min(i, j), max(i, j), edge))
    used = set()
    result = []
    for _, i, j, edge in sorted(choices):
        if i not in used and j not in used:
            used.update((i, j))
            result.append((i, j, edge))
    return result
