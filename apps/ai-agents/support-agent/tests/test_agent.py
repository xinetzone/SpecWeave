"""Agent 编排测试：多轮上下文 / 转人工 / 大模型失效降级。"""

from support_agent.agent import Agent
from support_agent.config import Config
from support_agent.faq import FaqIndex
from support_agent.store import MemoryStore
from support_agent import llm


def make_agent(chat=None, llm_key="sk-test"):
    cfg = Config(llm_api_key=llm_key, llm_base_url="https://example.test/v1")
    store = MemoryStore()
    return Agent(cfg, store, FaqIndex(), chat=chat), store


def echo_chat(_cfg, messages, **kwargs):
    assert messages[0]["role"] == "system"
    return "已收到，退款需在订单页申请。", 42


def test_multi_turn_keeps_history():
    agent, store = make_agent(chat=echo_chat)
    agent.handle("s1", "你好")
    second = agent.handle("s1", "我要退款")

    assert second.intent == "refund"
    assert second.source == "llm"
    assert len(store.session_messages("s1")) == 4
    # 第二轮请求里应带上第一轮的历史
    assert len([m for m in store.session_messages("s1") if m.role == "user"]) == 2


def test_explicit_human_request_creates_ticket():
    agent, _ = make_agent(chat=echo_chat)
    result = agent.handle("s2", "转人工")

    assert result.needs_human is True
    assert result.intent == "human"
    assert result.ticket_id.startswith("tk_")


def test_llm_failure_falls_back_to_faq():
    def broken(_cfg, messages, **kwargs):
        raise llm.LLMError("down")

    agent, _ = make_agent(chat=broken)
    result = agent.handle("s3", "退款多久到账？")

    assert result.source == "faq"
    assert "知识库" in result.reply or result.faq
    assert result.needs_human is False


def test_llm_failure_without_faq_transfers_to_human():
    def broken(_cfg, messages, **kwargs):
        raise llm.LLMError("down")

    agent, _ = make_agent(chat=broken)
    result = agent.handle("s4", "abcdefg 完全没头绪的问题")

    assert result.needs_human is True
    assert result.ticket_id


def test_low_confidence_reply_transfers_on_second_round():
    def unsure(_cfg, messages, **kwargs):
        return "抱歉，这个问题我无法回答，建议您联系人工。", 10

    agent, _ = make_agent(chat=unsure)
    first = agent.handle("s5", "zzz 无关问题")
    second = agent.handle("s5", "zzz 还是没解决")

    assert first.needs_human is False
    assert second.needs_human is True


def test_session_state_is_updated():
    agent, store = make_agent(chat=echo_chat)
    agent.handle("s6", "我要申请退款")
    session = store.sessions["s6"]
    assert session.last_intent == "refund"
    assert session.status == "open"
