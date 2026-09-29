# Optimize Your Project

**Version 0.6.73 · Free Unity Editor package · FISHHWB | Ded Zed**

Optimize Your Project speeds up recurring VR and VRChat project work: texture import overrides, particle settings, light audits and mesh diagnostics. It does not require the VRChat SDK or any third-party package.

## Install by platform

| Platform | Start here | What happens |
| --- | --- | --- |
| VRChat Creator Companion | [Add repository to VCC](vcc://vpm/addRepo?url=https%3A%2F%2Fdedzedofficial.github.io%2FOptimize-Your-Project%2Findex.json) | Opens VCC to add the package listing. Select your project and add the package there after the VPM listing is published. |
| Unity without VCC | Copy `https://github.com/dedzedofficial/Optimize-Your-Project.git` into Package Manager → Add package from git URL | Unity installs into the project you have open. |
| Blender | Follow the [Blender install guide](Blender/README.md) | Install the add-on ZIP from Blender Preferences, then enable it. The 0.7.5 build is a preview. |

A browser link cannot silently select a Unity project or install files into Blender. The [unified roadmap](Documentation/Roadmap.md#installation-experience) describes a dedicated Blender extension repository and optional project-aware installer to reduce the remaining steps.

## One click workflow

Choose **World**, **Avatar**, or **Project** and press the action you want. The work pages do not display individual warnings. Open **Project → Scan Entire Project** to see findings with All, Critical, and Warning filters.

- **Compress & Size Textures:** enter maximum PC, Android/Quest and iOS sizes, then press one button. Eligible uncompressed automatic platform imports use Unity's automatic compressed format. Existing explicitly chosen formats and stricter size limits are preserved. Each changed texture is reimported once. World covers textures under Assets, Avatar covers textures referenced by the selected hierarchy, and Project covers the chosen Assets folder.
- **Optimize Particles:** apply your entered particle count and selected module controls to loaded scenes or the avatar hierarchy. Unity Undo is supported.
- **Compress Imported Meshes:** apply a chosen Unity model compression level to imported meshes used by loaded scenes or the selected avatar. Confirm the batch before it reimports.
- **Disable Realtime Shadows:** turn off shadows on realtime lights in the selected scene scope after confirmation. Unity Undo is supported.
- **Scan Entire Project:** show individual asset and loaded-scene findings only when you request a full scan. Select an item to locate it in Unity.

The **Updates** page displays your installed version, checks GitHub releases, and offers a direct Unity update for Git installations. Embedded and VCC packages show source-specific update instructions.

Importer edits change metadata, not source files. Keep a project backup or version control commit and inspect results in the target build. This tool does not promise a frame-rate improvement or VRChat rank.

## Requirements

- Unity **2021.3 LTS or newer**. The package contains Editor code only and does not add runtime components to a build.
- Git installed and accessible to Unity for Git URL installation.
- A project backup or a version control commit before large texture import changes.

## Add to VRChat Creator Companion

[**ADD TO VCC**](vcc://vpm/addRepo?url=https%3A%2F%2Fdedzedofficial.github.io%2FOptimize-Your-Project%2Findex.json)

This button adds the package repository to Creator Companion, where you can then add **Optimize Your Project** to a project. It requires a published VPM release and GitHub Pages configured to deploy from **GitHub Actions**. Until the v0.6.73 tag is published and `https://dedzedofficial.github.io/Optimize-Your-Project/index.json` loads, use the Git installation below. A Git URL cannot be added directly as a VCC package repository.

## Install from GitHub

1. Open your Unity project.
2. Open **Window → Package Manager**.
3. Click **+ → Add package from git URL**.
4. Paste:

   ```text
   https://github.com/dedzedofficial/Optimize-Your-Project.git
   ```

5. Click **Add** and allow Unity to import the package.
6. Open **FISHHWB → Optimize Your Project** from the top menu.

This repository has `package.json` at its root, so no `?path=` suffix is needed. For a reproducible installation, append a released tag after publishing one, for example `https://github.com/dedzedofficial/Optimize-Your-Project.git#v0.6.73` (once tagged). A private repository requires Git credentials on the developer's machine; public users cannot install a private repository by URL. GitHub's **Download ZIP** is source distribution, not the Git URL install method. If Git installation is unavailable, extract the repository into `Packages/com.fishhwb.vr-optimizer` inside your Unity project and add it as an embedded package.

## Replacing an older embedded copy

If the window still says **v0.6.6** or **v0.6.7**, or only shows World and Avatar, Unity is loading the older package. Close Unity, replace the **entire** `Packages/com.fishhwb.vr-optimizer` folder with the contents of this v0.6.73 ZIP (the folder should directly contain `package.json`), then reopen the project. Do not keep a second copy under `Assets` or install a Git copy alongside an embedded copy. The new window shows **WORLD / AVATAR / PROJECT / UPDATES** across the top. If you installed by Git URL instead, GitHub must contain the new release before Package Manager can update it; a downloaded ZIP does not update a Git dependency automatically.

## Quick start

1. Open **FISHHWB → Optimize Your Project**.
2. Choose **World** for loaded scenes, **Avatar** for a selected root, or **Project** for an Assets folder.
3. Enter sizes or settings and press an action button. A confirmation appears before importer or light batches.
4. Use **Project → Scan Entire Project** only when you want individual warnings and issue details.

## Safety and scope

Texture optimization changes **Unity importer metadata**, never source image bytes. Importer changes are not guaranteed to be undoable through Unity Undo; commit your project first. The progress bar can cancel between assets, preserving completed changes. Particles and individual scene lights use Undo. Nothing deletes assets or decimates meshes. No automatic AssetPostprocessor runs on import in this version.

Texture source dimensions do not equal GPU memory usage. Particle overdraw depends on on-screen size and material; light cost depends on the render pipeline and quality settings. Scans report useful heuristics rather than measured frame times. A full diagnostic scan occurs only when you press **Scan Entire Project**. Scene checks inspect only **loaded scenes**; Project texture scans inspect the selected Assets folder. Unopened scene files are not modified or audited.

## Troubleshooting

- **Package Manager cannot install from Git:** verify Git is installed, the URL ends in `.git`, and you have permission to access the repository. For private repos, configure Git authentication outside Unity.
- **No FISHHWB menu appears:** wait for Unity compilation, then inspect Console compiler errors. Confirm that `Editor/FISHHWBVR/FISHHWB.VROptimizer.Editor.asmdef` and root `package.json` are present.
- **Texture still looks large:** platform importer caps take effect for the selected build target. Check the texture's Inspector platform tab and switch the Unity build target before comparing output.
- **No scene particles or lights found:** open the scene containing the objects and run the scan again. The World page filters particle findings to loaded scenes; project texture checks include assets.
- **An action changed a desired effect:** press **Edit → Undo** for scene object edits. For importer settings, restore the asset metadata (`.meta`) from version control.

## Repository layout

```text
package.json
Editor/FISHHWBVR/             Editor-only assembly, window, optimizers, scanners, settings
Blender/                      Separate Blender add-on and usage guide
Documentation/                Architecture notes and unified roadmap
README.md                     Install, use, safety and troubleshooting
CHANGELOG.md                  Release history
LICENSE                       MIT
```

## Community

[Website](https://fishhwb.github.io/) · [Discord](https://discord.gg/wZGxxkk4Jg) · [Patreon](https://www.patreon.com/cw/DedZed)

Optimize Your Project is free and licensed under MIT. Contributions and bug reports are welcome through GitHub issues and pull requests. Please include your Unity version, target platform, reproduction steps and relevant Console errors.

## Blender add-on (0.7.5 preview)

The [Blender add-on](Blender/README.md) is a separate native install under `Blender/vr_optimizer_blender/`. It creates reduced mesh and LOD copies, joins selected mesh copies with adjustable vertex welding, and can build a Base Color image atlas with remapped UVs for supported materials. Install the `Blender/vr_optimizer_blender` folder as a ZIP through Blender preferences; the repository root Git URL remains the Unity package at v0.6.73. The Blender 0.7.5 source is a preview pending tests in Blender and export round trips. See the [unified roadmap](Documentation/Roadmap.md#blender-track-075-preview-and-later-work).

## Future updates

See the [automation roadmap](Documentation/Roadmap.md) for planned batch restoration, scene branch actions, reviewed model imports, avatar material checks and options for other creator platforms. These are plans, not shipped features.
