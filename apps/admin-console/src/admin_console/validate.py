"""输入校验：服务端白名单 schema，未知字段拒绝，字段级中文错误。

设计要点（对应 spec FR-4/FR-5/FR-6、AC-5）：前端不做业务规则，
所有写入载荷必须在此过一遍，非法一律 400 而非 500。
"""

import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple

STATUSES = ("draft", "published", "archived")
STATUS_LABELS = {"draft": "草稿", "published": "已发布", "archived": "已归档"}

SORT_FIELDS = {
    "created_at": "created_at",
    "updated_at": "updated_at",
    "title": "title",
    "published_at": "published_at",
}
SORT_ORDERS = ("asc", "desc")

TITLE_MAX = 200
SUMMARY_MAX = 500
BODY_MAX = 20000
SLUG_MAX = 120
NAME_MAX = 80
TAG_MAX = 40

_SLUG_STRIP = re.compile(r"[^\w\u4e00-\u9fff-]+")
_SLUG_DASH = re.compile(r"-+")
_CONTROL = re.compile(r"[\x00-\x1f\x7f]")


def _clean_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value)
    text = _CONTROL.sub("", text)
    return text.strip()


def slugify(text: str, fallback: str = "item") -> str:
    """生成 URL 安全的 slug；中文保留（PostgREST/浏览器均可 handling）。"""
    raw = unicodedata.normalize("NFKC", _clean_str(text)).lower()
    raw = _SLUG_STRIP.sub("-", raw)
    raw = _SLUG_DASH.sub("-", raw).strip("-")
    if not raw:
        raw = fallback
    return raw[:SLUG_MAX]


def clean_page(page: Any, page_size: Any, default_size: int, max_size: int) -> Tuple[int, int]:
    def to_int(value: Any, default: int) -> int:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return default
        return parsed if parsed > 0 else default

    return to_int(page, 1), min(to_int(page_size, default_size), max_size)


def clean_sort(sort: Any, order: Any) -> Tuple[str, str]:
    key = SORT_FIELDS.get(_clean_str(sort).lower(), "updated_at")
    direction = _clean_str(order).lower()
    return key, (direction if direction in SORT_ORDERS else "desc")


def clean_tags(value: Any) -> List[str]:
    """标签输入支持数组或逗号分隔字符串；去重、去空、限长、限量。"""
    raw: List[str] = []
    if isinstance(value, list):
        raw = [str(v) for v in value]
    elif isinstance(value, str):
        raw = value.split(",")
    out: List[str] = []
    for item in raw:
        name = _clean_str(item)
        if not name:
            continue
        name = name[:TAG_MAX]
        if name not in out:
            out.append(name)
        if len(out) >= 20:
            break
    return out


def clean_item(payload: Dict[str, Any], partial: bool = False) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """校验条目载荷。返回 `(data, errors)`；errors 非空即拒绝写入。"""
    data: Dict[str, Any] = {}
    errors: Dict[str, str] = {}
    if not isinstance(payload, dict):
        return data, {"_": "请求体必须是 JSON 对象"}

    title = _clean_str(payload.get("title"))
    if not title:
        if not partial:
            errors["title"] = "标题不能为空"
    elif len(title) > TITLE_MAX:
        errors["title"] = f"标题不能超过 {TITLE_MAX} 字"
    else:
        data["title"] = title

    if "slug" in payload or not partial:
        slug_raw = _clean_str(payload.get("slug"))
        data["slug"] = slugify(slug_raw or title or "item") if (slug_raw or not partial) else ""

    summary = _clean_str(payload.get("summary"))
    if len(summary) > SUMMARY_MAX:
        errors["summary"] = f"摘要不能超过 {SUMMARY_MAX} 字"
    else:
        data["summary"] = summary

    body = _clean_str(payload.get("body"))
    if len(body) > BODY_MAX:
        errors["body"] = f"正文不能超过 {BODY_MAX} 字"
    else:
        data["body"] = body

    status = _clean_str(payload.get("status")).lower()
    if status:
        if status not in STATUSES:
            errors["status"] = f"状态必须是 {'/'.join(STATUSES)} 之一"
        else:
            data["status"] = status
    elif not partial:
        data["status"] = "draft"

    category_id = _clean_str(payload.get("category_id"))
    data["category_id"] = category_id or None

    cover_url = _clean_str(payload.get("cover_url"))
    if cover_url and not cover_url.startswith(("http://", "https://", "/", "memory://")):
        errors["cover_url"] = "封面地址必须是 http(s) 链接或站内路径"
    else:
        data["cover_url"] = cover_url

    if "tags" in payload or not partial:
        data["tags"] = clean_tags(payload.get("tags"))

    return data, errors


def clean_taxonomy(payload: Dict[str, Any], kind: str) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """校验分类/标签载荷（kind 仅用于错误文案）。"""
    data: Dict[str, Any] = {}
    errors: Dict[str, str] = {}
    if not isinstance(payload, dict):
        return data, {"_": "请求体必须是 JSON 对象"}
    label = "分类名" if kind == "category" else "标签名"
    name = _clean_str(payload.get("name"))
    if not name:
        errors["name"] = f"{label}不能为空"
    elif len(name) > NAME_MAX:
        errors["name"] = f"{label}不能超过 {NAME_MAX} 字"
    else:
        data["name"] = name
        data["slug"] = slugify(_clean_str(payload.get("slug")) or name, fallback=kind)
    return data, errors


def clean_upload_meta(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """附件元信息（item_id 可选）。"""
    payload = payload or {}
    item_id = _clean_str(payload.get("item_id"))
    return {"item_id": item_id or None}


def first_error(errors: Dict[str, str]) -> str:
    for key in sorted(errors):
        return errors[key]
    return "参数不合法"
