"""tracker.md 安全回写：行级最小替换 + 写前备份 + 幂等。"""

import os
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from ..errors import StorageError, TrackerFormatError
from ..models import TrackerItem
from .tracker import parse_tracker, parse_tracker_text
from .workspace import Workspace


@dataclass(frozen=True)
class CheckOffResult:
    item_id: str
    changed: bool
    date_text: str
    changed_line_no: int | None
    backup_path: Path | None
    note: str = ""


def _backup(workspace: Workspace, original: str) -> Path:
    workspace.ensure_dirs()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = workspace.backups_dir / f"tracker-{stamp}.md"
    counter = 1
    while path.exists():
        path = workspace.backups_dir / f"tracker-{stamp}-{counter}.md"
        counter += 1
    path.write_text(original, encoding="utf-8", newline="")
    return path


def _rewrite_line(line: str, item: TrackerItem, date_text: str) -> str:
    """在单行内做最小替换：复选标记与日期戳字段；保留行尾换行。"""
    if "- [ ]" not in line:
        raise TrackerFormatError(
            f"行动项 {item.item_id} 当前行不是未勾选形态，拒绝写入", item.line_no
        )
    updated = line.replace("- [ ]", f"- [x] {date_text}", 1)
    if "日期戳：____" in updated:
        updated = updated.replace("日期戳：____", f"日期戳：{date_text}", 1)
    return updated


def check_off(
    workspace: Workspace,
    item_id: str,
    when: date | str | None = None,
) -> CheckOffResult:
    """勾选指定行动项。幂等：重复勾选不改文件；已勾选不同日期保持原样。"""
    date_text = (when or date.today()).isoformat() if not isinstance(when, str) else when
    tracker_path = workspace.tracker
    # newline="" 关闭换行转换，保证非目标行字节级不变（兼容 CRLF 文件）
    original = tracker_path.read_text(encoding="utf-8", newline="")
    doc = parse_tracker_text(original, path_text=str(tracker_path))

    item = doc.get(item_id)
    if item is None:
        raise StorageError(f"tracker.md 中不存在行动项：{item_id}")
    if item.checked:
        return CheckOffResult(
            item_id=item_id,
            changed=False,
            date_text=item.date_stamp or date_text,
            changed_line_no=None,
            backup_path=None,
            note="该条目已勾选，重复操作保持原文件不变（幂等）。",
        )

    lines = original.splitlines(keepends=True)
    idx = item.line_no - 1
    lines[idx] = _rewrite_line(lines[idx], item, date_text)
    updated_text = "".join(lines)
    if updated_text == original:
        raise StorageError(f"勾选 {item_id} 未产生任何变化，疑似行形态异常，已中止。")

    backup_path = _backup(workspace, original)
    tmp = tracker_path.with_name(f".{tracker_path.name}.tmp")
    try:
        tmp.write_text(updated_text, encoding="utf-8", newline="")
        os.replace(tmp, tracker_path)
    except OSError as exc:
        raise StorageError(f"写回 tracker.md 失败：{exc}") from exc

    # round-trip 校验
    verify = parse_tracker(tracker_path)
    verified = verify.get(item_id)
    if verified is None or not verified.checked or verified.date_stamp != date_text:
        raise StorageError(
            f"回写后校验失败：{item_id} 状态/日期戳与预期不一致，请从备份恢复：{backup_path}"
        )

    return CheckOffResult(
        item_id=item_id,
        changed=True,
        date_text=date_text,
        changed_line_no=item.line_no,
        backup_path=backup_path,
    )
