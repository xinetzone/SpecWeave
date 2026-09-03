"""MyST 兼容钩子（直接 re-export mystx.myst_compat，F-004 事实）。

mystx 已内置 ``MYSTX_MYST_COMPAT_*`` 规范前缀，并保留了
``SW_MYST_COMPAT_*`` 的兼容处理（日志 INFO 警告）。详见
:func:`mystx.myst_compat._reload_env_settings`。
"""

from ._utils import ensure_mystx_on_syspath

ensure_mystx_on_syspath(__file__)

from mystx import myst_compat as _mystx_mc

quote_frontmatter_dates = _mystx_mc.quote_frontmatter_dates
dedupe_injected_h1 = _mystx_mc.dedupe_injected_h1
register_hooks = _mystx_mc.register_hooks
_reload_env_settings = _mystx_mc._reload_env_settings
_ENV_QUOTE_DATES = _mystx_mc._ENV_QUOTE_DATES
_ENV_DEDUPE_H1 = _mystx_mc._ENV_DEDUPE_H1
_FM_DELIM = _mystx_mc._FM_DELIM


def _sync_env_to_mystx() -> tuple[bool, bool]:
    """把本模块的 _ENV_* 状态写入 mystx 命名空间，返回原值。"""
    _oq = _mystx_mc._ENV_QUOTE_DATES
    _ood = _mystx_mc._ENV_DEDUPE_H1
    _mystx_mc._ENV_QUOTE_DATES = _ENV_QUOTE_DATES
    _mystx_mc._ENV_DEDUPE_H1 = _ENV_DEDUPE_H1
    return _oq, _ood


def _restore_env_to_mystx(orig_quote: bool, orig_dedupe: bool) -> None:
    """恢复 mystx 命名空间的 _ENV_* 原值。"""
    _mystx_mc._ENV_QUOTE_DATES = orig_quote
    _mystx_mc._ENV_DEDUPE_H1 = orig_dedupe


# —— 包装公共函数：调用前后同步 ENV 状态 ——

_original_quote_frontmatter_dates = quote_frontmatter_dates


def quote_frontmatter_dates(app, docname: str, source: list[str]) -> None:  # type: ignore[no-redef]
    _oq, _od = _sync_env_to_mystx()
    try:
        return _original_quote_frontmatter_dates(app, docname, source)
    finally:
        _restore_env_to_mystx(_oq, _od)


_original_dedupe_injected_h1 = dedupe_injected_h1


def dedupe_injected_h1(app, doctree) -> None:  # type: ignore[no-redef]
    _oq, _od = _sync_env_to_mystx()
    try:
        return _original_dedupe_injected_h1(app, doctree)
    finally:
        _restore_env_to_mystx(_oq, _od)


_original_register_hooks = register_hooks


def register_hooks(app) -> None:  # type: ignore[no-redef]
    _oq, _od = _sync_env_to_mystx()
    try:
        return _original_register_hooks(app)
    finally:
        _restore_env_to_mystx(_oq, _od)


_original_reload = _reload_env_settings


def _reload_env_settings() -> None:  # type: ignore[no-redef]
    """先让 mystx 从环境变量重新加载，再把结果同步回本模块。"""
    _original_reload()
    global _ENV_QUOTE_DATES, _ENV_DEDUPE_H1  # noqa: PLW0603
    _ENV_QUOTE_DATES = _mystx_mc._ENV_QUOTE_DATES
    _ENV_DEDUPE_H1 = _mystx_mc._ENV_DEDUPE_H1


__all__ = [
    "quote_frontmatter_dates",
    "dedupe_injected_h1",
    "register_hooks",
    "_ENV_QUOTE_DATES",
    "_ENV_DEDUPE_H1",
    "_FM_DELIM",
    "_reload_env_settings",
]
