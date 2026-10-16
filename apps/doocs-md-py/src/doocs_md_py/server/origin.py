"""Origin 白名单与通配匹配（upstream: apps/api/src/origin.ts 1:1）。"""

import re
from urllib.parse import urlsplit

# upstream: origin.ts:8
_EXTENSION_ORIGIN_RE = re.compile(
    r"^(?:chrome-extension|moz-extension|safari-web-extension)://[^/]+$", re.IGNORECASE
)

# 正则元字符转义（upstream: origin.ts:4）
_ESCAPE_RE = re.compile(r"[.*+?^${}()|[\]\\]")


def _escape_regex(s: str) -> str:
    return _ESCAPE_RE.sub(lambda m: "\\" + m.group(0), s)


def is_browser_extension_origin(origin: str | None) -> bool:
    """upstream: origin.ts:10 浏览器扩展页面 origin 放行。"""
    if not origin:
        return False
    return bool(_EXTENSION_ORIGIN_RE.match(origin))


def match_pattern(origin: str, pattern: str) -> bool:
    """upstream: origin.ts:22。

    精确匹配优先；含 ``*`` 时按 ``[^./]+`` 翻译为正则——单标签不跨点/斜杠，
    适用于预览子域（如 https://*--doocs-md.netlify.app、http://localhost:*）。
    """
    if not pattern:
        return False
    if pattern == origin:
        return True
    if "*" not in pattern:
        return False
    pieces = [_escape_regex(p) for p in pattern.split("*")]
    regex = "^" + "[^./]+".join(pieces) + "$"
    return re.match(regex, origin) is not None


def allowed_patterns(app_url: str) -> tuple[str, ...]:
    """upstream: origin.ts:34 解析逗号分隔的 APP_URL。"""
    return tuple(s.strip() for s in app_url.split(",") if s.strip())


def is_allowed_origin(app_url: str, origin: str | None) -> bool:
    """upstream: origin.ts:39。"""
    if not origin:
        return False
    return any(match_pattern(origin, p) for p in allowed_patterns(app_url))


def default_origin(app_url: str) -> str:
    """upstream: origin.ts:46 首个无通配符模式，否则首个模式，否则空串。"""
    patterns = allowed_patterns(app_url)
    return next((p for p in patterns if "*" not in p), patterns[0] if patterns else "")


def resolve_redirect(app_url: str, requested: str | None) -> str:
    """upstream: origin.ts:56 校验回跳 URL；不在白名单则回退默认 origin。"""
    if requested:
        try:
            parsed = urlsplit(requested)
            if parsed.scheme and parsed.netloc and is_allowed_origin(
                app_url, f"{parsed.scheme}://{parsed.netloc}"
            ):
                return requested
        except ValueError:
            pass
    return default_origin(app_url)
