"""TR-2.1 / TR-2.2：tracker.md 解析器。"""

from pathlib import Path

import pytest

from zhihu_checkin_hub.errors import TrackerFormatError
from zhihu_checkin_hub.storage.tracker import parse_tracker, parse_tracker_text

FIXTURE = Path(__file__).parent / "fixtures" / "tracker.md"

EXPECTED_IDS = [
    "W1-1",
    "W1-3",
    "W1-6",
    "W1-2",
    "W1-4",
    "W1-5",
    "W1-GONOGO",
    "W1-CLOSE",
    "M1-1",
    "M1-2",
    "M1-3",
    "M1-4",
    "M1-5",
    "M1-6",
    "O-6",
    "MONTHLY-CHECK",
    "REVIEW-STALE",
    "REVIEW-OFFICIAL-RULES",
]


def test_parse_real_fixture() -> None:
    doc = parse_tracker(FIXTURE)
    assert [i.item_id for i in doc.items] == EXPECTED_IDS
    assert len(doc.items) == 18
    assert all(not i.checked for i in doc.items)
    assert all(i.section for i in doc.items)
    # 锚点表 7 行（含日期范围行）
    assert len(doc.anchors) == 7
    anchor_dates = [a.date_text for a in doc.anchors]
    assert "**2026-09-29**" in anchor_dates
    assert any("10-08" in d for d in anchor_dates)
    gonogo = doc.get("W1-GONOGO")
    assert gonogo is not None
    assert "Go/No-Go" in gonogo.label
    assert doc.checked_count == 0


def test_section_assignment() -> None:
    doc = parse_tracker(FIXTURE)
    assert doc.get("W1-1").section.startswith("二、")
    assert doc.get("M1-1").section.startswith("三、")
    assert doc.get("MONTHLY-CHECK").section.startswith("四、")
    assert doc.get("REVIEW-STALE").section.startswith("七、")


def test_parse_checked_line_with_marker_date() -> None:
    text = (
        "## 二、第 1 周\n\n"
        "- [x] 2026-09-25 **W1-1 报名当期打卡**：说明｜日期戳：2026-09-25｜验收\n"
    )
    doc = parse_tracker_text(text)
    item = doc.get("W1-1")
    assert item.checked is True
    assert item.date_stamp == "2026-09-25"


def test_parse_abandoned_note_kept() -> None:
    text = (
        "## 二、第 1 周\n\n"
        "- [x] 2026-09-25 **W1-1 报名当期打卡**：说明｜日期戳：2026-09-25 放弃/降频｜x\n"
    )
    doc = parse_tracker_text(text)
    item = doc.get("W1-1")
    assert item.checked is True
    assert "放弃/降频" in item.raw_line


def test_malformed_checkbox_raises() -> None:
    text = "## 二、第 1 周\n\n- [ ] 缺少加粗编号形态的行动项\n"
    with pytest.raises(TrackerFormatError):
        parse_tracker_text(text)


def test_unknown_id_raises() -> None:
    text = "## 二、第 1 周\n\n- [ ] **X9-9 未知编号**：说明\n"
    with pytest.raises(TrackerFormatError, match="编号"):
        parse_tracker_text(text)


def test_duplicate_id_raises() -> None:
    text = (
        "## 二、第 1 周\n\n"
        "- [ ] **W1-1 a**：x\n"
        "- [ ] **W1-1 b**：y\n"
    )
    with pytest.raises(TrackerFormatError, match="重复"):
        parse_tracker_text(text)
