"""marked 自定义扩展的 markdown-it-py 移植包。

upstream: packages/core/src/extensions/。装配顺序对齐
renderer-impl.ts:468-497（component→markup→emoji→toc→slider→alert→…）。
"""

from .alert import register_alert
from .diagrams import register_infographic, register_mermaid, register_plantuml
from .component import register_component
from .emoji import register_emoji
from .footnotes import register_footnotes
from .katex import register_katex
from .markup import register_markup
from .ruby import register_ruby
from .slider import register_slider
from .toc import register_toc

__all__ = [
    "register_markup",
    "register_component",
    "register_emoji",
    "register_toc",
    "register_slider",
    "register_alert",
    "register_katex",
    "register_footnotes",
    "register_mermaid",
    "register_plantuml",
    "register_infographic",
    "register_ruby",
]
