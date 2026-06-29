"""InterceptorFormatter 拦截输出格式化器单元测试。"""

import sys
import json
import pytest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from lib.stage_guardrails.interceptor import (
    InterceptorFormatter,
    BypassDetector,
    FormattedOutput,
)
from lib.stage_guardrails.boundary import (
    BoundaryChecker,
    BoundaryResult,
    OperationType,
)
from lib.stage_guardrails.state import STAGE_NAMES


class TestFormattedOutput:
    """FormattedOutput数据类测试。"""

    def test_default_values(self):
        out = FormattedOutput()
        assert out.user_message == ''
        assert out.sg_log_line == ''
        assert out.is_intercept is False
        assert out.log_level == 'DEBUG'

    def test_str_with_content(self):
        out = FormattedOutput(user_message='intercept msg', sg_log_line='[SG-LOG] ...')
        s = str(out)
        assert 'intercept msg' in s
        assert '[SG-LOG]' in s


class TestInterceptorFormatterInit:
    """初始化测试。"""

    def test_creation(self):
        fmt = InterceptorFormatter(session_id='test-sess')
        assert fmt.session_id == 'test-sess'
        assert fmt.enable_color is False
        assert fmt.bypass_detector is not None

    def test_creation_no_bypass(self):
        fmt = InterceptorFormatter(session_id='test-sess', enable_bypass_detection=False)
        assert fmt.bypass_detector is None

    def test_creation_with_color(self):
        fmt = InterceptorFormatter(session_id='test-sess', enable_color=True)
        assert fmt.enable_color is True


class TestFormatSgLog:
    """SG-LOG基础格式化测试。"""

    def setup_method(self):
        self.fmt = InterceptorFormatter(session_id='sess-001', enable_color=False)

    def test_basic_log_format(self):
        line = self.fmt.format_sg_log(
            level='INFO', event='STAGE_ENTER', stage='S1',
            role='orchestrator', msg='进入需求接收阶段',
        )
        assert line.startswith('[SG-LOG]')
        assert 'level=INFO' in line
        assert 'event=STAGE_ENTER' in line
        assert 'stage=S1' in line
        assert 'role=orchestrator' in line
        assert 'session=sess-001' in line
        assert 'msg=进入需求接收阶段' in line

    def test_log_with_ctx(self):
        line = self.fmt.format_sg_log(
            level='WARN', event='INTERCEPT', stage='S1',
            role='developer', msg='拦截写代码',
            ctx={'op': 'write_code', 'target': 'S4'},
        )
        assert 'ctx=' in line
        parsed = InterceptorFormatter.parse_sg_log(line)
        assert parsed is not None
        assert parsed['level'] == 'WARN'
        assert parsed['event'] == 'INTERCEPT'
        assert parsed['ctx']['op'] == 'write_code'
        assert parsed['ctx']['target'] == 'S4'

    def test_log_without_ctx(self):
        line = self.fmt.format_sg_log(
            level='DEBUG', event='BOUNDARY_PASS', stage='S4',
            role='developer', msg='操作通过',
        )
        assert 'ctx=' not in line

    def test_ctx_json_single_line(self):
        line = self.fmt.format_sg_log(
            level='WARN', event='INTERCEPT', stage='S1',
            role='dev', msg='test',
            ctx={'key1': 'val1', 'key2': 'val2'},
        )
        assert '\n' not in line

    def test_chinese_in_msg(self):
        line = self.fmt.format_sg_log(
            level='WARN', event='INTERCEPT', stage='S4',
            role='developer', msg='擅自变更架构决策属于违规操作',
        )
        assert '擅自变更架构决策' in line
        parsed = InterceptorFormatter.parse_sg_log(line)
        assert parsed['msg'] == '擅自变更架构决策属于违规操作'


class TestBoundaryCheckLog:
    """BOUNDARY_CHECK/BOUNDARY_PASS日志测试。"""

    def setup_method(self):
        self.fmt = InterceptorFormatter(session_id='sess-002', enable_color=False)

    def test_boundary_check_log(self):
        line = self.fmt.format_boundary_check(
            OperationType.WRITE_CODE, 'S1', 'orchestrator',
            detail='编写Redis配置', allowed_ops=['澄清需求', '创建任务'],
        )
        assert 'event=BOUNDARY_CHECK' in line
        assert 'level=DEBUG' in line
        parsed = InterceptorFormatter.parse_sg_log(line)
        assert parsed['event'] == 'BOUNDARY_CHECK'
        assert parsed['ctx']['operation'] == 'write_code'

    def test_boundary_pass_log(self):
        line = self.fmt.format_boundary_pass(
            OperationType.WRITE_CODE, 'S4', 'developer',
            detail='实现登录接口',
        )
        assert 'event=BOUNDARY_PASS' in line
        assert 'level=DEBUG' in line
        assert '实现登录接口' in line


class TestFormatIntercept:
    """拦截输出格式化测试。"""

    def setup_method(self):
        self.fmt = InterceptorFormatter(session_id='sess-003', enable_color=False)
        self.checker = BoundaryChecker()

    def test_s1_write_code_intercept(self):
        result = self.checker.check(OperationType.WRITE_CODE, 'S1', 'orchestrator')
        out = self.fmt.format_intercept(result)
        assert out.is_intercept is True
        assert out.log_level == 'WARN'
        assert out.event_type == 'INTERCEPT'
        assert '⚠️' in out.user_message
        assert 'S1' in out.user_message
        assert '需求接收' in out.user_message
        assert 'event=INTERCEPT' in out.sg_log_line
        assert 'level=WARN' in out.sg_log_line

    def test_intercept_with_detail(self):
        result = self.checker.check(OperationType.WRITE_CODE, 'S1', 'orchestrator')
        out = self.fmt.format_intercept(result, detail='编写Redis缓存配置代码')
        assert '编写Redis缓存配置代码' in out.user_message
        assert '编写Redis缓存配置代码' in out.sg_log_line

    def test_intercept_contains_exit_criteria(self):
        result = self.checker.check(OperationType.WRITE_CODE, 'S1', 'orchestrator')
        out = self.fmt.format_intercept(result)
        assert '请先完成当前阶段' in out.user_message
        assert '明确功能边界与验收标准' in out.user_message

    def test_intercept_contains_jump_hint(self):
        result = self.checker.check(OperationType.WRITE_CODE, 'S1', 'orchestrator')
        out = self.fmt.format_intercept(result)
        assert '跳过' in out.user_message or '回退' in out.user_message or '跳转' in out.user_message

    def test_no_active_stage_intercept(self):
        result = self.checker.check(OperationType.WRITE_CODE, None, 'developer')
        out = self.fmt.format_intercept(result)
        assert out.is_intercept is True
        assert '未进入' in out.user_message or '无活跃阶段' in out.user_message or 'S1' in out.user_message
        assert 'event=INTERCEPT' in out.sg_log_line

    def test_role_mismatch_intercept(self):
        result = self.checker.check(OperationType.CLARIFY_REQUIREMENT, 'S1', 'tester')
        out = self.fmt.format_intercept(result)
        assert out.is_intercept is True
        assert 'tester' in out.user_message or '角色' in out.user_message

    def test_s5_fix_bug_intercept(self):
        result = self.checker.check(OperationType.FIX_BUG, 'S5', 'tester')
        out = self.fmt.format_intercept(result)
        assert out.is_intercept is True
        assert 'tester' in out.user_message or 'developer' in out.user_message

    def test_s4_to_s2_rollback_hint(self):
        result = self.checker.check(OperationType.MODIFY_ARCHITECTURE, 'S4', 'developer')
        out = self.fmt.format_intercept(result)
        assert '回退' in out.user_message or 'S2' in out.user_message


class TestFormatResult:
    """format_result自动路由测试。"""

    def setup_method(self):
        self.fmt = InterceptorFormatter(session_id='sess-004', enable_color=False)
        self.checker = BoundaryChecker()

    def test_allowed_result_produces_pass(self):
        result = self.checker.check(OperationType.CLARIFY_REQUIREMENT, 'S1', 'orchestrator')
        out = self.fmt.format_result(result)
        assert out.is_intercept is False
        assert out.user_message == ''
        assert 'BOUNDARY_PASS' in out.sg_log_line

    def test_denied_result_produces_intercept(self):
        result = self.checker.check(OperationType.WRITE_CODE, 'S1', 'orchestrator')
        out = self.fmt.format_result(result)
        assert out.is_intercept is True
        assert 'INTERCEPT' in out.sg_log_line
        assert out.user_message != ''


class TestBypassDetector:
    """绕过行为检测器测试。"""

    def setup_method(self):
        self.detector = BypassDetector()

    def test_record_and_detect_same_op(self):
        result = BoundaryResult(
            allowed=False, operation=OperationType.WRITE_CODE,
            current_stage='S1', current_role='orchestrator',
            violation_type='STAGE_BOUNDARY_VIOLATION',
        )
        self.detector.record_intercept(result)
        bypass = self.detector.check_bypass(OperationType.WRITE_CODE, 'S1', 'orchestrator')
        assert bypass is not None
        assert 'WRITE_CODE' in bypass['detection_reason'] or 'write_code' in bypass['detection_reason']

    def test_equivalent_bypass_detection(self):
        result = BoundaryResult(
            allowed=False, operation=OperationType.WRITE_CODE,
            current_stage='S1', current_role='developer',
            violation_type='STAGE_BOUNDARY_VIOLATION',
        )
        self.detector.record_intercept(result)
        bypass = self.detector.check_bypass(OperationType.MODIFY_BUSINESS_CODE, 'S1', 'developer')
        assert bypass is not None
        assert '替代操作' in bypass['detection_reason'] or '绕过' in bypass['detection_reason']

    def test_no_bypass_for_different_op(self):
        result = BoundaryResult(
            allowed=False, operation=OperationType.WRITE_CODE,
            current_stage='S1', current_role='orchestrator',
            violation_type='STAGE_BOUNDARY_VIOLATION',
        )
        self.detector.record_intercept(result)
        bypass = self.detector.check_bypass(OperationType.CLARIFY_REQUIREMENT, 'S1', 'orchestrator')
        assert bypass is None

    def test_clear(self):
        result = BoundaryResult(
            allowed=False, operation=OperationType.WRITE_CODE,
            current_stage='S1', current_role='orchestrator',
            violation_type='STAGE_BOUNDARY_VIOLATION',
        )
        self.detector.record_intercept(result)
        self.detector.clear()
        bypass = self.detector.check_bypass(OperationType.WRITE_CODE, 'S1', 'orchestrator')
        assert bypass is None

    def test_architecture_equivalents(self):
        result = BoundaryResult(
            allowed=False, operation=OperationType.CHOOSE_TECH_STACK,
            current_stage='S1', current_role='orchestrator',
            violation_type='STAGE_BOUNDARY_VIOLATION',
        )
        self.detector.record_intercept(result)
        assert self.detector.check_bypass(OperationType.MODIFY_ARCHITECTURE, 'S1', 'orchestrator') is not None
        self.detector.clear()
        self.detector.record_intercept(result)
        assert self.detector.check_bypass(OperationType.CHANGE_TECH_SELECTION, 'S1', 'orchestrator') is not None


class TestBypassDetected:
    """BYPASS_DETECTED格式化测试。"""

    def setup_method(self):
        self.fmt = InterceptorFormatter(session_id='sess-005', enable_color=False)

    def test_bypass_output(self):
        detection = {
            'detection_reason': '拦截后重复执行write_code',
            'evidence': 'S1阶段write_code已拦截但再次尝试',
        }
        out = self.fmt.format_bypass_detected(
            OperationType.WRITE_CODE, 'S1', 'developer', detection,
        )
        assert out.is_intercept is True
        assert out.log_level == 'ERROR'
        assert out.event_type == 'BYPASS_DETECTED'
        assert '❌' in out.user_message or '绕过' in out.user_message
        assert 'event=BYPASS_DETECTED' in out.sg_log_line
        assert 'level=ERROR' in out.sg_log_line
        parsed = InterceptorFormatter.parse_sg_log(out.sg_log_line)
        assert parsed['event'] == 'BYPASS_DETECTED'
        assert parsed['ctx']['detection_reason'] == '拦截后重复执行write_code'


class TestFormatError:
    """ERROR事件格式化测试。"""

    def setup_method(self):
        self.fmt = InterceptorFormatter(session_id='sess-006', enable_color=False)

    def test_error_output(self):
        out = self.fmt.format_error(
            stage='S4', role='developer',
            error_type='UNAUTHORIZED_JUMP',
            error_detail='S4→S6跳转无审批记录',
            impact='代码未经测试可能引入缺陷',
            recovery_hint='退回S5补充测试用例',
        )
        assert out.log_level == 'ERROR'
        assert out.event_type == 'ERROR'
        assert 'event=ERROR' in out.sg_log_line
        parsed = InterceptorFormatter.parse_sg_log(out.sg_log_line)
        assert parsed['ctx']['error_type'] == 'UNAUTHORIZED_JUMP'
        assert parsed['ctx']['impact'] == '代码未经测试可能引入缺陷'
        assert parsed['ctx']['recovery_hint'] == '退回S5补充测试用例'


class TestParseSgLog:
    """SG-LOG反向解析测试。"""

    def test_parse_valid_log(self):
        line = '[SG-LOG] | level=WARN | event=INTERCEPT | stage=S1 | role=dev | session=s1 | msg=test msg | ctx={"op":"write"}'
        parsed = InterceptorFormatter.parse_sg_log(line)
        assert parsed is not None
        assert parsed['level'] == 'WARN'
        assert parsed['event'] == 'INTERCEPT'
        assert parsed['stage'] == 'S1'
        assert parsed['role'] == 'dev'
        assert parsed['session'] == 's1'
        assert parsed['msg'] == 'test msg'
        assert parsed['ctx']['op'] == 'write'

    def test_parse_non_sg_log(self):
        assert InterceptorFormatter.parse_sg_log('regular log line') is None
        assert InterceptorFormatter.parse_sg_log('') is None

    def test_parse_log_without_ctx(self):
        line = '[SG-LOG] | level=INFO | event=STAGE_ENTER | stage=S1 | role=orch | session=s2 | msg=enter'
        parsed = InterceptorFormatter.parse_sg_log(line)
        assert parsed is not None
        assert 'ctx' not in parsed or 'ctx' not in parsed

    def test_roundtrip_format_parse(self):
        fmt = InterceptorFormatter(session_id='roundtrip', enable_color=False)
        line = fmt.format_sg_log(
            level='WARN', event='INTERCEPT', stage='S4',
            role='developer', msg='测试中文消息',
            ctx={'key': '中文值', 'num': 42},
        )
        parsed = InterceptorFormatter.parse_sg_log(line)
        assert parsed is not None
        assert parsed['msg'] == '测试中文消息'
        assert parsed['ctx']['key'] == '中文值'
        assert parsed['ctx']['num'] == 42


class TestColorOutput:
    """彩色输出测试。"""

    def test_color_enabled(self):
        fmt = InterceptorFormatter(session_id='sess-color', enable_color=True)
        result = BoundaryChecker().check(OperationType.WRITE_CODE, 'S1', 'orchestrator')
        out = fmt.format_intercept(result)
        assert '\033[' in out.user_message

    def test_color_disabled(self):
        fmt = InterceptorFormatter(session_id='sess-nocolor', enable_color=False)
        result = BoundaryChecker().check(OperationType.WRITE_CODE, 'S1', 'orchestrator')
        out = fmt.format_intercept(result)
        assert '\033[' not in out.user_message


class TestBypassIntegration:
    """绕过检测与format_result集成测试。"""

    def test_repeat_intercept_triggers_bypass(self):
        fmt = InterceptorFormatter(session_id='sess-bypass', enable_color=False, enable_bypass_detection=True)
        checker = BoundaryChecker()
        result1 = checker.check(OperationType.WRITE_CODE, 'S1', 'orchestrator')
        out1 = fmt.format_result(result1)
        assert out1.event_type == 'INTERCEPT'
        result2 = checker.check(OperationType.MODIFY_BUSINESS_CODE, 'S1', 'orchestrator')
        out2 = fmt.format_result(result2)
        assert out2.event_type == 'BYPASS_DETECTED'
        assert out2.log_level == 'ERROR'

    def test_no_bypass_when_detection_disabled(self):
        fmt = InterceptorFormatter(session_id='sess-nobypass', enable_color=False, enable_bypass_detection=False)
        checker = BoundaryChecker()
        result1 = checker.check(OperationType.WRITE_CODE, 'S1', 'orchestrator')
        fmt.format_result(result1)
        result2 = checker.check(OperationType.MODIFY_BUSINESS_CODE, 'S1', 'orchestrator')
        out2 = fmt.format_result(result2)
        assert out2.event_type == 'INTERCEPT'
