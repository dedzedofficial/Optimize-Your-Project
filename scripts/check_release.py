"""Static release, packaging and branding checks for Optimize Your Project."""
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

assert unity_manifest["displayName"] == "Optimize Your Project"
assert unity_manifest["name"] == "com.fishhwb.vr-optimizer"
assert unity_manifest["version"] == versions["unity"] == "0.7.60"
assert versions["unity_tag"] == "v" + versions["unity"]
assert versions["unity_url"].endswith("/releases/tag/" + versions["unity_tag"])
assert (root / "Editor/FISHHWBVR/VRUpdateChecker.cs").read_text().find('"' + versions["unity"] + '"') >= 0

assert versions["blender"] == "0.7.61"
assert versions["blender_tag"] == "blender-v0.7.61"
assert extension_manifest["schema_version"] == "1.0.0"
assert extension_manifest["id"] == "optimize_your_project"
assert extension_manifest["version"] == versions["blender"]
assert extension_manifest["type"] == "add-on"
assert extension_manifest["license"] == ["SPDX:GPL-3.0-or-later"]
assert extension_manifest["blender_version_min"] == "4.2.0"
assert len(extension_manifest["tagline"]) <= 64

icon = root / "Editor/FISHHWBVR/Icons/Optimize-Your-Project.png"
assert icon.read_bytes()[:8] == bytes.fromhex("89504e470d0a1a0a")
assert icon.with_suffix(".png.meta").is_file()

window = (root / "Editor/FISHHWBVR/FISHHWBVROptimizerWindow.cs").read_text(encoding="utf-8")
for required in [
    "Optimize Your Project", "VRMissingScriptCleaner.Clean", "VRUIRaycastOptimizer.Optimize",
    'T("optimize_ui_raycasts")', "VRProjectInsights.LargestTextures",
    "VRProjectInsights.ReadWriteReview", "FixExpensiveMaterialSetups",
]:
    assert required in window, required
assert "FISHHWB VR Optimizer" not in window

core = (root / "Blender/vr_optimizer_blender/__init__.py").read_text(encoding="utf-8")
for required in [
    'bl_idname = "fishhwb.one_click_remesh"',
    'bl_idname = "fishhwb.create_lods"',
    'bl_idname = "fishhwb.create_lods_selected"',
    "fishhwb_create_collision_proxy", "fishhwb_collision_proxy", "_COLLIDER",
]:
    assert required in core, required

proxy = (root / "__init__.py").read_text(encoding="utf-8")
for required in [
    "Blender 4.2+ extension entry point", "tools_42", '"version": (0, 7, 61)',
    '"blender": (4, 2, 0)', "_tools42.register()", "_tools42.unregister()",
]:
    assert required in proxy, required

tools = (root / "Blender/vr_optimizer_blender/tools_42.py").read_text(encoding="utf-8")
for required in [
    "MIN_BLENDER_VERSION = (4, 2, 0)",
    'bl_idname = "fishhwb.generate_lightmap_uv"',
    'bl_idname = "fishhwb.link_identical_mesh_data"',
    'bl_idname = "fishhwb.strip_collider_render_data"',
    'bl_idname = "FISHHWB_PT_optimizer_42"',
    'bl_parent_id = "FISHHWB_PT_optimizer"',
    "_pack_lightmap_face_atlas", "LIGHTMAP_UV_NAME", "_mesh_signature",
]:
    assert required in tools, required
assert "bpy.ops.uv.smart_project" not in tools

transfer = (root / "Blender/vr_optimizer_blender/deform_transfer.py").read_text(encoding="utf-8")
for required in ["_action_fcurves", "action_get_channelbag_for_slot", "_restore_copied_action_slot"]:
    assert required in transfer, required

build_extension = (root / "scripts/build_blender_extension.py").read_text(encoding="utf-8")
assert "tools_42.py" in build_extension
assert "optimize-your-project-blender-extension-" in build_extension

workflow = (root / ".github/workflows/release-checks.yml").read_text(encoding="utf-8")
assert "'3.6'" not in workflow
assert "optimize-your-project-blender-${{ steps.versions.outputs.blender }}.zip" not in workflow
for supported in ["'4.2'", "'4.5'", "'5.2'"]:
    assert supported in workflow, supported
assert "scripts/test_blender_42.py" in workflow
assert "scripts/test_blender_52.py" in workflow

for path in [root / "README.md", root / "Blender/README.md"]:
    text = path.read_text(encoding="utf-8")
    assert "Optimize-Your-Project.png" in text, path
    assert "Install / Download Optimize Your Project" in text, path
    assert "Blender 4.2+" in text, path
    assert "Generate Lightmap UV" in text, path
    assert "Link Identical Mesh Data" in text, path
    assert "Strip Collider Render Data" in text, path
    assert "Blender 3.6" not in text, path
    assert "optimize-your-project-blender-0.7.55.zip" not in text, path
    assert "Smart UV Project" not in text, path

readme = (root / "README.md").read_text(encoding="utf-8")
assert "general developer optimization" in readme.lower()
assert "VRChat / VCC (optional)" in readme
assert "Optimize UI Raycasts" in readme
assert "collision proxy" in readme.lower()
assert not re.search(r"made\s+by\s+(?:a\s+)?man|help\s+from\s+friends", readme, re.IGNORECASE)

for relative in subprocess.check_output(
    ["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=root, text=True
).splitlines():
    path = root / relative
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    assert chr(0x2014) not in content, f"Unsupported punctuation in {relative}"

env = dict(os.environ)
env["GITHUB_REF_NAME"] = versions["unity_tag"]
subprocess.run([sys.executable, "scripts/build_vpm.py"], cwd=root, env=env, check=True)
with ZipFile(root / "dist" / f"{unity_manifest['name']}-{versions['unity']}.zip") as package:
    assert package.testzip() is None
    assert "Editor/FISHHWBVR/VRUIRaycastOptimizer.cs" in package.namelist()

extension_built = subprocess.run(
    [sys.executable, "scripts/build_blender_extension.py"],
    cwd=root,
    check=True,
    capture_output=True,
    text=True,
)
extension_archive = Path(extension_built.stdout.strip())
assert extension_archive.name == "optimize-your-project-blender-extension-0.7.61.zip"
with ZipFile(extension_archive) as package:
    assert package.testzip() is None
    names = set(package.namelist())
    for required in [
        "blender_manifest.toml", "__init__.py", "Blender/__init__.py",
        "Blender/EXTENSION_LICENSE.txt", "Blender/vr_optimizer_blender/__init__.py",
        "Blender/vr_optimizer_blender/deform_transfer.py",
        "Blender/vr_optimizer_blender/tools_42.py",
        "Blender/vr_optimizer_blender/optimize-your-project-logo.png",
    ]:
        assert required in names, required

print("Unity v0.7.60 and Blender v0.7.61 static release checks passed.")
