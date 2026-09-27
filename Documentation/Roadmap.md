# FISHHWB VR Optimizer: automation roadmap

**Current release: v0.6.4.** Everything below is proposed future work, not a feature in the current package. Version numbers are planning targets, not release dates.

## Product goal

Turn repeated Unity Editor optimization chores into focused buttons: identify the relevant assets or scene objects, preview material changes when necessary, update only changed settings, and show exactly what happened. Prioritize **textures and particles**, then the recurring avatar and world tasks around them. Do not promise a frame-rate improvement from a static scan; verify results in the target platform build.

The [VRChat avatar performance ranking reference](https://creators.vrchat.com/avatars/avatar-performance-ranking-system/) counts factors including material slots, meshes, particles and lights, but its rank is a static assessment rather than a measurement of runtime frame time. The [avatar optimization guidance](https://creators.vrchat.com/avatars/avatar-optimizing-tips/) highlights material slots, particle rendering and realtime lights as practical areas to examine. For Quest worlds, use the [Android optimization guidance](https://creators.vrchat.com/platforms/android/quest-content-optimization/) alongside measured profiling.

## Planned releases

| Release | Core automation | Repeated work it removes | Safety boundary |
| --- | --- | --- | --- |
| **0.6.5 — Avatar starter** | Texture Change Preview; Avatar Check; OPTIMIZE AVATAR PARTICLES | Inspecting every texture setting and repeating particle changes on one avatar | Texture changes confirmed before import; particle changes use Undo; no rig or geometry edits |
| **0.6.6 — Scope and rollback** | Selection and folder scope for texture batches; restore last importer batch; per-item status | Repeatedly narrowing a global action and manually restoring changed `.meta` settings | Persistent before-state journal and a preview of restoration; no source-image changes |
| **0.6.7 — Scene lighting** | Batch review for shadow-casting realtime lights in a selected Hierarchy branch; opt-in batch shadow disable | Opening every light Inspector to turn off the same expensive setting | Preview names and old/new values; keep bake mode and light components intact; Undo |
| **0.6.8 — Particle workflow** | Per-effect cost shortlist and selected-root batch action; saved custom particle preset | Hunting through large effect hierarchies and re-entering a chosen set of particle limits | Only supported fields change; advanced curves and intentional modules are reported or explicitly opted in |
| **0.6.9 — Importer housekeeping** | Missing texture platform override fix; selected model importer Read/Write review | Repeating importer tab changes on many assets | Texture format stays untouched; Read/Write changes require an explicit per-model or batch preview because runtime mesh access may depend on it |
| **1.0 — Reliable release** | Unity version validation, documentation, sample project, automated package checks and release process | Repeated installation troubleshooting and regression checking | No new destructive feature required for 1.0 |

Each stage should be usable on its own. Release a stage only after testing in a representative Unity project, including an avatar with particles and a VR world scene.

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

## 0.6.6: Safer repeated batches

- **Scope picker:** Whole project, selected asset folder, or textures referenced under a selected scene root. Display scope and item count before running. The default remains explicit; never silently widen a selected scope.
- **Restore last texture batch:** Persist exact before-values for every touched platform override in a small project-local history record. Offer a preview and restore only paths whose importers still match the tool's recorded after-values; flag user edits as conflicts instead of overwriting them.
- **Useful completion report:** Per-asset errors, changed/unchanged/skipped totals, and a copyable list for investigating failures. Do not force a full rescan after a successful batch.

**Helps:** creators who try a preset, compare the result on Quest, and want to revise it without manually undoing hundreds of importer tabs.

## 0.6.7: Hierarchy light automation

- In a loaded scene or selected Hierarchy branch, list realtime lights with shadows, range, type and owning GameObject.
- Provide **DISABLE SELECTED SHADOWS** only after a review list. Record a single Unity Undo group, change only shadow mode, and report changed versus already off. Leave baked/mixed configuration and light intensity untouched.
- Preserve the individual review action from v0.6.4. Do not claim that disabling shadows is always visually acceptable.

**Helps:** world creators turning off shadows on a set of decorative lights without opening each Inspector. VRChat cautions that realtime avatar lights and shadows can be particularly costly; the visual decision still belongs to the creator.

## 0.6.8: Particle repetition at scale

- Reuse the current preset under a **selected Hierarchy branch**, not just the whole scene or selected avatar.
- Rank effects for review using observable settings: `maxParticles`, constant emission rate, mesh renderer, trails, collision, particle lights, shadows and transparent material. Label the ranking **heuristic**, never measured GPU time.
- Store one named custom preset in project settings so collaborators can run the same buttons with the same limits. Require an explicit opt-in for disabling any visual module; only cap supported constant values automatically.

**Helps:** effects-heavy avatars and worlds whose particle systems are nested in prefabs or subgroups. VRChat notes that a few large transparent particles can cost more than numerous small opaque ones, so raw particle count alone is not enough.

## 0.6.9: Importer chores with higher risk

- **FIX MISSING TEXTURE OVERRIDES:** use the chosen preset to add only missing platform maximum-size overrides for supported textures in the chosen scope. Keep the existing format and compression data.
- **REVIEW MODEL READ/WRITE:** list imported models used by the selected root with Read/Write on. Offer a previewed batch change only for checked models, with a warning that scripts, mesh baking and other runtime access can require readability. Reimport changed models only.
- Do **not** automatically decimate, merge meshes or delete materials. Those operations can affect rigs, UVs, blendshapes, animation and avatar appearance.

**Helps:** repetitive importer housekeeping while keeping potentially breaking model changes opt-in.

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
