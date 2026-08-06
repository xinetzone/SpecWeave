"""Memory 模块：记忆三分区与双线设计。

对应 Zleap-Agent 设计中的 Memory 概念：
- 记忆要有归属，不能混成一个篮子
- 三分区：人（用户偏好）、事（项目事实）、经验（脱敏方法）
- 双线设计：A 线 people notes（用户偏好/画像）、B 线 core records（工作事件/经验）
- 经验记忆准入规则：允许 4 类 / 禁止 6 类
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# 记忆分区
PARTITION_PEOPLE = "people"      # 人：用户偏好、稳定画像
PARTITION_TASK = "task"          # 事：项目事实、工作事件
PARTITION_EXPERIENCE = "experience"  # 经验：脱敏方法、可复用流程

# 经验记忆准入规则：允许进入
ALLOWED_EXPERIENCE_KEYS = [
    "可复用流程",
    "失败模式",
    "验证习惯",
    "恢复策略",
]

# 经验记忆准入规则：禁止进入
FORBIDDEN_EXPERIENCE_KEYS = [
    "公司名",
    "客户名",
    "项目名",
    "财务事实",
    "私有路径",
    "一次性任务结果",
]


class MemoryStore:
    """单个记忆分区的存储。"""

    def __init__(self, partition: str) -> None:
        self.partition = partition
        self._entries: Dict[str, Any] = {}

    def write(self, key: str, value: Any) -> None:
        self._entries[key] = value
        logger.info("[MemoryStore] 写入分区=%s key=%r value=%r", self.partition, key, value)

    def read(self, key: str) -> Any:
        val = self._entries.get(key)
        logger.info("[MemoryStore] 读取分区=%s key=%r hit=%s", self.partition, key, val is not None)
        return val

    def read_all(self) -> Dict[str, Any]:
        logger.info("[MemoryStore] 读取全部分区=%s entries=%d", self.partition, len(self._entries))
        return dict(self._entries)

    def __len__(self) -> int:
        return len(self._entries)


class MemoryManager:
    """记忆管理器：三分区 + 双线设计 + 经验准入规则。

    分区：
    - people    : A 线 people notes（用户偏好/画像）
    - task      : B 线 core records（工作事件）
    - experience: B 线 core records（经验，脱敏）
    """

    def __init__(self) -> None:
        self._stores = {
            PARTITION_PEOPLE: MemoryStore(PARTITION_PEOPLE),
            PARTITION_TASK: MemoryStore(PARTITION_TASK),
            PARTITION_EXPERIENCE: MemoryStore(PARTITION_EXPERIENCE),
        }

    def write(self, partition: str, key: str, value: Any) -> None:
        """向指定分区写入记忆。"""
        if partition not in self._stores:
            logger.error("[MemoryManager] 写入失败：未知分区 %r", partition)
            raise KeyError(f"未知分区 {partition!r}")
        self._stores[partition].write(key, value)
        logger.info("[MemoryManager] 写入记忆 partition=%s key=%r", partition, key)

    def read(self, partition: str, key: str) -> Any:
        """从指定分区读取记忆。"""
        return self._stores[partition].read(key)

    def read_partition(self, partition: str) -> Dict[str, Any]:
        """读取整个分区。"""
        return self._stores[partition].read_all()

    # ---- 双线设计的便捷方法 ----
    def write_people_note(self, key: str, value: Any) -> None:
        """A 线：写入 people notes（用户偏好/画像）。"""
        self.write(PARTITION_PEOPLE, key, value)

    def write_core_record(self, key: str, value: Any) -> None:
        """B 线：写入 core records（工作事件）。"""
        self.write(PARTITION_TASK, key, value)

    # ---- 经验记忆准入规则 ----
    def write_experience(self, content: str, key: str = "") -> bool:
        """写入经验记忆，执行准入规则。

        返回 True 表示写入成功，False 表示被禁止项拦截。
        """
        lower = content.lower()
        # 禁止项检查
        for forbidden in FORBIDDEN_EXPERIENCE_KEYS:
            if forbidden.lower() in lower or forbidden in content:
                logger.info(
                    "[MemoryManager] 经验写入被拦截（禁止项）：content=%r forbidden=%r",
                    content, forbidden,
                )
                return False
        # 允许项检查：必须命中至少一个允许类别
        if not any(allow in content for allow in ALLOWED_EXPERIENCE_KEYS):
            logger.info(
                "[MemoryManager] 经验写入被拦截（未命中允许类别）：content=%r",
                content,
            )
            return False
        self.write(PARTITION_EXPERIENCE, key or content[:20], content)
        logger.info("[MemoryManager] 经验写入成功 content=%r", content)
        return True

    def all_partitions(self) -> Dict[str, Dict[str, Any]]:
        """返回全部分区内容。"""
        return {p: store.read_all() for p, store in self._stores.items()}


def build_default_memory() -> MemoryManager:
    """构建带示例数据的默认记忆管理器。"""
    mem = MemoryManager()
    # A 线：用户偏好
    mem.write_people_note("语言偏好", "中文")
    mem.write_people_note("工作风格", "偏好简洁输出")
    # B 线：工作事件
    mem.write_core_record("当前项目", "Zleap-Agent Harness 学习")
    # 经验：可复用流程（允许）
    mem.write_experience("可复用流程：先选工作区再组装上下文")
    return mem