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
  <strong>Interface languages:</strong> English | 日本語 | 简体中文 | 한국어
</p>

<details open>
<summary><strong>Install / Download Optimize Your Project</strong></summary>

### Unity

Open **Window > Package Manager**, press **+**, choose **Add package from git URL**, then paste:

```text
https://github.com/dedzedofficial/Optimize-Your-Project.git
```

For the fixed v0.7.4 release:

```text
https://github.com/dedzedofficial/Optimize-Your-Project.git#v0.7.4
```

### Blender

[![INSTALL IN BLENDER 4.2+](https://img.shields.io/badge/INSTALL%20IN%20BLENDER-4.2%2B-EA7600?style=for-the-badge&logo=blender&logoColor=white)](https://github.com/dedzedofficial/Optimize-Your-Project/archive/refs/heads/main.zip?blender_version_min=4.2.0)

With **Blender 4.2 or newer already open**, drag the **INSTALL IN BLENDER** button from GitHub into the Blender window, then confirm **Install & Enable**. Blender downloads the extension and makes it available immediately in the open project. Clicking the button normally downloads the same extension ZIP instead. Blender documents website installation through a draggable extension URL.

For **Blender 3.6**, use the legacy ZIP from [GitHub Releases](https://github.com/dedzedofficial/Optimize-Your-Project/releases):

```text
optimize-your-project-blender-0.7.4.zip
```

Then use **Edit > Preferences > Add-ons > Install...**.

### VRChat Creator Companion / VCC

Use [Add Optimize Your Project to VCC](vcc://vpm/addRepo?url=https%3A%2F%2Fdedzedofficial.github.io%2FOptimize-Your-Project%2Findex.json), then add **Optimize Your Project** to the chosen project.

</details>

> **New here?** Start with the [Overview](README.md). You can read the complete documentation directly on GitHub before installing anything.


The product is now positioned as a **general developer optimization toolkit**. The historical Unity package ID `com.fishhwb.vr-optimizer` is retained for installation compatibility; it does not mean the tool is VR-only.

## 0.7.4

- Added interface language support for English, Japanese, Simplified Chinese and Korean across the main Unity and Blender workflows.
- Added a persistent Unity language selector and a Blender language selector so creators can switch the tool UI without changing their project language.
- Added Unity action search so common texture, mesh, particle, light, memory and scan tasks are easier to find.
- Added **Use Current Selection** for Unity asset scope so a selected Project asset or folder can set the working folder directly.
- Added Unity **Project Insights** with **Show Largest Textures**, **Review Read/Write Memory** and **Fix Oversized Mesh Imports** for supported high-triangle imported models.
- Added **Fix Texture Import Settings** for conservative normal-map and mask/data texture import corrections.
- Upgraded duplicate-material handling to **Fix Duplicate Material References**, remapping loaded renderer references to one exact matching material asset with Unity Undo while preserving duplicate asset files.
- Added **Clean Unused Material Slots** for trailing empty renderer slots beyond the mesh submesh count, with Unity Undo support. Non-empty extra materials are preserved.
- Upgraded material-cost handling to **Fix Safe Material Cost Issues**, combining exact duplicate remapping with safe trailing empty-slot cleanup while leaving topology-sensitive submesh changes untouched.
- Kept Read/Write review diagnostic-only because disabling CPU access can break runtime scripts, non-uniform mesh lighting and other workflows that require readable data.
- Added Blender **Clean Selected Meshes** for batch safe-copy cleanup while preserving every source object.
- Added Blender **Create Game-Ready Copy** for source-preserving static mesh preparation with optional modifier application, applied rotation/scale, geometry cleanup and unused material-slot removal.
- Added a Git-managed Blender install route using the repository Git URL plus the root Blender add-on proxy, with `git pull` updates.
- Added Blender **Create LODs for Selection** for supported static meshes using the existing guarded LOD workflow.
- Added Blender **Show Heavy Meshes** with a configurable triangle threshold.
- Reworked Blender layout around one-click cleanup, batch mesh preparation, advanced tools and compact result reporting.
- Expanded release checks and Blender regression tests to cover v0.7.4 languages and batch operations.
- Added a staged language roadmap for future releases while keeping new translations reviewable and optional.

## 0.7.1

- Added Blender **Clean Selected Mesh** as the first one-click action, producing a separate cleaned copy with unique output naming.
- Added conservative static-mesh checks, exact-coordinate vertex merging, loose geometry and zero-area face cleanup, unused material slot cleanup, and closed-surface normal repair.
- Preserved original meshes and added rollback if cleanup fails.
- Added consistent changed, unchanged, skipped, unsupported and failed summaries to Unity batches and Blender quick actions, with persistent Blender sidebar results.
- Improved Unity batch cancellation and per-item failure handling.
- Added Blender runtime regression checks and stronger release/version validation.

## 0.7.0

- Polished the Unity and Blender interfaces with clearer cards, stronger section hierarchy, larger primary actions and cleaner footers.
- Added a visible **Free for Developers** note explaining that the project is intended to help creators and newer developers without a paywall.
- Added optional Patreon support buttons; donations help fund testing, documentation, new optimization tools and future integrations while the project remains free.
- Collapsed Blender's advanced mesh controls behind an optional Advanced Tools section so one-click cleanup stays front and center.

- Repositioned Optimize Your Project around general Unity, Blender and real-time development workflows rather than VR-only development.
- Merged the old Unity World + Project split into one **PROJECT** page for ordinary Unity projects and loaded scenes.
- Kept **AVATAR** as an optional character hierarchy workflow without requiring the VRChat SDK.
- Removed the full Updates page and added a compact footer with green/current, orange/one-patch-behind, red/two-patches-or-newer-minor-behind, and grey/unknown status.
- Added a platform-specific `version.json` feed so Blender releases cannot be mistaken for Unity package updates.
- Added early Blender **One-Click Remesh** and **Merge Duplicate Vertices** actions.
- Kept Blender triangle reduction, join/atlas and static LOD tools under a clearer Advanced Mesh Tools section.
- Simplified installation and usage documentation around direct one-click jobs.
- Expanded static release validation for version consistency, Blender syntax and v0.7 UI/action expectations.

## 0.6.73

- Rebuilt World, Avatar and Project pages around direct action buttons; individual findings appear only after Scan Entire Project.
- Combined texture size caps and eligible automatic compression into one action with a single reimport per changed texture.
- Kept a dedicated Updates page and fixed package compiler and meta-file errors.

## 0.6.7

- Fixed ambiguous PackageInfo compiler reference in the update checker and completed Unity meta coverage.
- Added project texture compression cleanup and update checks.

## 0.6.6

- Split the Editor into World and Avatar pages with focused issue buttons and filters.
- Removed preset UI and added reviewed mesh compression.

## 0.6.5

- Added avatar inventory, avatar-scoped particle optimization and texture previews.
- Added VPM release automation and Creator Companion repository support.

## 0.6.4

- Simplified texture size controls and narrowed scene checks.

## 0.6.3

- Added platform texture overrides, particle optimization, light/mesh diagnostics and Git URL package support.
