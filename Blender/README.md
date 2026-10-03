# Optimize Your Project for Blender: v0.7.55

<img src="../Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" alt="Optimize Your Project logo" width="112">

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

For the fixed v0.7.55 release:

```text
https://github.com/dedzedofficial/Optimize-Your-Project.git#v0.7.55
```

### Blender

The Blender build now produces two real ZIP packages:

- **Blender 4.2+ / Blender Extensions:** `optimize-your-project-blender-extension-0.7.55.zip`
- **Blender 3.6 legacy add-on:** `optimize-your-project-blender-0.7.55.zip`

[![DOWNLOAD BLENDER ZIP BUILDS](https://img.shields.io/badge/DOWNLOAD%20BLENDER-ZIP%20BUILDS-EA7600?style=for-the-badge&logo=blender&logoColor=white)](https://github.com/dedzedofficial/Optimize-Your-Project/actions/workflows/release-checks.yml)

Open the latest successful **Check release packages** run and download the `optimize-your-project-blender-0.7.55` artifact. It contains both ZIP files. Use the **extension** ZIP for `extensions.blender.org`. The official Blender Extensions listing will replace this temporary download button after publication.

The legacy ZIP also remains available from [GitHub Releases](https://github.com/dedzedofficial/Optimize-Your-Project/releases) when a matching Blender release is published.

### VRChat Creator Companion / VCC

Use [Add Optimize Your Project to VCC](vcc://vpm/addRepo?url=https%3A%2F%2Fdedzedofficial.github.io%2FOptimize-Your-Project%2Findex.json), then add **Optimize Your Project** to the chosen project.

</details>

> **New here?** Start with the [Overview](../README.md). You can read the complete documentation directly on GitHub before installing anything.


Blender v0.7.55 is intentionally focused on **Remesh and LOD generation only**. Earlier experimental cleanup, Game-Ready, merge, heavy-mesh, triangle-limit, join/atlas and related controls were removed because they were not reliable or useful enough to keep presenting as supported features. The compact sidebar still supports English, Japanese, Simplified Chinese and Korean.

## Install

### Blender 4.2+ / Blender Extensions package

The package intended for Blender 4.2+ and `extensions.blender.org` is:

```text
optimize-your-project-blender-extension-0.7.55.zip
```

Download the `optimize-your-project-blender-0.7.55` artifact from the latest successful [Check release packages](https://github.com/dedzedofficial/Optimize-Your-Project/actions/workflows/release-checks.yml) run. The artifact contains the extension ZIP above plus the Blender 3.6 legacy ZIP.

For a local install in Blender 4.2+, use **Edit > Preferences > Get Extensions > Install from Disk** and choose the extension ZIP.

### Blender 3.6 legacy package

Use:

```text
optimize-your-project-blender-0.7.55.zip
```

Then use **Edit > Preferences > Add-ons > Install...**, enable **Optimize Your Project for Blender**, press **N** in the 3D Viewport and open the **FISHHWB** tab.

### Official Blender Extensions listing

The final GitHub install button will point directly to the official Blender Extensions listing after it is published. The extension ZIP above is the submission package for that listing.

The Blender extension package is licensed under **GPL-3.0-or-later**, as required for add-ons submitted to Blender Extensions. The repository's non-Blender portions retain their existing licensing.

## Supported Blender tools in v0.7.55

Select a supported static mesh in Object Mode.

### One-Click Remesh

Press **One-Click Remesh** to create a separate `_Remesh` copy. The source object is preserved.

The tool automatically selects a remesh detail level from the mesh dimensions. Shape-key, vertex-group and armature-driven meshes are skipped because remeshing changes topology.

### LOD Generation

Press **Create LOD0 / LOD1 / LOD2** to create a separate LOD collection for the active mesh:

- **LOD0** preserves the evaluated source triangle count.
- **LOD1** targets up to 66% of the LOD0 triangle count.
- **LOD2** targets up to 33% of the LOD0 triangle count.

The original source object remains untouched.

Enable **Apply Existing Modifiers** if supported non-armature modifiers should be baked into LOD0 before LOD1 and LOD2 are generated. When multiple supported meshes are selected, **Create LODs for Selection** creates a LOD set for each selection.

### Removed experimental tools

The following Blender tools are not part of the supported v0.7.55 UI anymore: mesh cleanup, Game-Ready copy, duplicate-vertex merge, heavy-mesh finder, triangle-limit copy, mesh joining and texture atlas tools.

They were removed from this version because they did not provide a reliable enough result or enough practical benefit to justify the extra UI.


## Interface languages

Use the **Language** control at the top of the sidebar. v0.7.55 includes English, Japanese, Simplified Chinese and Korean for the main Blender workflow. Future language additions are tracked in the project roadmap.

## Notes

Blender v0.7.55 is early support. Test generated meshes before replacing production assets, especially before GLB/FBX export into Unity or another engine.

## v0.7.55 compact workflow

Set the **Triangle target** slider and press **One-Click Remesh** to create a remeshed copy within that maximum triangle budget. A failed reduction removes its output and preserves the source.

The single LOD button automatically uses the batch operator when multiple mesh objects are selected. LOD0 remains full detail; LOD1 and LOD2 use 66% and 33% of its triangles. The remesh target does not silently change LOD0.

Blender runtime verification of the new target is pending; the CI regression suite covers budget enforcement and source preservation.
