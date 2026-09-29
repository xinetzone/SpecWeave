"""FastAPI 应用工厂与全部页面/表单路由（单用户、仅 loopback）。"""

import secrets
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..config import Config
from ..domain.gate import ClauseUse, GateAnswers, pass_gate
from ..domain.streak import (
    next_anchor,
    section_progress,
    streak_summary,
    tracker_readiness,
    weekly_stats,
)
from ..errors import BridgeError, CheckinHubError, GateRejected, PublishError
from ..publishing.bridge import BridgeClient, HealthState
from ..publishing.publisher import PublishState, Publisher
from ..storage.checkoff import check_off
from ..storage.drafts import (
    Draft,
    list_drafts,
    load_draft,
    save_draft,
    slugify,
    transition_status,
)
from ..storage.entries import (
    ContentKind,
    ContentRecord,
    DayEntry,
    Interaction,
    load_all_entries,
    load_entry,
    save_entry,
)
from ..storage.records import (
    add_earning,
    add_interruption,
    add_review,
    load_table,
    upsert_weekly,
)
from ..storage.tracker import parse_tracker
from .security import CSRF_COOKIE, CSRF_FIELD, UNSAFE_METHODS, SingleInstanceLock, verify_post

WEB_DIR = Path(__file__).parent
TEMPLATES_DIR = WEB_DIR / "templates"

# 中文类型标签
KIND_LABELS = {"article": "专栏文章", "answer": "问题回答", "pin": "想法"}
INTERACTION_LABELS = {
    "follow": "关注",
    "comment": "评论",
    "upvote": "赞同",
    "favorite": "收藏",
    "share": "分享",
}


@dataclass
class Services:
    cfg: Config
    bridge: BridgeClient
    publisher: Publisher
    lock: SingleInstanceLock | None = None
    flash: tuple[str, str] = ("", "")  # (level, message)


def create_app(
    cfg: Config,
    *,
    bridge: BridgeClient | None = None,
    acquire_lock: bool = False,
) -> FastAPI:
    bridge_client = bridge or BridgeClient(
        endpoint=cfg.webbridge_endpoint, session=cfg.session
    )
    services = Services(cfg=cfg, bridge=bridge_client, publisher=Publisher(bridge_client))
    if acquire_lock:
        lock = SingleInstanceLock(cfg.workspace.local / ".serve.lock")
        lock.acquire_nonblocking()
        services.lock = lock

    app = FastAPI(title="知乎打卡工作台", docs_url=None, redoc_url=None, openapi_url=None)
    app.state.svc = services
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
    app.mount("/static", StaticFiles(directory=str(WEB_DIR / "static")), name="static")

    # ---------------- 中间件 ----------------

    @app.middleware("http")
    async def local_security(request: Request, call_next):
        if request.method in UNSAFE_METHODS:
            ok, reason = verify_post(request, request.cookies.get(CSRF_COOKIE))
            if not ok:
                return PlainTextResponse(f"请求被安全策略拒绝：{reason}", status_code=403)
        response = await call_next(request)
        if not request.cookies.get(CSRF_COOKIE):
            response.set_cookie(
                CSRF_COOKIE,
                secrets.token_urlsafe(32),
                httponly=True,
                samesite="lax",
                max_age=60 * 60 * 12,
            )
        return response

    def ctx(request: Request, **extra: object) -> dict[str, object]:
        data = {
            "request": request,
            "csrf_token": request.cookies.get(CSRF_COOKIE, ""),
            "today": date.today().isoformat(),
            "kind_labels": KIND_LABELS,
            "interaction_labels": INTERACTION_LABELS,
            "flash": services.flash,
        }
        services.flash = ("", "")
        data.update(extra)
        return data

    def ws():
        return services.cfg.workspace

    def redirect(route: str, level: str = "", message: str = "") -> RedirectResponse:
        services.flash = (level, message)
        return RedirectResponse(route, status_code=303)

    def render(name: str, request: Request, **extra: object):
        return templates.TemplateResponse(request, name, ctx(request, **extra))

    # ---------------- 仪表盘 ----------------

    @app.get("/")
    def dashboard(request: Request):
        doc = parse_tracker(ws().tracker)
        entries = load_all_entries(ws())
        today = date.today()
        current_week = weekly_stats(entries, today=today, week_start=cfg.week_start)[-1:]
        session = services.publisher.session
        return render(
            "dashboard.html",
            request,
            doc=doc,
            streak=streak_summary(entries, today=today, week_start=cfg.week_start),
            week=current_week[0] if current_week else None,
            anchor=next_anchor(doc, today=today, default_year=cfg.week_start.year),
            progress=section_progress(doc),
            today_entry=load_entry(ws(), today),
            readiness={r.item_id: r for r in tracker_readiness(doc, entries, today=today)},
            publish_state=session.state.value if session else "idle",
            health_states=[s.value for s in HealthState],
        )

    # ---------------- 打卡 ----------------

    @app.get("/checkin")
    def checkin_page(request: Request):
        doc = parse_tracker(ws().tracker)
        today = date.today()
        entries = load_all_entries(ws())
        grouped: dict[str, list] = {}
        for item in doc.items:
            grouped.setdefault(item.section, []).append(item)
        return render(
            "checkin.html",
            request,
            grouped=grouped,
            today_entry=load_entry(ws(), today),
            readiness={r.item_id: r for r in tracker_readiness(doc, entries, today=today)},
            kinds=list(KIND_LABELS.items()),
            interactions=list(INTERACTION_LABELS.items()),
        )

    @app.post("/checkin/entry")
    def save_day_entry(
        request: Request,
        csrf_field: str = Form(alias=CSRF_FIELD),
        day: str = Form(...),
        note: str = Form(""),
        kind: list[str] = Form(default=[]),
        char_count: list[int] = Form(default=[]),
        url: list[str] = Form(default=[]),
        question_url: list[str] = Form(default=[]),
        draft_slug: list[str] = Form(default=[]),
        interaction: list[str] = Form(default=[]),
        interaction_target: list[str] = Form(default=[]),
    ):
        _guard_form(request, csrf_field)
        d = date.fromisoformat(day)
        entry = DayEntry(day=day, note=note.strip())
        for i, k in enumerate(kind):
            entry.contents.append(
                ContentRecord(
                    kind=k,
                    char_count=int(char_count[i]) if i < len(char_count) else 0,
                    url=(url[i] if i < len(url) else "").strip(),
                    question_url=(question_url[i] if i < len(question_url) else "").strip(),
                    draft_slug=(draft_slug[i] if i < len(draft_slug) else "").strip(),
                )
            )
        # 勾选框按固定五序提交子集，target 输入框恒为五项，按顺序对齐
        fixed_order = ["follow", "comment", "upvote", "favorite", "share"]
        target_by_kind = {
            fixed_order[i]: (interaction_target[i] if i < len(interaction_target) else "")
            for i in range(len(fixed_order))
        }
        for kind_value in interaction:
            entry.interactions.append(
                Interaction(kind=kind_value, target=target_by_kind.get(kind_value, "").strip())
            )
        # 保留当日已有的过门记录
        entry.gates = load_entry(ws(), d).gates
        save_entry(ws(), entry)
        return redirect("/checkin", "ok", f"{day} 打卡已保存")

    @app.post("/checkin/checkoff")
    def do_checkoff(
        request: Request,
        csrf_field: str = Form(alias=CSRF_FIELD),
        item_id: str = Form(...),
        day: str = Form(...),
    ):
        _guard_form(request, csrf_field)
        try:
            result = check_off(ws(), item_id, day)
        except CheckinHubError as exc:
            return redirect("/checkin", "error", str(exc))
        msg = (
            f"已勾选 {item_id}（{result.date_text}），备份：{result.backup_path.name}"
            if result.changed
            else f"{item_id}：{result.note}"
        )
        return redirect("/checkin", "ok" if result.changed else "info", msg)

    # ---------------- 记录 ----------------

    @app.get("/records")
    def records_page(request: Request):
        return render(
            "records.html",
            request,
            earnings=load_table(ws(), "earnings"),
            weekly=load_table(ws(), "weekly"),
            interruptions=load_table(ws(), "interruptions"),
            reviews=load_table(ws(), "reviews"),
        )

    @app.post("/records/earning")
    def add_earning_route(
        request: Request,
        csrf_field: str = Form(alias=CSRF_FIELD),
        day: str = Form(...),
        action: str = Form(...),
        salt_raw: str = Form(...),
        note: str = Form(""),
    ):
        _guard_form(request, csrf_field)
        try:
            add_earning(ws(), day=day, action=action, salt_raw=salt_raw, note=note)
        except CheckinHubError as exc:
            return redirect("/records", "error", str(exc))
        return redirect("/records", "ok", "盐粒到账已照抄登记")

    @app.post("/records/weekly")
    def add_weekly_route(
        request: Request,
        csrf_field: str = Form(alias=CSRF_FIELD),
        week_id: str = Form(...),
        start: str = Form(...),
        end: str = Form(...),
        answers: int = Form(...),
        pins: int = Form(...),
        confirmed: int = Form(...),
        note: str = Form(""),
    ):
        _guard_form(request, csrf_field)
        try:
            upsert_weekly(
                ws(),
                week_id=week_id,
                start=start,
                end=end,
                answers=answers,
                pins=pins,
                confirmed=confirmed,
                note=note,
            )
        except CheckinHubError as exc:
            return redirect("/records", "error", str(exc))
        return redirect("/records", "ok", f"{week_id} 周核对已保存")

    @app.post("/records/interruption")
    def add_interruption_route(
        request: Request,
        csrf_field: str = Form(alias=CSRF_FIELD),
        start_day: str = Form(...),
        days: int = Form(...),
        reason: str = Form(...),
    ):
        _guard_form(request, csrf_field)
        try:
            add_interruption(ws(), start_day=start_day, days=days, reason=reason)
        except CheckinHubError as exc:
            return redirect("/records", "error", str(exc))
        return redirect("/records", "ok", "中断已登记")

    @app.post("/records/review")
    def add_review_route(
        request: Request,
        csrf_field: str = Form(alias=CSRF_FIELD),
        day: str = Form(...),
        salt_total: int = Form(...),
        decision: str = Form(...),
        reason: str = Form(...),
    ):
        _guard_form(request, csrf_field)
        try:
            add_review(
                ws(),
                day=day,
                salt_total=salt_total,
                decision=decision,
                reason=reason,
            )
        except CheckinHubError as exc:
            return redirect("/records", "error", str(exc))
        return redirect("/records", "ok", "周期复核已保存（F-059 折算仅作估算标注）")

    # ---------------- 草稿 ----------------

    @app.get("/drafts")
    def drafts_page(request: Request):
        return render("drafts.html", request, drafts=list_drafts(ws()))

    @app.get("/drafts/{slug}")
    def draft_edit_page(request: Request, slug: str):
        draft = load_draft(ws(), slug)
        return render("draft_edit.html", request, draft=draft, kinds=list(KIND_LABELS.items()))

    @app.post("/drafts/save")
    def save_draft_route(
        request: Request,
        csrf_field: str = Form(alias=CSRF_FIELD),
        slug: str = Form(""),
        title: str = Form(""),
        kind: str = Form(...),
        body: str = Form(""),
        question_url: str = Form(""),
    ):
        _guard_form(request, csrf_field)
        final_slug = slug.strip() or slugify(title or kind)
        try:
            existing = load_draft(ws(), final_slug)
            draft = Draft(
                slug=final_slug,
                title=title,
                kind=kind,
                body=body,
                question_url=question_url,
                status=existing.status,
                created_at=existing.created_at,
                published_url=existing.published_url,
            )
        except CheckinHubError:
            draft = Draft(
                slug=final_slug, title=title, kind=kind, body=body, question_url=question_url
            )
        save_draft(ws(), draft)
        return redirect(f"/drafts/{final_slug}", "ok", "草稿已保存")

    @app.post("/drafts/{slug}/ready")
    def mark_ready_route(
        request: Request, slug: str, csrf_field: str = Form(alias=CSRF_FIELD)
    ):
        _guard_form(request, csrf_field)
        draft = load_draft(ws(), slug)
        try:
            draft.status = transition_status(draft.status, "ready")
            save_draft(ws(), draft)
        except CheckinHubError as exc:
            return redirect(f"/drafts/{slug}", "error", str(exc))
        return redirect(f"/drafts/{slug}", "ok", "草稿已标记 ready，可进发布向导")

    # ---------------- 发布向导 ----------------

    @app.get("/publish")
    def publish_page(request: Request, slug: str = ""):
        selected = load_draft(ws(), slug) if slug else None
        session = services.publisher.session
        health = None
        if session is not None:
            health = services.last_health if hasattr(services, "last_health") else None
        return render(
            "publish.html",
            request,
            drafts=list_drafts(ws()),
            selected=selected,
            session=session,
            health=health,
            fill_outcome=getattr(services, "last_fill", None),
            clauses=list(ClauseUse),
            publish_states=PublishState.__members__.keys(),
        )

    @app.post("/publish/gate")
    def publish_gate_route(
        request: Request,
        csrf_field: str = Form(alias=CSRF_FIELD),
        slug: str = Form(...),
        deletion_tested: str = Form(""),
        deletion_note: str = Form(""),
        ratio_selfcheck: str = Form(""),
        ratio_note: str = Form(""),
        clauses: list[str] = Form(default=[]),
        edge_confirmed: str = Form(""),
        edge_note: str = Form(""),
    ):
        _guard_form(request, csrf_field)
        draft = load_draft(ws(), slug)
        answers = GateAnswers(
            deletion_tested=bool(deletion_tested),
            deletion_note=deletion_note,
            ratio_selfcheck=bool(ratio_selfcheck),
            ratio_note=ratio_note,
            clauses=tuple(clauses),
            edge_confirmed=bool(edge_confirmed),
            edge_note=edge_note,
            kind=draft.kind,
            draft_slug=draft.slug,
        )
        try:
            result = pass_gate(ws(), answers)
            draft.status = transition_status(draft.status, "ready")
            save_draft(ws(), draft)
            services.publisher.begin(load_draft(ws(), slug), gate_at=result.at)
        except GateRejected as exc:
            return PlainTextResponse(f"固定门未通过：\n{exc}", status_code=422)
        except (CheckinHubError, PublishError) as exc:
            return PlainTextResponse(f"无法进入发布：{exc}", status_code=409)
        return redirect(f"/publish?slug={slug}", "ok", "固定门通过，已进入填充阶段")

    @app.post("/publish/health")
    def publish_health_route(
        request: Request, csrf_field: str = Form(alias=CSRF_FIELD), slug: str = Form("")
    ):
        _guard_form(request, csrf_field)
        report = services.bridge.health()
        services.last_health = report
        return JSONResponse(
            {"state": report.state.value, "message": report.message, "detail": report.detail}
        )

    @app.post("/publish/fill")
    def publish_fill_route(
        request: Request, csrf_field: str = Form(alias=CSRF_FIELD), slug: str = Form(...)
    ):
        _guard_form(request, csrf_field)
        session = services.publisher.session
        if session is None or session.state != PublishState.GATE_PASSED:
            return PlainTextResponse("必须先通过固定门才能开始填充。", status_code=409)
        if slug != session.draft_slug:
            return PlainTextResponse(
                "填充草稿与过门草稿不一致：请重新对当前草稿通过固定门。", status_code=409
            )
        draft = load_draft(ws(), slug)
        outcome = services.publisher.fill(draft)
        services.last_fill = outcome
        if outcome.state == PublishState.FILLED:
            services.publisher.hand_to_human()
        current_state = services.publisher.session.state.value
        return JSONResponse(
            {
                "state": current_state,
                "detail": outcome.detail,
                "instruction": (
                    "请在浏览器中由你本人完成发布，然后点「我已发布」。"
                    if outcome.state == PublishState.FILLED
                    else outcome.detail.get("instruction", "")
                ),
            }
        )

    @app.post("/publish/confirm")
    def publish_confirm_route(
        request: Request,
        csrf_field: str = Form(alias=CSRF_FIELD),
        slug: str = Form(...),
        pin_image: str = Form(""),
    ):
        _guard_form(request, csrf_field)
        session = services.publisher.session
        if session is None or session.state != PublishState.AWAITING_HUMAN:
            return PlainTextResponse("当前不在等待本人发布的阶段，无法确认。", status_code=409)
        if slug != session.draft_slug:
            return PlainTextResponse(
                "确认草稿与过门草稿不一致：请重新对当前草稿通过固定门。", status_code=409
            )
        if session.kind == ContentKind.PIN and pin_image not in ("inserted", "none"):
            return PlainTextResponse(
                "想法须先显式确认「图片已插入」或「无需图片」才能确认发布。", status_code=422
            )
        try:
            result = services.publisher.confirm(ws())
        except PublishError as exc:
            return PlainTextResponse(str(exc), status_code=409)
        except BridgeError as exc:
            return PlainTextResponse(f"读取浏览器状态失败：{exc}", status_code=502)
        services.publisher.session = None
        return JSONResponse(
            {
                "state": result.state.value,
                "published_url": result.published_url,
                "screenshot": result.screenshot_path,
                "content_id": result.content_id,
            }
        )

    def _guard_form(request: Request, token: str) -> None:
        cookie = request.cookies.get(CSRF_COOKIE)
        if not cookie or not token or not secrets.compare_digest(cookie, token):
            from fastapi import HTTPException

            raise HTTPException(status_code=403, detail="CSRF 令牌缺失或不匹配")

    return app
