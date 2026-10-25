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

Smart Remesh now supports **Active Mesh**, **Selected Meshes** and **Model Hierarchy** scopes. The **Triangle Limit** is an enforced **combined maximum** for all meshes in the chosen scope, not a separate target for each mesh. A generated job is only accepted when every mesh passes the budget and geometry checks. The operation always preserves the source objects.

- **Active Mesh:** process one mesh object.
- **Selected Meshes:** process all selected meshes with one shared budget.
- **Model Hierarchy:** choose a parent object (including an Empty) and process its descendant meshes, retaining their parent links.
- Each disconnected island reserves a small minimum allocation. Impossible budgets fail before editing anything.
- Each output records its assigned triangle ceiling, method and originating scope.
- Complete jobs report the combined before/after triangle count. All results are selected together.

**Preserving geometry:** A single closed manifold component uses voxel reconstruction with optional QuadriFlow and guarded reduction, including UV/material/deformation reprojection where supported. Open, nonmanifold or disconnected meshes avoid dangerous voxel welding: static meshes use a **surface-preserving simplification fallback** instead. That fallback is **not** equivalent to new quad retopology and is explicitly reported. Deformed meshes with unsafe boundaries are kept intact only if their allocated budget already fits; otherwise the whole operation is rejected.

**Validation:** Each generated mesh must have usable faces, meet its assigned triangle ceiling, preserve the number of disconnected surface components, and pass a coarse bounds check. Any failure removes *all* newly created outputs and restores the original selection. The validator cannot guarantee optimal animation edge flow or perfectly preserved UV appearance; inspect UV seams, normals, deformation and silhouettes before exporting.

Supported relative blendshapes, vertex groups and armature modifiers can be transferred on closed sources. Unsupported custom attributes, absolute shape keys, shape-key NLA tracks and unsupported modifier combinations still fail with an explicit reason, leaving originals untouched. Target limits over 500,000 triangles are rejected for resource safety.

This is the first game-ready pipeline milestone. The LOD and materials buttons are still separate; automated normal baking, export certification and cross-engine scene optimisation are planned rather than shipped in this update.

#### Included Smart Remesh detail protection

The public sidebar still has **three primary actions**. Smart Remesh has an **Advanced Options** disclosure rather than another button. Its Detail Handling offers:
- **Automatic** (default): rebuild safe closed meshes, otherwise preserve their surface.
- **Preserve Important Edges**: avoid voxel welding when authored UV seams or sharp edges are present, and reject results whose *sampled* surface deviation exceeds 4% of source bounds diagonal.
- **Preserve Surface**: favour topology-preserving mesh decimation instead of quad rebuilding. This is not quad retopology.

To protect specific vertices, create a vertex group named `FISHHWB_Protect` and paint weights of at least 0.5. Smart Remesh avoids voxel reconstruction for marked geometry, biases the Decimate modifier toward preserving those vertices and **rejects** any simplification that removes or moves a marked vertex. The protected region may make a low triangle budget impossible. This mask also applies to existing LOD simplification. It is a vertex position guard, not a guarantee of untouched neighbouring faces, UV layouts or deformation.

Generated results record an **approximate bidirectional vertex-to-surface deviation** relative to the source mesh diagonal. It samples mesh vertices, not all surface points, so it cannot prove that every thin detail, UV seam or face orientation is preserved. Model quality still requires inspection.

The **CURRENT SELECTION** box includes an optional **Mesh Health Details** disclosure (no extra action button): it lists UV/material counts, n-gons, open/nonmanifold edges, degenerate faces and loose vertices. These are diagnostics, not automatic repairs.

#### Saved settings and preview

Open **Smart Remesh → Advanced Options** to load a Balanced, Desktop, Mobile or Standalone VR **starting preset**. Targets are examples, not verified limits for every game. **Save My Project** records the current triangle, LOD and collider limits in the active .blend file; save the .blend to retain them. Applying a preset never runs optimisation. With advanced settings expanded, the current scope and combined pre-optimisation triangle count appear beneath the button.

**Create LODs → LOD & Collision Options** also includes LOD0/LOD1/LOD2 preview selectors. After running Create LODs, use these to switch visibility among the *generated* LOD objects. The original object is deliberately not hidden, so hide the original manually if its geometry overlaps the comparison. Preview does not modify mesh data. LOD outputs record approximate surface deviation for visual review.

A bounded **FISHHWB_Optimization_History** Text datablock stores the latest 100 action summaries locally inside the .blend, including warnings and preservation reports.

### Create LODs

Creates LOD0, LOD1 and LOD2 using existing safe triangle budgets. Source mesh is preserved; LODs are static-mesh only. Previous advanced preferences continue to exist but are deliberately not displayed in the main sidebar.

### Merge Materials

The button uses the existing **Merge Textures** atlas workflow to reduce compatible materials to one packed material with rebuilt AtlasUV. This operation is not a plain same-material-slot deduplicator: it may bake textures, and it rejects unsupported complex shaders instead of corrupting them. Original materials remain unchanged on the source.

## When the target cannot be safely met

The resulting operator message explains whether it used QuadriFlow, kept voxel quads, or rejected an unsupported source. Inspect the output's wireframe, UVs, shape keys, bones/weights and shading before exporting it to Unity or VRChat.

## Other retained tools

Legacy Clean Mesh, Lightmap UV, identical mesh linking, collider stripping and the more configurable Remesh workflow remain registered and available through Blender operator search (F3); they are hidden from the compact sidebar rather than deleted.

## Previous version history

See [CHANGELOG.md](../CHANGELOG.md) and the [main README](../README.md).
