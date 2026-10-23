---
id: "mystx-comprehensive-retrospective-export-facts"
title: "mystx 全面复盘 — R 阶段客观事实清单"
source: "mystx 仓库实体与 git 记录（只读采集，HEAD 45bd1e4）"
methodology: "seven-concepts R 阶段"
content-sensitivity: "public"
---

# mystx — R 阶段客观事实清单

## 元信息块

| 项 | 值 |
|---|---|
| 采集对象 | `d:/spaces/SpecWeave/projects/xuanspace/libs/mystx`（Sphinx HTML 主题包，纯 Python ≥3.14，基于 Sphinx Book Theme） |
| 采集基线 | HEAD = `45bd1e437e7bd2878d48f6c9a872e4b20d82821e`（2026-10-15） |
| 采集时间 | 2026-10-22 |
| 采集方式 | 只读：`git` 只读子命令（`rev-list` / `log` / `tag` / `ls-files` / `for-each-ref` / `submodule status` / `status --porcelain` / `cat-file` / `merge-base --is-ancestor` / `rev-list --max-parents=0` / `show` / `diff --stat`）+ 文件系统只读遍历（`Get-ChildItem` / `Get-Content` / `Select-String` / Python `ast` 解析）+ 外部只读 API（PyPI JSON API / GitHub Releases API，`Invoke-WebRequest` GET） |
| 只读边界复核 | `git -C projects/xuanspace status --porcelain` → 空输出（退出码 0）；`git -C projects/xuanspace/libs/mystx status --porcelain` → 空输出（退出码 0） |
| 行数口径 | 本清单行数同时给出「非空行」（`Get-Content \| Measure-Object -Line`）与「物理行」（`Get-Content` 数组 `.Count`）两个口径，二者不等 |
| 范围声明 | 本清单仅描述「是什么」（客观实体、配置字面量、命令输出、行数、文件存在性），**不含因果推断**；因果解释属 I 阶段职责 |
| 补充取证 | H 节 15 条（F-083~F-097）：F-083~F-087 为 I 阶段线索回填，F-088~F-091 为 V 阶段对抗审查后的补充取证，F-092~F-097 为发布面外部权威取证；采集时点同为 2026-10-22，A~G 节事实采集时点未变 |

> 边界声明：`projects/xuanspace` 为 SpecWeave 主仓的 git submodule，`libs/mystx` 为 `projects/xuanspace` 的 git submodule，二级只读。本次采集未对 `projects/` 下任何文件执行写入，也未执行任何 git 写操作。

---

## A. 仓库与发布状态

| 编号 | 事实 | 来源 |
|---|---|---|
| F-001 | mystx 仓库当前分支历史共 32 次提交，提交日期区间为 2026-08-21 至 2026-10-15 | 命令输出：`git rev-list --count HEAD` → 32；`git log --format=%ad --date=short` 排序首末值 → 2026-08-21 / 2026-10-15 |
| F-002 | 首个提交为 `88e2ff2aa81ee48f47e8f3155ff5a1837dec7f2f`，日期 2026-08-21，subject 为「项目重置」 | 命令输出：`git log --reverse --format=%H\|%ad\|%s --date=short` 首行 |
| F-003 | HEAD 提交为 `45bd1e437e7bd2878d48f6c9a872e4b20d82821e`，日期 2026-10-15，subject 为「fix(docs): 补齐 epub 必需配置并抑制未知 MIME 误报」 | 命令输出：`git log -1 --format=%H\|%ad\|%s --date=short` |
| F-004 | 当前分支为 `main`，上游追踪 `origin/main`；远端引用仅 `origin/HEAD → origin/main` 与 `origin/main` 两个 | 命令输出：`git branch -vv` / `git branch -a` |
| F-005 | 32 次提交分布在 7 个不同的日历日期：2026-08-21、08-23、09-03、09-04、09-16、10-12、10-15 | 命令输出：`git log --format=%ad --date=short` 去重后计数 |
| F-006 | 按月提交分布为 2026-08 共 4 次、2026-09 共 12 次、2026-10 共 16 次 | 命令输出：`git log --format=%ad --date=format:%Y-%m` 分组统计 |
| F-007 | 提交作者分布为 `xinetzone <735613050@qq.com>` 25 次、`xinzo <xinzo@trae.cn>` 7 次 | 命令输出：`git shortlog -sne HEAD` |
| F-008 | 仓库含 13 个 git tag，完整列表为 v0.1.1、v0.1.2、v0.1.3、v0.2.0、v0.2.1、v0.2.2、v0.3.0、v0.3.1、v0.3.2、v0.3.3、v0.3.4、v0.3.7、v0.3.8 | 命令输出：`git tag --list`（13 行） |
| F-009 | 版本序列中不存在 `v0.3.5` 与 `v0.3.6` 两个 tag，`v0.3.4` 之后直接跳至 `v0.3.7` | 命令输出：`git tag --list`（13 项中无 v0.3.5 / v0.3.6） |
| F-010 | 13 个 tag 均为轻量 tag（`git cat-file -t` 返回 `commit`，非 `tag` 对象） | 命令输出：`git cat-file -t v0.3.8` → commit；`git cat-file -t v0.1.1` → commit |
| F-011 | 11 个早期 tag（v0.1.1 至 v0.3.4）指向的提交均不是 HEAD 的祖先，其 creatordate 落在 2025-02-05 至 2025-11-17；仅 `v0.3.7`（aa9277e）与 `v0.3.8`（0b0b204）是 HEAD 的祖先 | 命令输出：`git merge-base --is-ancestor <tag-sha> HEAD` 逐个校验（v0.1.1/v0.2.2/v0.3.4 → False；v0.3.7/v0.3.8 → True）；`git for-each-ref --format=%(refname:short)\|%(creatordate:short)` |
| F-012 | HEAD 相对 `v0.3.8` tag 领先 6 次提交 | 命令输出：`git log --oneline v0.3.8..HEAD` 计数 → 6 |
| F-013 | mystx 工作区与 xuanspace 工作区均无未提交变更，两级 `git status --porcelain` 均为空输出（退出码 0） | 命令输出：`git -C projects/xuanspace status --porcelain` → 空；`git -C projects/xuanspace/libs/mystx status --porcelain` → 空 |
| F-014 | xuanspace 的 submodule status 中 mystx 指针行为 `45bd1e437e7bd2878d48f6c9a872e4b20d82821e libs/mystx (v0.3.8-6-g45bd1e4)`，行首为空格（前缀状态一致） | 命令输出：`git -C projects/xuanspace submodule status` |
| F-015 | mystx 仓库 git 跟踪文件总数为 81 个 | 命令输出：`git ls-files` 计数 → 81 |

---

## B. 构建与打包配置

| 编号 | 事实 | 来源 |
|---|---|---|
| F-016 | `[build-system]` 的 `requires` 为 `["scikit-build-core>=0.10", "setuptools-scm>=8.0"]`，`build-backend` 为 `scikit_build_core.build` | 文件：`pyproject.toml:1-3` |
| F-017 | `[project]` 声明 `name = "mystx"`、`dynamic = ["version"]`、`requires-python = ">=3.14"`、`license = {file = "LICENSE"}`（以文件引用方式声明，非 SPDX 字符串）；`authors` 与 `maintainers` 均为 xinetzone | 文件：`pyproject.toml:5-17` |
| F-018 | `classifiers` 中 Development Status 取值为 `3 - Alpha`，与仓库已发布至 v0.3.8 tag 的状态并存 | 文件：`pyproject.toml:25-36`（第 26 行为 `Development Status :: 3 - Alpha`） |
| F-019 | `[tool.scikit-build]` 声明 `minimum-version = "0.10"`、`metadata.version.provider = "scikit_build_core.metadata.setuptools_scm"`；`[tool.scikit-build.wheel]` 声明 `cmake = false`、`packages = ["src/mystx"]` | 文件：`pyproject.toml:184-193` |
| F-020 | `[tool.scikit-build]` 的 `sdist.cmake = false`；`sdist.include = ["README.md", "LICENSE", "pyproject.toml", "src/mystx"]`；`sdist.exclude` 列出 `src/mystx/**/__pycache__/**`、`src/mystx/**/*.pyc`、`src/mystx/**/*.pyo` 三条排除规则 | 文件：`pyproject.toml:187-189` |
| F-021 | `[tool.setuptools_scm]` 同时声明 `version_file = "src/mystx/_version.py"` 与 `write_to = "src/mystx/_version.py"`（两个键指向同一路径） | 文件：`pyproject.toml:195-197` |
| F-022 | `src/mystx/_version.py` 存在于工作区磁盘（20 非空行 / 24 物理行，首行为 `# file generated by vcs-versioning`），但未被 git 跟踪，且 `.gitignore` 第 161 行显式排除该路径 | 文件：`src/mystx/_version.py:1`；`.gitignore:161`；命令输出：`git ls-files --error-unmatch src/mystx/_version.py` → `error: pathspec ... did not match any file(s) known to git` |
| F-023 | `[project.entry-points."sphinx.html_themes"]` 声明入口点 `mystx = "mystx"` | 文件：`pyproject.toml:44-45` |

---

## C. 依赖声明三层比对

| 编号 | 事实 | 来源 |
|---|---|---|
| F-024 | `[project]` 的 `dependencies` 为空列表，即运行时依赖声明为 0 项 | 文件：`pyproject.toml:37`（`dependencies = []`） |
| F-025 | `[project.optional-dependencies]` 含 6 个组，条目数分别为：docs 25、test 4、lint 4、build 2、tasks 2、dev 21 | 文件：`pyproject.toml:47-117`；命令输出：脚本按段解析 `[project.optional-dependencies]` 后逐组计数 |
| F-026 | `[dependency-groups]` 含 6 个组，条目数分别为：dev 11、docs 25、test 4、lint 4、build 2、tasks 2 | 文件：`pyproject.toml:119-179`；命令输出：脚本按段解析 `[dependency-groups]` 后逐组计数 |
| F-027 | docs / test / lint / build / tasks 五组在 `[project.optional-dependencies]` 与 `[dependency-groups]` 两侧的条目集合逐项完全一致（集合差为空） | 命令输出：脚本对两侧同名组做双向集合比对 → 五组均输出 IDENTICAL |
| F-028 | dev 组两侧不一致：`[project.optional-dependencies]` 的 dev 组显式列出 21 个包；`[dependency-groups]` 的 dev 组为 11 项 = 5 个 `{include-group = ...}` 引用（docs / test / lint / build / tasks）+ 6 个显式包（pdm、typer>=0.12、rich>=13.0、packaging>=24.0、tomli-w>=1.0、sphinx-intl） | 文件：`pyproject.toml:95-117` 与 `pyproject.toml:120-132`；命令输出：脚本对 dev 组做集合差比对 |
| F-029 | docs 组在两侧均为同一份 25 项清单，含 sphinx>=8.0、myst-parser>=4.0、sphinx-book-theme>=1.1、myst-nb、sphinx-autoapi>=3.4、sphinx-pyscript 等条目 | 文件：`pyproject.toml:48-74` 与 `pyproject.toml:133-159` |
| F-030 | tasks 组在两侧均含 `invoke>=2.0` 与 `invocations>=3.0` 两条；test 组在两侧均含 pytest>=8.0、pytest-cov>=5.0、pytest-xdist>=3.5、invoke>=2.0 | 文件：`pyproject.toml:91-94`、`pyproject.toml:75-80`、`pyproject.toml:176-179`、`pyproject.toml:160-165` |
| F-031 | `[tool.ruff]` 声明 `line-length = 120`、`target-version = "py314"`；`[tool.ruff.lint]` 的 `select` 为 `E, W, F, I, UP`，`ignore` 为 `["E501"]`（行长检查被显式关闭） | 文件：`pyproject.toml:210-226` |
| F-032 | `[tool.mypy]` 声明 `python_version = "3.14"`、`strict = false`、`ignore_missing_imports = true`、`warn_return_any = false` | 文件：`pyproject.toml:228-238` |
| F-033 | `[tool.black]` 声明 `line-length = 120`、`target-version = ["py314"]`；`[tool.isort]` 声明 `profile = "black"`、`line_length = 120`、`multi_line_output = 3` | 文件：`pyproject.toml:240-247` |
| F-034 | `[tool.pytest.ini_options]` 声明 `testpaths = ["tests"]`、`python_files = ["test_*.py", "*_test.py"]`，`addopts` 为 `["-ra", "--strict-markers", "--strict-config"]`，addopts 中不含 `--cov` | 文件：`pyproject.toml:199-208` |
| F-035 | `pyproject.toml` 中不存在 `[tool.coverage]` 段；对全仓 TOML 文件检索 `coverage` 与 `fail_under` 两个关键词，命中数为 0（`pytest-cov>=5.0` 依赖串仅含 `pytest-cov` 字样，不含 `coverage` 字样） | 命令输出：Grep 工具在 `*.toml` 上检索模式 `coverage\|fail_under\|\[tool\.coverage\]` → `No matches found` |
| F-036 | 全仓构建与门禁配置（`pyproject.toml`、`.pre-commit-config.yaml`、`.readthedocs.yml`、`.github/workflows/*.yml`）中不存在 `fail_under` / `fail-under` / `--cov` 任一字符串 | 命令输出：Select-String 检索 `fail_under\|fail-under\|--cov` 于上述 5 个文件 → 无输出 |

---

## D. 源码结构

| 编号 | 事实 | 来源 |
|---|---|---|
| F-037 | `src/mystx/` 下 20 个 Python 文件的非空行 / 物理行分布为：`__init__.py` 67/79、`_version.py` 20/24、`config.py` 158/199、`configs.py` 73/85、`ext/__init__.py` 6/7、`extensions.py` 69/85、`myst_compat.py` 104/133、`presets/__init__.py` 7/11、`presets/_shared.py` 46/55、`presets/minimal_myst.py` 47/58、`tasks/__init__.py` 55/68、`tasks/docs.py` 311/363、`themes.py` 96/116、`tools/__init__.py` 0/0、`utils.py` 38/44、`version_switcher.py` 71/89、`ext/github_readme_stats/` 下 6 文件 `__init__.py` 27/36、`base.py` 40/52、`pinned_repo.py` 52/65、`stats.py` 40/51、`top_langs.py` 40/51、`wakatime.py` 57/70 | 命令输出：`Get-ChildItem -Recurse -File -Include *.py`（排除 `__pycache__` / `.git` / `_build`）+ `Get-Content \| Measure-Object -Line` 与 `.Count` 两种口径 |
| F-038 | 模块职责分布：`config.py` 为配置管理（`ConfigManager` dataclass、`load_custom_config` / `apply_config` / `_merge_html_theme_options` / `apply_book_theme_option_defaults` / `thebe_setup` / `config_inited_handler`）；`configs.py` 为常量与基配置（`DEFAULT_MYST_CONFIG` / `DEFAULT_BUILD_CONFIG` / `DEFAULT_EXT_CONFIG` / `DEFAULT_HTML_CONFIG` / `build_base_config`）；`extensions.py` 为扩展解析（`resolve_extensions` + `DEFAULT_OPTIONAL_EXTENSIONS` 9 项 + `DEFAULT_CONDITIONAL`）；`themes.py` 为主题选择与注册（`resolve_theme` / `resolve_theme_options` / `MySTX` dataclass）；`utils.py` 为 `deep_merge` + `has_module`；`myst_compat.py` 为双钩子兼容层；`version_switcher.py` 为版本切换下拉 | 文件：`src/mystx/config.py:24-199`、`src/mystx/configs.py:1-85`、`src/mystx/extensions.py:7-85`、`src/mystx/themes.py:10-116`、`src/mystx/utils.py:5-44`、`src/mystx/myst_compat.py:62-133`、`src/mystx/version_switcher.py:42-89` |
| F-039 | `src/mystx/tools/__init__.py` 为 0 字节空文件；对全仓 `src/` 与 `tests/` 下 Python 文件检索 `mystx.tools`、`from .tools`、`import tools` 三种模式，命中数为 0 | 文件：`src/mystx/tools/__init__.py`（0 字节）；命令输出：Select-String 三模式检索 → 无输出 |
| F-040 | `src/mystx/__init__.py` 第 34 行的 `__all__` 为单行列表，长度 472 个字符（超出项目自设的 ruff line-length 120；该规则的 E501 已被 `ignore` 关闭） | 命令输出：`(Get-Content src/mystx/__init__.py)[33].Length` → 472；文件：`src/mystx/__init__.py:34`、`pyproject.toml:211,226` |
| F-041 | 导入链事实：`src/mystx/__init__.py:19` 为 `from . import presets, tasks`；`src/mystx/tasks/__init__.py:24` 为 `from invoke import Collection`；`src/mystx/tasks/docs.py:34` 为 `from invoke import Collection, Exit, task`，`:37` 为 `from invocations import docs as _inv_docs`（包 `try/except ImportError` 包裹，`_HAVE_INVOCATIONS` 标志位控制）。即 `import mystx` 的导入链包含 `invoke` 与 `invocations`，而 `[project] dependencies` 为空 | 文件：`src/mystx/__init__.py:19`、`src/mystx/tasks/__init__.py:24`、`src/mystx/tasks/docs.py:34-41`、`pyproject.toml:37` |
| F-042 | `src/mystx/__init__.py` 的 `__version__` 为三级 fallback 链：先 `from ._version import __version__`（`except ImportError`），再 `from importlib.metadata import version as _pkg_version` 取 `mystx`（`except Exception`），最终回退为字符串 `"0.0.0.dev0"` | 文件：`src/mystx/__init__.py:6-13` |
| F-043 | `setup()` 的 Markdown/Notebook 链采用互斥注入：`markdown_chain = {"myst_parser", "myst_nb"}`；当 conf 未显式声明且 app 未预加载时，`has_module("myst_nb")` 为真则走 `_setup_myst_nb(app)`，否则 `app.setup_extension("myst_parser")` 并输出一条 warning | 文件：`src/mystx/__init__.py:39-69` |
| F-044 | `setup()` 的返回值为 `{"parallel_read_safe": True, "parallel_write_safe": True}`，两项均为 True | 文件：`src/mystx/__init__.py:76-79` |
| F-045 | `myst_compat.py` 实现环境变量双前缀：新规范前缀 `MYSTX_MYST_COMPAT_*`，弃用别名 `SW_MYST_COMPAT_*`（命中别名时输出 info 日志，文本中标注「removed in mystx>=0.7」）；两组开关分别为 `QUOTE_DATES` 与 `DEDUPE_H1`，取值 `0` / `false` / `off`（大小写不敏感）视为关闭 | 文件：`src/mystx/myst_compat.py:21-59`（别名弃用文本见 `:41` 与 `:52`） |
| F-046 | 主题资产 `src/mystx/theme/mystx/` 共 6 个文件：`static/css/custom.css` 4791 字节、`static/css/tippy.css` 607 字节、`static/css/try_examples.css` 1825 字节、`static/js/custom-icon.js` 2936 字节、`layout.html` 47 字节、`theme.toml` 2879 字节 | 命令输出：Get-ChildItem 递归枚举 + 文件 Length 属性 |
| F-047 | `src/mystx/ext/github_readme_stats/` 由 6 个文件构成，注册 4 条 Sphinx 指令：`github-stats`（`GitHubStatsDirective`）、`github-top-langs`（`GitHubTopLangsDirective`）、`github-pinned-repo`（`GitHubPinnedRepoDirective`）、`github-wakatime`（`GitHubWakaTimeDirective`）；4 个指令类均继承 `base.py` 中的 `BaseGitHubCardDirective`；`setup()` 返回 `parallel_read_safe` 与 `parallel_write_safe` 均为 True | 文件：`src/mystx/ext/github_readme_stats/__init__.py:14-36`、`base.py:15`、`stats.py:11`、`top_langs.py:11`、`pinned_repo.py:20`、`wakatime.py:33` |
| F-048 | `src/mystx/tasks/docs.py` 的并行策略 `_parallel_flag()` 按运行环境分流：`GITHUB_ACTIONS` 环境变量存在时返回 `-j {min(cpu_count 或 1, 8)}`；`sys.platform == "win32"` 时返回空字符串；其余情况返回 `-j {max(1, (cpu_count 或 2) - 1)}` | 文件：`src/mystx/tasks/docs.py:53-70` |

---

## E. 测试资产

| 编号 | 事实 | 来源 |
|---|---|---|
| F-049 | `tests/unit/` 下 9 个测试文件的 test 函数数量逐文件为：`test_config_book_theme_defaults.py` 5、`test_doc_parallel_extensions_p1.py` 3、`test_entrypoints.py` 5、`test_ext_themes.py` 5、`test_myst_compat.py` 7、`test_presets.py` 5、`test_repo_tasks_entry.py` 4、`test_utils.py` 6、`test_version_switcher.py` 11，合计 51 个；经 Python `ast` 解析独立复核得同一结果（AST TOTAL = 51），文件内无 `@pytest.mark.parametrize` 与 `async def test_` | 命令输出：Select-String 模式 `def test_` 逐文件计数 → 合计 51；命令输出：Python `ast` 脚本遍历 `tests/` 下 `test_*.py` → `AST TOTAL = 51`；命令输出：Select-String 检索 `@pytest.mark.parametrize` 与 `async def test_` → 无输出 |
| F-050 | `tests/conftest.py` 为 5 非空行 / 6 物理行（145 字节），功能为把 `<repo>/src` 插入 `sys.path`；`tests/__init__.py` 与 `tests/unit/__init__.py` 均为 0 字节空文件 | 文件：`tests/conftest.py:1-6`；命令输出：文件 Length 与 `Get-Content` 计数 |
| F-051 | 测试覆盖对照：存在直接测试文件的源码模块为 `__init__.py`（`test_entrypoints.py`）、`config.py`（`test_config_book_theme_defaults.py`）、`extensions.py` 与 `themes.py`（`test_ext_themes.py`）、`myst_compat.py`（`test_myst_compat.py`）、`presets/`（`test_presets.py`）、`tasks/`（`test_repo_tasks_entry.py`）、`utils.py`（`test_utils.py`）、`version_switcher.py`（`test_version_switcher.py`）；无对应测试文件的源码模块为 `configs.py`、`ext/` 与 `ext/github_readme_stats/` 全部 7 个文件、`tools/__init__.py`、`_version.py` | 命令输出：Select-String 检索 `from mystx` / `import mystx` 逐文件归组；命令输出：Select-String 检索 `from mystx.config import ConfigManager` 等确认覆盖；文件清单：`src/mystx/` 20 个 `.py` 与 `tests/unit/` 9 个测试文件对照 |
| F-052 | `tests/unit/test_repo_tasks_entry.py` 承担静态对账职责，共 4 个 test 函数：根 `tasks.py` 存在且可加载、命名空间把源目录与产物目录锁定为 `doc` 布局、pages.yml 中每个 `invoke <task>` 调用名可在命名空间中解析、build 任务拼装的 `sphinx-build` 命令指向 `doc → doc/_build/html`；该文件以 `pytest.importorskip("invoke")` 作为守卫 | 文件：`tests/unit/test_repo_tasks_entry.py:20,27,49,61,79,92-108` |
| F-053 | `tests/unit/test_doc_parallel_extensions_p1.py` 以 20 项扩展的 `TARGET_EXTS` 元组启动 `parallel=4` 的最小 Sphinx app，校验各扩展的 `parallel_read_safe` 与 `parallel_write_safe` 元数据 | 文件：`tests/unit/test_doc_parallel_extensions_p1.py:18-39,42-104` |
| F-054 | 测试资产侧无覆盖率门禁：`[tool.coverage]` 段不存在、pytest addopts 不含 `--cov`、全仓无 `fail_under` / `fail-under` 字符串、三个 GitHub Actions workflow 中无任何 pytest 执行步骤 | 文件：`pyproject.toml:199-208`；命令输出：Grep `coverage\|fail_under` 于 `*.toml` → 无匹配；命令输出：Grep `pytest\|coverage\|cov` 于 `.github/workflows/*.yml` → 无输出 |

---

## F. CI/CD 与托管平台配置

| 编号 | 事实 | 来源 |
|---|---|---|
| F-055 | `.github/workflows/lint.yml` 只含 1 个 job（`ruff`，name 为 `ruff check`）：`actions/checkout@v4` + `actions/setup-python@v5`（`python-version: "3.14"`）+ `pip install --upgrade pip "ruff==0.16.3"` + `ruff check .`；ruff 版本以 `==` 精确固定，文件内注释写明固定版本的意图 | 文件：`.github/workflows/lint.yml:1-25`（ruff 版本固定见 `:22`） |
| F-056 | `.github/workflows/pages.yml` 的触发路径为 `doc/**`、`src/**`、`tasks.py`、`pyproject.toml`、`.github/workflows/pages.yml`；安装步骤为 `pip install .[docs,dev]`；构建步骤为 `invoke build`；产物校验为 `if [ ! -f "doc/_build/html/index.html" ]` 则退出码 1；步骤注释中显式说明 extras 名是 `docs` 而非 `doc` | 文件：`.github/workflows/pages.yml:10-15,74-91` |
| F-057 | `.github/workflows/pages.yml` 的首个 step 为 `step-security/harden-runner@v2`，配置 `egress-policy: block`，允许端点白名单为 pypi.org:443、files.pythonhosted.org:443、github.com:443、api.github.com:443 | 文件：`.github/workflows/pages.yml:40-48` |
| F-058 | `.github/workflows/python-publish.yml` 使用浮动 ref：`actions/checkout@main`、`actions/setup-python@main`（`python-version: "3.x"`）、`pypa/gh-action-pypi-publish@unstable/v1`（`user: __token__`，`password: ${{ secrets.PYPI_API_TOKEN }}`）；触发条件为 `release: types: [published]` | 文件：`.github/workflows/python-publish.yml:10-33` |
| F-059 | 三个 workflow（lint.yml、pages.yml、python-publish.yml）中没有任何一个执行 pytest；pytest 仅以本地 pre-commit hook 形式存在（`entry: pytest`，`language: system`，`pass_filenames: false`，`stages: [push]`） | 命令输出：Grep `pytest\|coverage\|cov` 于 `.github/workflows/*.yml` → 无输出；文件：`.pre-commit-config.yaml:64-72` |
| F-060 | `.readthedocs.yml` 声明 `version: 2`、`build.os: ubuntu-24.04`、`build.tools.python: "3.14"`、`sphinx.configuration: doc/conf.py`、`sphinx.fail_on_warning: true`（注释标注等价 `-W --keep-going`）、`formats: [htmlzip, epub, pdf]`、`python.install` 为 method pip + path `.` + `extra_requirements: [docs]` | 文件：`.readthedocs.yml:6-47`（fail_on_warning 见 `:32`，formats 见 `:36-39`，pip extras 见 `:42-47`） |
| F-061 | `.readthedocs.yml` 注释中自述 CI 侧的 `invoke build` 默认不带 `-W`，该行是抬高到与 RTD 一致的质量门；同一文件注释亦记录了旧 `ubuntu-26.04` + `mambaforge-latest` 组合的失效现象与 RTD build 35084329 编号 | 文件：`.readthedocs.yml:28-31`（旧镜像记录见 `:10-15`） |
| F-062 | `.pre-commit-config.yaml` 含 9 个 `repo:` 块：8 个上游仓库（pre-commit/pre-commit-hooks rev v4.4.0、PyCQA/autoflake rev v2.2.1、pycqa/isort rev 5.12.0、psf/black rev 23.10.1、PyCQA/flake8 rev 6.1.0、pre-commit/mirrors-mypy rev v1.5.1、codespell-project/codespell rev v2.2.6、pre-commit/mirrors-prettier rev v3.0.3）+ 1 个 `local` 块；`- id:` 条目共 13 个（上游 12 个 + 本地 pytest 1 个） | 文件：`.pre-commit-config.yaml:6,16,22,28,34,41,48,55,64`；命令输出：Select-String `^\s+- id:` 计数 → 13；命令输出：Select-String `- repo:` 计数 → 9 |
| F-063 | pre-commit 配置内的 flake8 传入 `args: ['--max-line-length=100']`，与项目 `[tool.ruff]` / `[tool.black]` 的 `line-length = 120` 数值不同；pre-commit 的 isort 块无独立参数（走 `profile = "black"` 的 pyproject 配置） | 文件：`.pre-commit-config.yaml:37-39`、`pyproject.toml:211,241,246` |
| F-064 | pre-commit 的 black 块 rev 为 23.10.1 且声明 `language_version: python3.10`，而项目 `requires-python` 为 `>=3.14`；pre-commit 的 mypy 块 rev 为 v1.5.1，附加依赖 `types-all`，参数为 `--ignore-missing-imports --allow-untyped-defs` | 文件：`.pre-commit-config.yaml:28-32,41-46`、`pyproject.toml:11` |
| F-065 | `dev-environment.yml` 为 258 字节 / 16 物理行，内容为 conda 环境定义：`name: mystx-dev`、`channels: [conda-forge]`、`dependencies: [python, pip]` 加 pip 段 `- .[docs]` | 文件：`dev-environment.yml:1-16` |

---

## G. 文档与主题资产

| 编号 | 事实 | 来源 |
|---|---|---|
| F-066 | README「核心依赖」段（第 70 行 `## 📋 依赖`、第 72 行 `### 核心依赖`、第 74-78 行）逐条列出 5 项：`sphinx-book-theme>=1.1.4`（主题继承）、`sphinx>=8.0.0`（文档生成引擎）、`myst-nb`（Jupyter Notebook 支持）、`myst-parser`（MyST Markdown 解析器）、Python 3.14+（运行环境）；这 5 项在 `pyproject.toml:37` 的 `dependencies = []` 中均无对应声明 | 文件：`README.md:70-78`、`pyproject.toml:37` |
| F-067 | README 声明的 `sphinx-book-theme>=1.1.4` 与 pyproject 两侧（`pyproject.toml:51` 与 `:136`）声明的 `sphinx-book-theme>=1.1` 版本下界数值不同；README 的 `sphinx>=8.0.0` 与 pyproject 的 `sphinx>=8.0` 亦存在书写差异 | 文件：`README.md:74-75`、`pyproject.toml:49,51,134,136` |
| F-068 | README 第 59 行为 `pip install "mystx[docs]"`（文档扩展安装说明），第 67 行为 `pip install -ve .[dev]`（开发环境安装说明） | 文件：`README.md:59,67` |
| F-069 | README 第 90 行示例含 `locale_dirs = ['../locales/']`；对仓库全目录递归检索 `locales` 目录，命中数为 0（仓库根与 `doc/` 下均不存在该目录） | 文件：`README.md:90`；命令输出：`Get-ChildItem -Recurse -Directory -Filter locales` → 无输出；命令输出：`Test-Path <repo>/locales` → False；`Test-Path <repo>/doc/locales` → False |
| F-070 | README 提供两种主题配置方式：`html_theme_options` 字典形式位于第 122-135 行（字典自 122 行 `html_theme_options = {` 至 135 行 `}`），`_config.toml` 形式说明位于第 138-156 行（`[html_theme_options]` 段起于 143 行，示例块止于 156 行） | 文件：`README.md:122-135,138-156` |
| F-071 | `CHANGELOG.md` 为 18 物理行 / 10 非空行（1739 字节），只含一个版本条目 `## [v0.3.8] - 2026-10-15`；该条目下「### 修复」段含 2 条（主题重复搜索按钮、Read the Docs 构建配置），「### 测试」段含 1 条（新增 5 个单元测试锁定 `navbar_persistent` 注入语义）；文件无 Unreleased 段 | 文件：`CHANGELOG.md:1-18`（版本条目起于第 7 行，修复段 2 条，测试段 1 条，末行为 v0.3.8 比较链接） |
| F-072 | CHANGELOG 覆盖版本（v0.3.8，1 个）与 git tag 集合（13 个）不对齐：v0.1.1 至 v0.3.7 共 12 个 tag 在 CHANGELOG 中无对应条目 | 文件：`CHANGELOG.md:1-18`；命令输出：`git tag --list`（13 项） |
| F-073 | `doc/conf.py` 为 283 非空行 / 320 物理行；其中 `locale_dirs = ['../locales/']` 出现在第 48 行（与 README 第 90 行同一取值），`extensions` 基础列表在第 58 行为 `[e for e in ['mystx'] if _has(e)]`，第 253 行追加 `mystx.ext.github_readme_stats`；`setup()` 在第 255 行起，返回 `parallel_read_safe` 与 `parallel_write_safe` 均为 True | 文件：`doc/conf.py:48,58,253,255,316-317` |
| F-074 | `doc/_config.toml` 为 2194 字节，含 `[html_theme_options]` 段（announcement / repository_url / use_repository_button / path_to_docs = "doc" / show_navbar_depth = 1 / max_navbar_depth = 7 等）与 `[html_theme_options.launch_buttons]` 段（binderhub / colab / deepnote / notebook_interface / jupyterhub） | 文件：`doc/_config.toml`（全文 1-52 行） |
| F-075 | `doc/_ext/sphinx_docx/writer.py` 为 901 非空行 / 1133 物理行，定义 `DocxWriter`（第 65 行）、`DocxState`（第 109 行）、`DocxTranslator`（第 127 行）三个类；import 了 `docx.enum.style`（`WD_STYLE_TYPE`）、`docx.shared`（`Cm`）、`docx.table._Cell`，后两者所在 import 块带 `# noinspection` 注释 | 文件：`doc/_ext/sphinx_docx/writer.py:1-13,65,109,127` |
| F-076 | `doc/_ext/sphinx_docx/writer.py` 文件首行即为 `import logging`，无模块级 docstring；对该文件检索 `Licen` / `licen` / `Apache` / `MIT` / `copyright` / `attribution` / `Adapted from` / `based on` / `upstream` 等词，命中项仅为 docutils 节点处理函数名 `visit_attribution` / `depart_attribution`（第 261、266 行）与一行注释，无许可证头与上游归属声明 | 文件：`doc/_ext/sphinx_docx/writer.py:1,261,266,488`；命令输出：Select-String 归属关键词检索 → 仅 `:261`、`:266`、`:488` 三处非归属命中 |
| F-077 | `doc/_ext/sphinx_docx/builder.py` 为 115 非空行 / 141 物理行，定义 `DocxBuilder(Builder)`（`name = 'docx'`、`file_suffix = '.docx'`）并从 `.writer` 导入 `DocxWriter`；`doc/_ext/sphinx_docx/__init__.py` 为 4 非空行 / 6 物理行，`setup(app)` 注册 `DocxBuilder` 并添加 `docx_template` 配置值 | 文件：`doc/_ext/sphinx_docx/builder.py:1-40`、`doc/_ext/sphinx_docx/__init__.py:1-6` |
| F-078 | `doc/_ext/gallery_directive.py` 为 113 非空行 / 144 物理行，其模块 docstring 中写有「It currently exists for maintainers of the pydata-sphinx-theme, but might be abstracted into a standalone package if it proves useful.」；`doc/_ext/component_directive.py` 为 81 非空行 / 99 物理行，docstring 描述为「A directive to generate the list of all the built-in components.」 | 文件：`doc/_ext/gallery_directive.py:1-12`、`doc/_ext/component_directive.py:1-6` |
| F-079 | `doc/ext/live-preview/live_preview.py` 为 170 非空行 / 204 物理行，docstring 描述为基于 Docutils 与 MyST-Parser 在 PyScript/Pyodide 环境中的实时预览实现；`doc/gallery/sphinx-ext/sphinx-pyscript/convert_json_to_toml.py` 为 7 非空行 / 12 物理行，为浏览器端 js 脚本（`from js import document`，基于 `querySelector` 绑定输入事件） | 文件：`doc/ext/live-preview/live_preview.py:1-15`、`doc/gallery/sphinx-ext/sphinx-pyscript/convert_json_to_toml.py:1-12` |
| F-080 | 仓库根 `LICENSE` 为 Apache License 2.0 全文（首行 `Apache License`，第二行 `Version 2.0, January 2004`）；仓库内仅此一个 LICENSE 文件（无 LICENSE-MIT / LICENSE-APACHE 等并存副本） | 文件：`LICENSE:1-3`；命令输出：Get-ChildItem `-Filter LICENSE*` → 仅 `LICENSE` |
| F-081 | `README.md` 全文 169 物理行 / 131 非空行，含 12 个徽章链接定义（第 15-32 行）、GitHub 仓库 `https://github.com/xinetzone/mystx`、PyPI 页面 `https://pypi.org/project/mystx/`、官方文档 `https://mystx.readthedocs.io/` 三条对外链接 | 文件：`README.md:15-32,166-169` |
| F-082 | `CONTRIBUTING.md` 为 124 物理行；对其中检索 `pytest` / `coverage` / `ruff` / `black` / `pre-commit` / `invoke` 六个关键词，命中数为 0 | 文件：`CONTRIBUTING.md`（124 行）；命令输出：Select-String 六关键词检索 → 无输出 |

---

## H. 补充取证（I 阶段回填 + V 阶段复核追加，2026-10-22）

> 本节为 I 阶段发现线索后回主仓取证、以及 V 阶段对抗审查后补充取证的事实，编号自 F-083 起续接，与前述 A~G 同一体例。其中 F-083~F-087 为 I 阶段线索回填，F-088~F-091 为 V 阶段对抗审查后的仓库侧补充取证，F-092~F-097 为发布面外部权威取证（PyPI / GitHub API 实时响应）。

| 编号 | 事实 | 来源 |
|---|---|---|
| F-083 | PyPI 上存在名为 `invocations` 的发布包，当前版本 4.0.2，摘要为 "Common/best-practice Invoke tasks and collections"，其 `requires_dist` 列出 10 项传递依赖：`invoke>=1.7.2`、`blessings>=1.6`、`build>=1.3`、`pip~=25.2`、`releases>=1.6`、`semantic_version<2.7,>=2.4`、`tabulate>=0.7.5`、`tqdm>=4.8.1`、`twine>=1.15`、`wheel>=0.24.0` | 命令输出：`Invoke-WebRequest https://pypi.org/pypi/invocations/json` → HTTP 200；`info.name` = invocations；`info.version` = 4.0.2；`info.requires_dist` 10 项 |
| F-084 | `src/mystx/tasks/docs.py:37` 在 `try` 块内执行 `from invocations import docs as _inv_docs  # type: ignore[import-not-found]`，第 39 行为 `except ImportError:  # pragma: no cover - invocations 为可选依赖`；第 20 行 docstring 记载「安装 `invocations` 后，browse/tree/doctest(builder) 复用其稳定实现」 | 文件：`src/mystx/tasks/docs.py:20,37,39`；命令输出：Grep `invocations` 于 mystx 全仓 → 命中 `pyproject.toml:93`、`pyproject.toml:178`、`src/mystx/tasks/docs.py:20,37,39` |
| F-085 | `[project.optional-dependencies]` 与 `[dependency-groups]` 的 build、docs、lint、tasks、test 五组做双向集合比对，**五组两侧集合完全相同**；两侧 `dev` 组不同：optional 侧为 21 项显式包，group 侧为 11 项（5 个 `{include-group = ...}` 引用 + 6 个显式包 `pdm`、`typer>=0.12`、`rich>=13.0`、`packaging>=24.0`、`tomli-w>=1.0`、`sphinx-intl`） | 命令输出：Python `tomllib` 解析 `pyproject.toml` 后逐组集合比对 → `build opt=2 grp=2 IDENTICAL`、`docs opt=25 grp=25 IDENTICAL`、`lint opt=4 grp=4 IDENTICAL`、`tasks opt=2 grp=2 IDENTICAL`、`test opt=4 grp=4 IDENTICAL`、`dev opt=21 grp=11 DIFF` |
| F-086 | optional 侧 `dev` 组的 21 项**不等于** group 侧 `dev` 组的展开并集（42 项）：并集独有 23 项 = docs 组 22 项（`ablog`、`graphviz`、`ipywidgets`、`matplotlib`、`nbclient`、`numpy`、`pandas`、`plotly`、`sphinx-autoapi>=3.4`、`sphinx-book-theme>=1.1`、`sphinx-comments`、`sphinx-contributors`、`sphinx-copybutton`、`sphinx-design`、`sphinx-examples`、`sphinx-pyscript`、`sphinx-sitemap`、`sphinx-thebe`、`sphinx-tippy`、`sphinxcontrib-bibtex`、`sphinxcontrib-mermaid`、`sphinxext-opengraph`）+ tasks 组的 `invocations>=3.0`；同时 docs 组另有 `myst-nb` / `myst-parser>=4.0` / `sphinx>=8.0` 3 项不在并集内；optional 侧独有 2 项（`docutils>=0.20`、`myst-docutils>=4.0`） | 命令输出：Python `tomllib` 解析并做 `union \| extra` 与 `set(opt['dev'])` 双向差集比对 → `union+extra size 42`、`union_only size 23`、`opt dev == union+extra ? False`、`union_only == docs_set ? False`；`union_only - docs : ['invocations>=3.0']`；`docs - union_only : ['myst-nb', 'myst-parser>=4.0', 'sphinx>=8.0']`；`opt dev - union+extra : ['docutils>=0.20', 'myst-docutils>=4.0']` |
| F-087 | optional 侧 `dev` 组 21 项中**含** `invoke>=2.0`、**不含** `invocations>=3.0`；`invocations>=3.0` 仅出现在 `tasks` 组（optional 侧 `pyproject.toml:93`、group 侧 `pyproject.toml:178`） | 文件：`pyproject.toml:95-117`（dev 组 21 项清单）、`pyproject.toml:91-94`（tasks 组）、`pyproject.toml:176-179`（group tasks 组）；命令输出：同上差集比对结果中 `invocations>=3.0` 归入并集独有侧 |
| F-088 | `git diff --stat v0.3.4 HEAD` 在 v0.3.4 与 HEAD 之间输出 `69 files changed, 2892 insertions(+), 533 deletions(-)`；`git cat-file -t v0.3.4` 返回 `commit`；`git log --oneline -1 v0.3.4` 返回 `41b6483 feat: 更新版本至0.3.4并添加新功能`。即 tag v0.3.4 指向的提交对象完好且与 HEAD 之间的内容差异可直接比对 | 命令输出：`git diff --stat v0.3.4 HEAD` → 末行 `69 files changed, 2892 insertions(+), 533 deletions(-)`；`git cat-file -t v0.3.4` → `commit`；`git log --oneline -1 v0.3.4` → `41b6483 feat: 更新版本至0.3.4并添加新功能` |
| F-089 | 13 个 tag 分属 6 条互相独立的谱系，每条谱系的根提交（`git rev-list --max-parents=0 <tag>`）subject 均为「项目重置」；映射为：`root=9b61b35` → v0.1.2（根提交日期 2025-09-08）、`root=88e2ff2` → v0.3.7、v0.3.8（根提交日期 2026-08-21）、`root=96fbfa9` → v0.2.0、v0.2.1（根提交日期 2025-09-15）、`root=3dcd9f5` → v0.1.1（根提交日期 2024-12-25）、`root=fb76d06` → v0.2.2、v0.3.0、v0.3.1、v0.3.2、v0.3.3、v0.3.4（根提交日期 2025-09-18）、`root=bed5041` → v0.1.3（根提交日期 2025-09-10） | 命令输出：逐 tag 执行 `git rev-list --max-parents=0 <tag>` + `git log -1 --format=%s <root>`；13 个 tag 的根提交 subject 输出均为 `项目重置`；`git rev-list --max-parents=0 HEAD` → 仅 `88e2ff2aa81ee48f47e8f3155ff5a1837dec7f2f` 一条（即当前主线自身的谱系根） |
| F-090 | `git show v0.3.4:pyproject.toml` 显示旧谱系中 `[project]` 的 `name = "mystx"`、`version = "0.3.4"`、`requires-python = ">=3.10"`、`dependencies = []`，即旧谱系仍为同一个 mystx 项目 | 命令输出：`git show v0.3.4:pyproject.toml` → 前 20 行含 `name = "mystx"`（第 2 行）、`version = "0.3.4"`（第 3 行）、`requires-python = ">=3.10"`（第 8 行）、`dependencies = []`（第 14 行） |
| F-091 | 旧谱系不存在版本级变更记录：`git show v0.3.4:CHANGELOG.md` 输出仅 2 行模板头「# xyzstyle 项目变更日志」「本文档记录 xyzstyle 项目的所有重要变更。」，无任何版本条目；`git show v0.1.1:CHANGELOG.md` 报错 `fatal: path 'CHANGELOG.md' exists on disk, but not in 'v0.1.1'`（该版本树中无此路径） | 命令输出：`git show v0.3.4:CHANGELOG.md` → 2 行（`# xyzstyle 项目变更日志` / `本文档记录 xyzstyle 项目的所有重要变更。`）；`git show v0.1.1:CHANGELOG.md` → `fatal: path 'CHANGELOG.md' exists on disk, but not in 'v0.1.1'`（退出码 128） |
| F-092 | PyPI 上 mystx 实际发布 9 个版本：0.2.1（upload_time 2025-09-17 09:43:42）、0.2.2（2025-09-18 02:16:41）、0.3.0（2025-09-19 03:56:32）、0.3.1（2025-10-25 02:11:37）、0.3.2（2025-10-27 03:28:31）、0.3.3（2025-10-29 15:17:36）、0.3.4（2025-11-17 08:13:33）、0.3.6（2026-09-03 23:59:43）、0.3.7（2026-10-12 05:57:36）；`info.version`（latest）= 0.3.7 | 命令输出：`Invoke-WebRequest https://pypi.org/pypi/mystx/json` → HTTP 200；`info.name` = mystx；`info.version` = 0.3.7；`releases` 键数量 = 9；逐版本 `urls[0].upload_time` 见本条 |
| F-093 | PyPI 上 `mystx==0.3.6` 存在（HTTP 200，upload_time 2026-09-03 23:59:43，`requires_python` = `>=3.14`）；`mystx==0.3.5` 与 `mystx==0.3.8` 的 JSON 接口均返回 HTTP 404 | 命令输出：`https://pypi.org/pypi/mystx/0.3.6/json` → HTTP 200（`info.requires_python` = `>=3.14`，`urls[0].upload_time` = 2026-09-03 23:59:43）；`https://pypi.org/pypi/mystx/0.3.5/json` → HTTP 404；`https://pypi.org/pypi/mystx/0.3.8/json` → HTTP 404 |
| F-094 | GitHub 仓库 `xinetzone/mystx` 的 Releases 实测 11 条：v0.1.1、v0.1.2、v0.1.3、v0.2.1、v0.2.2、v0.3.0、v0.3.1、v0.3.2、v0.3.3、v0.3.4、v0.3.7；其中 `prerelease=true` 的 7 条为 v0.1.1、v0.1.2、v0.1.3、v0.3.1、v0.3.2、v0.3.3、v0.3.4；`draft=true` 的 0 条；无 v0.3.5 / v0.3.6 / v0.3.8 的 Release 条目 | 命令输出：`Invoke-WebRequest https://api.github.com/repos/xinetzone/mystx/releases` → HTTP 200，数组长度 = 11；逐条读取 `tag_name` / `prerelease` / `draft` / `published_at`；`prerelease=true` 计数 = 7（v0.1.1、v0.1.2、v0.1.3、v0.3.1、v0.3.2、v0.3.3、v0.3.4）；`draft=true` 计数 = 0 |
| F-095 | PyPI 上 mystx 0.3.7 的 `requires_dist` 共 58 项，其中 runtime 侧（无 `extra` 标记的顶层项）计数为 0：`sphinx>=8.0` / `myst-parser>=4.0` / `sphinx-book-theme>=1.1` / `myst-nb` 等全部标注 `extra == "docs"`；`invocations>=3.0` 标注 `extra == "tasks"`，不在 docs extra 内；`invoke>=2.0` 同时出现在 `extra == "test"` / `extra == "tasks"` / `extra == "dev"` 三处 | 命令输出：`Invoke-WebRequest https://pypi.org/pypi/mystx/0.3.7/json` → HTTP 200；`info.requires_dist` 共 58 行，无 `extra ==` 标记的行计数 = 0；按 extra 分组计数 = docs 25 / test 4 / lint 4 / build 2 / tasks 2 / dev 21；docs extra 中匹配 `invoke` 的行计数 = 0，匹配 `invocations` 的行计数 = 0 |
| F-096 | PyPI 各版本的 `requires_python` 呈三段分代：0.2.1 / 0.2.2 / 0.3.0 = `>=3.12`；0.3.1 / 0.3.2 / 0.3.3 / 0.3.4 = `>=3.10`；0.3.6 / 0.3.7 = `>=3.14` | 命令输出：逐版本 `Invoke-WebRequest https://pypi.org/pypi/mystx/<ver>/json` → HTTP 200 后读取 `info.requires_python`，9 个版本取值见本条 |
| F-097 | 仓库最新 tag `v0.3.8` 未出现在任何分发面：PyPI 无 0.3.8（`/0.3.8/json` → HTTP 404），GitHub Releases 无 v0.3.8 条目，PyPI `info.version`（latest）仍为 0.3.7；反向地，PyPI 上的 0.3.6 在仓库中无对应 tag（`git tag --list` 13 项中无 v0.3.6） | 命令输出：`https://pypi.org/pypi/mystx/0.3.8/json` → HTTP 404；`https://pypi.org/pypi/mystx/json` → `info.version` = 0.3.7；`https://api.github.com/repos/xinetzone/mystx/releases` → 11 条 `tag_name` 中无 `v0.3.8`；`git tag --list` → 13 项中无 `v0.3.6` |

---

## 附录：回溯抽样对照表

| F 编号 | 回溯路径 | 核验结论 |
|---|---|---|
| F-001 | `git rev-list --count HEAD` → 32 | ✅ 一致：32 次提交 |
| F-003 | `git log -1 --format=%H\|%ad\|%s --date=short` → `45bd1e437e7bd2878d48f6c9a872e4b20d82821e 2026-10-15 fix(docs): 补齐 epub 必需配置并抑制未知 MIME 误报` | ✅ 一致：HEAD SHA、日期、subject 三项均匹配 |
| F-009 | `git tag --list` → 13 行输出，逐行比对 v0.3.5 / v0.3.6 | ✅ 一致：两项均未出现在 tag 列表中 |
| F-011 | `git merge-base --is-ancestor 41b6483 HEAD`（v0.3.4）→ 退出码非 0 | ✅ 一致：v0.3.4 及其余 10 个早期 tag 均非 HEAD 祖先 |
| F-014 | `git -C projects/xuanspace submodule status` → ` 45bd1e437e7bd2878d48f6c9a872e4b20d82821e libs/mystx (v0.3.8-6-g45bd1e4)` | ✅ 一致：指针 SHA、路径、描述三重匹配 |
| F-016 | `pyproject.toml:1-3` → `requires = ["scikit-build-core>=0.10", "setuptools-scm>=8.0"]` / `build-backend = "scikit_build_core.build"` | ✅ 一致 |
| F-018 | `pyproject.toml:26` → `"Development Status :: 3 - Alpha",` | ✅ 一致：Development Status 取值为 Alpha |
| F-024 | `pyproject.toml:37` → `dependencies = []` | ✅ 一致：运行时依赖为空列表 |
| F-027 | 脚本对 docs / test / lint / build / tasks 五组做双向集合比对 → 全部输出 IDENTICAL | ✅ 一致：五组两侧无差异 |
| F-028 | `pyproject.toml:120-132` → dev 组 5 个 `{include-group = ...}` + 6 个显式包 = 11 项 | ✅ 一致：与 F-028 记录的 11 项吻合；optional 侧 `pyproject.toml:95-117` 为 21 项显式包 |
| F-031 | `pyproject.toml:226` → `ignore = ["E501"]` | ✅ 一致：行长检查在 ruff 中被关闭 |
| F-035 | Grep 模式 `coverage\|fail_under\|\[tool\.coverage\]` 于 `*.toml` → `No matches found` | ✅ 一致：无 `[tool.coverage]` 段 |
| F-040 | `(Get-Content src/mystx/__init__.py)[33].Length` → 472 | ✅ 一致：`__all__` 单行长度 472 字符 |
| F-041 | `src/mystx/__init__.py:19` → `from . import presets, tasks`；`src/mystx/tasks/__init__.py:24` → `from invoke import Collection` | ✅ 一致：导入链两跳均核实 |
| F-046 | Get-ChildItem 枚举 `src/mystx/theme/mystx` → custom.css 4791 / tippy.css 607 / try_examples.css 1825 / custom-icon.js 2936 / layout.html 47 / theme.toml 2879 | ✅ 一致：6 个文件字节数逐项匹配 |
| F-049 | Python `ast` 脚本遍历 `tests/` → `AST TOTAL = 51` | ✅ 一致：与 Select-String 计数 51 相同（原任务书所述 59 与实测不符，实测 51） |
| F-059 | Grep `pytest\|coverage\|cov` 于 `.github/workflows/*.yml` → 无输出 | ✅ 一致：三个 workflow 无 pytest 步骤 |
| F-063 | `.pre-commit-config.yaml:39` → `args: ['--max-line-length=100']`；`pyproject.toml:211` → `line-length = 120` | ✅ 一致：两处行长数值不同 |
| F-066 | `README.md:74-78` → 5 条核心依赖条目；`pyproject.toml:37` → `dependencies = []` | ✅ 一致：README 5 项在空依赖声明中无对应 |
| F-069 | `Get-ChildItem -Recurse -Directory -Filter locales` → 无输出 | ✅ 一致：仓库内不存在 locales 目录 |
| F-071 | `CHANGELOG.md` → 18 物理行，版本条目 `## [v0.3.8] - 2026-10-15` 唯一 | ✅ 一致：仅 v0.3.8 一个条目，无 Unreleased 段 |
| F-076 | `doc/_ext/sphinx_docx/writer.py:1` → `import logging`；归属关键词检索命中 `:261`/`:266`/`:488` | ✅ 一致：首行为 import，无许可证头与归属注释 |
| F-082 | `CONTRIBUTING.md` → 124 行；六关键词检索 → 无输出 | ✅ 一致：贡献指南未提及测试与工具链命令 |
| F-083 | `Invoke-WebRequest https://pypi.org/pypi/invocations/json` → HTTP 200，`info.name`=invocations，`info.version`=4.0.2 | ✅ 一致：包名有效存在 |
| F-085 | Python `tomllib` 逐组集合比对 → 五组 IDENTICAL，dev 组 `opt=21 grp=11 DIFF` | ✅ 一致：与 F-027、F-028 记录吻合 |
| F-086 | 同上脚本差集比对 → `union+extra size 42`、`opt dev == union+extra ? False` | ✅ 一致：optional dev 组确非 group 侧展开并集 |
| F-087 | 差集清单中 `invocations>=3.0` 归入并集独有侧；optional dev 组 21 项含 `invoke>=2.0` | ✅ 一致：invocations 仅在 tasks 组 |

**抽样覆盖**：27 条（要求 ≥12），覆盖 A / B / C / D / E / F / G 全部 7 个维度 + H 补充取证；**命中率 27/27 = 100%**（每条均能按"回溯路径"列重放命令或重读文件行得到一致结论）。
