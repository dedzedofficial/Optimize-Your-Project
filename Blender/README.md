# Optimize Your Project for Blender 4.2+

<img src="../Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" alt="Optimize Your Project logo" width="112">

<p align="center">
  <a href="../README.md"><strong>Overview</strong></a> |
  <a href="../Blender/README.md"><strong>Blender Guide</strong></a> |
  <a href="../Documentation/Roadmap.md"><strong>Roadmap</strong></a> |
  <a href="../Documentation/Architecture.md"><strong>Architecture</strong></a> |
  <a href="../CHANGELOG.md"><strong>Changelog</strong></a>
</p>

**Current Blender release: v0.7.66**

The Blender integration targets **Blender 4.2 and newer** through the Blender Extensions system. The supported download is one modern extension ZIP.

## Install / Download Optimize Your Project

Open the latest successful **Check release packages** workflow:

https://github.com/dedzedofficial/Optimize-Your-Project/actions/workflows/release-checks.yml

Download the `optimize-your-project-blender-0.7.66` artifact and install:

```text
optimize-your-project-blender-extension-0.7.66.zip
```

Use **Edit > Preferences > Get Extensions > Install from Disk**. Do not extract the ZIP.

After enabling the extension, press **N** in the 3D Viewport and open the **FISHHWB** tab.

## v0.7.66 interface

The Blender sidebar now uses one readable **Primary Actions** panel rather than splitting Remesh/LOD and modern static-mesh tools into separate stacked sections.

The panel includes:

- current selection and triangle/vertex summary,
- Protect detail and Reset history controls,
- One-Click Remesh,
- LOD0 / LOD1 / LOD2 generation,
- optional collision proxy generation,
- Generate Lightmap UV,
- Link Identical Mesh Data,
- Strip Collider Render Data,
- wrapped last-result text.

Long descriptions are width-aware and wrap to the sidebar instead of being cut off. Primary actions use taller rows to make the panel easier to read at normal Blender UI scaling.

## One-Click Remesh

Select a supported mesh and choose a triangle target.

**One-Click Remesh** creates a separate reduced copy while preserving the source. Supported UV layers and material assignments are retained. Supported relative shape keys, armature bindings and vertex weights are transferred through the surface-preserving reduction path.

Unsupported deformation cases are rejected instead of silently damaging output.

Blender 5.x animation transfer uses the modern slotted Action/channelbag API. Blender 4.2 uses the compatible legacy action access path.

## LOD Generation

**Create LOD0 / LOD1 / LOD2** creates a separate LOD collection for supported static meshes:

- **LOD0** keeps evaluated source detail.
- **LOD1** targets up to 66% of LOD0 triangles.
- **LOD2** targets up to 33% of LOD0 triangles.
- **Apply Existing Modifiers** can bake supported modifiers into LOD0 before lower levels are generated.

Select several supported meshes to batch the same workflow.

### Optional collision proxy

Enable **Create Collision Proxy from LOD2** to add a separate `<Source>_COLLIDER` object copied from LOD2.

The collider candidate has its own mesh data, is shown as wireframe, is disabled for rendering and is tracked with generated LOD history. It does not modify or replace the source mesh.

## Generate Lightmap UV

**Generate Lightmap UV** creates a `LightmapUV` channel for selected supported static meshes.

Safety rules:

- an existing primary UV map is required,
- `LightmapUV` is only created when it can become the second UV channel,
- geometry is unchanged,
- the primary UV map is unchanged,
- existing secondary UV maps are preserved instead of replaced,
- armature and shape-key meshes are skipped,
- Blender Undo is available.

The current generator uses a deterministic per-face atlas and prioritizes safety and non-overlap over maximum packing density.

## Link Identical Mesh Data

**Link Identical Mesh Data** scans selected meshes for exact static duplicates and links matching objects to one shared mesh datablock.

The match includes geometry, topology, UV data, mesh attributes and material assignments. The action skips meshes with modifiers, shape keys, linked-library data and object-level material overrides.

Object transforms stay independent.

## Strip Collider Render Data

**Strip Collider Render Data** only works on generated collision proxies carrying the optimizer's collision-proxy marker.

It removes materials, UV layers and color attributes while preserving geometry.

## History and protection

Remesh and LOD generated outputs are fingerprinted. Unchanged repeated actions can reuse existing outputs. Manual edits and protected generated objects are preserved rather than silently replaced.

Use **Protect detail** on important source objects. Use **Reset history** only when you deliberately want a fresh generated set while preserving earlier outputs.

## Blender version policy

The extension manifest minimum is **4.2.0**. Release CI validates the Blender integration on:

- Blender 4.2 LTS
- Blender 4.5 LTS
- Blender 5.2 LTS

The minimum stays at 4.2 until a future feature genuinely requires a newer Blender API.

## Languages

The Blender interface currently supports English, Japanese, Simplified Chinese and Korean. Language parity with Unity remains the next localization priority.

## Verification

Automated Blender runtime checks cover Remesh, deformation transfer, LODs, collision proxies, generated-output reuse, Lightmap UV generation, exact mesh-data linking, collider render-data stripping, Blender 5.x slotted Actions and extension validation.

The Blender extension package is licensed under **GPL-3.0-or-later**.
