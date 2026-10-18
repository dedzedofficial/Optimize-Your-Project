"""Static release, packaging and metadata checks for Optimize Your Project."""
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import tomllib
from zipfile import ZipFile

root = Path(__file__).resolve().parents[1]

unity_manifest = json.loads((root / "package.json").read_text(encoding="utf-8"))
versions = json.loads((root / "version.json").read_text(encoding="utf-8"))
extension_manifest = tomllib.loads((root / "blender_manifest.toml").read_text(encoding="utf-8"))


def version_tuple(value):
    parts = value.split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise AssertionError(f"Expected x.y.z version, got {value!r}")
    return tuple(int(part) for part in parts)


# The project feed follows the current Unity release. Blender can remain on its own
# integration version when a Unity-only hotfix is shipped.
assert versions["version"] == versions["unity"] == unity_manifest["version"]
assert versions["unity_tag"] == "v" + versions["unity"]
assert versions["unity_url"].endswith("/releases/tag/" + versions["unity_tag"])
assert versions["blender_tag"] == "v" + versions["blender"]

assert unity_manifest["displayName"] == "Optimize Your Project"
assert unity_manifest["name"] == "com.fishhwb.vr-optimizer"
assert unity_manifest["unity"] == "2021.3"

assert extension_manifest["schema_version"] == "1.0.0"
assert extension_manifest["id"] == "optimize_your_project"
assert extension_manifest["version"] == versions["blender"]
assert extension_manifest["type"] == "add-on"
assert extension_manifest["license"] == ["SPDX:GPL-3.0-or-later"]
assert extension_manifest["blender_version_min"] == "4.2.0"
assert len(extension_manifest["tagline"]) <= 64

# Immutable Unity packages cannot generate missing metadata in PackageCache.
# Every editor source/assembly asset must therefore ship with its .meta file.
editor_root = root / "Editor"
for suffix in ("*.cs", "*.asmdef", "*.png"):
    for asset in editor_root.rglob(suffix):
        meta = Path(str(asset) + ".meta")
        assert meta.is_file(), f"Missing Unity package metadata: {meta.relative_to(root)}"

icon = root / "Editor/FISHHWBVR/Icons/Optimize-Your-Project.png"
assert icon.read_bytes()[:8] == bytes.fromhex("89504e470d0a1a0a")

window = (root / "Editor/FISHHWBVR/FISHHWBVROptimizerWindow.cs").read_text(encoding="utf-8")
for required in [
    "Optimize Your Project",
    "window.minSize = new Vector2(500, 570)",
    "DrawOptimizeArea",
    'T("one_click")',
    'Primary(T("optimize_textures"))',
    'Primary(T("optimize_models"))',
    'Primary(T("optimize_particles"))',
    'Primary(T("fix_materials"))',
    'Primary(T("optimize_ui_raycasts"))',
    'Primary(T("optimize_audio"))',
    'Primary(T("clean_missing_scripts"))',
    "VRAudioOptimizer.Optimize",
    "VRMissingScriptCleaner.Clean",
    "VRUIRaycastOptimizer.Optimize",
    "VRUnusedAssetCleaner.DeleteUnused",
    "VRUnusedAssetCleaner.ExportDryRunReport",
]:
    assert required in window, required
assert "RunQuickOptimize" not in window
assert "ApplyConfiguration(" not in window


audio_path = root / "Editor/FISHHWBVR/VRAudioOptimizer.cs"
audio = audio_path.read_text(encoding="utf-8")
for required in [
    "AudioImporter",
    "AudioClipLoadType.Streaming",
    "AudioClipLoadType.CompressedInMemory",
    "AudioCompressionFormat.Vorbis",
    "StreamingThresholdSeconds",
    "Optimize Audio",
]:
    assert required in audio, required
assert Path(str(audio_path) + ".meta").is_file()

localization = (root / "Editor/FISHHWBVR/OYPLocalization.cs").read_text(encoding="utf-8")
for required in [
    "Dutch", "Polish", "Turkish", "Nederlands", "Polski", "Türkçe",
    '"optimize_audio"', '"danger_zone"', '"unused_assets_warning"', '"delete_unused_assets"',
]:
    assert required in localization, required
assert localization.count("OYPLanguage.") >= 14

unused_cleaner = (root / "Editor/FISHHWBVR/VRUnusedAssetCleaner.cs").read_text(encoding="utf-8")
for required in [
    "AssetDatabase.GetDependencies",
    "AssetDatabase.DeleteAsset",
    "PERMANENT DELETE - no Unity Undo",
    "runtime-only references cannot always be detected",
    "Resources",
    "StreamingAssets",
    "AddressableAssetsData",
    "assetBundleName",
    "GetLabels",
]:
    assert required in unused_cleaner, required

missing_cleaner = (root / "Editor/FISHHWBVR/VRMissingScriptCleaner.cs").read_text(encoding="utf-8")
assert "ExportDryRunReport" in unused_cleaner and "SaveFilePanel" in unused_cleaner
for required in ["pendingScripts", "bool confirm = true", "DisplayDialog"]:
    assert required in missing_cleaner, required

ui_optimizer = (root / "Editor/FISHHWBVR/VRUIRaycastOptimizer.cs").read_text(encoding="utf-8")
for required in ["bool confirm = true", "UnityEngine.UI.Selectable", "CanvasGroupAlreadyBlocksRaycasts"]:
    assert required in ui_optimizer, required

# Keep Blender's reported add-on version aligned with the Blender integration,
# even when the top-level project/Unity release has moved ahead.
proxy = (root / "__init__.py").read_text(encoding="utf-8")
blender_tuple = version_tuple(versions["blender"])
assert f'"version": ({blender_tuple[0]}, {blender_tuple[1]}, {blender_tuple[2]})' in proxy
assert '"blender": (4, 2, 0)' in proxy
for required in [
    "_draw_core_080",
    'row.operator("fishhwb.smart_optimize"',
    'row.operator("fishhwb.one_click_remesh"',
    'row.operator("fishhwb.clean_mesh"',
    'row.operator("fishhwb.generate_lightmap_uv"',
    'row.operator("fishhwb.link_identical_mesh_data"',
    'row.operator("fishhwb.strip_collider_render_data"',
    "FISHHWB_PT_optimizer.draw = _draw_core_080",
    "_effective_language",
    "_LOCALE_MAP",
]:
    assert required in proxy, required

core = (root / "Blender/vr_optimizer_blender/__init__.py").read_text(encoding="utf-8")
for required in [
    'bl_idname = "fishhwb.one_click_remesh"',
    'bl_idname = "fishhwb.create_lods"',
    'bl_idname = "fishhwb.create_lods_selected"',
    "fishhwb_create_collision_proxy",
    "fishhwb_collision_proxy",
    "_COLLIDER",
]:
    assert required in core, required

v088 = (root / "Blender/vr_optimizer_blender/v088_tools.py").read_text(encoding="utf-8")
for required in ['fishhwb.smart_optimize', 'invoke_props_dialog', '_bake_pbr_atlas', 'Original sources preserved']:
    assert required in v088, required

v08 = (root / "Blender/vr_optimizer_blender/v08_tools.py").read_text(encoding="utf-8")
for required in [
    'bl_idname = "fishhwb.clean_mesh"',
    "bmesh.ops.remove_doubles",
    "recalc_face_normals",
    "Remesh output rejected",
    "Original object kept unchanged",
]:
    assert required in v08, required

tools = (root / "Blender/vr_optimizer_blender/tools_42.py").read_text(encoding="utf-8")
for required in [
    "MIN_BLENDER_VERSION = (4, 2, 0)",
    'bl_idname = "fishhwb.generate_lightmap_uv"',
    'bl_idname = "fishhwb.link_identical_mesh_data"',
    'bl_idname = "fishhwb.strip_collider_render_data"',
    "LIGHTMAP_UV_NAME",
    "_mesh_signature",
]:
    assert required in tools, required
assert "bpy.ops.uv.smart_project" not in tools

workflow = (root / ".github/workflows/release-checks.yml").read_text(encoding="utf-8")
for supported in ["'4.2'", "'4.5'", "'5.2'"]:
    assert supported in workflow, supported

for path in [root / "README.md", root / "Blender/README.md"]:
    text = path.read_text(encoding="utf-8")
    assert "Optimize-Your-Project.png" in text, path
    assert "Install / Download Optimize Your Project" in text, path
    assert "Blender 4.2+" in text, path
    assert "Blender 3.6" not in text, path

readme = (root / "README.md").read_text(encoding="utf-8")
assert "general developer optimization" in readme.lower()
assert "VRChat / VCC (optional)" in readme
assert "Find and Permanently Delete Unused Assets" in readme
assert "Godot 4.x" in readme
assert "Unreal Engine 5.x" in readme
assert not re.search(r"made\s+by\s+(?:a\s+)?man|help\s+from\s+friends", readme, re.IGNORECASE)

# Catch unsupported punctuation in tracked UTF-8 text files.
for relative in subprocess.check_output(["git", "ls-files"], cwd=root, text=True).splitlines():
    path = root / relative
    if not path.is_file():
        continue
    try:
        content = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    assert chr(0x2014) not in content, f"Unsupported punctuation in {relative}"

# Build and inspect the Unity/VPM package using the Unity-specific release tag.
env = dict(os.environ)
env["GITHUB_REF_NAME"] = versions["unity_tag"]
subprocess.run([sys.executable, "scripts/build_vpm.py"], cwd=root, env=env, check=True)
unity_archive = root / "dist" / f"{unity_manifest['name']}-{versions['unity']}.zip"
with ZipFile(unity_archive) as package:
    assert package.testzip() is None
    names = set(package.namelist())
    for required in [
        "package.json",
        "Editor/FISHHWBVR/FISHHWBVROptimizerWindow.cs",
        "Editor/FISHHWBVR/VRAudioOptimizer.cs",
        "Editor/FISHHWBVR/VRAudioOptimizer.cs.meta",
        "Editor/FISHHWBVR/VRUIRaycastOptimizer.cs",
        "Editor/FISHHWBVR/VRMissingScriptCleaner.cs",
        "Editor/FISHHWBVR/VRUnusedAssetCleaner.cs",
    ]:
        assert required in names, required

# Build and inspect the independently-versioned Blender extension.
extension_built = subprocess.run(
    [sys.executable, "scripts/build_blender_extension.py"],
    cwd=root,
    check=True,
    capture_output=True,
    text=True,
)
extension_archive = Path(extension_built.stdout.strip())
assert extension_archive.name == f"optimize-your-project-blender-extension-{versions['blender']}.zip"
with ZipFile(extension_archive) as package:
    assert package.testzip() is None
    names = set(package.namelist())
    for required in [
        "blender_manifest.toml",
        "__init__.py",
        "Blender/__init__.py",
        "Blender/EXTENSION_LICENSE.txt",
        "Blender/vr_optimizer_blender/__init__.py",
        "Blender/vr_optimizer_blender/deform_transfer.py",
        "Blender/vr_optimizer_blender/tools_42.py",
        "Blender/vr_optimizer_blender/v08_tools.py",
        "Blender/vr_optimizer_blender/v088_tools.py",
        "Blender/vr_optimizer_blender/optimize-your-project-logo.png",
    ]:
        assert required in names, required

print(
    "Optimize Your Project release checks passed: "
    f"Unity v{versions['unity']}, Blender v{versions['blender']}."
)
