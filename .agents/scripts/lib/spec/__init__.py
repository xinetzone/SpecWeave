""".agents/scripts/lib/spec/ — Spec 文档检查共享工具库

提供 spec 文档解析、格式检查、一致性检查、报告生成等可复用模块。
"""

from .models import Issue, SpecCheckResult
from .utils import (
    extract_keywords,
    semantic_match,
    resolve_path,
    detect_meta_document,
    discover_spec_dirs,
    CORE_CHAPTERS,
    VAGUE_WORDS,
    calculate_score,
)
from .parsers import parse_spec, parse_tasks, parse_checklist
from .consistency_checkers import (
    check_requirement_task_coverage,
    check_scenario_checkpoint_coverage,
    check_data_consistency,
    check_cross_references,
    check_requirement_distinctness,
    check_requirement_clarity,
    check_scenario_executability,
)
from .format_checkers import (
    detect_core_chapters,
    find_chapter_end,
    check_chapter_not_empty,
    detect_requirements,
    check_acceptance_criteria,
    check_version_and_changelog,
)
from .reporters import (
    generate_consistency_terminal_report,
    generate_consistency_json_report,
    print_format_result_text,
    print_format_summary_text,
)

__all__ = [
    "Issue",
    "SpecCheckResult",
    "extract_keywords",
    "semantic_match",
    "resolve_path",
    "detect_meta_document",
    "discover_spec_dirs",
    "CORE_CHAPTERS",
    "VAGUE_WORDS",
    "calculate_score",
    "parse_spec",
    "parse_tasks",
    "parse_checklist",
    "check_requirement_task_coverage",
    "check_scenario_checkpoint_coverage",
    "check_data_consistency",
    "check_cross_references",
    "check_requirement_distinctness",
    "check_requirement_clarity",
    "check_scenario_executability",
    "detect_core_chapters",
    "find_chapter_end",
    "check_chapter_not_empty",
    "detect_requirements",
    "check_acceptance_criteria",
    "check_version_and_changelog",
    "generate_consistency_terminal_report",
    "generate_consistency_json_report",
    "print_format_result_text",
    "print_format_summary_text",
]
