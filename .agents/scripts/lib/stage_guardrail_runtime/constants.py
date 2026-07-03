from lib.stage_guardrails import OperationType

OPERATION_MAP: dict[str, OperationType] = {
    op.value: op for op in OperationType
}

VALID_ROLES = {'orchestrator', 'architect', 'developer', 'tester', 'reviewer'}

__all__ = ['OPERATION_MAP', 'VALID_ROLES']
