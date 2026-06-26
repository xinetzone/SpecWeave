"""Spec 文档解析器。

提供 spec.md、tasks.md、checklist.md 的解析功能，提取结构化数据。
"""

import re
from pathlib import Path
from typing import Any


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

        section_match = re.match(
            r"^##\s+(ADDED|MODIFIED|REMOVED)\s+Requirements?",
            stripped,
            re.IGNORECASE,
        )
        if section_match:
            current_section = section_match.group(1).upper()
            continue

        req_match = re.match(r"^###\s+Requirement:\s+(.+)", stripped)
        if req_match:
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

        scenario_match = re.match(r"^####\s+Scenario:\s+(.+)", stripped)
        if scenario_match:
            scenario_name = scenario_match.group(1).strip()
            scenarios.append(
                {"name": scenario_name, "requirement": current_requirement}
            )
            continue

        if current_requirement:
            if stripped and not stripped.startswith(("-", "*", "|", "```", "<!--")):
                current_description_lines.append(stripped)

    if current_requirement:
        requirements.append(
            {
                "name": current_requirement,
                "section": current_section,
                "description": "\n".join(current_description_lines).strip(),
            }
        )

    data_refs: dict[str, int] = {}
    ref_pattern = re.compile(
        r"(\d+)\+?\s*(?:个|条|项|类|份|种|张|个?)\s*([\u4e00-\u9fa5]{2,8})"
    )
    for match in ref_pattern.finditer(text):
        number = int(match.group(1))
        desc = match.group(2)
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

        cat_match = re.match(r"^##\s+(?!\#)(.+)", stripped)
        if cat_match:
            current_category = cat_match.group(1).strip()
            categories.append(current_category)
            continue

        cp_match = re.match(r"^-\s+\[([ xX])\]\s+(.+)", stripped)
        if cp_match:
            cp_text = cp_match.group(2).strip()
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
