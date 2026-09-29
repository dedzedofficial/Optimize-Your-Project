# FISHHWB VR Optimizer

**Version 0.6.7 · Free Unity Editor package · FISHHWB | Ded Zed**

FISHHWB VR Optimizer speeds up recurring VR and VRChat project work: texture import overrides, particle settings, light audits and mesh diagnostics. It does not require the VRChat SDK or any third-party package.

## What this helps with

Choose **WORLD**, **AVATAR** or **PROJECT**, then press **TEXTURES**, **PARTICLES**, **LIGHTS**, **MESHES** or (for avatars) **MATERIALS** to show only that area's findings. Results can display **ALL**, **CRITICAL** or **WARNING**; All also includes informational findings. World texture checks cover project assets; World particle, light and mesh actions target loaded scenes. Project texture compression scans the entered Assets folder. Avatar actions target a selected scene hierarchy. A selected avatar is required on the Avatar page.

Texture import sizes are entered directly for PC, Android and iOS. **PREVIEW TEXTURE CHANGES** shows effective caps and individual include controls before **APPLY SELECTED TEXTURES**. Existing stricter overrides remain stricter. Particle controls are direct switches and limits, and particle changes use Unity Undo.

**PREVIEW MESH COMPRESSION** lists imported model assets used in the current scene or avatar, their current compression, proposed level and renderer usage. Select specific models before applying. Reimporting a model can affect its appearance; inspect results in Unity and your target build. Mesh compression is primarily an asset-size option, not a guaranteed frame-rate improvement. Restore importer changes with version control if necessary. Models under immutable packages and meshes without a model importer are skipped.

### Project texture compression cleanup

Open **PROJECT → TEXTURE COMPRESSION**, enter an Assets folder, and press **SCAN UNCOMPRESSED TEXTURES**. The paged review lists Default and Normal Map 2D importers whose effective PC, Android or iOS setting is uncompressed and automatic. Untick exceptions, then press **APPLY SELECTED COMPRESSION**. The tool adds a platform override when needed and chooses Unity's automatic compressed format; source pixels, dimensions, filtering and existing explicit format choices are preserved. It reports the resolved format for each changed texture in Console after reimport. Check gradients, masks, transparency and normal maps in the target build. Importer edits are restored through version control, not Unity Undo.

### Package icon and updates

The Editor window includes a custom icon. **CHECK UPDATE** reads the latest stable GitHub Release, with automatic checks limited to once per day. When a newer numbered release exists, the window shows release notes and **UPDATE PACKAGE**. Git URL installs can update through Unity Package Manager after confirmation. For VCC/registry and embedded installs, the window gives source-specific instructions instead of replacing files itself. Network failures do not block optimization.

This is an Editor workflow tool. It does not measure device frame rate or guarantee a VRChat performance rank.

## Requirements

- Unity **2021.3 LTS or newer**. The package contains Editor code only and does not add runtime components to a build.
- Git installed and accessible to Unity for Git URL installation.
- A project backup or a version control commit before large texture import changes.

## Add to VRChat Creator Companion

[**ADD TO VCC**](vcc://vpm/addRepo?url=https%3A%2F%2Fdedzedofficial.github.io%2FVR-Optimizer%2Findex.json)

This button adds the package repository to Creator Companion, where you can then add **FISHHWB VR Optimizer** to a project. It requires a published VPM release and GitHub Pages configured to deploy from **GitHub Actions**. Until the v0.6.7 tag is published and `https://dedzedofficial.github.io/VR-Optimizer/index.json` loads, use the Git installation below. A Git URL cannot be added directly as a VCC package repository.

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

This repository has `package.json` at its root, so no `?path=` suffix is needed. For a reproducible installation, append a released tag after publishing one, for example `https://github.com/dedzedofficial/VR-Optimizer.git#v0.6.7` (once tagged). A private repository requires Git credentials on the developer's machine; public users cannot install a private repository by URL. GitHub's **Download ZIP** is source distribution, not the Git URL install method. If Git installation is unavailable, extract the repository into `Packages/com.fishhwb.vr-optimizer` inside your Unity project and add it as an embedded package.

## Quick start

1. Open **FISHHWB → VR Optimizer**.
2. Pick **WORLD**, **AVATAR** or **PROJECT**. On Avatar, select a root in a loaded scene; on Project, enter an Assets folder.
3. Press an area button to see that area's issues. Use **ALL**, **CRITICAL** or **WARNING** to filter the list and **SELECT** to locate the source.
4. Set texture caps or particle controls directly; preview changes and review selections before applying. Mesh compression also requires a review and confirmation.

## Actions and scope

| Area | World | Avatar |
| --- | --- | --- |
| Textures | Project assets under `Assets` | Textures referenced by materials on the selected hierarchy |
| Particles | Loaded scenes | Selected hierarchy |
| Lights | Loaded scenes | Selected hierarchy |
| Meshes | Loaded scenes | Selected hierarchy; imported model compression preview |
| Materials | — | Repeated and empty material slots, plus renderers with many slots |
| Texture compression | Project textures | Textures referenced by the avatar |

The Project page offers texture compression for a chosen Assets folder.

Issue reports are diagnostic. Light shadow changes require per-light confirmation; particle scene changes use Undo. Texture and model importer changes should be reviewed in version control before batch editing.

## Particle controls

Set the maximum particle count and optional constant lifetime cap directly. Toggle trails, collision, noise, lights, shadows and sub emitters individually. A cap affects only higher values. Lifetime capping applies only to a constant start lifetime. Emission, sorting, simulation space, 3D size/rotation, mesh rendering and potential overdraw are reported for review.

## Safety and scope

Texture optimization changes **Unity importer metadata**, never source image bytes. Importer changes are not guaranteed to be undoable through Unity Undo; commit your project first. The progress bar can cancel between assets, preserving completed changes. Particles and individual scene lights use Undo. Nothing deletes assets or decimates meshes. No automatic AssetPostprocessor runs on import in this version.

Texture source dimensions do not equal GPU memory usage. Particle overdraw depends on on-screen size and material; light cost depends on the render pipeline and quality settings. Scans report useful heuristics rather than measured frame times. Scanning occurs only when you press a button, shows cancellable progress, and keeps results in memory until the next scan or window close. Scene checks inspect only **loaded scenes**; Project texture scans inspect the selected Assets folder. Unopened scene files are not modified or audited.

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
Documentation/                Architecture notes and planned updates
README.md                     Install, use, safety and troubleshooting
CHANGELOG.md                  Release history
LICENSE                       MIT
```

## Community

[Website](https://fishhwb.github.io/) · [Discord](https://discord.gg/wZGxxkk4Jg) · [Patreon](https://www.patreon.com/cw/DedZed)

FISHHWB VR Optimizer is free and licensed under MIT. Contributions and bug reports are welcome through GitHub issues and pull requests. Please include your Unity version, target platform, reproduction steps and relevant Console errors.

## Future updates

See the [automation roadmap](Documentation/Roadmap.md) for planned batch restoration, scene branch actions, reviewed model imports, avatar material checks and options for other creator platforms. These are plans, not shipped features.
