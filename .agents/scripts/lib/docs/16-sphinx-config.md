---
id: "lib-api-sphinx_config"
title: "lib.sphinx_config — Sphinx + MyST 文档构建配置层"
source: "../api_docs.py"
x-toml-ref: "../../../../.meta/toml/.agents/scripts/lib/docs/16-sphinx-config.toml"
---

# lib.sphinx_config — Sphinx + MyST 文档构建配置层

从 `projects/awesome-okf-xs/doc/conf.py` 萃取的通用 Sphinx + MyST 配置层，解决项目特定硬编码与构建工程通用逻辑耦合的问题。

## 设计目标

- **三大分层**：通用默认字典层（core.py）→ 逻辑函数层（extensions/themes/myst_compat）→ 场景预设层（presets）
- **弹性扩展**：`resolve_extensions` 按 必选/可选/条件 三档探测模块可用性
- **主题降级队列**：`resolve_theme` 依优先级队列回退（mystx → sphinx_book_theme → alabaster）
- **MyST 兼容钩子**：`register_hooks` 统一注册 frontmatter 日期引号化 + H1 去重钩子

## 模块导航

| 子模块 | 说明 |
|--------|------|
| [lib.sphinx_config.core](16-sphinx-config.md#core) | 4 个 DEFAULT_* 基础字典 + build_base_config |
| [lib.sphinx_config.extensions](16-sphinx-config.md#extensions) | 扩展弹性加载（含 sphinxcontrib.mermaid 增量） |
| [lib.sphinx_config.themes](16-sphinx-config.md#themes) | 主题优先级队列与 book theme_options 合并 |
| [lib.sphinx_config.myst_compat](16-sphinx-config.md#myst_compat) | MyST 兼容钩子（re-export mystx） |
| [lib.sphinx_config.presets](16-sphinx-config.md#presets) | build_okf_config / build_minimal_myst_config 双预设 |

---

## 核心 API

| 函数 | 签名 | 说明 |
|------|------|------|
| `ensure_lib_on_syspath` | `(anchor: str \| None = None) -> Path` | 自举：把 `.agents/scripts/` + mystx src 插入 sys.path，返回 scripts 目录 |
| `build_base_config` | `(override: dict[str, Any] \| None = None) -> dict[str, Any]` | 合并 4 个 DEFAULT_* + override，注入 intersphinx / ogp_site_url |
| `resolve_extensions` | `(required: Sequence[str] = (), optional: Sequence[str] = (), conditional: Sequence[tuple[str, Callable[[], bool]]] = ()) -> list[str]` | 按必选/可选/条件三档弹性解析扩展列表 |
| `resolve_theme` | `(priority: Sequence[str] = DEFAULT_THEME_PRIORITY, extra_before: Sequence[str] = (), extra_after: Sequence[str] = ()) -> str` | 依优先级队列探测可用主题并返回主题名 |
| `resolve_theme_options` | `(theme: str, override: dict[str, object] \| None = None, *, book_defaults: dict[str, object] = DEFAULT_BOOK_THEME_OPTIONS) -> dict[str, object]` | 根据选定主题合并默认 book theme_options |
| `register_hooks` | `(app) -> None` | 注册 MyST 兼容钩子（日期引号化 + H1 去重） |
| `build_okf_config` | `(override: dict[str, Any] \| None = None) -> dict[str, Any]` | OKF 站点预设：10 可选扩展 + intersphinx + repo→site_url 自动推断 |
| `build_minimal_myst_config` | `(override: dict[str, Any] \| None = None) -> dict[str, Any]` | 轻量预设：仅 myst_parser + 双 MyST 兼容钩子 |

---

## 示例

任意项目 `doc/conf.py` 只需 5 行：

```python
from lib.sphinx_config import ensure_lib_on_syspath
ensure_lib_on_syspath()
from lib.sphinx_config.presets.okf_docs import build_config
globals().update(build_config({"project": "my-project", "author": "me"}))
```

---

## 相关模式

- [共享库引力定律](../../../../docs/retrospective/patterns/methodology-patterns/tools-automation/shared-lib-gravity.md)
- [临时sys.path修改](../../../../docs/retrospective/patterns/code-patterns/temporary-syspath-modification.md)

---

**[返回索引](../README.md)** | 上一章 ← [测试辅助工具库](15-testing.md)
