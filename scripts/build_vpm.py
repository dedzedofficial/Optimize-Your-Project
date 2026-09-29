"""Build a VPM listing and package ZIP for a tagged release."""
import json
import os
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parents[1]
out = root / 'dist'
out.mkdir(exist_ok=True)
manifest = json.loads((root / 'package.json').read_text())
version = manifest['version']
tag = os.environ.get('GITHUB_REF_NAME', 'v' + version)
if tag != 'v' + version:
    raise SystemExit(f'Tag {tag} does not match package version {version}')
name = manifest['name']
archive = f'{name}-{version}.zip'
url = f'https://github.com/dedzedofficial/Optimize-Your-Project/releases/download/{tag}/{archive}'
with zipfile.ZipFile(out / archive, 'w', zipfile.ZIP_DEFLATED) as zip_file:
    for path in [root / 'package.json', *sorted((root / 'Editor').rglob('*'))]:
        if path.is_file():
            zip_file.write(path, path.relative_to(root))
listing = {
    'name': 'Optimize Your Project',
    'id': 'com.fishhwb.vr-optimizer.repo',
    'url': 'https://dedzedofficial.github.io/Optimize-Your-Project/index.json',
    'author': 'FISHHWB | Ded Zed',
    'packages': {name: {'versions': {version: {**manifest, 'url': url}}}},
}
(out / 'index.json').write_text(json.dumps(listing, indent=2) + '\n')
