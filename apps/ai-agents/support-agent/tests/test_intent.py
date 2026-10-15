"""意图识别测试：规则快判 / 大模型兜底 / 无模型降级。"""

from support_agent.config import Config
from support_agent.intent import classify, rule_classify


def test_rule_refund():
    result = rule_classify("我要申请退款，怎么退？")
    assert result.intent == "refund"
    assert result.confidence >= 0.6


def test_rule_order_query():
    assert rule_classify("帮我查一下订单物流到哪了").intent == "order_query"


def test_rule_tech_support():
    assert rule_classify("App 一直闪退打不开").intent == "tech_support"


def test_rule_human_has_priority():
    result = rule_classify("退款一直没到账，我要转人工投诉")
    assert result.intent == "human"
    assert result.needs_human is True


def test_rule_other_without_keyword():
    assert rule_classify("今天天气不错").intent == "other"


def test_classify_falls_back_without_llm():
    cfg = Config(llm_api_key="")
    result = classify(cfg, "完全无关的闲聊内容")
    assert result.method in {"rule", "fallback"}
    assert result.intent in {"other", "smalltalk"}


def test_classify_uses_llm_when_rule_weak(monkeypatch):
    cfg = Config(llm_api_key="sk-test", llm_base_url="https://example.test/v1")

    def fake_chat(_cfg, messages, **kwargs):
        return '{"intent":"tech_support","confidence":0.88,"needs_human":false}', 30

    result = classify(cfg, "设备连不上网咋整", chat=fake_chat)
    assert result.intent == "tech_support"
    assert result.method == "llm"
    assert result.confidence == 0.88


def test_classify_llm_failure_degrades(monkeypatch):
    cfg = Config(llm_api_key="sk-test", llm_base_url="https://example.test/v1")

    def broken_chat(_cfg, messages, **kwargs):
        raise RuntimeError("boom")

    result = classify(cfg, "设备连不上网咋整", chat=broken_chat)
    assert result.method == "fallback"
