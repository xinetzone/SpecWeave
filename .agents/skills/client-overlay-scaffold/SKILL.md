---
name: client-overlay-scaffold
version: 1.1.0
description: "在 apps/containers/client/overlays/ 新建 podman-compose 工作负载叠加层（onnx-quantized/xmnn-dev/agent-monetize-dev 的下一个栈）的脚手架。当用户要求新增/创建 client 叠加层、新工作负载栈、新 invoke xxx.* compose 命名空间、照三栈再做一个栈、给 rootless 基底加声明式服务栈时，必须使用此技能。v1.1 起骨架改为「声明式 StackSpec + extends rootless-base 基段」：栈模块只写 <NAME>_SPEC（jpman_client/tasks/overlay_core.py 的 StackSpec）+ TASKS=make_stack_tasks(spec) + 六别名，compose.yaml 以 extends 继承 overlays/_shared/base-rootless.yaml（rootless 三必需/凭证四变量/network_mode bridge 单一事实源），不再复制任何生命周期代码。封装：栈形态决策树、标准 12 件套文件清单、compose/invoke/.env 三套骨架模板（templates/）、rootless 三必需与 Windows 桥接不可变纪律、7 个必改接线登记点（含 tests/test_tasks_surface.py 黄金清单与 tests/test_compose_merge.py GOLDEN 表）、静态门禁→真实构建→E2E→独立 Review 验证链，以及 podman-compose 1.6 extends rec_merge/OCI/双 ABI/SONAME/.dockerignore 等全部实测踩坑。不要凭记忆手写 compose 与任务模块——本技能的骨架与 Gotchas 来自三个已交付栈（quant/xmnn/monetize）的真实 E2E 与两轮独立审查。"
argument-hint: "<栈名/用途> [选项]"
disable-model-invocation: false
user-invocable: true
paths:
  - ".agents/skills/client-overlay-scaffold/**"
  - "apps/containers/client/overlays/**"
  - "apps/containers/client/src/jpman_client/tasks/*.py"
title: "client overlay 工作负载叠加层脚手架 (Client Overlay Scaffold)"
x-toml-ref: "../../../.meta/toml/.agents/skills/client-overlay-scaffold/SKILL.toml"
---
# client overlay 工作负载叠加层脚手架 (Client Overlay Scaffold)

## 1. Skill ID

`client-overlay-scaffold`

## 2. 功能描述

在 `apps/containers/client/overlays/<stack>/` 下创建一个**与根 SDK→CLI
运行路径平行的 podman-compose 声明式工作负载栈**，并在 client invoke 中新增
一个 `<ns>.*` 命名空间驱动它。提供两类已验证形态（三栈均为声明式实现）：

| 形态 | 参考实现 | 特征 |
|------|---------|------|
| **A. 运行时依赖栈（简单）** | [onnx-quantized](../../../apps/containers/client/overlays/onnx-quantized/README.md) | 镜像只装 pip/conda 包，6 任务（build/up/down/ps/logs/smoke），构建期守卫+冒烟；`gpu_override=True`、`auto_shortflags=True` |
| **B. 工具链/挂载栈（复杂）** | [xmnn-dev](../../../apps/containers/client/overlays/xmnn-dev/README.md)、[agent-monetize-dev](../../../apps/containers/client/overlays/agent-monetize-dev/README.md) | A 全部 + 运行时 bind 宿主源码目录（`source_mounts`）+ 重型 conda 工具链 + exec 长任务（xmnn build-tvm/wheel、monetize build-native/wheel）+ 专属内核/数据产物 |

核心交付：标准文件骨架、不可变编排纪律、接线登记清单、真实验证链。

v1.1 起栈的编排骨架是**数据驱动**的：Python 侧一份 `<NAME>_SPEC =
StackSpec(...)`（[overlay_core.py](../../../apps/containers/client/src/jpman_client/tasks/overlay_core.py)）
+ `TASKS = make_stack_tasks(spec)` 六任务工厂；compose 侧三必需/凭证/bridge
网络上移 [_shared/base-rootless.yaml](../../../apps/containers/client/overlays/_shared/base-rootless.yaml)，
栈文件只写 `extends` + 栈专属字段。**不再复制任何生命周期函数**。

> **为什么用脚手架而不是每次手写？** compose 字段、invoke 模块、`.env`、
> 规则、AGENTS 路由之间有约 10 个强耦合登记点，且 podman-compose 1.6 /
> buildah OCI / rootless 有多个"不报错但行为错"的隐性陷阱（见 §10）。
> 两个已交付栈独立审查各抓到过真实缺陷；本技能把这些教训前置，避免第三次重踩。

## 3. 何时使用本技能

触发词：新增/创建/再做一个 client 叠加层、工作负载栈、overlay、
`invoke <ns>.*` compose 命名空间、"照 onnx-quantized/xmnn-dev 那样"、
给 rootless 基底加声明式服务（带自己镜像+compose+生命周期）。

> **边界（不要误用）**：只是用 `invoke run --tag <img>` 跑一次任意镜像 →
> 不需要新栈；只改现有栈 → 直接改对应 overlay 与规则；构建端
> （jupyter-podman-rootless 基底本身）变更 → 走构建端规则，不在 client。

## 4. 决策树

```
用户要在 client 增加容器化能力？
├─ 一次性/任意镜像运行 → 根 invoke run，不建栈
├─ 有固定镜像+固定 compose+需要声明式生命周期（up/down/ps）
│  ├─ 只在镜像内装包、不挂宿主目录、无长任务 → 形态 A（抄 onnx-quantized）
│  └─ 要 bind 宿主源码/数据 或 容器内编译/打包等长任务 → 形态 B（抄 xmnn-dev）
└─ 与已有栈同域？ → 优先扩现有 overlay（加任务/compose 覆盖文件），慎重新建
```

**命名先冻结**（后续所有文件共用，改名成本高）：

| 变量 | 规则 | 示例 |
|------|------|------|
| 栈目录 `<STACK>` | kebab-case，名词 | `onnx-quantized`、`xmnn-dev`、`agent-monetize-dev` |
| 命名空间 `<NS>` | 目录名的点号化短名（通常短于栈目录） | `quant`、`xmnn`、`monetize` |
| 镜像标签 | `localhost/<STACK>:latest` | `localhost/xmnn-dev:latest` |
| 服务名 `<SVC>` | 单数短名 | `quant`、`xmnn`、`monetize` |
| env 前缀 | 大写命名空间专属前缀 | `QUANT_*`、`XMNN_*`、`MONETIZE_*` |
| 端口 | 与已运行栈错开，先查 §5 | 2222/8888 → 2223/8890 → 2224/8892 |

## 5. 标准产物清单（12 件套）

| # | 文件 | 形态 | 说明/骨架来源 |
|---|------|:----:|------|
| 1 | `Containerfile.<stack>` | A+B | 薄叠加 FROM `localhost/jupyter-podman-rootless:latest`；无模板（内容栈特化），抄对应形态参考 |
| 2 | `compose.yaml` | A+B | **用 `templates/compose.yaml.skeleton`**：顶部 `extends: {file: ../_shared/base-rootless.yaml, service: rootless-base}`，只写栈专属字段（image/build/ports/volumes/栈 environment/组件 label），三必需/凭证四变量/network_mode/restart/managed-by 一律不重复 |
| 3 | `.env.example` | A+B | **用 `templates/env.example.skeleton`**；插值键与 compose `${...}` 逐一对应，桥接键与 StackSpec `bridge_env_keys` 逐一对应 |
| 4 | `.dockerignore` | A+B | 必备：`**/__pycache__/`、`**/*.py[cod]`、`.env`、临时态（见 §9.6） |
| 5 | `README.md` | A+B | 人类入口：定位/镜像/服务/前置/两路径/参数表/关系表/排障 |
| 6 | `smoke/<guard>.py` | A+B | 构建期烤入 `/opt/<stack>-smoke/`，root+devuser 双跑；含引号逻辑只能进脚本文件；脚本名写入 StackSpec `SmokeSpec` |
| 7 | `smoke/smoke_*.py` | A | 功能冒烟（纯 CPU 固定输入断言），文件名写入 `SmokeSpec.exec_scripts/standalone_scripts` |
| 8 | `builder/scripts/`（bash） | B 可选 | exec 长任务脚本（编译/打包/验证），容器内绝对路径常为 `/opt/<stack>-builder/scripts/`；vendor 自有 lib，禁跨目录 source |
| 9 | `src/jpman_client/tasks/<ns>.py` | A+B | **用 `templates/namespace.py.skeleton`**：只写 `<NAME>_SPEC = StackSpec(...)` + `TASKS = make_stack_tasks(<NAME>_SPEC)` + 六别名；长任务（如有）在本模块用内核 helper 薄封装。禁 `import podman`、禁复制生命周期函数 |
| 10 | `.agents/rules/<ns>-overlay.md` | A+B | AI 硬约束（单一职责；边界/门禁/三必需继承自基段/特有契约），并在 client AGENTS 增登记 |
| 11 | 根 client `.env.example` 段 | A+B | 注释态键集合，与 overlay `.env.example` 双向同步（含 bridge_env_keys 全部键） |
| 12 | 长任务/产物约定 + 测试黄金表 | A+B | （B）内核注册脚本/产物落 bind 目录等约定；**新栈一律扩 client `tests/test_tasks_surface.py` 黄金清单与 `tests/test_compose_merge.py` GOLDEN 表**（形态 A 也要加） |

> **为什么 Containerfile 不做模板？** 装包层（pip 五包 vs conda LLVM
> 工具链）与守卫内容是栈特化的，机械模板会给错误安全感；结构纪律
> （OCI 引号/分层/标签/守卫位置）在 §8 与 Gotchas 固化，具体 RUN 抄参考。

## 6. 骨架模板使用（templates/）

三个高同构文件先复制再替换占位符（占位符统一 `__X__` 形态）：

```bash
cd apps/containers/client/overlays
mkdir -p <STACK>
cp ../../../.agents/skills/client-overlay-scaffold/templates/compose.yaml.skeleton   <STACK>/compose.yaml
cp ../../../.agents/skills/client-overlay-scaffold/templates/env.example.skeleton     <STACK>/.env.example
cp ../../../.agents/skills/client-overlay-scaffold/templates/namespace.py.skeleton    ../../src/jpman_client/tasks/<ns>.py
```

替换映射（逐文件 grep `__` 确认无残留）：
`__STACK__` 目录名/project name / `__NS__` 命名空间（小写短名）/
`__NSU__` 命名空间大写形（spec 变量名与 env 前缀值，如 MONETIZE）/
`__SVC__` 服务名 / `__IMAGE__` 镜像标签 /
`__SSH_PORT__`·`__JUPYTER_PORT__` 端口 / `__ENV_PREFIX__` env 前缀 /
`__CONTAINERFILE__` Containerfile 文件名。

> v1.1 骨架只覆盖**结构不变量**，且不再含任何生命周期函数：namespace
> 骨架的可变量全部收敛进 `StackSpec(...)` 字段（端口默认/挂载/冒烟形态/
> `bridge_env_keys`/`gpu_override`/`conda_mirror`/`auto_shortflags`/
> `docs=TaskDocs(...)` 等）；compose 骨架只留栈专属字段，公共段走 extends。
> 长任务（B 形态的 build-tvm/wheel/build-native 等）在骨架标注处按
> monetize.py/xmnn.py 的写法用内核 helper（gates/ensure_runtime_ready/
> require_running/run_compose）薄封装；增删键后必须同步三方键集合（§7.4）
> 与两个测试黄金表（§9 第 7 点）。

## 7. 不可变纪律（红线，直接抄 quant-overlay/xmnn-overlay 规则）

### 7.1 架构边界（声明式内核，零复制）
- 栈模块 `<ns>.py` **禁止 `import podman`**；只通过子进程驱动
  podman-compose；**禁止回流**为 `invoke run` 后端或与 SDK 层混写。
- 同构编排（门禁/argv/环境解析/镜像构建/up-down-ps-logs/冒烟双路径/残留
  自愈）**一律在内核** [overlay_core.py](../../../apps/containers/client/src/jpman_client/tasks/overlay_core.py)，
  栈模块只允许：`<NAME>_SPEC`、`TASKS`/六别名、以及用内核 helper 薄封装的
  长任务。`test_modules_bounded_and_declarative` 断言栈模块 ≤160 行且不含
  `def _gate_platform`/`_compose_argv`/`_run_compose`/`_prepare_env` 等。
- **内核零栈知识**：overlay_core 不得 import 任何具体栈模块、不得出现具体
  栈常量；jpman_common（apps/containers/shared）同样零栈知识。栈差异只能
  经 `StackSpec` 字段注入。
- 复用 `[compose]` extra（pyproject 已有 podman-compose），**新栈不改
  pyproject、不新增依赖**。

### 7.2 双门禁（内核统一实现，每个任务入口自动先过）
1. Windows 原生 CPython：优先**透明桥接 WSL 发行版**
   （`run_in_wsl_bridge(extra_env_keys=spec.bridge_env_keys)`，默认发行版
   podman-machine-default，`COMPOSE_WSL_DISTRO=none` 可关）；不可桥接才
   Exit(1) + 双路径中文指引（WSL2 发行版 / `invoke env.run-cmd`）；
   2. POSIX 缺 `podman-compose` → 提示装 `pip install -e ".[compose]"`。
   build/up/smoke/长任务另过 daemon 预检。栈模块不自己写门禁（由工厂生成
   的任务体调用 `gates(spec)`）。

### 7.3 rootless 三必需与公共段（extends 单一事实源，严禁 privileged）
三必需 `devices: [/dev/fuse:/dev/fuse]`、`security_opt: [label=disable]`、
`cgroupns: host`（podman-compose 1.6 无 cgroupns 翻译器，**空操作也保留**）
连同凭证四变量（USER_PASSWORD/JUPYTER_TOKEN/SSH_PUBLIC_KEY/GRANT_SUDO）、
`network_mode: bridge`、`org.specweave.managed-by` label、`restart:
unless-stopped` **只声明在** [_shared/base-rootless.yaml](../../../apps/containers/client/overlays/_shared/base-rootless.yaml)
的 `rootless-base` 服务；栈 compose.yaml 以 extends 继承，**不得重复声明**。
基段严禁 volumes/build/env_file/ports 与宿主路径（test_compose_merge 有
正向断言）。任何栈都不得 privileged / docker.sock / host 网络。

### 7.4 卷与键集合
- bind **一律长语法** `type: bind` + `bind.create_host_path: true`
  （短语法在 1.6 会在宿主侧 `os.makedirs` 误建目录，见 Gotcha G1）；
  named volume 用短语法安全。
- 挂载声明式：每个宿主 bind 在 `StackSpec.source_mounts` 写一个
  `SourceMount(env, default_rel, label, anchor="repo"|"client", must_exist)`；
  内核 `prepare_env` 把路径解析为**绝对 POSIX 路径**注入（复用
  jpman_common `to_posix_path`），`must_exist` 源码挂载做存在性硬校验
  （Exit 1 中文指引），workspace 自动 mkdir + checkpoint 放宽。栈模块不写解析。
- **桥接键声明式**：Windows 透明桥接需透传的栈专属键只在
  `StackSpec.bridge_env_keys` 枚举（通常 = 五个 `<PREFIX>_*` 插值键 +
  各源码路径键）；通用键由 utils `_BRIDGE_COMMON_ENV_KEYS` 内置，
  栈模块与 utils 都不得硬编码具体栈键（utils 零栈知识）。
- 键集合三方一致：compose `${VAR}` ≡ overlay `.env.example` ≡ 根 client
  `.env.example` 注释段；桥接键集 ≡ `bridge_env_keys`。构建参数
  （BASE_IMAGE/MIRROR）用注释态键也计入。

### 7.5 标签
运行探测只用 podman-compose 自动写的
`io.podman.compose.project`/`.service`；业务标签栈文件仅写
`org.specweave.component`，`org.specweave.managed-by` 由基段继承
（dict 深合并取并集）。

### 7.6 extends 合并语义（podman-compose 1.6.0，vendor 源码实证）
- 解析阶段 `_parse_compose_file`（L2844-L2849）把 `extends.file` 相对路径
  按**引用它的 compose 文件目录**重写为绝对路径——故 invoke 的绝对 `--file`
  + 任意 cwd、裸 podman-compose 在栈目录执行，两种方式都能解析基段。
- `resolve_extends`（L2364）以 `rec_merge({}, base, current)` 合并：dict
  深合并（environment/labels 键并集）；普通 list 追加（devices/security_opt
  不重复，因为栈文件不再声明）；`command`/`entrypoint` 无条件整体替换。
- **volumes 特例（L2289-L2297，易踩坑）**：仅**短语法字符串**按 target
  去重，且**覆盖方（栈/override 文件）获胜**、条目移至列表尾部；**长语法
  dict bind 不去重**（`":" in dict` 是键判断）——本技能规定 bind 一律长
  语法（G1），因此**不要指望合并器消除同 target 重复挂载**；override
  文件（如 compose.gpu.yaml 形态）若重声明同一 target 会下发重复挂载点，
  需人工规避。基段无 volumes，三栈当前无碰撞。等价模拟器（含与真实
  rec_merge 的对照探针）在 client `tests/test_compose_merge.py`。
- **network_mode bridge 实证注记**：2026-09-14 同机实证 podman-machine-default
  无 systemd user bus，默认项目网络启 aardvark-dns 必现
  「Failed to connect to user scope bus」（未改动的 onnx 栈同机复现），
  显式 bridge 绕过；故 bridge 上移基段三栈统一继承（见 G2），新栈不得在
  栈文件覆盖回默认网络，除非本机环境已复核变化并在注释保留实证日期。

## 8. Containerfile 结构纪律

- 全部 RUN 显式 `/bin/bash -lc '...'`；**不写** SHELL/HEALTHCHECK/USER/
  覆盖 ENTRYPOINT/CMD/WORKDIR（OCI 格式忽略 SHELL/HEALTHCHECK，见 G3）。
- 含引号/嵌套引号的验证逻辑**必须固化为脚本文件** COPY 进去执行，
  RUN 行禁止内层双引号 `python -c "..."`（buildah 对 shell-form RUN
  二次分词，quant/xmnn 两次踩过）。
- pip/conda 镜像源 build-arg 三段（official/aliyun|tuna）幂等设置。
- 末尾层：注册内核（如有）→ 跑守卫脚本（root）→ `su devuser` 复跑 →
  完成横幅。**构建期失败即镜像构建失败**，守卫是硬门不是提示。
- 形态 B 双 ABI 铁律（若栈涉及编译 Python 扩展）：编译解释器与
  Jupyter 服务解释器必须先实测冻结；cp314t 上 Nuitka 类工具失败而 cp314
  GIL 成功时，工具装 base env 并 pin conda env 的
  `python=*=*<abi>` 防求解互换，守卫做双向 ABI 断言（见 G5）。

## 9. 接线登记点（漏一个就半残，逐项打勾）

1. **`tasks/__init__.py`（循环注册，不逐个手写）**：顶部 `from . import ...,
   <ns>`；建 `<ns>_ns = Collection("<ns>")` 后
   `for _name, _task in <ns>.TASKS.items(): <ns>_ns.add_task(_task, _name)`；
   长任务再单独 `add_task`（参照 xmnn/monetize 命名空间段）；
   `ns.configure` 加该栈 image_tag/base_image/container_name/端口段；
   模块 docstring 更新命名空间总数与命令清单。
2. **根 client `.env.example`**：新增 `<NS>` 注释段，键与 overlay
   `.env.example` 双向同步、与 `bridge_env_keys` 对齐。
3. **client 测试黄金表（必改，漏改 CI 红）**：
   `tests/test_tasks_surface.py` 加新命名空间任务集/docstring/签名/
   auto_shortflags/模块边界断言；`tests/test_compose_merge.py` GOLDEN 加
   新栈条目（dir/service/component/image/container_name/dockerfile/ports/
   volume_targets/env 键集）。
4. **文档锚点**：client `README.md` 新栈小节（命令/端口/配置/AI 规则链接）；
   `docs/1x-<ns>-overlay.md`（编号递增）与 `docs/README.md` 索引；
   overlay 自身 `README.md`。
5. **client `AGENTS.md` / `.agents/README.md` / `apps/AGENTS.md`**：
   AGENTS 顶部说明与项目概述（命名空间数/overlay 行）、嵌套路由树、
   上下文路由表、规范入口表、P0 速览 `C##` 约束、变更日志；
   `.agents/README.md` rules 数量/目录树/资产表/文档↔规则对应表；
   apps 路由表 client 行与边界声明表。
6. **新建 `.agents/rules/<ns>-overlay.md`**：内容含 §7 全部红线
   （三必需/凭证来自 extends 基段、内核零栈知识、栈模块零 podman、
   bridge_env_keys 声明式）+ 栈特有契约（双 ABI/SONAME/源码锚点等）。
7. **pyproject 无需改**：`[compose]` extra（podman-compose）已存在，
   jpman-common 已在主依赖；新栈不得引入新依赖。

> **为什么这么多登记点？** AGENTS 是 AI 会话的唯一路由入口；漏登记
> 不会导致运行失败，但下一个会话发现不了新栈、或在错误路径重复造轮子。

## 10. Gotchas（实测，按踩中概率排序）

- **G1 podman-compose 1.6 短语法 bind**：`src:tgt` 短语法与长语法
  缺 create_host_path 时会在宿主 `os.makedirs`，把相对 source 当目录建
  （quant 栈据此废弃短语法）。形态 B 相对 source 还会在 invoke cwd 的
  workspace 下预创建空同名目录（不影响真实挂载，down 后 rmdir）；
  **invoke 注入绝对路径不产生该副产物**。
- **G2 aardvark-dns / user scope bus**：podman-machine-default 无
  systemd user bus，默认项目网络 up 时偶发
  `Failed to connect to user scope bus` 容器卡 Created。显式
  `network_mode: bridge` 绕过（2026-09-14 同机未改动的 onnx 栈复现，
  与镜像无关），注释里保留实证日期。**v1.1 起 bridge 已上移
  `_shared/base-rootless.yaml`，三栈经 extends 统一继承，栈文件不得再
  各自声明 network_mode**（新环境复核见 §7.6）。
- **G3 OCI 格式警告不是错误**：`SHELL/HEALTHCHECK is not supported for
  OCI image format` 是 buildah 提示；正确做法是不写这两条指令，而非
  切 docker format/wrapper。
- **G4 容器内非登录 exec 不读 profile.d**：compose `exec` 的环境只来自
  compose `environment:`；需要的库路径（如 LLVM lib）必须显式注入，
  不能假设登录 shell 会导出。
- **G5 free-threading ABI 不可互换**：rootless 基底 base=`/opt/conda`
  是 cp314 GIL、main=cp314t。Nuitka 4.1.3 在 cp314t 编译失败
  (allocator.h:606)、cp314 GIL 成功；判 ABI 用
  `sysconfig.get_config_var('Py_GIL_DISABLED')` + `sys._is_gil_enabled()`
  双断言，不要只看版本号。
- **G6 CMake 4.x 拼写/路径**：`list(REMOVE_DUPLICATES)` 必须复数
  （3.x 接受单数，4.4 报 does not recognize）；`install(CODE)` 里
  `execute_process` 默认**不检查返回码**，cp 失败会静默缺文件，必须
  `RESULT_VARIABLE` + `FATAL_ERROR`；取目标名先 `get_filename_component(...
  NAME)`，同名绝对路径会漏 basename。
- **G7 .dockerignore 嵌套匹配**：裸 `__pycache__/` 只锚定上下文根，
  匹配不到 `builder/scripts/__pycache__/`；嵌套目录用 `**/__pycache__/`
  与 `**/*.pyc`。宿主 py_compile 产生的错误版本 pyc（如 cpython-313）
  会被 COPY 烤入交付镜像；稳妥做法再加一道构建末层 find 清理。
- **G8 Python 包探测方式随版本变**：Nuitka 包对象无 `__version__`
  （用 `python -m nuitka --version`）；scikit-build-core 1.x 顶层包名
  是 `scikit_build_core`（0.x 是 `skbuild`）；系统 apt 工具在
  `/usr/bin` 不在 conda bin——版本/可执行探测统一走 PATH 与子进程，
  不写死目录与属性。
- **G9 验证自包含性要剥离开发环境变量**：在开发容器内验证 wheel/产物
  自包含时，compose 注入的 PYTHONPATH/TVM_LIBRARY_PATH 会让验证命中
  挂载源码而非产物；验证脚本必须显式 unset 这些变量（模拟客户无源码环境）。
- **G10 invoke 参数**：含路径/空格的 compose 与 build 参数一律
  `shlex.quote`；布尔/可选参数任务加 `auto_shortflags=False`，避免
  `-h` 被吞与布尔三态歧义（同族 invoke-tasks 规则）。
- **G11 重型构建在 9p**：宿主 /mnt/d 上全量编译极慢，文档给出
  WSL 原生克隆替代路径；Nuitka jobs 与内存近线性，给 `--jobs` 降档。
- **G12 源码默认路径锚仓库根，不锚 client**：`_project_root()`=
  `apps/containers/client`；`SourceMount` 的 `default_rel` 默认锚
  `root.parents[2]`（仓库根，anchor="repo"），仓库内应用写 `"apps/<dir>"`、
  external 写 `"external/..."`；锚 client（anchor="client"）只用于 client
  根内资源。锚成 repo 又带 `apps/` 前缀会拼成 `apps/apps/<dir>`
  （2026-09-14 monetize 实战）。注意三套锚点不同：invoke 默认值按
  SourceMount.anchor；compose.yaml 裸 compose 插值相对 compose.yaml
  所在 overlay 目录（通常 `../../../<dir>` / `../../../../<dir>`，按层级数）。
- **G13 Windows 平台门禁会遮蔽 Linux-only 分支的 NameError**：任务入口
  的门禁（现由内核 `gate_platform`/`gates` 统一实现，栈模块不再有
  `_gate_platform`）在 Windows 直接 Exit(1)（或先 WSL 桥接成功 Exit 0），
  其后的 `shutil.which(...)` 等 Linux/WSL 分支在 Windows 永不执行——
  `py_compile` 不查未定义名，漏 import（如 shutil）只能在 WSL 内复现。
  静态门禁必须包含：① `ruff check`（F821 undefined name）或 pyflakes
  对生成的任务模块；② WSL 发行版内 `invoke <ns>.build` 真实跑过门
  （不能只在 Windows 侧验证门禁 Exit 1）。
- **G14 同构编排复制即违规（v1.1 内核抽取）**：第四栈若在栈模块复制
  build/up/down/ps/logs/smoke 或门禁/argv/env 解析，等于把三栈已消除的
  漂移重新引回（旧 quant.py 裸 join argv 漂移即此类）。差异先评估能否
  加成 `StackSpec` 字段（开关/元组/文案），由 `make_stack_tasks` 消费；
  确需新行为时改内核并让三栈 GOLDEN 全过，不得在单栈私有实现。红线：
  jpman_common 与 overlay_core 零栈知识，栈模块零 `import podman`。
- **G15 extends 漏写或基段越界**：栈 compose 漏写 extends 会丢失三必需/
  凭证/bridge；反向错误是把 image/ports/volumes 等宿主路径字段塞进
  `base-rootless.yaml`——基段只放三栈逐字相同且无路径的字段。合并行为
  以 rec_merge 为准（dict 并集/普通 list 追加/command 无条件替换/volumes
  仅短语法去重且覆盖方胜、长语法 dict 不去重，见 §7.6），改动后跑
  `tests/test_compose_merge.py` 全套（含真实 rec_merge 对照探针）。

## 11. 验证链（门禁顺序，不可跳真实构建）

1. **静态**：新 py `py_compile`、bash `bash -n`；功能性文件 grep 禁项
   （`external/chaos/ai`、`--mount=type=bind`、`CHAOS_ROOT`、`/builder/`、
   `import podman`、`--privileged`，文档事实表述除外）；
   在 client 目录跑 `pytest tests/test_overlay_core.py
   tests/test_tasks_surface.py tests/test_compose_merge.py` 全绿
   （新栈黄金表已登记；现网基线 57 passed 1 skipped）；
   `podman-compose config` 渲染断言（extends 可解析、三必需来自基段）；
   `invoke --list` 任务齐；Windows 侧 `invoke <ns>.ps` 实跑确认桥接/
   门禁行为；md 相对链接可达；键集合三方 diff 为空
2. **真实构建**：WSL2 machine 内 `podman build`（或 invoke build）退出
   0；镜像 inspect 入口链/无 Healthcheck；构建期守卫 root+devuser PASS
3. **E2E**：up 后端口/HTTP、挂载点、内核（如有）、exec 冒烟；
   形态 B 验证源码来自挂载路径前缀；长任务跑通一次；down 幂等
   （容器/网络清零、bind 保留、volume 默认保留/--volumes 删除）
4. **独立 Review**：复杂/高影响栈走 Spec Mode fresh-context 审查
   （rule+rubric AC）；actionable 全部修复后才视为完成

## 12. 安全检查清单

- [ ] compose.yaml 顶部 extends rootless-base，栈文件无三必需/凭证/network_mode/restart 重复；无 privileged/socket/host 网络
- [ ] 所有 bind 长语法 + create_host_path；invoke 绝对 POSIX + 存在性校验（source_mounts 声明）
- [ ] Windows 原生桥接 WSL 成功或门禁 Exit 1 且指引可执行；bridge_env_keys 与 .env 对齐
- [ ] 构建期不读宿主源码（上下文=栈目录）；无 BuildKit bind/外部目录依赖
- [ ] 外部/只读源码树零修改（若运行时会临时改写：注入-还原幂等 +
  trap/自愈 + 前后 hash 快照，参见 xmnn AST 注入模式）
- [ ] 守卫为硬失败（FATAL/exit≠0），无 WARNING 静默放行关键项
- [ ] 产物验证在隔离环境（临时 venv/干净变量），不污染开发环境
- [ ] 栈模块仅 SPEC+TASKS+别名（+内核 helper 长任务），≤160 行、无 podman import、无生命周期函数复制
- [ ] test_tasks_surface.py / test_compose_merge.py 黄金表已扩且 pytest 全绿
- [ ] 键集合/任务名/端口/文档多处一致；登记点 7 项全勾
- [ ] `.dockerignore` 用 `**/` 嵌套模式，交付镜像无错误版本 pyc/临时态

## 13. Changelog

- **v1.1.0** (2026-09-15): 适配三栈声明式重构（quant/xmnn/monetize）。
  骨架从「复制生命周期代码」改为「`StackSpec` 声明 + `make_stack_tasks`
  工厂 + extends rootless-base 基段」：namespace 骨架瘦身为
  `<NAME>_SPEC`/TASKS/六别名（长任务用内核 helper 薄封装，参照
  monetize.py）；compose 骨架改为 extends `_shared/base-rootless.yaml`
  + 仅栈专属字段；env 骨架桥接键对齐 `bridge_env_keys`。SKILL.md 重写
  12 件套与 7 个接线登记点（新增 `tasks/__init__.py` 循环注册、
  test_tasks_surface.py 黄金清单、test_compose_merge.py GOLDEN 表、
  pyproject 无需改）；红线补内核/jpman_common 零栈知识、栈模块零 podman、
  extends rec_merge 语义（volumes 长短语法差异）与 L2844-L2849 路径解析、
  bridge 上移基段的实证
  注记；Gotchas 新增 G14/G15，G2/G12/G13 同步。
- **v1.0.0** (2026-09-14): 初始版本。萃取 onnx-quantized（形态 A）与
  xmnn-dev（形态 B，经两轮 fresh-context 审查）的共同骨架：3 个
  compose/namespace/.env 骨架模板、12 件套清单、7 个接线登记点、
  11 条实测 Gotchas（G1~G11）、四级验证链。
