# Optimize Your Project

<img src="Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" alt="Optimize Your Project logo" width="150">

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

The Blender build now produces two real ZIP packages:

- **Blender 4.2+ / Blender Extensions:** `optimize-your-project-blender-extension-0.7.4.zip`
- **Blender 3.6 legacy add-on:** `optimize-your-project-blender-0.7.4.zip`

[![DOWNLOAD BLENDER ZIP BUILDS](https://img.shields.io/badge/DOWNLOAD%20BLENDER-ZIP%20BUILDS-EA7600?style=for-the-badge&logo=blender&logoColor=white)](https://github.com/dedzedofficial/Optimize-Your-Project/actions/workflows/release-checks.yml)

Open the latest successful **Check release packages** run and download the `optimize-your-project-blender-0.7.4` artifact. It contains both ZIP files. Use the **extension** ZIP for `extensions.blender.org`. The official Blender Extensions listing will replace this temporary download button after publication.

The legacy ZIP also remains available from [GitHub Releases](https://github.com/dedzedofficial/Optimize-Your-Project/releases) when a matching Blender release is published.

### VRChat Creator Companion / VCC

Use [Add Optimize Your Project to VCC](vcc://vpm/addRepo?url=https%3A%2F%2Fdedzedofficial.github.io%2FOptimize-Your-Project%2Findex.json), then add **Optimize Your Project** to the chosen project.

</details>

> **New here?** Start with the [Overview](README.md). You can read the complete documentation directly on GitHub before installing anything.


**v0.7.4 · General developer optimization tools · Unity + Blender · FISHHWB | Ded Zed**

Optimize Your Project is a free toolkit for developers building real-time projects. Its priority is removing repetitive optimization work through clear one-click and batch actions for games, mobile projects, VR titles, social experiences, prototypes and reusable asset packs.

v0.7.4 is a major usability and workflow update. It adds searchable Unity actions, texture import repair, material-cost tools, richer mesh review, Blender batch preparation, a Game-Ready copy workflow and interface language support for **English, Japanese, Simplified Chinese and Korean**.

## Quick install

| Platform | Fastest install |
| --- | --- |
| **Unity** | Package Manager → **+** → **Add package from git URL** → paste `https://github.com/dedzedofficial/Optimize-Your-Project.git` |
| **Blender 4.2+** | Download `optimize-your-project-blender-extension-0.7.4.zip` from the latest successful release-check artifact; this is the Blender Extensions submission ZIP |
| **VRChat / VCC (optional)** | [Add the VPM repository](vcc://vpm/addRepo?url=https%3A%2F%2Fdedzedofficial.github.io%2FOptimize-Your-Project%2Findex.json), then add **Optimize Your Project** to the chosen project |

For a fixed Unity release after the v0.7.4 tag is published:

```text
https://github.com/dedzedofficial/Optimize-Your-Project.git#v0.7.4
```

## Languages

The main Unity and Blender workflows support:

- English
- Japanese
- Simplified Chinese
- Korean

Unity stores the selected tool language as an Editor preference. Blender exposes a Language control at the top of the sidebar.

Future language work is tracked in [Documentation/Roadmap.md](Documentation/Roadmap.md). Planned additions include Spanish, French, German, Brazilian Portuguese, Italian, Traditional Chinese, Polish, Turkish and Russian.

## Unity v0.7.4

Open **FISHHWB → Optimize Your Project**.

The Unity window keeps the two focused work pages:

- **PROJECT** for ordinary project assets and loaded scenes.
- **CHARACTER / AVATAR** for one selected character hierarchy without requiring a VR SDK.

### Faster navigation

- **Language selector** at the top of the window.
- **Find an action** search box to narrow the interface to texture, mesh, particle, light, memory or scan tasks.
- **Use Current Selection** can set the Project asset scope from the selected Project window asset or folder.
- Detailed findings stay hidden until a review or scan action is requested.

### Project optimization buttons

- **Compress & Size Textures** applies supported platform size caps and compression while preserving stricter existing limits and explicit formats.
- **Fix Texture Import Settings** applies conservative filename-based fixes for recognized normal maps and non-color mask/data textures while preserving unrelated import settings.
- **Optimize Particles** applies selected particle limits to loaded scenes or the chosen character hierarchy.
- **Compress Imported Meshes** applies Unity model-importer mesh compression to model assets used in the current scope.
- **Fix Duplicate Material References** remaps loaded renderers from exact duplicate material assets to one canonical exact match with Unity Undo. Duplicate asset files are preserved.
- **Clean Unused Material Slots** removes only trailing empty renderer slots beyond the mesh's actual submesh count and supports Unity Undo. Non-empty extra materials are preserved.
- **Fix Safe Material Cost Issues** combines exact duplicate-material remapping with safe trailing empty-slot cleanup. High submesh counts that require art or topology changes are left untouched.
- **Disable Realtime Shadows** disables supported realtime light shadows with Unity Undo support.
- **Scan Entire Project** runs the heavier diagnostic pass and shows filterable Critical / Warning results.

### Project Insights

These buttons help find expensive assets without changing project files:

- **Show Largest Textures** lists the largest source textures in the chosen Assets folder.
- **Review Read/Write Memory** lists textures and imported models with CPU-readable copies enabled.
- **Fix Oversized Mesh Imports** applies Medium mesh compression plus Unity vertex/polygon import optimization to supported high-triangle imported models without changing triangle topology.

Read/Write review is intentionally diagnostic-only. CPU-readable copies can consume additional memory, but disabling them automatically can break scripts, runtime mesh access and other workflows that require readable data. Unity documents the extra CPU memory cost for readable texture and mesh data.

### Compact update footer

The footer shows the installed version and update state:

- **Green:** current.
- **Orange:** one patch release behind.
- **Red:** two or more patch releases behind, or a newer minor/major release exists.
- **Grey:** update status has not been checked or could not be resolved.

Git-installed packages can use the footer update button directly. Embedded or VCC installs show the correct update route.

## Blender v0.7.4

The Blender add-on is under `Blender/vr_optimizer_blender/`.

After installation, open the 3D Viewport sidebar with **N**, then open the **FISHHWB** tab.

### One-click cleanup

- **Clean Active Mesh** creates a separate cleaned copy.
- **Clean Selected Meshes** batch-cleans supported selected static meshes and preserves every original.
- **Create Game-Ready Copy** creates a separate `_GameReady` static copy, optionally applies existing modifiers, applies rotation and scale, cleans geometry and removes unused material slots while preserving the source.
- **One-Click Remesh** creates a remeshed static-mesh copy.
- **Merge Duplicate Vertices** creates a copy and merges nearby vertices using the Merge Distance setting.

### Batch mesh preparation

- **Create LODs for Selection** creates LOD0 / LOD1 / LOD2 sets for supported selected static meshes.
- **Show Heavy Meshes** selects scene mesh objects over a configurable triangle threshold.
- Unsupported topology-sensitive content is skipped rather than forced through destructive processing.

### Advanced Mesh Tools

The earlier advanced tools remain available:

- **Create Reduced Copy**
- **Join Selected and Merge Vertices**
- **Merge Base Color Textures + UVs**
- **Create LOD0 / LOD1 / LOD2** for the active mesh

The add-on keeps source objects available for comparison whenever its copy-based workflow is used.

## Action results

Unity batches and Blender quick actions report **Changed**, **Unchanged**, **Skipped**, **Unsupported** and **Failed**.

Unity importer jobs work on unique assets. Blender copy-based jobs keep the source mesh untouched. Cancelled or unsupported items are reported instead of being silently changed.

## Future development

The [version-by-version development roadmap](Documentation/Roadmap.md) tracks the path toward v1.0.

The v1.0 goal remains at least **90% of identified, safely automatable optimization tasks** available through one action for each declared stable integration and target.

Planned work includes:

- deeper material consolidation and draw-call tooling beyond the safe automatic fixes in v0.7.4,
- lighting and effects preparation,
- physics and collider helpers,
- build-size and dependency review,
- safer restore and compare workflows,
- Godot and Unreal integrations,
- more language support,
- searchable help that can find, explain and route directly to supported fixes.

Roadmap items are future plans. Only implemented and tested behavior counts as current support.

## Free for developers

**Optimize Your Project is free to use.** It is built to reduce repetitive optimization work, make development easier and give newer creators useful tools without putting the basics behind a paywall.

If the project saves you time and you want to help it grow, you can support development on [Patreon](https://www.patreon.com/cw/DedZed). Optional support helps fund testing, documentation, new one-click tools and future integrations.

**Supporting is always optional. The project stays free either way.**

## Safety

Optimization changes can affect appearance or runtime behavior. Use source control or a backup before large batches and inspect the result in the target platform.

Unity importer jobs change import metadata rather than source image files. Scene particle and light changes support Undo where applicable. Read/Write review does not automatically disable CPU access.

Blender cleanup and preparation tools create copies for supported mesh workflows instead of replacing source objects.

## Repository layout

```text
package.json                         Unity package manifest
version.json                         Unity / Blender update feed
Editor/FISHHWBVR/                   Unity Editor implementation
Blender/vr_optimizer_blender/       Blender add-on
Blender/README.md                    Blender install and usage
Documentation/                      Architecture and roadmap
scripts/                            Release/package checks
.github/workflows/                  VPM, Blender and PR validation
```

## Release checks

Pull requests validate:

- Unity package and update-feed version consistency.
- Blender add-on version consistency and Python syntax.
- Required branding and package files.
- Unity v0.7 Project / Character UI shape.
- Unity language and Project Insights integration.
- Blender cleanup, Game-Ready copy, remesh, vertex merge, batch cleanup, batch LOD and heavy-mesh actions.
- English, Japanese, Simplified Chinese and Korean language entries.
- Buildability of the Unity VPM archive and Blender add-on ZIP.

Blender runtime regression checks run on Blender 3.6 and 4.2 in CI. Unity editor compilation and interactive editor checks are still required before publishing a release tag.

## Keywords

Optimize Your Project is indexed around: **Unity optimization, Blender add-on, one-click optimization, game optimization, asset optimization, texture optimization, mesh optimization, material optimization, duplicate materials, draw calls, LOD, game-ready assets, mobile optimization, VR, XR, VRChat, indie development and developer tools**.

## Community

[Website](https://fishhwb.github.io/) · [Discord](https://discord.gg/wZGxxkk4Jg) · [Patreon](https://www.patreon.com/cw/DedZed)

Optimize Your Project is free and licensed under MIT.
