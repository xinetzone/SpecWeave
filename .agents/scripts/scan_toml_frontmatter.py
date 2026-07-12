"""TOML frontmatter 基线扫描脚本。

递归扫描项目下所有 *.md 文件，识别 TOML frontmatter（+++ ... +++），
提取字段信息并生成基线清单 JSON，用于后续 TOML→YAML 迁移的一致性验证。
"""

import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from lib.atomic_write import atomic_write_json

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
EXCLUDE_DIRS = {".git", "vendor", ".temp", "__pycache__", "node_modules", ".venv"}
FRONTMATTER_RE = re.compile(r"^\+\+\+\s*\n(.*?)\n\+\+\+\s*$", re.MULTILINE | re.DOTALL)
FIELD_RE = re.compile(r'^(\w+)\s*=\s*(?:"([^"]*)"|(\S+))\s*$', re.MULTILINE)


def parse_toml_fields(fm_text: str) -> dict[str, str]:
    result = {}
    for m in FIELD_RE.finditer(fm_text):
        key = m.group(1)
        value = m.group(2) if m.group(2) is not None else m.group(3)
        result[key] = value
    return result


def scan_md_files(root: Path) -> list[dict]:
    files_data = []
    for md_path in sorted(root.rglob("*.md")):
        rel_parts = md_path.relative_to(root).parts
        if any(part in EXCLUDE_DIRS for part in rel_parts):
            continue
        try:
            content = md_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        m = FRONTMATTER_RE.match(content)
        if not m:
            continue
        fm_text = m.group(1)
        fields = parse_toml_fields(fm_text)
        fm_hash = hashlib.sha256(fm_text.encode("utf-8")).hexdigest()
        files_data.append({
            "rel_path": str(md_path.relative_to(root)).replace("\\", "/"),
            "fields": fields,
            "content_hash": fm_hash,
        })
    return files_data


def compute_stats(files_data: list[dict]) -> dict:
    dir_counts: dict[str, int] = defaultdict(int)
    field_counter: Counter = Counter()
    for entry in files_data:
        top_dir = entry["rel_path"].split("/")[0]
        dir_counts[top_dir] += 1
        for key in entry["fields"]:
            field_counter[key] += 1
    return {
        "total_files": len(files_data),
        "by_top_directory": dict(sorted(dir_counts.items())),
        "field_frequency": dict(field_counter.most_common()),
    }


def main():
    root = PROJECT_ROOT
    output_path = root / ".meta" / "baseline-manifest.json"

    print(f"Scanning {root} for TOML frontmatter files...")
    files_data = scan_md_files(root)
    stats = compute_stats(files_data)

    manifest = {
        "generated_at": __import__("datetime").datetime.now().isoformat(),
        "project_root": str(root),
        "stats": stats,
        "files": files_data,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(output_path, manifest, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"TOML Frontmatter Baseline Scan Summary")
    print(f"{'='*60}")
    print(f"Total files with TOML frontmatter: {stats['total_files']}")
    print(f"\nDistribution by top-level directory:")
    for d, cnt in stats["by_top_directory"].items():
        print(f"  {d}: {cnt}")
    print(f"\nTop 10 most frequent fields:")
    for i, (field, cnt) in enumerate(list(stats["field_frequency"].items())[:10], 1):
        print(f"  {i:2d}. {field}: {cnt}")
    print(f"\nManifest written to: {output_path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
