# Optimize Your Project: development roadmap

<img src="../Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" alt="Optimize Your Project logo" width="96">

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

Open the [GitHub Releases](https://github.com/dedzedofficial/Optimize-Your-Project/releases) page and download:

```text
optimize-your-project-blender-0.7.4.zip
```

Then in Blender use **Edit > Preferences > Add-ons > Install...** or **Get Extensions > Install from Disk**.

### VRChat Creator Companion / VCC

Use [Add Optimize Your Project to VCC](vcc://vpm/addRepo?url=https%3A%2F%2Fdedzedofficial.github.io%2FOptimize-Your-Project%2Findex.json), then add **Optimize Your Project** to the chosen project.

</details>

> **New here?** Start with the [Overview](../README.md). You can read the complete documentation directly on GitHub before installing anything.


**Current implementation: v0.7.4. Future versions below are planned, not available features.**

## The v1.0 goal

- **Put at least 90% of identified, safely automatable optimization tasks one button away on every supported integration and target platform.**
- Cover everyday game, app, simulation, asset-production, desktop, mobile, web and XR development.
- Give beginners clear buttons that explain what they do and experienced developers quick access to the same jobs.
- Make useful help immediately actionable: find the problem, select the affected item, apply a supported fix, or restore the previous result.
- Keep the product free, focused on optimization, and useful without any VR or social-platform SDK.
- Treat broad platform coverage as a development goal. The roadmap does not claim that every engine, device or optimization is already supported.

## What one click should mean

- Choose the object, folder, hierarchy, collection or project scope, then press one clearly named action.
- Use sensible automatic settings without requiring presets, a configuration page or repeated inspector edits.
- Offer a compact optional preview when quality or appearance may change. After approval, process the whole selected scope together.
- Show only relevant tools for the detected integration and chosen build target.
- Keep detailed diagnostics behind an explicit scan button.
- Report **Changed**, **Unchanged**, **Skipped**, **Unsupported** and **Failed**, with reasons and direct links where useful.
- Provide **Undo Last Optimization**, a checked settings restore, or an untouched source copy as appropriate.
- Avoid claiming that one button can decide art direction, rewrite arbitrary gameplay code, or guarantee an FPS increase.

## Platform coverage goal

- **Editor integrations:** Unity and Blender first, followed by native Godot and Unreal tools.
- **Build targets:** Windows, macOS, Linux, Android, iOS, web and standalone or PC-connected XR where the integration supports those targets.
- **Creator workflows:** optional VRChat/VCC, ChilloutVR and Resonite preparation tools alongside ordinary project workflows.
- **Console workflows:** investigate and document support where licensed SDK access, editor APIs and test hardware permit it. Do not advertise unverified support.
- **Other engines and DCC tools:** maintain a public request list for additions such as Maya and 3ds Max. Publish an integration's supported tasks before counting it toward coverage.
- **Support tracking:** distinguish implemented, tested, experimental, planned and unavailable combinations. One working desktop integration must not imply support everywhere.

## v0.7: reliable everyday buttons

### v0.7.0: one-click foundation | Implemented

- Unity **Project** and **Character / Avatar** pages.
- Direct texture compression/size, particle, model compression and realtime shadow actions.
- Detailed findings shown only after a project scan.
- Blender remesh and duplicate-vertex actions that create copies.
- Advanced Blender triangle reduction, join/atlas and static LOD tools.
- Compact update status and optional developer-support links.

### v0.7.1: clean selected mesh | Implemented

- Blender **Clean Selected Mesh**, with unique output names and an untouched original.
- Exact-coordinate vertex merging, loose geometry and zero-area face cleanup, unused material slot cleanup and closed-surface normal repair.
- Conservative checks for topology-sensitive inputs and rollback after cleanup failure.
- Consistent Unity batch and Blender quick-action completion summaries.
- Blender regression checks for source preservation, repeated cleanup, materials/UVs and existing quick actions.
- Synchronized package and add-on versions. Unity editor validation remains required before release tagging.

### v0.7.2 and v0.7.3: planning folded into v0.7.4 | Superseded

The selection, texture-review and usability ideas planned for these patch numbers were consolidated into the larger v0.7.4 release instead of publishing two smaller intermediate versions.

### v0.7.4: searchable, multilingual batch workflow | Implemented

- Added English, Japanese, Simplified Chinese and Korean interface support in Unity and Blender.
- Added a persistent Unity language preference and Blender scene language selector.
- Added Unity action search so texture, mesh, particle, light, memory and scan jobs are easier to reach.
- Added Unity **Use Current Selection** for Project-folder scope.
- Added **Show Largest Textures** for quick high-resolution texture review.
- Added **Review Read/Write Memory** for readable textures and imported models without automatically disabling settings that may be required at runtime.
- Added **Find Oversized Meshes** for high-triangle loaded-scene or character geometry with triangle, vertex, submesh and material-slot counts.
- Added **Fix Texture Import Settings** for conservative normal-map and non-color mask/data texture import corrections.
- Added **Find Duplicate Materials** by comparing shader state and saved material properties.
- Added **Clean Unused Material Slots** for trailing empty renderer slots beyond the mesh's submesh count, with Undo support. Non-empty extra materials are preserved.
- Added **Find Expensive Material Setups** for high material-slot and submesh-count renderers.
- Added Blender **Clean Selected Meshes** for copy-based batch cleanup.
- Added Blender **Create Game-Ready Copy** for source-preserving static mesh preparation with optional modifier application, applied rotation/scale, cleanup and unused material-slot removal.
- Added Blender **Create LODs for Selection** using the guarded static-mesh LOD path.
- Added Blender **Show Heavy Meshes** with a configurable triangle threshold.
- Expanded static release validation and Blender runtime regression coverage for the new batch and language features.
- Kept detailed scans optional and source-preservation behavior explicit.

### v0.7.5: helpful fixes within reach | Planned

- **Find Missing References:** open the next broken asset, component or object reference.
- **Find Missing Textures:** select materials with unresolved image inputs and offer verified replacement candidates.
- **Show Optimization Help:** explain the selected action, affected scope and restoration route in plain language.
- Add a searchable action panel so a developer can type a task and run its matching button.
- Apply only unambiguous fixes automatically; show uncertain matches for review.

## Language roadmap

v0.7.4 starts with **English, Japanese, Simplified Chinese and Korean**. New languages should be added only when the visible UI, critical warnings and release documentation can be reviewed together.

- **v0.8.x target:** Spanish, French and German.
- **v0.8.x later target:** Brazilian Portuguese, Italian and Traditional Chinese.
- **v0.9.x target:** Polish, Turkish and Russian, followed by additional community-requested languages.
- Keep English as the fallback language for missing translation keys.
- Add pseudo-localization and layout-overflow checks before v1.0 so long translations do not break compact Editor panels.
- Allow community translation corrections through small, reviewable language-table changes instead of requiring code rewrites.

## v0.8: broader optimization coverage

### v0.8.0: scene effects and lighting | Planned

- **Optimize Selected Effects:** batch supported particle limits and costly optional modules within a chosen hierarchy.
- **Review Realtime Shadows:** group expensive shadow candidates and apply the approved change together.
- **Find Expensive Lights:** select overlapping or high-cost candidates with an explanation.
- **Prepare Lighting Checks:** navigate objects missing suitable lightmap setup without guessing the intended lighting design.
- Keep scene changes reversible and preserve intentional effect quality.

### v0.8.1: materials and draw calls | Planned

- Expand the v0.7.4 duplicate-material review into **Consolidate Approved Materials** with a recorded restoration path.
- Expand the v0.7.4 material-cost review with shader-pass and pipeline-aware analysis where reliable.
- **Check Instancing and Batching:** find eligible candidates and apply only verified compatible changes.
- Add project-wide prefab and asset material-slot cleanup only where usage can be proven safely.
- Keep the v0.7.4 loaded-scene and character material tools available as the fast everyday path.

### v0.8.2: physics, animation and visibility | Planned

- **Create Simple Collider Copies:** offer suitable primitive or simplified collider candidates for static props.
- **Review Collision Cost:** find expensive collision meshes and unnecessary candidates without changing gameplay rules silently.
- **Optimize Animation Imports:** batch reviewed keyframe/compression settings where visual checks are available.
- **Set Up LOD Groups:** connect supported generated LODs and provide a quick preview.
- **Prepare Visibility Optimization:** check culling bounds, occlusion candidates and relevant editor setup.

### v0.8.3: Godot integration preview | Planned

- Add a native Godot action panel using the same simple labels and outcome summaries.
- Start with selected texture import/compression and supported mesh import jobs.
- Add **Find Missing Resources** and **Show Heavy Assets** navigation helpers.
- Record original import settings and provide a supported restore action.
- Publish tested Godot versions and desktop/mobile/web target coverage before describing this integration as stable.

### v0.8.4: Unreal integration preview | Planned

- Add a native Unreal editor action panel with selection-based scopes.
- Start with reviewed texture-size/compression and static-mesh LOD jobs.
- Add **Review Collision Cost** and **Check Nanite Eligibility** for applicable assets and targets.
- Add **Find Missing Assets** and **Show Heavy Assets** navigation helpers.
- Publish tested Unreal versions and target restrictions; use Unreal's own asset and editor APIs.

### v0.8.5: exports and platform preparation | Planned

- **Prepare for Target:** apply the approved, supported actions for the selected desktop, mobile, web or XR target.
- **Prepare FBX / GLB Export:** check Blender materials, textures, names and supported geometry before export.
- **Save Atlas Files:** write generated atlas images and maintain valid material references.
- **Check Platform Compatibility:** select incompatible formats or settings and explain supported fixes.
- Publish the first measured coverage report for each integration and target, including remaining gaps.

## v0.9: complete common workflows

### v0.9.0: one-button optimization passes | Planned

- **Optimize Selection:** run the relevant supported jobs in one pass after scope and quality-sensitive choices are approved.
- **Optimize Project Assets:** batch the supported asset-import tasks with progress, cancellation and per-item recovery.
- **Optimize Scene / Collection:** combine relevant mesh, material, effects and scene jobs for the selected scope.
- Avoid duplicate processing, repeated reimports and hidden whole-project changes.
- Expand Godot and Unreal beyond previews only as their integration tests and restoration paths pass.

### v0.9.1: character and creator-platform helpers | Planned

- **Check Character Cost:** collect mesh, material, texture, effects and supported platform-budget findings.
- **Optimize Character Assets:** apply supported texture/material/import jobs while preserving rigs, shape keys and required components.
- **Prepare for VRChat**, **Prepare for ChilloutVR** and **Prepare for Resonite:** expose tested preparation tasks through optional integration buttons.
- **Open Creator Tools:** launch the correct installed setup or package-management route where supported.
- Keep all social-platform dependencies optional and report unsupported cases explicitly.

### v0.9.2: the help button becomes a toolbox | Planned

- **Help Me Reduce Memory:** show measured or clearly labeled estimated memory candidates and run supported fixes.
- **Help Me Reduce Draw Calls:** find material, instancing and mesh candidates with one-button access to approved actions.
- **Help Me Find the Slow Part:** open the relevant profiler or analysis view and select supported findings.
- **Help Me Prepare a Build:** check target settings, dependencies and known compatibility issues.
- **Explain This Issue** and **Show Me Where:** give a short explanation and select the exact affected item.
- Make common help tasks accessible from one search field or a small set of clear buttons.

### v0.9.3: build size, loading and asset dependencies | Planned

- **Show Build Size Contributors:** use actual build reports where available to rank included content.
- **Review Unused Assets:** identify candidates while accounting for dynamic and indirect references.
- **Apply Approved Asset Exclusions:** adjust supported packaging rules with a restore record; never delete assets merely because a scan found no reference.
- **Review Loading Settings:** offer supported import, streaming and packaging changes with their trade-offs explained.
- Close high-impact coverage gaps across Unity, Blender, Godot and Unreal before adding less common tasks.

### v0.9.4: compare, restore and finish platform gaps | Planned

- **Compare Before / After:** show measured asset/build changes and comparable runtime results where captured.
- **Restore Selected Batch:** restore a chosen optimization run after checking for conflicting later edits.
- **Retry Failed Items:** rerun only suitable failed candidates with clear failure reasons.
- Validate the same workflows across supported editor host systems and build-target combinations.
- Publish a task-by-task gap list for every integration below the 90% target.

### v0.9.5: v1.0 release candidate | Planned

- Reach at least 90% verified one-click coverage for each declared stable integration and target, not just a combined project-wide percentage.
- Finish missing common tasks from the published inventory before treating the target as met.
- Test clean installation, upgrades, large batches, cancellation, repeated runs and restoration.
- Check beginner usability: common actions must be findable and understandable without reading a long manual.
- Keep incomplete integrations marked experimental with their coverage visible. Do not hide them to make the overall goal look complete.

## v1.0.0: everyday optimization, one button away | Target

- **Optimize Selection**, **Optimize Project Assets** and **Prepare for Target** cover the verified routine jobs relevant to the chosen scope.
- At least 90% of identified, safely automatable tasks are available through a single action in every declared stable integration and target.
- Useful help is one button away: find, explain, select, fix supported issues, compare results and restore changes.
- Unity, Blender, Godot and Unreal each have a documented capability list and native workflow; unavailable platform combinations remain clearly listed as gaps.
- Quality-sensitive actions provide a compact review, while repeatable approved jobs run together without repeated manual setup.
- Publish coverage, compatibility and test results alongside the release so developers can see what the toolkit can actually do.
- Keep the package free and continue expanding platform support and task coverage after v1.0.

## How the 90% goal will be measured

- **Count tasks, not buttons:** putting ten existing buttons behind one menu does not create ten new optimizations.
- **Publish the inventory:** give each distinct task a purpose, integration, target applicability, safety conditions, expected result and verification method.
- **Measure per integration and target:** coverage is verified one-action tasks divided by all identified safely automatable tasks applicable to that combination.
- **Count only working behavior:** a placeholder, diagnostic-only report or button that merely opens a manual workflow does not count as an automated optimization.
- **Track helpers separately:** navigation and explanation buttons are valuable, but they do not inflate the optimization percentage.
- **Keep unsupported tasks visible:** suitable tasks waiting on implementation or testing remain uncovered. Document genuinely inapplicable tasks and why they are excluded.
- **Keep the inventory honest:** record additions and scope changes publicly. Do not split simple jobs into multiple entries or discard difficult tasks to improve the score.
- **Require evidence:** verify the intended change, source preservation/restoration and safe repeated execution before marking a task complete.
- **Publish the remaining 10%:** explain which jobs need specialist judgment, restricted tooling or further development.
- **No performance-percentage promise:** 90% task coverage does not mean a 90% improvement in frame rate, memory or build size.

## Release standards

- Match package, add-on, update-feed and release-tag versions.
- Compile and test in the declared supported editor versions.
- Test each integration using its own APIs and representative projects.
- Preserve originals, record recoverable settings or use Undo as appropriate.
- Check cancellation, failure recovery and unchanged second runs.
- Preserve unsupported or topology-sensitive content and explain skipped work.
- Keep UI controls compact, button labels specific and detailed scans optional.
- Label new capabilities as planned or experimental until their implementation is verified.
- Keep historical Unity package and internal type names compatible while presenting **Optimize Your Project** consistently to users.
