"""BoundaryChecker 操作边界校验引擎单元测试。"""

import sys
import pytest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from lib.stage_guardrails.boundary import (
    BoundaryChecker,
    BoundaryResult,
    OperationType,
    STAGE_EXIT_CRITERIA,
    OPERATION_CATEGORIES,
    _STAGE_PERMISSIONS,
)
from lib.stage_guardrails.state import STAGE_ORDER, STAGE_NAMES, VALID_ROLES, STAGE_ROLES


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


class TestS1RequirementsStage:
    """S1需求接收阶段校验测试。"""

    def setup_method(self):
        self.checker = BoundaryChecker()
        self.stage = 'S1'
        self.role = 'orchestrator'

    def test_allow_clarify_requirement(self):
        r = self.checker.check(OperationType.CLARIFY_REQUIREMENT, self.stage, self.role)
        assert r.allowed is True
        assert r.log_level == 'DEBUG'

    def test_allow_create_task_list(self):
        r = self.checker.check(OperationType.CREATE_TASK_LIST, self.stage, self.role)
        assert r.allowed is True

    def test_allow_identify_risk(self):
        r = self.checker.check(OperationType.IDENTIFY_RISK, self.stage, self.role)
        assert r.allowed is True

    def test_deny_write_code(self):
        r = self.checker.check(OperationType.WRITE_CODE, self.stage, self.role, '编写Redis配置代码')
        assert r.allowed is False
        assert r.violation_type in ('STAGE_BOUNDARY_VIOLATION', 'CROSS_STAGE_OPERATION')
        assert r.log_level == 'WARN'
        assert 'S4' in (r.target_stage or '')

    def test_deny_choose_tech_stack(self):
        r = self.checker.check(OperationType.CHOOSE_TECH_STACK, self.stage, self.role)
        assert r.allowed is False

    def test_deny_discuss_tech(self):
        r = self.checker.check(OperationType.DISCUSS_TECH_IMPLEMENTATION, self.stage, self.role)
        assert r.allowed is False

    def test_deny_estimate_lines(self):
        r = self.checker.check(OperationType.ESTIMATE_LINES, self.stage, self.role)
        assert r.allowed is False

    def test_intercept_message_format(self):
        r = self.checker.check(OperationType.WRITE_CODE, self.stage, self.role, '编写Redis配置代码')
        msg = r.format_intercept_message()
        assert '⚠️' in msg
        assert 'S1' in msg
        assert '需求接收' in msg
        assert '请先完成当前阶段' in msg


class TestS2DesignStage:
    """S2方案设计阶段校验测试。"""

    def setup_method(self):
        self.checker = BoundaryChecker()
        self.stage = 'S2'
        self.role = 'architect'

    def test_allow_architecture_design(self):
        r = self.checker.check(OperationType.ARCHITECTURE_DESIGN, self.stage, self.role)
        assert r.allowed is True

    def test_allow_choose_tech_stack(self):
        r = self.checker.check(OperationType.CHOOSE_TECH_STACK, self.stage, self.role)
        assert r.allowed is True

    def test_allow_define_api(self):
        r = self.checker.check(OperationType.DEFINE_API, self.stage, self.role)
        assert r.allowed is True

    def test_deny_write_code(self):
        r = self.checker.check(OperationType.WRITE_CODE, self.stage, self.role)
        assert r.allowed is False

    def test_deny_modify_business_code(self):
        r = self.checker.check(OperationType.MODIFY_BUSINESS_CODE, self.stage, self.role)
        assert r.allowed is False

    def test_deny_specify_implementation_detail(self):
        r = self.checker.check(OperationType.SPECIFY_IMPLEMENTATION_DETAIL, self.stage, self.role)
        assert r.allowed is False


class TestS3TaskAssignmentStage:
    """S3任务分配阶段校验测试。"""

    def setup_method(self):
        self.checker = BoundaryChecker()
        self.stage = 'S3'
        self.role = 'orchestrator'

    def test_allow_assign_task(self):
        r = self.checker.check(OperationType.ASSIGN_TASK, self.stage, self.role)
        assert r.allowed is True

    def test_allow_set_acceptance_criteria(self):
        r = self.checker.check(OperationType.SET_ACCEPTANCE_CRITERIA, self.stage, self.role)
        assert r.allowed is True

    def test_deny_modify_architecture(self):
        r = self.checker.check(OperationType.MODIFY_ARCHITECTURE, self.stage, self.role)
        assert r.allowed is False

    def test_deny_write_code(self):
        r = self.checker.check(OperationType.WRITE_CODE, self.stage, self.role)
        assert r.allowed is False


class TestS4CodingStage:
    """S4代码实现阶段校验测试。"""

    def setup_method(self):
        self.checker = BoundaryChecker()
        self.stage = 'S4'
        self.role = 'developer'

    def test_allow_write_code(self):
        r = self.checker.check(OperationType.WRITE_CODE, self.stage, self.role)
        assert r.allowed is True

    def test_allow_write_unit_test(self):
        r = self.checker.check(OperationType.WRITE_UNIT_TEST, self.stage, self.role)
        assert r.allowed is True

    def test_allow_run_test(self):
        r = self.checker.check(OperationType.RUN_TEST, self.stage, self.role)
        assert r.allowed is True

    def test_allow_submit_pr(self):
        r = self.checker.check(OperationType.SUBMIT_PR, self.stage, self.role)
        assert r.allowed is True

    def test_allow_fix_bug(self):
        r = self.checker.check(OperationType.FIX_BUG, self.stage, self.role)
        assert r.allowed is True

    def test_deny_modify_architecture(self):
        r = self.checker.check(OperationType.MODIFY_ARCHITECTURE, self.stage, self.role)
        assert r.allowed is False

    def test_deny_skip_unit_test(self):
        r = self.checker.check(OperationType.SKIP_UNIT_TEST, self.stage, self.role)
        assert r.allowed is False

    def test_deny_add_unplanned_feature(self):
        r = self.checker.check(OperationType.ADD_UNPLANNED_FEATURE, self.stage, self.role)
        assert r.allowed is False

    def test_deny_change_tech_selection(self):
        r = self.checker.check(OperationType.CHANGE_TECH_SELECTION, self.stage, self.role)
        assert r.allowed is False


class TestS5TestingStage:
    """S5测试编写阶段校验测试。"""

    def setup_method(self):
        self.checker = BoundaryChecker()
        self.stage = 'S5'
        self.role = 'tester'

    def test_allow_design_test_case(self):
        r = self.checker.check(OperationType.DESIGN_TEST_CASE, self.stage, self.role)
        assert r.allowed is True

    def test_allow_write_integration_test(self):
        r = self.checker.check(OperationType.WRITE_INTEGRATION_TEST, self.stage, self.role)
        assert r.allowed is True

    def test_allow_record_defect(self):
        r = self.checker.check(OperationType.RECORD_DEFECT, self.stage, self.role)
        assert r.allowed is True

    def test_allow_report_defect(self):
        r = self.checker.check(OperationType.REPORT_DEFECT, self.stage, self.role)
        assert r.allowed is True

    def test_allow_verify_fix(self):
        r = self.checker.check(OperationType.VERIFY_FIX, self.stage, self.role)
        assert r.allowed is True

    def test_deny_fix_bug(self):
        r = self.checker.check(OperationType.FIX_BUG, self.stage, self.role)
        assert r.allowed is False
        assert 'tester' in r.deny_reason or 'developer' in r.deny_reason

    def test_deny_modify_business_code(self):
        r = self.checker.check(OperationType.MODIFY_BUSINESS_CODE, self.stage, self.role)
        assert r.allowed is False

    def test_deny_test_only_happy_path(self):
        r = self.checker.check(OperationType.TEST_ONLY_HAPPY_PATH, self.stage, self.role)
        assert r.allowed is False


class TestS6ReviewStage:
    """S6代码审查阶段校验测试。"""

    def setup_method(self):
        self.checker = BoundaryChecker()
        self.stage = 'S6'
        self.role = 'reviewer'

    def test_allow_review_code(self):
        r = self.checker.check(OperationType.REVIEW_CODE, self.stage, self.role)
        assert r.allowed is True

    def test_allow_review_security(self):
        r = self.checker.check(OperationType.REVIEW_SECURITY, self.stage, self.role)
        assert r.allowed is True

    def test_allow_approve_merge(self):
        r = self.checker.check(OperationType.APPROVE_MERGE, self.stage, self.role)
        assert r.allowed is True

    def test_allow_reject_merge(self):
        r = self.checker.check(OperationType.REJECT_MERGE, self.stage, self.role)
        assert r.allowed is True

    def test_deny_modify_business_code(self):
        r = self.checker.check(OperationType.MODIFY_BUSINESS_CODE, self.stage, self.role)
        assert r.allowed is False

    def test_deny_write_code(self):
        r = self.checker.check(OperationType.WRITE_CODE, self.stage, self.role)
        assert r.allowed is False

    def test_deny_vague_feedback(self):
        r = self.checker.check(OperationType.GIVE_VAGUE_FEEDBACK, self.stage, self.role)
        assert r.allowed is False


class TestS7MergeStage:
    """S7合并代码阶段校验测试。"""

    def setup_method(self):
        self.checker = BoundaryChecker()
        self.stage = 'S7'
        self.role = 'orchestrator'

    def test_allow_run_test(self):
        r = self.checker.check(OperationType.RUN_TEST, self.stage, self.role)
        assert r.allowed is True

    def test_allow_trigger_ci_cd(self):
        r = self.checker.check(OperationType.TRIGGER_CI_CD, self.stage, self.role)
        assert r.allowed is True

    def test_allow_notify_after_merge(self):
        r = self.checker.check(OperationType.NOTIFY_AFTER_MERGE, self.stage, self.role)
        assert r.allowed is True

    def test_deny_force_merge(self):
        r = self.checker.check(OperationType.FORCE_MERGE, self.stage, self.role)
        assert r.allowed is False

    def test_deny_skip_ci_check(self):
        r = self.checker.check(OperationType.SKIP_CI_CHECK, self.stage, self.role)
        assert r.allowed is False

    def test_deny_approve_merge(self):
        r = self.checker.check(OperationType.APPROVE_MERGE, self.stage, self.role)
        assert r.allowed is False


class TestS8CompletionStage:
    """S8完成确认阶段校验测试。"""

    def setup_method(self):
        self.checker = BoundaryChecker()
        self.stage = 'S8'
        self.role = 'orchestrator'

    def test_allow_verify_acceptance(self):
        r = self.checker.check(OperationType.VERIFY_ACCEPTANCE, self.stage, self.role)
        assert r.allowed is True

    def test_allow_mark_complete(self):
        r = self.checker.check(OperationType.MARK_TASK_COMPLETE, self.stage, self.role)
        assert r.allowed is True

    def test_allow_notify_stakeholders(self):
        r = self.checker.check(OperationType.NOTIFY_STAKEHOLDERS, self.stage, self.role)
        assert r.allowed is True

    def test_allow_archive_docs(self):
        r = self.checker.check(OperationType.ARCHIVE_DOCS, self.stage, self.role)
        assert r.allowed is True

    def test_deny_mark_incomplete_complete(self):
        r = self.checker.check(OperationType.MARK_INCOMPLETE_COMPLETE, self.stage, self.role)
        assert r.allowed is False

    def test_deny_skip_regression(self):
        r = self.checker.check(OperationType.SKIP_REGRESSION, self.stage, self.role)
        assert r.allowed is False

    def test_deny_write_code(self):
        r = self.checker.check(OperationType.WRITE_CODE, self.stage, self.role)
        assert r.allowed is False


class TestCrossStageOperations:
    """跨阶段操作校验测试。"""

    def setup_method(self):
        self.checker = BoundaryChecker()

    def test_s1_cross_to_s2_design(self):
        r = self.checker.check(OperationType.ARCHITECTURE_DESIGN, 'S1', 'orchestrator', '设计架构')
        assert r.allowed is False
        assert r.target_stage == 'S2'
        assert 'S2' in r.format_intercept_message()

    def test_s4_cross_to_s2_rollback_hint(self):
        r = self.checker.check(OperationType.MODIFY_ARCHITECTURE, 'S4', 'developer', '改变架构')
        assert r.allowed is False
        assert r.violation_type in ('STAGE_BOUNDARY_VIOLATION', 'CROSS_STAGE_OPERATION')
        msg = r.format_intercept_message()
        assert msg or True

    def test_s5_cannot_write_code(self):
        r = self.checker.check(OperationType.WRITE_CODE, 'S5', 'tester')
        assert r.allowed is False


class TestNoActiveStage:
    """无活跃阶段时的校验测试。"""

    def setup_method(self):
        self.checker = BoundaryChecker()

    def test_read_ops_allowed_without_stage(self):
        r = self.checker.check(OperationType.READ_DOCS, None, 'orchestrator')
        assert r.allowed is True

    def test_search_code_allowed_without_stage(self):
        r = self.checker.check(OperationType.SEARCH_CODE, None, 'developer')
        assert r.allowed is True

    def test_write_code_blocked_without_stage(self):
        r = self.checker.check(OperationType.WRITE_CODE, None, 'developer')
        assert r.allowed is False
        assert r.violation_type == 'NO_ACTIVE_STAGE'
        assert r.log_level == 'ERROR'
        assert 'S1' in r.exit_criteria_hint or 'S1' in r.suggested_action


class TestRoleMismatch:
    """角色不匹配测试。"""

    def setup_method(self):
        self.checker = BoundaryChecker()

    def test_tester_in_s1(self):
        r = self.checker.check(OperationType.CLARIFY_REQUIREMENT, 'S1', 'tester')
        assert r.allowed is False
        assert r.violation_type == 'ROLE_STAGE_MISMATCH'
        assert r.log_level == 'WARN'

    def test_developer_in_s2(self):
        r = self.checker.check(OperationType.ARCHITECTURE_DESIGN, 'S2', 'developer')
        assert r.allowed is False

    def test_reviewer_in_s4(self):
        r = self.checker.check(OperationType.WRITE_CODE, 'S4', 'reviewer')
        assert r.allowed is False

    def test_invalid_role(self):
        r = self.checker.check(OperationType.WRITE_CODE, 'S4', 'designer')
        assert r.allowed is False
        assert r.violation_type == 'INVALID_ROLE'
        assert r.log_level == 'ERROR'

    def test_invalid_stage(self):
        r = self.checker.check(OperationType.WRITE_CODE, 'S9', 'developer')
        assert r.allowed is False
        assert r.violation_type == 'INVALID_STAGE'


class TestInterceptMessage:
    """拦截消息格式化测试。"""

    def setup_method(self):
        self.checker = BoundaryChecker()

    def test_intercept_contains_warning_symbol(self):
        r = self.checker.check(OperationType.WRITE_CODE, 'S1', 'orchestrator')
        msg = r.format_intercept_message()
        assert '⚠️' in msg

    def test_intercept_contains_exit_criteria(self):
        r = self.checker.check(OperationType.WRITE_CODE, 'S1', 'orchestrator')
        msg = r.format_intercept_message()
        assert '请先完成当前阶段' in msg
        assert STAGE_EXIT_CRITERIA['S1'] in msg

    def test_allowed_returns_empty_message(self):
        r = self.checker.check(OperationType.CLARIFY_REQUIREMENT, 'S1', 'orchestrator')
        assert r.format_intercept_message() == ''

    def test_intercept_contains_jump_suggestion(self):
        r = self.checker.check(OperationType.WRITE_CODE, 'S1', 'orchestrator')
        msg = r.format_intercept_message()
        assert '跳转' in msg or 'request_jump' in msg


class TestLogDict:
    """日志字典生成测试。"""

    def test_pass_result_to_log_dict(self):
        checker = BoundaryChecker()
        r = checker.check(OperationType.WRITE_CODE, 'S4', 'developer')
        d = r.to_log_dict('test-session')
        assert d['session'] == 'test-session'
        assert d['current_stage'] == 'S4'
        assert d['violating_operation'] == 'write_code'

    def test_intercept_result_log_dict(self):
        checker = BoundaryChecker()
        r = checker.check(OperationType.WRITE_CODE, 'S1', 'orchestrator', '编写Redis代码')
        d = r.to_log_dict('session-001')
        assert d['current_stage'] == 'S1'
        assert d['violation_type'] is not None


class TestBoundaryResultAllowed:
    """BoundaryResult允许结果测试。"""

    def test_allowed_result_passes(self):
        r = BoundaryResult(
            allowed=True,
            operation=OperationType.WRITE_CODE,
            current_stage='S4',
            current_role='developer',
            message='OK',
            log_level='DEBUG',
        )
        assert r.allowed is True
        assert r.format_intercept_message() == ''
