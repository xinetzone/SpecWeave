"""Spec 文档一致性检查器。

提供需求→任务覆盖、场景→检查点覆盖、数据一致性、交叉引用等检查功能。
"""

import re
from collections import Counter
from pathlib import Path
from typing import Any

from .utils import (
    extract_keywords,
    resolve_path,
    semantic_match,
)


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

    desc_mapping: dict[str, tuple[int, str]] = {}

    all_task_keywords = ["主任务", "任务", "Task"]
    for kw in all_task_keywords:
        desc_mapping[kw] = (tasks_stats["tasks"], "tasks.md")

    all_subtask_keywords = ["子任务", "SubTask"]
    for kw in all_subtask_keywords:
        desc_mapping[kw] = (tasks_stats["subtasks"], "tasks.md")

    all_category_keywords = ["检查类别", "类别", "分类"]
    for kw in all_category_keywords:
        desc_mapping[kw] = (checklist_stats["categories"], "checklist.md")

    all_checkpoint_keywords = ["检查点", "检查项"]
    for kw in all_checkpoint_keywords:
        desc_mapping[kw] = (checklist_stats["checkpoints"], "checklist.md")

    for desc, expected in spec_data_refs.items():
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

    path_pattern = re.compile(r"`([^`]+)`")
    for match in path_pattern.finditer(spec_text):
        path_str = match.group(1).strip()

        if "/" not in path_str and "\\" not in path_str:
            continue
        if re.match(r"^https?://", path_str):
            continue
        if " " in path_str:
            continue
        if re.match(r"^\d+\.\d+", path_str):
            continue
        if re.match(r"^[\d.]+$", path_str):
            continue
        if re.match(r"^[a-zA-Z]:\\", path_str):
            continue
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
    repetitive: list[dict[str, Any]] = []

    for req in requirements:
        desc = req.get("description", "")
        if not desc:
            continue

        words = extract_keywords(desc)
        if len(words) < 4:
            continue

        word_counts = Counter(words)
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

        scenario_pattern = re.compile(
            r"^####\s+Scenario:\s+" + re.escape(scenario_name) + r"(.*?)(?=^####|\Z)",
            re.MULTILINE | re.DOTALL,
        )
        match = scenario_pattern.search(spec_text)

        if not match:
            continue

        scenario_content = match.group(1)

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
