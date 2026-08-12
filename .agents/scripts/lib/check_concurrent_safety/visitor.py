"""并发安全AST访问器 - 重构后为协调器的向后兼容别名。

本文件已重构为coordinator.py的向后兼容包装，所有检查逻辑已拆分到独立检查器类。
"""


from ..python310_version_check import enforce_python310

enforce_python310()

from .coordinator import ConcurrentSafetyCoordinator, ConcurrentSafetyVisitor

__all__ = ["ConcurrentSafetyVisitor", "ConcurrentSafetyCoordinator"]
