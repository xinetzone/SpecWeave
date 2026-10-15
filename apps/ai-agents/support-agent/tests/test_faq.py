"""知识库检索测试。"""

from support_agent.faq import BUILTIN_FAQ, FaqEntry, FaqIndex, score_entry


def test_search_hits_refund_policy():
    index = FaqIndex(list(BUILTIN_FAQ))
    hits = index.search("退款政策是怎样的", top_k=3)
    assert hits
    assert hits[0][0].category == "refund"
    assert hits[0][1] > 3.0


def test_search_hits_logistics():
    index = FaqIndex(list(BUILTIN_FAQ))
    hits = index.search("我的快递什么时候到", top_k=1)
    assert hits[0][0].category == "order_query"


def test_search_returns_empty_for_irrelevant():
    index = FaqIndex(list(BUILTIN_FAQ))
    assert index.search("zzzz无关内容") == [] or index.search("zzzz无关内容")[0][1] < 3.0


def test_score_entry_zero_for_empty_query():
    assert score_entry("", FaqEntry(id="x", category="other", question="q", answer="a")) == 0.0


def test_custom_entry_is_searchable():
    index = FaqIndex(
        [
            FaqEntry(
                id="faq-custom",
                category="other",
                question="会员怎么升级",
                answer="在个人中心点击升级会员即可。",
                keywords="会员,升级",
            )
        ]
    )
    hits = index.search("会员怎么升级")
    assert hits and hits[0][0].id == "faq-custom"
