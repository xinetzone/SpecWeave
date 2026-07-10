"""阶段状态管理器跳转审批逻辑混入。"""

from __future__ import annotations

import time
from typing import Optional

from .constants import STAGE_ORDER, STAGE_ROLES
from .exceptions import (
    ExitWithoutEntryError,
    InvalidJumpError,
    UnauthorizedJumpError,
)
from .models import JumpRecord, StageStatus


class StageJumpMixin:
    """阶段跳转审批逻辑混入类。"""

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
                     rollback_scope: str | None = None,
                     conditions: str | None = None) -> JumpRecord:
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
                     ctx: dict | None = None):
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

        target_roles = STAGE_ROLES.get(record.to_stage, set())
        if role in target_roles:
            target_role = role
        elif target_roles:
            target_role = next(iter(target_roles))
        else:
            target_role = role
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
