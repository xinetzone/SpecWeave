#!/usr/bin/env python3
"""阶段守卫运行时集成门面（GuardrailRuntime）。

将 StageStateManager、BoundaryChecker、InterceptorFormatter 三个核心组件
串联为统一的运行时拦截入口，提供：

1. 统一的生命周期管理：enter_stage / exit_stage / request_jump / approve_jump
2. 核心拦截入口 guard_operation()：操作前检查 + 自动格式化 + 日志收集
3. 全链路 SG-LOG 自动采集：所有状态转换和拦截事件均落盘到内存日志列表
4. 状态查询与异常处理：封装TransitionError为FormattedOutput

典型用法::

    runtime = GuardrailRuntime(session_id='task-auth-001')
    runtime.enter_stage('S1', 'orchestrator', '收到用户需求：实现登录功能')

    out = runtime.guard_operation(OperationType.WRITE_CODE, 'orchestrator',
                                   detail='直接开始写登录代码')
    if out.is_intercept:
        print(out.user_message)  # ⚠️ 阶段守卫拦截：当前为【S1需求接收】阶段...
        # 终止操作，引导先走需求流程
    else:
        # 操作被允许，继续执行
        ...

    runtime.mark_doc_check(required_docs=['spec.md', 'standards.md'])
    runtime.mark_pdr_done()
    runtime.exit_stage('S1', 'orchestrator', '需求澄清完成',
                       exit_criteria_met=['需求已澄清', '任务已分解'],
                       output_artifacts=['任务分解清单', '需求文档'],
                       next_stage='S2')
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from lib.stage_guardrails.state import (
    StageStateManager,
    TransitionError,
    JumpRecord,
    StageStatus,
    STAGE_NAMES,
    STAGE_ORDER,
    VALID_ROLES,
)
from lib.stage_guardrails.boundary import (
    BoundaryChecker,
    BoundaryResult,
    OperationType,
)
from lib.stage_guardrails.interceptor import (
    InterceptorFormatter,
    BypassDetector,
    FormattedOutput,
)


@dataclass
class RuntimeStatus:
    """运行时状态快照。"""
    session_id: str
    is_active: bool
    current_stage: Optional[str]
    current_stage_name: Optional[str]
    current_role: Optional[str]
    completed_stages: list[str]
    pending_jump: Optional[dict]
    interception_count: int
    bypass_count: int
    log_line_count: int


class GuardrailRuntime:
    """阶段守卫运行时门面。

    封装状态管理、边界校验、输出格式化三组件，提供一站式
    工具调用拦截与阶段生命周期管理能力。
    """

    def __init__(self, session_id: str, *,
                 enable_color: bool = False,
                 enable_bypass_detection: bool = True,
                 strict_mode: bool = False):
        self.session_id = session_id
        self.strict_mode = strict_mode
        self._state = StageStateManager(session_id=session_id)
        self._checker = BoundaryChecker()
        self._formatter = InterceptorFormatter(
            session_id=session_id,
            enable_color=enable_color,
            enable_bypass_detection=enable_bypass_detection,
        )
        self._log_lines: list[str] = []
        self._interception_count = 0
        self._bypass_count = 0
        self._start_time = time.time()

    @property
    def state(self) -> StageStateManager:
        return self._state

    @property
    def checker(self) -> BoundaryChecker:
        return self._checker

    @property
    def formatter(self) -> InterceptorFormatter:
        return self._formatter

    @property
    def current_stage(self) -> Optional[str]:
        return self._state.current_stage

    @property
    def current_stage_name(self) -> Optional[str]:
        return self._state.current_stage_name

    @property
    def current_role(self) -> Optional[str]:
        return self._state.current_role

    @property
    def is_active(self) -> bool:
        return self._state.is_active

    @property
    def log_lines(self) -> list[str]:
        return list(self._log_lines)

    @property
    def interception_count(self) -> int:
        return self._interception_count

    @property
    def bypass_count(self) -> int:
        return self._bypass_count

    def guard_operation(self, operation: OperationType, role: str,
                        detail: str = '') -> FormattedOutput:
        """操作前拦截检查（核心入口）。

        执行流程：
        1. 通过 BoundaryChecker 校验当前阶段/角色是否允许该操作
        2. 通过 BypassDetector 检测是否绕过之前的拦截
        3. 通过 InterceptorFormatter 生成用户消息和 SG-LOG
        4. 自动将日志行追加到内存日志列表
        5. 统计拦截/绕过计数

        Args:
            operation: 操作类型
            role: 执行角色
            detail: 操作描述（用户可读的具体行为）

        Returns:
            FormattedOutput 包含 is_intercept 标志、用户消息、SG-LOG行
        """
        boundary_log = self._formatter.format_boundary_check(
            operation, self._state.current_stage, role, detail=detail,
        )
        self._append_log(boundary_log)

        result = self._checker.check(
            operation=operation,
            current_stage=self._state.current_stage,
            current_role=role,
            detail=detail,
        )

        if not result.allowed:
            if self._formatter.bypass_detector is not None:
                bypass_info = self._formatter.bypass_detector.check_bypass(
                    operation, self._state.current_stage, role, detail=detail,
                )
                if bypass_info is not None:
                    out = self._formatter.format_bypass_detected(
                        operation, self._state.current_stage, role, bypass_info,
                    )
                    self._append_log(out.sg_log_line)
                    self._bypass_count += 1
                    self._interception_count += 1
                    return out

            out = self._formatter.format_intercept(result, detail=detail)
            self._append_log(out.sg_log_line)
            self._interception_count += 1
            return out

        pass_log = self._formatter.format_boundary_pass(
            operation, self._state.current_stage, role, detail=detail,
        )
        self._append_log(pass_log)
        return FormattedOutput(
            user_message='',
            sg_log_line=pass_log,
            is_intercept=False,
            log_level='DEBUG',
            event_type='BOUNDARY_PASS',
        )

    def enter_stage(self, stage: str, role: str, message: str,
                    ctx: Optional[dict] = None) -> FormattedOutput:
        """进入阶段（封装状态管理器异常为FormattedOutput）。

        Returns:
            FormattedOutput 成功时 sg_log_line 包含 STAGE_ENTER 日志；
            失败时 is_intercept=True，user_message 含错误描述。
        """
        try:
            self._state.enter_stage(stage, role, message, ctx=ctx)
            sg_log = self._formatter.format_sg_log(
                level='INFO',
                event='STAGE_ENTER',
                stage=stage,
                role=role,
                msg=message,
                ctx={'prev_stage': ctx.get('prev_stage') if ctx else None,
                     'via_jump': ctx.get('via_jump', False) if ctx else False},
            )
            self._append_log(sg_log)
            return FormattedOutput(
                user_message='',
                sg_log_line=sg_log,
                is_intercept=False,
                log_level='INFO',
                event_type='STAGE_ENTER',
            )
        except TransitionError as e:
            return self._format_transition_error(e, stage=stage, role=role)

    def exit_stage(self, stage: str, role: str, message: str,
                   exit_criteria_met: Optional[list[str]] = None,
                   output_artifacts: Optional[list[str]] = None,
                   next_stage: Optional[str] = None,
                   ctx: Optional[dict] = None) -> FormattedOutput:
        """退出当前阶段。"""
        try:
            record = self._state.exit_stage(
                stage, role, message,
                exit_criteria_met=exit_criteria_met,
                output_artifacts=output_artifacts,
                next_stage=next_stage,
                ctx=ctx,
            )
            sg_log = self._formatter.format_sg_log(
                level='INFO',
                event='STAGE_EXIT',
                stage=stage,
                role=role,
                msg=message,
                ctx={
                    'exit_criteria_met': exit_criteria_met or [],
                    'output_artifacts': output_artifacts or [],
                    'next_stage': next_stage,
                    'duration': round(record.exited_at - record.entered_at, 2)
                    if record.exited_at and record.entered_at else None,
                },
            )
            self._append_log(sg_log)
            return FormattedOutput(
                user_message='',
                sg_log_line=sg_log,
                is_intercept=False,
                log_level='INFO',
                event_type='STAGE_EXIT',
            )
        except TransitionError as e:
            return self._format_transition_error(e, stage=stage, role=role)

    def mark_doc_check(self, required_docs: list[str]) -> FormattedOutput:
        """标记前置文档检查完成。"""
        try:
            self._state.mark_doc_check(required_docs)
            sg_log = self._formatter.format_sg_log(
                level='INFO',
                event='DOC_CHECK',
                stage=self._state.current_stage or 'NONE',
                role=self._state.current_role or '',
                msg=f'前置文档检查完成：共{len(required_docs)}份必读文档',
                ctx={'required_docs': required_docs},
            )
            self._append_log(sg_log)
            return FormattedOutput(
                user_message='',
                sg_log_line=sg_log,
                is_intercept=False,
                log_level='INFO',
                event_type='DOC_CHECK',
            )
        except TransitionError as e:
            return self._format_transition_error(e)

    def mark_pdr_done(self) -> FormattedOutput:
        """标记PDR前置文档读取流程完成。"""
        try:
            self._state.mark_pdr_done()
            sg_log = self._formatter.format_sg_log(
                level='INFO',
                event='PDR_CONFIRM',
                stage=self._state.current_stage or 'NONE',
                role=self._state.current_role or '',
                msg='前置文档读取流程完成',
            )
            self._append_log(sg_log)
            return FormattedOutput(
                user_message='',
                sg_log_line=sg_log,
                is_intercept=False,
                log_level='INFO',
                event_type='PDR_CONFIRM',
            )
        except TransitionError as e:
            return self._format_transition_error(e)

    def request_jump(self, jump_type: str, to_stage: str, requested_by: str,
                     reason: str) -> tuple[Optional[JumpRecord], FormattedOutput]:
        """提交阶段跳转申请。

        Returns:
            (JumpRecord, FormattedOutput) 成功时返回跳转记录和日志；
            失败时返回 (None, 错误输出)。
        """
        try:
            record = self._state.request_jump(jump_type, to_stage, requested_by, reason)
            sg_log = self._formatter.format_sg_log(
                level='INFO',
                event='JUMP_REQUEST',
                stage=self._state.current_stage or 'NONE',
                role=requested_by,
                msg=f'申请{jump_type}跳转: {record.from_stage}→{to_stage}',
                ctx={
                    'jump_id': record.jump_id,
                    'jump_type': jump_type,
                    'from_stage': record.from_stage,
                    'to_stage': to_stage,
                    'reason': reason,
                },
            )
            self._append_log(sg_log)
            return record, FormattedOutput(
                user_message='',
                sg_log_line=sg_log,
                is_intercept=False,
                log_level='INFO',
                event_type='JUMP_REQUEST',
            )
        except TransitionError as e:
            return None, self._format_transition_error(e, to_stage=to_stage, role=requested_by)

    def approve_jump(self, jump_id: str, approved_by: str,
                     rollback_scope: Optional[str] = None,
                     conditions: Optional[str] = None) -> FormattedOutput:
        """批准阶段跳转（rollback会自动进入目标阶段）。"""
        try:
            record = self._state.approve_jump(jump_id, approved_by,
                                              rollback_scope=rollback_scope,
                                              conditions=conditions)
            sg_log = self._formatter.format_sg_log(
                level='INFO',
                event='JUMP_APPROVED',
                stage=record.from_stage,
                role=approved_by,
                msg=f'跳转已批准: {record.from_stage}→{record.to_stage}（{record.jump_type}）',
                ctx={
                    'jump_id': jump_id,
                    'jump_type': record.jump_type,
                    'approved_by': approved_by,
                    'rollback_scope': rollback_scope,
                    'conditions': conditions,
                },
            )
            self._append_log(sg_log)

            if record.jump_type == 'rollback' and self._state.current_stage == record.to_stage:
                enter_log = self._formatter.format_sg_log(
                    level='INFO',
                    event='STAGE_ENTER',
                    stage=record.to_stage,
                    role=self._state.current_role or '',
                    msg=f'通过逆向回退进入{record.to_stage}',
                    ctx={'jump_id': jump_id, 'via_jump': True},
                )
                self._append_log(enter_log)

            return FormattedOutput(
                user_message='',
                sg_log_line=sg_log,
                is_intercept=False,
                log_level='INFO',
                event_type='JUMP_APPROVED',
            )
        except TransitionError as e:
            return self._format_transition_error(e, role=approved_by)

    def reject_jump(self, jump_id: str, rejected_by: str, reject_reason: str) -> FormattedOutput:
        """拒绝阶段跳转。"""
        try:
            record = self._state.reject_jump(jump_id, rejected_by, reject_reason)
            sg_log = self._formatter.format_sg_log(
                level='WARN',
                event='JUMP_REJECTED',
                stage=record.from_stage,
                role=rejected_by,
                msg=f'跳转被拒绝: {record.from_stage}→{record.to_stage}，原因: {reject_reason}',
                ctx={
                    'jump_id': jump_id,
                    'rejected_by': rejected_by,
                    'reject_reason': reject_reason,
                },
            )
            self._append_log(sg_log)
            return FormattedOutput(
                user_message='',
                sg_log_line=sg_log,
                is_intercept=False,
                log_level='WARN',
                event_type='JUMP_REJECTED',
            )
        except TransitionError as e:
            return self._format_transition_error(e, role=rejected_by)

    def execute_skip(self, jump_id: str, role: str, message: str = '',
                     ctx: Optional[dict] = None) -> FormattedOutput:
        """执行已批准的正向跳过（进入目标阶段）。"""
        try:
            self._state.execute_skip(jump_id, role, message, ctx=ctx)
            target_stage = self._state.current_stage
            sg_log = self._formatter.format_sg_log(
                level='INFO',
                event='STAGE_ENTER',
                stage=target_stage or 'NONE',
                role=self._state.current_role or role,
                msg=message or f'通过正向跳过进入{target_stage}',
                ctx={'jump_id': jump_id, 'via_jump': True, 'jump_type': 'skip'},
            )
            self._append_log(sg_log)
            return FormattedOutput(
                user_message='',
                sg_log_line=sg_log,
                is_intercept=False,
                log_level='INFO',
                event_type='STAGE_ENTER',
            )
        except TransitionError as e:
            return self._format_transition_error(e, role=role)

    def advance_to_next_stage(self, role: str, exit_message: str,
                              enter_message: str = '',
                              exit_criteria_met: Optional[list[str]] = None,
                              output_artifacts: Optional[list[str]] = None,
                              enter_ctx: Optional[dict] = None) -> FormattedOutput:
        """顺序推进到下一阶段（退出当前 + 进入下一阶段的便捷方法）。

        Raises:
            RuntimeError: 当前无活跃阶段无法推进
        """
        current = self._state.current_stage
        if current is None:
            return self._format_transition_error(
                TransitionError(
                    code='NO_ACTIVE_STAGE',
                    message='无活跃阶段，无法顺序推进。请先enter_stage进入S1。',
                ),
                role=role,
            )

        next_order = STAGE_ORDER[current] + 1
        next_stage_candidates = [s for s, o in STAGE_ORDER.items() if o == next_order]
        if not next_stage_candidates:
            return FormattedOutput(
                user_message=f'⚠️ 当前处于{current}（{STAGE_NAMES[current]}）阶段，已是最终阶段。',
                sg_log_line='',
                is_intercept=True,
                log_level='WARN',
                event_type='STAGE_BOUNDARY',
            )

        next_stage = next_stage_candidates[0]
        next_role = next(iter(self._get_stage_role(next_stage)), role)

        exit_out = self.exit_stage(
            current, role, exit_message,
            exit_criteria_met=exit_criteria_met,
            output_artifacts=output_artifacts,
            next_stage=next_stage,
        )
        if exit_out.is_intercept:
            return exit_out

        enter_out = self.enter_stage(
            next_stage, next_role,
            enter_message or f'进入{next_stage}（{STAGE_NAMES[next_stage]}）阶段',
            ctx=enter_ctx,
        )
        return enter_out

    def can_transition_to(self, target_stage: str) -> tuple[bool, str]:
        """查询是否可以转换到目标阶段。"""
        return self._state.can_transition_to(target_stage)

    def get_status(self) -> RuntimeStatus:
        """获取运行时状态快照。"""
        state_dict = self._state.to_dict()
        return RuntimeStatus(
            session_id=self.session_id,
            is_active=state_dict['is_active'],
            current_stage=state_dict['current_stage'],
            current_stage_name=state_dict['current_stage_name'],
            current_role=state_dict['current_role'],
            completed_stages=state_dict['completed_stages'],
            pending_jump=state_dict['pending_jump'],
            interception_count=self._interception_count,
            bypass_count=self._bypass_count,
            log_line_count=len(self._log_lines),
        )

    def get_logs_since(self, event_type: Optional[str] = None,
                       level: Optional[str] = None) -> list[str]:
        """按事件类型或日志级别过滤日志。"""
        result = []
        for line in self._log_lines:
            parsed = InterceptorFormatter.parse_sg_log(line)
            if parsed is None:
                continue
            if event_type and parsed.get('event') != event_type:
                continue
            if level and parsed.get('level') != level:
                continue
            result.append(line)
        return result

    def dump_logs(self) -> str:
        """将所有日志行导出为单个字符串（换行分隔）。"""
        return '\n'.join(self._log_lines)

    def clear_logs(self):
        """清空内存日志列表。"""
        self._log_lines.clear()

    def reset(self):
        """重置运行时状态（清空状态、日志、计数）。"""
        self._state = StageStateManager(session_id=self.session_id)
        if self._formatter.bypass_detector is not None:
            self._formatter.bypass_detector.clear()
        self._log_lines.clear()
        self._interception_count = 0
        self._bypass_count = 0

    def _append_log(self, line: str):
        if line:
            self._log_lines.append(line)

    def _format_transition_error(self, error: TransitionError,
                                 stage: Optional[str] = None,
                                 role: Optional[str] = None,
                                 to_stage: Optional[str] = None) -> FormattedOutput:
        """将TransitionError转换为FormattedOutput。"""
        error_type = type(error).__name__
        impact_map = {
            'DuplicateEntryError': '可能导致阶段状态混乱，跳过必要的退出标准检查',
            'ExitWithoutEntryError': '无对应进入记录，无法验证阶段完成度',
            'StageMismatchError': '退出阶段与活跃阶段不一致，状态机可能已损坏',
            'InvalidStageError': '阶段ID无效，无法进行状态转换',
            'InvalidRoleError': '角色无权执行该操作，违反角色职责边界',
            'UnauthorizedJumpError': '未经审批的跳转将绕过阶段守卫强制执行层',
            'InvalidJumpError': '非法跳转目标，可能导致流程短路',
        }
        recovery_map = {
            'DuplicateEntryError': '先退出当前阶段或提交JUMP_REQUEST获得审批',
            'ExitWithoutEntryError': '先通过enter_stage进入对应阶段',
            'StageMismatchError': '确认当前活跃阶段后再执行退出',
            'InvalidStageError': f'使用有效阶段ID: {list(STAGE_ORDER.keys())}',
            'InvalidRoleError': f'使用对应阶段的负责角色: orchestrator/architect/developer/tester/reviewer',
            'UnauthorizedJumpError': '提交JUMP_REQUEST并由orchestrator审批后再执行',
            'InvalidJumpError': '检查跳转类型（skip/rollback）和目标阶段是否合法',
        }

        impact = impact_map.get(error_type, '状态转换失败，可能影响流程合规性')
        recovery = recovery_map.get(error_type, '检查参数后重试')

        out = self._formatter.format_error(
            stage=stage or self._state.current_stage or 'NONE',
            role=role or self._state.current_role or '',
            error_type=error.code,
            error_detail=error.message,
            impact=impact,
            recovery_hint=recovery,
        )
        self._append_log(out.sg_log_line)
        return out

    @staticmethod
    def _get_stage_role(stage: str) -> set[str]:
        from lib.stage_guardrails.state import STAGE_ROLES
        return STAGE_ROLES.get(stage, set())
