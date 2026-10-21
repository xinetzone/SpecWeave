# okw CLI 架构重构（借鉴 xuan-compose 分层模式）- 实施计划

> 与 [spec.md](spec.md) 配套。任务按依赖序排列，除 Task 1 为基线确认外，每个切片都是可独立验证的纵切；全程遵循 TDD 纪律——快照与新门禁测试在改动生产代码前先在现网结构上跑绿（先红/先绿锚定，再迁移保绿）。

## Task 1: 环境定位与现网基线全绿确认

- **Status**: `completed`
- **Completion Evidence**（2026-10-12）：
  - TR-1.1 ✅ 解释器 `C:\Users\XMICUser\AppData\Local\Programs\Python\Python314\python.exe`，Windows 原生 Python 3.14.7（py 启动器与 Python312 目录均不可用/不完整）；pytest 9.0.3、pytest-cov 可用。
  - TR-1.2 ✅ 现网全量 `pytest -q`：**279 passed in 10.19s**；覆盖率基线：TOTAL 1255 stmts / 75 miss / **94%**；cli.py 84%、distro 97%、image 94%、podman 98%、ref/scaffold 100%、verify 98%、__main__ 0%（3 stmts）。
  - TR-1.3 ✅ grep 证实包外对 `okw.cli` 的依赖仅：pyproject `okw.cli:main`、`__main__.py` 的 `from okw.cli import main`、5 个测试文件的 `from okw import cli` 且属性访问只有 `cli.main`（95 处调用，无 build_parser 等其他符号依赖）。
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 PATH 被裁剪的终端中定位可用的 Windows Python 3.10+（依次尝试 `py -3`、`$env:WINDIR` 外常见安装路径、`Get-Command python*`；记录解释器全路径与版本）。
  - 在 `apps/dev-tools/openkylin-wsl-devkit` 下执行现网全量 `pytest`（使用 pyproject 既有 pythonpath/cov 配置），记录用例总数与通过率作为回归基线。
  - 全仓 grep 确认包外无对 `okw.cli` 内部符号（除 `main`/`build_parser` 外）的依赖。
- **Acceptance Criteria Addressed**: AC-2、AC-8
- **Test Requirements**:
  - `rule` TR-1.1：存在一个 Windows 原生 Python（非 WSL）且版本 ≥ 3.10；`python --version` 输出存档；若找不到，任务转 `blocked`，Blocked By=无可用解释器，Unblock Condition=用户提供解释器路径/安装 Python。
  - `rule` TR-1.2：现网全量 pytest 通过，用例数/子用例数/覆盖率数字完整记录（作为 AC-2 与 AC-10 的 before 基线）；若现网非全绿，停止并向用户报告既有失败，不得带病迁移。
  - `rule` TR-1.3：grep 输出证实外部仅依赖 `okw.cli:main`（console script）与测试中的 `from okw import cli`（仅用 `cli.main`）；新发现的其他依赖登记到本任务证据。
- **Notes**: 解释器定位结果同时回填 spec Constraints 的 Environment 项。

## Task 2: CLI 表面快照基线（从现网生成，先入库）

- **Status**: `completed`
- **Completion Evidence**（2026-10-12）：
  - 新增 [tests/cli_surface_lib.py](../../../apps/dev-tools/openkylin-wsl-devkit/tests/cli_surface_lib.py)（递归序列化器，口径注释列明跳过 _HelpAction、纳入 _VersionAction 与 choice_helps）、[tests/generate_cli_snapshot.py](../../../apps/dev-tools/openkylin-wsl-devkit/tests/generate_cli_snapshot.py)、[tests/test_cli_surface.py](../../../apps/dev-tools/openkylin-wsl-devkit/tests/test_cli_surface.py)（3 用例）与 [tests/snapshots/cli_surface.json](../../../apps/dev-tools/openkylin-wsl-devkit/tests/snapshots/cli_surface.json)。
  - TR-2.1 ✅ 快照由生成器从现网 `okw.cli.build_parser()` 一次性生成；choice_helps 证实 11 个顶层/子组 help 文本入库，epilog/参数 help 抽查（podman 组 epilog、preflight 的 name help）与源码一致。
  - TR-2.2 ✅ 迁移前 `pytest tests/test_cli_surface.py` → 3 passed；叶子命令实测 14 个（9 顶层 + image build/verify + podman preflight/install/verify）。
  - TR-2.3 ✅ 连续两次生成文件 SHA256 相同（idempotent: True）。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 新增 `tests/cli_surface_lib.py`：递归遍历 argparse parser 树（含 podman/image 二级 subparsers），确定性序列化命令序、每个 parser 的 prog/help/description/epilog、每个 action 的 option strings/action 类名/default/required/choices/nargs/metavar/help（default 用可复现的 repr；跳过 version/help 等不影响业务的差异项时须在库注释中列明口径并对新旧两端同口径）。
  - 新增 `tests/generate_cli_snapshot.py`：从**现网** `okw.cli.build_parser()` 生成 `tests/snapshots/cli_surface.json`。
  - 新增 `tests/test_cli_surface.py`：断言当前 parser 序列化结果 == 快照文件；该测试在现网结构上必须先跑绿（证明基线可信）。
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-2.1：`tests/snapshots/cli_surface.json` 由脚本一次性生成、手工零编辑（生成命令与时间戳写入提交说明）；包含 14 个叶子命令的完整参数面。
  - `rule` TR-2.2：`pytest tests/test_cli_surface.py` 在**迁移前**通过（基线自洽），且快照覆盖 podman 与 image 两个子组的全部叶子（preflight/install/verify/build/verify-image）。
  - `rule` TR-2.3：快照 JSON 键序固定（sort_keys 或确定序写入），重复运行两次字节相同（幂等）。

## Task 3: errors.py 异常体系与旧路径兼容

- **Status**: `completed`
- **Completion Evidence**（2026-10-12）：
  - 新增 [src/okw/errors.py](../../../apps/dev-tools/openkylin-wsl-devkit/src/okw/errors.py)（`OkwError`，零第三方导入）；[distro.py](../../../apps/dev-tools/openkylin-wsl-devkit/src/okw/distro.py) 与 [scaffold.py](../../../apps/dev-tools/openkylin-wsl-devkit/src/okw/scaffold.py) 仅改基类为 OkwError，raise 点消息零改动。
  - 新增 tests/test_errors.py（6 L0 断言）；新增文件自动被 test_no_future_annotations 参数化覆盖。
  - TR-3.1/3.2/3.3 ✅ 全量 **293 passed**（基线 279 + 新断言与守护参数化 14 项，差异已逐源解释：6 异常断言 +3 快照断言 + 守护对 5 个新 .py 的展开）；总覆盖率维持 94%，errors.py 100%，distro/scaffold 消息用例全绿。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 新增 `src/okw/errors.py`：`OkwError(Exception)` 基类（docstring 说明用户可恢复错误由 main 单点收口）。
  - `distro.WslError` 与 `scaffold.ScaffoldError` 改为继承 `OkwError`（类名、构造签名、消息行为不变；类定义可留在原模块，仅改基类并 re-export）。
  - 不改动任何 raise 点的消息文案。
- **Acceptance Criteria Addressed**: AC-5、AC-8
- **Test Requirements**:
  - `rule` TR-3.1：`from okw.errors import OkwError`、`from okw.distro import WslError`、`from okw.scaffold import ScaffoldError` 均可导入，且后两者是前者子类（`issubclass` 断言）。
  - `rule` TR-3.2：现有 `test_distro.py`、`test_scaffold.py` 及全部依赖异常文案的用例零修改通过（消息逐字节不变）。
  - `rule` TR-3.3：errors.py 无第三方导入、无 `from __future__ import annotations`、可在 Python 3.10 语法下解析。

## Task 4: 导入时 Python 版本守卫

- **Status**: `completed`
- **Completion Evidence**（2026-10-12）：
  - [src/okw/__init__.py](../../../apps/dev-tools/openkylin-wsl-devkit/src/okw/__init__.py) 顶部加入 `MINIMUM_PYTHON_VERSION = (3, 10)` 与 `require_python_version()` 并在定义后立即调用（仅 stdlib `sys` 在调用前导入；函数无 PEP 604/match，支持 2 元/3 元版本元组）。
  - 新增 tests/test_python_version_guard.py（10 L0 断言：常量、3.9.18 拒绝且消息含双版本、3.10.0/3.10.99/3.14.7 放行、二元组边界、默认 current、AST 无 BitOr、守卫调用位置先于业务导入）。
  - TR-4.1/4.2/4.3 ✅ 守卫测试 10 passed；全量 **304 passed**（293 + 10 新断言 + AST 守护对新测试文件的参数化 +1）。
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 在 `src/okw/__init__.py` 中 docstring 之后、一切其他导入之前加入 `MINIMUM_PYTHON_VERSION = (3, 10)` 与 `require_python_version(minimum=MINIMUM_PYTHON_VERSION, current=None)`（current 仅测试注入）；调用置于同位置。
  - 守卫函数只用各版本通用语法：无 PEP 604 联合注解、无 match 语句；消息含所需版本、实际版本与 pyproject 阈值提示。
  - 新增 `tests/test_python_version_guard.py`（不触发真实导入守卫副作用：以 `importlib` 重载或直接对函数做注入测试；测试文件自身不写 `from __future__ import annotations`）。
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `rule` TR-4.1：L0 精确断言 ≥ 8 例：current=(3,9,x) 抛 RuntimeError；(3,10,0) 放行；(3,10,99) 放行（补丁不影响判定）；(3,14) 放行；默认 current 取 `sys.version_info`；异常消息同时包含 "3.10" 与实际版本字符串；minimum 默认值等于模块常量；函数位置在所有第三方导入之前（静态断言）。
  - `rule` TR-4.2：守卫源码无 `X | Y` 形式注解（AST 断言），可被 3.10 解释器编译。
  - `rule` TR-4.3：现网全量测试（含 test_no_future_annotations）通过。

## Task 5: commands/ 显式注册表与 handler 迁移

- **Status**: `completed`
- **Completion Evidence**（2026-10-12）：
  - 新建 commands 包 7 文件：[__init__.py](../../../apps/dev-tools/openkylin-wsl-devkit/src/okw/commands/__init__.py)（14 键 COMMAND_HANDLERS，键形 docstring 固化）+ distro_cmds(82 行)/verify_cmds/scaffold_cmds/ref_cmds/podman_cmds/image_cmds 六分组；14 个 handler 函数体逐字迁入。
  - [podman.py](../../../apps/dev-tools/openkylin-wsl-devkit/src/okw/podman.py) 与 [image.py](../../../apps/dev-tools/openkylin-wsl-devkit/src/okw/image.py) 仅删除 handler 定义并追加 PEP 562 `__getattr__` 惰性别名（迁移期 cli.py 仍经别名调用，已验证可工作）。
  - 新增 tests/test_command_registry.py（12 断言：键集恰好 14、值皆 callable、普通 dict、5 个别名 `is` 同一对象、负向 AttributeError 2 例、干净子进程零副作用探针）。
  - TR-5.1/5.2/5.3/5.4 ✅ 全量 **324 passed**（304 + 12 注册表断言 + AST 守护对 8 个新 .py 的参数化）；test_podman*/test_image* 零修改通过。
  - TR-5.5 评分 **5/5**：六分组行数 14–82 均远低于 250 行预算；grep 证实领域模块对 commands 的引用仅存在于 `__getattr__` 惰性函数内（image.py:509、podman.py:1101），无顶层反向依赖。
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 新建 `src/okw/commands/` 包：`__init__.py` 定义显式 `COMMAND_HANDLERS`（键为叶子命令的解析路径标识：顶层 9 个用原名，podman 组用 `podman preflight` 等点式/路径式键，image 组同理——具体键形以能被 main 机械查表为准并在模块 docstring 固化）；handler 按域分组模块（如 `distro_cmds.py`（list/status/import/export/unregister/exec）、`verify_cmds.py`、`scaffold_cmds.py`、`ref_cmds.py`、`podman_cmds.py`、`image_cmds.py`），签名统一 `def handler(args) -> int`。
  - 迁移 cli.py 的 9 个 cmd_* 与 podman.py/image.py 的 5 个 cmd_*：函数体原样搬迁（输出文案、退出码、try/except 边界不变）；仅把异常上抛给 main 收口的最小改动允许发生在 Task 6，本任务保持函数内现有错误处理不变以缩小 diff。
  - podman.py/image.py 删除迁出的函数定义，改用 PEP 562 模块级 `__getattr__("cmd_*")` 惰性从 commands 包取别名（避免循环导入）；模块 docstring 注明别名仅为兼容、新代码走注册表。
  - `import okw.commands` 零副作用：不实例化、不触子进程。
- **Acceptance Criteria Addressed**: AC-4、AC-5、AC-7、AC-9
- **Test Requirements**:
  - `rule` TR-5.1：`COMMAND_HANDLERS` 含且仅含 14 个叶子命令键；每个值 `callable`；注册表为普通 dict 且导入时即定型（新增 `test_command_registry.py` 计数与键集断言）。
  - `rule` TR-5.2：旧路径兼容：`podman.cmd_preflight/cmd_install/cmd_verify`、`image.cmd_build/cmd_verify` 经 `__getattr__` 仍可调用且 `is` 等于注册表里同一对象；引用不存在属性仍抛 AttributeError（负向断言）。
  - `rule` TR-5.3：test_podman.py/test_podman_install.py/test_podman_verify.py/test_image.py 全部**零修改**通过（别名充分性的机械证明）。
  - `rule` TR-5.4：子进程探针：monkeypatch `okw.distro` 的 WSL 执行入口为"调用即 raise AssertionError"，`import okw.commands` 不触发探针。
  - `rubric` TR-5.5：分组合理性；scale 1-5；anchors 1=迁移后仍有跨域大杂烩模块或领域层反向 import commands；3=分组存在但 1 个模块越界；5=六分组边界清晰、领域模块不反向依赖 commands、单组 ≤250 行；threshold ≥ 4；evidence=目录树+行数+依赖方向 grep。

## Task 6: cli/ 分层装配（parser 纯函数 + main 单点分发收口）

- **Status**: `completed`
- **Completion Evidence**（2026-07-02）：
  - 新建 [cli/parser.py](../../../apps/dev-tools/openkylin-wsl-devkit/src/okw/cli/parser.py)（build_parser 纯装配，default 仍引用 distro.DEFAULT_IMPORT_VERSION 与 image.DEFAULT_TAG/DEFAULT_BASE_IMAGE/DEFAULT_IMAGE）、[cli/main.py](../../../apps/dev-tools/openkylin-wsl-devkit/src/okw/cli/main.py)（解析→查表→OkwError 单点收口）、[cli/__init__.py](../../../apps/dev-tools/openkylin-wsl-devkit/src/okw/cli/__init__.py)（重导出 main/build_parser）；旧 403 行 cli.py 已删除；__main__.py 零改动。
  - 4 处私有 hack 由装配期闭包取代：`p_podman.set_defaults(_group_help=p_podman.print_help)` 与 image 同款；main 仅判 `podman_cmd/image_cmd is None` 后调用 `args._group_help()` 返回 2。
  - 收口统一：distro_cmds 的 list/status/import 与 verify_cmds、scaffold_cmds 内 WslError/ScaffoldError 自捕获全部移除，改由 main 单点 `except OkwError`（stderr「错误：…」+ return 1）；富文本路径（排障三问、exec stderr 透传、未知类型 return 2）原样保留。
  - 新增 tests/test_no_private_argparse_api.py（全包 token 门禁，带点号形态避免误伤公有 add_subparsers）、tests/test_cli_architecture.py（11 断言：叶子键集交叉校验、两子组空命令回打、WslError/ScaffoldError 收口、ValueError 不被吞、AST 禁裸 except/仅 OkwError、parser 无 IO/argv 耦合、main 无装配调用、双文件行数预算）、tests/test_command_handlers.py（9 断言补 handler 分支：空列表/未找到/导出成败/exit code 透传/-- 剥离/stderr 回显/dput 写文件/未知类型）。
  - TR-6.1 ✅ test_cli_surface.py 3 断言零修改通过（快照 JSON 未重生成）；TR-6.2 ✅ test_cli.py 零修改全绿；TR-6.3 ✅ 全包无 `._subparsers/._group_actions/._name_parser_map` 属性访问；TR-6.4 ✅ collect_leaf_commands(build_parser()) 排序后 == COMMAND_HANDLERS 键集；TR-6.5 ✅ 收口/不吞用例全绿；TR-6.6 ✅ `from okw.cli import main, build_parser` 与 `PYTHONPATH=src python -m okw --version` 输出 `okw 0.1.0`（console script editable 冒烟留 Task 7）；TR-6.7 评 **5/5**（parser 201 行、main 40 行，均 ≤300；parser 不读 argv/无 subprocess，main 无 add_*）。
  - 全量 **349 passed**，总覆盖率 **97%**：cli/__init__ 100%、cli/main 100%、cli/parser 100%，commands 六模块 90–100%（distro_cmds/scaffold_cmds 经 handler 层补测达 100%），errors 100%。
- **Priority**: high
- **Depends On**: Task 2、Task 4、Task 5
- **Description**:
  - 新建 `src/okw/cli/` 包：`parser.py` 承载现 cli.py 的全部 `add_parser/add_argument` 装配（help/description/epilog/default/choices 逐字保留），暴露无副作用纯函数 `build_parser()`；`main.py` 承载 `main(argv)`：解析 → 注册表查表分发 → OkwError 单点收口（stderr `错误：{e}`，return 1）。
  - 子组空命令帮助回打：在装配 podman/image 子 parser 时用闭包/parser 自身引用实现（如解析后 `args.podman_cmd is None` 时调用装配期绑定的该子 parser 的 `print_help()`），彻底移除 4 处 `_subparsers/_group_actions/_name_parser_map` 访问。
  - 富文本错误路径保持原状：import 排障三问、exec 的 stderr 透传、scaffold/ref 的退出码 2 等均不被 OkwError 收口吞掉（逐用例核对）。
  - `cli/__init__.py` 重导出 `main`、`build_parser`（保持 `okw.cli:main` 入口与 `cli.main(...)` 测试调用可用）；删除旧 `src/okw/cli.py` 单文件；`__main__.py` 不变（仍走 `okw.cli.main`）。
- **Acceptance Criteria Addressed**: AC-1、AC-3、AC-4、AC-5、AC-8、AC-9
- **Test Requirements**:
  - `rule` TR-6.1：`pytest tests/test_cli_surface.py` 在新结构下仍零 diff 通过（AC-1 机械证据）。
  - `rule` TR-6.2：`tests/test_cli.py` 零修改全绿；`okw podman` 与 `okw image` 无子命令仍输出帮助并返回 2（既有/新增断言）。
  - `rule` TR-6.3：静态断言 `src/okw` 全包不含 `_subparsers`、`_group_actions`、`_name_parser_map` 字符串（新增测试用 AST/读源码双重检查）。
  - `rule` TR-6.4：交叉校验：从 `build_parser()` 递归收集 14 个叶子命令键集 == `COMMAND_HANDLERS` 键集（两子组用同一键形规则）；未知命令与无命令行为返回 2 的既有断言保持。
  - `rule` TR-6.5：OkwError 收口新增用例：构造 handler 抛 WslError/ScaffoldError，断言 stderr 单行 `错误：…` 且返回 1；非 OkwError 异常不被吞（无 except Exception 兜底，静态断言）。
  - `rule` TR-6.6：`python -c "from okw.cli import main, build_parser; main(['--version'])"` 与 `python -m okw --version` 均正常；pyproject 入口无需变更即可解析（editable 重装后 console `okw` 可执行，若环境允许安装则验证，否则以 entry point 静态解析为准）。
  - `rubric` TR-6.7：parser/main 职责纯净度；scale 1-5；anchors 1=parser 仍读 argv 或 main 仍拼参数；3=基本分离但有越权调用；5=parser 不读 argv/无 IO、main 不含 add_argument、两文件均 ≤300 行；threshold ≥ 4；evidence=走查+行数。

## Task 7: 零副作用导入与全包验证、覆盖率与清洁核查

- **Status**: `completed`
- **Completion Evidence**（2026-07-02）：
  - TR-7.1 ✅ 全量 **349 passed**（基线 279，只增不减），TOTAL 1247 stmts / 36 miss / **97%**（≥80%）；新结构模块覆盖率：cli/__init__、cli/main、cli/parser、errors、commands/__init__、distro_cmds、image_cmds、podman_cmds、ref_cmds、scaffold_cmds、verify_cmds 全部 **100%**（≥90% 阈值）；既有领域模块 podman 98%、image 94%、distro 97%、verify 98%。
  - TR-7.2 ✅ pyproject.toml 文本未改：`requires-python = ">=3.10"`（L10）、`dependencies = []`（L19）、`okw = "okw.cli:main"`（L22）、scikit-build-core>=0.9 后端不变；src/ 全树 `from __future__` 命中 0；全部新增文件 SPDX/GPL/License 标识 grep 命中 0（延续 MIT 仓本体，不携带他方许可证头）。
  - TR-7.3 ✅ 逐文件清洁声明（独立实现，未复制 xc 代码/注释/快照）：
    - `errors.py`、`__init__.py` 版本守卫：本仓原创，xc 无对应物；
    - `cli/parser.py`：装配内容（prog/help/epilog/default/choices/中文文案）逐字迁自**本仓旧 cli.py**（okw 自有领域文案），借鉴的仅「parser 装配独立成纯函数模块」这一结构模式；
    - `cli/main.py`：注册表查表 + 装配期 `set_defaults(print_help)` 闭包去私有 hack + OkwError 单点收口为独立设计（xc 的分发函数与其键形、闭包方案无源码对应）；
    - `commands/` 六模块：handler 函数体迁自本仓 cli.py/podman.py/image.py，注册表 dict 与别名体系独立设计；
    - 快照设施（cli_surface_lib/generate_cli_snapshot/快照 JSON）：序列化器手写，JSON 内容是 okw 自身 CLI 面的序列化，不含 xc 任何字节；
    - 机械交叉验证：新文件 grep `xuan|compose` 0 命中；xc 源码 grep okw 特有文案（「排障三问」「星标保护」）0 命中；新文件无 GPL SPDX。
  - TR-7.4 ✅ 行数预算实测：parser 201 / main 40（≤300）；commands 分组最大 distro_cmds 85（≤250）；errors 10、cli/__init__ 11、commands/__init__ 44。editable 真实冒烟（Python 3.14.7 环境，scikit-build-core 构建）：console `okw.exe --version` → `okw 0.1.0`；`okw list` → rc 0，真实列出 2 个 WSL 发行版（含星标与默认保护文案，中文输出完好）；`okw podman` 无子命令 → 打印子组帮助（rc 2 已由 test_cli_architecture 锁定）。
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - 全量 pytest + 覆盖率，核对阈值；运行既有 `test_no_future_annotations.py` 与新增静态门禁。
  - 法律清洁：逐文件比对新增代码与 xuan-compose 对应文件，确认无逐字搬入的代码/注释/Snapshot 内容；新增文件不携带 GPL SPDX。
  - 行数预算统计（parser/main ≤300、命令分组 ≤250）；确认 `dependencies=[]`、`requires-python>=3.10`、构建配置未变。
  - 若 editable 环境可行，执行一次真实 `okw list`（只读路径）冒烟；不可行则以测试证据为准并在 Review 中标注。
- **Acceptance Criteria Addressed**: AC-2、AC-8、AC-9、AC-10
- **Test Requirements**:
  - `rule` TR-7.1：全量测试通过且用例数 ≥ Task 1 基线（只增不减）；整体覆盖率 ≥80%，okw.cli/okw.commands/okw.errors/`__init__` 新逻辑 ≥90%；未达标的缺口须补测试而非调阈值。
  - `rule` TR-7.2：`dependencies = []` 与 `requires-python = ">=3.10"` 文本不变；`grep -r "from __future__" src/` 零命中；新文件无 GPL 标识。
  - `rule` TR-7.3：Review 前由实施者出具逐文件清洁声明（新文件清单 vs xuan-compose 参考点：parser/main/commands/snapshot，说明独立实现差异点）。
  - `rule` TR-7.4：行数统计输出满足预算；真实 `okw list` 冒烟结果（通过或环境豁免说明）记录在案。

## 任务—验收标准映射总表

| AC | 覆盖任务（TR） |
|---|---|
| AC-1 CLI 表面逐字节不变 | Task 2（基线）、Task 6（TR-6.1） |
| AC-2 现有测试零回归 | Task 1（基线）、Task 3/4/5/6 各保持用例、Task 7（TR-7.1） |
| AC-3 私有 API 清零 | Task 6（TR-6.3） |
| AC-4 注册表交叉校验 | Task 5（TR-5.1）、Task 6（TR-6.4） |
| AC-5 异常体系与收口 | Task 3、Task 5、Task 6（TR-6.5） |
| AC-6 版本守卫 | Task 4 |
| AC-7 零副作用导入 | Task 5（TR-5.4）、Task 6（parser/main 纪律）、Task 7 |
| AC-8 工程红线 | Task 1、Task 3/4、Task 6（TR-6.6）、Task 7（TR-7.2/7.3） |
| AC-9 分层结构质量 | Task 5（TR-5.5）、Task 6（TR-6.7）、Task 7（TR-7.4） |
| AC-10 覆盖率 | Task 1（before）、Task 7（after） |
