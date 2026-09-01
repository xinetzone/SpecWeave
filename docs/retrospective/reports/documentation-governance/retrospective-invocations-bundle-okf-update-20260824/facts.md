---
type: Facts
id: "facts"
title: "invocations v4.1.0 — 事实采集基线（R 阶段）"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/documentation-governance/retrospective-invocations-bundle-okf-update-20260824/facts.toml"
---

# invocations v4.1.0 — 事实采集基线（R 阶段）

> 本文档为「源码 → OKF wiki」工作流的 R（事实采集）阶段产物。
> 数据来源：`d:\spaces\SpecWeave\external\libs\tools\pyinvoke\invocations\` 下各源码文件的**实际行内容**。
> 纪律（G1）：只陈述代码中真实存在的内容，并标注来源文件；不使用「用于/目的是/设计为」等推断词；不臆造任何 API；不能从源码验证的细节一律省略。

---

## 1. 版本确认

- 来源：`pyproject.toml`（`[project]` 段，第 4 行）
- `version = "4.1.0"`
- 包名：`name = "invocations"`
- `requires-python = ">=3.9"`
- 运行时依赖（`[project].dependencies`）：`invoke>=1.7.2`、`blessings>=1.6`、`build>=1.3`、`pip>=25.1`、`releases>=1.6`、`semantic_version>=2.4,<2.7`、`tabulate>=0.7.5`、`tqdm>=4.8.1`、`twine>=1.15`、`wheel>=0.24.0`
- 构建后端：`[build-system]` → `setuptools.build_meta`，`requires = ["setuptools >= 77"]`
- 注：`invocations/__init__.py` 第 3 行通过 `metadata.version("invocations")` 运行时读取版本号，源码本身未硬编码版本数字。

## 2. 真实模块清单

`packaging/` 子包实际存在的文件（经目录列举核实）：

- `invocations/packaging/__init__.py`
- `invocations/packaging/release.py`
- `invocations/packaging/semantic_version_monkey.py`
- `invocations/packaging/vendorize.py`

**确认：`packaging/version.py` 不存在**（Glob 检索 `invocations/packaging/version.py` 返回空）。

顶层模块实际存在的文件：

- `invocations/__init__.py`
- `invocations/autodoc.py`
- `invocations/checks.py`
- `invocations/ci.py`
- `invocations/console.py`
- `invocations/docs.py`
- `invocations/environment.py`
- `invocations/pytest.py`
- `invocations/testing.py`
- `invocations/util.py`
- `invocations/watch.py`

---

## 3. 各模块事实

> 说明：`setuptools` 包默认情况下，若某模块未定义 `ns`/`ns = Collection(...)`，则其 `@task` 不会被自动注册；下文仅陈述源码中实际出现的结构。

### F-autodoc — `invocations/autodoc.py`

- 无任何 `@task` 装饰的 `task` 函数。
- 定义类 `TaskDocumenter(autodoc.DocstringSignatureMixin, autodoc.ModuleLevelDocumenter)`（第 52 行）。
  - 类属性 `objtype = "task"`、`directivetype = "function"`（第 55-56 行）。
  - 类方法 `can_document_member(cls, member, membername, isattr, parent)`（第 58 行）：函数体 `return isinstance(member, Task)`。
  - 实例方法 `format_args(self)`（第 62 行）：函数体 `function = self.object.body`，返回 `autodoc.stringify_signature(inspect.signature(function))`。
  - 实例方法 `document_members(self, all_members=False)`（第 73 行）：函数体为 `pass`（被改写为空实现）。
- 顶层函数 `setup(app)`（第 79 行）：调用 `app.setup_extension("sphinx.ext.autodoc")` 与 `app.add_autodocumenter(TaskDocumenter)`。
- 模块导入 `from invoke import Task` 与 `from sphinx.ext import autodoc`。

### F-checks — `invocations/checks.py`

- `from invoke import task`（第 7 行）。未定义 `ns`。

| 任务函数 | 装饰器 | 参数与默认值 | 函数体要点 |
|---|---|---|---|
| `blacken` | `@task(name="blacken", aliases=["format"], iterable=["folders"])` | `c, line_length=79, folders=None, check=False, diff=False, find_opts=None` | 读 `c.config.get("blacken", {})` 的 `folders`（默认 `["."]`）与 `find_opts`；拼 `find ... -name '*.py' | xargs black ...` 命令并 `c.run(cmd, pty=True)` |
| `lint` | `@task` | `c` | 执行 `c.run("flake8", warn=True, pty=True)` |
| `all_` | `@task(default=True)` | `c` | 设 `c.config.run.echo = True`；依次调用 `blacken(c)`、`lint(c)` |

- `blacken` 配置项（`blacken` 子树）：`folders`、`find_opts`（均由函数体内 `config.get(...)` 读取）。

### F-ci — `invocations/ci.py`

- `from invoke import task, Collection`（第 29 行）。

| 任务函数 | 参数与默认值 | 函数体要点 |
|---|---|---|
| `make_sudouser` | `c` | 读 `c.ci.sudo.user / .password / .groups`；`c.sudo("useradd ... --create-home --groups ...")`；`c.run("echo %s:%s | sudo chpasswd")` |
| `sudo_run` | `c, command` | 执行 `c.run('sudo su <user> -c "export PATH=$PATH && <command>"')` |
| `make_sshable` | `c` | 设 `c.config.sudo.user/password`；循环 `mkdir`/`chmod 0700` 目录；`ssh-keygen -t rsa`；`cp id_rsa.pub authorized_keys` |

- Collection 结构（第 94-105 行）：
  - `ns = Collection(make_sudouser, sudo_run, make_sshable)`
  - `ns.configure({...})`，config 键：`ci.sudo.user`（默认 `"invoker"`）、`ci.sudo.password`（默认 `"secret"`）、`ci.sudo.groups`（默认 `["sudo", "circleci"]`）。

### F-console — `invocations/console.py`

- 无 `@task`。无 `ns`。
- 顶层函数 `confirm(question, assume_yes=True)`（第 9 行）：循环 `input("{} [{}] ".format(...))`；接受 `y/yes` 返回 `True`、`n/no` 返回 `False`、空输入返回 `assume_yes`；`suffix` 依 `assume_yes` 为 `"Y/n"` 或 `"y/N"`；无效输入向 `sys.stderr` 打印 `"I didn't understand you. Please specify '(y)es' or '(n)o'."` 后重试。返回 `bool`。

### F-docs — `invocations/docs.py`

- `from invoke import task, Collection, Context`（第 10 行）；`from .watch import make_handler, observe`（第 12 行）。

| 任务函数 | 装饰器 | 参数与默认值 | 函数体要点 |
|---|---|---|---|
| `_clean` | `@task(name="clean")` | `c` | `if isdir(c.sphinx.target): rmtree(c.sphinx.target)` |
| `_browse` | `@task(name="browse")` | `c` | `index = join(c.sphinx.target, c.sphinx.target_file)`；`c.run("open {}".format(index))` |
| `build` | `@task(default=True, help={...})` `help` 键含 `opts/clean/browse/nitpick/source/target` | `c, clean=False, browse=False, nitpick=False, opts=None, source=None, target=None` | `clean` 时调 `_clean(c)`；`nitpick` 时 `opts += " -n -W -T"`；`cmd = "sphinx-build..."` 用 `source or c.sphinx.source`、`target or c.sphinx.target`，`c.run(cmd, pty=True)`；`browse` 时调 `_browse(c)` |
| `doctest` | `@task` | `c` | `mkdtemp()` 建临时目录，调 `build(c, clean=True, target=tmpdir, opts="-b doctest")`，`finally: rmtree(tmpdir)` |
| `tree` | `@task` | `c` | `ignore = ".git|*.pyc|*.swp|dist|*.egg-info|_static|_build|_templates"`；`c.run('tree -Ca -I "..." <c.sphinx.source>')` |
| `sites` | `@task` | `c` | 构造 `docs_c`/`www_c` 两个 `Context(config=c.config.clone())` 并 `update(**...configuration())`；先 `hide=True` 静默构建两站，再以 `nitpick=True` 实际构建 |
| `watch_docs` | `@task` | `c` | 分别为 www 与 docs 构造 handler（`make_handler`），www 用 `www["build"]`，docs 用 `docs["build"]`；包名取自 `c.get("packaging",{}).get("package")` 或回退 `c.get("tests",{}).get("package")`；最后 `observe(www_handler, api_handler)` |

- Collection 结构（第 104-114 行）：
  - `ns = Collection(_clean, _browse, build, tree, doctest)`
  - `ns.configure({"sphinx": {...}})`，config 键：`sphinx.source`（`"docs"`）、`sphinx.target`（`join("docs", "_build")`）、`sphinx.target_file`（`"index.html"`）。
- 模块级子集合（第 122-139 行）：
  - 辅助函数 `_site(name, help_part)`：基于 `sys.modules[__name__]` 调用 `Collection.from_module(self, name=name, config={"sphinx": {"source": _path, "target": join(_path,"_build")}})`，并改写集合与 `coll["build"]` 的 `__doc__`。
  - `docs = _site("docs", "the API docs subsite.")`；`www = _site("www", "the main project website.")`。
- `build` 任务实际引用的配置键：`c.sphinx.source`、`c.sphinx.target`、`c.sphinx.target_file`（见上）。

### F-environment — `invocations/environment.py`

- 无 `@task`、无 `ns`。
- 顶层函数 `in_ci()`：遍历哨兵 `("CIRCLECI", "TRAVIS")`，`os.environ.get(sentinel, False)` 非空即返回 `True`，否则 `False`。

### F-pytest — `invocations/pytest.py`

- `from invoke import task`（第 5 行）。未定义 `ns`。

| 任务函数 | 装饰器 | 参数与默认值 | 函数体要点 |
|---|---|---|---|
| `test` | `@task` | `c, verbose=True, color=True, capture="sys", module=None, k=None, x=False, opts="", pty=True, warnings=True` | 组装 flags（`--verbose`/`--color=yes`/`--capture=`…）；`module` 非 None 时 `modstr = " tests/<m>.py"`；`c.run("pytest ...", pty=pty)`。`module`/`k`/`opts`/`pty` 等见 docstring |
| `integration` | `@task(help=test.help)` | `c, opts=None, pty=True, x=False, k=None, verbose=True, color=True, capture="sys", module=None` | `opts += " integration/"`；转发调用 `test(...)` |
| `coverage` | `@task(iterable=["additional_testers"])` | `c, report="term", opts="", tester=None, codecov=False, additional_testers=None` | 构造 `--cov --no-cov-on-fail --cov-report=<report>`；`(tester or test)(c, opts=my_opts)`；`additional_testers` 循环追加 `--cov-append`；`report=="html"` 时 `c.run("open htmlcov/index.html")`；`codecov` 时 `coverage xml` + `codecov` |

### F-testing — `invocations/testing.py`

- `from invoke import task`（第 5 行）；`from .watch import watch`（第 8 行）。未定义 `ns`。

| 任务函数 | 装饰器 | 参数与默认值 | 函数体要点 |
|---|---|---|---|
| `test` | `@task(help={...})` `help` 键含 `module/runner/opts/pty` | `c, module=None, runner=None, opts=None, pty=True` | `runner = runner or "spec"`；`args` 拼接 `--tests=tests/<module>.py`、`opts`、`--with-timing`；读 `c.config.get("tests",{}).get("logformat")`；`c.run(runner + args, pty=pty)` |
| `integration` | `@task(help=test.help)` | `c, module=None, runner=None, opts=None, pty=True` | `opts += " --tests=integration/"`；转发调用 `test(c, ...)` |
| `watch_tests` | `@task` | `c, module=None, opts=None` | 读 `c.config.get("tests",{}).get("package")` 决定 watchdog 模式；`c.config.run.warn = True` 后调 `test(c, **kwargs)`；再 `watch(c, test, patterns, [r".*/\..*\.swp"], **kwargs)` |
| `coverage` | `@task` | `c, html=True, integration_=True` | 先 `which coverage` 校验；`test_opts = "--with-coverage"`；`test(c, opts=test_opts)`；`integration_` 时 `integration(c, opts=test_opts)`；`html` 时 `c.run("coverage html && open htmlcov/index.html")` |
| `count_errors` | `@task` | `c, command, trials=10, verbose=False, fail_fast=False` | `tqdm(range(trials))` 循环 `c.run(command, hide=True, warn=True)`；统计 goods/bads、失败间隔 min/mean/mode/max；`fail_fast` 或 `result.exited == -2` 时 break |

- `tests` 配置键：`logformat`、`package`（由 `test` / `watch_tests` 读取）。

### F-util — `invocations/util.py`

- 无 `@task`。无 `ns`。
- 上下文管理器函数 `tmpdir(skip_cleanup=False, explicit=None)`：`tmp = explicit if explicit is not None else mkdtemp()`；`yield tmp`；`finally` 中若 `not skip_cleanup` 则 `rmtree(tmp)`。

### F-watch — `invocations/watch.py`

- 无 `@task`。无 `ns`。
- 顶层函数（均依赖 watchdog）：
  - `make_handler(ctx, task_, regexes, ignore_regexes, *args, **kwargs)`（第 9 行）：`args = [ctx] + list(args)`；尝试 `from watchdog.events import RegexMatchingEventHandler`，`ImportError` 时 `sys.exit("If you want to use this, 'pip install watchdog' first.")`；定义内部 `Handler` 类（`on_any_event` 中对 `BaseException` 静默 `pass`）；返回 `Handler(regexes=regexes, ignore_regexes=ignore_regexes)`。
  - `observe(*handlers)`（第 26 行）：`from watchdog.observers import Observer`（`ImportError` 同样 `sys.exit(...)`）；建 `Observer()`，对每个 handler `observer.schedule(handler, ".", recursive=True)`；`observer.start()`；`time.sleep(1)` 循环，`KeyboardInterrupt` 时 `stop()`，`join()`。
  - `watch(c, task_, regexes, ignore_regexes, *args, **kwargs)`（第 45 行）：`observe(make_handler(c, task_, regexes, ignore_regexes, *args, **kwargs))`。

### F-packaging.__init__ — `invocations/packaging/__init__.py`

- 第 2-3 行：`from .vendorize import vendorize`；`from . import release`。
- 第 7 行：`ns = release`（指向 `release` 模块的 Collection）。末尾含 `# flake8: noqa`。

### F-release — `invocations/packaging/release.py`

- `from invoke import Collection, Exit, task`（第 26 行）。
- 模块级导入：`blessings.Terminal`、`build._builder._read_pyproject_toml`、`docutils.utils.Reporter`、`pip.__version__ as pip_version`、`releases.util.parse_changelog`、`tabulate.tabulate`、`twine.commands.check.check as twine_check`、`..console.confirm`、`..environment.in_ci`、`..util.tmpdir`、`.semantic_version_monkey.Version` 等。
- 模块级全局：`t = Terminal()`；`check = "✔"`；`ex = "✘"`；`Release = Enum("Release", "BUGFIX FEATURE UNDEFINED")`；枚举类 `Changelog`/`VersionFile`/`Tag`（值均为带颜色/符号的状态文案）；正则 `BUGFIX_RE = r"^\d+\.\d+$"`、`BUGFIX_RELEASE_RE = r"^\d+\.\d+\.\d+$"`、`FEATURE_RE = r"^(main|master)$"`；异常类 `UndefinedReleaseType(Exception)`。
- 模块加载时（第 47-48 行）对 `readme_renderer.rst.SETTINGS`（`halt_level`、`report_level`）赋 `Reporter.INFO_LEVEL`。
- **`@task` 任务函数**：

| 任务函数 | 装饰器 | 参数与默认值 | 函数体要点 |
|---|---|---|---|
| `status` | `@task` | `c` | 调 `_converge(c)` 得 `(actions, state)`；`tabulate` 打印 `changelog/version/tag` 各行；`return actions, state` |
| `all_` | `@task(name="all", default=True)` | `c, dry_run=False` | 依次 `prepare(c, dry_run=dry_run)`、`publish(c, dry_run=dry_run)`、`push(c, dry_run=dry_run)` |
| `prepare` | `@task` | `c, dry_run=False` | 调 `status(c)`（`UndefinedReleaseType` 且非 dry-run 时 `raise`，否则 `Exit(0,"Can't dry-run...")`）；`actions.all_okay` 时 `return True`；非 dry-run 时 `confirm(...)` 否则 `Exit("Aborting.")`；据 `actions` 执行 `$EDITOR` 编辑 changelog / pyproject.toml / git tag 等（均带 `dry=dry_run`）；末尾复检 `status(c)`，非 all_okay 时 `Exit("Something went wrong! Please fix.")` |
| `build` | `@task` | `c, sdist=True, wheel=True, directory=None, python=None, clean=False, opts: Optional[str] = None` | 读 `c.config.get("packaging", {})` 覆盖 `sdist/wheel/clean/directory/python`；`print(f"Building into {directory}...")`；`parts = [python, "-m build"]` 拼 `--outdir`/`--sdist`/`--wheel`/`opts`；`clean` 时 `rmtree(directory)` 与 `rmtree(Path.cwd()/"build")`；`c.run(" ".join(parts))`；`ls -l <directory>`。`sdist`+`wheel` 均 False 时 `Exit("You said no sdists...")` |
| `publish` | `@task` | `c, sdist=True, wheel=True, index=None, sign=False, dry_run=False, directory=None` | `c.config.run.hide/echo` 设 False/True；`index`/`sign` 覆盖读 `packaging` 配置；`with tmpdir(skip_cleanup=dry_run, explicit=directory) as tmp:` 内 `partial(build, c, ...)` 构建；`rebuild_with_env` 配置存在时设临时环境变量重构建；`twine_check(dists=[os.path.join(tmp,"*")])` 失败 `Exit(1)`；`test_install(c, directory=tmp)`；`upload(c, directory=tmp, index=index, sign=sign, dry_run=dry_run)` |
| `test_install` | `@task` | `c, directory, verbose=False, skip_import=False` | `venv.EnvBuilder(with_pip=True)`；`get_archives(directory)` 为空 `Exit(...)`；`tmpdir()` 内建 venv、`pip install pip==<pip_version>`、`pip install --disable-pip-version-check <archive>`；`not skip_import` 时 `_find_package(c)` 并 `python -c 'import <package>'`；若 `<package>/py.typed` 存在再 `pip install mypy` 与 `mypy -c 'import <package>'` |
| `upload` | `@task` | `c, directory, index=None, sign=False, dry_run=False` | `get_archives(directory)`；`sign` 时用 `find_gpg(c)` 定位 gpg（找不到 `Exit("You need to have one of `gpg`, `gpg1` or `gpg2`...")`），`getpass.getpass(prompt)` 取口令后逐档 `--detach-sign`；组装 `twine upload` 命令；`dry_run` 时 `print("Would publish via: ...")` + `ls -l <paths>`，否则 `c.run(cmd)` |
| `push` | `@task` | `c, dry_run=False` | `opts = "--follow-tags --no-verify"`；`dry_run` 时 `kwargs["echo"]=True`，`in_ci()` 为真则 `kwargs["dry"]=True` 否则 `opts += " --dry-run"`；`c.run("git push {}".format(opts), **kwargs)` |

- **非任务公共/辅助函数**：
  - `_converge(c)`：返回 `(actions, state)`，`state` 为 `Lexicon`（含 `branch/release_type/changelog/latest_line_release/latest_overall_release/unreleased_issues/current_version/tags/latest_version/next_version/expected_version`）；`actions` 为 `Lexicon`（`changelog/version/tag/all_okay`）。
  - `find_gpg(c)`：在 `"gpg gpg1 gpg2"` 中 `which` 探测，返回存在的候选名（否则返回 `None`）。
  - `get_archives(directory: Union[str, Path]) -> list[Path]`：`sorted(target.glob("*.whl")) + sorted(target.glob("*.tar.gz"))`。
  - 私有内部函数：`_release_line(c)`、`_latest_feature_bucket(changelog)`、`_versions_from_changelog(changelog)`、`_release_and_issues(changelog, branch, release_type)`、`_get_tags(c)`、`_latest_and_next_version(state)`、`_find_package(c)`。
- Collection 结构（第 914-926 行）：
  - `ns = Collection("release", all_, status, prepare, build, publish, push, test_install, upload)`
  - `ns.configure({"run": {"hide": "stdout"}})`。
- **说明**：本模块未定义任何名为 `success`/`timed` 的 `@task` 装饰器或辅助函数（对 `def (success|timed)(` 的检索在整包内无匹配）。

### F-vendorize — `invocations/packaging/vendorize.py`

- `from invoke import task`（第 8 行）。

| 任务函数 | 参数与默认值 | 函数体要点 |
|---|---|---|
| `vendorize` | `c, distribution, version, vendor_dir, package=None, git_url=None, license=None` | `tmpdir()` 内 `package = package or distribution`；`target = Path(vendor_dir)/package`；`_unpack(...)` 解包；校验 `source_package.exists()` 否则 `ValueError`；`target` 存在则 `rmtree(target)`；`copytree(source_package, target)`；`license` 给定时 `copy(l_, target)` |

- 私有辅助函数 `_unpack(c, tmp, package, version, git_url=None)`：`git_url` 真时暂为空实现（`pass`）；否则 `pip install --download=. --build=build --no-use-wheel <package>==<version>`，按 `zip/tgz/tar.gz` 后缀识别归档并解压；返回 `(real_version, source)`。
- 本模块未定义 `ns`（`packaging/__init__.py` 通过 `from .vendorize import vendorize` 直接导入该任务函数，而非经 Collection）。

### F-semantic_version_monkey — `invocations/packaging/semantic_version_monkey.py`

- 无 `@task`。无 `ns`。
- `from semantic_version import Version`（第 9 行）。
- 定义且**在模块级挂到 `Version` 上**的方法（jit/monkey-patch）：
  - `clone(self)` → `return Version(str(self))`；挂载 `Version.clone = clone`。
  - `next_minor(self)` → `self.clone()` 后 `clone.minor += 1; clone.patch = 0`；挂载 `Version.next_minor = next_minor`。
  - `next_patch(self)` → `self.clone()` 后 `clone.patch += 1`；挂载 `Version.next_patch = next_patch`。

---

## 4. Collection 结构总览

| 文件 | `ns` 定义 | `ns.configure(...)` config 键 | 成员任务 |
|---|---|---|---|
| `checks.py` | 未定义 `ns` | — | （不自动注册）`blacken`/`lint`/`all_` |
| `ci.py` | `Collection(make_sudouser, sudo_run, make_sshable)` | `ci.sudo.{user,password,groups}` | `make_sudouser`/`sudo_run`/`make_sshable` |
| `docs.py` | `Collection(_clean, _browse, build, tree, doctest)`（另建模块级子集合 `docs`、`www`） | `sphinx.{source,target,target_file}` | `clean`(=`_clean`)/`browse`(=`_browse`)/`build`/`tree`/`doctest`/`sites`/`watch_docs` |
| `pytest.py` | 未定义 `ns` | — | `test`/`integration`/`coverage` |
| `testing.py` | 未定义 `ns` | — | `test`/`integration`/`watch_tests`/`coverage`/`count_errors` |
| `packaging/__init__.py` | `ns = release`（即 `release` 的 Collection） | 同 `release` | 见下 |
| `packaging/release.py` | `Collection("release", all_, status, prepare, build, publish, push, test_install, upload)` | `run.hide = "stdout"`；另读 `packaging.{changelog_file,package,index,sign,sdist,wheel,clean,directory,python,rebuild_with_env}` | `all`(=`all_`)/`status`/`prepare`/`build`/`publish`/`push`/`test_install`/`upload` |
| `packaging/vendorize.py` | 未定义 `ns` | — | `vendorize`（被 `packaging/__init__.py` 直接导入） |

集合注册方式汇总：
- `ci.py`、`docs.py`、`packaging/release.py` 通过在模块级定义 `ns = Collection(...)` 自动注册任务。
- `packaging/__init__.py` 复用 `release` 的 Collection 作为自身 `ns`，并将 `vendorize` 任务直接导入供使用。
- `checks.py`、`pytest.py`、`testing.py`、`vendorize.py`、`console.py`、`environment.py`、`util.py`、`watch.py`、`autodoc.py` 均**未定义模块级 `ns`**（其中 `autodoc.py` 本身不含 `@task`，`console/environment/util/watch` 亦无 `@task`）。

---

## 附注：任务参数默认值精度说明

- 所有 `@task` 函数与其参数默认值均逐字取自源码函数签名。
- `docs.build`、`testing.test`、`pytest.test` 等任务带显式 `help={...}` 字典，键名见各节。
- `ci.py`、`packaging/release.py` 的 `ns.configure(...)` 为模块加载期确定的固定配置；`checks.py`/`pytest.py`/`testing.py` 等的配置读取发生在任务函数体内（`c.config.get(...)`、`c.<key>`），并非由 `ns.configure` 预设。