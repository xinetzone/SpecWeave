# devcontainer-win11 - AI协作者入口 (AGENTS Manifest)

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
> 本文件是 devcontainer-win11 子项目的 AI 协作者入口。本项目是一个 Windows 容器全功能开发容器基础镜像构建项目，
> 集成 SSH + Jupyter + Miniforge3(Python 3.14 free-threading cp314t) + Docker CLI(DooD)，通过 PowerShell entrypoint 管理多服务启动，
> 所有全局规则（沟通语言、提交规范、上下文节省等）继承自 SpecWeave 根工作区，本文件仅定义
> 本项目特有的上下文路由与约束。项目详细规范已原子化到 [.agents/](.agents/README.md) 目录。

## 项目概述

- **项目类型**：Windows Docker 容器镜像构建项目（Windows Server 2022 + SSH + Docker DooD + Jupyter，PowerShell管理）
- **基础镜像**：mcr.microsoft.com/windows/servercore:ltsc2022
- **核心功能**：OpenSSH Server + Docker CLI(DooD, host named pipe) + JupyterLab，PowerShell entrypoint 统一管理
- **中文环境**：zh-CN 语言包 / China Standard Time 时区 (UTC+8)
- **非root用户**：devuser（本地用户，非Administrators组）
- **服务端口**：sshd(22) + jupyter(8888)
- **Python环境**：C:\conda（Miniforge3 + Python 3.14.6 cp314t free-threading，通过 conda-forge `python-freethreading` 元包安装）
- **父级工作区**：SpecWeave 根目录（[../../AGENTS.md](../../AGENTS.md)）— 全局规则、Skill、角色均以父级为准
- **构建环境要求**：Windows 宿主 + Docker Desktop 切换到 Windows 容器模式
- **AI资产容器**：[.agents/](.agents/README.md) 目录（本项目特有规则/脚本/工作流）

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则、Skill、角色、团队）
  └─ apps/AGENTS.md（应用区入口路由）
       └─ docker-images/（容器镜像类分组）
            └─ devcontainer-win11/AGENTS.md（本文件，项目路由入口）
                 ├─ .agents/         ← 本项目AI资产容器（详细规范）
                 │   ├─ README.md   ← .agents 目录索引
                 │   └─ rules/      ← 项目特有规则（dockerfile/entrypoint/services/build-test）
                 ├─ Dockerfile      ← 多阶段构建定义（7 Stage单镜像）
                 ├─ entrypoint.ps1  ← 容器启动脚本（PowerShell）
                 ├─ config/         ← 服务配置文件
                 ├─ scripts/        ← 辅助脚本（构建/启动/健康检查）
                 └─ examples/       ← 示例代码（free-threading演示）
```

**嵌套优先原则**：进入本目录后优先读取本文件；项目详细规范在 [.agents/rules/](.agents/README.md) 下；
本文件和 `.agents/` 未覆盖的规则回退到 SpecWeave 根 AGENTS.md。

## 上下文路由表（任务类型→必读规范）

| 任务类型 | 必读入口 | 说明 |
|---------|---------|------|
| 定位文件/了解项目结构 | [.agents/README.md](.agents/README.md) | .agents 目录索引 |
| Dockerfile修改/构建优化 | [.agents/rules/dockerfile.md](.agents/rules/dockerfile.md) | 7 Stage架构、escape字符、PowerShell SHELL、缓存策略、同层修改、中文环境、非管理员用户、free-threading配置 |
| entrypoint.ps1启动脚本 | [.agents/rules/entrypoint.md](.agents/rules/entrypoint.md) | 启动流程、日志规范、服务启动、密码动态设置、命令模式 |
| 服务配置（sshd/jupyter/docker dood） | [.agents/rules/services.md](.agents/rules/services.md) | sshd/jupyter服务配置、DooD命名管道、健康检查、端口映射 |
| Python free-threading配置 | [.agents/rules/dockerfile.md#python-free-threading-配置](.agents/rules/dockerfile.md#python-free-threading-配置) | cp314t安装、Py_GIL_DISABLED环境变量、C编译工具链、源码编译支持 |
| SSH配置 | [.agents/rules/services.md#ssh-服务sshd](.agents/rules/services.md#ssh-服务sshd) | OpenSSH Server安装、密码+密钥认证、host keys启动时生成 |
| Jupyter配置 | [.agents/rules/services.md#jupyter-服务](.agents/rules/services.md#jupyter-服务) | conda环境路径、token配置、工作目录C:\workspace、CORS策略 |
| Docker DooD配置 | [.agents/rules/services.md#docker-dood-服务](.agents/rules/services.md#docker-dood-服务) | CLI静态二进制、命名管道npipe:////./pipe/docker_engine、DooD模式 |
| 镜像构建/启动/测试 | [.agents/rules/build-test.md](.agents/rules/build-test.md) | build.ps1/build.sh/start.ps1命令、健康检查、验证流程、问题排查 |
| 健康检查脚本 | [.agents/rules/services.md#健康检查](.agents/rules/services.md#健康检查) | healthcheck.ps1条件检查逻辑、端口检测方式 |
| 全局规则（提交/代码风格/沟通） | [../../AGENTS.md](../../AGENTS.md) → [../../.agents/global-core-rules.md](../../../.agents/global-core-rules.md) | 回退到父级工作区 |
| Skill使用 | [../../.agents/skills/](../../../.agents/skills/) | 所有SpecWeave全局Skill可用 |
| 复盘/洞察/原子化/原子提交 | [../../.agents/commands/](../../../.agents/commands/) | 七概念指令集，通过父级调用 |

## 快速开始

```powershell
# 一键构建基础镜像（PowerShell）
.\scripts\build.ps1

# 使用国内镜像源
.\scripts\build.ps1 -Cn

# 一键启动（含健康验证+SSH/Jupyter连接信息）
.\scripts\start.ps1

# 从WSL/Git Bash构建
bash scripts/build.sh
```

完整构建、运行、验证命令和常见问题排查见 [.agents/rules/build-test.md](.agents/rules/build-test.md)。

## 引用父级 SpecWeave 规范

本项目完全遵循 SpecWeave 工作区发现协议：
- AGENTS.md 包含「启动协议」关键词
- 正确引用父级 `../../AGENTS.md`
- 遵循嵌套优先原则，未覆盖的规则回退到父级工作区
- 项目详细规范原子化到 `.agents/` 目录，遵循单一职责原则
