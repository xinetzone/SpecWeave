"""vendor 引用扫描模块。

扫描代码中对 vendor 目录的引用。
"""

from __future__ import annotations

from pathlib import Path

try:
    from constants import EXCLUDED_DIRS
except ImportError:
    EXCLUDED_DIRS = {".git", "vendor", ".venv", "__pycache__", "node_modules", ".temp"}


def _scan_refs(project_root: Path, vendor_dir: Path) -> dict[str, list[str]]:
    """扫描项目中所有对 vendor 路径的引用。"""
    refs: dict[str, list[str]] = {}
    vendor_name = vendor_dir.name
    exclude = EXCLUDED_DIRS | {vendor_name}
    exts = {
        ".py", ".js", ".ts", ".jsx", ".tsx", ".md", ".json", ".yaml", ".yml",
        ".toml", ".cfg", ".ini", ".ps1", ".sh", ".bat", ".cmd",
    }
    for f in project_root.rglob("*"):
        if not f.is_file():
            continue
        if any(part in exclude for part in f.parts):
            continue
        if f.suffix.lower() not in exts:
            continue
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
            file_refs = []
            for i, line in enumerate(content.splitlines(), 1):
                s = line.strip()
                if vendor_name in line:
                    if s.startswith("#") or s.startswith("//"):
                        continue
                    if "vendor/" in line or "vendor\\" in line or (vendor_name + "/") in line:
                        file_refs.append(f"L{i}: {s[:80]}")
            if file_refs:
                refs[str(f.relative_to(project_root))] = file_refs
        except (OSError, UnicodeDecodeError):
            continue
    return refs
