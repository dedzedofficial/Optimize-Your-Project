# VR Optimizer for Blender — 0.7.5 plan

The existing repository root remains the Unity Package Manager package. Blender lives in `Blender/vr_optimizer_blender/` as a separate native add-on. **0.7.5 names the Blender add-on milestone, not the Unity package version.** Do not change Unity's `package.json` until a Unity release is independently ready.

## 0.7.5 scope

1. Provide four direct actions in the FISHHWB sidebar: reduce a selected mesh to a triangle cap, join selected meshes with an adjustable vertex weld distance, optionally make one Base Color image atlas with remapped UVs while joining, and create three static mesh LOD variants at 100%, 66%, and 33% triangle targets.
2. Always create copies; select the result and leave source objects and image files alone. Show triangle and merged-vertex counts in operator reports.
3. Gate the atlas on simple image-based materials and 0–1 UVs. Report why an unsupported material was skipped before creating an output. Support distinct materials sharing one image without duplicating atlas tiles.
4. Package one installable ZIP and document installation, workflow and texture limitations. Keep Blender scripts separate from Unity Editor assemblies.
5. Test LOD0/1/2 on static meshes with modifiers, UVs and materials. Confirm each measured result is at or below its target and that the original remains intact. These objects are authoring variants, not an automatic distance switch; Unity LODGroup setup remains manual.
6. Test in supported Blender versions before announcing 0.7.5 as released: two cubes with different transforms and materials, adjacent seam vertices, shared images, non-square images, alpha, modifiers, missing UV, tiled UV, UDIM, shape keys, multiple material slots, undo and save/reopen. Verify atlas appearance and triangle count in an exported GLB/FBX where applicable.

## Follow-on work

| Stage | One-button work | Release condition |
| --- | --- | --- |
| 0.7.5 stabilization | Real Blender regression scenes; atlas export PNG and size report; clear errors and progress on large images | Generated atlas survives save/reopen and exports with the mesh |
| 0.7.6 | Atlas packing that respects image aspect ratio, pixel padding and mip bleeding; separate image atlases for Base Color, normal and mask channels when mappings align | No visible seams in a tested target build |
| 0.8 | Preview selected mesh/texture memory and triangle counts; batch reduce static props with per-object targets and naming | Original files recoverable; measured counts match output |
| 0.9 | UV overlap and missing-texture checks; optional unwrap on copies; LOD copies for static objects | Detect unsupported rigs, shape keys and texture dependencies |
| 1.0 | Guided select → preview → run → report for Blender asset preparation, with export checks for Unity and VR social platforms | Real asset round trip and platform-specific validation |

Keep the interface short: choose the mesh operation, enter only the size or distance it needs, press one button. Place detailed warnings in a deliberate scan/report action later. Do not claim a VRChat rank or frame-rate increase from triangle counts alone.

## Camera visibility separation idea (research, after 0.7.5)

Provide a **Camera Visibility Preview** action for a chosen room or area. Place a camera at its center (or use selected cameras), sample all requested directions, test face visibility with frustum and occlusion checks, and report visible/uncertain/hidden faces. On confirmation, separate a **copy** into visible and candidate hidden geometry so the creator can reduce or inspect the latter. Keep source topology, UVs and materials unchanged. Never delete faces automatically. One central camera cannot describe every player viewpoint, mirrors, portals, moving props or the outside of the room; offer multiple camera positions and a conservative uncertainty class before any optimization.

The initial release gate is a test scene with doorways, occluders, two floors and several viewpoint positions. Confirm that faces visible from any selected camera remain in the visible set, compare counts before and after separation, and verify material/UV continuity. This is a proposed feature, not implemented in 0.7.5.
