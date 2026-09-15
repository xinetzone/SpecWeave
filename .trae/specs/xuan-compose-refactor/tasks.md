# xuan-compose：podman-compose 单体重构进 xuanspace/libs - 实施计划

> 切片策略：自底向上垂直切片，每片"实现 + 对应上游单元测试移植 + 本层门禁证据"同时交付。
> 方法纪律：翻译式搬迁（translate-then-move），每一片禁止顺手重写算法；Python 3.14 必需的兼容性最小修复须登记到差异表（T10 汇总）。
> 全部产物路径：`projects/xuanspace/libs/xuan-compose/`；每片完成后运行本层 `ruff check`、`mypy`、`pytest -q`。

## Task 1: 子项目脚手架与 GPL-2.0 合规基线

- **Status**: `pending`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 `libs/xuan-compose/` 目录树：`src/xuan_compose/`、`tests/`。
  - 编写 `pyproject.toml`：scikit-build-core 后端（纯 Python，无 cmake 段，`wheel.packages=["src/xuan_compose"]`、`build-dir="build/{wheel_tag}"`、`minimum-version="0.10"`）；PEP 621 元数据（name=`xuan-compose`、requires-python=`>=3.14.6`、deps `pyyaml`/`python-dotenv`、optional test 组 `pytest`/`pytest-cov`/`parameterized`）；**不写** `[project.scripts]`；ruff 继承根配置（line 120、py314、select E/W/F/I/UP）；mypy；pytest `pythonpath=["src"]`、testpaths=["tests"]。
  - 复制上游 GPL-2.0-only `LICENSE` 全文；创建 `README.md` 骨架（安装、占位用法、架构占位、"Derived from containers/podman-compose v1.6.0" 署名、上游 URL、pinned commit、GPL 说明）；`CHANGELOG.md` 记 0.1.0。
  - 创建 `src/xuan_compose/__init__.py`（`__version__="1.6.0+xuan.0.1.0"` 风格派生版本、SPDX 头）、`py.typed`。
  - py314 环境验证可编辑安装与导入；记录 PDM workspace 识别证据。
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `rule` TR-1.1：`pip install -e libs/xuan-compose`（py314）成功且 `python -c "import xuan_compose; print(xuan_compose.__version__)"` 退出码 0；证据=命令输出。
  - `rule` TR-1.2：pyproject.toml 含全部必需字段且不含 `[project.scripts]`；证据=文件内容 grep 结果。
  - `rule` TR-1.3：LICENSE 与 `vendor/podman-compose/LICENSE` hash 一致；署名段含上游 URL 与 `git -C vendor/podman-compose rev-parse HEAD` 的 commit；证据=hash 对比输出与 README 段落。
  - `rule` TR-1.4：新建 `.py` 文件 100% 携带 `SPDX-License-Identifier: GPL-2.0-only` 头；证据=扫描命令输出。
- **Notes**: 派生版本号建议 `1.6.0+xuan0` 形式，表明上游基线；最终格式实现时确定并登记。

## Task 2: 基础层——compat / errors / types / logging_utils / interpolation / envfile

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 搬迁 `errors.py`（`PodmanComposeError`）、`compat.py`（`is_list/is_relative_ref/filteri/try_int/try_float/str_to_seconds/ver_as_list/strverscmp_lt/try_parse_bool`、ntpath/posixpath 交叉 isabs）、`types.py`（`Service` 等类型别名、`DependField`）、`logging_utils.py`（模块 logger 与着色常量/函数）。
  - 搬迁 `interpolation.py`：`var_interpolate` 及其内部 tokenizer（`$VAR`、`${VAR}`、`:-/-/:?/?` 全部语法），逐行翻译为 py314 现代写法（去 overload 冗余处保持签名等价）。
  - 搬迁 `envfile.py`：`dotenv_to_dict`。
  - 移植测试：`tests/unit/test_var_interpolate.py`、`test_rec_subs.py`（rec_subs 如归入 normalize 则该测试随 T3，本任务只搬 interpolation 相关用例——按目标归属执行，禁止重复）。
  - 新增导入无副作用冒烟测试：import 包不触碰 `sys.argv`、不启动进程。
- **Acceptance Criteria Addressed**: AC-3, AC-5, AC-7, AC-11, AC-12
- **Test Requirements**:
  - `rule` TR-2.1：移植后的 test_var_interpolate 全部用例通过、零 skip；证据=pytest 输出（用例数与上游一致）。
  - `rule` TR-2.2：`python -c "import xuan_compose, xuan_compose.interpolation"` 过程中无子进程产生、无 `sys.argv` 读取（静态检查 `sys.argv` 仅出现在 cli/__main__）；证据=grep + 冒烟测试。
  - `rule` TR-2.3：`ruff check src/xuan_compose tests` 与 `mypy src/xuan_compose` 退出码 0；证据=命令输出。
  - `rubric` TR-2.4：现代化程度；1-5；1=保留 future annotations/旧式 Union；3=语法现代但注解残缺；5=全面 py314 惯用法 + 完整注解；阈值 ≥4；证据=代码审查。

## Task 3: 规范层——normalize / merge / discovery

- **Status**: `done`（2026-09-15 验收）
- **Priority**: high
- **Depends On**: Task 2
- **完成记录**：
  - WSL py3.14 权威门禁：121 passed / 0 skip（含 T2 的 50 例）；ruff、mypy 均零错误；层间边扫描无 runner/engine/commands/cli 依赖；merge↔normalize 双平台导入无环。
  - TR-3.1 范围调整（经计划口径确认）：① `test_include.py` 整体依赖引擎 `_parse_compose_file`（上游 2852-2887 行），随 **T6** 迁移；② `test_normalize_final_build.py` 本轮只移植 2 个纯函数方法（18 例），另 2 个引擎方法（23 例）随 T6 迁入 `test_parse_compose_file_build.py`，数据与断言原样保留。拆分说明已写入测试模块 docstring。
  - `!override`/`!reset` 采用上游等价行为（YAMLObject 全局注册副作用保留；包根不导入 merge，包导入无副作用），差异登记入 T10 差异表，未做显式注册函数改造。
  - 权威测试门禁平台为 WSL Python 3.14（POSIX 路径语义，与上游 CI 一致）；Windows 原生 109/121，12 例失败全部为 `\`/`/` 与盘符根的平台路径差异，非逻辑差异，已写入 README。
- **Description**:
  - `normalize.py`：`rec_subs`、`norm_as_list/norm_as_dict/norm_ulimit`、`normalize_service/normalize/normalize_service_final/normalize_final`。
  - `merge.py`：`clone/rec_merge_one/rec_merge`、`OverrideTag/ResetTag`（YAMLObject 注册）、`load_yaml_or_die`、`resolve_extends`。
  - `discovery.py`：`find_compose_files_recursively`。
  - 移植测试：`test_rec_subs.py`、`test_normalize_service.py`、`test_normalize_final_build.py`、`test_normalize_depends_on.py`、`test_rec_merge_depends_on.py`、`test_include.py`。
  - 注意：`!override_tag`/`!reset_tag` 的 YAML 注册时序改为显式注册函数，避免 import 副作用污染全局 yaml.Loader（若上游依赖全局注册则保留等价行为并在差异表登记）。
- **Acceptance Criteria Addressed**: AC-3, AC-5, AC-7, AC-9, AC-11
- **Test Requirements**:
  - `rule` TR-3.1：6 个移植测试文件全部通过、零 skip，用例数与上游一致；证据=pytest 输出。
  - `rule` TR-3.2：normalize/merge/discovery 不 import runner/cli 层（层间边检查）；证据=静态 import 扫描。
  - `rule` TR-3.3：ruff/mypy 退出码 0；证据=命令输出。

## Task 4: 执行层与值对象——runner / model / dependencies

- **Status**: `done`（2026-09-15 验收）
- **Priority**: high
- **Depends On**: Task 2
- **完成记录**：
  - WSL py3.14 权威门禁：145 passed / 0 skip（较 T3 新增 24 例：condition 5 + depends_on 9 + pull_image 10）；Windows 原生仍仅 T3 那 12 例路径分隔符失败，T4 新例全绿。
  - 模块：`runner.py`（Podman/ExistingContainer/wait_with_timeout，并再导出 CalledProcessError 作为子进程异常统一入口）、`model.py`（ServiceDependencyCondition 现代化为 StrEnum——差异表已记、ServiceDependency、PullImageSettings dataclass 原样保留）、`dependencies.py`（rec_deps/calc_dependents/flat_deps + check_dep_conditions/_validate_completed_successfully，后两者上游位于 up 命令辅助区，按 test_depends_on.py 归属提前迁入；compose 形参为 Any 鸭子类型，执行层不反向依赖引擎层）。
  - 范围微调：`pull.py`（PullImageSettings 之外的 settings_to_pull_args/pull_image/pull_images）与 `translate/run_args.py` 的 `is_local` 蓝图属 T6/T5，因 test_pull_image.py 直接依赖提前落地，T6 仅补 prepare_images 等引擎装配函数。
  - TR-4.2 证据：全包 `import subprocess` 仅命中 runner.py（另一条命中是注释行）。
  - py3.14 现代化（记 T10 差异表）：①全包移除 `from __future__ import annotations`（PEP 649 下 3.14 注解默认惰性，8 个文件）；②`wait_with_timeout` 的 `except asyncio.TimeoutError as exc: raise TimeoutError from exc` 收敛为 `except TimeoutError: raise`（3.11+ 两者同一类型，ruff UP041）；③`asyncio.exceptions.IncompleteReadError/LimitOverrunError` 收敛为 `asyncio.*` 限定名。
  - runner.py 覆盖率 16% 属预期：与上游一致，Podman 子进程封装无单元测试（需真实 podman 守护的集成测试不在本库门禁，见 README）；T9 总门按"关键模块 90%/整体 80%"口径时 runner 作为 I/O 边界单列说明。
- **Description**:
  - `runner.py`：`Podman`（同步/异步 exec、output、信号量、dry_run、版本探测）与 `ExistingContainer`；构造函数显式传入引擎引用与参数，消除全局单例引用。
  - `model.py`：`ServiceDependencyCondition`、`ServiceDependency`、`PullImageSettings`（保留 dataclass）。
  - `dependencies.py`：`rec_deps/calc_dependents/flat_deps`。
  - 移植测试：`test_service_dependency_condition.py`、`test_depends_on.py`、`test_pull_image.py`。
- **Acceptance Criteria Addressed**: AC-3, AC-5, AC-7, AC-9
- **Test Requirements**:
  - `rule` TR-4.1：3 个移植测试文件全部通过；证据=pytest 输出。
  - `rule` TR-4.2：runner 是包内唯一 import subprocess/asyncio.subprocess 的模块（允许 logging_utils 等无关标准库）；证据=import 扫描（grep "import subprocess" 命中文件清单）。
  - `rule` TR-4.3：ruff/mypy 退出码 0；证据=命令输出。

## Task 5: 翻译层——translate 子包

- **Status**: `done`（2026-09-15 验收，未提交，等用户原子提交指令）
- **Priority**: high
- **Depends On**: Task 3, Task 4
- **完成记录**：
  - WSL py3.14 权威门禁：**401 passed / 0 skip**（T4 基线 145 + T5 新增 256）；Windows 原生 374 passed / 27 failed，27 例全部是已登记的 POSIX 路径分隔符/HOME 语义平台差异（见下条），无逻辑回归。
  - TR-5.1 逐文件用例数对照（`pytest --collect-only` 实测，11 个交付文件共 256 例，与上游同文件用例数逐一相等）：

    | 移植测试文件 | 用例数 | 覆盖生产符号 |
    |---|---:|---|
    | test_volumes.py | 1 | mounts.parse_short_mount |
    | test_get_network_create_args.py | 11 | networks.get_network_create_args |
    | test_get_net_args.py | 31 | networks.get_net_args 全分支 |
    | test_container_to_args.py | 78 | container_args.container_to_args（最大函数 L1344-1622） |
    | test_container_to_args_secrets.py | 25 | secrets.get_secret_args（env/file/external 三分支） |
    | test_container_to_build_args.py | 20 | build.container_to_build_args/adjust_build_ssh_key_paths |
    | test_compose_cp_args.py | 3 | run_args.compose_cp_args |
    | test_compose_exec_args.py | 2 | run_args.compose_exec_args |
    | test_compose_run_update_container_from_args.py | 6 | run_args.compose_run_update_container_from_args |
    | test_compose_run_log_format.py | 11 | runner.Podman._format_stream（生产实现 T4 已落地，测试随 T5 交付） |
    | test_is_context_git_url.py | 68 | build.is_context_git_url（从 normalize 再导出） |

  - **3 个上游测试文件延期，不落地 tests/（故不计入收集、不产生 skip）**：
    - `test_can_merge_build.py`（38 例）→ **延 T6**：上游不存在 `can_merge_build` 符号，实际测引擎 `_parse_compose_file`/`original_configuration` 的 merge 行为；
    - `test_build_deps.py`（4 例）→ **延 T6**：测引擎 `_resolve_context_dependencies(services)`；
    - `test_compose_up_args.py`（2 例）→ **延 T7**：测 CLI `_parse_args`。
    - 三文件合计 44 例，延期理由为被测符号属引擎/CLI 层（沿用 T3 延 test_include.py 的登记先例）；TR-5.1 口径相应由"14 文件"调整为"11 文件 + 3 文件显式延期"。
  - 生产模块：`ports.py`（port_dict_to_str/norm_ports）、`resources.py`（ulimit 三函数 + res/gpu/cpu，pids_limit 一致性检查原样）、`mounts.py`（模块级 dir_re/propagation_re + 9 个符号）、`networks.py`（6 个符号，invalid network_mode 保留 `log.fatal`+`sys.exit(1)`）、`secrets.py`（get_secret_args）、`build.py`（container_to_build_args/adjust_build_ssh_key_paths，并从 normalize 再导出 is_context_git_url）、`container_args.py`（container_to_args 逐行翻译，约 280 行）、`run_args.py`（is_local T4 已落地，T5 追加 get_excluded/deps_from_container/get_service_info/get_volume_names/compose_run_update_container_from_args/compose_cp_args/compose_exec_args 共 7 函数）。
  - 上游符号勘误：`_add_build` 是 `compose_build` handler 内依赖局部 `pending_builds` 的闭包（属 T7 命令层），`can_merge_build` 在上游不存在——两者均未翻译，与延期测试归属一致。
  - **测试翻译发现并纠正 1 处生产翻译偏差**：初译把 `cnt["environment"] = env` 误移出 `if args.env:` 块（上游 L4610 在块内），run_update 4 例即时失败暴露，已按上游缩进修正后全绿。
  - 测试夹具策略变更（相对摘要计划的微调）：未新建 `tests/fixtures/` 数据文件；test_container_to_args.py 在模块导入时于系统临时目录构建等价 `REPO_ROOT`（含 project-1.env/project-2.env 的逐字节副本），`compose.dirname` 取绝对路径复现上游"仓根+test_dirname"的 realpath 拼接语义；build ssh 测试保留上游本地 mock 的相对 `dirname="test_dirname"`（该路径只 join 不 realpath）。test_compose_run_update 按 tasks.md 许可以 MinimalCompose 最小 stub 替代真实 PodmanCompose（仅需 project_name/format_name）。
  - TR-5.2 证据：对 translate/ 执行 `grep -E '^\s*(from|import)\s+.*\b(engine|commands|cli|subprocess)\b'` 命中 0（另有 2 条仅注释文本命中）；实际依赖仅 compat/types/normalize/merge/model/errors/envfile/logging_utils/runner（再导出的 CalledProcessError，不在 translate 直接 import subprocess）及同包子模块。
  - TR-5.3：`ruff check src tests` 全过（含修复 2 处 I001 导入排序）、`mypy src` 0 issue（23 源文件）。
  - Windows 27 例失败构成：T3/T4 既有 12 例（normalize 路径拼接）+ T5 新增 15 例——bind mount HOME 展开 1、file secret realpath 7、build ssh 路径拼接/HOME 5、containerfile 探测 join 1、parse_short_mount POSIX 绝对路径 1；均为 `\`/`/`、盘符根或 Windows expanduser 不读 HOME 的平台语义（README"测试"节已声明该类别，上游在 Windows 同构）。
  - py3.14 现代化（记 T10 差异表）：①上游 `PodmanCompose` 嵌套 `Enum`（XPodmanSettingKey，6 键）提层为 model.py 的模块级 `StrEnum`，测试改从 xuan_compose.model 导入；②build.py cleanup_callbacks 注解 `list[Callable[[], object]]`、测试 `Union[...]`→`... | None`；③translate 层 compose/cnt 句柄统一 `Any` 鸭子类型，为 T6 引擎装配留解耦面。
- **Description**:
  - `translate/mounts.py`：`parse_short_mount/fix_mount_dict/mount_desc_to_mount_args/mount_desc_to_volume_args/get_mnt_dict`。
  - `translate/networks.py`：`default_network_name_for_project/get_network_create_args/get_net_args_from_network_mode/get_net_args/get_net_args_from_networks`。
  - `translate/ports.py`：`port_dict_to_str/norm_ports`。
  - `translate/resources.py`：`container_to_res_args/container_to_gpu_res_args/container_to_cpu_res_args/ulimit*`。
  - `translate/secrets.py`：`get_secret_args`。
  - `translate/build.py`：`is_context_git_url/adjust_build_ssh_key_paths/container_to_build_args/_add_build/can_merge_build`（如存在）。
  - `translate/run_args.py`：`get_excluded/deps_from_container/get_service_info/get_volume_names/is_local/compose_run_update_container_from_args/compose_cp_args/compose_exec_args`。
  - 移植测试：`test_volumes.py`、`test_get_network_create_args.py`、`test_get_net_args.py`、`test_container_to_args.py`、`test_container_to_args_secrets.py`、`test_container_to_build_args.py`、`test_can_merge_build.py`、`test_build_deps.py`、`test_compose_cp_args.py`、`test_compose_exec_args.py`、`test_compose_run_update_container_from_args.py`、`test_compose_run_log_format.py`、`test_compose_up_args.py`、`test_is_context_git_url.py`。
  - 上游测试中对 `PodmanCompose` 的轻量构造改用测试夹具/最小 stub，保持断言语义。
- **Acceptance Criteria Addressed**: AC-3, AC-5, AC-7, AC-8, AC-9
- **Test Requirements**:
  - `rule` TR-5.1：14 个移植测试文件全部通过、零 skip；证据=pytest 输出（逐文件用例数对照上游）。
  - `rule` TR-5.2：translate 包只依赖 compat/types/normalize/merge/model，不 import engine/commands/cli；证据=import 扫描。
  - `rule` TR-5.3：ruff/mypy 退出码 0；证据=命令输出。

## Task 6: 引擎层——engine / pull / logs

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - `engine.py`：以 `PodmanCompose` 为蓝本实现 `ComposeEngine`——状态字段、`assert_services/get_podman_args/config_hash/original_configuration/resolve_pod_name/resolve_pod_args/join_name_parts/format_name/_parse_x_podman_settings/_parse_compose_file/_resolve_profiles/_resolve_context_dependencies`；`_parse_args/run` 的命令分发职责移交 cli（保留引擎所需的纯解析辅助）。
  - `pull.py`：拉取策略编排与 `settings_to_pull_args` 相关异步流程。
  - `logs.py`：`create_format_logs_task/_task_cancelled` 与日志流着色编排。
  - 引擎构造显式化：`ComposeEngine()` 可独立实例化、可注入 runner；命令表不再于构造时被装饰器填充。
  - 新增引擎实例化冒烟测试（无 argv/无进程/多实例隔离）。
- **Acceptance Criteria Addressed**: AC-3, AC-7, AC-9, AC-11, AC-12
- **Test Requirements**:
  - `rule` TR-6.1：实例化两个 `ComposeEngine` 状态互不污染；实例化过程零子进程；证据=冒烟测试输出。
  - `rule` TR-6.2：engine 不 import cli/commands（commands 可 import engine，方向单向）；证据=import 扫描。
  - `rule` TR-6.3：ruff/mypy 退出码 0；证据=命令输出。
  - `rubric` TR-6.4：单例解耦彻底度；1-5；1=仍存在模块级活引擎；3=主路径显式但残留全局状态；5=全部装配显式、无残留全局可变单例；阈值 ≥4；证据=代码审查 + grep。

## Task 7: 命令层——22 个 handler 与显式注册表

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 按 `commands/` 蓝图搬迁全部 handler：version、wait、systemd、pull/push、build（含 build_one）、up、down、ps、run、cp、exec、start/stop/restart、logs、config、port、pause/unpause、kill、stats、images、ls。
  - 用显式 `COMMAND_HANDLERS: dict[str, Handler]` 替代 `@cmd_run` 对全局单例的副作用注册；装饰器可保留为注册该表的薄语法糖，但禁止模块导入时触碰引擎实例。
  - handler 签名保持 `async def handler(engine, args)` 等价，便于逐行对照。
- **Acceptance Criteria Addressed**: AC-3, AC-7, AC-9, AC-11
- **Test Requirements**:
  - `rule` TR-7.1：22 命令名全部在 COMMAND_HANDLERS 中可枚举，与上游 `@cmd_run` 清单集合相等；证据=集合对比测试输出。
  - `rule` TR-7.2：导入 commands 包不产生引擎实例/子进程；证据=冒烟测试。
  - `rule` TR-7.3：ruff/mypy 退出码 0；证据=命令输出。

## Task 8: CLI 层——parser / main / __main__

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 7
- **Description**:
  - `cli/parser.py`：全局 parser、`_init_global_parser` 与全部 `compose_*_parse`（24 处注册，含共享 parser 的 down/stop/restart、build/up 等组合）；显式 parser 注册表替代 `@cmd_parse` 单例副作用。
  - `cli/main.py`：装配 runner/engine、podman 版本探测、compose 文件加载条件（version/systemd 例外）、handler 分发、退出码处理。
  - `__main__.py`：`python -m xuan_compose` 入口。
  - 移植测试：`test_parse_args.py`、`test_main.py`（按新装配方式调整夹具，断言语义不变）。
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-5, AC-7, AC-12
- **Test Requirements**:
  - `rule` TR-8.1：对 22 命令逐一执行 `python -m xuan_compose <cmd> --help` 退出码 0；证据=批量脚本输出。
  - `rule` TR-8.2：移植 test_parse_args.py、test_main.py 全部通过；证据=pytest 输出。
  - `rule` TR-8.3：`sys.argv` 引用仅存在于 cli/ 与 __main__.py；证据=grep。
  - `rule` TR-8.4：ruff/mypy 退出码 0；证据=命令输出。

## Task 9: 全量对等门禁——argparse 对等测试 / 覆盖率 / lint 总门

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 新增 `tests/test_cli_parity.py`：程序化枚举新旧 parser（通过 importlib 从 vendor 路径加载上游仅用于对比，或手工快照上游参数表——优先不依赖 vendor 路径的快照方案，快照生成脚本入 tests/ 并附生成说明），断言 option strings/action/default/nargs/required 完全一致（prog 除外）。
  - 新增 `tests/test_command_surface.py`：命令集合与 help 快照对等。
  - 覆盖率补齐：对未达标的核心模块（interpolation/normalize/merge/translate/engine ≥90%、整体 ≥80%）补针对性测试（基于上游真实分支，禁止无意义凑数）。
  - 全量门禁：`ruff check`、`mypy src`、`pytest --cov` 在 py314 一次过；记录命令与输出。
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-7, AC-8, AC-11
- **Test Requirements**:
  - `rule` TR-9.1：argparse 对等测试通过、零差异；证据=pytest 输出 + 快照文件。
  - `rule` TR-9.2：27 个上游测试文件在新库 tests/ 中均有对应且全部通过，总用例数 ≥ 上游、skip=0；证据=pytest 汇总与文件清单对照。
  - `rule` TR-9.3：coverage 报告核心模块 ≥90%、包整体 ≥80%；证据=`--cov-report=term-missing` 输出。
  - `rule` TR-9.4：ruff/mypy 全量退出码 0；证据=命令输出。

## Task 10: 对等审计与文档收尾——符号映射表 / 差异登记 / README / CHANGELOG

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 9
- **Description**:
  - 产出符号映射表（README 附录或 `docs/parity.md`，位于子项目内）：上游约 145 个公开符号 → 新模块/新名；标注删除项（仅限模块级 `script` 副作用与单例本身）与重命名项（如 PodmanCompose→ComposeEngine）。
  - 差异登记表：每条 Python 3.14 兼容修复/机械现代化记录上游行号、变更内容、行为等价理由。
  - 完成 README：安装、库 API 快速开始、`python -m` CLI、Mermaid 架构分层图、与上游关系/GPL、测试方法、集成测试手工验证（WSL+podman）说明。
  - CHANGELOG 完稿；逐文件 SPDX 头复扫。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-10, AC-11, AC-13
- **Test Requirements**:
  - `rule` TR-10.1：映射表条目数 = 上游公开符号总数（脚本统计），无遗漏；证据=统计输出。
  - `rule` TR-10.2：全部 `.py` SPDX 头覆盖率 100%；README 署名三要素齐备；证据=扫描输出。
  - `rubric` TR-10.3：行为等价可信度；1-5；1=断言被删改/差异无登记；3=通过但有未登记微调；5=零削弱 + 差异逐条可回溯上游行号；阈值 ≥4；证据=映射表/差异表审查。
  - `rubric` TR-10.4：文档完备性；1-5；锚点 1=缺安装/用法/许可；3=要素齐但无架构图或示例不可运行；5=全部要素齐且快速开始可照做成功；阈值 ≥4；证据=文档审查。

## Task 11: V 对抗审查（独立 reviewer，fresh context）与修复闭环

- **Status**: `pending`
- **Priority**: high
- **Depends On**: Task 10
- **Description**:
  - 由全新上下文的独立 reviewer 执行只读审查：① 22 命令/145 符号对等抽查深读；② 分层依赖反向边扫描；③ 移植测试保真性 diff 比对；④ 五攻击者视角（安全/边界/完整性/时序/模糊）审查 runner/engine；⑤ GPL 合规；⑥ py314 现代化。
  - 审查结果写入 `review.md`；fail 则每个可执行发现物化为 pending issue 并回到 Implement 修复，修复后重新发起新一轮 V。
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-6, AC-9, AC-10, AC-12
- **Test Requirements**:
  - `rule` TR-11.1：`git -C vendor/podman-compose status --porcelain` 为空；证据=命令输出。
  - `rule` TR-11.2：review.md 每个 AC 均有独立证据，最终 Review result=pass；证据=review.md。
  - `rubric` TR-11.3：分层单向性最终评分；1-5；阈值 ≥4；证据=review.md CP 结论。
  - `rubric` TR-11.4：对抗审查实质度；1-5；1=表演式通过；3=有发现但修复不彻底；5=多视角具体发现 ≥5 条且全部闭环并回归；阈值 ≥4；证据=review.md 发现清单与回归记录。

## Task 12: C 阶段——原子提交建议序列（仅用户批准后执行）

- **Status**: `pending`
- **Priority**: medium
- **Depends On**: Task 11
- **Description**:
  - 按切片产出 Conventional Commits 提交建议（中文主体、`feat(xuan-compose): ...` 序列），在 xuanspace 子模块内提交；不自动执行，待用户明确批准。
  - 提交前复跑 T9 全量门禁；提交后 `git show --stat` 验证单一职责。
- **Acceptance Criteria Addressed**: AC-1（交付完整性）
- **Test Requirements**:
  - `rule` TR-12.1：未获用户批准前工作树保持未提交状态；批准后每个提交仅含单一切片文件集且门禁通过；证据=git log/show 输出。
- **Notes**: 遵循全局规则：不主动 commit；本子任务是七概念 C 阶段的显式闸门。
