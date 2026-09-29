"""Static release package and branding checks. Runtime tests remain separate."""
import json
import os
from pathlib import Path
import subprocess
import sys
from zipfile import ZipFile

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / "package.json").read_text(encoding="utf-8"))
assert manifest["displayName"] == "Optimize Your Project"
assert manifest["name"] == "com.fishhwb.vr-optimizer"
icon = root / "Editor/FISHHWBVR/Icons/Optimize-Your-Project.png"
assert icon.read_bytes()[:8] == bytes.fromhex("89504e470d0a1a0a")
assert icon.with_suffix(".png.meta").is_file()
window = (root / "Editor/FISHHWBVR/FISHHWBVROptimizerWindow.cs").read_text(encoding="utf-8")
assert "Icons/Optimize-Your-Project.png" in window

for path in [root / "README.md", root / "Blender/README.md",
             root / "CHANGELOG.md", *sorted((root / "Documentation").glob("*.md"))]:
    content = path.read_text(encoding="utf-8")
    assert "Optimize-Your-Project.png" in content, path
    assert "dedzedofficial/VR-Optimizer" not in content, path
    assert "Documentation/Blender-0.7.5.md" not in content, path

env = dict(os.environ)
env["GITHUB_REF_NAME"] = "v" + manifest["version"]
subprocess.run([sys.executable, "scripts/build_vpm.py"], cwd=root, env=env, check=True)
with ZipFile(root / "dist" / f"{manifest['name']}-{manifest['version']}.zip") as package:
    assert package.testzip() is None
    assert "Editor/FISHHWBVR/Icons/Optimize-Your-Project.png" in package.namelist()
listing = json.loads((root / "dist/index.json").read_text(encoding="utf-8"))
assert "Optimize-Your-Project/index.json" in listing["url"]
env.pop("GITHUB_REF_NAME", None)
subprocess.run([sys.executable, "scripts/build_blender.py"], cwd=root, env=env, check=True)
print("Static release checks passed; Blender and Unity runtime tests still required.")
