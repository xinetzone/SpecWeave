"""trae_edge_case_handler 汇总报告模块。

边界情况汇总报告数据结构和格式化输出。
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .models import BoundaryDecision, BoundaryLevel


@dataclass
class BoundarySummary:
    """边界情况汇总报告（规范文档第206行）。"""

    total: int = 0
    fatal_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    entries: list[BoundaryDecision] = field(default_factory=list)

    def add(self, decision: BoundaryDecision) -> None:
        """添加一条边界决策到汇总。"""
        self.total += 1
        if decision.level == BoundaryLevel.FATAL:
            self.fatal_count += 1
        elif decision.level == BoundaryLevel.WARNING:
            self.warning_count += 1
        else:
            self.info_count += 1
        self.entries.append(decision)

    def report(self) -> str:
        """生成汇总报告文本。"""
        lines = [
            f"边界情况汇总: 共 {self.total} 条",
            f"  致命(fatal): {self.fatal_count}",
            f"  警告(warning): {self.warning_count}",
            f"  提示(info): {self.info_count}",
        ]
        for entry in self.entries:
            lines.append(
                f"  [{entry.level.value}] {entry.boundary_type}: {entry.rationale}"
            )
        return "\n".join(lines)
