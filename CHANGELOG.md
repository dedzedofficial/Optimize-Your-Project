# Optimize Your Project changelog

<img src="Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" alt="Optimize Your Project logo" width="96">

<p align="center">
  <a href="README.md"><strong>Overview</strong></a> |
  <a href="Blender/README.md"><strong>Blender Guide</strong></a> |
  <a href="Documentation/Roadmap.md"><strong>Roadmap</strong></a> |
  <a href="Documentation/Architecture.md"><strong>Architecture</strong></a> |
  <a href="CHANGELOG.md"><strong>Changelog</strong></a>
</p>

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
