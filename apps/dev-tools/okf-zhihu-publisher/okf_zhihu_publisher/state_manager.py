"""状态文件管理。

维护 publish-state.json，记录每个已发布内容项的状态，
用于增量同步的判断依据。
"""

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional


# ── 数据结构 ──────────────────────────────────────────────


@dataclass
class ContentState:
    """单个内容项的同步状态。"""

    # 本地相对路径（相对 bundles_dir），如 "jishu/ai/ai-agent/zhihu-cli/index.md"
    local_path: str
    # 远程内容 ID（RecallContentID）
    recall_content_id: str
    # 文件内容 SHA256 哈希（十六进制）
    content_hash: str
    # 所属知识库 ID
    knowledge_base_id: str
    # 上传后的标题（含层级前缀）
    remote_title: str
    # 上次同步时间戳（秒级）
    synced_at: int
    # 文件大小（字节）
    file_size: int


@dataclass
class PublishState:
    """发布状态文件。"""

    version: int = 1
    # 状态项：{local_path: ContentState}
    items: dict[str, ContentState] = field(default_factory=dict)
    # 默认知识库 ID
    default_kb_id: Optional[str] = None
    # 最后一次全量扫描时间
    last_full_scan_at: int = 0


# ── 状态管理器 ────────────────────────────────────────────


class StateManager:
    """发布状态管理器。"""

    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.state = PublishState()
        self._loaded = False

    # ── 持久化 ────────────────────────────────────────

    def load(self) -> None:
        """从磁盘加载状态文件。"""
        if not self.state_file.exists():
            self._loaded = True
            return

        with open(self.state_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.state.version = data.get("version", 1)
        self.state.default_kb_id = data.get("default_kb_id")
        self.state.last_full_scan_at = data.get("last_full_scan_at", 0)

        items_data = data.get("items", {})
        for path, item_data in items_data.items():
            self.state.items[path] = ContentState(
                local_path=item_data["local_path"],
                recall_content_id=item_data["recall_content_id"],
                content_hash=item_data["content_hash"],
                knowledge_base_id=item_data["knowledge_base_id"],
                remote_title=item_data.get("remote_title", ""),
                synced_at=item_data.get("synced_at", 0),
                file_size=item_data.get("file_size", 0),
            )

        self._loaded = True

    def save(self) -> None:
        """保存状态到磁盘。"""
        data = {
            "version": self.state.version,
            "default_kb_id": self.state.default_kb_id,
            "last_full_scan_at": self.state.last_full_scan_at,
            "items": {
                path: asdict(item) for path, item in self.state.items.items()
            },
        }
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ── 查询 ──────────────────────────────────────────

    def get(self, local_path: str) -> Optional[ContentState]:
        """获取指定路径的状态。"""
        if not self._loaded:
            self.load()
        return self.state.items.get(local_path)

    def has(self, local_path: str) -> bool:
        """检查指定路径是否有记录。"""
        if not self._loaded:
            self.load()
        return local_path in self.state.items

    def all_paths(self) -> set[str]:
        """返回所有已记录的本地路径集合。"""
        if not self._loaded:
            self.load()
        return set(self.state.items.keys())

    # ── 更新 ──────────────────────────────────────────

    def upsert(
        self,
        local_path: str,
        recall_content_id: str,
        content_hash: str,
        knowledge_base_id: str,
        remote_title: str,
        synced_at: int,
        file_size: int,
    ) -> None:
        """新增或更新一条状态记录。"""
        if not self._loaded:
            self.load()
        self.state.items[local_path] = ContentState(
            local_path=local_path,
            recall_content_id=recall_content_id,
            content_hash=content_hash,
            knowledge_base_id=knowledge_base_id,
            remote_title=remote_title,
            synced_at=synced_at,
            file_size=file_size,
        )

    def remove(self, local_path: str) -> bool:
        """删除一条状态记录。返回是否存在。"""
        if not self._loaded:
            self.load()
        if local_path in self.state.items:
            del self.state.items[local_path]
            return True
        return False

    def set_default_kb_id(self, kb_id: str) -> None:
        """设置默认知识库 ID。"""
        if not self._loaded:
            self.load()
        self.state.default_kb_id = kb_id

    def get_default_kb_id(self) -> Optional[str]:
        """获取记录的默认知识库 ID。"""
        if not self._loaded:
            self.load()
        return self.state.default_kb_id

    # ── 重建 ──────────────────────────────────────────

    def rebuild_from_remote(
        self,
        remote_items: dict[str, str],  # {title: recall_content_id}
        knowledge_base_id: str,
    ) -> int:
        """从远程列表重建状态（用于状态文件丢失时恢复）。

        注意：从远程无法获取内容哈希，因此哈希字段留空，
        下次同步时会按标题匹配并重新计算哈希。

        Returns:
            重建的条目数
        """
        if not self._loaded:
            self.load()

        count = 0
        for title, content_id in remote_items.items():
            # 用标题作为临时 key（因为不知道原始路径）
            self.state.items[f"remote:{title}"] = ContentState(
                local_path=f"remote:{title}",
                recall_content_id=content_id,
                content_hash="",  # 未知
                knowledge_base_id=knowledge_base_id,
                remote_title=title,
                synced_at=0,
                file_size=0,
            )
            count += 1

        return count

    # ── 工具方法 ──────────────────────────────────────

    @staticmethod
    def compute_file_hash(file_path: Path) -> str:
        """计算文件内容的 SHA256 哈希。"""
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()

    def count(self) -> int:
        """返回状态记录总数。"""
        if not self._loaded:
            self.load()
        return len(self.state.items)
