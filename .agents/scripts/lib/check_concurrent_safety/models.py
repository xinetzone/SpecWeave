"""并发安全检查数据模型。"""

from dataclasses import dataclass, field
from pathlib import Path

import lib.quality_report as quality_report


@dataclass
class ConcurrencyIssue:
    dimension: str
    code: str
    severity: str
    message: str
    line: int
    snippet: str
    dimension_name: str = ""

    @property
    def name(self) -> str:
        return f"{self.code}: L{self.line}"

    @property
    def passed(self) -> bool:
        return False


@dataclass
class FileReport(quality_report.ResultGroupMixin):
    file_path: Path
    issues: list[ConcurrencyIssue] = field(default_factory=list)
    score: int = 100
    lines_scanned: int = 0

    @property
    def results(self):
        return self.issues

    @property
    def infos(self) -> list[ConcurrencyIssue]:
        return [i for i in self.issues if i.severity == "info"]

    def passed(self, threshold: int = 70) -> bool:
        return self.score >= threshold
