# Optimize Your Project

<img src="Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" alt="Optimize Your Project logo" width="150">

**v0.7.0 · Unity + early Blender tools · FISHHWB | Ded Zed**

Optimize Your Project turns repetitive optimization work into clear, focused buttons. v0.7 keeps Unity simple, adds early Blender mesh cleanup, and removes UI pages that duplicated the same jobs.

## Quick install

| Platform | Fastest install |
| --- | --- |
| **Unity** | Package Manager → **+** → **Add package from git URL** → paste `https://github.com/dedzedofficial/Optimize-Your-Project.git` |
| **VRChat Creator Companion** | [Add the VPM repository](vcc://vpm/addRepo?url=https%3A%2F%2Fdedzedofficial.github.io%2FOptimize-Your-Project%2Findex.json), then add **Optimize Your Project** to the project |
| **Blender** | Download `optimize-your-project-blender-0.7.0.zip` from Releases → Blender Preferences / Get Extensions → **Install from Disk** |

For a fixed Unity release after the v0.7.0 tag is published, use:

```text
https://github.com/dedzedofficial/Optimize-Your-Project.git#v0.7.0
```

## Unity v0.7

Open **FISHHWB → Optimize Your Project**.

The Unity window now has only two work pages:

- **PROJECT** — replaces the old World + Project split. Texture work uses the chosen Assets folder; particle, imported-mesh and realtime-light jobs operate on loaded scenes.
- **AVATAR** — runs the same focused jobs against one selected avatar hierarchy.

Each job is a direct action. Detailed findings stay hidden unless you explicitly press **Scan Entire Project**.

### Project buttons

- **Compress & Size Textures** — applies platform size caps and automatic compression to supported textures while preserving explicit formats and stricter existing limits.
- **Optimize Particles** — applies the selected particle limits/settings to loaded scenes or the selected avatar.
- **Compress Imported Meshes** — changes Unity model-importer mesh compression for model assets used in the current scope.
- **Disable Realtime Shadows** — disables realtime light shadows in the current scope with Unity Undo support.
- **Scan Entire Project** — runs the heavier diagnostic pass and shows filterable Critical / Warning results.

### Small update footer

Updates no longer take a full page. The bottom footer shows the installed version and a status dot:

- **Green** — current.
- **Orange** — an update is available and the install is one patch release behind.
- **Red** — two or more patch releases behind, or a newer minor/major release exists. Example: **0.6.3 → 0.6.5** is red.
- **Grey** — update status has not been checked or could not be resolved.

Git-installed Unity packages can use the footer update button directly. Embedded/VCC installs show the correct update route instead.

## Blender v0.7

The Blender add-on is under `Blender/vr_optimizer_blender/`.

After installation, open the 3D Viewport sidebar (**N**) → **FISHHWB**.

The first section is **ONE-CLICK CLEANUP**:

- **One-Click Remesh** — makes a new static-mesh copy and remeshes it with an automatically selected detail size.
- **Merge Duplicate Vertices** — makes a new copy and merges nearby duplicate vertices using **Merge Distance**.

The original mesh is kept untouched. Rigged meshes, shape-key meshes, or cases where topology changes are unsafe are rejected rather than silently damaged.

Existing triangle-limit, join/atlas, and static LOD tools remain under **Advanced Mesh Tools**.

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
- Presence of the one-click Blender remesh and vertex-merge operators.
- Buildability of both the Unity VPM archive and Blender add-on ZIP.

Editor runtime testing is still required before publishing a release tag.

## Community

[Website](https://fishhwb.github.io/) · [Discord](https://discord.gg/wZGxxkk4Jg) · [Patreon](https://www.patreon.com/cw/DedZed)

Optimize Your Project is free and licensed under MIT.
