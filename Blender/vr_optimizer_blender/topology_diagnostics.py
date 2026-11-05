"""Pure-Python topology diagnostics for non-destructive retopology candidates.

No bpy dependency: usable in CI and by the Blender adapter. This is a gate,
not a quad generator; a high quad ratio alone never certifies edge flow.
"""
from collections import Counter, defaultdict


def analyze_faces(vertex_count, faces):
    """Return reproducible topology statistics for indexed polygon faces.

    A vertex-connected component includes isolated vertices. Boundary and
    nonmanifold counts use undirected edge incidence, not face winding.
    """
    if vertex_count < 0:
        raise ValueError("Negative vertex count")
    edge_faces = Counter()
    adjacency = [set() for _ in range(vertex_count)]
    polygons = []
    for face in faces:
        face = tuple(face)
        if len(face) < 3 or len(set(face)) != len(face):
            raise ValueError("Degenerate polygon vertex indices")
        if any(not isinstance(v, int) or v < 0 or v >= vertex_count
               for v in face):
            raise ValueError("Face vertex index out of range")
        polygons.append(face)
        for a, b in zip(face, face[1:] + face[:1]):
            if a == b:
                raise ValueError("Zero-length indexed edge")
            edge_faces[tuple(sorted((a, b)))] += 1
            adjacency[a].add(b)
            adjacency[b].add(a)
    seen = set()
    parts = []
    for start in range(vertex_count):
        if start in seen:
            continue
        pending = [start]
        seen.add(start)
        size = 0
        while pending:
            vertex = pending.pop()
            size += 1
            for neighbor in adjacency[vertex] - seen:
                seen.add(neighbor)
                pending.append(neighbor)
        parts.append(size)
    tri = sum(len(f) == 3 for f in polygons)
    quad = sum(len(f) == 4 for f in polygons)
    ngon = len(polygons) - tri - quad
    return {
        "vertices": vertex_count,
        "faces": len(polygons),
        "triangles": tri,
        "quads": quad,
        "ngons": ngon,
        "quad_percent": round(100.0 * quad / len(polygons), 4) if polygons else 0.0,
        "triangle_equivalents": sum(len(f) - 2 for f in polygons),
        "components": len(parts),
        "component_vertex_sizes": sorted(parts),
        "loose_vertices": sum(not neighbors for neighbors in adjacency),
        "boundary_edges": sum(n == 1 for n in edge_faces.values()),
        "nonmanifold_edges": sum(n > 2 for n in edge_faces.values()),
        "edge_count": len(edge_faces),
    }


def compare_topology(source, candidate, *, max_triangles=None,
                     preserve_components=True, preserve_boundary=True,
                     minimum_quad_percent=None):
    """Return explicit failed gates; caller must additionally verify UVs, skin,
    shape keys, normals, materials, surface deviation and posed deformation.
    """
    failures = []
    if max_triangles is not None and candidate["triangle_equivalents"] > max_triangles:
        failures.append("triangle budget exceeded")
    if preserve_components and (
        source["components"] != candidate["components"]
        or source["component_vertex_sizes"] != candidate["component_vertex_sizes"]
    ):
        failures.append("vertex-connected component structure changed")
    if preserve_boundary and (
        source["boundary_edges"] != candidate["boundary_edges"]
        or source["nonmanifold_edges"] != candidate["nonmanifold_edges"]
    ):
        failures.append("boundary/nonmanifold edge counts changed")
    if minimum_quad_percent is not None and candidate["quad_percent"] < minimum_quad_percent:
        failures.append("quad percentage below target")
    return failures
