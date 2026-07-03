"""sg-dashboard 数据模型。

定义日志条目、会话统计、聚合统计三个核心dataclass。
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field


@dataclass
class LogEntry:
    """单条结构化日志条目。"""
    prefix: str
    level: str
    event: str
    stage: str
    role: str
    session: str
    msg: str
    ctx: dict
    source_file: str
    line_num: int
    timestamp: str = ''


@dataclass
class SessionStats:
    """单个会话的统计信息。"""
    session_id: str
    source_file: str
    stages_entered: list[str] = field(default_factory=list)
    stages_exited: list[str] = field(default_factory=list)
    operations_checked: int = 0
    operations_passed: int = 0
    operations_intercepted: int = 0
    bypass_detected: int = 0
    errors: int = 0
    jumps_requested: int = 0
    jumps_approved: int = 0
    jumps_rejected: int = 0
    jump_types: Counter = field(default_factory=Counter)
    intercept_reasons: Counter = field(default_factory=Counter)
    roles_seen: set[str] = field(default_factory=set)
    first_event_time: str = ''
    last_event_time: str = ''
    events: list[LogEntry] = field(default_factory=list)
    completed: bool = False


@dataclass
class AggregateStats:
    """全局聚合统计结果。"""
    total_sessions: int = 0
    total_entries: int = 0
    total_sg_entries: int = 0
    total_pdr_entries: int = 0
    total_operations_checked: int = 0
    total_passed: int = 0
    total_intercepted: int = 0
    total_bypasses: int = 0
    total_errors: int = 0
    total_jumps_requested: int = 0
    total_jumps_approved: int = 0
    total_jumps_rejected: int = 0
    sessions_completed: int = 0
    event_counts: Counter = field(default_factory=Counter)
    level_counts: Counter = field(default_factory=Counter)
    stage_intercept_counts: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    stage_pass_counts: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    stage_entry_counts: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    role_intercept_counts: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    top_intercept_reasons: list[tuple[str, int]] = field(default_factory=list)
    sessions: list[SessionStats] = field(default_factory=list)

    @property
    def interception_rate(self) -> float:
        if self.total_operations_checked == 0:
            return 0.0
        return self.total_intercepted / self.total_operations_checked * 100

    @property
    def approval_rate(self) -> float:
        total_decided = self.total_jumps_approved + self.total_jumps_rejected
        if total_decided == 0:
            return 0.0
        return self.total_jumps_approved / total_decided * 100

    @property
    def completion_rate(self) -> float:
        if self.total_sessions == 0:
            return 0.0
        return self.sessions_completed / self.total_sessions * 100
