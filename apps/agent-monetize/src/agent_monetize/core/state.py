"""状态持久化：LoopState ↔ JSON 文件（余额、通道权重、历史记录）。"""

from __future__ import annotations

import json
import logging
import os

from ..models import ChannelState, LoopState

logger = logging.getLogger(__name__)


def _channel_from_dict(data: dict) -> ChannelState:
    history = data.get("history", [])
    return ChannelState(
        channel_id=data["channel_id"],
        weight=float(data.get("weight", 1.0)),
        revenue=float(data.get("revenue", 0.0)),
        cost=float(data.get("cost", 0.0)),
        conversions=int(data.get("conversions", 0)),
        actions=int(data.get("actions", 0)),
        enabled=bool(data.get("enabled", True)),
        history=list(history) if isinstance(history, list) else [],
    )


class StateStore:
    """LoopState 的 JSON 持久化存储。"""

    def save(self, state: LoopState, path: str) -> None:
        """将循环状态保存为 JSON。"""
        directory = os.path.dirname(os.path.abspath(path))
        os.makedirs(directory, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state.to_dict(), f, ensure_ascii=False, indent=2)
        logger.info("状态已持久化到 %s", path)

    def load(self, path: str) -> LoopState | None:
        """从 JSON 加载循环状态；文件不存在返回 None。"""
        if not os.path.exists(path):
            return None
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        state = LoopState(
            balance=float(data.get("balance", 0.0)),
            round_count=int(data.get("round_count", 0)),
        )
        for cid, cdata in (data.get("channels") or {}).items():
            state.channels[cid] = _channel_from_dict(cdata)
        return state
