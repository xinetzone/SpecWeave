# Sphinx Config → mystx 模块萃取与整合 — Implementation Plan (Decomposed Task List)

> 任务分区：7 个高优 + 2 个中优 = 9 Tasks。执行顺序严格按 DAG 依赖：T0 → T1/T2/T3/T4 并行 → T5/T6 → T7/T8。
> 子代理委托要求：每个 Task 完成后必须跑通自身的 programmatic Test Requirements 才能标记完成，不得留未 PASS 的用例交给后续 Task。

## [x] Task 0：前期侦查与基线测试 —— 建立萃取前状态快照
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 `playground/books/libs/mystx/` 独立 Git 仓库中执行 `git status --short` 记录初始 untracked / unstaged（禁止把 mystx 当 SpecWeave 子仓 add）。
  - 阅读 `mystx/src/mystx/config.py`、`theme.py`、`version_switcher.py`、`__init__.py` 剩余全文（已读部分限 config:L100、theme:L60、version:L50；补到尾行并标记后续改造 touch 点清单）。
  - 检查 `src/mystx/**/*.py` 中 `from __future__ import annotations` 残存量；若 >0 记为 T1 前置清理项。
  - `pip install -e .[doc,dev]`（Python 3.14 环境）执行 `mystx/doc/` 最小构建 smoke 一次，记录 exit code（萃取前基线）。
- **Acceptance Criteria Addressed**: AC-2 / AC-4 / AC-11（前置基线的可验证前提）
- **Test Requirements**:
  - `programmatic` TR-0.1: `grep -rc "from __future__ import annotations" src/mystx/` 报告实际数量并输出路径清单
  - `programmatic` TR-0.2: `git status --short playground/books/libs/mystx -- ':(exclude)*.git/*'` → 将快照写入 `_temp/mystx-pre-extract-status.txt`（用于 T9 比对残留）
  - `programmatic` TR-0.3: `cd playground/books/libs/mystx ; sphinx-build -b html doc doc/_build/html -W --keep-going 2>&1 | tail -20`（允许失败但要 exit code 0/非0 都记快照）
- **Notes**: 侦查结果写入 checklist.md 的参考备注（不要改 spec.md）；禁止在 T0 改代码。

## [x] Task 1：萃取工具层 mystx.utils —— deep_merge + has_module
- **Priority**: high
- **Depends On**: T0
- **Description**:
  - 新建 `src/mystx/utils.py`（或子包 `src/mystx/_internal/utils.py` + `utils.py` re-export，按 SIGIL-S Stable API 要求对外模块名无下划线）。
  - 从 `lib/sphinx_config/_utils.py` 拷贝两个函数 **保留注释但替换字符串 "sphinx_config" → "mystx"**；ImportError/ModuleNotFoundError 异常捕获保持不变。
  - 类型注解：`deep_merge(base: dict[str, Any], override: dict[str, Any] | None = None, *, remove_marker: Any = None) -> dict[str, Any]`；禁止裸 dict。
  - 在 `mystx/__init__.py` 通过 `from .utils import deep_merge, has_module` 并加入 `__all__`。
  - 如果 T0 中发现 `from __future__ import annotations` > 0，在此 Task 一并清除。
- **Acceptance Criteria Addressed**: AC-1 / AC-8 / AC-10 / NFR-1 / NFR-4
- **Test Requirements**:
  - `programmatic` TR-1.1: `from mystx.utils import deep_merge, has_module` 运行不抛
  - `programmatic` TR-1.2: `deep_merge({"a":{"b":1}}, {"a":{"c":2}})` == `{"a":{"b":1,"c":2}}`（嵌套 2 层）
  - `programmatic` TR-1.3: `deep_merge({"a":1,"b":2},{"b":None,"c":3})` == `{"a":1,"c":3}`（None 删除语义 + 旧键删 + 新键增）
  - `programmatic` TR-1.4: `has_module("myst_parser")` 类型 bool，与 `importlib.util.find_spec()` 返回一致（可在测试里比对）
  - `programmatic` TR-1.5: `dir(mystx)` 含 `deep_merge, has_module` 且无 `_utils` 可见
  - `human-judgement` TR-1.6: 代码审查 `src/mystx/utils.py` 顶不含 "SpecWeave" ".agents/scripts" 字符串（AC-10）

## [x] Task 2：萃取配置层 mystx.configs —— 4 DEFAULT_* + build_base_config（裁剪 OKF 专属）
- **Priority**: high
- **Depends On**: T1（依赖 deep_merge）
- **Description**:
  - 新建 `src/mystx/configs.py`：迁移 `DEFAULT_MYST_CONFIG / DEFAULT_BUILD_CONFIG / DEFAULT_EXT_CONFIG / DEFAULT_HTML_CONFIG` + `build_base_config` + `_resolve_html_baseurl`。
  - **OKF 裁剪**：`DEFAULT_EXT_CONFIG` 去掉所有 `tippy_* / sitemap_locales / ogp_social_cards / mermaid_*` 等非 mystx 默认硬值（保留空 dict 默认键 `extlinks` + `copybutton_exclude / copybutton_selector` 仅当 copybutton 是 [doc] optional；找不到的键置 `{}` 空占位，不在 mystx 侧强制写入 value）。
  - `build_base_config(params=None)` 不注入 `intersphinx_mapping`（原 awesome-okf-xs 专属）；保留 html_baseurl / ogp_site_url 基础推断逻辑即可。
  - Gateway：`mystx/__init__.py` re-export `DEFAULT_MYST_CONFIG / DEFAULT_BUILD_CONFIG / DEFAULT_EXT_CONFIG / DEFAULT_HTML_CONFIG / build_base_config`；`_resolve_html_baseurl` **不** 对外 export。
  - 所有常量 `dict[str, Any]` 全泛型化；禁止裸 dict。
- **Acceptance Criteria Addressed**: AC-11 / NFR-1 / G1（与 OKF 特定 decouple）
- **Test Requirements**:
  - `programmatic` TR-2.1: `from mystx.configs import build_base_config, DEFAULT_BUILD_CONFIG` 成功
  - `programmatic` TR-2.2: `build_base_config()["myst_enable_extensions"]` 包含 "dollarmath" / "deflist" / "colon_fence"（至少 3 项，来自 DEFAULT_MYST_CONFIG）
  - `programmatic` TR-2.3: `build_base_config({"config_override": {"numfig": False}})["numfig"]` → False（deep_merge override 生效）
  - `programmatic` TR-2.4: `set(DEFAULT_EXT_CONFIG.keys()) & {"tippy_rtd_urls", "mermaid_version", "ogp_social_cards"}` 为空集（OKF 关键被裁剪）
  - `human-judgement` TR-2.5: 人工核对 `DEFAULT_EXT_CONFIG` 剩余键是否都是 mystx 用户纯主题配置项

## [x] Task 3：萃取扩展层 + 主题层 —— mystx.extensions / mystx.themes
- **Priority**: high
- **Depends On**: T1（依赖 has_module）
- **Description**:
  - 新建 `src/mystx/extensions.py`：拷贝 `resolve_extensions(required, optional, conditional)` + `DEFAULT_OPTIONAL_EXTENSIONS`（仅保留 `mystx pyproject.toml [doc] optional-dependencies` 存在的条目，缺的在注释中标"非 mystx optional，已移除以避免 has_module 误判"）+ `DEFAULT_CONDITIONAL`（仅保留 `_sitemap_conditional`，错误前缀 `[sphinx_config]` 改为 `[mystx.extensions]`）。
  - 新建 `src/mystx/themes.py`：拷贝 `DEFAULT_BOOK_THEME_OPTIONS` + `resolve_theme(extra_before, priority, extra_after)` + `resolve_theme_options(theme, override, book_defaults)`。
    - `DEFAULT_THEME_PRIORITY` 默认首位由 "mystx" 开始，顺序：`mystx → sphinx_book_theme → alabaster`（和上游一致，但保证队首是本包）。
    - `resolve_theme_options` 对 `theme == "mystx"` 返回 `book_defaults`（与 sphinx_book_theme 同等处理）。
  - Gateway re-export：`mystx/__init__.py` 加入 `resolve_extensions, DEFAULT_OPTIONAL_EXTENSIONS, DEFAULT_CONDITIONAL, resolve_theme, DEFAULT_THEME_PRIORITY, DEFAULT_BOOK_THEME_OPTIONS, resolve_theme_options`；类型签名 Callable 参数化 `Callable[[], bool]`。
- **Acceptance Criteria Addressed**: AC-5 / AC-6 / AC-8 / NFR-1
- **Test Requirements**:
  - `programmatic` TR-3.1: `resolve_theme()` 返回 == "mystx"（环境装了 mystx 自身）
  - `programmatic` TR-3.2: `resolve_theme(extra_before=["not_exist_theme"])` → 返回仍 "mystx"（extra_before has_module 失败跳过）
  - `programmatic` TR-3.3: `resolve_extensions(required=("__no_such_mod__",))` 抛 ImportError，消息含前缀 `[mystx.extensions]`
  - `programmatic` TR-3.4: `resolve_theme_options("mystx", override={"path_to_docs": "docs"})["path_to_docs"]` == "docs"
  - `programmatic` TR-3.5: `len(resolve_extensions(required=("myst_parser",), optional=("sphinx_copybutton","__absent__")))` ∈ {1, 2}（按 copybutton 装/未装都合法）

## [x] Task 4：萃取 mystx.myst_compat —— 双钩子 + register_hooks（环境变量前缀重写 + SW alias）
- **Priority**: high
- **Depends On**: T1（无直接 import 依赖，但按 DAG 顺序同步完成）
- **Description**:
  - 新建 `src/mystx/myst_compat.py`：完整拷贝 `quote_frontmatter_dates / dedupe_injected_h1 / register_hooks` + 正则 + 常量。
  - **重命名**：环境变量前缀 `SW_MYST_COMPAT_*` → `MYSTX_MYST_COMPAT_*`；但保留 SW_ 前缀读取 alias：
    - 读取逻辑改为：先看 `MYSTX_*`；若未设置再回退看 `SW_MYST_COMPAT_*`；若回退命中，`logger.info("Deprecated MYSTX_* alias SW_ used, will be removed in >=0.7")`
  - 补完整签名（app: "Sphinx", doctree: "nodes.document", source: list[str], docname: str）
  - `register_hooks` 中 `priority=400` 保持不变（< TocTreeCollector 默认 500）。
  - Gateway export：`mystx/__init__.py` 暴露 `register_myst_compat_hooks(app)`（别名指向内部 `register_hooks`；原命名避免与下游 `register_hooks` 太泛冲突）。
- **Acceptance Criteria Addressed**: AC-3 / AC-4 / AC-10 / NFR-1
- **Test Requirements**:
  - `programmatic` TR-4.1: 构造 YAML FM `date: 2026-09-03` → 经过 hook 后 source[0] 含 `date: "2026-09-03"`
  - `programmatic` TR-4.2: TOML FM `+++ date = 2026-09-03 +++` → 经过 hook 后 source[0] **不变**（不修改 TOML）
  - `programmatic` TR-4.3: FakeDoctree 2 sections，首 section 仅 1 个 children → dedupe 后仅剩 section[1]
  - `programmatic` TR-4.4: `monkeypatch.setenv("MYSTX_MYST_COMPAT_QUOTE_DATES", "0")` → hook 立刻 no-op（需要 `_reload_env_settings()` 函数提供给测试刷新）
  - `programmatic` TR-4.5: `monkeypatch.delenv(..., raising=False); monkeypatch.setenv("SW_MYST_COMPAT_DEDUPE_H1", "0")` → hook 关闭且 caplog 有 Deprecated 字样（AC-4）

## [x] Task 5：萃取 presets 子包 + PRESET-SETUP 模式落地（_shared 生成器 + minimal_myst）
- **Priority**: high
- **Depends On**: T1 / T2 / T3（依赖 utils / configs / extensions / themes 已就位）
- **Description**:
  - 新建 `src/mystx/presets/` 目录，含：`__init__.py`（module docstring + `build_minimal_myst_config` re-export + `__all__`）、`_shared.py`（`build_project_meta(key_defaults=COMMON_KEY_DEFAULTS)` + `build_setup_closure(register_fns, user_setup)`，9 键白名单 + 严格注册顺序 + PRESET-SETUP 模式迁移）、`minimal_myst.py`（用生成器替代 15 行 copy，和上游一致）。
  - **OKF 裁剪**：不迁移 `okf_docs.py`（Non-Goal，已在 PRD 声明）。
  - Gateway export：`mystx/__init__.py` 加入 `build_minimal_myst_config` + `mystx.presets` 可 `from mystx import presets`（是否需要？：是，`__init__.py` 顶部显式 `from . import presets; __all__ += ["presets"]`）。
- **Acceptance Criteria Addressed**: AC-7 / AC-8 / G3
- **Test Requirements**:
  - `programmatic` TR-5.1: `from mystx.presets import build_minimal_myst_config` + `from mystx import build_minimal_myst_config as alt` 两个路径都成功且同一对象（或等价）
  - `programmatic` TR-5.2: `conf = build_minimal_myst_config({"project":"t","author":"a"}); conf["project"] == "t"`；白名单外键 `"projecT":"x"` 被忽略（不在 result key 集合内）
  - `programmatic` TR-5.3: 自定义 user_setup 与 register_fns 执行顺序严格：`[reg_a, reg_b, user]`（按 PRESET-SETUP 模式的迁移断言 4 条中第 2 条）
  - `programmatic` TR-5.4: `conf.get("html_theme")` 非空；`conf["extensions"][:1]` == `["myst_parser"]`

## [x] Task 6：整合 mystx.setup() 自动注册 + ConfigManager 切换 deep_merge
- **Priority**: high
- **Depends On**: T4（myst_compat 就绪）/ T1（deep_merge）/ T5（presets 就绪）
- **Description**:
  - **改造 `mystx/__init__.py` 的 `setup(app)`**：
    1. 追加：`register_myst_compat_hooks(app)`（FR-6①）
    2. 追加：若 `"myst_parser"` 不在初始 extensions list → `app.setup_extension("myst_parser")` or `app.add_post_transform` 等同效（优先 `app.setup_extension`）；`logger.warn("myst_parser not loaded; mystx auto-injecting.")` 记录（FR-6②）
    3. 返回 dict 保持 `{"parallel_read_safe": True, "parallel_write_safe": True}`（AC-11）
  - **改造 `config.py` 的 `ConfigManager._merge_html_theme_options`**：内部切换使用 `mystx.utils.deep_merge` 递归合并；保留外层 if 判断逻辑（仅实现替换，接口不变）。同时新增对 `None` = 删除 base 键的支持（如果原手写合并未支持的话）。
  - **保证入口零破坏性**：`ConfigManager / MySTX / version_switcher_setup / _setup_myst_nb` 4 个对象的公开签名不变。
- **Acceptance Criteria Addressed**: AC-2 / AC-3 / AC-11 / NFR-2 / FR-6
- **Test Requirements**:
  - `programmatic` TR-6.1: 构造 FakeApp 跑 `setup(FakeApp)`，断言 `register_hooks` 被调用 1 次（或 hooks list 长度 +2 项：source-read / doctree-read）
  - `programmatic` TR-6.2: FakeApp 初始 extensions 无 myst_parser → setup 后 extensions 新增 myst_parser（并捕获 logger.warn）
  - `programmatic` TR-6.3: ConfigManager + custom _config.toml 二级嵌套（模拟 icon_links 列表 + dict）→ 实际合并后 base 键保留，override 的嵌套 dict 键被 recursively merge
  - `programmatic` TR-6.4: `hasattr(mystx.ConfigManager, "_merge_html_theme_options")` True / 返回值不抛（接口存在性）

## [x] Task 7：单元测试文件落盘 —— 4 文件 ≥15 条 pytest（SIGIL-S I 门）
- **Priority**: medium
- **Depends On**: T1~T6 均完成（但可与 T6 并行写文件，最后再统一跑 pytest）
- **Description**:
  - `mystx/tests/unit/`（如果 mystx 已有 tests/unit；否则在根 `tests/unit/`，按已存在的 tests 结构）创建 `test_utils.py（≥4）` / `test_myst_compat.py（≥5）` / `test_presets.py（≥3）` / `test_ext_themes.py（≥3）`，共 ≥15 条。
  - 复用 SpecWeave `test_sphinx_config/` 的用例结构（FakeDoctree / _reload_env_settings / monkeypatch finally 清 env），但**代码迁移时去除 lib.sphinx_config 引用改为 mystx.\***。
  - pytest 根目录配置：若 mystx 缺 `pytest.ini / pyproject.toml [tool.pytest.ini_options]`，仅在 pyproject.toml 增加 `[tool.pytest.ini_options] testpaths = ["tests/unit"]`（如 mystx 已有 conftest，不破坏现有 testpaths）。
- **Acceptance Criteria Addressed**: AC-9 / NFR-3 / G4
- **Test Requirements**:
  - `programmatic` TR-7.1: 在 mystx 根 `pytest tests/unit -q --tb=short` exit 0
  - `programmatic` TR-7.2: passed count ≥ 15
  - `programmatic` TR-7.3: skipped + xfailed count ≤ 2（不允许大面积 mark skip）
  - `human-judgement` TR-7.4: 审查测试文件没有对 `.agents/scripts`、`lib.sphinx_config` 的 import（AC-10 防线最终落盘）

## [x] Task 8：最终集成验证 & SpecWeave-私有引用 grep 扫描（AC-10 / AC-11 闭环）
- **Priority**: medium
- **Depends On**: T7
- **Description**:
  - `AC-10`：执行 `rg -n "SpecWeave|\.agents/scripts|lib/sphinx_config" playground/books/libs/mystx/src/mystx --glob '*.py'`，要求 exit 1（无匹配）。
  - `AC-11`：写 `tests/unit/test_entrypoints.py`（2 条）做 import smoke：`from mystx.theme import MySTX; from mystx.config import ConfigManager, config_inited_handler; from mystx.version_switcher import sphinx_setup; from mystx import setup` → 全成功 + setup 返回 dict schema 对。
  - AC-3 端到端：如 T0 的 doc 构建可跑，在 `mystx/doc/` 构建一次（允许 1 warning 但不能 error exit）验证钩子与主题整合实际生效。
  - 更新 tasks.md 所有 checkbox 为 [x]；更新 checklist.md 对应项。
- **Acceptance Criteria Addressed**: AC-10 / AC-11 / AC-3
- **Test Requirements**:
  - `programmatic` TR-8.1: ripgrep 无匹配（exit code 1）
  - `programmatic` TR-8.2: 4 条入口 import + setup 返回 schema 验证全 PASS
  - `programmatic` TR-8.3: `pytest tests/unit -q` 最终再次运行仍 exit 0 + passed ≥ 15（确保 T7 的 tests 在 Task 整合后不被破坏）
  - `human-judgement` TR-8.4: 对 checklist.md 逐项人工勾选已验证项

---

**DAG 可视化**（仅依赖关系，高优先跑）：
```
T0 侦查
 ├── T1 utils
 │    ├─ T2 configs
 │    ├─ T3 extensions/themes
 │    ├─ T4 myst_compat
 │    └─────── T5 presets + T6 integrate
 │                 └── T7 tests
 │                      └── T8 final
```
