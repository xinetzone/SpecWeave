"""持久化层：Supabase（云端）为主，内存为降级兜底。

设计要点：
- Serverless 环境无本地磁盘持久性，状态必须外置 -> 默认走 Supabase REST（PostgREST）。
- 云端不可用时（未配置 / 网络失败）自动降级到内存，保证「永远不 500」。
- 统计在 Python 侧聚合，避免依赖数据库视图，便于多云迁移。
"""

import uuid
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence

from .config import Config
from .http_client import HttpError, request_json

SESSIONS = "cs_sessions"
MESSAGES = "cs_messages"
FEEDBACK = "cs_feedback"
TICKETS = "cs_tickets"
FAQS = "cs_faq"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_id(prefix: str = "cs") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


@dataclass
class Session:
    id: str
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    status: str = "open"  # open | transferred | closed
    last_intent: str = ""
    transferred: bool = False
    channel: str = "web"


@dataclass
class Message:
    session_id: str
    role: str  # user | assistant
    content: str
    intent: str = ""
    confidence: float = 0.0
    source: str = "llm"  # llm | faq | human
    needs_human: bool = False
    low_confidence: bool = False
    faq_ids: str = ""
    latency_ms: int = 0
    created_at: str = field(default_factory=_now)


@dataclass
class Feedback:
    session_id: str
    rating: int = 0  # 1..5
    resolved: bool = True
    comment: str = ""
    created_at: str = field(default_factory=_now)


@dataclass
class Ticket:
    id: str
    session_id: str
    intent: str = ""
    reason: str = ""
    status: str = "pending"
    created_at: str = field(default_factory=_now)


class Store(ABC):
    """仓储抽象。"""

    backend = "memory"

    @abstractmethod
    def ensure_session(self, session_id: str) -> Session: ...

    @abstractmethod
    def append_message(self, message: Message) -> None: ...

    @abstractmethod
    def update_session(self, session_id: str, **fields: Any) -> None: ...

    @abstractmethod
    def recent_messages(self, session_id: str, limit: int = 12) -> List[Message]: ...

    @abstractmethod
    def session_messages(self, session_id: str, limit: int = 500) -> List[Message]: ...

    @abstractmethod
    def list_sessions(self, limit: int = 50) -> List[Session]: ...

    @abstractmethod
    def add_feedback(self, feedback: Feedback) -> None: ...

    @abstractmethod
    def add_ticket(self, ticket: Ticket) -> None: ...

    @abstractmethod
    def list_feedback(self, limit: int = 500) -> List[Feedback]: ...

    @abstractmethod
    def list_faq(self) -> List[Dict[str, Any]]: ...

    @abstractmethod
    def add_faq(self, entry: Dict[str, Any]) -> Dict[str, Any]: ...

    def stats(self, limit: int = 200) -> Dict[str, Any]:
        sessions = self.list_sessions(limit=limit)
        ids = {s.id for s in sessions}
        messages: List[Message] = []
        for sid in ids:
            messages.extend(self.session_messages(sid))
        feedbacks = [f for f in self.list_feedback() if f.session_id in ids]
        return summarize(sessions, messages, feedbacks, backend=self.backend)

    def health(self) -> Dict[str, Any]:
        return {"backend": self.backend, "ok": True}


def summarize(
    sessions: Sequence[Session],
    messages: Sequence[Message],
    feedbacks: Sequence[Feedback],
    *,
    backend: str,
    degraded: bool = False,
) -> Dict[str, Any]:
    """把原始记录聚合为管理后台指标。"""
    total = len(sessions)
    transferred = sum(1 for s in sessions if s.transferred or s.status == "transferred")
    user_messages = sum(1 for m in messages if m.role == "user")
    assistant_messages = sum(1 for m in messages if m.role == "assistant")
    human_messages = sum(1 for m in messages if m.needs_human)

    intent_dist: Dict[str, int] = {}
    for m in messages:
        if m.role == "user" and m.intent:
            intent_dist[m.intent] = intent_dist.get(m.intent, 0) + 1

    ratings = [f.rating for f in feedbacks if isinstance(f.rating, int) and f.rating > 0]
    resolved_flags = [bool(f.resolved) for f in feedbacks]
    counts: Dict[str, int] = {}
    for m in messages:
        counts[m.session_id] = counts.get(m.session_id, 0) + 1

    return {
        "backend": backend,
        "degraded": degraded,
        "sessions": total,
        "messages": len(messages),
        "user_messages": user_messages,
        "assistant_messages": assistant_messages,
        "human_messages": human_messages,
        "transferred": transferred,
        "transfer_rate": round(100.0 * transferred / total, 1) if total else 0.0,
        "feedback_count": len(feedbacks),
        "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else 0.0,
        "resolved_rate": (
            round(100.0 * sum(1 for r in resolved_flags if r) / len(resolved_flags), 1)
            if resolved_flags
            else 0.0
        ),
        "intent_distribution": intent_dist,
        "recent_sessions": [
            {
                "id": s.id,
                "status": s.status,
                "transferred": s.transferred,
                "last_intent": s.last_intent,
                "updated_at": s.updated_at,
                "message_count": counts.get(s.id, 0),
            }
            for s in sorted(sessions, key=lambda x: x.updated_at, reverse=True)[:20]
        ],
    }


class MemoryStore(Store):
    """进程内仓储（降级 / 本地开发用）。"""

    backend = "memory"

    def __init__(self) -> None:
        self.sessions: Dict[str, Session] = {}
        self.messages: List[Message] = []
        self.feedbacks: List[Feedback] = []
        self.tickets: Dict[str, Ticket] = {}
        self.faqs: List[Dict[str, Any]] = []

    def ensure_session(self, session_id: str) -> Session:
        session = self.sessions.get(session_id)
        if session is None:
            session = Session(id=session_id)
            self.sessions[session_id] = session
        return session

    def append_message(self, message: Message) -> None:
        self.messages.append(message)

    def update_session(self, session_id: str, **fields: Any) -> None:
        session = self.ensure_session(session_id)
        for key, value in fields.items():
            if hasattr(session, key):
                setattr(session, key, value)
        session.updated_at = _now()

    def recent_messages(self, session_id: str, limit: int = 12) -> List[Message]:
        rows = [m for m in self.messages if m.session_id == session_id]
        return rows[-limit:]

    def session_messages(self, session_id: str, limit: int = 500) -> List[Message]:
        rows = [m for m in self.messages if m.session_id == session_id]
        return rows[:limit]

    def list_sessions(self, limit: int = 50) -> List[Session]:
        rows = sorted(self.sessions.values(), key=lambda s: s.updated_at, reverse=True)
        return rows[:limit]

    def add_feedback(self, feedback: Feedback) -> None:
        self.feedbacks.append(feedback)

    def add_ticket(self, ticket: Ticket) -> None:
        self.tickets[ticket.id] = ticket

    def list_feedback(self, limit: int = 500) -> List[Feedback]:
        return self.feedbacks[:limit]

    def list_faq(self) -> List[Dict[str, Any]]:
        return list(self.faqs)

    def add_faq(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        self.faqs.append(entry)
        return entry


class SupabaseStore(Store):
    """Supabase（PostgREST）仓储。"""

    backend = "supabase"

    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.base = cfg.supabase_url.rstrip("/") + "/rest/v1"

    # ---- 底层 -----------------------------------------------------------
    def _headers(self, prefer: str = "") -> Dict[str, str]:
        headers = {
            "apikey": self.cfg.supabase_key,
            "Authorization": f"Bearer {self.cfg.supabase_key}",
            "Accept": "application/json",
        }
        if prefer:
            headers["Prefer"] = prefer
        return headers

    def _insert(self, table: str, rows: Any, *, prefer: str = "return=minimal") -> Any:
        url = f"{self.base}/{table}"
        return request_json(
            "POST",
            url,
            headers=self._headers(prefer),
            payload=rows,
            timeout=self.cfg.request_timeout,
        )

    def _select(self, table: str, query: str) -> Any:
        url = f"{self.base}/{table}?{query}"
        return request_json(
            "GET", url, headers=self._headers(), timeout=self.cfg.request_timeout
        )

    def _patch(self, table: str, query: str, payload: Dict[str, Any]) -> Any:
        url = f"{self.base}/{table}?{query}"
        return request_json(
            "PATCH",
            url,
            headers=self._headers("return=minimal"),
            payload=payload,
            timeout=self.cfg.request_timeout,
        )

    # ---- 接口 -----------------------------------------------------------
    def ensure_session(self, session_id: str) -> Session:
        row = self._select(SESSIONS, f"id=eq.{session_id}&select=*&limit=1")
        if row:
            return _to_session(row[0])
        session = Session(id=session_id)
        # resolution=ignore-duplicates：并发首次访问不会产生 409
        self._insert(
            SESSIONS,
            [asdict(session)],
            prefer="return=minimal,resolution=ignore-duplicates",
        )
        return session

    def append_message(self, message: Message) -> None:
        self._insert(MESSAGES, [asdict(message)])

    def update_session(self, session_id: str, **fields: Any) -> None:
        payload = dict(fields)
        payload["updated_at"] = _now()
        self._patch(SESSIONS, f"id=eq.{session_id}", payload)

    def recent_messages(self, session_id: str, limit: int = 12) -> List[Message]:
        rows = self._select(
            MESSAGES,
            f"session_id=eq.{session_id}&select=*&order=created_at.desc&limit={limit}",
        )
        return [_to_message(r) for r in reversed(rows or [])]

    def session_messages(self, session_id: str, limit: int = 500) -> List[Message]:
        rows = self._select(
            MESSAGES,
            f"session_id=eq.{session_id}&select=*&order=created_at.asc&limit={limit}",
        )
        return [_to_message(r) for r in (rows or [])]

    def list_sessions(self, limit: int = 50) -> List[Session]:
        rows = self._select(
            SESSIONS, f"select=*&order=updated_at.desc&limit={limit}"
        )
        return [_to_session(r) for r in (rows or [])]

    def add_feedback(self, feedback: Feedback) -> None:
        self._insert(FEEDBACK, [asdict(feedback)])

    def add_ticket(self, ticket: Ticket) -> None:
        self._insert(TICKETS, [asdict(ticket)])

    def list_feedback(self, limit: int = 500) -> List[Feedback]:
        rows = self._select(FEEDBACK, f"select=*&order=created_at.desc&limit={limit}")
        return [_to_feedback(r) for r in (rows or [])]

    def list_faq(self) -> List[Dict[str, Any]]:
        rows = self._select(FAQS, "select=*&order=id.asc&limit=500")
        return list(rows or [])

    def add_faq(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        rows = self._insert(FAQS, [entry], prefer="return=representation")
        return rows[0] if rows else entry

    def stats(self, limit: int = 200) -> Dict[str, Any]:
        """云端聚合：批量拉取而非按会话逐个请求，控制 Serverless 耗时。"""
        sessions = self.list_sessions(limit=limit)
        ids = {s.id for s in sessions}
        rows = self._select(MESSAGES, "select=*&order=created_at.desc&limit=2000") or []
        messages = [_to_message(r) for r in rows if r.get("session_id") in ids]
        feedbacks = [f for f in self.list_feedback(limit=1000) if f.session_id in ids]
        return summarize(sessions, messages, feedbacks, backend=self.backend)

    def health(self) -> Dict[str, Any]:
        self._select(SESSIONS, "select=id&limit=1")
        return {"backend": self.backend, "ok": True}


class FallbackStore(Store):
    """主仓储失败时自动降级到内存，保证请求不中断。"""

    def __init__(self, primary: Store, fallback: Optional[Store] = None) -> None:
        self.primary = primary
        self.fallback = fallback or MemoryStore()
        self.degraded = False
        self.last_error = ""

    @property
    def backend(self) -> str:  # type: ignore[override]
        return self.primary.backend

    def _run(self, name: str, *args: Any, **kwargs: Any) -> Any:
        try:
            return getattr(self.primary, name)(*args, **kwargs)
        except (HttpError, OSError, ValueError, KeyError, TypeError) as exc:
            self.degraded = True
            self.last_error = str(exc)[:300]
            return getattr(self.fallback, name)(*args, **kwargs)

    def ensure_session(self, session_id: str) -> Session:
        return self._run("ensure_session", session_id)

    def append_message(self, message: Message) -> None:
        self._run("append_message", message)

    def update_session(self, session_id: str, **fields: Any) -> None:
        self._run("update_session", session_id, **fields)

    def recent_messages(self, session_id: str, limit: int = 12) -> List[Message]:
        return self._run("recent_messages", session_id, limit)

    def session_messages(self, session_id: str, limit: int = 500) -> List[Message]:
        return self._run("session_messages", session_id, limit)

    def list_sessions(self, limit: int = 50) -> List[Session]:
        return self._run("list_sessions", limit)

    def add_feedback(self, feedback: Feedback) -> None:
        self._run("add_feedback", feedback)

    def add_ticket(self, ticket: Ticket) -> None:
        self._run("add_ticket", ticket)

    def list_feedback(self, limit: int = 500) -> List[Feedback]:
        return self._run("list_feedback", limit)

    def list_faq(self) -> List[Dict[str, Any]]:
        return self._run("list_faq")

    def add_faq(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        return self._run("add_faq", entry)

    def stats(self, limit: int = 200) -> Dict[str, Any]:
        data: Optional[Dict[str, Any]] = None
        try:
            data = self.primary.stats(limit=limit)
        except AttributeError:  # 主仓储未实现聚合 -> 走通用路径
            data = None
        except (HttpError, OSError, ValueError, KeyError, TypeError) as exc:
            self.degraded = True
            self.last_error = str(exc)[:300]
            data = None
        if data is None:
            data = Store.stats(self, limit=limit)
        data["degraded"] = self.degraded
        data["last_error"] = self.last_error
        return data

    def health(self) -> Dict[str, Any]:
        try:
            return self.primary.health()
        except (HttpError, OSError, ValueError) as exc:
            self.degraded = True
            self.last_error = str(exc)[:300]
            return {"backend": self.backend, "ok": False, "error": self.last_error}


def build_store(cfg: Config) -> Store:
    """按配置构建仓储：云端优先，未配置则内存。"""
    if cfg.cloud_ready:
        return FallbackStore(SupabaseStore(cfg), MemoryStore())
    return MemoryStore()


# ---- 反序列化 ------------------------------------------------------------


def _to_session(row: Dict[str, Any]) -> Session:
    return Session(
        id=row.get("id", ""),
        created_at=row.get("created_at") or _now(),
        updated_at=row.get("updated_at") or _now(),
        status=row.get("status") or "open",
        last_intent=row.get("last_intent") or "",
        transferred=bool(row.get("transferred")),
        channel=row.get("channel") or "web",
    )


def _to_message(row: Dict[str, Any]) -> Message:
    return Message(
        session_id=row.get("session_id", ""),
        role=row.get("role") or "user",
        content=row.get("content") or "",
        intent=row.get("intent") or "",
        confidence=float(row.get("confidence") or 0.0),
        source=row.get("source") or "llm",
        needs_human=bool(row.get("needs_human")),
        low_confidence=bool(row.get("low_confidence")),
        faq_ids=row.get("faq_ids") or "",
        latency_ms=int(row.get("latency_ms") or 0),
        created_at=row.get("created_at") or _now(),
    )


def _to_feedback(row: Dict[str, Any]) -> Feedback:
    return Feedback(
        session_id=row.get("session_id", ""),
        rating=int(row.get("rating") or 0),
        resolved=bool(row.get("resolved", True)),
        comment=row.get("comment") or "",
        created_at=row.get("created_at") or _now(),
    )
