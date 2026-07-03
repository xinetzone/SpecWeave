"""阶段状态管理器验证逻辑混入。"""

from __future__ import annotations

from .constants import STAGE_NAMES, STAGE_ORDER, STAGE_ROLES, VALID_ROLES
from .exceptions import InvalidRoleError, InvalidStageError


class StageValidatorMixin:
    """阶段与角色验证混入类。"""

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
