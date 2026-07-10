"""阶段状态管理器数据模型定义。"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


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
    from_stage: str | None = None


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
    approved_by: str | None = None
    approved: bool = False
    reject_reason: str | None = None
    rollback_scope: str | None = None
    conditions: str | None = None


@dataclass
class _StageRecord:
    """内部阶段状态记录。"""
    stage: str
    role: str
    entered_at: float
    exited_at: float | None = None
    status: StageStatus = StageStatus.ACTIVE
    doc_check_done: bool = False
    pdr_done: bool = False
    exit_ctx: dict = field(default_factory=dict)
