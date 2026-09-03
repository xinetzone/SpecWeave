from __future__ import annotations

import os
from typing import Any

from ._utils import deep_merge

DEFAULT_MYST_CONFIG: dict[str, Any] = {
    "myst_enable_extensions": [
        "dollarmath",
        "amsmath",
        "deflist",
        "colon_fence",
        "replacements",
        "substitution",
    ],
    "myst_fence_as_directive": ["mermaid"],
    "myst_heading_anchors": 3,
    "myst_commonmark_only": False,
    "myst_title_to_header": True,
}

DEFAULT_BUILD_CONFIG: dict[str, Any] = {
    "templates_path": ["_templates"],
    "exclude_patterns": [
        "_build",
        "Thumbs.db",
        ".DS_Store",
        "**.ipynb_checkpoints",
        "**/.spec/**",
        "**/.spec",
    ],
    "numfig": True,
    "nitpicky": False,
    "suppress_warnings": [
        "myst.xref_missing",
        "myst.domains",
        "ref.ref",
        "toc.external",
        "etoc.toctree",
        "ref.footnote",
        "misc.highlighting_failure",
        "tippy.rtd",
        "tippy.wiki",
        "tippy.doi",
    ],
}

DEFAULT_EXT_CONFIG: dict[str, Any] = {
    "copybutton_exclude": ".linenos, .gp",
    "copybutton_selector": ":not(.prompt) > div.highlight pre",
    "mermaid_version": "11.4.1",
    "mermaid_init_js": """
mermaid.initialize({
  startOnLoad: true,
  theme: 'default',
  securityLevel: 'loose',
  fontFamily: '"Noto Sans SC", "Microsoft YaHei", sans-serif',
});
""".strip(),
    "tippy_enable_wikitips": False,
    "tippy_enable_doitips": False,
    "tippy_rtd_urls": [],
    "tippy_skip_urls": [
        "https://*.readthedocs.io/*",
        "https://www.readthedocs.org/",
        "https://en.wikipedia.org/wiki/",
        "https://doi.org/",
    ],
    "sitemap_url_scheme": "{link}",
    "sitemap_locales": [None],
    "ogp_social_cards": {"enable": False},
    "extlinks": {},
}

DEFAULT_HTML_CONFIG: dict[str, Any] = {
    "html_static_path": ["_static"],
    "html_css_files": ["local.css"],
    "html_last_updated_fmt": "%Y-%m-%d, %H:%M:%S",
}


def _resolve_html_baseurl(params: dict) -> str | None:
    """从环境变量 / 项目参数中推断 ``html_baseurl``（sitemap + ogp 需要）。"""
    if os.environ.get("GITHUB_ACTIONS"):
        return os.environ.get("SITEMAP_URL_BASE", params.get("site_url"))
    if not os.environ.get("READTHEDOCS"):
        return params.get("site_url") or "http://127.0.0.1:8000/"
    return None


def build_base_config(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """基于默认字典 + 项目覆盖，组装出 Sphinx 所需的核心配置。

    不包含 extensions / html_theme / hooks（这些在各自模块中处理）。
    """
    params = params or {}
    merged: dict[str, Any] = {}
    merged.update(DEFAULT_BUILD_CONFIG)
    merged.update(DEFAULT_MYST_CONFIG)
    merged.update(DEFAULT_EXT_CONFIG)
    merged.update(DEFAULT_HTML_CONFIG)

    baseurl = _resolve_html_baseurl(params)
    if baseurl is not None:
        merged["html_baseurl"] = baseurl
    if "site_url" in params:
        merged["ogp_site_url"] = params["site_url"]
    if "intersphinx_mapping" in params:
        merged["intersphinx_mapping"] = params["intersphinx_mapping"]

    return deep_merge(merged, params.get("config_override") or {})
