from __future__ import annotations

from .constants import (
    PLATFORM_RISK_PROFILES,
    PLATFORM_SEMANTIC_DEFAULTS,
    RETEST_SUGGESTION_MAP,
    RISK_KEYWORDS,
    RISK_PRIORITY,
    STATUS_VALUE_MAP,
)
from .metrics import build_risk_score, count_status_words
from .utils import normalize_metric_key, normalize_text


def extract_risk_rows(sheet) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    for row in sheet.iter_rows(values_only=True):
        status = None
        text_candidates: list[str] = []

        for cell in row:
            value = normalize_text(cell)
            if not value:
                continue

            status_key = STATUS_VALUE_MAP.get(normalize_metric_key(value))
            if status_key:
                status = status_key
                continue

            text_candidates.append(value)

        if status not in {"fail", "notest", "block"} or not text_candidates:
            continue

        issue_text = max(text_candidates, key=len)
        rows.append(
            {
                "sheet": sheet.title,
                "status": status,
                "text": issue_text,
            }
        )

    return rows


def classify_risk_text(text: str) -> str | None:
    normalized = normalize_text(text)
    if not normalized:
        return None

    for label in RISK_PRIORITY:
        for keyword in RISK_KEYWORDS[label]:
            if keyword in normalized:
                return label
    return None


def build_risk_cluster_details(workbook, overview_sheet: str | None) -> list[dict[str, object]]:
    buckets: dict[str, dict[str, object]] = {}

    for sheet in workbook.worksheets:
        if overview_sheet and sheet.title == overview_sheet:
            continue

        sheet_score = build_risk_score(count_status_words(sheet))
        for item in extract_risk_rows(sheet):
            label = classify_risk_text(item["text"])
            if label is None:
                continue

            bucket = buckets.setdefault(
                label,
                {
                    "label": label,
                    "count": 0,
                    "examples": [],
                    "source_sheets": set(),
                    "_score": 0,
                },
            )
            bucket["count"] += 1
            if item["text"] not in bucket["examples"] and len(bucket["examples"]) < 3:
                bucket["examples"].append(item["text"])
            if item["sheet"] not in bucket["source_sheets"]:
                bucket["_score"] += sheet_score
                bucket["source_sheets"].add(item["sheet"])

    priority_index = {label: index for index, label in enumerate(RISK_PRIORITY)}
    ordered = sorted(
        buckets.values(),
        key=lambda item: (
            -int(item["_score"]),
            -int(item["count"]),
            priority_index.get(str(item["label"]), len(RISK_PRIORITY)),
        ),
    )

    details: list[dict[str, object]] = []
    for item in ordered:
        details.append(
            {
                "label": item["label"],
                "count": item["count"],
                "examples": item["examples"],
                "source_sheets": sorted(item["source_sheets"]),
            }
        )

    return details


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
    details = build_risk_cluster_details(workbook, overview_sheet)
    if details:
        return [str(item["label"]) for item in details[:5]]

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


def build_retest_suggestions(risk_clusters: list[str]) -> list[str]:
    result: list[str] = []
    for label in risk_clusters[:5]:
        result.append(RETEST_SUGGESTION_MAP.get(label, f"复测模块：{label}（优先复核 FAIL/Block 用例）"))
    return result


def get_platform_semantic_profile(risk_label: str) -> dict[str, object] | None:
    profile = PLATFORM_RISK_PROFILES.get(risk_label)
    if profile is None:
        return None
    return {**PLATFORM_SEMANTIC_DEFAULTS, **profile}


def build_platform_semantic_mapping(risk_clusters: list[str]) -> list[dict[str, object]]:
    mappings: list[dict[str, object]] = []
    for label in risk_clusters[:5]:
        semantic = get_platform_semantic_profile(label)
        if semantic is None:
            continue
        mappings.append({"risk_label": label, **semantic})
    return mappings
