"""表装配：把 :class:`Repository` 的 JSON 表映射为具体模型类型。"""

from pathlib import Path

from ..models import (
    AdItem,
    AdminConfig,
    AuditEvent,
    BillingEvent,
    EscrowRecord,
    NewsItem,
    PaymentOrder,
    RecoveryRecord,
    TokenRecord,
    UsageRecord,
    User,
    UserSettings,
    VaultKeyRecord,
)
from ..models.catalog import Capability, ModelEntry, Provider, ProviderProtocol, Tier
from ..models.catalog import Catalog as CatalogModel
from .repository import Repository, Table


def _provider(data: dict) -> Provider:
    data = dict(data)
    data["capabilities"] = frozenset(Capability(c) for c in data.get("capabilities", []))
    return Provider.model_validate(data)


def _model_entry(data: dict) -> ModelEntry:
    data = dict(data)
    data["capabilities"] = frozenset(Capability(c) for c in data.get("capabilities", []))
    return ModelEntry.model_validate(data)


class Store:
    """所有持久化表的聚合入口。"""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = Path(data_dir)
        self.repo = Repository(self.data_dir)
        self.users: Table[User] = self.repo.table("users", User.model_validate)
        self.tokens: Table[TokenRecord] = self.repo.table("tokens", TokenRecord.model_validate)
        self.recovery: Table[RecoveryRecord] = self.repo.table(
            "recovery", RecoveryRecord.model_validate
        )
        self.escrow: Table[EscrowRecord] = self.repo.table("escrow", EscrowRecord.model_validate)
        self.keys: Table[VaultKeyRecord] = self.repo.table("keys", VaultKeyRecord.model_validate)
        self.settings: Table[UserSettings] = self.repo.table(
            "settings", UserSettings.model_validate
        )
        self.usage: Table[UsageRecord] = self.repo.table("usage", UsageRecord.model_validate)
        self.billing: Table[BillingEvent] = self.repo.table(
            "billing", BillingEvent.model_validate
        )
        self.orders: Table[PaymentOrder] = self.repo.table("orders", PaymentOrder.model_validate)
        self.ads: Table[AdItem] = self.repo.table("ads", AdItem.model_validate)
        self.news: Table[NewsItem] = self.repo.table("news", NewsItem.model_validate)
        self.audit: Table[AuditEvent] = self.repo.table("audit", AuditEvent.model_validate)
        self.admin_config: Table[AdminConfig] = self.repo.table(
            "admin_config", AdminConfig.model_validate
        )
        self.custom_providers: Table[Provider] = self.repo.table(
            "custom_providers", _provider
        )
        self.custom_models: Table[ModelEntry] = self.repo.table("custom_models", _model_entry)

    def ensure_admin_config(self) -> AdminConfig:
        rows = self.admin_config.all()
        if rows:
            return rows[0]
        config = AdminConfig()
        self.admin_config.add(config)
        return config

    def set_admin_config(self, config: AdminConfig) -> AdminConfig:
        self.admin_config.clear()
        self.admin_config.add(config)
        return config

    def raw_text(self) -> str:
        """把所有表拼成一段文本，供「落盘不含明文」的审计断言使用。"""
        return self.repo.raw_text()

    def custom_catalog(self) -> tuple[CatalogModel, ...]:
        """用户自定义厂商构成的增量目录（并入主目录使用）。"""
        return (
            CatalogModel(
                providers=tuple(self.custom_providers.all()),
                models=tuple(self.custom_models.all()),
            ),
        )


__all__ = [
    "Store",
    "_model_entry",
    "_provider",
    "CatalogModel",
    "ProviderProtocol",
    "Tier",
]
