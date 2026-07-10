from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import lib.quality_report as quality_report


@dataclass
class CheckResult:
    name: str
    passed: bool
    severity: str
    message: str
    line: int | None = None


@dataclass
class SkillReport(quality_report.ResultGroupMixin):
    skill_path: Path
    skill_name: str
    results: list[CheckResult] = field(default_factory=list)
    score: int = 0
