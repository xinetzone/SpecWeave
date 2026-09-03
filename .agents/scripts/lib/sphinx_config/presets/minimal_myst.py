"""最小 MyST 文档项目预设（直接转发 mystx.presets.minimal_myst）。"""

from .._utils import ensure_mystx_on_syspath

ensure_mystx_on_syspath(__file__)

from mystx.presets.minimal_myst import build_config

__all__ = ["build_config"]
