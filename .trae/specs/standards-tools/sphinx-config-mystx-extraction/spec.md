---
status: "draft"
id: "sphinx-config-mystx-extraction"
title: "Sphinx Config → mystx 模块萃取与整合"
source: "d:/spaces/SpecWeave/.agents/scripts/lib/sphinx_config"
x-toml-ref: "../../.meta/toml/.trae/specs/standards-tools/sphinx-config-mystx-extraction.toml"
---

# Sphinx Config → mystx 模块萃取与整合 — Product Requirement Document

## Overview
- **Summary**: 将 SpecWeave 主权区 `lib/sphinx_config`（9 子模块 + 2 preset）中与 mystx 主题强相关的 Sphinx/MyST 通用工具层萃取到第三方 Git 独立项目 `playground/books/libs/mystx/src/mystx`，作为 mystx 主题原生提供的 Sphinx 扩展能力对外发布；保留 SpecWeave 内部 `lib/sphinx_config` 作为上游来源，仅通过 API 稳定层保持复用。
- **Purpose**: 解决当前 mystx `config.py` 中 `_merge_html_theme_options` 手写两层合并（易与 deep_merge 不一致）、无通用 `has_module/resolve_extensions/resolve_theme` 辅助、缺 MyST 兼容钩子（YAML 日期加引号 + 重复 H1 去重）、缺 preset 级一键 `build_config` 等 7 类可复用缺口；通过萃取整合将 SIGIL-S 共享库的 5 道门能力下沉到 mystx 第三方发布包，惠及更广泛的 Sphinx 生态用户。
- **Target Users**: ① mystx 主题终端用户（Python ≥3.14，Sphinx ≥7）；② mystx 仓库维护者（独立 Git 项目，`pyproject.toml` 由 scikit-build-core 构建）；③ SpecWeave 内部项目（awesome-okf-xs 等）作为上游消费者。

## Goals
- **G1（萃取层）**：从 `lib/sphinx_config` 中精确识别 **6 个与 OKF/awesome-okf-xs 无业务耦合**的纯工具子模块，迁移到 mystx `src/mystx/` 下独立子包，保持 API 向后兼容 100%。
- **G2（层间整合）**：mystx 现有的 `config.py`（ConfigManager/theme_options_merge）、`theme.py`（MySTX dataclass）、`version_switcher.py` 与新萃取子模块无逻辑冲突；用萃取的 `deep_merge` 替代手写 `_merge_html_theme_options`。
- **G3（注册与启用）**：新萃取模块以 `mystx` Sphinx extension 的 setup 流程自动注册钩子和默认配置；当用户 `extensions += ["mystx"]` 时，无需额外代码即可获得 MyST 兼容保护。
- **G4（SIGIL-S 下沉）**：萃取后的 mystx 代码严格遵循 SIGIL-S 5 道门：Stable API（`__all__`）/ Intact Types（PEP 695 泛型）/ Gateway（mystx `__init__.py` re-export）/ Integration Tests（≥15 条 pytest）/ License（MIT 保持一致）。
- **G5（上游对齐）**：SpecWeave 侧 `lib/sphinx_config` 保留不删；如 mystx 侧修 bug，同步机制为"在 mystx 独立 PR 合入后，由维护者 cherry-pick 回 SpecWeave"，单次修改最多 2 处（非强制镜像）。

## Non-Goals (Out of Scope)
- 不迁移 `lib/sphinx_config/presets/okf_docs.py`（含 awesome-okf-xs 专属 intersphinx 三映射 + GitHub Pages repo→site_url 推断，属于 OKF 域特定）。
- 不迁移 `ensure_lib_on_syspath`（SpecWeave `.agents/scripts` 自举专用，mystx 是 pip-installable 包，sys.path 由 setuptools/PEP 420 处理）。
- 不改变 mystx 的 scikit-build-core 构建系统与 `pyproject.toml` 版本号（`0.3.6` 保持；萃取内容只增加 API，不删除现有接口）。
- 不做 JSON frontmatter 支持（YAGNI 永久否决项，与上游 sphinx_config I-8 一致）。
- 不在本次迁移中新增 mystx 主题 CSS / HTML 模板 / JS 交互修改（纯配置 & 工具层）。
- 不引入 `myst-nb` 作为硬依赖（保持当前 optional-dependencies 语义不变）。

## Background & Context
- 上游现状：SpecWeave `.agents/scripts/lib/sphinx_config` 源自 `projects/awesome-okf-xs/doc/conf.py` 萃取，经 dd0c49a8f→f983f8d3b→c349c695c→Batch-0~3 共 7 commits 迭代，已完成 SIGIL-S 5 道门（Gateway 登记于 [README.md](file:///d:/spaces/SpecWeave/.agents/scripts/lib/README.md#L16-L30)、Integration Tests 38 条 100% PASS）。
- 下游现状：`playground/books/libs/mystx/` 是 **独立 Git 仓库**（非 submodule，已 clone 到 playground/books/libs/ 下进行本地开发），拥有 `src/mystx/__init__.py`、`config.py`、`theme.py`、`version_switcher.py`，入口 `setup(app)` 目前只做 3 件事：`_setup_myst_nb(optional)` + `MySTX(app)` 注册主题 + `config-inited → config_inited_handler`；无 MyST date/H1 兼容钩子、无扩展优先级队列、无主题优先级队列、手写的浅合并 theme options。
- 技术约束：Python ≥3.14（PEP 649 默认延迟注解，禁止 `from __future__ import annotations`）；Sphinx ≥7 钩子 API 不变；`myst_parser` 为 mystx 的硬依赖（被 `myst-nb` 通过 optional-dependency 引入，但 pure 主题用户未必安装——本次萃取后将 `myst_parser` 提升为 mystx 硬依赖？见 Open Question Q1）。
- 已萃取的 PRESET-SETUP L1.5 模式（见 [preset-setup-closure-generator.md](file:///d:/spaces/SpecWeave/docs/retrospective/patterns/code-patterns/preset-setup-closure-generator.md)）将在 mystx 侧应用为 `mystx.presets` 子包，提供 `build_minimal_myst_config` 与未来更多预设。

## Functional Requirements
- **FR-1（工具函数子包 `mystx.utils`）**：迁移 `deep_merge`、`has_module` 两个纯函数，保持调用签名与返回类型 100% 不变，`deep_merge` 必须保留 `remove_marker=None` 语义。
- **FR-2（配置子包 `mystx.configs` 或等价命名）**：迁移 4 个 DEFAULT_* 常量字典 + `build_base_config` + `_resolve_html_baseurl`，但移除 `DEFAULT_EXT_CONFIG` 中含 `tippy/mermaid/contributors/sphinx_sitemap` 的 OKF 专属配置（只保留 Sphinx 通用项，或通过 `factory=lambda:` 允许覆盖）。
- **FR-3（扩展加载层 `mystx.extensions`）**：迁移 `resolve_extensions(req/opt/cond)`、`DEFAULT_OPTIONAL_EXTENSIONS`（裁剪到 mystx 声明的 optional-dependencies 中存在的 8 个）、`DEFAULT_CONDITIONAL`（保留 `_sitemap_conditional`，但将其 has_module 检查绑定到 mystx `[doc]` optional 键）。
- **FR-4（主题优先级层 `mystx.themes`）**：迁移 `resolve_theme(extra_before, priority, extra_after)` + `DEFAULT_BOOK_THEME_OPTIONS` + `resolve_theme_options(theme, override, book_defaults)`；`DEFAULT_THEME_PRIORITY` 默认值首位从 "mystx" 开始（避免上游 sphinx_config 的默认 mystx 排首位导致找不到的 OKF 特定行为）。
- **FR-5（MyST 兼容钩子 `mystx.myst_compat`）**：完整迁移两个 Sphinx 钩子 `quote_frontmatter_dates` + `dedupe_injected_h1` + `register_hooks(app)`；环境变量前缀从 `SW_MYST_COMPAT_*` 改为 `MYSTX_MYST_COMPAT_*`（但保留 SW_ 作为 alias 3 个版本，见 AC-4）。
- **FR-6（mystx `setup()` 自动注册）**：在 `src/mystx/__init__.py` 现有 `setup(app)` 中追加 3 件事：① `from .myst_compat import register_hooks; register_hooks(app)`；② 若用户 `extensions` 未显式加载 `myst_parser`，静默注入并 warn；③ 用 `mystx.utils.deep_merge` 重写 `ConfigManager._merge_html_theme_options`，保证嵌套递归合并 + None 删除语义。
- **FR-7（Presets 子包 `mystx.presets`）**：迁移 `presets/_shared.py`（两生成器 `build_project_meta / build_setup_closure`）+ `presets/minimal_myst.py`（`build_minimal_myst_config`），保持 PRESET-SETUP L1.5 模式一致；`presets/__init__.py` 带 module docstring + `__all__`。
- **FR-8（Gateway re-export）**：`mystx/__init__.py` 中新增 re-export，所有对外 API 经 `__all__` 显式列出（不暴露内部 `_utils / _shared` 单下划线模块名）。

## Non-Functional Requirements
- **NFR-1（类型完整）**：新萃取模块的所有公共函数/常量必须有 PEP 695 类型注解，禁止裸 `dict` / 裸 `Callable`；对 Sphinx / docutils 类型以字符串前向引用（`app: "Sphinx"` / `doctree: "nodes.document"`），不新增顶层 import。
- **NFR-2（零破坏性变更）**：不删除、不重命名 `mystx` 当前已有的类/函数（`ConfigManager`, `MySTX`, `config_inited_handler`, `version_switcher_setup`, `_setup_myst_nb` 等保持不变；允许在原方法内部切换底层实现）。
- **NFR-3（pytest 覆盖率 ≥ 80%，新增测试 ≥ 15 条）**：`tests/unit/` 目录新增 `test_utils.py`（≥4）、`test_myst_compat.py`（≥5）、`test_presets.py`（≥3）、`test_ext_themes.py`（≥3）共 ≥15 条用例，在 mystx 根目录 `pytest tests/unit/ -q` 全 PASS。
- **NFR-4（PEP 649 合规）**：整个 mystx `src/mystx/` 包残留 `from __future__ import annotations` 数量为 0（如现存立即去掉）。
- **NFR-5（License 兼容）**：所有新文件顶行携带与 mystx 其他源文件一致的 MIT License 文件头（如原有文件存在，则保持一致即可），文件顶部 SPDX tag 可选。
- **NFR-6（源路径 ≤ 500 行/文件）**：新子模块不得超过 500 行；若超过按 SRP 拆分。
- **NFR-7（无 SpecWeave 引用）**：迁移后的 mystx 源文件 **不得出现** 字符串 "SpecWeave" / ".agents/scripts"，`ensure_lib_on_syspath` 与 `SW_* 自举常量` 不在迁移之列。

## Constraints
- **Technical**：Python ≥3.14；Sphinx ≥7（`app.connect` priority kwarg 存在）；myst-parser ≥ 4.x（含 `source-read / doctree-read` 事件）；构建系统锁定 scikit-build-core ≥ 0.12（不切 hatch / pdm）。
- **Business**：mystx `version = "0.3.6"` 不得在本次迁移中 bump（维护者后续择机 bump 到 0.4.0 并单独发版）；所有 `[doc]` optional-dependency 键名保持不变。
- **Dependencies**：不新增除必需外的第三方运行时依赖；测试时可加 `pytest`（若 mystx 缺此依赖，只在 test requirements 中加，不进运行时 deps）。
- **流程**：因目标项目是独立 Git 仓库（非 submodule），迁移完成后所有提交必须落在 `playground/books/libs/mystx/` 其自身的 Git 历史链（或 playground 根仓库 history 由维护者选择；实现任务中禁止用 SpecWeave 根仓库 `git add mystx/`）。

## Assumptions
- ① 当前 mystx 的 optional-dependency `[doc]` 已经覆盖迁移所需核心扩展（`myst-parser`, `sphinx-book-theme`, `sphinx-copybutton`, `sphinx-design`, `sphinx-sitemap`, `sphinxext-opengraph`, `sphinx-tippy`, `sphinx-contributors`, `sphinxcontrib-mermaid`）——比对 OKF DEFAULT_OPTIONAL_EXTENSIONS 存在 9/10 的对应关系，缺失 `sphinx.ext.intersphinx / sphinx.ext.extlinks / sphinx.ext.graphviz` 为 Sphinx 内置扩展，不影响。
- ② Python 3.14 PEP 649 延迟注解求值已默认开启（这是 project_memory 中用户 profile 的既定工程约定）。
- ③ `mystx.doc/_config.toml` 合并到 Sphinx 的现有 `config_inited_handler` 与新 FR-6 不冲突（同一事件上两个 handler 顺序由优先级控制）。
- ④ 独立 mystx 仓库维护者允许在 playground 本地做开发性修改（即使是 untracked 的本地文件修改）。
- ⑤ 用户使用 mystx 时主要通过 `extensions = ["mystx"]` 或 `html_theme = "mystx"` 两种路径；两种路径下 FR-5 的 MyST 兼容钩子都必须生效。

## Acceptance Criteria

### AC-1: 工具函数萃取可 import
- **Given**: 安装 mystx 的 Python 环境（≥3.14）
- **When**: 执行 `from mystx.utils import deep_merge, has_module`
- **Then**: ① 不抛 ImportError；② 调用 `deep_merge({"a":{"b":1}}, {"a":{"c":2}})` 返回 `{"a":{"b":1,"c":2}}`（嵌套递归合并）；③ `has_module("myst_parser")` 当且仅当安装时返回 True
- **Verification**: `programmatic`（pytest test_utils.py ≥4 条）

### AC-2: deep_merge 替换手写合并无行为回归
- **Given**: Sphinx app 使用 `ConfigManager`，自定义 `_config.toml[html_theme_options]` 嵌套二级（如 `icon_links` 内 dict 列表）
- **When**: `config-inited` 事件触发 `apply_config()`
- **Then**: ① 配置被合并的层数 ≥2 均生效；② `remove_marker=None` 语义生效（toml 中显式写 `key = null` 表示删除 base 的 key）
- **Verification**: `programmatic`（unit test + doc 构建 smoke）

### AC-3: MyST 兼容钩子自动生效
- **Given**: `extensions = ["mystx"]` 的 Sphinx 构建；Markdown 文件含 YAML frontmatter `date: 2026-09-03` 且正文第一句为 `# Title`（H1），frontmatter 亦含 `title: Title`
- **When**: `sphinx-build -b html` 完成
- **Then**: ① `json.dumps` frontmatter 不抛 `date is not JSON serializable`（quote_frontmatter_dates 生效）；② 文档顶级 section 只有 1 个（`dedupe_injected_h1` 生效）；③ 两种钩子均可通过 `MYSTX_MYST_COMPAT_*=0` 环境变量关闭
- **Verification**: `programmatic`（pytest test_myst_compat ≥5 条 + 环境变量 reload）

### AC-4: 环境变量前缀向后兼容
- **Given**: 设置 `SW_MYST_COMPAT_QUOTE_DATES=0`（旧 SpecWeave 前缀）
- **When**: 运行 `register_hooks(app)` 时判断开关
- **Then**: 旧前缀依然生效（与新 `MYSTX_*` 等价），并在日志中以 `logger.info` 记录 "Deprecated: use MYSTX_* instead"；迁移完成后保留 ≥3 个 mystx minor 版本（至少至 0.6.x）
- **Verification**: `programmatic`（环境变量 monkeypatch + caplog 断言）

### AC-5: resolve_theme 主题优先级队列包含 mystx
- **Given**: 环境不装 `sphinx_book_theme`，装了 `mystx`（本包）和 Sphinx（alabaster 内置）
- **When**: `from mystx.themes import resolve_theme; resolve_theme()`
- **Then**: 返回值 == `"mystx"`；`extra_before=["my_theme"]` 插入成功；alabaster 始终在队尾保底
- **Verification**: `programmatic`（test_ext_themes.py）

### AC-6: resolve_extensions 三类列表行为不变
- **Given**: required=("myst_parser",)，optional=("sphinx_copybutton",) 未安装，conditional 为空
- **When**: `from mystx.extensions import resolve_extensions; lst = resolve_extensions(required, optional, conditional)`
- **Then**: ① `myst_parser` 在返回列表且排第 1；② `sphinx_copybutton` 未安装时被静默跳过（无 ImportError）；③ required 缺模块时抛 ImportError 消息含 `[mystx.extensions] required extension missing:` 前缀
- **Verification**: `programmatic`

### AC-7: Presets 子包可用且 PRESET-SETUP 模式一致
- **Given**: Python 环境装 mystx
- **When**: `from mystx.presets import build_minimal_myst_config; conf = build_minimal_myst_config({"project":"Hello","author":"Me"})`
- **Then**: ① 返回 dict 包含 `project="Hello"`、`author="Me"`、`html_theme` 走 resolve_theme 保底；② `conf["extensions"]` 包含 `myst_parser` 至少 1 项；③ 返回值 `conf["setup"](app FakeApp)` 会按 register_fns → user_setup 的顺序执行
- **Verification**: `programmatic`（test_presets.py ≥3 条 + 白名单键断言 `projecT not in meta`）

### AC-8: Gateway re-export 显式经 `__all__`
- **Given**: `import mystx`
- **When**: `dir(mystx)` 枚举
- **Then**: 至少包含 `deep_merge, has_module, resolve_theme, resolve_theme_options, resolve_extensions, register_myst_compat_hooks, build_minimal_myst_config`（别名允许），且 `hasattr(mystx, "__all__")` == True，所有 re-export 名被包含；`_utils / _shared` 不对外可见
- **Verification**: `programmatic` + `human-judgment`（代码审查 `mystx/__init__.py` 导出清单是否合理）

### AC-9: 全部新增单元测试通过 ≥15 条
- **Given**: 在 `playground/books/libs/mystx/` 根目录
- **When**: `pytest tests/unit -q`
- **Then**: exit code 0，passed count ≥15，无 skip/xfail 超过 2 条
- **Verification**: `programmatic`

### AC-10: 无 SpecWeave 私有引用残留
- **Given**: 所有 `src/mystx/**/*.py` 文件
- **When**: 全文 grep 字符串 "SpecWeave" / ".agents/scripts" / "lib/sphinx_config"
- **Then**: 匹配数为 0；`ensure_lib_on_syspath` 函数未被迁移
- **Verification**: `programmatic`（grep 退出码 1 表示无匹配即为通过）

### AC-11: 保持 `mystx` 当前入口无破坏性变更
- **Given**: 一个原使用 mystx 0.3.6 纯主题（不含 presets/hooks）的用户
- **When**: `import mystx; from mystx.theme import MySTX; from mystx.config import ConfigManager; from mystx.version_switcher import sphinx_setup`
- **Then**: ① 三个 import 全成功；② `ConfigManager._merge_html_theme_options` 仍可调用（只是底层换了 deep_merge，AC-2 已保无回归）；③ 入口 `setup(app)` 返回仍是 dict，键 `parallel_read_safe/parallel_write_safe` 保持 True
- **Verification**: `programmatic`（import smoke test + 返回值 schema 验证）

## Open Questions
- [ ] **Q1 (HARD DEP DECISION)**: `myst_parser` 是否应从 mystx `[doc]` optional 升级为 `[project].dependencies` 硬依赖？当前 mystx 的 setup 中 `_setup_myst_nb` 只在装了 myst_nb 时执行，但 pure theme 用户若只用 RST，可能并不希望被强装 myst_parser。**当前默认假设**：保持 optional 不变，在 FR-6 ② 中仅 logger.warn 不强制。
- [ ] **Q2 (DEFAULT_MYST_CONFIG COPY)**: 迁移到 mystx 的 4 个 DEFAULT_* 常量是否允许用户在 `setup()` 时注入覆盖？（例如 `setup(app, overrides: Mapping | None = None)` 扩展参数，Sphinx 扩展允许额外 kwargs）。**当前默认假设**：允许，但仅做 minimal MVP，不设计跨扩展合并策略。
