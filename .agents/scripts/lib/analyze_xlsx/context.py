from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .metrics import (
    build_final_conclusion,
    build_release_judgment,
    collect_module_findings,
    detect_overview_sheet,
    extract_basic_info,
    extract_key_value_metrics,
    fallback_metrics,
    has_complete_overview_metrics,
    summarize_workbook,
)
from .risk_analyzer import build_platform_semantic_mapping, build_risk_cluster_details, build_risk_clusters
from .utils import load_workbook


def extract_report_context(input_path: Path) -> dict:
    workbook = load_workbook(input_path)
    overview_name = detect_overview_sheet(workbook)
    overview_sheet = workbook[overview_name] if overview_name else None

    metrics = extract_key_value_metrics(overview_sheet) if overview_sheet else None
    used_fallback = metrics is None or not has_complete_overview_metrics(metrics)
    overall_metrics = fallback_metrics(workbook) if used_fallback else metrics

    workbook_summary = summarize_workbook(workbook, overview_name)
    risk_cluster_details = build_risk_cluster_details(workbook, overview_name)
    risk_clusters = (
        [str(item["label"]) for item in risk_cluster_details[:5]]
        if risk_cluster_details
        else build_risk_clusters(workbook, overview_name)
    )
    release_judgment = build_release_judgment(overall_metrics)

    return {
        "title": f"{input_path.stem} 测试报告学习摘要",
        "source": str(input_path),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "overview_sheet": overview_name,
        "used_fallback": used_fallback,
        "basic_info": extract_basic_info(overview_sheet, input_path),
        "workbook_summary": workbook_summary,
        "overall_metrics": overall_metrics,
        "release_judgment": release_judgment,
        "module_findings": collect_module_findings(workbook, overview_name),
        "risk_cluster_details": risk_cluster_details,
        "risk_clusters": risk_clusters,
        "platform_semantic_mapping": build_platform_semantic_mapping(risk_clusters),
        "final_conclusion": build_final_conclusion(
            release_judgment, risk_clusters, used_fallback
        ),
    }
