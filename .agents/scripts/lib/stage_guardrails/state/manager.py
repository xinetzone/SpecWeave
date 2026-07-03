"""阶段状态管理器主类。"""

from __future__ import annotations

import time
from typing import Optional

from .constants import STAGE_NAMES
from .jumps import StageJumpMixin
from .models import JumpRecord, StageStatus, StageTransition, _StageRecord
from .transitions import StageTransitionMixin
from .validators import StageValidatorMixin


class StageStateManager(StageValidatorMixin, StageTransitionMixin, StageJumpMixin):
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
