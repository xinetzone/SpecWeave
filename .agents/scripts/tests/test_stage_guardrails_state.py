"""StageStateManager 单元测试。"""

import sys
import pytest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from lib.stage_guardrails.state import (
    StageStateManager,
    StageStatus,
    TransitionError,
    DuplicateEntryError,
    ExitWithoutEntryError,
    StageMismatchError,
    UnauthorizedJumpError,
    InvalidJumpError,
    InvalidStageError,
    InvalidRoleError,
    STAGE_ORDER,
    STAGE_NAMES,
    VALID_ROLES,
)


class TestConstants:
    """常量定义测试。"""

    def test_stage_order_has_8_stages(self):
        assert len(STAGE_ORDER) == 8
        assert STAGE_ORDER['S1'] == 1
        assert STAGE_ORDER['S8'] == 8

    def test_stage_names_complete(self):
        assert set(STAGE_NAMES.keys()) == set(STAGE_ORDER.keys())
        assert STAGE_NAMES['S1'] == '需求接收'
        assert STAGE_NAMES['S4'] == '代码实现'

    def test_valid_roles(self):
        assert VALID_ROLES == {'orchestrator', 'architect', 'developer', 'tester', 'reviewer'}


class TestStageStateManagerInit:
    """初始化测试。"""

    def test_default_state(self):
        mgr = StageStateManager(session_id='test-001')
        assert mgr.session_id == 'test-001'
        assert mgr.current_stage is None
        assert mgr.current_role is None
        assert mgr.is_active is False
        assert mgr.completed_stages == []
        assert mgr.transitions == []
        assert mgr.jump_records == []

    def test_initial_stage_status(self):
        mgr = StageStateManager(session_id='test-002')
        assert mgr.stage_status('S1') == StageStatus.NOT_ENTERED
        assert mgr.stage_status('S4') == StageStatus.NOT_ENTERED


class TestStageEntry:
    """阶段进入测试。"""

    def test_enter_first_stage(self):
        mgr = StageStateManager(session_id='test-enter')
        mgr.enter_stage('S1', 'orchestrator', '收到用户需求')
        assert mgr.current_stage == 'S1'
        assert mgr.current_stage_name == '需求接收'
        assert mgr.current_role == 'orchestrator'
        assert mgr.is_active is True
        assert mgr.stage_status('S1') == StageStatus.ACTIVE

    def test_enter_records_transition(self):
        mgr = StageStateManager(session_id='test-trans')
        mgr.enter_stage('S1', 'orchestrator', 'entry msg')
        assert len(mgr.transitions) == 1
        t = mgr.transitions[0]
        assert t.event == 'STAGE_ENTER'
        assert t.stage == 'S1'
        assert t.role == 'orchestrator'
        assert t.from_stage is None

    def test_duplicate_entry_raises(self):
        mgr = StageStateManager(session_id='test-dup')
        mgr.enter_stage('S1', 'orchestrator', 'first entry')
        with pytest.raises(DuplicateEntryError) as exc_info:
            mgr.enter_stage('S2', 'architect', 'try enter S2 without exiting S1')
        assert exc_info.value.code == 'DUPLICATE_ENTRY'

    def test_invalid_stage_raises(self):
        mgr = StageStateManager(session_id='test-invalid-stage')
        with pytest.raises(InvalidStageError) as exc_info:
            mgr.enter_stage('S9', 'orchestrator', 'bad stage')
        assert exc_info.value.code == 'INVALID_STAGE'

    def test_invalid_role_raises(self):
        mgr = StageStateManager(session_id='test-invalid-role')
        with pytest.raises(InvalidRoleError) as exc_info:
            mgr.enter_stage('S1', 'designer', 'bad role')
        assert exc_info.value.code == 'INVALID_ROLE'

    def test_role_stage_mismatch_raises(self):
        mgr = StageStateManager(session_id='test-role-mismatch')
        with pytest.raises(InvalidRoleError) as exc_info:
            mgr.enter_stage('S4', 'tester', 'developer should implement')
        assert exc_info.value.code == 'ROLE_STAGE_MISMATCH'
        assert 'developer' in exc_info.value.message


class TestStageExit:
    """阶段退出测试。"""

    def test_exit_after_enter(self):
        mgr = StageStateManager(session_id='test-exit')
        mgr.enter_stage('S1', 'orchestrator', 'enter')
        record = mgr.exit_stage('S1', 'orchestrator', 'exit',
                                exit_criteria_met=['需求已澄清'],
                                output_artifacts=['任务清单'],
                                next_stage='S2')
        assert mgr.current_stage is None
        assert mgr.current_role is None
        assert mgr.is_active is False
        assert mgr.stage_status('S1') == StageStatus.COMPLETED
        assert mgr.completed_stages == ['S1']

    def test_exit_records_transition(self):
        mgr = StageStateManager(session_id='test-exit-trans')
        mgr.enter_stage('S1', 'orchestrator', 'enter')
        mgr.exit_stage('S1', 'orchestrator', 'exit')
        assert len(mgr.transitions) == 2
        exit_trans = mgr.transitions[-1]
        assert exit_trans.event == 'STAGE_EXIT'
        assert exit_trans.stage == 'S1'

    def test_exit_without_entry_raises(self):
        mgr = StageStateManager(session_id='test-no-entry')
        with pytest.raises(ExitWithoutEntryError) as exc_info:
            mgr.exit_stage('S1', 'orchestrator', 'exit')
        assert exc_info.value.code == 'EXIT_WITHOUT_ENTRY'

    def test_exit_wrong_stage_raises(self):
        mgr = StageStateManager(session_id='test-wrong-stage')
        mgr.enter_stage('S1', 'orchestrator', 'enter')
        with pytest.raises(StageMismatchError) as exc_info:
            mgr.exit_stage('S2', 'architect', 'exit wrong stage')
        assert exc_info.value.code == 'STAGE_MISMATCH'


class TestSequentialFlow:
    """顺序流程测试（S1→S2→S3）。"""

    def test_three_stage_flow(self):
        mgr = StageStateManager(session_id='test-flow')
        mgr.enter_stage('S1', 'orchestrator', '需求接收')
        mgr.mark_doc_check(required_docs=['用户需求文档'])
        mgr.mark_pdr_done()
        mgr.exit_stage('S1', 'orchestrator', 'S1完成',
                       exit_criteria_met=['需求澄清', '验收标准明确'],
                       output_artifacts=['任务分解清单'],
                       next_stage='S2')

        mgr.enter_stage('S2', 'architect', '方案设计')
        assert mgr.current_stage == 'S2'
        assert mgr.completed_stages == ['S1']

        mgr.exit_stage('S2', 'architect', 'S2完成',
                       exit_criteria_met=['技术方案完成', '风险评估覆盖'],
                       output_artifacts=['技术方案文档'],
                       next_stage='S3')

        mgr.enter_stage('S3', 'orchestrator', '任务分配')
        assert mgr.current_stage == 'S3'
        assert mgr.completed_stages == ['S1', 'S2']
        assert mgr.stage_status('S1') == StageStatus.COMPLETED
        assert mgr.stage_status('S2') == StageStatus.COMPLETED
        assert mgr.stage_status('S3') == StageStatus.ACTIVE

    def test_doc_check_marks_record(self):
        mgr = StageStateManager(session_id='test-doccheck')
        mgr.enter_stage('S4', 'developer', '编码')
        mgr.mark_doc_check(required_docs=['spec.md', 'standards.md'])
        record = mgr.get_stage_record('S4')
        assert record.doc_check_done is True

    def test_pdr_done_marks_record(self):
        mgr = StageStateManager(session_id='test-pdr')
        mgr.enter_stage('S6', 'reviewer', '审查')
        mgr.mark_pdr_done()
        record = mgr.get_stage_record('S6')
        assert record.pdr_done is True


class TestCanTransitionTo:
    """转换可行性检查测试。"""

    def test_initial_can_enter_s1(self):
        mgr = StageStateManager(session_id='test-can-s1')
        ok, reason = mgr.can_transition_to('S1')
        assert ok is True

    def test_s1_to_s2_normal(self):
        mgr = StageStateManager(session_id='test-can-s2')
        mgr.enter_stage('S1', 'orchestrator', 'enter')
        ok, reason = mgr.can_transition_to('S2')
        assert ok is True
        assert 'S1→S2' in reason

    def test_s1_to_s4_needs_skip(self):
        mgr = StageStateManager(session_id='test-can-skip')
        mgr.enter_stage('S1', 'orchestrator', 'enter')
        ok, reason = mgr.can_transition_to('S4')
        assert ok is False
        assert '跳过' in reason

    def test_s4_to_s2_needs_rollback(self):
        mgr = StageStateManager(session_id='test-can-rollback')
        mgr.enter_stage('S1', 'orchestrator', 's1')
        mgr.exit_stage('S1', 'orchestrator', 'exit', next_stage='S2')
        mgr.enter_stage('S2', 'architect', 's2')
        mgr.exit_stage('S2', 'architect', 'exit', next_stage='S3')
        mgr.enter_stage('S3', 'orchestrator', 's3')
        mgr.exit_stage('S3', 'orchestrator', 'exit', next_stage='S4')
        mgr.enter_stage('S4', 'developer', 's4')
        ok, reason = mgr.can_transition_to('S2')
        assert ok is False
        assert '回退' in reason


class TestJumpFlow:
    """阶段跳转审批测试。"""

    def test_request_and_approve_skip(self):
        mgr = StageStateManager(session_id='test-skip')
        mgr.enter_stage('S2', 'architect', '方案设计')
        jump = mgr.request_jump('skip', 'S4', 'developer', '文案修改极简单点修复')
        assert jump.jump_type == 'skip'
        assert jump.from_stage == 'S2'
        assert jump.to_stage == 'S4'
        assert jump.approved is False
        assert mgr._pending_jump is not None

        approved = mgr.approve_jump(jump.jump_id, 'orchestrator',
                                     conditions='developer自行确认影响范围')
        assert approved.approved is True
        assert approved.approved_by == 'orchestrator'
        assert mgr._pending_jump is None

    def test_execute_skip_after_approval(self):
        mgr = StageStateManager(session_id='test-skip-exec')
        mgr.enter_stage('S2', 'architect', '方案设计')
        jump = mgr.request_jump('skip', 'S4', 'developer', '极简单点修复')
        mgr.approve_jump(jump.jump_id, 'orchestrator', conditions='确认影响范围')
        mgr.execute_skip(jump.jump_id, 'orchestrator', '跳过S3直接进入S4')
        assert mgr.current_stage == 'S4'
        assert mgr.stage_status('S2') == StageStatus.COMPLETED
        assert mgr.completed_stages == ['S2']

    def test_request_and_reject_jump(self):
        mgr = StageStateManager(session_id='test-reject')
        mgr.enter_stage('S2', 'architect', '设计中')
        jump = mgr.request_jump('skip', 'S4', 'developer', '想跳过')
        rejected = mgr.reject_jump(jump.jump_id, 'orchestrator', '方案尚未评审不可跳过')
        assert rejected.approved is False
        assert rejected.reject_reason is not None
        assert mgr.current_stage == 'S2'

    def test_request_and_approve_rollback(self):
        mgr = StageStateManager(session_id='test-rollback')
        mgr.enter_stage('S1', 'orchestrator', 's1')
        mgr.exit_stage('S1', 'orchestrator', 'exit', next_stage='S2')
        mgr.enter_stage('S2', 'architect', 's2')
        mgr.exit_stage('S2', 'architect', 'exit', next_stage='S3')
        mgr.enter_stage('S3', 'orchestrator', 's3')
        mgr.exit_stage('S3', 'orchestrator', 'exit', next_stage='S4')
        mgr.enter_stage('S4', 'developer', '编码中')

        jump = mgr.request_jump('rollback', 'S2', 'architect',
                                'JWT方案不适合微服务架构需重新设计')
        assert jump.jump_type == 'rollback'
        approved = mgr.approve_jump(jump.jump_id, 'orchestrator',
                                     rollback_scope='auth.py已实现的50行JWT代码作废',
                                     conditions='回退后S3/S4必须重新执行')
        assert approved.approved is True
        assert mgr.current_stage == 'S2'
        assert mgr.stage_status('S4') == StageStatus.ROLLED_BACK

    def test_non_orchestrator_approve_raises(self):
        mgr = StageStateManager(session_id='test-approve-perm')
        mgr.enter_stage('S2', 'architect', 's2')
        jump = mgr.request_jump('skip', 'S4', 'developer', '理由')
        with pytest.raises(UnauthorizedJumpError) as exc_info:
            mgr.approve_jump(jump.jump_id, 'developer', '自我批准')
        assert exc_info.value.code == 'JUMP_APPROVER_NOT_ORCHESTRATOR'

    def test_jump_to_s8_forbidden(self):
        mgr = StageStateManager(session_id='test-no-s8')
        mgr.enter_stage('S6', 'reviewer', '审查中')
        with pytest.raises(InvalidJumpError) as exc_info:
            mgr.request_jump('skip', 'S8', 'reviewer', '直接完成')
        assert exc_info.value.code == 'JUMP_TO_COMPLETION_FORBIDDEN'

    def test_invalid_rollback_target_raises(self):
        mgr = StageStateManager(session_id='test-bad-rollback')
        mgr.enter_stage('S4', 'developer', 's4')
        with pytest.raises(InvalidJumpError) as exc_info:
            mgr.request_jump('rollback', 'S6', 'developer', '回退到S6')
        assert exc_info.value.code == 'INVALID_ROLLBACK_TARGET'

    def test_invalid_skip_target_raises(self):
        mgr = StageStateManager(session_id='test-bad-skip')
        mgr.enter_stage('S4', 'developer', 's4')
        with pytest.raises(InvalidJumpError) as exc_info:
            mgr.request_jump('skip', 'S2', 'developer', '跳到S2')
        assert exc_info.value.code == 'INVALID_SKIP_TARGET'

    def test_approve_without_request_raises(self):
        mgr = StageStateManager(session_id='test-no-req')
        mgr.enter_stage('S1', 'orchestrator', 's1')
        with pytest.raises(InvalidJumpError) as exc_info:
            mgr.approve_jump('jump-nonexistent-1', 'orchestrator')
        assert exc_info.value.code == 'JUMP_NOT_FOUND'

    def test_execute_unapproved_jump_raises(self):
        mgr = StageStateManager(session_id='test-unapproved')
        mgr.enter_stage('S2', 'architect', 's2')
        jump = mgr.request_jump('skip', 'S4', 'developer', '理由')
        with pytest.raises(UnauthorizedJumpError) as exc_info:
            mgr.execute_skip(jump.jump_id, 'orchestrator', '执行')
        assert exc_info.value.code == 'JUMP_NOT_APPROVED'


class TestDocCheckWithoutStage:
    """无活跃阶段时的操作异常测试。"""

    def test_doc_check_without_stage_raises(self):
        mgr = StageStateManager(session_id='test-nostage-doc')
        with pytest.raises(ExitWithoutEntryError):
            mgr.mark_doc_check(['doc.md'])

    def test_pdr_without_stage_raises(self):
        mgr = StageStateManager(session_id='test-nostage-pdr')
        with pytest.raises(ExitWithoutEntryError):
            mgr.mark_pdr_done()

    def test_jump_without_stage_raises(self):
        mgr = StageStateManager(session_id='test-nostage-jump')
        with pytest.raises(ExitWithoutEntryError):
            mgr.request_jump('skip', 'S4', 'developer', '理由')


class TestToDict:
    """序列化测试。"""

    def test_to_dict_initial(self):
        mgr = StageStateManager(session_id='test-dict')
        d = mgr.to_dict()
        assert d['session_id'] == 'test-dict'
        assert d['current_stage'] is None
        assert d['is_active'] is False
        assert d['pending_jump'] is None

    def test_to_dict_active(self):
        mgr = StageStateManager(session_id='test-dict-active')
        mgr.enter_stage('S4', 'developer', '编码')
        d = mgr.to_dict()
        assert d['current_stage'] == 'S4'
        assert d['current_stage_name'] == '代码实现'
        assert d['current_role'] == 'developer'
        assert d['is_active'] is True
        assert d['completed_stages'] == []
        assert d['transition_count'] == 1
