"""主题管理模块（直接 re-export mystx.themes，F-010 事实）。

本模块所有 API 均来自 :mod:`mystx.themes` 原封不动 re-export，
仅在模块导入时通过 :func:`ensure_mystx_on_syspath` 自举 git submodule 路径。

为了兼容 monkeypatch，``has_module`` 绑定到本模块命名空间，并在
调用 mystx 函数前替换 ``mystx.themes`` 子模块命名空间中的 has_module。
"""

from typing import Sequence

from ._utils import ensure_mystx_on_syspath, has_module as _sc_has_module

ensure_mystx_on_syspath(__file__)

import mystx.themes as _mystx_theme_mod
from mystx.themes import (
    DEFAULT_BOOK_THEME_OPTIONS,
    DEFAULT_THEME_PRIORITY,
    resolve_theme as _mystx_resolve_theme,
    resolve_theme_options,
)

has_module = _sc_has_module


def resolve_theme(
    priority: Sequence[str] = DEFAULT_THEME_PRIORITY,
    extra_before: Sequence[str] = (),
    extra_after: Sequence[str] = (),
) -> str:
    """包装 mystx.resolve_theme：调用前替换子模块命名空间的 has_module。

    这样 monkeypatch ``sphinx_config.themes.has_module`` 即可影响 mystx 内部。
    mystx 中 ``extra_before`` / ``extra_after`` 是关键字参数（`*` 之后）。
    """
    _orig = _mystx_theme_mod.__dict__.get("has_module")
    _mystx_theme_mod.has_module = has_module
    try:
        return _mystx_resolve_theme(
            priority, extra_before=tuple(extra_before), extra_after=tuple(extra_after)
        )
    finally:
        if _orig is None:
            _mystx_theme_mod.__dict__.pop("has_module", None)
        else:
            _mystx_theme_mod.has_module = _orig


__all__ = [
    "DEFAULT_THEME_PRIORITY",
    "DEFAULT_BOOK_THEME_OPTIONS",
    "resolve_theme",
    "resolve_theme_options",
    "has_module",
]
