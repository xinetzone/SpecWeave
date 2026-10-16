"""业务管线单元测试。

重点覆盖**降级路径**：每个能力都要验证「没有大模型时仍然产出可用结果」，
这是本应用的地基约定（见 doc/guide/design.md 的 A3）。
"""

from info_butler.config import Settings
from info_butler.llm import LLMError
from info_butler.models import KIND_IDEA, KIND_MATERIAL, KIND_TODO
from info_butler.pipeline import (
    _parse_due_date,
    answer,
    build_summary,
    capture,
    enrich_item,
    extract_highlights,
    find_related,
    heuristic_enrich,
    heuristic_kind,
    organize_todos,
    search_items,
    tag_cloud,
)
from info_butler.store import MemoryStore


class FakeLLM:
    """替身：只实现管线真正用到的三个方法。"""

    def __init__(self, json_result=None, chat_result="模型回答", available=True, raises=None):
        self._json = json_result
        self._chat = chat_result
        self._available = available
        self._raises = raises
        self.calls: list[tuple[str, str]] = []

    def available(self, override=None) -> bool:
        return self._available

    def chat(self, system, user, *, override=None, **kwargs):
        self.calls.append((system, user))
        if self._raises is not None:
            raise self._raises
        return self._chat

    def chat_json(self, system, user, *, override=None, **kwargs):
        self.calls.append((system, user))
        if self._raises is not None:
            raise self._raises
        return self._json


def make_store(rows=None):
    store = MemoryStore()
    for row in rows or []:
        store.create_item(row)
    return store


# -- 启发式归类 ---------------------------------------------------------------


def test_heuristic_kind_detects_todo():
    assert heuristic_kind("记得明天把发票寄出去") == KIND_TODO


def test_heuristic_kind_detects_material():
    assert heuristic_kind("参考链接 https://example.com/report") == KIND_MATERIAL


def test_heuristic_kind_defaults_to_idea():
    assert heuristic_kind("我觉得这件事还有另一种可能") == KIND_IDEA


def test_parse_due_date_variants():
    assert _parse_due_date("2026-10-21 前完成") == "2026-10-21"
    assert _parse_due_date("10月21日开会").endswith("-10-21")
    assert _parse_due_date("明天记得交") is not None
    assert _parse_due_date("没有时间信息") is None


def test_heuristic_enrich_shape():
    result = heuristic_enrich("记得明天把定价方案发给客户")
    assert result["kind"] == KIND_TODO
    assert result["source"] == "heuristic"
    assert result["title"] and result["summary"]
    assert result["todos"], "待办类内容必须派生出待办条目"


# -- 模型归类与降级 -----------------------------------------------------------


def test_enrich_without_llm_falls_back_to_heuristic():
    result = enrich_item("记得明天交方案", llm=None)
    assert result["source"] == "heuristic"


def test_enrich_with_unavailable_llm_falls_back():
    result = enrich_item("记得明天交方案", llm=FakeLLM(available=False))
    assert result["source"] == "heuristic"


def test_enrich_uses_llm_result():
    llm = FakeLLM(
        json_result={
            "kind": "material",
            "title": "行业报告摘录",
            "summary": "报告指出定价带正在上移",
            "tags": ["行业", "定价"],
            "todos": [],
        }
    )
    result = enrich_item("报告说定价带上移 https://x.com/r", llm=llm)
    assert result["source"] == "llm"
    assert result["kind"] == KIND_MATERIAL
    assert result["title"] == "行业报告摘录"
    assert result["tags"] == ["行业", "定价"]
    assert result["todos"] == [], "模型明确说没有待办时不得用兜底覆盖"


def test_enrich_rejects_invalid_kind():
    llm = FakeLLM(json_result={"kind": "unknown", "title": "x", "summary": "", "tags": []})
    assert enrich_item("任意内容", llm=llm)["source"] == "heuristic"


def test_enrich_falls_back_when_model_returns_none():
    assert enrich_item("任意内容", llm=FakeLLM(json_result=None))["source"] == "heuristic"


def test_enrich_falls_back_when_model_raises():
    llm = FakeLLM(raises=LLMError("boom"))
    assert enrich_item("任意内容", llm=llm)["source"] == "heuristic"


def test_enrich_falls_back_tags_but_keeps_structure():
    """标签缺失会损害检索，必须退回启发式标签。"""
    llm = FakeLLM(json_result={"kind": "idea", "title": "一个念头", "summary": "摘要", "tags": []})
    result = enrich_item("关于组织协同效率的思考", llm=llm)
    assert result["source"] == "llm"
    assert result["tags"], "标签为空时应回退到启发式标签"


# -- 录入与关联 ---------------------------------------------------------------


def test_capture_persists_item_and_derived_todos():
    store = MemoryStore()
    settings = Settings()
    result = capture(store, settings, {"content": "记得明天把定价方案发给客户"})
    assert result["item"]["kind"] == KIND_TODO
    assert result["todos"], "待办内容应派生出待办条目"
    assert store.get_item(result["item"]["id"]) is not None


def test_capture_respects_explicit_kind():
    store = MemoryStore()
    result = capture(store, Settings(), {"content": "记得明天交方案", "kind": "material"})
    assert result["item"]["kind"] == KIND_MATERIAL


def test_find_related_links_similar_items():
    store = make_store(
        [
            {
                "kind": KIND_IDEA,
                "title": "定价方案初稿",
                "content": "定价方案需要重新评估，客户对价格敏感",
                "summary": "定价方案需重估",
                "tags": ["定价", "客户"],
            }
        ]
    )
    item = store.create_item(
        {
            "kind": KIND_IDEA,
            "title": "定价方案二稿",
            "content": "定价方案再次调整，客户仍嫌贵",
            "summary": "定价方案再调整",
            "tags": ["定价", "客户"],
        }
    )
    links = find_related(store, Settings(), item, llm=None)
    assert links, "高相似度条目应被关联"
    assert links[0]["reason"], "关联必须带可解释的理由"


def test_find_related_ignores_dissimilar_items():
    store = make_store(
        [
            {
                "kind": KIND_IDEA,
                "title": "周末爬山",
                "content": "周末去爬香山，天气不错",
                "summary": "周末爬山",
                "tags": ["生活"],
            }
        ]
    )
    item = store.create_item(
        {
            "kind": KIND_IDEA,
            "title": "定价方案",
            "content": "定价方案需要重新评估",
            "summary": "定价方案",
            "tags": ["定价"],
        }
    )
    assert find_related(store, Settings(), item, llm=None) == []


def test_find_related_never_links_to_self():
    store = MemoryStore()
    item = store.create_item(
        {"kind": KIND_IDEA, "title": "同一条", "content": "内容", "summary": "摘要", "tags": []}
    )
    assert find_related(store, Settings(), item, llm=None) == []


# -- 检索 ---------------------------------------------------------------------


def test_search_without_query_returns_all():
    store = make_store(
        [
            {"kind": KIND_IDEA, "title": "甲", "content": "甲内容", "summary": "甲", "tags": []},
            {"kind": KIND_TODO, "title": "乙", "content": "乙内容", "summary": "乙", "tags": []},
        ]
    )
    assert len(search_items(store, Settings(), "")) == 2


def test_search_ranks_matching_first():
    store = make_store(
        [
            {"kind": KIND_IDEA, "title": "爬山", "content": "周末爬山", "summary": "爬山", "tags": []},
            {"kind": KIND_IDEA, "title": "定价", "content": "定价方案", "summary": "定价", "tags": []},
        ]
    )
    rows = search_items(store, Settings(), "定价")
    assert rows and rows[0]["title"] == "定价"


def test_search_filters_by_kind():
    store = make_store(
        [
            {"kind": KIND_IDEA, "title": "甲", "content": "甲", "summary": "甲", "tags": []},
            {"kind": KIND_TODO, "title": "乙", "content": "乙", "summary": "乙", "tags": []},
        ]
    )
    rows = search_items(store, Settings(), "", kind=KIND_TODO)
    assert len(rows) == 1 and rows[0]["title"] == "乙"


# -- 问答 / 提取 / 待办 / 总结 -------------------------------------------------


def test_answer_without_records():
    result = answer(MemoryStore(), Settings(), "问点什么", llm=None)
    assert result["source"] == "none"
    assert result["citations"] == []


def test_answer_degrades_to_snippets_without_llm():
    store = make_store(
        [{"kind": KIND_IDEA, "title": "定价判断", "content": "定价带应当上移", "summary": "定价判断", "tags": []}]
    )
    result = answer(store, Settings(), "定价", llm=None)
    assert result["source"] == "heuristic"
    assert result["citations"], "降级也要给出来源，否则用户无法判断可信度"


def test_answer_uses_llm_when_available():
    store = make_store(
        [{"kind": KIND_IDEA, "title": "定价判断", "content": "定价带应当上移", "summary": "定价判断", "tags": []}]
    )
    result = answer(store, Settings(), "定价", llm=FakeLLM(chat_result="结论：定价带上移。"))
    assert result["source"] == "llm"
    assert result["answer"] == "结论：定价带上移。"


def test_answer_reports_error_but_still_returns():
    store = make_store(
        [{"kind": KIND_IDEA, "title": "定价", "content": "定价带应当上移", "summary": "定价", "tags": []}]
    )
    result = answer(store, Settings(), "定价", llm=FakeLLM(raises=LLMError("超时")))
    assert result["source"] == "error"
    assert "超时" in result["answer"]


def test_extract_without_records():
    assert extract_highlights(MemoryStore(), Settings(), llm=None)["source"] == "none"


def test_extract_degrades_to_statistics():
    store = make_store(
        [
            {"kind": KIND_TODO, "title": "发方案", "content": "发方案", "summary": "发方案", "tags": ["定价"]},
            {"kind": KIND_IDEA, "title": "想法", "content": "想法", "summary": "想法", "tags": ["定价"]},
        ]
    )
    result = extract_highlights(store, Settings(), llm=None)
    assert result["source"] == "heuristic"
    assert "高频标签" in result["markdown"]


def test_extract_uses_llm():
    store = make_store([{"kind": KIND_IDEA, "title": "甲", "content": "甲", "summary": "甲", "tags": []}])
    result = extract_highlights(store, Settings(), llm=FakeLLM(chat_result="## 观点与判断\n- x"))
    assert result["source"] == "llm"
    assert "观点与判断" in result["markdown"]


def test_organize_todos_without_records():
    result = organize_todos(MemoryStore(), Settings(), llm=None)
    assert result["source"] == "none" and result["count"] == 0


def test_organize_todos_groups_by_first_tag_without_llm():
    store = make_store(
        [
            {"kind": KIND_TODO, "title": "发方案", "content": "发方案", "summary": "", "tags": ["定价"], "status": "open"},
            {"kind": KIND_TODO, "title": "约访谈", "content": "约访谈", "summary": "", "tags": ["客户"], "status": "open"},
        ]
    )
    result = organize_todos(store, Settings(), llm=None)
    assert result["source"] == "heuristic"
    assert {g["theme"] for g in result["groups"]} == {"定价", "客户"}


def test_organize_todos_skips_done_items():
    store = make_store(
        [{"kind": KIND_TODO, "title": "已完成", "content": "x", "summary": "", "tags": [], "status": "done"}]
    )
    assert organize_todos(store, Settings(), llm=None)["count"] == 0


def test_organize_todos_uses_llm():
    store = make_store(
        [{"kind": KIND_TODO, "title": "发方案", "content": "发方案", "summary": "", "tags": ["定价"], "status": "open"}]
    )
    llm = FakeLLM(json_result={"groups": [{"theme": "定价", "todos": [{"title": "发方案", "priority": 1}]}], "suggestions": ["先发草稿"]})
    result = organize_todos(store, Settings(), llm=llm)
    assert result["source"] == "llm"
    assert result["groups"][0]["theme"] == "定价"
    assert result["suggestions"] == ["先发草稿"]


def test_organize_todos_falls_back_on_garbage_from_llm():
    store = make_store(
        [{"kind": KIND_TODO, "title": "发方案", "content": "发方案", "summary": "", "tags": ["定价"], "status": "open"}]
    )
    result = organize_todos(store, Settings(), llm=FakeLLM(json_result={"groups": "not-a-list"}))
    assert result["source"] == "heuristic"


def test_build_summary_without_records():
    assert build_summary(MemoryStore(), Settings(), llm=None)["source"] == "none"


def test_build_summary_degrades_and_archives():
    store = make_store(
        [{"kind": KIND_IDEA, "title": "甲", "content": "甲", "summary": "甲", "tags": ["定价"]}]
    )
    result = build_summary(store, Settings(), days=7, llm=None)
    assert result["source"] == "heuristic"
    assert "阶段总结" in result["markdown"]
    assert store.list_summaries(), "每次总结都要存档，否则历史无从追溯"


def test_build_summary_uses_llm():
    store = make_store([{"kind": KIND_IDEA, "title": "甲", "content": "甲", "summary": "甲", "tags": []}])
    result = build_summary(store, Settings(), days=7, llm=FakeLLM(chat_result="## 概览\n- 一切正常"))
    assert result["source"] == "llm"
    assert "概览" in result["markdown"]


# -- 概览 ---------------------------------------------------------------------


def test_tag_cloud_counts_tags_and_kinds():
    store = make_store(
        [
            {"kind": KIND_IDEA, "title": "甲", "content": "甲", "summary": "甲", "tags": ["定价", "客户"]},
            {"kind": KIND_TODO, "title": "乙", "content": "乙", "summary": "乙", "tags": ["定价"]},
        ]
    )
    cloud = tag_cloud(store, Settings())
    assert cloud["total"] == 2
    assert cloud["tags"][0] == {"tag": "定价", "count": 2}
    assert cloud["kinds"]["todo"] == 1
