#!/usr/bin/env python3
"""
版本涟漪效应检测器 (Version Ripple Detector)

检测模式/模板更新后，下游文档中残留的旧版引用。
设计哲学：高确定性规则零误报，模糊匹配仅作提示(warn)；递归自举验证先行。

检测机制：
1. 废弃短语检测：直接检测非历史上下文中的旧版描述（如"7类9项"）
2. 配对模式检测："X类可复用资产...Y项增强验证"同时出现时检查数字
3. Step 5上下文检测："Step 5 ... N项验证"
4. frontmatter-TOML双星同步：检查.md frontmatter与对应_meta TOML值是否一致
5. 自动发现模式（--auto-discover）：扫描关键词数字变体，人工确认
6. 递归自举验证（--bootstrap）：验证脚本自身权威值与源文件一致、其他脚本无旧版引用

用法：
    python .agents/scripts/check-version-ripple.py [--root DIR] [--auto-discover] [--bootstrap]

退出码：
    0 - 无error级涟漪
    1 - 发现error级涟漪（或自举验证失败）
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "vendor", ".trae"}
MD_EXTS = {".md", ".mdx"}

HISTORY_MARKER_PATTERN = re.compile(
    r'(?:初版|最初|之前|旧版|原为|仅覆盖|只覆盖|遗漏了|扩展为|升级为|更新为'
    r'|仍写|仍描述|发现\d+处|历史版本|v1|早期版本|原本|原先'
    r'|从[^。\n]{0,10}(?:更新|升级|扩展|迁移|演变|改为|调整为))',
)

DEPRECATED_PHRASES = [
    (re.compile(r'7\s*类\s*(?:可复用)?资产[^。\n]{0,40}?9\s*项'), "7类9项（初版）"),
    (re.compile(r'9\s*项(?:增强)?验证[^。\n]{0,40}?7\s*类'), "9项7类（初版）"),
    (re.compile(r'7\s*类资产全覆盖'), "7类资产全覆盖（初版）"),
    (re.compile(r'8\s*类\s*(?:可复用)?资产[^。\n\d]{0,50}?11\s*项(?:增强)?验证'), "8类11项（上一版，已扩展为12项）"),
    (re.compile(r'11\s*项(?:增强)?验证[^。\n\d]{0,50}?8\s*类'), "11项8类（上一版，已扩展为12项）"),
]

PAIRED_PATTERN = re.compile(
    r'(\d+)\s*类\s*可复用资产[^。\n\d]{0,50}(\d+)\s*项(?:增强)?验证'
)

STEP5_VERIFY_PATTERN = re.compile(
    r'Step\s*5[^。\n\d]{0,50}(\d+)\s*项(?:增强)?验证',
    re.IGNORECASE,
)

CANONICAL_ASSET_COUNT = 8
CANONICAL_VERIFY_COUNT = 12
CANONICAL_SOURCE = ".agents/docs/retrospective/patterns/methodology-patterns/ai-collaboration/edit-verify-separation.md"


@dataclass
class RippleHit:
    rule_name: str
    file_path: Path
    line_no: int
    found_value: str
    expected_value: str
    line_content: str
    severity: str = "error"


@dataclass
class VersionVariant:
    keyword: str
    values: dict[str, list[tuple[Path, int, str]]] = field(default_factory=dict)


def is_historical_context(line: str, match_start: int) -> bool:
    before = line[:match_start]
    return bool(HISTORY_MARKER_PATTERN.search(before))


def extract_frontmatter(text: str) -> tuple[dict[str, str], int]:
    if not text.startswith("---\n"):
        return {}, 0
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, 0
    fm_text = text[4:end]
    result: dict[str, str] = {}
    for line in fm_text.splitlines():
        if ":" in line and not line.strip().startswith("#"):
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if value:
                result[key] = value
    return result, end + 5


def _compute_expected_toml_rel(md_path: Path) -> str:
    project_root = Path(__file__).resolve().parent.parent.parent
    try:
        rel_path = md_path.resolve().relative_to(project_root).as_posix()
    except ValueError:
        return "(路径解析失败)"
    toml_rel = '.meta/toml/' + rel_path.replace('.md', '.toml')
    parent_depth = len(Path(rel_path).parent.parts)
    if parent_depth == 0:
        return toml_rel
    return '../' * parent_depth + toml_rel


def scan_file(file_path: Path) -> list[RippleHit]:
    hits: list[RippleHit] = []
    try:
        content = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return hits

    lines = content.splitlines()
    fm, _ = extract_frontmatter(content)

    for line_no, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("http") or stripped.startswith("```") or stripped.startswith("<!--"):
            continue

        for dep_pat, label in DEPRECATED_PHRASES:
            for m in dep_pat.finditer(line):
                if is_historical_context(line, m.start()):
                    continue
                snippet = line[max(0, m.start()-10):m.end()+10].strip()
                hits.append(RippleHit(
                    rule_name=f"旧版残留: {label}",
                    file_path=file_path,
                    line_no=line_no,
                    found_value=m.group(0),
                    expected_value=f"应更新为{CANONICAL_ASSET_COUNT}类{CANONICAL_VERIFY_COUNT}项，或加入历史叙述标记（如「初版」「从X更新为」）",
                    line_content=stripped,
                    severity="error",
                ))

        m = PAIRED_PATTERN.search(line)
        if m and not is_historical_context(line, m.start()):
            asset_v, verify_v = m.group(1), m.group(2)
            if asset_v != str(CANONICAL_ASSET_COUNT):
                hits.append(RippleHit(
                    rule_name="资产类别数不一致",
                    file_path=file_path,
                    line_no=line_no,
                    found_value=asset_v,
                    expected_value=str(CANONICAL_ASSET_COUNT),
                    line_content=stripped,
                    severity="error",
                ))
            if verify_v != str(CANONICAL_VERIFY_COUNT):
                hits.append(RippleHit(
                    rule_name="验证项数不一致",
                    file_path=file_path,
                    line_no=line_no,
                    found_value=verify_v,
                    expected_value=str(CANONICAL_VERIFY_COUNT),
                    line_content=stripped,
                    severity="error",
                ))

        for m in STEP5_VERIFY_PATTERN.finditer(line):
            if is_historical_context(line, m.start()):
                continue
            v = m.group(1)
            if v != str(CANONICAL_VERIFY_COUNT):
                hits.append(RippleHit(
                    rule_name="Step 5验证项数不一致",
                    file_path=file_path,
                    line_no=line_no,
                    found_value=v,
                    expected_value=str(CANONICAL_VERIFY_COUNT),
                    line_content=stripped,
                    severity="error",
                ))

    def _should_require_toml_ref(fpath: Path, frontmatter: dict) -> bool:
        rel_str = str(fpath.as_posix())
        if "TEMPLATE" in fpath.name or "template" in fpath.name.lower():
            return False
        if "example" in rel_str.lower():
            return False
        if "SKILL-TEMPLATE" in rel_str:
            return False
        if fpath.name.lower() == "readme.md":
            return bool(frontmatter.get("id")) and bool(frontmatter.get("title"))
        if frontmatter.get("id") and frontmatter.get("title"):
            return True
        return False

    if tomllib and fm:
        if "x-toml-ref" in fm:
            toml_rel = fm["x-toml-ref"]
            toml_path = (file_path.parent / toml_rel).resolve()
            if not toml_path.exists():
                expected_rel = _compute_expected_toml_rel(file_path)
                hits.append(RippleHit(
                    rule_name="TOML双星断裂: x-toml-ref指向不存在文件",
                    file_path=file_path,
                    line_no=1,
                    found_value=toml_rel,
                    expected_value=f"路径应为: {expected_rel}，或运行fix-x-toml-ref.py自动修复",
                    line_content="(TOML文件不存在)",
                    severity="error",
                ))
            else:
                try:
                    with open(toml_path, "rb") as f:
                        toml_data = tomllib.load(f)
                    meta = toml_data.get("meta", {})
                    for field_name in ("reuse_count", "validation_count"):
                        toml_val = meta.get(field_name)
                        fm_val = fm.get(field_name)
                        if fm_val is not None and toml_val is not None:
                            if str(toml_val) != str(fm_val):
                                hits.append(RippleHit(
                                    rule_name=f"TOML双星漂移: {field_name}",
                                    file_path=file_path,
                                    line_no=1,
                                    found_value=f"frontmatter={fm_val}, toml={toml_val}",
                                    expected_value="两者应一致",
                                    line_content=f"(TOML: {toml_path.name})",
                                    severity="error",
                                ))
                    toml_id = toml_data.get("id")
                    fm_id = fm.get("id")
                    if toml_id and fm_id:
                        toml_id_clean = str(toml_id).strip('"\'').strip()
                        fm_id_clean = str(fm_id).strip('"\'').strip()
                        if toml_id_clean != fm_id_clean:
                            hits.append(RippleHit(
                                rule_name="TOML双星漂移: id",
                                file_path=file_path,
                                line_no=1,
                                found_value=f"frontmatter={fm_id}, toml={toml_id}",
                                expected_value="两者id应一致（id是唯一标识符，必须完全匹配）",
                                line_content=f"(TOML: {toml_path.name})",
                                severity="error",
                            ))
                except Exception:
                    pass
        elif _should_require_toml_ref(file_path, fm):
            expected_rel = _compute_expected_toml_rel(file_path)
            hits.append(RippleHit(
                rule_name="TOML双星缺失: 缺少x-toml-ref字段",
                file_path=file_path,
                line_no=1,
                found_value="(无x-toml-ref)",
                expected_value=f"添加 x-toml-ref: \"{expected_rel}\"，或运行fix-x-toml-ref.py自动修复",
                line_content="(frontmatter有id+title但缺少x-toml-ref)",
                severity="warn",
            ))

    return hits


def auto_discover(root: Path) -> list[VersionVariant]:
    keywords = [
        ("类可复用资产", re.compile(r"(\d+)\s*类\s*可复用资产")),
        ("项增强验证", re.compile(r"(\d+)\s*项\s*增强验证")),
    ]
    variants: dict[str, VersionVariant] = {}
    for kw_name, _ in keywords:
        variants[kw_name] = VersionVariant(keyword=kw_name)

    for file_path in collect_markdown_files(root):
        try:
            content = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for line_no, line in enumerate(content.splitlines(), start=1):
            for kw_name, pattern in keywords:
                for m in pattern.finditer(line):
                    if is_historical_context(line, m.start()):
                        continue
                    val = m.group(1)
                    if val not in variants[kw_name].values:
                        variants[kw_name].values[val] = []
                    variants[kw_name].values[val].append((file_path, line_no, line.strip()[:100]))
    return list(variants.values())


def collect_markdown_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for p in root.rglob("*"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.is_file() and p.suffix.lower() in MD_EXTS:
            files.append(p)
    return sorted(files)


def format_hits(hits: list[RippleHit]) -> str:
    if not hits:
        return "  ✅ 未发现版本涟漪。\n"
    errors = [h for h in hits if h.severity == "error"]
    warns = [h for h in hits if h.severity == "warn"]
    lines = [f"  发现 {len(hits)} 处版本涟漪（{len(errors)} 错误, {len(warns)} 警告）:\n"]
    by_rule: dict[str, list[RippleHit]] = {}
    for h in hits:
        by_rule.setdefault(h.rule_name, []).append(h)
    for rule_name, rule_hits in by_rule.items():
        icon = "🔴" if rule_hits[0].severity == "error" else "🟡"
        lines.append(f"  ▸ {rule_name}")
        for h in rule_hits[:20]:
            try:
                rel = h.file_path.relative_to(Path.cwd()) if h.file_path.is_absolute() else h.file_path
            except ValueError:
                rel = h.file_path
            lines.append(f"    {icon} {rel}:{h.line_no}  找到\"{h.found_value}\"，应为\"{h.expected_value}\"")
            if h.line_content:
                lines.append(f"       {h.line_content[:120]}")
        if len(rule_hits) > 20:
            lines.append(f"       ... 还有 {len(rule_hits) - 20} 处")
        lines.append("")
    return "\n".join(lines)


def format_auto_discover(variants: list[VersionVariant]) -> str:
    lines = ["\n  🔍 自动发现模式（数字变体分布，人工确认）:"]
    found_any = False
    for v in variants:
        if len(v.values) > 1:
            found_any = True
            lines.append(f"\n  ▸ 关键词「{v.keyword}」出现多个数值:")
            for val, occurrences in sorted(v.values.items(), key=lambda x: -len(x[1])):
                files = len({occ[0] for occ in occurrences})
                lines.append(f"    {val} → {len(occurrences)}次（{files}个文件）")
                for fp, ln, content in occurrences[:3]:
                    rel = fp.relative_to(Path.cwd()) if fp.is_absolute() else fp
                    lines.append(f"      - {rel}:{ln}  {content[:80]}")
    if not found_any:
        lines.append("  ✅ 所有关键词数值一致，无异常变体。")
    return "\n".join(lines)


def bootstrap_self_check(script_path: Path) -> list[str]:
    """递归自举验证：检查脚本自身的一致性"""
    issues: list[str] = []
    script_dir = script_path.parent
    project_root = script_dir.parent.parent

    source_path = project_root / CANONICAL_SOURCE
    if not source_path.exists():
        issues.append(f"权威源文件不存在: {CANONICAL_SOURCE}")
        return issues

    try:
        source_content = source_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        issues.append(f"无法读取权威源文件: {e}")
        return issues

    asset_section = re.search(
        r"(\d+)\s*类\s*(?:完整清单|可复用资产)",
        source_content,
    )
    verify_section = re.search(
        r"验证增强项[（(](\d+)\s*项",
        source_content,
    )
    if asset_section:
        actual_asset = int(asset_section.group(1))
        if actual_asset != CANONICAL_ASSET_COUNT:
            issues.append(
                f"CANONICAL_ASSET_COUNT={CANONICAL_ASSET_COUNT}与权威源实际值{actual_asset}不一致"
            )
    else:
        issues.append("无法从权威源文件提取资产类别数，正则可能过时")

    if verify_section:
        actual_verify = int(verify_section.group(1))
        if actual_verify != CANONICAL_VERIFY_COUNT:
            issues.append(
                f"CANONICAL_VERIFY_COUNT={CANONICAL_VERIFY_COUNT}与权威源实际值{actual_verify}不一致"
            )
    else:
        issues.append("无法从权威源文件提取验证项数，正则可能过时")

    deprecated_in_scripts = re.compile(
        r'(?:7\s*类\s*(?:可复用)?资产|9\s*项(?:增强)?验证|7\s*类资产全覆盖'
        r'|8\s*类[^。\n]{0,20}11\s*项(?:增强)?验证|11\s*项增强验证)'
    )
    history_py = re.compile(
        r'(?:初版|旧版|历史|deprecated|obsolete|原为|从\d+类|上一版|v1|早期)',
        re.IGNORECASE,
    )
    for py_file in script_dir.glob("*.py"):
        if py_file == script_path:
            continue
        try:
            content = py_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for line_no, line in enumerate(content.splitlines(), start=1):
            if deprecated_in_scripts.search(line) and not history_py.search(line):
                rel = py_file.relative_to(project_root)
                issues.append(f"{rel}:{line_no} Python脚本中存在旧版版本引用: {line.strip()[:80]}")

    return issues


def main():
    parser = argparse.ArgumentParser(description="版本涟漪效应检测器")
    parser.add_argument("--root", default=".agents/docs/retrospective", help="扫描根目录")
    parser.add_argument("--auto-discover", action="store_true", help="启用自动发现模式")
    parser.add_argument("--bootstrap", action="store_true", help="递归自举验证（检查脚本自身一致性）")
    args = parser.parse_args()

    if args.bootstrap:
        print(f"{'='*60}")
        print("递归自举验证 (Bootstrap Self-Check)")
        print(f"{'='*60}")
        script_path = Path(__file__).resolve()
        issues = bootstrap_self_check(script_path)
        if issues:
            print(f"  🔴 发现 {len(issues)} 个自举问题:\n")
            for i, issue in enumerate(issues, 1):
                print(f"    {i}. {issue}")
            print(f"\n{'='*60}")
            print("  自举验证失败，请修复后再使用。")
            sys.exit(1)
        else:
            print("  ✅ 自举验证通过：权威值与源文件一致，脚本无旧版引用。")
            print(f"{'='*60}")
            print()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"错误：目录不存在: {root}", file=sys.stderr)
        sys.exit(2)

    print(f"{'='*60}")
    print(f"版本涟漪检测: {root.relative_to(Path.cwd()) if root.is_relative_to(Path.cwd()) else root}")
    print(f"{'='*60}")

    files = collect_markdown_files(root)
    print(f"  扫描文件: {len(files)} 个Markdown文件")
    print(f"  权威值: {CANONICAL_ASSET_COUNT}类可复用资产 / {CANONICAL_VERIFY_COUNT}项增强验证")
    print(f"  来源: {CANONICAL_SOURCE}")
    print()

    all_hits: list[RippleHit] = []
    for fp in files:
        all_hits.extend(scan_file(fp))

    print(format_hits(all_hits))

    if args.auto_discover:
        variants = auto_discover(root)
        print(format_auto_discover(variants))

    errors = [h for h in all_hits if h.severity == "error"]
    print(f"{'='*60}")
    print(f"检查摘要: 错误 {len(errors)} 项")
    if errors:
        print("  💡 修复建议：")
        print("     1. 正文中的旧版数字 → 更新为当前权威值")
        print("     2. 历史叙述 → 在前面加入「初版」「从X更新为」等标记词")
        print("     3. TOML双星漂移 → 同步更新.md frontmatter和_meta.toml")
        sys.exit(1)
    else:
        print("  ✅ 版本一致，无涟漪效应。")
        sys.exit(0)


if __name__ == "__main__":
    main()
