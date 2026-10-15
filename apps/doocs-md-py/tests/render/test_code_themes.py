"""render/code_themes.py 测试（upstream: config-options.ts/render-article.ts）。"""

import httpx
import pytest

from doocs_md_py.render import code_themes

PREFIX = (
    "https://cdn-doocs.oss-cn-shenzhen.aliyuncs.com/npm/"
    "highlightjs/11.11.1/styles/"
)
EXPECTED_NAMES = (
    "github",
    "github-dark",
    "atom-one-light",
    "atom-one-dark",
    "monokai",
    "vs",
    "xcode",
    "nord",
    "tokyo-night-light",
    "tokyo-night-dark",
)


@pytest.fixture(autouse=True)
def _reset_cache():
    code_themes.clear_hljs_css_cache()
    yield
    code_themes.clear_hljs_css_cache()


def test_ten_preset_urls():
    assert len(code_themes.ALLOWED_CODE_BLOCK_THEME_URLS) == 10
    for name in EXPECTED_NAMES:
        assert f"{PREFIX}{name}.min.css" in code_themes.ALLOWED_CODE_BLOCK_THEME_URLS


def test_options_shape():
    options = code_themes.list_code_block_themes()
    assert len(options) == 10
    assert options[0] == {"label": "github", "value": f"{PREFIX}github.min.css", "desc": ""}
    for option in options:
        assert set(option) == {"label", "value", "desc"}


def test_assert_allowed_accepts_preset():
    code_themes.assert_allowed_code_block_theme_url(f"{PREFIX}nord.min.css")


def test_assert_allowed_rejects_arbitrary_url():
    with pytest.raises(ValueError, match="codeBlockTheme must be a preset URL"):
        code_themes.assert_allowed_code_block_theme_url("https://example.com/evil.css")


def test_fetch_success_escapes_and_caches():
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, text=".hljs{color:red}\n</style escape>")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    url = f"{PREFIX}github.min.css"

    first = code_themes.fetch_code_block_css(url, client=client)
    second = code_themes.fetch_code_block_css(url, client=client)

    assert first == second == ".hljs{color:red}\n<\\/style escape>"
    assert calls == 1  # 第二次命中缓存，未发起请求


def test_fetch_non_200_raises_with_status():
    client = httpx.Client(
        transport=httpx.MockTransport(lambda r: httpx.Response(404, text="nope"))
    )
    url = f"{PREFIX}vs.min.css"
    with pytest.raises(RuntimeError, match=r"Failed to fetch code block theme CSS \(404\)"):
        code_themes.fetch_code_block_css(url, client=client)


def test_fetch_timeout_translated():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("simulated")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    url = f"{PREFIX}xcode.min.css"
    with pytest.raises(TimeoutError, match="Timed out fetching code block theme CSS after 10000ms"):
        code_themes.fetch_code_block_css(url, client=client)


def test_fetch_rejects_non_whitelist_before_request():
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("must not perform request")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    with pytest.raises(ValueError, match="codeBlockTheme must be a preset URL"):
        code_themes.fetch_code_block_css("https://evil.example/x.css", client=client)


def test_clear_cache_forces_refetch():
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(200, text=f"/*v{calls}*/")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    url = f"{PREFIX}monokai.min.css"

    assert code_themes.fetch_code_block_css(url, client=client) == "/*v1*/"
    assert code_themes.fetch_code_block_css(url, client=client) == "/*v1*/"
    code_themes.clear_hljs_css_cache()
    assert code_themes.fetch_code_block_css(url, client=client) == "/*v2*/"
    assert calls == 2
