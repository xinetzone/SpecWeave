"""FastAPI 应用工厂：SSR 路由、模板渲染、导入导出与 AI 生成链路。

全部页面为服务端渲染（Jinja2 自动转义）；全部 POST 走 CSRF 依赖。
错误统一走受控异常处理器，中文信息、无堆栈泄露。
"""

import json
import logging
from datetime import date
from pathlib import Path
from typing import Callable

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from ..config import LLMConfig
from ..domain import (
    budget_summary,
    day_count,
    day_views,
    packing_progress,
    today_day_index,
    unfinished_count,
)
from ..errors import LLMError, StorageError, TravelPlannerError, ValidationError
from ..llm import GenerateRequest, LLMClient
from ..models import (
    ITEM_TYPE_LABELS,
    ITEM_TYPES,
    MAX_DAYS,
    TRIP_STATUS_LABELS,
    TRIP_STATUSES,
    Item,
    PackingItem,
    Trip,
    new_id,
)
from ..storage import TripStore
from .security import CSRF_FIELD, csrf_protect, install_security

logger = logging.getLogger("travel_planner")

_WEB_DIR = Path(__file__).parent
_POST = {"dependencies": [Depends(csrf_protect)]}

_IMPORT_WRAPPER_KEYS = {"format", "version", "trips"}


def fmt_money(value) -> str:
    """金额展示：整数不带小数，千分位分组。"""
    if value is None:
        return "—"
    value = float(value)
    return f"{int(value):,}" if value.is_integer() else f"{value:,.2f}"


def _to_int(raw: str, field_name: str, *, minimum: int, maximum: int) -> int:
    raw = (raw or "").strip()
    try:
        value = int(raw)
    except ValueError:
        raise ValidationError(f"{field_name}必须是整数") from None
    if not minimum <= value <= maximum:
        raise ValidationError(f"{field_name}必须在 {minimum} ~ {maximum} 之间")
    return value


def _to_cost(raw: str, field_name: str = "费用") -> float | None:
    raw = (raw or "").strip()
    if not raw:
        return None
    try:
        value = float(raw)
    except ValueError:
        raise ValidationError(f"{field_name}必须是数字（如 45 或 45.5）") from None
    return value


def create_app(
    store: TripStore,
    llm_cfg: LLMConfig,
    llm_client_factory: Callable[[], LLMClient] | None = None,
) -> FastAPI:
    """构建 travel-planner Web 应用。

    ``llm_client_factory`` 供测试注入 mock 客户端；默认按 ``llm_cfg`` 构造。
    """
    app = FastAPI(title="travel-planner", docs_url=None, redoc_url=None, openapi_url=None)
    install_security(app)
    templates = Jinja2Templates(directory=str(_WEB_DIR / "templates"))
    templates.env.globals.update(
        ITEM_TYPE_LABELS=ITEM_TYPE_LABELS,
        TRIP_STATUS_LABELS=TRIP_STATUS_LABELS,
        ITEM_TYPES=ITEM_TYPES,
        TRIP_STATUSES=TRIP_STATUSES,
        fmt_money=fmt_money,
    )
    app.mount("/static", StaticFiles(directory=str(_WEB_DIR / "static")), name="static")

    if llm_client_factory is None:
        llm_client_factory = lambda: LLMClient(llm_cfg)  # noqa: E731

    # ------------------------------------------------------------- 渲染辅助
    def render(request: Request, template: str, status_code: int = 200, **ctx):
        context = {
            "csrf_field": CSRF_FIELD,
            "csrf_token": getattr(request.state, "csrf_token", ""),
            "llm_configured": llm_cfg.configured,
            "llm_model": llm_cfg.model,
            **ctx,
        }
        return templates.TemplateResponse(request, template, context, status_code=status_code)

    def csrf_value(request: Request) -> str:
        return getattr(request.state, "csrf_token", "")

    # ------------------------------------------------------------- 异常处理
    @app.exception_handler(TravelPlannerError)
    async def controlled_error(request: Request, exc: TravelPlannerError):
        if isinstance(exc, ValidationError):
            status = 422
        elif isinstance(exc, StorageError) and "不存在" in str(exc):
            status = 404
        elif isinstance(exc, LLMError):
            status = 502
        else:
            status = 400
        back = request.headers.get("referer") or "/trips"
        return render(
            request,
            "error.html",
            status_code=status,
            message=str(exc),
            status_code_label=status,
            back_url=back,
            retry=isinstance(exc, LLMError),
        )

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException):
        return render(
            request,
            "error.html",
            status_code=exc.status_code,
            message=str(exc.detail),
            status_code_label=exc.status_code,
            back_url="/trips",
            retry=False,
        )

    @app.exception_handler(RequestValidationError)
    async def form_error(request: Request, exc: RequestValidationError):
        return render(
            request,
            "error.html",
            status_code=422,
            message="请求参数缺失或格式错误，请从应用页面重新提交",
            status_code_label=422,
            back_url="/trips",
            retry=False,
        )

    @app.exception_handler(Exception)
    async def uncontrolled_error(request: Request, exc: Exception):
        logger.exception("未受控异常")
        return render(
            request,
            "error.html",
            status_code=500,
            message="服务器内部错误，请重试；若持续出现请查看数据目录备份",
            status_code_label=500,
            back_url="/trips",
            retry=False,
        )

    # ------------------------------------------------------------- 表单解析
    def _trip_data_from_form(
        name: str, destination: str, start_date: str, end_date: str,
        currency: str, budget_total: str, status: str, notes: str,
        trip_id: str = "",
    ) -> dict:
        data = {
            "name": name,
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "currency": (currency or "CNY").strip() or "CNY",
            "budget_total": _to_cost(budget_total, "总预算"),
            "status": status or "planning",
            "notes": notes,
        }
        if trip_id:
            data["id"] = trip_id
        return data

    # ------------------------------------------------------------- 基础路由
    @app.get("/")
    def index():
        return RedirectResponse("/trips", status_code=302)

    @app.get("/trips")
    def trips_list(request: Request):
        trips = store.list_trips()
        today = date.today()
        cards = []
        for trip in trips:
            cards.append(
                {
                    "trip": trip,
                    "days": max(1, day_count(trip)),
                    "today": today_day_index(trip, today),
                    "unfinished": unfinished_count(trip),
                    "total_items": len(trip.items),
                    "packed": packing_progress(trip),
                }
            )
        return render(request, "trips.html", cards=cards, load_errors=store.load_errors)

    @app.get("/trips/new")
    def trip_new(request: Request):
        return render(request, "trip_form.html", trip=None)

    @app.post("/trips", **_POST)
    def trip_create(
        request: Request,
        name: str = Form(""),
        destination: str = Form(""),
        start_date: str = Form(""),
        end_date: str = Form(""),
        currency: str = Form("CNY"),
        budget_total: str = Form(""),
        status: str = Form("planning"),
        notes: str = Form(""),
    ):
        data = _trip_data_from_form(
            name, destination, start_date, end_date, currency,
            budget_total, status, notes,
        )
        trip = store.save(Trip.from_dict(data))
        return RedirectResponse(f"/trips/{trip.id}", status_code=303)

    @app.get("/trips/{trip_id}")
    def trip_detail(request: Request, trip_id: str):
        trip = store.load(trip_id)
        return render(
            request,
            "trip_detail.html",
            trip=trip,
            days=day_views(trip),
            budget=budget_summary(trip),
            today=today_day_index(trip, date.today()),
            unfinished=unfinished_count(trip),
            packed=packing_progress(trip),
        )

    @app.get("/trips/{trip_id}/edit")
    def trip_edit_form(request: Request, trip_id: str):
        return render(request, "trip_form.html", trip=store.load(trip_id))

    @app.post("/trips/{trip_id}/edit", **_POST)
    def trip_edit(
        request: Request,
        trip_id: str,
        name: str = Form(""),
        destination: str = Form(""),
        start_date: str = Form(""),
        end_date: str = Form(""),
        currency: str = Form("CNY"),
        budget_total: str = Form(""),
        status: str = Form("planning"),
        notes: str = Form(""),
    ):
        trip = store.load(trip_id)
        data = _trip_data_from_form(
            name, destination, start_date, end_date, currency,
            budget_total, status, notes, trip_id=trip.id,
        )
        data["items"] = trip.to_dict()["items"]
        data["packing"] = trip.to_dict()["packing"]
        data["created_at"] = trip.created_at
        store.save(Trip.from_dict(data))
        return RedirectResponse(f"/trips/{trip_id}", status_code=303)

    @app.post("/trips/{trip_id}/delete", **_POST)
    def trip_delete(request: Request, trip_id: str):
        store.delete(trip_id)
        return RedirectResponse("/trips", status_code=303)

    @app.post("/trips/{trip_id}/duplicate", **_POST)
    def trip_duplicate(request: Request, trip_id: str):
        copy = store.duplicate(trip_id)
        return RedirectResponse(f"/trips/{copy.id}", status_code=303)

    # ------------------------------------------------------------- 条目编排
    @app.post("/trips/{trip_id}/items", **_POST)
    def item_add(
        request: Request,
        trip_id: str,
        day_index: str = Form(""),
        type: str = Form("other"),
        title: str = Form(""),
        start_time: str = Form(""),
        end_time: str = Form(""),
        location: str = Form(""),
        cost: str = Form(""),
        notes: str = Form(""),
    ):
        trip = store.load(trip_id)
        data = {
            "id": new_id("i"),
            "day_index": _to_int(day_index, "第几天（day_index）", minimum=1, maximum=MAX_DAYS),
            "type": type,
            "title": title,
            "start_time": start_time,
            "end_time": end_time,
            "location": location,
            "cost": _to_cost(cost),
            "notes": notes,
        }
        trip.items.append(
            Item.from_dict(data, path="新条目", max_days=max(1, day_count(trip)))
        )
        store.save(trip)
        return RedirectResponse(f"/trips/{trip_id}", status_code=303)

    @app.get("/trips/{trip_id}/items/{item_id}/edit")
    def item_edit_form(request: Request, trip_id: str, item_id: str):
        trip = store.load(trip_id)
        item = _find_item(trip, item_id)
        return render(
            request, "item_edit.html", trip=trip, item=item, days_max=max(1, day_count(trip))
        )

    @app.post("/trips/{trip_id}/items/{item_id}/edit", **_POST)
    def item_edit(
        request: Request,
        trip_id: str,
        item_id: str,
        day_index: str = Form(""),
        type: str = Form("other"),
        title: str = Form(""),
        start_time: str = Form(""),
        end_time: str = Form(""),
        location: str = Form(""),
        cost: str = Form(""),
        notes: str = Form(""),
    ):
        trip = store.load(trip_id)
        index = _find_item_index(trip, item_id)
        data = {
            "id": item_id,
            "day_index": _to_int(day_index, "第几天（day_index）", minimum=1, maximum=MAX_DAYS),
            "type": type,
            "title": title,
            "start_time": start_time,
            "end_time": end_time,
            "location": location,
            "cost": _to_cost(cost),
            "notes": notes,
            "done": trip.items[index].done,
            "source": trip.items[index].source,
        }
        trip.items[index] = Item.from_dict(
            data, path="条目修改", max_days=max(1, day_count(trip))
        )
        store.save(trip)
        return RedirectResponse(f"/trips/{trip_id}", status_code=303)

    @app.post("/trips/{trip_id}/items/{item_id}/delete", **_POST)
    def item_delete(request: Request, trip_id: str, item_id: str):
        trip = store.load(trip_id)
        trip.items.pop(_find_item_index(trip, item_id))
        store.save(trip)
        return RedirectResponse(f"/trips/{trip_id}", status_code=303)

    @app.post("/trips/{trip_id}/items/{item_id}/move", **_POST)
    def item_move(request: Request, trip_id: str, item_id: str, direction: str = Form("up")):
        trip = store.load(trip_id)
        index = _find_item_index(trip, item_id)
        same_day = [i for i, it in enumerate(trip.items) if it.day_index == trip.items[index].day_index]
        pos = same_day.index(index)
        if direction == "up" and pos > 0:
            other = same_day[pos - 1]
        elif direction == "down" and pos < len(same_day) - 1:
            other = same_day[pos + 1]
        else:
            return RedirectResponse(f"/trips/{trip_id}", status_code=303)
        trip.items[index], trip.items[other] = trip.items[other], trip.items[index]
        store.save(trip)
        return RedirectResponse(f"/trips/{trip_id}", status_code=303)

    @app.post("/trips/{trip_id}/items/{item_id}/toggle", **_POST)
    def item_toggle(request: Request, trip_id: str, item_id: str):
        trip = store.load(trip_id)
        index = _find_item_index(trip, item_id)
        trip.items[index].done = not trip.items[index].done
        store.save(trip)
        return RedirectResponse(f"/trips/{trip_id}", status_code=303)

    # ------------------------------------------------------------- 打包清单
    @app.post("/trips/{trip_id}/packing", **_POST)
    def packing_add(
        request: Request, trip_id: str, name: str = Form(""), quantity: str = Form("1"),
    ):
        trip = store.load(trip_id)
        trip.packing.append(
            PackingItem.from_dict(
                {
                    "id": new_id("p"),
                    "name": name,
                    "quantity": _to_int(quantity, "数量", minimum=1, maximum=999),
                },
                path="新清单条目",
            )
        )
        store.save(trip)
        return RedirectResponse(f"/trips/{trip_id}", status_code=303)

    @app.post("/trips/{trip_id}/packing/{pack_id}/toggle", **_POST)
    def packing_toggle(request: Request, trip_id: str, pack_id: str):
        trip = store.load(trip_id)
        for pack in trip.packing:
            if pack.id == pack_id:
                pack.packed = not pack.packed
                break
        else:
            raise StorageError(f"清单条目不存在：{pack_id}")
        store.save(trip)
        return RedirectResponse(f"/trips/{trip_id}", status_code=303)

    @app.post("/trips/{trip_id}/packing/{pack_id}/delete", **_POST)
    def packing_delete(request: Request, trip_id: str, pack_id: str):
        trip = store.load(trip_id)
        trip.packing = [p for p in trip.packing if p.id != pack_id]
        store.save(trip)
        return RedirectResponse(f"/trips/{trip_id}", status_code=303)

    # ------------------------------------------------------------- 导入导出
    @app.get("/trips/{trip_id}/export")
    def trip_export(request: Request, trip_id: str):
        trip = store.load(trip_id)
        content = json.dumps(trip.to_dict(), ensure_ascii=False, indent=2) + "\n"
        return Response(
            content,
            media_type="application/json",
            headers={
                "Content-Disposition": f'attachment; filename="travel-planner-{trip_id}.json"'
            },
        )

    @app.get("/export-all")
    def export_all(request: Request):
        payload = {
            "format": "travel-planner-export",
            "version": 1,
            "trips": [trip.to_dict() for trip in store.list_trips()],
        }
        content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        return Response(
            content,
            media_type="application/json",
            headers={"Content-Disposition": 'attachment; filename="travel-planner-all.json"'},
        )

    @app.get("/import")
    def import_form(request: Request):
        return render(request, "import.html")

    @app.post("/import", **_POST)
    def import_upload(request: Request, upload: UploadFile | None = File(None)):
        if upload is None or not upload.filename:
            raise ValidationError("请选择要导入的 JSON 文件")
        raw = upload.file.read()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            raise ValidationError("文件不是 UTF-8 编码的 JSON，无法导入") from None
        trips_raw, conflicts = _import_plan(store, text)
        rows = [
            {
                "name": t.get("name", ""),
                "destination": t.get("destination", ""),
                "start_date": t.get("start_date", ""),
                "end_date": t.get("end_date", ""),
                "status": t.get("status", "planning"),
                "items": len(t.get("items", [])),
                "conflict": conflict,
            }
            for t, conflict in zip(trips_raw, conflicts)
        ]
        return render(
            request, "import_preview.html", rows=rows, payload=text, filename=upload.filename
        )

    @app.post("/import/confirm", **_POST)
    def import_confirm(request: Request, payload: str = Form("")):
        trips_raw, _ = _import_plan(store, payload)
        created = []
        for data in trips_raw:
            if store.exists(data.get("id", "")):
                data = dict(data)
                data["id"] = new_id("t")
            created.append(store.save(Trip.from_dict(data)).id)
        return RedirectResponse("/trips", status_code=303)

    # ------------------------------------------------------------- AI 生成
    @app.get("/trips/{trip_id}/generate")
    def generate_form(request: Request, trip_id: str):
        trip = store.load(trip_id)
        return render(
            request,
            "generate_form.html",
            trip=trip,
            days=max(1, day_count(trip)),
            budget=fmt_money(trip.budget_total),
        )

    @app.post("/trips/{trip_id}/generate", **_POST)
    def generate(
        request: Request,
        trip_id: str,
        destination: str = Form(""),
        start_date: str = Form(""),
        end_date: str = Form(""),
        people: str = Form("1"),
        preferences: str = Form(""),
        budget_tier: str = Form(""),
    ):
        trip = store.load(trip_id)
        destination = (destination or "").strip()
        if not destination:
            raise ValidationError("目的地不能为空")
        try:
            start = date.fromisoformat((start_date or "").strip())
            end = date.fromisoformat((end_date or "").strip())
        except ValueError:
            raise ValidationError("日期格式必须为 YYYY-MM-DD 且不能为空") from None
        if end < start:
            raise ValidationError("结束日期不得早于开始日期")
        days = (end - start).days + 1
        if days > MAX_DAYS:
            raise ValidationError(f"行程天数超过上限（{MAX_DAYS} 天）")
        req = GenerateRequest(
            destination=destination,
            days=days,
            start_date=start.isoformat(),
            end_date=end.isoformat(),
            people=_to_int(people, "同行人数", minimum=1, maximum=99),
            preferences=preferences.strip(),
            budget_tier=budget_tier.strip(),
            currency=trip.currency,
        )
        draft = llm_client_factory().generate_draft(req)  # LLMError → 502 错误页
        return render(
            request, "draft_preview.html", trip=trip, draft=draft, days=day_count(trip)
        )

    @app.post("/trips/{trip_id}/import-draft", **_POST)
    async def import_draft(request: Request, trip_id: str, draft_count: str = Form("0")):
        trip = store.load(trip_id)
        days = max(1, day_count(trip))
        form = await request.form()
        count = _to_int(draft_count, "草稿条目数", minimum=0, maximum=200)
        added = 0
        for i in range(count):
            if form.get(f"di_{i}_keep") is None:
                continue
            data = {
                "id": new_id("i"),
                "day_index": _to_int(
                    str(form.get(f"di_{i}_day", "1") or "1"), "草稿第几天", minimum=1, maximum=MAX_DAYS
                ),
                "type": str(form.get(f"di_{i}_type", "other") or "other"),
                "title": str(form.get(f"di_{i}_title", "") or ""),
                "start_time": str(form.get(f"di_{i}_start_time", "") or ""),
                "end_time": str(form.get(f"di_{i}_end_time", "") or ""),
                "location": str(form.get(f"di_{i}_location", "") or ""),
                "cost": _to_cost(str(form.get(f"di_{i}_cost", "") or "")),
                "notes": str(form.get(f"di_{i}_notes", "") or ""),
                "source": "ai",
            }
            trip.items.append(
                Item.from_dict(data, path=f"草稿条目 {i + 1}", max_days=days)
            )
            added += 1
        if added:
            store.save(trip)
        return RedirectResponse(f"/trips/{trip_id}", status_code=303)

    # ------------------------------------------------------------- 健康检查
    @app.get("/health")
    def health():
        return JSONResponse({"status": "ok", "trips": store.count()})

    return app


def _find_item(trip: Trip, item_id: str) -> Item:
    for item in trip.items:
        if item.id == item_id:
            return item
    raise StorageError(f"条目不存在：{item_id}")


def _find_item_index(trip: Trip, item_id: str) -> int:
    for index, item in enumerate(trip.items):
        if item.id == item_id:
            return index
    raise StorageError(f"条目不存在：{item_id}")


def _parse_import_raw(text: str) -> list[dict]:
    """解析导入文本为已校验的行程字典列表（不落盘）。"""
    if not (text or "").strip():
        raise ValidationError("导入内容为空")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValidationError(
            f"文件不是合法 JSON（第 {exc.lineno} 行第 {exc.colno} 列附近），已拒绝导入"
        ) from exc
    if isinstance(data, dict) and "trips" in data:
        unknown = set(data) - _IMPORT_WRAPPER_KEYS
        if unknown:
            raise ValidationError(f"导入文件顶层存在未知字段 {sorted(unknown)}，已拒绝")
        trips_raw = data["trips"]
    elif isinstance(data, list):
        trips_raw = data
    elif isinstance(data, dict):
        trips_raw = [data]
    else:
        raise ValidationError("导入文件顶层必须是行程对象、行程数组或 {\"trips\": [...]} 包装")
    if not isinstance(trips_raw, list) or not trips_raw:
        raise ValidationError("导入文件中没有可导入的行程")
    result: list[dict] = []
    for i, raw in enumerate(trips_raw):
        trip = Trip.from_dict(raw, path=f"导入行程[{i + 1}]")
        result.append(trip.to_dict())
    return result


def _import_plan(store: TripStore, text: str) -> tuple[list[dict], list[bool]]:
    trips_raw = _parse_import_raw(text)
    conflicts = [store.exists(t.get("id", "")) for t in trips_raw]
    return trips_raw, conflicts


__all__ = ["create_app"]
