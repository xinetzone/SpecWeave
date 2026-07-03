from __future__ import annotations

from pathlib import Path

from .constants import METRIC_KEY_MAP, STATUS_VALUE_MAP, BASIC_INFO_KEY_MAP
from .utils import normalize_metric_key, normalize_text


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


def extract_basic_info(overview_sheet, input_path: Path) -> dict[str, str]:
    basic_info = {"项目": input_path.stem}
    if overview_sheet is None:
        return basic_info

    for row in overview_sheet.iter_rows(values_only=True):
        if len(row) < 2:
            continue
        key = normalize_text(row[0])
        if key in BASIC_INFO_KEY_MAP and row[1] is not None:
            basic_info[BASIC_INFO_KEY_MAP[key]] = normalize_text(row[1])

    return basic_info


def build_release_judgment(metrics: dict[str, int | None]) -> dict[str, str]:
    from .constants import RELEASE_THRESHOLD

    threshold = RELEASE_THRESHOLD
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
