# okw 应用自带文档站点配置：本目录即真源，不从他处同步。

import re

from sphinx.search import IndexBuilder

project = "openKylin WSL 开发工具包"
author = "SpecWeave"
copyright = "%Y, SpecWeave"

language = "zh_CN"
version = release = "0.1.0"

extensions = [
    "myst_parser",
    "sphinx_book_theme",
    "sphinx_copybutton",
    "sphinx_design",
]

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "tasklist",
    "substitution",
    "attrs_inline",
]
myst_heading_anchors = 3

# 跨出本站源目录（doc/）的相对 .md 链接无法映射为本站 docname，
# 与 docs/conf.py 的既有口径保持一致，不将其视为构建告警。
suppress_warnings = ["myst.xref_missing"]

source_suffix = {".md": "markdown"}
root_doc = "index"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "README.md"]

# 搜索词干器全局名修补：Sphinx 生成 language_data.js 时按 language_name 拼赋值行——
# zh 站为 "Chinese"，得到 `window.Stemmer = ChineseStemmer;`；但 zh 复用的词干器文件
# 实际导出的是 EnglishStemmer，引用落空后 window.Stemmer 为 undefined，searchtools.js
# 抛 "ChineseStemmer is not defined"，搜索框打不开。这里按词干器文件名推导真实全局名
# 并改写该赋值行；上游若修好，推导结果与赋值行一致，本补丁自动失效。
_STEMMER_ASSIGNMENT = re.compile(r"(?:window\.)?Stemmer\s*=\s*(\w+Stemmer);")


def _stemmer_global_name(rawcode: str) -> str:
    """由词干器文件名推导其导出的全局名：english-stemmer.js -> EnglishStemmer。"""
    stem = rawcode.removesuffix(".js").removesuffix("-stemmer")
    return "".join(part.capitalize() for part in re.split(r"[-_]", stem)) + "Stemmer"


_ORIGINAL_GET_JS_STEMMER_CODE = IndexBuilder.get_js_stemmer_code


def _get_js_stemmer_code(self):  # noqa: ANN001
    code = _ORIGINAL_GET_JS_STEMMER_CODE(self)
    rawcode = self.lang.js_stemmer_rawcode
    if not rawcode:
        return code
    match = _STEMMER_ASSIGNMENT.search(code)
    expected = _stemmer_global_name(rawcode)
    if match is None or match.group(1) == expected:
        return code
    return _STEMMER_ASSIGNMENT.sub(f"window.Stemmer = {expected};", code)


IndexBuilder.get_js_stemmer_code = _get_js_stemmer_code

html_theme = "sphinx_book_theme"
html_theme_options = {
    "use_download_button": False,
    "use_fullscreen_button": False,
    "use_issues_button": False,
    "use_edit_page_button": False,
    "use_repository_button": False,
    "show_toc_level": 2,
    "navigation_with_keys": True,
    # 关闭顶栏。pydata-sphinx-theme 0.20 在未显式设置 navbar_persistent 时会自动塞入
    # 「搜索按钮」，使 book-theme 的顶栏（本是空容器）被渲染出来；而顶栏模板无条件输出
    # 一个 class 含 primary-toggle 的侧栏开关。两个主题的脚本都用
    # document.querySelector(".primary-toggle") 取**第一个**匹配：
    #   - sphinx-book-theme 用它做 ≥992px 的 .pst-sidebar-hidden 折叠；
    #   - pydata 用它做 <992px 的侧栏模态。
    # 第一个匹配落在被 CSS 隐藏的顶栏按钮上，正文页头里那个可见的开关就再也没有监听器，
    # 表现为「主侧边栏无法折叠」。置空后顶栏整体不渲染，唯一开关回到正文页头。
    "navbar_persistent": [],
}
html_title = "openKylin WSL 开发工具包"
html_static_path = ["_static"]
html_css_files = ["okw.css"]

# 侧栏白名单：品牌 + 搜索 + 文档树，与 book 主题默认一致（book 主题默认值即
# navbar-logo.html, icon-links.html, search-button-field.html, sbt-sidebar-nav.html，
# 这里只去掉本站未使用的 icon-links）。
# 搜索入口的显隐由主题 CSS 分流：≥992px 显示侧栏里的「搜索 Ctrl+K」带文字按钮，
# <992px 显示正文页头里的图标按钮——任一宽度下都恰好一个。白名单是全量替换而非增量，
# 删项即失去对应组件；此前删掉 search-button-field 会导致全宽度下搜索入口归零。
html_sidebars = {"**": ["navbar-logo.html", "search-button-field.html", "sbt-sidebar-nav.html"]}