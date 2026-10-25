# Optimize Your Project changelog

<img src="Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" alt="Optimize Your Project logo" width="96">

<p align="center">
  <a href="README.md"><strong>Overview</strong></a> |
  <a href="Blender/README.md"><strong>Blender Guide</strong></a> |
  <a href="Documentation/Roadmap.md"><strong>Roadmap</strong></a> |
  <a href="Documentation/Architecture.md"><strong>Architecture</strong></a> |
  <a href="CHANGELOG.md"><strong>Changelog</strong></a>
</p>

## Unreleased - indie-developer workflow improvements

- Unity: local per-project Balanced/Desktop/Mobile/Standalone VR starting profiles under Advanced Settings; preview-only texture and model importer batches; model importer processing extended to a selected Assets folder.
- Unity: Project Review now prioritizes high-severity actionable findings, with read-only texture-waste checks, SHA-256-based exact duplicate-source identification for files up to 32 MiB, prefab/loaded-scene missing-script checks, missing shader checks and evidence-based model import warnings.
- Unity: optional serialized asset usage lookup with bounded input (4,000 candidate files), local CSV report export and a read-only preview of the fingerprint-guarded last import batch. Runtime-created dependencies remain out of scope.
- Blender: non-destructive local game-target preset save/load under Smart Remesh; scope counts and triangle-budget preflight; persistent bounded local optimisation log; per-LOD viewport preview under existing Create LODs advanced options.
- Added Unity EditMode tests for issue ranking, independent preset selection and exact duplicate-source warnings; extended Blender tests for local presets, bounded history and generated LOD preview.
- No extra main buttons, no new online services, no Unity shader changes. Unity EditMode tests have not been run by the Blender/Python-only GitHub Actions workflow.

## Unreleased - whole-model Smart Remesh foundation

- Added Active Mesh, Selected Meshes and Model Hierarchy scopes in the Blender sidebar.
- Added deterministic per-component allocation under one strict combined triangle limit. Reject impossible models before producing outputs.
- Added atomic multi-object output creation and cleanup, original selection recovery, per-object budget metadata and combined before/after reporting.
- Added open/nonmanifold/disconnected-geometry safeguards. Such static meshes use a clearly reported surface-preserving simplification rather than unsafe voxel welding; deformation-sensitive exceptions reject over-budget inputs.
- Added component-count and bounding-box validation. Reconstructed mesh results that lose connected pieces or exceed the limit are discarded.
- Added standalone budget tests and multi-object Blender regressions; no Unity functionality or release version changed.
- Kept exactly three primary Blender buttons; added compact expandable mesh-health, Smart Remesh, LOD/collision and material-atlas settings within the existing controls.
- Added automatic detail masking via the `FISHHWB_Protect` vertex group: guarded Decimate reductions reject outputs that remove or displace explicitly marked vertices.
- Added detail-focused remeshing to protect authored seam/sharp edge geometry and an optional 4%-of-diagonal sampled surface deviation gate, plus output deviation reporting.
- Added LOD surface-deviation reports and a 12-triangle bounding-box collider candidate under Create LODs, with safe failure when collider budget is below 12.
- Added Blender integration tests for diagnostics, detail modes, protected positions, box colliders and impossible budgets.

- Known limitations: automatic retopology cannot guarantee animation-quality edge flow; surface-preserving fallback is not quad retopology; bounds and UV checks are conservative and do not replace visual review.

## Blender 8.8.3 | Smart Remesh and custom normal fix\n\n- Smart Remesh now projects supported authored `custom_normal` FLOAT_VECTOR POINT/CORNER attributes onto rebuilt topology rather than rejecting the mesh. Projected directions are normalized; source mesh and attribute data are unchanged.\n- Unsupported custom-normal storage and other unknown attributes still produce a clear, non-destructive rejection.\n- Restored the Blender extension version to the user-requested **8.8.3**; Unity remains **0.8.8**.\n\n### Smart Remesh and simplified UI (features retained from the previous development build)

- Redesigned the Blender sidebar to show language, active mesh statistics and exactly three main operations: **Smart Remesh**, **Create LODs** and **Merge Materials**.
- Smart Remesh always creates an independent output copy and attempts geometry repair, voxel-based surface reconstruction and QuadriFlow retopology, even when an input is under the triangle target or a prior Remesh output.
- Uses best-effort triangle budget adjustment and nearest-surface reprojection of UV maps, face material IDs, vertex-group weights and supported relative shape-key deltas. Supported armature modifiers and relative shape-key animation configuration are restored on the output.
- On static meshes, modifier effects are evaluated on a private copy before remeshing. Unsupported custom attributes, destructive modifier/deformation combinations and unsupported shape-key arrangements are rejected safely.
- Removed advanced tools from the main sidebar without deleting their existing operator registrations.
- Added Blender runtime regression cases for repeat remesh, shape keys, rigging, vertex groups, modifier effects and original preservation.
- Maintains separate Unity v0.8.8 metadata until a Unity-specific update.

## 0.8.8

### Blender Smart Optimize diagnostics and rebuild correction (same version)

- Smart Optimize now attempts Repair & Rebuild retopology when explicitly chosen even on meshes below the triangle target. Preserve Surface still skips needless remeshing below target.
- Safe independent copy-based rebuild of a previously generated Remesh output without silently replacing that output or changing its original source.
- Added per-operation reasons when Smart Optimize does nothing (below triangle target, shape keys/rigging, protected/linked input, no materials, or unsupported LOD/atlas job).
- Exposed Remesh Mode and Triangle Target in the Smart Optimize preview dialog.

### Blender Remesh correction (same version)

- Restored a visible **Preserve Surface / Repair & Rebuild** control above One-Click Remesh. The rebuild option performs controlled static-mesh voxel reconstruction, attempts QuadriFlow quad retopology, and reprojects UVs/material IDs when supported.
- Kept original objects intact; topology-sensitive shape keys and unsupported custom attributes trigger a surface-preserving fallback instead of destructive rebuilding.
- Added a distinct sidebar subtitle **Blender v0.8.8 (Remesh Fix)** to help identify whether Blender is still loading the older installed v0.8.5.
- Added runtime checks for rebuilt output and shape-key fallback on supported Blender versions.

### Blender 4.2+

- Added **Smart Optimize (Preview)**: inspect selected mesh count and choose source-preserving cleanup, Remesh, LOD, texture-atlas and LightmapUV operations before execution. Rigged or protected inputs are skipped where actions cannot preserve them.
- Upgraded **Remesh** to fill only tiny closed boundary loops and avoid automatic voxel closure of intentional large openings. Existing UV/material/shape-key preservation guards remain active.
- Added configurable **LOD1** and **LOD2** triangle percentages, plus a separate triangle cap for generated collider proxies. Generated-output caching now respects these settings.
- Expanded **Merge Textures** to bake supported Principled material roughness, metallic, alpha, emission and tangent-normal channels where needed, alongside Base Color. Complex mixed shaders are explicitly rejected.
- Added configurable 1024/2048/4096 atlas sizes and kept input texture sampling on the source UV map during baking.
- Preserved original objects for Smart Optimize lightmap operations and made the batch result summary report changed, skipped and failed inputs.

### Unity

- Added **Export Unused Asset Report (No Deletion)**, a CSV dry run of conservative cleanup candidates and protected/unsupported counts, separate from the existing two-confirmation permanent deletion.
- Retained existing texture, audio, particle, material, script and UI optimization actions without changing their conservative defaults.

### Packaging and documentation

- Updated the Blender Extensions bundle, release metadata, readmes, and static/runtime verification for 0.8.8.

## 0.8.5

### Blender 4.2+

- Upgraded the existing **Remesh to Triangle Target** action with automatic crack welding, small-hole repair, manifold voxel rebuilding and QuadriFlow retopology for supported static meshes before the final triangle-target reduction.
- Kept deformation-sensitive meshes on the guarded deformation-transfer path rather than forcing destructive topology rebuilding.
- Added the single new **Merge Textures** action, which creates a preserved copy with rebuilt `AtlasUV`, a packed 2048x2048 texture atlas and one replacement material.
- Kept the existing simple button-first UI and original-object preservation behaviour.
- Unified Blender and Unity/package release metadata at **0.8.5**.

## 0.7.66

### UI correction

- Restored a button-first Unity layout where each optimization feature is a primary action instead of leading with bundled configurations.
- Kept Advanced settings and all 0.7.65 safety improvements behind the same feature buttons.
- Kept permanent unused-asset deletion isolated in the Unity danger zone.
- Changed Blender to a single Primary Actions panel with direct Remesh, LOD, Lightmap UV, identical-mesh linking and collider-cleanup buttons.
- Reduced explanatory UI clutter while keeping operator tooltips, confirmations and result summaries.

## 0.7.65

### Project release

- Bumped the unified Unity and Blender release to **v0.7.65**.
- Consolidated the current-engine quality work planned across the earlier 0.7.62 to 0.7.65 milestones into one release.
- Kept Unity and Blender on the same project version and release feed.

### Unity

- Rebuilt the Editor window for readability with a larger minimum width, separate navigation and language rows, wrapped button text and a two-row footer so controls no longer clip at normal window sizes.
- Replaced the old crowded One Click area with a single **Quick Optimize** section.
- Added **Balanced**, **Mobile** and **VR** configuration buttons for conservative texture, particle and model-import targets.
- Added **Optimize Current Scope** and **Optimize Character / Avatar** bundled workflows. They run texture, model import, particle, material, UI-raycast and missing-script jobs behind one confirmation while leaving lighting and realtime-shadow changes explicit.
- Updated **Optimize Model Imports** so stronger existing mesh-compression settings are preserved instead of being reduced to the requested level.
- Updated importer-history policies to `textures-v0765` and `models-v0765` so the new release logic can be evaluated correctly on previously processed assets.
- Updated **Optimize UI Raycasts** to preserve Selectable hierarchies and UI already blocked by CanvasGroup in addition to existing EventSystem-interface checks.
- Updated **Clean Missing Scripts** with a preflight count and confirmation before removing broken MonoBehaviour entries.
- Added **Find and Permanently Delete Unused Assets** in a separate Danger Zone.
- The unused-asset cleaner only considers conservative asset categories, scans serialized inbound dependencies, protects common dynamic-use paths and externally marked assets, previews candidates and requires two confirmations.
- Permanent asset deletion explicitly warns that Unity Undo cannot restore deleted project files and that runtime-only references cannot always be detected.

### Blender 4.2+

- Reworked the sidebar around one readable **Quick Optimize** panel.
- Remesh, LOD, Lightmap UV, identical-mesh linking and collider render-data cleanup are now grouped in the main panel instead of being split between stacked panels.
- Added width-aware wrapped descriptions and result text to reduce clipping in narrow Blender sidebars.
- Increased action-row height for easier scanning and selection.
- Kept Remesh/LOD source preservation, generated-output history, collision proxies and Blender 5.x slotted Action support intact.
- Kept runtime CI targets at Blender 4.2 LTS, 4.5 LTS and 5.2 LTS.

## 0.7.61

### Project release

- Unified Unity and Blender under the same **v0.7.61** project release instead of maintaining separate integration version numbers.
- Added a top-level project version to `version.json` while retaining integration fields for compatibility with existing build/update code.
- Updated the Unity package, update checker, documentation and release validation to use v0.7.61.

### Unity

- Improved **Optimize Textures** so it does not create unnecessary platform overrides when the base importer already uses an equal or stricter size limit.
- Existing stricter platform texture limits are preserved instead of being increased.
- Improved **Optimize Particles** lifetime capping to support both Constant and Two Constants modes while preserving authored curve-based lifetime data.
- Tightened **Disable Realtime Shadows** so the optimizer itself rejects disabled, Mixed and Baked lights and records prefab-instance changes correctly.
- Updated the Unity update checker to read the unified project version first while remaining compatible with the older Unity-specific version field.

### Blender 4.2+

- Moved the supported Blender release path to Blender 4.2+ Extensions only.
- Added Generate Lightmap UV, Link Identical Mesh Data and Strip Collider Render Data.
- Updated shape-key animation handling for Blender 5.x slotted Actions/channelbags while retaining Blender 4.2 compatibility.
- Updated Blender runtime CI to test Blender 4.2 LTS, 4.5 LTS and 5.2 LTS.

## 0.7.60

- Rebuilt the Unity Editor window into a smaller Project / Character dashboard.
- Added **Clean Missing Scripts** with Unity Undo support.
- Added **Optimize UI Raycasts** for decorative UI graphics while preserving detected interactive controls.
- Expanded interface localization and added Auto language detection.
- Kept texture, model, particle, material, lighting, review and importer-history workflows compact.

## 0.7.55

- Added guarded Blender Remesh deformation transfer for supported armature weights and relative shape keys.
- Added persistent generated-output reuse and manual-edit protection.
- Added Blender LOD0 / LOD1 / LOD2 generation and later the optional LOD2 collision proxy.
- Consolidated Unity model, material and lighting workflows around owning buttons.

## 0.7.4

- Simplified Blender around Remesh and LOD instead of broad unreliable cleanup panels.
- Added Unity project insights, language selection and material/import maintenance improvements.

## 0.7.1

- Added early Blender copy-based mesh cleanup experiments and the first cross-tool result summaries.
- Improved Unity batch cancellation and reporting.

## 0.7.0

- Repositioned Optimize Your Project as a general developer optimization toolkit for Unity, Blender and real-time projects.
