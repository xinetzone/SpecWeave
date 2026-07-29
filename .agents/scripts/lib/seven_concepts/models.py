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

