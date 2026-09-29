"""TR-3.1 / TR-3.2：tracker.md 行级安全回写。"""

import shutil
from pathlib import Path

import pytest

from zhihu_checkin_hub.errors import StorageError
from zhihu_checkin_hub.storage.checkoff import check_off
from zhihu_checkin_hub.storage.tracker import parse_tracker
from zhihu_checkin_hub.storage.workspace import open_workspace

FIXTURE = Path(__file__).parent / "fixtures" / "tracker.md"


@pytest.fixture()
def live_workbench(tmp_path: Path) -> Path:
    ws = tmp_path / "zhihu-monetization"
    ws.mkdir()
    shutil.copy(FIXTURE, ws / "tracker.md")
    return ws


def _lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", newline="").splitlines(keepends=True)


def test_checkoff_byte_level_diff(live_workbench: Path) -> None:
    original_lines = _lines(live_workbench / "tracker.md")
    workspace = open_workspace(live_workbench)

    r1 = check_off(workspace, "W1-1", "2026-09-28")
    assert r1.changed is True
    assert r1.backup_path is not None and r1.backup_path.is_file()

    # 幂等重复
    r1b = check_off(workspace, "W1-1", "2026-09-28")
    assert r1b.changed is False

    r2 = check_off(workspace, "M1-1", "2026-09-28")
    assert r2.changed is True

    new_lines = _lines(live_workbench / "tracker.md")
    assert len(new_lines) == len(original_lines)
    changed_idx = {r1.changed_line_no - 1, r2.changed_line_no - 1}
    for i, (before, after) in enumerate(zip(original_lines, new_lines, strict=True)):
        if i in changed_idx:
            assert before != after
        else:
            assert before == after, f"非目标行被改动：第 {i + 1} 行"

    w1_line = new_lines[r1.changed_line_no - 1]
    assert "- [x] 2026-09-28 **W1-1" in w1_line
    assert "日期戳：2026-09-28" in w1_line
    assert "____" not in w1_line

    doc = parse_tracker(live_workbench / "tracker.md")
    assert doc.get("W1-1").checked
    assert doc.get("W1-1").date_stamp == "2026-09-28"
    assert doc.checked_count == 2


def test_checkoff_unknown_item_no_change(live_workbench: Path) -> None:
    before = (live_workbench / "tracker.md").read_bytes()
    workspace = open_workspace(live_workbench)
    with pytest.raises(StorageError, match="不存在"):
        check_off(workspace, "W9-9", "2026-09-28")
    assert (live_workbench / "tracker.md").read_bytes() == before


def test_checkoff_preserves_crlf(live_workbench: Path) -> None:
    tracker = live_workbench / "tracker.md"
    raw = tracker.read_text(encoding="utf-8", newline="")
    # 统一成 CRLF（真实文件为 LF；防止 Windows 编辑后换行被破坏）
    tracker.write_bytes(raw.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8"))
    before = _lines(tracker)

    workspace = open_workspace(live_workbench)
    r = check_off(workspace, "W1-1", "2026-09-28")
    assert r.changed is True
    after = _lines(tracker)
    assert len(after) == len(before)
    # 行尾形态保持（含末行无终止符的情形）；除目标行外逐字节不变
    for i, (b, a) in enumerate(zip(before, after, strict=True)):
        assert a.endswith("\r\n") == b.endswith("\r\n"), f"第 {i + 1} 行行尾被改变"
        if i != r.changed_line_no - 1:
            assert a == b, f"非目标行被改动：第 {i + 1} 行"
    assert after[r.changed_line_no - 1].endswith("\r\n")
    # 幂等：再次勾选零改动且行尾形态不变
    assert check_off(workspace, "W1-1", "2026-09-28").changed is False
    final = _lines(tracker)
    assert all(
        a.endswith("\r\n") == b.endswith("\r\n") for a, b in zip(final, before, strict=True)
    )


def test_backup_is_original(live_workbench: Path) -> None:
    original_bytes = (live_workbench / "tracker.md").read_bytes()
    workspace = open_workspace(live_workbench)
    result = check_off(workspace, "W1-2", "2026-09-28")
    assert result.backup_path.read_bytes() == original_bytes
