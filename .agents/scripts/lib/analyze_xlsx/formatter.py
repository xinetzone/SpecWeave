from __future__ import annotations


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


def format_platform_mapping_lines(platform_mapping: list[dict[str, object]]) -> str:
    if not platform_mapping:
        return "- 未建立平台语义映射"

    lines: list[str] = []
    for item in platform_mapping:
        traits = " / ".join(str(value) for value in item["integration_traits"])
        surfaces = " / ".join(str(value) for value in item["observation_surfaces"])
        lines.append(
            "- "
            f"{item['risk_label']}: "
            f"映射到 `{item['ha_domain']}` 域的 `{item['entity_scope']}` 观察面；"
            f"集成特征={traits}；"
            f"重点字段={surfaces}；"
            f"{item['diagnostic_focus']}"
        )
    return "\n".join(lines)


def format_platform_impact_lines(platform_mapping: list[dict[str, object]]) -> str:
    if not platform_mapping:
        return "- 未识别平台影响面"

    lines: list[str] = []
    for item in platform_mapping[:3]:
        traits = " / ".join(str(value) for value in item["integration_traits"])
        surfaces = " / ".join(str(value) for value in item["observation_surfaces"])
        lines.append(
            "- "
            f"{item['risk_label']}: "
            f"`{item['ha_domain']}`.{item['entity_scope']} "
            f"(特征: {traits}; 观察面: {surfaces})"
        )
    return "\n".join(lines)


def format_core_metrics_lines(overall_metrics: dict[str, object]) -> str:
    return format_overall_metrics_lines(overall_metrics)


def format_top_risks_lines(risk_clusters: list[str]) -> str:
    if not risk_clusters:
        return "- 未识别到明显风险"
    return "\n".join(f"- {item}" for item in risk_clusters[:5])


def format_blockers_lines(context: dict) -> str:
    decision = context["release_judgment"]["decision"]
    if decision == "建议发布":
        return "- 无明显阻塞项"

    lines = [f"- {context['release_judgment']['gap']}"]
    for item in context.get("module_findings", [])[:3]:
        lines.append(f"- {item['sheet']}: {item['summary']}")
    return "\n".join(lines)
