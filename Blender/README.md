# Optimize Your Project for Blender: v0.7.4

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

For the fixed v0.7.4 release:

```text
https://github.com/dedzedofficial/Optimize-Your-Project.git#v0.7.4
```

### Blender

**Git URL install:** clone the repository into one of Blender's add-on script directories using an import-safe folder name:

```bash
git clone https://github.com/dedzedofficial/Optimize-Your-Project.git optimize_your_project
```

To print Blender's available add-on directories, run this in Blender's Python Console:

```python
import addon_utils
print("\\n".join(addon_utils.paths()))
```

Run the `git clone` command from one of those add-on directories, then restart Blender or use **Refresh Local** and enable **Optimize Your Project for Blender**. Update a Git install later with:

```bash
git -C optimize_your_project pull
```

Blender's Add-ons screen does not directly consume an arbitrary Git clone URL, so this Git method uses the repository itself as the installed add-on. The normal ZIP route remains available from [GitHub Releases](https://github.com/dedzedofficial/Optimize-Your-Project/releases):

```text
optimize-your-project-blender-0.7.4.zip
```

Then use **Edit > Preferences > Add-ons > Install...** or **Get Extensions > Install from Disk**.

### VRChat Creator Companion / VCC

Use [Add Optimize Your Project to VCC](vcc://vpm/addRepo?url=https%3A%2F%2Fdedzedofficial.github.io%2FOptimize-Your-Project%2Findex.json), then add **Optimize Your Project** to the chosen project.

</details>

> **New here?** Start with the [Overview](../README.md). You can read the complete documentation directly on GitHub before installing anything.


Blender support for **Optimize Your Project** now combines fast one-click cleanup, Game-Ready static copies and batch preparation for static meshes. The v0.7.4 sidebar also supports English, Japanese, Simplified Chinese and Korean.

## Install

### Git URL install

1. In Blender's Python Console, run `import addon_utils; print("\\n".join(addon_utils.paths()))` and choose one of the displayed add-on directories.
2. Open a terminal in that directory.
3. Clone the repository with `git clone https://github.com/dedzedofficial/Optimize-Your-Project.git optimize_your_project`.
4. Restart Blender or use **Refresh Local** in Preferences.
5. Enable **Optimize Your Project for Blender**.
6. In the 3D Viewport press **N** and open the **FISHHWB** tab.

To update the Git install later, run `git -C optimize_your_project pull` from the same add-on directory.

The destination name `optimize_your_project` is intentional: it gives Blender an import-safe Python module folder while still using the normal GitHub Git URL.

### ZIP install

1. Download `optimize-your-project-blender-0.7.4.zip` from the GitHub Releases page after the `blender-v0.7.4` release is published.
2. In Blender, use **Edit > Preferences > Add-ons > Install...** or **Get Extensions > Install from Disk**.
3. Enable **Optimize Your Project for Blender**.
4. In the 3D Viewport press **N** and open the **FISHHWB** tab.

## One-click cleanup

Select one static mesh in Object Mode.

### Clean Selected Mesh

Press **Clean Selected Mesh** to process the active mesh and select a separate `_Clean` copy in Object Mode. Existing names get a numbered suffix such as `_Clean_001`. Other selected objects are not processed.

The button merges vertices at exactly equal coordinates, removes zero-area faces, loose edges and isolated vertices, then removes unused material slots. It recalculates normals only on closed manifold components. Valid disconnected faces and open surfaces are kept, including their winding. UVs and used material assignments are retained. The original object and mesh data are untouched.

The tool refuses shape keys, vertex groups, rigs, modifiers, linked/overridden data, custom split normals, empty meshes and non-finite coordinates with a reason. Make a separate static copy and resolve these conditions first. Loose lines and points are removed intentionally, so compare the result before replacing an asset that uses them.

The **Last Result** panel reports object outcomes plus vertices removed, exact duplicates merged, loose edges removed, zero-area faces removed, material slots removed and faces reoriented. Duplicate counts are part of the total removed vertices, not an additional total. A clean mesh reports **Unchanged** even though an output copy is created. Failures discard the incomplete copy and restore the original selection.

### Create Game-Ready Copy

Press **Create Game-Ready Copy** on a supported static mesh. The add-on creates a separate `_GameReady` object and keeps the original unchanged.

When **Apply Existing Modifiers** is enabled, modifiers are evaluated onto the new copy. The copy then applies rotation and scale, performs the conservative cleanup pass, removes unused material slots and reports the resulting triangle count. Rigged meshes, shape keys, vertex groups, linked data and custom split normals are skipped instead of being flattened silently.

### One-Click Remesh

Press **One-Click Remesh**. The add-on creates a new `_Remesh` copy and automatically chooses a practical remesh detail size from the mesh dimensions.

This is intended for static props and cleanup meshes. Rigged, vertex-group, armature, and shape-key meshes are skipped because remeshing changes topology.

### Merge Duplicate Vertices

Set **Merge Distance** and press **Merge Duplicate Vertices**. The add-on creates a new `_Merged` copy and welds nearby vertices.

Shape-key meshes are skipped to avoid breaking topology-dependent keys.

## Batch mesh preparation

Select multiple mesh objects in Object Mode.

- **Clean Selected Meshes** creates a separate cleaned copy for every supported selected static mesh. Unsupported topology-sensitive meshes are skipped and the originals stay untouched.
- **Create LODs for Selection** runs the guarded LOD0 / LOD1 / LOD2 workflow across supported selected static meshes.
- **Show Heavy Meshes** selects scene mesh objects above the configured triangle threshold so high-cost geometry is easier to find.

## Interface languages

Use the **Language** control at the top of the sidebar. v0.7.4 includes English, Japanese, Simplified Chinese and Korean for the main Blender workflow. Future language additions are tracked in the project roadmap.

## Advanced Mesh Tools

The earlier preview tools are still available below the quick section:

- **Create Reduced Copy**: decimated duplicate under a triangle limit.
- **Join Selected and Merge Vertices**: joins selected mesh copies and welds nearby vertices.
- **Merge Base Color Textures + UVs**: optional supported Base Color atlas path for the join tool.
- **Create LOD0 / LOD1 / LOD2**: static mesh copies at 100%, up to 66%, and up to 33% triangle counts.

These tools create output copies so the source object remains available for comparison.

## Notes

Blender v0.7.4 is early support. Test generated meshes before replacing production assets, especially before GLB/FBX export into Unity or another engine.
