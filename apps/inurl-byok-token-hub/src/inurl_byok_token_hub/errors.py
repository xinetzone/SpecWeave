"""统一错误码、异常体系与 HTTP 映射。

错误响应体遵循 OpenAI 兼容风格::

    {"error": {"message": "...", "type": "...", "code": "...", "param": null}}

另有一类「裸 JSON」形态（``{"error": "unauthorized"}``），用于对齐源文档 F-085 /
F-099 记录的鉴权语义：用户类接口未授权返回 401 裸 JSON，管理员类接口越权返回
403 裸 JSON，未匹配路由同样返回 401 裸 JSON。
"""

import enum
from dataclasses import dataclass


class ErrorCode(enum.Enum):
    """错误码枚举：(HTTP 状态码, code 字段, 默认中文消息)。"""

    # 鉴权与权限（4xx）
    UNAUTHORIZED = (401, "unauthorized", "未提供有效令牌或令牌已失效")
    FORBIDDEN = (403, "forbidden", "当前令牌无权访问该资源")
    TURNSTILE_REQUIRED = (401, "turnstile_required", "需先通过人机验证")
    INVALID_CREDENTIALS = (401, "invalid_credentials", "邮箱或密码错误")

    # 请求校验（4xx）
    INVALID_REQUEST = (400, "invalid_request_error", "请求参数不合法")
    REQUEST_TOO_LARGE = (413, "request_too_large", "请求体超出限制")
    UNSUPPORTED_FEATURE = (422, "unsupported_feature", "暂不支持该特性")
    UNSUPPORTED_CAPABILITY = (422, "unsupported_capability", "当前没有支持该类别的厂商")
    MODEL_NOT_FOUND = (404, "model_not_found", "模型不存在或不在可路由池中")
    PROVIDER_NOT_FOUND = (404, "provider_not_found", "厂商不存在")
    KEY_NOT_FOUND = (404, "key_not_found", "密钥记录不存在")

    # 业务规则（4xx / 409）
    KEY_LIMIT_EXCEEDED = (409, "key_limit_exceeded", "已达当前套餐的厂商密钥上限，请升级套餐")
    KEY_ALREADY_EXISTS = (409, "key_already_exists", "该厂商密钥已存在")
    VAULT_LOCKED = (409, "vault_locked", "密钥库已锁定，请先解锁")
    INVALID_RECOVERY = (401, "invalid_recovery", "恢复密语无效")
    QUOTA_EXHAUSTED = (409, "quota_exhausted", "该厂商额度已用尽")
    ORDER_STATE_INVALID = (409, "order_state_invalid", "订单状态不允许该操作")

    # 上游与可用性（5xx / 429）
    NO_AVAILABLE_PROVIDER = (503, "no_available_provider", "当前没有可用厂商")
    ALL_PROVIDERS_RATE_LIMITED = (429, "all_providers_rate_limited", "全部候选厂商均被限流")
    UPSTREAM_TIMEOUT = (504, "upstream_timeout", "上游厂商响应超时")
    UPSTREAM_AUTH_ERROR = (502, "upstream_auth_error", "上游厂商鉴权失败")
    UPSTREAM_ERROR = (502, "upstream_error", "上游厂商返回错误")
    ALL_PROVIDERS_FAILED = (502, "all_providers_failed", "全部候选厂商调用失败")

    # 服务端
    INTERNAL_ERROR = (500, "internal_error", "服务内部错误")

    @property
    def http_status(self) -> int:
        return self.value[0]

    @property
    def code(self) -> str:
        return self.value[1]

    @property
    def default_message(self) -> str:
        return self.value[2]


#: 裸 JSON 鉴权语义使用的固定文案（与源文档逐字一致）
BARE_UNAUTHORIZED = {"error": "unauthorized"}
BARE_FORBIDDEN = {"error": "forbidden"}


class ByokError(Exception):
    """项目异常基类。"""

    def __init__(
        self,
        error_code: ErrorCode,
        message: str | None = None,
        param: str | None = None,
    ) -> None:
        self.error_code = error_code
        self.message = message or error_code.default_message
        self.param = param
        super().__init__(self.message)

    @property
    def http_status(self) -> int:
        return self.error_code.http_status

    def to_body(self) -> dict:
        """OpenAI 兼容风格错误响应体。"""
        return {
            "error": {
                "message": self.message,
                "type": self.error_code.name.lower(),
                "code": self.error_code.code,
                "param": self.param,
            }
        }

    def bare_body(self) -> dict:
        """裸 JSON 错误响应体（仅鉴权类错误使用）。"""
        if self.error_code is ErrorCode.FORBIDDEN:
            return dict(BARE_FORBIDDEN)
        return dict(BARE_UNAUTHORIZED)


class ConfigError(ByokError):
    """配置加载/校验失败。"""

    def __init__(self, message: str) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, message)


class AuthError(ByokError):
    """鉴权失败。"""


class VaultError(ByokError):
    """密钥库操作失败。"""


class BillingError(ByokError):
    """套餐/额度规则拒绝。"""


class RoutingError(ByokError):
    """路由失败。"""


class UpstreamError(ByokError):
    """上游厂商调用失败。"""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        provider_id: str | None = None,
        retryable: bool = False,
    ) -> None:
        code = ErrorCode.UPSTREAM_ERROR
        if status_code == 429:
            code = ErrorCode.ALL_PROVIDERS_RATE_LIMITED
        elif status_code == 401 or status_code == 403:
            code = ErrorCode.UPSTREAM_AUTH_ERROR
        elif status_code == 404:
            code = ErrorCode.UPSTREAM_ERROR
        super().__init__(code, message)
        self.status_code = status_code
        self.provider_id = provider_id
        self.retryable = retryable


@dataclass(frozen=True)
class TimeoutSpec:
    """超时配置（供 UpstreamError 判定是否可切换）。"""

    connect: float = 5.0
    read: float = 30.0
    write: float = 10.0
    pool: float = 5.0


