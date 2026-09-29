# Optimize Your Project for Blender — v0.7.0

<img src="../Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" alt="Optimize Your Project logo" width="112">

Early Blender support for **Optimize Your Project**, focused on fast mesh cleanup instead of a large settings panel.

## Install

1. Download `optimize-your-project-blender-0.7.0.zip` from the GitHub Releases page after the `blender-v0.7.0` release is published.
2. In Blender, use **Edit → Preferences → Add-ons → Install...** or **Get Extensions → Install from Disk**.
3. Enable **Optimize Your Project for Blender**.
4. In the 3D Viewport press **N** and open the **FISHHWB** tab.

## One-click cleanup

Select one static mesh in Object Mode.

### One-Click Remesh

Press **One-Click Remesh**. The add-on creates a new `_Remesh` copy and automatically chooses a practical remesh detail size from the mesh dimensions.

This is intended for static props and cleanup meshes. Rigged, vertex-group, armature, and shape-key meshes are skipped because remeshing changes topology.

### Merge Duplicate Vertices

Set **Merge Distance** and press **Merge Duplicate Vertices**. The add-on creates a new `_Merged` copy and welds nearby vertices.

Shape-key meshes are skipped to avoid breaking topology-dependent keys.

## Advanced Mesh Tools

The earlier preview tools are still available below the quick section:

- **Create Reduced Copy** — decimated duplicate under a triangle limit.
- **Join Selected and Merge Vertices** — joins selected mesh copies and welds nearby vertices.
- **Merge Base Color Textures + UVs** — optional supported Base Color atlas path for the join tool.
- **Create LOD0 / LOD1 / LOD2** — static mesh copies at 100%, up to 66%, and up to 33% triangle counts.

These tools create output copies so the source object remains available for comparison.

## Notes

Blender v0.7 is early support. Test generated meshes before replacing production assets, especially before GLB/FBX export into Unity or another engine.
