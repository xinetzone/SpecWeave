# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LogEntry:
    prefix: str
    level: str
    event: str
    stage: str
    role: str
    session: str
    msg: str
    ctx: dict = field(default_factory=dict)
    line_num: int = 0

    @property
    def is_sg(self) -> bool:
        return self.prefix == 'SG-LOG'

    @property
    def is_pdr(self) -> bool:
        return self.prefix == 'PDR-LOG'


@dataclass
class AnalysisIssue:
    severity: str
    code: str
    message: str
    line_num: int = 0
    entry: LogEntry | None = None
