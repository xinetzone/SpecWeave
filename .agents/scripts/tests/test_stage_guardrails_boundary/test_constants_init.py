from lib.stage_guardrails.boundary import (
    BoundaryChecker,
    OperationType,
    STAGE_EXIT_CRITERIA,
    OPERATION_CATEGORIES,
    _STAGE_PERMISSIONS,
)
from lib.stage_guardrails.state import STAGE_ORDER, STAGE_ROLES


class TestConstants:
    """常量完整性测试。"""

    def test_all_stages_have_permissions(self):
        for stage in STAGE_ORDER:
            assert stage in _STAGE_PERMISSIONS, f'{stage} 缺少权限定义'
            perm = _STAGE_PERMISSIONS[stage]
            assert 'allowed' in perm, f'{stage} 缺少allowed集合'
            assert 'denied' in perm, f'{stage} 缺少denied集合'

    def test_all_stages_have_exit_criteria(self):
        for stage in STAGE_ORDER:
            assert stage in STAGE_EXIT_CRITERIA, f'{stage} 缺少退出标准'

    def test_allowed_denied_disjoint(self):
        for stage, perm in _STAGE_PERMISSIONS.items():
            overlap = perm['allowed'] & perm['denied']
            assert not overlap, f'{stage} allowed和denied存在交集: {overlap}'

    def test_universal_read_ops_in_all_allowed(self):
        read_ops = OPERATION_CATEGORIES['read_only']
        for stage, perm in _STAGE_PERMISSIONS.items():
            for op in read_ops:
                assert op in perm['allowed'], f'{stage} 缺少只读操作 {op.value}'

    def test_stage_roles_match_permissions(self):
        for stage, roles in STAGE_ROLES.items():
            assert stage in _STAGE_PERMISSIONS


class TestBoundaryCheckerInit:
    """初始化测试。"""

    def test_creation(self):
        checker = BoundaryChecker()
        assert checker is not None

    def test_get_allowed_operations_s1(self):
        checker = BoundaryChecker()
        allowed = checker.get_allowed_operations('S1')
        assert OperationType.CLARIFY_REQUIREMENT in allowed
        assert OperationType.CREATE_TASK_LIST in allowed
        assert OperationType.IDENTIFY_RISK in allowed

    def test_get_denied_operations_s1(self):
        checker = BoundaryChecker()
        denied = checker.get_denied_operations('S1')
        assert OperationType.WRITE_CODE in denied
        assert OperationType.CHOOSE_TECH_STACK in denied

    def test_is_read_only(self):
        checker = BoundaryChecker()
        assert checker.is_read_only_operation(OperationType.READ_DOCS)
        assert checker.is_read_only_operation(OperationType.SEARCH_CODE)
        assert not checker.is_read_only_operation(OperationType.WRITE_CODE)
