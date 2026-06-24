#!/usr/bin/env python3
"""规格文档一致性检查工具。

检查 spec.md、tasks.md、checklist.md 三份文档之间的一致性，包括：
- 需求 → 任务覆盖检查
- 场景 → 检查点覆盖检查
- 关键数据引用一致性检查
- 交叉引用路径有效性检查
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from constants import (
    META_DOC_KEYWORDS as _META_DOC_KEYWORDS,
    PROJECT_ROOT_PREFIXES,
    SPEC_MATCH_THRESHOLD,
)
from lib.project import resolve_project_root
from lib.cli import print_pass, print_warn, print_error, print_header, print_summary, add_common_args


# ============================================================================
# 工具函数
# ============================================================================

def extract_keywords(text: str) -> list[str]:
    """从文本中提取中文关键词（2+ 字符的连续中文字符串）。"""
    # 提取连续中文字符（长度 >= 2）
    chinese_words = re.findall(r"[\u4e00-\u9fa5]{2,}", text)
    # 同时提取英文单词（长度 >= 2）
    english_words = re.findall(r"[a-zA-Z]{2,}", text)
    return chinese_words + english_words


def semantic_match(source_text: str, target_text: str, min_matches: int = 2) -> bool:
    """检查两个文本是否语义匹配。

    提取 source 中的关键词，检查 target 中是否包含足够多的相同关键词。
    """
    source_keywords = set(extract_keywords(source_text))
    if not source_keywords:
        return False
    target_keywords = set(extract_keywords(target_text))
    common = source_keywords & target_keywords
    return len(common) >= min_matches




def resolve_path(ref: str, spec_dir: Path, project_root: Path) -> Path:
    """根据引用路径前缀选择基准目录进行解析。

    以 PROJECT_ROOT_PREFIXES 中列出的前缀开头的路径，以项目根目录为基准；
    其他相对路径以 spec 所在目录为基准。
    """
    for prefix in PROJECT_ROOT_PREFIXES:
        if ref.startswith(prefix):
            return project_root / ref
    return spec_dir / ref


# 显式元文档标记模式（HTML 注释，不可见渲染）
# 格式：<!-- meta_type: retrospective -->
_META_TYPE_PATTERN = re.compile(r"<!--\s*meta_type:\s*(\w+)\s*-->")



def detect_meta_document(spec_text: str) -> tuple[bool, str]:
    """检测 spec.md 是否为元文档（描述其他文档/项目的文档）。

    检测策略：
    1. 优先查找显式标记 `<!-- meta_type: xxx -->`（零误判）
    2. 未找到显式标记时，回退到关键词检测（有误判风险）

    Returns:
        (is_meta, detection_method): 是否为元文档，以及检测方式
            - detection_method: "explicit" | "keyword" | "none"
    """
    # 策略 1：显式标记
    match = _META_TYPE_PATTERN.search(spec_text)
    if match:
        return True, "explicit"

    # 策略 2：关键词兜底
    if any(kw in spec_text for kw in _META_DOC_KEYWORDS):
        return True, "keyword"

    return False, "none"


# ============================================================================
# 解析器
# ============================================================================

def parse_spec(filepath: Path) -> dict[str, Any]:
    """解析 spec.md，提取需求、场景和关键数据引用。

    Returns:
        {
            "requirements": [{"name": str, "section": str, "description": str}, ...],
            "scenarios": [{"name": str, "requirement": str}, ...],
            "data_refs": {描述: 数字, ...}
        }
    """
    if not filepath.exists():
        return {"requirements": [], "scenarios": [], "data_refs": {}}

    text = filepath.read_text(encoding="utf-8")

    requirements: list[dict[str, str]] = []
    scenarios: list[dict[str, str]] = []
    current_section = "UNKNOWN"
    current_requirement = ""
    current_description_lines: list[str] = []

    lines = text.splitlines()
    for line in lines:
        stripped = line.strip()

        # 检测章节标题（## ADDED/MODIFIED/REMOVED Requirements）
        section_match = re.match(
            r"^##\s+(ADDED|MODIFIED|REMOVED)\s+Requirements?",
            stripped,
            re.IGNORECASE,
        )
        if section_match:
            current_section = section_match.group(1).upper()
            continue

        # 检测需求标题（### Requirement: XXX）
        req_match = re.match(r"^###\s+Requirement:\s+(.+)", stripped)
        if req_match:
            # 保存前一个 requirement 的描述
            if current_requirement:
                requirements.append(
                    {
                        "name": current_requirement,
                        "section": current_section,
                        "description": "\n".join(current_description_lines).strip(),
                    }
                )
            current_requirement = req_match.group(1).strip()
            current_description_lines = []
            continue

        # 检测场景标题（#### Scenario: XXX）
        scenario_match = re.match(r"^####\s+Scenario:\s+(.+)", stripped)
        if scenario_match:
            scenario_name = scenario_match.group(1).strip()
            scenarios.append(
                {"name": scenario_name, "requirement": current_requirement}
            )
            continue

        # 收集当前 requirement 的描述行
        if current_requirement:
            # 跳过空行和纯 Markdown 符号行，收集实际内容
            if stripped and not stripped.startswith(("-", "*", "|", "```", "<!--")):
                current_description_lines.append(stripped)

    # 保存最后一个 requirement
    if current_requirement:
        requirements.append(
            {
                "name": current_requirement,
                "section": current_section,
                "description": "\n".join(current_description_lines).strip(),
            }
        )

    # 提取关键数据引用（如 "9 个主任务"、"42 个子任务" 等）
    data_refs: dict[str, int] = {}
    # 匹配模式：数字 + 可选"+" + 可选中文量词（个/条/项/类/份）+ 中文描述
    ref_pattern = re.compile(
        r"(\d+)\+?\s*(?:个|条|项|类|份|种|张|个?)\s*([\u4e00-\u9fa5]{2,8})"
    )
    for match in ref_pattern.finditer(text):
        number = int(match.group(1))
        desc = match.group(2)
        # 避免重复，同名覆盖
        data_refs[desc] = number

    return {
        "requirements": requirements,
        "scenarios": scenarios,
        "data_refs": data_refs,
    }


def parse_tasks(filepath: Path) -> dict[str, Any]:
    """解析 tasks.md，提取任务、子任务和统计信息。

    Returns:
        {
            "tasks": [{"name": str, "completed": bool}, ...],
            "subtasks": [{"name": str, "task": str, "completed": bool}, ...],
            "stats": {"tasks": int, "subtasks": int}
        }
    """
    if not filepath.exists():
        return {"tasks": [], "subtasks": [], "stats": {"tasks": 0, "subtasks": 0}}

    text = filepath.read_text(encoding="utf-8")

    tasks: list[dict[str, Any]] = []
    subtasks: list[dict[str, Any]] = []
    current_task_name = ""

    lines = text.splitlines()
    for line in lines:
        stripped = line.strip()

        # 匹配 Task：- [ ] Task N: XXX 或 - [x] Task N: XXX
        task_match = re.match(
            r"^-\s+\[([ xX])\]\s+Task\s+\d+:\s+(.+)", stripped
        )
        if task_match:
            current_task_name = task_match.group(2).strip()
            tasks.append(
                {
                    "name": current_task_name,
                    "completed": task_match.group(1).lower() == "x",
                }
            )
            continue

        # 匹配 SubTask：- [ ] SubTask N.M: XXX 或 - [x] SubTask N.M: XXX
        subtask_match = re.match(
            r"^-\s+\[([ xX])\]\s+SubTask\s+[\d.]+:\s+(.+)", stripped
        )
        if subtask_match:
            subtasks.append(
                {
                    "name": subtask_match.group(2).strip(),
                    "task": current_task_name,
                    "completed": subtask_match.group(1).lower() == "x",
                }
            )

    return {
        "tasks": tasks,
        "subtasks": subtasks,
        "stats": {"tasks": len(tasks), "subtasks": len(subtasks)},
    }


def parse_checklist(filepath: Path) -> dict[str, Any]:
    """解析 checklist.md，提取检查类别、检查点和统计信息。

    Returns:
        {
            "categories": [str, ...],
            "checkpoints": [{"text": str, "category": str, "completed": bool}, ...],
            "stats": {"categories": int, "checkpoints": int}
        }
    """
    if not filepath.exists():
        return {
            "categories": [],
            "checkpoints": [],
            "stats": {"categories": 0, "checkpoints": 0},
        }

    text = filepath.read_text(encoding="utf-8")

    categories: list[str] = []
    checkpoints: list[dict[str, Any]] = []
    current_category = ""

    lines = text.splitlines()
    for line in lines:
        stripped = line.strip()

        # 匹配二级标题（## XXX），但不匹配更深层级的标题
        cat_match = re.match(r"^##\s+(?!\#)(.+)", stripped)
        if cat_match:
            current_category = cat_match.group(1).strip()
            categories.append(current_category)
            continue

        # 匹配检查点：- [ ] XXX 或 - [x] XXX
        # 注意：需要排除 Task/SubTask 格式的行
        cp_match = re.match(r"^-\s+\[([ xX])\]\s+(.+)", stripped)
        if cp_match:
            cp_text = cp_match.group(2).strip()
            # 排除 Task/SubTask 格式的行（这些不应该出现在 checklist 中，但以防万一）
            if not re.match(r"^(Task|SubTask)\s+\d", cp_text):
                checkpoints.append(
                    {
                        "text": cp_text,
                        "category": current_category,
                        "completed": cp_match.group(1).lower() == "x",
                    }
                )

    return {
        "categories": categories,
        "checkpoints": checkpoints,
        "stats": {
            "categories": len(categories),
            "checkpoints": len(checkpoints),
        },
    }


# ============================================================================
# 一致性检查引擎
# ============================================================================

def check_requirement_task_coverage(
    requirements: list[dict[str, str]],
    tasks: list[dict[str, Any]],
    match_threshold: int = 1,
) -> dict[str, Any]:
    """检查需求 → 任务覆盖。

    Returns:
        {"covered": [(req_name, task_name), ...], "uncovered": [req_name, ...]}
    """
    covered: list[tuple[str, str]] = []
    uncovered: list[str] = []

    for req in requirements:
        req_name = req["name"]
        matched = False
        for task in tasks:
            if semantic_match(req_name, task["name"], min_matches=match_threshold):
                covered.append((req_name, task["name"]))
                matched = True
                break
        if not matched:
            uncovered.append(req_name)

    return {"covered": covered, "uncovered": uncovered}


def check_scenario_checkpoint_coverage(
    scenarios: list[dict[str, str]],
    checkpoints: list[dict[str, Any]],
    match_threshold: int = 1,
) -> dict[str, Any]:
    """检查场景 → 检查点覆盖。

    Returns:
        {"covered": [(scenario_name, checkpoint_text), ...], "uncovered": [scenario_name, ...]}
    """
    covered: list[tuple[str, str]] = []
    uncovered: list[str] = []

    for scenario in scenarios:
        scenario_name = scenario["name"]
        matched = False
        for cp in checkpoints:
            if semantic_match(scenario_name, cp["text"], min_matches=match_threshold):
                covered.append((scenario_name, cp["text"]))
                matched = True
                break
        if not matched:
            uncovered.append(scenario_name)

    return {"covered": covered, "uncovered": uncovered}


def check_data_consistency(
    spec_data_refs: dict[str, int],
    tasks_stats: dict[str, int],
    checklist_stats: dict[str, int],
    is_meta: bool = False,
) -> dict[str, Any]:
    """检查关键数据引用一致性。

    区分自引用数据（is_meta=False）与外部引用数据（is_meta=True）：
    - 自引用数据不一致 → 错误（需立即修复）
    - 外部引用数据不一致 → 警告（引用的是被描述对象的数据）

    Returns:
        {"consistent": [...], "inconsistent": [...], "warnings": [...]}
    """
    consistent: list[str] = []
    inconsistent: list[str] = []
    warnings: list[str] = []

    # 建立描述到实际值的映射
    desc_mapping: dict[str, tuple[int, str]] = {}

    # 任务相关
    all_task_keywords = ["主任务", "任务", "Task"]
    for kw in all_task_keywords:
        desc_mapping[kw] = (tasks_stats["tasks"], "tasks.md")

    # 子任务相关
    all_subtask_keywords = ["子任务", "SubTask"]
    for kw in all_subtask_keywords:
        desc_mapping[kw] = (tasks_stats["subtasks"], "tasks.md")

    # 检查相关
    all_category_keywords = ["检查类别", "类别", "分类"]
    for kw in all_category_keywords:
        desc_mapping[kw] = (checklist_stats["categories"], "checklist.md")

    all_checkpoint_keywords = ["检查点", "检查项"]
    for kw in all_checkpoint_keywords:
        desc_mapping[kw] = (checklist_stats["checkpoints"], "checklist.md")

    for desc, expected in spec_data_refs.items():
        # 在映射中查找匹配的描述
        found = False
        for keyword, (actual, source) in desc_mapping.items():
            if keyword in desc or desc in keyword:
                found = True
                if expected == actual:
                    consistent.append(
                        f"{desc}数量: spec 引用 {expected}，实际 {actual} — 一致"
                    )
                else:
                    if is_meta:
                        warnings.append(
                            f"{desc}数量: spec 引用 {expected}，实际 {actual}（{source}）— 疑似引用外部项目数据（元文档）"
                        )
                    else:
                        inconsistent.append(
                            f"{desc}数量: spec 引用 {expected}，实际 {actual}（{source}）— 不一致"
                        )
                break
        if not found:
            # 无法匹配的描述，视为无法验证，记录为一致
            consistent.append(f"{desc}数量: spec 引用 {expected}，无法验证对应数据源")

    return {"consistent": consistent, "inconsistent": inconsistent, "warnings": warnings}


def check_cross_references(
    spec_text: str,
    base_dir: Path,
    spec_dir: Path,
) -> dict[str, Any]:
    """检查 spec.md 中的路径引用有效性。

    Args:
        spec_text: spec.md 文本内容
        base_dir: 项目根目录
        spec_dir: spec.md 所在目录

    Returns:
        {"valid": [path, ...], "invalid": [path, ...]}
    """
    valid: list[str] = []
    invalid: list[str] = []

    # 匹配路径引用：反引号包裹的、包含目录分隔符的路径
    path_pattern = re.compile(
        r"`([^`]+)`"
    )
    for match in path_pattern.finditer(spec_text):
        path_str = match.group(1).strip()

        # 只检查包含路径分隔符的引用（排除裸文件名、命令、代码片段等）
        if "/" not in path_str and "\\" not in path_str:
            continue
        # 排除 HTTP/HTTPS URL
        if re.match(r"^https?://", path_str):
            continue
        # 排除命令行示例（包含空格）
        if " " in path_str:
            continue
        # 排除版本号
        if re.match(r"^\d+\.\d+", path_str):
            continue
        # 排除纯数字或版本标识
        if re.match(r"^[\d.]+$", path_str):
            continue
        # 排除 Windows 绝对路径（如 d:\AI\...）
        if re.match(r"^[a-zA-Z]:\\", path_str):
            continue
        # 只检查以 . 开头的项目相对路径，或包含明确文件扩展名的路径
        if not path_str.startswith(".") and not re.search(r"\.[a-zA-Z]{2,6}(?:/|$)", path_str):
            continue

        full_path = resolve_path(path_str, spec_dir, base_dir)
        if full_path.exists():
            if path_str not in valid:
                valid.append(path_str)
        else:
            if path_str not in invalid:
                invalid.append(path_str)

    return {"valid": valid, "invalid": invalid}


def check_requirement_distinctness(
    requirements: list[dict[str, str]],
) -> dict[str, Any]:
    """检查 Requirement 名称唯一性。

    Returns:
        {"duplicates": [{"name": str, "count": int, "sections": [str, ...]}, ...]}
    """
    name_count: dict[str, dict[str, Any]] = {}
    for req in requirements:
        name = req["name"]
        if name not in name_count:
            name_count[name] = {"count": 0, "sections": []}
        name_count[name]["count"] += 1
        if req["section"]:
            name_count[name]["sections"].append(req["section"])

    duplicates = [
        {"name": name, "count": data["count"], "sections": list(set(data["sections"]))}
        for name, data in name_count.items()
        if data["count"] > 1
    ]

    return {"duplicates": duplicates}


def check_requirement_clarity(
    requirements: list[dict[str, str]],
) -> dict[str, Any]:
    """检查 Requirement 描述关键词重复。

    描述中连续出现相同的2+字符词超过3次，视为重复。

    Returns:
        {"repetitive": [{"name": str, "repeated_words": [{"word": str, "count": int}, ...]}, ...]}
    """
    from collections import Counter

    repetitive: list[dict[str, Any]] = []

    for req in requirements:
        desc = req.get("description", "")
        if not desc:
            continue

        # 提取2+字符的词
        words = extract_keywords(desc)
        if len(words) < 4:
            continue

        # 统计词频
        word_counts = Counter(words)
        # 找出出现超过3次的词
        repeated = [
            {"word": word, "count": count}
            for word, count in word_counts.items()
            if count > 3
        ]

        if repeated:
            repetitive.append({"name": req["name"], "repeated_words": repeated})

    return {"repetitive": repetitive}


def check_scenario_executability(
    scenarios: list[dict[str, str]],
    spec_text: str,
) -> dict[str, Any]:
    """检查 Scenario 结构完整性（是否包含 WHEN 和 THEN）。

    Returns:
        {"missing_structure": [{"name": str, "requirement": str, "missing": [str, ...]}, ...]}
    """
    missing_structure: list[dict[str, Any]] = []

    for scenario in scenarios:
        scenario_name = scenario["name"]

        # 在 spec_text 中查找该 scenario 的内容
        # Scenario 标题格式：#### Scenario: XXX
        scenario_pattern = re.compile(
            r"^####\s+Scenario:\s+" + re.escape(scenario_name) + r"(.*?)(?=^####|\Z)",
            re.MULTILINE | re.DOTALL,
        )
        match = scenario_pattern.search(spec_text)

        if not match:
            continue

        scenario_content = match.group(1)

        # 检查是否包含 WHEN 和 THEN
        missing: list[str] = []
        if "WHEN" not in scenario_content and "GIVEN" not in scenario_content:
            missing.append("WHEN/GIVEN")
        if "THEN" not in scenario_content and "EXPECT" not in scenario_content:
            missing.append("THEN/EXPECT")

        if missing:
            missing_structure.append({
                "name": scenario_name,
                "requirement": scenario.get("requirement", ""),
                "missing": missing,
            })

    return {"missing_structure": missing_structure}


# ============================================================================
# 输出模块
# ============================================================================

def generate_terminal_report(
    spec_dir: str,
    requirement_coverage: dict[str, Any],
    scenario_coverage: dict[str, Any],
    data_consistency: dict[str, Any],
    cross_references: dict[str, Any],
    requirement_distinctness: dict[str, Any],
    requirement_clarity: dict[str, Any],
    scenario_executability: dict[str, Any],
) -> tuple[int, int, int]:
    """生成终端彩色报告，返回 (通过数, 警告数, 错误数)。"""
    pass_count = 0
    warn_count = 0
    error_count = 0

    print_header("规格文档一致性检查报告")
    print(f"检查目录: {spec_dir}")
    print()

    # ── 需求 → 任务覆盖 ──
    print("[需求 → 任务覆盖]")
    for req_name, task_name in requirement_coverage["covered"]:
        print_pass(f"需求 \"{req_name}\" → 任务 \"{task_name}\"")
        pass_count += 1
    for req_name in requirement_coverage["uncovered"]:
        print_warn(f"需求 \"{req_name}\" 在 tasks.md 中无对应任务")
        warn_count += 1
    print()

    # ── 场景 → 检查点覆盖 ──
    print("[场景 → 检查点覆盖]")
    for scenario_name, cp_text in scenario_coverage["covered"]:
        print_pass(f"场景 \"{scenario_name}\" → 检查点 \"{cp_text}\"")
        pass_count += 1
    for scenario_name in scenario_coverage["uncovered"]:
        print_warn(f"场景 \"{scenario_name}\" 在 checklist.md 中无对应检查点")
        warn_count += 1
    print()

    # ── 数据引用一致性 ──
    print("[数据引用一致性]")
    for item in data_consistency["consistent"]:
        print_pass(item)
        pass_count += 1
    for item in data_consistency["inconsistent"]:
        print_error(item)
        error_count += 1
    for item in data_consistency.get("warnings", []):
        print_warn(item)
        warn_count += 1
    print()

    # ── 交叉引用有效性 ──
    print("[交叉引用有效性]")
    for path_str in cross_references["valid"]:
        print_pass(path_str)
        pass_count += 1
    for path_str in cross_references["invalid"]:
        print_error(f"{path_str} — 文件不存在")
        error_count += 1
    print()

    # ── 区分度检查（Requirement 名称唯一性） ──
    print("[区分度检查 - Requirement 名称唯一性]")
    duplicates = requirement_distinctness.get("duplicates", [])
    if not duplicates:
        print_pass("所有 Requirement 名称唯一")
        pass_count += 1
    else:
        for dup in duplicates:
            sections_str = ", ".join(dup["sections"]) if dup["sections"] else "未知"
            print_warn(f"Requirement 名称 \"{dup['name']}\" 重复 {dup['count']} 次（出现章节：{sections_str}）")
            warn_count += 1
    print()

    # ── 清晰度检查（描述关键词重复） ──
    print("[清晰度检查 - Requirement 描述关键词重复]")
    repetitive = requirement_clarity.get("repetitive", [])
    if not repetitive:
        print_pass("Requirement 描述无明显关键词重复")
        pass_count += 1
    else:
        for item in repetitive:
            words_str = ", ".join(
                f"\"{w['word']}\"({w['count']}次)" for w in item["repeated_words"]
            )
            print_warn(f"Requirement \"{item['name']}\" 描述存在关键词重复: {words_str}")
            warn_count += 1
    print()

    # ── 可执行性检查（Scenario 结构完整性） ──
    print("[可执行性检查 - Scenario 结构完整性]")
    missing_structure = scenario_executability.get("missing_structure", [])
    if not missing_structure:
        print_pass("所有 Scenario 结构完整（包含 WHEN/GIVEN 和 THEN/EXPECT）")
        pass_count += 1
    else:
        for item in missing_structure:
            missing_str = ", ".join(item["missing"])
            print_error(f"Scenario \"{item['name']}\" 缺少结构: {missing_str}")
            error_count += 1
    print()

    print_summary(pass_count, warn_count, error_count)

    return pass_count, warn_count, error_count


def generate_json_report(
    spec_dir: str,
    requirement_coverage: dict[str, Any],
    scenario_coverage: dict[str, Any],
    data_consistency: dict[str, Any],
    cross_references: dict[str, Any],
    requirement_distinctness: dict[str, Any],
    requirement_clarity: dict[str, Any],
    scenario_executability: dict[str, Any],
    pass_count: int,
    warn_count: int,
    error_count: int,
) -> str:
    """生成 JSON 格式报告。"""
    report = {
        "spec_dir": spec_dir,
        "summary": {
            "pass": pass_count,
            "warning": warn_count,
            "error": error_count,
        },
        "checks": {
            "requirement_task_coverage": {
                "covered": [
                    {"requirement": r, "task": t}
                    for r, t in requirement_coverage["covered"]
                ],
                "uncovered": requirement_coverage["uncovered"],
            },
            "scenario_checkpoint_coverage": {
                "covered": [
                    {"scenario": s, "checkpoint": c}
                    for s, c in scenario_coverage["covered"]
                ],
                "uncovered": scenario_coverage["uncovered"],
            },
            "data_consistency": {
                "consistent": data_consistency["consistent"],
                "inconsistent": data_consistency["inconsistent"],
                "warnings": data_consistency.get("warnings", []),
            },
            "cross_references": {
                "valid": cross_references["valid"],
                "invalid": cross_references["invalid"],
            },
            "requirement_distinctness": requirement_distinctness,
            "requirement_clarity": requirement_clarity,
            "scenario_executability": scenario_executability,
        },
    }
    return json.dumps(report, ensure_ascii=False, indent=2)


# ============================================================================
# 主流程
# ============================================================================

def check_single_spec(
    spec_dir: Path,
    json_output: bool = False,
    match_threshold: int = 1,
) -> int:
    """对单个 spec 目录执行一致性检查。

    Args:
        spec_dir: spec 目录路径
        json_output: 是否以 JSON 格式输出
        match_threshold: 语义匹配最少共同关键词数

    Returns:
        退出码：0 表示全部通过，1 表示有错误
    """
    spec_file = spec_dir / "spec.md"
    tasks_file = spec_dir / "tasks.md"
    checklist_file = spec_dir / "checklist.md"

    # 检查文件是否存在
    missing_files = []
    if not spec_file.exists():
        missing_files.append("spec.md")
    if not tasks_file.exists():
        missing_files.append("tasks.md")
    if not checklist_file.exists():
        missing_files.append("checklist.md")

    if missing_files:
        if json_output:
            error_report = {
                "spec_dir": str(spec_dir),
                "summary": {"pass": 0, "warning": 0, "error": 1},
                "checks": {},
                "error": f"缺少文件: {', '.join(missing_files)}",
            }
            print(json.dumps(error_report, ensure_ascii=False, indent=2))
        else:
            print_error(f"spec 目录 {spec_dir} 中缺少文件: {', '.join(missing_files)}")
        return 1

    # 解析
    spec_data = parse_spec(spec_file)
    tasks_data = parse_tasks(tasks_file)
    checklist_data = parse_checklist(checklist_file)

    # 读取 spec 文本（用于元文档检测和交叉引用检查）
    spec_text = spec_file.read_text(encoding="utf-8")

    # 确定项目根目录（spec_dir → .trae/specs/XXX → .trae/specs → .trae → 项目根）
    project_root = spec_dir.parent.parent.parent
    is_meta, detection_method = detect_meta_document(spec_text)

    # 一致性检查
    requirement_coverage = check_requirement_task_coverage(
        spec_data["requirements"], tasks_data["tasks"], match_threshold=match_threshold
    )
    scenario_coverage = check_scenario_checkpoint_coverage(
        spec_data["scenarios"], checklist_data["checkpoints"], match_threshold=match_threshold
    )
    data_consistency = check_data_consistency(
        spec_data["data_refs"],
        tasks_data["stats"],
        checklist_data["stats"],
        is_meta=is_meta,
    )
    cross_references = check_cross_references(
        spec_text,
        project_root,
        spec_dir,
    )

    # 新增检查
    requirement_distinctness = check_requirement_distinctness(spec_data["requirements"])
    requirement_clarity = check_requirement_clarity(spec_data["requirements"])
    scenario_executability = check_scenario_executability(
        spec_data["scenarios"], spec_text
    )

    # 统计
    pass_count = 0
    warn_count = 0
    error_count = 0

    pass_count += len(requirement_coverage["covered"])
    warn_count += len(requirement_coverage["uncovered"])

    pass_count += len(scenario_coverage["covered"])
    warn_count += len(scenario_coverage["uncovered"])

    pass_count += len(data_consistency["consistent"])
    error_count += len(data_consistency["inconsistent"])
    warn_count += len(data_consistency.get("warnings", []))

    pass_count += len(cross_references["valid"])
    error_count += len(cross_references["invalid"])

    # 新增统计
    warn_count += len(requirement_distinctness["duplicates"])
    warn_count += len(requirement_clarity["repetitive"])
    error_count += len(scenario_executability["missing_structure"])

    # 输出
    if json_output:
        print(
            generate_json_report(
                str(spec_dir),
                requirement_coverage,
                scenario_coverage,
                data_consistency,
                cross_references,
                requirement_distinctness,
                requirement_clarity,
                scenario_executability,
                pass_count,
                warn_count,
                error_count,
            )
        )
    else:
        generate_terminal_report(
            str(spec_dir),
            requirement_coverage,
            scenario_coverage,
            data_consistency,
            cross_references,
            requirement_distinctness,
            requirement_clarity,
            scenario_executability,
        )

    return 0 if error_count == 0 else 1


def discover_spec_dirs(project_root: Path) -> list[Path]:
    """发现项目中的所有 spec 目录。"""
    specs_root = project_root / ".trae" / "specs"
    if not specs_root.exists():
        return []
    return sorted(
        [d for d in specs_root.iterdir() if d.is_dir()],
        key=lambda p: p.name,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="规格文档一致性检查工具",
    )
    add_common_args(parser)
    parser.add_argument(
        "--spec-dir",
        type=str,
        default=None,
        help="指定要检查的 spec 目录路径",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        default=False,
        help="扫描所有 spec 目录（默认行为）",
    )
    parser.add_argument(
        "--match-threshold",
        type=int,
        default=SPEC_MATCH_THRESHOLD,
        help="语义匹配最少共同关键词数（默认：1）",
    )

    args = parser.parse_args()
    project_root = resolve_project_root(__file__)

    if args.spec_dir:
        # 指定单个 spec 目录
        spec_dir = Path(args.spec_dir)
        if not spec_dir.is_absolute():
            spec_dir = project_root / args.spec_dir
        if not spec_dir.exists():
            print_error(f"spec 目录不存在: {spec_dir}")
            return 1
        return check_single_spec(
            spec_dir, json_output=args.json, match_threshold=args.match_threshold
        )

    # --all 或默认行为：扫描所有 spec 目录
    spec_dirs = discover_spec_dirs(project_root)
    if not spec_dirs:
        print_warn("未找到任何 spec 目录")
        return 0

    overall_exit_code = 0

    if args.json:
        # JSON 模式下输出一个数组
        all_reports = []
        for spec_dir in spec_dirs:
            spec_file = spec_dir / "spec.md"
            tasks_file = spec_dir / "tasks.md"
            checklist_file = spec_dir / "checklist.md"

            missing = []
            if not spec_file.exists():
                missing.append("spec.md")
            if not tasks_file.exists():
                missing.append("tasks.md")
            if not checklist_file.exists():
                missing.append("checklist.md")

            if missing:
                all_reports.append({
                    "spec_dir": str(spec_dir),
                    "summary": {"pass": 0, "warning": 0, "error": 1},
                    "checks": {},
                    "error": f"缺少文件: {', '.join(missing)}",
                })
                overall_exit_code = 1
                continue

            spec_data = parse_spec(spec_file)
            tasks_data = parse_tasks(tasks_file)
            checklist_data = parse_checklist(checklist_file)

            spec_text = spec_file.read_text(encoding="utf-8")
            is_meta, _ = detect_meta_document(spec_text)

            requirement_coverage = check_requirement_task_coverage(
                spec_data["requirements"], tasks_data["tasks"],
                match_threshold=args.match_threshold,
            )
            scenario_coverage = check_scenario_checkpoint_coverage(
                spec_data["scenarios"], checklist_data["checkpoints"],
                match_threshold=args.match_threshold,
            )
            data_consistency = check_data_consistency(
                spec_data["data_refs"],
                tasks_data["stats"],
                checklist_data["stats"],
                is_meta=is_meta,
            )
            cross_references = check_cross_references(
                spec_text,
                project_root,
                spec_dir,
            )

            # 新增检查
            requirement_distinctness = check_requirement_distinctness(spec_data["requirements"])
            requirement_clarity = check_requirement_clarity(spec_data["requirements"])
            scenario_executability = check_scenario_executability(
                spec_data["scenarios"], spec_text
            )

            pass_count = (
                len(requirement_coverage["covered"])
                + len(scenario_coverage["covered"])
                + len(data_consistency["consistent"])
                + len(cross_references["valid"])
            )
            warn_count = (
                len(requirement_coverage["uncovered"])
                + len(scenario_coverage["uncovered"])
                + len(data_consistency.get("warnings", []))
                + len(requirement_distinctness["duplicates"])
                + len(requirement_clarity["repetitive"])
            )
            error_count = (
                len(data_consistency["inconsistent"])
                + len(cross_references["invalid"])
                + len(scenario_executability["missing_structure"])
            )

            if error_count > 0:
                overall_exit_code = 1

            all_reports.append({
                "spec_dir": str(spec_dir),
                "summary": {
                    "pass": pass_count,
                    "warning": warn_count,
                    "error": error_count,
                },
                "checks": {
                    "requirement_task_coverage": {
                        "covered": [
                            {"requirement": r, "task": t}
                            for r, t in requirement_coverage["covered"]
                        ],
                        "uncovered": requirement_coverage["uncovered"],
                    },
                    "scenario_checkpoint_coverage": {
                        "covered": [
                            {"scenario": s, "checkpoint": c}
                            for s, c in scenario_coverage["covered"]
                        ],
                        "uncovered": scenario_coverage["uncovered"],
                    },
                    "data_consistency": {
                        "consistent": data_consistency["consistent"],
                        "inconsistent": data_consistency["inconsistent"],
                        "warnings": data_consistency.get("warnings", []),
                    },
                    "cross_references": {
                        "valid": cross_references["valid"],
                        "invalid": cross_references["invalid"],
                    },
                    "requirement_distinctness": requirement_distinctness,
                    "requirement_clarity": requirement_clarity,
                    "scenario_executability": scenario_executability,
                },
            })

        print(json.dumps(all_reports, ensure_ascii=False, indent=2))
    else:
        for spec_dir in spec_dirs:
            exit_code = check_single_spec(
                spec_dir, json_output=False, match_threshold=args.match_threshold
            )
            if exit_code != 0:
                overall_exit_code = 1
            print()  # 多目录之间空行分隔

    return overall_exit_code


if __name__ == "__main__":
    sys.exit(main())