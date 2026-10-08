# Optimize Your Project

<img src="Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" alt="Optimize Your Project logo" width="150">

<p align="center">
  <a href="README.md"><strong>Overview</strong></a> |
  <a href="Blender/README.md"><strong>Blender Guide</strong></a> |
  <a href="Documentation/Roadmap.md"><strong>Roadmap</strong></a> |
  <a href="Documentation/Architecture.md"><strong>Architecture</strong></a> |
  <a href="CHANGELOG.md"><strong>Changelog</strong></a>
</p>

**v0.8.0 | Unity + Blender 4.2+ | General developer optimization tools | FISHHWB | Ded Zed**

Optimize Your Project is a free general developer optimization toolkit focused on turning repetitive project cleanup and optimization work into clear, guarded actions. Unity and Blender share one project release version, with more engine integrations planned under the same safety and localization rules.

## Install / Download Optimize Your Project

### Unity

Open **Window > Package Manager**, press **+**, choose **Add package from git URL**, then paste:

```text
https://github.com/dedzedofficial/Optimize-Your-Project.git
```

For fixed v0.8.0:

```text
https://github.com/dedzedofficial/Optimize-Your-Project.git#v0.8.0
```

### Blender 4.2+

Blender support targets the modern **Blender Extensions** system only. The minimum supported Blender version is **4.2**.

Open the latest successful release-check workflow:

https://github.com/dedzedofficial/Optimize-Your-Project/actions/workflows/release-checks.yml

Download the `optimize-your-project-blender-0.8.0` artifact and install:

```text
optimize-your-project-blender-extension-0.8.0.zip
```

Use **Edit > Preferences > Get Extensions > Install from Disk** and choose the ZIP without extracting it. Then press **N** in the 3D Viewport and open the **FISHHWB** tab.

### VRChat / VCC (optional)

```text
vcc://vpm/addRepo?url=https%3A%2F%2Fdedzedofficial.github.io%2FOptimize-Your-Project%2Findex.json
```

The Unity package does not require a VR SDK for normal projects.

## Unity v0.8.0

The Unity window stays button-first and keeps project-wide destructive actions separate from normal optimization jobs.

### One-click tools

- **Optimize Textures** preserves explicit formats and stricter existing size caps.
- **Optimize Model Imports** preserves a stronger existing mesh-compression level instead of lowering it to the requested level.
- **Optimize Particles** handles Constant and Two Constants lifetime caps without rewriting authored curve lifetimes.
- **Fix Material Costs** remaps exact duplicate material references and removes safe trailing empty slots.
- **Optimize Lighting** retains its guarded baked-light workflow as an explicit project action.
- **Disable Realtime Shadows** only changes supported realtime lights on character/avatar scope.
- **Optimize UI Raycasts** preserves Selectable hierarchies and CanvasGroup-blocked UI while keeping EventSystem handler detection.
- **Optimize Audio** is new in v0.8.0. Long clips use Streaming and shorter clips use Compressed In Memory with Vorbis compression and conservative quality settings.
- **Clean Missing Scripts** previews the affected object/script count before removing broken MonoBehaviour entries.

### Permanent unused-asset cleanup

The Project page includes a separate **Danger Zone** action: **Find and Permanently Delete Unused Assets**.

The cleaner is intentionally conservative:

- it only considers selected safe asset categories such as textures, materials, audio clips, animation clips and physics materials,
- it checks serialized inbound dependencies from the rest of the Assets tree,
- it protects Resources, StreamingAssets, Editor, Plugins, Gizmos, Addressable-related paths, labelled assets and AssetBundle assets,
- it shows candidate examples before deletion,
- it requires a second explicit permanent-delete confirmation,
- it clearly states that Unity Undo cannot restore deleted asset files,
- it warns that runtime-only string/reflection/custom-loader references cannot always be detected.

Use source control or a backup before any permanent cleanup.

## Blender v0.8.0

Blender remains focused on **4.2+** and keeps Remesh, LOD and modern static-mesh tools in one readable **Primary Actions** panel.

- **One-Click Remesh** keeps the original object and now runs an additional v0.8 preservation validation before accepting generated output.
- UV maps, material slots, vertex groups and shape keys are checked after Remesh. If preservation validation fails, the generated result is rejected and the original is reselected.
- **Clean Mesh** is new in v0.8.0. Static meshes can merge duplicate vertices, remove loose/degenerate geometry and recalculate face normals.
- Clean Mesh avoids topology-changing cleanup on shape-key, vertex-group or armature-bound meshes so vertex correspondence is not intentionally destroyed.
- **Create LOD0 / LOD1 / LOD2** remains source-preserving and can optionally create a collision proxy from LOD2.
- **Generate Lightmap UV**, **Link Identical Mesh Data** and **Strip Collider Render Data** remain in the same primary panel.
- runtime validation remains on Blender 4.2 LTS, 4.5 LTS and 5.2 LTS.

### Blender tools

**One-Click Remesh** creates a separate reduced copy while preserving the source. Supported UV layers, material assignments, relative shape keys, armature bindings and vertex weights are retained through the guarded workflow, with v0.8 adding a rejection pass if required data is missing from the result.

**Create LOD0 / LOD1 / LOD2** creates source-preserving static-mesh LOD sets. Optional **Create Collision Proxy from LOD2** adds a separate render-disabled wireframe collider candidate.

**Clean Mesh** performs safe cleanup on selected meshes. Static meshes receive topology cleanup; deformed meshes use the non-topology-safe path so their authored deformation correspondence is preserved.

**Generate Lightmap UV** creates a protected `LightmapUV` second channel without replacing existing secondary UV data.

**Link Identical Mesh Data** lets exact selected static duplicates share one Blender mesh datablock while keeping object transforms independent.

**Strip Collider Render Data** removes materials, UV layers and color attributes only from generated collider proxies.

## Languages

Unity and Blender now have matching language coverage in v0.8.0:

- Auto
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
- Dutch
- Polish
- Turkish

Unity Auto follows the system language. Blender Auto follows Blender's interface language and falls back to English for an unknown locale.

Future language expansion can now be added to both integrations together instead of Blender lagging behind Unity.

## Roadmap showcase

The full priority-led roadmap is in [Documentation/Roadmap.md](Documentation/Roadmap.md).

| Priority | Focus | Showcase |
| --- | --- | --- |
| **P0** | Current integrations | Continue improving every useful Unity and Blender button, recovery route, result summary and regression check. |
| **P1** | Languages | Expand Unity and Blender together now that they have localization parity. |
| **P1** | Godot 4.x | First planned new game-engine integration, focused on safe import, scene and selected-node optimization. |
| **P2** | Unreal Engine 5.x | Planned editor plugin for texture, static-mesh, collision and asset optimization after the shared cross-engine layer is proven. |
| **P3** | Later engines | Flax, Stride and other engines are evaluated only after the main integrations are stable enough to justify more surface area. |

The project will continue to favor useful single-button jobs over large settings panels.

## Free for developers

Optimize Your Project is free to use. The goal is to turn repetitive optimization jobs into clear, useful actions without putting basic developer help behind a paywall.

Optional support: https://www.patreon.com/cw/DedZed

## Safety

Use source control or backups for production projects and inspect generated results in the target engine.

Blender Remesh and LOD preserve source objects. Clean Mesh avoids topology edits on deformation-sensitive meshes. Lightmap UV generation preserves geometry and primary UVs. Identical mesh-data linking is Undoable, but linked duplicates intentionally share later mesh-data edits until unlinked again. Collider render-data stripping is restricted to generated collision proxies.

Unity importer changes use guarded history and restoration. Scene-object optimizations use Unity Undo where practical. Permanent unused-asset deletion is the explicit exception and uses two warning dialogs because file deletion cannot be restored with Unity Undo.

## Repository layout

```text
package.json                                  Unity package manifest
version.json                                  Unified project release version
Editor/FISHHWBVR/                            Unity Editor implementation
Blender/vr_optimizer_blender/                Blender core and 4.2+ tools
blender_manifest.toml                        Blender Extensions manifest
scripts/test_blender.py                      Remesh / LOD regression tests
scripts/test_blender_42.py                   Blender 4.2+ tool regression tests
scripts/test_blender_52.py                   Blender 5.2 slotted Action regression tests
scripts/build_blender_extension.py           Blender Extensions ZIP builder
.github/workflows/release-checks.yml         Package and runtime validation
```

## Keywords

Unity optimization, Blender 4.2 extension, Godot optimization, Unreal Engine optimization, one-click optimization, game optimization, asset optimization, texture optimization, audio optimization, mesh optimization, lightmap UV, mesh instancing, collision proxy, LOD, VR, XR, VRChat, mobile optimization and indie development.

## Community

Website: https://fishhwb.github.io/

Discord: https://discord.gg/wZGxxkk4Jg

Patreon: https://www.patreon.com/cw/DedZed
