"""渲染选项（upstream: packages/shared/src/types/common.ts IOpts 1:1）。"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

# upstream: renderer-impl.ts:47-48（英文兜底；Web 端按 locale 注入）
DEFAULT_COUNT_SUMMARY = "{words} words, about {minutes} min read"
DEFAULT_FOOTNOTE_TITLE = "References"


@dataclass(slots=True)
class DiagramMessages:
    """upstream: DiagramMessages（图表加载/错误文案，error 支持 {detail}）。"""

    mermaid_loading: str = ""
    mermaid_error: str = ""
    plantuml_loading: str = ""
    plantuml_error: str = ""
    infographic_loading: str = ""
    infographic_error: str = ""


@dataclass(slots=True)
class CountMessages:
    """upstream: CountMessages。"""

    summary: str = DEFAULT_COUNT_SUMMARY


@dataclass(slots=True)
class RenderMessages:
    """upstream: RenderMessages。"""

    footnote_title: str = DEFAULT_FOOTNOTE_TITLE
    unknown_component: str = ""
    katex_loading: str = ""


@dataclass(slots=True)
class IOpts:
    """upstream: common.ts IOpts（CSS 注入主题系统的渲染开关）。"""

    legend: str | None = None
    cite_status: bool = False
    count_status: bool = False
    is_mac_code_block: bool = False
    is_show_line_number: bool = False
    theme_mode: str = "light"  # 'light' | 'dark'
    # 自定义组件注册表（T6 component 扩展落地具体类型）
    components: Any = None
    diagram_messages: DiagramMessages | None = None
    count_messages: CountMessages | None = None
    render_messages: RenderMessages | None = None
    asset_resolver: Callable[[str], str] | None = None

    def merge(self, patch: dict[str, Any] | None) -> "IOpts":
        """upstream: setOptions 的 ``{ ...opts, ...newOpts }`` 浅合并。

        仅接受显式给出的键（dict 形态），false/0/空串同样覆盖。
        """
        if patch:
            for key, value in patch.items():
                setattr(self, key, value)
        return self
