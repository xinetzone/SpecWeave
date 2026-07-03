from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from lib.quality_report import ResultGroupMixin


@dataclass
class CheckResult:
    name: str
    passed: bool
    severity: str
    message: str
    line: Optional[int] = None


@dataclass
class PatternReport(ResultGroupMixin):
    pattern_path: Path
    pattern_id: str
    pattern_title: str
    results: list[CheckResult] = field(default_factory=list)
    score: int = 0
