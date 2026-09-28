"""tracker.md 解析器。

行级解析，保留原文供回写器做字节级最小修改。任何复选行不符合既定形态即抛
``TrackerFormatError``（fail-fast，不静默丢弃）。
"""

import re
from pathlib import Path

from ..errors import TrackerFormatError
from ..models import Anchor, TrackerDoc, TrackerItem

_CHECKBOX_RE = re.compile(r"^(\s*)-\s+\[([ xX])\]\s*(.*)$")
_ITEM_RE = re.compile(r"^\*\*(.+?)\*\*\s*[：:](.*)$")
_CODE_ID_RE = re.compile(r"^(W\d+-\d+|M\d+-\d+|O-\d+)\b")
_DATE_FIELD_RE = re.compile(r"日期戳：([^｜|]*)")
_SECTION_RE = re.compile(r"^##\s+(.+?)\s*$")
_TABLE_SEP_RE = re.compile(r"^\|[\s:|-]+\|\s*$")

_SPECIAL_ID_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"Go/No-Go"), "W1-GONOGO"),
    (re.compile(r"收官"), "W1-CLOSE"),
    (re.compile(r"每月末勾选核对"), "MONTHLY-CHECK"),
    (re.compile(r"本系列强制复核"), "REVIEW-STALE"),
    (re.compile(r"官方细则发布"), "REVIEW-OFFICIAL-RULES"),
)


def _item_id(label: str) -> str:
    match = _CODE_ID_RE.match(label)
    if match:
        return match.group(1)
    for pattern, synthetic_id in _SPECIAL_ID_RULES:
        if pattern.search(label):
            return synthetic_id
    raise TrackerFormatError(f"无法识别行动项编号：{label}")


def _split_table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_tracker(path: str | Path) -> TrackerDoc:
    """解析 tracker.md。"""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    return parse_tracker_text(text, path_text=str(path))


def parse_tracker_text(text: str, *, path_text: str = "<mem>") -> TrackerDoc:
    """从文本解析 tracker.md（供测试与回写 round-trip 复用）。"""
    lines = text.splitlines(keepends=True)
    section = ""
    in_anchor_section = False
    anchors: list[Anchor] = []
    items: list[TrackerItem] = []
    seen_ids: set[str] = set()

    for idx, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        section_match = _SECTION_RE.match(stripped)
        if section_match:
            section = section_match.group(1)
            in_anchor_section = section.startswith("一、")
            continue

        checkbox = _CHECKBOX_RE.match(stripped)
        if checkbox:
            marker = checkbox.group(2)
            rest = checkbox.group(3)
            # 剥离标记后可选日期前缀（[x] 2026-09-25 **...**）
            rest = re.sub(r"^\d{4}-\d{2}-\d{2}\s*", "", rest)
            item_match = _ITEM_RE.match(rest)
            if not item_match:
                raise TrackerFormatError(
                    "复选行动项缺少 **加粗编号标题：** 形态，解析器拒绝猜测", idx
                )
            label = item_match.group(1)
            item_id = _item_id(label)
            if item_id in seen_ids:
                raise TrackerFormatError(f"行动项编号重复：{item_id}", idx)
            seen_ids.add(item_id)

            date_stamp = ""
            # 复选标记后直接跟日期的形态：[x] 2026-09-24
            m = re.search(r"\[[xX]\]\s*(\d{4}-\d{2}-\d{2})?", stripped)
            if m and m.group(1):
                date_stamp = m.group(1)
            # 「日期戳：____」字段
            field_match = _DATE_FIELD_RE.search(rest)
            if field_match:
                field_value = field_match.group(1).strip()
                if field_value and field_value != "____":
                    value_date = re.match(r"(\d{4}-\d{2}-\d{2})", field_value)
                    if not date_stamp and value_date:
                        date_stamp = value_date.group(1)

            checked = marker.lower() == "x"
            items.append(
                TrackerItem(
                    item_id=item_id,
                    label=label,
                    checked=checked,
                    date_stamp=date_stamp,
                    section=section,
                    line_no=idx,
                    raw_line=raw,
                )
            )
            continue

        # 锚点表（仅在 §一 内解析三列数据表）
        if in_anchor_section and stripped.startswith("|") and stripped.endswith("|"):
            if _TABLE_SEP_RE.match(stripped):
                continue
            cells = _split_table_cells(stripped)
            if cells[:3] == ["日期", "事件", "依据"]:
                continue
            if len(cells) < 3:
                raise TrackerFormatError("关键时间锚点表列数不足 3 列", idx)
            date_text, event, basis = cells[0], cells[1], cells[2]
            if not date_text or not event:
                raise TrackerFormatError("关键时间锚点表存在空单元格", idx)
            anchors.append(
                Anchor(date_text=date_text, event=event, basis=basis, line_no=idx)
            )

    return TrackerDoc(
        path_text=path_text,
        anchors=tuple(anchors),
        items=tuple(items),
    )
