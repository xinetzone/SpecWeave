# jupyter-podman-rootless - AI协作者入口 (AGENTS Manifest)

> **启动协议（PRIORITY ZERO — 所有智能体必须遵循）**
>
> ```
> 步骤 1：读取本文件全文
> 步骤 2：确认父级工作区 — 本项目是 SpecWeave apps/ 下的子应用，全局规则继承自 SpecWeave 根 AGENTS.md
> 步骤 3：按上下文路由表加载本项目特有规范（.agents/rules/ 下对应文件）
> 步骤 3.5：自检 — 确认已理解父级规则与本项目特有约束
> 步骤 4：在规范指导下执行任务
> ```
>
> 本文件是 jupyter-podman-rootless 子项目的 AI 协作者入口。本项目是一个基于 Podman rootless 模式的
> Jupyter 开发容器构建项目，所有全局规则（沟通语言、提交规范、上下文节省等）继承自 SpecWeave 根工作区，
> 本文件仅定义本项目特有的上下文路由与约束入口。详细规则已原子化拆分至 `.agents/rules/` 目录。

## 项目概述

- **项目类型**：容器镜像构建项目（Podman rootless + Jupyter Notebook 开发环境）
- **基础镜像**：ubuntu:26.04
- **核心功能**：OpenSSH Server + JupyterLab + Podman (rootless DinP)，通过 supervisord 管理多服务
- **Python 环境**：Python 3.14t (free-threading, cp314t, 无GIL) + Miniforge3 + libmamba
- **中文环境**：zh_CN.UTF-8 / Asia/Shanghai
- **非root用户**：devuser (UID 1000)，sudo 默认关闭（`--grant-sudo`/`GRANT_SUDO=yes` 开启）
- **任务管理**：使用 invoke 作为任务管理工具（tasks/ 目录）
- **编排架构**：三层后端自动降级——podman-compose 声明式（优先）→ podman-py SDK → CLI fallback
- **ML 模型管理**：容器内预装 omlmd + olot[oras-py]，支持 OCI artifact 分发和 KServe ModelCar 打包
- **Toolbx 兼容**：镜像满足 Toolbx 自定义镜像规范（LABEL + /run/host + markers + capsh），可直接 toolbox create/enter
- **透传模式**：`compose.dev.yaml` 提供 opt-in 开发透传（SSH agent/git/X11/pip cache）
- **模型仓库**：内置 model-registry 服务（profile: `registry`），本地 OCI registry 用于开发测试
- **零依赖 CLI**：`bin/jpman` 纯bash脚本，无需Python依赖，提供快速容器管理、镜像缓存、WSL2导出等功能
- **镜像缓存**：`.image-cache/` 目录支持 podman save/load 快速备份恢复，pigz 多线程压缩
- **WSL2 集成**：一键导出为 WSL2 发行版，自动配置 wsl.conf 和 Conda 激活，含环境验证脚本
- **增量重建**：`Containerfile.hidden` 支持配置变更快速重建（<10秒）
- **构建系统**：使用 scikit-build-core + CMake 进行 Python 包构建
- **跨平台**：支持 WSL/Linux/macOS（bash）+ Windows（cmd/ps1）
- **父级工作区**：SpecWeave 根目录（`../../../AGENTS.md`）— 全局规则、Skill、角色均以父级为准
- **AI资产容器**：`.agents/` 目录（本项目特有规则，已按单一职责原子化拆分）

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则、Skill、角色、团队）
  └─ apps/containers/jupyter-podman-rootless/AGENTS.md（本文件，项目路由入口）
       ├─ .agents/README.md          ← AI资产容器索引
       │   └─ rules/
       │       ├─ containerfile.md   ← Containerfile 编写规范（7层架构/Toolbx兼容/free-threading）
       │       ├─ entrypoint.md      ← Entrypoint 启动脚本规范（7步启动流程）
       │       ├─ services.md        ← supervisord/SSH/Jupyter/Podman服务配置规范
       │       ├─ compose.md         ← compose编排/profiles/透传配置规范
       │       ├─ invoke-tasks.md    ← invoke任务开发规范（三层后端/client.py）
       │       ├─ ml-models.md       ← ML模型管理规范（OMLMD/OLOT/model-registry）
       │       └─ build-test.md      ← 构建与测试规范
       ├─ bin/                       ← jpman零依赖CLI（跨平台）
       │   ├─ jpman                  ← WSL/Linux/macOS bash版本
       │   ├─ jpman.cmd              ← Windows cmd版本
       │   └─ jpman.ps1              ← Windows PowerShell版本
       ├─ docs/                       ← 人类可读文档（原子化拆分，17个文档+索引）
       │   └─ README.md              ← 文档索引
       ├─ pyproject.toml             ← Python项目配置（invoke依赖声明，含[compose]/[full]/[model] extras，scikit-build-core）
       ├─ CMakeLists.txt             ← scikit-build-core CMake配置
       ├─ tasks/                     ← invoke任务定义目录
       ├─ config/                    ← 配置文件目录
       ├─ scripts/                   ← 辅助脚本
       ├─ conda-lock/                ← conda环境定义（environment.yml，含omlmd+olot）
       ├─ Containerfile              ← Podman构建定义（7层架构，含Toolbx兼容标记）
       ├─ Containerfile.hidden       ← 增量构建补丁（配置变更快速重建）
       ├─ entrypoint.sh              ← 容器启动脚本（7步启动流程）
       ├─ compose.yaml               ← podman-compose 声明式编排（jupyter + model-registry服务）
       ├─ compose.dev.yaml           ← 开发透传覆盖文件（SSH/git/X11/pip cache，opt-in）
       ├─ .env.example               ← 环境变量模板（含REGISTRY_*和DEV透传说明）
       ├─ .containerignore           ← Docker/Podman构建忽略规则
       ├─ .gitignore                 ← Git忽略规则（含.image-cache/.wsl-cache）
       ├─ .image-cache/              ← 镜像缓存目录（git忽略）
       └─ .wsl-cache/                ← WSL发行版缓存目录（git忽略）
```

**嵌套优先原则**：进入本目录后优先读取本文件；详细约束按主题加载 `.agents/rules/` 对应文件；未覆盖的规则回退到 SpecWeave 根 AGENTS.md。

## 上下文路由表

| 任务类型 | 必读入口 | 说明 |
|---------|---------|------|
| Containerfile修改/构建优化 | [.agents/rules/containerfile.md](.agents/rules/containerfile.md) | 7层架构、Toolbx兼容、free-threading、层缓存策略、安全规范 |
| entrypoint.sh启动脚本 | [.agents/rules/entrypoint.md](.agents/rules/entrypoint.md) | 7步启动流程、日志规范、信号处理、Podman初始化、Jupyter配置 |
| supervisord/SSH/Jupyter/Podman服务配置 | [.agents/rules/services.md](.agents/rules/services.md) | 多服务管理、权限配置、存储驱动 |
| compose编排/profiles/透传配置 | [.agents/rules/compose.md](.agents/rules/compose.md) | compose.yaml服务定义、compose.dev.yaml透传、安全设计 |
| invoke任务开发 | [.agents/rules/invoke-tasks.md](.agents/rules/invoke-tasks.md) | 三层后端架构、client.py封装、任务编写规范、路径自动转换 |
| ML模型管理（OMLMD/OLOT） | [.agents/rules/ml-models.md](.agents/rules/ml-models.md) | OCI artifact分发、ModelCar打包、本地model-registry |
| jpman CLI脚本修改 | [bin/jpman](bin/jpman) | 零依赖CLI脚本，bash实现，需保持跨平台兼容 |
| 镜像构建与测试 | [.agents/rules/build-test.md](.agents/rules/build-test.md) | build/run命令、7步验证流程、常见问题排查 |
| AI资产容器索引 | [.agents/README.md](.agents/README.md) | .agents/目录结构、父级继承关系 |
| 人类可读文档索引 | [docs/README.md](docs/README.md) | 使用指南、参考文档、FAQ |
| 全局规则（提交/代码风格/沟通） | [../../../AGENTS.md](../../../AGENTS.md) → [../../../.agents/global-core-rules.md](../../../.agents/global-core-rules.md) | 回退到父级工作区 |
| Skill使用 | [../../../.agents/skills/](../../../.agents/skills/) | 所有SpecWeave全局Skill可用 |
| 复盘/洞察/原子化/原子提交 | [../../../.agents/commands/](../../../.agents/commands/) | 七概念指令集，通过父级调用 |

## 核心规范入口

| 规范 | 入口 | 说明 |
|-----|------|------|
| 父级全局规则 | [../../../AGENTS.md](../../../AGENTS.md) | SpecWeave根工作区入口（启动协议必经之路） |
| 本文件入口 | AGENTS.md（本文件） | jupyter-podman-rootless子项目路由入口 |
| AI资产容器 | [.agents/README.md](.agents/README.md) | .agents/目录索引与父级继承关系 |
| Containerfile规范 | [.agents/rules/containerfile.md](.agents/rules/containerfile.md) | 7层架构/Toolbx兼容/free-threading/层缓存/安全 |
| 入口点脚本规范 | [.agents/rules/entrypoint.md](.agents/rules/entrypoint.md) | 7步启动流程/日志/信号/Podman初始化 |
| 服务配置规范 | [.agents/rules/services.md](.agents/rules/services.md) | supervisord/SSH/Jupyter/Podman配置 |
| Compose编排规范 | [.agents/rules/compose.md](.agents/rules/compose.md) | compose.yaml/dev.yaml/profiles/透传/安全 |
| Invoke任务规范 | [.agents/rules/invoke-tasks.md](.agents/rules/invoke-tasks.md) | 三层后端/client.py/任务编写规范 |
| ML模型规范 | [.agents/rules/ml-models.md](.agents/rules/ml-models.md) | OMLMD/OLOT/ModelCar/model-registry |
| jpman CLI | [bin/jpman](bin/jpman) | 零依赖CLI脚本（跨平台bash/cmd/ps1） |
| 构建测试规范 | [.agents/rules/build-test.md](.agents/rules/build-test.md) | 构建/运行/验证/问题排查 |
| 人类可读文档 | [docs/README.md](docs/README.md) | 使用文档索引（快速开始/参考/FAQ） |

## 项目约束速览

详细约束已按主题拆分到 `.agents/rules/` 下各文件，以下是核心约束索引：

| 约束主题 | 所在文件 |
|---------|---------|
| 中文环境（locale/timezone）、基础镜像锁定 | [containerfile.md](.agents/rules/containerfile.md#基础约定) |
| 7层构建架构、层缓存优化、Toolbx兼容标记 | [containerfile.md](.agents/rules/containerfile.md#7层构建设计) |
| Python 3.14 cp314t free-threading配置 | [containerfile.md](.agents/rules/containerfile.md#基础约定) |
| 非root用户（devuser/UID1000/docker组/sudo） | [containerfile.md](.agents/rules/containerfile.md#基础约定) |
| Rootless Podman配置（fuse-overlayfs/crun/subuid） | [containerfile.md](.agents/rules/containerfile.md#rootless-podman配置) |
| 敏感信息（禁止硬编码密码/密钥） | [containerfile.md](.agents/rules/containerfile.md#安全规范) |
| 镜像优化（--no-install-recommends/缓存清理） | [containerfile.md](.agents/rules/containerfile.md#体积优化) |
| tini init进程、7步启动流程 | [entrypoint.md](.agents/rules/entrypoint.md#基础约定) |
| 启动日志规范、信号处理、Podman初始化 | [entrypoint.md](.agents/rules/entrypoint.md#7步启动流程) |
| SSH配置（PermitRootLogin/主机密钥/公钥注入） | [entrypoint.md](.agents/rules/entrypoint.md#7步启动流程) |
| supervisord服务管理（sshd/jupyter优先级） | [services.md](.agents/rules/services.md#supervisord配置) |
| compose透传安全设计（opt-in/只读挂载） | [compose.md](.agents/rules/compose.md#安全设计原则) |
| 三层后端自动降级（compose→SDK→CLI） | [invoke-tasks.md](.agents/rules/invoke-tasks.md#三层后端架构clientpy) |
| invoke命令兼容性保证（命名空间/参数/输出） | [invoke-tasks.md](.agents/rules/invoke-tasks.md#命令兼容性保证) |
| OMLMD/OLOT cp314t兼容（--ignore-requires-python） | [ml-models.md](.agents/rules/ml-models.md#python兼容性说明) |
| jpman CLI跨平台兼容（bash/cmd/ps1保持功能一致） | [bin/jpman](bin/jpman) |
| Jupyter隐藏文件显示（allow_hidden=True） | [config/jupyter_notebook_config.py](config/jupyter_notebook_config.py) |
| 镜像缓存目录（.image-cache/）和WSL缓存（.wsl-cache/）git忽略 | [.gitignore](.gitignore) |

## 快速开始

```bash
# 方式一：jpman零依赖CLI（推荐快速上手，无需Python依赖）
bash bin/jpman rebuild-all   # 全量构建镜像（清华源加速）
bash bin/jpman start         # 启动容器
bash bin/jpman info          # 查看访问信息

# 方式二：安装依赖（invoke + podman-compose）
pip install -e ".[compose]"

# 构建镜像（清华源加速）
invoke build --apt-mirror tuna --conda-mirror tuna --pip-mirror tuna

# 启动容器（自动生成密码和token）
invoke run

# 查看可用任务（应列出13个：8核心+5model）
invoke --list
```

完整构建、运行、验证命令和常见问题排查见 [.agents/rules/build-test.md](.agents/rules/build-test.md)，用户文档见 [docs/](docs/README.md)。

## 引用父级 SpecWeave 规范

本项目完全遵循 SpecWeave 工作区发现协议：
- AGENTS.md 包含「启动协议」关键词
- 正确引用父级 `../../../AGENTS.md`
- 遵循嵌套优先原则，未覆盖的规则回退到父级工作区
- 支持工作区发现协议的五步发现流程
- AI资产已原子化拆分至 `.agents/` 目录，遵循单一职责原则
- 人类可读文档已原子化拆分至 `docs/` 目录

## 变更日志

完整变更历史见 [.agents/CHANGELOG.md](.agents/CHANGELOG.md)。

- **2026-08-27** | feat: jpman零依赖CLI（跨平台bash/cmd/ps1）、镜像缓存、WSL2一键导出、增量重建
- **2026-08-27** | refactor: 文档原子化拆分（AGENTS.md→.agents/rules/，README.md→docs/）
- **2026-08-27** | feat: R1-R5（三层后端架构+OMLMD+OLOT+Toolbx透传）
- **2026-08-26** | feat: 初始版本发布（7层Containerfile+7步Entrypoint+invoke+healthcheck）
