"""提示词装配测试：编号锚点、上下文预算截断、降级文案。"""

import pytest

from okfqa import prompts
from okfqa.retrieval import Hit


def _hit(idx: int, body: str) -> Hit:
    return Hit(
        chunk_id=idx,
        title=f"标题{idx}",
        body=body,
        bundle=f"domain/group/bundle{idx}",
        grp="group",
        domain="domain",
        path=f"domain/group/bundle{idx}/concepts/01.md",
        score=0.0,
    )


def test_build_context_numbers_from_one() -> None:
    hits = [_hit(1, "甲内容"), _hit(2, "乙内容")]
    ctx = prompts.build_context(hits)
    assert ctx.startswith("[1]《标题1》")
    assert "[2]《标题2》" in ctx
    assert "bundle1" in ctx


def test_build_context_respects_budget(monkeypatch) -> None:
    """超出预算时必须截断，而不是把 6 段长文本整体塞进 prompt 撑爆 token。"""
    monkeypatch.setenv("MAX_CONTEXT_CHARS", "600")
    hits = [_hit(i, "知" * 400) for i in range(1, 7)]
    ctx = prompts.build_context(hits)
    assert len(ctx) <= 650
    assert ctx.startswith("[1]")


def test_build_context_drops_chunk_without_room(monkeypatch) -> None:
    """剩余预算不足 200 字符时整体丢弃后续片段，避免产出无意义的半截文本。"""
    monkeypatch.setenv("MAX_CONTEXT_CHARS", "250")
    hits = [_hit(1, "知" * 100), _hit(2, "识" * 100), _hit(3, "包" * 100)]
    ctx = prompts.build_context(hits)
    assert "[1]" in ctx
    assert "[3]" not in ctx


def test_build_context_truncated_chunk_ends_with_ellipsis(monkeypatch) -> None:
    """剩余预算 > 200 时，截断后追加省略号而非整段丢弃。"""
    monkeypatch.setenv("MAX_CONTEXT_CHARS", "400")
    ctx = prompts.build_context([_hit(1, "甲" * 100), _hit(2, "乙" * 400)])
    assert ctx.rstrip().endswith("…")
    assert "[2]" in ctx  # 第二段被截断保留，而非丢弃


def test_build_user_prompt_contains_question_and_material() -> None:
    prompt = prompts.build_user_prompt("道法自然是什么", [_hit(1, "甲内容")])
    assert "【参考资料】" in prompt
    assert "【用户问题】" in prompt
    assert "道法自然是什么" in prompt
    assert "甲内容" in prompt


def test_build_degraded_answer_states_reason_and_cites() -> None:
    text = prompts.build_degraded_answer([_hit(1, "甲内容"), _hit(2, "乙内容")])
    assert "未配置大模型凭据" in text
    assert "[1]" in text and "[2]" in text


def test_build_degraded_answer_truncates_long_body() -> None:
    text = prompts.build_degraded_answer([_hit(1, "长" * 1000)])
    assert "…" in text
    assert len(text) < 500


def test_system_prompt_forbids_fabrication() -> None:
    """系统提示必须显式禁止编造，否则模型会用先验知识填补检索空缺。"""
    assert "禁止" in prompts.SYSTEM_PROMPT
    assert "未涉及" in prompts.SYSTEM_PROMPT


@pytest.mark.parametrize("hits", [[], None])
def test_build_context_handles_empty(hits) -> None:
    assert prompts.build_context(hits or []) == ""
