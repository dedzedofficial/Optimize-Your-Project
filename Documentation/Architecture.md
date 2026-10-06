# Optimize Your Project architecture

<img src="../Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" alt="Optimize Your Project logo" width="96">

<p align="center">
  <a href="../README.md"><strong>Overview</strong></a> |
  <a href="../Blender/README.md"><strong>Blender Guide</strong></a> |
  <a href="../Documentation/Roadmap.md"><strong>Roadmap</strong></a> |
  <a href="../Documentation/Architecture.md"><strong>Architecture</strong></a> |
  <a href="../CHANGELOG.md"><strong>Changelog</strong></a>
</p>

## Release identity

Optimize Your Project is a general developer optimization toolkit. Unity and Blender share one public release version. In v0.7.65 both integrations report **0.7.65**.

Blender support starts at **4.2** and uses the Blender Extensions system. The legacy pre-4.2 add-on path is not supported.

## Unity architecture

The repository root is a Unity Package Manager package. The Editor window is split into Project and Character / Avatar pages, but both pages now use one **Quick Optimize** area for the common workflow.

Quick Optimize coordinates the existing owning actions instead of duplicating their implementation. It runs texture, model-import, particle, material, decorative UI-raycast and missing-script jobs behind one confirmation. Lighting and realtime-shadow changes remain explicit because they can visibly alter the scene.

### Unity owning actions

- `VRTextureOptimizer` handles conservative texture caps and preserves explicit formats and stricter limits.
- `VRMeshCompression` plus the window model-import action apply Unity mesh-import optimization while preserving a stronger existing compression level.
- `VRParticleOptimizer` handles particle limits and optional module changes.
- `VRProjectMaintenance` owns exact duplicate-material reference cleanup and safe trailing empty-slot cleanup.
- `VRLightingSetup` owns baked-light preparation and bake start.
- `VRLightOptimizer` owns guarded realtime-shadow disabling.
- `VRUIRaycastOptimizer` disables decorative Raycast Target flags while preserving Selectable hierarchies, EventSystem handlers and CanvasGroup-blocked UI.
- `VRMissingScriptCleaner` removes only missing MonoBehaviour entries after a preflight count.
- `VRProjectInsights` and `VRProjectScanner` own review/report workflows.

### Import history and recovery

`VRImportHistory` stores source and importer-metadata fingerprints, per-job policies, explicit protection and recoverable last-batch metadata.

`VRImportBatch` is the guarded entry point for importer changes. Unknown later edits are preserved rather than overwritten. Batch Options can restore the last supported importer batch.

### Permanent unused-asset cleanup

`VRUnusedAssetCleaner` is intentionally isolated from normal Quick Optimize actions because deletion cannot use Unity Undo.

The cleaner:

- only scans the user-selected Assets scope,
- only considers conservative asset categories,
- builds inbound-reference evidence from `AssetDatabase.GetDependencies`,
- protects common runtime/dynamic-use folders,
- protects labelled and AssetBundle assets,
- previews candidates,
- requires two warning dialogs,
- permanently deletes through `AssetDatabase.DeleteAsset` only after the final confirmation.

The tool explicitly warns that runtime-only string/reflection/custom-loader references cannot always be proven by Unity's serialized dependency graph.

## Blender architecture

The maintained Blender core lives under:

```text
Blender/vr_optimizer_blender/
```

The root `blender_manifest.toml` and extension `__init__.py` provide the Blender 4.2+ package entry point.

In v0.7.65 the extension entry point replaces the older stacked draw layout with one width-aware **Quick Optimize** panel. The modern 4.2+ operators remain implemented in `tools_42.py`, but their old child panel is intentionally not registered because those actions are surfaced in the main panel.

### Blender mesh workflows

- One-Click Remesh preserves source objects and transfers supported UV/material/deformation data.
- LOD generation creates LOD0 / LOD1 / LOD2 plus an optional collision proxy.
- Generate Lightmap UV creates a protected second UV channel for supported static meshes.
- Link Identical Mesh Data links exact static duplicates to shared mesh data while preserving object transforms.
- Strip Collider Render Data removes render-only data only from generated collider proxies.

Generated Remesh/LOD outputs are fingerprinted so unchanged jobs can reuse them. Manual edits block automatic replacement until history is explicitly reset.

### Blender 5.x animation compatibility

`deform_transfer.py` supports Blender 5.x slotted Action/channelbag animation data while retaining the compatible path required by Blender 4.2.

## Validation

The release workflow:

- validates unified versions and package contents,
- checks the Unity 0.7.65 UI and destructive-cleanup guard rails,
- builds the Unity package,
- builds and uploads the Blender Extensions ZIP,
- runs Blender runtime tests on 4.2 LTS, 4.5 LTS and 5.2 LTS,
- validates the final extension ZIP with Blender 4.2.

## Update architecture

`version.json` contains the unified project version plus compatibility fields used by the current Unity and Blender build paths.

The Unity footer checks the same project feed. Git installs can update through Unity Package Manager; embedded, VCC or registry installs receive source-appropriate instructions instead of being modified automatically.

## Compatibility principle

Historical package IDs and internal class names remain when changing them would break installations. User-facing naming, documentation and future work use the broader **Optimize Your Project** identity.
