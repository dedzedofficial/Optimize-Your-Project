# Optimize Your Project roadmap

<img src="../Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" alt="Optimize Your Project logo" width="96">

<p align="center">
  <a href="../README.md"><strong>Overview</strong></a> |
  <a href="../Blender/README.md"><strong>Blender Guide</strong></a> |
  <a href="../Documentation/Roadmap.md"><strong>Roadmap</strong></a> |
  <a href="../Documentation/Architecture.md"><strong>Architecture</strong></a> |
  <a href="../CHANGELOG.md"><strong>Changelog</strong></a>
</p>

## Direction

Optimize Your Project is intended to become a cross-engine optimization toolkit built around a small number of reliable one-click jobs. The project should remove repetitive developer work without hiding risky changes, guessing at artistic intent, or turning the interface into a wall of settings.

Unity and Blender share one project version. Blender support starts at **4.2** and uses Blender Extensions. Future engine integrations should use the same release version, safety rules, localization direction and result-summary style.

## Priority key

- **P0 - Core / release critical:** stability, recovery, existing-button improvements and issues that directly affect current users.
- **P1 - High priority:** major useful additions that fit the one-click design and broaden supported workflows.
- **P2 - Medium priority:** new integrations or deeper automation that need more validation before becoming default behavior.
- **P3 - Later / experimental:** useful ideas that should not delay the main Unity, Blender, Godot and Unreal work.

## Current baseline: v0.7.66

### Unity

- readable Project / Character interface with separate navigation and language rows,
- one **Quick Optimize** area instead of scattered top-level workflows,
- Balanced, Mobile and VR quick configurations,
- bundled Optimize Current Scope / Optimize Character actions,
- texture optimization and import repair,
- model-import compression that preserves stronger existing compression,
- particle limits including Constant and Two Constants lifetime caps,
- safe material-cost fixes,
- baked-light setup kept as an explicit action,
- guarded realtime-shadow disabling kept as an explicit action,
- missing-script preflight and cleanup,
- UI raycast optimization with Selectable, CanvasGroup and EventSystem safety checks,
- project and character review tools,
- importer history, protection, trial and restore infrastructure,
- conservative permanent unused-asset cleanup behind a dedicated Danger Zone and two warnings,
- automatic interface-language detection,
- unified project update checking.

### Blender 4.2+

- one readable **Quick Optimize** sidebar panel,
- One-Click Remesh with guarded UV, material and deformation preservation,
- LOD0 / LOD1 / LOD2 generation,
- optional collision proxy from LOD2,
- generated-output reuse and manual-edit protection,
- Generate Lightmap UV,
- Link Identical Mesh Data,
- Strip Collider Render Data,
- width-aware wrapped help/result text,
- Blender 4.2+ Extensions packaging,
- runtime validation on Blender 4.2 LTS, 4.5 LTS and 5.2 LTS.

## Engine priority showcase

- **P0 - Unity:** keep deepening existing buttons, recovery, reports and safe project cleanup.
- **P0 - Blender 4.2+:** keep improving Remesh fidelity, LOD/collider quality, lightmap preparation and export readiness.
- **P1 - Godot 4.x:** first new game-engine integration after Unity, focused on import, scene and asset optimization jobs.
- **P2 - Unreal Engine 5.x:** Editor plugin focused on safe texture, static-mesh, collision and project optimization jobs.
- **P3 - Flax / Stride / other engines:** evaluate only after the shared cross-engine layer is proven.

## Language priority showcase

### P0 - parity across current integrations

- Auto detect
- English
- Japanese
- Simplified Chinese
- Traditional Chinese
- Korean
- Spanish
- French
- German
- Portuguese
- Russian
- Italian

Unity already exposes this set. Blender parity is the next localization job.

### P1 - next language expansion

- Dutch
- Polish
- Turkish
- Ukrainian
- Czech
- Indonesian
- Hindi

### P2 - broader coverage

- Thai
- Vietnamese
- Swedish
- Norwegian
- Danish
- Finnish
- Romanian
- Hungarian

### P3 - layout-sensitive languages

- Arabic with tested right-to-left layout
- Hebrew with tested right-to-left layout

A language should not be marked complete until primary buttons, warnings, confirmations, results and update messages are covered.

## Existing-button upgrade priorities

### Unity

- **P0 - Optimize Textures:** better changed/preserved/avoided-override reporting and safer recognized data-texture handling.
- **P0 - Optimize Model Imports:** better unsupported/import-history summaries and evidence-based Read/Write reduction only when runtime modification can be ruled out.
- **P0 - Optimize Particles:** add safe emission-rate review and clearer expensive-module summaries without rewriting authored curves.
- **P0 - Fix Material Costs:** add before/after reference-count estimates and stronger exact-duplicate evidence.
- **P0 - Optimize Lighting:** split scene preparation from bake start so users can prepare without immediately baking.
- **P0 - Clean Missing Scripts:** improve prefab-stage and nested-prefab reporting.
- **P0 - Optimize UI Raycasts:** continue TextMeshPro-aware and nested-interaction safety improvements without hard package dependencies.
- **P0 - Unused Asset Cleanup:** add optional exportable dry-run reports and stronger dynamic-loader detection while keeping permanent deletion conservative.
- **P1 - Build evidence:** shader/build-waste cleanup only when player/build evidence proves the change is safe.
- **P1 - Packaging diagnostics:** asset-loading, duplicate-content and packaging review with guarded fixes.

### Blender

- **P0 - One-Click Remesh:** improve blendshape, armature-weight, normal, seam and hard-edge transfer fidelity.
- **P0 - Create LODs:** configurable LOD ratios with safe defaults, stronger collection organization and output naming.
- **P0 - Collision Proxy:** independent collider triangle target and stronger export-oriented cleanup.
- **P0 - Generate Lightmap UV:** better packing efficiency while preserving non-overlap and existing secondary UV data.
- **P0 - Link Identical Mesh Data:** preview exact duplicate groups and estimated mesh-data savings before linking.
- **P1 - Optimize Material Slots:** remove only truly unused material slots with explicit index remapping and Undo.
- **P1 - Static Mesh Optimize Selection:** coordinate proven static-mesh actions without duplicating their implementations.
- **P1 - Build Game LOD Package:** generate LODs, optional collider, optional LightmapUV and organized output collections in one confirmed action.
- **P1 - Export preparation:** portable Unity, Godot and Unreal metadata without silently rewriting engine-specific project settings.

## Version roadmap

### v0.7.66 - Current integration polish

**Primary priority: P0**

- Blender language parity with the current Unity language set.
- Unity lighting prepare-only path.
- richer per-action before/after summaries,
- unused-asset cleanup dry-run export,
- Blender configurable LOD ratios and collider target,
- Remesh transfer-quality diagnostics,
- Lightmap UV packing improvements.

### v0.7.7 - Godot 4.x preview

**Primary priority: P1**

- initial Godot 4.x EditorPlugin,
- safe imported texture review and limits,
- static mesh and scene review,
- selected-node optimization for proven safe properties,
- missing/broken external-resource diagnostics without automatic deletion,
- Blender export-preparation path for Godot LOD/lightmap/collider assets,
- shared result-summary and localization conventions.

### v0.7.8 - Unreal Engine 5.x preview

**Primary priority: P2**

- initial Unreal Editor plugin,
- texture import and maximum-size review,
- static-mesh LOD/import configuration where the active Unreal version exposes safe Editor APIs,
- collision-complexity and static-mesh preparation review,
- exact duplicate material/asset diagnostics where identity can be proven,
- Blender export-preparation path for Unreal,
- no automatic project-wide Nanite, shader or rendering changes without version-specific validation.

### v0.8 - Shared multi-engine beta

**Primary priority: P1 + P2**

- shared optimization-result schema across integrations,
- shared warning/severity language,
- shared configuration definitions so Balanced/Mobile/VR mean the same class of safe changes,
- common localization keys and coverage checks,
- recovery/Undo requirements for every integration,
- CI coverage expanded to every integration that can be validated headlessly,
- measured savings shown where memory, asset count, material references or geometry reductions can be calculated reliably.

### v0.9 - Release-quality automation

**Primary priority: P0**

- recovery and conflict handling for every destructive or metadata-changing batch,
- project-wide dry-run summaries before large batches,
- stronger import-history conflict detection across engines,
- translation completeness checks,
- remove overlapping actions that do not provide a distinct outcome,
- evaluate P3 engine candidates only if Unity, Blender, Godot and Unreal work is stable.

### v1.0 - Stable cross-engine release

**Primary priority: P0**

- a small set of dependable one-click workflows rather than a huge toolbox,
- at least 90% coverage of the published safely automatable task inventory for every integration declared stable,
- Unity and Blender treated as mature core integrations,
- Godot promoted to stable if its automation and recovery meet the same standard,
- Unreal promoted only if version-specific regression coverage and recovery are dependable,
- consistent Auto language detection and translation coverage across maintained integrations,
- clear supported-version policy for every engine and DCC,
- no duplicate buttons that perform the same outcome,
- no automatic deletion of ambiguous project content,
- source-preserving, Undo-backed or restore-backed behavior wherever practical.

## Post-1.0 candidates

**Priority: P3**

- evaluate Flax Engine integration,
- evaluate Stride integration,
- community translation contribution workflow,
- optional command-line/headless optimization reports for CI,
- engine-neutral asset-preparation reports for teams using more than one engine.

## Admission rules

A new optimization action should only ship when it has:

- a distinct outcome,
- a real repetitive manual job to replace,
- clear supported inputs,
- a recovery route,
- regression coverage,
- no safer existing button that should simply be extended instead.

A new engine integration should only become stable when it has:

- version-specific compatibility rules,
- automated or repeatable regression testing,
- recovery or Undo for every change where the host supports it,
- the shared result-summary behavior,
- localization coverage for the maintained language set,
- at least one genuinely useful one-click workflow rather than only reports or navigation helpers.
