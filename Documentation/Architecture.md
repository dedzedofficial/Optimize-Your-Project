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

Open the [GitHub Releases](https://github.com/dedzedofficial/Optimize-Your-Project/releases) page and download:

```text
optimize-your-project-blender-0.7.4.zip
```

Then in Blender use **Edit > Preferences > Add-ons > Install...** or **Get Extensions > Install from Disk**.

### VRChat Creator Companion / VCC

Use [Add Optimize Your Project to VCC](vcc://vpm/addRepo?url=https%3A%2F%2Fdedzedofficial.github.io%2FOptimize-Your-Project%2Findex.json), then add **Optimize Your Project** to the chosen project.

</details>

> **New here?** Start with the [Overview](../README.md). You can read the complete documentation directly on GitHub before installing anything.


Optimize Your Project is a **general developer optimization toolkit**. Unity is the first full integration and Blender is the first external DCC integration. VRChat, VCC and other social-VR workflows are supported where useful, but they are optional targets rather than the product's core identity.

## Unity

The repository root is a Unity Package Manager package. The v0.7.4 workflow is split into **Project** and **Avatar** pages, with a persistent interface language selector and action search:

- **Project** covers ordinary Unity projects: textures in an Assets folder plus particles, model imports, materials and realtime lights in loaded scenes. Project Insights adds largest-texture, Read/Write memory and oversized-mesh review. Material review finds exact-state duplicates and high-slot renderers.
- **Avatar** provides a narrower hierarchy scope for character/avatar projects. It does not require the VRChat SDK.

`VRProjectScanner` coordinates the existing scanner modules and `VRIssue` records. Those internal type names are retained for compatibility during v0.7; they do not limit the supported project type.

`VRTextureOptimizer` edits supported importer metadata and reimports only changed assets. `VRProjectMaintenance` handles conservative filename-based texture import fixes and trims only renderer material slots beyond the source mesh submesh count. `VRProjectInsights` compares saved material state for duplicates and reports oversized meshes and high material-slot setups. `VRParticleOptimizer` and `VRLightOptimizer` use Unity Undo for loaded scene objects where applicable. `VRSettings` stores per-user tool settings.

Automatic AssetPostprocessor-based optimization remains intentionally disabled. The user explicitly presses an optimization action so the scope is visible.

## Blender

`Blender/vr_optimizer_blender/` is a separate Blender add-on. The folder name is retained for compatibility during the v0.7 transition.

The primary v0.7.4 Blender workflow is split into **One-Click Cleanup** and **Batch Mesh Prep**. Single-object cleanup, Game-Ready copy, remesh and duplicate-vertex actions remain available, while selected static meshes can be cleaned or prepared as LOD sets in a batch. The Game-Ready path produces a separate static copy, can evaluate existing modifiers, applies rotation and scale, performs conservative cleanup and removes unused material slots. Heavy mesh review selects scene geometry over a chosen triangle threshold. Source objects are preserved.

Both Unity and Blender expose English, Japanese, Simplified Chinese and Korean interface options. The localization tables live inside each integration so the tool does not require a separate localization package or alter the user's game localization setup.

## Update architecture

`version.json` separates Unity and Blender release versions so one platform's release cannot incorrectly trigger an update warning for the other.

The Unity footer uses four states: current, one-patch update available, two-or-more-patches/newer-minor out of date, and unknown. Git installs can update through Unity Package Manager; other sources receive source-appropriate instructions.

## Compatibility principle

Historical package IDs and internal class names are kept when changing them would break installations. User-facing naming, documentation and future features use the broader **Optimize Your Project** identity.
