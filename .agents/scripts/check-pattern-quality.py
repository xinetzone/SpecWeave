#!/usr/bin/env python3
"""方法论模式质量检查器：验证 docs/retrospective/patterns/ 下的模式文档是否符合规范。

检查项基于模式文档规范：
  1. Frontmatter 完整性（TOML格式，id/domain/layer/maturity/source必需字段）
  2. 必要章节完整性（模式类型/成熟度/适用场景/问题背景/核心内容/检查清单/正例/反例/关联模式）
  3. 检查清单质量（包含- [ ]格式的可执行检查项）
  4. Why 解释覆盖率（关键规则有设计意图说明）
  5. 交叉引用完整性（与现有模式的关系章节存在）
  6. 文件长度合理性（建议80-300行）
  7. Mermaid 可视化（复杂模式建议包含流程图）
  8. 成熟度字段合法性（L1/L2/L3）

用法：
  python check-pattern-quality.py                     # 检查所有模式
  python check-pattern-quality.py --path <pattern-dir> # 检查指定目录
  python check-pattern-quality.py --json              # JSON格式输出
  python check-pattern-quality.py --score             # 仅输出质量评分(0-100)
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from lib.project import resolve_project_root
from lib.cli import print_pass, print_warn, print_error, print_header, print_summary, add_common_args, setup_safe_output
from lib.frontmatter import parse_toml_frontmatter, extract_frontmatter_field, extract_all_fields

PATTERNS_DIR = "docs/retrospective/patterns"
MIN_PATTERN_LINES = 50
MAX_PATTERN_LINES = 400
RECOMMENDED_MIN_LINES = 80
RECOMMENDED_MAX_LINES = 300

FRONTMATTER_REQUIRED_FIELDS = {"id", "domain", "layer", "maturity", "source"}
FRONTMATTER_RECOMMENDED_FIELDS = {"validation_count", "reuse_count", "documentation_level"}

REQUIRED_SECTIONS = {
    "模式类型": "pattern_type",
    "成熟度": "maturity",
    "适用场景": "applicable_scenarios",
    "问题背景": "problem_background",
}

RECOMMENDED_SECTIONS = {
    "核心规则": "core_rules",
    "核心要素": "core_elements",
    "解决方案": "solution",
    "核心内容": "core_content",
    "操作流程": "workflow",
    "决策速查": "decision_cheatsheet",
}

IMPORTANT_SECTIONS = {
    "实施检查清单": "checklist",
    "反例警示": "anti_patterns",
    "正例": "positive_examples",
    "与现有模式的关系": "related_patterns",
}

VALID_MATURITY_LEVELS = {"L1", "L2", "L3"}

WHY_EXPLANATION_PATTERN = re.compile(r">\s*\*\*为什么", re.MULTILINE)
CHECKLIST_ITEM_PATTERN = re.compile(r"^- \[ \]", re.MULTILINE)
SECTION_HEADER_PATTERN = re.compile(r"^##\s+(.+)$", re.MULTILINE)
MERMAID_PATTERN = re.compile(r"```mermaid", re.MULTILINE)
FILE_URL_PATTERN = re.compile(r"(?:\[[^\]]*\]\(|<)file:///[^)\s>]+(?:\)|>)", re.MULTILINE)
CROSS_REFERENCE_PATTERN = re.compile(r"(?:\[[^\]]*\]\(|<a[^>]*>|`)([^)`\s]+\.md)(?:\)|</a>|`)", re.MULTILINE)
ID_PATTERN = re.compile(r"^pattern-[a-z0-9-]+$")


@dataclass
class CheckResult:
    """单个检查项结果"""
    name: str
    passed: bool
    severity: str
    message: str
    line: Optional[int] = None


@dataclass
class PatternReport:
    """单个模式的完整检查报告"""
    pattern_path: Path
    pattern_id: str
    pattern_title: str
    results: list[CheckResult] = field(default_factory=list)
    score: int = 0

    @property
    def errors(self) -> list[CheckResult]:
        return [r for r in self.results if r.severity == "error" and not r.passed]

    @property
    def warnings(self) -> list[CheckResult]:
        return [r for r in self.results if r.severity == "warn" and not r.passed]

    @property
    def passes(self) -> list[CheckResult]:
        return [r for r in self.results if r.passed]


def find_pattern_files(root: Path, patterns_dir: Path, target_path: Optional[Path] = None) -> list[Path]:
    """发现所有模式.md文件（排除README.md、CATEGORIES.md等索引文件）"""
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


def check_frontmatter(pattern_md: Path, content: str, frontmatter_text: Optional[str]) -> list[CheckResult]:
    """检查Frontmatter完整性"""
    results = []

    if not frontmatter_text:
        results.append(CheckResult(
            name="frontmatter存在",
            passed=False,
            severity="error",
            message="缺少TOML frontmatter（+++分隔的元数据块）"
        ))
        return results

    results.append(CheckResult(
        name="frontmatter存在",
        passed=True,
        severity="error",
        message="TOML frontmatter存在"
    ))

    fields = extract_all_fields(frontmatter_text)

    pattern_id = fields.get("id", "")
    if pattern_id:
        id_valid = bool(ID_PATTERN.match(pattern_id))
        results.append(CheckResult(
            name="frontmatter.id格式",
            passed=id_valid,
            severity="warn",
            message=f"id格式正确（{pattern_id}）" if id_valid
            else f"id格式建议为'pattern-xxx'格式，当前为'{pattern_id}'"
        ))
    else:
        results.append(CheckResult(
            name="frontmatter.id格式",
            passed=False,
            severity="error",
            message="缺少id字段"
        ))

    for fname in FRONTMATTER_REQUIRED_FIELDS - {"id"}:
        value = fields.get(fname)
        passed = value is not None and len(str(value).strip()) > 0
        results.append(CheckResult(
            name=f"frontmatter.{fname}",
            passed=passed,
            severity="error",
            message=f"必需字段 '{fname}' {'存在' if passed else '缺失'}"
        ))

    maturity = fields.get("maturity", "")
    if maturity:
        maturity_valid = maturity in VALID_MATURITY_LEVELS
        results.append(CheckResult(
            name="frontmatter.maturity合法性",
            passed=maturity_valid,
            severity="error" if not maturity_valid else "info",
            message=f"成熟度等级'{maturity}'合法" if maturity_valid
            else f"成熟度等级'{maturity}'不合法，应为L1/L2/L3之一"
        ))

    for fname in FRONTMATTER_RECOMMENDED_FIELDS:
        value = fields.get(fname)
        passed = value is not None
        if not passed:
            results.append(CheckResult(
                name=f"frontmatter.{fname}",
                passed=False,
                severity="warn",
                message=f"建议字段 '{fname}' 缺失（用于成熟度追踪）"
            ))
        else:
            results.append(CheckResult(
                name=f"frontmatter.{fname}",
                passed=True,
                severity="warn",
                message=f"建议字段 '{fname}' 存在（值: {value}）"
            ))

    validation_count = fields.get("validation_count")
    reuse_count = fields.get("reuse_count")
    maturity = fields.get("maturity", "")
    if maturity == "L1":
        try:
            vc = int(validation_count) if validation_count else 0
            if vc < 1:
                results.append(CheckResult(
                    name="frontmatter.maturity_validation_consistency",
                    passed=False,
                    severity="warn",
                    message="L1模式应至少有1次验证（validation_count≥1）"
                ))
            else:
                results.append(CheckResult(
                    name="frontmatter.maturity_validation_consistency",
                    passed=True,
                    severity="info",
                    message=f"L1成熟度与验证次数一致（validation_count={vc}）"
                ))
        except (ValueError, TypeError):
            pass
    elif maturity == "L2":
        try:
            vc = int(validation_count) if validation_count else 0
            if vc < 2:
                results.append(CheckResult(
                    name="frontmatter.maturity_validation_consistency",
                    passed=False,
                    severity="warn",
                    message="L2模式应至少有2次验证（validation_count≥2）"
                ))
            else:
                results.append(CheckResult(
                    name="frontmatter.maturity_validation_consistency",
                    passed=True,
                    severity="info",
                    message=f"L2成熟度与验证次数一致（validation_count={vc}）"
                ))
        except (ValueError, TypeError):
            pass
    elif maturity == "L3":
        try:
            rc = int(reuse_count) if reuse_count else 0
            if rc < 1:
                results.append(CheckResult(
                    name="frontmatter.maturity_validation_consistency",
                    passed=False,
                    severity="warn",
                    message="L3模式应至少被复用1次（reuse_count≥1）"
                ))
            else:
                results.append(CheckResult(
                    name="frontmatter.maturity_validation_consistency",
                    passed=True,
                    severity="info",
                    message=f"L3成熟度与复用次数一致（reuse_count={rc}）"
                ))
        except (ValueError, TypeError):
            pass

    return results


def check_sections(content: str) -> list[CheckResult]:
    """检查必要章节完整性"""
    results = []
    section_headers = {m.group(1).strip(): m.start() for m in SECTION_HEADER_PATTERN.finditer(content)}
    section_names = set(section_headers.keys())

    for sec_name, sec_id in REQUIRED_SECTIONS.items():
        found = any(sec_name in name for name in section_names)
        results.append(CheckResult(
            name=f"sections.required.{sec_id}",
            passed=found,
            severity="error",
            message=f"包含必要章节「{sec_name}」" if found
            else f"缺少必要章节「{sec_name}」"
        ))

    core_found = False
    for sec_name, sec_id in RECOMMENDED_SECTIONS.items():
        if any(sec_name in name for name in section_names):
            core_found = True
            break
    results.append(CheckResult(
        name="sections.core_content",
        passed=core_found,
        severity="error",
        message="包含核心内容章节（核心规则/核心要素/解决方案/操作流程等）" if core_found
        else "缺少核心内容章节（应包含核心规则/核心要素/解决方案/操作流程之一）"
    ))

    for sec_name, sec_id in IMPORTANT_SECTIONS.items():
        found = any(sec_name in name for name in section_names)
        results.append(CheckResult(
            name=f"sections.important.{sec_id}",
            passed=found,
            severity="warn",
            message=f"包含重要章节「{sec_name}」" if found
            else f"建议补充「{sec_name}」章节（提高模式可复用性）"
        ))

    checklist_items = len(CHECKLIST_ITEM_PATTERN.findall(content))
    has_checklist_section = any("检查清单" in name for name in section_names)
    if has_checklist_section:
        checklist_ok = checklist_items >= 3
        results.append(CheckResult(
            name="sections.checklist_items",
            passed=checklist_ok,
            severity="warn",
            message=f"实施检查清单包含{checklist_items}个可执行检查项" if checklist_ok
            else f"检查清单只有{checklist_items}个项，建议至少3个可执行检查项（- [ ]格式）"
        ))
    else:
        results.append(CheckResult(
            name="sections.checklist_items",
            passed=False,
            severity="warn",
            message="无实施检查清单章节，跳过检查项计数"
        ))

    return results


def check_file_length(pattern_md: Path, content: str) -> list[CheckResult]:
    """检查文件长度合理性"""
    results = []
    lines = content.count("\n") + 1

    if lines < MIN_PATTERN_LINES:
        passed = False
        severity = "error"
        msg = f"文件仅{lines}行，过短可能内容不完整（建议≥{RECOMMENDED_MIN_LINES}行）"
    elif lines > MAX_PATTERN_LINES:
        passed = False
        severity = "warn"
        msg = f"文件{lines}行，过长建议考虑拆分（建议≤{RECOMMENDED_MAX_LINES}行）"
    elif lines < RECOMMENDED_MIN_LINES:
        passed = True
        severity = "warn"
        msg = f"文件{lines}行（建议≥{RECOMMENDED_MIN_LINES}行以保证完整性）"
    elif lines > RECOMMENDED_MAX_LINES:
        passed = True
        severity = "warn"
        msg = f"文件{lines}行（建议≤{RECOMMENDED_MAX_LINES}行以保持可读性）"
    else:
        passed = True
        severity = "info"
        msg = f"文件{lines}行（长度适中）"

    results.append(CheckResult(
        name="file.length",
        passed=passed,
        severity=severity,
        message=msg
    ))

    return results


def check_why_explanations(content: str) -> list[CheckResult]:
    """检查Why解释覆盖率"""
    results = []

    why_count = len(WHY_EXPLANATION_PATTERN.findall(content))
    has_why = why_count >= 1

    results.append(CheckResult(
        name="why.explanations",
        passed=has_why,
        severity="warn",
        message=f"包含{why_count}个Why设计意图解释" if has_why
        else "建议补充关键规则的Why解释（帮助理解设计意图和边界情况判断）"
    ))

    return results


def check_visualization(content: str) -> list[CheckResult]:
    """检查是否有Mermaid可视化"""
    results = []

    mermaid_count = len(MERMAID_PATTERN.findall(content))
    has_mermaid = mermaid_count >= 1

    results.append(CheckResult(
        name="visualization.mermaid",
        passed=has_mermaid,
        severity="info",
        message=f"包含{mermaid_count}个Mermaid可视化图表" if has_mermaid
        else "建议添加Mermaid流程图/决策树增强理解（非强制）"
    ))

    return results


def check_paths(content: str) -> list[CheckResult]:
    """检查路径规范"""
    results = []

    file_urls = FILE_URL_PATTERN.findall(content)
    has_file_url = len(file_urls) > 0
    results.append(CheckResult(
        name="paths.no_file_url",
        passed=not has_file_url,
        severity="error",
        message="无file:///绝对路径" if not has_file_url
        else f"发现{len(file_urls)}处file:///绝对路径（应使用相对路径）"
    ))

    return results


def check_cross_references(content: str) -> list[CheckResult]:
    """检查交叉引用"""
    results = []

    xref_count = len(CROSS_REFERENCE_PATTERN.findall(content))
    has_related_section = "与现有模式的关系" in content or "关联模式" in content or "相关模式" in content

    if has_related_section:
        xref_ok = xref_count >= 2
        results.append(CheckResult(
            name="cross_references.exist",
            passed=xref_ok,
            severity="warn",
            message=f"包含{xref_count}个模式交叉引用链接" if xref_ok
            else f"关联模式章节只有{xref_count}个链接，建议至少引用2个相关模式构建知识网络"
        ))
    else:
        results.append(CheckResult(
            name="cross_references.exist",
            passed=False,
            severity="warn",
            message="缺少「与现有模式的关系」章节，无法建立模式间知识网络"
        ))

    return results


def calculate_score(report: PatternReport) -> int:
    """计算质量评分（0-100）"""
    score = 100

    for r in report.results:
        if r.passed:
            continue
        if r.severity == "error":
            score -= 10
        elif r.severity == "warn":
            score -= 5
        elif r.severity == "info":
            score -= 1

    return max(0, min(100, score))


def check_pattern(pattern_md: Path, root: Path) -> PatternReport:
    """检查单个模式文档"""
    content = pattern_md.read_text(encoding="utf-8")
    frontmatter_text = parse_toml_frontmatter(pattern_md)

    fields = extract_all_fields(frontmatter_text) if frontmatter_text else {}
    pattern_id = fields.get("id", pattern_md.stem)

    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    pattern_title = title_match.group(1).strip() if title_match else pattern_md.stem

    report = PatternReport(
        pattern_path=pattern_md,
        pattern_id=pattern_id,
        pattern_title=pattern_title
    )

    report.results.extend(check_frontmatter(pattern_md, content, frontmatter_text))
    report.results.extend(check_sections(content))
    report.results.extend(check_file_length(pattern_md, content))
    report.results.extend(check_why_explanations(content))
    report.results.extend(check_visualization(content))
    report.results.extend(check_paths(content))
    report.results.extend(check_cross_references(content))

    report.score = calculate_score(report)
    return report


def print_pattern_report(report: PatternReport, root_dir: Path, verbose: bool = False) -> None:
    """打印单个模式检查结果"""
    try:
        rel_path = report.pattern_path.relative_to(root_dir)
    except (ValueError, IndexError):
        rel_path = report.pattern_path
    score_color = "\033[92m" if report.score >= 80 else "\033[93m" if report.score >= 60 else "\033[91m"
    reset = "\033[0m"
    print(f"\n  {score_color}【{report.pattern_id}】{report.score}分{reset} {report.pattern_title[:40]}")
    print(f"     ({rel_path})")

    for r in report.results:
        if r.passed and not verbose:
            continue
        if r.severity == "error" and not r.passed:
            print_error(f"    [FAIL] {r.name}: {r.message}")
        elif r.severity == "warn" and not r.passed:
            print_warn(f"    [WARN] {r.name}: {r.message}")
        elif verbose:
            if r.passed:
                print_pass(f"    [PASS] {r.name}: {r.message}")


def main() -> None:
    setup_safe_output()
    parser = argparse.ArgumentParser(
        description="方法论模式质量检查：验证docs/retrospective/patterns/下的模式文档符合规范"
    )
    add_common_args(parser)
    parser.add_argument("--score", action="store_true", help="仅输出质量评分")
    parser.add_argument("--verbose", "-v", action="store_true", help="显示通过项详情")
    parser.add_argument("--threshold", type=int, default=60, help="评分阈值（低于则退出码1，默认60）")
    args = parser.parse_args()

    root_dir = resolve_project_root(__file__)
    patterns_dir = root_dir / PATTERNS_DIR

    target_path = Path(args.path).resolve() if args.path else None
    pattern_files = find_pattern_files(root_dir, patterns_dir, target_path)

    if not pattern_files:
        msg = f"未找到模式文件（目录: {patterns_dir}）"
        if args.json:
            print(json.dumps({"error": msg, "patterns": []}, ensure_ascii=False, indent=2))
        else:
            print_error(msg)
        sys.exit(1)

    reports = [check_pattern(f, root_dir) for f in pattern_files]

    if args.json:
        output = {
            "patterns_dir": str(patterns_dir),
            "pattern_count": len(reports),
            "patterns": [
                {
                    "id": r.pattern_id,
                    "title": r.pattern_title,
                    "path": str(r.pattern_path.relative_to(root_dir)),
                    "score": r.score,
                    "errors": [{"name": res.name, "message": res.message} for res in r.errors],
                    "warnings": [{"name": res.name, "message": res.message} for res in r.warnings],
                    "pass_count": len(r.passes),
                }
                for r in reports
            ],
            "average_score": sum(r.score for r in reports) // len(reports) if reports else 0,
            "total_errors": sum(len(r.errors) for r in reports),
            "total_warnings": sum(len(r.warnings) for r in reports),
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    if args.score:
        for r in sorted(reports, key=lambda x: x.score):
            print(f"{r.pattern_id}: {r.score}  {r.pattern_title[:50]}")
        avg = sum(r.score for r in reports) // len(reports) if reports else 0
        print(f"\n平均: {avg}/100")
        failed = [r for r in reports if r.score < args.threshold]
        sys.exit(1 if failed else 0)

    print_header("方法论模式质量检查")
    print(f"  扫描目录: {patterns_dir}")
    print(f"  检查项: Frontmatter/必要章节/检查清单/Why解释/可视化/路径规范/交叉引用")
    print(f"  发现 {len(reports)} 个模式文件")

    for report in sorted(reports, key=lambda x: x.score):
        print_pattern_report(report, root_dir, verbose=args.verbose)

    total_errors = sum(len(r.errors) for r in reports)
    total_warnings = sum(len(r.warnings) for r in reports)
    total_passes = sum(len(r.passes) for r in reports)
    avg_score = sum(r.score for r in reports) // len(reports) if reports else 0

    print()
    print(f"  平均质量分: {avg_score}/100")
    print_summary(
        pass_count=total_passes,
        warn_count=total_warnings,
        error_count=total_errors,
    )

    if avg_score < args.threshold:
        print()
        print_warn(f"平均评分{avg_score}低于阈值{args.threshold}，建议根据上述改进项优化")
        print()
        print("改进指引：")
        print("  1. Frontmatter：补齐必需字段id/domain/layer/maturity/source")
        print("  2. 必要章节：模式类型/成熟度/适用场景/问题背景/核心内容缺一不可")
        print("  3. 检查清单：添加至少3个- [ ]格式的可执行检查项，方便落地验证")
        print("  4. Why解释：关键规则后添加'> **为什么？**'解释设计意图")
        print("  5. 正例/反例：补充正反案例对比，帮助理解模式边界")
        print("  6. 交叉引用：在「与现有模式的关系」章节链接2+个相关模式，构建知识网络")
        print("  7. Mermaid：复杂流程建议添加Mermaid可视化降低理解门槛")

    failed = [r for r in reports if r.errors]
    sys.exit(1 if failed and avg_score < args.threshold else 0)


if __name__ == "__main__":
    main()
