# Optimize Your Project for Blender: v0.7.60

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

### Blender

Blender v0.7.60 is produced as both a Blender 4.2+ extension ZIP and Blender 3.6 legacy add-on ZIP by the release checks workflow:

[![DOWNLOAD BLENDER ZIP BUILDS](https://img.shields.io/badge/DOWNLOAD%20BLENDER-ZIP%20BUILDS-EA7600?style=for-the-badge&logo=blender&logoColor=white)](https://github.com/dedzedofficial/Optimize-Your-Project/actions/workflows/release-checks.yml)

Install the downloaded ZIP directly using **Install from Disk**. Do not extract it.

### VRChat Creator Companion / VCC

Use [Add Optimize Your Project to VCC](vcc://vpm/addRepo?url=https%3A%2F%2Fdedzedofficial.github.io%2FOptimize-Your-Project%2Findex.json), then add **Optimize Your Project** to the chosen project.

</details>

Blender v0.7.60 keeps the compact **Remesh + LOD** design and extends the existing LOD button with an optional collision proxy output. It does not restore the older experimental cleanup, Game-Ready, merge, atlas or heavy-mesh panels.

## Install

### Blender 4.2+

Download `optimize-your-project-blender-extension-0.7.60.zip` from the latest successful [Check release packages](https://github.com/dedzedofficial/Optimize-Your-Project/actions/workflows/release-checks.yml) artifact, then use **Edit > Preferences > Get Extensions > Install from Disk**.

### Blender 3.6

Download `optimize-your-project-blender-0.7.60.zip` from the same workflow artifact, then use **Edit > Preferences > Add-ons > Install...**.

After enabling the add-on, press **N** in the 3D Viewport and open the **FISHHWB** tab.

## One-Click Remesh

Select a supported mesh in Object Mode, choose the triangle target and press **One-Click Remesh**.

The action creates a separate `_Remesh` copy and preserves the source. Surface reduction retains supported UV layers and material assignments. Supported armature bindings, vertex weights and relative blendshapes are carried through the reduced topology. Unsupported deformation cases are rejected rather than silently damaged.

## LOD Generation

Press **Create LOD0 / LOD1 / LOD2** for one selected static mesh, or select several supported meshes and use the same visible LOD action to process the selection.

- **LOD0** preserves the evaluated source detail.
- **LOD1** targets up to 66% of LOD0 triangles.
- **LOD2** targets up to 33% of LOD0 triangles.
- **Apply Existing Modifiers** optionally bakes supported existing modifiers into LOD0 before lower levels are generated.

The original source is preserved.

## Optional collision proxy

Enable **Create Collision Proxy from LOD2** inside the existing LOD section before running the LOD action.

When enabled, the same action creates a separate `<Source>_COLLIDER` object copied from LOD2. The proxy:

- has its own mesh data,
- uses the LOD2 geometry instead of reducing the source again,
- is marked as wireframe in Blender,
- is disabled for rendering,
- is stored with the generated LOD set,
- participates in the existing generated-output history and reuse checks,
- never replaces or modifies the original source mesh.

This is a collision proxy candidate, not an engine-specific collider component. Configure the actual collider or physics component after importing the mesh into Unity or another target engine.

With the option disabled, the LOD workflow behaves as before and creates only LOD0, LOD1 and LOD2.

## History and protection

Repeated Remesh and LOD actions reuse verified unchanged outputs. If a generated result has been manually edited or protected, the add-on preserves it instead of silently overwriting it. Use **Reset history** on the original source only when you deliberately want a fresh generated set.

## Interface languages

The Blender sidebar currently supports English, Japanese, Simplified Chinese and Korean. The new collision proxy option is translated in all four supported Blender languages.

## Verification

Blender runtime regression checks run on Blender 3.6 and 4.2 and cover Remesh, LOD, source preservation, generated-output reuse, manual-edit protection and the optional collision proxy path.

Workflow: https://github.com/dedzedofficial/Optimize-Your-Project/actions/workflows/release-checks.yml

The Blender extension package uses **GPL-3.0-or-later**. The repository's non-Blender portions retain their existing licensing.
