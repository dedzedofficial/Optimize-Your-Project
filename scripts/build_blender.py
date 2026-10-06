"""Deprecated legacy Blender package builder.

Blender releases now use the 4.2+ Extensions package built by
scripts/build_blender_extension.py. This file remains only as a clear error for
old local automation that still invokes the former legacy builder.
"""
raise SystemExit(
    "Legacy Blender add-on ZIP builds are no longer supported. "
    "Use scripts/build_blender_extension.py for Blender 4.2+."
)
