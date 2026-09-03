"""Sphinx 配置核心——直接从 mystx.configs 取 4 个基础字典，再 D3 增量叠加。

A2 公理：增量叠加不覆盖。4 个 DEFAULT_* 字典的结构/键由 mystx 定义；
sphinx_config 的 tippy / mermaid / ogp / suppress_warnings 增量通过
``deep_merge`` 叠加到基础值之上，不重定义整个字典。
"""

from __future__ import annotations

from typing import Any

from ._utils import deep_merge, ensure_mystx_on_syspath

ensure_mystx_on_syspath(__file__)

from mystx.configs import (  # noqa: E402
    DEFAULT_BUILD_CONFIG as _MYSTX_BUILD,
    DEFAULT_EXT_CONFIG as _MYSTX_EXT,
    DEFAULT_HTML_CONFIG as _MYSTX_HTML,
    DEFAULT_MYST_CONFIG as _MYSTX_MYST,
)

# —— D3 维度：SpecWeave 独有的扩展/构建配置增量 —— #

_EXT_INCREMENT: dict[str, Any] = {
    "mermaid_version": "11.4.1",
    "mermaid_init_js": (
        "mermaid.initialize({\n"
        "  startOnLoad: true,\n"
        "  theme: 'default',\n"
        "  securityLevel: 'loose',\n"
        "  fontFamily: '\"Noto Sans SC\", \"Microsoft YaHei\", sans-serif',\n"
        "});"
    ),
    "tippy_enable_wikitips": False,
    "tippy_enable_doitips": False,
    "tippy_rtd_urls": [],
    "sitemap_locales": [None],
    "tippy_skip_urls": [
        "https://*.readthedocs.io/*",
        "https://www.readthedocs.org/",
        "https://en.wikipedia.org/wiki/",
        "https://doi.org/",
    ],
    "ogp_social_cards": {"enable": False},
}

_BUILD_INCREMENT: dict[str, Any] = {
    "suppress_warnings": ["tippy.rtd", "tippy.wiki", "tippy.doi"],
}

DEFAULT_MYST_CONFIG: dict[str, Any] = dict(_MYSTX_MYST)
DEFAULT_EXT_CONFIG: dict[str, Any] = deep_merge(dict(_MYSTX_EXT), _EXT_INCREMENT)
DEFAULT_BUILD_CONFIG: dict[str, Any] = deep_merge(dict(_MYSTX_BUILD), _BUILD_INCREMENT)
DEFAULT_HTML_CONFIG: dict[str, Any] = dict(_MYSTX_HTML)


def build_base_config(override: dict[str, Any] | None = None) -> dict[str, Any]:
    """生成 Sphinx 基础 conf——合并 4 个 DEFAULT_* + override 再注入 intersphinx / ogp。

    保持 sphinx_config 原有的三个注入约定：
    1. ``override['intersphinx_mapping']`` → 直接加入最终 conf（D2 维度 OKF 预设需要）
    2. ``override['site_url']`` → 映射到 Sphinx ext: ogp 的 ``ogp_site_url``
    3. 合并完成后再 ``deep_merge(override, remove_marker=None)`` 允许显式删除默认键
    """
    override = override or {}
    cfg: dict[str, Any] = deep_merge(
        DEFAULT_BUILD_CONFIG,
        DEFAULT_MYST_CONFIG,
        DEFAULT_EXT_CONFIG,
        DEFAULT_HTML_CONFIG,
    )
    if "intersphinx_mapping" in override:
        cfg["intersphinx_mapping"] = override["intersphinx_mapping"]
    if "site_url" in override:
        cfg["ogp_site_url"] = override["site_url"]
        cfg["html_baseurl"] = override["site_url"]
    return deep_merge(cfg, override)


__all__: tuple[str, ...] = (
    "DEFAULT_MYST_CONFIG",
    "DEFAULT_EXT_CONFIG",
    "DEFAULT_BUILD_CONFIG",
    "DEFAULT_HTML_CONFIG",
    "build_base_config",
)
