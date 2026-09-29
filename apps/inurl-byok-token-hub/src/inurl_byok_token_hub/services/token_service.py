"""统一令牌服务：注册 / 登录 / 签发 / 校验 / 轮换 / 吊销 / 改密重加密。

鉴权语义（源文档 F-085 / F-099）：
- 用户类接口未提供或无效令牌 → **HTTP 401**，裸 JSON ``{"error": "unauthorized"}``；
- 管理员类接口越权 → **HTTP 403**，裸 JSON ``{"error": "forbidden"}``；
- 未匹配路由 → **HTTP 401**。
"""

import secrets
import time
from dataclasses import dataclass

from ..crypto import (
    derive_master_key,
    digest,
    digests_equal,
    issue_recovery_secret,
    issue_token,
    random_salt,
)
from ..errors import AuthError, BillingError, ErrorCode
from ..logging_utils import fingerprint, get_logger
from ..models import (
    RECOVERY_PREFIX,
    TOKEN_PREFIX,
    RecoveryRecord,
    Role,
    TokenRecord,
    TokenStatus,
    User,
)
from ..storage import Store

logger = get_logger("services.token")

#: 轮换后旧令牌的默认宽限期（秒）
DEFAULT_GRACE_SECONDS = 3600.0


def hash_password(password: str, salt: bytes) -> str:
    return derive_master_key(password, salt).hex()


@dataclass(frozen=True)
class RegistrationResult:
    """注册结果：明文凭证**只在此处出现一次**，之后不再可检索。"""

    user: User
    token: str
    recovery_secret: str


class TokenService:
    def __init__(self, store: Store) -> None:
        self.store = store

    # ---------------------------------------------------------------- 注册
    def register(
        self,
        email: str,
        password: str,
        *,
        invited_by: str | None = None,
        plan_key: str = "free",
        vault: object | None = None,
    ) -> RegistrationResult:
        email_key = email.strip().lower()
        if self.store.users.find(lambda u: u.email.lower() == email_key):
            raise BillingError(ErrorCode.INVALID_REQUEST.default_message + "：邮箱已注册")
        salt = random_salt()
        user = User(
            id=secrets.token_hex(8),
            email=email,
            password_digest=hash_password(password, salt),
            password_salt=salt.hex(),
            plan_key=plan_key,
            invited_by=invited_by,
        )
        self.store.users.add(user)

        token = issue_token()
        self.store.tokens.add(
            TokenRecord(
                id=secrets.token_hex(8),
                user_id=user.id,
                digest=digest(token),
                status=TokenStatus.ACTIVE,
            )
        )
        recovery = issue_recovery_secret()
        self.store.recovery.add(
            RecoveryRecord(user_id=user.id, digest=digest(recovery))
        )

        if vault is not None:
            vault.create_escrow(user.id, password, recovery)
        if invited_by:
            inviter = self.store.users.find(lambda u: u.id == invited_by)
            if inviter is not None:
                # 邀请奖励：默认 +1，上限 +5（文档未给数值，属合理默认）
                bonus = min(inviter.invite_bonus + 1, 5)
                self.store.users.replace(
                    lambda u, _uid=inviter.id: u.id == _uid,
                    inviter.model_copy(update={"invite_bonus": bonus}),
                )

        logger.info("注册用户 %s，令牌 %s", user.id, fingerprint(token))
        return RegistrationResult(user=user, token=token, recovery_secret=recovery)

    # ---------------------------------------------------------------- 登录
    def login(self, email: str, password: str) -> str:
        email_key = email.strip().lower()
        user = self.store.users.find(lambda u: u.email.lower() == email_key)
        if user is None:
            raise AuthError(ErrorCode.INVALID_CREDENTIALS)
        if not digests_equal(user.password_digest, hash_password(password, b64d_hex(user.password_salt))):
            raise AuthError(ErrorCode.INVALID_CREDENTIALS)
        return self.issue(user.id)

    def issue(self, user_id: str) -> str:
        token = issue_token()
        self.store.tokens.add(
            TokenRecord(
                id=secrets.token_hex(8),
                user_id=user_id,
                digest=digest(token),
                status=TokenStatus.ACTIVE,
            )
        )
        return token

    # ---------------------------------------------------------------- 校验
    def verify(self, token: str | None) -> User | None:
        if not token or not token.startswith(TOKEN_PREFIX):
            return None
        presented = digest(token)
        now = time.time()
        for record in self.store.tokens.all():
            if not digests_equal(record.digest, presented):
                continue
            if record.status is TokenStatus.REVOKED:
                return None
            if record.status is TokenStatus.ROTATED and record.grace_until < now:
                return None
            #: 写放大治理：``last_used_at`` 按 60s 节流，避免每次鉴权都整表重写
            if record.last_used_at is None or now - record.last_used_at > 60.0:
                self.store.tokens.replace(
                    lambda r, _rid=record.id: r.id == _rid,
                    record.model_copy(update={"last_used_at": now}),
                )
            return self.store.users.find(lambda u, _uid=record.user_id: u.id == _uid)
        return None

    def require_user(self, token: str | None) -> User:
        user = self.verify(token)
        if user is None:
            raise AuthError(ErrorCode.UNAUTHORIZED)
        return user

    def require_admin(self, token: str | None) -> User:
        user = self.require_user(token)
        if user.role is not Role.ADMIN:
            raise AuthError(ErrorCode.FORBIDDEN)
        return user

    # ---------------------------------------------------------------- 轮换/吊销
    def rotate(self, user_id: str, *, grace_seconds: float = DEFAULT_GRACE_SECONDS) -> str:
        now = time.time()
        for record in self.store.tokens.where(lambda r: r.user_id == user_id):
            if record.status is TokenStatus.ACTIVE:
                self.store.tokens.replace(
                    lambda r, _rid=record.id: r.id == _rid,
                    record.model_copy(
                        update={"status": TokenStatus.ROTATED, "grace_until": now + grace_seconds}
                    ),
                )
        return self.issue(user_id)

    def revoke(self, token_id: str) -> None:
        record = self.store.tokens.find(lambda r: r.id == token_id)
        if record is None:
            raise AuthError(ErrorCode.UNAUTHORIZED)
        self.store.tokens.replace(
            lambda r: r.id == token_id,
            record.model_copy(
                update={"status": TokenStatus.REVOKED, "revoked_at": time.time()}
            ),
        )

    # ---------------------------------------------------------------- 恢复
    def verify_recovery(self, recovery_secret: str) -> User | None:
        if not recovery_secret.startswith(RECOVERY_PREFIX):
            return None
        presented = digest(recovery_secret)
        for record in self.store.recovery.all():
            if digests_equal(record.digest, presented):
                return self.store.users.find(lambda u, _uid=record.user_id: u.id == _uid)
        return None

    def reset_password_with_recovery(self, recovery_secret: str, new_password: str) -> User:
        user = self.verify_recovery(recovery_secret)
        if user is None:
            raise AuthError(ErrorCode.INVALID_RECOVERY)
        return self._set_password(user, new_password)

    def change_password(self, user_id: str, old_password: str, new_password: str) -> User:
        user = self.store.users.find(lambda u: u.id == user_id)
        if user is None:
            raise AuthError(ErrorCode.UNAUTHORIZED)
        if not digests_equal(
            user.password_digest, hash_password(old_password, b64d_hex(user.password_salt))
        ):
            raise AuthError(ErrorCode.INVALID_CREDENTIALS)
        return self._set_password(user, new_password)

    def _set_password(self, user: User, new_password: str) -> User:
        salt = random_salt()
        updated = user.model_copy(
            update={
                "password_digest": hash_password(new_password, salt),
                "password_salt": salt.hex(),
            }
        )
        self.store.users.replace(lambda u: u.id == user.id, updated)
        return updated


def b64d_hex(value: str) -> bytes:
    """十六进制 salt → bytes。"""
    return bytes.fromhex(value)


__all__ = [
    "DEFAULT_GRACE_SECONDS",
    "RegistrationResult",
    "TokenService",
    "b64d_hex",
    "hash_password",
]
