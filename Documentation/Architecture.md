# Optimize Your Project architecture

<img src="../Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" alt="Optimize Your Project logo" width="96">

<p align="center">
  <a href="../README.md"><strong>Overview</strong></a> |
  <a href="../Blender/README.md"><strong>Blender Guide</strong></a> |
  <a href="../Documentation/Roadmap.md"><strong>Roadmap</strong></a> |
  <a href="../Documentation/Architecture.md"><strong>Architecture</strong></a> |
  <a href="../CHANGELOG.md"><strong>Changelog</strong></a>
</p>

## Install / Download Optimize Your Project

### Unity

Open **Window > Package Manager**, press **+**, choose **Add package from git URL**, then paste:

```text
https://github.com/dedzedofficial/Optimize-Your-Project.git
```

For fixed v0.7.61:

```text
https://github.com/dedzedofficial/Optimize-Your-Project.git#v0.7.61
```

### Blender 4.2+

Blender is distributed only through the modern Blender Extensions package:

```text
optimize-your-project-blender-extension-0.7.61.zip
```

Open the latest successful **Check release packages** run and download the `optimize-your-project-blender-0.7.61` artifact. Install the extension ZIP through **Edit > Preferences > Get Extensions > Install from Disk**.

Blender 3.6 and the old legacy add-on ZIP are no longer part of the supported release path.

### VRChat Creator Companion / VCC

Use:

```text
vcc://vpm/addRepo?url=https%3A%2F%2Fdedzedofficial.github.io%2FOptimize-Your-Project%2Findex.json
```

VRChat remains optional. The Unity tools do not require a VR SDK for ordinary projects.

## Product identity

Optimize Your Project is a **general developer optimization toolkit**. Unity is the primary game-engine integration and Blender is the first DCC integration. VRChat, VCC and other social-VR workflows are supported where useful, but they do not define the product.

The project uses one public release version. In v0.7.61 both Unity and Blender report **0.7.61**.

## Unity architecture

The repository root is a Unity Package Manager package. The editor window is split into **Project** and **Avatar** pages and intentionally keeps the visible action set compact.

Project actions currently cover:

- texture import optimization and safe import repair,
- model import compression and Unity mesh import optimization,
- particle limits and optional module disabling,
- safe material-reference and trailing-slot cleanup,
- baked lighting setup,
- missing-script cleanup,
- UI raycast optimization,
- project reviews and scans.

Avatar uses the same owning actions but limits scene-object work to the selected hierarchy where supported. It does not require the VRChat SDK.

`VRProjectScanner` coordinates scanner modules and `VRIssue` results. The historical `VR` prefix remains in internal class names during v0.7 for compatibility and does not limit the supported project type.

`VRTextureOptimizer` edits supported importer metadata and avoids unnecessary platform overrides when the base texture limit is already strict enough. Explicit formats, compression choices and stricter size limits are preserved.

`VRParticleOptimizer` handles the existing particle action. Constant and Two Constants lifetime modes can be capped without rewriting authored lifetime curves. Other optional particle-module changes remain user-controlled through Advanced settings.

`VRLightOptimizer` is restricted to enabled realtime lights when disabling realtime shadows. Baked and Mixed lights are rejected by the optimizer itself. Scene-object edits use Unity Undo and prefab-instance recording where applicable.

`VRLightingSetup` performs the larger baked-light preparation workflow. It checks scene state before changes, prepares secondary UV imports where supported, marks suitable static meshes for GI and starts a bake only after setup succeeds.

`VRProjectMaintenance` owns conservative material and texture-import maintenance. `VRProjectInsights` owns review-style diagnostics. `VRSettings` stores per-user tool settings.

Automatic AssetPostprocessor-based optimization remains intentionally disabled. Users explicitly press an optimization action so the scope and timing stay visible.

## Import history and recovery

`VRImportHistory` stores source and metadata fingerprints, per-job policy identifiers, explicit protection and recoverable last-batch metadata in a project-local `ScriptableSingleton`.

`VRImportBatch` is the shared guarded entry point for texture, model and UV importer changes. Known changes rebase other records for the same GUID so the tool does not mistake its own work for a manual edit. Unknown later importer edits are preserved rather than overwritten.

A memory trial retains only changes that show a positive sampled native asset-memory reduction. This is a narrow importer check and is not presented as proof of player FPS or visual quality.

## Blender architecture

Blender support starts at **4.2** and uses the Blender Extensions system.

The maintained core lives under:

```text
Blender/vr_optimizer_blender/
```

The root `blender_manifest.toml` and `__init__.py` provide the extension package entry point. `scripts/build_blender_extension.py` builds the supported ZIP.

### Core mesh workflow

The existing Blender core provides:

- One-Click Remesh,
- LOD0 / LOD1 / LOD2 generation,
- optional collision proxy generation from LOD2,
- generated-output ownership and reuse,
- guarded transfer of supported UVs, materials, vertex weights, armature bindings and relative shape keys.

Source objects are preserved. Generated outputs are tracked so unchanged runs can reuse them and changed sources replace only verified untouched generated copies. Manual edits block automatic replacement until the user explicitly resets history.

### Blender 4.2+ tools

`tools_42.py` extends the compact core with modern static-mesh actions:

- **Generate Lightmap UV** creates a protected second UV channel using deterministic face-island packing without context-sensitive UV operators.
- **Link Identical Mesh Data** links exact supported static duplicates to one shared mesh datablock while preserving separate object transforms.
- **Strip Collider Render Data** removes materials, UV layers and color attributes only from optimizer-generated collision proxies.

The tools reject ambiguous or unsupported inputs rather than guessing.

### Blender 5.x animation compatibility

Blender 5.x removed the old direct `Action.fcurves` workflow. `deform_transfer.py` supports the newer slotted Action/channelbag API while retaining the compatible path required by Blender 4.2.

## Validation

The release workflow builds the Unity package and Blender extension, runs static release checks, and exercises Blender runtime tests on:

- Blender 4.2 LTS,
- Blender 4.5 LTS,
- Blender 5.2 LTS.

Blender 4.2 also validates the final Extensions ZIP with Blender's own extension validator.

## Update architecture

`version.json` contains the unified project version plus compatibility fields used by the existing Unity and Blender build paths.

The Unity footer checks the same project feed. Git installs can update through Unity Package Manager; embedded, VCC or registry installs receive source-appropriate instructions instead of being modified behind the user's back.

## Compatibility principle

Historical package IDs and internal class names are retained when changing them would break existing installations. User-facing naming, documentation and future work use the broader **Optimize Your Project** identity.
