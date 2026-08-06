#!/usr/bin/env python3
"""
Spec Sanity Check - 规划文档主题健全性检查脚本

检测长上下文会话中可能发生的"spec内容污染"问题：
1. spec/tasks/checklist三件套标题主题一致性
2. 目录名与文档标题主题匹配度
3. 快速发现上下文压缩/会话恢复导致的文件内容错位问题

用法：
  python spec-sanity-check.py                     # 检查所有spec目录
  python spec-sanity-check.py --spec-dir <path>   # 检查指定spec目录
  python spec-sanity-check.py --json              # JSON输出
  python spec-sanity-check.py --strict            # 警告也视为错误

退出码：
  0 = 所有检查通过
  1 = 发现错误
  2 = 参数错误
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# 版本校验：导入共享库
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from python310_version_check import enforce_python310
enforce_python310()

from lib.cli import print_error, print_pass, print_warn, print_header


@dataclass
class CheckResult:
    name: str
    passed: bool
    message: str
    severity: str = "error"  # error | warning | info
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class SanityReport:
    spec_dir: Path
    results: list[CheckResult] = field(default_factory=list)
    spec_title: str = ""
    tasks_title: str = ""
    checklist_title: str = ""
    dir_name: str = ""
    dir_keywords: list[str] = field(default_factory=list)
    error_count: int = 0
    warn_count: int = 0
    pass_count: int = 0

    def add(self, result: CheckResult) -> None:
        self.results.append(result)
        if result.passed:
            self.pass_count += 1
        elif result.severity == "warning":
            self.warn_count += 1
        else:
            self.error_count += 1


def extract_title_from_markdown(content: str) -> str:
    """从Markdown内容中提取第一个H1标题"""
    for line in content.splitlines()[:50]:
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def extract_frontmatter_title(content: str) -> str:
    """从YAML frontmatter中提取title字段"""
    if not content.startswith("---"):
        return ""
    end_marker = content.find("---", 3)
    if end_marker == -1:
        return ""
    frontmatter = content[3:end_marker]
    for line in frontmatter.splitlines():
        line = line.strip()
        if line.startswith("title:"):
            title = line[6:].strip().strip('"').strip("'")
            return title
    return ""


def extract_dir_keywords(dir_name: str) -> list[str]:
    """从目录名提取关键词，用于主题匹配"""
    # 移除常见前缀后缀
    clean = re.sub(r'^[0-9]+-', '', dir_name)
    clean = re.sub(r'-spec$', '', clean)
    # 按-分割为关键词
    keywords = [k for k in clean.split('-') if k and len(k) > 1]
    return keywords


def keyword_match_score(keywords: list[str], text: str) -> tuple[int, list[str]]:
    """计算关键词在文本中的匹配分数，返回(匹配数, 匹配到的关键词)"""
    text_lower = text.lower()
    matched = []
    score = 0
    for kw in keywords:
        kw_lower = kw.lower()
        if len(kw_lower) >= 3 and kw_lower in text_lower:
            matched.append(kw)
            score += 1
    return score, matched


def check_single_spec(spec_dir: Path, strict: bool = False) -> SanityReport:
    """对单个spec目录执行sanity check"""
    report = SanityReport(spec_dir=spec_dir)
    report.dir_name = spec_dir.name
    report.dir_keywords = extract_dir_keywords(spec_dir.name)

    spec_file = spec_dir / "spec.md"
    tasks_file = spec_dir / "tasks.md"
    checklist_file = spec_dir / "checklist.md"

    # 检查文件存在
    missing = []
    for f, name in [(spec_file, "spec.md"), (tasks_file, "tasks.md"), (checklist_file, "checklist.md")]:
        if not f.exists():
            missing.append(name)

    if missing:
        report.add(CheckResult(
            name="文件存在性",
            passed=False,
            message=f"缺少必需文件: {', '.join(missing)}",
            severity="error"
        ))
        return report

    report.add(CheckResult(
        name="文件存在性",
        passed=True,
        message="spec.md/tasks.md/checklist.md三件套文件齐全",
        severity="info"
    ))

    # 读取所有文件内容
    try:
        spec_content = spec_file.read_text(encoding="utf-8")
        tasks_content = tasks_file.read_text(encoding="utf-8")
        checklist_content = checklist_file.read_text(encoding="utf-8")
    except Exception as e:
        report.add(CheckResult(
            name="文件可读性",
            passed=False,
            message=f"读取文件失败: {e}",
            severity="error"
        ))
        return report

    # 提取标题
    report.spec_title = extract_title_from_markdown(spec_content)
    spec_fm_title = extract_frontmatter_title(spec_content)
    report.tasks_title = extract_title_from_markdown(tasks_content)
    report.checklist_title = extract_title_from_markdown(checklist_content)

    # 检查1: spec.md有H1标题
    if not report.spec_title:
        report.add(CheckResult(
            name="spec.md标题",
            passed=False,
            message="spec.md缺少H1一级标题（# 开头）",
            severity="error"
        ))
    else:
        report.add(CheckResult(
            name="spec.md标题",
            passed=True,
            message=f"标题: {report.spec_title[:60]}...",
            severity="info"
        ))

    # 检查2: tasks.md有H1标题
    if not report.tasks_title:
        report.add(CheckResult(
            name="tasks.md标题",
            passed=False,
            message="tasks.md缺少H1一级标题",
            severity="error"
        ))
    else:
        report.add(CheckResult(
            name="tasks.md标题",
            passed=True,
            message=f"标题: {report.tasks_title[:60]}...",
            severity="info"
        ))

    # 检查3: checklist.md有H1标题
    if not report.checklist_title:
        report.add(CheckResult(
            name="checklist.md标题",
            passed=False,
            message="checklist.md缺少H1一级标题",
            severity="error"
        ))
    else:
        report.add(CheckResult(
            name="checklist.md标题",
            passed=True,
            message=f"标题: {report.checklist_title[:60]}...",
            severity="info"
        ))

    # 如果没有标题，无法进行后续主题检查
    if not report.spec_title or not report.tasks_title or not report.checklist_title:
        return report

    # 检查4: 三件套标题主题一致性（核心检查！）
    def normalize_title(t: str) -> str:
        """归一化标题：移除常见后缀、标点，保留核心主题"""
        # 移除中英文常见后缀
        t = re.sub(r'\s*[-–—|]\s*(产品需求文档|PRD|实施计划|验证清单|Verification Checklist|Implementation Plan|Decomposed.*|The Implementation Plan.*|Product Requirement Document.*)$', '', t, flags=re.IGNORECASE)
        # 移除标点，保留中英文和数字
        t = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', t)
        t = re.sub(r'\s+', ' ', t).strip().lower()
        return t

    def get_ngrams(text: str, n: int = 2) -> set[str]:
        """提取n-gram，处理中英文混合"""
        # 先按空格分词
        words = text.split()
        ngrams = set()
        for word in words:
            # 英文单词按整体
            if re.match(r'^[a-z0-9]+$', word) and len(word) >= 2:
                ngrams.add(word)
            # 中文字符按bigram
            chinese_chars = re.findall(r'[\u4e00-\u9fff]', word)
            if len(chinese_chars) >= n:
                for i in range(len(chinese_chars) - n + 1):
                    ngrams.add(''.join(chinese_chars[i:i+n]))
        return ngrams

    def title_similarity(a: str, b: str) -> float:
        """计算两个标题的相似度，结合n-gram Jaccard和前缀匹配"""
        if not a or not b:
            return 0.0
        # n-gram相似度
        ng_a = get_ngrams(a)
        ng_b = get_ngrams(b)
        if not ng_a or not ng_b:
            return 0.0
        jaccard = len(ng_a & ng_b) / len(ng_a | ng_b)
        # 前缀匹配：取较短标题的前50%作为前缀，检查是否被长标题包含
        min_len = min(len(a), len(b))
        prefix_len = max(8, min_len // 2)
        a_prefix = a[:prefix_len].strip()
        b_prefix = b[:prefix_len].strip()
        prefix_match = 1.0 if (a_prefix in b or b_prefix in a) else 0.0
        # 综合得分：jaccard为主，前缀匹配加权
        return max(jaccard, prefix_match * 0.8)

    spec_norm = normalize_title(report.spec_title)
    tasks_norm = normalize_title(report.tasks_title)
    checklist_norm = normalize_title(report.checklist_title)

    st_ratio = title_similarity(spec_norm, tasks_norm)
    sc_ratio = title_similarity(spec_norm, checklist_norm)
    tc_ratio = title_similarity(tasks_norm, checklist_norm)

    # 阈值：0.4，且三者都要通过
    titles_consistent = st_ratio > 0.4 and sc_ratio > 0.4 and tc_ratio > 0.4

    if not titles_consistent:
        report.add(CheckResult(
            name="三件套主题一致性",
            passed=False,
            message=f"检测到主题不一致！spec/tasks/checklist标题可能属于不同项目（重叠率: spec-tasks={st_ratio:.0%}, spec-checklist={sc_ratio:.0%}, tasks-checklist={tc_ratio:.0%}）。这通常是长上下文会话中文件内容被污染的信号！",
            severity="error",
            details={
                "spec_title": report.spec_title,
                "tasks_title": report.tasks_title,
                "checklist_title": report.checklist_title,
                "overlap_ratios": {"spec_tasks": st_ratio, "spec_checklist": sc_ratio, "tasks_checklist": tc_ratio}
            }
        ))
    else:
        report.add(CheckResult(
            name="三件套主题一致性",
            passed=True,
            message=f"spec/tasks/checklist三件套标题主题一致（重叠率: {min(st_ratio, sc_ratio, tc_ratio):.0%}+）",
            severity="info"
        ))

    # 检查5: 目录名与文档标题匹配度
    if report.dir_keywords and report.spec_title:
        dir_score, dir_matched = keyword_match_score(report.dir_keywords, report.spec_title)
        total_kw = len(report.dir_keywords)
        match_ratio = dir_score / max(total_kw, 1) if total_kw > 0 else 0

        if match_ratio < 0.2 and total_kw >= 2:
            # 低匹配率可能是目录名用英文、标题用中文导致的，降级为警告
            report.add(CheckResult(
                name="目录名-标题主题匹配",
                passed=False,
                message=f"目录名关键词与spec标题匹配度低（{dir_score}/{total_kw}关键词匹配，匹配率{match_ratio:.0%}）。目录关键词: {report.dir_keywords}。注意：如果目录名是英文、标题是中文，这可能是误报，请人工确认。",
                severity="warning",
                details={"matched_keywords": dir_matched, "dir_keywords": report.dir_keywords}
            ))
        else:
            report.add(CheckResult(
                name="目录名-标题主题匹配",
                passed=True,
                message=f"目录名与标题主题匹配（{dir_score}/{total_kw}关键词匹配）",
                severity="info"
            ))

    # 检查6: frontmatter title与H1标题一致性
    if spec_fm_title:
        fm_norm = normalize_title(spec_fm_title)
        fm_ratio = title_similarity(spec_norm, fm_norm)
        if fm_ratio < 0.4:
            report.add(CheckResult(
                name="frontmatter标题一致性",
                passed=False,
                message=f"spec.md的YAML frontmatter title与H1标题不一致",
                severity="warning",
                details={"frontmatter_title": spec_fm_title, "h1_title": report.spec_title}
            ))
        else:
            report.add(CheckResult(
                name="frontmatter标题一致性",
                passed=True,
                message="frontmatter title与H1标题一致",
                severity="info"
            ))

    return report


def discover_spec_dirs(root: Path) -> list[Path]:
    """发现所有.trae/specs下的spec目录"""
    specs_root = root / ".trae" / "specs"
    if not specs_root.exists():
        return []
    spec_dirs = []
    for cat_dir in specs_root.iterdir():
        if cat_dir.is_dir():
            for spec_dir in cat_dir.iterdir():
                if spec_dir.is_dir():
                    # 只要有spec.md就算
                    if (spec_dir / "spec.md").exists():
                        spec_dirs.append(spec_dir)
    return sorted(spec_dirs)


def print_terminal_report(report: SanityReport) -> None:
    """打印终端友好的报告"""
    print_header(f"Spec Sanity Check: {report.spec_dir.name}")
    print(f"ℹ 目录: {report.spec_dir}")
    print()

    for r in report.results:
        if r.passed:
            print_pass(f"  ✓ {r.name}: {r.message}")
        else:
            if r.severity == "warning":
                print_warn(f"  ⚠ {r.name}: {r.message}")
            else:
                print_error(f"  ✗ {r.name}: {r.message}")

    print()
    if report.error_count > 0:
        print_error(f"结果: ❌ {report.error_count}个错误, {report.warn_count}个警告, {report.pass_count}项通过")
    elif report.warn_count > 0:
        print_warn(f"结果: ⚠ {report.error_count}个错误, {report.warn_count}个警告, {report.pass_count}项通过")
    else:
        print_pass(f"结果: ✓ 全部通过 ({report.pass_count}项检查)")
    print()


def generate_json_report(reports: list[SanityReport]) -> str:
    """生成JSON报告"""
    output = []
    for r in reports:
        output.append({
            "spec_dir": str(r.spec_dir),
            "dir_name": r.dir_name,
            "spec_title": r.spec_title,
            "tasks_title": r.tasks_title,
            "checklist_title": r.checklist_title,
            "summary": {
                "pass": r.pass_count,
                "warning": r.warn_count,
                "error": r.error_count,
            },
            "checks": [
                {
                    "name": cr.name,
                    "passed": cr.passed,
                    "severity": cr.severity,
                    "message": cr.message,
                    "details": cr.details,
                }
                for cr in r.results
            ]
        })
    return json.dumps(output, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Spec Sanity Check - 检测规划文档主题污染问题",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python spec-sanity-check.py                     # 检查所有spec
  python spec-sanity-check.py --spec-dir .trae/specs/core-foundation/agent-evaluation-methodology-wiki
  python spec-sanity-check.py --json              # JSON输出
  python spec-sanity-check.py --strict            # 警告视为错误
        """
    )
    parser.add_argument("--spec-dir", type=str, help="指定要检查的spec目录路径")
    parser.add_argument("--path", type=str, help="项目根目录（默认自动检测）")
    parser.add_argument("--json", action="store_true", help="JSON格式输出")
    parser.add_argument("--strict", action="store_true", help="严格模式：警告也视为错误")

    args = parser.parse_args()

    # 确定项目根目录
    if args.path:
        root = Path(args.path).resolve()
    else:
        root = Path(__file__).resolve().parent.parent  # 从scripts/到项目根

    if not root.exists():
        print_error(f"项目根目录不存在: {root}")
        return 2

    # 收集要检查的spec目录
    if args.spec_dir:
        spec_dir = Path(args.spec_dir)
        if not spec_dir.is_absolute():
            spec_dir = root / spec_dir
        if not spec_dir.exists():
            print_error(f"spec目录不存在: {spec_dir}")
            return 2
        spec_dirs = [spec_dir]
    else:
        spec_dirs = discover_spec_dirs(root)
        if not spec_dirs:
            print_warn("未找到任何spec目录（.trae/specs/*/）")
            return 0

    if not args.json:
        print(f"ℹ 共发现 {len(spec_dirs)} 个spec目录，开始sanity check...")
        print()

    # 执行检查
    reports: list[SanityReport] = []
    total_errors = 0
    total_warnings = 0

    for sd in spec_dirs:
        report = check_single_spec(sd, strict=args.strict)
        reports.append(report)
        total_errors += report.error_count
        total_warnings += report.warn_count

        if not args.json:
            print_terminal_report(report)

    if args.json:
        print(generate_json_report(reports))
        return 1 if total_errors > 0 or (args.strict and total_warnings > 0) else 0

    # 总结
    print_header("总结")
    if total_errors > 0:
        print_error(f"❌ 检查完成，发现 {total_errors} 个错误，{total_warnings} 个警告")
        print(f"ℹ 提示：'三件套主题一致性'错误通常表明spec.md内容在长会话中被意外覆盖，建议检查并重建spec.md")
        return 1
    elif total_warnings > 0:
        if args.strict:
            print_error(f"⚠ 严格模式：{total_warnings} 个警告视为错误")
            return 1
        print_warn(f"⚠ 检查完成，{total_warnings} 个警告（建议人工确认），无错误")
        return 0
    else:
        print_pass(f"✓ 所有 {len(spec_dirs)} 个spec目录通过sanity check！")
        return 0


if __name__ == "__main__":
    sys.exit(main())
