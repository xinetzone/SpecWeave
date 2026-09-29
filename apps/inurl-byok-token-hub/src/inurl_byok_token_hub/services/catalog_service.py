"""厂商目录服务：加载种子目录、快照语义与能力维度查询。

口径（源文档 F-077/F-082/F-090/F-091）：46 家厂商 = 17 free + 29 paid，其中 10 家
``public: false`` 的付费厂商虽不在 /models 页面渲染，但仍随公开接口下发；共 133 个
模型；能力标签仅 text/code/image 三类，video/audio 无可路由模型，查询时抛
``UNSUPPORTED_CAPABILITY``。

快照语义（源文档 F-090）：目录在进程启动时读入内存，运行期改动需重启代理才生效，
因此本服务只在 :meth:`CatalogService.load` / :meth:`CatalogService.reload` 时读盘。
"""

import json
from collections.abc import Iterable
from pathlib import Path

from ..config import Settings
from ..errors import ByokError, ConfigError, ErrorCode
from ..models.catalog import Capability, Catalog, ModelEntry, Provider, Tier

#: ``UNSUPPORTED_CAPABILITY`` 的固定文案（与源文档逐字一致）
UNSUPPORTED_CAPABILITY_MESSAGE = "当前没有支持该类别的厂商"


def _as_capability(capability: Capability | str) -> Capability:
    """把能力标签参数归一化为 :class:`Capability`。"""
    if isinstance(capability, Capability):
        return capability
    try:
        return Capability(str(capability).strip().lower())
    except ValueError as exc:
        raise ByokError(ErrorCode.UNSUPPORTED_CAPABILITY, param=str(capability)) from exc


def _as_tier(tier: Tier | str) -> Tier:
    """把档位参数归一化为 :class:`Tier`。"""
    if isinstance(tier, Tier):
        return tier
    try:
        return Tier(str(tier).strip().lower())
    except ValueError as exc:
        raise ConfigError(f"未知厂商档位 {tier!r}") from exc


def _read_catalog(path: Path) -> Catalog:
    """读取目录 JSON 并反序列化；文件缺失或格式错误直接抛配置错误。"""
    target = Path(path)
    if not target.exists():
        raise ConfigError(f"目录文件不存在：{target}")
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"目录文件 {target} 解析失败：{exc}") from exc
    return Catalog.model_validate(raw)


class CatalogService:
    """厂商目录服务：进程内持有一份不可变 :class:`Catalog` 快照。"""

    def __init__(self, settings: Settings, catalog: Catalog) -> None:
        self._settings = settings
        self._catalog = catalog

    @classmethod
    def load(cls, settings: Settings) -> CatalogService:
        """按 ``settings.catalog_path`` 载入目录（对应进程启动时读盘）。"""
        return cls(settings, _read_catalog(Path(settings.catalog_path)))

    @property
    def settings(self) -> Settings:
        return self._settings

    @property
    def catalog(self) -> Catalog:
        """当前目录快照。"""
        return self._catalog

    def snapshot(self) -> Catalog:
        """返回目录快照（供 ``/api/catalog`` 直接下发）。"""
        return self._catalog

    def reload(self) -> Catalog:
        """重新读盘并替换快照；对应「目录更新需重启代理」的人工触发路径。"""
        self._catalog = _read_catalog(Path(self._settings.catalog_path))
        return self._catalog

    # ---------------------------------------------------------------- 厂商

    def list_providers(
        self,
        *,
        tier: Tier | str | None = None,
        include_hidden: bool | None = None,
    ) -> tuple[Provider, ...]:
        """列出厂商。

        ``include_hidden`` 为 ``None`` 时取 ``hide_hidden_providers`` 的反面，即默认
        保留隐藏厂商（与原产品「隐藏厂商仍随公开接口下发」的行为一致，等价于 ``?all=1``）。
        """
        if include_hidden is None:
            include_hidden = not self._settings.hide_hidden_providers
        wanted = None if tier is None else _as_tier(tier)
        return tuple(
            provider
            for provider in self._catalog.providers
            if (wanted is None or provider.tier is wanted)
            and (include_hidden or not provider.is_hidden)
        )

    def provider(self, provider_id: str) -> Provider | None:
        """按 id 取厂商；不存在返回 ``None``。"""
        return self._catalog.provider(provider_id)

    # ---------------------------------------------------------------- 模型

    def list_models(
        self,
        *,
        capability: Capability | str | None = None,
        provider_id: str | None = None,
        free: bool | None = None,
    ) -> tuple[ModelEntry, ...]:
        """按能力 / 厂商 / 免费档过滤模型；三条件同时满足才保留。"""
        wanted = None if capability is None else _as_capability(capability)
        return tuple(
            entry
            for entry in self._catalog.models
            if (wanted is None or entry.has(wanted))
            and (provider_id is None or entry.provider_id == provider_id)
            and (free is None or entry.free is free)
        )

    def models_of(self, provider_id: str) -> tuple[ModelEntry, ...]:
        """取某厂商旗下的全部模型。"""
        return self._catalog.models_of(provider_id)

    def by_capability(self, capability: Capability | str) -> tuple[ModelEntry, ...]:
        """按能力标签取可路由模型；无任何命中时抛 ``UNSUPPORTED_CAPABILITY``。"""
        wanted = _as_capability(capability)
        matched = self._catalog.with_capability(wanted)
        if not matched:
            raise ByokError(
                ErrorCode.UNSUPPORTED_CAPABILITY,
                UNSUPPORTED_CAPABILITY_MESSAGE,
                param=wanted.value,
            )
        return matched

    def resolve_model(self, model_or_alias: str) -> ModelEntry | None:
        """解析模型：真实 id 精确匹配（大小写敏感），逻辑别名返回 ``None``。"""
        if not model_or_alias:
            return None
        return self._catalog.model(model_or_alias)

    def routable_models(
        self,
        provider_ids: Iterable[str],
        capability: Capability | str | None = None,
    ) -> tuple[ModelEntry, ...]:
        """限定在用户已录入 Key 的厂商集合内，返回可路由模型。"""
        allowed = frozenset(provider_ids)
        wanted = None if capability is None else _as_capability(capability)
        return tuple(
            entry
            for entry in self._catalog.models
            if entry.provider_id in allowed and (wanted is None or entry.has(wanted))
        )

    # ---------------------------------------------------------------- 统计

    @property
    def free_count(self) -> int:
        """免费厂商数量（全部厂商口径，不受 ``hide_hidden_providers`` 影响）。"""
        return self._catalog.free_count

    @property
    def paid_count(self) -> int:
        return self._catalog.paid_count

    @property
    def hidden_count(self) -> int:
        return self._catalog.hidden_count
