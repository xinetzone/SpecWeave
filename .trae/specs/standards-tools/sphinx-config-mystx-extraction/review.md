# Sphinx Config → mystx 模块萃取与整合 — Verification Checklist

所有检查点在对应子任务完成后（或 T8 最终阶段）由独立子代理黑箱验证。
检查点顺序与 tasks.md Task 依赖序一致：T0→T1→T2→T3→T4→T5→T6→T7→T8。

- [x] **Checkpoint T0.1**：`playground/books/libs/mystx/` 独立 Git 状态快照已写入（不得使用 SpecWeave 根 git add mystx）
- [x] **Checkpoint T0.2**：已审查 mystx 4 个现存源文件（__init__ / config / theme / version_switcher）并列出改造 touch 点清单
- [x] **Checkpoint T0.3**：`src/mystx/**/*.py` 中 `from __future__ import annotations` 残存量记录，>0 时已在 T1 前清零（PEP 649）

- [x] **Checkpoint T1.1**：`mystx.utils` 可 import：`from mystx.utils import deep_merge, has_module` 无 ImportError
- [x] **Checkpoint T1.2**：deep_merge 通过 4 条核心断言：嵌套/None 删除/新键/原 base 不被就地修改
- [x] **Checkpoint T1.3**：`mystx/__init__.py` 包含 `deep_merge` 和 `has_module` 在 `__all__`，`_utils` 内部模块名不可见
- [x] **Checkpoint T1.4**：AC-10 grep 扫描 T1 新文件：不含 SpecWeave/.agents/scripts/lib.sphinx_config（0 匹配）
- [x] **Checkpoint T1.5**：T0 中发现的 `future annotations` 残留已清零

- [x] **Checkpoint T2.1**：`mystx.configs` 4 DEFAULT_* 常量对外 export，build_base_config 可调用
- [x] **Checkpoint T2.2**：DEFAULT_EXT_CONFIG 已去除 OKF 专属 5 键（tippy*/mermaid*/ogp_social_cards/sitemap_locales）——集合差为空
- [x] **Checkpoint T2.3**：`build_base_config({"config_override":...})` 覆盖生效，嵌套字典合并不丢键
- [x] **Checkpoint T2.4**：所有 dict/Callable 泛型参数完整，静态分析告警 0 条（`mypy --strict` 可忽略无 stub，但裸类型计数 0）

- [x] **Checkpoint T3.1**：`resolve_theme()` 在当前环境返回 `mystx`（已安装主题保底第一命中）
- [x] **Checkpoint T3.2**：`resolve_extensions()` 的错误前缀已改成 `[mystx.extensions]`，不含 `[sphinx_config]`
- [x] **Checkpoint T3.3**：DEFAULT_OPTIONAL_EXTENSIONS 仅保留 mystx `[doc]` optional-dependencies 中真实条目，条目个数与 pyproject 比对一致
- [x] **Checkpoint T3.4**：`resolve_theme_options("mystx", override=...)` 返回 dict，`override` 的值深度合并覆盖 base，非 book_defaults 键不被注入
- [x] **Checkpoint T3.5**：Gateway `mystx/__all__` 暴露 T3 全部 6 个公共符号（`resolve_theme / DEFAULT_THEME_PRIORITY / DEFAULT_BOOK_THEME_OPTIONS / resolve_theme_options / resolve_extensions / DEFAULT_OPTIONAL_EXTENSIONS / DEFAULT_CONDITIONAL`）

- [x] **Checkpoint T4.1**：`quote_frontmatter_dates` 对 YAML FM 补引号，TOML FM 不修改（2 条断言 PASS）
- [x] **Checkpoint T4.2**：`dedupe_injected_h1` 对首 section len(children)<=1 删除，其他情况不删
- [x] **Checkpoint T4.3**：`register_myst_compat_hooks(app)` 注册的事件对：`source-read + doctree-read (priority=400)` 数量正确
- [x] **Checkpoint T4.4**：AC-4 双前缀兼容：`SW_MYST_COMPAT_QUOTE_DATES=0` 生效且 caplog 有 Deprecated 字样
- [x] **Checkpoint T4.5**：测试提供 `_reload_env_settings()` 刷新模块级常量，monkeypatch 后无状态污染（首跑 pytest 全部用例无 FAIL 由 env 泄露导致）

- [x] **Checkpoint T5.1**：PRESET-SETUP 的 `build_project_meta` 白名单 9 键生效，拼错键名 `"projecT":"x"` 静默丢弃（白名单断言）
- [x] **Checkpoint T5.2**：`build_setup_closure([reg_a,reg_b], user_setup)` 执行顺序严格为 reg_a → reg_b → user_setup（顺序断言）
- [x] **Checkpoint T5.3**：`build_minimal_myst_config({"project":"p","author":"a"})` 返回 dict 含 extensions 至少 1 项且首项为 `myst_parser`
- [x] **Checkpoint T5.4**：`mystx.presets.__init__` 有 module docstring 说明 preset 定位（OKF 不迁移 / minimal 轻量），含 `__all__`
- [x] **Checkpoint T5.5**：`from mystx import presets; from mystx import build_minimal_myst_config` 两条路径都成功

- [x] **Checkpoint T6.1**：`setup(FakeApp)` 自动调用 `register_myst_compat_hooks(FakeApp)`（断言钩子已挂）
- [x] **Checkpoint T6.2**：FakeApp 初始 extensions 无 myst_parser 时，setup() 后自动注入并产生 logger.warn（可被 caplog 捕获）
- [x] **Checkpoint T6.3**：`ConfigManager.apply_config()` 的 `_merge_html_theme_options` 底层改用 `deep_merge`，原接口返回值 shape 不变（破坏性变更 0 条）
- [x] **Checkpoint T6.4**：入口返回 schema：`setup(app)` 的 return dict 仍然含 `parallel_read_safe=True, parallel_write_safe=True`（AC-11）
- [x] **Checkpoint T6.5**：`ConfigManager / MySTX / version_switcher_setup / _setup_myst_nb` 四个对外类/函数公共签名与 T0 基线完全一致（通过 `inspect.signature()` diff 0 条）

- [x] **Checkpoint T7.1**：mystx 根目录运行 `pytest tests/unit -q` → exit 0，passed ≥ 15，skipped+xfailed ≤ 2
- [x] **Checkpoint T7.2**：4 个 test_ 文件个数匹配 T7 规定的 `test_utils / test_myst_compat / test_presets / test_ext_themes`，每文件用例数达到最低要求（≥4/≥5/≥3/≥3）
- [x] **Checkpoint T7.3**：所有测试 import 仅引用 `mystx.*`，无 `.agents/scripts/lib.sphinx_config` 导入（grep 0 匹配）
- [x] **Checkpoint T7.4**：测试文件 ≤ 500 行/文件，遵循单文件单职责

- [x] **Checkpoint T8.1**：最终 ripgrep 扫描整个 `src/mystx/**/*.py`（严格 globs）：`SpecWeave|.agents/scripts|lib/sphinx_config|ensure_lib_on_syspath` 0 匹配（AC-10）
- [x] **Checkpoint T8.2**：`tests/unit/test_entrypoints.py` 2 条入口 import + schema 断言 PASS（`MySTX / ConfigManager / config_inited_handler / version_switcher_setup.sphinx_setup` 全部可 import + setup 返回 schema 对）
- [x] **Checkpoint T8.3**：`pytest tests/unit -q` 最终二刷全部通过，passed 数量 ≥ 15（T8 验证不被 T7 后整合破坏）
- [x] **Checkpoint T8.4**：doc 构建 smoke（如 T0 成功过可复用）：sphinx-build 对 mystx/doc/ 执行（非 -W 模式 exit 0；-W 警告来自 AutoAPI 历史 docstring 非本次迁移引入）验证主题与钩子实际生效
- [x] **Checkpoint T8.5**：所有 `tasks.md` 方框已 [x] 化，所有 `review.md` 方框已 [x] 化——100% 完工
