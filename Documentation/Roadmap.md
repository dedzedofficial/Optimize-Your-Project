# FISHHWB VR Optimizer: automation roadmap

**Current release: v0.6.4.** Everything below is proposed future work, not a feature in the current package. Version numbers are planning targets, not release dates.

## Product goal

Turn repeated Unity Editor optimization chores into focused buttons: identify the relevant assets or scene objects, preview material changes when necessary, update only changed settings, and show exactly what happened. Prioritize **textures and particles**, then the recurring avatar and world tasks around them. Do not promise a frame-rate improvement from a static scan; verify results in the target platform build.

The [VRChat avatar performance ranking reference](https://creators.vrchat.com/avatars/avatar-performance-ranking-system/) counts factors including material slots, meshes, particles and lights, but its rank is a static assessment rather than a measurement of runtime frame time. The [avatar optimization guidance](https://creators.vrchat.com/avatars/avatar-optimizing-tips/) highlights material slots, particle rendering and realtime lights as practical areas to examine. For Quest worlds, use the [Android optimization guidance](https://creators.vrchat.com/platforms/android/quest-content-optimization/) alongside measured profiling.

## Release progression

Use **0.6.5** for the agreed improvement to the current 0.6 line. Each subsequent **minor release** delivers a complete workflow, not one isolated checkbox. Use patch numbers after those milestones for fixes and polish; do not reserve a separate release for every small action.

| Milestone | Theme and headline | Creator benefit |
| --- | --- | --- |
| **0.6.4 — Current** | Texture and particle actions, scene light and mesh diagnostics | First useful set of repeatable Editor buttons |
| **0.6.5 — Avatar starter** | Preview texture edits; check one avatar; optimize its particles | Try the tool on an avatar and know what will change |
| **0.7.0 — Controlled batches** | Optimize by project, folder or selection; restore the last texture batch | Safely handle many assets without repeating Inspector work |
| **0.8.0 — World effects** | Selected-branch particle batches and reviewed light-shadow batches | Tackle the scene work VR world creators repeat most |
| **0.9.0 — Quest preparation** | Cross-platform texture override fixes and reviewed model importer changes | Prepare PC/Quest assets without visiting every import tab |
| **1.0.0 — Creator workflow** | One guided preview and run for a selected avatar or scene branch, built from the proven actions above | Finish a routine optimization pass from one place |

These are proposed scopes, not dates or guarantees. New features move into release notes only when implemented and tested. Each milestone must work on its own; fixes to a released milestone can ship as 0.7.1, 0.8.1 and so on.

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

Apply the existing particle preset to particle systems under the selected avatar root only. Show found, changed, unchanged and skipped totals. Record scene changes through Unity Undo. If the selected root is a prefab asset instead of an editable scene object, make the editing behavior explicit before changes.

**Helps:** applying one sensible cap across an avatar's effect hierarchy without modifying world effects elsewhere in the scene.

## 0.7.0: Controlled batches and recovery

**Headline:** choose exactly what the texture button touches, then be able to restore a batch.

- **Scope picker:** Whole project, selected asset folder, or textures referenced under a selected scene root. Show scope and item count before preview. Never silently widen a selected scope.
- **Restore last texture batch:** Save exact before-values for touched platform overrides in a project-local history record. Preview restoration; restore only importers that still match recorded after-values, and flag subsequent user edits as conflicts.
- **Completion report:** Changed, unchanged, excluded, unsupported and failed counts, with paths and a copyable failure list. A second identical run should reimport nothing.

**Helps:** creators iterating on Quest texture settings across hundreds of assets without manually editing or restoring importer tabs.

## 0.8.0: World effects workflow

**Headline:** optimize particles and light shadows within a chosen scene branch, using a review list.

- **PARTICLES IN SELECTION:** apply the existing preset to a selected Hierarchy branch, not the entire scene. Rank effects for review using observable settings such as maximum count, constant emission, trails, collision, mesh rendering, lights, shadows and transparent material. Label the ranking a heuristic, not measured GPU cost.
- **REVIEW SCENE LIGHTS:** list realtime shadow-casting lights in the selected branch with type, range and owning object. **DISABLE SELECTED SHADOWS** changes only checked lights after confirmation. One Undo group restores the batch; leave bake mode, intensity and light objects intact.
- **Shared custom particle preset:** save a named preset with the project so collaborators can repeat the same changes; visual modules remain explicit opt-ins.

**Helps:** effects-heavy worlds where dozens of particle and light components need the same limited set of settings changed. VRChat notes that large transparent particles can cost more than raw counts suggest, so the review list does not equate particle count with actual frame time.

## 0.9.0: Quest preparation and importer chores

**Headline:** automate platform importer checks after avatar and world edits are under control.

- **PC / QUEST TEXTURE VIEW:** compare the platform caps for textures in the chosen scope; flag missing Android overrides and show which files a proposed Quest preset would change. **FIX MISSING OVERRIDES** adds only selected missing size overrides, preserving format, compression and source images.
- **MODEL READ/WRITE REVIEW:** list models used by a selected root that are imported as readable. Offer a previewed, checked batch action; warn that scripts, mesh baking and other runtime operations may depend on Read/Write. Reimport changed models only and provide a restore path.
- **Quest readiness summary:** report work still needed using actual observed settings. Do not claim a VRChat rating or device frame-rate result based on this static summary.

**Helps:** creators preparing an Android / Quest version who would otherwise work through platform and model importer tabs asset by asset. No automatic decimation, mesh merging or material deletion.

## 1.0.0: Complete creator workflow

**Headline:** one guided run that brings the proven actions together without hiding their effects.

1. Select an avatar root or loaded scene branch and choose PC, Quest or both.
2. Show a single prioritized preview: texture import changes, particle settings and eligible light-shadow changes. Leave mesh geometry diagnostic only.
3. Include or exclude items, run the selected actions, and produce a concise completion report with restoration options for importers and Undo for scene changes.
4. Ship a sample avatar/scene, a clean Git URL installation check, compatibility tests for supported Unity versions, a clear changelog and regression coverage for cancellation and second-run no-op behavior.

**Helps:** an experienced creator finish a routine pass in minutes while still seeing exactly which assets or components will be edited. This is an integration of tested 0.6–0.9 actions; it is not a new automatic decimation or hidden "optimize everything" button.

## Engineering rules for every release

1. **Explicit scope:** show whether an action touches the project, a folder, loaded scenes, a selected Hierarchy branch or one avatar. Scan unopened scenes only if a future feature explicitly supports it.
2. **Compare first:** skip assets with matching settings. Report unsupported texture types instead of forcing overrides.
3. **Preview when appearance or runtime behavior may change:** exact per-item old/new values; explicit confirmation for large importer batches and light/model actions.
4. **Recovery:** Unity Undo for scene-object changes; before-state journal plus conflict detection for importer changes. Cancel between items without claiming rollback of completed work.
5. **Large-project behavior:** process in chunks, show progress and cancellation, avoid scans every editor frame and avoid full AssetDatabase refreshes unless required.
6. **Modular scanners and actions:** add new modules without rewriting `VRProjectScanner`; separate analysis from mutation.
7. **Honest metrics:** label importer dimensions, estimated costs and static VRChat limits correctly. Use Unity Profiler and on-device testing for frame-rate claims.
8. **Compatibility:** keep the core editor package free of external dependencies; optional VRChat-specific checks must be guarded by presence of the SDK and Unity version.

## Release acceptance checklist

- Git URL install works with `package.json` at the repository root in a clean supported Unity project; Editor assembly compiles without the VRChat SDK.
- Previewed changes match the saved importer/object settings exactly; a second run without user edits makes zero changes.
- Cancellation clears progress UI and reports partial results without corrupting project state.
- Undo restores scene-object edits; importer batch restoration either restores recorded settings or reports a conflict.
- Tests include default/normal textures, intentional platform overrides, large particle systems, nested avatar roots, prefab instances, inactive children and multiple loaded scenes.
- README and changelog state what shipped; planned items stay in this roadmap until implemented and verified.
