# jupyter-podman-client - AI协作者入口 (AGENTS Manifest)

> **启动协议（PRIORITY ZERO — 所有智能体必须遵循）**
>
> ```
> 步骤 1：读取本文件全文（含首部「启动协议」四个字）
> 步骤 2：确认父级工作区 — 本项目是 SpecWeave apps/containers/ 下的消费端子应用，
>         全局规则继承自 SpecWeave 根 AGENTS.md 与 apps/AGENTS.md（应用区入口路由）
> 步骤 3：按「文档边界」声明：本项目对外的人类可读文档已原子化拆分至 `docs/` 目录（`docs/README.md` 为唯一索引入口）；AI 级硬约束以本文件路由表指向的 .agents/rules/*.md 为唯一权威
> 步骤 3.5：自检 — 逐项勾选：
>   □ 已完成内容敏感度预检（本项目=公开开源代码，产出物一律放 client 根目录
>     或 docs/ 对应子目录，禁止向 apps/containers/client/.agents/docs/ 写入）
>   □ 父级 AGENTS.md 已回读磁盘原文（启动协议步骤 1.1），与系统注入一致
>   □ 本次任务若命中 vendor 方法论资产（podman-py/七概念/等），对应规范已加载
>   □ 进入 client 子目录后遵循「嵌套优先」，未覆盖规则回退到根/ apps/ 两级
> 步骤 4：在规范指导下执行任务
> ```
>
> 本文件是 **jupyter-podman-client（镜像消费端）** 的 AI 协作者入口。本项目定位为
`apps/containers/jupyter-podman-rootless` 的消费端：基于 `podman-py` 从本地 tar 缓存加载镜像，
并提供极简 invoke 任务的容器生命周期管理；**根运行路径没有构建流程、没有 ML 模型管理**，
核心能力是「跨平台 SDK 连接 + rootless 三必需」，其中 **Windows 11 WSL2 支持是本项目的差异化场景**。
自 2026-09-13 起新增 **opt-in 的 `quant.*` 工作负载栈命名空间**（podman-compose 子进程层，
驱动 `overlays/onnx-quantized` 量化叠加镜像）；该层与根运行路径平行、互不回流，
Windows 原生门禁（详见 [.agents/rules/quant-overlay.md](.agents/rules/quant-overlay.md)）。
自 2026-09-14 起新增第二个 opt-in 工作负载栈 **`xmnn.*` 命名空间**（同样
podman-compose 子进程层），驱动 `overlays/xmnn-dev` 开发/打包叠加镜像：
运行时 bind 挂载 npu_tvm/npuusertools/models 源码，容器内 LLVM 22 + Nuitka 4.2.1
工具链支撑源码调试与 xmnn whl 打包，Windows 原生门禁
（详见 [.agents/rules/xmnn-overlay.md](.agents/rules/xmnn-overlay.md)）。
同日新增第三个 opt-in 工作负载栈 **`monetize.*` 命名空间**（podman-compose
子进程层），驱动 `overlays/agent-monetize-dev`：client-overlay-scaffold
形态 B 轻量变体，apt clang + pip apache-tvm-ffi 编译单 C++ tvm-ffi 模块、
单一 cp314 GIL ABI、setuptools 纯 Python wheel，运行时挂载
apps/agent-monetize 源码，Windows 原生门禁
（详见 [.agents/rules/monetize-overlay.md](.agents/rules/monetize-overlay.md)）。
2026-09-16 起新增第四个 opt-in 工作负载栈 **`xmnnrt.*` 命名空间**（同为
podman-compose 子进程层），驱动 `overlays/xmnn-runtime` **wheel 消费型
运行时镜像**：与 xmnn-dev 构建器/builder 分离——`xmnn.wheel` 只产 whl，
xmnnrt 把预构建 whl 装入干净运行时镜像（无 LLVM/Nuitka 工具链、零源码
挂载，cp314 GIL base env + 交付 Jupyter 内核，2225/8893），Windows
原生门禁（详见 [.agents/rules/xmnnrt-overlay.md](.agents/rules/xmnnrt-overlay.md)）。
>
> 所有全局规则（沟通语言、提交规范、上下文节省、路径引用）继承自 SpecWeave 根工作区；
> 本文件仅定义本项目特有的上下文路由与约束入口。

## 项目概述

- **项目类型**：容器镜像消费端（Invoke 任务包 + podman-py SDK 强依赖）
- **目标镜像**：`localhost/jupyter-podman-client:latest`（基于 rootless 叠加的通用镜像管理枢纽，可在其中运行/管理任意本地镜像）
- **编排架构**：根运行路径为两层后端自动降级——podman-py SDK（优先）→ CLI fallback（`podman.exe` 子进程）；**另有 opt-in 的 `quant.*` podman-compose 子进程层**（仅工作负载栈，不回流根 run）
- **Python 环境**：Python ≥ 3.14，构建后端 scikit-build-core，src 布局，wheel package=`["src/jpman_client"]`
- **跨平台**：WSL2 / Linux（原生 unix socket）+ macOS + **Windows 11 原生 CPython（WSL9P/Machine/tcp 多候选）**
- **任务管理**：invoke（`src/jpman_client/tasks/` 包，根 `tasks.py` 仅转发入口），七命名空间——根（`load`/`images`/`save`/`run`/`stop`/`status`/`clean`）+ `container.*` 别名 + `env.*` 自举（`build-layer`/`run-cmd`/`shell`）+ `quant.*` 量化栈（6 任务）+ `xmnn.*` 开发/打包栈（10 任务，LLVM/Nuitka 双 ABI，含离线归档 save/load）+ `monetize.*` 开发/tvm-ffi 原生编译打包栈（`build`/`up`/`down`/`ps`/`logs`/`smoke`/`build-native`/`wheel`，apt clang+apache-tvm-ffi 轻量栈）+ `xmnnrt.*` wheel 消费运行时栈（6 任务，build/up 自动暂存 workspace/dist 最新 whl）；后四者为 podman-compose 子进程层，Windows 原生门禁
- **编排内核（2026-09-15 重构后）**：三栈共享数据驱动内核 `tasks/overlay_core.py`（`StackSpec`/`SourceMount`/`SmokeSpec`/`TaskDocs` frozen dataclass + gates/prepare_env/compose_argv/run_compose/reconcile/build/up/down/ps/logs/smoke 内核 + `make_stack_tasks()` 六任务工厂，`supports_offline` 栈额外生成 `save`/`load`）；`quant.py`/`xmnn.py`/`monetize.py` 已瘦身为纯声明模块（`<NAME>_SPEC` + `TASKS` 字典 + 六别名，长任务例外），同构编排函数唯一定义在内核（详见 C14）
- **组内共享包**：平台/进程/容器只读工具与 SDK 连接层唯一实现在兄弟目录 [../shared](../shared)（包名 `jpman_common`，发行名 jpman-common 0.1.0，scikit-build-core 纯 Python 包）；本包 `utils.py`/`client_core.py` 仅再导出垫片，pyproject 依赖 `jpman-common`；安装顺序先 shared 后 client（见 [docs/01-getting-started.md](docs/01-getting-started.md)）；**叠加镜像构建同序**——`env.build-layer` 经命名构建上下文 `--build-context shared=../shared` 把 shared 送入 Containerfile.client 的 `COPY --from=shared`（2026-09-15 修复，详见 [docs/08-env-bootstrap.md](docs/08-env-bootstrap.md)）
- **工作负载叠加层**：`overlays/_shared/base-rootless.yaml`（rootless 基服务 `rootless-base`：三必需+凭证四变量+network_mode bridge+公共 label/restart，extends 单一事实源）；`overlays/onnx-quantized/`（ONNX 量化，cp314t 五包+3 冒烟，2222/8888）；`overlays/xmnn-dev/`（XMNN 源码调试+Nuitka 打包【构建器】，双 ABI+LLVM 22，2223/8890，bind npu 源码）；`overlays/agent-monetize-dev/`（agent-monetize 源码调试 + apt clang/apache-tvm-ffi 编译单 tvm-ffi .so + 纯 Python wheel，单一 cp314 GIL，2224/8892，bind apps/agent-monetize）；`overlays/xmnn-runtime/`（**wheel 消费型运行时**：安装预构建 whl 到 base env，无工具链/零源码挂载，2225/8893，wheels/ 暂存 whl 不入 git）。四栈 compose.yaml 以 `extends: {file: ../_shared/base-rootless.yaml, service: rootless-base}` 继承基段
- **Windows WSL 核心能力**：SDK 连接四级优先级（P0 env → P1 WSL9P → P2 Machine → P3 tcp），三变量逃生舱（`PODMAN_CLIENT_SDK_STRATEGY` / `WSL_DISTRO_NAME` / `CONTAINER_HOST`），W-I1~W-I3 30秒速查表
- **rootless 三必需**（所有启动路径硬编码，调用方不可覆盖）：`--device /dev/fuse` + `--security-opt label=disable` + `--cgroupns=host`，**严禁 `--privileged`**
- **运行时透传**（对齐构建端 `docs/07-toolbx-passthrough.md`）：`invoke run` 提供 5 个独立开关 `--host-network` / `--wayland` / `--gpu` / `--usb` / `--dbus`，**默认全关 = 默认隔离**；参数由 `utils.py::build_passthrough_spec` 统一产出（SDK 与 CLI 共用同一份，禁止各自拼接）；资源在 daemon 宿主侧解析，缺失时按 **C-I3** 诊断翻译为可执行指引
- **挂载/连接 A/B 维度分离**：Dimension A=容器卷挂载路径（D:\→/mnt/d/，`to_posix_path`）；Dimension B=SDK daemon URL（Windows 原生必须显式 `base_url`，`sdk_base_url_candidates`）
- **父级工作区**：SpecWeave 根目录（`../../../AGENTS.md`） → apps 入口（`../../AGENTS.md`）— 全局规则、Skill、角色、七概念指令均以父级为准
- **AI 资产容器**：`.agents/` 目录（本项目特有规则，按单一职责原子化拆分；其余子目录预留占位，未定义即回退父级）
- **内容敏感度**：本项目所有代码/文档均为公开内容，产出物入根 `docs/` 或本目录；私域镜像 tar / 个人工作区路径默认不入 git，由 `.gitignore` 守卫

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则、Skill、角色、团队、七概念指令）
  └─ apps/AGENTS.md（应用区入口路由，containers/client 条目回退到本文件）
       └─ apps/containers/client/AGENTS.md（本文件 = 消费端子应用路由入口）
            ├─ README.md                       ← 人类可读文档入口（项目定位 + 文档导航）
            ├─ docs/                           ← 人类可读文档集（00-12 原子文档 + 索引，对齐构建端 docs/ 先例）
            ├─ .agents/README.md               ← AI 资产容器索引
            │   ├─ CHANGELOG.md                ← 项目变更日志（原子提交汇总）
            │   └─ rules/                      ← 单一职责原子化硬约束
            │       ├─ invoke-tasks.md         ← src/jpman_client/tasks/ 包结构 / 命名空间 / CLI fallback 行为承诺
            │       ├─ sdk-connection.md       ← podman-py 连接策略、6 scheme 白名单、逃逸舱四策略
            │       ├─ windows-wsl.md          ← Windows 11 × WSL2 三级探测 + W-I1~W-I3 速查
            │       ├─ quant-overlay.md        quant.* podman-compose 工作负载栈（门禁/三必需映射/深合并/镜像契约）
            │       ├─ xmnn-overlay.md         xmnn.* 开发/打包栈（双 ABI/LLVM 22/源码运行时挂载/AST 还原/SONAME 守卫）
            │       ├─ monetize-overlay.md     monetize.* tvm-ffi 原生编译栈（apt clang/单一 GIL/3 处源码适配/.so 不入 wheel）
            │       └─ xmnnrt-overlay.md       xmnnrt.* wheel 消费运行时栈（builder/runtime 分离/whl 暂存/干净环境 9 项守卫/交付内核）
            ├─ overlays/                      ← 工作负载叠加层（opt-in，镜像与 compose 栈自包含）
            │   ├─ _shared/base-rootless.yaml ← rootless 基服务（extends 单一事实源：三必需/凭证四变量/bridge/logging k8s-file/labels/restart）
            │   ├─ onnx-quantized/            ← ONNX 量化工具链（Containerfile.quantized + compose*.yaml + smoke/ + docs/）
            │   ├─ xmnn-dev/                  ← XMNN 源码调试+Nuitka 打包【构建器】（Containerfile.xmnn-dev + compose.yaml + builder/ + smoke/）
            │   ├─ agent-monetize-dev/        ← agent-monetize 调试+tvm-ffi 原生编译/纯 Python wheel（Containerfile.agent-monetize + compose.yaml + builder/ + smoke/）
            │   └─ xmnn-runtime/              ← XMNN wheel 消费运行时【运行时】（Containerfile.xmnn-runtime + compose.yaml + wheels/ whl 暂存 + smoke/ + scripts/）
            ├─ ../shared/                     ← 组内共享包 apps/containers/shared（jpman_common：connection 连接层 + proc/platform_paths/containers 只读工具；先安装）
            ├─ tasks.py                        ← invoke 入口转发器（转发至 jpman_client.tasks）
            ├─ src/jpman_client/tasks/         ← invoke 任务定义（10 个模块：__init__ / client_core / env_in_container / manage / overlay_core 内核 / quant / xmnn / monetize / xmnnrt 声明栈 / utils 垫片）
            ├─ tests/                          ← daemon-free 单测：test_overlay_core.py（内核黄金快照）+ test_tasks_surface.py（命名空间表面黄金清单）+ test_compose_merge.py（extends 合并 AC-3）
            ├─ pyproject.toml                  ← Python 配置（jpman-common + podman + python-dotenv + scikit-build-core；[compose] extra = podman-compose）
            ├─ .env.example                    ← 环境变量模板（容器级 9 + SDK 4 + 四栈插值键）
            └─ .gitignore                      ← git 忽略（.env / __pycache__ / .temp / workspace / 等）
```

**嵌套优先原则**：进入本目录后优先读取本文件；详细约束按主题加载 `.agents/rules/` 对应文件；未覆盖的规则按 client → apps/containers → apps → SpecWeave 根 逐级回退。

## 上下文路由表

| 任务类型 | 必读入口 | 说明 |
|---------|---------|------|
| invoke 任务新增/修改（load/run/stop/status/clean） | [.agents/rules/invoke-tasks.md](.agents/rules/invoke-tasks.md) | 两层后端架构、`get_client() yield None` 零回归承诺、命名空间别名一致性 |
| podman-py SDK 连接行为修改 / 新增 scheme | [.agents/rules/sdk-connection.md](.agents/rules/sdk-connection.md) | 6 合法 scheme 白名单、无 npipe、`base_url` 在 Windows 必须显式、策略归一化 |
| Windows 11 WSL2 探测逻辑修改 / 新增发行版兼容 | [.agents/rules/windows-wsl.md](.agents/rules/windows-wsl.md) | 3 级发行版回退、UID 不硬编码 1000、UTF-16 LE 解析中文 Windows、W-I1~W-I3 修复 |
| 容器配置（rootless 三必需 / 卷挂载 / 端口映射） | `src/jpman_client/tasks/utils.py::ContainerConfig`（源代码真源，定义于 utils.py:197；注意 `../shared` 的 `containers.py` 仅有只读探测两函数） + [docs/06-run-discipline.md](docs/06-run-discipline.md) | 严禁 `--privileged`；挂载路径走 `to_posix_path` |
| 新增第四工作负载栈（声明 StackSpec） | [.agents/rules/invoke-tasks.md](.agents/rules/invoke-tasks.md) §声明式栈 + [../../../.agents/skills/client-overlay-scaffold/SKILL.md](../../../.agents/skills/client-overlay-scaffold/SKILL.md) | 2026-09-15 后新栈只能写声明模块：`<NAME>_SPEC` StackSpec + `TASKS` + 六别名；compose 用 extends `_shared/base-rootless.yaml`；禁止复制编排同构函数（C14） |
| quant.\* 工作负载栈（量化叠加镜像/compose up-down/冒烟/GPU opt-in） | [.agents/rules/quant-overlay.md](.agents/rules/quant-overlay.md) | 子进程边界（禁 import podman）、Windows 原生门禁、三必需 compose 映射、list 追加深合并、镜像守卫契约 |
| 叠加镜像 Containerfile.quantized 修改 / 量化包版本 / 冒烟脚本 | [overlays/onnx-quantized/](overlays/onnx-quantized/README.md) + [quant-overlay.md](.agents/rules/quant-overlay.md) §6 | FROM rootless、main cp314t、版本三重实证、OCI 引号教训、守卫不可删 |
| xmnn.\* 开发/打包栈（源码挂载/TVM 编译/Nuitka wheel/双 ABI） | [.agents/rules/xmnn-overlay.md](.agents/rules/xmnn-overlay.md) | 子进程边界（禁 import podman）、Windows 门禁、双 ABI 不互换、源码仅运行时挂载、AST 注入还原、SONAME glob 守卫、ccache 卷 |
| xmnn-dev 叠加镜像/工具链/打包脚本/内核修改 | [overlays/xmnn-dev/](overlays/xmnn-dev/README.md) + [xmnn-overlay.md](.agents/rules/xmnn-overlay.md) | base cp314 GIL 打包/main cp314t 服务、LLVM 22.1.8 装 main、builder 资产自包含禁引 ai/、OCI 引号教训 |
| xmnnrt.\* wheel 消费运行时栈（whl 安装镜像/builder-runtime 分离/交付内核） | [.agents/rules/xmnnrt-overlay.md](.agents/rules/xmnnrt-overlay.md) + [overlays/xmnn-runtime/](overlays/xmnn-runtime/README.md) | wheel 唯一制品契约、whl 暂存 wheels/、cp314 GIL base env、无工具链零源码挂载、9 项干净环境守卫 |
| podman-compose 行为冲突裁决（G1 可信源，只读） | `../../../projects/awesome-okf-xs/doc/bundles/jishu/containers/podman-compose/`（concepts/02、03、06、08、10） | 深合并/插值/x-podman/选型以 OKF 知识包为准 |
| 人类可读文档更新（快速开始、WSL 落地、.env 清单） | [docs/README.md](docs/README.md) + [.env.example](.env.example) | 排障速查表（docs/04-troubleshooting-guide.md）与 utils.py `windows_diagnose_hint` 必须保持一一对应 |
| AI 资产容器索引 | [.agents/README.md](.agents/README.md) | .agents/ 目录结构、父级继承关系、预留占位目录说明 |
| 全局规则（提交/代码风格/沟通/修复闭环） | [../../../AGENTS.md](../../../AGENTS.md) → [.agents/global-core-rules.md](../../../.agents/global-core-rules.md) | 中文 commit、Conventional Commits、修复即闭环三阶段 |
| Skill 使用 | [../../../.agents/skills/](../../../.agents/skills/) | 优先 seven-concepts-cmd / jpman-podman-ops / atomic-commit-cmd / check-duplication-cmd |
| 七概念指令（R→I→E→C→A→F→V） | [../../../.agents/commands/seven-concepts.md](../../../.agents/commands/seven-concepts.md) | 复杂任务（如本次 WSL 支持改造）必须走方法论编排，禁止凭经验跳跃 |
| podman-py OKF v0.2 知识包（冲突裁决只读源） | `../../../projects/awesome-okf-xs/doc/bundles/jishu/containers/podman-py/concepts/01-connection.md` + `05-advanced.md` | 所有与 podman-py 行为相关的冲突以知识包 bundles 为最高可信度（G1级） |

## 核心规范入口

| 规范 | 入口 | 说明 |
|-----|------|------|
| 父级全局规则 | [../../../AGENTS.md](../../../AGENTS.md) | SpecWeave 根工作区入口（启动协议必经之路，必回读磁盘原文） |
| apps 应用区路由 | [../../AGENTS.md](../../AGENTS.md) | apps 区域总入口，containers/client 条目显式回退到本文件 |
| 本文件入口 | AGENTS.md（本文件） | jupyter-podman-client 子应用路由入口（启动协议嵌套路由） |
| AI 资产容器索引 | [.agents/README.md](.agents/README.md) | .agents/ 目录结构与父级继承关系清单 |
| Invoke 任务规范 | [.agents/rules/invoke-tasks.md](.agents/rules/invoke-tasks.md) | 两层后端 / CLI fallback / 命名空间 / 命令一致性 |
| SDK 连接硬约束 | [.agents/rules/sdk-connection.md](.agents/rules/sdk-connection.md) | 6 scheme / base_url 必显式 / 四策略逃生舱 |
| Windows WSL 规则 | [.agents/rules/windows-wsl.md](.agents/rules/windows-wsl.md) | 3 级发行版探测 / UTF-16 LE / W-I1~W-I3 速查 |
| quant 工作负载栈规则 | [.agents/rules/quant-overlay.md](.agents/rules/quant-overlay.md) | quant.\* 六任务 / podman-compose 子进程层 / 双门禁 / 三必需映射 / GPU 覆盖深合并 / 镜像守卫契约 |
| 量化叠加层（人类文档） | [overlays/onnx-quantized/README.md](overlays/onnx-quantized/README.md) | 快速开始、compose/inv 两路径、与 Docker 源变体差异表 |
| xmnn 开发/打包栈规则 | [.agents/rules/xmnn-overlay.md](.agents/rules/xmnn-overlay.md) | xmnn.\* 十任务 / 双 ABI 工具链 / 源码运行时挂载 / Nuitka 打包契约 / AST 还原 / SONAME 守卫 / §10 离线契约（`XMNN_OFFLINE` 单一事实源 + save/load 归档） |
| xmnn-dev 叠加层（人类文档） | [overlays/xmnn-dev/README.md](overlays/xmnn-dev/README.md) | 开发调试/打包手册、双 ABI、invoke/裸 compose、**两个过程（镜像构建有网 / 离线开发无网；归档导出导入 + 禁网开关 + 构建期离线完备性守卫）**、参数表、性能与排障 |
| monetize tvm-ffi 栈规则 | [.agents/rules/monetize-overlay.md](.agents/rules/monetize-overlay.md) | monetize.\* 八任务 / apt clang / 单一 cp314 GIL / tvm-ffi rpath / 3 处源码适配 / .so 不入 wheel |
| agent-monetize-dev 叠加层（人类文档） | [overlays/agent-monetize-dev/README.md](overlays/agent-monetize-dev/README.md) | tvm-ffi 原生编译/纯 Python wheel、invoke/裸 compose、与 xmnn-dev 轻量对比、排障 |
| xmnnrt wheel 消费运行时栈规则 | [.agents/rules/xmnnrt-overlay.md](.agents/rules/xmnnrt-overlay.md) | xmnnrt.\* 六任务 / builder-runtime 分离 / whl 暂存契约 / cp314 GIL 安装 / 交付内核 / 9 项硬守卫 |
| xmnn-runtime 叠加层（人类文档） | [overlays/xmnn-runtime/README.md](overlays/xmnn-runtime/README.md) | whl 消费镜像、invoke/裸 compose、与 xmnn-dev 分工表、暂存契约、排障 |
| 人类操作文档 | [docs/README.md](docs/README.md) | 文档导航索引：入门 / 使用参考 / 架构与高级主题（安装 / 快速开始 / WSL 说明 / .env 完整清单 / 分工表） |
| 环境变量模板 | [.env.example](.env.example) | 容器级 9 项 + SDK 级 4 项 + 四栈插值键完整带注释模板 |
| 源代码真源 | 编排内核 `src/jpman_client/tasks/overlay_core.py`；声明栈 `quant.py` / `xmnn.py` / `monetize.py` / `xmnnrt.py`；共享只读层与连接层 [../shared/src/jpman_common/](../shared/src/jpman_common/)（`utils.py`/`client_core.py` 仅再导出垫片） | 行为与文档冲突时以源代码为准，README/AGENTS 同步后通过对抗审查更新 |

## 项目约束速览（P0 硬约束，违反 = PR 打回）

详细约束已按主题拆分到 `.agents/rules/` 下 6 个文件；以下是违反即打回的 P0 清单：

| # | P0 约束 | 所在文件 |
|---|--------|---------|
| C1 | **podman-py 合法 scheme 只有 6 个**：`unix / http+unix / ssh / http+ssh / tcp / http`；**严禁**出现 `npipe://`（Windows 命名管道）——抛 `ValueError: Unsupported URL scheme` | [sdk-connection.md](.agents/rules/sdk-connection.md) |
| C2 | **Windows 原生 CPython 环境下，PodmanClient 构造必须显式传 `base_url`**；无参构造等价于调用 `from_env()`，其回退路径为纯 Linux 语义（`XDG_RUNTIME_DIR/run/user/$UID/podman/podman.sock`），Windows 原生必抛 `FileNotFoundError` 进入 W-I1 诊断 | [sdk-connection.md](.agents/rules/sdk-connection.md) |
| C3 | **所有 run 路径（SDK 与 CLI fallback）必须硬编码携带 rootless 三必需**：`--device /dev/fuse` + `--security-opt label=disable` + `--cgroupns=host`；**严禁** 任何路径出现 `--privileged` | [invoke-tasks.md](.agents/rules/invoke-tasks.md) + `utils.py::ContainerConfig` |
| C4 | **CLI fallback 行为承诺**：`get_client()` 必须是 `@contextmanager`，**只有所有 4 条候选路径都失败** 才 `yield None`；调用方 `if client is not None:` 判断零修改；新增候选不能破坏 CLI 回退 | [invoke-tasks.md](.agents/rules/invoke-tasks.md) + `client_core.py::get_client` |
| C5 | **WSL UID 不得硬编码 1000**；必须通过 `wsl.exe -d <Distro> id -u` 实际探测并 `lru_cache` 缓存 | [windows-wsl.md](.agents/rules/windows-wsl.md) + `utils.py::_wsl_user_uid` |
| C6 | **wsl.exe 输出编码必须显式 UTF-16 LE**（不是 UTF-8！）；中文 Windows PowerShell 5.1 默认输出是 UTF-16 LE，UTF-8 解析会乱码无法匹配发行版名 | [windows-wsl.md](.agents/rules/windows-wsl.md) + `utils.py::wsl_distro_name` |
| C7 | **逃生舱策略四值白名单**：`{auto, legacy, wsl, machine}`；非白名单值必须归一化为 `auto`，不得抛错；`legacy` 必须严格等价于旧行为（单次 `from_env()`，不走多候选） | [sdk-connection.md](.agents/rules/sdk-connection.md) + `utils.py::sdk_strategy_from_env` |
| C8 | **A/B 维度分离，禁止混淆**：容器卷挂载路径（`--workspace D:\...`）和 SDK 连接 URL（`PodmanClient(base_url=...)`）是两个彼此独立的维度，修改其中一个不能顺带改另一个的代码路径 | [windows-wsl.md](.agents/rules/windows-wsl.md) 维度表 + README §5.5 |
| C9 | **.env → os.environ 同步必须使用 `load_dotenv(override=False)`**；shell 中已显式 `export` / `$env:` 的同名变量优先级必须高于 `.env`，不得用 `override=True` 覆盖用户显式设置 | `manage.py::_load_env_overrides` |
| C10 | **修复即闭环三阶段**：任何 Bug 修复必须走 `修复点 → 预防（为什么下次不会再出现？如加白名单/加断言） → 闭环（诊断文案对齐速查表 W-I1~W-I3 / C-I1~C-I2，README 同步更新）`；严禁只做纯点修复不改对应 README/诊断文案。**容器内坑（C-Ix）与平台无关，其在 `windows_diagnose_hint()` 中的分支必须置于 `platform.system() != "Windows"` 守卫之前**，否则容器内（Linux）永远匹配不到 | 根 AGENTS 开发规范 + 本文件 §约束速览 |
| C11 | **quant.\* 是 podman-compose 子进程层**：quant.py 禁止 `import podman`；Windows 原生一律门禁 Exit(1)（双路径指引），POSIX 缺二进制提示 `[compose]` extra；rootless 三必需只允许用 compose 标准字段（devices/security_opt/cgroupns）表达，严禁 privileged，GPU 覆盖遵循 list 追加语义只写新增设备；compose 层禁止回流根 `invoke run` | [quant-overlay.md](.agents/rules/quant-overlay.md) + `quant.py` |
| C12 | **xmnn.\* 同为 podman-compose 子进程层**：xmnn.py 禁止 `import podman`，沿用 C11 双门禁/三必需标准字段、严禁 privileged、不回流根 run；**双 ABI 不可互换**——Nuitka 打包/内核固定 base env `/opt/conda/bin/python`（cp314 GIL，nuitka==4.2.1），main env 保持 cp314t，conda 装 LLVM 22.1.8 必须 pin `python=*=*cp314t`；**源码仅运行时 bind 挂载**（构建期零接触 external/chaos，禁引 ai/ 与 BuildKit bind）；打包内核自包含于 `/opt/xmnn-builder`，AST PREAMBLE 注入必须 trap 还原（外部源码树零修改），**容器内对宿主 bind 树禁 `cp -p`/`cp -a`/`--preserve` 复制元数据**（ACL 含未映射 UID 时内核 setxattr EINVAL；备份只复制字节、还原用内容回写原 inode、CMake 组装用 `cp -R`），SONAME glob 守卫不得降级为 WARNING；**离线契约（§10）**——`supports_offline` 声明 + `XMNN_OFFLINE` 单一事实源（`--offline` 必须在 `gates()` 前回写环境才能过 WSL 桥接）+ 离线 `up` 强制 `skip_build=True`（`--no-build` 已恒真，见 C16）+ 容器内禁网一律硬失败不降级 + **两阶段契约（§10）**——阶段一（有网）`build`+`save` 产出离线自足镜像并由构建期 §7 离线完备性守卫实测断言（编译/打包前端 + pyproject 声明的运行时依赖），阶段二（无网）`load`+`up --offline`+`build-tvm`/`wheel` 不得再补装依赖（缺项一律回阶段一） | [xmnn-overlay.md](.agents/rules/xmnn-overlay.md) + `xmnn.py` |
| C13 | **monetize.\* 同族子进程 + 单一 GIL/源码适配边界**：monetize.py 沿用 C11 双门禁/三必需/禁 privileged/不回流；编译/内核固定 base cp314 GIL（apache-tvm-ffi wheel 仅 cp314 GIL），apt clang + pip tvm-ffi 头库；agent-monetize 源码改动**仅限 3 处跨平台适配**（config.py/config.yaml/test_ffi.py，.dll→平台选择），不改打分业务与 build.ps1；.so 不打入 wheel | [monetize-overlay.md](.agents/rules/monetize-overlay.md) + `overlay_core.py` + `monetize.py` |
| C14 | **声明式栈分层红线（2026-09-15 重构后）**：① `jpman_common`（../shared）与 `overlay_core.py` **零栈知识**——内核只允许 import 标准库/`.manage`/`.utils`/`jpman_common`，**禁止 import quant/xmnn/monetize 或 podman**；所有栈差异经 `StackSpec` 字段表达；② `quant.py`/`xmnn.py`/`monetize.py` 及未来栈模块**只写声明**（`<NAME>_SPEC` + `TASKS` + 别名，长任务例外），**禁止内嵌与内核同构的编排函数**，模块 ≤160 行；③ compose 三必需/凭证/bridge 公共段**唯一事实源**为 `overlays/_shared/base-rootless.yaml`，栈 compose.yaml 只保留差异段并 `extends` 服务级继承，禁止重复三必需字段；④ podman SDK 只允许出现在 `jpman_common.connection`（optional `[sdk]` extra），栈模块禁 `import podman`（沿用 C11-C13） | [invoke-tasks.md](.agents/rules/invoke-tasks.md) §声明式栈 + [quant-overlay.md](.agents/rules/quant-overlay.md) §1 + `overlay_core.py` |
| C15 | **构建参数单一事实源（2026-09-18）**：四栈 build-arg 只允许经 `overlay_core.resolve_build_args()` 解析，键固定为**无前缀** `.env` 键 `PIP_MIRROR` / `CONDA_MIRROR` / `BASE_IMAGE` / `TORCH_FLAVOR`（与 `overlays/*/compose.yaml` 的 `${KEY:-默认}` 同键）；`invoke x.build`、`up` 内联构建、compose 内部 build 段三处必须同值——任一处硬编码 `"official"` / `spec.default_base_image` 都会让层缓存互失效（症状：换镜像源后每次 `up` 白重建）。CLI 旗标只覆盖单次 `build`，跨三处一致**必须写 `.env`**；新栈不得自建解析 | [invoke-tasks.md](.agents/rules/invoke-tasks.md) §5 + `overlay_core.py::resolve_build_args` + [docs/02-invoke-reference.md](docs/02-invoke-reference.md) |
| C16 | **构建执行者唯一（2026-09-18）**：`invoke x.up` 恒以 `up -d --no-build` 起容器（`compose_up_tail()` 无分支，离线/在线同构），镜像存在性**只由内核 `build_image()` 负责**——`compose.yaml` 的 `build:` 段自此仅服务裸 `podman-compose` 路径。默认 `up` 内联构建一次即起容器（此前内核与 compose 段各构建一次）；`--skip-build` 与 `--offline` 不做任何构建，**必须先过本地镜像存在性预检**（缺失 `Exit(1)` + 中文可执行指引），严禁让 compose 兜底。安全性依据：`image_tag(spec, env)` 与 compose 的 `${PREFIX}_IMAGE_TAG:-默认}` 同键同默认 → 内核产出的 tag 与 compose 解析的 tag 必然一致 | [invoke-tasks.md](.agents/rules/invoke-tasks.md) §5 + `overlay_core.py::compose_up_tail` + [docs/02-invoke-reference.md](docs/02-invoke-reference.md) |
| C17 | **`up` 输出收敛（2026-09-18）**：`invoke x.up` 起容器必须经 `overlay_core.run_compose_up()`（捕获 stdout/stderr 后过滤），不得用 `run_compose()` 裸透传——podman-compose 无 log_formatter 时以 `close_fds=False` 让 podman 继承 stdio，64 位对象 ID / 容器与网络名回显、rootless netns「无 systemd 会话总线」ERROR 会直通终端冲散编排层提示。判据唯一实现在 `is_benign_compose_noise()`，**只认白名单三式**（裸 64 位 hex / 整行等于容器名·`pod_<project>`·`<project>_default` / pasta-user.slice-dbus 行），有疑问一律保留。**失败路径零过滤**：非零退出码下 stdout/stderr 全量原样回放后再 `Exit(code=rc)`。仅 `up` 适用；`down`/`ps`/`logs`/`exec` 与 `build`/`build-tvm`/`wheel` 保持逐字实时透传 | [invoke-tasks.md](.agents/rules/invoke-tasks.md) §5 + `overlay_core.py::run_compose_up` + [docs/02-invoke-reference.md](docs/02-invoke-reference.md) |
| C18 | **xmnn 可选能力 opt-in（2026-09-20）**：GPU 与 torch 均**默认全关 = 默认隔离**，不开时镜像体积/设备面/离线契约与改造前逐字等价。① **GPU**：仅 `up --gpu` 才追加 GPU 覆盖文件（形态选择与运行期可用性门禁见 C19）；override 内 devices **只写一条** `${GPU_DEVICE:-/dev/dri}` 单 token 插值（`/` 开头=宿主机设备路径，否则=CDI 引用 `nvidia.com/gpu=all`，与根 `invoke run --gpu` 同键同语义）——podman-compose 1.6.0 把 devices 列表项**原样**下传为 `--device <item>`（vendor `podman_compose.py` L1382-L1383，不做冒号拆分），写成 `a:b` 两条并列必有一条非法；② **torch**：仅 `build --torch cpu\|cu130`（或 `.env TORCH_FLAVOR`）才装 wheel，取值是**白名单**而非自由文本（`""/cpu/cu130`，构建期网络请求目标不得由用户输入拼接），索引 `download.pytorch.org/whl/<flavor>`，pin `torch==2.14.0`（cu130 是 2026-09-20 实测唯一与 CPU 侧同 pin 的 CUDA 索引），装 **base env `/opt/conda`**（C13 双 ABI 不可互换），形态落 `/opt/xmnn-torch-flavor` 由构建期守卫 §8 断言「声明 vs 实物」；③ flavor **不参与镜像 tag**（沿用 `XMNN_IMAGE_TAG`，一 tag 一形态）；④ 内核 `make_stack_tasks()` 的 `up`/`smoke` 形参面 = **能力并集**（四路正交 + `_up_impl`），**禁止 if/elif 互斥分支**——否则同时声明 gpu 与 offline 后 `--offline`/`--no-offline` 会被 gpu 分支吃掉 | [xmnn-overlay.md](.agents/rules/xmnn-overlay.md) + `overlay_core.py::make_stack_tasks` + [docs/11-xmnn-overlay.md](docs/11-xmnn-overlay.md) |
| C19 | **opt-in 设备的运行期可用性门禁（2026-09-20）**：`--gpu` 类 opt-in 设备能力必须在**运行期 podman 宿主侧**验证可用性后再透传，**严禁**把缺省设备路径直接交给 podman（症状：WSL2 无 `/dev/dri` → `Error: stat /dev/dri: no such file or directory` + `up` exit 125）。内核 `resolve_gpu_device(c, spec, env) -> (token, form)` 是唯一解析入口，**三态**：① 显式设备路径（`/` 开头）经 `test -e` 校验；② 显式 CDI 引用校验 `/etc/cdi/*.yaml` 或 `/var/run/cdi/*.yaml` 已生成；③ 未设/空 → 按 `GPU_DEVICE_FORMS`（`/dev/dri` → `/dev/dxg`）顺序自动探测并**回写 `os.environ`**（compose 插值与提示同源）；全部失败 fail-fast + 中文指引。探测必须经 `run_cmd` 落在 podman 宿主侧，**禁止**本机 `Path.exists()`（Windows 原生与 WSL 发行版非同一文件视图，同 C-I3 纪律）。`form` 决定覆盖文件（`gpu_override_file`），**禁止**在 compose argv 处 if/elif 分派。WSL2 形态（`/dev/dxg`）必须叠加 `compose.gpu.wsl.yaml`——单文件挂载 `/usr/lib/wsl/lib/libcuda.so.1` → `/usr/lib/libcuda.so.1:ro` **到标准搜索路径**，**禁止**改 `LD_LIBRARY_PATH`（compose `environment` 是 mapping **替换**语义，设 `/usr/lib/wsl/lib` 会冲掉栈原有 TVM 库路径；挂整目录亦实测失败） | [xmnn-overlay.md](.agents/rules/xmnn-overlay.md) §11.1 + [quant-overlay.md](.agents/rules/quant-overlay.md) §3·§4 + `overlay_core.py::resolve_gpu_device` + [docs/04-troubleshooting-guide.md](docs/04-troubleshooting-guide.md) W-I16 |
| C22 | **Jupyter 登录态必须跨容器重建持久化（2026-09-20）**：栈 compose 若不持久化 `/home/devuser/.local/share/jupyter`（`jupyter_cookie_secret`/`notebook_secret` 所在），每次 `down/up` 重建容器即轮换密钥，旧浏览器标签页的 Terminal/notebook REST **在浏览器层被重定向/中止、服务端访问日志零记录**——表象像 PTY/WebSocket/rootless 权限故障，实为纯登录态失效。规则：① 该目录走**栈内命名卷**（xmnn 栈名 `xmnn-jupyter`），镜像内属主 1000:1000/mode 700，新卷首次 copy-up 属主与可写性必须真机实测保持；普通 down 默认保留，仅 `down --volumes` 与 ccache 卷同删（删后重登属预期）；**禁止 bind 宿主家目录/全局共享 secret 文件**（宿主耦合、跨栈串用、uid 漂移）；② `invoke <ns>.up` 横幅在 `JUPYTER_TOKEN` 非空时打印「直达」URL（`http://localhost:<port>/lab?token=...`），唯一实现为内核纯函数 `overlay_core.jupyter_direct_url(port, token)`（空/空白/None → 空串不打印，四栈同构），env 经 `prepare_env → _load_env_overrides`（dotenv 容忍 .env CRLF）；③ 排障纪律——浏览器 UI 请求失败时**第一刀二分「失败请求是否到达服务端日志」**，未到达即认证/浏览器层，禁止下查容器权限或重建镜像；Jupyter WS 路径是 `/terminals/websocket/<n>`（**无 `/api` 前缀**），REST 才是 `/api/terminals`，探测勿混用（速查 [04 C-I6](docs/04-troubleshooting-guide.md)） | [xmnn-overlay.md](.agents/rules/xmnn-overlay.md) §5·§6 + `overlay_core.py::jupyter_direct_url` + [docs/04-troubleshooting-guide.md](docs/04-troubleshooting-guide.md) C-I6 |
| C24 | **`.env` 留空时容器内生成的凭证必须由 `up` 横幅回读打印（2026-09-20）**：`USER_PASSWORD`/`JUPYTER_TOKEN` 留空是**常态**，此时两值由基底 entrypoint 在**容器内** `pwgen` 生成、只打印到**容器启动日志**——`up` 若只转发 `.env` 必然只能拿到空串（用户即据此误判「凭证丢失 / .env 未生效」）。规则：① `up` 收尾按 PROJECT/SERVICE 标签定位容器、从日志**头部**回读（`podman logs <cid> 2>&1 \| head -n 300`）并打印 `密码 <user> / <password>` 与「直达」URL，唯一实现为内核 `read_container_credentials` + 纯函数 `parse_container_credentials`（四栈同构）；**禁止用 `--tail`** ——凭证横幅在启动日志头部，`invoke <ns>.logs` 默认 `--tail=100` 只看尾部，正是「哪里都看不到」的第二重成因；② 密码必须用 `SSH login:` 行取到的用户名**反查**其 password 行，**禁止**只按 `password:` 匹配（`ALLOW_ROOT_SSH=yes` 时先命中 `Root password:`，会把 root 密码误报为开发用户密码）；③ **`.env` 全程只读、禁止回写**——凭证生成责任唯一留在基底 entrypoint，overlay 回写即制造第二处事实源并与 entrypoint 的 `-z` 判定打架（同 C9 单向同步契约）；④ 回读失败（容器未跑 / 日志无横幅）静默降级为不打印，**不得**阻断 up 主流程；⑤ **日志驱动必须为 podman 可读的 `k8s-file`**——基段 `_shared/base-rootless.yaml` 显式声明 `logging: {driver: k8s-file}`（四栈同构继承，`test_compose_merge.py` 正向断言锁死），**禁止**依赖宿主默认驱动：本机发行版默认 `log_driver = journald`，WSL 嵌套 systemd 命名空间下 `podman logs` 返回 0 字节（日志只在宿主 `journalctl` 里），会同时打挂凭证回读与 `invoke <ns>.logs`；改驱动后旧容器需重建一次生效 | [xmnn-overlay.md](.agents/rules/xmnn-overlay.md) §6 + `overlay_core.py::read_container_credentials` + [overlays/_shared/base-rootless.yaml](overlays/_shared/base-rootless.yaml) + [docs/11-xmnn-overlay.md](docs/11-xmnn-overlay.md) |

### 新增第四栈的唯一正确路径（2026-09-15 后）

禁止再复制 quant/xmnn/monetize 任一模块起手。标准路径：① 装载 [client-overlay-scaffold](../../../.agents/skills/client-overlay-scaffold/SKILL.md) 技能生成 12 件套；② Python 侧只写 `tasks/<name>.py` 声明模块（`StackSpec(...)` 经 `make_stack_tasks(spec)` 产六任务，按形态 B 追加长任务并在 `TASKS` 注册）；③ compose 侧以 `extends: {file: ../_shared/base-rootless.yaml, service: rootless-base}` 继承基段，只写 image/build/ports/volumes/栈专属 env；④ 在 `tests/test_tasks_surface.py` 黄金清单与 `tests/test_compose_merge.py` 渲染断言中登记新栈；⑤ 静态等价 + daemon-free 单测验收，真机 E2E 后补（清单见 [.agents/CHANGELOG.md](.agents/CHANGELOG.md) 2026-09-15 条目）。

## 快速开始（人类 & AI 共用最小验证路径）

```powershell
# === Windows 11 原生 CPython（推荐验证 WSL9P 路径） ===
# 1. WSL2 发行版内一次性启动 podman.socket（WSL9P 前置条件）
wsl -d Ubuntu -- bash -lc "sudo loginctl enable-linger \$USER && systemctl --user enable --now podman.socket"

# 2. 首次使用 Podman Machine 顺手把 known_hosts 写了（防 W-I3，没装可跳过）
# podman machine ssh true  # yes 回车

# 3. 先装组内共享包，再装消费端，验证 invoke 命名空间
cd apps/containers
pip install -e shared -e client
cd client
invoke --list   # 应看到：load / images / run / stop / status / clean + container.* 别名 + env.* 自举 + quant.*(6) + xmnn.*(10) + monetize.*(8) + xmnnrt.*(6)

# 4. 加载构建端最新缓存镜像 + 启动容器
invoke load      # 自动从 ../jupyter-podman-rootless/.image-cache/ 拿最新 tar
invoke run --workspace D:/spaces/SpecWeave   # 启动成功打印 SSH/Jupyter URL
```

Linux/WSL2 内原生跑消费端的步骤完全相同，Windows 特有分支零差异。

## 引用父级 SpecWeave 规范

本项目完全遵循 SpecWeave 工作区发现协议（五步发现流程）：
- AGENTS.md 包含「启动协议」关键词（文件首部醒目块，含 PRIORITY ZERO 字样）
- 正确声明嵌套父级：`apps/containers → apps → SpecWeave 根`，路由指向 `../../../AGENTS.md`
- 遵循嵌套优先原则，未覆盖规则逐级回退，不重复父级已定义规则
- AI 资产已原子化拆分至 `.agents/rules/` 目录（3 个主题文件 = 单一职责单一事实源）
- 预留占位目录（roles / skills / scripts / workflows / templates / docs）各有 `.gitkeep`，未来扩展可直接填充
- 人类可读文档以 `docs/` 为唯一文档中心（`docs/README.md` 索引），不新增 `.agents/docs/` 冲突路径

## 变更日志

- **2026-09-20 | fix: 三内部栈补齐 SSH host key 命名卷（quant / monetize / xmnnrt）**：承接同日 xmnn-dev 条目，把 host key 持久化推广到其余三个内部栈——三者同源于 rootless 基底且此前**无任何命名卷**，SSH host key 同样随重建轮换。命名规则取「卷名前缀 = invoke 命名空间前缀」（`quant-` / `monetize-` / `xmnnrt-ssh-host-keys`）；xmnnrt 内部栈**刻意与客户交付栈 `release/compose.yaml` 的 `xmnn-ssh-host-keys` 不同名**——两者项目名同为 `xmnn-runtime`，同名即共享实际卷、清理互相牵连（内部栈与交付包属不同生命周期）。同步修正 `xmnn.py` / `xmnnrt.py` 的 `down --volumes` help 文案（后者原写「本栈无命名卷，参数为空操作」已失真）。验收：三栈黄金快照增列 target → 五测试文件 **194 passed / 7 skipped**；三栈真实 `podman-compose config` 渲染逐一核对卷声明与挂载逐字正确（真机重建未做，两个栈正在运行避免中断，机制与 xmnn-dev 同源）。
- **2026-09-20 | fix: 补挂 `xmnn-ssh-host-keys` 命名卷，SSH 主机指纹跨容器重建稳定**：用户请求「验证 SSH 密钥与 Jupyter token 是否已正确挂载」，实测（`ssh -p 2223 devuser@localhost` 登录成功、Jupyter `/api/status` 带 token 200 / 无 token 403、命名卷 `xmnn-jupyter` 内 `notebook_secret` 时间戳早于本次重建）确认凭证链路全通，但 `podman inspect` 挂载表 + 启动日志 `[WARN] Host key volume not mounted at /var/lib/jpman/ssh-host-keys` 暴露**唯一缺口**：SSH host key 未持久化，住容器层、每次重建轮换（客户端遭 `REMOTE HOST IDENTIFICATION HAS CHANGED`）。修复：`overlays/xmnn-dev/compose.yaml` 新增第三个命名卷 `xmnn-ssh-host-keys` 挂 `/var/lib/jpman/ssh-host-keys`（基底 entrypoint 以 `mountpoint -q` 为唯一分流判据——挂载即持久模式，key 落卷内且 `sshd_config` 的 `HostKey` 指向卷路径；未挂载回退容器层生成并打 WARN）；卷名与落点**与客户交付栈 `overlays/xmnn-runtime/release/compose.yaml` 一致**。验收：`test_compose_merge.py` 黄金快照 `volume_targets` 增列该 target 后 **142 passed / 1 skipped**（1 例 `test_vs_real_rec_merge_probes` 为已知 WSL 侧 rec_merge 分歧，非本次回归）。同步 rules/xmnn-overlay §5、docs/11（持久化段 + 排障表 `REMOTE HOST IDENTIFICATION` 行改为「已根治 + 三情形甄别」）、overlay README（命令表/持久化块/调试工作流）。
- **2026-09-20 | fix: 工作区 9p 无主文件致 Jupyter 保存报 Permission denied（排障 W-I19）**：用户现场在 xmnn-dev 栈 JupyterLab（localhost:8890）打开工作区既有 `main.ipynb`，工具栏显示 `notebook is read-only`、保存弹 `File Save Error — Permission denied`，而**同目录新建**的 `Untitled.ipynb` 保存正常。七概念 I→F→V→C 诊断：决定性判据是容器内 `ls -lan /workspace` 显示该文件属主 **`65534 65534`**（nobody）、宿主侧为 **`100999:100999`**；实测 `/proc/1/uid_map` 为 `0→1000`、`1..65536→524288..589823`（`/etc/subuid` 基线 524288），宿主 100999 **不在任何映射区间** → 容器内呈现 nobody，容器 root 仅对已映射 uid 持 `CAP_DAC_OVERRIDE`，对该文件读写皆 EPERM、`chown` 报 `Operation not permitted` —— 即**容器内无解**；100999 = 100000+999 与 subuid 基线 100000 的运行时自洽，说明这批文件由**另一 UID 映射上下文**（Docker / 其他 WSL podman 实例）写入，工作区根 0777 使新建文件取挂载默认属主 1000，故只有旧文件卡死。V 阶段实测**证伪了两条直觉路径**：容器内 `chmod`（同需 CAP_FOWNER）与宿主侧 `chown`/`chmod`（`/mnt/d` 是 9p/drvfs 且挂载项**无 `metadata`**，`sudo chmod 600 f` 返回 0 而权限位不变、`sudo chown` 后属主不变）——「改属性」在本机无效。修复采用**宿主侧换 inode**：`cp` 备份 → `rm` → `cp` 回原路径（新 inode 取挂载默认属主 1000:1000），空垃圾目录 `.Trash-1000` 直接 `rm -rf`；递归扫描（剪除三个源码 bind）得 3 处同类一并处理。验收：容器内 `test -w` 通过、真机 `podman exec xmnn-dev cp` 覆盖写回成功、notebook 内容完好（JSON 可解析 / 3 cells / 983 字节与修复前一致）、容器内属主由 `65534` 变为 `0 0`。**无代码改动**（两条错误路径均经实测排除，自愈代码无处落脚）。同步 [docs/04](docs/04-troubleshooting-guide.md) 新增 **W-I19**（`65534` 判据 + 换 inode 三步 + chmod/chown 空操作陷阱）与 [rules/xmnn-overlay.md](.agents/rules/xmnn-overlay.md) §4「工作区 9p 无主文件契约」。
- **2026-09-20 | fix: 基段显式声明 `logging: k8s-file`，恢复 `podman logs` 可读（C24 前置）**：C24 落地后用户反馈「还是没有显示」——实测发现**真正的根因**：本机发行版把默认日志驱动设为 `log_driver = journald`（`/usr/share/containers/containers.conf`），而 WSL 嵌套 systemd 命名空间下 podman 读 journald 日志返回**空**（`podman logs <cid>` 0 字节；新建一次性容器复现；日志其实进了宿主 journal，只有 `journalctl CONTAINER_NAME=<name>` 能读）——于是凭证回读与 `invoke <ns>.logs` **同时**失效，后者其实一直是空的。修复：`overlays/_shared/base-rootless.yaml` 显式声明 `logging: {driver: k8s-file}`（四栈同构继承；podman-compose 支持该键并映射为 `--log-driver`，已核实其源码；`test_compose_merge.py` 新增 `test_base_declares_podman_readable_log_driver` 正向断言锁死，防「顺手删掉」静默回退）。真机验收：`inv xmnn.down && inv xmnn.up --gpu --skip-build` 重建后，容器驱动为 `k8s-file`、`podman logs` 9872 字节可读，up 横幅打印 `密码 devuser / <16 位>` 与 `直达 http://localhost:8890/lab?token=<32 位>`；单测 137 passed / 1 skipped（`test_compose_merge.py` + `test_overlay_core.py`）。代价：日志不再进宿主 journal（不跨容器删除保留）。同步 rules/xmnn-overlay §6、rules/quant-overlay §3、docs/11 凭证段、.agents/README 与 C24 条款⑤。
- **2026-09-20 | feat: `up` 横幅回读容器内生成的 SSH 密码与 Jupyter token（C24）**：用户反馈 `invoke xmnn.up --gpu` 后看不到 SSH 密码与 Jupyter token，且 `.env` 未见更新，疑为凭证丢失/配置未生效。七概念 I→F→V→C 诊断：`.env` 的 `USER_PASSWORD`/`JUPYTER_TOKEN` 留空是**设计常态**（经 `_shared/base-rootless.yaml` 以 `${KEY:-}` 空串透传，由基底 entrypoint 在**容器内** `pwgen` 生成、只打印到启动日志），而 overlay 路径对 `.env` 是**单向只读**（`_load_env_overrides` 只做 `.env → os.environ`，内核无写 `.env` 代码）→ 横幅只转发 `.env` 必然只见空串；第二重成因是 `invoke <ns>.logs` 恒带 `--tail=100` 只看日志**尾部**，而凭证横幅在**头部**，长日志下已被挤出窗口，导致「哪里都看不到」。修复：内核新增纯函数 `parse_container_credentials`（用户名反查密码行，避免误命中 `Root password:`）与 I/O 包装 `read_container_credentials`（按 PROJECT/SERVICE 标签定位容器，`podman logs <cid> 2>&1 | head -n 300` 从**头部**回读），`up_stack` 横幅打印 `密码 <user> / <password>（容器内自动生成，仅本机开发）`，「直达」行 token 改为 `回读值 or .env`（预设时同源，行为不变）；**`.env` 保持只读不回写**（凭证生成责任唯一留在 entrypoint），回读失败静默降级不阻断 up。验收：`tests/test_overlay_core.py` 新增 8 例（解析 4 类边界 + 横幅 2 分支，FakeRunner 增 ` logs ` 分派与 `container_logs` 注入点，默认空串保证既有用例零变化）→ **103 passed / 1 skipped**；全量 `pytest tests -q`（py314）**238 passed / 2 skipped / 8 failed**（8 例均为 `test_ast_inject.py` 既有 Windows 原生 bash 环境差异，非本次回归）；`py_compile` 零告警、`check-links.py` 无断链。同步 rules/xmnn-overlay §6、docs/11 凭证段、overlay README 与本 P0 清单（C24）。
- **2026-09-20 | fix: 容器重建轮换 Jupyter cookie secret 导致 Terminal 打开失败（C22 / C-I6）**：用户现场 xmnn-dev 栈 09:28-09:30 经 `invoke xmnn.up --offline` 重建后，旧浏览器标签页点 JupyterLab Terminal 打开失败（Console 见 `net::ERR_ABORTED`）。七概念 F→V→C→R→I→E（V 门强制）诊断：必要条件链逐级实测——curl `POST /api/terminals` 返 200、容器内 tornado 打 `/terminals/websocket/1`（WS 路径**无** `/api` 前缀）回显成功、devuser(1000) `pty.openpty()`+bash 正常、token 直访与 127.0.0.1 表单登录两路径 Terminal 均成功，且浏览器失败请求在服务端访问日志**零记录**（09:31:16 `Clearing invalid/expired login cookie`）→ 根因坐实为 `jupyter_cookie_secret` 位于容器临时层无持久化，重建即轮换密钥，旧 cookie 失效后请求在浏览器层被中止。即时恢复：硬刷新重登（用户已确认）。预防两改：① `overlays/xmnn-dev/compose.yaml` 新增命名卷 `xmnn-jupyter` 挂 `/home/devuser/.local/share/jupyter`（实测镜像内 1000:1000/700，新卷 copy-up 属主与可写性保持；真实 `podman-compose config` 渲染双命名卷通过），普通 down 保留、`--volumes` 与 ccache 同删；② 内核新增纯函数 `overlay_core.jupyter_direct_url(port, token)`（空/空白/None→空串），`up_stack()` 横幅打印带 token 的「直达」URL（env 走 prepare_env/`_load_env_overrides`，dotenv 容忍 .env CRLF），`xmnn.py` down --volumes help 文案同步。验收：compose 黄金快照 volume_targets 增列 jupyter（`tests/test_compose_merge.py`）+ 新 3 测试函数/5 用例（`tests/test_overlay_core.py`），全量 pytest 数字见 [.agents/CHANGELOG.md](.agents/CHANGELOG.md)（2 个存量失败与本次无关）；**真机已验证（用户批准后两次 down/up）**：卷挂载属主正确、密钥落卷内 `runtime/jupyter_cookie_secret`、两次重建 md5 逐字一致、旧登录 cookie 跨重建不带 token 访问/POST（带 XSRF 头）均 200、横幅直达 URL 两次均打印。同步 docs/04 新增 **C-I6**（含「服务端零日志⇒认证/浏览器层」判别四连与 WS 路径排障点）、rules/xmnn-overlay §5/§6、docs/11、overlay README 与本 P0 清单。
- **2026-09-20 | fix: `inv xmnn.up --gpu` WSL2 失败修复（C19）——opt-in 设备的运行期可用性门禁**：用户实测 `inv xmnn.up --gpu --skip-build` 在 `podman-machine-default` 内 exit 125，报 `Error: stat /dev/dri: no such file or directory`。根因：C18 的 `--gpu` 只追加覆盖文件、**零设备预检**，而 `compose.gpu.yaml` 缺省 `${GPU_DEVICE:-/dev/dri}` 是 PCI 形态假设——WSL2 无 `/dev/dri`，只有 `/dev/dxg`。修复：内核新增 `GPU_DEVICE_FORMS`（`/dev/dri` → `/dev/dxg`，顺序=探测优先级）、`gpu_override_file(spec, form)`、`resolve_gpu_device(c, spec, env)`（三态：显式设备路径 `test -e` / 显式 CDI 查 `/etc/cdi` 或 `/var/run/cdi` / 未设按顺序自动探测并**回写 `os.environ`**；全失败 fail-fast + 中文指引；探测一律经 run_cmd 落 podman 宿主侧，禁本机 `Path.exists()`），`compose_argv`/`run_compose`/`run_compose_up` 增 `gpu_form`（默认 `generic` 零回归）；新增 `compose.gpu.wsl.yaml`（xmnn/quant 各一）= `devices: [/dev/dxg]` + 单文件挂载 `/usr/lib/wsl/lib/libcuda.so.1` → `/usr/lib/libcuda.so.1:ro` 到**标准搜索路径**，**刻意不设 `LD_LIBRARY_PATH`**（compose `environment` 是 mapping 替换语义，设了会冲掉 TVM 库路径；挂整目录亦实测失败）；quant `compose.gpu.yaml` 由硬编码 `/dev/dri:/dev/dri` 改单条 `${GPU_DEVICE:-/dev/dri}` 与 xmnn 同构，`quant.py` 补 `gpu_device_env` + `bridge_env_keys`。验收：`pytest tests -q --ignore=tests/test_ast_inject.py` **182 passed / 1 skipped**（`-k "gpu or wsl"` 26 passed，新增 C19 用例 9 例 + 渲染断言 2 例）；真机 `inv xmnn.up --gpu --skip-build` 自动选中 `compose.gpu.wsl.yaml`、提示 `GPU /dev/dxg 已透传`、退出 0，容器内 `CDLL("libcuda.so.1")` 成功且 `LD_LIBRARY_PATH` 未被污染；quant 侧 `-f compose.gpu.wsl.yaml config` 解析通过。同步规则 §11.1.1/§11.1.2/§11.4 + quant-overlay §3/§4 + `docs/04` W-I16 + 两个 overlay README 与本 P0 清单。
- **2026-09-18 | fix: `up` 输出收敛（C17）——过滤 podman 原生回显噪声**：用户实测 `invoke xmnn.up --offline` 一屏中文编排提示被 4 行 podman 原生行冲散（2 行裸 64 位对象 ID + 1 行裸容器名 `xmnn-dev` + 1 行 `ERROR[0001] failed to move the rootless netns pasta process to the systemd user.slice: dbus: couldn't determine address of session bus`）。根因：podman-compose 无 `log_formatter` 时以 `close_fds=False` 让 podman 子进程**继承 stdio**（vendor `podman_compose.py` L1907），而仓库侧 `run_compose()` 是裸转发、无过滤层；podman-compose 亦无全局静默旗标（`-q` 语义恰为「只显示容器 ID」）。修复：内核新增 `run_compose_up()`——捕获 stdout/stderr → 按 `is_benign_compose_noise()` 白名单过滤 → 打印，命中时输出一行 `ℹ 已过滤 N 行 podman 原生回显噪声`；`up_stack()` 改走该函数。白名单只认三式：① 整行恰为 64 位十六进制；② 整行与 `compose_echo_names(spec)`（容器名 / `pod_<project>` / `<project>_default`）全等；③ pasta-user.slice-dbus 良性行（容器照常运行）。**失败路径零过滤**：非零退出码下 stdout/stderr 全量原样回放后再 `Exit(code=rc)`。验收：`pytest tests -q --ignore=tests/test_ast_inject.py` **166 passed / 1 skipped**（较 C16 基线净增 4 例：白名单四反例、成功路径过滤计数、失败零过滤+退出码透传、up 捕获 kwargs）；真机经 WSL 桥接实测 `xmnn.up --offline` 过滤 1 行、`quant.up --skip-build`（真实新建路径）过滤 3 行且栈可用。**范围**：仅 `up`；`down`/`ps`/`logs`/`exec` 仍为原生输出（`quant.down` 实测有同类 3 行噪声，如需收敛另行提案）。同步规则 §5 C17 / §6 测试现状、`docs/02`（C17 契约段）与本 P0 清单。
- **2026-09-18 | fix: 构建执行者唯一（C16）——`up` 恒 `--no-build`，消除双构建**：承接同日 C15 诊断的残留项——C15 只对齐了构建**参数**，未消除**执行者**，故 podman-compose 的 `up` 仍会对含 `build:` 段的服务再构建一次（vendor `podman_compose.py` L4098 `if not args.no_build:`），且那一半看不到 CLI 旗标、时点在内核之后。修复：`compose_up_tail()` 去掉 `offline` 分叉、**无参恒返回 `["up","-d","--no-build"]`**；`up_stack()` 预检条件由 `if offline:` 改为 `if skip_build:`（覆盖 `--skip-build` 与离线两条路径）；`_require_local_image()` 增加必填 `offline` 关键字并出两套中文可执行指引（离线指向 `save`/`load`，非离线指向 `up`/`build && up --skip-build`）。**语义变更**：`--skip-build` 自此诚实——不做任何构建，镜像缺失立即 `Exit(1)` 而非静默让 compose 兜底；依据是全仓 `--skip-build` 用法一律与「已有镜像」共现，`monetize.py` 的 `not_running_hint` 已同步改为指向默认路径。安全性依据：`image_tag(spec, env)` 与 compose 的 `${PREFIX}_IMAGE_TAG:-默认}` 同键同默认，tag 不会漂移。验收：`pytest tests -q --ignore=tests/test_ast_inject.py` **162 passed / 1 skipped**（较 C15 基线净增 2 例：`test_up_inline_build_runs_exactly_once`、`test_up_skip_build_without_local_image_exits_with_guidance`）；`test_compose_up_tail_adds_no_build_offline` 改写为 `test_compose_up_tail_always_no_build`（旧签名 `offline=` 已失效）。同步 `docs/02`（C16 权威契约段）、`docs/10`-`13`、规则 §5 C16 与 §6 测试现状、本 P0 清单与 C12 离线条款、四 overlay README、`.env.example`。
- **2026-09-18 | fix: 构建参数单一事实源（C15）——`up` 内联构建与 compose 段同键**：诊断出 `inv build` 与 `inv up` 在**默认参数子集上功能重叠**（`up` 未加 `--skip-build` 时内联调用同一个 `build_image()`，非重复实现），但重叠处有三处实伤：① `up_stack` 硬编码 `pip_mirror="official"`/`conda_mirror="official"`/`base_image=spec.default_base_image`，与 `overlays/*/compose.yaml` 的 `${PIP_MIRROR:-official}` 等**无前缀 .env 插值键**参数源不一致 → 按 `docs/10`/`docs/11` 的裸 `up` 示例换源后会全量白重建；② podman-compose 的 `up` 默认对含 build 段的服务执行构建，故非 `--skip-build` 的 `up` 会构建两次，且 `--skip-build` 只跳过内核那次、compose 段仍构建（语义名不副实）；③ 文档自相矛盾（`docs/10`/`11` 裸 `up` vs `docs/12`/`13` 的 `up --skip-build`），两处 overlay README 还写着"独立 build 只认 CLI 旗标"。修复：内核新增 `resolve_build_args()` 单点解析（`CLI 旗标 > shell export > .env > 默认值`），三个 build-arg 键固定为无前缀 `PIP_MIRROR`/`CONDA_MIRROR`/`BASE_IMAGE`（与 compose 段天然同键）；`build_image()` 与四栈 `build` 任务默认值改 `None` 走解析，`up_stack()` 不再传死值；新增 4 例断言（up 内联读 env / build 默认跟随 env / 无 env 回退 / 旗标优先）+ harness 清空三键防宿主污染。**跨三处一致必须写 `.env`，CLI 旗标只覆盖单次 `build`**。验收：`pytest tests -q` 160 passed / 1 skipped（非 bash 模块），未设 `.env` 时 argv 与旧行为逐字一致；同步 `docs/02`（新增 C15 契约段）、`docs/10`-`13`、`.env.example`、四 overlay README/.env.example、规则 §5 C15 与 P0 清单。
- **2026-09-17 | refactor: xmnn-dev 固化为「镜像构建（有网）/ 离线开发（无网）」两个过程**：不新增命令名（仍 10 任务），把既有任务固化为两阶段契约——阶段一 `xmnn.build` + `xmnn.save`（有网侧一次性），阶段二 `xmnn.load` + `xmnn.up --offline` + `build-tvm`/`wheel`/`verify-wheel.sh`（无网侧全可用）。核心新增**构建期离线完备性守卫**（`smoke/_toolchain_guards.py` §7）：断言编译/打包前端在脚本实际建立的 PATH 上可解析、`pyproject [project].dependencies` 声明的全部运行时依赖已装（单一事实源，用发行版元数据判定以避开 dist→import 名映射）、打包工具链已装——把「离线能不能用」从运行期问题转为构建期断言，缺口在有网侧 fail-fast，随 root/devuser 双跑自动双覆盖且不另设守卫入口；`build-tvm.sh` 补离线指引（源码 3rdparty 子模块属过程一预备，无网侧不可补），`verify-wheel.sh` 头注声明无联网点，Containerfile 横幅标示 phase-2 全离线；README 原「离线模式」章节改写为「两个过程」，`docs/11`、W-I14、规则 §10（三条新契约）/§8、C12、路由表同步。
- **2026-09-17 | feat: xmnn.\* 离线模式（镜像归档 save/load + `XMNN_OFFLINE` 全链路禁网）**：新增 `invoke xmnn.save`（导出 tar.gz + manifest/SHA256 + latest 软链，复用既有镜像缓存约定）与 `invoke xmnn.load --path`（manifest 校验后导入，幂等）；`StackSpec.supports_offline` 声明驱动工厂额外生成这两个任务，非离线栈表面零变化；新增 `up --offline`（等价 `XMNN_OFFLINE=1`，`--no-offline` 覆盖 `.env`）——强制跳过构建并追加 `--no-build`（podman-compose `up` 默认会重建含 build 段的服务，仅 `--skip-build` 不足以禁网）、镜像缺失 fail-fast 给中文指引、`build` 离线立即 Exit(1)、容器内打包禁网硬失败（numpy/scipy 不再 pip 兜底、Nuitka 去 `--assume-yes-for-downloads`、缺 gcc Exit 2）；关键约束：`--offline` 必须在 `gates()` 之前回写 `os.environ` 才能过 WSL 桥接（桥接只透传 env、不转发 CLI 参数）；不触碰 compose `environment` 段以保住合并黄金快照；版本边界明确为「运行 + 容器内编译打包」，**不含从零构建镜像**；测试新增 10 例（147 passed, 1 skipped）；规则见 xmnn-overlay §10 / C12，README 与 `.env.example` 同步离线章节与参数/排障行。
- **2026-09-16 | feat: xmnnrt.\* wheel 消费运行时栈 + xmnn-runtime 叠加层（builder/runtime 分离）**：`inv xmnn.wheel` 职责收敛为只产 whl；新增第四栈 `overlays/xmnn-runtime`（FROM 同一 rootless 基底，whl 装 base env cp314 GIL + ipykernel，注册 `Python 3.14 (xmnn runtime)` 交付内核，无 LLVM/Nuitka 工具链、零源码挂载，2225/8893）；`xmnnrt.build/up` 构建前自动从 workspace/dist 暂存最新 whl 进 wheels/（不入 git；`--wheel` 可指定）；构建期 9 项干净环境硬验证（site-packages 路径黑名单 + `_libs` 自包含 + `tvm.build('llvm')` + 内核可见，root/devuser 双跑）；新增规则 xmnnrt-overlay.md，落地 xmnn-overlay §9 的 scratch 栈裁决；测试黄金表（surface/compose-merge）登记，79 passed。
- **2026-09-15 | refactor: 学习 OKF 容器知识包（projects/awesome-okf-xs/doc/bundles/jishu/containers）重构 apps/containers**：新增组内共享包 `apps/containers/shared`（jpman-common：平台/进程/容器只读层 + connection 连接层唯一事实源，client 与 builder 共同依赖）；新增数据驱动内核 `tasks/overlay_core.py`（StackSpec + 六任务工厂），quant/xmnn/monetize 三栈瘦身为声明模块（88/158/121 行，同构编排函数零复制）；compose 公共段抽 `overlays/_shared/base-rootless.yaml` 经 extends 服务级继承（podman-compose 1.6.0 rec_merge 语义双证）；新增约束 C14；**已知行为变更**：quant 栈随基文件获得 `network_mode: bridge`（对齐 2026-09-14 xmnn aardvark-dns 实证）；真机 E2E 后置清单见 [.agents/CHANGELOG.md](.agents/CHANGELOG.md)；规格 `.trae/specs/infra-env/containers-okf-refactor/`。
- **2026-09-15 | docs: README.md 原子化为 docs/（00-12）+ 根入口精简**：对齐构建端 docs/ 先例；人类可读文档中心从根 README 迁至 `docs/README.md` 索引，AGENTS/.agents/README/构建端 entrypoint 锚点同步（详见 [.agents/CHANGELOG.md](.agents/CHANGELOG.md)）。
- **2026-09-14 | feat: agent-monetize-dev 叠加层 + monetize.\* 八任务**：client-overlay-scaffold 技能首次实战（形态 B 轻量变体）；apt clang + pip apache-tvm-ffi 0.1.13 编译单 tvm-ffi .so、单一 cp314 GIL、纯 Python wheel、3 处源码跨平台适配；端口 2224/8892，规则 C13；规格 `.trae/specs/infra-env/agent-monetize-dev-overlay/`。
- **2026-09-14 | feat: xmnn-dev 叠加层 + xmnn.\* 八任务**（经两轮独立审查 R2 pass）。

完整原子提交历史见 [.agents/CHANGELOG.md](.agents/CHANGELOG.md)。

- **2026-09-14** | feat: 新增 `overlays/xmnn-dev/` XMNN 源码调试+Nuitka 打包叠加层与 `xmnn.*` 八任务命名空间（build/up/down/ps/logs/smoke/build-tvm/wheel）——FROM rootless 薄叠加；双 ABI（base `/opt/conda` cp314 GIL 用 nuitka==4.1.3 打包/main 保持 cp314t 跑 Jupyter；LLVM/Clang 22.1.8 经 mamba pin `python=*=*cp314t` 装入 main）；运行时 bind 挂载 npu_tvm/npuusertools/models（四路径 invoke 侧绝对 POSIX 解析+存在性硬校验）；打包内核 `/opt/xmnn-builder` 自包含（移植 chaos/ai 能力但对 ai 目录零依赖：AST trap 还原、LLVM 库 SONAME glob+硬守卫、verify 临时 venv 零污染、ccache 命名卷）；compose 2223/8890 + bridge 实证 + 三必需；新增规则 xmnn-overlay.md（C12），规格见 `.trae/specs/infra-env/xmnn-dev-overlay/`
- **2026-09-13** | feat/refactor: onnx-quantized 从 docker-images 迁移至 client（Podman rootless + podman-compose）——新增 `overlays/onnx-quantized/`（Containerfile.quantized 薄叠加层 FROM rootless:latest，main cp314t 五包 onnx 1.22.0/onnxruntime 1.28.0/onnx-simplifier 0.5.0(wheel onnxsim 0.7.3)/onnxscript 0.7.1/onnxconverter-common 1.16.0 + `_quant_guards.py` 三守卫 + 3 纯 ONNX 冒烟脚本）与 compose.yaml/compose.gpu.yaml（三必需标准字段、GPU list 追加覆盖、长语法 bind）；新增 opt-in `quant.*` 命名空间（build/up/down/ps/logs/smoke，podman-compose 子进程，Windows 原生门禁+缺二进制门禁，C11）；pyproject 新增 `[compose]` extra；machine 端 E2E 实测：构建守卫/冒烟全 PASS（INT8 diff=0.0019/FP16=0.0002/QDQ 10 节点 0.0145）、up 端口 2222/8888 可达、标签接缝可用、down 零残留、run --rm 兜底路径通过；源 Docker 变体目录零改动

- **2026-09-12** | fix: `inv run` 在 UID≠1000 的原生 Linux exit=125 修复（B-scheme）——新增 `host_runtime_uid()` 单一事实源（`PODMAN_RUNTIME_UID`→`$XDG_RUNTIME_DIR` 末段→`os.getuid()`→Windows 回落 1000），`podman_sock_path()`/`host_runtime_dir()` 不再硬编码；新增 `ensure_host_podman_socket()` 预检+自愈（socket 缺失自动 `systemctl --user start podman.socket`，容器内/非 Linux 放行）；新增 C-I5 诊断并与 C-I3 分流（podman.sock 缺失不再误报"去掉 --wayland/--gpu"）；实测 UID 1006 宿主容器启动成功、devuser 可读写宿主 socket；同步 invoke-tasks S6/§6、README §5.4、.env.example
- **2026-09-12** | fix: `inv load` POSIX 平台 exit=125 修复（CLI 喂入方式平台分流）——新增 `utils.image_load_cli_command()` 单一事实源：POSIX 改 `podman load -i`（旧实现误用 Windows cmd 的 `type file |` 管道，且 podman 3.4.x 的 stdin 路径对未压缩 docker-archive 会误报 payload does not match；同文件 `-i` 实测正常），Windows 原生保留 `type |` 管道（WSL2 远距 daemon EOF 历史约束）；新增 C-I4 诊断并让失败消息携带原生 stderr；同步 invoke-tasks.md §3.2/S5、README §5.4 速查表
- **2026-09-10** | fix: 布尔参数改为三态 + `run` 任务关闭自动短选项——① 新增 `_resolve_bool()`（显式开 > 显式关 > `.env` > 默认；同开同关报参数冲突）并为每个布尔项配对 `--no-x`；**更正上一条**：`GRANT_SUDO=no` 与「CLI 关闭 .env 开启项」在单参数写法下实为无效（invoke 的 True/False 与「未指定」不可区分、反向旗标仅在 `default is True` 时自动生成），本次才真正生效；② `@task(auto_shortflags=False)` 修复 `-h` 被 `--ssh-public-key` 劫持（`invoke run -h` 直接报错）与 `--host-network` 退化到短名 `-`
- **2026-09-10** | feat: 同步构建端 `docs/07-toolbx-passthrough.md` 的 5 项运行时透传——`invoke run` 新增 `--host-network` / `--wayland` / `--gpu` / `--usb` / `--dbus`（默认全关）；新增 `utils.build_passthrough_spec` 统一 SDK/CLI 两条路径参数；新增 **C-I3** 诊断（透传资源缺失的原生报错翻译，含缺失路径 + 覆盖变量 + daemon 侧自检）；修复 `GRANT_SUDO=no` 因 `bool("no")` 判真而失效的既有缺陷
- **2026-09-10** | fix: 补全容器内 EACCES（C-I2）诊断与修复闭环（socket 属组自适应）并续接 `windows_diagnose_hint()` C-I2 分支；`inv load` / `inv run` 增加 podman 就绪预检与中文提示
- **2026-09-09** | fix: B-scheme 宿主 socket 直通端到端连通；`inv load` 增加镜像缓存完整性校验；`ensure_known_hosts` / `refresh_host_keys` 修复 Windows 路径失效与 sshd 就绪等待
- **2026-09-08** | feat/fix: 默认目标镜像泛化为 `jupyter-podman-client` 管理枢纽（叠加镜像 2.82 GB → 1.80 GB）；修复非 root 运行 entrypoint 致 `chpasswd` 失败容器退出；修复容器内 SDK socket ENOENT（C-I1，bootstrap 预建 `libpod/tmp` + `PODMAN_SERVICE_BOOT` 自举）
- **2026-09-07** | feat: Windows 11 WSL2 SDK 支持（四策略逃生舱、3 级发行版探测、W-I1~W-I3 诊断速查）；`tasks/` 迁移至 `src/jpman_client/tasks/`（5 模块）并保留根 `tasks.py` 转发层；新增 `env.*` 自举命名空间（`build-layer` / `run-cmd` / `shell`）；同步新增 `AGENTS.md` + `.agents/` AI 自治规范容器
- **2026-08-31** | refactor: 消费端首次拆分自构建端；初始版本发布（ContainerConfig + podman-py 两层后端 + rootless 三必需）
