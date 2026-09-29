"""密钥库服务：双 escrow 托管、厂商密钥加解密、改密重加密。

加密口径（源文档 ``concepts/02`` §4.1，F-052）：
``PBKDF2(password, salt, 100000, SHA-256)`` 派生 AES-GCM-256 主密钥；
注册时生成**双份 escrow**（``escrow_pw`` 口令密文 + ``escrow_rec`` 恢复密语密文）。

服务端只持久化密文；明文 Key 仅在内存中作为参数/返回值出现。
"""

import secrets
import time

from ..crypto import (
    b64d,
    b64e,
    derive_master_key,
    encrypt_secret,
    new_master_key,
    random_salt,
    unwrap_master_key,
    wrap_master_key,
)
from ..errors import ErrorCode, VaultError
from ..logging_utils import fingerprint, get_logger
from ..models import (
    CipherBlob,
    EscrowBlob,
    EscrowRecord,
    KeyStatus,
    VaultKeyRecord,
)
from ..providers.base import ProviderProtocol
from ..storage import Store

logger = get_logger("services.vault")


class VaultService:
    def __init__(
        self, store: Store, billing: object | None = None, catalog: object | None = None
    ) -> None:
        self.store = store
        self.billing = billing
        self.catalog = catalog

    def _resolve_protocol(
        self, provider_id: str, protocol: ProviderProtocol | None
    ) -> ProviderProtocol:
        """协议解析优先级：显式指定 > 目录厂商协议 > OpenAI 兼容兜底。

        目录是本实现中厂商线协议的唯一事实源（源文档 F-047「三协议」）：
        Anthropic/Gemini 厂商若沿用默认的 ``openai_compat``，将永远无法走到
        对应适配器，故此处必须回落到目录协议。
        """
        if protocol is not None:
            return protocol
        if self.catalog is not None:
            provider = self.catalog.provider(provider_id)
            if provider is not None and provider.protocol is not None:
                return ProviderProtocol(provider.protocol)
        return ProviderProtocol.OPENAI_COMPAT

    # ------------------------------------------------------------ escrow
    def create_escrow(self, user_id: str, password: str, recovery_secret: str) -> EscrowRecord:
        if self.store.escrow.find(lambda e: e.user_id == user_id):
            raise VaultError(ErrorCode.KEY_ALREADY_EXISTS, "该用户已初始化密钥托管")
        master_key = new_master_key()

        pw_salt = random_salt()
        pw_iv, pw_wrapped = wrap_master_key(master_key, password, pw_salt)
        rec_salt = random_salt()
        rec_iv, rec_wrapped = wrap_master_key(master_key, recovery_secret, rec_salt)

        record = EscrowRecord(
            user_id=user_id,
            escrow_pw=EscrowBlob(
                kind="pw",
                cipher=CipherBlob(salt=b64e(pw_salt), iv=b64e(pw_iv), ct=b64e(pw_wrapped)),
            ),
            escrow_rec=EscrowBlob(
                kind="rec",
                cipher=CipherBlob(salt=b64e(rec_salt), iv=b64e(rec_iv), ct=b64e(rec_wrapped)),
            ),
            master_salt=b64e(pw_salt),
        )
        self.store.escrow.add(record)
        logger.info("用户 %s 初始化双 escrow（generation=%d）", user_id, record.generation)
        return record

    def unlock_with_password(self, user_id: str, password: str) -> bytes:
        record = self._escrow(user_id)
        blob = record.escrow_pw.cipher
        return unwrap_master_key(
            b64d(blob.ct), b64d(blob.iv), password, b64d(blob.salt)
        )

    def unlock_with_recovery(self, user_id: str, recovery_secret: str) -> bytes:
        record = self._escrow(user_id)
        blob = record.escrow_rec.cipher
        return unwrap_master_key(
            b64d(blob.ct), b64d(blob.iv), recovery_secret, b64d(blob.salt)
        )

    def _escrow(self, user_id: str) -> EscrowRecord:
        record = self.store.escrow.find(lambda e: e.user_id == user_id)
        if record is None:
            raise VaultError(ErrorCode.VAULT_LOCKED, "尚未初始化密钥托管")
        return record

    # ------------------------------------------------------------ 厂商密钥
    def add_key(
        self,
        user_id: str,
        provider_id: str,
        api_key: str,
        master_key: bytes,
        *,
        display_name: str = "",
        protocol: ProviderProtocol | None = None,
        base_url: str = "",
        quota_total: int | None = None,
    ) -> VaultKeyRecord:
        if self.store.keys.find(lambda k: k.user_id == user_id and k.provider_id == provider_id):
            raise VaultError(ErrorCode.KEY_ALREADY_EXISTS)
        if self.billing is not None:
            self.billing.assert_within_key_limit(user_id)
        iv, ct = encrypt_secret(master_key, api_key)
        record = VaultKeyRecord(
            id=secrets.token_hex(8),
            user_id=user_id,
            provider_id=provider_id,
            display_name=display_name or provider_id,
            protocol=self._resolve_protocol(provider_id, protocol),
            base_url=base_url,
            cipher=CipherBlob(salt="", iv=b64e(iv), ct=b64e(ct)),
            status=KeyStatus.ACTIVE,
            quota_total=quota_total,
        )
        self.store.keys.add(record)
        logger.info("用户 %s 录入厂商 %s 密钥（%s）", user_id, provider_id, fingerprint(api_key))
        return record

    def decrypt_key(self, record: VaultKeyRecord, master_key: bytes) -> str:
        from ..crypto import decrypt_secret

        try:
            return decrypt_secret(master_key, b64d(record.cipher.iv), b64d(record.cipher.ct))
        except Exception as exc:  # noqa: BLE001 - 统一归一化为 VaultError
            raise VaultError(ErrorCode.VAULT_LOCKED, "主密钥无法解密该记录") from exc

    def list_keys(self, user_id: str) -> tuple[VaultKeyRecord, ...]:
        """列表**永不下发明文**，也不含 cipher 内容以外的敏感字段。"""
        return tuple(self.store.keys.where(lambda k: k.user_id == user_id))

    def remove_key(self, user_id: str, key_id: str) -> int:
        return self.store.keys.remove(lambda k: k.user_id == user_id and k.id == key_id)

    def mark_error(self, key_id: str, message: str) -> None:
        record = self.store.keys.find(lambda k: k.id == key_id)
        if record is None:
            return
        self.store.keys.replace(
            lambda k: k.id == key_id,
            record.model_copy(update={"status": KeyStatus.ERROR, "last_error": message}),
        )

    # ------------------------------------------------------------ 重加密
    def reencrypt_all(self, user_id: str, old_master: bytes, new_master: bytes) -> int:
        """改密重加密：用新主密钥重写全部厂商密钥密文。"""
        count = 0
        for record in self.store.keys.where(lambda k: k.user_id == user_id):
            plaintext = self.decrypt_key(record, old_master)
            iv, ct = encrypt_secret(new_master, plaintext)
            self.store.keys.replace(
                lambda k, _kid=record.id: k.id == _kid,
                record.model_copy(
                    update={
                        "cipher": CipherBlob(salt="", iv=b64e(iv), ct=b64e(ct)),
                        "generation": record.generation + 1,
                        "updated_at": time.time(),
                    }
                ),
            )
            count += 1
        return count

    # ------------------------------------------------------------ escrow 上传
    def adopt_client_escrow(
        self,
        user_id: str,
        escrow_pw: dict,
        escrow_rec: dict,
        password: str,
    ) -> tuple[EscrowRecord, bytes, int]:
        """接管客户端生成的双 escrow（对应 ``POST /api/escrow``）。

        原产品是浏览器端 E2EE：主密钥在客户端生成，服务端只存两份密文。
        本复刻的本地代理**需要明文 Key 才能转发**，故服务端必须能解出主密钥，
        因此接管客户端 escrow 时要求同传 ``password``：

        1. 用 ``password`` 解开**当前** escrow 拿到旧主密钥（顺带校验口令正确）；
        2. 用 ``password`` 解开**上传的** ``escrow_pw`` 拿到客户端新主密钥；
        3. 以新主密钥重写该用户全部厂商密钥密文（``reencrypt_all``）；
        4. 落盘新 escrow 并递增 ``generation``。

        做不到静默收下密文就返回 200——那会让客户端误以为托管成功。
        """
        record = self._escrow(user_id)
        old_master = self.unlock_with_password(user_id, password)
        new_pw = _parse_blob(escrow_pw, kind="pw")
        new_rec = _parse_blob(escrow_rec, kind="rec")
        new_master = unwrap_master_key(
            b64d(new_pw.cipher.ct), b64d(new_pw.cipher.iv), password, b64d(new_pw.cipher.salt)
        )
        count = self.reencrypt_all(user_id, old_master, new_master)
        updated = record.model_copy(
            update={
                "escrow_pw": new_pw,
                "escrow_rec": new_rec,
                "master_salt": new_pw.cipher.salt,
                "generation": record.generation + 1,
            }
        )
        self.store.escrow.replace(lambda e: e.user_id == user_id, updated)
        logger.info("用户 %s 接管客户端 escrow（generation=%d，重写 %d 条密钥）", user_id, updated.generation, count)
        return updated, new_master, count

    def rotate_escrow(
        self,
        user_id: str,
        old_credential: str | None,
        new_credential: str,
        *,
        kind: str = "pw",
        master_key: bytes | None = None,
    ) -> EscrowRecord:
        """重建对应 escrow（主密钥默认保持不变）。

        改密/重置后调用。若已持有主密钥（例如走恢复流程）可直接传入
        ``master_key``，避免在不知道旧口令的情况下重复解锁。
        """
        record = self._escrow(user_id)
        if master_key is None:
            if old_credential is None:
                raise VaultError(ErrorCode.VAULT_LOCKED, "缺少旧凭证且未提供主密钥")
            master_key = (
                self.unlock_with_password(user_id, old_credential)
                if kind == "pw"
                else self.unlock_with_recovery(user_id, old_credential)
            )
        salt = random_salt()
        iv, wrapped = wrap_master_key(master_key, new_credential, salt)
        blob = EscrowBlob(kind=kind, cipher=CipherBlob(salt=b64e(salt), iv=b64e(iv), ct=b64e(wrapped)))
        updated = record.model_copy(
            update={
                "escrow_pw": blob if kind == "pw" else record.escrow_pw,
                "escrow_rec": blob if kind == "rec" else record.escrow_rec,
                "generation": record.generation + 1,
            }
        )
        self.store.escrow.replace(lambda e: e.user_id == user_id, updated)
        return updated


def _parse_blob(payload: dict, *, kind: str) -> EscrowBlob:
    """校验并归一化上传的 escrow blob（拒绝非 dict 或缺字段的载荷）。"""
    if not isinstance(payload, dict):
        raise VaultError(ErrorCode.INVALID_REQUEST, f"escrow_{kind} 必须是对象")
    try:
        blob = EscrowBlob.model_validate(payload)
    except Exception as exc:  # noqa: BLE001 - pydantic 校验错误统一归一化为 VaultError
        raise VaultError(ErrorCode.INVALID_REQUEST, f"escrow_{kind} 结构非法：{exc}") from exc
    return blob.model_copy(update={"kind": kind})


def derive_from_password(password: str, salt: bytes) -> bytes:
    """暴露给测试：确认 KDF 参数与文档逐字一致（PBKDF2-SHA256/100000）。"""
    return derive_master_key(password, salt)


__all__ = ["VaultService", "derive_from_password"]
