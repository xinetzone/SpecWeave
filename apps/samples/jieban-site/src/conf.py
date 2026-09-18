"""结伴站点 Sphinx 配置。

技术选型依据：`playground/reports/jieban-brand-20260918/结伴-技术选型建议-Sphinx与JupyterLite.md`
（三层分离架构之「内容层」；本应用只承担 `/guide/` 这一层）。

主题偏离说明：选型报告原写「furo 主题定制为纸感」，但构建环境未安装 furo，
改用 `sphinx_book_theme`——同为阅读优先主题，且更易做纸感定制。
"""

from __future__ import annotations

import re
from pathlib import Path

# -- 项目元信息 ------------------------------------------------------------

project = "结伴"
author = "结伴"
copyright = "2026, 结伴"
language = "zh_CN"

# -- 路径 ------------------------------------------------------------------
# src/ 为唯一事实来源；构建产物落到应用目录下的 build/（根 .gitignore 已排除）

SRC_DIR = Path(__file__).resolve().parent
BUILD_DIR = SRC_DIR.parent / "build"

# -- 扩展 ------------------------------------------------------------------

extensions = [
    "myst_parser",  # MyST Markdown 作为一等源格式
    "sphinx_book_theme",  # 阅读优先主题
    "sphinx_copybutton",  # 代码块一键复制
    "sphinx_design",  # 卡片 / 栅格 / 标签页
    "sphinxcontrib.mermaid",  # Mermaid 图（项目规范：图表优先）
]

# -- MyST ------------------------------------------------------------------

myst_enable_extensions = [
    "colon_fence",  # ::: 围栏，sphinx-design 卡片与 container 所需
    "deflist",
    "fieldlist",
    "tasklist",
    "substitution",  # 复用品牌名称与引文出处
    "attrs_inline",  # 行内属性：给按钮链接挂 class（[文字](页.md){.jb-btn}）
]
myst_heading_anchors = 3

myst_substitutions = {
    "brand": "结伴",
    "yiwei": "既以予人矣，己愈多",  # 帛书乙本·末章（唯一合规短引文）
}

source_suffix = {".md": "markdown"}
root_doc = "index"

# Mermaid 由 sphinxcontrib-mermaid 在前端加载 mermaid.js 渲染，
# 固定版本号避免上游更新导致图表样式漂移。
mermaid_version = "11.4.1"

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "README.md"]

# -- HTML 输出 -------------------------------------------------------------

html_theme = "sphinx_book_theme"
html_title = "结伴 · 好好生活的人，终会相逢"
html_static_path = ["_static"]
html_css_files = ["jieban.css"]
html_js_files = ["jieban.js"]
html_show_sourcelink = False
html_last_updated_fmt = ""

# 侧栏保留主题默认（左侧文档树 + 右侧本页目录）。
# 曾试过清空侧栏改单栏纸面，但首页是六屏长卷，没有右侧 TOC 就丢了页内锚点导航；
# 内容增长后左侧文档树也不可替代。视觉改造因此只做「表皮」——
# 配色、章节语言、卡片、印章、打印样式，不动骨架。
# （注：sphinx-book-theme 的品牌与主导航本身就挂在左侧栏内，侧栏就是导航。）

html_theme_options = {
    # 一期为单页展示型站点，隐藏仓库/下载/编辑等与品牌无关的按钮
    "use_download_button": False,
    "use_fullscreen_button": False,
    "use_repository_button": False,
    "use_edit_page_button": False,
    "use_issues_button": False,
    "home_page_in_toc": False,
    "show_navbar_depth": 1,
    "show_toc_level": 3,
    # 页脚：与落地页同形（印章行由 CSS 生成，此处只给正文两行）
    "extra_footer": (
        "知足 · 恒与 · 知和 · 愈多 —— 四个微信群共同的客厅<br>"
        "本站不提供任何婚恋中介或投资理财服务。"
        "引文据马王堆帛书本《老子》，详见《社群公约》页的版本说明。"
    ),
}

# -- 构建期一致性检查 ------------------------------------------------------


def _check_version_labels(app, config):  # noqa: ANN001
    """版本身份证（构建期硬检查）。

    两条正向不变量——引文出现在哪，版本标识就必须跟到哪：
    1. 出现末章短引文「己愈多」的页面，必须同时出现「帛书乙本」；
    2. 出现「知和曰明」的页面，必须同时出现「帛书甲本」。

    不做「帛书本」字样的负例扫描：公约页本身要引用这条规则，
    机械匹配必然误伤，故该纪律以文字条款形式写在公约页，不纳入自动检查。
    """
    problems: list[str] = []
    for md in sorted(SRC_DIR.glob("**/*.md")):
        if "_build" in md.parts:
            continue
        text = md.read_text(encoding="utf-8")
        where = md.relative_to(SRC_DIR).as_posix()
        # 归一化：去掉强调标记与空白，避免「帛书**甲本**」这类排版绕过检查
        flat = re.sub(r"[*\s\u3000]", "", text)

        if "己愈多" in flat and "帛书乙本" not in flat:
            problems.append(f"{where}：引用了末章短引文，但未标注「帛书乙本」")
        if "知和曰明" in flat and "帛书甲本" not in flat:
            problems.append(f"{where}：引用了「知和曰明」，但未标注「帛书甲本」")

    if problems:
        raise RuntimeError("引文版本标注不合规：\n  - " + "\n  - ".join(problems))


def setup(app):  # noqa: ANN001
    app.connect("config-inited", _check_version_labels)
    return {"parallel_read_safe": True, "parallel_write_safe": True}