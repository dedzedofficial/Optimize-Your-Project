# Optimize Your Project architecture

<img src="../Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" alt="Optimize Your Project logo" width="96">

<p align="center">
  <a href="../README.md"><strong>Overview</strong></a> |
  <a href="../Blender/README.md"><strong>Blender Guide</strong></a> |
  <a href="../Documentation/Roadmap.md"><strong>Roadmap</strong></a> |
  <a href="../Documentation/Architecture.md"><strong>Architecture</strong></a> |
  <a href="../CHANGELOG.md"><strong>Changelog</strong></a>
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

The Blender build now produces two real ZIP packages:

- **Blender 4.2+ / Blender Extensions:** `optimize-your-project-blender-extension-0.7.4.zip`
- **Blender 3.6 legacy add-on:** `optimize-your-project-blender-0.7.4.zip`

[![DOWNLOAD BLENDER ZIP BUILDS](https://img.shields.io/badge/DOWNLOAD%20BLENDER-ZIP%20BUILDS-EA7600?style=for-the-badge&logo=blender&logoColor=white)](https://github.com/dedzedofficial/Optimize-Your-Project/actions/workflows/release-checks.yml)

Open the latest successful **Check release packages** run and download the `optimize-your-project-blender-0.7.4` artifact. It contains both ZIP files. Use the **extension** ZIP for `extensions.blender.org`. The official Blender Extensions listing will replace this temporary download button after publication.

The legacy ZIP also remains available from [GitHub Releases](https://github.com/dedzedofficial/Optimize-Your-Project/releases) when a matching Blender release is published.

### VRChat Creator Companion / VCC

Use [Add Optimize Your Project to VCC](vcc://vpm/addRepo?url=https%3A%2F%2Fdedzedofficial.github.io%2FOptimize-Your-Project%2Findex.json), then add **Optimize Your Project** to the chosen project.

</details>

> **New here?** Start with the [Overview](../README.md). You can read the complete documentation directly on GitHub before installing anything.


Optimize Your Project is a **general developer optimization toolkit**. Unity is the first full integration and Blender is the first external DCC integration. VRChat, VCC and other social-VR workflows are supported where useful, but they are optional targets rather than the product's core identity.

## Unity

The repository root is a Unity Package Manager package. The v0.7.4 workflow is split into **Project** and **Avatar** pages, with a persistent interface language selector and action search:

- **Project** covers ordinary Unity projects: textures in an Assets folder plus particles, model imports, materials and realtime lights in loaded scenes. Project Insights adds largest-texture and Read/Write memory review plus importer-side oversized-mesh fixes. Material maintenance remaps exact-state duplicate references and removes only safely identifiable trailing empty slots.
- **Avatar** provides a narrower hierarchy scope for character/avatar projects. It does not require the VRChat SDK.

`VRProjectScanner` coordinates the existing scanner modules and `VRIssue` records. Those internal type names are retained for compatibility during v0.7; they do not limit the supported project type.

`VRTextureOptimizer` edits supported importer metadata and reimports only changed assets. `VRProjectMaintenance` handles conservative filename-based texture import fixes, exact duplicate-material remapping, trailing empty material-slot cleanup and importer-side optimization for oversized imported meshes. `VRProjectInsights` retains the exact material signature and diagnostic helpers used to decide safe automated fixes. `VRParticleOptimizer` and `VRLightOptimizer` use Unity Undo for loaded scene objects where applicable. `VRSettings` stores per-user tool settings.

Automatic AssetPostprocessor-based optimization remains intentionally disabled. The user explicitly presses an optimization action so the scope is visible.

## Blender

`Blender/vr_optimizer_blender/` is a separate Blender add-on. The folder name is retained for compatibility during the v0.7 transition.

The v0.7.4 Blender workflow is intentionally limited to **Remesh** and **LOD generation**. The add-on creates source-preserving remeshed copies and LOD0 / LOD1 / LOD2 sets for supported static meshes. A batch LOD operator handles multiple selected meshes. Shape-key, vertex-group and armature-driven inputs are rejected because these operations change topology. Earlier experimental cleanup, Game-Ready, merge, heavy-mesh, triangle-limit and atlas code was removed from the supported Blender add-on because it was not reliable or useful enough to justify the larger UI.

### Blender package architecture

The repository root contains `blender_manifest.toml` plus a small `__init__.py` proxy. `scripts/build_blender_extension.py` packages those files with the maintained Blender add-on into `optimize-your-project-blender-extension-0.7.4.zip`, which is the Blender 4.2+ and Blender Extensions submission package. Blender 3.6 continues to use the dedicated legacy add-on ZIP.

Both Unity and Blender expose English, Japanese, Simplified Chinese and Korean interface options. The localization tables live inside each integration so the tool does not require a separate localization package or alter the user's game localization setup.

## Update architecture

`version.json` separates Unity and Blender release versions so one platform's release cannot incorrectly trigger an update warning for the other.

The Unity footer uses four states: current, one-patch update available, two-or-more-patches/newer-minor out of date, and unknown. Git installs can update through Unity Package Manager; other sources receive source-appropriate instructions.

## Compatibility principle

Historical package IDs and internal class names are kept when changing them would break installations. User-facing naming, documentation and future features use the broader **Optimize Your Project** identity.
