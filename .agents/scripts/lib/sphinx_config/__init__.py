"""Sphinx 文档构建可复用配置模块。

从 ``projects/awesome-okf-xs/doc/conf.py`` 萃取的通用 Sphinx+MyST 配置层，
解决项目特定硬编码与构建工程通用逻辑耦合的问题。

三大分层（对应洞察 1 的分层架构建议）：
    1. 通用默认字典层——``core.py`` 汇总 MyST、扩展、HTML 等通用默认值
    2. 逻辑函数层——``extensions`` 弹性加载、``themes`` 优先级队列、``myst_compat`` 兼容钩子
    3. 场景预设层——``presets.okf_docs`` / ``presets.minimal_myst`` 一键组装完整 conf

Hello World（任意项目 ``doc/conf.py`` 只需 5 行）::

    from specweave_lib.sphinx_config import ensure_lib_on_syspath
    ensure_lib_on_syspath()
    from specweave_lib.sphinx_config.presets.okf_docs import build_config
    globals().update(build_config({"project": "my-project", "author": "me"}))

模块对外公开的函数/变量均在本文件显式导出，其他子模块视为私有。
"""

import sys
from pathlib import Path

from ._utils import deep_merge, has_module
from .core import (
    DEFAULT_BUILD_CONFIG,
    DEFAULT_EXT_CONFIG,
    DEFAULT_HTML_CONFIG,
    DEFAULT_MYST_CONFIG,
    build_base_config,
)
from .extensions import (
    DEFAULT_CONDITIONAL,
    DEFAULT_OPTIONAL_EXTENSIONS,
    resolve_extensions,
)
from .myst_compat import (
    dedupe_injected_h1,
    quote_frontmatter_dates,
    register_hooks,
)
from .themes import (
    DEFAULT_BOOK_THEME_OPTIONS,
    DEFAULT_THEME_PRIORITY,
    resolve_theme,
    resolve_theme_options,
)
from .presets import build_minimal_myst_config, build_okf_config


def ensure_lib_on_syspath(anchor: str | None = None) -> Path:
    """把 ``.agents/scripts/`` 绝对路径插入 ``sys.path``（自举辅助）。

    典型场景：子项目的 ``doc/conf.py``（在 projects/<name>/doc/）想复用本模块，
    但 Sphinx 启动时 ``sys.path`` 不包含 SpecWeave 主仓的共享脚本目录。
    调用本函数后即可正常 ``from lib.sphinx_config import ...``。

    参数 ``anchor`` 默认为本模块的 ``__file__``，用于反向推导
    ``<repo_root>/.agents/scripts/`` 的位置——调用方传入自定义 anchor
    也可兼容模块被复制到其他目录后的自举。

    返回：实际插入到 ``sys.path`` 的目录（:class:`Path`），便于调试。
    """
    anchor_path = Path(anchor or __file__).resolve()
    scripts_dir: Path | None = None
    for parent in anchor_path.parents:
        if parent.name == "scripts" and parent.parent.name == ".agents":
            scripts_dir = parent
            break
    if scripts_dir is None:
        scripts_dir = anchor_path.parent
    scripts_str = str(scripts_dir)
    if scripts_str not in sys.path:
        sys.path.insert(0, scripts_str)
    return scripts_dir


__all__ = [
    "deep_merge",
    "has_module",
    "ensure_lib_on_syspath",
    "DEFAULT_BUILD_CONFIG",
    "DEFAULT_EXT_CONFIG",
    "DEFAULT_HTML_CONFIG",
    "DEFAULT_MYST_CONFIG",
    "build_base_config",
    "DEFAULT_CONDITIONAL",
    "DEFAULT_OPTIONAL_EXTENSIONS",
    "resolve_extensions",
    "dedupe_injected_h1",
    "quote_frontmatter_dates",
    "register_hooks",
    "DEFAULT_BOOK_THEME_OPTIONS",
    "DEFAULT_THEME_PRIORITY",
    "resolve_theme",
    "resolve_theme_options",
    "build_minimal_myst_config",
    "build_okf_config",
]
