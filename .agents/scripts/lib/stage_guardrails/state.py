#!/usr/bin/env python3
"""阶段状态管理器。

维护开发会话的阶段状态机，提供：
- 阶段进入/退出（STAGE_ENTER / STAGE_EXIT）
- 阶段跳转审批记录（JUMP_REQUEST / JUMP_APPROVED / JUMP_REJECTED）
- 状态合法性校验（重复进入、未进入就退出、非法阶段ID等）
- 状态查询API（当前阶段、历史轨迹、审批记录）

与离线检查工具 check-stage-guardrails.py 的关系：
- 离线工具做事后日志分析（日志→异常报告）
- 状态管理器做运行时实时校验（状态转换→拒绝非法操作）
- 两者共用 STAGE_ORDER / STAGE_NAMES 常量
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


STAGE_ORDER: dict[str, int] = {
    'S1': 1, 'S2': 2, 'S3': 3, 'S4': 4,
    'S5': 5, 'S6': 6, 'S7': 7, 'S8': 8,
}

STAGE_NAMES: dict[str, str] = {
    'S1': '需求接收', 'S2': '方案设计', 'S3': '任务分配', 'S4': '代码实现',
    'S5': '测试编写', 'S6': '代码审查', 'S7': '合并代码', 'S8': '完成确认',
}

VALID_ROLES: set[str] = {'orchestrator', 'architect', 'developer', 'tester', 'reviewer'}

STAGE_ROLES: dict[str, set[str]] = {
    'S1': {'orchestrator'},
    'S2': {'architect'},
    'S3': {'orchestrator'},
    'S4': {'developer'},
    'S5': {'tester'},
    'S6': {'reviewer'},
    'S7': {'orchestrator'},
    'S8': {'orchestrator'},
}


class TransitionError(Exception):
    """阶段转换异常基类。"""
    def __init__(self, code: str, message: str, details: Optional[dict] = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class InvalidStageError(TransitionError):
    """无效阶段ID。"""
    pass


class InvalidRoleError(TransitionError):
    """角色无权操作当前阶段。"""
    pass


class DuplicateEntryError(TransitionError):
    """重复进入同一阶段而未退出。"""
    pass


class ExitWithoutEntryError(TransitionError):
    """未进入阶段就尝试退出。"""
    pass


class StageMismatchError(TransitionError):
    """退出的阶段与当前活跃阶段不一致。"""
    pass


class UnauthorizedJumpError(TransitionError):
    """未经审批的阶段跳转。"""
    pass


class InvalidJumpError(TransitionError):
    """非法跳转（如跳至完成确认之前跳过验证）。"""
    pass


class StageStatus(Enum):
    """阶段状态枚举。"""
    NOT_ENTERED = 'not_entered'
    ACTIVE = 'active'
    COMPLETED = 'completed'
    ROLLED_BACK = 'rolled_back'


@dataclass
class StageTransition:
    """阶段转换记录。"""
    timestamp: float
    event: str
    stage: str
    role: str
    message: str
    ctx: dict = field(default_factory=dict)
    from_stage: Optional[str] = None


@dataclass
class JumpRecord:
    """阶段跳转审批记录。"""
    timestamp: float
    jump_id: str
    jump_type: str
    from_stage: str
    to_stage: str
    requested_by: str
    reason: str
    approved_by: Optional[str] = None
    approved: bool = False
    reject_reason: Optional[str] = None
    rollback_scope: Optional[str] = None
    conditions: Optional[str] = None


@dataclass
class _StageRecord:
    """内部阶段状态记录。"""
    stage: str
    role: str
    entered_at: float
    exited_at: Optional[float] = None
    status: StageStatus = StageStatus.ACTIVE
    doc_check_done: bool = False
    pdr_done: bool = False
    exit_ctx: dict = field(default_factory=dict)


class StageStateManager:
    """阶段状态管理器。

    维护单个开发会话的阶段状态机，确保阶段转换合法。

    用法:
        mgr = StageStateManager(session_id='task-20260629-auth')
        mgr.enter_stage('S1', 'orchestrator', '收到用户需求')
        mgr.mark_doc_check(docs=['spec.md', 'standards.md'])
        mgr.mark_pdr_done()
        mgr.exit_stage('S1', 'orchestrator', exit_criteria_met=['需求已澄清'], output_artifacts=['任务分解清单'], next_stage='S2')
        mgr.enter_stage('S2', 'architect', '开始方案设计')
    """

    def __init__(self, session_id: str, start_time: Optional[float] = None):
        self.session_id = session_id
        self._start_time = start_time or time.time()
        self._current_stage: Optional[str] = None
        self._current_role: Optional[str] = None
        self._stage_records: list[_StageRecord] = []
        self._transitions: list[StageTransition] = []
        self._jump_records: list[JumpRecord] = []
        self._jump_counter: int = 0
        self._pending_jump: Optional[JumpRecord] = None

    @property
    def current_stage(self) -> Optional[str]:
        """当前活跃阶段ID，无活跃阶段返回None。"""
        return self._current_stage

    @property
    def current_stage_name(self) -> Optional[str]:
        """当前活跃阶段中文名。"""
        if self._current_stage:
            return STAGE_NAMES.get(self._current_stage, self._current_stage)
        return None

    @property
    def current_role(self) -> Optional[str]:
        """当前活跃角色。"""
        return self._current_role

    @property
    def is_active(self) -> bool:
        """是否有活跃阶段（处于某阶段中）。"""
        return self._current_stage is not None

    @property
    def transitions(self) -> list[StageTransition]:
        """所有阶段转换记录的只读副本。"""
        return list(self._transitions)

    @property
    def jump_records(self) -> list[JumpRecord]:
        """所有跳转审批记录的只读副本。"""
        return list(self._jump_records)

    @property
    def completed_stages(self) -> list[str]:
        """已完成的阶段列表（按顺序）。"""
        return [r.stage for r in self._stage_records if r.status == StageStatus.COMPLETED]

    def stage_status(self, stage: str) -> StageStatus:
        """查询指定阶段的当前状态。"""
        self._validate_stage_id(stage)
        for r in reversed(self._stage_records):
            if r.stage == stage:
                return r.status
        return StageStatus.NOT_ENTERED

    def get_stage_record(self, stage: str) -> Optional[_StageRecord]:
        """获取指定阶段的最近一条记录。"""
        for r in reversed(self._stage_records):
            if r.stage == stage:
                return r
        return None

    def _validate_stage_id(self, stage: str):
        if stage not in STAGE_ORDER:
            raise InvalidStageError(
                code='INVALID_STAGE',
                message=f'无效阶段ID: {stage}，有效阶段为 S1~S8',
                details={'stage': stage, 'valid_stages': list(STAGE_ORDER.keys())},
            )

    def _validate_role(self, role: str):
        if role not in VALID_ROLES:
            raise InvalidRoleError(
                code='INVALID_ROLE',
                message=f'无效角色: {role}，有效角色为 {sorted(VALID_ROLES)}',
                details={'role': role, 'valid_roles': sorted(VALID_ROLES)},
            )

    def _validate_stage_role(self, stage: str, role: str):
        self._validate_stage_id(stage)
        self._validate_role(role)
        allowed = STAGE_ROLES.get(stage, set())
        if allowed and role not in allowed:
            raise InvalidRoleError(
                code='ROLE_STAGE_MISMATCH',
                message=f'角色 {role} 无权执行 {stage}（{STAGE_NAMES[stage]}）阶段，该阶段负责角色为 {sorted(allowed)}',
                details={'stage': stage, 'role': role, 'allowed_roles': sorted(allowed)},
            )

    def _record_transition(self, event: str, stage: str, role: str, message: str,
                           ctx: Optional[dict] = None, from_stage: Optional[str] = None):
        self._transitions.append(StageTransition(
            timestamp=time.time(),
            event=event,
            stage=stage,
            role=role,
            message=message,
            ctx=ctx or {},
            from_stage=from_stage,
        ))

    def enter_stage(self, stage: str, role: str, message: str,
                    ctx: Optional[dict] = None, via_jump: bool = False):
        """进入一个阶段。

        Args:
            stage: 阶段ID (S1~S8)
            role: 执行角色
            message: 进入原因/描述
            ctx: 附加上下文
            via_jump: 是否通过审批跳转进入

        Raises:
            DuplicateEntryError: 当前已有活跃阶段且未通过跳转
            InvalidStageError: 无效阶段ID
            InvalidRoleError: 角色无权操作该阶段
        """
        self._validate_stage_role(stage, role)
        ctx = ctx or {}

        if self._current_stage is not None and not via_jump:
            raise DuplicateEntryError(
                code='DUPLICATE_ENTRY',
                message=f'重复进入阶段 {stage}（{STAGE_NAMES[stage]}），'
                        f'当前已在 {self._current_stage}（{STAGE_NAMES[self._current_stage]}）且未退出。'
                        f'如需跳转请先提交 JUMP_REQUEST 并获得审批。',
                details={
                    'current_stage': self._current_stage,
                    'target_stage': stage,
                },
            )

        prev_stage = self._current_stage
        self._current_stage = stage
        self._current_role = role
        self._stage_records.append(_StageRecord(
            stage=stage,
            role=role,
            entered_at=time.time(),
        ))

        entry_ctx = {**ctx}
        if via_jump:
            entry_ctx['via_jump'] = True
        if prev_stage:
            entry_ctx['prev_stage'] = prev_stage

        self._record_transition(
            event='STAGE_ENTER',
            stage=stage,
            role=role,
            message=message,
            ctx=entry_ctx,
            from_stage=prev_stage,
        )

    def exit_stage(self, stage: str, role: str, message: str,
                   exit_criteria_met: Optional[list[str]] = None,
                   output_artifacts: Optional[list[str]] = None,
                   next_stage: Optional[str] = None,
                   ctx: Optional[dict] = None) -> _StageRecord:
        """退出当前阶段。

        Args:
            stage: 阶段ID（必须与当前活跃阶段一致）
            role: 执行角色
            message: 退出描述
            exit_criteria_met: 满足的退出标准列表
            output_artifacts: 产出物清单
            next_stage: 下一阶段ID
            ctx: 附加上下文

        Returns:
            完成的阶段记录

        Raises:
            ExitWithoutEntryError: 无活跃阶段
            StageMismatchError: 退出的阶段与当前活跃阶段不一致
            InvalidRoleError: 角色无权操作
        """
        self._validate_role(role)
        self._validate_stage_id(stage)
        ctx = ctx or {}

        if self._current_stage is None:
            raise ExitWithoutEntryError(
                code='EXIT_WITHOUT_ENTRY',
                message=f'尝试退出阶段 {stage}（{STAGE_NAMES[stage]}）但当前无活跃阶段。',
                details={'target_stage': stage},
            )

        if self._current_stage != stage:
            raise StageMismatchError(
                code='STAGE_MISMATCH',
                message=f'退出阶段不匹配：尝试退出 {stage}（{STAGE_NAMES.get(stage, "?")}），'
                        f'当前活跃阶段为 {self._current_stage}（{STAGE_NAMES[self._current_stage]}）。',
                details={'current_stage': self._current_stage, 'exit_stage': stage},
            )

        record = self._get_active_record()
        record.exited_at = time.time()
        record.status = StageStatus.COMPLETED
        record.exit_ctx = {
            'exit_criteria_met': exit_criteria_met or [],
            'output_artifacts': output_artifacts or [],
            'next_stage': next_stage,
            **ctx,
        }

        prev_stage = self._current_stage
        self._current_stage = None
        self._current_role = None

        exit_ctx = {**record.exit_ctx}
        self._record_transition(
            event='STAGE_EXIT',
            stage=stage,
            role=role,
            message=message,
            ctx=exit_ctx,
            from_stage=prev_stage,
        )

        return record

    def _get_active_record(self) -> _StageRecord:
        for r in reversed(self._stage_records):
            if r.status == StageStatus.ACTIVE:
                return r
        raise TransitionError(
            code='NO_ACTIVE_STAGE',
            message='内部状态错误：is_active=True 但找不到活跃阶段记录。',
        )

    def mark_doc_check(self, required_docs: list[str]):
        """标记前置文档检查已完成（DOC_CHECK）。"""
        if self._current_stage is None:
            raise ExitWithoutEntryError(
                code='NO_ACTIVE_STAGE',
                message='无活跃阶段，无法标记文档检查。',
            )
        record = self._get_active_record()
        record.doc_check_done = True
        self._record_transition(
            event='DOC_CHECK',
            stage=self._current_stage,
            role=self._current_role or '',
            message=f'前置文档检查：共{len(required_docs)}份必读文档',
            ctx={'required_docs': required_docs},
        )

    def mark_pdr_done(self):
        """标记PDR前置文档读取流程完成。"""
        if self._current_stage is None:
            raise ExitWithoutEntryError(
                code='NO_ACTIVE_STAGE',
                message='无活跃阶段，无法标记PDR完成。',
            )
        record = self._get_active_record()
        record.pdr_done = True
        self._record_transition(
            event='PDR_CONFIRM',
            stage=self._current_stage,
            role=self._current_role or '',
            message='前置文档读取流程完成',
        )

    def request_jump(self, jump_type: str, to_stage: str, requested_by: str,
                     reason: str) -> JumpRecord:
        """提交阶段跳转申请。

        Args:
            jump_type: 'skip'（正向跳过）或 'rollback'（逆向回退）
            to_stage: 目标阶段ID
            requested_by: 申请角色
            reason: 跳转理由

        Returns:
            跳转记录（待审批状态）

        Raises:
            UnauthorizedJumpError: 禁止跳转场景（如跳至S8完成确认）
        """
        self._validate_role(requested_by)
        self._validate_stage_id(to_stage)

        if self._current_stage is None:
            raise ExitWithoutEntryError(
                code='NO_ACTIVE_STAGE',
                message='无活跃阶段，无法申请跳转。',
            )

        if to_stage == 'S8':
            raise InvalidJumpError(
                code='JUMP_TO_COMPLETION_FORBIDDEN',
                message='禁止跳至⑧完成确认阶段，必须经过验证才能标记完成。',
                details={'to_stage': to_stage},
            )

        if jump_type == 'rollback' and STAGE_ORDER[to_stage] >= STAGE_ORDER[self._current_stage]:
            raise InvalidJumpError(
                code='INVALID_ROLLBACK_TARGET',
                message=f'逆向回退目标阶段 {to_stage} 必须早于当前阶段 {self._current_stage}。',
                details={'current_stage': self._current_stage, 'to_stage': to_stage},
            )

        if jump_type == 'skip' and STAGE_ORDER[to_stage] <= STAGE_ORDER[self._current_stage]:
            raise InvalidJumpError(
                code='INVALID_SKIP_TARGET',
                message=f'正向跳过目标阶段 {to_stage} 必须晚于当前阶段 {self._current_stage}。',
                details={'current_stage': self._current_stage, 'to_stage': to_stage},
            )

        self._jump_counter += 1
        jump_id = f'jump-{self.session_id}-{self._jump_counter}'

        record = JumpRecord(
            timestamp=time.time(),
            jump_id=jump_id,
            jump_type=jump_type,
            from_stage=self._current_stage,
            to_stage=to_stage,
            requested_by=requested_by,
            reason=reason,
        )
        self._jump_records.append(record)
        self._pending_jump = record

        self._record_transition(
            event='JUMP_REQUEST',
            stage=self._current_stage,
            role=requested_by,
            message=f'申请阶段跳转: {self._current_stage}→{to_stage}（{jump_type}）',
            ctx={
                'jump_id': jump_id,
                'jump_type': jump_type,
                'from_stage': self._current_stage,
                'to_stage': to_stage,
                'reason': reason,
            },
        )

        return record

    def approve_jump(self, jump_id: str, approved_by: str,
                     rollback_scope: Optional[str] = None,
                     conditions: Optional[str] = None) -> JumpRecord:
        """批准阶段跳转。

        Args:
            jump_id: 跳转ID
            approved_by: 审批人（必须是orchestrator）
            rollback_scope: 回退范围（仅rollback时）
            conditions: 附加条件

        Returns:
            更新后的跳转记录

        Raises:
            UnauthorizedJumpError: 审批人不是orchestrator
            InvalidJumpError: 跳转不存在或已处理
        """
        if approved_by != 'orchestrator':
            raise UnauthorizedJumpError(
                code='JUMP_APPROVER_NOT_ORCHESTRATOR',
                message=f'阶段跳转必须由 orchestrator 批准，当前审批人: {approved_by}',
                details={'approved_by': approved_by},
            )

        record = self._find_jump(jump_id)
        if record.approved:
            raise InvalidJumpError(
                code='JUMP_ALREADY_APPROVED',
                message=f'跳转 {jump_id} 已被批准。',
                details={'jump_id': jump_id},
            )
        if record.reject_reason:
            raise InvalidJumpError(
                code='JUMP_ALREADY_REJECTED',
                message=f'跳转 {jump_id} 已被拒绝。',
                details={'jump_id': jump_id},
            )

        record.approved = True
        record.approved_by = approved_by
        record.rollback_scope = rollback_scope
        record.conditions = conditions
        self._pending_jump = None

        if record.jump_type == 'rollback':
            active = self._get_active_record()
            active.status = StageStatus.ROLLED_BACK
            self._current_stage = None
            self._current_role = None

        self._record_transition(
            event='JUMP_APPROVED',
            stage=record.from_stage,
            role=approved_by,
            message=f'阶段跳转已批准: {record.from_stage}→{record.to_stage}',
            ctx={
                'jump_id': jump_id,
                'jump_type': record.jump_type,
                'approved_by': approved_by,
                'rollback_scope': rollback_scope,
                'conditions': conditions,
            },
        )

        if record.jump_type == 'rollback':
            target_roles = STAGE_ROLES.get(record.to_stage, set())
            if record.requested_by in target_roles:
                entry_role = record.requested_by
            elif target_roles:
                entry_role = next(iter(target_roles))
            else:
                entry_role = 'orchestrator'
            self.enter_stage(
                stage=record.to_stage,
                role=entry_role,
                message=f'通过逆向回退进入 {record.to_stage}',
                ctx={
                    'jump_id': jump_id,
                    'rollback_scope': rollback_scope,
                    'conditions': conditions,
                },
                via_jump=True,
            )

        return record

    def reject_jump(self, jump_id: str, rejected_by: str, reject_reason: str) -> JumpRecord:
        """拒绝阶段跳转。"""
        record = self._find_jump(jump_id)
        if record.approved or record.reject_reason:
            raise InvalidJumpError(
                code='JUMP_ALREADY_PROCESSED',
                message=f'跳转 {jump_id} 已处理。',
                details={'jump_id': jump_id},
            )

        record.approved = False
        record.reject_reason = reject_reason
        self._pending_jump = None

        self._record_transition(
            event='JUMP_REJECTED',
            stage=record.from_stage,
            role=rejected_by,
            message=f'阶段跳转被拒绝: {record.from_stage}→{record.to_stage}',
            ctx={
                'jump_id': jump_id,
                'rejected_by': rejected_by,
                'reject_reason': reject_reason,
            },
        )

        return record

    def can_transition_to(self, target_stage: str) -> tuple[bool, str]:
        """检查是否可以正常转换到目标阶段（顺序推进）。

        Returns:
            (是否可以, 原因描述)
        """
        self._validate_stage_id(target_stage)
        if self._current_stage is None:
            if len(self._stage_records) == 0 and target_stage == 'S1':
                return True, '可以从S1开始'
            return False, '无活跃阶段且非初始状态，需通过审批跳转'
        expected_next = STAGE_ORDER[self._current_stage] + 1
        target_order = STAGE_ORDER[target_stage]
        if target_order == expected_next:
            return True, f'正常顺序推进 {self._current_stage}→{target_stage}'
        if target_order == STAGE_ORDER[self._current_stage]:
            return False, f'已在{self._current_stage}阶段'
        if target_order > expected_next:
            return False, f'跳过中间阶段，需提交skip跳转申请'
        return False, f'逆向回退需提交rollback申请'

    def execute_skip(self, jump_id: str, role: str, message: str,
                     ctx: Optional[dict] = None):
        """执行已批准的正向跳过：直接进入目标阶段。

        前提：JUMP_APPROVED已记录。
        """
        record = self._find_jump(jump_id)
        if not record.approved:
            raise UnauthorizedJumpError(
                code='JUMP_NOT_APPROVED',
                message=f'跳转 {jump_id} 未获得批准，无法执行。',
                details={'jump_id': jump_id},
            )
        if record.jump_type != 'skip':
            raise InvalidJumpError(
                code='WRONG_JUMP_TYPE',
                message=f'跳转 {jump_id} 类型为 {record.jump_type}，不是 skip。',
                details={'jump_id': jump_id, 'jump_type': record.jump_type},
            )

        if self._current_stage is not None:
            active = self._get_active_record()
            active.status = StageStatus.COMPLETED
            active.exited_at = time.time()
            active.exit_ctx = {'via_skip': True, 'jump_id': jump_id}
            self._record_transition(
                event='STAGE_EXIT',
                stage=self._current_stage,
                role=role,
                message=f'通过跳过退出 {self._current_stage}',
                ctx={'via_skip': True, 'jump_id': jump_id},
            )
            self._current_stage = None
            self._current_role = None

        target_role = next(iter(STAGE_ROLES.get(record.to_stage, {role})), role)
        self.enter_stage(
            stage=record.to_stage,
            role=target_role,
            message=message or f'通过正向跳过进入 {record.to_stage}',
            ctx={'jump_id': jump_id, 'conditions': record.conditions, **(ctx or {})},
            via_jump=True,
        )

    def _find_jump(self, jump_id: str) -> JumpRecord:
        for r in reversed(self._jump_records):
            if r.jump_id == jump_id:
                return r
        raise InvalidJumpError(
            code='JUMP_NOT_FOUND',
            message=f'跳转记录不存在: {jump_id}',
            details={'jump_id': jump_id},
        )

    def to_dict(self) -> dict:
        """导出当前状态为字典（用于序列化/调试）。"""
        return {
            'session_id': self.session_id,
            'current_stage': self._current_stage,
            'current_stage_name': self.current_stage_name,
            'current_role': self._current_role,
            'is_active': self.is_active,
            'completed_stages': self.completed_stages,
            'transition_count': len(self._transitions),
            'jump_count': len(self._jump_records),
            'pending_jump': {
                'jump_id': self._pending_jump.jump_id,
                'jump_type': self._pending_jump.jump_type,
                'to_stage': self._pending_jump.to_stage,
                'reason': self._pending_jump.reason,
            } if self._pending_jump else None,
        }
