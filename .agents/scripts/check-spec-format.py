#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spec 文档标准化检查工具

检查 spec.md 文档是否符合标准格式规范，包括：
- 核心章节完整性
- Requirement 结构和 Scenario 完整性
- 验收标准可验证性
- 版本号与变更日志规范
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


# ============================================================================
# 数据结构定义
# ============================================================================

@dataclass
class Issue:
    """检查问题记录"""
    type: str
    name: str
    message: str
    severity: str = "error"  # error, warning

@dataclass
class SpecCheckResult:
    """单个 Spec 文件的检查结果"""
    spec_path: str
    score: int = 0
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    def to_dict(self):
        return {
            "spec_dir": self.spec_path,
            "score": self.score,
            "errors": self.errors,
            "warnings": self.warnings
        }


# ============================================================================
# 核心章节检测器
# ============================================================================

# 必须的核心章节（按顺序）
CORE_CHAPTERS = [
    ("Why（动机）", r"##\s+Why（动机）"),
    ("What Changes（变更摘要）", r"##\s+What Changes（变更摘要）"),
    ("Impact（影响范围）", r"##\s+Impact（影响范围）"),
    ("ADDED Requirements（新增需求）", r"##\s+ADDED Requirements（新增需求）"),
    ("MODIFIED Requirements（修改需求）", r"##\s+MODIFIED Requirements（修改需求）"),
    ("REMOVED Requirements（移除需求）", r"##\s+REMOVED Requirements（移除需求）"),
]

def detect_core_chapters(content: str) -> tuple[list[Issue], list[str]]:
    """
    检测核心章节是否存在及顺序是否正确

    Returns:
        (issues, found_chapters): 问题列表和已找到的章节名列表
    """
    issues = []
    found_chapters = []
    found_positions = {}

    for chapter_name, pattern in CORE_CHAPTERS:
        match = re.search(pattern, content)
        if match:
            found_chapters.append(chapter_name)
            found_positions[chapter_name] = match.start()
        else:
            issues.append(Issue(
                type="missing_chapter",
                name=chapter_name,
                message=f"缺少核心章节: {chapter_name}",
                severity="error"
            ))

    # 检查顺序
    sorted_chapters = sorted(found_positions.items(), key=lambda x: x[1])
    expected_order = [name for name, _ in CORE_CHAPTERS if name in found_chapters]
    actual_order = [name for name, _ in sorted_chapters]

    if expected_order != actual_order:
        issues.append(Issue(
            type="chapter_order",
            name="章节顺序",
            message=f"章节顺序不正确，期望: {' → '.join(expected_order)}, 实际: {' → '.join(actual_order)}",
            severity="warning"
        ))

    return issues, found_chapters


def check_chapter_not_empty(content: str, chapter_name: str, pattern: str) -> Optional[Issue]:
    """
    检查章节是否有实质内容（不只是标题）
    """
    # 找到章节位置
    match = re.search(pattern, content)
    if not match:
        return None

    start = match.end()
    # 找到下一个 ## 标题或文件结尾
    next_chapter = re.search(r"\n##\s+", content[start:])
    end = next_chapter.start() + start if next_chapter else len(content)

    chapter_content = content[start:end].strip()

    # 检查是否只有空白字符或内容太少（少于10个字符视为空）
    if len(chapter_content) < 10:
        return Issue(
            type="empty_chapter",
            name=chapter_name,
            message=f"章节 '{chapter_name}' 内容为空或过于简略",
            severity="error"
        )

    return None


# ============================================================================
# Requirement 完整性验证器
# ============================================================================

def detect_requirements(content: str) -> tuple[list[Issue], list[dict]]:
    """
    检测 Requirement 结构的完整性

    每个 Requirement 必须包含:
    - 名称（以 "### Requirement:" 开头）
    - 主体描述
    - 至少一个 Scenario
    """
    issues = []
    requirements = []

    # 匹配所有 Requirement（使用 ### Requirement: 标题）
    req_pattern = r"###\s+Requirement:\s*(.+?)(?=\n###|\n##|\n#|$)"
    req_matches = list(re.finditer(req_pattern, content, re.DOTALL))

    if not req_matches:
        issues.append(Issue(
            type="missing_requirement",
            name="Requirement",
            message="未找到任何 Requirement 定义",
            severity="error"
        ))
        return issues, requirements

    for i, req_match in enumerate(req_matches):
        req_name = req_match.group(1).strip()
        req_content = req_match.group(0)

        # 检查是否有主体描述（系统 SHALL/SHALL NOT）
        has_shall = bool(re.search(r"系统\s+SHALL|系统\s+SHALL\s+NOT", req_content))

        # 查找 Scenario
        scenario_pattern = r"####\s+Scenario:\s*(.+?)(?=\n####|\n###|\n##|\n#|$)"
        scenarios = list(re.finditer(scenario_pattern, req_content, re.DOTALL))

        req_info = {
            "name": req_name,
            "has_shall": has_shall,
            "scenario_count": len(scenarios),
            "scenarios": []
        }

        # 检查 Scenario 完整性
        for scenario in scenarios:
            scenario_name = scenario.group(1).strip()
            scenario_content = scenario.group(0)

            # 检查 WHEN 和 THEN
            has_when = bool(re.search(r"#####\s+WHEN", scenario_content))
            has_then = bool(re.search(r"#####\s+THEN", scenario_content))

            req_info["scenarios"].append({
                "name": scenario_name,
                "has_when": has_when,
                "has_then": has_then
            })

            # Scenario 本身的完整性检查
            if not has_when:
                issues.append(Issue(
                    type="missing_scenario_part",
                    name=f"Scenario: {scenario_name}",
                    message=f"Scenario '{scenario_name}' 缺少 WHEN 部分",
                    severity="error"
                ))

            if not has_then:
                issues.append(Issue(
                    type="missing_scenario_part",
                    name=f"Scenario: {scenario_name}",
                    message=f"Scenario '{scenario_name}' 缺少 THEN 部分",
                    severity="error"
                ))

        # Requirement 级别检查
        if not has_shall:
            issues.append(Issue(
                type="missing_shall",
                name=f"Requirement: {req_name}",
                message=f"Requirement '{req_name}' 缺少系统 SHALL/SHALL NOT 描述",
                severity="error"
            ))

        if len(scenarios) == 0:
            issues.append(Issue(
                type="missing_scenario",
                name=f"Requirement: {req_name}",
                message=f"Requirement '{req_name}' 缺少 Scenario 定义",
                severity="error"
            ))

        requirements.append(req_info)

    return issues, requirements


# ============================================================================
# 验收标准可验证性检查器
# ============================================================================

# 禁止使用的模糊词汇
VAGUE_WORDS = [
    "良好", "优秀", "合适", "不错", "还行",
    "可能", "也许", "大约", "较好", "较快",
    "适量", "基本上", "令人满意", "正确", "合适"
]

# 更严格的模糊词汇（用于 THEN 部分）
STRICT_VAGUE_WORDS = [
    "良好", "优秀", "合适", "不错", "还行",
    "可能", "也许", "大约", "较好", "较快",
    "适量", "基本上", "令人满意"
]

def check_acceptance_criteria(content: str) -> list[Issue]:
    """
    检查 Scenario 的验收标准是否具体可测量
    """
    issues = []

    # 查找所有 THEN 部分
    then_pattern = r"#####\s+THEN\s*\n((?:\s*-\s*.+\n)*)"
    then_matches = re.finditer(then_pattern, content)

    for match in then_matches:
        then_content = match.group(1)

        for word in STRICT_VAGUE_WORDS:
            if word in then_content:
                issues.append(Issue(
                    type="vague_criteria",
                    name="验收标准",
                    message=f"验收标准使用了模糊词汇 '{word}'，应使用具体数值或可验证状态描述",
                    severity="warning"
                ))
                break  # 每个 THEN 块只报告一次

    return issues


# ============================================================================
# 版本号与变更日志检测器
# ============================================================================

def check_version_and_changelog(content: str) -> tuple[list[Issue], dict]:
    """
    检查版本号声明和变更日志格式
    """
    issues = []
    info = {"has_version": False, "has_changelog": False, "version": None}

    # 检查版本号声明 (TOML frontmatter 格式)
    version_pattern = r"^---\s*\n.*?version:\s*(\d+\.\d+)\s*\n.*?---"
    version_match = re.search(version_pattern, content, re.DOTALL | re.MULTILINE)

    if version_match:
        info["has_version"] = True
        info["version"] = version_match.group(1)
    else:
        issues.append(Issue(
            type="missing_version",
            name="版本号",
            message="缺少版本号声明，应使用 TOML frontmatter 格式: version: X.Y",
            severity="error"
        ))

    # 检查变更日志标记
    changelog_start = re.search(r"<!--\s+changelog\s+-->", content)
    changelog_end = re.search(r"<!--\s+changelog\s+-->", content[changelog_start.end():] if changelog_start else content)

    if changelog_start and changelog_end:
        info["has_changelog"] = True

        # 计算变更日志内容区域
        end_pos = changelog_start.end() + (changelog_end.start() if changelog_end else 0)
        changelog_content = content[changelog_start.end():changelog_start.end() + changelog_end.start()]

        # 检查变更日志是否包含实质性内容
        # 移除标题行，检查是否还有变更记录
        changelog_lines = [line.strip() for line in changelog_content.split('\n') if line.strip()]
        changelog_lines = [line for line in changelog_lines if not line.startswith('#') and line != '## Changelog']

        if not changelog_lines:
            issues.append(Issue(
                type="empty_changelog",
                name="Changelog",
                message="变更日志章节为空，缺少实质性变更记录",
                severity="warning"
            ))
        else:
            # 检查每条变更记录格式
            entry_pattern = r"^\d{4}-\d{2}-\d{2}\s*\|\s*(added|modified|removed|deprecated)\s*\|"
            valid_entries = 0
            for line in changelog_lines:
                if re.match(entry_pattern, line):
                    valid_entries += 1

            if valid_entries == 0:
                issues.append(Issue(
                    type="invalid_changelog_format",
                    name="Changelog",
                    message="变更日志格式不正确，应为: YYYY-MM-DD | type | description",
                    severity="error"
                ))
    else:
        issues.append(Issue(
            type="missing_changelog",
            name="Changelog",
            message="缺少变更日志章节，需包含 <!-- changelog --> 标记",
            severity="warning"
        ))

    return issues, info


# ============================================================================
# 评分计算
# ============================================================================

def calculate_score(total_issues: list[Issue], chapters_found: list[str], requirements: list) -> int:
    """
    基于检查结果计算评分 (0-100)
    """
    score = 100

    # 严重错误扣分
    for issue in total_issues:
        if issue.severity == "error":
            if issue.type in ["missing_chapter", "empty_chapter", "missing_version"]:
                score -= 15
            elif issue.type in ["missing_requirement", "missing_scenario", "missing_scenario_part"]:
                score -= 10
            elif issue.type == "missing_shall":
                score -= 8
            elif issue.type == "invalid_changelog_format":
                score -= 5
        else:  # warning
            if issue.type == "vague_criteria":
                score -= 3
            elif issue.type == "chapter_order":
                score -= 2
            elif issue.type in ["empty_changelog", "missing_changelog"]:
                score -= 5

    # 核心章节缺失扣分
    missing_chapters = 6 - len(chapters_found)
    score -= missing_chapters * 5

    # Requirement 数量过少扣分
    if len(requirements) == 0:
        score -= 20

    return max(0, min(100, score))


# ============================================================================
# 主检查逻辑
# ============================================================================

def check_spec_file(spec_path: str, verbose: bool = False) -> SpecCheckResult:
    """
    执行完整的 spec 文件检查
    """
    result = SpecCheckResult(spec_path=spec_path)

    try:
        with open(spec_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        result.errors.append({
            "type": "file_not_found",
            "name": spec_path,
            "message": f"文件不存在: {spec_path}"
        })
        return result
    except Exception as e:
        result.errors.append({
            "type": "read_error",
            "name": spec_path,
            "message": f"读取文件失败: {str(e)}"
        })
        return result

    all_issues = []

    # 1. 核心章节检测
    if verbose:
        print(f"[检查中] 核心章节检测...")
    chapter_issues, found_chapters = detect_core_chapters(content)
    all_issues.extend(chapter_issues)

    # 2. 检查每个核心章节是否有实质内容
    for chapter_name, pattern in CORE_CHAPTERS:
        issue = check_chapter_not_empty(content, chapter_name, pattern)
        if issue:
            all_issues.append(issue)

    # 3. Requirement 完整性验证
    if verbose:
        print(f"[检查中] Requirement 完整性验证...")
    req_issues, requirements = detect_requirements(content)
    all_issues.extend(req_issues)

    # 4. 验收标准可验证性检查
    if verbose:
        print(f"[检查中] 验收标准可验证性检查...")
    criteria_issues = check_acceptance_criteria(content)
    all_issues.extend(criteria_issues)

    # 5. 版本号与变更日志检测
    if verbose:
        print(f"[检查中] 版本号与变更日志检测...")
    version_issues, version_info = check_version_and_changelog(content)
    all_issues.extend(version_issues)

    # 分类错误和警告
    result.errors = [{"type": i.type, "name": i.name, "message": i.message}
                    for i in all_issues if i.severity == "error"]
    result.warnings = [{"type": i.type, "name": i.name, "message": i.message}
                       for i in all_issues if i.severity == "warning"]

    # 计算评分
    result.score = calculate_score(all_issues, found_chapters, requirements)

    if verbose:
        print(f"[完成] 评分: {result.score}, 错误: {len(result.errors)}, 警告: {len(result.warnings)}")

    return result


def find_spec_directories(base_path: str, check_all: bool) -> list[str]:
    """
    查找要检查的 spec 目录
    """
    base = Path(base_path)
    if not base.exists():
        return []

    if check_all:
        # 递归查找所有包含 spec.md 的目录
        spec_dirs = []
        for spec_file in base.rglob("spec.md"):
            spec_dirs.append(str(spec_file.parent))
        return spec_dirs
    else:
        # 只检查指定的目录
        if (base / "spec.md").exists():
            return [str(base)]
        return []


def print_result_text(result: SpecCheckResult, verbose: bool = False):
    """以文本格式输出检查结果"""
    print(f"\n{'='*60}")
    print(f"检查文件: {result.spec_path}")
    print(f"评分: {result.score}/100")
    print(f"{'='*60}")

    if result.errors:
        print(f"\n❌ 错误 ({len(result.errors)} 项):")
        for err in result.errors:
            print(f"  - [{err['type']}] {err['name']}: {err['message']}")

    if result.warnings:
        print(f"\n⚠️  警告 ({len(result.warnings)} 项):")
        for warn in result.warnings:
            print(f"  - [{warn['type']}] {warn['name']}: {warn['message']}")

    if not result.errors and not result.warnings:
        print("\n✅ 检查通过，无错误和警告")

    if verbose and not result.errors:
        print("\n📋 检查详情:")
        print("  ✓ 核心章节结构完整")
        print("  ✓ Requirement 定义规范")
        print("  ✓ Scenario 结构完整")
        print("  ✓ 验收标准可验证")
        print("  ✓ 版本号与变更日志规范")


def print_summary_text(results: list[SpecCheckResult]):
    """输出检查摘要（多文件模式）"""
    total = len(results)
    passed = sum(1 for r in results if r.score >= 80 and not r.errors)
    failed = total - passed

    print(f"\n{'='*60}")
    print(f"检查摘要")
    print(f"{'='*60}")
    print(f"总计检查: {total} 个 spec 目录")
    print(f"通过: {passed} 个")
    print(f"未通过: {failed} 个")

    if failed > 0:
        print(f"\n未通过的 spec:")
        for r in results:
            if r.score < 80 or r.errors:
                print(f"  - {r.spec_path}: 评分 {r.score}/100")


# ============================================================================
# 命令行入口
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Spec 文档标准化检查工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python check-spec-format.py                           # 检查默认目录
  python check-spec-format.py --spec-dir ./specs        # 指定目录
  python check-spec-format.py --check-all               # 检查所有子目录
  python check-spec-format.py --format json --verbose   # JSON 输出格式
        """
    )

    parser.add_argument(
        "--spec-dir",
        type=str,
        default=".trae/specs/",
        help="指定要检查的 spec 目录路径 (默认: .trae/specs/)"
    )

    parser.add_argument(
        "--format",
        type=str,
        choices=["text", "json", "yaml"],
        default="text",
        help="输出格式 (默认: text)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示详细输出"
    )

    parser.add_argument(
        "--check-all",
        action="store_true",
        help="检查 .trae/specs/ 下所有 spec 目录"
    )

    args = parser.parse_args()

    # 查找要检查的目录
    spec_dirs = find_spec_directories(args.spec_dir, args.check_all)

    if not spec_dirs:
        if args.format == "json":
            error_result = {
                "spec_dir": args.spec_dir,
                "score": 0,
                "errors": [{"type": "not_found", "name": args.spec_dir, "message": "未找到 spec 目录或 spec.md 文件"}],
                "warnings": []
            }
            print(json.dumps(error_result, ensure_ascii=False, indent=2))
            sys.exit(2)
        else:
            print(f"错误: 未找到 spec 目录或 spec.md 文件: {args.spec_dir}", file=sys.stderr)
            sys.exit(2)

    # 执行检查
    results = []
    for spec_dir in spec_dirs:
        spec_path = os.path.join(spec_dir, "spec.md")
        if args.verbose:
            print(f"\n正在检查: {spec_path}")
        result = check_spec_file(spec_path, args.verbose)
        results.append(result)

    # 根据格式输出结果
    if args.format == "json":
        if len(results) == 1:
            print(json.dumps(results[0].to_dict(), ensure_ascii=False, indent=2))
        else:
            print(json.dumps([r.to_dict() for r in results], ensure_ascii=False, indent=2))
    elif args.format == "yaml":
        import yaml
        if len(results) == 1:
            print(yaml.dump([results[0].to_dict()], allow_unicode=True, default_flow_style=False))
        else:
            print(yaml.dump([r.to_dict() for r in results], allow_unicode=True, default_flow_style=False))
    else:
        if len(results) == 1:
            print_result_text(results[0], args.verbose)
        else:
            print_summary_text(results)
            for r in results:
                print_result_text(r, args.verbose)

    # 确定退出码
    has_errors = any(r.errors for r in results)
    if has_errors:
        sys.exit(1)
    elif any(r.score < 80 for r in results):
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
