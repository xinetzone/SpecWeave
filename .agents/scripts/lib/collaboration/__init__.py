"""多智能体协作模块。

包含冲突解决、任务交接、消息传递等协作协议的实现。
"""

from .conflict_resolution import (
    ConflictType,
    ConflictReport,
    ArbitrationResult,
    ResolutionStatus,
    ConflictResolver,
)

__all__ = [
    "ConflictType",
    "ConflictReport",
    "ArbitrationResult",
    "ResolutionStatus",
    "ConflictResolver",
]
