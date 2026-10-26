# Optimize Your Project for Blender 4.2+

<img src="../Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" alt="Optimize Your Project" width="112">

**Current Blender version: 8.8.3**

The sidebar is intentionally minimal. Select a mesh in **Object Mode**, press **N** in the 3D Viewport, and open the **FISHHWB** tab.

## Install / Download Optimize Your Project

Supported Blender 4.2+ builds can install this ZIP as an extension.

1. Open the latest successful **Check release packages** build on GitHub:
   https://github.com/dedzedofficial/Optimize-Your-Project/actions/workflows/release-checks.yml
2. Download artifact **optimize-your-project-blender-8.8.3** and extract the artifact container ZIP if GitHub wraps it.
3. Install **optimize-your-project-blender-extension-8.8.3.zip** using **Edit > Preferences > Get Extensions > Install from Disk**. Do not unzip the extension ZIP itself.
4. Disable/remove any previously installed 0.8.5/0.8.8 duplicate extension, restart Blender, and enable the 8.8.3 extension.

## Sidebar layout

```text
OPTIMIZE YOUR PROJECT

Language: [ Auto / English / ... ]

CURRENT SELECTION
ObjectName
Triangles: ...
Vertices: ...
Faces: ...

[ SMART REMESH ]
Triangle Limit: ...

[ CREATE LODS ]

[ MERGE MATERIALS ]
```

### Smart Remesh

**Quality-first mode:** If QRemeshify is separately installed and its QuadWild operator is available, Smart Remesh attempts that quad solver first on a private working copy. QRemeshify is GPL-3.0 and its platform-specific binaries are not bundled with this project. If QRemeshify is missing, fails, or the object's scale/rotation is unsuitable for the current adapter, Smart Remesh uses Blender QuadriFlow and finally a labelled voxel fallback. QRemeshify's results are best-effort, not guaranteed on every mesh. Blender rigging, UVs and materials still require visual checking after data reprojection.


**Runs even when the mesh has fewer triangles than the target and on earlier generated Remesh objects.** The triangle setting is a best-effort **budget**, not a guarantee that a quad topology has precisely that many triangles.

- Creates a private output copy without modifying the selected mesh or previously generated results.
- For static meshes, evaluates existing modifiers on the private copy before reconstruction. For rigged meshes, preserves supported armature modifiers instead of baking the pose.
- Repairs near-duplicate vertices, degenerate/loose geometry and small boundary loops, and attempts to join nearby surface gaps with controlled voxel reconstruction. Voxel recovery can bridge close islands or seal openings. Always inspect disconnected parts, cavities and thin surfaces.
- After the optional QuadWild pass, tries QuadriFlow directly on the repaired mesh first, retaining more of the surface and boundary features when successful. If that fails, reconstructs the surface with voxel remeshing and retries QuadriFlow. If the quad solver still fails but voxel reconstruction is usable, labels the output **voxel quad topology**, not QuadriFlow success. This is a best-effort Blender-native pipeline, not the QuadWild solver used by QRemeshify.
- Attempts triangle reduction or adds topology where useful, staying within safety and detail limits; subdivision does not invent new sculpted detail.
- Reprojects supported UVs, material slots and face material IDs.
- For compatible relative shape keys, vertex groups and armature modifiers, reprojects blendshape deltas and weights onto the new vertices, and restores the original relative shape-key configuration and supported animation bindings. **Review the result**: nearest-surface interpolation can distort weights, facial expression shapes, texture seams and details.

Smart Remesh supports Blender's built-in `custom_normal` corner normals stored as compressed `INT16_2D` values (as well as authored `FLOAT_VECTOR` normals on POINT/CORNER). Native packed normal integers are never interpreted as XYZ vectors; the actual 3D corner directions are decoded through Blender's mesh API, reprojected, and encoded correctly for rebuilt topology. Blender 4.2's legacy custom split normals are also supported. Because topology and seams change, inspect shading, hard edges, deformation and UV seams before exporting. Other unknown custom mesh attributes still require a supported transfer method.\n\nUnsupported custom mesh attributes, absolute shape keys, shape-key NLA tracks and non-armature modifier stacks on rigged sources are **not silently destroyed**. The operator refuses those cases with a reason and preserves the source. Models with highly intricate geometry may require manual retopology and corrections.

Very high target limits (above 500,000) are rejected for memory/performance safety.

### Create LODs

Creates LOD0, LOD1 and LOD2 using existing safe triangle budgets. Source mesh is preserved; LODs are static-mesh only. Previous advanced preferences continue to exist but are deliberately not displayed in the main sidebar.

### Merge Materials

The button uses the existing **Merge Textures** atlas workflow to reduce compatible materials to one packed material with rebuilt AtlasUV. This operation is not a plain same-material-slot deduplicator: it may bake textures, and it rejects unsupported complex shaders instead of corrupting them. Original materials remain unchanged on the source.

## When the target cannot be safely met

The resulting operator message explains whether it used QuadWild, QuadriFlow, kept voxel quads, or rejected an unsupported source. No automatic solver guarantees clean quad edge flow for every nonmanifold, extremely thin or multi-island mesh. Voxel fallback prioritizes producing usable game geometry over preserving exact fine details. Inspect the output's wireframe, UVs, shape keys, bones/weights and shading before exporting it to Unity or VRChat.

## Other retained tools

Legacy Clean Mesh, Lightmap UV, identical mesh linking, collider stripping and the more configurable Remesh workflow remain registered and available through Blender operator search (F3); they are hidden from the compact sidebar rather than deleted.

## Previous version history

See [CHANGELOG.md](../CHANGELOG.md) and the [main README](../README.md).
