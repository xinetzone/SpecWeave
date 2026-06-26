"""Spec 检查数据模型。

定义规格文档检查过程中使用的数据结构。
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Issue:
    """检查问题记录"""
    type: str
    name: str
    message: str
    severity: str = "error"


@dataclass
class SpecCheckResult:
    """单个 Spec 文件的检查结果"""
    spec_path: str
    score: int = 0
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "spec_dir": self.spec_path,
            "score": self.score,
            "errors": self.errors,
            "warnings": self.warnings,
        }
