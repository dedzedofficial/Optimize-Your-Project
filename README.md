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
  <strong>Unity interface languages:</strong> Auto | English | 日本語 | 简体中文 | 繁體中文 | 한국어 | Español | Français | Deutsch | Português | Русский | Italiano
</p>

<details open>
<summary><strong>Install / Download Optimize Your Project</strong></summary>

### Unity

Open **Window > Package Manager**, press **+**, choose **Add package from git URL**, then paste:

```text
https://github.com/dedzedofficial/Optimize-Your-Project.git
```

After the v0.7.60 tag is published:

```text
https://github.com/dedzedofficial/Optimize-Your-Project.git#v0.7.60
```

### Blender

Download the installable v0.7.55 package directly:

- [**Blender 4.2+ extension ZIP**](https://github.com/dedzedofficial/Optimize-Your-Project/raw/refs/heads/main/Blender/Downloads/optimize-your-project-blender-extension-0.7.55.zip)
- [**Blender 3.6 legacy add-on ZIP**](https://github.com/dedzedofficial/Optimize-Your-Project/raw/refs/heads/main/Blender/Downloads/optimize-your-project-blender-0.7.55.zip)

[![DOWNLOAD BLENDER ZIP BUILDS](https://img.shields.io/badge/DOWNLOAD%20BLENDER-ZIP%20BUILDS-EA7600?style=for-the-badge&logo=blender&logoColor=white)](https://github.com/dedzedofficial/Optimize-Your-Project/actions/workflows/release-checks.yml)

Release history: [GitHub Releases](https://github.com/dedzedofficial/Optimize-Your-Project/releases)

Install the downloaded ZIP directly using **Install from Disk**. Do not extract it. These packages include surface/UV preservation and the latest blendshape correspondence fix. Restart Blender after replacing an older installation of the same version.

### VRChat Creator Companion / VCC

Use [Add Optimize Your Project to VCC](vcc://vpm/addRepo?url=https%3A%2F%2Fdedzedofficial.github.io%2FOptimize-Your-Project%2Findex.json), then add **Optimize Your Project** to the chosen project.

</details>

> **New here?** Start with the [Overview](README.md). You can read the complete documentation directly on GitHub before installing anything.


**Unity v0.7.60 · Blender v0.7.55 · General developer optimization tools · FISHHWB | Ded Zed**

Optimize Your Project is a free toolkit for developers building real-time projects. Its priority is removing repetitive optimization work through clear one-click and batch actions for games, mobile projects, VR titles, social experiences, prototypes and reusable asset packs.

Unity v0.7.60 focuses on a much smaller interface, automatic language detection, broader localization and one more safe one-click maintenance action. Blender remains on v0.7.55 and keeps its intentionally focused Remesh + LOD workflow.

## v0.7.60 Unity update

- Rebuilt the Unity window into a compact action dashboard instead of a long wall of cards.
- Removed the old action search box because the primary actions now fit directly in the window.
- Kept **Project** and **Character / Avatar** as the two top-level pages.
- Grouped the main work into six one-click actions with advanced options collapsed by default.
- Moved project reviews into one compact Review area and kept detailed findings hidden until requested.
- Replaced the large support/version cards with a slim footer containing version status, update access and support links.
- Added **Clean Missing Scripts**. It removes only missing MonoBehaviour entries from loaded scene objects or the selected character hierarchy and records Unity Undo before each affected object is changed.
- Added **Auto** language mode. Unity now detects the operating-system language on first use unless the user already has a saved manual language choice.
- Expanded the Unity language selector to English, Japanese, Simplified Chinese, Traditional Chinese, Korean, Spanish, French, German, Portuguese, Russian and Italian.
- Manual language selection remains available at all times from the top toolbar.
- Existing 0.7.55 importer history, detail protection, restore and memory-trial behavior remains available under the collapsed advanced settings.

## v0.7.55 cleanup

- **Optimize Lighting** is the Project lighting action: set loaded scene lights to Baked, prepare eligible meshes for static lighting, enable baked GI and start Unity's bake.
- Save loaded scenes first. Known animated/physics-driven meshes are skipped; custom script movement needs review. Baked lights do not directly light moving objects; suitable probes remain the scene author's responsibility.
- Only lighting/batching static flags are set. Existing quality settings are retained. Check lightmap UVs and the Lighting window for bake completion or errors.
- Setup Undo restores light/mesh settings; it does not restore generated lightmap files.
- Material fixes use one combined action. Texture size controls and Project Insights are collapsed.
- Blender has a **Triangle target** slider for the remeshed copy and one LOD button that handles one or several selected meshes. LOD0 preserves the source detail; LOD1/LOD2 use the existing ratios.
- This code update passes static package checks; Unity and Blender editor runtime verification is still pending.

## Quick install

| Platform | Fastest install |
| --- | --- |
| **Unity** | Package Manager → **+** → **Add package from git URL** → paste `https://github.com/dedzedofficial/Optimize-Your-Project.git` |
| **Blender 4.2+** | Download `optimize-your-project-blender-extension-0.7.55.zip` from the latest successful release-check artifact; this is the Blender Extensions submission ZIP |
| **VRChat / VCC (optional)** | [Add the VPM repository](vcc://vpm/addRepo?url=https%3A%2F%2Fdedzedofficial.github.io%2FOptimize-Your-Project%2Findex.json), then add **Optimize Your Project** to the chosen project |

For a fixed Unity release after the v0.7.60 tag is published:

```text
https://github.com/dedzedofficial/Optimize-Your-Project.git#v0.7.60
```

## Languages

The Unity editor window supports:

- Auto-detect from the operating-system language
- English
- Japanese
- Simplified Chinese
- Traditional Chinese
- Korean
- Spanish
- French
- German
- Portuguese
- Russian
- Italian

The selector stays visible in the compact top toolbar. Auto mode is the default for new users. Existing English, Japanese, Simplified Chinese and Korean choices from the older preference are migrated when possible. If a less common label has not yet been translated, the Unity UI falls back to English instead of showing a broken key.

Blender v0.7.55 continues to expose English, Japanese, Simplified Chinese and Korean in its sidebar.

## Unity tools

Open **FISHHWB → Optimize Your Project**.

The Unity window keeps the two focused work pages:

- **PROJECT** for ordinary project assets and loaded scenes.
- **CHARACTER / AVATAR** for one selected character hierarchy without requiring a VR SDK.

### Minimal navigation

- The Project / Character switch is always visible in the top toolbar.
- The language selector sits beside it and can stay on **Auto** or be manually overridden.
- **Use Selection** can set the Project asset scope from the selected Project window asset or folder.
- Primary optimization buttons are always visible.
- Texture, particle and model settings live under one collapsed **Advanced settings** foldout.
- Detailed findings stay hidden until a Review or full Scan action is requested.

### Project optimization buttons

- **Optimize Textures** applies size/compression and recognized normal/data import repairs in one batch, preserving stricter existing limits and explicit formats.
- **Optimize Model Imports** applies compression and vertex/polygon import optimization to scoped model assets without reducing triangle counts or changing Read/Write, rigs, animations or blendshapes.
- **Optimize Particles** applies selected particle limits to loaded scenes or the chosen character hierarchy.
- **Fix Material Costs** remaps loaded renderers from exact duplicate material assets to one canonical exact match and removes only safe trailing empty material slots. Unity Undo is supported.
- **Optimize Lighting** prepares and starts baked scene lighting. Character / Avatar retains its scoped realtime-shadow action.
- **Clean Missing Scripts** removes only missing script component entries in the current loaded-scene or selected-character scope and supports Undo.
- **Scan Entire Project** runs the heavier diagnostic pass and shows filterable Critical / Warning results.

### Project Insights

These buttons help find expensive assets without changing project files:

- **Largest Textures** lists the largest source textures in the chosen Assets folder.
- **Read/Write Memory** lists textures and imported models with CPU-readable copies enabled.
- **Heavy Meshes** lists high-cost mesh candidates without automatically changing topology.

Read/Write review is intentionally diagnostic-only. CPU-readable copies can consume additional memory, but disabling them automatically can break scripts, runtime mesh access and other workflows that require readable data. Unity documents the extra CPU memory cost for readable texture and mesh data.

### Compact update footer

The footer shows the installed version and update state:

- **Green:** current.
- **Orange:** one patch release behind.
- **Red:** two or more patch releases behind, or a newer minor/major release exists.
- **Grey:** update status has not been checked or could not be resolved.

Git-installed packages can use the footer update button directly. Embedded or VCC installs show the correct update route.

## Blender v0.7.55

The Blender add-on is under `Blender/vr_optimizer_blender/`.

After installation, open the 3D Viewport sidebar with **N**, then open the **FISHHWB** tab.

**Blender v0.7.55 intentionally supports only Remesh and LOD generation.** The earlier cleanup, Game-Ready, duplicate-vertex, heavy-mesh, triangle-limit, join/atlas and related experimental Blender tools were removed because they were not reliable or useful enough to keep presenting as supported optimization features.

The simplified Blender UI now contains only:

- **One-Click Remesh**: creates a separate automatically remeshed copy of the active supported mesh, transferring supported armature weights and relative shape keys.
- **Create LOD0 / LOD1 / LOD2**: creates three LOD copies for the active supported static mesh while preserving the original.
- The same LOD button processes selected meshes when several are selected, using the existing batch operator.
- **Apply Existing Modifiers**: the only LOD option retained, allowing supported modifiers to be baked into LOD0 before lower LODs are generated.

Remesh and LOD preserve the original. Remesh transfers vertex weights, relative shape keys and armature bindings on supported inputs. LOD remains static-mesh only.


## Action results

Unity batches and Blender quick actions report **Changed**, **Unchanged**, **Skipped**, **Unsupported** and **Failed**.

Unity importer jobs work on unique assets. Blender copy-based jobs keep the source mesh untouched. Cancelled or unsupported items are reported instead of being silently changed.

## Future development

The [version-by-version development roadmap](Documentation/Roadmap.md) tracks the path toward v1.0.

The revised direction prioritizes distinct, useful one-click workflows and consolidates overlapping controls before expanding.

Planned work includes:

- one primary route for material fixes, model imports and selection-aware Blender LOD generation,
- recoverable batches and shared processing,
- UI rendering, animation data, shader build-size and asset-loading improvements,
- collider proxies and verified instancing support,
- one selection-based optimization pass using the existing task implementations,
- measured results and removal of redundant or unproven tools.

Additional engines will be evaluated after the Unity and Blender workflows are reliable, and only where they add meaningful automation beyond native tools. More remesh, LOD and image-compression variants are deferred.

The v1.0 goal remains **90% of the published, safely automatable task inventory** for each declared stable integration and target. Reports, helper buttons and duplicate routes do not count toward that coverage.

Roadmap items are future plans. Only implemented and tested behavior counts as current support.

## Free for developers

**Optimize Your Project is free to use.** It is built to reduce repetitive optimization work, make development easier and give newer creators useful tools without putting the basics behind a paywall.

If the project saves you time and you want to help it grow, you can support development on [Patreon](https://www.patreon.com/cw/DedZed). Optional support helps fund testing, documentation, new one-click tools and future integrations.

**Supporting is always optional. The project stays free either way.**

## Safety

Optimization changes can affect appearance or runtime behavior. Use source control or a backup before large batches and inspect the result in the target platform.

Unity importer jobs change import metadata rather than source image files. Scene particle, missing-script and light changes support Undo where applicable. Read/Write review does not automatically disable CPU access.

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
- Unity compact Project / Character UI shape.
- Unity Auto language detection and expanded interface language integration.
- Unity missing-script cleaner and meta coverage.
- Unity Project Insights integration.
- Blender Remesh, active LOD generation, batch LOD generation, source preservation and unsupported-topology guards.
- Buildability of the Unity VPM archive and Blender add-on ZIP.

Blender runtime regression checks run on Blender 3.6 and 4.2 in CI. Unity editor compilation and interactive editor checks are still required before publishing a release tag.

## Keywords

Optimize Your Project is indexed around: **Unity optimization, Blender add-on, one-click optimization, game optimization, asset optimization, texture optimization, mesh optimization, material optimization, duplicate materials, draw calls, LOD, game-ready assets, mobile optimization, VR, XR, VRChat, indie development and developer tools**.

## Community

[Website](https://fishhwb.github.io/) · [Discord](https://discord.gg/wZGxxkk4Jg) · [Patreon](https://www.patreon.com/cw/DedZed)

Optimize Your Project remains free. The Unity/general repository code is MIT-licensed; the Blender extension package is distributed under **GPL-3.0-or-later** to meet Blender Extensions requirements.

### Owning-button rule for v0.7.55

Related operations belong to their existing action. Optimize Textures includes recognized texture import repair alongside size/compression. Optimize Model Imports includes vertex/polygon import optimization alongside compression. Material fixes use the combined action. Reviews remain diagnostic and do not introduce competing fix buttons. Model topology is preserved; Blender handles actual remesh and LOD generation.


## v0.7.55 additions: smarter owning buttons

These additions stay in v0.7.55 and extend existing actions rather than introducing another optimization dashboard.

| Capability | Supported scope | Behavior |
| --- | --- | --- |
| Finish Lighting Setup | Unity loaded saved scenes and supported imported static models | Generate secondary UVs only where the mesh lacks UV1, then prepare static lighting and request a bake. Existing UVs are not repacked. Unsupported/protected or manually edited imports are skipped. |
| Optimize New Changes | Unity texture/model/lighting-UV import jobs | Persistent per-project source/settings history skips accepted unchanged work and preserves later manual importer edits. |
| Optimize New Changes | Blender Remesh/LOD | Reuse verified generated copies when source geometry/settings are unchanged; replace only untouched owned outputs after a successful source update. Preserve edited/protected outputs. |
| Protect Important Detail | Unity texture/model assets and Blender source objects | Explicit protection opts assets out of importer/UV changes or topology-changing jobs. No automatic guessing about faces, signs or hero objects. |
| Test and Keep Improvements | Optional Unity texture/model import trial | Compare sampled native texture/mesh asset memory before/after. Restore a changed trial when no saving is measured or measurement is unavailable. |
| Restore Last Import Batch | Unity recorded importer batches | Restore metadata only if the source and current importer state still match the recorded output. Preserve later edits and report conflicts. |

### Using the compact controls

Unity: expand **Advanced settings** and open **Batch options**. Select texture/model assets, a material, or a scene hierarchy to protect its referenced textures/models. Removing protection does not remove manual-edit protection; **Reset history for selection** explicitly makes current import settings the next baseline. **Restore last import batch** restores the most recent batch that actually changed imports, including lighting UV preparation.

Blender: **Protect detail** is beside the selected object. Repeated actions on the original source reuse outputs. Reset history on the original source only when you deliberately want fresh copies while preserving previous outputs. Changed sources replace verified untouched generated sets after successful generation. History is stored as object metadata; geometry remains preserved. Renaming/duplicating a source may create a fresh set rather than taking ownership of another source's copies.

### Limits and verification

- The memory trial is an editor asset-memory experiment, not an FPS benchmark or an appearance check. It does not prove a visual change is acceptable. Model compression may help disk/build size without reducing sampled native memory; the trial can therefore reject it even when normal optimization is useful.
- Play-mode frame-time, player-build and rendered-image comparisons remain future work. Do not advertise automatic whole-project performance certification in v0.7.55.
- Unity importer history lives in ProjectSettings/OptimizeYourProjectHistory.asset. Keep it with project backups; missing history means a new baseline. Import source files are preserved. Source changes or unrecognized metadata changes can require review.
- Scene lights/flags use native Undo; generated bake files are outside importer restore. Existing scene settings and known dynamic geometry still require the restrictions documented above.
- UV readiness checks channel presence, not full chart overlap/distortion quality. Generated UVs use Unity's importer defaults. Custom/procedural geometry and unsupported importers are reported, not silently rebuilt.
- Unity Edit Mode regression tests for caching, manual edits, protection, rollback, restoration and memory-trial rejection are in Editor/Tests. Enable package tests with Unity Test Framework to run them. Unity editor compilation and bake validation are still required before tagging.
- Blender runtime regression checks include unchanged reuse, output rename, source updates, manual-edit preservation and detail protection on supported CI versions.
