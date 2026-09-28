"""凭证脱敏日志工具。

通过正则在日志输出前遮蔽常见敏感参数（token / key / pass_ticket /
cookie / secret / Authorization 头等），保证日志中不落明文凭证。
"""

import logging
import re

_MASK = "***REDACTED***"

# key=value、key:value 形式（值在空白/引号/& 处结束）
_KV_PATTERN = re.compile(
    r"(?i)((?:pass_ticket|token|ticket|secret|appsecret|cookie|session|sessionid|password|key)\s*[=:]\s*)"
    r"[^\s&;\"']+"
)
# Authorization: Bearer xxx
_BEARER_PATTERN = re.compile(
    r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s]+"
)


def redact(text: str | None, mask: str = _MASK) -> str:
    """遮蔽字符串中的敏感值；非字符串输入安全转为字符串。"""
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    text = _KV_PATTERN.sub(rf"\g<1>{mask}", text)
    text = _BEARER_PATTERN.sub(rf"\g<1>{mask}", text)
    return text


class RedactingFormatter(logging.Formatter):
    """对渲染后的日志消息统一执行脱敏。"""

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        return redact(message)


def configure_logging(level: str = "INFO") -> logging.Logger:
    """配置根 logger，幂等（重复调用不重复挂 handler）。"""
    root = logging.getLogger("mp_archiver")
    root.setLevel(level.upper())
    if not any(getattr(h, "_mp_archiver_handler", False) for h in root.handlers):
        handler = logging.StreamHandler()
        handler.setFormatter(
            RedactingFormatter("%(asctime)s %(levelname)-7s %(name)s: %(message)s")
        )
        handler._mp_archiver_handler = True  # type: ignore[attr-defined]
        root.addHandler(handler)
    root.propagate = False
    return root


def get_logger(name: str = "mp_archiver") -> logging.Logger:
    return logging.getLogger(name if name.startswith("mp_archiver") else f"mp_archiver.{name}")
