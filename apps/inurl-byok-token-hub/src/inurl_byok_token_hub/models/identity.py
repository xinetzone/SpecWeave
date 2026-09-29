"""身份与令牌模型。

关键约束：统一令牌以 ``byok_live_`` 为前缀，**库内只存 SHA-256 摘要**，
明文仅在签发时一次性返回；恢复密语同理只存摘要。
"""

import enum
import time

from pydantic import BaseModel, ConfigDict, Field

#: 令牌前缀（源文档 F-045：令牌前缀 ``byok_live_``）
TOKEN_PREFIX = "byok_live_"  # noqa: S105 - 令牌前缀常量，非口令
#: 恢复密语前缀（复刻实现自定，用于识别与脱敏）
RECOVERY_PREFIX = "byok_rec_"


class Role(enum.StrEnum):
    USER = "user"
    ADMIN = "admin"


class TokenStatus(enum.StrEnum):
    ACTIVE = "active"
    ROTATED = "rotated"
    REVOKED = "revoked"


class User(BaseModel):
    """用户。密码只存摘要，邮箱保留原文（演示用途）。"""

    model_config = ConfigDict(frozen=True)

    id: str
    email: str
    password_digest: str
    password_salt: str
    role: Role = Role.USER
    plan_key: str = "free"
    #: 邀请带来的额外密钥额度
    invite_bonus: int = 0
    invited_by: str | None = None
    created_at: float = Field(default_factory=time.time)

    def key_limit(self, plan_key_limit: int | None) -> int | None:
        """套餐上限 + 邀请奖励；``None`` 表示无限。"""
        if plan_key_limit is None:
            return None
        return plan_key_limit + self.invite_bonus


class TokenRecord(BaseModel):
    """统一令牌记录（仅存摘要）。"""

    model_config = ConfigDict(frozen=True)

    id: str
    user_id: str
    digest: str
    status: TokenStatus = TokenStatus.ACTIVE
    created_at: float = Field(default_factory=time.time)
    #: 轮换后旧令牌的宽限期截止（epoch 秒）；0 表示无宽限
    grace_until: float = 0.0
    revoked_at: float | None = None
    last_used_at: float | None = None


class RecoveryRecord(BaseModel):
    """恢复密语记录（仅存摘要）。"""

    model_config = ConfigDict(frozen=True)

    user_id: str
    digest: str
    created_at: float = Field(default_factory=time.time)
