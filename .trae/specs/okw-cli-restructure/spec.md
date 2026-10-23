# okw CLI 架构重构（借鉴 xuan-compose 分层模式）- 产品需求文档

> 方法论链路：I（现状洞察）→ F（第一性原理：包结构应反映"装配/分发/领域"三类职责）→ V（对抗审查：以逐字节快照锁死用户可见面，将重构风险降为零）→ C（原子交付）。参考库 `projects/xuanspace/libs/xuan-compose` 为 GPL-2.0-only，本项目为 MIT：**只借鉴架构模式与测试范式，所有代码在 okw 内从零独立书写，禁止复制其源码片段**。

## Overview

- **Summary**：对 `apps/dev-tools/openkylin-wsl-devkit/src/okw` 做纯内部结构重构：把单文件 403 行的 `cli.py`（handler + parser 装配 + if 链分发三重职责）拆为 `cli/`（parser 纯装配 + main 装配分发）与 `commands/`（显式命令注册表，handler 按领域分组）两层；新增 `errors.py` 异常体系与 main 单点错误收口；新增导入时 Python 版本守卫；新增 CLI 表面 JSON 快照与注册表交叉校验测试。**用户可见的一切（命令名、参数、帮助/描述/epilog 文本、中文提示、退出码）逐字节不变**。
- **Purpose**：消除三类已识别结构风险——① 分发逻辑依赖 argparse 私有 API（`parser._subparsers._group_actions..._name_parser_map`，4 处重复 hack，CPython 升级即可能碎）；② 命令 handler 散落三处（cli.py 9 个、podman.py 3 个、image.py 2 个），新增命令需同时改 if 链与子组判断；③ 异常捕获模板重复（5 处 `try/except WslError|ScaffoldError → print 错误：… → return 1`），措辞与退出码靠人工保持一致。重构后命令面由快照机械锁定，命令增删改有注册表键集校验拦截。
- **Target Users**：okw 的维护者（未来增改命令的开发者/智能体）；终端用户无感知（输出逐字节不变）。

## Goals

- G1：`cli/` 分层——`parser.py` 仅含无副作用的 parser 装配（纯函数 `build_parser()`），`main.py` 仅含 argv 解析、注册表查表分发与错误收口；包内只有 main 运行时路径读取 argv。
- G2：`commands/` 显式注册表——全部 14 个命令 handler（list/status/import/export/unregister/exec/verify/scaffold/ref + podman 组 3 个 + image 组 2 个）按领域模块分组，经显式映射注册；parser 注册的命令集合与 handler 注册表键集机械交叉校验。
- G3：消除全部 argparse 私有 API 访问；子组空命令（`okw podman`、`okw image`）的帮助回打改用装配期闭包捕获自身 parser，退出码仍为 2。
- G4：`errors.py` 统一异常体系（`OkwError` 基类；`WslError`/`ScaffoldError` 成为其子类且旧导入路径保持可用）；异常类错误由 main 单点捕获，统一输出 `错误：{msg}` 到 stderr 并返回 1。富文本/特殊退出码路径（import 排障三问、exec 失败、未知主题退出码 2 等）保持在 handler 内、输出不变。
- G5：`okw/__init__.py` 顶部、一切其他导入之前设置 `MINIMUM_PYTHON_VERSION = (3, 10)` 版本守卫，低版本解释器得到可诊断的 `RuntimeError`；守卫函数自身使用各版本通用语法（不用 PEP 604 联合注解）。
- G6：零副作用导入纪律——import `okw` 及任意子模块（含 `okw.cli`、`okw.commands`）不发起子进程、不读取 argv、不触碰文件系统副作用；注册表与 parser 构造全程惰性。
- G7：CLI 表面快照锁定——重构前先从**现网 cli.py** 生成基线快照（命令序、help/description/epilog、每个参数的 option strings/action/default/required/choices/nargs/metavar/help），重构后序列化结果与基线完全相等；注册表键集与 parser 命令面交叉校验。
- G8：保持既有工程红线——零第三方运行时依赖、`requires-python = ">=3.10"`、scikit-build-core 纯 Python 包、入口 `okw = "okw.cli:main"` 可继续解析（cli 降级为包后由 `cli/__init__.py` 重导出 main）、禁止 `from __future__ import annotations`。

## Non-Goals

- **不改变任何用户可见行为**：命令名/参数/帮助文本/中文输出/退出码逐字节锁定；不做措辞统一、不做退出码"修正"。
- **不重构领域逻辑**：`distro.py`、`podman.py`、`image.py`、`verify.py`、`scaffold.py`、`ref.py` 内的业务函数与判定矩阵一行不动（仅迁出其中的 cmd_* handler 并以 PEP 562 模块级 `__getattr__` 保留旧路径别名）。
- **不新增/删除命令**，不新增功能特性。
- **不引入异步、日志框架或任何第三方依赖**（xuan-compose 的 async/engine 模式与其问题域相关，okw 为同步短命令，不照搬）。
- **不改文档**：`apps/dev-tools/openkylin-wsl-devkit/doc/` 与 README 描述的 CLI 表面不变，无需同步。
- **不修改测试断言口径**：现有 12 个测试文件保持通过；因迁移导致的唯一允许变动是 import 路径（且 G4 别名设计目标是零变动，若别名可覆盖则测试文件完全不动）。
- **不做 Git 提交**：完成后按原子提交原则另行征求用户确认。

## Background & Context

- 现状结构（实测行数）：`cli.py` 403 行（9 个 cmd_* handler + 约 250 行 parser 装配 + if 链分发 + 4 处私有 API hack）；`podman.py` 983 行（含 cmd_preflight/cmd_install/cmd_verify）；`image.py` 455 行（含 cmd_build/cmd_verify）；领域模块 distro 203 / verify 163 / scaffold 100 / ref 79。
- xuan-compose 可借鉴模式（仅模式，不复制代码）：① `cli/parser.py` 纯函数装配 + `cli/main.py` 单点装配收口；② `commands/__init__.py` 显式 `COMMAND_HANDLERS` 注册表，import 无副作用；③ parser 注册表与 handler 注册表键集相等的交叉校验测试；④ JSON 快照锁定命令序与 help/description 文本（`tests/snapshots/cli_parity.json` 范式）；⑤ 异常基类 + main 单点 `Error: …` + exit 1 收口，用户不见 traceback；⑥ 导入时版本守卫（其 `MINIMUM_PYTHON_VERSION`/`require_python_version` 模式，本项目阈值取 3.10）。
- 兼容耦合事实：现有测试直接引用 `podman.cmd_preflight`、`podman.cmd_install`、`podman.cmd_verify`、`image.cmd_build`、`image.cmd_verify`、`from okw.distro import WslError`、`from okw.scaffold import ScaffoldError`，故旧模块路径必须以别名继续可用。
- 许可证事实：xuan-compose 为 GPL-2.0-only（文件头 SPDX 标识），okw 为 MIT。架构思想与测试范式不受版权保护，但实现必须独立书写，不得拷贝其代码/注释/Snapshot 内容。

## Functional Requirements

- **FR-1**：包结构调整为 `okw/cli/`（`__init__.py` 重导出 `main` 与 `build_parser`；`parser.py`；`main.py`）+ `okw/commands/`（`__init__.py` 注册表；按领域分组的 handler 模块）+ 新增 `okw/errors.py`；`okw/cli.py` 单文件移除。
- **FR-2**：全部 14 个命令 handler 迁入 `commands/`，按领域分组（发行版生命周期/验收/脚手架/知识参考/podman 组/image 组）；handler 签名统一为 `def handler(args) -> int`。
- **FR-3**：`podman.py`、`image.py` 仅以 PEP 562 模块级 `__getattr__` 惰性暴露旧 cmd_* 别名，杜绝循环导入；领域代码不反向依赖 commands 包。
- **FR-4**：parser 装配为纯函数；子组空命令帮助回打通过装配期闭包实现，全包不得出现 `_subparsers`/`_group_actions`/`_name_parser_map` 私有属性访问。
- **FR-5**：main 作为唯一错误收口点：捕获 `OkwError` 体系 → stderr `错误：{msg}` → 返回 1；`KeyboardInterrupt`/SystemExit 不吞；未预期异常不伪装（维持 traceback，属程序缺陷而非用户错误）。
- **FR-6**：版本守卫置于 `okw/__init__.py` 最顶部（docstring 之后、任何其他 import 之前）；测试可注入 current 版本元组。
- **FR-7**：新增 `tests/snapshots/cli_surface.json`（重构前从现网生成基线并随本次变更入库）与快照/注册表测试模块；新增版本守卫测试模块；新增零副作用导入与无私有 API 静态断言。
- **FR-8**：`pyproject.toml` 的 `[project.scripts] okw = "okw.cli:main"` 保持不变且可解析（包 `cli/__init__.py` 暴露 main）；`__main__.py`（`python -m okw`）行为不变。

## Non-Functional Requirements

- **NFR-1（兼容性）**：重构前后 CLI 表面逐字节相等（快照机械证明）；现有全部测试零断言修改通过。
- **NFR-2（测试覆盖）**：整体覆盖率不低于 80%，新增/重构模块（cli/、commands/、errors.py、__init__ 守卫）不低于 90%。
- **NFR-3（可维护性）**：单文件职责单一；`cli/parser.py` 与 `cli/main.py` 各不超过 300 行，`commands/` 单个分组模块不超过 250 行；新增一个命令的改动面可由注册表键集测试一次性约束。
- **NFR-4（法律清洁）**：新增文件不得携带 GPL SPDX 标识；审查须确认无 xuan-compose 代码/注释逐字片段。
- **NFR-5（Windows 优先）**：测试沿用 conftest 对 WSL 调用的全 mock 策略，不要求真实 WSL；全量 pytest 在 Windows 本机 Python 3.10+ 环境通过。

## Constraints

- **Technical**：零第三方运行时依赖（`dependencies = []`，纯标准库）；Python ≥ 3.10（不得使用 3.10 不可运行的语法；禁用 `from __future__ import annotations`，既有 AST 守护测试继续通过）；scikit-build-core 构建配置不变；Windows + WSL2 运行环境。
- **Business**：用户可见行为逐字节锁定；不做大版本升级、不变更包名/命令名；MIT 许可不变。
- **Dependencies**：参考资产位于只读 git submodule `projects/xuanspace/libs/xuan-compose`，**只读取经、不动其文件**；不引入该包作为依赖。
- **Environment**：当前 Trae 终端 PATH 被裁剪（`python`/`okw` 不可见），实施阶段须先定位可用的 Windows Python 3.10+（`py` 启动器或常见安装路径）；若本机确无可用解释器，相关任务标记 blocked 并请用户解除，不得用 WSL Python 的结论冒充 Windows 结论。

## Assumptions

- 重构开始前现网测试在 Windows Python 3.10+ 下为全绿（Task 1 先机械证实；若非全绿，先行报告，不得把既有失败计入重构回归）。
- 快照基线从现网 `okw.cli.build_parser()` 程序化生成，人工不编辑基线内容。
- `python -m okw` 与 console script 的分发仅依赖 `okw.cli:main` 这一个公开入口，包外无其他对 `okw.cli` 内部符号的依赖（Task 1 全仓 grep 证实；若存在则在 spec 审批时补充）。
- 保持 `dependencies = []`：新代码仅使用 argparse/dataclasses/importlib/sys/types 等标准库。

## Acceptance Criteria

### AC-1：CLI 表面逐字节不变
- **Type**： `rule`
- **Given**：重构前从现网 cli 生成并入库 `tests/snapshots/cli_surface.json` 基线
- **When**：重构完成后以同一序列化器遍历新 `build_parser()`
- **Then**：命令顺序、每个命令/子组的 help/description/epilog、每个参数的 option strings/action/default/required/choices/nargs/metavar/help 与基线完全相等
- **Pass Condition**：快照对比测试通过（零 diff），且基线文件生成自现网 cli（提交记录/生成脚本可复现）
- **Evidence**：`pytest tests/test_cli_surface.py` 输出；`tests/generate_cli_snapshot.py` 生成脚本

### AC-2：现有测试零回归
- **Type**： `rule`
- **Given**：现网 12 个测试文件
- **When**：重构后全量执行
- **Then**：全部通过，测试文件无断言修改（仅在别名无法覆盖时允许 import 行调整，且须在证据中逐处说明）
- **Pass Condition**：全量 pytest 通过，用例数/子用例数不减少
- **Evidence**：重构前后两次 pytest 全量输出对比

### AC-3：argparse 私有 API 清零
- **Type**： `rule`
- **Given**：`src/okw` 全包
- **When**：静态搜索私有解析器属性标识
- **Then**：不存在 `_subparsers`、`_group_actions`、`_name_parser_map` 任一字符串
- **Pass Condition**：仓库内静态断言测试通过且 grep 零命中
- **Evidence**：新增 `test_no_private_argparse_api` 用例 + grep 输出

### AC-4：显式注册表与命令面交叉校验
- **Type**： `rule`
- **Given**：`commands` 注册表与 `build_parser()` 命令树
- **When**：执行交叉校验测试
- **Then**：parser 实际注册的 14 个叶子命令（含 podman/image 子组）与 handler 注册表键集严格相等；每个注册表值为可调用对象；无子命令时的组帮助分发可触达
- **Pass Condition**：交叉校验测试通过
- **Evidence**：`pytest tests/test_command_registry.py` 输出

### AC-5：异常体系与单点错误收口
- **Type**： `rule`
- **Given**：`errors.py` 与 main 收口逻辑
- **When**：WslError/ScaffoldError 等 OkwError 子类在命令执行中抛出
- **Then**：stderr 输出 `错误：{msg}`，退出码 1；旧导入路径（`okw.distro.WslError`、`okw.scaffold.ScaffoldError`）仍可导入且为 OkwError 子类；既有错误消息文案逐字节不变
- **Pass Condition**：相关现有用例（list_error/bad_series/bad magic 等）零修改通过，新增收口用例通过
- **Evidence**：pytest 输出 + 新 errors.py 类层次

### AC-6：导入时 Python 版本守卫
- **Type**： `rule`
- **Given**：`okw/__init__.py` 顶部守卫
- **When**：以注入方式模拟低于 (3, 10) 的版本元组
- **Then**：抛 RuntimeError 且消息含所需版本与实际版本；等于/高于阈值时静默放行；守卫代码不含 PEP 604 注解
- **Pass Condition**：守卫 L0 精确断言测试（≥ 8 例：边界 3.9/3.10/3.10.x/补丁版本/注入参数/消息内容/位置顺序）全通过
- **Evidence**：`pytest tests/test_python_version_guard.py -v`

### AC-7：零副作用导入
- **Type**： `rule`
- **Given**：将 `okw.distro` 的子进程执行函数替换为"被调用即失败"的探针
- **When**：在干净进程中依次 import `okw`、`okw.cli`、`okw.commands`、`okw.cli.parser` 并调用 `build_parser()`
- **Then**：探针零触发、不读 argv、不产生文件写入；import 与 parser 构造成功
- **Pass Condition**：零副作用导入测试通过
- **Evidence**：新增测试用例输出

### AC-8：工程红线保持
- **Type**： `rule`
- **Given**：pyproject.toml、AST 守护、license 头
- **When**：检查构建配置与静态门禁
- **Then**：`dependencies = []`、`requires-python = ">=3.10"`、入口 `okw.cli:main` 不变且可解析；`test_no_future_annotations.py` 通过；新增文件无 GPL SPDX 头、无从 xuan-compose 逐字搬入的代码/注释
- **Pass Condition**：配置断言与人工法律清洁核查均通过
- **Evidence**：pyproject 内容、pytest 输出、Review 阶段逐文件比对结论

### AC-9：分层结构质量
- **Type**： `rubric`
- **Dimension**：职责分离与可维护性
- **Scale**：1-5
- **Anchors**：1 = handler/parser/分发仍混杂或存在领域层反向依赖；3 = 分层存在但个别模块越界/超长；5 = parser 纯装配、main 纯分发、commands 按域分组、领域模块零 handler，且行数预算（parser/main ≤300、分组 ≤250）全部满足、新增命令只需"一个 handler + 一行注册 + 一个 parser 函数"
- **Pass Threshold**：≥ 4
- **Evidence**：重构后目录树、行数统计、注册表/parser 装配代码走查

### AC-10：测试覆盖率
- **Type**： `rule`
- **Given**：全量测试带覆盖率执行
- **When**：汇总 coverage
- **Then**：整体 ≥ 80%，`okw.cli`、`okw.commands`、`okw.errors` 及 `__init__` 守卫新逻辑 ≥ 90%
- **Pass Condition**：覆盖率报告同时满足两个阈值
- **Evidence**：`pytest --cov=okw --cov-report=term-missing` 输出

## Open Questions

- 无（优化力度=全套借鉴行为不变、兼容红线=逐字节锁定，已经用户 2026-10-12 确认；环境解释器定位留待 Task 1 实证，属阻塞处理项而非需求分歧）。
