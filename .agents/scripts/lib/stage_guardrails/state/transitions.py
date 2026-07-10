"""阶段状态管理器阶段转换逻辑混入。"""

from __future__ import annotations

import time
from typing import Optional

from .constants import STAGE_NAMES
from .exceptions import (
    DuplicateEntryError,
    ExitWithoutEntryError,
    StageMismatchError,
    TransitionError,
)
from .models import StageStatus, StageTransition, _StageRecord


class StageTransitionMixin:
    """阶段进入/退出/标记逻辑混入类。"""

    def _record_transition(self, event: str, stage: str, role: str, message: str,
                           ctx: dict | None = None, from_stage: str | None = None):
        self._transitions.append(StageTransition(
            timestamp=time.time(),
            event=event,
            stage=stage,
            role=role,
            message=message,
            ctx=ctx or {},
            from_stage=from_stage,
        ))

    def _get_active_record(self) -> _StageRecord:
        for r in reversed(self._stage_records):
            if r.status == StageStatus.ACTIVE:
                return r
        raise TransitionError(
            code='NO_ACTIVE_STAGE',
            message='内部状态错误：is_active=True 但找不到活跃阶段记录。',
        )

    def enter_stage(self, stage: str, role: str, message: str,
                    ctx: dict | None = None, via_jump: bool = False):
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
                   exit_criteria_met: list[str] | None = None,
                   output_artifacts: list[str] | None = None,
                   next_stage: str | None = None,
                   ctx: dict | None = None) -> _StageRecord:
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
