"""模式成熟度工具 - 数据模型定义。"""


# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PatternInfo:
    """模式信息数据类。"""
    id: str
    file: str
    maturity: str = ''
    domain: str = ''
    validation_count: int = 0
    reuse_count: int = 0
    issues: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class UpgradeStats:
    """升级统计数据类。"""
    total: int = 0
    validation_total: int = 0
    avg_validation: float = 0.0
    maturity_counts: dict[str, int] = field(default_factory=dict)
    upgrades: list[dict[str, Any]] = field(default_factory=list)
    anomalies: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class Discrepancy:
    """统计差异数据类。"""
    directory: str
    field: str
    grep: int
    readme: int
    diff: int


@dataclass
class IndexCheckResult:
    """索引检查结果数据类。"""
    directory: str
    declared: int
    actual: int
    consistent: bool

