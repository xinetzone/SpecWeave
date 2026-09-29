"""发布前固定门：四项全绿才放行。

四项（缺一不可，任一否/缺说明即 ``GateRejected``）：
1. 删稿测试：已做真实删稿/仅自己可见测试，并留说明；
2. 占比自检：确认本期创作不依赖活动条款（检索/编辑/调试占比达标）；
3. 条款留痕：勾选实际用到的检索/编辑/调试三级条款，或显式「无」；
4. 边缘场景：主动确认已处理边缘场景（如图片、转载、活动边界）。
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

from ..errors import GateRejected
from ..storage.atomic import atomic_write_text
from ..storage.entries import load_entry, save_entry
from ..storage.workspace import Workspace


class ClauseUse(StrEnum):
    SEARCH = "search"  # 检索类条款
    EDIT = "edit"  # 编辑类条款
    DEBUG = "debug"  # 调试类条款
    NONE = "none"  # 显式声明：以上均未使用


_CLAUSE_LABELS = {
    ClauseUse.SEARCH: "检索类",
    ClauseUse.EDIT: "编辑类",
    ClauseUse.DEBUG: "调试类",
    ClauseUse.NONE: "无",
}


@dataclass(frozen=True)
class GateAnswers:
    deletion_tested: bool
    deletion_note: str
    ratio_selfcheck: bool
    ratio_note: str
    clauses: tuple[str, ...]
    edge_confirmed: bool
    edge_note: str = ""
    kind: str = ""
    draft_slug: str = ""


@dataclass(frozen=True)
class GateResult:
    passed: bool
    at: str
    failures: tuple[str, ...]
    record: dict[str, Any] = field(default_factory=dict)
    export_path: Path | None = None


def evaluate_gate(answers: GateAnswers) -> tuple[tuple[str, ...], dict[str, Any]]:
    """纯函数：返回（失败原因列表，留痕记录 dict）。不抛异常、不写盘。"""
    failures: list[str] = []

    if not answers.deletion_tested:
        failures.append("删稿测试未完成：必须先做一次真实删稿/仅自己可见测试")
    if not answers.deletion_note.strip():
        failures.append("删稿测试缺少说明留痕")

    if not answers.ratio_selfcheck:
        failures.append("占比自检未通过：不得声称或依赖活动条款收益")
    if not answers.ratio_note.strip():
        failures.append("占比自检缺少说明留痕")

    clauses = set(answers.clauses)
    if not clauses:
        failures.append("条款留痕缺失：至少勾选实际使用的条款级别，或显式选择「无」")
    elif ClauseUse.NONE in clauses and len(clauses) > 1:
        failures.append("条款留痕冲突：「无」不能与检索/编辑/调试同时选择")
    else:
        invalid = clauses - {c.value for c in ClauseUse}
        if invalid:
            failures.append(f"条款留痕含非法取值：{sorted(invalid)}")

    if not answers.edge_confirmed:
        failures.append("边缘场景未主动确认（图片/转载/活动边界等）")

    record = {
        "deletion_tested": answers.deletion_tested,
        "deletion_note": answers.deletion_note.strip(),
        "ratio_selfcheck": answers.ratio_selfcheck,
        "ratio_note": answers.ratio_note.strip(),
        "clauses": sorted(clauses),
        "edge_confirmed": answers.edge_confirmed,
        "edge_note": answers.edge_note.strip(),
        "kind": answers.kind,
        "draft_slug": answers.draft_slug,
    }
    return tuple(failures), record


def _export_markdown(ws: Workspace, record: dict[str, Any], at: str, day: str) -> Path:
    ws.ensure_dirs()
    stamp = at.replace(":", "").replace("-", "").replace("T", "-")
    path = ws.ensure_within_local(ws.gate_exports_dir / f"gate-{stamp}.md")
    counter = 1
    while path.exists():
        path = ws.ensure_within_local(ws.gate_exports_dir / f"gate-{stamp}-{counter}.md")
        counter += 1
    clause_text = "、".join(_CLAUSE_LABELS[ClauseUse(c)] for c in record["clauses"])
    lines = [
        f"# 发布前固定门留痕（{day}）",
        "",
        "| 项目 | 结果 | 说明 |",
        "| --- | --- | --- |",
        f"| 删稿测试 | 已完成 | {record['deletion_note']} |",
        f"| 占比自检 | 已确认 | {record['ratio_note']} |",
        f"| 条款留痕 | {clause_text} | — |",
        f"| 边缘场景 | 已确认 | {record['edge_note'] or '—'} |",
        "",
        f"- 内容类型：{record['kind'] or '—'}",
        f"- 草稿：{record['draft_slug'] or '—'}",
        f"- 通过时间：{at}",
        "",
    ]
    atomic_write_text(path, "\n".join(lines))
    return path


def pass_gate(
    ws: Workspace,
    answers: GateAnswers,
    *,
    day: date | None = None,
    now: datetime | None = None,
) -> GateResult:
    """评估固定门；通过才写当日 entry 与 gate-exports 留痕，否则抛 GateRejected。"""
    day = day or date.today()
    at = (now or datetime.now()).isoformat(timespec="seconds")
    failures, record = evaluate_gate(answers)
    if failures:
        raise GateRejected("固定门未通过：\n- " + "\n- ".join(failures))

    record = {"passed": True, "at": at, **record}
    entry = load_entry(ws, day)
    entry.gates.append(record)
    save_entry(ws, entry)
    export_path = _export_markdown(ws, record, at, day.isoformat())
    return GateResult(passed=True, at=at, failures=(), record=record, export_path=export_path)
