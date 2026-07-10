"""分析 frontmatter 路径问题的分类统计。"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / ".agents" / "scripts"))

import importlib.util

_spec = importlib.util.spec_from_file_location("check_links", ROOT / ".agents" / "scripts" / "check-links.py")
check_links = importlib.util.module_from_spec(_spec)
sys.modules["check_links"] = check_links
_spec.loader.exec_module(check_links)
check_frontmatter_paths = check_links.check_frontmatter_paths
from lib.markdown import find_markdown_files

docs = ROOT / "docs"
md_files = find_markdown_files(docs)
broken = check_frontmatter_paths(md_files)

docs_prefix = [b for b in broken if "docs/绝对路径前缀" in b[3] or "docs/前缀" in b[3]]
missing_file = [b for b in broken if "文件不存在" in b[3]]

print(f"Total frontmatter issues: {len(broken)}")
print(f"  docs/ prefix: {len(docs_prefix)}")
print(f"  missing file: {len(missing_file)}")
print()

# Show docs/ prefix issues
if docs_prefix:
    print("=== docs/ prefix issues ===")
    for md_path, field, value, error in docs_prefix[:15]:
        rel = md_path.relative_to(ROOT)
        print(f"  {rel}: {value[:70]}")
    if len(docs_prefix) > 15:
        print(f"  ... and {len(docs_prefix) - 15} more")
    print()

# Show missing file issues by directory
if missing_file:
    print("=== missing file issues (by directory) ===")
    dirs = {}
    for md_path, field, value, error in missing_file:
        rel = md_path.relative_to(ROOT)
        dir_key = str(rel.parent)
        if dir_key not in dirs:
            dirs[dir_key] = []
        dirs[dir_key].append(value[:70])
    for dir_key, values in sorted(dirs.items()):
        print(f"  {dir_key} ({len(values)} issues)")
        for v in values[:3]:
            print(f"    - {v}")
        if len(values) > 3:
            print(f"    ... and {len(values) - 3} more")
