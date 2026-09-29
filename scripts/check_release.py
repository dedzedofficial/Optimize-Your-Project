"""Static release package, version and branding checks for Optimize Your Project."""
import ast
import json
import os
from pathlib import Path
import subprocess
import sys
from zipfile import ZipFile

root = Path(__file__).resolve().parents[1]

manifest = json.loads((root / "package.json").read_text(encoding="utf-8"))
versions = json.loads((root / "version.json").read_text(encoding="utf-8"))

assert manifest["displayName"] == "Optimize Your Project"
assert manifest["name"] == "com.fishhwb.vr-optimizer"  # historical compatibility ID
assert manifest["version"] == "0.7.0"
assert versions["unity"] == manifest["version"]
assert versions["unity_tag"] == "v" + manifest["version"]

icon = root / "Editor/FISHHWBVR/Icons/Optimize-Your-Project.png"
assert icon.read_bytes()[:8] == bytes.fromhex("89504e470d0a1a0a")
assert icon.with_suffix(".png.meta").is_file()

window_path = root / "Editor/FISHHWBVR/FISHHWBVROptimizerWindow.cs"
window = window_path.read_text(encoding="utf-8")
assert "Icons/Optimize-Your-Project.png" in window
assert 'new[] { "PROJECT", "CHARACTER / AVATAR" }' in window
assert '"WORLD"' not in window
assert '"UPDATES"' not in window
assert "DrawUpdateFooter();" in window
assert "VRUpdateHealth.FarBehind" in window
assert "Android / Mobile" in window
assert "FISHHWB VR Optimizer" not in window

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
assert blender_version == versions["blender"] == "0.7.0"
assert versions["blender_tag"] == "blender-v" + blender_version
assert 'bl_idname = "fishhwb.one_click_remesh"' in source_text
assert 'bl_idname = "fishhwb.merge_vertices"' in source_text
assert "ONE-CLICK CLEANUP" in source_text
assert "ADVANCED MESH TOOLS" in source_text

for path in [
    root / "README.md",
    root / "Blender/README.md",
    root / "CHANGELOG.md",
    *sorted((root / "Documentation").glob("*.md")),
]:
    content = path.read_text(encoding="utf-8")
    assert "Optimize-Your-Project.png" in content, path
    assert "dedzedofficial/VR-Optimizer" not in content, path

readme = (root / "README.md").read_text(encoding="utf-8")
assert "general developer optimization" in readme.lower()
assert "VRChat / VCC (optional)" in readme

env = dict(os.environ)
env["GITHUB_REF_NAME"] = "v" + manifest["version"]
subprocess.run([sys.executable, "scripts/build_vpm.py"], cwd=root, env=env, check=True)

with ZipFile(root / "dist" / f"{manifest['name']}-{manifest['version']}.zip") as package:
    assert package.testzip() is None
    assert "Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" in package.namelist()

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

print("v0.7 static release checks passed; Unity and Blender runtime editor tests remain required.")
