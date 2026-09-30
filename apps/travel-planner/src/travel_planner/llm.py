"""BYOK LLM 客户端：OpenAI 兼容 chat/completions + 行程草稿 schema 校验。

安全纪律（NFR-8）：api_key 仅注入请求头；任何异常信息、日志、返回值
不得包含密钥原文。未配置时直接抛「未配置」错误，不发起网络请求。
"""

import json
import re
from dataclasses import dataclass

import httpx

from .config import LLMConfig
from .errors import LLMError
from .models import ITEM_TYPES, MAX_COST, TIME_PATTERN

_DRAFT_ITEM_KEYS = {"type", "title", "start_time", "end_time", "location", "cost", "notes"}
_MAX_DRAFT_ITEMS = 200


@dataclass(frozen=True)
class GenerateRequest:
    """一次行程草稿生成请求。"""

    destination: str
    days: int
    start_date: str
    end_date: str
    people: int = 1
    preferences: str = ""
    budget_tier: str = ""
    currency: str = "CNY"


@dataclass(frozen=True)
class DraftItem:
    """草稿条目（导入前不落盘）。"""

    day_index: int
    type: str
    title: str
    start_time: str = ""
    end_time: str = ""
    location: str = ""
    cost: float | None = None
    notes: str = ""


_SYSTEM_PROMPT = """\
你是旅游行程规划助手。你的输出必须是严格 JSON（不要 markdown 代码围栏、不要任何解释文字），结构如下：
{{"days":[{{"day_index":1,"items":[{{"type":"sight","start_time":"09:00","end_time":"11:30","title":"景点名","location":"位置","cost":45,"notes":"衔接提示"}}]}}]}}

硬性约束：
- day_index 只能取 1 到 {days} 的整数
- type 只能是 sight/meal/lodging/transport/shopping/other 之一
- start_time/end_time 是 "HH:MM" 字符串或留空；同一条目 end_time 不得早于 start_time
- cost 是非负数字或留空（{currency} 计价，不确定就留空）
- title 必填且不超过 60 字；location 与 notes 可留空
- 每天 3~6 个条目，覆盖早中晚节奏；notes 简要给出衔接/预约/交通提示
- 只输出上述 JSON 结构，禁止添加任何其他字段
"""


class LLMClient:
    """OpenAI 兼容端点客户端（同步、单次调用）。"""

    def __init__(self, cfg: LLMConfig, transport: httpx.BaseTransport | None = None) -> None:
        self._cfg = cfg
        self._transport = transport

    def generate_draft(self, req: GenerateRequest) -> list[DraftItem]:
        if not self._cfg.configured:
            raise LLMError(
                "LLM 未配置：请在数据目录 config.yaml 填写 llm.base_url 与 llm.model，"
                "并用环境变量 TRAVEL_PLANNER_API_KEY（或配置文件）提供密钥"
            )
        payload = {
            "model": self._cfg.model,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT.format(days=req.days, currency=req.currency)},
                {"role": "user", "content": self._user_message(req)},
            ],
        }
        try:
            with httpx.Client(transport=self._transport, timeout=self._cfg.timeout) as client:
                resp = client.post(self._endpoint(), json=payload, headers=self._headers())
        except httpx.TimeoutException as exc:
            raise LLMError(
                f"LLM 请求超时（{self._cfg.timeout:.0f} 秒）：请重试，或在 config.yaml 调大 llm.timeout"
            ) from exc
        except httpx.HTTPError as exc:
            raise LLMError(
                f"LLM 端点不可达或响应异常（{type(exc).__name__}）：请检查 base_url 与网络"
            ) from exc
        if resp.status_code != 200:
            raise LLMError(
                f"LLM 端点返回 HTTP {resp.status_code}：请检查模型名称与密钥是否有效"
            )
        return parse_draft(_content_text(resp), req.days)

    def _endpoint(self) -> str:
        base = self._cfg.base_url.strip().rstrip("/")
        if base.endswith("/chat/completions"):
            return base
        return f"{base}/chat/completions"

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._cfg.api_key}"}

    def _user_message(self, req: GenerateRequest) -> str:
        lines = [
            f"目的地：{req.destination}",
            f"行程日期：{req.start_date} 至 {req.end_date}（共 {req.days} 天）",
            f"同行人数：{req.people}",
        ]
        if req.budget_tier:
            lines.append(f"预算档位：{req.budget_tier}")
        if req.preferences:
            lines.append(f"偏好与要求：{req.preferences}")
        lines.append("请按 system 约定的 JSON 结构输出完整行程草稿。")
        return "\n".join(lines)


def _content_text(resp: httpx.Response) -> str:
    try:
        data = resp.json()
        text = data["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError):
        raise LLMError("LLM 响应结构异常（缺少 choices/message/content），请检查端点兼容性") from None
    if not isinstance(text, str) or not text.strip():
        raise LLMError("LLM 返回了空内容，请重试")
    return text


def extract_json(text: str) -> dict:
    """从模型输出中提取 JSON 对象（容忍围栏与前后杂文）。"""
    fence = re.search(r"```(?:json)?\s*(.+?)```", text, re.S)
    candidate = fence.group(1) if fence else text
    start = candidate.find("{")
    if start == -1:
        raise LLMError("模型未返回 JSON 内容，请重试（可微调偏好描述）")
    end = candidate.rfind("}")
    snippet = candidate[start : end + 1] if end > start else candidate[start:]
    try:
        data = json.loads(snippet)
    except json.JSONDecodeError as exc:
        raise LLMError(
            f"模型返回的 JSON 无法解析（第 {exc.lineno} 行第 {exc.colno} 列附近），请重试"
        ) from exc
    if not isinstance(data, dict):
        raise LLMError("模型返回的 JSON 顶层必须是对象（{{\"days\": [...]}}）")
    return data


def parse_draft(text: str, days: int) -> list[DraftItem]:
    """解析并按白名单校验草稿；任何不合格结构抛中文 LLMError。"""
    data = extract_json(text)
    raw_days = data.get("days")
    if not isinstance(raw_days, list) or not raw_days:
        raise LLMError("草稿缺少 days 数组（或为空），请重试")
    unknown = set(data) - {"days"}
    if unknown:
        raise LLMError(f"草稿 JSON 存在未知字段 {sorted(unknown)}，已拒绝")
    items: list[DraftItem] = []
    for di, day in enumerate(raw_days):
        path = f"days[{di}]"
        if not isinstance(day, dict):
            raise LLMError(f"草稿 {path} 必须是对象")
        day_unknown = set(day) - {"day_index", "items"}
        if day_unknown:
            raise LLMError(f"草稿 {path} 存在未知字段 {sorted(day_unknown)}，已拒绝")
        day_index = day.get("day_index")
        if not isinstance(day_index, int) or isinstance(day_index, bool):
            raise LLMError(f"草稿 {path}.day_index 必须是整数")
        if not 1 <= day_index <= days:
            raise LLMError(f"草稿 {path}.day_index={day_index} 超出行程天数（1~{days}）")
        raw_items = day.get("items", [])
        if not isinstance(raw_items, list):
            raise LLMError(f"草稿 {path}.items 必须是列表")
        for ii, raw in enumerate(raw_items):
            items.append(_draft_item(raw, f"{path}.items[{ii}]", day_index, days))
    if not items:
        raise LLMError("草稿没有任何条目，请重试")
    if len(items) > _MAX_DRAFT_ITEMS:
        raise LLMError(f"草稿条目数超过上限（{_MAX_DRAFT_ITEMS}），已拒绝")
    return items


def _draft_item(raw: object, path: str, day_index: int, days: int) -> DraftItem:
    """校验单个草稿条目；day_index 继承自所属天（条目内不允许该字段）。"""
    if not isinstance(raw, dict):
        raise LLMError(f"草稿 {path} 必须是对象")
    unknown = set(raw) - _DRAFT_ITEM_KEYS
    if unknown:
        raise LLMError(f"草稿 {path} 存在未知字段 {sorted(unknown)}，已拒绝")
    item_type = raw.get("type")
    if item_type not in ITEM_TYPES:
        raise LLMError(f"草稿 {path}.type 必须是 {'/'.join(ITEM_TYPES)} 之一")
    title = raw.get("title")
    if not isinstance(title, str) or not title.strip() or len(title.strip()) > 60:
        raise LLMError(f"草稿 {path}.title 必填且不超过 60 字")
    start_time = _draft_time(raw.get("start_time"), f"{path}.start_time")
    end_time = _draft_time(raw.get("end_time"), f"{path}.end_time")
    if start_time and end_time and end_time < start_time:
        raise LLMError(f"草稿 {path}：结束时间不得早于开始时间")
    location = raw.get("location", "") or ""
    if not isinstance(location, str) or len(location) > 200:
        raise LLMError(f"草稿 {path}.location 必须是不超过 200 字的字符串")
    cost = raw.get("cost")
    if cost is not None:
        if isinstance(cost, bool) or not isinstance(cost, (int, float)) or not 0 <= cost <= MAX_COST:
            raise LLMError(f"草稿 {path}.cost 必须是 0~{MAX_COST:g} 的数字或留空")
        cost = float(cost)
    notes = raw.get("notes", "") or ""
    if not isinstance(notes, str) or len(notes) > 500:
        raise LLMError(f"草稿 {path}.notes 必须是不超过 500 字的字符串")
    return DraftItem(
        day_index=day_index,
        type=item_type,
        title=title.strip(),
        start_time=start_time,
        end_time=end_time,
        location=location.strip(),
        cost=cost,
        notes=notes.strip(),
    )


def _draft_time(value: object, path: str) -> str:
    if value is None or value == "":
        return ""
    if not isinstance(value, str) or not TIME_PATTERN.match(value):
        raise LLMError(f"草稿 {path} 必须是 HH:MM 格式或留空")
    return value
