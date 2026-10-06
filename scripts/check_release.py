"""Static release package, version and branding checks for Optimize Your Project."""
import ast
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import tomllib
from zipfile import ZipFile

root = Path(__file__).resolve().parents[1]

manifest = json.loads((root / "package.json").read_text(encoding="utf-8"))
versions = json.loads((root / "version.json").read_text(encoding="utf-8"))

assert manifest["displayName"] == "Optimize Your Project"
assert manifest["name"] == "com.fishhwb.vr-optimizer"  # historical compatibility ID
assert manifest["version"] == "0.7.60"
for keyword in [
    "optimize-your-project", "one-click-optimization", "game-optimization",
    "unity", "blender", "blender-addon", "asset-optimization",
    "texture-optimization", "mesh-optimization", "material-optimization",
    "draw-calls", "lod", "game-ready", "vrchat",
]:
    assert keyword in manifest["keywords"], keyword
assert versions["unity"] == manifest["version"]
assert versions["unity_tag"] == "v" + manifest["version"]
assert versions["unity_url"].endswith("/releases/tag/" + versions["unity_tag"])

extension_manifest = tomllib.loads((root / "blender_manifest.toml").read_text(encoding="utf-8"))
assert extension_manifest["schema_version"] == "1.0.0"
assert extension_manifest["id"] == "optimize_your_project"
assert extension_manifest["version"] == versions["blender"] == "0.7.55"
assert extension_manifest["type"] == "add-on"
assert extension_manifest["license"] == ["SPDX:GPL-3.0-or-later"]
assert extension_manifest["blender_version_min"] == "4.2.0"
assert (root / "Editor/FISHHWBVR/VRUpdateChecker.cs").read_text().find('"' + manifest["version"] + '"') >= 0

icon = root / "Editor/FISHHWBVR/Icons/Optimize-Your-Project.png"
assert icon.read_bytes()[:8] == bytes.fromhex("89504e470d0a1a0a")
assert icon.with_suffix(".png.meta").is_file()

window_path = root / "Editor/FISHHWBVR/FISHHWBVROptimizerWindow.cs"
window = window_path.read_text(encoding="utf-8")
assert "Icons/Optimize-Your-Project.png" in window
assert 'new[] { T("project"), T("avatar") }' in window
assert '"WORLD"' not in window
assert '"UPDATES"' not in window
assert "DrawFooter();" in window
assert "VRUpdateHealth.FarBehind" in window
assert 'T("android")' in window
assert "FISHHWB VR Optimizer" not in window
assert 'T("support")' in window
assert "https://www.patreon.com/cw/DedZed" in window
assert "panelStyle" in window
assert "DrawTopBar" in window
assert "VRMissingScriptCleaner.Clean" in window
assert 'T("clean_missing_scripts")' in window

legacy_localization = (root / "Editor/FISHHWBVR/VRLocalization.cs").read_text(encoding="utf-8")
for language in ["English", "Japanese", "SimplifiedChinese", "Korean"]:
    assert language in legacy_localization

localization = (root / "Editor/FISHHWBVR/OYPLocalization.cs").read_text(encoding="utf-8")
for language in [
    "Auto", "English", "Japanese", "SimplifiedChinese", "TraditionalChinese", "Korean",
    "Spanish", "French", "German", "Portuguese", "Russian", "Italian",
]:
    assert language in localization
for required in [
    "Application.systemLanguage", "SystemLanguage.Japanese", "SystemLanguage.ChineseSimplified",
    "SystemLanguage.ChineseTraditional", "SystemLanguage.Korean", "SystemLanguage.Spanish",
    "SystemLanguage.French", "SystemLanguage.German", "SystemLanguage.Portuguese",
    "SystemLanguage.Russian", "SystemLanguage.Italian", "Auto (",
    "Español", "Français", "Deutsch", "Português", "Русский", "Italiano",
]:
    assert required in localization, required

assert "VRProjectInsights.LargestTextures" in window
assert "VRProjectInsights.ReadWriteReview" in window
assert "FixExpensiveMaterialSetups" in window
assert "VRProjectMaintenance.CollectTextureImportFixes" in window
assert "VRProjectMaintenance.CollectDuplicateMaterialFixes" in window
assert "VRProjectMaintenance.CollectUnusedMaterialSlots" in window

maintenance = (root / "Editor/FISHHWBVR/VRProjectMaintenance.cs").read_text(encoding="utf-8")
assert "CollectTextureImportFixes" in maintenance
assert "ApplyTextureImportFix" in maintenance
assert "CollectUnusedMaterialSlots" in maintenance
assert "ApplyUnusedMaterialSlotFix" in maintenance
assert "CollectDuplicateMaterialFixes" in maintenance
assert "ApplyDuplicateMaterialFix" in maintenance
assert "TextureImporterType.NormalMap" in maintenance
assert "optimizeMeshPolygons" in window
assert "optimizeMeshVertices" in window
assert "mesh.subMeshCount" in maintenance

cleaner = (root / "Editor/FISHHWBVR/VRMissingScriptCleaner.cs").read_text(encoding="utf-8")
assert "GetMonoBehavioursWithMissingScriptCount" in cleaner
assert "RemoveMonoBehavioursWithMissingScript" in cleaner
assert "Undo.RegisterCompleteObjectUndo" in cleaner

project_scanner = (root / "Editor/FISHHWBVR/VRProjectScanner.cs").read_text(encoding="utf-8")
assert '"Optimize Your Project"' in project_scanner
assert "FISHHWB VR Optimizer" not in project_scanner

texture_scanner = (root / "Editor/FISHHWBVR/VRTextureScanner.cs").read_text(encoding="utf-8")
assert "Android / Mobile" in texture_scanner
assert "Android / Quest" not in texture_scanner

blender_source = root / "Blender/vr_optimizer_blender/__init__.py"
source_text = blender_source.read_text(encoding="utf-8")
tree = ast.parse(source_text, filename=str(blender_source))
info = next(
    ast.literal_eval(node.value)
    for node in tree.body
    if isinstance(node, ast.Assign)
    and any(isinstance(target, ast.Name) and target.id == "bl_info" for target in node.targets)
)
blender_version = ".".join(map(str, info["version"]))
assert blender_version == versions["blender"] == "0.7.55"
assert versions["blender_tag"] == "blender-v" + blender_version
assert 'bl_idname = "fishhwb.one_click_remesh"' in source_text
assert 'bl_idname = "fishhwb.create_lods"' in source_text
assert 'bl_idname = "fishhwb.create_lods_selected"' in source_text
assert "FISHHWB_OT_one_click_remesh" in source_text.split("classes =", 1)[1]
assert "FISHHWB_OT_create_lods" in source_text.split("classes =", 1)[1]
assert "FISHHWB_OT_create_lods_selected" in source_text.split("classes =", 1)[1]
assert "LANGUAGE_ITEMS" in source_text
for language_code in ["'EN'", "'JA'", "'ZH'", "'KO'"]:
    assert language_code in source_text
assert "Blender v0.7.55: Remesh + LOD only" in source_text
assert "ONE-CLICK REMESH" in source_text
assert "LOD GENERATION" in source_text
for removed in [
    'fishhwb.clean_selected_mesh',
    'fishhwb.clean_selected_meshes',
    'fishhwb.create_game_ready_copy',
    'fishhwb.merge_vertices',
    'fishhwb.show_heavy_meshes',
    'fishhwb.tri_limit',
    'fishhwb.join_merge',
    'ONE-CLICK CLEANUP',
    'Show Advanced Mesh Tools',
    '_GameReady',
]:
    assert removed not in source_text, removed

extension_proxy = (root / "__init__.py").read_text(encoding="utf-8")
assert extension_proxy.startswith("# SPDX-License-Identifier: GPL-3.0-or-later")
assert "Blender 4.2+ extension entry point" in extension_proxy
assert "from .Blender.vr_optimizer_blender import bl_info" in extension_proxy
assert "def register()" in extension_proxy
assert "def unregister()" in extension_proxy
assert (root / "Blender/__init__.py").is_file()
assert (root / "Blender/EXTENSION_LICENSE.txt").is_file()
assert (root / "Blender/vr_optimizer_blender/__init__.py").read_text(encoding="utf-8").startswith(
    "# SPDX-License-Identifier: GPL-3.0-or-later"
)

for path in [
    root / "README.md",
    root / "Blender/README.md",
    root / "CHANGELOG.md",
    *sorted((root / "Documentation").glob("*.md")),
]:
    content = path.read_text(encoding="utf-8")
    assert "Optimize-Your-Project.png" in content, path
    assert "dedzedofficial/VR-Optimizer" not in content, path
    assert "Install / Download Optimize Your Project" in content, path
    assert "Blender Guide" in content, path
    assert "Roadmap" in content, path
    assert "Architecture" in content, path
    assert "Changelog" in content, path
    assert "https://github.com/dedzedofficial/Optimize-Your-Project.git" in content, path
    assert "https://github.com/dedzedofficial/Optimize-Your-Project/releases" in content, path
    assert "DOWNLOAD BLENDER ZIP BUILDS" in content, path
    assert "optimize-your-project-blender-extension-0.7.55.zip" in content, path
    assert "optimize-your-project-blender-0.7.55.zip" in content, path
    assert "https://github.com/dedzedofficial/Optimize-Your-Project/actions/workflows/release-checks.yml" in content, path
    assert "Remesh" in content, path
    assert "LOD" in content, path
    assert "archive/refs/heads/main.zip?blender_version_min=4.2.0" not in content, path
    assert "git clone https://github.com/dedzedofficial/Optimize-Your-Project.git optimize_your_project" not in content, path
    assert "git -C optimize_your_project pull" not in content, path

readme = (root / "README.md").read_text(encoding="utf-8")
assert "general developer optimization" in readme.lower()
assert "VRChat / VCC (optional)" in readme
assert "## Keywords" in readme
assert "Optimize Lighting" in readme
assert "Clean Missing Scripts" in readme
assert "auto-detect" in readme.lower()
assert "optimize-your-project-blender-extension-0.7.55.zip" in readme
assert "Blender v0.7.55 intentionally supports only" in readme
assert not re.search(r"made\s+by\s+(?:a\s+)?man|help\s+from\s+friends", readme, re.IGNORECASE)

assert "## " + manifest["version"] in (root / "CHANGELOG.md").read_text()
assert "v" + manifest["version"] in readme
assert "v" + blender_version in (root / "Blender/README.md").read_text()
for relative in subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=root, text=True).splitlines():
    path = root / relative
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    assert chr(0x2014) not in content, f"Unsupported punctuation in {relative}"

assert "VRActionSummary.Run" in window
for path in (root / "Editor").rglob("*.cs"):
    assert path.with_suffix(".cs.meta").is_file(), path

env = dict(os.environ)
env["GITHUB_REF_NAME"] = "v" + manifest["version"]
subprocess.run([sys.executable, "scripts/build_vpm.py"], cwd=root, env=env, check=True)

with ZipFile(root / "dist" / f"{manifest['name']}-{manifest['version']}.zip") as package:
    assert package.testzip() is None
    assert "Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" in package.namelist()
    assert "Editor/FISHHWBVR/VRMissingScriptCleaner.cs" in package.namelist()
    assert "Editor/FISHHWBVR/OYPLocalization.cs" in package.namelist()

listing = json.loads((root / "dist/index.json").read_text(encoding="utf-8"))
assert "Optimize-Your-Project/index.json" in listing["url"]

env["GITHUB_REF_NAME"] = versions["blender_tag"]
built = subprocess.run(
    [sys.executable, "scripts/build_blender.py"],
    cwd=root,
    env=env,
    check=True,
    capture_output=True,
    text=True,
)

with ZipFile(Path(built.stdout.strip())) as package:
    assert package.testzip() is None
    assert "vr_optimizer_blender/__init__.py" in package.namelist()
    assert "vr_optimizer_blender/optimize-your-project-logo.png" in package.namelist()

extension_built = subprocess.run(
    [sys.executable, "scripts/build_blender_extension.py"],
    cwd=root,
    check=True,
    capture_output=True,
    text=True,
)
extension_archive = Path(extension_built.stdout.strip())
assert extension_archive.name == "optimize-your-project-blender-extension-0.7.55.zip"
with ZipFile(extension_archive) as package:
    assert package.testzip() is None
    names = set(package.namelist())
    assert "blender_manifest.toml" in names
    assert "__init__.py" in names
    assert "Blender/vr_optimizer_blender/deform_transfer.py" in names
    assert "Blender/__init__.py" in names
    assert "Blender/EXTENSION_LICENSE.txt" in names
    assert "Blender/vr_optimizer_blender/__init__.py" in names
    assert "Blender/vr_optimizer_blender/optimize-your-project-logo.png" in names

print("v0.7.60 static release checks passed; Unity and Blender runtime editor tests remain required.")
