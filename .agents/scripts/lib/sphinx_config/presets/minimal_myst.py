from typing import Any

from .._utils import deep_merge
from ..core import build_base_config
from ..extensions import resolve_extensions
from ..myst_compat import register_hooks
from ..themes import resolve_theme, resolve_theme_options
from ._shared import build_project_meta, build_setup_closure

_MINIMAL_KEY_DEFAULTS: dict[str, Any] = {
    "project": "Untitled Project",
    "author": "Unknown Author",
    "release": "0.1.0",
    "version": "0.1.0",
    "language": "en",
}


def build_config(override: dict[str, Any] | None = None) -> dict[str, Any]:
    """极简 MyST 预设：仅保留 ``myst_parser`` + 两个兼容性钩子。

    适用于轻量个人笔记、小型文档站点，不引入任何可选扩展。
    ``override`` 支持的核心键（与 okf_docs 预设保持字段名一致）：

    * ``project`` / ``author`` / ``release`` / ``version`` / ``language``
    * ``html_title`` / ``html_theme`` / ``html_theme_options``
    * ``extensions_required`` / ``extensions_optional``
    * ``config_override`` 其余任意 Sphinx 配置覆盖
    """
    override = override or {}
    params = dict(override)

    extensions = resolve_extensions(
        required=params.get("extensions_required", ("myst_parser",)),
        optional=params.get("extensions_optional", ()),
    )

    theme = params.get("html_theme") or resolve_theme()
    theme_options = resolve_theme_options(
        theme, params.get("html_theme_options")
    )

    params["html_theme"] = theme
    params["html_theme_options"] = theme_options
    params["extensions"] = extensions
    project_meta = build_project_meta(params, _MINIMAL_KEY_DEFAULTS)
    project_meta["extensions"] = extensions
    project_meta["html_theme"] = theme
    project_meta["html_theme_options"] = theme_options

    base = build_base_config(params)
    merged = deep_merge(base, project_meta)

    merged["setup"] = build_setup_closure(
        register_fns=[register_hooks],
        user_setup=params.get("setup"),
    )
    return merged
