# FISHHWB VR Optimizer

**Version 0.6.3 · Free Unity Editor package · FISHHWB | Ded Zed**

FISHHWB VR Optimizer speeds up recurring VR and VRChat project work: texture import overrides, particle settings, light audits and mesh diagnostics. It does not require the VRChat SDK or any third-party package.

## Requirements

- Unity **2021.3 LTS or newer**. The package contains Editor code only and does not add runtime components to a build.
- Git installed and accessible to Unity for Git URL installation.
- A project backup or a version control commit before large texture import changes.

## Install from GitHub

1. Open your Unity project.
2. Open **Window → Package Manager**.
3. Click **+ → Add package from git URL**.
4. Paste:

   ```text
   https://github.com/dedzedofficial/VR-Optimizer.git
   ```

5. Click **Add** and allow Unity to import the package.
6. Open **FISHHWB → VR Optimizer** from the top menu.

This repository has `package.json` at its root, so no `?path=` suffix is needed. For a reproducible installation, append a released tag after publishing one, for example `https://github.com/dedzedofficial/VR-Optimizer.git#v0.6.3`. A private repository requires Git credentials on the developer's machine; public users cannot install a private repository by URL. GitHub's **Download ZIP** is source distribution, not the Git URL install method. If Git installation is unavailable, extract the repository into `Packages/com.fishhwb.vr-optimizer` inside your Unity project and add it as an embedded package.

## Quick start

1. Select **Target Platform** (Android / Quest, Standalone, or iOS).
2. Select a **Texture Preset**: PC Quality (4096/1024/1024), Quest Balanced (2048/512/512), Quest Performance (1024/256/256), or Custom. Values are maximum importer caps in PC/Android/iOS order, not permanent image resizes.
3. Review **Override PC/Android/iOS**, compression and optional texture controls. Set a size field to customize the preset. Mipmap, filter and anisotropy changes require their separate checkboxes.
4. Select a **Particle Preset**: Conservative, Balanced, Quest Performance, or Custom. Review every particle checkbox before optimizing; the Quest Performance preset disables several costly modules intentionally.
5. Press **SCAN FOR PROBLEMS** for an audit or run one of the focused actions. The scan has INFO, WARNING and CRITICAL results, SELECT links and safe individual actions where supported.

## Actions

| Button | What it does | What to check afterward |
| --- | --- | --- |
| **OPTIMIZE TEXTURES** | Scans supported 2D Default and Normal Map texture importers under `Assets`, applies selected platform overrides, and reimports only changed assets. Existing stricter size limits stay stricter. | Check representative textures in the target build, especially normal maps, alpha and compression. Importer changes should be reverted through source control if needed. |
| **OPTIMIZE PARTICLES** | Optimizes particle systems in currently loaded scenes, applying only the selected caps and module switches. Uses Unity Undo. | Check appearance and performance; save scenes when satisfied. Prefab assets outside loaded scenes are audited but are not batch edited. |
| **OPTIMIZE LIGHTS (AUDIT)** | Reports lights in prefabs and loaded scenes. A scene light can be changed through **REVIEW & OPTIMIZE** after a per-light confirmation: its shadows are disabled and, when enabled, its range is capped. | Use Unity Undo if the result changes the scene's intended lighting. There is no automatic bulk light change. |
| **SCAN FOR PROBLEMS** | Reads project texture/mesh imports, prefab effects/lights and loaded scene effects/lights. | Select each reported asset or object and assess it in context. The scan never applies changes. |
| **CHECK MESHES** | Reports imported mesh vertices, triangles, bounds, Read/Write, compression and import optimization. | Decide manually whether model changes are safe for rigs, UVs, blendshapes and animation. |

**Individual OPTIMIZE** is available for supported textures and scene particles. Prefab asset particle and light issues can be selected for inspection; open the prefab in Prefab Mode to edit it through Unity. The results list is a snapshot: rerun the scan to refresh it after edits.

### Particle preset details

- **Conservative:** caps maximum particles to 500 when higher; preserves costly modules.
- **Balanced:** caps maximum particles to 500 and disables particle shadow casting; leaves other modules intact.
- **Quest Performance:** caps particles to 250 and constant lifetime to 10 seconds; disables trails, collision, noise, particle lights and shadows. Sub emitters remain enabled unless explicitly checked.
- **Custom:** each setting is controlled by its checkbox and value.

A cap affects only higher values. Lifetime capping applies only to constant start lifetime, not random ranges or curves. Emission, sorting, simulation space, 3D size/rotation, mesh rendering and potential overdraw are reported for review rather than silently rewritten.

## Safety and scope

Texture optimization changes **Unity importer metadata**, never source image bytes. Importer changes are not guaranteed to be undoable through Unity Undo; commit your project first. The progress bar can cancel between assets, preserving completed changes. Particles and individual scene lights use Undo. Nothing deletes assets or decimates meshes. No automatic AssetPostprocessor runs on import in this version.

Texture source dimensions do not equal GPU memory usage. Particle overdraw depends on on-screen size and material; light cost depends on the render pipeline and quality settings. Scans report useful heuristics rather than measured frame times. Scanning occurs only when you press a button, shows cancellable progress, and keeps results in memory until the next scan or window close. Only **loaded scenes** are scanned; unopened scene files are not modified or audited.

## Troubleshooting

- **Package Manager cannot install from Git:** verify Git is installed, the URL ends in `.git`, and you have permission to access the repository. For private repos, configure Git authentication outside Unity.
- **No FISHHWB menu appears:** wait for Unity compilation, then inspect Console compiler errors. Confirm that `Editor/FISHHWBVR/FISHHWB.VROptimizer.Editor.asmdef` and root `package.json` are present.
- **Texture still looks large:** platform importer caps take effect for the selected build target. Check the texture's Inspector platform tab and switch the Unity build target before comparing output.
- **No scene particles or lights found:** open the scene containing the objects and run the scan again. Prefabs are audited as assets, while particle bulk optimization is limited to loaded scenes.
- **A preset changed a desired effect:** press **Edit → Undo** for scene object edits. For importer settings, restore the asset metadata (`.meta`) from version control.

## Repository layout

```text
package.json
Editor/FISHHWBVR/             Editor-only assembly, window, optimizers, scanners, settings
Documentation/                Architecture notes
README.md                     Install, use, safety and troubleshooting
CHANGELOG.md                  Release history
LICENSE                       MIT
```

## Community

[Website](https://fishhwb.github.io/) · [Discord](https://discord.gg/wZGxxkk4Jg) · [Patreon](https://www.patreon.com/cw/DedZed)

FISHHWB VR Optimizer is free and licensed under MIT. Contributions and bug reports are welcome through GitHub issues and pull requests. Please include your Unity version, target platform, reproduction steps and relevant Console errors.
