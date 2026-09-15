# apps/containers - AI协作者入口 (AGENTS Manifest)

> **启动协议（PRIORITY ZERO — 所有智能体必须遵循）**
>
> ```
> 步骤 1：读取本文件全文（含首部「启动协议」四个字）
> 步骤 2：确认父级工作区 — 本目录是 SpecWeave apps/ 下的容器分组（Podman rootless 生态），
>         全局规则继承自 ../AGENTS.md（apps 应用区入口）与 ../../AGENTS.md（根契约）
> 步骤 3：按「成员路由表」确定目标成员，进入后读取成员自身 AGENTS.md（嵌套优先）；
>         shared 成员无独立 AGENTS，其治理由本文件 + .agents/rules/shared-package.md 代管
> 步骤 3.5：自检 — 逐项勾选：
>   □ 已完成内容敏感度预检（本组=公开开源代码；产出物落本目录 docs/ 或成员目录，
>     禁止向 .agents/docs/ 写入任何产出物）
>   □ 父级 AGENTS.md 已回读磁盘原文（启动协议步骤 1.1），与系统注入一致
>   □ 改动涉及 shared/ 或镜像/rootless 共同契约时，已加载 .agents/rules/shared-package.md
>   □ 未把成员规则/文档搬迁或复制到组层（组层反双写纪律 G4）
> 步骤 4：在规范指导下执行任务
> ```
>
> 本文件是 **apps/containers 容器分组**（Podman rootless 生态：构建端 + 消费端 + 组内共享包）
> 的组级路由入口。本文件**只承载跨成员事实与组级契约**（离开任一成员视角才成立的信息）：
> 成员内规则一律以成员自身 AGENTS.md / .agents/rules/ 为权威，本文件不复制、不搬迁。

## 分组概述

- **分组类型**：Podman rootless 容器生态，三成员协同——一个构建端、一个消费端、一个组内共享包
- **镜像流**：构建端 `invoke build` 产出 rootless Jupyter 镜像 → `podman save` 至构建端 `.image-cache/*.tar.gz` → 消费端 `invoke load` 自动取最新 tar 加载 → `invoke run` 管理生命周期
- **依赖流**：三成员同为 scikit-build-core 纯 Python 包（Python ≥ 3.14）；两端 pyproject 均声明依赖 `jpman-common`，**必须先 editable 安装 shared，再安装任一端**
- **共同运行契约**：全组所有容器启动路径携带 rootless 三必需（`--device /dev/fuse` + `--security-opt label=disable` + `--cgroupns=host`），**严禁 `--privileged`**（见 G3）
- **父级工作区**：[../AGENTS.md](../AGENTS.md)（apps 应用区路由）→ [../../AGENTS.md](../../AGENTS.md)（全局规则、Skill、角色、七概念指令）
- **AI 资产容器**：[.agents/](.agents/README.md)（组级仅一个规则主题：shared-package；其余子目录预留占位，未定义即回退父级）
- **人类文档**：[docs/](docs/README.md)（组级仅 2 篇：组全景 + 跨成员端到端快速开始）

## 成员路由表

| 成员 | 角色 | 包 / import 名 | AGENTS 入口 | 何时进入 |
|------|------|---------------|-------------|---------|
| [jupyter-podman-rootless/](jupyter-podman-rootless/README.md) | **构建端**：rootless Jupyter 镜像生产（Containerfile + entrypoint + 三层后端 compose→SDK→CLI + OMLMD/OLOT + Toolbx） | jupyter-podman-rootless / `jpman_builder` | [AGENTS.md](jupyter-podman-rootless/AGENTS.md)（7 rules + 18 docs） | 改镜像/Containerfile/entrypoint/构建期服务/ML 模型管理/jpman CLI |
| [client/](client/README.md) | **消费端**：加载 tar 镜像 + 容器生命周期（SDK→CLI 两层后端，Windows 11 原生 WSL2 差异化）+ 3 个 opt-in podman-compose 工作负载栈（quant/xmnn/monetize） | jupyter-podman-client / `jpman_client` | [AGENTS.md](client/AGENTS.md)（C1-C14 约束 + 6 rules + 13 docs） | 改 load/run/stop 任务、SDK 连接、Windows/WSL、任一 overlay 工作负载栈 |
| [shared/](shared/pyproject.toml) | **组内共享包**：SDK 连接层唯一事实源 + 平台/进程/容器只读工具；零栈知识 | jpman-common 0.1.0 / `jpman_common` | 无（**本文件 + [.agents/rules/shared-package.md](.agents/rules/shared-package.md) 代管**） | 改连接策略/路径转换/进程与容器探测；任何 `import podman` 新需求 |

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则、Skill、角色、七概念指令）
  └─ apps/AGENTS.md（应用区入口路由）
       └─ apps/containers/AGENTS.md（本文件 = 组级路由入口，仅跨成员事实）
            ├─ README.md                         ← 组级人类入口（三成员导航 + 端到端最短路径）
            ├─ docs/                             ← 组级人类文档（仅 2 篇，不复制成员文档）
            │    ├─ README.md                    ← 文档索引
            │    ├─ 00-overview.md               ← 组全景：三角关系 / 镜像流 / 端口与栈速查
            │    └─ 01-getting-started.md        ← 跨成员端到端：shared → 构建 → 缓存 → load/run
            ├─ .agents/                          ← 组级 AI 资产容器
            │    ├─ README.md                    ← 资产容器索引 + 父级回退链
            │    ├─ CHANGELOG.md                 ← 组级治理变更日志
            │    └─ rules/
            │         └─ shared-package.md       ← 唯一组级规则：jpman_common 治理边界
            ├─ shared/                           ← jpman-common（连接层 + 只读工具，先安装）
            ├─ jupyter-podman-rootless/AGENTS.md ← 构建端入口（嵌套优先；7 rules + 18 docs）
            └─ client/AGENTS.md                  ← 消费端入口（嵌套优先；C1-C14 + 6 rules + 13 docs）
```

**嵌套优先原则**：进入任一成员目录后优先读取最近的 AGENTS.md；未覆盖的规则按 成员 → apps/containers（本文件）→ apps → SpecWeave 根 逐级回退。

## 上下文路由表（任务类型 → 入口）

| 任务类型 | 必读入口 |
|---------|---------|
| 改 shared 包 / 新增 `import podman` / 连接层与只读工具归属裁决 | [.agents/rules/shared-package.md](.agents/rules/shared-package.md) |
| 镜像构建、Containerfile、entrypoint、supervisord、OMLMD/OLOT | [jupyter-podman-rootless/AGENTS.md](jupyter-podman-rootless/AGENTS.md) → 其 `.agents/rules/` 对应文件 |
| 消费端 load/run/stop、SDK 连接、Windows/WSL、排障速查 | [client/AGENTS.md](client/AGENTS.md) → 其 `.agents/rules/` 对应文件 |
| quant / xmnn / monetize 工作负载栈 | [client/AGENTS.md](client/AGENTS.md) C11-C14 + client `.agents/rules/{quant,xmnn,monetize}-overlay.md` |
| 组级人类文档（全景/端到端） | [docs/README.md](docs/README.md) |
| 成员内人类文档 | 各成员 `docs/README.md`（构建端 18 篇 / 消费端 13 篇） |
| 全局规则（提交/沟通/修复闭环/敏感度） | [../../AGENTS.md](../../AGENTS.md) → [../../.agents/global-core-rules.md](../../.agents/global-core-rules.md) |
| Skill / 七概念指令 | [../../.agents/skills/README.md](../../.agents/skills/README.md) / [../../.agents/commands/README.md](../../.agents/commands/README.md) |

## 组级约束速览（G1-G4，违反 = PR 打回）

组级约束只规定**跨成员边界**；成员内 P0 约束（client C1-C14、builder 各 rules）在成员文件中权威定义，此处不复制。

| # | 约束 | 权威事实源 |
|---|------|-----------|
| G1 | **jpman_common 是组内唯一共享运行时层**：podman SDK 只允许在 `jpman_common.connection` 中 import（optional `[sdk]` extra）；两端任务包仅经再导出垫片使用连接能力。shared **零栈知识**——禁止出现 quant/xmnn/monetize 等任何具体栈常量 | [shared/src/jpman_common/__init__.py](shared/src/jpman_common/__init__.py)（docstring + `connection.py`）；client AGENTS C14；[shared-package.md](.agents/rules/shared-package.md) |
| G2 | **安装顺序不可颠倒**：`pip install -e shared` 先于 builder/client 任一端（两端依赖 `jpman-common` 且本地以 editable 方式提供） | 三成员 `pyproject.toml`；[docs/01-getting-started.md](docs/01-getting-started.md) |
| G3 | **rootless 三必需 + 禁 privileged 是全组共同契约**：每条容器启动路径必须携带 `--device /dev/fuse`、`--security-opt label=disable`、`--cgroupns=host`，任何路径不得出现 `--privileged` | 构建端 [jupyter-podman-rootless/src/jpman_builder/tasks/manage.py](jupyter-podman-rootless/src/jpman_builder/tasks/manage.py)；消费端 [client/src/jpman_client/tasks/utils.py](client/src/jpman_client/tasks/utils.py) `ContainerConfig`；三栈公共段 [client/overlays/_shared/base-rootless.yaml](client/overlays/_shared/base-rootless.yaml)；成员规则 client C3 |
| G4 | **组层反双写纪律**：成员 rules/docs 不搬迁、不在组层复制；新增组级规则主题必须满足"跨 ≥2 成员成立且无现有归属者"，在 `.agents/rules/` 落单一文件，并同步本文件路由表 | 本文件；[.agents/README.md](.agents/README.md) |

## 快速开始（组级最短路径）

```bash
cd apps/containers
pip install -e shared                      # G2：共享包必须先装

# 路径 A（消费镜像）：构建端产出 → 缓存 tar → 消费端加载运行
cd jupyter-podman-rootless && pip install -e ".[compose]" && invoke build
# 按 jupyter-podman-rootless/docs/16-image-cache.md 导出 tar 至 .image-cache/
cd ../client && pip install -e . && invoke load && invoke run --workspace D:/spaces/SpecWeave

# 路径 B（仅日常驾驶构建端容器）：直接用 jupyter-podman-rootless/bin/jpman 零依赖 CLI
```

完整跨成员步骤、验证清单与可选工作负载栈见 [docs/01-getting-started.md](docs/01-getting-started.md)。

## 引用父级 SpecWeave 规范

- AGENTS.md 包含「启动协议」关键词（文件首部醒目块，含 PRIORITY ZERO 字样）
- 嵌套父级声明：apps/containers → apps → SpecWeave 根；未覆盖规则逐级回退
- AI 资产原子化于 `.agents/`（组级仅 shared-package 一个主题），预留占位目录各持 `.gitkeep`
- 人类可读文档以 `docs/` 为唯一组级文档中心（索引 + 2 篇），不新增 `.agents/docs/` 产出物路径
