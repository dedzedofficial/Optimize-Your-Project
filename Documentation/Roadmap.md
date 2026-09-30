# Optimize Your Project: roadmap

<img src="../Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" alt="Optimize Your Project logo" width="96">

**Current target: v0.7.1.**

Optimize Your Project is a **general developer optimization toolkit**. It should remove repetitive optimization chores from ordinary game, app, simulation, VR, social, prototype and asset-production workflows. Platform-specific helpers are optional layers on top of the general tools.

The product rule is simple:

> If a developer repeatedly opens inspectors, modifiers, import tabs, or menus to perform the same safe optimization task, turn that work into one clear button.

## Product priorities

1. **General projects first.** A normal Unity or Blender user should never feel that the tool expects a VRChat project.
2. **One-click actions before dashboards.** Keep common jobs direct and obvious.
3. **Small scope by default.** Work on the selected folder, loaded scenes, selected hierarchy or selected mesh; do not surprise users with whole-project changes.
4. **Safe outputs.** Use Undo, importer before/after data, or output copies when topology/appearance may change.
5. **Detailed scans only on request.** Do not flood the main UI with warnings before the user asks for diagnostics.
6. **Platform support is additive.** PC, mobile, VR, VRChat/VCC and future engine integrations can provide target-specific guidance without redefining the core tool.

## v0.7.0: unified one-click foundation

### Unity

The main Unity surface is reduced to two pages:

| Page | Scope | Main purpose |
| --- | --- | --- |
| **PROJECT** | Assets folder + loaded scenes | General game/project optimization |
| **AVATAR** | Selected character/avatar hierarchy | Focused character asset/effect optimization |

The old **World** page is merged into **Project** because loaded-scene optimization is useful to every developer, not only world creators.

Current direct jobs:

- Compress & size textures.
- Optimize particle systems.
- Compress imported meshes.
- Disable realtime shadows.
- Scan the entire project only when a detailed report is wanted.

The full **Updates** page is removed. Update status becomes a small footer:

- Green: current.
- Orange: one patch release behind.
- Red: two or more patches behind, or a newer minor/major version exists.
- Grey: status unknown.

The version feed keeps Unity and Blender versions separate so releases for one integration do not incorrectly trigger updates for the other.

### Blender

Blender v0.7 introduces a quick **One-Click Cleanup** section:

- **One-Click Remesh**: create a remeshed copy using automatically selected detail.
- **Merge Duplicate Vertices**: create a copy and weld nearby duplicate vertices.

Existing triangle-limit, join/atlas and LOD tools remain under **Advanced Mesh Tools**.

The first priority is static asset preparation for any real-time project. Rigged/shape-key assets are guarded where topology-changing actions could damage them.

## v0.7.1: focused mesh cleanup

Implemented:

- Blender **Clean Selected Mesh**, creating a separate copy with exact vertex merging, loose geometry cleanup, zero-area face cleanup, unused material slot cleanup and closed-surface normal repair.
- Conservative refusal of topology-sensitive inputs and cleanup rollback on failure.
- Consistent completion summaries for Unity batches and Blender quick actions.
- Blender regression coverage for source preservation, repeated cleanup, naming, materials/UVs, unsupported inputs and existing quick actions.
- Synchronized package, add-on and update-feed versions.

## v0.7.x: dependable batch cleanup

### Unity

- Selected-folder / selected-hierarchy scope picker shared across suitable actions.
- Restore the last texture-import batch when current settings still match the optimizer's previous result.
- Review Read/Write Enabled model and texture imports before changing them.
- Missing-reference navigator for loaded scenes and prefabs.

### Blender

- Batch merge-duplicate-vertices across selected static meshes.
- Batch remesh static prop selections with clear output naming.
- Export generated atlas images to durable files.

## v0.8: scene and asset workflow

### Unity

- Selected hierarchy branch particle optimization.
- Reviewed realtime-light shadow batches.
- Large-texture review by selected folder.
- Duplicate/redundant material usage report.
- Static batching candidate report without automatically changing batching.
- Build-size inventory using measured project/build information where available.

### Blender

- Batch LOD generation for selected static props.
- UV and missing-texture checks.
- Better atlas packing and padding.
- Before/after triangle, vertex and material-slot summaries.

## v0.9: project preparation

### Unity

- PC/mobile texture override review.
- Model importer review for Read/Write and compression.
- Optional project profiles for common import targets.
- Safer batch restoration history.
- Exportable optimization report for teams.

### Blender

- Export-preparation checks for FBX/GLB.
- Missing image and unsupported material diagnostics.
- Optional UV repair on copies.
- Collection-level cleanup actions.

## v1.0: general creator workflow

v1.0 should allow a developer to choose a scope and complete a routine optimization pass without navigating dozens of individual inspectors.

A guided run may include:

1. Select **project assets**, **scene hierarchy**, **character/avatar**, or **Blender selection**.
2. Show only relevant one-click actions for that scope.
3. Preview actions that can materially affect visuals or importer behavior.
4. Apply selected changes.
5. Produce a concise completion report and restoration path.

The core workflow must remain useful without any VR or social-platform SDK installed.

## Optional platform helpers

Platform helpers can be added when they remove real repetitive work and have been tested against the target platform.

### Unity targets

- PC / standalone.
- Android / general mobile.
- iOS.
- Console workflows where public tooling and testing make a safe integration possible.
- XR/VR projects.

### Social platforms

- VRChat / VCC.
- ChilloutVR.
- Resonite preparation.
- Other creator platforms where verified workflows exist.

These integrations should add platform-specific guidance or actions while leaving the same Project tools available to ordinary developers.

## Other engines

The goal is not to turn v0.7 into an unfocused multi-engine suite. New engine integrations should arrive after the Unity/Blender one-click patterns are proven.

### Godot

Good early candidates:

- Imported texture-size/compression review.
- Mesh import review.
- Scene resource cleanup/navigation.
- One-click project diagnostics for common oversized assets.

### Unreal Engine

Potential editor-plugin candidates:

- Texture LOD-group / maximum-size review.
- Static mesh LOD and Nanite eligibility review.
- Collision complexity checks.
- Repeated material-instance cleanup/navigation.

Any Unreal implementation should use Unreal's own editor APIs rather than trying to reuse Unity code.

### Other DCC tools

Future integrations may include tools such as Maya or 3ds Max if there are repeatable asset-cleanup jobs that can be implemented safely and maintained.

## One-click candidate backlog

| Area | Button / workflow | Repetitive work removed |
| --- | --- | --- |
| Unity textures | Compress & Size | Opening platform importer tabs asset by asset |
| Unity models | Review Read/Write | Checking model importers one at a time |
| Unity scenes | Optimize Particles | Repeating the same limits across effects |
| Unity scenes | Disable Selected Realtime Shadows | Editing lights individually |
| Unity project | Missing References | Hunting broken references manually |
| Unity project | Build Size Inventory | Searching for oversized content manually |
| Blender mesh | One-Click Remesh | Adding/configuring/applying remesh manually |
| Blender mesh | Merge Duplicate Vertices | Entering Edit Mode and running Merge by Distance repeatedly |
| Blender mesh | Clean Selected Mesh | Repeated loose/duplicate geometry cleanup |
| Blender mesh | Make LODs | Creating and naming decimated copies by hand |
| Blender export | Prepare Export | Rechecking names, textures, UVs and output files before engine import |

## Release quality gates

Every release should pass the following before being tagged:

- Package/add-on version matches the intended release tag.
- Static package checks pass.
- Unity compiles in the minimum supported editor version.
- Blender add-on enables without Python errors in supported versions.
- Destructive-looking Blender actions actually create copies unless clearly documented otherwise.
- Unity scene edits use Undo where practical.
- Importer changes avoid unnecessary reimports on a second identical run.
- Install instructions work from a clean project/profile.
- General project usage is documented before optional VR/platform-specific instructions.
- No release claims a guaranteed FPS gain from a static scan.

## Compatibility note

The Unity package ID `com.fishhwb.vr-optimizer` and several `VR*` internal type/folder names are historical. They remain during the v0.7 line to avoid breaking existing Unity package installations and references.

Public branding, UI text and future architecture use **Optimize Your Project** and are not limited to VR.
