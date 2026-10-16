"""FastAPI 应用：路由、鉴权、CORS 与请求级 BYOK。

边界纪律：

- **密钥永不下发浏览器**。服务端配置读环境变量；用户在页面填的 BYOK 凭据
  随请求头进来，只活在当次请求的内存里。
- **鉴权是可选的**。``APP_TOKEN`` 未设置时不鉴权——这是为本地回环体验留的口子，
  上线必须设置，README 与部署指南都把它写成硬要求。
- **存储是注入的**。``create_app`` 接受外部传入的 store，测试才能在没有
  Supabase 的情况下把路由跑完整。
"""

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .config import LLMOverride, Settings
from .llm import LLMClient
from .models import AskIn, ExtractIn, ItemIn, ItemPatch, SummaryIn
from .pipeline import (
    answer,
    build_summary,
    capture,
    extract_highlights,
    organize_todos,
    search_items,
    tag_cloud,
)
from .store import Store, StoreError, create_store

TOKEN_HEADER = "X-App-Token"


def create_app(
    settings: Settings | None = None,
    store: Store | None = None,
    llm: LLMClient | None = None,
) -> FastAPI:
    """构建应用。三个依赖均可注入，缺省时按环境变量自动装配。"""
    settings = settings or Settings.from_env()
    store = store or create_store(settings)
    llm = llm or LLMClient(settings)

    app = FastAPI(
        title="个人信息管家 Agent",
        description="随手录入 → 自动分类/摘要/关联 → 检索、问答、重点提取、待办整理、阶段总结。",
        version=__version__,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", TOKEN_HEADER, "X-LLM-Base-Url", "X-LLM-Api-Key", "X-LLM-Model"],
    )

    def require_token(request: Request) -> None:
        """``APP_TOKEN`` 未设置 → 不鉴权（仅本地）；已设置 → 必须匹配。"""
        if not settings.app_token:
            return
        provided = request.headers.get("x-app-token", "").strip()
        authorization = request.headers.get("authorization", "").strip()
        if not provided and authorization.lower().startswith("bearer "):
            provided = authorization[7:].strip()
        if provided != settings.app_token:
            raise HTTPException(status_code=401, detail="缺少或错误的访问令牌")

    def byok(
        base_url: str | None = Header(default=None, alias="X-LLM-Base-Url"),
        api_key: str | None = Header(default=None, alias="X-LLM-Api-Key"),
        model: str | None = Header(default=None, alias="X-LLM-Model"),
    ) -> LLMOverride:
        """页面 BYOK：只在本请求内存活，不落盘、不写日志。"""
        return LLMOverride(base_url=base_url or "", api_key=api_key or "", model=model or "")

    router = APIRouter(prefix="/api", dependencies=[Depends(require_token)])

    def _guard(exc: StoreError) -> HTTPException:
        return HTTPException(status_code=503, detail=str(exc))

    @app.get("/", summary="服务信息")
    def root() -> dict:
        return {
            "service": "info-butler",
            "version": __version__,
            "storage": store.mode,
            "llm_ready": llm.available(),
        }

    @router.get("/health", summary="健康检查")
    def health(override: LLMOverride = Depends(byok)) -> dict:
        # llm_ready 要算上请求级 BYOK，否则页面填了密钥的人会一直看到
        # "模型：未接入"，而他的请求其实一直在用模型——状态徽标不能说谎。
        return {
            "status": "ok",
            "storage": store.mode,
            "llm_ready": llm.available(override),
            "llm_source": "byok" if override.active else ("server" if llm.available() else ""),
            "version": __version__,
            "auth_required": bool(settings.app_token),
        }

    @router.post("/llm/test", summary="验证页面 BYOK 凭据")
    def test_llm(override: LLMOverride = Depends(byok)) -> dict:
        """用请求级 BYOK 打一次最小探针，永久返回 200。

        它挂在 /api 路由上，因此**继承 APP_TOKEN 鉴权**：探针会真实发起一次
        模型调用，若不鉴权就等于给公网开了一个免费代理。用户填错凭据则只体现
        在响应体的 reason 里，不用状态码——那样页面就只能显示"服务器出错"。
        """
        return llm.probe(override)

    @router.get("/items", summary="列表与关键词检索")
    def list_items(
        q: str = Query(default=""),
        kind: str | None = Query(default=None),
        tag: str | None = Query(default=None),
        status: str | None = Query(default=None),
        limit: int = Query(default=50, ge=1, le=200),
    ) -> dict:
        try:
            rows = search_items(store, settings, q, kind=kind, tag=tag, status=status, limit=limit)
        except StoreError as exc:
            raise _guard(exc) from exc
        return {"items": rows, "count": len(rows), "query": q}

    @router.post("/items", status_code=201, summary="录入一条内容")
    def create_item(payload: ItemIn, override: LLMOverride = Depends(byok)) -> dict:
        try:
            return capture(store, settings, payload.model_dump(), llm=llm, override=override)
        except StoreError as exc:
            raise _guard(exc) from exc

    @router.get("/item", summary="读取单条（兼容 ?id= 形式）")
    def get_item_by_query(id: str = Query(...)) -> dict:
        try:
            row = store.get_item(id)
        except StoreError as exc:
            raise _guard(exc) from exc
        if row is None:
            raise HTTPException(status_code=404, detail="条目不存在")
        return row

    @router.get("/items/{item_id}", summary="读取单条")
    def get_item(item_id: str) -> dict:
        try:
            row = store.get_item(item_id)
        except StoreError as exc:
            raise _guard(exc) from exc
        if row is None:
            raise HTTPException(status_code=404, detail="条目不存在")
        return row

    @router.patch("/items/{item_id}", summary="局部更新")
    def patch_item(item_id: str, payload: ItemPatch) -> dict:
        try:
            row = store.update_item(
                item_id, {k: v for k, v in payload.model_dump().items() if v is not None}
            )
        except StoreError as exc:
            raise _guard(exc) from exc
        if row is None:
            raise HTTPException(status_code=404, detail="条目不存在")
        return row

    @router.delete("/items/{item_id}", summary="删除")
    def delete_item(item_id: str) -> dict:
        try:
            ok = store.delete_item(item_id)
        except StoreError as exc:
            raise _guard(exc) from exc
        return {"deleted": ok}

    @router.get("/items/{item_id}/links", summary="关联条目")
    def links(item_id: str) -> dict:
        try:
            rows = store.list_links(item_id)
        except StoreError as exc:
            raise _guard(exc) from exc
        return {"links": rows, "count": len(rows)}

    @router.post("/ask", summary="智能问答（带引用）")
    def ask(payload: AskIn, override: LLMOverride = Depends(byok)) -> dict:
        try:
            return answer(store, settings, payload.question, llm=llm, override=override, limit=payload.limit)
        except StoreError as exc:
            raise _guard(exc) from exc

    @router.post("/extract", summary="重点信息提取")
    def extract(payload: ExtractIn, override: LLMOverride = Depends(byok)) -> dict:
        try:
            return extract_highlights(
                store, settings, llm=llm, override=override, limit=payload.limit, scope=payload.scope
            )
        except StoreError as exc:
            raise _guard(exc) from exc

    @router.get("/todos", summary="待办整理")
    def todos(override: LLMOverride = Depends(byok)) -> dict:
        try:
            return organize_todos(store, settings, llm=llm, override=override)
        except StoreError as exc:
            raise _guard(exc) from exc

    @router.get("/summary", summary="历史阶段总结")
    def history(limit: int = Query(default=10, ge=1, le=50)) -> dict:
        try:
            rows = store.list_summaries(limit=limit)
        except StoreError as exc:
            raise _guard(exc) from exc
        return {"summaries": rows, "count": len(rows)}

    @router.post("/summary", summary="生成阶段总结")
    def summarize(payload: SummaryIn, override: LLMOverride = Depends(byok)) -> dict:
        try:
            return build_summary(
                store, settings, days=payload.days, llm=llm, override=override, limit=payload.limit
            )
        except StoreError as exc:
            raise _guard(exc) from exc

    @router.get("/tags", summary="标签云与统计")
    def tags() -> dict:
        try:
            return tag_cloud(store, settings)
        except StoreError as exc:
            raise _guard(exc) from exc

    app.include_router(router)
    return app
