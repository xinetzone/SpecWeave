"""TR-6：发布前固定门。"""

import shutil
from datetime import date, datetime
from pathlib import Path

import pytest

from zhihu_checkin_hub.domain.gate import ClauseUse, GateAnswers, evaluate_gate, pass_gate
from zhihu_checkin_hub.errors import GateRejected
from zhihu_checkin_hub.storage.entries import load_entry
from zhihu_checkin_hub.storage.workspace import open_workspace

FIXTURE = Path(__file__).parent / "fixtures" / "tracker.md"


def _answers(**over) -> GateAnswers:
    base = dict(
        deletion_tested=True,
        deletion_note="已做删稿测试，仅自己可见后删除",
        ratio_selfcheck=True,
        ratio_note="本期不依赖活动条款，常规回答 3 篇",
        clauses=(ClauseUse.SEARCH,),
        edge_confirmed=True,
        edge_note="无图片",
        kind="answer",
        draft_slug="first-answer",
    )
    base.update(over)
    return GateAnswers(**base)


@pytest.fixture()
def workspace(tmp_path: Path):
    d = tmp_path / "zhihu-monetization"
    d.mkdir()
    shutil.copy(FIXTURE, d / "tracker.md")
    return open_workspace(d)


def test_evaluate_pure_failures() -> None:
    failures, _ = evaluate_gate(_answers(deletion_tested=False))
    assert any("删稿" in f for f in failures)

    failures, _ = evaluate_gate(_answers(clauses=(ClauseUse.NONE, ClauseUse.EDIT)))
    assert any("冲突" in f for f in failures)

    failures, _ = evaluate_gate(_answers(clauses=()))
    assert any("条款留痕缺失" in f for f in failures)

    failures, _ = evaluate_gate(_answers(edge_confirmed=False, ratio_note=" "))
    assert any("边缘场景" in f for f in failures)
    assert any("占比自检缺少" in f for f in failures)

    failures, _ = evaluate_gate(_answers())
    assert failures == ()


def test_pass_gate_writes_entry_and_export(workspace) -> None:
    day = date(2026, 10, 1)
    clock = datetime(2026, 10, 1, 20, 0, 0)
    result = pass_gate(workspace, _answers(), day=day, now=clock)
    assert result.passed is True
    assert result.export_path.is_file()

    entry = load_entry(workspace, day)
    assert len(entry.gates) == 1
    assert entry.gates[0]["passed"] is True
    assert entry.gates[0]["clauses"] == ["search"]

    md = result.export_path.read_text(encoding="utf-8")
    assert "固定门" in md and "删稿" in md and "检索类" in md

    # 固定门每次发布独立留痕
    pass_gate(workspace, _answers(), day=day, now=clock)
    assert len(load_entry(workspace, day).gates) == 2


def test_reject_writes_nothing(workspace) -> None:
    day = date(2026, 10, 1)
    with pytest.raises(GateRejected):
        pass_gate(workspace, _answers(deletion_tested=False), day=day)
    entry = load_entry(workspace, day)
    assert entry.gates == []
    assert list((workspace.local / "gate-exports").glob("*.md")) == []
