# FISHHWB VR Optimizer: automation roadmap

**Current package target: v0.6.7.** Later milestones below are proposed future work. Version numbers are planning targets, not release dates. The existing Git URL package is **Unity Editor only**.

## Product goal

Turn repeated Unity Editor optimization chores into focused buttons: identify the relevant assets or scene objects, preview material changes when necessary, update only changed settings, and show exactly what happened. Prioritize **textures and particles**, then recurring avatar, world and indie-game tasks around them. Do not promise a frame-rate improvement from a static scan; verify results in the target platform build.

The window should eventually offer three **workflow choices**, not three separate packages or a wall of options:

| Workflow | Default scope | Useful actions |
| --- | --- | --- |
| **VR Avatar** | Selected avatar root | Texture preview, avatar check, particle controls; optional platform-specific guidance after platform validation |
| **VR World** | Selected scene branch or loaded scenes | Texture preview, particle changes, reviewed light shadows; optional platform-specific guidance after platform validation |
| **Unity Game** | Selected folder or scene branch | Texture and Sprite import caps, particle and light changes, reviewed model imports |

Every action still shows its actual scope. A game developer should be able to use the same texture button without adopting VRChat conventions. VRChat-specific checks remain optional.

The [VRChat avatar performance ranking reference](https://creators.vrchat.com/avatars/avatar-performance-ranking-system/) counts factors including material slots, meshes, particles and lights, but its rank is a static assessment rather than a measurement of runtime frame time. The [avatar optimization guidance](https://creators.vrchat.com/avatars/avatar-optimizing-tips/) highlights material slots, particle rendering and realtime lights as practical areas to examine. For Quest worlds, use the [Android optimization guidance](https://creators.vrchat.com/platforms/android/quest-content-optimization/) alongside measured profiling.

## Release progression

Use **0.6.6** for the World/Avatar UI and reviewed mesh compression. Each subsequent **minor release** delivers a complete workflow, not one isolated checkbox. Use patch numbers after those milestones for fixes and polish; do not reserve a separate release for every small action.

| Milestone | Theme and headline | Creator benefit |
| --- | --- | --- |
| **0.6.4 — Foundation** | Texture and particle actions, scene light and mesh diagnostics | First useful set of repeatable Editor buttons |
| **0.6.5 — Avatar starter** | Preview texture edits; check one avatar; optimize its particles | Try the tool on an avatar and know what will change |
| **0.6.6 — World and avatar pages** | World / Avatar pages, area issue buttons, severity filters, direct controls, reviewed mesh compression | Find one issue type and selectively apply a model compression level |
| **0.6.7 — Current implementation** | Editor icon, update status/action, first general Unity asset workflow | Keep the package current and help non-VR projects with one useful batch action |
| **0.7.0 — Controlled batches** | Expand folder/selection scopes and add texture batch restoration to the Project page | Safely handle game and VR textures without repeating Inspector work |
| **0.8.0 — Scene effects** | Selected-branch particle batches and reviewed light-shadow batches; validate a ChilloutVR choice | Tackle effects and lighting in VR worlds and indie-game levels |
| **0.9.0 — Platform imports** | PC/mobile texture override fixes, reviewed model importer actions and Resonite preparation guidance | Prepare assets for more destinations without visiting every import tab |
| **1.0.0 — Unity creator workflow** | One guided preview and run for an avatar, scene branch or game asset folder, with validated platform choices | Finish a routine VR or indie-game optimization pass from one place |
| **After 1.0 — Other engines** | Prove a Godot editor add-on, then investigate an Unreal Editor plugin | Bring proven repetitive actions to other engines using their native tools |

These are proposed scopes, not dates or guarantees. New features move into release notes only when implemented and tested. Each milestone must work on its own; fixes to a released milestone can ship as 0.7.1, 0.8.1 and so on.

## VR social platform expansion

**Platform selection changes recommendations, not the meaning of Unity importer settings.** The main optimizer remains useful without choosing a social platform. Add a platform choice only after testing against that platform's current creator tooling; unsupported or unavailable integrations must say so in the UI.

| Platform | Practical automation path | Release gate |
| --- | --- | --- |
| **VRChat** | Keep optional avatar/world guidance on top of the Unity texture, particle and light buttons; do not require the SDK for the core package. | Verify any SDK-specific check and current performance guidance in a VRChat project. |
| **ChilloutVR** | Its [Content Creation Kit uses Unity](https://docs.chilloutvr.net/cck/setup/), so reuse proven Unity actions. In 0.8.0, investigate an optional CCK-aware avatar/world choice that detects the installed kit and reports only verified platform-specific issues. | Test in a supported CCK project; do not change CCK components, rigs or upload settings automatically. |
| **Resonite** | Offer a **preparation report** for meshes, textures and effects when a creator is preparing source assets. Resonite also documents a [UnitySDK import route](https://wiki.resonite.com/UnitySDK), but Unity import settings cannot be assumed to describe final in-game behavior. | Test the real Resonite import path and consult its [optimization guidance](https://wiki.resonite.com/Optimization_guidelines/) before suggesting any platform-specific automatic fix. |
| **Meta Horizon Worlds** | Investigate a separate asset-preparation or editor workflow for its [Desktop Editor model import](https://developers.meta.com/horizon-worlds/learn/videos/importing-custom-models/). The Unity package must not claim it can edit a Horizon world. | Prove a supported interchange format and an authorized workflow in the native creator tools; no platform claims based on Unity scene scans. |

**Sequence:** general Unity actions first; verified ChilloutVR support as a Unity-based pilot; Resonite preparation reporting; Horizon Worlds investigation after the core Unity workflow is stable. Additional social VR platforms can be evaluated using the same criteria instead of being added as empty dropdown entries. A platform-specific button should remove an actual repetitive creator task, such as applying reviewed asset caps to a selected avatar, rather than only displaying a score.

## 0.6.5: Texture Change Preview and first avatar buttons

### Texture Change Preview

1. Collect supported 2D textures once and compare current PC / Android / iOS importer maximums with proposed values. Clearly show when a source texture is already smaller than the proposed cap.
2. Show **path, current size, proposed size, changed/unchanged/unsupported**, with an **Include** checkbox per proposed change. Offer *Include all* and *Exclude all* for a manageable batch.
3. Reimport only included textures with actual changes. A cancel stops between assets; report changed, unchanged, excluded, unsupported and failed counts with paths for failures.
4. Fix the current cap-only behavior deliberately: if the user picks a larger maximum than an existing platform override, show that increase in the preview and apply it only if included. Never change source image pixels, format, compression, mipmaps or filters.

**Helps:** safely applying Quest caps to hundreds of textures while excluding a face, UI or decal that needs detail. The preview replaces opening every texture Inspector.

### Avatar Check

Select one avatar root in the Hierarchy. Show a concise inventory of used textures, skinned mesh triangle and vertex counts, material slot totals, and particle systems, with **SELECT** for the responsible object or asset. Reuse existing scanners where sensible. No required VRChat SDK dependency and no automatic geometry changes.

**Helps:** finding the expensive pieces of one avatar without filtering a whole-project report.

### OPTIMIZE AVATAR PARTICLES

Apply the selected particle controls to particle systems under the selected avatar root only. Show found, changed, unchanged and skipped totals. Record scene changes through Unity Undo. If the selected root is a prefab asset instead of an editable scene object, make the editing behavior explicit before changes.

**Helps:** applying one sensible cap across an avatar's effect hierarchy without modifying world effects elsewhere in the scene.

## 0.6.7 proposal: recognizable tool, reliable updates, broader Unity utility

**Implemented in code, pending Unity Editor verification and a published release.** The package manifest is now 0.6.7. The one or two button goal remains: open an area, preview changes, apply selected changes.

### Icon and package identity

- Add a simple, readable square icon in the Editor assembly. Show it in the docked tab through `EditorWindow.titleContent`, the window header, and the package documentation. Include a high-resolution source asset and Unity-friendly small sizes; check it in light and dark themes.
- Remove the discarded illustrative UI image from the README. Use a real Unity Editor capture only when the layout has been tested in Unity.

### Version notice and Update action

1. Read the installed version from the package metadata. On a user-initiated check, fetch the newest stable GitHub Release tag, compare numeric versions, and show a small **Update available: vX.Y.Z** notice. Check at most once per day while the window is open, cache the result locally, offer **Check now**, and show a quiet error only after a manual check. Ignore prereleases unless explicitly chosen later.
2. **View release notes** opens the exact GitHub release. **Update** first displays source, installed version, target version and whether project changes must be saved. No silent installs or forced domain reloads.
3. If installed from a Git URL in Unity Package Manager, update using Unity's Package Manager API with a URL pinned to the verified release tag. Track request completion and show the real result. If installed from VCC/VPM, link to the package in Creator Companion and let VCC resolve it. If embedded/local, show instructions to update that source rather than overwriting files. Do not attempt to update an unknown source.
4. A GitHub Release and VPM listing must be published and reachable before enabling update notices for that version. The first v0.6.7 acceptance test covers no release, offline/network failure, already-current, newer stable release, and each supported install source.

### General texture workflow to choose

The Sprite-only proposal was declined. The PROJECT page now includes **Texture Compression Cleanup**: list uncompressed platform imports by source asset and target platform, preview what Unity's automatic GPU compression choice would become, and selectively fix them without touching maximum size, alpha, normal map type, filter mode or source pixels. Explicit format choices are skipped. The preview describes the importer setting change and logs the resolved format after reimport; it does not promise a frame-rate percentage.

Other candidate buttons: review **Read/Write Enabled** textures and disable it only after explicit selection; enable **mipmap streaming** on checked large 3D textures when project streaming is configured; review textures using a format unsuitable for the chosen platform. These need separate previews because scripts may require CPU pixel data, UI textures may need full-resolution mip levels, and format support differs by device. None should silently rewrite every texture.

**Release gate once chosen:** icon legible at tab size; updater tested against supported install sources; texture batch verified in Unity on opaque, alpha, normal map, UI and mask assets across relevant build targets. A second identical run must reimport nothing.

### Other general Unity candidates (choose after testing 0.6.7)

| Candidate | Repetitive job it could remove | Why it needs review |
| --- | --- | --- |
| Texture compression cleanup | Selectively fix uncompressed platform imports | Preserve texture type, alpha and intentional format overrides |
| Read/Write import cleanup | Find models and textures holding CPU-side data unnecessarily | Scripts, colliders and runtime mesh edits may depend on access |
| Missing references | Collect broken scene/prefab references into one navigable list | Deleting or replacing references needs context |
| Static batching candidates | Find repeated static props with compatible materials | Profile draw calls and memory before changing batching |
| Light shadow batch | Review and disable selected costly shadows in game scenes | Affects visual intent and baked/realtime behavior |
| Build size inventory | Group large assets and packages by measured build contribution | Editor asset size alone does not equal build size |

## Additional update options after 0.6.6

| Candidate | Repetitive job removed | Sensible stage |
| --- | --- | --- |
| Material usage map | Locate duplicate and unused material slots across an avatar | 0.7.x |
| Texture restore batches | Restore importer overrides after a rejected Quest test | 0.7.0 |
| Scene branch controls | Apply saved particle controls to an effects hierarchy | 0.8.0 |
| Shadow review batch | Turn off selected realtime shadows with one Undo group | 0.8.0 |
| Model importer review | Find and selectively disable Read/Write on safe assets | 0.9.0 |
| Broken reference navigation | Jump directly to missing scene or prefab references | 0.8.x |
| Reusable team profiles | Run a named project profile for repeat imports | 1.0.0 |
| Other social VR preparation | Generate platform-specific asset preparation where verified | After 1.0 |

Each candidate needs an exact before/after preview where importer or visual behavior changes, and a verified way back. Keep VRChat, ChilloutVR, Resonite and Horizon Worlds integrations separate where their creator pipelines differ.

## Mesh and avatar work to evaluate

| Stage | Mesh or avatar task | Safe release boundary |
| --- | --- | --- |
| 0.7.x | Record model importer changes for batch restoration | Restore only importers whose current settings still match the tool's last edit |
| 0.7.x | Find unused or duplicate material slots in a selected avatar | Preview references; report only until animation and shader behavior can be checked |
| 0.8.x | Selected branch mesh audit with large bounds and redundant hidden meshes | Never remove components without a dependency and animation review |
| 0.8.x | Avatar effect inventory and per-system particle selections | Apply only checked scene objects with a single Undo group |
| 0.9.x | Reviewed model Read/Write changes and mesh optimization import flags | Require per-model opt-in and verify scripts that need CPU mesh access |
| 0.9.x | Optional LOD authoring guidance for world props | Avoid automatic LOD generation that alters silhouettes or collision |
| 1.x | Mesh merge candidates for repeated static props | Check occlusion, lightmaps, materials, colliders and draw calls first; no blind joining |
| 1.x | Avatar material and skinned mesh workflows | Require animation/rig/shader compatibility validation and a reversible result |

Mesh compression reduces stored mesh data but is not a reliable way to improve frame rate. Prioritize profiling, visibility and draw-call investigations where those are the bottlenecks. Performance estimates must be measured in the target build.

## 0.7.0: Controlled batches and recovery for Unity games

**Headline:** choose exactly what the texture button touches, then be able to restore a batch.

- **Scope picker:** Whole project, selected asset folder, or textures referenced under a selected scene root. Show scope and item count before preview. Never silently widen a selected scope.
- **Restore last texture batch:** Save exact before-values for touched platform overrides in a project-local history record. Preview restoration; restore only importers that still match recorded after-values, and flag subsequent user edits as conflicts.
- **Completion report:** Changed, unchanged, excluded, unsupported and failed counts, with paths and a copyable failure list. A second identical run should reimport nothing.
- **Unity Game workflow choice:** use a selected asset folder or scene root without an avatar or VRChat SDK. Extend the Sprite workflow to mixed texture folders and restore history; a 2D developer should be able to review and restore an entire art batch.

**Helps:** creators iterating on Quest textures or PC/mobile game art across hundreds of assets without manually editing or restoring importer tabs.

## 0.8.0: Scene effects workflow

**Headline:** optimize particles and light shadows within a chosen scene branch, using a review list.

- **PARTICLES IN SELECTION:** apply the selected controls to a selected Hierarchy branch, not the entire scene. Rank effects for review using observable settings such as maximum count, constant emission, trails, collision, mesh rendering, lights, shadows and transparent material. Label the ranking a heuristic, not measured GPU cost.
- **REVIEW SCENE LIGHTS:** list realtime shadow-casting lights in the selected branch with type, range and owning object. **DISABLE SELECTED SHADOWS** changes only checked lights after confirmation. One Undo group restores the batch; leave bake mode, intensity and light objects intact.
- **Shared particle settings:** optionally save a project configuration for repeat actions; the interface retains direct controls and visual modules remain explicit opt-ins.
- **ChilloutVR validation pilot:** test the same selected avatar/world actions in a supported Unity + CCK project. Show a platform choice only for checks and actions that have been validated there; keep the core actions usable without CCK.

**Helps:** effects-heavy VR worlds and indie-game levels where dozens of particle and light components need the same limited set of settings changed. VRChat notes that large transparent particles can cost more than raw counts suggest, so the review list does not equate particle count with actual frame time.

## 0.9.0: Platform preparation and importer chores

**Headline:** automate PC/mobile importer checks after avatar and scene actions are under control.

- **PC / MOBILE TEXTURE VIEW:** compare platform caps for textures in the chosen scope; flag missing Android and iOS overrides and show which files the entered Quest or general mobile cap would change. **FIX MISSING OVERRIDES** adds only selected missing size overrides, preserving format, compression and source images.
- **MODEL READ/WRITE REVIEW:** list models used by a selected root that are imported as readable. Offer a previewed, checked batch action; warn that scripts, mesh baking and other runtime operations may depend on Read/Write. Reimport changed models only and provide a restore path.
- **Platform readiness summary:** report work still needed using actual observed settings. Do not claim a VRChat rating or device frame-rate result based on this static summary.
- **Resonite preparation report:** list source meshes, textures and effects from a selected hierarchy and link each finding to the source asset. Label the output as pre-import guidance, not a measured Resonite performance result or an automatic in-game optimizer.

**Helps:** creators preparing Quest avatars or Android/iOS indie games who would otherwise work through platform, model importer tabs asset by asset. No automatic decimation, mesh merging or material deletion.

## 1.0.0: Complete Unity creator workflow

**Headline:** one guided run that brings the proven actions together without hiding their effects.

1. Choose **VR Avatar**, **VR World** or **Unity Game**, then select an avatar root, loaded scene branch or asset folder and a PC/mobile target. An optional social-platform choice appears only for validated integrations.
2. Show a single prioritized preview of applicable texture import changes, particle settings, eligible light-shadow changes and any explicitly selected importer action. Leave mesh geometry diagnostic only.
3. Include or exclude items, run the selected actions, and produce a concise completion report with restoration options for importers and Undo for scene changes.
4. Ship a sample avatar/scene, a clean Git URL installation check, compatibility tests for supported Unity versions, a clear changelog and regression coverage for cancellation and second-run no-op behavior.

**Helps:** an experienced VR or indie-game creator finish a routine pass in minutes while still seeing exactly which assets or components will be edited. This integrates tested 0.6–0.9 actions; it is not a hidden "optimize everything" button.

## After 1.0: Other engine options

The Unity Package Manager package cannot run in another engine. Treat each new engine as a **separate native editor add-on** with its own installation instructions, versioning and tests. Reuse the product approach—scope, preview, compare, apply, restore and report—rather than copying Unity importer code or assuming equal engine settings.

1. **Godot pilot:** build a small `EditorPlugin` add-on with one complete workflow: select a project folder, preview texture import settings, apply checked changes, then restore a batch. Validate against a supported Godot version and a real 2D/3D sample project before adding particle or light actions. Godot exposes editor extension points through [`EditorPlugin`](https://docs.godotengine.org/en/stable/classes/class_editorplugin.html).
2. **Unreal investigation and pilot:** use editor-only tooling such as Editor Utility Widgets or Python to trial a selected-folder texture import review. First confirm the appropriate asset API, transaction/undo behavior and packaging path in the targeted Unreal version. Epic documents editor scripting and utility widgets for asset workflows: [Scripting and Automating the Unreal Editor](https://dev.epicgames.com/documentation/unreal-engine/scripting-and-automating-the-unreal-editor).
3. **Shared roadmap, engine-specific behavior:** use common terms for what a batch proposes and records, but maintain separate rules for each engine's texture, particle and light systems. A feature ships for an engine only after native preview, cancellation, restoration and test coverage exist there.

**Release approach:** decide the first non-Unity engine from actual creator demand and a working prototype. A Godot or Unreal add-on starts at its own pre-1.0 version; do not label an untested port as part of the Unity 1.0.0 release.

## Engineering rules for every release

1. **Explicit scope:** show whether an action touches the project, a folder, loaded scenes, a selected Hierarchy branch or one avatar. Scan unopened scenes only if a future feature explicitly supports it.
2. **Compare first:** skip assets with matching settings. Report unsupported texture types instead of forcing overrides.
3. **Preview when appearance or runtime behavior may change:** exact per-item old/new values; explicit confirmation for large importer batches and light/model actions.
4. **Recovery:** Unity Undo for scene-object changes; before-state journal plus conflict detection for importer changes. Cancel between items without claiming rollback of completed work.
5. **Large-project behavior:** process in chunks, show progress and cancellation, avoid scans every editor frame and avoid full AssetDatabase refreshes unless required.
6. **Modular scanners and actions:** add new modules without rewriting `VRProjectScanner`; separate analysis from mutation.
7. **Honest metrics:** label importer dimensions, estimated costs and static VRChat limits correctly. Use Unity Profiler and on-device testing for frame-rate claims.
8. **Compatibility:** keep the core editor package free of external dependencies; optional VRChat or ChilloutVR checks must be guarded by presence of the relevant SDK/CCK and supported Unity version. Do not transfer one platform's limits to another.

## Release acceptance checklist

- Git URL install works with `package.json` at the repository root in a clean supported Unity project; Editor assembly compiles without the VRChat SDK.
- Previewed changes match the saved importer/object settings exactly; a second run without user edits makes zero changes.
- Cancellation clears progress UI and reports partial results without corrupting project state.
- Undo restores scene-object edits; importer batch restoration either restores recorded settings or reports a conflict.
- Tests include default/normal textures, intentional platform overrides, large particle systems, nested avatar roots, prefab instances, inactive children and multiple loaded scenes.
- README and changelog state what shipped; planned items stay in this roadmap until implemented and verified.
