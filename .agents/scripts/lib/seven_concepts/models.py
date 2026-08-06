# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MatchResult:
    scenario: str
    confidence: int
    concepts: list[str]
    workflow: Optional[str]
    notes: str = ""
    quality_gates: list[str] = field(default_factory=list)
    anti_patterns: list[str] = field(default_factory=list)


