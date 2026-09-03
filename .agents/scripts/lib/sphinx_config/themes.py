from typing import Sequence

from ._utils import deep_merge, has_module

DEFAULT_THEME_PRIORITY: tuple[str, ...] = (
    "mystx",
    "sphinx_book_theme",
    "alabaster",
)


def resolve_theme(
    priority: Sequence[str] = DEFAULT_THEME_PRIORITY,
    *,
    extra_before: Sequence[str] = (),
    extra_after: Sequence[str] = (),
) -> str:
    """按优先级队列选择第一个已安装的主题（公理 A4 实现）。

    默认回退链：``mystx → sphinx_book_theme → alabaster``；
    其中 ``alabaster`` 是 Sphinx 内置主题，保证永不缺失。

    参数 ``extra_before`` / ``extra_after`` 允许在默认队列前后插入自定义主题：
    ``extra_before`` 的项目**优先于**默认主题；``extra_after`` 的项目排在默认
    主题之后、**alabaster 之前**——保证回退到 alabaster 始终是最后一条。
    """
    full: list[str] = []
    full.extend(extra_before)
    for t in priority:
        if t == "alabaster":
            continue
        full.append(t)
    full.extend(extra_after)
    full.append("alabaster")
    for theme in full:
        if theme == "alabaster":
            return "alabaster"
        if has_module(theme):
            return theme
    return "alabaster"


DEFAULT_BOOK_THEME_OPTIONS: dict = {
    "use_repository_button": True,
    "repository_branch": "main",
    "use_source_button": True,
    "use_edit_page_button": False,
    "use_issues_button": True,
    "path_to_docs": "doc",
    "toc_title": "目录",
    "show_navbar_depth": 10,
    "max_navbar_depth": 4,
    "collapse_navbar": False,
    "use_download_button": True,
    "use_fullscreen_button": True,
    "footer_content_items": "author.html, copyright.html, last-updated.html, extra-footer.html",
    "navbar_persistent": [],
}


def resolve_theme_options(
    theme: str,
    override: dict | None = None,
    *,
    book_defaults: dict = DEFAULT_BOOK_THEME_OPTIONS,
) -> dict:
    """根据选定主题合并默认 theme_options。

    目前对 ``sphinx_book_theme`` / ``mystx`` 提供完整默认字典；
    其他主题返回空字典或 override 原样。
    """
    base: dict = {}
    if theme in ("sphinx_book_theme", "mystx"):
        base = dict(book_defaults)
    return deep_merge(base, override or {})
