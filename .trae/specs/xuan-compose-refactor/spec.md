# xuan-compose：podman-compose 单体重构进 xuanspace/libs - 产品需求文档

> 方法论编排：七概念场景 3「重构优化」链路 I → F → A → V → C
> Session：sc-20260915-podman-compose-refactor

## Overview

- **Summary**：将 `vendor/podman-compose/podman_compose.py`（containers/podman-compose v1.6.0，5541 行单文件、GPL-2.0-only、Python>=3.9）等价重构为 xuanspace monorepo 下的分层 Python 3.14+ 库 **xuan-compose**（import 名 `xuan_compose`），落位 `projects/xuanspace/libs/xuan-compose/`，采用 src 布局；全量保留 22 个子命令与全部辅助函数，移植上游 27 个单元测试文件作为行为等价安全网。
- **Purpose**：把一个"CLI 脚本单体"转化为可被 xuanspace 内其他 `apps/`、`libs/` 以 import 方式复用的 Compose 规范编排引擎；消除 import 时全局单例副作用；以分层包结构替代 5541 行翻译单元；同步完成 Python 3.9 → 3.14 的现代化。
- **Target Users**：xuanspace 生态中需要声明式容器编排（解析 compose 文件、翻译 podman 参数、编排服务生命周期）的 Python 开发者；以及需要通过 `python -m xuan_compose` 使用兼容 CLI 的运维场景。

## Goals

- **G1**：在 `projects/xuanspace/libs/xuan-compose/` 建立符合 xuanspace 子项目规范（src 布局、scikit-build-core、requires-python>=3.14.6、ruff py314/行宽 120）的纯 Python 库。
- **G2**：行为全量对等——上游 1.6.0 的全部公开符号、22 个命令、argparse 参数表不裁剪、不语义变更。
- **G3**：分层清晰——执行层（runner）/ 规范层（interpolation、normalize、merge、envfile、discovery）/ 翻译层（translate）/ 引擎层（engine、dependencies）/ 命令层（commands）/ CLI 层（cli、__main__）单向依赖。
- **G4**：库优先——显式构造的 `ComposeEngine` 公共 API，import 无副作用（不读 `sys.argv`、不创建全局单例、不触达网络/进程）；CLI 通过 `python -m xuan_compose` 提供，不注册 `[project.scripts]`。
- **G5**：GPL-2.0-only 合规——保留上游许可证全文与来源署名，衍生文件携带 SPDX 头。
- **G6**：质量门禁——移植的 27 个单元测试文件在 Python 3.14 下全部通过；ruff 零错误、mypy 零告警；覆盖率满足 xuanspace 验收基线。

## Non-Goals

- **NG1**：不做行为/CLI 参数/输出格式的功能性变更（纯结构重构；Python 3.14 必需的语法现代化除外）。
- **NG2**：不把 dict 形态的服务模型重写为 dataclass/pydantic 领域模型（Compose 规范 JSON 对象即规范模型，重新建模将使对等性不可证）。
- **NG3**：不修改 `vendor/podman-compose/` 内任何文件（第三方只读子模块）。
- **NG4**：不迁移、不门禁化上游集成测试（`tests/integration/`，依赖真实 podman 守护进程）；仅在 README 中记录手工 WSL 验证路径。
- **NG5**：不替换 `apps/containers/client/` 现有对外部 podman-compose 二进制的调用（后续接入另立任务）。
- **NG6**：不发布 PyPI；不自动执行 git commit（七概念 C 阶段仅产出提交建议，提交需用户明确批准；子模块内提交走 xuanspace 子项目流程）。
- **NG7**：不引入 APScheduler/requests/tzlocal 等仅上游 devel 测试链使用的依赖（除非移植后的测试真实需要）。

## Background & Context

### R 阶段：客观事实清单（G1 已通过，无因果判断词）

- F-001：源文件 `vendor/podman-compose/podman_compose.py` 共 5541 行、213KB，单文件承载全部逻辑。
- F-002：上游版本 `__version__ = "1.6.0"`；`pyproject.toml` 声明 `requires-python = ">=3.9"`、依赖 `python-dotenv` 与 `pyyaml`、许可证 `GPL-2.0-only`、console script `podman-compose = "podman_compose:main"`、setuptools `py-modules = ["podman_compose"]`。
- F-003：文件第 56 行存在模块级 `script = os.path.realpath(sys.argv[0])`；第 3270 行存在模块级单例 `podman_compose = PodmanCompose()`；装饰器 `@cmd_run`/`@cmd_parse` 在 import 时向该单例注册命令与参数器。
- F-004：约 145 个顶层函数/类。按代码段落可分为 5 个关注点：① 子进程执行（`Podman`/`ExistingContainer`，1845-2077 行）；② Compose 规范处理（`var_interpolate` 275-465、`rec_subs/norm_*` 466-560、`normalize_*` 2078-2220、`rec_merge*/OverrideTag/ResetTag/resolve_extends/dotenv_to_dict/find_compose_files_recursively` 2221-2418）；③ spec→podman argv 翻译（mount/network/port/resource/secret/build 等 643-1624 与 3549-4943 分散段）；④ 异步生命周期编排与上帝类 `PodmanCompose`（2419-3275，约 857 行）；⑤ argparse CLI（各 `compose_*_parse` 4944-5531 与 `main`）。
- F-005：22 个 `@cmd_run` 命令：ls、version、wait、systemd、pull、push、build、up、down、ps、run、cp、exec、start、stop、restart、logs、config、port、pause、unpause、kill、stats、images（注册条目 24 个，含别名/共享装饰器展开）。
- F-006：27 个单元测试文件位于 `vendor/podman-compose/tests/unit/`，全部以 `from podman_compose import ...` 扁平导入；测试框架为 unittest + `parameterized`；另有约 100 个集成测试文件依赖 podman 二进制。
- F-007：源文件头部含 `from __future__ import annotations` 与 `typing.Any/Callable/ClassVar/Iterable/Sequence/overload` 的 3.9 时代导入；服务对象统一标注为 `dict[str, Any]`。
- F-008：源文件含双平台路径处理（posix 下导入 `ntpath.isabs`、nt 下导入 `posixpath.isabs`）。
- F-009：目标 monorepo 规范：根 `pyproject.toml` 要求 `requires-python>=3.14.6`、ruff `line-length=120`、`target-version="py314"`、PDM workspace `{from="libs"}`；Python 模板采用 scikit-build-core + src 布局（`wheel.packages=["src/<pkg>"]`）、pytest `pythonpath=["src"]`。
- F-010：`libs/README.md` 准入规则：对外提供 importable API；不定义 `[project.scripts]`；命名 kebab-case、核心库 `xuan-` 前缀；独立 pyproject；公开 API 经 `__init__.py` 导出；含单元测试。
- F-011：xuanspace AI 提交验收基线：核心模块覆盖率 ≥90%、一般模块 ≥80%；ruff check 零错误；mypy 零新增告警；每新功能 ≥1 测试。
- F-012：xuanspace 根包与模板许可证为 Apache-2.0/MIT；GPL-2.0-only 与之不同，新库须独立声明 GPL-2.0-only。
- F-013：本地默认 Python 环境为 conda `py314`（Python 3.14.x）。
- F-014：上游 test-requirements 固定 `parameterized==0.9.0`、`pytest==8.0.2`、`types-PyYAML` 等。
- F-015：关键纯函数分布——插值器含完整 tokenizer（`tokenize/resolve_brace_content/interpolate_str`，支持 `$VAR`、`${VAR}`、`:-/-/:?/?` 语法）；合并层支持 `!reset_tag`、`!override_tag`；翻译层覆盖 mounts/volumes/secrets/networks/ports/ulimits/gpu/cpu/build ssh&context；编排层含依赖图（`rec_deps/calc_dependents/flat_deps`、`ServiceDependencyCondition` 五态）、profiles、include、extends、异步信号量并发与日志着色。

### I 阶段：核心洞察（G2）

- **I-1（陈述）** 重构本质是"恢复五层 + 显式装配"，不是重写逻辑。**（证据）** F-001/F-004/F-005 显示全部逻辑已存在且分层边界在代码段落中天然可辨。**（反常识）** 最大风险不是设计不足，而是 Compose 规范边角语义在搬运中走样——设计优雅但行为漂移即为失败。**（行动）** 采用翻译式搬迁（translate-then-move），以移植的 27 个测试文件逐切片锁死等价性，禁止顺手重写算法。
- **I-2（陈述）** import 时单例 + 装饰器注册是库化的核心障碍。**（证据）** F-003：模块导入即读 `sys.argv`、即构造引擎实例，命令表通过副作用写入全局对象；测试只能依赖"导入底部已注册完毕"的隐式时序。**（反常识）** 看似方便的装饰器注册表模式，实际把"对象生命周期"与"模块导入机制"耦合，使引擎无法被库调用方持有多个独立实例。**（行动）** 引擎改为显式构造的 `ComposeEngine`；命令表改为 `commands` 包内显式数据结构（dict 映射），由 `cli/main.py` 在进程入口装配；库导入零副作用。
- **I-3（陈述）** dict 服务模型必须保留。**（证据）** F-007/F-015：normalize/merge/translate 全链路以 Compose 规范 JSON 对象（plain dict）为载体，键数量随规范演进而增。**（反常识）** "重构=上 dataclass"在此是负优化：全量 typed model 会让本次 diff 无法与上游逐行对照，且 100+ 规范键的建模本身是另一个项目。**（行动）** v1 保留 dict 模型，仅在模块边界提供类型别名（如 `Service = dict[str, Any]`）与少量已有值对象（`ServiceDependency`、`PullImageSettings`）；typed model 留待未来。

### F 阶段：第一性原理设计（经 V 在审查阶段验证）

- **公理 1**：compose 文件是符合 Compose Specification 的 YAML/JSON 文档，其规范化结果就是一个 dict——规范本身即模型。
- **公理 2**：podman 是 CLI；一切副作用 = argv 向量 + cwd + env 经单一进程边界发出。`runner` 是唯一允许 subprocess/asyncio.subprocess 的地方。
- **公理 3**：服务动作 = translate(规范化服务) → argv → runner 执行；生命周期 = 依赖图排序后的异步调度。
- **公理 4**：CLI 是最薄适配层：argv → Namespace → 装配 Engine/Runner → 查表分发 handler。
- **自下而上推出的依赖方向**：`runner →（被）translate/engine →（被）commands →（被）cli`；规范处理（interpolation/normalize/merge/envfile/discovery）不依赖执行层；禁止反向 import。

### 目标包结构（A 阶段拆分蓝图）

```text
projects/xuanspace/libs/xuan-compose/
├── LICENSE                         # 上游 GPL-2.0-only 全文
├── README.md                       # 含来源署名、架构、用法、GPL 说明
├── CHANGELOG.md
├── pyproject.toml                  # scikit-build-core src 布局，requires-python>=3.14.6
└── src/xuan_compose/
    ├── __init__.py                 # 公共 API 显式导出 + __version__
    ├── __main__.py                 # python -m xuan_compose
    ├── py.typed
    ├── errors.py                   # PodmanComposeError
    ├── compat.py                   # 双平台 isabs、try_int/float、str_to_seconds、ver_as_list、try_parse_bool 等
    ├── types.py                    # 类型别名、DependField 等枚举
    ├── logging_utils.py            # logger 与日志着色
    ├── interpolation.py            # var_interpolate + tokenizer
    ├── envfile.py                  # dotenv_to_dict
    ├── discovery.py                # find_compose_files_recursively
    ├── normalize.py                # normalize(_service)(_final)、norm_*、rec_subs
    ├── merge.py                    # clone/rec_merge(_one)、!override/!reset、load_yaml_or_die、resolve_extends
    ├── runner.py                   # Podman、ExistingContainer（唯一子进程边界）
    ├── model.py                    # ServiceDependency(Condition)、PullImageSettings
    ├── dependencies.py             # rec_deps、calc_dependents、flat_deps
    ├── pull.py                     # settings_to_pull_args 及拉取编排
    ├── logs.py                     # create_format_logs_task、取消判定、compose_logs
    ├── translate/
    │   ├── mounts.py  networks.py  ports.py  resources.py
    │   ├── secrets.py  build.py    run_args.py
    ├── engine.py                   # ComposeEngine（原 PodmanCompose：解析/命名/pod/profiles/上下文依赖/哈希）
    ├── commands/                   # 22 命令 handler + 显式 COMMAND_HANDLERS 注册表
    │   └── version/build/updown/lifecycle/runexec/inspect/pullpush/systemd/logs.py
    └── cli/
        ├── parser.py               # 全局 parser + 全部 compose_*_parse
        └── main.py                 # 显式装配 + main()
```

## Functional Requirements

- **FR-1**：在 `libs/xuan-compose/` 建立 src 布局纯 Python 库，构建后端 scikit-build-core（纯 Python 包不写 `[tool.scikit-build.cmake]` 段），PDM workspace 自动识别。
- **FR-2**：上游每个公开顶层符号（函数、类、命令 handler、parser 函数、常量、版本）在新包中有可定位落点；维护一份符号映射表并随代码交付。
- **FR-3**：22 个命令全部保留，handler 经显式注册表分发；`python -m xuan_compose <cmd> --help` 全部可用。
- **FR-4**：argparse 参数表与上游 1.6.0 等价（参数名、短选项、默认值、action、nargs 一致；仅 prog 名差异）。
- **FR-5**：`ComposeEngine` 可脱离 CLI 显式实例化；`import xuan_compose` 不读 `sys.argv`、不创建全局引擎、不发起进程/网络访问。
- **FR-6**：移植全部 27 个单元测试文件，导入路径更新为新包模块，断言与数据不弱化；在 py314 环境全部通过。
- **FR-7**：Python 3.14 现代化：移除 `from __future__ import annotations` 与 3.9 兼容写法；内置泛型/联合类型；按行宽 120 ruff 格式化；补全公开 API 类型注解。
- **FR-8**：GPL-2.0-only 合规交付（LICENSE、SPPX 头、署名）。
- **FR-9**：双平台路径逻辑（ntpath/posixpath 交叉 isabs）原样保留。
- **FR-10**：README（安装、库用法、`python -m` CLI 用法、架构分层、与上游关系与许可证）与 CHANGELOG 齐备。

## Non-Functional Requirements

- **NFR-1（等价性）**：以移植测试零跳过、零断言削弱为行为等价的可观测证据；结构性偏差必须在符号映射表中登记。
- **NFR-2（可测试性）**：runner 可被注入/替换（dry_run 与 fake runner 路径保留），命令 handler 不直接 import 具体单例。
- **NFR-3（可维护性）**：层间依赖单向；任何模块不得跨层反向 import；`__init__.py` 只导出稳定公共 API。
- **NFR-4（质量门禁）**：ruff check 零错误；mypy 对新包零告警；pytest 全绿；核心模块（interpolation/normalize/merge/translate/engine）覆盖率 ≥90%，包整体 ≥80%。
- **NFR-5（可审计性）**：实现按原子切片推进，每切片有独立测试证据；vendor 源树零改动。

## Constraints

- **Technical**：Python `>=3.14.6`；ruff target py314、line-length 120；scikit-build-core>=0.10（纯 Python）；src 布局；测试 `pythonpath=["src"]`；依赖仅限 `pyyaml`、`python-dotenv`（运行）与 `pytest`、`pytest-cov`、`parameterized`（测试）。
- **Business/Legal**：衍生作品必须以 **GPL-2.0-only** 分发（用户已确认）；每个源文件携带 `SPDX-License-Identifier: GPL-2.0-only`；README/NOTICE 注明 "Derived from containers/podman-compose v1.6.0" 与上游仓库 URL 及 pinned commit。
- **Boundary**：`vendor/` 只读；工作产物限 `projects/xuanspace/libs/xuan-compose/`（子模块内开发）；`.trae/specs/` 承载本流程产物；不向 `docs/` 落盘技术文档（README 在子项目内即足够）。
- **Dependencies**：py314 conda 环境可用；Windows 宿主运行单元测试（不要求 podman 守护进程）。

## Assumptions

- 移植过程中如发现上游代码在 Python 3.14 下的真实不兼容（如废弃 API），以"最小行为保持改动"修复，并在映射表/CHANGELOG 逐条登记。
- `parameterized` 在 py314 可正常工作；若不兼容，改用 pytest.mark.parametrize 等价改写（仅测试侧，断言不变）。
- 不进行 git commit，除非用户在实施完成后明确批准。
- 集成测试手工验证（WSL + podman）为可选项，不构成本次验收条件。

## Acceptance Criteria

### AC-1：子项目落位与骨架合规（rule）

- **Given**：实施完成
- **When**：检查 `projects/xuanspace/libs/xuan-compose/`
- **Then**：存在 src 布局包 `src/xuan_compose/`、`pyproject.toml`（scikit-build-core 后端、`requires-python>=3.14.6`、运行依赖 pyyaml + python-dotenv、无 `[project.scripts]`、`wheel.packages=["src/xuan_compose"]`）、`py.typed`、独立 pytest 配置（pythonpath=["src"]）
- **Pass Condition**：上述文件/字段逐项存在；`python -c "import xuan_compose"`（可编辑安装后）退出码 0；`pip install -e .` 在 py314 环境成功
- **Evidence**：目录清单 + pyproject.toml 内容 + 安装/导入命令输出

### AC-2：GPL-2.0-only 许可合规（rule）

- **Given**：新库全部源文件
- **When**：检查许可证载体
- **Then**：`LICENSE` 为 GPL-2.0-only 全文（与上游 vendor/podman-compose/LICENSE 一致）；每个 `.py` 文件首行含 `SPDX-License-Identifier: GPL-2.0-only`；README 含 "Derived from containers/podman-compose v1.6.0"、上游 URL、pinned commit hash
- **Pass Condition**：脚本扫描 `.py` 文件 SPDX 头覆盖率 100%；LICENSE 与上游 hash 一致；署名三要素齐备
- **Evidence**：扫描脚本输出 + git 上游 commit hash（`git -C vendor/podman-compose rev-parse HEAD`）+ README 段落

### AC-3：上游符号全量映射（rule）

- **Given**：上游 1.6.0 全部公开顶层符号清单（约 145 个函数/类 + 版本常量）
- **When**：对照新包
- **Then**：每个符号在映射表中有目标模块落点；模块级 `sys.argv[0]` 读取与全局单例被移除（以显式装配替代）；不存在未登记的语义性丢弃
- **Pass Condition**：映射表覆盖 100%（有意重命名者同时记录新旧名）；评审抽查 10 个符号实现可在新包定位且代码同源
- **Evidence**：仓库内 `docs/internal/` 或 README 附录的符号映射表 + `grep "sys.argv"` 仅出现在 cli 层

### AC-4：22 命令与 argparse 对等（rule）

- **Given**：上游 22 个命令与 24 个 `compose_*_parse` 注册
- **When**：对新库逐命令执行 `python -m xuan_compose <cmd> --help`，并程序化对比 parser 参数表
- **Then**：22 命令全部 exit 0；参数表（option strings、action、default、nargs、required）与上游 diff 为空（prog 名除外）
- **Pass Condition**：命令清单完全一致；参数对比脚本零差异
- **Evidence**：help 命令批量输出 + 参数对比测试（可作为 tests/ 中一个新增对等性测试）

### AC-5：27 个单元测试文件全量移植并通过（rule）

- **Given**：`vendor/podman-compose/tests/unit/` 的 27 个测试文件
- **When**：在 py314 环境执行 `pytest`（新库 tests/）
- **Then**：27 个文件全部移植（允许 import 路径更新与 parameterized→pytest 机械改写）；无 skip/xfail 增加；全部通过
- **Pass Condition**：pytest 汇总通过数 ≥ 上游用例数，失败=0，跳过=0（环境硬约束者除外且需登记）
- **Evidence**：`pytest -q` 完整输出与上游用例数对照

### AC-6：vendor 子模块零改动（rule）

- **Given**：实施全程
- **When**：`git -C vendor/podman-compose status --porcelain`
- **Then**：输出为空
- **Pass Condition**：空输出
- **Evidence**：命令输出

### AC-7：Lint / 类型 / 测试门禁（rule）

- **Given**：新库代码
- **When**：在子项目目录运行 ruff 与 mypy（py314）
- **Then**：`ruff check src tests` 零错误；`mypy src` 零告警；`pytest` 全绿
- **Pass Condition**：三条命令退出码均为 0
- **Evidence**：命令输出

### AC-8：覆盖率达标（rule）

- **Given**：移植测试与新增脚手架测试
- **When**：`pytest --cov=src/xuan_compose --cov-report=term-missing`
- **Then**：包整体覆盖率 ≥80%；interpolation/normalize/merge/translate/engine 核心模块 ≥90%
- **Pass Condition**：报告数字达标
- **Evidence**：coverage 报告

### AC-9：分层依赖单向性（rubric）

- **Dimension**：包结构与依赖方向（runner←规范层/翻译层←engine←commands←cli，无反向、无环）
- **Scale**：1-5
- **Anchors**：1 = 仍存在跨层反向 import 或环状依赖；3 = 分层存在但有少量绕行（如 commands 直接碰 argparse 细节）；5 = 严格单向、`__init__` 导出克制、层间边界可用 import-linter 式检查证明
- **Pass Threshold**：≥4
- **Evidence**：目录结构、import 审查（可用静态扫描列出层间边）

### AC-10：行为等价可信度（rubric）

- **Dimension**：测试搬运保真性与差异登记完备性
- **Scale**：1-5
- **Anchors**：1 = 大量断言被删改/测试被跳过；3 = 测试通过但存在未登记的语义微调；5 = 断言零削弱、全部差异点（含 3.14 兼容修复）逐条登记并可回溯到上游行号
- **Pass Threshold**：≥4
- **Evidence**：移植前后测试 diff、差异登记表

### AC-11：Python 3.14 现代化质量（rubric）

- **Dimension**：现代语法/类型/工程化程度
- **Scale**：1-5
- **Anchors**：1 = 保留 `from __future__ import annotations`、Optional/Union 旧式写法、无类型注解；3 = 语法现代化但注解不完整；5 = 全面使用 py314 惯用法、公共 API 注解完整、无死代码/无 3.9 兼容分支
- **Pass Threshold**：≥4
- **Evidence**：代码抽查 + ruff UP 规则集结果

### AC-12：库 API 无副作用可用（rule）

- **Given**：仅 `import xuan_compose`
- **When**：静态检查导入路径与构造行为
- **Then**：`from xuan_compose import ComposeEngine` 可显式实例化；导入过程不访问 `sys.argv`、不启动子进程、不触网；多个引擎实例相互独立
- **Pass Condition**：代码中 `sys.argv` 仅出现于 `cli/` 与 `__main__.py`；实例化冒烟测试通过
- **Evidence**：grep 结果 + 冒烟测试输出

### AC-13：子项目文档齐备（rule）

- **Given**：新库 README.md 与 CHANGELOG.md
- **When**：内容审查
- **Then**：README 含安装、库快速开始、`python -m` CLI 用法、架构分层图（Mermaid）、与上游关系及 GPL-2.0-only 说明、测试运行方式；CHANGELOG 记录 0.1.0 初始重构
- **Pass Condition**：各要素齐备
- **Evidence**：文档内容

## Open Questions

无（许可证、对等范围、CLI 形态、包名四个决策点已经用户确认：GPL-2.0-only 署名 / 全量对等 / 库优先 + python -m / xuan-compose）。
