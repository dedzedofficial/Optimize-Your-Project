# Optimize Your Project changelog

<img src="Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" alt="Optimize Your Project logo" width="96">

<p align="center">
  <a href="README.md"><strong>Overview</strong></a> |
  <a href="Blender/README.md"><strong>Blender Guide</strong></a> |
  <a href="Documentation/Roadmap.md"><strong>Roadmap</strong></a> |
  <a href="Documentation/Architecture.md"><strong>Architecture</strong></a> |
  <a href="CHANGELOG.md"><strong>Changelog</strong></a>
</p>

<p align="center">
  <strong>Unity interface languages:</strong> Auto | English | 日本語 | 简体中文 | 繁體中文 | 한국어 | Español | Français | Deutsch | Português | Русский | Italiano
</p>

<details open>
<summary><strong>Install / Download Optimize Your Project</strong></summary>

### Unity

Open **Window > Package Manager**, press **+**, choose **Add package from git URL**, then paste:

```text
https://github.com/dedzedofficial/Optimize-Your-Project.git
```

For the fixed v0.7.60 release after the tag is published:

```text
https://github.com/dedzedofficial/Optimize-Your-Project.git#v0.7.60
```

### Blender

Blender v0.7.60 packages are built by the release workflow:

[![DOWNLOAD BLENDER ZIP BUILDS](https://img.shields.io/badge/DOWNLOAD%20BLENDER-ZIP%20BUILDS-EA7600?style=for-the-badge&logo=blender&logoColor=white)](https://github.com/dedzedofficial/Optimize-Your-Project/actions/workflows/release-checks.yml)

The workflow produces the Blender 4.2+ extension ZIP and Blender 3.6 legacy add-on ZIP. Install the downloaded ZIP directly without extracting it.

### VRChat Creator Companion / VCC

Use [Add Optimize Your Project to VCC](vcc://vpm/addRepo?url=https%3A%2F%2Fdedzedofficial.github.io%2FOptimize-Your-Project%2Findex.json), then add **Optimize Your Project** to the chosen project.

</details>

The product is positioned as a **general developer optimization toolkit**. The historical Unity package ID `com.fishhwb.vr-optimizer` remains for compatibility and does not mean the tool is VR-only.

## 0.7.60

### Unity

- Rebuilt the Unity Editor window into a smaller action dashboard with Project and Character / Avatar pages, collapsed advanced settings and a slim update/support footer.
- Removed the old action search and large stacked descriptive cards.
- Added **Clean Missing Scripts** for loaded scenes and selected character hierarchies, removing only missing MonoBehaviour entries with Unity Undo support.
- Added **Optimize UI Raycasts** as another one-click action for both Project and Character / Avatar scopes.
- Optimize UI Raycasts disables `Raycast Target` only on detected decorative `UnityEngine.UI.Graphic` components that are not inside a detected EventSystem interaction hierarchy.
- UI controls and hierarchies containing pointer, drag, scroll, select, submit, cancel, move or update-selected handlers are skipped.
- The UI raycast optimizer uses serialized properties and type/interface discovery instead of taking a hard package reference on UGUI.
- Added Auto language detection using `Application.systemLanguage`, plus Traditional Chinese, Spanish, French, German, Portuguese, Russian and Italian alongside the existing languages.
- Kept manual language override, English fallback, importer history, detail protection, restore and optional memory trials.

### Blender

- Bumped the Blender add-on and extension metadata to v0.7.60 so the Blender behavior change is versioned with the rest of the milestone.
- Kept the existing **Remesh** and **LOD** focused interface rather than adding another large tool panel.
- Extended the existing LOD workflow with an optional **Create Collision Proxy from LOD2** setting.
- When enabled, the LOD action creates a separate `<Source>_COLLIDER` mesh copied from LOD2, with independent mesh data, wireframe display and rendering disabled.
- The collision proxy is source-preserving and participates in the same generated-output history, manual-edit protection and unchanged-result reuse as LOD0/LOD1/LOD2.
- The collision proxy option defaults off, so the standard LOD action still creates only LOD0, LOD1 and LOD2 unless requested.
- Added Blender 3.6 and 4.2 regression coverage for collision proxy generation, LOD2 equivalence, source preservation and unchanged second-pass reuse.

## 0.7.55

- Added surface-preserving Blender Remesh with guarded transfer of supported armature bindings, vertex weights and relative blendshapes.
- Added persistent generated-output history, detail protection and guarded replacement for Blender Remesh and LOD outputs.
- Added Unity Optimize Lighting with guarded static-lighting preparation and optional missing secondary-UV generation for supported imported static models.
- Added importer history, manual-edit protection, optional native asset-memory trials and conflict-checked Restore Last Import Batch.
- Consolidated model-import and material actions into their owning buttons.
- Simplified Blender to the reliable Remesh and LOD workflows and removed experimental cleanup, atlas, merge and Game-Ready controls.

## 0.7.4

- Added English, Japanese, Simplified Chinese and Korean interface support across the main Unity and Blender workflows.
- Added Unity action search, selection-based asset scope, Project Insights and conservative texture/material import fixes.
- Added Blender extension packaging for Blender 4.2+ while retaining the Blender 3.6 legacy add-on package.
- Introduced the compact Blender Remesh and selection-aware LOD direction.

## 0.7.1

- Added the first Blender one-click mesh workflow and source-preserving output model.
- Added consistent changed, unchanged, skipped, unsupported and failed summaries.
- Improved Unity batch cancellation and per-item failure handling.

## 0.7.0

- Repositioned Optimize Your Project around general Unity, Blender and real-time development workflows rather than VR-only development.
- Merged the older Unity World and Project views into one Project page and retained Character / Avatar as an optional scoped workflow.
- Added early Blender integration, VPM/update work and simplified installation documentation.

## Earlier releases

The 0.6.x line established texture, particle, light and mesh diagnostics, package installation, update checks, avatar scope and early optimization automation. The project has since consolidated those experiments into fewer owning actions and source-preserving workflows.
