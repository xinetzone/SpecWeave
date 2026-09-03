"""Sphinx 扩展弹性加载（来自 mystx.extensions，D3 维度增量叠加 mermaid）。

- ``resolve_extensions`` / ``DEFAULT_CONDITIONAL``：来自 mystx.extensions 完全相同
  实现（F-003 事实）。
- ``DEFAULT_OPTIONAL_EXTENSIONS``：mystx 中已移除 ``sphinxcontrib.mermaid``
  （不在 mystx 的 optional-dependencies），但 sphinx_config 场景保留该项
  （D3 维度，A2 公理：增量叠加不覆盖）。
"""

from collections.abc import Callable
from typing import Sequence

from ._utils import ensure_mystx_on_syspath, has_module as _sc_has_module

ensure_mystx_on_syspath(__file__)

import mystx.extensions as _mystx_ext_mod
from mystx.extensions import (
    DEFAULT_CONDITIONAL as _MYSTX_CONDITIONAL,
    DEFAULT_OPTIONAL_EXTENSIONS as _MYSTX_OPTIONAL,
    resolve_extensions as _mystx_resolve_extensions,
)

DEFAULT_OPTIONAL_EXTENSIONS: tuple[str, ...] = tuple(_MYSTX_OPTIONAL) + (
    "sphinxcontrib.mermaid",
)
DEFAULT_CONDITIONAL = _MYSTX_CONDITIONAL

has_module = _sc_has_module


def resolve_extensions(
    required: Sequence[str] = (),
    optional: Sequence[str] = (),
    conditional: Sequence[tuple[str, Callable[[], bool]]] = (),
) -> list[str]:
    """调用 mystx 前，把 sphinx_config 子模块的 has_module 注入到 mystx.extensions。

    这样 monkeypatch ``sphinx_config.extensions.has_module`` 即可影响 mystx 内部。
    """
    _orig = _mystx_ext_mod.__dict__.get("has_module")
    _mystx_ext_mod.has_module = has_module
    try:
        return _mystx_resolve_extensions(required, optional, conditional)
    finally:
        if _orig is None:
            _mystx_ext_mod.__dict__.pop("has_module", None)
        else:
            _mystx_ext_mod.has_module = _orig


__all__ = [
    "resolve_extensions",
    "DEFAULT_OPTIONAL_EXTENSIONS",
    "DEFAULT_CONDITIONAL",
    "has_module",
]
