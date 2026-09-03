"""预设共享工具（build_* 从 mystx.presets._shared 直接 re-export）。

历史注解：
    曾有 ``merge_html_theme`` 辅助函数通过 ``html_theme_options`` 深度合并
    包装 resolve_theme_options。该语义已由
    ``resolve_theme_options(theme, override_dict)`` 的第二参数 +
    ``_utils.deep_merge`` 显式实现，不在此处提供单函数封装。
"""

from .._utils import ensure_mystx_on_syspath, deep_merge
from ..themes import resolve_theme_options

ensure_mystx_on_syspath(__file__)

from mystx.presets._shared import (  # noqa: E402
    build_project_meta,
    build_setup_closure,
)


def merge_html_theme(
    base_options: dict, custom_options: dict | None = None
) -> dict:
    """显式合并两组 ``html_theme_options``——保留历史 API 以防外部调用。

    等效于 ``deep_merge(base_options, custom_options)``，
    内部最终结果交由 ``resolve_theme_options`` 判断使用。
    """
    return deep_merge(base_options, custom_options or {})


__all__ = ["build_project_meta", "build_setup_closure", "merge_html_theme"]
