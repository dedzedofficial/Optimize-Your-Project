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
- **P2 - Medium priority:** new integrations or deeper automation that require more validation before becoming default behavior.
- **P3 - Later / experimental:** useful ideas that should not delay the core Unity, Blender, Godot and Unreal work.

## Current baseline: v0.7.61

### Unity

- texture optimization and import repair,
- model-import compression and mesh import optimization,
- particle limits including Constant and Two Constants lifetime caps,
- safe material-cost fixes,
- baked-light setup,
- guarded realtime-shadow disabling,
- missing-script cleanup,
- UI raycast optimization,
- project and character review tools,
- importer history, protection, trial and restore infrastructure,
- automatic interface-language detection,
- unified project update checking.

### Blender 4.2+

- One-Click Remesh with guarded UV, material and deformation preservation,
- LOD0 / LOD1 / LOD2 generation,
- optional collision proxy from LOD2,
- generated-output reuse and manual-edit protection,
- Generate Lightmap UV,
- Link Identical Mesh Data,
- Strip Collider Render Data,
- Blender 4.2+ Extensions packaging,
- runtime validation on Blender 4.2 LTS, 4.5 LTS and 5.2 LTS.

## Integration priority showcase

| Priority | Integration | Goal |
| --- | --- | --- |
| **P0** | Unity | Keep the existing compact one-click workflow stable and deepen every useful button. |
| **P0** | Blender 4.2+ | Improve Remesh, LOD, lightmap, collision and static-mesh workflows without rebuilding the old cluttered panel. |
| **P1** | Godot 4.x | First new game-engine integration after Unity, focused on import, scene and asset optimization jobs. |
| **P2** | Unreal Engine 5.x | Editor plugin focused on safe asset, texture, static-mesh and project optimization jobs. |
| **P3** | Flax / Stride and other engines | Evaluate only after the shared cross-engine layer is proven and the engine exposes safe automation APIs. |

## Language priority showcase

The long-term goal is for every maintained integration to share the same language list and use **Auto** language detection where the host application exposes locale information.

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

No language should be marked supported until the important buttons, warnings, confirmation dialogs, result summaries and update messages are covered.

## Existing-button upgrade priorities

### Unity - Optimize Textures

- **P0:** preserve stricter existing platform limits and explicit formats.
- **P0:** report which textures changed, which were already safe and which overrides were intentionally preserved.
- **P1:** detect textures that can safely use a smaller cap without ever upscaling smaller sources.
- **P1:** improve recognized normal-map and data-texture import repair while preserving artistic settings.
- **P2:** target-aware one-click configurations for desktop, mobile, standalone VR and general balanced projects.

### Unity - Optimize Model Imports

- **P0:** preserve stronger existing mesh-compression settings instead of weakening them to the selected level.
- **P0:** improve reporting for unsupported meshes, source packages and manually protected imports.
- **P1:** safe secondary-UV preparation when the owning workflow requires lightmaps.
- **P1:** optional Read/Write reduction only when the tool has strong evidence the mesh is not modified at runtime.
- **P2:** build-target-aware import configuration without touching rigs, animations or blendshapes unless an owning action explicitly handles them.

### Unity - Optimize Particles

- **P0:** keep Constant and Two Constants lifetime handling safe and fully summarized.
- **P1:** add guarded emission-rate review and caps without rewriting authored curves automatically.
- **P1:** improve renderer-cost handling for shadows, trails, lights and expensive modules.
- **P2:** one-click particle configurations for mobile, desktop and VR with a preview of exactly what each configuration will change.

### Unity - Fix Material Costs

- **P0:** keep exact-state duplicate remapping and safe empty-slot cleanup reliable.
- **P1:** report estimated renderer/material-reference reductions before applying fixes.
- **P1:** detect material instances that differ only by safely mergeable state without merging automatically until the match is proven.
- **P2:** shader keyword and build-waste cleanup using build evidence rather than guesses.

### Unity - Optimize Lighting

- **P0:** add a stronger preflight summary before changing static flags, UV import settings or starting a bake.
- **P0:** clearly separate changed lights, changed renderers, generated UV imports and skipped dynamic objects.
- **P1:** add a safe lighting-preparation action that can stop before baking for users who only want scene setup.
- **P2:** target-aware lighting recommendations for mobile, desktop and VR without replacing custom lighting design.

### Unity - Clean Missing Scripts

- **P0:** add a preview count before removal on large scenes and hierarchies.
- **P1:** improve nested-prefab and prefab-stage reporting so users know exactly what is editable.
- **P1:** add selection-only and loaded-scene configurations while keeping Undo support.

### Unity - Optimize UI Raycasts

- **P0:** expand interactive-control detection without taking unnecessary package dependencies.
- **P1:** improve CanvasGroup, nested interaction and TextMeshPro-aware safety checks when those packages are present.
- **P1:** report changed canvases and graphics rather than only a total count.
- **P2:** add safe UI rendering-work checks that remain separate from layout or visual-design changes.

### Blender - One-Click Remesh

- **P0:** continue improving blendshape, armature-weight, UV and material-transfer fidelity.
- **P0:** add clearer warnings when a source cannot be reproduced accurately enough for automatic transfer.
- **P1:** improve normal, seam and hard-edge preservation where topology changes allow it.
- **P1:** add a quality comparison summary showing source triangles, output triangles and transferred-data coverage.
- **P2:** optional quality-focused and reduction-focused configurations using the same Remesh button rather than duplicate tools.

### Blender - Create LODs

- **P0:** configurable LOD ratios with sensible defaults and source-safe reuse.
- **P0:** improve collection organization and output naming.
- **P1:** optional independent collider triangle target rather than always copying LOD2 exactly.
- **P1:** optional automatic LightmapUV generation for created static LODs.
- **P1:** export-friendly LOD metadata for supported engines.

### Blender - Generate Lightmap UV

- **P0:** improve packing efficiency while keeping non-overlap and source UV protection.
- **P1:** batch generation for selected static assets and generated LOD collections.
- **P1:** configurable padding based on intended lightmap resolution.
- **P2:** engine-aware validation for Unity, Godot and Unreal export workflows.

### Blender - Link Identical Mesh Data

- **P0:** add a preview of exact duplicate groups before linking.
- **P1:** show estimated mesh-data memory savings.
- **P1:** add a safe unlink selected action for artists who later need unique edits.

### Blender - Strip Collider Render Data

- **P0:** keep the action restricted to verified generated collision proxies.
- **P1:** optionally simplify collision geometry to a separate triangle target.
- **P1:** remove additional render-only attributes only when they are proven unnecessary for collision.

## New one-click configuration priorities

These are orchestration buttons, not another preset system. Each configuration should call existing tested jobs, show the planned changes, and keep the owning buttons available individually.

### P1 - Unity

- **Optimize Loaded Scene:** coordinates safe scene-scope material, particle, UI, missing-script and lighting-preflight jobs.
- **Optimize Selected Hierarchy:** runs only supported safe actions against the selected object hierarchy.
- **Prepare Static Environment:** coordinates static-mesh import checks, material cleanup, lightmap preparation and lighting preflight.
- **Optimize Character:** coordinates the current Character page actions while avoiding world-only lighting/static changes.
- **Prepare for Mobile:** applies only the mobile-safe texture, particle and rendering limits that the user previews first.

### P1 - Blender

- **Static Mesh Optimize Selection:** coordinates safe material-slot cleanup, duplicate-data review, LightmapUV and optional LOD preparation.
- **Build Game LOD Package:** creates LODs, optional collider, optional lightmap UVs and organized output collections in one confirmed action.
- **Prepare Static Prop:** runs non-destructive static-prop checks and only applies the user-approved safe fixes.
- **Prepare Collision Proxy:** creates or updates a collider, strips render-only data and optionally simplifies it to the chosen target.

### P2 - Cross-engine

- **Prepare for Unity**
- **Prepare for Godot**
- **Prepare for Unreal**

These should write only portable/export metadata and prepare assets. They should not silently rewrite engine-specific project settings from Blender.

## Version roadmap

## v0.7.62 - Existing tools first

**Primary priority: P0**

- Unity model-import preservation improvements.
- Unity texture result reporting and override accounting.
- Unity lighting preflight and safer no-bake setup path.
- Unity particle and UI safety improvements.
- Blender Optimize Material Slots with explicit index remapping and Undo.
- Blender LOD ratio and collection improvements.
- Blender collider simplification target.
- Blender Remesh transfer diagnostics and fidelity work.
- Blender batch LightmapUV improvements.
- Blender language parity with the current Unity language set plus Auto detection where Blender exposes the locale.

## v0.7.63 - One-click configurations

**Primary priority: P1**

- Unity Optimize Loaded Scene.
- Unity Optimize Selected Hierarchy.
- Unity Prepare Static Environment.
- Unity Optimize Character orchestration.
- Blender Static Mesh Optimize Selection.
- Blender Build Game LOD Package.
- Blender Prepare Static Prop.
- Shared result-summary format for orchestration actions.
- P1 language expansion begins across Unity and Blender.

## v0.7.64 - Godot 4.x preview

**Primary priority: P1**

- Initial Godot 4.x EditorPlugin integration.
- Optimize imported texture settings with source-safe limits.
- Static mesh and scene review tools.
- One-click selected-node optimization for proven safe properties.
- Missing/broken external-resource diagnostics without automatic deletion.
- Blender export metadata path for Godot LOD, lightmap and collider preparation.
- Shared localization and result-summary framework reused from Unity/Blender.

## v0.7.65 - Deeper current-engine automation

**Primary priority: P0 + P1**

- More measurable Unity material/rendering savings.
- Better build-evidence-driven Unity shader cleanup.
- Improved Unity asset-loading and packaging diagnostics.
- Blender Remesh quality comparison and transfer-coverage results.
- Blender stronger lightmap packing and collision workflows.
- Godot preview fixes based on real project testing.
- Continue P1 language expansion.

## v0.7.7 - Unreal Engine 5.x preview

**Primary priority: P2**

- Initial Unreal Editor plugin integration.
- Texture import and maximum-size optimization review.
- Static-mesh LOD/import configuration where the active Unreal version exposes safe editor APIs.
- Collision complexity and static-mesh preparation review.
- Exact duplicate material/asset diagnostics where identity can be proven.
- Blender export metadata path for Unreal LOD and collider preparation.
- No automatic project-wide Nanite, shader or rendering changes without explicit version-specific validation.

## v0.7.8 - Shared cross-engine core

**Primary priority: P1 + P2**

- Shared optimization result schema across integrations.
- Shared priority/severity language for warnings and skipped work.
- Shared configuration definitions so "Prepare for Mobile" means the same class of safe changes across supported engines.
- Common localization keys and translation coverage checks.
- Recovery/Undo requirements for every integration.
- CI coverage expanded to every engine integration that can be validated headlessly.

## v0.8 - Multi-engine beta

**Primary priority: P1**

- Unity and Blender remain stable integrations.
- Godot moves from preview toward supported beta after regression coverage is proven.
- Unreal remains preview/beta until editor automation is equally recoverable and testable.
- One selection-based orchestration route per stable integration.
- Target-aware desktop, mobile and VR configurations built from existing safe actions.
- Measured savings shown where memory, asset count, material references or geometry reductions can be calculated reliably.

## v0.9 - Release-quality automation

**Primary priority: P0**

- recovery and conflict handling for every destructive or metadata-changing batch,
- performance/result evidence where it can be measured reliably,
- project-wide dry-run summaries before large batches,
- stronger import-history conflict detection across engines,
- translation completeness checks,
- remove overlapping actions that do not provide a distinct outcome,
- evaluate P3 engine candidates only if Unity, Blender, Godot and Unreal work is stable.

## v1.0 - Stable cross-engine release

**Primary priority: P0**

- a small set of dependable one-click workflows rather than a huge toolbox,
- at least 90% coverage of the published safely automatable task inventory for every integration declared stable,
- Unity and Blender treated as mature core integrations,
- Godot promoted to stable if its automation and recovery rules meet the same standard,
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
- evaluate additional creation platforms only where editor automation APIs allow safe, testable actions,
- shared community translation contribution workflow,
- optional command-line/headless optimization reports for CI pipelines,
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

Reports, navigation helpers and duplicated wrappers do not count as optimization coverage.