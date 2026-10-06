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

For the fixed v0.7.60 release after the tag is published:

```text
https://github.com/dedzedofficial/Optimize-Your-Project.git#v0.7.60
```

### Blender

Blender v0.7.60 is built as both a Blender 4.2+ extension ZIP and a Blender 3.6 legacy add-on ZIP. The release workflow is available here:

[![DOWNLOAD BLENDER ZIP BUILDS](https://img.shields.io/badge/DOWNLOAD%20BLENDER-ZIP%20BUILDS-EA7600?style=for-the-badge&logo=blender&logoColor=white)](https://github.com/dedzedofficial/Optimize-Your-Project/actions/workflows/release-checks.yml)

Release history: [GitHub Releases](https://github.com/dedzedofficial/Optimize-Your-Project/releases)

Install the downloaded ZIP directly using **Install from Disk**. Do not extract it.

### VRChat / VCC (optional)

Use [Add Optimize Your Project to VCC](vcc://vpm/addRepo?url=https%3A%2F%2Fdedzedofficial.github.io%2FOptimize-Your-Project%2Findex.json), then add **Optimize Your Project** to the chosen project.

</details>

**Unity v0.7.60 | Blender v0.7.60 | General developer optimization tools | FISHHWB | Ded Zed**

Optimize Your Project is a free **general developer optimization** toolkit for Unity and Blender. It focuses on repetitive jobs that can be turned into a clear one-click action while keeping risky or art-direction-sensitive changes out of automatic workflows.

## v0.7.60 highlights

### Unity

The Unity editor window remains intentionally compact. Project and Character / Avatar are the only top-level pages, advanced settings stay collapsed, and detailed findings only appear when requested.

Current one-click actions include:

- **Optimize Textures**: resize/compress supported textures and repair recognized normal/data imports.
- **Optimize Model Imports**: apply model compression plus Unity vertex/polygon import optimization without changing triangle counts, rigs, animations or blendshapes.
- **Optimize Particles**: apply the configured particle limits to the loaded scene or selected character hierarchy.
- **Fix Material Costs**: remap exact duplicate material references and remove safe trailing empty material slots.
- **Optimize Lighting**: prepare supported loaded-scene geometry for baked lighting and start a bake.
- **Optimize UI Raycasts**: disable `Raycast Target` only on decorative UI graphics that are not inside a detected EventSystem interaction hierarchy. Interactive controls and custom pointer/select handlers are skipped, and Unity Undo is supported.
- **Clean Missing Scripts**: remove only missing MonoBehaviour entries from the selected scope, with Unity Undo support.

The Unity language selector supports **auto-detect** from the operating-system language, plus manual selection for English, Japanese, Simplified Chinese, Traditional Chinese, Korean, Spanish, French, German, Portuguese, Russian and Italian.

### Blender

Blender stays focused on the existing **Remesh** and **LOD** workflows instead of growing another large tool panel.

- **One-Click Remesh** creates a separate surface-preserving reduced copy while retaining supported UVs, materials, armature weights and relative blendshapes.
- **Create LOD0 / LOD1 / LOD2** still preserves the original and works on one or several selected supported static meshes.
- The existing LOD workflow now has an optional **Create Collision Proxy from LOD2** setting. When enabled, the same button creates a separate `_COLLIDER` mesh copied from LOD2, marks it as a wireframe/render-disabled collision proxy candidate, and keeps it in the same generated LOD set.
- The collision proxy is optional and off by default. Normal LOD generation still creates only LOD0, LOD1 and LOD2.
- Re-running an unchanged LOD job reuses the verified generated outputs instead of creating duplicates.

The Blender collision proxy is intentionally a candidate mesh. Import it into the target engine and configure the appropriate collider/physics component there; the add-on does not guess gameplay collision rules.

## Unity tools

Open **FISHHWB > Optimize Your Project**.

### Project

Project mode works with the selected Assets folder and loaded scenes. Reviews include Largest Textures, Read/Write Memory, Heavy Meshes and Scan Entire Project.

### Character / Avatar

Character mode limits supported one-click jobs to the selected hierarchy. It does not require a VR SDK and can be used for ordinary characters.

### Safety and recovery

Importer history, detail protection, optional memory trials and Restore Last Import Batch remain under Advanced settings. Scene changes such as particle edits, UI raycast changes, missing-script cleanup and supported lighting changes use native Unity Undo where applicable.

## Blender tools

Open the 3D Viewport sidebar with **N**, then choose the **FISHHWB** tab.

The Blender add-on intentionally avoids bringing back the previously removed generic cleanup, merge, atlas and Game-Ready panels. Remesh changes topology; LOD creates alternate meshes; the optional collision proxy extends the LOD result rather than introducing another competing geometry workflow.

## Languages

Unity supports Auto plus 11 manual interface languages. Blender currently supports English, Japanese, Simplified Chinese and Korean in its compact sidebar.

## Release checks

The repository validates package/version consistency, Unity editor source expectations, Blender packaging, and Blender runtime behavior. Blender runtime checks run against Blender 3.6 and 4.2 and cover Remesh, LOD, cache/history behavior, source preservation and the optional collision proxy path.

Workflow: https://github.com/dedzedofficial/Optimize-Your-Project/actions/workflows/release-checks.yml

## Free for developers

Optimize Your Project is free to use. Optional Patreon support helps fund testing, documentation and future one-click workflows, but the core project remains free.

## Repository layout

```text
package.json                         Unity package manifest
version.json                         Unity / Blender update feed
Editor/FISHHWBVR/                   Unity Editor implementation
Blender/vr_optimizer_blender/       Blender add-on
Blender/README.md                    Blender install and usage
Documentation/                      Architecture and Roadmap
scripts/                            Release/package checks
.github/workflows/                  Package and runtime validation
```

## Keywords

Unity optimization, Blender add-on, one-click optimization, game optimization, asset optimization, texture optimization, mesh optimization, material optimization, UI optimization, raycast optimization, missing-script cleanup, LOD, collision proxy, collider workflow, mobile optimization, VR, XR, VRChat, indie development and developer tools.

## Community

[Website](https://fishhwb.github.io/) | [Discord](https://discord.gg/wZGxxkk4Jg) | [Patreon](https://www.patreon.com/cw/DedZed)

Optimize Your Project remains free. The Unity/general repository code is MIT-licensed; the Blender extension package is distributed under **GPL-3.0-or-later** to meet Blender Extensions requirements.
