"""日志与脱敏工具。

硬约束：明文厂商 Key、统一令牌、主密钥、恢复密语**不得**进入日志、异常或指标。
统一走 :func:`redact` 与 :func:`fingerprint`。
"""

import logging
import re

LOGGER_NAME = "inurl_byok_token_hub"

#: 需要脱敏的查询参数/字段名
_SENSITIVE_KEYS = ("key", "api_key", "apikey", "token", "authorization", "x-api-key", "secret", "password")

_QUERY_PATTERN = re.compile(r"([?&](?:key|api_key|apikey|token|access_token)=)([^&#\s]+)", re.I)
_JSON_PATTERN = re.compile(
    r'("(?:api[-_]?key|key|token|secret|password|authorization)"\s*:\s*")([^"]+)(")', re.I
)

#: 原产品令牌前缀（复刻时同样用于识别需脱敏的字面量）
TOKEN_PREFIX = "byok_live_"  # noqa: S105 - 仅用于脱敏识别的前缀常量


def redact(value: str | None) -> str:
    """把字符串中的敏感片段替换为 ``[REDACTED]``。"""
    if not value:
        return ""
    text = _QUERY_PATTERN.sub(r"\1[REDACTED]", value)
    text = _JSON_PATTERN.sub(r"\1[REDACTED]\3", text)
    if TOKEN_PREFIX in text:
        text = re.sub(re.escape(TOKEN_PREFIX) + r"[A-Za-z0-9_\-]+", TOKEN_PREFIX + "[REDACTED]", text)
    return text


def fingerprint(secret: str | None, head: int = 6, tail: int = 4) -> str:
    """仅保留前缀与后若干位，用于日志中定位但不泄露。"""
    if not secret:
        return "<empty>"
    if len(secret) <= head + tail:
        return "*" * len(secret)
    return f"{secret[:head]}…{secret[-tail:]}"


class RedactingFilter(logging.Filter):
    """日志过滤器：对已格式化的消息做二次脱敏，防止漏网。"""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            record.msg = redact(str(record.msg))
            if record.args:
                # 仅对字符串型参数脱敏，数值/其他类型保持原样，
                # 否则 "%d" 之类的格式占位符会因参数被转成 str 而报错。
                if isinstance(record.args, dict):
                    record.args = {
                        k: (redact(v) if isinstance(v, str) else v)
                        for k, v in record.args.items()
                    }
                else:
                    record.args = tuple(
                        (redact(a) if isinstance(a, str) else a) for a in record.args
                    )
        except Exception:  # pragma: no cover - 日志路径不应影响业务
            return True
        return True


def get_logger(name: str | None = None) -> logging.Logger:
    logger = logging.getLogger(f"{LOGGER_NAME}.{name}" if name else LOGGER_NAME)
    if not any(isinstance(f, RedactingFilter) for f in logger.filters):
        logger.addFilter(RedactingFilter())
    return logger
