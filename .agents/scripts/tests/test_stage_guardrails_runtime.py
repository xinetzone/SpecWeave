"""GuardrailRuntime 集成门面单元测试。"""

import sys
import pytest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from lib.stage_guardrails import (
    GuardrailRuntime,
    RuntimeStatus,
    OperationType,
    FormattedOutput,
    StageStatus,
)


@pytest.fixture
def rt():
    """创建一个新的GuardrailRuntime实例，默认进入S1阶段。"""
    runtime = GuardrailRuntime(session_id='test-session', enable_bypass_detection=True)
    runtime.enter_stage('S1', 'orchestrator', 'test start')
    return runtime


class TestInit:
    """初始化测试。"""

    def test_creation(self):
        rt = GuardrailRuntime(session_id='sess-001')
        assert rt.session_id == 'sess-001'
        assert rt.is_active is False
        assert rt.current_stage is None
        assert rt.interception_count == 0
        assert rt.bypass_count == 0
        assert rt.log_lines == []

    def test_creation_with_options(self):
        rt = GuardrailRuntime(session_id='sess-002', enable_color=True,
                              strict_mode=True, enable_bypass_detection=False)
        assert rt.strict_mode is True
        assert rt.formatter.enable_color is True
        assert rt.formatter.bypass_detector is None


class TestEnterExitStage:
    """阶段进入/退出测试。"""

    def test_enter_stage_success(self, rt):
        assert rt.is_active is True
        assert rt.current_stage == 'S1'
        assert rt.current_role == 'orchestrator'
        assert rt.current_stage_name == '需求接收'

    def test_enter_s1_logs_st_entry(self, rt):
        entry_logs = rt.get_logs_since(event_type='STAGE_ENTER')
        assert len(entry_logs) == 1
        assert 'S1' in entry_logs[0]
        assert 'orchestrator' in entry_logs[0]

    def test_duplicate_enter_produces_error(self, rt):
        out = rt.enter_stage('S1', 'orchestrator', 'duplicate')
        assert out.is_intercept is True
        assert out.log_level == 'ERROR'
        assert 'DUPLICATE_ENTRY' in out.sg_log_line

    def test_invalid_stage_produces_error(self):
        rt = GuardrailRuntime(session_id='sess')
        out = rt.enter_stage('SX', 'orchestrator', 'invalid')
        assert out.is_intercept is True
        assert 'INVALID_STAGE' in out.sg_log_line

    def test_invalid_role_produces_error(self):
        rt = GuardrailRuntime(session_id='sess')
        out = rt.enter_stage('S1', 'hacker', 'invalid role')
        assert out.is_intercept is True
        assert 'INVALID_ROLE' in out.sg_log_line or 'ROLE_STAGE_MISMATCH' in out.sg_log_line

    def test_exit_stage_success(self, rt):
        out = rt.exit_stage('S1', 'orchestrator', 'S1 done',
                            exit_criteria_met=['req clarified'],
                            output_artifacts=['task list'],
                            next_stage='S2')
        assert out.is_intercept is False
        assert out.event_type == 'STAGE_EXIT'
        assert rt.is_active is False
        exit_logs = rt.get_logs_since(event_type='STAGE_EXIT')
        assert len(exit_logs) == 1

    def test_exit_without_entry_produces_error(self):
        rt = GuardrailRuntime(session_id='sess')
        out = rt.exit_stage('S1', 'orchestrator', 'no entry')
        assert out.is_intercept is True
        assert 'EXIT_WITHOUT_ENTRY' in out.sg_log_line

    def test_exit_wrong_stage_produces_error(self, rt):
        out = rt.exit_stage('S2', 'orchestrator', 'wrong stage')
        assert out.is_intercept is True
        assert 'STAGE_MISMATCH' in out.sg_log_line


class TestGuardOperation:
    """guard_operation核心拦截入口测试。"""

    def test_allowed_operation_passes(self, rt):
        out = rt.guard_operation(OperationType.CLARIFY_REQUIREMENT, 'orchestrator',
                                  detail='clarify requirements')
        assert out.is_intercept is False
        assert out.event_type == 'BOUNDARY_PASS'
        assert out.log_level == 'DEBUG'

    def test_denied_operation_intercepted(self, rt):
        out = rt.guard_operation(OperationType.WRITE_CODE, 'orchestrator',
                                  detail='writing code too early')
        assert out.is_intercept is True
        assert out.event_type == 'INTERCEPT'
        assert out.log_level == 'WARN'
        assert 'S1' in out.user_message
        assert rt.interception_count == 1

    def test_bypass_detected_after_repeat(self, rt):
        out1 = rt.guard_operation(OperationType.WRITE_CODE, 'orchestrator', detail='first try')
        assert out1.event_type == 'INTERCEPT'
        out2 = rt.guard_operation(OperationType.MODIFY_BUSINESS_CODE, 'orchestrator',
                                   detail='equivalent op')
        assert out2.event_type == 'BYPASS_DETECTED'
        assert out2.log_level == 'ERROR'
        assert rt.bypass_count == 1
        assert rt.interception_count == 2

    def test_bypass_detection_disabled(self):
        rt = GuardrailRuntime(session_id='sess-nobypass', enable_bypass_detection=False)
        rt.enter_stage('S1', 'orchestrator', 'start')
        out1 = rt.guard_operation(OperationType.WRITE_CODE, 'orchestrator', detail='try1')
        out2 = rt.guard_operation(OperationType.MODIFY_BUSINESS_CODE, 'orchestrator', detail='try2')
        assert out1.event_type == 'INTERCEPT'
        assert out2.event_type == 'INTERCEPT'
        assert rt.bypass_count == 0

    def test_read_ops_always_allowed(self, rt):
        for op in [OperationType.SEARCH_CODE, OperationType.READ_DOCS]:
            out = rt.guard_operation(op, 'orchestrator')
            assert out.is_intercept is False, f'{op.value} should be allowed'

    def test_role_mismatch_intercepted(self, rt):
        out = rt.guard_operation(OperationType.CLARIFY_REQUIREMENT, 'tester', detail='wrong role')
        assert out.is_intercept is True
        assert out.event_type == 'INTERCEPT'

    def test_every_call_produces_check_log(self, rt):
        rt.guard_operation(OperationType.CLARIFY_REQUIREMENT, 'orchestrator')
        rt.guard_operation(OperationType.WRITE_CODE, 'orchestrator')
        check_logs = rt.get_logs_since(event_type='BOUNDARY_CHECK')
        assert len(check_logs) == 2


class TestDocCheckAndPDR:
    """前置文档检查和PDR测试。"""

    def test_mark_doc_check_success(self, rt):
        out = rt.mark_doc_check(required_docs=['spec.md', 'standards.md'])
        assert out.is_intercept is False
        assert out.event_type == 'DOC_CHECK'
        logs = rt.get_logs_since(event_type='DOC_CHECK')
        assert len(logs) == 1
        assert 'spec.md' in logs[0]

    def test_mark_pdr_done_success(self, rt):
        out = rt.mark_pdr_done()
        assert out.is_intercept is False
        assert out.event_type == 'PDR_CONFIRM'

    def test_doc_check_without_stage_error(self):
        rt = GuardrailRuntime(session_id='sess')
        out = rt.mark_doc_check(required_docs=['a.md'])
        assert out.is_intercept is True
        assert 'NO_ACTIVE_STAGE' in out.sg_log_line

    def test_pdr_without_stage_error(self):
        rt = GuardrailRuntime(session_id='sess')
        out = rt.mark_pdr_done()
        assert out.is_intercept is True


class TestJumpFlow:
    """阶段跳转申请/审批/拒绝/执行测试。"""

    def test_request_skip_success(self, rt):
        record, out = rt.request_jump('skip', 'S4', 'orchestrator', reason='simple task, jump to coding')
        assert record is not None
        assert record.jump_type == 'skip'
        assert record.to_stage == 'S4'
        assert out.is_intercept is False
        assert out.event_type == 'JUMP_REQUEST'
        assert rt.get_status().pending_jump is not None

    def test_request_rollback_success(self):
        rt = GuardrailRuntime(session_id='sess-rb')
        rt.enter_stage('S4', 'developer', 'coding')
        record, out = rt.request_jump('rollback', 'S2', 'developer', reason='design flaw found')
        assert record is not None
        assert record.jump_type == 'rollback'
        assert out.is_intercept is False

    def test_request_jump_without_stage_error(self):
        rt = GuardrailRuntime(session_id='sess')
        record, out = rt.request_jump('skip', 'S4', 'orchestrator', reason='test')
        assert record is None
        assert out.is_intercept is True

    def test_request_jump_to_s8_forbidden(self, rt):
        record, out = rt.request_jump('skip', 'S8', 'orchestrator', reason='jump to done')
        assert record is None
        assert out.is_intercept is True
        assert 'JUMP_TO_COMPLETION_FORBIDDEN' in out.sg_log_line

    def test_approve_skip(self, rt):
        rt.request_jump('skip', 'S4', 'orchestrator', reason='simple task')
        out = rt.approve_jump(f'jump-{rt.session_id}-1', 'orchestrator')
        assert out.is_intercept is False
        assert out.event_type == 'JUMP_APPROVED'
        assert rt.get_status().pending_jump is None

    def test_approve_jump_non_orchestrator_fails(self, rt):
        rt.request_jump('skip', 'S4', 'orchestrator', reason='x')
        out = rt.approve_jump(f'jump-{rt.session_id}-1', 'developer')
        assert out.is_intercept is True
        assert 'JUMP_APPROVER_NOT_ORCHESTRATOR' in out.sg_log_line

    def test_reject_jump(self, rt):
        rt.request_jump('skip', 'S4', 'orchestrator', reason='test')
        out = rt.reject_jump(f'jump-{rt.session_id}-1', 'orchestrator', reject_reason='insufficient reason')
        assert out.is_intercept is False
        assert out.event_type == 'JUMP_REJECTED'
        assert rt.get_status().pending_jump is None

    def test_execute_skip_after_approval(self, rt):
        rt.mark_doc_check(['spec.md'])
        rt.mark_pdr_done()
        rt.exit_stage('S1', 'orchestrator', 'S1 done',
                       exit_criteria_met=['done'], output_artifacts=['a'], next_stage='S2')
        rt.enter_stage('S2', 'architect', 'design')
        rt.request_jump('skip', 'S4', 'architect', reason='skip design detail')
        rt.approve_jump(f'jump-{rt.session_id}-1', 'orchestrator')
        out = rt.execute_skip(f'jump-{rt.session_id}-1', 'developer', 'execute skip to coding')
        assert out.is_intercept is False
        assert rt.current_stage == 'S4'
        assert rt.current_role == 'developer'

    def test_approve_rollback_auto_enters_target(self):
        rt = GuardrailRuntime(session_id='sess-rb2')
        rt.enter_stage('S4', 'developer', 'coding')
        rt.request_jump('rollback', 'S2', 'developer', reason='redesign needed')
        out = rt.approve_jump(f'jump-{rt.session_id}-1', 'orchestrator',
                               rollback_scope='discard current code')
        assert out.is_intercept is False
        assert rt.current_stage == 'S2'

    def test_execute_skip_without_approval_fails(self, rt):
        rt.request_jump('skip', 'S4', 'orchestrator', reason='x')
        out = rt.execute_skip(f'jump-{rt.session_id}-1', 'orchestrator')
        assert out.is_intercept is True
        assert 'JUMP_NOT_APPROVED' in out.sg_log_line


class TestAdvanceToNextStage:
    """顺序推进便捷方法测试。"""

    def test_advance_s1_to_s2(self, rt):
        rt.mark_doc_check(['spec.md'])
        rt.mark_pdr_done()
        out = rt.advance_to_next_stage(
            'orchestrator', exit_message='S1 complete',
            enter_message='start design',
            exit_criteria_met=['req clarified'],
            output_artifacts=['task list'],
        )
        assert out.is_intercept is False
        assert rt.current_stage == 'S2'
        assert rt.current_role == 'architect'
        assert rt.current_stage_name == '方案设计'
        assert 'S1' in rt.get_status().completed_stages

    def test_advance_without_active_stage(self):
        rt = GuardrailRuntime(session_id='sess')
        out = rt.advance_to_next_stage('orchestrator', exit_message='fail')
        assert out.is_intercept is True

    def test_advance_from_s8_fails(self):
        rt = GuardrailRuntime(session_id='sess-s8')
        rt.enter_stage('S8', 'orchestrator', 'final')
        out = rt.advance_to_next_stage('orchestrator', exit_message='try advance')
        assert out.is_intercept is True


class TestCanTransitionTo:
    """can_transition_to查询测试。"""

    def test_s1_to_s2_ok(self, rt):
        ok, reason = rt.can_transition_to('S2')
        assert ok is True

    def test_s1_to_s4_needs_skip(self, rt):
        ok, reason = rt.can_transition_to('S4')
        assert ok is False
        assert 'skip' in reason.lower() or '跳过' in reason

    def test_initial_to_s1_ok(self):
        rt = GuardrailRuntime(session_id='sess')
        ok, reason = rt.can_transition_to('S1')
        assert ok is True

    def test_s4_to_s2_needs_rollback(self):
        rt = GuardrailRuntime(session_id='sess-rb')
        rt.enter_stage('S4', 'developer', 'coding')
        ok, reason = rt.can_transition_to('S2')
        assert ok is False
        assert 'rollback' in reason.lower() or '回退' in reason


class TestGetStatus:
    """运行时状态快照测试。"""

    def test_initial_status(self):
        rt = GuardrailRuntime(session_id='sess')
        s = rt.get_status()
        assert isinstance(s, RuntimeStatus)
        assert s.session_id == 'sess'
        assert s.is_active is False
        assert s.current_stage is None
        assert s.interception_count == 0
        assert s.bypass_count == 0
        assert s.log_line_count == 0

    def test_active_status(self, rt):
        rt.guard_operation(OperationType.WRITE_CODE, 'orchestrator', detail='bad')
        s = rt.get_status()
        assert s.is_active is True
        assert s.current_stage == 'S1'
        assert s.current_stage_name == '需求接收'
        assert s.interception_count == 1
        assert s.log_line_count >= 3


class TestLogCollection:
    """日志收集与查询测试。"""

    def test_all_operations_logged(self, rt):
        rt.mark_doc_check(['a.md'])
        rt.mark_pdr_done()
        rt.guard_operation(OperationType.CLARIFY_REQUIREMENT, 'orchestrator')
        rt.guard_operation(OperationType.WRITE_CODE, 'orchestrator', detail='x')
        logs = rt.log_lines
        assert len(logs) >= 6
        for line in logs:
            assert line.startswith('[SG-LOG]')

    def test_get_logs_by_event_type(self, rt):
        rt.guard_operation(OperationType.CLARIFY_REQUIREMENT, 'orchestrator')
        check_logs = rt.get_logs_since(event_type='BOUNDARY_CHECK')
        pass_logs = rt.get_logs_since(event_type='BOUNDARY_PASS')
        entry_logs = rt.get_logs_since(event_type='STAGE_ENTER')
        assert len(check_logs) == 1
        assert len(pass_logs) == 1
        assert len(entry_logs) == 1

    def test_get_logs_by_level(self, rt):
        rt.guard_operation(OperationType.WRITE_CODE, 'orchestrator', detail='bad')
        rt.guard_operation(OperationType.CLARIFY_REQUIREMENT, 'orchestrator', detail='ok')
        warn_logs = rt.get_logs_since(level='WARN')
        info_logs = rt.get_logs_since(level='INFO')
        debug_logs = rt.get_logs_since(level='DEBUG')
        assert len(warn_logs) >= 1
        assert len(info_logs) >= 1
        assert len(debug_logs) >= 3

    def test_dump_logs(self, rt):
        rt.mark_doc_check(['a.md'])
        dump = rt.dump_logs()
        assert isinstance(dump, str)
        assert '[SG-LOG]' in dump
        assert '\n' in dump

    def test_clear_logs(self, rt):
        rt.guard_operation(OperationType.CLARIFY_REQUIREMENT, 'orchestrator')
        assert len(rt.log_lines) > 0
        rt.clear_logs()
        assert rt.log_lines == []


class TestReset:
    """重置测试。"""

    def test_reset_clears_state(self, rt):
        rt.guard_operation(OperationType.WRITE_CODE, 'orchestrator', detail='bad')
        assert rt.interception_count > 0
        assert len(rt.log_lines) > 0
        rt.reset()
        assert rt.is_active is False
        assert rt.current_stage is None
        assert rt.interception_count == 0
        assert rt.bypass_count == 0
        assert rt.log_lines == []


class TestFullFlowScenario:
    """完整生命周期场景测试。"""

    def test_happy_path_s1_to_s4(self):
        rt = GuardrailRuntime(session_id='full-flow')
        out = rt.enter_stage('S1', 'orchestrator', 'receive auth requirement')
        assert not out.is_intercept

        assert not rt.guard_operation(OperationType.CLARIFY_REQUIREMENT, 'orchestrator').is_intercept
        assert not rt.guard_operation(OperationType.CREATE_TASK_LIST, 'orchestrator').is_intercept
        assert not rt.guard_operation(OperationType.IDENTIFY_RISK, 'orchestrator').is_intercept
        assert rt.guard_operation(OperationType.WRITE_CODE, 'orchestrator').is_intercept

        out = rt.mark_doc_check(['spec.md', 'standards.md'])
        assert not out.is_intercept
        out = rt.mark_pdr_done()
        assert not out.is_intercept

        out = rt.advance_to_next_stage('orchestrator', 'S1 complete', enter_message='design phase',
                                       exit_criteria_met=['req clear'], output_artifacts=['tasks'])
        assert not out.is_intercept
        assert rt.current_stage == 'S2'

        assert not rt.guard_operation(OperationType.ARCHITECTURE_DESIGN, 'architect').is_intercept
        assert not rt.guard_operation(OperationType.CHOOSE_TECH_STACK, 'architect').is_intercept
        assert not rt.guard_operation(OperationType.DEFINE_API, 'architect').is_intercept
        assert rt.guard_operation(OperationType.WRITE_CODE, 'architect').is_intercept

        out = rt.mark_doc_check(['architecture.md'])
        out = rt.mark_pdr_done()
        out = rt.advance_to_next_stage('architect', 'S2 complete', enter_message='assign tasks')
        assert not out.is_intercept
        assert rt.current_stage == 'S3'

        assert not rt.guard_operation(OperationType.ASSIGN_TASK, 'orchestrator').is_intercept
        assert not rt.guard_operation(OperationType.SET_ACCEPTANCE_CRITERIA, 'orchestrator').is_intercept

        out = rt.mark_doc_check(['task-list.md'])
        out = rt.mark_pdr_done()
        out = rt.advance_to_next_stage('orchestrator', 'S3 complete', enter_message='start coding')
        assert not out.is_intercept
        assert rt.current_stage == 'S4'

        assert not rt.guard_operation(OperationType.WRITE_CODE, 'developer').is_intercept
        assert not rt.guard_operation(OperationType.WRITE_UNIT_TEST, 'developer').is_intercept
        assert not rt.guard_operation(OperationType.RUN_TEST, 'developer').is_intercept
        assert not rt.guard_operation(OperationType.SUBMIT_PR, 'developer').is_intercept
        assert rt.guard_operation(OperationType.MODIFY_ARCHITECTURE, 'developer').is_intercept

        status = rt.get_status()
        assert status.completed_stages == ['S1', 'S2', 'S3']
        assert status.current_stage == 'S4'
        assert status.interception_count == 3
        assert status.bypass_count == 0

    def test_jump_flow_with_skip(self):
        rt = GuardrailRuntime(session_id='jump-flow')
        rt.enter_stage('S1', 'orchestrator', 'simple bug fix')
        rt.mark_doc_check(['bug-report.md'])
        rt.mark_pdr_done()
        rt.exit_stage('S1', 'orchestrator', 'S1 done', exit_criteria_met=['bug understood'],
                       output_artifacts=['fix plan'], next_stage='S2')
        rt.enter_stage('S2', 'architect', 'design fix')

        record, out = rt.request_jump('skip', 'S4', 'architect', reason='trivial fix, skip design detail')
        assert record is not None
        out = rt.approve_jump(record.jump_id, 'orchestrator')
        assert not out.is_intercept
        out = rt.execute_skip(record.jump_id, 'developer', 'jump to coding')
        assert not out.is_intercept
        assert rt.current_stage == 'S4'
        assert not rt.guard_operation(OperationType.WRITE_CODE, 'developer').is_intercept

    def test_error_recovery_via_format(self):
        rt = GuardrailRuntime(session_id='err-flow')
        out = rt.enter_stage('S1', 'orchestrator', 'start')
        out_dup = rt.enter_stage('S1', 'orchestrator', 'duplicate')
        assert out_dup.is_intercept is True
        assert out_dup.user_message != ''
        assert 'DUPLICATE_ENTRY' in out_dup.sg_log_line
        assert out_dup.event_type == 'ERROR'
