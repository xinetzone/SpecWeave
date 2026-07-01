#!/usr/bin/env python3
"""解析 .xlsx 测试报告并导出 Markdown 报告。"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import openpyxl

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

PROJECT_ROOT = SCRIPTS_DIR.parents[1]
DEFAULT_TEMPLATE = (
    PROJECT_ROOT / "docs" / "retrospective" / "templates" / "xlsx-test-report-template.md"
)

METRIC_KEY_MAP = {
    "总用例": "total_cases",
    "所有用例": "total_cases",
    "PASS": "pass",
    "FAIL": "fail",
    "NOTEST": "notest",
    "NOT TEST": "notest",
    "NT": "notest",
    "BLOCK": "block",
    "DI": "di",
    "DI值": "di",
    "严重问题数": "serious_issues",
    "所有严重问题": "serious_issues",
}

STATUS_VALUE_MAP = {
    "PASS": "pass",
    "FAIL": "fail",
    "NT": "notest",
    "NOTEST": "notest",
    "NOT TEST": "notest",
    "BLOCK": "block",
}


def configure_stdio() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="解析 .xlsx 测试报告并导出 Markdown")
    parser.add_argument("--input", required=True, help="输入 .xlsx 文件路径")
    parser.add_argument("--output", required=True, help="输出 Markdown 文件路径")
    parser.add_argument(
        "--template",
        default=str(DEFAULT_TEMPLATE),
        help="Markdown 模板路径",
    )
    return parser.parse_args()


def load_workbook(input_path: Path):
    if not input_path.exists():
        raise FileNotFoundError(f"输入文件不存在: {input_path}")

    try:
        return openpyxl.load_workbook(input_path, data_only=True)
    except Exception as exc:  # pragma: no cover - 依赖 openpyxl 具体异常类型
        raise RuntimeError(f"无法读取工作簿: {input_path}") from exc


def normalize_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def normalize_metric_key(value: object) -> str:
    return normalize_text(value).upper()


def detect_overview_sheet(workbook) -> str | None:
    for sheet in workbook.worksheets:
        if "测试报告" in sheet.title:
            return sheet.title
    return None


def count_status_words(sheet) -> dict[str, int]:
    counts = {"pass": 0, "fail": 0, "notest": 0, "block": 0}

    for row in sheet.iter_rows(values_only=True):
        for cell in row:
            normalized = normalize_metric_key(cell)
            status_key = STATUS_VALUE_MAP.get(normalized)
            if status_key:
                counts[status_key] += 1

    return counts


def extract_key_value_metrics(sheet) -> dict[str, int | None]:
    metrics = {value: None for value in METRIC_KEY_MAP.values()}

    for row in sheet.iter_rows(values_only=True):
        for index in range(len(row) - 1):
            key = normalize_metric_key(row[index])
            metric_name = METRIC_KEY_MAP.get(key)
            metric_value = row[index + 1]
            if metric_name is None or not isinstance(metric_value, (int, float)):
                continue
            metrics[metric_name] = int(metric_value)

    return metrics


def fallback_metrics(workbook) -> dict[str, int | None]:
    merged = {
        "total_cases": 0,
        "pass": 0,
        "fail": 0,
        "notest": 0,
        "block": 0,
        "di": None,
        "serious_issues": None,
    }

    for sheet in workbook.worksheets:
        counts = count_status_words(sheet)
        merged["pass"] += counts["pass"]
        merged["fail"] += counts["fail"]
        merged["notest"] += counts["notest"]
        merged["block"] += counts["block"]

    merged["total_cases"] = (
        merged["pass"] + merged["fail"] + merged["notest"] + merged["block"]
    )
    return merged


def has_complete_overview_metrics(metrics: dict[str, int | None]) -> bool:
    required = ("total_cases", "pass", "fail", "notest", "block")
    return all(metrics.get(key) is not None for key in required)


def infer_sheet_role(sheet_name: str, overview_sheet: str | None) -> str:
    if overview_sheet and sheet_name == overview_sheet:
        return "总表"
    if "专项" in sheet_name:
        return "专项页"
    if "测试" in sheet_name:
        return "功能主表"
    if "WIFI" in sheet_name.upper() or "弱网" in sheet_name:
        return "弱网页"
    if "升级" in sheet_name:
        return "升级页"
    return "分析页"


def summarize_workbook(workbook, overview_sheet: str | None) -> dict:
    sheets: list[dict[str, object]] = []
    for sheet in workbook.worksheets:
        sheets.append(
            {
                "name": sheet.title,
                "role": infer_sheet_role(sheet.title, overview_sheet),
                "rows": sheet.max_row,
                "cols": sheet.max_column,
            }
        )
    return {"sheet_count": len(sheets), "sheets": sheets}


def summarize_sheet_findings(sheet) -> str:
    counts = count_status_words(sheet)
    risk_count = counts["fail"] + counts["notest"] + counts["block"]
    if risk_count == 0:
        return "未识别到高风险状态。"
    return (
        f"发现 {risk_count} 条高风险状态，"
        f"其中 FAIL={counts['fail']}、NT={counts['notest']}、Block={counts['block']}。"
    )


def build_risk_score(counts: dict[str, int]) -> int:
    return counts["fail"] * 20 + counts["block"] * 20 + counts["notest"]


def has_meaningful_risk(counts: dict[str, int]) -> bool:
    return counts["fail"] > 0 or counts["block"] > 0 or counts["notest"] > 0


def collect_module_findings(workbook, overview_sheet: str | None) -> list[dict[str, str]]:
    findings: list[tuple[int, dict[str, str]]] = []

    for sheet in workbook.worksheets:
        if overview_sheet and sheet.title == overview_sheet:
            continue

        counts = count_status_words(sheet)
        if not has_meaningful_risk(counts):
            continue

        findings.append(
            (
                build_risk_score(counts),
                {
                    "sheet": sheet.title,
                    "summary": summarize_sheet_findings(sheet),
                },
            )
        )

    findings.sort(key=lambda item: item[0], reverse=True)
    return [item[1] for item in findings[:5]]


def categorize_risk(sheet_name: str) -> str:
    upper_name = sheet_name.upper()
    if "音频" in sheet_name:
        return "音频"
    if "预览" in sheet_name or "直播" in sheet_name:
        return "预览传输"
    if "回放" in sheet_name or "TF" in upper_name or "存储" in sheet_name:
        return "存储回放"
    if "WIFI" in upper_name or "弱网" in sheet_name:
        return "弱网"
    if "升级" in sheet_name:
        return "升级稳定性"
    return sheet_name


def build_risk_clusters(workbook, overview_sheet: str | None) -> list[str]:
    candidates: list[tuple[int, str]] = []

    for sheet in workbook.worksheets:
        if overview_sheet and sheet.title == overview_sheet:
            continue

        counts = count_status_words(sheet)
        if counts["fail"] == 0 and counts["block"] == 0:
            continue

        label = categorize_risk(sheet.title)
        candidates.append((build_risk_score(counts), label))

    candidates.sort(key=lambda item: item[0], reverse=True)

    clusters: list[str] = []
    for _, label in candidates:
        if label not in clusters:
            clusters.append(label)
        if len(clusters) == 5:
            break

    return clusters


def build_release_judgment(metrics: dict[str, int | None]) -> dict[str, str]:
    threshold = "DI <= 12 且 致命+严重 <= 2"
    di = metrics.get("di")
    serious = metrics.get("serious_issues")

    if di is None or serious is None:
        return {
            "decision": "需人工判断",
            "threshold": threshold,
            "gap": "缺少 DI 或严重问题数，需结合人工复核。",
        }

    if di <= 12 and serious <= 2:
        return {
            "decision": "建议发布",
            "threshold": threshold,
            "gap": "当前指标已满足发布门槛。",
        }

    return {
        "decision": "不建议发布",
        "threshold": threshold,
        "gap": f"DI={di}，严重问题数={serious}，均未满足门槛。",
    }


def extract_basic_info(overview_sheet, input_path: Path) -> dict[str, str]:
    basic_info = {"项目": input_path.stem}
    if overview_sheet is None:
        return basic_info

    mapping = {
        "项目": "项目",
        "设备型号": "设备型号",
        "固件版本": "固件版本",
        "APP版本": "APP版本",
        "APP": "APP版本",
        "测试时间": "测试时间",
        "测试完成时间": "测试时间",
        "测试人员": "测试人员",
    }

    for row in overview_sheet.iter_rows(values_only=True):
        if len(row) < 2:
            continue
        key = normalize_text(row[0])
        if key in mapping and row[1] is not None:
            basic_info[mapping[key]] = normalize_text(row[1])

    return basic_info


def build_final_conclusion(
    judgment: dict[str, str], risk_clusters: list[str], used_fallback: bool
) -> str:
    if judgment["decision"] == "建议发布":
        prefix = "当前版本核心指标满足发布门槛，可进入后续发布确认。"
    elif judgment["decision"] == "不建议发布":
        prefix = "当前版本仍存在明显风险，不建议直接发布。"
    else:
        prefix = "当前版本缺少完整总表指标，需结合人工复核后再做发布判断。"

    if risk_clusters:
        prefix += f" 主要风险集中在：{'、'.join(risk_clusters)}。"
    if used_fallback:
        prefix += " 本次结论包含降级统计结果。"
    return prefix


def extract_report_context(input_path: Path) -> dict:
    workbook = load_workbook(input_path)
    overview_name = detect_overview_sheet(workbook)
    overview_sheet = workbook[overview_name] if overview_name else None

    metrics = extract_key_value_metrics(overview_sheet) if overview_sheet else None
    used_fallback = metrics is None or not has_complete_overview_metrics(metrics)
    overall_metrics = fallback_metrics(workbook) if used_fallback else metrics

    workbook_summary = summarize_workbook(workbook, overview_name)
    risk_clusters = build_risk_clusters(workbook, overview_name)
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
        "risk_clusters": risk_clusters,
        "final_conclusion": build_final_conclusion(
            release_judgment, risk_clusters, used_fallback
        ),
    }


def format_basic_info_lines(basic_info: dict[str, object]) -> str:
    return "\n".join(f"- {key}: {value}" for key, value in basic_info.items())


def format_workbook_summary_lines(workbook_summary: dict[str, object]) -> str:
    lines: list[str] = []
    for item in workbook_summary.get("sheets", []):
        name = item.get("name", "未知工作表")
        role = item.get("role", "未分类")
        rows = item.get("rows")
        cols = item.get("cols")
        if rows is not None and cols is not None:
            lines.append(f"- {name}: {role}，{rows} 行，{cols} 列")
        else:
            lines.append(f"- {name}: {role}")
    return "\n".join(lines)


def format_overall_metrics_lines(overall_metrics: dict[str, object]) -> str:
    labels = [
        ("总用例", overall_metrics.get("total_cases")),
        ("Pass", overall_metrics.get("pass")),
        ("Fail", overall_metrics.get("fail")),
        ("NoTest", overall_metrics.get("notest")),
        ("Block", overall_metrics.get("block")),
        ("DI", overall_metrics.get("di")),
        ("严重问题数", overall_metrics.get("serious_issues")),
    ]
    return "\n".join(f"- {label}: {value}" for label, value in labels)


def format_module_findings_lines(module_findings: list[dict[str, str]]) -> str:
    if not module_findings:
        return "- 未提取到重点模块结论"
    return "\n".join(
        f"- {item['sheet']}: {item['summary']}" for item in module_findings
    )


def format_risk_cluster_lines(risk_clusters: list[str]) -> str:
    if not risk_clusters:
        return "- 未识别到明显风险聚类"
    return "\n".join(f"- {item}" for item in risk_clusters)


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
        final_conclusion=context["final_conclusion"],
    )


def main() -> int:
    configure_stdio()
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    template_path = Path(args.template)

    try:
        context = extract_report_context(input_path)
        markdown = render_report(context, template_path=template_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
        print(f"已生成报告: {output_path}")
        return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
