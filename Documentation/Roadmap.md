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

The Blender build now produces two real ZIP packages:

- **Blender 4.2+ / Blender Extensions:** `optimize-your-project-blender-extension-0.7.4.zip`
- **Blender 3.6 legacy add-on:** `optimize-your-project-blender-0.7.4.zip`

[![DOWNLOAD BLENDER ZIP BUILDS](https://img.shields.io/badge/DOWNLOAD%20BLENDER-ZIP%20BUILDS-EA7600?style=for-the-badge&logo=blender&logoColor=white)](https://github.com/dedzedofficial/Optimize-Your-Project/actions/workflows/release-checks.yml)

Open the latest successful **Check release packages** run and download the `optimize-your-project-blender-0.7.4` artifact. It contains both ZIP files. Use the **extension** ZIP for `extensions.blender.org`. The official Blender Extensions listing will replace this temporary download button after publication.

The legacy ZIP also remains available from [GitHub Releases](https://github.com/dedzedofficial/Optimize-Your-Project/releases) when a matching Blender release is published.

### VRChat Creator Companion / VCC

Use [Add Optimize Your Project to VCC](vcc://vpm/addRepo?url=https%3A%2F%2Fdedzedofficial.github.io%2FOptimize-Your-Project%2Findex.json), then add **Optimize Your Project** to the chosen project.

</details>

> **New here?** Start with the [Overview](../README.md). You can read the complete documentation directly on GitHub before installing anything.


**Current implementation: v0.7.4. Revised direction: 3 October 2026. All future milestones are plans, not shipped features.**

## Direction

Make repetitive optimization jobs a selection and one clearly named button. Grow through distinct, useful outcomes rather than more remesh, LOD or texture-compression variants. Improve an existing action before adding another action that reaches the same result.

New means new to this toolkit. This roadmap does not claim these techniques have never been implemented elsewhere. Native editor functions should be reused; a wrapper belongs here only when it removes meaningful repeated work, handles a batch correctly or supplies recovery and verification.

Unity and Blender remain the supported integrations. Stabilize these before adding engines. Blender remains focused on Remesh and LOD until a separate new workflow proves useful and reliable. Do not restore previously removed experimental mesh cleanup, atlas or Game-Ready tools simply to fill the roadmap.

## Existing capability baseline

| Area | Current v0.7.4 behavior | Future ownership |
| --- | --- | --- |
| Unity textures | Compression/size caps, recognized normal/data import fixes, largest-texture and Read/Write review | One texture workflow; new import corrections extend it |
| Unity meshes | Model compression; oversized import fix adds vertex/polygon import optimization without reducing topology | One model-import workflow; compression and triangle reduction are different outcomes |
| Unity materials | Exact duplicate reference remapping, trailing empty renderer-slot cleanup, combined safe material fix | One material workflow with shared collectors |
| Unity effects/lights | Particle limits and disabling realtime shadows | Improve these actions internally; no duplicate default buttons |
| Unity review | Project scan, character review, category findings, search and selection scope | One findings system and the existing search field |
| Blender geometry | Copy-based remesh, active-object and selected-object LOD generation | Remesh plus one LOD workflow with automatic selection scope |
| Shared workflow | Outcome summaries, languages, source preservation and update checks | Extend shared infrastructure rather than copy it |

Review helpers are useful but do not count as automated optimizations. Remesh changes topology, LOD creates alternate meshes, and importer compression changes stored data; do not merge them as though they were interchangeable.

## v0.7.5: consolidate before expanding | Planned

- **Materials:** make the existing combined safe material fix the primary action. Move its two component actions into optional details; keep one implementation for each operation. Preserve duplicate assets and intentional extra material passes.
- **Model imports:** replace competing compression and oversized-import entry points with one primary **Optimize Model Imports** workflow. Retain compression-only access in details. Describe exactly what changes; never suggest that compression removes triangles.
- **Blender LODs:** expose one **Create LODs** button that uses the active object or selected supported objects automatically. Reuse the existing guarded implementation and preserve sources.
- **Textures:** retain compression/size and import correction as distinct operations inside one compact section. They solve different problems; avoid a second generic image-compression feature.
- **Reviews:** put largest textures, readable memory and heavy meshes behind **Review** or the existing search. Reuse project and character findings rather than adding parallel report panels.
- Remove superseded controls, obsolete help and localization entries after checking callers, tests and compatibility. Keep old operator identifiers only where saved workflows need compatibility.
- Publish a task inventory mapping each outcome to one implementation and primary UI route.
- Keep the installed version at v0.7.4 until implementation and editor verification justify a release.

## v0.7.6: recovery and reliable batches | Planned

- **Restore Last Batch:** record exact importer settings before changes; restore only entries whose current state still matches that batch's output. Report conflicts instead of overwriting later edits.
- Use native Undo for scene edits and preserved source copies for Blender geometry.
- Share scope resolution, unique-asset processing, cancellation and outcome reporting across actions.
- Run an unchanged second pass without repeated reimports. Retry failed items through the existing result panel.
- These are infrastructure improvements, not additional optimization tasks or a second help toolbox.

## v0.8.0: UI rendering waste | Planned, Unity first

- **Optimize UI Raycasts:** batch-disable raycast targets only on explicitly eligible decorative graphics. Exclude controls, custom pointer handlers and uncertain runtime uses; preview uncertain candidates.
- **Optimize Hidden UI Work:** support an explicit visibility contract for selected UI roots and stop eligible offscreen rendering work through a reversible setup. Do not guess whether gameplay scripts may stop.
- Use one UI section with relevant actions; avoid a new dashboard.
- Verify input, navigation, custom events and hide/show behavior. Measure UI rendering or raycast work in representative scenes before claiming a benefit.

## v0.8.1: animation data waste | Planned, Unity first

- **Optimize Animation Data:** create recoverable import changes or clip copies for explicitly approved static-prop clips; remove redundant constant curves only when bindings and behavior remain equivalent.
- Treat reviewed clip compression as an option in this workflow, not a competing button.
- Preserve events, root motion, rig settings and required bindings. Skip humanoid, additive, procedural and unsupported clips until tested.
- Compare sampled transforms across the clip and check events before counting success.

## v0.8.2: shader build waste | Planned, Unity first

- **Reduce Shader Build Waste:** provide a reversible, pipeline-specific build rule for verified unused variant categories.
- Use actual build evidence and explicit supported rendering configurations. A material scan alone cannot prove a variant unused at runtime.
- Preserve runtime keyword changes, quality tiers, addressable content and shader warming requirements.
- Verify representative builds and rendering paths; report measured variant count, build time and build-size changes.
- Keep unsupported pipelines in review mode. Do not expose a universal strip-all button.

## v0.8.3: asset loading and packaging waste | Planned, Unity first

- **Fix Duplicate Build Inclusion:** use build reports and supported packaging metadata to find content redundantly included through Resources, scenes or addressable groups, then apply a reviewed packaging change.
- **Optimize Loading Settings:** batch only settings supported by a declared loading contract; preserve runtime access and record restoration data.
- Treat dependency analysis as part of this workflow, not a separate unused-file deletion tool.
- Never delete an asset because static references were not found. Dynamic paths and external content remain unresolved until verified.
- Measure included bytes and loading behavior before reporting savings.

## v0.8.4: collision cost | Planned

- **Create Collider Proxies:** generate separate collider candidates for explicitly selected static props and connect them through a reversible action.
- Reuse existing generated geometry where appropriate; do not introduce a second visual remesher.
- Preserve visual meshes, collision layers, triggers and gameplay intent. Skip animated, concave-sensitive and unsupported objects.
- Verify contact behavior and physics cost. Primitive proxies need a compact fit preview before applying when the shape changes.

## v0.8.5: supported draw submission improvements | Planned

- Extend the existing material workflow with **Enable Compatible Instancing** only for verified shader, pipeline and renderer combinations.
- Do not rename duplicate-material cleanup as a new draw-call optimizer; material identity alone does not guarantee fewer draw calls.
- Keep batching, instancing and dynamic material behavior distinct internally while sharing one review and result panel.
- Require a representative rendering comparison and profiler evidence. Unsupported or ambiguous candidates remain review-only.

## v0.9.0: one orchestration button | Planned

- **Optimize Selection:** coordinate already verified actions using the detected scope and explicit eligibility rules.
- Resolve conflicting settings before applying changes, deduplicate assets and reimport once where possible.
- Quality-sensitive choices use one compact preview. Approved repeatable work runs without repeated setup.
- This is a convenience entry point, not another set of implementations and not extra task coverage.
- Retain focused actions for users who need a specific outcome.

## v0.9.1: prove usefulness and remove clutter | Planned

- Measure changed settings, included bytes, animation data, shader variants or relevant profiler counters according to the task.
- Compare results under the same build target, scene and capture conditions. Label estimates and do not promise FPS improvements from asset counts.
- Remove or fold in actions with duplicate outcomes, confusing scope or no demonstrated practical value.
- Keep comparisons and restoration in the existing results panel.
- Test clean installs, upgrades, large batches, cancellation, failure recovery and repeated runs in supported Unity and Blender versions.

## v0.9.2: character compatibility | Planned

- Apply existing verified workflows to character scopes only when rigs, shape keys, events and runtime access remain intact.
- Extend the existing Character / Avatar page rather than adding a parallel character optimizer.
- Optional creator-platform checks can supply eligibility rules for the same actions.
- Do not add separate VRChat, ChilloutVR and Resonite optimization buttons that merely repeat a generic batch.

## v0.9.3: focused integration evaluation | Planned

- Evaluate Godot and Unreal only after the core workflows meet the release gates.
- Prefer unmet automation needs such as supported UI, animation, build-dependency or loading workflows over another texture compressor or LOD wrapper.
- Ship at most one experimental integration at a time, with native APIs, recovery and a published tested capability list.
- Keep an integration deferred if its proposed actions add little beyond native tools. Engine count is not a release target.
- Other DCCs, consoles and social-platform integrations remain requests until access and a distinct useful workflow are established.

## v0.9.4: localization and usability | Planned

- Review the four existing languages against the final compact UI before expanding translations.
- Add Spanish, French, German and further community languages only when critical warnings and action descriptions can be reviewed.
- Keep English fallback, test long text and ensure unsupported actions do not appear as working buttons.
- Common tasks must be understandable and reachable without reading a long manual.

## v0.9.5: release candidate | Planned

- Freeze the verified task inventory and publish each supported scope and restriction.
- Close high-value gaps before introducing more categories.
- Complete editor compilation, representative runtime checks, restore/conflict checks and packaging validation.
- Mark unfinished integrations experimental; do not inflate coverage with reports, wrappers or repeated buttons.

## v1.0.0: useful optimization without clutter | Target

- A small set of proven actions with one primary route per distinct outcome.
- One selection-based batch, relevant focused actions, optional review and recovery.
- At least 90% one-action coverage of the published, safely automatable task inventory for each declared stable integration and target.
- Count tasks, not buttons. Reports, navigation, localization, recovery and orchestration do not inflate optimization coverage.
- Publish remaining gaps and verification evidence. The 90% goal is task coverage, not a performance improvement promise.
- Keep the toolkit free and useful without a VR SDK.

## Superseded roadmap items

| Earlier proposal | Revised treatment |
| --- | --- |
| New searchable action panel | Already shipped in v0.7.4; improve the current search |
| More particle-limit and shadow buttons | Extend existing actions only when they add verified behavior |
| Several material cleanup/consolidation buttons | One primary material workflow; specialized options in details |
| Separate compression and heavy-model fix routes | One model-import workflow; explicit compression-only option |
| Active LOD and batch LOD buttons | One selection-aware LOD route |
| More remesh, decimation and image-compression variants | Deferred; improve the existing implementation instead |
| Atlas save/export preparation | Removed from this plan; current Blender has no supported atlas generator |
| Missing-reference help suite | Optional review navigation only; ambiguous repairs remain manual |
| Multiple memory/draw-call/help dashboards | Existing search and findings route to the owning action |
| Blanket target/scene/platform optimize buttons | One orchestration workflow with explicit scope and eligibility |
| Godot/Unreal texture and LOD previews | Replaced with distinct-workflow evaluation after core stability |
| Automatic unused-asset deletion or Read/Write disabling | Excluded without an explicit verified usage contract |

## Admission and release rules

- Before adding an action, identify its distinct outcome, current overlap, repeated manual work, supported inputs, recovery route and verification evidence.
- If an existing action achieves the same outcome, extend that action and retire the redundant route.
- Prefer one primary action per section. Advanced settings stay collapsed; detailed findings appear only after review.
- One click means select a scope, press an action and receive a clear result. A button that opens a manual checklist is a helper.
- Skip uncertain cases with a reason. Never conceal partial failures behind a success count.
- Reuse native editor APIs and common task implementations. Avoid speculative gameplay rewrites and automatic art-direction choices.
- Match package, add-on, update feed and release tag versions only for actual releases.
- Preserve historical package/type names where compatibility requires them.
- This update changes the roadmap and public future-development description. Runtime consolidation and new tools require implementation in their planned milestones.
