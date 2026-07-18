#!/usr/bin/env python3
"""解析 .xlsx 测试报告并导出 Markdown 报告。"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.analyze_xlsx import main
from lib.analyze_xlsx.context import extract_report_context
from lib.analyze_xlsx.renderer import render_release_summary, render_report
from lib.analyze_xlsx.risk_analyzer import (
    build_risk_cluster_details,
    build_risk_clusters,
    build_platform_semantic_mapping,
    classify_risk_text,
    get_platform_semantic_profile,
)
from lib.analyze_xlsx.utils import load_workbook

__all__ = [
    "main",
    "extract_report_context",
    "render_report",
    "render_release_summary",
    "build_risk_cluster_details",
    "build_risk_clusters",
    "build_platform_semantic_mapping",
    "classify_risk_text",
    "get_platform_semantic_profile",
    "load_workbook",
]


if __name__ == "__main__":
    sys.exit(main())
