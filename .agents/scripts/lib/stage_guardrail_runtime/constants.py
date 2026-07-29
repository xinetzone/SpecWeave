# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

from lib.stage_guardrails import OperationType

OPERATION_MAP: dict[str, OperationType] = {
    op.value: op for op in OperationType
}

VALID_ROLES = {'orchestrator', 'architect', 'developer', 'tester', 'reviewer'}

__all__ = ['OPERATION_MAP', 'VALID_ROLES']

