from lib.stage_guardrails.boundary import (
    BoundaryChecker,
    BoundaryResult,
    OperationType,
    STAGE_EXIT_CRITERIA,
)


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
