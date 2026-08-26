# jupyter-podman-rootless - AI协作者入口 (AGENTS Manifest)

> **启动协议（PRIORITY ZERO — 所有智能体必须遵循）**
>
> ```
> 步骤 1：读取本文件全文
> 步骤 2：确认父级工作区 — 本项目是 SpecWeave apps/ 下的子应用，全局规则继承自 SpecWeave 根 AGENTS.md
> 步骤 3：按上下文路由表加载本项目特有规范
> 步骤 3.5：自检 — 确认已理解父级规则与本项目特有约束
> 步骤 4：在规范指导下执行任务
> ```
>
> 本文件是 jupyter-podman-rootless 子项目的 AI 协作者入口。本项目是一个基于 Podman rootless 模式的
> Jupyter 开发容器构建项目，所有全局规则（沟通语言、提交规范、上下文节省等）继承自 SpecWeave 根工作区，
> 本文件仅定义本项目特有的上下文路由与约束入口。

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
- **父级工作区**：SpecWeave 根目录（`../../../AGENTS.md`）— 全局规则、Skill、角色均以父级为准

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则、Skill、角色、团队）
  └─ apps/containers/jupyter-podman-rootless/AGENTS.md（本文件，项目路由入口）
       ├─ pyproject.toml      ← Python项目配置（invoke依赖声明，含[compose]/[full]/[model] extras）
       ├─ tasks/              ← invoke任务定义目录
       │   ├── __init__.py    ← 任务入口与命名空间（核心命令+model.*命令）
       │   ├── utils.py       ← 工具函数（运行时检测/路径转换/随机字符串）
       │   ├── client.py      ← Podman/Docker client wrapper（三层后端优先级检测）
       │   ├── compose_backend.py ← podman-compose 后端封装
       │   ├── build.py       ← 镜像构建任务
       │   ├── manage.py      ← 容器生命周期管理（run/stop/status/clean）
       │   ├── interact.py    ← 容器交互（shell/logs/exec）
       │   ├── model.py       ← ML模型管理（push/pull/config/pack/extract via OMLMD/OLOT）
       │   └── container.py   ← 向后兼容聚合模块
       ├─ config/             ← 配置文件目录
       │   ├─ supervisord.conf ← supervisord 主配置
       │   ├─ sshd_config      ← SSH 服务配置
       │   ├─ jupyter_notebook_config.py ← Jupyter 基础配置
       │   ├─ supervisor/      ← supervisord 配置
       │   │   └─ conf.d/      ← sshd/jupyter服务配置文件
       │   └─ containers/      ← Podman容器存储配置（fuse-overlayfs）
       ├─ scripts/             ← 辅助脚本
       │   ├── healthcheck.sh  ← 健康检查脚本（sshd+jupyter+podman）
       │   ├── olot_car.py     ← 容器内OLOT ModelCar辅助脚本
       │   └── lib/            ← 脚本共享库（彩色日志等）
       ├─ conda-lock/          ← conda环境定义（environment.yml，含omlmd+olot）
       ├─ Containerfile        ← Podman构建定义（7层架构，含Toolbx兼容标记）
       ├─ entrypoint.sh        ← 容器启动脚本（7步启动流程）
       ├─ compose.yaml         ← podman-compose 声明式编排（jupyter + model-registry服务）
       ├─ compose.dev.yaml     ← 开发透传覆盖文件（SSH/git/X11/pip cache，opt-in）
       ├─ .env.example         ← 环境变量模板（含REGISTRY_*和DEV透传说明）
       ├─ .containerignore     ← Docker/Podman构建忽略规则
       └─ README.md            ← 使用文档（含ML模型管理、Toolbx透传、三层后端章节）
```

**嵌套优先原则**：进入本目录后优先读取本文件；未覆盖的规则回退到 SpecWeave 根 AGENTS.md。

## 上下文路由表

| 任务类型 | 必读入口 | 说明 |
|---------|---------|------|
| invoke任务开发 | tasks/ 目录 | 使用invoke进行构建、测试、部署等任务管理 |
| Containerfile/Dockerfile编写 | 参考../../docker-images/jupyter-ssh-base/ | 多阶段构建规范适配Podman，注意Toolbx LABEL/markers |
| supervisord/SSH/Jupyter服务配置 | config/supervisor/conf.d/ | 多服务管理配置 |
| Podman rootless配置 | config/containers/ | rootless模式下的Podman配置 |
| ML模型管理（OMLMD/OLOT） | tasks/model.py + scripts/olot_car.py | OCI artifact分发、ModelCar打包逻辑 |
| compose编排/profiles | compose.yaml + compose.dev.yaml | 服务定义、registry profile、透传配置 |
| 三层后端逻辑 | tasks/client.py + tasks/compose_backend.py | 后端自动降级机制 |
| 全局规则（提交/代码风格/沟通） | [../../../AGENTS.md](../../../AGENTS.md) → [.agents/global-core-rules.md](../../../.agents/global-core-rules.md) | 回退到父级工作区 |
| Skill使用 | [.agents/skills/](../../../.agents/skills/) | 所有SpecWeave全局Skill可用 |

## 核心约束速查

| 约束主题 | 说明 |
|---------|------|
| 运行时 | 优先使用 Podman，同时兼容 Docker；.containerignore 双兼容 |
| 用户模式 | Rootless 模式运行，禁止容器内使用 root 用户作为默认用户 |
| 非root用户 | devuser (UID 1000)，sudo 默认关闭（GRANT_SUDO=yes/--grant-sudo 开启） |
| Python版本 | Python 3.14t (cp314t, free-threading, 无GIL) |
| Python发行版 | Miniforge3 (conda-forge)，main环境；omlmd/olot通过--ignore-requires-python兼容cp314t |
| 任务管理 | 使用 invoke，任务定义在 tasks/ 目录；13个命令（8核心+5model） |
| 三层后端 | podman-compose（优先）→ podman-py SDK → CLI fallback；自动检测对用户透明 |
| 可选依赖 | podman-compose/podman-py/omlmd/olot均为可选，未安装时自动降级不影响核心功能 |
| 服务管理 | supervisord管理sshd(22)、jupyter(8888)；Podman按需rootless运行 |
| 中文环境 | locale: zh_CN.UTF-8, timezone: Asia/Shanghai |
| 工作目录 | /workspace |
| 透传设计 | 默认隔离优先，所有透传（SSH/GUI/GPU/hostnet）均为opt-in；compose.yaml注释文档+compose.dev.yaml开箱覆盖 |
| Toolbx兼容 | 镜像内置com.github.containers.toolbox=true LABEL、/run/host、/.toolboxenv、capsh |
| 模型仓库 | model-registry服务通过profile: registry启用，默认不启动 |
| invoke命令兼容 | 所有invoke命令名/参数/输出格式对用户透明，新增功能通过新命令/新参数添加 |
| 敏感信息 | 禁止硬编码密码/密钥，通过环境变量注入 |

## 快速开始

```bash
# 安装依赖（invoke）
pip install -e .

# 查看可用任务（应列出13个：8核心+5model）
invoke --list

# 构建镜像
invoke build

# 运行容器（后台启动，端口2222:22, 8888:8888，挂载./workspace）
invoke run

# 开发透传模式（podman-compose直接使用）
podman-compose -f compose.yaml -f compose.dev.yaml up -d

# 启动本地模型仓库+开发透传
podman-compose -f compose.yaml -f compose.dev.yaml --profile registry up -d

# 查看容器状态
invoke status

# 查看日志
invoke logs

# 进入容器shell（devuser）
invoke shell

# ML模型操作示例
invoke model.push ./model --ref localhost:5000/models/bert:v1
invoke model.pack ./model --base jupyter-podman-rootless:latest --ref localhost:5000/models/car:v1

# 在容器中执行命令
invoke exec --command "python --version"

# 停止容器
invoke stop

# 清理（删除容器和镜像）
invoke clean --image
```

## 环境变量

### 运行时环境变量

| 变量 | 默认值 | 说明 |
|------|-------|------|
| USER_PASSWORD | 随机生成 | devuser用户密码 |
| JUPYTER_TOKEN | 随机生成 | Jupyter访问token |
| JUPYTER_PASSWORD | 无 | Jupyter密码（与token二选一） |
| SSH_PUBLIC_KEY | 无 | SSH公钥（注入authorized_keys） |
| GRANT_SUDO | no | 是否授予devuser无密码sudo权限 |
| ALLOW_ROOT_SSH | no | 是否允许root SSH登录 |
| APT_MIRROR | official | APT镜像源（official/tuna/aliyun） |
| CONDA_MIRROR | official | Conda镜像源（official/tuna/aliyun） |
| PIP_MIRROR | official | PIP镜像源（official/tuna/aliyun） |
| DEBUG | 0 | 设为1启用entrypoint调试输出 |
| REGISTRY_URL | localhost:5000 | ML模型OCI registry地址 |
| REGISTRY_PORT | 5000 | 本地model-registry服务端口 |
| REGISTRY_PLAIN_HTTP | true | 本地registry使用HTTP |

## Invoke 命令清单

| 命名空间 | 命令 | 功能 |
|---------|------|------|
| (root) | build, run, stop, status, shell, logs, exec, clean | 核心8命令 |
| container.* | build, run, stop, status, shell, logs, exec, clean | 核心命令别名（命名空间隔离） |
| model.* | push, pull, config, pack, extract | ML模型管理5命令（OMLMD/OLOT） |

## 引用父级 SpecWeave 规范

本项目完全遵循 SpecWeave 工作区发现协议：
- AGENTS.md 包含「启动协议」关键词
- 正确引用父级 `../../../AGENTS.md`
- 遵循嵌套优先原则，未覆盖的规则回退到父级工作区
- 支持工作区发现协议的五步发现流程

## 变更日志

- 2026-08-27 | feat | R5/Toolbx集成：Toolbx兼容标记(LABEL+/run/host+markers+capsh)、compose.dev.yaml透传覆盖文件、注释式透传文档
- 2026-08-27 | feat | R4/OLOT集成：KServe ModelCar标准镜像打包(model.pack/extract)、olot_car.py辅助脚本
- 2026-08-27 | feat | R3/OMLMD集成：ML模型OCI artifact分发(model.push/pull/config)、model-registry compose service(profile:registry)
- 2026-08-27 | feat | R2/podman-compose集成：声明式compose.yaml编排、.env配置管理、compose_backend.py
- 2026-08-27 | feat | R1/podman-py SDK集成：三层exec后端架构、client.py封装
- 2026-08-26 | feat | 完整实现：Containerfile(7层)、entrypoint.sh(7步)、config/配置、invoke任务、healthcheck
- 2026-08-26 | feat | 初始化项目结构：AGENTS.md、目录结构、pyproject.toml、.containerignore、README.md
