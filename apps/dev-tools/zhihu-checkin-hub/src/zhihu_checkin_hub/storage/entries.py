"""每日打卡 entry：local/entries/YYYY-MM-DD.yaml。"""

from dataclasses import asdict, dataclass, field
from datetime import date
from enum import StrEnum
from pathlib import Path
from typing import Any

import yaml

from .atomic import atomic_write_text, dump_yaml
from .workspace import Workspace


class ContentKind(StrEnum):
    ARTICLE = "article"  # 专栏文章
    ANSWER = "answer"  # 问题回答
    PIN = "pin"  # 想法


class InteractionKind(StrEnum):
    FOLLOW = "follow"  # 关注
    COMMENT = "comment"  # 评论
    UPVOTE = "upvote"  # 赞同
    FAVORITE = "favorite"  # 收藏
    SHARE = "share"  # 分享


# 各类内容计入「合格创作」的最低字数（口径来自 tracker/content-plan 登记：回答 ≥100 F-033，想法 ≥20 F-040）
KIND_MIN_CHARS = {
    ContentKind.ANSWER: 100,
    ContentKind.PIN: 20,
    ContentKind.ARTICLE: 100,
}


@dataclass
class ContentRecord:
    kind: str
    char_count: int = 0
    url: str = ""
    question_url: str = ""
    draft_slug: str = ""
    published_at: str = ""


@dataclass
class Interaction:
    kind: str
    target: str = ""


@dataclass
class DayEntry:
    day: str  # YYYY-MM-DD
    contents: list[ContentRecord] = field(default_factory=list)
    interactions: list[Interaction] = field(default_factory=list)
    note: str = ""
    gates: list[dict[str, Any]] = field(default_factory=list)

    @property
    def as_date(self) -> date:
        return date.fromisoformat(self.day)


def entry_path(ws: Workspace, day: date) -> Path:
    return ws.entries_dir / f"{day.isoformat()}.yaml"


def load_entry(ws: Workspace, day: date) -> DayEntry:
    path = ws.ensure_within_local(entry_path(ws, day))
    if not path.is_file():
        return DayEntry(day=day.isoformat())
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return DayEntry(
        day=data.get("day", day.isoformat()),
        contents=[ContentRecord(**c) for c in data.get("contents", [])],
        interactions=[Interaction(**i) for i in data.get("interactions", [])],
        note=data.get("note", ""),
        gates=list(data.get("gates", [])),
    )


def save_entry(ws: Workspace, entry: DayEntry) -> Path:
    day = date.fromisoformat(entry.day)
    path = ws.ensure_within_local(entry_path(ws, day))
    payload = asdict(entry)
    atomic_write_text(path, dump_yaml(payload))
    return path


def load_all_entries(ws: Workspace) -> list[DayEntry]:
    if not ws.entries_dir.is_dir():
        return []
    entries: list[DayEntry] = []
    for path in sorted(ws.entries_dir.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        entries.append(
            DayEntry(
                day=data.get("day", path.stem),
                contents=[ContentRecord(**c) for c in data.get("contents", [])],
                interactions=[Interaction(**i) for i in data.get("interactions", [])],
                note=data.get("note", ""),
                gates=list(data.get("gates", [])),
            )
        )
    return entries


def is_qualified_day(entry: DayEntry) -> bool:
    """当日是否满足「1 合格创作 + 3 互动」底盘。"""
    content_ok = any(
        c.char_count >= KIND_MIN_CHARS.get(ContentKind(c.kind), 10**9)
        for c in entry.contents
    )
    return content_ok and len(entry.interactions) >= 3


def content_counts(entry: DayEntry) -> dict[str, int]:
    counts = {kind: 0 for kind in ContentKind}
    for c in entry.contents:
        counts[ContentKind(c.kind)] += 1
    return counts
