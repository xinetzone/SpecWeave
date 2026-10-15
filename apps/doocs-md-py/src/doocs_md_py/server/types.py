"""同步与用户数据契约（upstream: apps/api/src/types.ts）。

线上传输为 camelCase JSON；存储与内部逻辑用 snake_case。时间戳一律 epoch 毫秒整数。
"""

from dataclasses import dataclass, field


@dataclass(slots=True)
class SyncHistoryEntry:
    """upstream: SyncDocument.history[]（datetime 新数据为 ms 数字，历史遗留可能是字符串）。"""

    datetime: int | str
    content: str

    def to_api_dict(self) -> dict:
        return {"datetime": self.datetime, "content": self.content}

    @classmethod
    def from_api_dict(cls, d: dict) -> "SyncHistoryEntry":
        return cls(datetime=d["datetime"], content=d["content"])


@dataclass(slots=True)
class SyncDocument:
    """upstream: apps/api/src/types.ts SyncDocument。"""

    id: str
    title: str
    content: str
    parent_id: str | None
    history: list[SyncHistoryEntry] = field(default_factory=list)
    create_datetime: int = 0
    update_datetime: int = 0
    deleted: bool = False

    def to_api_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "parentId": self.parent_id,
            "history": [h.to_api_dict() for h in self.history],
            "createDatetime": self.create_datetime,
            "updateDatetime": self.update_datetime,
            "deleted": self.deleted,
        }

    @classmethod
    def from_api_dict(cls, d: dict) -> "SyncDocument":
        raw_history = d.get("history") or []
        return cls(
            id=d["id"],
            title=d.get("title", ""),
            content=d.get("content", ""),
            parent_id=d.get("parentId"),
            history=[SyncHistoryEntry.from_api_dict(h) for h in raw_history],
            create_datetime=int(d["createDatetime"]),
            update_datetime=int(d["updateDatetime"]),
            deleted=bool(d.get("deleted", False)),
        )


@dataclass(slots=True)
class SyncSetting:
    """upstream: SyncSetting；value 是 localStorage 原始字符串或 null。"""

    key: str
    value: str | None
    updated_at: int

    def to_api_dict(self) -> dict:
        return {"key": self.key, "value": self.value, "updatedAt": self.updated_at}

    @classmethod
    def from_api_dict(cls, d: dict) -> "SyncSetting":
        return cls(key=d["key"], value=d.get("value"), updated_at=int(d["updatedAt"]))


@dataclass(slots=True)
class UserRow:
    """upstream: UserRow（users 表完整行；plan/plan_expires_at 由 0002 迁移加入）。"""

    id: str
    github_id: int
    login: str
    name: str | None
    avatar: str | None
    created_at: int
    plan: str = "free"
    plan_expires_at: int | None = None

    @classmethod
    def from_row(cls, row) -> "UserRow":
        return cls(
            id=row["id"],
            github_id=row["github_id"],
            login=row["login"],
            name=row["name"],
            avatar=row["avatar"],
            created_at=row["created_at"],
            plan=row["plan"],
            plan_expires_at=row["plan_expires_at"],
        )
