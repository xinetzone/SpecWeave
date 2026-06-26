"""Spec 文档格式检查器。

提供核心章节检测、Requirement 完整性、验收标准、版本号与变更日志等格式检查功能。
"""

import re
from typing import Any, Optional

from .models import Issue
from .utils import CORE_CHAPTERS, VAGUE_WORDS


def detect_core_chapters(content: str) -> tuple[list[Issue], list[str], dict]:
    """检测核心章节是否存在及顺序是否正确。

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
                severity="error",
            ))

    sorted_chapters = sorted(found_positions.items(), key=lambda x: x[1])
    expected_order = [name for name, _, _ in CORE_CHAPTERS if name in found_chapters]
    actual_order = [name for name, _ in sorted_chapters]

    if expected_order != actual_order:
        issues.append(Issue(
            type="chapter_order",
            name="章节顺序",
            message=f"章节顺序不正确，期望: {' → '.join(expected_order)}, 实际: {' → '.join(actual_order)}",
            severity="warning",
        ))

    return issues, found_chapters, found_positions


def find_chapter_end(content: str, chapter_start_match, next_patterns: list[re.Pattern]) -> int:
    """找到章节结束位置（下一个同级或更高级标题的起始位置）。"""
    start = chapter_start_match.end()
    earliest_end = len(content)

    for pat in next_patterns:
        m = pat.search(content, start)
        if m and m.start() < earliest_end:
            earliest_end = m.start()

    return earliest_end


def check_chapter_not_empty(content: str, chapter_name: str, pattern: re.Pattern) -> Optional[Issue]:
    """检查章节是否有实质内容（不只是标题）。"""
    match = pattern.search(content)
    if not match:
        return None

    next_chapter = re.search(r"\n##\s+", content[match.end():])
    end = next_chapter.start() + match.end() if next_chapter else len(content)

    chapter_content = content[match.end():end].strip()

    if len(chapter_content) < 10:
        no_content_markers = ["无", "暂无", "N/A", "n/a", "None", "none", "无。", "暂无。"]
        is_explicit_no = any(chapter_content.strip() in [m, m + "。"] for m in no_content_markers)
        if not is_explicit_no:
            return Issue(
                type="empty_chapter",
                name=chapter_name,
                message=f"章节 '{chapter_name}' 内容为空或过于简略（若无内容请注明「无」）",
                severity="error",
            )

    return None


def detect_requirements(content: str) -> tuple[list[Issue], list[dict]]:
    """检测 Requirement 结构的完整性。

    每个 Requirement 必须包含:
    - 名称（以 "### Requirement:" 开头）
    - 主体描述（建议使用"系统 SHALL"，但不强制）
    - 至少一个 Scenario
    """
    issues = []
    requirements = []

    req_pattern = re.compile(
        r"^###\s+Requirement:\s*(.+?)$",
        re.MULTILINE,
    )
    req_matches = list(req_pattern.finditer(content))

    if not req_matches:
        has_req_section = bool(re.search(r"^##\s+(?:ADDED|MODIFIED|REMOVED)\s+Requirements", content, re.MULTILINE))
        if has_req_section:
            issues.append(Issue(
                type="missing_requirement",
                name="Requirement",
                message="未找到标准格式的 Requirement 定义（应以 '### Requirement:' 开头）",
                severity="warning",
            ))
        return issues, requirements

    req_blocks = []
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
            next_section = re.search(r"\n##\s+", content[req_match.end():])
            end_pos = next_section.start() + req_match.end() if next_section else len(content)
        req_content = content[start_pos:end_pos]
        section = get_section_for_pos(start_pos)
        req_blocks.append((req_name, req_content, start_pos, section))

    for req_name, req_content, _, section in req_blocks:
        has_shall = bool(re.search(r"系统\s+SHALL|系统\s+SHALL\s+NOT|SHALL\s+|SHALL\s+NOT\s+", req_content))

        scenario_pattern = re.compile(r"^####\s+Scenario:\s*(.+?)$", re.MULTILINE)
        scenario_matches = list(scenario_pattern.finditer(req_content))

        req_info: dict[str, Any] = {
            "name": req_name,
            "has_shall": has_shall,
            "scenario_count": len(scenario_matches),
            "scenarios": [],
        }

        for i, scenario in enumerate(scenario_matches):
            scenario_name = scenario.group(1).strip()
            scen_start = scenario.start()
            if i + 1 < len(scenario_matches):
                scen_end = scenario_matches[i + 1].start()
            else:
                next_req = req_pattern.search(req_content, scenario.end())
                next_section = re.search(r"\n##\s+", req_content[scenario.end():])
                end1 = next_req.start() + scenario.end() if next_req else len(req_content)
                end2 = next_section.start() + scenario.end() if next_section else len(req_content)
                scen_end = min(end1, end2)
            scenario_content = req_content[scen_start:scen_end]

            has_when_title = bool(re.search(r"^#{3,5}\s+WHEN\s*$", scenario_content, re.MULTILINE))
            has_then_title = bool(re.search(r"^#{3,5}\s+THEN\s*$", scenario_content, re.MULTILINE))
            has_when_list = bool(re.search(r"^[\s]*[-*+]\s+\*\*WHEN\*\*", scenario_content, re.MULTILINE))
            has_then_list = bool(re.search(r"^[\s]*[-*+]\s+\*\*THEN\*\*", scenario_content, re.MULTILINE))
            has_when = has_when_title or has_when_list
            has_then = has_then_title or has_then_list

            req_info["scenarios"].append({
                "name": scenario_name,
                "has_when": has_when,
                "has_then": has_then,
                "has_and": bool(re.search(r"^#{3,5}\s+AND\s*$|^[\s]*[-*+]\s+\*\*AND\*\*", scenario_content, re.MULTILINE)),
            })

            if not has_when:
                issues.append(Issue(
                    type="missing_scenario_part",
                    name=f"Scenario: {scenario_name}",
                    message=f"Scenario '{scenario_name}' 缺少 WHEN 部分（应使用 '#### Scenario:' 下的 '- **WHEN**' 列表项或 '##### WHEN' 标题）",
                    severity="error",
                ))

            if not has_then:
                issues.append(Issue(
                    type="missing_scenario_part",
                    name=f"Scenario: {scenario_name}",
                    message=f"Scenario '{scenario_name}' 缺少 THEN 部分（应使用 '#### Scenario:' 下的 '- **THEN**' 列表项或 '##### THEN' 标题）",
                    severity="error",
                ))

        if not has_shall and section != "REMOVED":
            issues.append(Issue(
                type="missing_shall",
                name=f"Requirement: {req_name}",
                message=f"Requirement '{req_name}' 建议使用 '系统 SHALL' 句式描述功能行为",
                severity="warning",
            ))

        if len(scenario_matches) == 0:
            issues.append(Issue(
                type="missing_scenario",
                name=f"Requirement: {req_name}",
                message=f"Requirement '{req_name}' 缺少 Scenario 定义",
                severity="error",
            ))

        requirements.append(req_info)

    return issues, requirements


def check_acceptance_criteria(content: str) -> list[Issue]:
    """检查 Scenario 的验收标准是否具体可测量。

    支持两种格式: ##### THEN 标题格式 和 - **THEN** 列表项格式
    """
    issues = []

    then_title_pattern = re.compile(
        r"^#{3,5}\s+THEN\s*\n((?:\s*[-*+]\s*.+\n)*)",
        re.MULTILINE,
    )
    then_list_pattern = re.compile(
        r"^[\s]*[-*+]\s+\*\*THEN\*\*\s*\n((?:\s*[-*+]\s*.+\n)*)",
        re.MULTILINE,
    )

    then_contents = []
    for m in then_title_pattern.finditer(content):
        then_contents.append(m.group(1))
    for m in then_list_pattern.finditer(content):
        then_contents.append(m.group(1))

    reported_words = set()
    for then_content in then_contents:
        for word in VAGUE_WORDS:
            if word in then_content and word not in reported_words:
                issues.append(Issue(
                    type="vague_criteria",
                    name="验收标准",
                    message=f"验收标准使用了模糊词汇 '{word}'，应使用具体数值或可验证状态描述",
                    severity="warning",
                ))
                reported_words.add(word)

    return issues


def check_version_and_changelog(content: str) -> tuple[list[Issue], dict]:
    """检查版本号声明和变更日志格式。

    支持两种版本号格式:
    1. TOML frontmatter 格式（推荐）: ---\\nversion: X.Y\\n---
    2. 简单头部声明（兼容旧格式）: version: X.Y（文件前5行）
    """
    issues = []
    info: dict[str, Any] = {"has_version": False, "has_changelog": False, "version": None, "version_format": None}

    fm_version_pattern = re.compile(
        r"^---\s*\n(?:.*\n)*?version:\s*(\d+\.\d+)\s*\n(?:.*\n)*?---",
        re.MULTILINE,
    )
    fm_match = fm_version_pattern.search(content)

    if fm_match:
        info["has_version"] = True
        info["version"] = fm_match.group(1)
        info["version_format"] = "toml-frontmatter"
    else:
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
                    severity="warning",
                ))
                break

    if not info["has_version"]:
        issues.append(Issue(
            type="missing_version",
            name="版本号",
            message="缺少版本号声明，推荐使用 TOML frontmatter 格式: ---\\nversion: X.Y\\n---",
            severity="error",
        ))

    changelog_marker = "<!-- changelog -->"
    all_markers = [m.start() for m in re.finditer(re.escape(changelog_marker), content)]

    if len(all_markers) >= 2:
        info["has_changelog"] = True
        changelog_start = all_markers[0] + len(changelog_marker)
        changelog_end = all_markers[1]
        changelog_content = content[changelog_start:changelog_end]

        changelog_lines = [line.strip() for line in changelog_content.split('\n') if line.strip()]
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
                severity="warning",
            ))
        else:
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
                    severity="error",
                ))

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
                            severity="warning",
                        ))
                        break

    elif len(all_markers) == 1:
        info["has_changelog"] = True
        issues.append(Issue(
            type="changelog_missing_end",
            name="Changelog",
            message="变更日志缺少结束标记 <!-- changelog -->，应使用成对标记包裹 Changelog 章节",
            severity="warning",
        ))
        changelog_start = all_markers[0] + len(changelog_marker)
        changelog_content = content[changelog_start:]
        cl_title = re.search(r"##\s+Changelog\s*\n", changelog_content)
        if cl_title:
            entries_content = changelog_content[cl_title.end():]
            entry_pattern = re.compile(r"^(?:[-*+]\s+)?\d{4}-\d{2}-\d{2}\s*\|\s*(added|modified|removed|deprecated)\s*\|", re.MULTILINE)
            if not entry_pattern.search(entries_content):
                issues.append(Issue(
                    type="invalid_changelog_format",
                    name="Changelog",
                    message="变更日志格式不正确，应为: YYYY-MM-DD | type | description",
                    severity="error",
                ))
    else:
        issues.append(Issue(
            type="missing_changelog",
            name="Changelog",
            message="缺少变更日志章节，需包含成对的 <!-- changelog --> 标记包裹 ## Changelog",
            severity="warning",
        ))

    return issues, info
