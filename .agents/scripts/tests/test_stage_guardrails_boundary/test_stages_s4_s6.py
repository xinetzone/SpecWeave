from lib.stage_guardrails.boundary import BoundaryChecker, OperationType


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
