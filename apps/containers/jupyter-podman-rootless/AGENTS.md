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
- **核心功能**：OpenSSH Server + Jupyter Notebook + Podman (rootless)，通过 supervisord 管理多服务
- **Python 环境**：Python 3.14t (free-threading) + Miniforge3
- **中文环境**：zh_CN.UTF-8 / Asia/Shanghai
- **非root用户**：devuser (UID 1000)
- **任务管理**：使用 invoke 作为任务管理工具（tasks/ 目录）
- **父级工作区**：SpecWeave 根目录（`../../../AGENTS.md`）— 全局规则、Skill、角色均以父级为准

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则、Skill、角色、团队）
  └─ apps/containers/jupyter-podman-rootless/AGENTS.md（本文件，项目路由入口）
       ├─ pyproject.toml      ← Python项目配置（invoke依赖声明）
       ├─ tasks/              ← invoke任务定义目录
       ├─ config/             ← 配置文件目录
       │   ├─ supervisord.conf ← supervisord 主配置
       │   ├─ sshd_config      ← SSH 服务配置
       │   ├─ jupyter_notebook_config.py ← Jupyter 基础配置
       │   ├─ supervisor/      ← supervisord 配置
       │   │   └─ conf.d/      ← sshd/jupyter服务配置文件
       │   └─ containers/      ← Podman容器存储配置（fuse-overlayfs）
       ├─ scripts/             ← 辅助脚本（healthcheck等）
       │   └─ lib/             ← 脚本共享库（彩色日志等）
       ├─ conda-lock/          ← conda环境定义（environment.yml）
       ├─ Containerfile        ← Podman构建定义（7层架构）
       ├─ entrypoint.sh        ← 容器启动脚本（7步启动流程）
       ├─ .containerignore     ← Docker/Podman构建忽略规则
       └─ README.md            ← 使用文档
```

**嵌套优先原则**：进入本目录后优先读取本文件；未覆盖的规则回退到 SpecWeave 根 AGENTS.md。

## 上下文路由表

| 任务类型 | 必读入口 | 说明 |
|---------|---------|------|
| invoke任务开发 | tasks/ 目录 | 使用invoke进行构建、测试、部署等任务管理 |
| Containerfile/Dockerfile编写 | 参考../../docker-images/jupyter-ssh-base/ | 多阶段构建规范适配Podman |
| supervisord/SSH/Jupyter服务配置 | config/supervisor/conf.d/ | 多服务管理配置 |
| Podman rootless配置 | config/containers/ | rootless模式下的Podman配置 |
| 全局规则（提交/代码风格/沟通） | [../../../AGENTS.md](../../../AGENTS.md) → [.agents/global-core-rules.md](../../../.agents/global-core-rules.md) | 回退到父级工作区 |
| Skill使用 | [.agents/skills/](../../../.agents/skills/) | 所有SpecWeave全局Skill可用 |

## 核心约束速查

| 约束主题 | 说明 |
|---------|------|
| 运行时 | 优先使用 Podman，同时兼容 Docker；.containerignore 双兼容 |
| 用户模式 | Rootless 模式运行，禁止容器内使用 root 用户作为默认用户 |
| 非root用户 | devuser (UID 1000)，默认无sudo权限（GRANT_SUDO=yes时启用） |
| Python版本 | Python 3.14t (cp314t, free-threading, 无GIL) |
| Python发行版 | Miniforge3 (conda-forge)，main环境 |
| 任务管理 | 使用 invoke，任务定义在 tasks/ 目录（替代docker-compose） |
| 服务管理 | supervisord管理sshd(22)、jupyter(8888)；Podman按需rootless运行 |
| 中文环境 | locale: zh_CN.UTF-8, timezone: Asia/Shanghai |
| 工作目录 | /workspace |
| 敏感信息 | 禁止硬编码密码/密钥，通过环境变量注入 |

## 快速开始

```bash
# 安装依赖（invoke）
pip install -e .

# 查看可用任务
invoke --list

# 构建镜像
invoke build

# 运行容器（后台启动，端口2222:22, 8888:8888，挂载./workspace）
invoke run

# 查看容器状态
invoke status

# 查看日志
invoke logs

# 进入容器shell（devuser）
invoke shell

# 在容器中执行命令
invoke exec --command "python --version"

# 停止容器
invoke stop

# 清理（删除容器和镜像）
invoke clean --image
```

## 环境变量

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

## 引用父级 SpecWeave 规范

本项目完全遵循 SpecWeave 工作区发现协议：
- AGENTS.md 包含「启动协议」关键词
- 正确引用父级 `../../../AGENTS.md`
- 遵循嵌套优先原则，未覆盖的规则回退到父级工作区
- 支持工作区发现协议的五步发现流程

## 变更日志

- 2026-08-26 | feat | 完整实现：Containerfile(7层)、entrypoint.sh(7步)、config/配置、invoke任务、healthcheck
- 2026-08-26 | feat | 初始化项目结构：AGENTS.md、目录结构、pyproject.toml、.containerignore、README.md
