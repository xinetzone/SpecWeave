from __future__ import annotations

from pathlib import Path

from .constants import DEFAULT_SUMMARY_TEMPLATE, DEFAULT_TEMPLATE
from .formatter import (
    format_basic_info_lines,
    format_blockers_lines,
    format_core_metrics_lines,
    format_module_findings_lines,
    format_overall_metrics_lines,
    format_platform_impact_lines,
    format_platform_mapping_lines,
    format_risk_cluster_lines,
    format_top_risks_lines,
    format_workbook_summary_lines,
)
from .risk_analyzer import build_retest_suggestions


def render_release_summary(context: dict, template_path: Path | None = None) -> str:
    resolved_template = template_path or DEFAULT_SUMMARY_TEMPLATE
    if not resolved_template.exists():
        raise FileNotFoundError(f"摘要模板不存在: {resolved_template}")

    template = resolved_template.read_text(encoding="utf-8")
    retest_suggestions = build_retest_suggestions(context.get("risk_clusters", []))
    retest_suggestions_lines = "\n".join(f"- {item}" for item in retest_suggestions)

    return template.format(
        title=context["title"],
        source=context["source"],
        date=context["date"],
        release_decision=context["release_judgment"]["decision"],
        release_threshold=context["release_judgment"]["threshold"],
        release_gap=context["release_judgment"]["gap"],
        core_metrics_lines=format_core_metrics_lines(context["overall_metrics"]),
        top_risks_lines=format_top_risks_lines(context.get("risk_clusters", [])),
        blockers_lines=format_blockers_lines(context),
        platform_impact_lines=format_platform_impact_lines(
            context.get("platform_semantic_mapping", [])
        ),
        retest_suggestions_lines=retest_suggestions_lines,
    )


def render_report(context: dict, template_path: Path | None = None) -> str:
    resolved_template = template_path or DEFAULT_TEMPLATE
    template = resolved_template.read_text(encoding="utf-8")

    fallback_notice = ""
    if context.get("used_fallback"):
        fallback_notice = "> 注：未识别标准总表，以下结论基于全工作簿状态词降级统计。\n"

    return template.format(
        title=context["title"],
        source=context["source"],
        date=context["date"],
        fallback_notice=fallback_notice,
        basic_info_lines=format_basic_info_lines(context["basic_info"]),
        workbook_summary_lines=format_workbook_summary_lines(context["workbook_summary"]),
        overall_metrics_lines=format_overall_metrics_lines(context["overall_metrics"]),
        release_decision=context["release_judgment"]["decision"],
        release_threshold=context["release_judgment"]["threshold"],
        release_gap=context["release_judgment"]["gap"],
        module_findings_lines=format_module_findings_lines(context["module_findings"]),
        risk_clusters_lines=format_risk_cluster_lines(context["risk_clusters"]),
        platform_mapping_lines=format_platform_mapping_lines(
            context.get("platform_semantic_mapping", [])
        ),
        final_conclusion=context["final_conclusion"],
    )
