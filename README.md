# Optimize Your Project

<img src="Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" alt="Optimize Your Project logo" width="150">

**v0.7.1 · General developer optimization tools · Unity + Blender · FISHHWB | Ded Zed**

Optimize Your Project is for developers building **any kind of real-time project**. Its priority is removing repetitive optimization work through clear one-click actions, whether you are making a PC game, mobile project, VR title, social experience, prototype, or reusable asset pack. Unity is the first full integration and Blender is the first external creation-tool integration.

## Quick install

| Platform | Fastest install |
| --- | --- |
| **Unity** | Package Manager → **+** → **Add package from git URL** → paste `https://github.com/dedzedofficial/Optimize-Your-Project.git` |
| **Blender** | Download `optimize-your-project-blender-0.7.1.zip` from Releases → Blender Preferences / Get Extensions → **Install from Disk** |
| **VRChat / VCC (optional)** | [Add the VPM repository](vcc://vpm/addRepo?url=https%3A%2F%2Fdedzedofficial.github.io%2FOptimize-Your-Project%2Findex.json), then add **Optimize Your Project** to the chosen project |

For a fixed Unity release after the v0.7.1 tag is published, use:

```text
https://github.com/dedzedofficial/Optimize-Your-Project.git#v0.7.1
```

## Unity v0.7.1

Open **FISHHWB → Optimize Your Project**.

The Unity window now has only two work pages. Neither page requires a VR SDK:

- **PROJECT**: replaces the old World + Project split. Texture work uses the chosen Assets folder; particle, imported-mesh and realtime-light jobs operate on loaded scenes.
- **CHARACTER / AVATAR**: runs the same focused jobs against one selected character/avatar hierarchy. This can be used for ordinary game characters as well as social-VR avatars.

Each job is a direct action. Detailed findings stay hidden unless you explicitly press **Scan Entire Project**. v0.7 also uses a cleaner card-based interface with clearer action hierarchy, larger primary buttons, compact version status, and a small optional support panel.

### Project buttons

- **Compress & Size Textures**: applies platform size caps and automatic compression to supported textures while preserving explicit formats and stricter existing limits.
- **Optimize Particles**: applies the selected particle limits/settings to loaded scenes or the selected avatar.
- **Compress Imported Meshes**: changes Unity model-importer mesh compression for model assets used in the current scope.
- **Disable Realtime Shadows**: disables realtime light shadows in the current scope with Unity Undo support.
- **Scan Entire Project**: runs the heavier diagnostic pass and shows filterable Critical / Warning results.

### Small update footer

Updates no longer take a full page. The bottom footer shows the installed version and a status dot:

- **Green**: current.
- **Orange**: an update is available and the install is one patch release behind.
- **Red**: two or more patch releases behind, or a newer minor/major release exists. Example: **0.6.3 → 0.6.5** is red.
- **Grey**: update status has not been checked or could not be resolved.

Git-installed Unity packages can use the footer update button directly. Embedded/VCC installs show the correct update route instead.

## Blender v0.7.1

Blender support is also project-general: these tools are intended for game assets, environment props, characters without topology-sensitive rigs, prototypes, VR content, and other real-time workflows.

The Blender add-on is under `Blender/vr_optimizer_blender/`.

After installation, open the 3D Viewport sidebar (**N**) → **FISHHWB**.

The Blender sidebar mirrors the same cleaner product layout: selection summary, **ONE-CLICK CLEANUP**, collapsible advanced tools, and the optional free/support note. The first action section is **ONE-CLICK CLEANUP**:

- **Clean Selected Mesh**: makes a `_Clean` copy, removes loose geometry and exact duplicate vertices, removes zero-area faces and unused material slots, and fixes closed-surface normals.
- **One-Click Remesh**: makes a new static-mesh copy and remeshes it with an automatically selected detail size.
- **Merge Duplicate Vertices**: makes a new copy and merges nearby duplicate vertices using **Merge Distance**.

The original mesh is kept untouched. Clean Selected Mesh supports static local meshes without shape keys, vertex groups, modifiers or custom split normals. Open surface faces and their winding are preserved. Remesh also rejects rigged and shape-key meshes; Merge Duplicate Vertices rejects shape keys.

Existing triangle-limit, join/atlas, and static LOD tools remain under **Advanced Mesh Tools**.

### Action results

Unity batches and Blender quick actions report **Changed**, **Unchanged**, **Skipped**, **Unsupported**, and **Failed**. Counts refer to candidates in the chosen scope. Unity texture/model counts refer to unique assets; Blender quick actions process the active mesh only. Cancelled Unity batches show partial results and count unprocessed candidates as skipped. Blender keeps its latest report in the sidebar.

## Future development

- Follow the [version-by-version development roadmap](Documentation/Roadmap.md) for planned one-click tools and platform integrations.
- The v1.0 goal is at least **90% of identified, safely automatable optimization tasks** in each supported integration and target, with progress measured against a public task inventory.
- Planned work covers Unity, Blender, Godot and Unreal, plus target-specific preparation and simple **find, explain, fix and restore** helper buttons.
- Roadmap entries are future plans. Only implemented and tested capabilities count toward coverage.

## Free for developers

**Optimize Your Project is free to use.** The goal is to make development easier, remove repetitive optimization work, and give newer creators useful tools without putting the basics behind a paywall.

If the project saves you time and you would like to help it keep growing, you can support development on [Patreon](https://www.patreon.com/cw/DedZed). Optional support helps fund testing, documentation, new one-click optimization tools, maintenance, and future integrations with more engines and creator workflows.

**Supporting is always optional. The project stays free either way.**

## Safety

Optimization changes can affect appearance. Use source control or a backup before large batches and inspect the result in the target platform.

Unity importer jobs change import metadata rather than source image files. Scene particle/light changes support Undo where applicable. Blender quick cleanup creates copies rather than replacing the source mesh.

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

Pull requests run static package checks that validate:

- Unity package/version feed consistency.
- Blender add-on version consistency and Python syntax.
- Required branding/package files.
- v0.7 Project/Avatar UI shape.
- Presence of the Blender cleanup, remesh and vertex-merge operators.
- Buildability of both the Unity VPM archive and Blender add-on ZIP.

Blender runtime regression checks run on Blender 3.6 and 4.2 in CI. They cover source preservation, cleanup idempotence, UV/material retention, safe refusal, failure rollback, remesh and vertex merging. Run locally with `blender --background --factory-startup --python-exit-code 1 --python scripts/test_blender.py`.

Unity editor compilation and interactive editor checks are still required before publishing a release tag.

## Community

[Website](https://fishhwb.github.io/) · [Discord](https://discord.gg/wZGxxkk4Jg) · [Patreon](https://www.patreon.com/cw/DedZed)

Optimize Your Project is free and licensed under MIT.
