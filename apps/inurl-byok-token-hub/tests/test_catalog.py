"""厂商目录种子数据与目录服务测试。

断言口径（源文档 F-077/F-082/F-090/F-091）：46 家厂商 = 17 free + 29 paid、10 家
``public: false`` 隐藏厂商、133 个模型；能力标签仅 text/code/image，video/audio 无
可路由模型。
"""

from pathlib import Path

import pytest

from inurl_byok_token_hub.config import Settings
from inurl_byok_token_hub.errors import ByokError, ErrorCode
from inurl_byok_token_hub.models.catalog import Capability, Tier
from inurl_byok_token_hub.services.catalog_service import CatalogService

CATALOG_PATH = Path(__file__).resolve().parents[1] / "data" / "catalog.json"

UNSUPPORTED_TEXT = "当前没有支持该类别的厂商"


@pytest.fixture(scope="module")
def settings() -> Settings:
    """默认配置（``hide_hidden_providers=False``）+ 仓库内的种子目录。"""
    return Settings(catalog_path=CATALOG_PATH)


@pytest.fixture(scope="module")
def service(settings: Settings) -> CatalogService:
    return CatalogService.load(settings)


def _dump(providers) -> list[dict]:
    return [provider.model_dump(mode="json") for provider in providers]


def test_catalog_counts(service: CatalogService) -> None:
    """46 家厂商 = 17 free + 29 paid，10 家隐藏，133 个模型。"""
    catalog = service.catalog
    assert len(catalog.providers) == 46
    assert catalog.free_count == 17
    assert catalog.paid_count == 29
    assert catalog.hidden_count == 10
    assert len(catalog.models) == 133
    assert len(service.list_providers(tier=Tier.FREE)) == 17
    assert len(service.list_providers(tier=Tier.PAID)) == 29


def test_hidden_providers_are_paid(service: CatalogService) -> None:
    """隐藏厂商全部落在付费区（原产品付费区 10 家不下发到 /models）。"""
    hidden = [p for p in service.catalog.providers if p.is_hidden]
    assert len(hidden) == 10
    assert all(p.tier is Tier.PAID for p in hidden)


def test_all_one_is_default_behaviour(settings: Settings, service: CatalogService) -> None:
    """``?all=1`` 语义：默认结果等价于 ``include_hidden=True``。"""
    assert _dump(service.list_providers()) == _dump(service.list_providers(include_hidden=True))
    assert len(service.list_providers()) == 46

    strict = Settings(catalog_path=CATALOG_PATH, hide_hidden_providers=True)
    strict_service = CatalogService.load(strict)
    visible = strict_service.list_providers()
    assert len(visible) == 36
    assert all(not p.is_hidden for p in visible)
    assert len(strict_service.list_providers(include_hidden=True)) == 46


def test_unsupported_capabilities_raise(service: CatalogService) -> None:
    """video / audio 没有任何可路由模型，抛 ``UNSUPPORTED_CAPABILITY``。"""
    for capability in (Capability.VIDEO, Capability.AUDIO):
        with pytest.raises(ByokError) as excinfo:
            service.by_capability(capability)
        assert excinfo.value.error_code is ErrorCode.UNSUPPORTED_CAPABILITY
        assert UNSUPPORTED_TEXT in excinfo.value.message
    assert service.list_models(capability=Capability.VIDEO) == ()
    assert service.list_models(capability=Capability.AUDIO) == ()


@pytest.mark.parametrize(
    ("capability", "expected"),
    [(Capability.TEXT, 12), (Capability.CODE, 5), (Capability.IMAGE, 7)],
)
def test_capability_counts(
    service: CatalogService, capability: Capability, expected: int
) -> None:
    """text 12 / code 5 / image 7 个模型带能力标签。"""
    matched = service.by_capability(capability)
    assert len(matched) == expected
    assert matched
    assert all(entry.has(capability) for entry in matched)


def test_no_video_or_audio_models(service: CatalogService) -> None:
    for entry in service.catalog.models:
        assert not entry.has(Capability.VIDEO)
        assert not entry.has(Capability.AUDIO)


def test_paid_models_are_behind_flagship(service: CatalogService) -> None:
    """付费卡一律带「落后当期旗舰 ≥1 大版本」标记（G5）。"""
    paid = [entry for entry in service.catalog.models if not entry.free]
    assert paid
    assert all(entry.behind_flagship for entry in paid)
    assert all(entry.behind_flagship for entry in service.list_models(free=False))


def test_deepseek_is_paid(service: CatalogService) -> None:
    """文档勘误 E2：DeepSeek 官方 API 收费，属于付费区。"""
    provider = service.provider("deepseek")
    assert provider is not None
    assert provider.tier is Tier.PAID
    assert provider.base_url == "https://api.deepseek.com/v1"


def test_agnes_free_context_is_512k(service: CatalogService) -> None:
    """Agnes 免费档为 512K 上下文（文档勘误：不是 1M）。"""
    entry = service.resolve_model("agnes-2.5-flash")
    assert entry is not None
    assert entry.free
    assert entry.context_window == 524288
    assert [m.context_window for m in service.catalog.models_of("agnes") if m.free] == [524288]


def test_named_providers_recorded_with_doc_source(service: CatalogService) -> None:
    """具名厂商如实录入且标注 ``metadata_source="doc"``。"""
    named = ("zhipu", "longcat", "agnes", "siliconflow", "groq", "qianfan", "openrouter", "deepseek")
    for provider_id in named:
        provider = service.provider(provider_id)
        assert provider is not None, provider_id
        assert provider.metadata_source == "doc"
    assert service.provider("zhipu").base_url == "https://open.bigmodel.cn/api/paas/v4"
    assert service.provider("longcat").base_url == "https://api.longcat.chat/openai"
    assert service.provider("agnes").base_url == "https://apihub.agnes-ai.com/v1"
    assert service.provider("siliconflow").base_url == "https://api.siliconflow.cn/v1"


def test_resolve_model(service: CatalogService) -> None:
    """真实 id 精确命中且大小写敏感；逻辑别名返回 ``None``。"""
    entry = service.resolve_model("glm-4-flash")
    assert entry is not None
    assert entry.provider_id == "zhipu"
    assert service.resolve_model("seed-free-01-a") is not None
    for alias in ("inurl", "inurl-text", "inurl-code", "inurl-image", "inurl-video", "auto"):
        assert service.resolve_model(alias) is None
    assert service.resolve_model("GLM-4-FLASH") is None
    assert service.resolve_model("") is None


def test_list_models_filters(service: CatalogService) -> None:
    free_models = service.list_models(free=True)
    provider_models = service.list_models(provider_id="groq")
    assert free_models
    assert all(entry.free for entry in free_models)
    assert len(provider_models) == len(service.catalog.models_of("groq"))
    assert all(entry.provider_id == "groq" for entry in provider_models)
    assert service.list_models(provider_id="groq", capability=Capability.TEXT)


def test_routable_models(service: CatalogService) -> None:
    """可路由池限定在用户已录入 Key 的厂商集合内。"""
    scoped = service.routable_models(["zhipu", "groq"])
    assert scoped
    assert {entry.provider_id for entry in scoped} == {"zhipu", "groq"}
    assert service.routable_models(["zhipu"], capability=Capability.TEXT)
    assert service.routable_models(["zhipu"], capability=Capability.IMAGE) == ()
    assert service.routable_models([]) == ()


def test_snapshot_and_reload(settings: Settings, service: CatalogService) -> None:
    """快照为同一份不可变对象；``reload()`` 重新读盘后计数不变。"""
    assert service.snapshot() is service.catalog
    reloaded = service.reload()
    assert len(reloaded.providers) == 46
    assert len(reloaded.models) == 133
    assert service.snapshot() is reloaded
