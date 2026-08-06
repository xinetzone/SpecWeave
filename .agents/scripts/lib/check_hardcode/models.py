# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

from dataclasses import dataclass, field
from pathlib import Path

import lib.quality_report as quality_report


@dataclass
class HardcodeIssue:
    category: str
    severity: str
    message: str
    line: int
    snippet: str

    @property
    def name(self) -> str:
        return f"{self.category}: L{self.line}"

    @property
    def passed(self) -> bool:
        return False


@dataclass
class FileReport(quality_report.ResultGroupMixin):
    file_path: Path
    issues: list[HardcodeIssue] = field(default_factory=list)
    score: int = 100
    lines_scanned: int = 0

    @property
    def results(self):
        return self.issues

