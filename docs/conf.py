#!/usr/bin/env python3
"""Sphinx configuration file for the 'SpecWeave' project documentation."""

import importlib.util as _ilut
import os
import sys
from pathlib import Path

if sys.platform == "win32":
    import asyncio

    if hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


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
