"""渲染包入口（upstream: packages/core/src/renderer/index.ts）。"""

from typing import Any

from .options import (
    CountMessages,
    DiagramMessages,
    IOpts,
    RenderMessages,
)
from .renderer import CollectedHeading, ParseResult, Renderer

__all__ = [
    "init_renderer",
    "Renderer",
    "IOpts",
    "CollectedHeading",
    "ParseResult",
    "DiagramMessages",
    "CountMessages",
    "RenderMessages",
]

_OPTION_FIELDS = set(IOpts.__dataclass_fields__)


def init_renderer(opts: IOpts | dict[str, Any] | None = None) -> Renderer:
    """upstream: renderer-impl.ts initRenderer。"""
    if opts is None:
        return Renderer(IOpts())
    if isinstance(opts, IOpts):
        return Renderer(opts)
    known = {k: v for k, v in opts.items() if k in _OPTION_FIELDS}
    return Renderer(IOpts(**known))
