"""FastAPI 服务层：健康检查 + 知识问答 + 静态页面托管。

静态资源由本模块显式托管——Vercel 的 Python 运行时不会像 Node 运行时那样
自动托管根目录静态文件（对抗性审查 V4），必须显式挂载，否则线上只剩 API。
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import config, llm, prompts, retrieval

MAX_QUESTION_LEN = 500
NO_HIT_ANSWER = "知识库中未检索到与该问题相关的内容，请换个说法或换一个主题试试。"

app = FastAPI(
    title="OKF 知识库问答 Agent",
    # 不在此硬编码知识包/片段规模：那会与构建产物形成第二个事实来源并逐渐失真，
    # 运行时规模一律以 /api/health 的 stats 为准。
    description="基于 SpecWeave OKF 知识包的检索增强问答服务",
    version="0.1.0",
)

if config.STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=MAX_QUESTION_LEN)
    top_k: int | None = Field(default=None, ge=1, le=20)


class Citation(BaseModel):
    index: int
    title: str
    bundle: str
    group: str
    domain: str
    path: str
    snippet: str
    score: float


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    hit_count: int
    degraded: bool
    error: str | None = None


def _to_citations(hits: list[retrieval.Hit]) -> list[Citation]:
    return [
        Citation(
            index=i,
            title=h.title,
            bundle=h.bundle,
            group=h.grp,
            domain=h.domain,
            path=h.path,
            snippet=h.body if len(h.body) <= 200 else h.body[:200] + "…",
            score=round(h.score, 4),
        )
        for i, h in enumerate(hits, start=1)
    ]


@app.get("/")
def index() -> FileResponse:
    index_file = config.STATIC_DIR / "index.html"
    if not index_file.is_file():
        raise HTTPException(status_code=404, detail="静态页面缺失：static/index.html")
    return FileResponse(index_file)


@app.get("/api/health")
def health() -> dict:
    """服务自检：索引状态 + 大模型就绪状态 + 索引元信息。"""
    db = config.db_path()
    info: dict = {
        "service": "okf-knowledge-qa",
        "version": "0.1.0",
        "llm_ready": config.llm_ready(),
        "llm_model": config.llm_model() if config.llm_ready() else None,
        "db_ready": False,
        "stats": {},
        "error": None,
    }
    try:
        con = retrieval.connect(db)
    except retrieval.KnowledgeBaseUnavailable as exc:
        info["error"] = str(exc)
        return info
    try:
        stats = retrieval.stats(con)
    except retrieval.KnowledgeBaseUnavailable as exc:
        # 索引可打开但元信息读不出，说明索引损坏；此时不得上报 db_ready=true
        info["error"] = str(exc)
        return info
    finally:
        con.close()
    info["db_ready"] = True
    info["stats"] = stats
    return info


@app.post("/api/ask", response_model=AskResponse)
async def ask(req: AskRequest) -> AskResponse:
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="问题不能为空")

    k = req.top_k or config.top_k()

    try:
        con = retrieval.connect(config.db_path())
    except retrieval.KnowledgeBaseUnavailable as exc:
        # 索引缺失是部署问题，必须显式报错而非返回空答案（对抗性审查 V5）
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    try:
        hits = retrieval.search(con, question, k)
    finally:
        con.close()

    if not hits:
        return AskResponse(answer=NO_HIT_ANSWER, citations=[], hit_count=0, degraded=False)

    citations = _to_citations(hits)

    if not config.llm_ready():
        return AskResponse(
            answer=prompts.build_degraded_answer(hits),
            citations=citations,
            hit_count=len(hits),
            degraded=True,
        )

    try:
        answer = await llm.chat(prompts.SYSTEM_PROMPT, prompts.build_user_prompt(question, hits))
    except llm.LLMError as exc:
        # 大模型故障时降级为抽取式片段直出，并如实告知降级原因
        return AskResponse(
            answer=prompts.build_degraded_answer(hits, llm_failed=True),
            citations=citations,
            hit_count=len(hits),
            degraded=True,
            error=str(exc),
        )

    return AskResponse(answer=answer, citations=citations, hit_count=len(hits), degraded=False)
