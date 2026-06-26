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
    size = full.stat().st_size if exists == "PASS" else 0
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
from lib.frontmatter import parse_toml_frontmatter, extract_frontmatter_field

for p in new_patterns:
    fm = parse_toml_frontmatter(root / p)
    if fm:
        pid = extract_frontmatter_field(fm, "id") or "MISSING"
        mat = extract_frontmatter_field(fm, "maturity") or "MISSING"
        src = extract_frontmatter_field(fm, "source") or "MISSING"
        has_methodology = "methodology-analysis-report.md" in src
        valid_maturity = mat in {"L0", "L1", "L2", "L3", "L4"}
        is_valid = has_methodology and pid != "MISSING" and mat != "MISSING" and valid_maturity
        print(f"  [{'PASS' if is_valid else 'FAIL'}] {Path(p).name}: id={pid}, maturity={mat}{' (invalid)' if mat != 'MISSING' and not valid_maturity else ''}, source has methodology-analysis-report.md: {has_methodology}")
    else:
        print(f"  [FAIL] {Path(p).name}: TOML frontmatter not found")
