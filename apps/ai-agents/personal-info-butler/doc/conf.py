"""个人信息管家 Agent —— Sphinx 站点配置。

本目录是应用的**前端与文档的唯一事实来源**：Sphinx 把 MyST Markdown 与
``_static/`` 下的样式/脚本构建成静态站，由 GitHub Actions 发布到 GitHub Pages。
``app.md`` 那一页就是产品的工作台界面，其余页面是使用说明与接口契约。

与参考站 daoapps.github.io 同构：MyST 源 + sphinx-book-theme + ``-W`` 构建门禁。
"""

import json
import os
import re
from pathlib import Path

from sphinx.search import IndexBuilder

# -- 项目元信息 ------------------------------------------------------------

project = "个人信息管家"
author = "SpecWeave"
copyright = "2026, SpecWeave"
language = "zh_CN"

# -- 路径 ------------------------------------------------------------------

DOC_DIR = Path(__file__).resolve().parent
BUILD_DIR = DOC_DIR.parent / "_build"

# -- 扩展 ------------------------------------------------------------------

extensions = [
    "myst_parser",            # MyST Markdown 作为一等源格式
    "sphinx_book_theme",      # 阅读优先主题
    "sphinx_copybutton",      # 代码块一键复制
    "sphinx_design",          # 卡片 / 栅格 / 标签页
    "sphinxcontrib.mermaid",  # Mermaid 图（项目规范：图表优先）
]

# -- MyST ------------------------------------------------------------------

myst_enable_extensions = [
    "colon_fence",    # ::: 围栏，sphinx-design 卡片所需
    "deflist",
    "fieldlist",
    "tasklist",
    "substitution",
    "attrs_inline",
]
myst_heading_anchors = 3

myst_substitutions = {
    "app_name": "个人信息管家",
}

source_suffix = {".md": "markdown"}
root_doc = "index"

# Mermaid 由 sphinxcontrib-mermaid 在前端加载 mermaid.js 渲染，
# 固定版本号避免上游更新导致图表样式漂移。
mermaid_version = "11.4.1"

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "README.md"]

# -- API 基址 --------------------------------------------------------------
# 静态站发布后，浏览器不知道后端部署在哪。构建时把 BUTLER_API_BASE 注入页面，
# 读者打开即可直连；未设置时前端走同源 /api/*（本地 python -m http.server 预览 +
# uvicorn 同机时可用），并可在页面「设置」里手动覆盖（存 localStorage）。
#
# 用 metatags 注入而非模板覆盖：metatags 由 basic/layout.html 直接渲染，
# 不依赖任何主题的 block 名，换主题也不会哑。

API_BASE = os.environ.get("BUTLER_API_BASE", "").strip().rstrip("/")

# -- HTML 输出 -------------------------------------------------------------

html_theme = "sphinx_book_theme"
html_title = "个人信息管家 · Agent"
html_static_path = ["_static"]
html_css_files = ["butler.css"]
html_js_files = ["butler.js"]
html_show_sourcelink = False
html_last_updated_fmt = ""

html_theme_options = {
    "use_download_button": False,
    "use_fullscreen_button": False,
    "use_repository_button": False,
    "use_edit_page_button": False,
    "use_issues_button": False,
    "home_page_in_toc": False,
    "show_navbar_depth": 1,
    "show_toc_level": 3,
    "extra_footer": "",  # 实际内容由 _inject_footer 注入
    # 搜索框只能有一个；此处显式置空导航栏的持久组件位。
    #
    # sphinx-book-theme 自己的 theme.conf 把 `search-button-field.html` 列进主侧边栏
    # （顺序即阅读动线：品牌 → 搜索 → 导航），同时把 `navbar_persistent` 留空——它的
    # 本意就是「搜索住侧边栏」。但底层 pydata 主题发现该键为空时会补上默认值
    # `["search-button-field"]`，于是同一屏出现两个长得一样、开的也是同一个对话框的
    # 搜索框：冗余的代价不是像素，而是**歧义**——用户会以为上面那个搜文档、下面那个
    # 搜自己的条目。
    #
    # 显式给出空列表（而非依赖主题的留空）是必须的：pydata 的判据是「键在不在」，
    # 不是「值空不空」，所以只有我们明确写出来才拦得住那个默认值。
    # 入口不会因此变少：侧边栏那个仍在，正文区右上角的图标变体也仍在（窄视口靠它）。
    "navbar_persistent": [],
}

# -- 搜索 ------------------------------------------------------------------
# 中文搜索需要 jieba 分词：SearchChinese 未装 jieba 时 cut_for_search 返回空集，
# 中文内容一个字都进不了索引——构建期不报错，只是搜不到。requirements.txt 已列入。
#
# 另一道坎是词干器：中文站若声明了 js_stemmer_rawcode，Sphinx 会按
# language_name 拼出 `Stemmer = ChineseStemmer;`，而词干器文件里定义的是
# EnglishStemmer，引用落空后搜索框直接打不开。按文件名推导真实全局名改正该行；
# 上游若修好，推导结果与赋值行一致，补丁自动失效（防御性，非必现修复）。

_STEMMER_GLOBAL = re.compile(r"(?:window\.)?Stemmer\s*=\s*(\w+Stemmer);")


def _derive_stemmer_global(rawcode: str) -> str:
    """``english-stemmer.js`` → ``EnglishStemmer``。"""
    name = rawcode.removesuffix(".js").removesuffix("-stemmer")
    return "".join(part.capitalize() for part in re.split(r"[-_]", name)) + "Stemmer"


_original_get_js_stemmer_code = IndexBuilder.get_js_stemmer_code


def _get_js_stemmer_code(self):  # noqa: ANN001
    code = _original_get_js_stemmer_code(self)
    rawcode = self.lang.js_stemmer_rawcode
    if not rawcode:
        return code
    found = _STEMMER_GLOBAL.search(code)
    expected = _derive_stemmer_global(rawcode)
    if found is None or found.group(1) == expected:
        return code
    return _STEMMER_GLOBAL.sub(f"window.Stemmer = {expected};", code)


IndexBuilder.get_js_stemmer_code = _get_js_stemmer_code

# -- 页脚 ------------------------------------------------------------------

_FOOTER = (
    "个人信息管家 · SpecWeave<br>"
    "数据存于你自己的云端库，页面 BYOK 凭据只留在本机浏览器"
)


def _inject_footer(app, pagename, templatename, context, doctree):  # noqa: ANN001
    context["theme_extra_footer"] = _FOOTER


def _inject_api_base(app, pagename, templatename, context, doctree):  # noqa: ANN001
    """把 API 基址写进 <head>，供 _static/butler.js 读取。"""
    context["metatags"] = context.get("metatags", "") + (
        f'<script>window.BUTLER_API_BASE={json.dumps(API_BASE)};</script>'
    )


# -- 构建期守卫 ------------------------------------------------------------
# 前端脚本靠一组固定 id 挂事件。改页面时漏删一个 id，构建期看不出来，
# 上线后按钮点了没反应——把「页面必须提供这些挂载点」变成构建期硬错误。

_REQUIRED_IDS = (
    "composer", "btn-capture", "capture-result",
    "search-input", "btn-search", "item-list",
    "ask-input", "btn-ask", "ask-result",
    "btn-extract", "extract-result",
    "btn-todos", "todos-result",
    "btn-summary", "summary-result",
    "set-api-base", "set-token", "btn-save-settings",
    "status-storage", "status-llm",
    # 连接状态是全局事实：横幅是它唯一的呈现位，重连入口必须在顶栏
    "butler-banner", "btn-reconnect",
    # 大模型卡片：三个输入框 + 验证 + 清除 + 结论区
    "set-llm-base", "set-llm-key", "set-llm-model",
    "btn-llm-test", "btn-llm-clear", "llm-result",
)


def _check_app_shell(app, config):  # noqa: ANN001
    """工作台页面必须包含前端脚本所需的全部挂载点。"""
    app_md = DOC_DIR / "app.md"
    if not app_md.exists():
        raise RuntimeError("缺少 doc/app.md：工作台页面是产品的主界面")
    text = app_md.read_text(encoding="utf-8")
    missing = [key for key in _REQUIRED_IDS if f'id="{key}"' not in text]
    if missing:
        raise RuntimeError(
            "doc/app.md 缺少前端挂载点：\n  - " + "\n  - ".join(missing)
        )


def setup(app):  # noqa: ANN001
    app.connect("config-inited", _check_app_shell)
    app.connect("html-page-context", _inject_footer)
    app.connect("html-page-context", _inject_api_base)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
