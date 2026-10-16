"""市场主题/组件发布与更新校验（upstream: apps/api/src/marketplace-validate.ts 1:1）。

JS 语义对照：
- ``byteLength`` = UTF-8 字节数（TextEncoder）；
- ``undefined``/``null`` 区分：用 ``_UNSET`` 哨兵表达键缺失，None 表达显式 null；
- ``Number(segment)`` 兼容空串→0、十六进制串→十进制、非法值→NaN；
- 结果对象沿用上游 ``{ok, value|error}`` 可判别联合形态。
"""

import json
import math
import re
from dataclasses import dataclass
from typing import Any, Generic, TypeVar
from urllib.parse import urlparse

# upstream: marketplace-validate.ts:8-16
MAX_THEME_CSS_BYTES = 200 * 1024
MAX_COMPONENT_JSON_BYTES = 50 * 1024
MAX_SAMPLE_MARKDOWN_BYTES = 32 * 1024
MAX_NAME_LENGTH = 64
MAX_SLUG_LENGTH = 48
MAX_DESCRIPTION_LENGTH = 2000
MAX_VERSION_LENGTH = 32
MAX_COVER_URL_LENGTH = 512
MAX_REJECT_REASON_LENGTH = 500

# upstream: marketplace-validate.ts:18-20
_SLUG_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,46}[a-z0-9])?$")
_PASCAL_CASE_RE = re.compile(r"^[A-Z][A-Za-z0-9]*$")
_HEX_COLOR_RE = re.compile(r"^#(?:[0-9a-f]{3}|[0-9a-f]{6}|[0-9a-f]{8})$", re.IGNORECASE)

# upstream: marketplace-validate.ts:22-26
_DANGEROUS_TAG_RE = re.compile(
    r"<\s*(?:/\s*)?(?:script|iframe|object|embed|link|meta|base|form)\b",
    re.IGNORECASE,
)
_EVENT_HANDLER_RE = re.compile(r"\son[a-z]+\s*=", re.IGNORECASE)
_JS_URL_RE = re.compile(r"""(?:href|src|action)\s*=\s*(?:["']\s*)?javascript:""", re.IGNORECASE)
_CSS_IMPORT_RE = re.compile(r"@import\b", re.IGNORECASE)
_CSS_EXTERNAL_URL_RE = re.compile(r"""url\s*\(\s*(?:["']\s*)?https?://""", re.IGNORECASE)

# upstream: marketplace-validate.ts:60
INITIAL_MARKETPLACE_VERSION = "1.0.0"

T = TypeVar("T")

# 键缺失哨兵（对齐 JS undefined；None 对齐显式 null）
_UNSET: Any = object()


@dataclass(slots=True)
class ValidateResult(Generic[T]):
    """upstream: ValidateOk<T> | ValidateErr 判别联合。"""

    ok: bool
    value: T | None = None
    error: str | None = None

    @classmethod
    def success(cls, value: T) -> "ValidateResult[T]":
        return cls(ok=True, value=value)

    @classmethod
    def failure(cls, error: str) -> "ValidateResult[T]":
        return cls(ok=False, error=error)


def _byte_length(text: str) -> int:
    # upstream: marketplace-validate.ts:32-34
    return len(text.encode("utf-8"))


def _trim_string(value: Any, max_length: int) -> str | None:
    # upstream: marketplace-validate.ts:36-43
    if not isinstance(value, str):
        return None
    trimmed = value.strip()
    if not trimmed or len(trimmed) > max_length:
        return None
    return trimmed


def _optional_trim_string(value: Any, max_length: int) -> Any:
    # upstream: marketplace-validate.ts:45-51；返回 _UNSET/None/str 三态
    if value is _UNSET:
        return _UNSET
    if value is None or value == "":
        return None
    return _trim_string(value, max_length)


def parse_slug(value: Any) -> str | None:
    """upstream: marketplace-validate.ts:53-58。"""
    slug = _trim_string(value, MAX_SLUG_LENGTH)
    if not slug or not _SLUG_RE.match(slug):
        return None
    return slug


# ---- 版本号（upstream: marketplace-validate.ts:62-124）----


def _js_number(segment: str) -> float:
    """等价 JS ``Number(segment)``：空串/纯空白→0，0x 十六进制→十进制，非法→NaN。"""
    s = segment.strip()
    if s == "":
        return 0.0
    if s[:2].lower() == "0x":
        try:
            return float(int(s, 16))
        except ValueError:
            return float("nan")
    try:
        return float(s)
    except ValueError:
        return float("nan")


def _parse_version_triple(version: str) -> tuple[int, int, int]:
    # upstream: marketplace-validate.ts:68-76
    raw = re.sub(r"^v", "", version.strip(), count=1, flags=re.IGNORECASE)
    raw = raw.split("-", 1)[0]
    parts = raw.split(".")
    nums = [_js_number(p) for p in parts]

    def seg(index: int, default: int) -> int:
        n = nums[index] if index < len(nums) else float("nan")
        if not math.isfinite(n):
            return default
        return max(0, math.floor(n))

    return seg(0, 1), seg(1, 0), seg(2, 0)


def _normalize_version_triple(triple: tuple[int, int, int]) -> tuple[int, int, int]:
    """upstream: marketplace-validate.ts:79-90 十进制进位（1.0.9→1.1.0）。"""
    major, minor, patch = triple
    while patch >= 10:
        patch -= 10
        minor += 1
    while minor >= 10:
        minor -= 10
        major += 1
    return major, minor, patch


def _format_version_triple(triple: tuple[int, int, int]) -> str:
    # upstream: marketplace-validate.ts:92-95
    major, minor, patch = _normalize_version_triple(triple)
    return f"{major}.{minor}.{patch}"


def bump_marketplace_version(current: str | None) -> str:
    """upstream: marketplace-validate.ts:101-110；空白/非法→1.0.0，否则 patch+1 进位。"""
    if not current or not current.strip():
        return INITIAL_MARKETPLACE_VERSION
    major, minor, patch = _normalize_version_triple(_parse_version_triple(current))
    return _format_version_triple((major, minor, patch + 1))


def compare_marketplace_versions(a: str, b: str) -> int:
    """upstream: marketplace-validate.ts:116-124；负/0/正。"""
    pa = _normalize_version_triple(_parse_version_triple(a))
    pb = _normalize_version_triple(_parse_version_triple(b))
    if pa[0] != pb[0]:
        return pa[0] - pb[0]
    if pa[1] != pb[1]:
        return pa[1] - pb[1]
    return pa[2] - pb[2]


# ---- 颜色与封面 ----


def _parse_primary_color(value: Any) -> Any:
    # upstream: marketplace-validate.ts:126-135；三态 _UNSET/None/str
    if value is _UNSET:
        return _UNSET
    if value is None or value == "":
        return None
    color = _trim_string(value, 16)
    if not color or not _HEX_COLOR_RE.match(color):
        return None
    return color


def _parse_cover_url(value: Any) -> Any:
    """upstream: marketplace-validate.ts:137-150；仅接受 http/https。"""
    cover = _optional_trim_string(value, MAX_COVER_URL_LENGTH)
    if cover is _UNSET or cover is None:
        return cover
    # urllib 对 https?: 之外协议的判定与 JS URL 基本一致；相对串 netloc 为空
    try:
        parsed = urlparse(cover)
    except ValueError:
        return None
    if parsed.scheme not in ("https", "http") or not parsed.netloc:
        return None
    return cover


# ---- CSS 与样例 ----


def validate_theme_css(css: str) -> ValidateResult[str]:
    """upstream: marketplace-validate.ts:152-160；字节→@import→外链 顺序固定。"""
    if _byte_length(css) > MAX_THEME_CSS_BYTES:
        return ValidateResult.failure("payload_too_large")
    if _CSS_IMPORT_RE.search(css):
        return ValidateResult.failure("css_import_forbidden")
    if _CSS_EXTERNAL_URL_RE.search(css):
        return ValidateResult.failure("css_external_url_forbidden")
    return ValidateResult.success(css)


def parse_sample_markdown(value: Any) -> ValidateResult[Any]:
    """upstream: marketplace-validate.ts:163-174；value 为 _UNSET/None/str 三态。"""
    if value is _UNSET:
        return ValidateResult.success(_UNSET)
    if value is None or value == "":
        return ValidateResult.success(None)
    if not isinstance(value, str):
        return ValidateResult.failure("invalid_sample_markdown")
    if _byte_length(value) > MAX_SAMPLE_MARKDOWN_BYTES:
        return ValidateResult.failure("payload_too_large")
    trimmed = value.strip()
    return ValidateResult.success(trimmed or None)


# ---- 组件 ----


def _is_prop_def(raw: Any) -> bool:
    # upstream: marketplace-validate.ts:176-190
    if not raw or not isinstance(raw, dict):
        return False
    name = raw.get("name", _UNSET)
    if not isinstance(name, str) or not name.strip():
        return False
    prop_type = raw.get("type", _UNSET)
    if prop_type is not _UNSET and prop_type not in (
        "string",
        "number",
        "boolean",
        "array",
    ):
        return False
    return True


def validate_component_payload(component: Any) -> ValidateResult[str]:
    """upstream: marketplace-validate.ts:192-223；返回紧凑 JSON 字符串。"""
    if not isinstance(component, dict):
        return ValidateResult.failure("invalid_component")

    name = _trim_string(component.get("name", _UNSET), MAX_NAME_LENGTH)
    if not name or not _PASCAL_CASE_RE.match(name):
        return ValidateResult.failure("invalid_component_name")

    template_raw = component.get("template", _UNSET)
    template = template_raw if isinstance(template_raw, str) else ""
    if not template.strip():
        return ValidateResult.failure("invalid_component_template")

    if (
        _DANGEROUS_TAG_RE.search(template)
        or _EVENT_HANDLER_RE.search(template)
        or _JS_URL_RE.search(template)
    ):
        return ValidateResult.failure("unsafe_component_template")

    props = component.get("props", _UNSET)
    if not isinstance(props, list) or not all(_is_prop_def(p) for p in props):
        return ValidateResult.failure("invalid_component_props")

    # upstream: marketplace-validate.ts:209-217 字段顺序 name/description/template/props/example
    payload_obj: dict[str, Any] = {
        "name": name,
        "description": (
            component["description"].strip()[:MAX_DESCRIPTION_LENGTH]
            if isinstance(component.get("description", _UNSET), str)
            else ""
        ),
        "template": template,
        "props": props,
    }
    example = component.get("example", _UNSET)
    if isinstance(example, str):
        payload_obj["example"] = example

    payload = json.dumps(payload_obj, ensure_ascii=False, separators=(",", ":"))
    if _byte_length(payload) > MAX_COMPONENT_JSON_BYTES:
        return ValidateResult.failure("payload_too_large")
    return ValidateResult.success(payload)


# ---- 发布/更新归一化 ----


def _base_publish_fields(raw: dict) -> tuple[str | None, str | None, str, Any, Any]:
    """抽取 slug/name/description/cover/color；返回 (slug, name, description, cover, color)。"""
    slug = parse_slug(raw.get("slug", _UNSET))
    name = _trim_string(raw.get("name", _UNSET), MAX_NAME_LENGTH)
    description_raw = raw.get("description", _UNSET)
    description = (
        description_raw.strip()[:MAX_DESCRIPTION_LENGTH]
        if isinstance(description_raw, str)
        else ""
    )
    cover_url = _parse_cover_url(raw.get("coverUrl", _UNSET))
    primary_color = _parse_primary_color(raw.get("primaryColor", _UNSET))
    return slug, name, description, cover_url, primary_color


def validate_publish_theme(body: Any) -> ValidateResult[dict]:
    """upstream: marketplace-validate.ts:237-288。"""
    if not isinstance(body, dict):
        return ValidateResult.failure("invalid_body")

    slug, name, description, cover_url, primary_color = _base_publish_fields(body)
    if not slug:
        return ValidateResult.failure("invalid_slug")
    if not name:
        return ValidateResult.failure("invalid_name")

    raw_cover = body.get("coverUrl", _UNSET)
    if cover_url is None and raw_cover is not _UNSET and raw_cover is not None and raw_cover != "":
        return ValidateResult.failure("invalid_cover_url")

    raw_color = body.get("primaryColor", _UNSET)
    if primary_color is None and raw_color is not _UNSET and raw_color is not None and raw_color != "":
        return ValidateResult.failure("invalid_primary_color")

    sample_result = parse_sample_markdown(body.get("sampleMarkdown", _UNSET))
    if not sample_result.ok:
        return ValidateResult.failure(sample_result.error)
    sample_markdown = None if sample_result.value is _UNSET else sample_result.value

    css = body.get("css", _UNSET)
    if not isinstance(css, str) or not css.strip():
        return ValidateResult.failure("invalid_css")
    css_result = validate_theme_css(css)
    if not css_result.ok:
        return ValidateResult.failure(css_result.error)

    return ValidateResult.success(
        {
            "type": "theme",
            "slug": slug,
            "name": name,
            "description": description,
            "version": INITIAL_MARKETPLACE_VERSION,
            "coverUrl": cover_url if cover_url is not _UNSET else None,
            "primaryColor": primary_color if primary_color is not _UNSET else None,
            "sampleMarkdown": sample_markdown,
            "payload": css_result.value,
        }
    )


def validate_publish_component(body: Any) -> ValidateResult[dict]:
    """upstream: marketplace-validate.ts:290-332。"""
    if not isinstance(body, dict):
        return ValidateResult.failure("invalid_body")

    slug, name, description, cover_url, _ = _base_publish_fields(body)
    if not slug:
        return ValidateResult.failure("invalid_slug")
    if not name:
        return ValidateResult.failure("invalid_name")

    raw_cover = body.get("coverUrl", _UNSET)
    if cover_url is None and raw_cover is not _UNSET and raw_cover is not None and raw_cover != "":
        return ValidateResult.failure("invalid_cover_url")

    component = body.get("component", _UNSET)
    if not isinstance(component, dict):
        return ValidateResult.failure("invalid_component")

    payload_result = validate_component_payload(component)
    if not payload_result.ok:
        return ValidateResult.failure(payload_result.error)

    return ValidateResult.success(
        {
            "type": "component",
            "slug": slug,
            "name": name,
            "description": description,
            "version": INITIAL_MARKETPLACE_VERSION,
            "coverUrl": cover_url if cover_url is not _UNSET else None,
            "primaryColor": None,
            "sampleMarkdown": None,
            "payload": payload_result.value,
        }
    )


def validate_update(
    item_type: str, body: Any, current_version: str | None = None
) -> ValidateResult[dict]:
    """upstream: marketplace-validate.ts:344-418；客户端 version 恒被忽略，服务端自增。"""
    if not isinstance(body, dict):
        return ValidateResult.failure("invalid_body")

    result: dict[str, Any] = {}

    name_raw = body.get("name", _UNSET)
    if name_raw is not _UNSET:
        name = _trim_string(name_raw, MAX_NAME_LENGTH)
        if not name:
            return ValidateResult.failure("invalid_name")
        result["name"] = name

    description_raw = body.get("description", _UNSET)
    if description_raw is not _UNSET:
        if not isinstance(description_raw, str):
            return ValidateResult.failure("invalid_description")
        result["description"] = description_raw.strip()[:MAX_DESCRIPTION_LENGTH]

    # upstream: marketplace-validate.ts:368-370 服务端按当前版本自动 bump
    if current_version is not None:
        result["version"] = bump_marketplace_version(current_version)

    cover_raw = body.get("coverUrl", _UNSET)
    if cover_raw is not _UNSET:
        cover_url = _parse_cover_url(cover_raw)
        if cover_url is None and cover_raw is not None and cover_raw != "":
            return ValidateResult.failure("invalid_cover_url")
        result["coverUrl"] = cover_url if cover_url is not _UNSET else None

    if item_type == "theme":
        color_raw = body.get("primaryColor", _UNSET)
        if color_raw is not _UNSET:
            primary_color = _parse_primary_color(color_raw)
            if primary_color is None and color_raw is not None and color_raw != "":
                return ValidateResult.failure("invalid_primary_color")
            result["primaryColor"] = primary_color if primary_color is not _UNSET else None

        sample_raw = body.get("sampleMarkdown", _UNSET)
        if sample_raw is not _UNSET:
            sample_result = parse_sample_markdown(sample_raw)
            if not sample_result.ok:
                return ValidateResult.failure(sample_result.error)
            if sample_result.value is not _UNSET:
                result["sampleMarkdown"] = sample_result.value

        css_raw = body.get("css", _UNSET)
        if css_raw is not _UNSET:
            if not isinstance(css_raw, str) or not css_raw.strip():
                return ValidateResult.failure("invalid_css")
            css_result = validate_theme_css(css_raw)
            if not css_result.ok:
                return ValidateResult.failure(css_result.error)
            result["payload"] = css_result.value
    else:
        component_raw = body.get("component", _UNSET)
        if component_raw is not _UNSET:
            if not isinstance(component_raw, dict):
                return ValidateResult.failure("invalid_component")
            payload_result = validate_component_payload(component_raw)
            if not payload_result.ok:
                return ValidateResult.failure(payload_result.error)
            result["payload"] = payload_result.value

    # upstream: marketplace-validate.ts:411-415 除 version 外无任何字段→empty_update
    non_version_keys = [k for k in result if k != "version"]
    if not non_version_keys:
        return ValidateResult.failure("empty_update")

    return ValidateResult.success(result)


def parse_reject_reason(value: Any) -> str | None:
    """upstream: marketplace-validate.ts:420-426；截断 500，空白→None。"""
    if value is _UNSET or value is None or value == "":
        return None
    if not isinstance(value, str):
        return None
    return value.strip()[:MAX_REJECT_REASON_LENGTH] or None
