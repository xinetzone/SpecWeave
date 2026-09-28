"""pytest 公共夹具。"""

from pathlib import Path

import pytest


def make_tracker(path: Path) -> Path:
    tracker = path / "tracker.md"
    tracker.write_text(
        "# 知乎变现执行台账（tracker）\n\n"
        "## 二、第 1 周\n\n"
        "- [ ] **W1-1 报名当期打卡**：说明文字｜日期戳：____｜验收见链接\n"
        "- [ ] **W1-2 首日打卡**：说明文字｜日期戳：____｜验收见链接\n",
        encoding="utf-8",
    )
    return tracker


@pytest.fixture()
def workbench(tmp_path: Path) -> Path:
    """一个合法的临时执行工作台（含 tracker.md，无 local/）。"""
    ws = tmp_path / "zhihu-monetization"
    ws.mkdir()
    make_tracker(ws)
    return ws
