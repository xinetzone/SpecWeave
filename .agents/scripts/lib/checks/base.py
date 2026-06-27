"""检查框架共享定义。"""

from dataclasses import dataclass, field


@dataclass
class CheckResult:
    """单个检查项的结果。"""

    name: str
    passed: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    fixed_count: int = 0

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        return len(self.warnings)
