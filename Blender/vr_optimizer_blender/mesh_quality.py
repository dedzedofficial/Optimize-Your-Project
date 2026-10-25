# SPDX-License-Identifier: GPL-3.0-or-later
"""Conservative mesh diagnostics used by the existing optimization buttons.

These checks report issues and approximate surface deviations; they do not
certify a mesh as game-ready or replace inspecting UVs, normals and animation.
"""
import math

from mathutils.bvhtree import BVHTree


PROTECTED_GROUP_NAME = "FISHHWB_Protect"


def inspect_mesh(mesh):
    """Read-only checks; open meshes and missing UVs are warnings, not errors."""
    mesh.calc_loop_triangles()
    edge_faces = {}
    used = set()
    degenerate = 0
    for polygon in mesh.polygons:
        if polygon.area <= 1.0e-12:
            degenerate += 1
        corners = tuple(polygon.vertices)
        used.update(corners)
        for i, start in enumerate(corners):
            end = corners[(i + 1) % len(corners)]
            edge = tuple(sorted((start, end)))
            edge_faces[edge] = edge_faces.get(edge, 0) + 1
    boundary = sum(count == 1 for count in edge_faces.values())
    non_manifold = sum(count > 2 for count in edge_faces.values())
    loose = len(mesh.vertices) - len(used)
    return {
        'triangles': len(mesh.loop_triangles),
        'vertices': len(mesh.vertices),
        'material_slots': len(mesh.materials),
        'uv_layers': len(mesh.uv_layers),
        'boundary_edges': boundary,
        'non_manifold_edges': non_manifold,
        'loose_vertices': loose,
        'degenerate_faces': degenerate,
        'ngons': sum(len(poly.vertices) > 4 for poly in mesh.polygons),
    }


def summary_lines(stats):
    """Only highlight useful actionable warnings, not arbitrary score badges."""
    warnings = []
    if stats['degenerate_faces']:
        warnings.append(f"{stats['degenerate_faces']} degenerate faces")
    if stats['non_manifold_edges']:
        warnings.append(f"{stats['non_manifold_edges']} nonmanifold edges")
    if stats['loose_vertices']:
        warnings.append(f"{stats['loose_vertices']} loose vertices")
    if stats['boundary_edges']:
        warnings.append(f"{stats['boundary_edges']} open boundary edges")
    if not stats['uv_layers']:
        warnings.append("No UV map (needed for texture baking)")
    return warnings


def protected_positions(obj, min_weight=0.5):
    """Vertices a user explicitly marked for vertex-position protection."""
    group = obj.vertex_groups.get(PROTECTED_GROUP_NAME)
    if group is None:
        return []
    return [
        vert.co.copy()
        for vert in obj.data.vertices
        if any(g.group == group.index and g.weight >= min_weight
               for g in vert.groups)
    ]


def verify_protected_positions(reference_positions, target_mesh, tolerance=1.0e-5):
    """Guard against deleting/moving marked vertices during surface reduction."""
    if not reference_positions:
        return
    if not target_mesh.vertices:
        raise ValueError("Protected detail has no remaining vertices.")
    vertices = [vert.co for vert in target_mesh.vertices]
    squared = tolerance * tolerance
    for position in reference_positions:
        if not any((position - vertex).length_squared <= squared
                   for vertex in vertices):
            raise ValueError(
                "Triangle limit would alter vertices marked by "
                "FISHHWB_Protect. Increase the budget or reduce the "
                "protected region.")


def _tree(mesh):
    mesh.calc_loop_triangles()
    triangles = [tuple(t.vertices) for t in mesh.loop_triangles]
    if not triangles:
        return None
    return BVHTree.FromPolygons(
        [vert.co.copy() for vert in mesh.vertices], triangles,
        all_triangles=True)


def _nearest_maximum(mesh, tree, max_samples):
    if tree is None or not mesh.vertices:
        return float('inf')
    stride = max(1, math.ceil(len(mesh.vertices) / max_samples))
    maximum = 0.0
    for vertex in list(mesh.vertices)[::stride]:
        nearest, _normal, _index, distance = tree.find_nearest(vertex.co)
        if nearest is None or distance is None:
            return float('inf')
        maximum = max(maximum, distance)
    return maximum


def surface_deviation_ratio(reference, result, max_samples=1024):
    """Approximate *bidirectional* local-space surface deviation / diagonal.

    Explicitly approximate: vertex sampling may miss narrow protrusions,
    flipped normals, UV problems and gaps between sampled vertices.
    """
    if not reference.vertices or not result.vertices:
        return float('inf')
    xs = [v.co.x for v in reference.vertices]
    ys = [v.co.y for v in reference.vertices]
    zs = [v.co.z for v in reference.vertices]
    diagonal = math.sqrt(
        (max(xs) - min(xs))**2
        + (max(ys) - min(ys))**2
        + (max(zs) - min(zs))**2)
    if diagonal <= 1.0e-8:
        return float('inf')
    forward = _nearest_maximum(result, _tree(reference), max_samples)
    reverse = _nearest_maximum(reference, _tree(result), max_samples)
    return max(forward, reverse) / diagonal
