"""代码块高亮主题（highlight.js 预设 CDN 白名单与抓取）。

upstream: packages/mcp-server/src/config-options.ts:105-136
          packages/mcp-server/src/render-article.ts:65-94、176-178
"""

from typing import Any

import httpx

from .css import escape_style_content

# upstream: config-options.ts:105
CODE_BLOCK_URL_PREFIX = (
    "https://cdn-doocs.oss-cn-shenzhen.aliyuncs.com/npm/"
    "highlightjs/11.11.1/styles/"
)

# upstream: config-options.ts:107-118
CODE_BLOCK_THEME_NAMES = (
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

# upstream: config-options.ts:120-124
CODE_BLOCK_THEME_OPTIONS = tuple(
    {"label": name, "value": f"{CODE_BLOCK_URL_PREFIX}{name}.min.css", "desc": ""}
    for name in CODE_BLOCK_THEME_NAMES
)

# upstream: config-options.ts:126-128
ALLOWED_CODE_BLOCK_THEME_URLS = frozenset(
    option["value"] for option in CODE_BLOCK_THEME_OPTIONS
)

# upstream: render-article.ts:15
CODE_BLOCK_FETCH_TIMEOUT_MS = 10_000

# upstream: render-article.ts:65（模块级内存缓存）
_hljs_css_cache: dict[str, str] = {}
_default_client: httpx.Client | None = None


def assert_allowed_code_block_theme_url(url: str) -> None:
    """upstream: config-options.ts:130-136。"""
    if url not in ALLOWED_CODE_BLOCK_THEME_URLS:
        raise ValueError(
            "codeBlockTheme must be a preset URL from list_code_block_themes. "
            f"Received: {url}"
        )


def fetch_code_block_css(url: str, *, client: httpx.Client | None = None) -> str:
    """upstream: render-article.ts:67-94（同步等价实现）。

    成功抓取的 CSS 经 escapeStyleContent 后按 URL 缓存；
    httpx 超时错误转换为与上游一致的 10s 超时文案。
    """
    assert_allowed_code_block_theme_url(url)

    cached = _hljs_css_cache.get(url)
    if cached:
        return cached

    global _default_client
    if client is None:
        # 模块级默认 client 跨调用复用（同上游模块级 fetch 环境）
        if _default_client is None:
            _default_client = httpx.Client(timeout=CODE_BLOCK_FETCH_TIMEOUT_MS / 1000)
        client = _default_client

    try:
        response = client.get(url)
    except httpx.TimeoutException as err:
        raise TimeoutError(
            "Timed out fetching code block theme CSS after "
            f"{CODE_BLOCK_FETCH_TIMEOUT_MS}ms: {url}"
        ) from err
    if response.status_code != 200:
        raise RuntimeError(
            "Failed to fetch code block theme CSS "
            f"({response.status_code}): {url}"
        )
    css = escape_style_content(response.text)
    _hljs_css_cache[url] = css
    return css


def clear_hljs_css_cache() -> None:
    """upstream: render-article.ts:176-178。"""
    _hljs_css_cache.clear()


def _reset_default_client() -> None:
    """测试辅助：关闭并重置模块级默认 client。"""
    global _default_client
    if _default_client is not None:
        _default_client.close()
        _default_client = None


def list_code_block_themes() -> tuple[dict[str, Any], ...]:
    """MCP list_code_block_themes 工具的静态选项列表。"""
    return CODE_BLOCK_THEME_OPTIONS
