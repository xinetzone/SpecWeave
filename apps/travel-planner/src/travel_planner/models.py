"""数据模型与校验：存储加载、导入、AI 草稿共用的唯一校验真源。

所有校验错误为 ``ValidationError``，信息含字段路径定位（中文），
未知字段一律拒绝（白名单校验，防结构漂移与注入）。
"""

import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import date, datetime

from .errors import ValidationError

ITEM_TYPES = ("sight", "meal", "lodging", "transport", "shopping", "other")
ITEM_TYPE_LABELS = {
    "sight": "景点",
    "meal": "餐饮",
    "lodging": "住宿",
    "transport": "交通",
    "shopping": "购物",
    "other": "其他",
}
TRIP_STATUSES = ("planning", "ongoing", "completed", "archived")
TRIP_STATUS_LABELS = {
    "planning": "规划中",
    "ongoing": "进行中",
    "completed": "已完成",
    "archived": "已归档",
}
ITEM_SOURCES = ("manual", "ai")

ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

MAX_NAME = 200
MAX_TITLE = 120
MAX_LONG_TEXT = 2000
MAX_COST = 10_000_000.0
MAX_DAYS = 365
MAX_ITEMS = 2000
MAX_QUANTITY = 999

_ITEM_KEYS = {
    "id", "day_index", "type", "title", "start_time", "end_time",
    "location", "cost", "notes", "done", "source",
}
_PACKING_KEYS = {"id", "name", "quantity", "packed"}
_TRIP_KEYS = {
    "id", "name", "destination", "start_date", "end_date", "currency",
    "budget_total", "status", "notes", "items", "packing",
    "created_at", "updated_at",
}


def new_id(prefix: str) -> str:
    """生成短 id（文件名安全字符集）。"""
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _check_id(value: object, path: str) -> str:
    if not isinstance(value, str) or not ID_PATTERN.match(value):
        raise ValidationError(f"{path}：id 格式不合法（只允许小写字母、数字与连字符）")
    return value


def _str_field(
    data: dict,
    key: str,
    path: str,
    *,
    default: str = "",
    max_len: int = MAX_LONG_TEXT,
    required: bool = False,
) -> str:
    if key not in data or data[key] is None:
        if required:
            raise ValidationError(f"{path}：缺少必填字段「{key}」")
        return default
    value = data[key]
    if not isinstance(value, str):
        raise ValidationError(f"{path}.{key}：必须是字符串")
    value = value.strip()
    if required and not value:
        raise ValidationError(f"{path}.{key}：不能为空")
    if len(value) > max_len:
        raise ValidationError(f"{path}.{key}：长度超过 {max_len} 字符")
    return value


def _opt_float(
    data: dict, key: str, path: str, *, minimum: float = 0.0, maximum: float = MAX_COST,
) -> float | None:
    if key not in data or data[key] is None or data[key] == "":
        return None
    value = data[key]
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{path}.{key}：必须是数字")
    value = float(value)
    if not minimum <= value <= maximum:
        raise ValidationError(f"{path}.{key}：必须在 {minimum:g} ~ {maximum:g} 之间")
    return value


def _opt_int(
    data: dict, key: str, path: str, *, default: int | None = None,
    minimum: int = 1, maximum: int = MAX_ITEMS,
) -> int | None:
    if key not in data or data[key] is None or data[key] == "":
        return default
    value = data[key]
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError(f"{path}.{key}：必须是整数")
    if not minimum <= value <= maximum:
        raise ValidationError(f"{path}.{key}：必须在 {minimum} ~ {maximum} 之间")
    return value


def _time_field(data: dict, key: str, path: str) -> str:
    value = data.get(key, "") or ""
    if not isinstance(value, str):
        raise ValidationError(f"{path}.{key}：必须是字符串（HH:MM）")
    value = value.strip()
    if value and not TIME_PATTERN.match(value):
        raise ValidationError(f"{path}.{key}：时间格式必须为 HH:MM（如 09:30），留空表示不定时")
    return value


def _date_field(data: dict, key: str, path: str, *, required: bool = False) -> str:
    value = data.get(key, "") or ""
    if not isinstance(value, str):
        raise ValidationError(f"{path}.{key}：必须是字符串（YYYY-MM-DD）")
    value = value.strip()
    if not value:
        if required:
            raise ValidationError(f"{path}.{key}：不能为空")
        return ""
    if not DATE_PATTERN.match(value):
        raise ValidationError(f"{path}.{key}：日期格式必须为 YYYY-MM-DD")
    try:
        date.fromisoformat(value)
    except ValueError:
        raise ValidationError(f"{path}.{key}：不是合法日期（{value}）") from None
    return value


def _enum_field(data: dict, key: str, path: str, allowed: tuple[str, ...], default: str) -> str:
    value = data.get(key, default)
    if value is None or value == "":
        return default
    if not isinstance(value, str) or value not in allowed:
        raise ValidationError(f"{path}.{key}：只能是 {'/'.join(allowed)} 之一")
    return value


def _bool_field(data: dict, key: str, path: str, *, default: bool = False) -> bool:
    if key not in data or data[key] is None:
        return default
    value = data[key]
    if not isinstance(value, bool):
        raise ValidationError(f"{path}.{key}：必须是布尔值")
    return value


@dataclass
class Item:
    """一天内的活动条目。"""

    id: str
    day_index: int
    type: str
    title: str
    start_time: str = ""
    end_time: str = ""
    location: str = ""
    cost: float | None = None
    notes: str = ""
    done: bool = False
    source: str = "manual"

    @classmethod
    def from_dict(cls, data: dict, path: str = "条目", *, max_days: int = MAX_DAYS) -> "Item":
        if not isinstance(data, dict):
            raise ValidationError(f"{path}：必须是对象")
        unknown = set(data) - _ITEM_KEYS
        if unknown:
            raise ValidationError(f"{path}：存在未知字段 {sorted(unknown)}")
        item_id = data.get("id") or new_id("i")
        day_index = _opt_int(data, "day_index", path, minimum=1, maximum=max_days)
        if day_index is None:
            raise ValidationError(f"{path}.day_index：缺少 day_index（1 起始的天序号）")
        item_type = _enum_field(data, "type", path, ITEM_TYPES, "other")
        title = _str_field(data, "title", path, max_len=MAX_TITLE, required=True)
        start_time = _time_field(data, "start_time", path)
        end_time = _time_field(data, "end_time", path)
        if start_time and end_time and end_time < start_time:
            raise ValidationError(f"{path}：结束时间（{end_time}）不得早于开始时间（{start_time}）")
        location = _str_field(data, "location", path, max_len=MAX_NAME)
        cost = _opt_float(data, "cost", path)
        notes = _str_field(data, "notes", path)
        done = _bool_field(data, "done", path)
        source = _enum_field(data, "source", path, ITEM_SOURCES, "manual")
        return cls(
            id=_check_id(item_id, path),
            day_index=day_index,
            type=item_type,
            title=title,
            start_time=start_time,
            end_time=end_time,
            location=location,
            cost=cost,
            notes=notes,
            done=done,
            source=source,
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PackingItem:
    """打包清单条目。"""

    id: str
    name: str
    quantity: int = 1
    packed: bool = False

    @classmethod
    def from_dict(cls, data: dict, path: str = "清单条目") -> "PackingItem":
        if not isinstance(data, dict):
            raise ValidationError(f"{path}：必须是对象")
        unknown = set(data) - _PACKING_KEYS
        if unknown:
            raise ValidationError(f"{path}：存在未知字段 {sorted(unknown)}")
        item_id = data.get("id") or new_id("p")
        name = _str_field(data, "name", path, max_len=MAX_NAME, required=True)
        quantity = _opt_int(data, "quantity", path, default=1, minimum=1, maximum=MAX_QUANTITY)
        packed = _bool_field(data, "packed", path)
        return cls(id=_check_id(item_id, path), name=name, quantity=quantity or 1, packed=packed)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Trip:
    """一次旅行的完整数据（存储与导入导出的顶层单元）。"""

    id: str
    name: str
    destination: str = ""
    start_date: str = ""
    end_date: str = ""
    currency: str = "CNY"
    budget_total: float | None = None
    status: str = "planning"
    notes: str = ""
    items: list[Item] = field(default_factory=list)
    packing: list[PackingItem] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: dict, path: str = "行程") -> "Trip":
        if not isinstance(data, dict):
            raise ValidationError(f"{path}：必须是对象")
        unknown = set(data) - _TRIP_KEYS
        if unknown:
            raise ValidationError(f"{path}：存在未知字段 {sorted(unknown)}")
        trip_id = data.get("id") or new_id("t")
        name = _str_field(data, "name", path, max_len=MAX_NAME, required=True)
        destination = _str_field(data, "destination", path, max_len=MAX_NAME)
        start_date = _date_field(data, "start_date", path)
        end_date = _date_field(data, "end_date", path)
        if start_date and end_date and end_date < start_date:
            raise ValidationError(
                f"{path}：结束日期（{end_date}）不得早于开始日期（{start_date}）"
            )
        currency = _str_field(data, "currency", path, default="CNY", max_len=8) or "CNY"
        budget_total = _opt_float(data, "budget_total", f"{path}.budget_total")
        status = _enum_field(data, "status", path, TRIP_STATUSES, "planning")
        notes = _str_field(data, "notes", path)
        raw_items = data.get("items", [])
        if not isinstance(raw_items, list):
            raise ValidationError(f"{path}.items：必须是列表")
        if len(raw_items) > MAX_ITEMS:
            raise ValidationError(f"{path}.items：条目数超过上限 {MAX_ITEMS}")
        raw_packing = data.get("packing", [])
        if not isinstance(raw_packing, list):
            raise ValidationError(f"{path}.packing：必须是列表")
        days = _days_between(start_date, end_date)
        items = [Item.from_dict(d, f"{path}.items[{i}]") for i, d in enumerate(raw_items)]
        if days:
            overflow = [it for it in items if it.day_index > days]
            if overflow:
                raise ValidationError(
                    f"{path}：条目「{overflow[0].title}」的 day_index={overflow[0].day_index} "
                    f"超出行程天数（{days} 天），请先调整日期范围或条目所属天"
                )
        packing = [
            PackingItem.from_dict(d, f"{path}.packing[{i}]") for i, d in enumerate(raw_packing)
        ]
        now = datetime.now().isoformat(timespec="seconds")
        created_at = _str_field(data, "created_at", path, default=now, max_len=40)
        updated_at = _str_field(data, "updated_at", path, default=created_at, max_len=40)
        return cls(
            id=_check_id(trip_id, path),
            name=name,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            currency=currency,
            budget_total=budget_total,
            status=status,
            notes=notes,
            items=items,
            packing=packing,
            created_at=created_at,
            updated_at=updated_at,
        )

    def to_dict(self) -> dict:
        data = asdict(self)
        return data

    def touch(self) -> None:
        self.updated_at = datetime.now().isoformat(timespec="seconds")


def _days_between(start_date: str, end_date: str) -> int:
    """行程天数；日期不全时返回 0（不校验 day_index 边界）。"""
    if not start_date or not end_date:
        return 0
    return (date.fromisoformat(end_date) - date.fromisoformat(start_date)).days + 1
