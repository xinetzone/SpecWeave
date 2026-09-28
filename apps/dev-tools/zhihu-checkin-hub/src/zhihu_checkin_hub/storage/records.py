"""四类台账：local/records/*.yaml（append-only，修正追加不覆盖）。"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from ..errors import StorageError
from .atomic import atomic_write_text, dump_yaml
from .workspace import Workspace


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _table_path(ws: Workspace, name: str) -> Path:
    return ws.ensure_within_local(ws.records_dir / f"{name}.yaml")


def _load_rows(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return []
    if not isinstance(data, list):
        raise StorageError(f"台账 {path.name} 顶层必须是列表")
    return data


def _save_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    atomic_write_text(path, dump_yaml(rows))


# ---------------- earnings（盐粒，append-only + corrections 追加） ----------------


def add_earning(
    ws: Workspace, *, day: str, action: str, salt_raw: str, note: str = ""
) -> dict[str, Any]:
    """登记一条盐粒到账。salt_raw 只允许整数盐粒；人民币换算不在应用内估算。"""
    try:
        salt = int(salt_raw)
    except (TypeError, ValueError) as exc:
        raise StorageError("盐粒必须是整数（官方创作者中心显示值）") from exc
    if salt < 0:
        raise StorageError("盐粒不允许负数；扣减请用修正记录。")
    row = {
        "id": uuid.uuid4().hex[:12],
        "date": day,
        "action": action,
        "salt_raw": salt,
        "currency": "salt",
        "note": note,
        "created_at": _now(),
        "corrections": [],
    }
    path = _table_path(ws, "earnings")
    rows = _load_rows(path)
    rows.append(row)
    _save_rows(path, rows)
    return row


def correct_earning(ws: Workspace, *, row_id: str, new_salt: int, note: str) -> dict[str, Any]:
    path = _table_path(ws, "earnings")
    rows = _load_rows(path)
    for row in rows:
        if row["id"] == row_id:
            row.setdefault("corrections", []).append(
                {"from": row["salt_raw"], "to": new_salt, "note": note, "at": _now()}
            )
            row["salt_raw"] = new_salt
            _save_rows(path, rows)
            return row
    raise StorageError(f"未找到盐粒记录：{row_id}")


# ---------------- weekly（周执行台账） ----------------


def upsert_weekly(
    ws: Workspace,
    *,
    week_id: str,
    start: str,
    end: str,
    answers: int,
    pins: int,
    confirmed: int,
    note: str = "",
) -> dict[str, Any]:
    if answers < 0 or pins < 0 or not 0 <= confirmed <= 3:
        raise StorageError("周台账数值非法（answers/pins 非负，confirmed ∈ 0..3）")
    path = _table_path(ws, "weekly")
    rows = _load_rows(path)
    for row in rows:
        if row["week_id"] == week_id:
            row.update(
                answers=answers, pins=pins, confirmed=confirmed, note=note, updated_at=_now()
            )
            _save_rows(path, rows)
            return row
    row = {
        "week_id": week_id,
        "start": start,
        "end": end,
        "answers": answers,
        "pins": pins,
        "confirmed": confirmed,
        "note": note,
        "created_at": _now(),
    }
    rows.append(row)
    _save_rows(path, rows)
    return row


# ---------------- interruptions（中断/断档） ----------------


def add_interruption(
    ws: Workspace, *, start_day: str, days: int, reason: str, resumed_at: str = ""
) -> dict[str, Any]:
    if days < 1:
        raise StorageError("中断天数必须 ≥ 1")
    row = {
        "id": uuid.uuid4().hex[:12],
        "start_day": start_day,
        "days": days,
        "reason": reason,
        "resumed_at": resumed_at,
        "created_at": _now(),
    }
    path = _table_path(ws, "interruptions")
    rows = _load_rows(path)
    rows.append(row)
    _save_rows(path, rows)
    return row


# ---------------- reviews（周期复核） ----------------


def add_review(
    ws: Workspace,
    *,
    day: str,
    salt_total: int,
    decision: str,
    reason: str,
    note: str = "",
) -> dict[str, Any]:
    if decision not in {"continue", "pause", "stop"}:
        raise StorageError("复核决定必须是 continue/pause/stop")
    row = {
        "id": uuid.uuid4().hex[:12],
        "date": day,
        "salt_total": salt_total,
        # 折算口径：官方 100 盐粒=1 元（F-059），仅在展示层换算并强制标注
        "yuan_estimate": salt_total // 100,
        "conversion_basis": "F-059：100 盐粒 = 1 元（估算，非承诺收益）",
        "decision": decision,
        "reason": reason,
        "note": note,
        "created_at": _now(),
    }
    path = _table_path(ws, "reviews")
    rows = _load_rows(path)
    rows.append(row)
    _save_rows(path, rows)
    return row


def load_table(ws: Workspace, name: str) -> list[dict[str, Any]]:
    """通用只读加载（供仪表盘与导出使用）。"""
    return _load_rows(_table_path(ws, name))
