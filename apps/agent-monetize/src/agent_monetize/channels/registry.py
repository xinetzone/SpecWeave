"""通道注册表：注册 / 查找 / 枚举。"""

from __future__ import annotations

from typing import Any

from .base import Channel


class ChannelRegistry:
    """通道注册表（key = channel_id）。"""

    def __init__(self) -> None:
        self._channels: dict[str, Channel] = {}

    def register(self, channel: Channel) -> None:
        if not channel.channel_id:
            raise ValueError("channel_id 不能为空")
        self._channels[channel.channel_id] = channel

    def get(self, channel_id: str) -> Channel | None:
        return self._channels.get(channel_id)

    def get_or_raise(self, channel_id: str) -> Channel:
        if channel_id not in self._channels:
            raise KeyError(f"通道未注册: {channel_id}")
        return self._channels[channel_id]

    def all(self) -> list[Channel]:
        return list(self._channels.values())

    def enabled(self) -> list[Channel]:
        return [c for c in self._channels.values() if getattr(c, "enabled", True)]

    def register_all(self, channels: list[Channel]) -> None:
        for ch in channels:
            self.register(ch)

    def __contains__(self, channel_id: str) -> bool:
        return channel_id in self._channels

    def describe_all(self) -> dict[str, dict[str, Any]]:
        return {cid: ch.describe() for cid, ch in self._channels.items()}
