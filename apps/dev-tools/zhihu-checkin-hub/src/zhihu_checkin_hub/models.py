"""领域数据模型（frozen dataclass，解析层输出）。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Anchor:
    """§一 关键时间锚点表的一行。"""

    date_text: str
    event: str
    basis: str
    line_no: int


@dataclass(frozen=True)
class TrackerItem:
    """tracker.md 中的一条复选行动项。"""

    item_id: str
    label: str
    """加粗区全文，如「W1-1 报名当期打卡」。"""
    checked: bool
    date_stamp: str
    """勾选/字段中的日期戳；未勾选为空串。"""
    section: str
    line_no: int
    raw_line: str
    """含换行符的原始行（回写定位与审计用）。"""


@dataclass(frozen=True)
class TrackerDoc:
    """tracker.md 解析结果。"""

    path_text: str
    """绝对路径（展示用）。"""
    anchors: tuple[Anchor, ...]
    items: tuple[TrackerItem, ...]

    def get(self, item_id: str) -> TrackerItem | None:
        for item in self.items:
            if item.item_id == item_id:
                return item
        return None

    @property
    def checked_count(self) -> int:
        return sum(1 for i in self.items if i.checked)
