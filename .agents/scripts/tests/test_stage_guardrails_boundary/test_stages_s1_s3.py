from lib.stage_guardrails.boundary import BoundaryChecker, OperationType


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
