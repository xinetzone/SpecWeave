from __future__ import annotations

import os
from typing import Iterable, Sequence

from ._utils import has_module


def resolve_extensions(
    required: Sequence[str] = ("myst_parser",),
    optional: Sequence[str] = (),
    conditional: Sequence[tuple[str, callable]] = (),
) -> list[str]:
    """解析三类扩展列表（公理 A3 实现）。

    参数：
        required: 必须加载的扩展，缺失直接抛 :class:`ImportError`。
        optional: 可选扩展，不存在则静默跳过。
        conditional: ``(ext_name, predicate)`` 列表——predicate 返回真值才加载；
            典型 predicate 如检查 :envvar:`GITHUB_ACTIONS` / :envvar:`READTHEDOCS`。

    返回合并去重后的 extensions 列表（保持首次出现的顺序）。
    """
    result: list[str] = []
    seen: set[str] = set()

    def _add(ext: str) -> None:
        if ext not in seen:
            seen.add(ext)
            result.append(ext)

    for ext in required:
        if not has_module(ext):
            raise ImportError(
                f"[sphinx_config] required extension missing: {ext!r}. "
                f"Install it or remove it from the `required` list."
            )
        _add(ext)

    for ext in optional:
        if has_module(ext):
            _add(ext)

    for ext, predicate in conditional:
        try:
            ok = bool(predicate())
        except Exception:
            ok = False
        if ok and has_module(ext):
            _add(ext)

    return result


DEFAULT_OPTIONAL_EXTENSIONS: tuple[str, ...] = (
    "sphinx_design",
    "sphinx_copybutton",
    "sphinx_tippy",
    "sphinx_sitemap",
    "sphinx.ext.intersphinx",
    "sphinx.ext.extlinks",
    "sphinx.ext.graphviz",
    "sphinx_contributors",
    "sphinxext.opengraph",
    "sphinxcontrib.mermaid",
)


def _sitemap_conditional() -> bool:
    """sitemap 扩展启用条件：非 RTD 环境且有本地/CI 可用的 baseurl。"""
    if os.environ.get("GITHUB_ACTIONS"):
        return True
    if not os.environ.get("READTHEDOCS"):
        return True
    return False


DEFAULT_CONDITIONAL: tuple[tuple[str, callable], ...] = (
    # 设计取舍（2026-09-03 V 阶段对抗审查确认）：
    #   「conditional 扩展是否启用」的判断逻辑，和「该扩展对应的 Sphinx 配置键」
    #   是两套独立机制。当 CI 环境触发 _sitemap_conditional() 但实际未安装
    #   sphinx_sitemap 包时，resolve_extensions() 内部 has_module() 会静默跳过注册，
    #   而 core.py 已注入的 html_baseurl/sitemap_url_scheme 等配置键会被 Sphinx
    #   作为「未知配置」安全忽略，不影响构建。因此此处不强制绑定配置键与扩展存在性。
    ("sphinx_sitemap", _sitemap_conditional),
)
