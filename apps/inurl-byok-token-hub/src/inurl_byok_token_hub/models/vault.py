"""密钥库（Vault）模型：密文 blob、密钥记录与双 escrow。

加密口径（源文档 ``concepts/02`` §4.1，F-052）：
浏览器侧 ``PBKDF2(password, salt, iterations=100000, SHA-256)`` 派生 256-bit
主密钥 → ``AES-256-GCM`` 加密厂商 Key；生成**双份 escrow**
（``escrow_pw`` 口令恢复密文 + ``escrow_rec`` 恢复密语密文）。

服务端只持久化密文（含 alg/kdf/iterations/salt/iv/ct），明文永不落盘。
"""

import enum
import time

from pydantic import BaseModel, ConfigDict, Field

from ..crypto import ALG_AES_GCM, KDF_PBKDF2_SHA256, PBKDF2_ITERATIONS
from .catalog import ProviderProtocol


class CipherBlob(BaseModel):
    """密文封装。只承载密文与公开参数，绝不含明文。"""

    model_config = ConfigDict(frozen=True)

    alg: str = ALG_AES_GCM
    kdf: str = KDF_PBKDF2_SHA256
    iterations: int = PBKDF2_ITERATIONS
    salt: str
    iv: str
    ct: str

    @property
    def params(self) -> dict[str, object]:
        return {
            "alg": self.alg,
            "kdf": self.kdf,
            "iterations": self.iterations,
        }


class EscrowBlob(BaseModel):
    """单份 escrow：用某一凭证派生的密钥包裹主密钥后的密文。"""

    model_config = ConfigDict(frozen=True)

    kind: str  # "pw" | "rec"
    cipher: CipherBlob


class EscrowRecord(BaseModel):
    """双份 escrow 记录（``escrow_pw`` + ``escrow_rec``）。"""

    model_config = ConfigDict(frozen=True)

    user_id: str
    escrow_pw: EscrowBlob
    escrow_rec: EscrowBlob
    master_salt: str
    iterations: int = PBKDF2_ITERATIONS
    created_at: float = Field(default_factory=time.time)
    #: 主密钥版本，改密重加密时递增
    generation: int = 1


class KeyStatus(enum.StrEnum):
    ACTIVE = "active"
    ERROR = "error"
    QUOTA_EXHAUSTED = "quota_exhausted"
    DISABLED = "disabled"


class VaultKeyRecord(BaseModel):
    """厂商密钥记录（密文）。"""

    model_config = ConfigDict(frozen=True)

    id: str
    user_id: str
    provider_id: str
    display_name: str = ""
    protocol: ProviderProtocol = ProviderProtocol.OPENAI_COMPAT
    base_url: str = ""
    cipher: CipherBlob
    status: KeyStatus = KeyStatus.ACTIVE
    last_error: str = ""
    #: 「手填额度 − 已用 = 剩余」中的手填额度（token 计数单位；None 表示未填）
    quota_total: int | None = None
    quota_used: int = 0
    #: 所属主密钥版本
    generation: int = 1
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)

    @property
    def quota_remaining(self) -> int | None:
        if self.quota_total is None:
            return None
        return max(0, self.quota_total - self.quota_used)

    @property
    def is_usable(self) -> bool:
        return self.status is KeyStatus.ACTIVE and self.quota_remaining != 0
