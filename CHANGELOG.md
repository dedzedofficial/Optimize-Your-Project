# Optimize Your Project changelog

<img src="Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" alt="Optimize Your Project logo" width="96">

The product is now positioned as a **general developer optimization toolkit**. The historical Unity package ID `com.fishhwb.vr-optimizer` is retained for installation compatibility; it does not mean the tool is VR-only.

## 0.7.0

- Polished the Unity and Blender interfaces with clearer cards, stronger section hierarchy, larger primary actions and cleaner footers.
- Added a visible **Free for Developers** note explaining that the project is intended to help creators and newer developers without a paywall.
- Added optional Patreon support buttons; donations help fund testing, documentation, new optimization tools and future integrations while the project remains free.
- Collapsed Blender's advanced mesh controls behind an optional Advanced Tools section so one-click cleanup stays front and center.

- Repositioned Optimize Your Project around general Unity, Blender and real-time development workflows rather than VR-only development.
- Merged the old Unity World + Project split into one **PROJECT** page for ordinary Unity projects and loaded scenes.
- Kept **AVATAR** as an optional character hierarchy workflow without requiring the VRChat SDK.
- Removed the full Updates page and added a compact footer with green/current, orange/one-patch-behind, red/two-patches-or-newer-minor-behind, and grey/unknown status.
- Added a platform-specific `version.json` feed so Blender releases cannot be mistaken for Unity package updates.
- Added early Blender **One-Click Remesh** and **Merge Duplicate Vertices** actions.
- Kept Blender triangle reduction, join/atlas and static LOD tools under a clearer Advanced Mesh Tools section.
- Simplified installation and usage documentation around direct one-click jobs.
- Expanded static release validation for version consistency, Blender syntax and v0.7 UI/action expectations.

## 0.6.73

- Rebuilt World, Avatar and Project pages around direct action buttons; individual findings appear only after Scan Entire Project.
- Combined texture size caps and eligible automatic compression into one action with a single reimport per changed texture.
- Kept a dedicated Updates page and fixed package compiler and meta-file errors.

## 0.6.7

- Fixed ambiguous PackageInfo compiler reference in the update checker and completed Unity meta coverage.
- Added project texture compression cleanup and update checks.

## 0.6.6

- Split the Editor into World and Avatar pages with focused issue buttons and filters.
- Removed preset UI and added reviewed mesh compression.

## 0.6.5

- Added avatar inventory, avatar-scoped particle optimization and texture previews.
- Added VPM release automation and Creator Companion repository support.

## 0.6.4

- Simplified texture size controls and narrowed scene checks.

## 0.6.3

- Added platform texture overrides, particle optimization, light/mesh diagnostics and Git URL package support.
