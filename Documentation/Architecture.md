# Architecture

`VRProjectScanner` coordinates `IVRScanner` modules. Each scanner inspects paths or loaded scene objects and appends `VRIssue` records. Future audio/material modules can implement the same interface and register in `Modules`.

`VRTextureOptimizer` edits only platform maximum-size importer metadata and reimports changed assets. `VRParticleOptimizer` and `VRLightOptimizer` record Unity Undo on loaded scene objects before editing. Light and mesh scanners inspect loaded Hierarchy scenes only. `VRSettings` stores the window profile in per-user EditorPrefs. Automatic import optimization is deliberately deferred; no AssetPostprocessor runs on every import.
