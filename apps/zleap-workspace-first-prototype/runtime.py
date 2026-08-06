"""Runtime 模块：可审计的运行轨迹记录。

对应 Zleap-Agent 设计中的 Runtime 概念：
- 每一次循环都应该留下可复盘的轨迹
- 记录读取的上下文、调用的工具、执行结果
- 支持轨迹查询与审计（原型用内存存储模拟 PostgreSQL 持久化）
"""

from __future__ import annotations

import time
from typing import Any, Dict, List


class RuntimeTrace:
    """单条运行轨迹记录。"""

    def __init__(
        self,
        workspace_id: str,
        action: str,
        context_snapshot: Dict[str, Any],
        result: Any,
    ) -> None:
        self.workspace_id = workspace_id
        self.action = action
        self.context_snapshot = context_snapshot
        self.result = result
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workspace_id": self.workspace_id,
            "action": self.action,
            "context_snapshot": self.context_snapshot,
            "result": self.result,
            "timestamp": self.timestamp,
        }

    def __repr__(self) -> str:
        return (
            f"RuntimeTrace(ws={self.workspace_id}, action={self.action}, "
            f"result={self.result})"
        )


class RuntimeRecorder:
    """运行轨迹记录器，记录每次执行的上下文与结果。"""

    def __init__(self) -> None:
        self._traces: List[RuntimeTrace] = []

    def start_session(self, workspace_id: str) -> None:
        """开始一次会话（记录上下文快照）。"""
        self._workspace_id = workspace_id

    def record(
        self,
        workspace_id: str,
        action: str,
        context_snapshot: Dict[str, Any],
        result: Any,
    ) -> RuntimeTrace:
        """记录一次执行轨迹。"""
        trace = RuntimeTrace(workspace_id, action, context_snapshot, result)
        self._traces.append(trace)
        return trace

    def query(self, workspace_id: str = "") -> List[RuntimeTrace]:
        """按工作区查询轨迹（空则返回全部）。"""
        if not workspace_id:
            return list(self._traces)
        return [t for t in self._traces if t.workspace_id == workspace_id]

    def audit(self, workspace_id: str = "") -> List[Dict[str, Any]]:
        """审计视图：返回可读的轨迹数据。"""
        return [t.to_dict() for t in self.query(workspace_id)]

    def __len__(self) -> int:
        return len(self._traces)