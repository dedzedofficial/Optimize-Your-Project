# Planned v0.6.5 update

This document describes planned work. **The features below are not available in v0.6.4.** The aim is to remove small, repetitive avatar optimization jobs while keeping changes easy to understand.

## 1. Texture Change Preview

Before **OPTIMIZE TEXTURES** reimports assets, show a list with each texture's path and its current and proposed PC, Android / Quest and iOS maximum sizes. Show an **Include** control for each changed texture and separate unchanged and unsupported textures from proposed changes. Confirm once to apply only included changes, then report changed, skipped and failed items.

**Where it helps:** large projects where a broad preset could affect a texture that needs special treatment, such as an avatar face or detailed UI. The developer reviews the exact importer changes before waiting for reimports. Source image files stay intact. Importer changes should still be committed to version control for restoration.

## 2. Avatar Check

Select an avatar root in the Hierarchy and run a focused, read-only check of the hierarchy under it. Show its skinned mesh vertex and triangle counts, materials and texture sizes, and particle system findings. Results select and ping the relevant scene object or asset. Use the same plain INFO / WARNING / CRITICAL language as the project scan. Keep this useful in ordinary Unity projects without a required VRChat SDK dependency.

**Where it helps:** finding which part of one avatar needs attention without sorting through findings from an entire world or project. This check diagnoses; it does not alter rigs, blendshapes, meshes or materials.

## 3. Optimize Avatar Particles

With an avatar root selected, press **OPTIMIZE AVATAR PARTICLES** to reuse the existing particle preset on particle systems underneath that root only. Show the number found, changed, unchanged and skipped. Record changes through Unity Undo and keep prefab editing behavior explicit so a scene instance is not confused with the original prefab asset.

**Where it helps:** an avatar with many effects can have its particle counts and selected costly modules adjusted in one pass without affecting effects elsewhere in the scene. Developers still review the visual result and save their scene or prefab when satisfied.

## Release boundary

No automatic mesh decimation, rig editing, material merging or physics changes. Scope the avatar actions to the selected root. Keep the window concise; reuse the existing presets rather than adding another large settings panel.
