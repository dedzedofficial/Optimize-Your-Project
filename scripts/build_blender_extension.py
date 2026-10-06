"""Build the Blender 4.2+ Extensions ZIP."""
from pathlib import Path
import tomllib
import zipfile

root = Path(__file__).resolve().parents[1]
manifest_path = root / "blender_manifest.toml"
manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
version = manifest["version"]

required = [
    root / "blender_manifest.toml",
    root / "__init__.py",
    root / "Blender" / "__init__.py",
    root / "Blender" / "EXTENSION_LICENSE.txt",
    root / "Blender" / "vr_optimizer_blender" / "__init__.py",
    root / "Blender" / "vr_optimizer_blender" / "deform_transfer.py",
    root / "Blender" / "vr_optimizer_blender" / "tools_42.py",
    root / "Blender" / "vr_optimizer_blender" / "optimize-your-project-logo.png",
]
for path in required:
    if not path.is_file():
        raise SystemExit(f"Missing Blender extension file: {path.relative_to(root)}")

out = root / "dist"
out.mkdir(exist_ok=True)
archive = out / f"optimize-your-project-blender-extension-{version}.zip"

with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as package:
    for path in required:
        package.write(path, path.relative_to(root))

with zipfile.ZipFile(archive) as package:
    if package.testzip() is not None:
        raise SystemExit("Blender extension ZIP integrity check failed")
    names = set(package.namelist())
    for required_name in [
        "blender_manifest.toml",
        "__init__.py",
        "Blender/__init__.py",
        "Blender/EXTENSION_LICENSE.txt",
        "Blender/vr_optimizer_blender/__init__.py",
        "Blender/vr_optimizer_blender/deform_transfer.py",
        "Blender/vr_optimizer_blender/tools_42.py",
        "Blender/vr_optimizer_blender/optimize-your-project-logo.png",
    ]:
        if required_name not in names:
            raise SystemExit(f"Missing extension member: {required_name}")

print(archive)
