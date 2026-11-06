"""Fail-closed orchestration for conservative indexed triangle-pair previews.

No Blender object is created or changed. This is NOT flow-aware retopology.
The caller must supply all protected per-loop attributes; omitted layers cannot
be validated. Vertex coordinates and all vertex-indexed payloads are untouched.
"""
from .triangle_pair_preview import build_face_preview
from .preview_validation import validate_preview
from .preview_attributes import validate_preview_attributes


def validated_pair_preview(vertices, faces, *, materials, corner_signatures,
                           protected_edges=(), minimum_dot=0.75):
    """Return validated faces, provenance, corners, materials and metrics.

    Requires explicit material IDs and complete loop signatures (all UV maps,
    split normals, color layers and other protected per-corner attributes).
    Fails closed if either layer is missing. Does not modify input arrays.
    """
    if materials is None or corner_signatures is None:
        raise ValueError("Explicit materials and loop signatures are required")
    if len(materials) != len(faces) or len(corner_signatures) != len(faces):
        raise ValueError("Source attribute count mismatch")
    output, provenance, corners = build_face_preview(
        vertices, faces, materials=materials,
        corner_signatures=corner_signatures, protected_edges=protected_edges,
        minimum_dot=minimum_dot)
    output_materials = [materials[group[0]] for group in provenance]
    validate_preview(faces, output, provenance)
    validate_preview_attributes(
        faces, output, provenance, source_materials=materials,
        output_materials=output_materials, source_corners=corner_signatures,
        output_corners=corners)
    paired = sum(len(group) == 2 for group in provenance)
    return {
        "faces": output,
        "provenance": provenance,
        "corners": corners,
        "materials": output_materials,
        "paired_triangles": paired * 2,
        "quad_joins": paired,
        "source_faces": len(faces),
        "output_faces": len(output),
        "source_triangle_equivalents": sum(len(face)-2 for face in faces),
        "output_triangle_equivalents": sum(len(face)-2 for face in output),
    }
