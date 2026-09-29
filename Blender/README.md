# Optimize Your Project for Blender — 0.7.5 preview

<img src="../Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" alt="Optimize Your Project logo" width="112">

Publisher: FISHHWB | Ded Zed. See the [unified roadmap](../Documentation/Roadmap.md#blender-track-075-preview-and-later-work). Blender 3.6+ add-on, developed alongside the Unity package in [Optimize Your Project](https://github.com/dedzedofficial/Optimize-Your-Project). The Unity package has its own version and installation path.

## Install

After the `blender-v0.7.5` release is published, download `optimize-your-project-blender-0.7.5.zip` from [Releases](https://github.com/dedzedofficial/Optimize-Your-Project/releases). Install this add-on ZIP in Blender's **Edit > Preferences > Add-ons > Install...** (or **Get Extensions > Install from Disk** in newer versions), then enable it. In the 3D Viewport press **N** and open the **FISHHWB** tab.

## Blender mesh optimization: common tasks

**How do I reduce a mesh to a triangle limit in Blender?** Select one mesh, set **Triangle Limit** and use **Create Reduced Copy**. The add-on makes a decimated copy at or below that count while keeping the original. This is useful when preparing a static prop for Unity, VRChat or another real-time scene.

**How do I make LOD meshes in Blender?** Select a static mesh and press **Create LOD0 / LOD1 / LOD2**. It creates separate copies at 100%, at most 66% and at most 33% of the original triangle count. These are exportable mesh variants; automatic distance switching is configured later in the target engine.

**How do I join meshes, merge vertices and combine textures?** Select at least two mesh objects, set a weld distance, then use **Join Selected and Merge Vertices**. Enable **Merge Base Color Textures + UVs** when the materials meet the atlas requirements below. The tool creates a new mesh, one Base Color image atlas and remapped UVs. It does not bake normal, metallic or roughness maps.

All actions create copies so you can compare before and after. Inspect the result in Blender and the target engine before replacing production assets.

## Actions

- **Create Reduced Copy:** select one mesh in Object Mode, enter a triangle limit, then create a decimated duplicate at or below that count. Original remains intact.
- **Create LOD0 / LOD1 / LOD2:** select one static mesh in Object Mode. Make a new collection containing full-detail LOD0, LOD1 capped at 66% of LOD0 triangles, and LOD2 capped at 33%. Existing modifiers are applied to copies when enabled. The original stays intact. Lower LODs are hidden in the viewport for easier inspection. These are mesh variants, not an automatic Blender runtime distance switch or a Unity LODGroup. Shape keys, vertex groups, and armature modifiers are rejected.
- **Join Selected and Merge Vertices:** select two or more mesh objects, set a Merge Distance and create a single joined copy. The copy preserves world transforms and material slots. Nearby vertices are welded. Original objects remain intact.
- **Merge Base Color Textures + UVs:** enable this option before joining. The action gathers direct image Base Color links from supported Principled materials, makes one square atlas image and material, joins the copies, and remaps the joined mesh's active UVs to the atlas. Set Atlas Size and Padding. The generated image is stored in the Blend file; save or export it separately when preparing assets for another engine. For a triangle budget, run Create Reduced Copy on the joined result afterward.

**Apply Existing Modifiers** is enabled by default for each action and applies modifiers only to the output copy.

## Texture atlas limits

This first pass supports loaded single-file images directly linked to Principled BSDF Base Color, UV coordinates in the 0–1 range, and up to 64 distinct source images. It rejects UDIMs, mapped texture vectors, additional linked shader maps, missing UVs and shape keys on joined objects. The atlas copies Base Color image pixels and alpha; it does not bake procedural nodes, normal/metallic/roughness maps, shader values, animated UVs or custom shader behavior. It creates a fresh atlas material, so inspect shading before exporting. All images are fitted into equal square tiles, which can reduce detail or distort non-square source images. A large Merge Distance can damage UV seams and hard edges. Inspect the output and retain the originals.

The ZIP is source-checked. Runtime verification in Blender is required before publishing the release. Test on a copy of an actual asset before release.
