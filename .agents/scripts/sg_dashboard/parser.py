"""sg-dashboard 日志解析模块。

提供ctx JSON解析、日志文件解析、日志文件收集功能。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .constants import LOG_LINE_RE
from .models import LogEntry


def parse_ctx(ctx_str: Optional[str]) -> dict:
    """解析ctx字段的JSON字符串，失败时返回raw文本。"""
    if not ctx_str or not ctx_str.strip():
        return {}
    try:
        return json.loads(ctx_str.strip())
    except json.JSONDecodeError:
        return {'_raw': ctx_str.strip()}


def parse_log_file(file_path: Path) -> list[LogEntry]:
    """解析单个日志文件，返回LogEntry列表。"""
    entries = []
    try:
        content = file_path.read_text(encoding='utf-8')
    except (UnicodeDecodeError, OSError):
        return entries

    for line_num, line in enumerate(content.splitlines(), 1):
        line = line.strip()
        if not line or ('[SG-LOG]' not in line and '[PDR-LOG]' not in line):
            continue
        m = LOG_LINE_RE.search(line)
        if not m:
            continue
        prefix, level, event, stage, role, session, msg, ctx_str = m.groups()
        entries.append(LogEntry(
            prefix=prefix,
            level=level.strip(),
            event=event.strip(),
            stage=stage.strip(),
            role=role.strip(),
            session=session.strip(),
            msg=msg.strip(),
            ctx=parse_ctx(ctx_str),
            source_file=str(file_path.name),
            line_num=line_num,
        ))
    return entries


def collect_log_files(log_dir: Path) -> list[Path]:
    """收集日志目录下所有.log和.txt文件。"""
    if not log_dir.exists():
        return []
    files = []
    for ext in ('*.log', '*.txt'):
        files.extend(log_dir.glob(ext))
    return sorted(files)
