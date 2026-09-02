#!/usr/bin/env python3
"""Sphinx configuration file for the 'SpecWeave' project documentation."""

import importlib.util as _ilut
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


project = "SpecWeave"
author = "SpecWeave Team"
copyright = "2026, SpecWeave Team"
release = "1.0.0"
version = release

language = "zh_CN"


def _has(mod: str) -> bool:
    try:
        return _ilut.find_spec(mod) is not None
    except ModuleNotFoundError:
        return False


core_exts = [
    "sphinx.ext.napoleon",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
]

optional_exts = [
    "myst_parser",
    "sphinx_design",
    "sphinxcontrib.mermaid",
    "sphinx_copybutton",
]

extensions = core_exts.copy()
extensions.extend([e for e in optional_exts if _has(e)])


exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    ".venv",
]

master_doc = "index"
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}

html_static_path = ["_static"]
html_css_files = [
    "variables.css",
    "local.css",
    "mermaid.css",
]
html_favicon = "_static/images/favicon.png"
html_logo = "_static/images/logo.png"

html_last_updated_fmt = "%Y-%m-%d, %H:%M:%S"


if _has("sphinx_book_theme"):
    html_theme = "sphinx_book_theme"
elif _has("sphinx_rtd_theme"):
    html_theme = "sphinx_rtd_theme"
else:
    html_theme = "alabaster"

html_title = "SpecWeave"
html_copy_source = False

html_show_sourcelink = False
html_show_sphinx = False
html_show_copyright = True

html_compact_lists = True


intersphinx_mapping = {}


copybutton_exclude = ".linenos, .gp"
copybutton_selector = ":not(.prompt) > div.highlight pre"


html_theme_options = {}
try:
    import tomllib as _tomllib

    cfg_path = Path(__file__).parent / "_config.toml"
    if cfg_path.exists():
        _cfg = _tomllib.loads(cfg_path.read_text("utf-8"))
        html_theme_options = _cfg.get("html_theme_options", {})
except Exception:
    pass


html_baseurl = os.environ.get("SITEMAP_URL_BASE", "http://localhost:8000/")


numfig = True

myst_enable_extensions = [
    "dollarmath",
    "amsmath",
    "deflist",
    "colon_fence",
    "replacements",
    "substitution",
]
myst_footnote_transition = False

myst_fence_as_directive = ["mermaid"]

suppress_warnings = ["myst.xref_missing"]

templates_path = ["_templates"]


napoleon_use_ivar = True


# --- frontmatter 裸日期/时间戳自动加引号 -------------------------------
# myst_parser 会把无引号的 YAML 日期解析为 datetime.date 对象，进而在
# dict_to_fm_field_list 中 json.dumps 时报 "Object of type date is not
# JSON serializable"。此钩子在解析前为 frontmatter 内的裸日期/时间戳补上
# 双引号，避免逐个文件修改。覆盖行级（`stale_after: 2027-02-23`）与
# 嵌套 map（`at: 2026-08-23 }` / `at: 2026-08-23T10:00:00+08:00 }`）两种场景。
import re as _re

_ISO_DATETIME_RE = _re.compile(
    r"([A-Za-z_][A-Za-z0-9_-]*\s*:\s*)"
    r"(\d{4}-\d{2}-\d{2}(?:[Tt]\d{2}:\d{2}:\d{2}(?:[+-]\d{2}:\d{2}|Z)?)?)"
)

_FRONTMATTER_DELIM = _re.compile(r"^(?:---|\+\+\+|\.\.\.)\s*$", _re.MULTILINE)


def _quote_frontmatter_dates(app, docname, source):
    """source-read 钩子：为 frontmatter 块内无引号的裸日期/时间戳补上双引号。

    仅当日期/时间戳本身构成完整值时才加引号：值尾允许行尾、行内空白后直接
    换行，或 flow map/list 的闭合标点（``}``/``]``/``,``）。必须避免误伤
    以日期开头的长纯标量（如 ``description: 2026-08-28对博文……``）——
    早期版本无条件替换会在中文值中间插入孤立引号，导致 myst 报
    ``Malformed YAML [myst.topmatter]``。
    """
    text = source[0]
    delims = list(_FRONTMATTER_DELIM.finditer(text))
    # 仅处理真正的 frontmatter：首条定界符必须位于文件起始；否则正文中的
    # 水平线（``---`` transition）会被误当作 frontmatter 栅栏，导致正文被
    # 注入引号。
    if len(delims) < 2 or delims[0].start() != 0:
        return
    fm = text[delims[0].end(): delims[1].start()]

    def _repl(match: _re.Match) -> str:
        # 同一行日期之后的剩余内容（跨行的 key: 值 中日期总在值首行）。
        line_tail = fm[match.end():].split("\n", 1)[0].strip()
        if line_tail == "" or line_tail[-1] in "}]," or line_tail.startswith("#"):
            return match.expand(r'\1"\2"')
        return match.group(0)

    quoted = _ISO_DATETIME_RE.sub(_repl, fm)
    if quoted != fm:
        source[0] = text[: delims[0].end()] + quoted + text[delims[1].start():]


def setup(app):
    app.connect("source-read", _quote_frontmatter_dates)
