# Optimize Your Project changelog

<img src="Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" alt="Optimize Your Project logo" width="96">

The Unity package retains its historical `com.fishhwb.vr-optimizer` ID. Blender add-on previews are tracked in the [unified roadmap](Documentation/Roadmap.md); they are not Unity package releases.

## 0.6.73

- Rebuilt World, Avatar and Project pages around direct action buttons; individual findings appear only after Scan Entire Project.
- Combined texture size caps and eligible automatic compression into one action with a single reimport per changed texture.
- Kept a dedicated Updates page and fixed the package compiler and meta-file errors.

## 0.6.7

- Fixed ambiguous PackageInfo compiler reference in the update checker and completed Unity meta coverage for package files.

- Added a Project page with folder-scoped texture compression cleanup, individual platform selections, batch reimports and resolved-format reporting.
- Added an Editor window icon, a clearly separated Updates page, and more visible job and action sections.
- Added GitHub stable-release checks, release notes and confirmed Git package updates through Unity Package Manager. Other install sources show update guidance.

## 0.6.6

- Split the Editor into World and Avatar pages with focused issue buttons and All / Critical / Warning filters.
- Removed preset UI and kept direct texture and particle controls.
- Added selected model importer mesh compression preview and application with per-model exclusion and confirmation.
- Expanded mesh and avatar roadmap options.

## 0.6.5

- Selected scene avatar inventory and material-slot checks.
- Avatar-scoped particle optimization with grouped Unity Undo.
- Preview and selective application of project or avatar texture caps.
- VPM release automation and Creator Companion repository button (available after first tagged release and Pages deployment).

## 0.6.4

- Simplified editor window with platform size dropdowns and custom entry.
- Removed target selector and advanced texture importer controls; preserve existing compression and filtering.
- Light and mesh checks now inspect loaded Hierarchy scenes only.

## 0.6.3

- Native platform texture overrides and configurable PC, Quest and iOS presets.
- Undoable loaded-scene particle optimization and individually confirmed light edits.
- Modular texture, particle, light and imported mesh diagnostics with cancellable scans.
- Git URL Unity Package Manager layout and editor-only assembly.
