# Optimize Your Project

<img src="Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" alt="Optimize Your Project logo" width="150">

<p align="center">
  <a href="README.md"><strong>Overview</strong></a> |
  <a href="Blender/README.md"><strong>Blender Guide</strong></a> |
  <a href="Documentation/Roadmap.md"><strong>Roadmap</strong></a> |
  <a href="Documentation/Architecture.md"><strong>Architecture</strong></a> |
  <a href="CHANGELOG.md"><strong>Changelog</strong></a>
</p>

**v0.7.61 | Unity + Blender 4.2+ | General developer optimization tools | FISHHWB | Ded Zed**

Optimize Your Project is a free general developer optimization toolkit for reducing repetitive project cleanup and optimization work. Unity and Blender now share one project release version so the package, documentation and downloads stay easier to follow.

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

Blender support targets the modern **Blender Extensions** system only. The minimum supported Blender version is **4.2**.

Open the latest successful release-check workflow:

https://github.com/dedzedofficial/Optimize-Your-Project/actions/workflows/release-checks.yml

Download the `optimize-your-project-blender-0.7.61` artifact and install:

```text
optimize-your-project-blender-extension-0.7.61.zip
```

Use **Edit > Preferences > Get Extensions > Install from Disk** and choose the ZIP without extracting it. Then press **N** in the 3D Viewport and open the **FISHHWB** tab.

### VRChat / VCC (optional)

```text
vcc://vpm/addRepo?url=https%3A%2F%2Fdedzedofficial.github.io%2FOptimize-Your-Project%2Findex.json
```

The Unity package does not require a VR SDK for normal projects.

## Unity v0.7.61

The compact Unity Project / Character interface includes:

- **Optimize Textures**
- **Optimize Model Imports**
- **Optimize Particles**
- **Fix Material Costs**
- **Optimize Lighting**
- **Clean Missing Scripts**
- **Optimize UI Raycasts**
- project reviews for large textures, Read/Write memory, heavy meshes and full scans
- importer history, protection, memory trials and last-batch restoration under Advanced settings

### Existing-feature improvements in 0.7.61

- Texture optimization no longer creates unnecessary platform overrides when the base texture limit is already equal to or stricter than the selected target.
- Existing stricter platform texture limits are preserved instead of being increased.
- Particle lifetime capping now supports both Constant and Two Constants lifetime modes while leaving authored curve-based lifetimes untouched.
- Realtime shadow optimization now independently refuses disabled, Mixed and Baked lights, and records prefab-instance changes correctly.
- The Unity update checker now reads the unified project version feed while remaining compatible with the older Unity-specific field.

## Blender v0.7.61

Blender is focused on **4.2+** rather than carrying a legacy pre-4.2 release path.

### One-Click Remesh

Creates a separate reduced copy while preserving the source. Supported UV layers, material assignments, relative shape keys, armature bindings and vertex weights are retained through the guarded workflow.

### LOD Generation

**Create LOD0 / LOD1 / LOD2** creates source-preserving static-mesh LOD sets. The same visible action handles one or several selected supported meshes.

Optional **Create Collision Proxy from LOD2** adds a separate render-disabled wireframe collider candidate while keeping LOD2 and the original source intact.

### Generate Lightmap UV

**Generate Lightmap UV** creates a protected `LightmapUV` second UV channel on supported static meshes.

The tool:

- preserves geometry and the primary UV map,
- only creates `LightmapUV` when it can safely be the second channel,
- never guesses which existing secondary UV should be replaced,
- builds a deterministic non-overlapping per-face lightmap atlas directly in UV data,
- keeps every face island inside the 0 to 1 UV range,
- avoids context-sensitive UV operators so batch and headless processing remain reliable,
- supports Blender Undo.

The face-island layout favors reliability and separation over maximum packing efficiency. More advanced shared-island packing can be added later without replacing user UV data automatically.

### Link Identical Mesh Data

**Link Identical Mesh Data** finds exact selected static duplicates and makes them share one Blender mesh datablock.

Matching includes geometry, topology, UV data, mesh attributes and material assignments. It skips modifiers, shape keys, linked-library meshes and object-level material overrides. Each object's transform remains independent.

### Strip Collider Render Data

**Strip Collider Render Data** operates only on generated objects marked as collision proxies.

It removes render-only data that a collider candidate does not need:

- material slots,
- UV layers,
- color attributes.

The collider geometry and object transform are preserved. Ordinary meshes are rejected instead of being modified accidentally.

### Blender 4.2+ validation

The release workflow validates:

- Blender 4.2 LTS
- Blender 4.5 LTS
- Blender 5.2 LTS

Blender 5.x uses the modern slotted Action/channelbag animation API while 4.2 remains supported through the compatible path.

## Languages

Unity supports Auto, English, Japanese, Simplified Chinese, Traditional Chinese, Korean, Spanish, French, German, Portuguese, Russian and Italian.

The Blender interface currently supports English, Japanese, Simplified Chinese and Korean for its main workflows and 4.2+ tools.

## Free for developers

Optimize Your Project is free to use. The goal is to turn repetitive optimization jobs into clear, useful actions without putting basic developer help behind a paywall.

Optional support: https://www.patreon.com/cw/DedZed

## Safety

Use source control or backups for production projects and inspect generated results in the target engine.

Blender Remesh and LOD preserve source objects. Lightmap UV generation preserves geometry and primary UVs. Identical mesh-data linking is Undoable, but linked duplicates intentionally share later mesh-data edits until unlinked again. Collider render-data stripping is restricted to generated collision proxies.

Unity importer changes use guarded history and restoration. Scene-object optimizations use Unity Undo where practical.

## Repository layout

```text
package.json                                  Unity package manifest
version.json                                  Unified project release version
Editor/FISHHWBVR/                            Unity Editor implementation
Blender/vr_optimizer_blender/                Blender core and 4.2+ tools
blender_manifest.toml                        Blender Extensions manifest
scripts/test_blender.py                      Remesh / LOD regression tests
scripts/test_blender_42.py                   Blender 4.2+ tool regression tests
scripts/test_blender_52.py                   Blender 5.2 slotted Action regression tests
scripts/build_blender_extension.py           Blender Extensions ZIP builder
.github/workflows/release-checks.yml         Package and runtime validation
```

## Keywords

Unity optimization, Blender 4.2 extension, one-click optimization, game optimization, asset optimization, texture optimization, mesh optimization, lightmap UV, mesh instancing, collision proxy, LOD, VR, XR, VRChat, mobile optimization and indie development.

## Community

Website: https://fishhwb.github.io/

Discord: https://discord.gg/wZGxxkk4Jg

Patreon: https://www.patreon.com/cw/DedZed
