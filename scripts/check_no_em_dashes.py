"""Reject em dash punctuation anywhere in tracked text files.

Use ordinary commas, colons, periods, or hyphens instead. This check scans
source code, documentation, configuration, and Unity metadata without editing
files. Non-UTF-8 binary assets are skipped.
"""
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
EM_DASH = chr(0x2014)


def tracked_paths(root):
    try:
        output = subprocess.check_output(
            ["git", "-C", str(root), "ls-files", "-z"],
            stderr=subprocess.DEVNULL,
        )
        return [root / part.decode("utf-8")
                for part in output.split(bytes([0])) if part]
    except (FileNotFoundError, subprocess.CalledProcessError):
        # Also support an exported source tree without its Git metadata.
        ignored = {".git", ".venv", "venv", "__pycache__", "dist", "build"}
        return [path for path in root.rglob("*")
                if path.is_file()
                and not any(part in ignored for part in path.relative_to(root).parts)]


def find_em_dashes(root=ROOT, paths=None):
    """Return all violations as (relative path, line number, count)."""
    violations = []
    if paths is None:
        paths = tracked_paths(root)
    for path in paths:
        if not path.is_file():
            continue
        try:
            contents = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            # Images and binary assets cannot contain editable text punctuation.
            continue
        for line_number, line in enumerate(contents.splitlines(), 1):
            count = line.count(EM_DASH)
            if count:
                violations.append((str(path.relative_to(root)), line_number, count))
    return violations


def main():
    paths = tracked_paths(ROOT)
    violations = find_em_dashes(ROOT, paths)
    if violations:
        print("Em dashes are not permitted in repository text files.")
        for path, line_number, count in violations:
            print(f"  {path}:{line_number}: {count} em dash(es)")
        print("Use a hyphen, colon, comma, or full stop as appropriate.")
        return 1
    print(f"Em dash style check passed: {len(paths)} tracked files inspected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
