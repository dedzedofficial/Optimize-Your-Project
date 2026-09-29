# Optimize Your Project architecture

`VRProjectScanner` coordinates `IVRScanner` modules. Each scanner inspects paths or loaded scene objects and appends `VRIssue` records. Future audio/material modules can implement the same interface and register in `Modules`.

`VRTextureOptimizer` edits only platform maximum-size importer metadata and reimports changed assets. `VRParticleOptimizer` and `VRLightOptimizer` record Unity Undo on loaded scene objects before editing. Light and mesh scanners inspect loaded Hierarchy scenes only. `VRSettings` stores the window profile in per-user EditorPrefs. Automatic import optimization is deliberately deferred; no AssetPostprocessor runs on every import.

The repository root is a Unity Package Manager package. `Blender/vr_optimizer_blender/` is a separate native Blender add-on; it is not loaded by the Unity Editor assembly. See the [unified roadmap](Roadmap.md) for Unity and Blender plans. The Unity v0.6.73 window has World, Avatar, Project and Updates pages.
