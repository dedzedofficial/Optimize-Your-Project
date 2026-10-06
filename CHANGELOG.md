# Optimize Your Project changelog

<img src="Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" alt="Optimize Your Project logo" width="96">

<p align="center">
  <a href="README.md"><strong>Overview</strong></a> |
  <a href="Blender/README.md"><strong>Blender Guide</strong></a> |
  <a href="Documentation/Roadmap.md"><strong>Roadmap</strong></a> |
  <a href="Documentation/Architecture.md"><strong>Architecture</strong></a> |
  <a href="CHANGELOG.md"><strong>Changelog</strong></a>
</p>

## Blender 0.7.61

- Moved the supported Blender release path to **Blender 4.2+ Extensions only**.
- Stopped publishing and validating the legacy pre-4.2 add-on ZIP.
- Added **Generate Lightmap UV** for selected supported static meshes.
- Lightmap UV generation preserves geometry and the primary UV map, only creates `LightmapUV` when it can safely become the second UV channel, and refuses to replace existing secondary UV data automatically.
- Replaced context-sensitive UV operators with a deterministic non-overlapping per-face lightmap atlas so the tool works reliably in interactive and headless Blender.
- Added **Link Identical Mesh Data** for exact selected static duplicates.
- Exact duplicate linking preserves object transforms and skips modifiers, shape keys, linked-library meshes and object-level material overrides.
- Added **Strip Collider Render Data** for generated collision proxies, removing materials, UVs and color attributes while preserving geometry.
- Added a compact **Blender 4.2+ Tools** child panel beneath the existing Remesh / LOD interface.
- Kept One-Click Remesh, LOD generation and the optional LOD2 collision proxy intact.
- Updated shape-key animation handling for Blender 5.x slotted Actions/channelbags while retaining Blender 4.2 compatibility.
- Added Blender 4.2+ regression tests for Lightmap UV generation, island separation, secondary-UV protection, exact mesh linking, collider render-data stripping and operator guards.
- Updated Blender runtime CI to test **4.2 LTS, 4.5 LTS and 5.2 LTS**.
- Updated the Blender extension package builder to include the 4.2+ tools module.
- Blender now has its own v0.7.61 release line while Unity remains v0.7.60.

## Unity 0.7.60

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
