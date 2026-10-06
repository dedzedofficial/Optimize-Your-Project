# Optimize Your Project

<img src="Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" alt="Optimize Your Project logo" width="150">

<p align="center">
  <a href="README.md"><strong>Overview</strong></a> |
  <a href="Blender/README.md"><strong>Blender Guide</strong></a> |
  <a href="Documentation/Roadmap.md"><strong>Roadmap</strong></a> |
  <a href="Documentation/Architecture.md"><strong>Architecture</strong></a> |
  <a href="CHANGELOG.md"><strong>Changelog</strong></a>
</p>

**Unity v0.7.60 | Blender v0.7.61 | General developer optimization tools | FISHHWB | Ded Zed**

Optimize Your Project is a free general developer optimization toolkit for reducing repetitive project cleanup and optimization work. Unity and Blender are developed independently so one integration can improve without forcing a version bump on the other.

## Install / Download Optimize Your Project

### Unity

Open **Window > Package Manager**, press **+**, choose **Add package from git URL**, then paste:

```text
https://github.com/dedzedofficial/Optimize-Your-Project.git
```

For fixed Unity v0.7.60:

```text
https://github.com/dedzedofficial/Optimize-Your-Project.git#v0.7.60
```

### Blender 4.2+

Blender support now targets the modern **Blender Extensions** system only. The minimum supported Blender version is **4.2**.

Download the latest successful `optimize-your-project-blender-<version>` workflow artifact from:

https://github.com/dedzedofficial/Optimize-Your-Project/actions/workflows/release-checks.yml

Inside it, install:

```text
optimize-your-project-blender-extension-0.7.61.zip
```

In Blender, use **Edit > Preferences > Get Extensions > Install from Disk**, choose the ZIP without extracting it, then open the **FISHHWB** tab in the 3D Viewport sidebar.

### VRChat / VCC (optional)

Use the VCC repository link when you want the Unity package in a VRChat Creator Companion project:

```text
vcc://vpm/addRepo?url=https%3A%2F%2Fdedzedofficial.github.io%2FOptimize-Your-Project%2Findex.json
```

The Unity tools do not require a VR SDK for normal projects.

## Unity v0.7.60

The Unity window stays compact with Project and Character / Avatar pages.

Primary actions include:

- **Optimize Textures** for size, compression and recognized import fixes.
- **Optimize Model Imports** for mesh compression and Unity importer optimization without reducing source topology.
- **Optimize Particles** for selected particle-cost limits.
- **Fix Material Costs** for exact duplicate references and safe trailing empty slots.
- **Optimize Lighting** for guarded baked-light setup on eligible loaded-scene content.
- **Clean Missing Scripts** with Unity Undo support.
- **Optimize UI Raycasts** to disable unnecessary `Raycast Target` flags on decorative UI while preserving detected interactive controls.
- Project reviews for largest textures, Read/Write memory, heavy meshes and full scans.

Unity importer history, detail protection, memory trials and last-batch restoration remain under Advanced settings.

## Blender v0.7.61

Blender is now focused on **4.2+** and is packaged only as a Blender Extension.

### Remesh

**One-Click Remesh** creates a separate reduced copy while preserving the source. Supported UV layers, material assignments, armature bindings, vertex weights and relative shape keys are retained through the guarded workflow.

### LOD generation

**Create LOD0 / LOD1 / LOD2** creates source-preserving static-mesh LOD sets. Multiple selected supported meshes can be processed in one action.

Optional **Create Collision Proxy from LOD2** adds a separate render-disabled wireframe collider candidate without modifying the original mesh.

### Generate Lightmap UV

The new **Generate Lightmap UV** action is for selected supported static meshes. It:

- preserves geometry and the primary UV map,
- creates `LightmapUV` only when it can safely become the second UV channel,
- uses Blender Smart UV Project with a fractional island margin,
- keeps existing secondary UV channels untouched instead of guessing which one to replace,
- supports Blender Undo.

This is useful for static assets intended for baked lighting workflows in Unity and other real-time engines.

### Link Identical Mesh Data

The new **Link Identical Mesh Data** action finds exact selected static duplicates and makes them share one Blender mesh datablock.

It only links meshes whose geometry, topology, UV data, attributes and material assignments match. It skips modifiers, shape keys, linked-library meshes and object-level material overrides. Object transforms remain independent.

This reduces duplicated live mesh data in repeated static props and gives downstream pipelines a clearer instancing opportunity without changing where objects are placed.

### Blender 4.2+ validation

The Blender workflow now tests the extension against:

- Blender 4.2 LTS
- Blender 4.5 LTS
- Blender 5.2 LTS

The release path no longer publishes or validates a legacy pre-4.2 add-on ZIP.

## Languages

Unity supports Auto, English, Japanese, Simplified Chinese, Traditional Chinese, Korean, Spanish, French, German, Portuguese, Russian and Italian.

The Blender sidebar currently supports English, Japanese, Simplified Chinese and Korean for the main workflows, including the 4.2+ tools.

## Free for developers

Optimize Your Project is free to use. The goal is to turn repetitive optimization work into clear actions that are useful to experienced developers and easier for newer creators to understand.

Optional development support: https://www.patreon.com/cw/DedZed

## Safety

Optimization can affect appearance or runtime behavior. Keep source control or backups for production projects and inspect generated results in the target engine.

Blender Remesh and LOD workflows preserve source objects. Lightmap UV generation does not change geometry or the primary UV channel. Identical mesh-data linking is Undoable, but linked duplicates intentionally share later mesh-data edits until unlinked again.

## Repository layout

```text
package.json                                  Unity package manifest
version.json                                  Independent Unity / Blender versions
Editor/FISHHWBVR/                            Unity Editor implementation
Blender/vr_optimizer_blender/                Blender core and 4.2+ tools
blender_manifest.toml                        Blender Extensions manifest
scripts/test_blender.py                      Remesh / LOD regression tests
scripts/test_blender_42.py                   Blender 4.2+ tool regression tests
scripts/build_blender_extension.py           Blender Extensions ZIP builder
.github/workflows/release-checks.yml         Package and Blender runtime validation
```

## Keywords

Unity optimization, Blender 4.2 extension, one-click optimization, game optimization, asset optimization, texture optimization, mesh optimization, lightmap UV, mesh instancing, collision proxy, LOD, VR, XR, VRChat, mobile optimization and indie development.

## Community

Website: https://fishhwb.github.io/

Discord: https://discord.gg/wZGxxkk4Jg

Patreon: https://www.patreon.com/cw/DedZed
