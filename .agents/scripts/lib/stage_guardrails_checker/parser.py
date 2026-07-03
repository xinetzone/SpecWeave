import json
from typing import Optional

from .constants import LOG_LINE_RE, SG_EVENTS, PDR_EVENTS, SG_LEVELS, STAGE_ORDER
from .models import LogEntry, AnalysisIssue


def parse_ctx(ctx_str: Optional[str]) -> dict:
    if not ctx_str or not ctx_str.strip():
        return {}
    ctx_str = ctx_str.strip()
    try:
        return json.loads(ctx_str)
    except json.JSONDecodeError:
        return {"_raw": ctx_str, "_parse_error": True}


def parse_log_file(content: str) -> tuple[list[LogEntry], list[AnalysisIssue]]:
    entries = []
    issues = []
    for line_num, line in enumerate(content.splitlines(), 1):
        line = line.strip()
        if '[SG-LOG]' not in line and '[PDR-LOG]' not in line:
            continue
        m = LOG_LINE_RE.search(line)
        if not m:
            issues.append(AnalysisIssue(
                severity='WARN',
                code='MALFORMED_LOG',
                message=f'日志格式不规范，无法解析',
                line_num=line_num,
            ))
            continue
        prefix, level, event, stage, role, session, msg, ctx_str = m.groups()
        ctx = parse_ctx(ctx_str)

        entry = LogEntry(
            prefix=prefix,
            level=level.strip(),
            event=event.strip(),
            stage=stage.strip(),
            role=role.strip(),
            session=session.strip(),
            msg=msg.strip(),
            ctx=ctx,
            line_num=line_num,
        )

        if entry.is_sg and entry.event not in SG_EVENTS:
            issues.append(AnalysisIssue(
                severity='WARN',
                code='UNKNOWN_EVENT',
                message=f'未知的SG事件类型: {entry.event}',
                line_num=line_num,
                entry=entry,
            ))
        if entry.is_pdr and entry.event not in PDR_EVENTS:
            issues.append(AnalysisIssue(
                severity='WARN',
                code='UNKNOWN_EVENT',
                message=f'未知的PDR事件类型: {entry.event}',
                line_num=line_num,
                entry=entry,
            ))
        if entry.level not in SG_LEVELS:
            issues.append(AnalysisIssue(
                severity='WARN',
                code='UNKNOWN_LEVEL',
                message=f'未知的日志级别: {entry.level}',
                line_num=line_num,
                entry=entry,
            ))
        if entry.stage not in STAGE_ORDER:
            issues.append(AnalysisIssue(
                severity='WARN',
                code='UNKNOWN_STAGE',
                message=f'未知的阶段ID: {entry.stage}',
                line_num=line_num,
                entry=entry,
            ))

        entries.append(entry)

    return entries, issues