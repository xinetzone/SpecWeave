"""OKF（开源知识格式）文档项目预设——D2 维度 sphinx_config 独有增量叠加。

A3 公理：差异包裹，不嵌入。在 :mod:`mystx.presets.minimal_myst` 的
基础之上，通过 :func:`deep_merge` 叠加以下 OKF 专属逻辑：
    1. ``_detect_release``：从 PyPI importlib.metadata 自动取版本
    2. ``_DEFAULT_INTERSPHINX``：Python/Sphinx/MyST 三个交叉引用默认值
    3. GitHub URL → site_url 自动推断
    4. ``_OKF_KEY_DEFAULTS``：中文默认 language/默认 project 名
    5. book_overrides：repository_url/path_to_docs 注入 book theme options + extlinks
"""

import importlib.metadata
from typing import Any

from ._shared import build_project_meta, build_setup_closure
from .._utils import deep_merge, ensure_mystx_on_syspath
from ..core import build_base_config
from ..extensions import (
    DEFAULT_CONDITIONAL,
    DEFAULT_OPTIONAL_EXTENSIONS,
    resolve_extensions,
)
from ..myst_compat import register_hooks
from ..themes import resolve_theme, resolve_theme_options

ensure_mystx_on_syspath(__file__)

from mystx.presets.minimal_myst import build_config as _base_minimal_build_config  # noqa: E402

_DEFAULT_INTERSPHINX: dict[str, tuple[str, None]] = {
    "python": ("https://docs.python.org/3.14", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master", None),
    "myst-parser": ("https://myst-parser.readthedocs.io/en/latest", None),
}

_OKF_KEY_DEFAULTS: dict[str, Any] = {
    "project": "Untitled OKF Project",
    "author": "Unknown Author",
    "language": "zh_CN",
}


def _detect_release(package_name: str | None, fallback: str = "0.1.0") -> str:
    """从已安装的包元数据中读取版本号，未安装则回退 fallback。"""
    if not package_name:
        return fallback
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return fallback


def build_config(override: dict[str, Any] | None = None) -> dict[str, Any]:
    """OKF 文档项目预设——还原 awesome-okf-xs 的全量配置。

    典型用法（任意项目 ``doc/conf.py`` 只需 5-8 行）::

        from specweave_lib.sphinx_config.presets.okf_docs import build_config

        globals().update(build_config({
            "project": "my-project",
            "author": "my-org",
            "package_name": "my-project",
            "language": "zh_CN",
            "html_title": "My Project Docs",
            "repository_url": "https://github.com/my-org/my-project",
            "site_url": "https://my-org.github.io/my-project/",
            "path_to_docs": "doc",
            "intersphinx_mapping": {"mylib": ("https://...", None)},
        }))

    ``override`` 支持的完整键：

    * 元信息：``project`` ``author`` ``package_name`` ``release`` ``version`` ``language``
    * 展示：``html_title`` ``html_theme`` ``html_theme_options``
    * 仓库链接：``repository_url`` ``repository_branch`` ``path_to_docs`` ``site_url``
    * 扩展：``extensions_required`` ``extensions_optional`` ``intersphinx_mapping`` ``extlinks``
    * 兜底：``config_override`` 其余任意 Sphinx 配置字典，最深合并
    """
    override = override or {}
    params = dict(override)

    release = params.get("release") or _detect_release(
        params.get("package_name"), params.get("version", "0.1.0")
    )
    params["release"] = release
    params.setdefault("version", release)

    extensions = resolve_extensions(
        required=params.get("extensions_required", ("myst_parser",)),
        optional=params.get("extensions_optional", DEFAULT_OPTIONAL_EXTENSIONS),
        conditional=params.get("extensions_conditional", DEFAULT_CONDITIONAL),
    )

    theme = params.get("html_theme") or resolve_theme()
    book_overrides: dict[str, Any] = {}
    if params.get("repository_url"):
        book_overrides["repository_url"] = params["repository_url"]
    if params.get("repository_branch"):
        book_overrides["repository_branch"] = params["repository_branch"]
    if params.get("path_to_docs"):
        book_overrides["path_to_docs"] = params["path_to_docs"]
    book_overrides.update(params.get("html_theme_options") or {})
    theme_options = resolve_theme_options(theme, book_overrides)

    intersphinx = dict(_DEFAULT_INTERSPHINX)
    if params.get("intersphinx_mapping"):
        intersphinx.update(params["intersphinx_mapping"])
    params["intersphinx_mapping"] = intersphinx

    if not params.get("site_url") and params.get("repository_url"):
        repo = params["repository_url"].rstrip("/")
        if "github.com" in repo:
            parts = repo.rstrip("/").split("/")
            if len(parts) >= 2:
                name = parts[-1].removesuffix(".git")
                org = parts[-2]
                params["site_url"] = f"https://{org}.github.io/{name}/"

    params["html_theme"] = theme
    params["html_theme_options"] = theme_options
    params["extensions"] = extensions
    params["html_title"] = params.get(
        "html_title", params.get("project", "Untitled OKF Project")
    )

    base = build_base_config(params)
    if params.get("extlinks"):
        base["extlinks"] = dict(params["extlinks"])

    project_meta = build_project_meta(params, _OKF_KEY_DEFAULTS)
    project_meta["extensions"] = extensions
    project_meta["html_theme"] = theme
    project_meta["html_theme_options"] = theme_options
    merged = deep_merge(base, project_meta)

    merged["setup"] = build_setup_closure(
        register_fns=[register_hooks],
        user_setup=params.get("setup"),
    )
    return merged


__all__ = ["build_config"]
