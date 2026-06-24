#!/usr/bin/env python3
"""原子化完成度验证脚本"""
from pathlib import Path

root = Path(".")

# 1. 验证 8 个新模式文件存在
new_patterns = [
    "docs/retrospective/patterns/methodology-patterns/retrospective-four-step-method.md",
    "docs/retrospective/patterns/methodology-patterns/insight-iceberg-model.md",
    "docs/retrospective/patterns/methodology-patterns/extraction-four-layer-funnel.md",
    "docs/retrospective/patterns/methodology-patterns/export-four-channel-progressive.md",
    "docs/retrospective/patterns/methodology-patterns/atomization-three-criteria-test.md",
    "docs/retrospective/patterns/methodology-patterns/modularization-interface-design.md",
    "docs/retrospective/patterns/methodology-patterns/closed-loop-pdca-mapping.md",
    "docs/retrospective/patterns/methodology-patterns/methodology-five-level-maturity.md",
]
print("=== 1. 8 new pattern files ===")
for p in new_patterns:
    full = root / p
    exists = "PASS" if full.exists() else "FAIL"
    size = full.stat().st_size if full.exists() else 0
    print(f"  [{exists}] {p}  ({size} bytes)")

# 2. 验证 README 索引更新
print()
print("=== 2. Index updates ===")
readme = (root / "docs/retrospective/patterns/methodology-patterns/README.md").read_text(encoding="utf-8")
for p in new_patterns:
    name = Path(p).name
    in_readme = "PASS" if name in readme else "FAIL"
    print(f"  [{in_readme}] methodology-patterns/README.md contains {name}")

patterns_readme = (root / "docs/retrospective/patterns/README.md").read_text(encoding="utf-8")
expected = "methodology-patterns/ | 44"
in_stats = "PASS" if expected in patterns_readme else "FAIL"
print(f"  [{in_stats}] patterns/README.md statistics updated to 44")

# 3. 验证源文档降级
print()
print("=== 3. Source document downgrade ===")
source = root / "docs/methodology-analysis-report.md"
src_content = source.read_text(encoding="utf-8")
src_lines = len(src_content.splitlines())
print(f"  Source file lines: {src_lines} (original: 740)")

checks = [
    ("contains '已原子化至' marker", "已原子化至" in src_content),
    ("contains '已有模式覆盖' marker", "已有模式覆盖" in src_content),
    ("contains downgrade notice", "本文档已原子化拆分" in src_content),
    ("contains chapter-pattern mapping table", "章节→权威模式映射" in src_content),
]
for desc, ok in checks:
    print(f"  [{'PASS' if ok else 'FAIL'}] {desc}")

# 4. 验证 8 个模式的 TOML frontmatter
print()
print("=== 4. TOML frontmatter validation ===")
import re
TOML_ID_RE = re.compile(r'^\+\+\+\s*\n(.*?)\n\+\+\+', re.DOTALL)
ID_RE = re.compile(r'^id\s*=\s*"([^"]+)"', re.MULTILINE)
MATURITY_RE = re.compile(r'^maturity\s*=\s*"(L\d)"', re.MULTILINE)
SOURCE_RE = re.compile(r'^source\s*=\s*"([^"]+)"', re.MULTILINE)

for p in new_patterns:
    content = (root / p).read_text(encoding="utf-8")
    m = TOML_ID_RE.match(content)
    if m:
        fm = m.group(1)
        id_match = ID_RE.search(fm)
        mat_match = MATURITY_RE.search(fm)
        src_match = SOURCE_RE.search(fm)
        pid = id_match.group(1) if id_match else "MISSING"
        mat = mat_match.group(1) if mat_match else "MISSING"
        src = src_match.group(1) if src_match else "MISSING"
        has_methodology = "methodology-analysis-report.md" in src
        print(f"  [{'PASS' if has_methodology and pid != 'MISSING' else 'FAIL'}] {Path(p).name}: id={pid}, maturity={mat}, source has methodology-analysis-report.md: {has_methodology}")
    else:
        print(f"  [FAIL] {Path(p).name}: TOML frontmatter not found")
