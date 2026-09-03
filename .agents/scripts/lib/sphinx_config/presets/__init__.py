"""lib.sphinx_config — Sphinx + MyST 文档构建可复用配置层预设包。

双预设定位差异：
  - build_okf_config（来自 presets.okf_docs）：10 可选扩展 + intersphinx + repo→site_url 自动推断，适合正式 OKF 站点
  - build_minimal_myst_config（来自 presets.minimal_myst）：仅 myst_parser + 双 MyST 兼容钩子，适合个人轻量笔记
"""

from .okf_docs import build_config as build_okf_config
from .minimal_myst import build_config as build_minimal_myst_config

__all__ = ["build_okf_config", "build_minimal_myst_config"]
