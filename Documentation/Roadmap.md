# Optimize Your Project roadmap

<img src="../Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" alt="Optimize Your Project logo" width="96">

<p align="center">
  <a href="../README.md"><strong>Overview</strong></a> |
  <a href="../Blender/README.md"><strong>Blender Guide</strong></a> |
  <a href="../Documentation/Roadmap.md"><strong>Roadmap</strong></a> |
  <a href="../Documentation/Architecture.md"><strong>Architecture</strong></a> |
  <a href="../CHANGELOG.md"><strong>Changelog</strong></a>
</p>

## Direction

Optimize Your Project should turn repetitive optimization jobs into clear one-click or batch actions without becoming a confusing general-purpose toolbox.

Unity and Blender have independent release numbers. Blender support now starts at **4.2** and uses the Blender Extensions system. New Blender work should target modern APIs and be tested on active LTS releases rather than carrying legacy compatibility that blocks useful features.

## Current baseline

### Unity v0.7.60

- texture optimization and import repair,
- model-import compression and mesh import optimization,
- particle limits,
- safe material-cost fixes,
- baked-light setup,
- missing-script cleanup,
- UI raycast optimization,
- project and character review tools,
- importer history, protection, trial and restore infrastructure.

### Blender v0.7.61

- One-Click Remesh with guarded UV/material/deformation preservation,
- LOD0 / LOD1 / LOD2 generation,
- optional collision proxy from LOD2,
- generated-output reuse and manual-edit protection,
- Generate Lightmap UV,
- Link Identical Mesh Data,
- Blender 4.2+ Extensions packaging,
- runtime validation on Blender 4.2 LTS, 4.5 LTS and 5.2 LTS.

## Blender 0.7.62 target

Focus on useful static-mesh preparation without recreating the removed cleanup wall.

Candidate work:

- **Optimize Material Slots**: remove only truly unused material slots with explicit index remapping and Undo.
- **Batch Lightmap UV** improvements for generated LOD collections and selected static-prop groups.
- **Instance Review**: show which selected meshes could be safely linked before changing data.
- **Collider Simplification**: optional independent triangle target for collision proxies instead of always copying LOD2 exactly.
- Better result summaries showing estimated duplicate mesh-data savings and UV channel outcomes.

## Blender 0.7.7 target

- optional export-preparation metadata for Unity, Godot and Unreal without forcing engine-specific settings into the mesh,
- guarded transform review for negative or non-uniform scale before LOD/export jobs,
- optional collection organization for generated LOD and collider outputs,
- improved static-mesh batch cancellation and retry reporting.

## Blender 0.8 target

- **Static Mesh Optimize Selection** orchestration button that coordinates already-proven actions instead of duplicating their implementations,
- measured mesh-data and material-slot savings,
- optional lightmap workflow presets for common real-time asset sizes,
- stronger Blender 5.x API usage where it provides a clear benefit while retaining 4.2 as the minimum until that becomes unreasonable.

## Unity 0.8 target

- safe UI rendering-work reductions,
- animation-data cleanup for explicitly supported clips,
- shader build-waste reduction using build evidence,
- asset-loading and packaging diagnostics with guarded fixes,
- collider proxy integration where imported generated Blender metadata can help without requiring Blender.

## 0.9 target

- one selection-based orchestration route per stable integration,
- recovery and conflict handling for every destructive or metadata-changing batch,
- performance/result evidence where it can be measured reliably,
- remove actions that overlap or do not prove useful.

## 1.0 target

- a small set of dependable one-click workflows,
- at least 90% coverage of the published safely automatable task inventory for each declared stable integration,
- clear supported-version policy,
- no duplicate buttons that perform the same outcome,
- no automatic deletion of ambiguous project content,
- source-preserving or Undo-backed behavior wherever practical.

## Admission rules

A new optimization action should only ship when it has:

- a distinct outcome,
- a real repetitive manual job to replace,
- clear supported inputs,
- a recovery route,
- regression coverage,
- no safer existing button that should simply be extended instead.

Reports, navigation helpers and duplicated wrappers do not count as optimization coverage.
