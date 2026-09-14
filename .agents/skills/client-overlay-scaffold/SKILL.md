---
name: client-overlay-scaffold
version: 1.0.0
description: "在 apps/containers/client/overlays/ 新建 podman-compose 工作负载叠加层（如 onnx-quantized/xmnn-dev 的下一个栈）的脚手架。当用户要求新增/创建 client 叠加层、新工作负载栈、新 invoke xxx.* compose 命名空间、照 onnx-quantized 或 xmnn-dev 再做一个栈、给 rootless 基底加声明式服务栈时，必须使用此技能。封装：栈形态决策树、标准 12 件套文件清单、compose/invoke/.env 三套骨架模板（templates/）、rootless 三必需与 Windows 门禁不可变纪律、7 个必改接线登记点、静态门禁→真实构建→E2E→独立 Review 验证链，以及 podman-compose 1.6/OCI/双 ABI/SONAME/.dockerignore 等全部实测踩坑。不要凭记忆手写 compose 与任务模块——本技能的骨架与 Gotchas 来自两个已交付栈（quant/xmnn）的真实 E2E 与两轮独立审查。"
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
一个 `<ns>.*` 命名空间驱动它。提供两类已验证形态：

| 形态 | 参考实现 | 特征 |
|------|---------|------|
| **A. 运行时依赖栈（简单）** | [onnx-quantized](../../../apps/containers/client/overlays/onnx-quantized/README.md) | 镜像只装 pip/conda 包，6 任务（build/up/down/ps/logs/smoke），构建期守卫+冒烟 |
| **B. 工具链/挂载栈（复杂）** | [xmnn-dev](../../../apps/containers/client/overlays/xmnn-dev/README.md) | A 全部 + 运行时 bind 宿主源码目录 + 重型 conda 工具链 + exec 长任务（编译/打包）+ 专属内核/数据产物 |

核心交付：标准文件骨架、不可变编排纪律、接线登记清单、真实验证链。

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
| 栈目录 `<STACK>` | kebab-case，名词 | `onnx-quantized`、`xmnn-dev` |
| 命名空间 `<NS>` | 目录名的点号化，通常同栈名 | `quant`、`xmnn` |
| 镜像标签 | `localhost/<STACK>:latest` | `localhost/xmnn-dev:latest` |
| 服务名 `<SVC>` | 单数短名 | `quant`、`xmnn` |
| env 前缀 | 大写命名空间专属前缀 | `QUANT_*`、`XMNN_*` |
| 端口 | 与已运行栈错开，先查 §5 | 2222/8888 → 2223/8890 |

## 5. 标准产物清单（12 件套）

| # | 文件 | 形态 | 说明/骨架来源 |
|---|------|:----:|------|
| 1 | `Containerfile.<stack>` | A+B | 薄叠加 FROM `localhost/jupyter-podman-rootless:latest`；无模板（内容栈特化），抄对应形态参考 |
| 2 | `compose.yaml` | A+B | **用 `templates/compose.yaml.skeleton`** |
| 3 | `.env.example` | A+B | **用 `templates/env.example.skeleton`**；键集合必须与 compose 插值键逐一对应 |
| 4 | `.dockerignore` | A+B | 必备：`**/__pycache__/`、`**/*.py[cod]`、`.env`、临时态（见 §9.6） |
| 5 | `README.md` | A+B | 人类入口：定位/镜像/服务/前置/两路径/参数表/关系表/排障 |
| 6 | `smoke/<guard>.py` | A+B | 构建期烤入 `/opt/<stack>-smoke/`，root+devuser 双跑；含引号逻辑只能进脚本文件 |
| 7 | `smoke/smoke_*.py` | A | 功能冒烟（纯 CPU 固定输入断言） |
| 8 | `scripts/`（bash） | B 可选 | exec 长任务脚本（编译/打包/验证）；vendor 自有 lib，禁跨目录 source |
| 9 | `src/jpman_client/tasks/<ns>.py` | A+B | **用 `templates/namespace.py.skeleton`**；禁 `import podman` |
| 10 | `.agents/rules/<ns>-overlay.md` | A+B | AI 硬约束（单一职责；边界/门禁/三必需/特有契约），并在 AGENTS 增 C# |
| 11 | 根 client `.env.example` 段 | A+B | 注释态键集合，与 overlay `.env.example` 同键 |
| 12 | （B）内核/数据产物约定 | B | 内核注册脚本/产物落 bind 目录等 |

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
`__STACK__` 目录名 / `__NS__` 命名空间 / `__SVC__` 服务名 /
`__IMAGE__` 镜像标签 / `__SSH_PORT__`·`__JUPYTER_PORT__` 端口 /
`__ENV_PREFIX__` env 前缀 / `__CONTAINERFILE__` Containerfile 文件名。

> 模板只覆盖**结构不变量**；任务集（B 形态的 build-tvm/wheel 等）与
> 环境变量业务键按栈在骨架标注处增删，增删后必须同步三方键集合（§7.4）。

## 7. 不可变纪律（红线，直接抄 quant-overlay/xmnn-overlay 规则）

### 7.1 架构边界
- `<ns>.py` **禁止 `import podman`**；只走 podman-compose 子进程；
  **禁止回流**为 `invoke run` 后端或与 SDK 层混写。
- 复用 `[compose]` extra（pyproject 已有 podman-compose），**不新增依赖**。

### 7.2 双门禁（每个任务入口先过门）
1. Windows 原生 CPython → Exit(1) + 双路径中文指引（WSL2 发行版 /
   `invoke env.run-cmd`）；2. POSIX 缺 `podman-compose` → 提示装
   `pip install -e ".[compose]"`。build/up/smoke/长任务另过 daemon 预检。

### 7.3 rootless 三必需（compose 标准字段，严禁 privileged）
`devices: [/dev/fuse:/dev/fuse]`、`security_opt: [label=disable]`、
`cgroupns: host`（podman-compose 1.6 无翻译器，**空操作也要保留并注释**）。
无 privileged / docker.sock / host 网络。

### 7.4 卷与键集合
- bind **一律长语法** `type: bind` + `bind.create_host_path: true`
  （短语法在 1.6 会在宿主侧 `os.makedirs` 误建目录，见 Gotcha G1）；
  named volume 用短语法安全。
- invoke 路径把宿主路径解析为**绝对 POSIX 路径**（复用 utils.to_posix_path）
  注入；源码类挂载做**存在性硬校验**（Exit 1 中文指引），workspace 自动 mkdir。
- 键集合三方一致：compose `${VAR}` ≡ overlay `.env.example` ≡ 根 client
  `.env.example` 注释段。构建参数（BASE_IMAGE/MIRROR）用注释态键也计入。

### 7.5 标签
运行探测只用 podman-compose 自动写的
`io.podman.compose.project`/`.service`；业务标签仅 `org.specweave.*`。

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

1. `tasks/__init__.py`：`from . import <ns>`、建 Collection 注册全部任务、
   `ns.configure` 加端口/镜像段、模块 docstring 更新命名空间总数
2. 根 client `.env.example`：新增 `<NS>` 段
3. 根 client `README.md`：新增该栈小节（命令/端口/配置/AI 规则链接）
4. client `AGENTS.md`：顶部说明、项目概述（命名空间数/overlay 行）、
   嵌套路由树、上下文路由表（2 行：任务行+镜像行）、规范入口表、
   P0 速览新增 `C##` 约束、变更日志
5. `.agents/README.md`：rules 数量、目录树、资产表、文档↔规则对应表、changelog
6. `apps/AGENTS.md`：应用路由表 client 行 + 边界声明表（若新规则文件）
7. 新建 `.agents/rules/<ns>-overlay.md`（内容含 §7 全部红线 + 栈特有契约）

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
  与镜像无关），注释里保留实证日期。
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
  `apps/containers/client`；`_SOURCE_MOUNTS` 默认值锚
  `root.parents[2]`（仓库根），仓库内应用写 `"apps/<dir>"`、
  external 写 `"external/..."`。锚成 client 又带 `apps/` 前缀会拼成
  `apps/apps/<dir>`（2026-09-14 monetize 实战）。注意三套锚点不同：
  invoke 默认值锚仓库根；compose.yaml 裸 compose 插值相对 compose.yaml
  所在 overlay 目录（通常 `../../../<dir>` / `../../../../<dir>`，按层级数）。
- **G13 Windows 平台门禁会遮蔽 Linux-only 分支的 NameError**：任务入口
  `_gate_platform()` 在 Windows 直接 Exit(1)，其后的
  `shutil.which(...)` 等 Linux/WSL 分支在 Windows 永不执行——
  `py_compile` 不查未定义名，漏 import（如 shutil）只能在 WSL 内复现。
  静态门禁必须包含：① `ruff check`（F821 undefined name）或 pyflakes
  对生成的任务模块；② WSL 发行版内 `invoke <ns>.build` 真实跑过门
  （不能只在 Windows 侧验证门禁 Exit 1）。

## 11. 验证链（门禁顺序，不可跳真实构建）

1. **静态**：新 py `py_compile`、bash `bash -n`；功能性文件 grep 禁项
   （`external/chaos/ai`、`--mount=type=bind`、`CHAOS_ROOT`、`/builder/`、
   `import podman`、`--privileged`，文档事实表述除外）；
   `podman-compose config` 渲染断言；`invoke --list` 任务齐；
   Windows 侧 `invoke <ns>.ps` 实跑确认 Exit 1 门禁；md 相对链接可达；
   键集合三方 diff 为空
2. **真实构建**：WSL2 machine 内 `podman build`（或 invoke build）退出
   0；镜像 inspect 入口链/无 Healthcheck；构建期守卫 root+devuser PASS
3. **E2E**：up 后端口/HTTP、挂载点、内核（如有）、exec 冒烟；
   形态 B 验证源码来自挂载路径前缀；长任务跑通一次；down 幂等
   （容器/网络清零、bind 保留、volume 默认保留/--volumes 删除）
4. **独立 Review**：复杂/高影响栈走 Spec Mode fresh-context 审查
   （rule+rubric AC）；actionable 全部修复后才视为完成

## 12. 安全检查清单

- [ ] 三必需标准字段、无 privileged/socket/host 网络
- [ ] 所有 bind 长语法 + create_host_path；invoke 绝对 POSIX + 存在性校验
- [ ] Windows 原生门禁 Exit 1 且指引可执行
- [ ] 构建期不读宿主源码（上下文=栈目录）；无 BuildKit bind/外部目录依赖
- [ ] 外部/只读源码树零修改（若运行时会临时改写：注入-还原幂等 +
  trap/自愈 + 前后 hash 快照，参见 xmnn AST 注入模式）
- [ ] 守卫为硬失败（FATAL/exit≠0），无 WARNING 静默放行关键项
- [ ] 产物验证在隔离环境（临时 venv/干净变量），不污染开发环境
- [ ] 键集合/任务名/端口/文档三处一致；登记点 7 项全勾
- [ ] `.dockerignore` 用 `**/` 嵌套模式，交付镜像无错误版本 pyc/临时态

## 13. Changelog

- **v1.0.0** (2026-09-14): 初始版本。萃取 onnx-quantized（形态 A）与
  xmnn-dev（形态 B，经两轮 fresh-context 审查）的共同骨架：3 个
  compose/namespace/.env 骨架模板、12 件套清单、7 个接线登记点、
  11 条实测 Gotchas（G1~G11）、四级验证链。
