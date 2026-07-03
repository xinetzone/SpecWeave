import json
from typing import Optional

from .constants import GOVERNANCE_LAYERS, GOVERNANCE_KEYWORDS
from .models import LogEntry, AnalysisIssue


def identify_governance_layer(msg: str, ctx: dict) -> Optional[str]:
    text = msg.lower()
    ctx_str = json.dumps(ctx, ensure_ascii=False).lower() if ctx else ''
    combined = text + ' ' + ctx_str

    for layer, keywords in GOVERNANCE_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in combined:
                return layer
    return None


def check_governance_layers(
    entry: LogEntry,
    governance_layers_delivered: set,
    governance_layer_first_seen: dict
) -> list[AnalysisIssue]:
    issues = []
    gov_layer = identify_governance_layer(entry.msg, entry.ctx)
    if not gov_layer:
        return issues

    if gov_layer not in governance_layer_first_seen:
        governance_layer_first_seen[gov_layer] = entry
        layer_order = GOVERNANCE_LAYERS[gov_layer]['order']
        required_layers = [l for l, info in GOVERNANCE_LAYERS.items() if info['order'] < layer_order]
        missing_prereqs = [l for l in required_layers if l not in governance_layers_delivered]
        if missing_prereqs:
            missing_names = [f"{l}({GOVERNANCE_LAYERS[l]['name']})" for l in missing_prereqs]
            issues.append(AnalysisIssue(
                severity='WARN',
                code='GOVERNANCE_LAYER_SKIP',
                message=f'治理基建跳层风险: 检测到{gov_layer}({GOVERNANCE_LAYERS[gov_layer]["name"]})，但前置层{",".join(missing_names)}尚未交付，可能违反四层递进模型',
                entry=entry,
            ))
    if entry.event in ('STAGE_EXIT', 'DOC_READ', 'BOUNDARY_PASS'):
        governance_layers_delivered.add(gov_layer)

    return issues