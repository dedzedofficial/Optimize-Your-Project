"""Build the Blender add-on ZIP for a blender-vX.Y.Z release tag."""
import ast
import os
from pathlib import Path
import py_compile
import zipfile

root = Path(__file__).resolve().parents[1]
addon = root / "Blender" / "vr_optimizer_blender"
source = addon / "__init__.py"
tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
info = next(
    ast.literal_eval(node.value)
    for node in tree.body
    if isinstance(node, ast.Assign)
    and any(isinstance(target, ast.Name) and target.id == "bl_info" for target in node.targets)
)
version = ".".join(map(str, info["version"]))
tag = os.environ.get("GITHUB_REF_NAME", "blender-v" + version)
if tag != "blender-v" + version:
    raise SystemExit(f"Tag {tag} does not match Blender add-on version {version}")
py_compile.compile(str(source), doraise=True)

out = root / "dist"
out.mkdir(exist_ok=True)
archive = out / f"optimize-your-project-blender-{version}.zip"
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as package:
    for path in sorted(addon.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            package.write(path, path.relative_to(root / "Blender"))
with zipfile.ZipFile(archive) as package:
    if package.testzip():
        raise SystemExit("Blender ZIP integrity check failed")
    if "vr_optimizer_blender/__init__.py" not in package.namelist():
        raise SystemExit("Blender add-on entry point is missing")
print(archive)
