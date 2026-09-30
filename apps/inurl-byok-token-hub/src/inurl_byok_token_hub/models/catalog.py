"""目录相关模型：厂商、模型条目、能力标签与协议类型。

事实口径（源自源文档 ``references/article-source.md`` F-077/F-082/F-090/F-091）：
46 家厂商 = 17 free + 29 paid（其中 10 家 ``public:false``）、133 个模型；
capabilities 仅有 text/code/image 三类，**video/audio 无任何可路由厂商**。
"""

import enum

from pydantic import BaseModel, ConfigDict, Field


class Capability(enum.StrEnum):
    """能力标签。"""

    TEXT = "text"
    CODE = "code"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


class ProviderProtocol(enum.StrEnum):
    """自定义厂商支持的三种协议。"""

    OPENAI_COMPAT = "openai_compat"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"


class Tier(enum.StrEnum):
    FREE = "free"
    PAID = "paid"


class ModelEntry(BaseModel):
    """模型条目。"""

    model_config = ConfigDict(frozen=True)

    id: str
    name: str = ""
    provider_id: str
    capabilities: frozenset[Capability] = Field(default_factory=frozenset)
    context_window: int | None = None
    free: bool = False
    rate_limit_note: str = ""
    #: 付费卡「落后当期旗舰 ≥1 大版本」的时效标记（G5 复核结论）
    behind_flagship: bool = False
    metadata_source: str = "seed"

    def has(self, capability: Capability) -> bool:
        return capability in self.capabilities


class Provider(BaseModel):
    """厂商条目。"""

    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    protocol: ProviderProtocol = ProviderProtocol.OPENAI_COMPAT
    base_url: str = ""
    tier: Tier = Tier.FREE
    public: bool = True
    capabilities: frozenset[Capability] = Field(default_factory=frozenset)
    models: tuple[str, ...] = ()
    website: str = ""
    #: 是否为用户自定义厂商
    custom: bool = False
    metadata_source: str = "seed"

    @property
    def is_hidden(self) -> bool:
        return not self.public


class Catalog(BaseModel):
    """厂商目录快照。"""

    model_config = ConfigDict(frozen=True)

    providers: tuple[Provider, ...] = ()
    models: tuple[ModelEntry, ...] = ()

    def provider(self, provider_id: str) -> Provider | None:
        for provider in self.providers:
            if provider.id == provider_id:
                return provider
        return None

    def model(self, model_id: str) -> ModelEntry | None:
        for entry in self.models:
            if entry.id == model_id:
                return entry
        return None

    def models_of(self, provider_id: str) -> tuple[ModelEntry, ...]:
        return tuple(m for m in self.models if m.provider_id == provider_id)

    def with_capability(self, capability: Capability) -> tuple[ModelEntry, ...]:
        return tuple(m for m in self.models if m.has(capability))

    @property
    def free_count(self) -> int:
        return sum(1 for p in self.providers if p.tier is Tier.FREE)

    @property
    def paid_count(self) -> int:
        return sum(1 for p in self.providers if p.tier is Tier.PAID)

    @property
    def hidden_count(self) -> int:
        return sum(1 for p in self.providers if p.is_hidden)
