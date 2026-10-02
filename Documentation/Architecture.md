# Optimize Your Project architecture

<img src="../Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" alt="Optimize Your Project logo" width="96">

Optimize Your Project is a **general developer optimization toolkit**. Unity is the first full integration and Blender is the first external DCC integration. VRChat, VCC and other social-VR workflows are supported where useful, but they are optional targets rather than the product's core identity.

## Unity

The repository root is a Unity Package Manager package. The v0.7.4 workflow is split into **Project** and **Avatar** pages, with a persistent interface language selector and action search:

- **Project** covers ordinary Unity projects: textures in an Assets folder plus particles, model imports and realtime lights in loaded scenes. Project Insights adds largest-texture, Read/Write memory and heavy-mesh review without changing project files.
- **Avatar** provides a narrower hierarchy scope for character/avatar projects. It does not require the VRChat SDK.

`VRProjectScanner` coordinates the existing scanner modules and `VRIssue` records. Those internal type names are retained for compatibility during v0.7; they do not limit the supported project type.

`VRTextureOptimizer` edits supported importer metadata and reimports only changed assets. `VRParticleOptimizer` and `VRLightOptimizer` use Unity Undo for loaded scene objects where applicable. `VRSettings` stores per-user tool settings.

Automatic AssetPostprocessor-based optimization remains intentionally disabled. The user explicitly presses an optimization action so the scope is visible.

## Blender

`Blender/vr_optimizer_blender/` is a separate Blender add-on. The folder name is retained for compatibility during the v0.7 transition.

The primary v0.7.4 Blender workflow is split into **One-Click Cleanup** and **Batch Mesh Prep**. Single-object cleanup, remesh and duplicate-vertex actions remain available, while selected static meshes can now be cleaned or prepared as LOD sets in a batch. Heavy mesh review selects scene geometry over a chosen triangle threshold. Source objects are preserved.

Both Unity and Blender expose English, Japanese, Simplified Chinese and Korean interface options. The localization tables live inside each integration so the tool does not require a separate localization package or alter the user's game localization setup.

## Update architecture

`version.json` separates Unity and Blender release versions so one platform's release cannot incorrectly trigger an update warning for the other.

The Unity footer uses four states: current, one-patch update available, two-or-more-patches/newer-minor out of date, and unknown. Git installs can update through Unity Package Manager; other sources receive source-appropriate instructions.

## Compatibility principle

Historical package IDs and internal class names are kept when changing them would break installations. User-facing naming, documentation and future features use the broader **Optimize Your Project** identity.
