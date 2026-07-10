"""分析 frontmatter source 字段指向缺失文件的情况。

扫描所有 .md 文件和对应的 .toml 文件，检查 source 字段指向的文件是否存在。
输出缺失文件的 source 字段列表，用于手动修复决策。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / ".agents" / "scripts"))
from lib.frontmatter import parse_frontmatter_unified


def analyze():
    docs = ROOT / "docs"
    missing = []
    scanned = 0
    for md in docs.rglob("*.md"):
        scanned += 1
        try:
            meta = parse_frontmatter_unified(md)
        except Exception:
            continue
        if not meta:
            continue
        source = meta.get("source")
        if not source or not isinstance(source, str):
            continue
        # Skip external references
        if source.startswith("external:") or source.startswith("http"):
            continue
        # Extract path (before anchor)
        path_str = source.split("#")[0]
        if not path_str:
            continue
        # Check if file exists
        target = (md.parent / path_str).resolve()
        if not target.exists():
            missing.append({
                "md_file": str(md.relative_to(ROOT)),
                "source": source,
                "target": str(target),
                "in_toml": "x-toml-ref" in meta,
            })
    print(f"扫描 {scanned} 个 md 文件")
    print(f"缺失 source 目标: {len(missing)} 个")
    print()
    for item in missing:
        print(f"  {item['md_file']}")
        print(f"    source: {item['source'][:80]}")
        print()


if __name__ == "__main__":
    analyze()
