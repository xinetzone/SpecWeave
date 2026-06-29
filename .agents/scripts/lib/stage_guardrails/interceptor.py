#!/usr/bin/env python3
"""拦截输出格式化器。

负责将边界校验结果转换为：
1. 标准SG-LOG结构化日志行（供日志文件落盘）
2. 面向用户的拦截警告消息（含终端彩色输出）
3. 绕过行为检测（BYPASS_DETECTED）

严格遵循[stage-guardrails.md]中定义的日志格式和拦截输出规范。
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from lib.stage_guardrails.boundary import BoundaryResult, OperationType, STAGE_NAMES
from lib.stage_guardrails.state import STAGE_ORDER


class BypassDetector:
    """绕过行为检测器。

    跟踪已拦截的操作，在后续操作中检测疑似绕过行为。

    绕过场景：
    1. INTERCEPT后短时间内执行了同类操作（未走审批流程）
    2. 通过替代操作类型执行被禁止的行为（如用Write直接写代码绕过WRITE_CODE检查）
    3. 未进入阶段直接执行阶段专属操作
    """

    def __init__(self):
        self._intercepted_ops: list[dict] = []
        self._max_history = 50

    def record_intercept(self, result: BoundaryResult):
        self._intercepted_ops.append({
            'timestamp': datetime.now(timezone.utc).timestamp(),
            'operation': result.operation,
            'stage': result.current_stage,
            'role': result.current_role,
            'violation_type': result.violation_type,
        })
        if len(self._intercepted_ops) > self._max_history:
            self._intercepted_ops = self._intercepted_ops[-self._max_history:]

    def check_bypass(self, operation: OperationType, current_stage: Optional[str],
                     current_role: str, detail: str = '') -> Optional[dict]:
        """检测当前操作是否疑似绕过之前的拦截。

        Returns:
            检测结果字典，或None表示无绕过
        """
        now = datetime.now(timezone.utc).timestamp()
        recent_window = 300

        for record in reversed(self._intercepted_ops):
            if now - record['timestamp'] > recent_window:
                break

            if record['operation'] == operation and record['stage'] == current_stage:
                return {
                    'detection_reason': f'拦截后重复执行同类操作: {operation.value}',
                    'evidence': f'操作{operation.value}在{current_stage}阶段已被拦截但再次尝试执行',
                    'original_violation': record['violation_type'],
                }

            if self._is_equivalent_bypass(record['operation'], operation):
                return {
                    'detection_reason': f'疑似通过替代操作绕过拦截: {record["operation"].value} -> {operation.value}',
                    'evidence': f'原操作{record["operation"].value}被拦截，改用{operation.value}执行同类行为',
                    'original_violation': record['violation_type'],
                }

        return None

    @staticmethod
    def _is_equivalent_bypass(original: OperationType, current: OperationType) -> bool:
        equivalents = {
            OperationType.WRITE_CODE: {OperationType.MODIFY_BUSINESS_CODE, OperationType.FIX_BUG},
            OperationType.MODIFY_BUSINESS_CODE: {OperationType.WRITE_CODE, OperationType.FIX_BUG},
            OperationType.FIX_BUG: {OperationType.WRITE_CODE, OperationType.MODIFY_BUSINESS_CODE},
            OperationType.CHOOSE_TECH_STACK: {OperationType.MODIFY_ARCHITECTURE, OperationType.CHANGE_TECH_SELECTION},
            OperationType.MODIFY_ARCHITECTURE: {OperationType.CHOOSE_TECH_STACK, OperationType.CHANGE_TECH_SELECTION},
            OperationType.CHANGE_TECH_SELECTION: {OperationType.CHOOSE_TECH_STACK, OperationType.MODIFY_ARCHITECTURE},
            OperationType.FORCE_MERGE: {OperationType.SKIP_CI_CHECK, OperationType.IGNORE_CONFLICT},
            OperationType.SKIP_CI_CHECK: {OperationType.FORCE_MERGE, OperationType.IGNORE_CONFLICT},
            OperationType.MARK_INCOMPLETE_COMPLETE: {OperationType.SKIP_REGRESSION, OperationType.CLOSE_WITHOUT_NOTIFICATION},
        }
        return current in equivalents.get(original, set())

    def clear(self):
        self._intercepted_ops.clear()


@dataclass
class FormattedOutput:
    """格式化输出结果。"""
    user_message: str = ''
    sg_log_line: str = ''
    is_intercept: bool = False
    log_level: str = 'DEBUG'
    event_type: str = ''

    def __str__(self):
        parts = []
        if self.user_message:
            parts.append(self.user_message)
        if self.sg_log_line:
            parts.append(self.sg_log_line)
        return '\n'.join(parts)


class InterceptorFormatter:
    """拦截输出格式化器。

    将BoundaryResult转换为标准的[SG-LOG]日志行和面向用户的拦截消息。

    用法:
        fmt = InterceptorFormatter(session_id='task-20260629-auth')
        result = checker.check(OperationType.WRITE_CODE, 'S1', 'orchestrator', '编写Redis代码')
        output = fmt.format_result(result, detail='编写Redis配置代码')
        print(output.user_message)  # ⚠️ 拦截消息
        print(output.sg_log_line)   # [SG-LOG] | level=WARN | event=INTERCEPT | ...
    """

    SG_LOG_PREFIX = '[SG-LOG]'
    FIELD_SEP = ' | '

    LEVEL_SYMBOLS = {
        'DEBUG': '🔍',
        'INFO': 'ℹ️',
        'WARN': '⚠️',
        'ERROR': '❌',
    }

    ANSI_COLORS = {
        'reset': '\033[0m',
        'red': '\033[91m',
        'yellow': '\033[93m',
        'green': '\033[92m',
        'cyan': '\033[96m',
        'bold': '\033[1m',
        'dim': '\033[2m',
    }

    def __init__(self, session_id: str, enable_color: bool = False,
                 enable_bypass_detection: bool = True):
        self.session_id = session_id
        self.enable_color = enable_color
        self.bypass_detector = BypassDetector() if enable_bypass_detection else None

    def format_sg_log(self, level: str, event: str, stage: str, role: str,
                      msg: str, ctx: Optional[dict] = None) -> str:
        """生成标准[SG-LOG]日志行。

        格式: [SG-LOG] | level=<LEVEL> | event=<EVENT> | stage=<STAGE> | role=<ROLE>
              | session=<SESSION> | msg=<MSG> | ctx=<JSON>

        ctx为None时省略ctx字段。JSON压缩为单行，无换行。
        """
        fields = [
            self.SG_LOG_PREFIX,
            f'level={level}',
            f'event={event}',
            f'stage={stage}',
            f'role={role}',
            f'session={self.session_id}',
            f'msg={msg}',
        ]
        if ctx:
            ctx_json = json.dumps(ctx, ensure_ascii=False, separators=(',', ':'))
            fields.append(f'ctx={ctx_json}')
        return self.FIELD_SEP.join(fields)

    def format_boundary_check(self, operation: OperationType, stage: str, role: str,
                              detail: str = '', allowed_ops: Optional[list[str]] = None) -> str:
        """生成BOUNDARY_CHECK日志（DEBUG级别）。"""
        op_desc = detail or operation.value
        ctx = {'operation': operation.value}
        if allowed_ops:
            ctx['allowed_ops'] = allowed_ops
        return self.format_sg_log(
            level='DEBUG',
            event='BOUNDARY_CHECK',
            stage=stage,
            role=role,
            msg=f'校验操作合法性: {op_desc}',
            ctx=ctx,
        )

    def format_boundary_pass(self, operation: OperationType, stage: str, role: str,
                             detail: str = '') -> str:
        """生成BOUNDARY_PASS日志（DEBUG级别）。"""
        op_desc = detail or operation.value
        return self.format_sg_log(
            level='DEBUG',
            event='BOUNDARY_PASS',
            stage=stage,
            role=role,
            msg=f'操作通过边界检查: {op_desc}',
            ctx={'operation': operation.value},
        )

    def format_intercept(self, result: BoundaryResult, detail: str = '') -> FormattedOutput:
        """生成拦截输出（用户消息 + INTERCEPT日志）。

        Returns:
            FormattedOutput 包含面向用户的拦截消息和SG-LOG日志行
        """
        stage = result.current_stage
        role = result.current_role
        op = result.operation
        base_desc = result.deny_reason or result.message or op.value
        op_desc = f'{detail}（{base_desc}）' if detail else base_desc
        target = result.target_stage or ''

        user_msg = self._build_intercept_user_message(result, op_desc)

        log_ctx = result.to_log_dict(self.session_id)
        if detail:
            log_ctx['detail'] = detail
        sg_log = self.format_sg_log(
            level='WARN',
            event='INTERCEPT',
            stage=stage if stage != 'NONE' else 'NONE',
            role=role,
            msg=f'阶段守卫拦截: {op_desc}',
            ctx=log_ctx,
        )

        if self.bypass_detector:
            self.bypass_detector.record_intercept(result)

        return FormattedOutput(
            user_message=user_msg,
            sg_log_line=sg_log,
            is_intercept=True,
            log_level='WARN',
            event_type='INTERCEPT',
        )

    def format_bypass_detected(self, operation: OperationType, stage: str, role: str,
                               detection_result: dict) -> FormattedOutput:
        """生成BYPASS_DETECTED输出（ERROR级别）。"""
        reason = detection_result.get('detection_reason', '疑似绕过阶段守卫')
        evidence = detection_result.get('evidence', '')

        user_msg = self._colorize(
            f'{self.LEVEL_SYMBOLS["ERROR"]} 检测到疑似绕过阶段守卫行为！\n'
            f'原因: {reason}\n'
            f'证据: {evidence}\n'
            f'此操作已被记录为ERROR级别事件，请立即停止并通过正规审批流程处理。',
            'red', bold=True,
        )

        sg_log = self.format_sg_log(
            level='ERROR',
            event='BYPASS_DETECTED',
            stage=stage if stage else 'NONE',
            role=role,
            msg=f'疑似绕过阶段守卫: {reason}',
            ctx=detection_result,
        )

        return FormattedOutput(
            user_message=user_msg,
            sg_log_line=sg_log,
            is_intercept=True,
            log_level='ERROR',
            event_type='BYPASS_DETECTED',
        )

    def format_error(self, stage: str, role: str, error_type: str,
                     error_detail: str, impact: str = '', recovery_hint: str = '') -> FormattedOutput:
        """生成ERROR级别事件输出。"""
        msg = error_detail
        ctx = {
            'error_type': error_type,
            'error_detail': error_detail,
        }
        if impact:
            ctx['impact'] = impact
        if recovery_hint:
            ctx['recovery_hint'] = recovery_hint

        user_msg = self._colorize(
            f'{self.LEVEL_SYMBOLS["ERROR"]} 阶段守卫错误: {error_detail}',
            'red', bold=True,
        )
        if impact:
            user_msg += f'\n影响范围: {impact}'
        if recovery_hint:
            user_msg += f'\n建议恢复: {recovery_hint}'

        sg_log = self.format_sg_log(
            level='ERROR',
            event='ERROR',
            stage=stage if stage else 'NONE',
            role=role,
            msg=msg,
            ctx=ctx,
        )

        return FormattedOutput(
            user_message=user_msg,
            sg_log_line=sg_log,
            is_intercept=True,
            log_level='ERROR',
            event_type='ERROR',
        )

    def format_result(self, result: BoundaryResult, detail: str = '') -> FormattedOutput:
        """格式化BoundaryResult，自动选择正确的输出类型。

        - 不允许 → INTERCEPT拦截输出
        - 允许 → BOUNDARY_PASS日志（用户消息为空）
        - 同时检测绕过行为
        """
        if not result.allowed:
            if self.bypass_detector:
                bypass = self.bypass_detector.check_bypass(
                    result.operation, result.current_stage,
                    result.current_role, detail,
                )
                if bypass:
                    return self.format_bypass_detected(
                        result.operation, result.current_stage,
                        result.current_role, bypass,
                    )
            return self.format_intercept(result, detail)

        sg_log = self.format_boundary_pass(
            result.operation, result.current_stage,
            result.current_role, detail or result.message,
        )
        return FormattedOutput(
            user_message='',
            sg_log_line=sg_log,
            is_intercept=False,
            log_level='DEBUG',
            event_type='BOUNDARY_PASS',
        )

    def _build_intercept_user_message(self, result: BoundaryResult, op_desc: str) -> str:
        stage = result.current_stage
        stage_name = STAGE_NAMES.get(stage, stage) if stage != 'NONE' else '无活跃阶段'
        lines = []

        symbol = self.LEVEL_SYMBOLS.get('WARN', '⚠️')

        if stage == 'NONE':
            header = f'{symbol} 阶段守卫拦截：当前未进入任何开发阶段，无法执行【{op_desc}】。'
        else:
            header = (
                f'{symbol} 阶段守卫拦截：当前为【{stage}{stage_name}】阶段，'
                f'【{op_desc}】。'
            )
        lines.append(self._colorize(header, 'yellow', bold=True))

        if stage != 'NONE' and result.exit_criteria_hint:
            lines.append(f'请先完成当前阶段：{result.exit_criteria_hint}')

        if result.suggested_action:
            lines.append(result.suggested_action)
        elif result.violation_type == 'NO_ACTIVE_STAGE':
            lines.append('请先进入S1需求接收阶段开始任务。')
        elif result.target_stage:
            target_name = STAGE_NAMES.get(result.target_stage, result.target_stage)
            curr_order = STAGE_ORDER.get(stage, 0) if stage != 'NONE' else 0
            target_order = STAGE_ORDER.get(result.target_stage, 0)
            if target_order > curr_order + 1:
                lines.append(
                    f'如需跳至{result.target_stage}（{target_name}）阶段，'
                    f'请提交正向跳过申请并经orchestrator批准。'
                )
            elif target_order < curr_order:
                lines.append(
                    f'如需回退至{result.target_stage}（{target_name}）阶段，'
                    f'请提交逆向回退申请并经orchestrator+reviewer联合审批。'
                )
            else:
                lines.append('请先完成当前阶段并退出后再进入下一阶段。')
        else:
            lines.append('如需跳过或回退阶段，请提交阶段跳转申请并经orchestrator批准。')

        return '\n'.join(lines)

    def _colorize(self, text: str, color: str = '', bold: bool = False, dim: bool = False) -> str:
        if not self.enable_color:
            return text
        prefix = ''
        if bold:
            prefix += self.ANSI_COLORS['bold']
        if dim:
            prefix += self.ANSI_COLORS['dim']
        if color:
            prefix += self.ANSI_COLORS.get(color, '')
        suffix = self.ANSI_COLORS['reset']
        return f'{prefix}{text}{suffix}'

    @staticmethod
    def parse_sg_log(line: str) -> Optional[dict]:
        """解析SG-LOG日志行为字典（反向解析，用于日志分析）。

        Returns:
            解析后的字段字典，或None表示格式不匹配
        """
        if not line.startswith(InterceptorFormatter.SG_LOG_PREFIX):
            return None
        line = line.strip()
        parts = line.split(' | ')
        if not parts or parts[0] != InterceptorFormatter.SG_LOG_PREFIX:
            return None

        result = {}
        for part in parts[1:]:
            if '=' in part:
                key, _, value = part.partition('=')
                key = key.strip()
                value = value.strip()
                if key == 'ctx':
                    try:
                        result[key] = json.loads(value)
                    except json.JSONDecodeError:
                        result[key] = value
                else:
                    result[key] = value
        return result
