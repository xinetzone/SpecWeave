"""仓储与统计测试（内存实现 + 降级聚合）。"""

from support_agent.store import (
    FallbackStore,
    Feedback,
    MemoryStore,
    Message,
    Session,
    build_store,
    summarize,
)
from support_agent.config import Config
from support_agent.http_client import HttpError


def test_memory_store_roundtrip():
    store = MemoryStore()
    store.ensure_session("s1")
    store.append_message(Message(session_id="s1", role="user", content="退款", intent="refund"))
    store.append_message(Message(session_id="s1", role="assistant", content="可以退", intent="refund"))
    store.add_feedback(Feedback(session_id="s1", rating=5, resolved=True))

    assert len(store.session_messages("s1")) == 2
    stats = store.stats()
    assert stats["sessions"] == 1
    assert stats["user_messages"] == 1
    assert stats["avg_rating"] == 5.0
    assert stats["resolved_rate"] == 100.0
    assert stats["intent_distribution"]["refund"] == 1


def test_summarize_transfer_rate():
    sessions = [Session(id="a", transferred=True), Session(id="b")]
    messages = [Message(session_id="a", role="user", content="x", intent="human")]
    stats = summarize(sessions, messages, [], backend="memory")
    assert stats["transferred"] == 1
    assert stats["transfer_rate"] == 50.0


def test_build_store_without_cloud():
    cfg = Config(supabase_url="", supabase_key="")
    assert isinstance(build_store(cfg), MemoryStore)


def test_build_store_with_cloud_uses_fallback_wrapper():
    cfg = Config(supabase_url="https://demo.supabase.co", supabase_key="key")
    store = build_store(cfg)
    assert isinstance(store, FallbackStore)
    assert store.backend == "supabase"


def test_fallback_store_degrades_on_failure():
    class Broken:
        backend = "supabase"

        def list_sessions(self, limit=50):
            raise HttpError(500, "boom")

        def session_messages(self, session_id, limit=500):
            raise HttpError(500, "boom")

        def list_feedback(self, limit=500):
            raise HttpError(500, "boom")

    store = FallbackStore(Broken(), MemoryStore())
    stats = store.stats()
    assert store.degraded is True
    assert "boom" in store.last_error
    assert stats["degraded"] is True
