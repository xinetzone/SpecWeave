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

# 必须的核心章节（按顺序）—— 兼容纯英文标题和带中文括号标题两种格式
# 格式: (规范名称, 匹配正则, 中文别名)
CORE_CHAPTERS = [
    ("Why", re.compile(r"^##\s+Why(?:[（\(].*?[）\)])?\s*$", re.MULTILINE), "动机"),
    ("What Changes", re.compile(r"^##\s+What\s+Changes(?:[（\(].*?[）\)])?\s*$", re.MULTILINE), "变更摘要"),
    ("Impact", re.compile(r"^##\s+Impact(?:[（\(].*?[）\)])?\s*$", re.MULTILINE), "影响范围"),
    ("ADDED Requirements", re.compile(r"^##\s+ADDED\s+Requirements(?:[（\(].*?[）\)])?\s*$", re.MULTILINE), "新增需求"),
    ("MODIFIED Requirements", re.compile(r"^##\s+MODIFIED\s+Requirements(?:[（\(].*?[）\)])?\s*$", re.MULTILINE), "修改需求"),
    ("REMOVED Requirements", re.compile(r"^##\s+REMOVED\s+Requirements(?:[（\(].*?[）\)])?\s*$", re.MULTILINE), "移除需求"),
]

def detect_core_chapters(content: str) -> tuple[list[Issue], list[str], dict]:
    """
    检测核心章节是否存在及顺序是否正确

    Returns:
        (issues, found_chapters, found_positions): 问题列表、已找到的章节名列表、位置字典
    """
    issues = []
    found_chapters = []
    found_positions = {}

    for chapter_name, pattern, cn_name in CORE_CHAPTERS:
        match = pattern.search(content)
        if match:
            found_chapters.append(chapter_name)
            found_positions[chapter_name] = match.start()
        else:
            issues.append(Issue(
                type="missing_chapter",
                name=chapter_name,
                message=f"缺少核心章节: {chapter_name}（{cn_name}）",
                severity="error"
            ))

    # 检查顺序
    sorted_chapters = sorted(found_positions.items(), key=lambda x: x[1])
    expected_order = [name for name, _, _ in CORE_CHAPTERS if name in found_chapters]
    actual_order = [name for name, _ in sorted_chapters]

    if expected_order != actual_order:
        issues.append(Issue(
            type="chapter_order",
            name="章节顺序",
            message=f"章节顺序不正确，期望: {' → '.join(expected_order)}, 实际: {' → '.join(actual_order)}",
            severity="warning"
        ))

    return issues, found_chapters, found_positions


def find_chapter_end(content: str, chapter_start_match, next_patterns: list[re.Pattern]) -> int:
    """
    找到章节结束位置（下一个同级或更高级标题的起始位置）
    """
    start = chapter_start_match.end()
    earliest_end = len(content)

    for pat in next_patterns:
        m = pat.search(content, start)
        if m and m.start() < earliest_end:
            earliest_end = m.start()

    return earliest_end


def check_chapter_not_empty(content: str, chapter_name: str, pattern: re.Pattern) -> Optional[Issue]:
    """
    检查章节是否有实质内容（不只是标题）
    """
    match = pattern.search(content)
    if not match:
        return None

    # 找到下一个 ## 标题或文件结尾
    next_chapter = re.search(r"\n##\s+", content[match.end():])
    end = next_chapter.start() + match.end() if next_chapter else len(content)

    chapter_content = content[match.end():end].strip()

    # 检查是否只有空白字符或内容太少（少于10个字符视为空）
    # 例外：如果内容明确表示"无"（如"无"、"暂无"、"N/A"、"无。"等简短表述），视为合规
    if len(chapter_content) < 10:
        no_content_markers = ["无", "暂无", "N/A", "n/a", "None", "none", "无。", "暂无。"]
        is_explicit_no = any(chapter_content.strip() in [m, m + "。"] for m in no_content_markers)
        if not is_explicit_no:
            return Issue(
                type="empty_chapter",
                name=chapter_name,
                message=f"章节 '{chapter_name}' 内容为空或过于简略（若无内容请注明「无」）",
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
    - 主体描述（建议使用"系统 SHALL"，但不强制）
    - 至少一个 Scenario
    """
    issues = []
    requirements = []

    # 匹配所有 Requirement（使用 ### Requirement: 标题）
    # 结束边界：下一个 ### Requirement: 或下一个 ## 章节或文件结尾
    req_pattern = re.compile(
        r"^###\s+Requirement:\s*(.+?)$",
        re.MULTILINE
    )
    req_matches = list(req_pattern.finditer(content))

    if not req_matches:
        # 检查 ADDED/MODIFIED/REMOVED Requirements 章节内是否有内容
        # 如果 Requirements 章节都有内容但没有标准 Requirement 格式，给出警告而非错误
        has_req_section = bool(re.search(r"^##\s+(?:ADDED|MODIFIED|REMOVED)\s+Requirements", content, re.MULTILINE))
        if has_req_section:
            issues.append(Issue(
                type="missing_requirement",
                name="Requirement",
                message="未找到标准格式的 Requirement 定义（应以 '### Requirement:' 开头）",
                severity="warning"
            ))
        return issues, requirements

    # 构建每个 Requirement 的内容块边界，并确定所属章节
    req_blocks = []
    # 先找到各 Requirements 章节的位置，用于判断 Requirement 归属
    added_match = re.search(r"^##\s+ADDED\s+Requirements", content, re.MULTILINE)
    modified_match = re.search(r"^##\s+MODIFIED\s+Requirements", content, re.MULTILINE)
    removed_match = re.search(r"^##\s+REMOVED\s+Requirements", content, re.MULTILINE)

    def get_section_for_pos(pos: int) -> str:
        """根据位置判断 Requirement 属于哪个 Requirements 章节"""
        section = "unknown"
        if added_match and pos > added_match.start():
            section = "ADDED"
        if modified_match and pos > modified_match.start():
            section = "MODIFIED"
        if removed_match and pos > removed_match.start():
            section = "REMOVED"
        return section

    for i, req_match in enumerate(req_matches):
        req_name = req_match.group(1).strip()
        start_pos = req_match.start()
        if i + 1 < len(req_matches):
            end_pos = req_matches[i + 1].start()
        else:
            # 找到下一个 ## 章节或文件结尾
            next_section = re.search(r"\n##\s+", content[req_match.end():])
            end_pos = next_section.start() + req_match.end() if next_section else len(content)
        req_content = content[start_pos:end_pos]
        section = get_section_for_pos(start_pos)
        req_blocks.append((req_name, req_content, start_pos, section))

    for req_name, req_content, _, section in req_blocks:
        # 检查是否有 SHALL 描述（推荐但不强制错误）
        # REMOVED Requirements 下的 Requirement 描述被移除的旧功能，不强制 SHALL
        has_shall = bool(re.search(r"系统\s+SHALL|系统\s+SHALL\s+NOT|SHALL\s+|SHALL\s+NOT\s+", req_content))

        # 查找 Scenario（#### Scenario: 开头）
        scenario_pattern = re.compile(r"^####\s+Scenario:\s*(.+?)$", re.MULTILINE)
        scenario_matches = list(scenario_pattern.finditer(req_content))

        req_info = {
            "name": req_name,
            "has_shall": has_shall,
            "scenario_count": len(scenario_matches),
            "scenarios": []
        }

        # 检查 Scenario 完整性
        for i, scenario in enumerate(scenario_matches):
            scenario_name = scenario.group(1).strip()
            scen_start = scenario.start()
            if i + 1 < len(scenario_matches):
                scen_end = scenario_matches[i + 1].start()
            else:
                # 下一个 Requirement 或 ## 章节
                next_req = req_pattern.search(req_content, scenario.end())
                next_section = re.search(r"\n##\s+", req_content[scenario.end():])
                end1 = next_req.start() + scenario.end() if next_req else len(req_content)
                end2 = next_section.start() + scenario.end() if next_section else len(req_content)
                scen_end = min(end1, end2)
            scenario_content = req_content[scen_start:scen_end]

            # 检查 WHEN 和 THEN —— 兼容两种格式：
            # 格式1: ##### WHEN / ##### THEN（五级标题）
            # 格式2: - **WHEN** / - **THEN**（列表项加粗）
            has_when_title = bool(re.search(r"^#{3,5}\s+WHEN\s*$", scenario_content, re.MULTILINE))
            has_then_title = bool(re.search(r"^#{3,5}\s+THEN\s*$", scenario_content, re.MULTILINE))
            has_when_list = bool(re.search(r"^[\s]*[-*+]\s+\*\*WHEN\*\*", scenario_content, re.MULTILINE))
            has_then_list = bool(re.search(r"^[\s]*[-*+]\s+\*\*THEN\*\*", scenario_content, re.MULTILINE))
            # 无格式但包含 WHEN 关键词（宽松检测，仅作提示）
            has_when = has_when_title or has_when_list
            has_then = has_then_title or has_then_list

            req_info["scenarios"].append({
                "name": scenario_name,
                "has_when": has_when,
                "has_then": has_then,
                "has_and": bool(re.search(r"^#{3,5}\s+AND\s*$|^[\s]*[-*+]\s+\*\*AND\*\*", scenario_content, re.MULTILINE))
            })

            # Scenario 本身的完整性检查
            if not has_when:
                issues.append(Issue(
                    type="missing_scenario_part",
                    name=f"Scenario: {scenario_name}",
                    message=f"Scenario '{scenario_name}' 缺少 WHEN 部分（应使用 '#### Scenario:' 下的 '- **WHEN**' 列表项或 '##### WHEN' 标题）",
                    severity="error"
                ))

            if not has_then:
                issues.append(Issue(
                    type="missing_scenario_part",
                    name=f"Scenario: {scenario_name}",
                    message=f"Scenario '{scenario_name}' 缺少 THEN 部分（应使用 '#### Scenario:' 下的 '- **THEN**' 列表项或 '##### THEN' 标题）",
                    severity="error"
                ))

        # Requirement 级别检查
        # REMOVED Requirements 下的 Requirement 描述被移除的旧功能，不强制 SHALL
        if not has_shall and section != "REMOVED":
            issues.append(Issue(
                type="missing_shall",
                name=f"Requirement: {req_name}",
                message=f"Requirement '{req_name}' 建议使用 '系统 SHALL' 句式描述功能行为",
                severity="warning"
            ))

        if len(scenario_matches) == 0:
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

# 禁止使用的模糊词汇（已去重）
VAGUE_WORDS = [
    "良好", "优秀", "合适", "不错", "还行",
    "可能", "也许", "大约", "较好", "较快",
    "适量", "基本上", "令人满意"
]

# 更严格的模糊词汇（用于 THEN 部分）
STRICT_VAGUE_WORDS = VAGUE_WORDS  # 与上面相同

def check_acceptance_criteria(content: str) -> list[Issue]:
    """
    检查 Scenario 的验收标准是否具体可测量
    支持两种格式: ##### THEN 标题格式 和 - **THEN** 列表项格式
    """
    issues = []

    # 查找所有 THEN 部分（兼容两种格式）
    # 格式1: ##### THEN 后跟列表项
    then_title_pattern = re.compile(
        r"^#{3,5}\s+THEN\s*\n((?:\s*[-*+]\s*.+\n)*)",
        re.MULTILINE
    )
    # 格式2: - **THEN** 行开始的块
    then_list_pattern = re.compile(
        r"^[\s]*[-*+]\s+\*\*THEN\*\*\s*\n((?:\s*[-*+]\s*.+\n)*)",
        re.MULTILINE
    )

    then_contents = []
    for m in then_title_pattern.finditer(content):
        then_contents.append(m.group(1))
    for m in then_list_pattern.finditer(content):
        then_contents.append(m.group(1))

    reported_words = set()
    for then_content in then_contents:
        for word in STRICT_VAGUE_WORDS:
            if word in then_content and word not in reported_words:
                issues.append(Issue(
                    type="vague_criteria",
                    name="验收标准",
                    message=f"验收标准使用了模糊词汇 '{word}'，应使用具体数值或可验证状态描述",
                    severity="warning"
                ))
                reported_words.add(word)

    return issues


# ============================================================================
# 版本号与变更日志检测器
# ============================================================================

def check_version_and_changelog(content: str) -> tuple[list[Issue], dict]:
    """
    检查版本号声明和变更日志格式
    支持两种版本号格式:
    1. TOML frontmatter 格式（推荐）: ---\\nversion: X.Y\\n---
    2. 简单头部声明（兼容旧格式）: version: X.Y（文件前5行）
    """
    issues = []
    info = {"has_version": False, "has_changelog": False, "version": None, "version_format": None}

    # 检查版本号声明 - 优先 TOML frontmatter 格式
    fm_version_pattern = re.compile(
        r"^---\s*\n(?:.*\n)*?version:\s*(\d+\.\d+)\s*\n(?:.*\n)*?---",
        re.MULTILINE
    )
    fm_match = fm_version_pattern.search(content)

    if fm_match:
        info["has_version"] = True
        info["version"] = fm_match.group(1)
        info["version_format"] = "toml-frontmatter"
    else:
        # 兼容旧格式：文件开头（前5行）的简单 version: X.Y 声明
        lines = content.split('\n')[:10]
        for line in lines:
            simple_match = re.match(r"^version:\s*(\d+\.\d+)\s*$", line.strip())
            if simple_match:
                info["has_version"] = True
                info["version"] = simple_match.group(1)
                info["version_format"] = "simple"
                issues.append(Issue(
                    type="version_format",
                    name="版本号",
                    message="版本号建议使用 TOML frontmatter 格式（---\\nversion: X.Y\\n---）包裹",
                    severity="warning"
                ))
                break

    if not info["has_version"]:
        issues.append(Issue(
            type="missing_version",
            name="版本号",
            message="缺少版本号声明，推荐使用 TOML frontmatter 格式: ---\\nversion: X.Y\\n---",
            severity="error"
        ))

    # 检查变更日志标记
    changelog_marker = "<!-- changelog -->"
    all_markers = [m.start() for m in re.finditer(re.escape(changelog_marker), content)]

    if len(all_markers) >= 2:
        info["has_changelog"] = True
        # 两个标记之间的内容是 changelog 区域
        changelog_start = all_markers[0] + len(changelog_marker)
        changelog_end = all_markers[1]
        changelog_content = content[changelog_start:changelog_end]

        # 检查变更日志是否包含实质性内容
        changelog_lines = [line.strip() for line in changelog_content.split('\n') if line.strip()]
        # 过滤掉标题行和标记行
        changelog_lines = [
            line for line in changelog_lines
            if not line.startswith('#')
            and line != '## Changelog'
            and line != changelog_marker
        ]

        if not changelog_lines:
            issues.append(Issue(
                type="empty_changelog",
                name="Changelog",
                message="变更日志章节为空，缺少实质性变更记录",
                severity="warning"
            ))
        else:
            # 检查每条变更记录格式（允许可选的列表项前缀 -/*+ ）
            entry_pattern = re.compile(r"^(?:[-*+]\s+)?\d{4}-\d{2}-\d{2}\s*\|\s*(added|modified|removed|deprecated)\s*\|")
            date_extract_pattern = re.compile(r"^(?:[-*+]\s+)?(\d{4}-\d{2}-\d{2})\s*\|")
            valid_entries = 0
            for line in changelog_lines:
                if entry_pattern.match(line):
                    valid_entries += 1

            if valid_entries == 0:
                issues.append(Issue(
                    type="invalid_changelog_format",
                    name="Changelog",
                    message="变更日志格式不正确，应为: - YYYY-MM-DD | type | description（type: added/modified/removed/deprecated）",
                    severity="error"
                ))

            # 检查是否按时间倒序排列（最新在顶部）
            dated_entries = []
            for line in changelog_lines:
                dm = date_extract_pattern.match(line)
                if dm:
                    dated_entries.append(dm.group(1))
            if len(dated_entries) >= 2:
                for i in range(len(dated_entries) - 1):
                    if dated_entries[i] < dated_entries[i + 1]:
                        issues.append(Issue(
                            type="changelog_order",
                            name="Changelog",
                            message="变更记录应按时间倒序排列（最新变更在顶部）",
                            severity="warning"
                        ))
                        break

    elif len(all_markers) == 1:
        # 只有开始标记没有结束标记
        info["has_changelog"] = True  # 有标记就算有，但给警告
        issues.append(Issue(
            type="changelog_missing_end",
            name="Changelog",
            message="变更日志缺少结束标记 <!-- changelog -->，应使用成对标记包裹 Changelog 章节",
            severity="warning"
        ))
        # 仍然检查内容
        changelog_start = all_markers[0] + len(changelog_marker)
        changelog_content = content[changelog_start:]
        # 尝试找到 ## Changelog 标题后的内容
        cl_title = re.search(r"##\s+Changelog\s*\n", changelog_content)
        if cl_title:
            entries_content = changelog_content[cl_title.end():]
            entry_pattern = re.compile(r"^(?:[-*+]\s+)?\d{4}-\d{2}-\d{2}\s*\|\s*(added|modified|removed|deprecated)\s*\|", re.MULTILINE)
            if not entry_pattern.search(entries_content):
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
            message="缺少变更日志章节，需包含成对的 <!-- changelog --> 标记包裹 ## Changelog",
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
                score -= 12
            elif issue.type in ["missing_requirement", "missing_scenario"]:
                score -= 8
            elif issue.type in ["missing_scenario_part", "invalid_changelog_format"]:
                score -= 6
            elif issue.type == "missing_shall":
                score -= 4
        else:  # warning
            if issue.type in ["vague_criteria", "version_format", "changelog_missing_end", "changelog_order"]:
                score -= 3
            elif issue.type == "chapter_order":
                score -= 2
            elif issue.type in ["empty_changelog", "missing_changelog"]:
                score -= 4

    # 核心章节缺失扣分
    missing_chapters = len(CORE_CHAPTERS) - len(chapters_found)
    score -= missing_chapters * 5

    # Requirement 数量过少扣分
    if len(requirements) == 0:
        score -= 15

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
    chapter_issues, found_chapters, _ = detect_core_chapters(content)
    all_issues.extend(chapter_issues)

    # 2. 检查每个核心章节是否有实质内容
    for chapter_name, pattern, _ in CORE_CHAPTERS:
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
    elif not result.errors and result.warnings:
        print("\n✅ 检查通过（有警告，建议优化）")

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
    passed = sum(1 for r in results if not r.errors)
    failed = total - passed

    print(f"\n{'='*60}")
    print(f"检查摘要")
    print(f"{'='*60}")
    print(f"总计检查: {total} 个 spec 目录")
    print(f"通过（无错误）: {passed} 个")
    print(f"未通过（有错误）: {failed} 个")

    if failed > 0:
        print(f"\n未通过的 spec:")
        for r in results:
            if r.errors:
                print(f"  - {r.spec_path}: 评分 {r.score}/100, {len(r.errors)} 个错误")

    # 列出评分较低的
    low_score = [r for r in results if r.score < 80]
    if low_score:
        print(f"\n评分低于 80 分的 spec:")
        for r in low_score:
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
  python check-spec-format.py                                    # 检查默认目录
  python check-spec-format.py --spec-dir .trae/specs/XXX         # 指定目录
  python check-spec-format.py --check-all                        # 检查所有子目录
  python check-spec-format.py --format json --verbose            # JSON 输出格式
  python check-spec-format.py --check-all --format text          # 检查所有 spec 并文本输出
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
        help="递归检查指定目录下所有包含 spec.md 的子目录"
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
        try:
            import yaml
            if len(results) == 1:
                print(yaml.dump(results[0].to_dict(), allow_unicode=True, default_flow_style=False))
            else:
                print(yaml.dump([r.to_dict() for r in results], allow_unicode=True, default_flow_style=False))
        except ImportError:
            print("错误: 需要 PyYAML 库支持 YAML 输出，请安装: pip install pyyaml", file=sys.stderr)
            sys.exit(2)
    else:
        if len(results) == 1:
            print_result_text(results[0], args.verbose)
        else:
            print_summary_text(results)
            for r in results:
                print_result_text(r, args.verbose)

    # 确定退出码: 有错误则退出码为1
    has_errors = any(r.errors for r in results)
    if has_errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
