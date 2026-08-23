---
id: "python314-stdlib-wiki-16"
title: "mystx 主题单元测试用例清单（54 项）"
source: "https://docs.python.org/3.14/"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/04-docs-markup-tooling/python314-stdlib-wiki/16-mystx-tests-catalog.toml"
---

# mystx 主题单元测试用例清单（54 项）

> 一句话摘要：本清单完整索引 `mystx` Sphinx 主题（`d:\spaces\SpecWeave\playground\books\libs\mystx`）测试套件的全部 54 项单元测试，按测试文件、被测模块、断言要点与 Spec 要求组织，并给出运行方式与维护约定（命名规范、覆盖率门槛、Python 3.14 特性「诚实记录」原则），作为团队后续维护的索引。

## 一、概览

| 测试文件 | 覆盖模块 | 用例数 | 对应 Spec 要求 |
|---|---|---|---|
| `unit/test_github_cards.py` | `ext/github_readme_stats/*`（指令） | 11 | 指令 URL 构建 / HTML 节点 / `run()` 合法与错误路径 |
| `unit/test_config.py` | `config.py`（配置合并） | 18 | 配置加载 / 合并 / thebe / config-inited |
| `unit/test_theme.py` | `theme.py`（主题解析） | 3 | 主题目录解析 / slots 内存 |
| `unit/test_version_switcher.py` | `version_switcher.py`（版本推断） | 5 | 版本匹配推导 / RTD 资产注入 |
| `unit/test_import_fallback.py` | `__init__.py`（可选依赖） | 4 | myst_nb 惰性加载 |
| `unit/test_python314_features.py` | 跨模块（Python 3.14 新特性） | 13 | annotationlib / field(doc=) / traceback / sys.monitoring |
| **合计** | 全量 `src/mystx` | **54** | 语句覆盖率 97%（基线 ≥80%） |

## 二、运行方式

```bash
# 需先准备依赖：将 sphinx 复制到 _tmp_sphinx（见 run_tests.py）
$env:PYTHONPATH = "_tmp_sphinx;src"
python -m pytest tests --cov=mystx --cov-report=term-missing
```

> 注意：`pytest` 退出码可能因沙箱限制 coverage 写入站点包 `__pycache__` 而为 1，但输出 `54 passed` 即为全部通过；需 HTML 报告可追加 `--cov-report=html`。

## 三、详细用例清单

### 3.1 GitHub Readme Stats 指令（11 项）

文件：`unit/test_github_cards.py`

| 用例 | 被测目标 | 断言要点 |
|---|---|---|
| `test_build_url_basic` | `BaseGitHubCardDirective.build_url` | 常规键值正确拼接进 URL |
| `test_build_url_omit_empty` | `BaseGitHubCardDirective.build_url` | 空值 / None 键被省略 |
| `test_create_image_node_escapes` | `create_image_node` | 生成 `raw` 节点，HTML 属性转义（`A&B` → `A&amp;B`） |
| `test_stats_run` | `GitHubStatsDirective.run` | 返回单节点，username/theme/show_icons/hide 正确 |
| `test_top_langs_run` | `GitHubTopLangsDirective.run` | `api/top-langs`、langs_count 正确 |
| `test_pinned_repo_run` | `GitHubPinnedRepoDirective.run` | `api/pin`、username/repo 正确 |
| `test_pinned_repo_missing_required` | `GitHubPinnedRepoDirective.run` | 缺必填项触发 reporter.error |
| `test_pinned_repo_run_with_link` | `GitHubPinnedRepoDirective.run` | `link` 生成 `<a href>` |
| `test_wakatime_run` | `GitHubWakaTimeDirective.run` | `api/wakatime`、range/hide_* 正确 |
| `test_wakatime_run_custom_domain_and_title` | `GitHubWakaTimeDirective.run` | `api_domain` URL 编码、`custom_title` |
| `test_github_readme_stats_setup_registers_directives` | `setup` | 注册 4 条指令，`parallel_read_safe=True` |

### 3.2 ConfigManager 配置加载与合并（18 项）

文件：`unit/test_config.py`

**加载 `load_custom_config`**

| 用例 | 断言要点 |
|---|---|
| `test_load_custom_config_missing` | 无文件返回 `None` |
| `test_load_custom_config_valid` | 返回解析后字典 |
| `test_load_custom_config_invalid_toml` | 抛 `tomllib.TOMLDecodeError` |
| `test_load_custom_config_non_toml_error` | 非 TOML 异常走 `except Exception` 分支 |

**合并 `_merge_html_theme_options`**

| 用例 | 断言要点 |
|---|---|
| `test_merge_html_theme_options_scalar` | 标量值被写入 |
| `test_merge_html_theme_options_nested` | 嵌套键深度合并、已有键不覆盖 |
| `test_merge_html_theme_options_no_section` | 无 `html_theme_options` 段时无副作用 |
| `test_merge_html_theme_options_creates_missing_attr` | 目标属性缺失时自动创建 |

**应用 `apply_config`**

| 用例 | 断言要点 |
|---|---|
| `test_apply_config` | 有配置时合并成功 |
| `test_apply_config_no_file_returns_early` | 无配置时提前返回 |

**slots 内存优化**

| 用例 | 断言要点 |
|---|---|
| `test_config_manager_no_dict` | 实例无 `__dict__` |
| `test_config_manager_logger_initialized` | `logger` 已初始化 |

**thebe 集成 `thebe_setup`**

| 用例 | 断言要点 |
|---|---|
| `test_thebe_setup_enables_launch_buttons` | 开启 thebe 并 `setup_extension("sphinx_thebe")` |
| `test_thebe_setup_extension_error_swallowed` | `ExtensionError` 被吞掉不抛 |
| `test_thebe_setup_extension_already_present` | 已存在时不重复注册 |

**config-inited 事件 `config_inited_handler`**

| 用例 | 断言要点 |
|---|---|
| `test_config_inited_handler_no_features` | 无特性时不注册扩展 |
| `test_config_inited_handler_thebe_enabled` | `use_thebe=True` 时启动 thebe |
| `test_config_inited_handler_handler_error_propagates` | 运行时异常向上传播 |

### 3.3 MySTX 主题解析（3 项）

文件：`unit/test_theme.py`

| 用例 | 断言要点 |
|---|---|
| `test_mystx_resolves_theme_dir` | 解析到 `.../theme/mystx` 并注册 |
| `test_mystx_no_dict` | slots 启用，无 `__dict__` |
| `test_mystx_missing_theme_dir` | 目录不存在抛 `FileNotFoundError` |

### 3.4 版本切换器（5 项）

文件：`unit/test_version_switcher.py`

| 用例 | 断言要点 |
|---|---|
| `test_infer_stable_release` | 稳定版匹配 `v1.2.3` |
| `test_infer_dev_marker` | `.dev1` 匹配 `dev`，json_url 指向本地 |
| `test_stable_readthedocs_version` | RTD `stable` 仍匹配 `v1.2.3` |
| `test_primary_sidebar_end` | 注入 `version-switcher` 组件 |
| `test_inject_rtd_assets_in_local_development` | 本地开发注入 RTD CSS / JS |

### 3.5 可选依赖 `myst_nb` 加载（4 项）

文件：`unit/test_import_fallback.py`

| 用例 | 断言要点 |
|---|---|
| `test_setup_myst_nb_missing` | 缺 `myst_nb` 时静默跳过 |
| `test_setup_myst_nb_present` | 已安装时调用 `sphinx_setup` |
| `test_setup_registers_theme_and_handler` | `setup(app)` 注册主题 + `config-inited` 句柄 |
| `test_import_mystx_smoke` | `import mystx` 成功 |

### 3.6 Python 3.14 标准库新特性（13 项）

文件：`unit/test_python314_features.py`

**annotationlib（7 项）**

| 用例 | 断言要点 |
|---|---|
| `test_config_manager_annotation_keys` | 注解键集合正确 |
| `test_config_manager_annotation_value_resolves` | `Format.VALUE` 解析到 `Sphinx`/`Config` |
| `test_config_manager_annotation_forwardref_safe` | `Format.FORWARDREF` 无未解析引用 |
| `test_config_manager_annotation_string_format` | `Format.STRING` 返回字符串 |
| `test_mystx_annotation_keys_and_value` | `MySTX` 注解键与值正确 |
| `test_get_annotations_returns_fresh_dict` | 每次返回新字典 |
| `test_forward_ref_resolution` | `ForwardRef` 延迟求值语义 |

**dataclasses.field(doc=)（2 项）**

| 用例 | 断言要点 |
|---|---|
| `test_field_doc_stored_and_readable` | `Field.doc` 存储并可读 |
| `test_mystx_fields_expose_doc_attribute` | mystx 字段以版本无关方式内省 doc（默认 `None`） |

**traceback（2 项）**

| 用例 | 断言要点 |
|---|---|
| `test_invalid_toml_preserves_traceback` | 异常链保留、`exc_type_str` 定位 |
| `test_traceback_exception_renders_source_location` | 渲染输出含类型与调用位置 |

**sys.monitoring（2 项）**

| 用例 | 断言要点 |
|---|---|
| `test_sys_monitoring_instruments_mystx_function` | 目标函数 `PY_START` 事件触发回调 |
| `test_sys_monitoring_local_events_scoped_to_target` | 局部事件仅作用于目标代码对象 |

## 四、维护约定

1. **同步更新**：新增 / 删除 / 重命名测试后，须同步更新本清单对应条目与「概览」数量（源文件位于 `playground/books/libs/mystx/tests/README.md`，与本笔记保持双向一致）。
2. **命名规范**：继续遵循 `test_<被测函数>_<场景>` 命名；Python 3.14 特性用例沿用 `@annotationlib_skip` / `@py314_skip` 装饰器做版本守卫。
3. **覆盖率门槛**：`src/mystx` 核心逻辑语句覆盖率不低于 80%（当前 97%）。剩余未覆盖的 6 行（`config.py:110/168-169`、`theme.py:55-57`）为极端异常兜底路径，可暂不补齐。
4. **新增 Python 3.14 特性**：按 Spec「诚实记录」原则，仅在 mystx 代码有实际落点时才新增对应测试，不为凑齐模块而强行引入无收益用例。相关落点评估见 [14-mystx-optimization-mapping](14-mystx-optimization-mapping.md)，优化前后量化对比见 [15-mystx-optimization-report](15-mystx-optimization-report.md)。