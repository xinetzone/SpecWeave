"""阶段状态管理器包。

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

from .constants import STAGE_NAMES, STAGE_ORDER, STAGE_ROLES, VALID_ROLES
from .exceptions import (
    DuplicateEntryError,
    ExitWithoutEntryError,
    InvalidJumpError,
    InvalidRoleError,
    InvalidStageError,
    StageMismatchError,
    TransitionError,
    UnauthorizedJumpError,
)
from .manager import StageStateManager
from .models import JumpRecord, StageStatus, StageTransition

__all__ = [
    'STAGE_ORDER',
    'STAGE_NAMES',
    'VALID_ROLES',
    'STAGE_ROLES',
    'TransitionError',
    'InvalidStageError',
    'InvalidRoleError',
    'DuplicateEntryError',
    'ExitWithoutEntryError',
    'StageMismatchError',
    'UnauthorizedJumpError',
    'InvalidJumpError',
    'StageStatus',
    'StageTransition',
    'JumpRecord',
    'StageStateManager',
]
