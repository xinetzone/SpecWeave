"""业务管线：录入归类、关联、检索、问答、提取、待办整理、阶段总结。

贯穿全模块的一条纪律：**每个能力都有无大模型的等价实现**。

这不是"顺便加个兜底"，而是产品前提——个人信息管家第一次被人打开时，
很可能还没有任何密钥。若那时点了「智能问答」只得到一句「请先配置 API Key」，
用户不会去配 Key，只会关掉页面。因此降级路径必须产出**可用的结果**
（统计直出、相似度排序、启发式归类），只是没那么聪明。
"""

import re
from datetime import date, timedelta

from .config import LLMOverride, Settings
from .llm import LLMClient, LLMError
from .models import (
    KIND_IDEA,
    KIND_MATERIAL,
    KIND_TODO,
    KINDS,
    STATUS_DONE,
)
from .prompts import (
    ASK_SYSTEM,
    CLASSIFY_SYSTEM,
    EXTRACT_SYSTEM,
    LINK_SYSTEM,
    SUMMARIZE_SYSTEM,
    TODO_SYSTEM,
    ask_user,
    classify_user,
    extract_user,
    link_user,
    summarize_user,
    todo_user,
)
from .similarity import keyword_score, similarity, top_terms
from .store import Store, now_iso

TODO_SIGNALS = (
    "待办", "记得", "要做", "需要做", "别忘了", "截止", "提醒", "跟进",
    "安排", "计划", "下周", "明天", "后天", "todo", "TODO",
)
MATERIAL_SIGNALS = (
    "http://", "https://", "出处", "来源", "摘录", "参考", "链接", "引用",
    "文档", "报告", "论文", "参考链接",
)

_DATE_ISO_RE = re.compile(r"(\d{4})-(\d{1,2})-(\d{1,2})")
_DATE_CN_RE = re.compile(r"(\d{1,2})月(\d{1,2})日")


def _item_text(item: dict) -> str:
    """条目参与相似度/检索比对的完整文本。"""
    parts = [item.get("title") or "", item.get("summary") or "", item.get("content") or ""]
    return "\n".join(p for p in parts if p)


def _first_sentence(text: str, limit: int) -> str:
    flat = " ".join(text.split())
    for sep in ("。", "！", "？", "\n", "；", ". "):
        idx = flat.find(sep)
        if 0 < idx < limit:
            return flat[:idx].strip()
    return (flat[:limit] + "…") if len(flat) > limit else flat


def heuristic_kind(text: str) -> str:
    """无大模型时的类型判定：按信号词投票，平票归想法。"""
    lowered = text.lower()
    todo_hits = sum(1 for s in TODO_SIGNALS if s.lower() in lowered)
    material_hits = sum(1 for s in MATERIAL_SIGNALS if s.lower() in lowered)
    if todo_hits > material_hits and todo_hits:
        return KIND_TODO
    if material_hits:
        return KIND_MATERIAL
    return KIND_IDEA


def _parse_due_date(text: str) -> str | None:
    """从自然语言里抠出截止日期；抠不出来返回 None（不猜）。"""
    today = date.today()
    match = _DATE_ISO_RE.search(text)
    if match:
        return f"{int(match.group(1)):04d}-{int(match.group(2)):02d}-{int(match.group(3)):02d}"
    match = _DATE_CN_RE.search(text)
    if match:
        return f"{today.year:04d}-{int(match.group(1)):02d}-{int(match.group(2)):02d}"
    if "明天" in text:
        return (today + timedelta(days=1)).isoformat()
    if "后天" in text:
        return (today + timedelta(days=2)).isoformat()
    if "下周" in text:
        return (today + timedelta(days=7)).isoformat()
    return None


def heuristic_enrich(text: str) -> dict:
    """启发式归类：标题/摘要/标签/待办全部本地算出。"""
    kind = heuristic_kind(text)
    todos: list[dict] = []
    if kind == KIND_TODO:
        todos = [
            {
                "title": _first_sentence(text, 40),
                "priority": 2,
                "due_date": _parse_due_date(text),
            }
        ]
    return {
        "kind": kind,
        "title": _first_sentence(text, 24),
        "summary": _first_sentence(text, 80),
        "tags": top_terms(text, 4),
        "todos": todos,
        "source": "heuristic",
    }


def _clean_tags(tags: object) -> list[str]:
    if not isinstance(tags, list):
        return []
    out: list[str] = []
    for tag in tags:
        if isinstance(tag, str) and tag.strip() and tag not in out:
            out.append(tag.strip()[:24])
        if len(out) >= 6:
            break
    return out


def _clean_todos(todos: object, text: str) -> list[dict]:
    if not isinstance(todos, list):
        return []
    out: list[dict] = []
    for raw in todos:
        if not isinstance(raw, dict):
            continue
        title = raw.get("title")
        if not isinstance(title, str) or not title.strip():
            continue
        priority = raw.get("priority", 2)
        if not isinstance(priority, int) or priority not in (1, 2, 3):
            priority = 2
        due = raw.get("due_date")
        out.append(
            {
                "title": title.strip()[:120],
                "priority": priority,
                "due_date": due if isinstance(due, str) else _parse_due_date(text),
            }
        )
    return out


def enrich_item(
    text: str,
    llm: LLMClient | None = None,
    override: LLMOverride | None = None,
) -> dict:
    """把一段随手输入整理成结构化条目；模型不可用/不守约时退回启发式。"""
    fallback = heuristic_enrich(text)
    if llm is None or not llm.available(override):
        return fallback

    try:
        parsed = llm.chat_json(
            CLASSIFY_SYSTEM, classify_user(text), override=override, temperature=0.2
        )
    except LLMError:
        return fallback
    if not parsed:
        return fallback

    kind = parsed.get("kind")
    title = parsed.get("title")
    summary = parsed.get("summary")
    if kind not in KINDS or not isinstance(title, str) or not title.strip():
        return fallback

    # 标签为空会直接损害检索，故空列表退回启发式；
    # 待办为空是模型的有效判断（"这段没有待办"），必须尊重，不能拿兜底覆盖。
    tags = _clean_tags(parsed["tags"]) if isinstance(parsed.get("tags"), list) else []
    todos = (
        _clean_todos(parsed["todos"], text)
        if isinstance(parsed.get("todos"), list)
        else fallback["todos"]
    )

    return {
        "kind": kind,
        "title": title.strip()[:60],
        "summary": summary.strip()[:400] if isinstance(summary, str) else fallback["summary"],
        "tags": tags or fallback["tags"],
        "todos": todos,
        "source": "llm",
    }


def capture(
    store: Store,
    settings: Settings,
    payload: dict,
    llm: LLMClient | None = None,
    override: LLMOverride | None = None,
) -> dict:
    """录入一条内容：归类 → 落库 → 派生待办 → 关联已有条目。

    返回 ``{item, todos, links}``，前端一次渲染完整个"入库回执"。
    """
    content = payload["content"]
    enriched = enrich_item(content, llm, override)
    if payload.get("kind") in KINDS:
        enriched["kind"] = payload["kind"]  # 用户显式指定优先于模型判断

    item = store.create_item(
        {
            "kind": enriched["kind"],
            "title": payload.get("title") or enriched["title"],
            "content": content,
            "summary": enriched["summary"],
            "tags": list(dict.fromkeys(list(payload.get("tags") or []) + enriched["tags"])),
            "status": "open",
            "priority": 2,
            "due_date": None,
            "source": payload.get("source", "web"),
        }
    )

    todos: list[dict] = []
    for todo in enriched["todos"]:
        record = store.create_item(
            {
                "kind": KIND_TODO,
                "title": todo["title"],
                "content": todo["title"],
                "summary": f"由「{item.get('title')}」派生",
                "tags": enriched["tags"][:3],
                "status": "open",
                "priority": todo["priority"],
                "due_date": todo["due_date"],
                "source": "derived",
            }
        )
        todos.append(record)

    links = find_related(store, settings, item, llm=llm, override=override)
    return {"item": item, "todos": todos, "links": links}


def find_related(
    store: Store,
    settings: Settings,
    item: dict,
    llm: LLMClient | None = None,
    override: LLMOverride | None = None,
    limit: int | None = None,
) -> list[dict]:
    """找出与 ``item`` 相关的已有条目，并把关联关系写进库。

    打分 = 文本 Dice 相似度 + 标签重合加成。关联理由优先问模型，
    拿不到就给出可解释的统计理由——**宁可说"共享标签 X"，也不要留空**，
    因为无法解释的关联等于没有关联。
    """
    limit = limit or settings.link_limit
    candidates = store.list_items(limit=settings.max_candidates)
    own_tags = set(item.get("tags") or [])
    text = _item_text(item)

    scored: list[dict] = []
    for candidate in candidates:
        candidate_id = candidate.get("id")
        if not candidate_id or candidate_id == item.get("id"):
            continue
        base = similarity(text, _item_text(candidate))
        overlap = own_tags & set(candidate.get("tags") or [])
        total = min(1.0, base + (0.15 if overlap else 0.0))
        if total < settings.link_threshold:
            continue
        reason = f"共享标签：{'、'.join(sorted(overlap))}" if overlap else f"文本相似度 {total:.2f}"
        scored.append(
            {
                "id": candidate_id,
                "title": candidate.get("title") or "",
                "score": round(total, 4),
                "reason": reason,
            }
        )

    scored.sort(key=lambda entry: entry["score"], reverse=True)
    scored = scored[:limit]

    if scored and llm is not None and llm.available(override):
        for entry in scored[:3]:  # 只为最相关的三条问模型，控制成本
            try:
                reason = llm.chat(
                    LINK_SYSTEM,
                    link_user(text, entry["title"]),
                    override=override,
                    max_tokens=80,
                )
            except LLMError:
                continue
            if reason:
                entry["reason"] = reason.strip()[:120]

    if scored:
        store.create_links(item["id"], scored)
    return scored


def search_items(
    store: Store,
    settings: Settings,
    query: str = "",
    *,
    kind: str | None = None,
    tag: str | None = None,
    status: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """关键词检索：取候选集 → 本地打分 → 排序截断。

    ``query`` 为空时退化为普通列表（按创建时间倒序），不打分。
    """
    rows = store.list_items(
        kind=kind, tag=tag, status=status, limit=settings.max_candidates
    )
    if not query:
        return rows[:limit]

    scored: list[dict] = []
    for row in rows:
        text = _item_text(row)
        score = keyword_score(query, text)
        if query in (row.get("title") or ""):
            score = min(1.0, score + 0.35)  # 标题命中是最强的相关信号
        if score <= 0:
            continue
        scored.append({**row, "score": round(score, 4)})
    scored.sort(key=lambda row: row["score"], reverse=True)
    return scored[:limit]


def _passages(rows: list[dict], limit: int) -> list[tuple[int, str]]:
    return [(i, _item_text(row)) for i, row in enumerate(rows[:limit], start=1)]


def answer(
    store: Store,
    settings: Settings,
    question: str,
    llm: LLMClient | None = None,
    override: LLMOverride | None = None,
    limit: int = 8,
) -> dict:
    """智能问答，带来源引用。无大模型时退化为"最相关的几条原文"。"""
    rows = search_items(store, settings, question, limit=limit)
    citations = [
        {
            "id": row.get("id"),
            "title": row.get("title") or "",
            "snippet": (row.get("summary") or row.get("content") or "")[:200],
            "score": row.get("score", 0.0),
        }
        for row in rows
    ]
    if not rows:
        return {"answer": "记录里没有找到相关内容。", "citations": [], "source": "none"}

    if llm is None or not llm.available(override):
        lines = [f"未接入大模型，以下为相关度最高的 {len(rows)} 条原文："]
        for idx, (_, text) in enumerate(_passages(rows, limit), start=1):
            lines.append(f"[{idx}] {text[:160]}")
        return {
            "answer": "\n".join(lines),
            "citations": citations,
            "source": "heuristic",
        }

    try:
        content = llm.chat(
            ASK_SYSTEM,
            ask_user(question, _passages(rows, limit)),
            override=override,
            temperature=0.3,
            max_tokens=1200,
        )
    except LLMError as exc:
        return {
            "answer": f"大模型调用失败，已退回检索结果：{exc}",
            "citations": citations,
            "source": "error",
        }
    return {"answer": content, "citations": citations, "source": "llm"}


def extract_highlights(
    store: Store,
    settings: Settings,
    llm: LLMClient | None = None,
    override: LLMOverride | None = None,
    limit: int = 40,
    scope: str = "recent",
) -> dict:
    """重点信息提取，输出 Markdown。"""
    kind = KIND_TODO if scope == "todo" else None
    rows = store.list_items(kind=kind, limit=limit)
    if not rows:
        return {"markdown": "（暂无记录）", "count": 0, "source": "none"}

    if llm is None or not llm.available(override):
        return {
            "markdown": _statistical_digest(rows),
            "count": len(rows),
            "source": "heuristic",
        }

    try:
        markdown = llm.chat(
            EXTRACT_SYSTEM,
            extract_user(_passages(rows, limit)),
            override=override,
            temperature=0.2,
            max_tokens=1600,
        )
    except LLMError as exc:
        return {
            "markdown": f"大模型调用失败，已退回统计摘要：\n\n{_statistical_digest(rows)}",
            "count": len(rows),
            "source": "error",
        }
    return {"markdown": markdown, "count": len(rows), "source": "llm"}


def _statistical_digest(rows: list[dict]) -> str:
    """无大模型时的重点直出：按类型分组 + 高频标签 + 高优先级待办。"""
    by_kind: dict[str, list[dict]] = {}
    for row in rows:
        by_kind.setdefault(row.get("kind", KIND_IDEA), []).append(row)

    counts: dict[str, int] = {}
    for row in rows:
        for tag in row.get("tags") or []:
            counts[tag] = counts.get(tag, 0) + 1
    hot = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:8]

    label = {KIND_IDEA: "想法", KIND_MATERIAL: "资料", KIND_TODO: "待办"}
    lines = ["## 统计摘要（未接入大模型）", ""]
    lines.append(
        "、".join(f"{label.get(k, k)} {len(v)} 条" for k, v in sorted(by_kind.items()))
    )
    if hot:
        lines.append("")
        lines.append("高频标签：" + "、".join(f"{t}({c})" for t, c in hot))
    urgent = [r for r in rows if r.get("kind") == KIND_TODO and r.get("status") != STATUS_DONE]
    if urgent:
        lines.append("")
        lines.append("待办：")
        lines.extend(f"- {r.get('title')}" for r in urgent[:10])
    return "\n".join(lines)


def organize_todos(
    store: Store,
    settings: Settings,
    llm: LLMClient | None = None,
    override: LLMOverride | None = None,
) -> dict:
    """待办整理：去重合并 + 优先级排序。"""
    rows = [
        row
        for row in store.list_items(limit=settings.max_candidates)
        if row.get("kind") == KIND_TODO and row.get("status") != STATUS_DONE
    ]
    if not rows:
        return {"groups": [], "suggestions": [], "count": 0, "source": "none"}

    if llm is None or not llm.available(override):
        groups: dict[str, list[dict]] = {}
        for row in rows:
            theme = (row.get("tags") or ["未分类"])[0]
            groups.setdefault(theme, []).append(
                {"title": row.get("title"), "priority": row.get("priority", 2), "reason": ""}
            )
        return {
            "groups": [
                {"theme": theme, "todos": todos} for theme, todos in groups.items()
            ],
            "suggestions": ["接入大模型后可获得去重合并与推进建议。"],
            "count": len(rows),
            "source": "heuristic",
        }

    try:
        parsed = llm.chat_json(
            TODO_SYSTEM,
            todo_user(_passages(rows, settings.max_candidates)),
            override=override,
            temperature=0.2,
        )
    except LLMError:
        parsed = None
    groups_raw = (parsed or {}).get("groups")
    if not isinstance(groups_raw, list) or not groups_raw:
        return organize_todos(store, settings, llm=None) | {"source": "heuristic"}

    groups: list[dict] = []
    for raw in groups_raw:
        if not isinstance(raw, dict):
            continue
        theme = raw.get("theme")
        todos = raw.get("todos")
        if not isinstance(theme, str) or not isinstance(todos, list):
            continue
        groups.append(
            {
                "theme": theme,
                "todos": [
                    {
                        "title": str(t.get("title", ""))[:120],
                        "priority": t.get("priority", 2),
                        "reason": str(t.get("reason", "")),
                    }
                    for t in todos
                    if isinstance(t, dict)
                ],
            }
        )
    suggestions = (parsed or {}).get("suggestions")
    return {
        "groups": groups,
        "suggestions": suggestions if isinstance(suggestions, list) else [],
        "count": len(rows),
        "source": "llm",
    }


def build_summary(
    store: Store,
    settings: Settings,
    days: int = 7,
    llm: LLMClient | None = None,
    override: LLMOverride | None = None,
    limit: int = 200,
) -> dict:
    """阶段总结 + 后续行动建议，并自动存档一份。"""
    rows = store.list_items(limit=limit)
    cutoff = (date.today() - timedelta(days=max(1, days))).isoformat()
    recent = [row for row in rows if (row.get("created_at") or "")[:10] >= cutoff]
    if not recent:
        recent = rows[:20]
    if not recent:
        return {"markdown": "（暂无记录可总结）", "count": 0, "source": "none"}

    if llm is None or not llm.available(override):
        markdown = _statistical_summary(recent, days)
        source = "heuristic"
    else:
        try:
            markdown = llm.chat(
                SUMMARIZE_SYSTEM,
                summarize_user(days, _passages(recent, limit)),
                override=override,
                temperature=0.3,
                max_tokens=2000,
            )
            source = "llm"
        except LLMError as exc:
            markdown = f"大模型调用失败，已退回统计总结：\n\n{_statistical_summary(recent, days)}"
            source = "error"

    record = store.create_summary(
        {
            "period_start": cutoff,
            "period_end": date.today().isoformat(),
            "title": f"近 {days} 天阶段总结",
            "content": markdown,
            "actions": [],
        }
    )
    return {"markdown": markdown, "count": len(recent), "source": source, "saved": record}


def _statistical_summary(rows: list[dict], days: int) -> str:
    counts: dict[str, int] = {}
    for row in rows:
        for tag in row.get("tags") or []:
            counts[tag] = counts.get(tag, 0) + 1
    hot = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
    open_todos = [
        r for r in rows if r.get("kind") == KIND_TODO and r.get("status") != STATUS_DONE
    ]
    lines = [
        f"## 阶段总结（近 {days} 天 · 统计直出）",
        "",
        f"共 {len(rows)} 条记录，其中待办 {len(open_todos)} 条未完成。",
    ]
    if hot:
        lines += ["", "主题分布：" + "、".join(f"{t}({c})" for t, c in hot)]
    if open_todos:
        lines += ["", "后续行动建议："]
        lines += [f"- P2 {r.get('title')}" for r in open_todos[:10]]
    return "\n".join(lines)


def tag_cloud(store: Store, settings: Settings) -> dict:
    """标签云与概览统计。"""
    rows = store.list_items(limit=settings.max_candidates)
    counts: dict[str, int] = {}
    kinds: dict[str, int] = {}
    for row in rows:
        kinds[row.get("kind", KIND_IDEA)] = kinds.get(row.get("kind", KIND_IDEA), 0) + 1
        for tag in row.get("tags") or []:
            counts[tag] = counts.get(tag, 0) + 1
    return {
        "tags": [
            {"tag": tag, "count": count}
            for tag, count in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        ],
        "kinds": kinds,
        "total": len(rows),
        "generated_at": now_iso(),
    }
