from pathlib import Path
from typing import Optional


def find_pattern_files(root, patterns_dir, target_path=None):
    pattern_files = []
    exclude_names = {"README.md", "CATEGORIES.md"}

    if target_path:
        if target_path.is_file() and target_path.suffix == ".md" and target_path.name not in exclude_names:
            return [target_path]
        if target_path.is_dir():
            for f in target_path.rglob("*.md"):
                if f.name not in exclude_names:
                    pattern_files.append(f)
            return sorted(pattern_files)
        return []

    if not patterns_dir.exists():
        return []

    for category_dir in patterns_dir.iterdir():
        if not category_dir.is_dir() or category_dir.name.startswith("."):
            continue
        for f in category_dir.rglob("*.md"):
            if f.name in exclude_names:
                continue
            pattern_files.append(f)

    return sorted(pattern_files)
