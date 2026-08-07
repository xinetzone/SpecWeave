# jupyter-ssh-base - AI协作者入口 (AGENTS Manifest)

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
> 本文件是 jupyter-ssh-base 子项目的 AI 协作者入口。本项目是一个 SSH + Jupyter Notebook 基础镜像构建项目，
> 所有全局规则（沟通语言、提交规范、上下文节省等）继承自 SpecWeave 根工作区，本文件仅定义
> 本项目特有的上下文路由与约束入口。详细规则已原子化拆分至 `.agents/rules/` 目录。

## 项目概述

- **项目类型**：Docker 镜像构建项目（SSH + Jupyter Notebook 基础镜像）
- **基础镜像**：ubuntu:26.04
- **核心功能**：OpenSSH Server + Jupyter Notebook，通过 supervisord 管理双服务
- **中文环境**：zh_CN.UTF-8 / Asia/Shanghai
- **非root用户**：jupyteruser (UID 1000)
- **父级工作区**：SpecWeave 根目录（`../../AGENTS.md`）— 全局规则、Skill、角色均以父级为准
- **AI资产容器**：`.agents/` 目录（本项目特有规则/脚本/模板）

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则、Skill、角色、团队）
  └─ apps/jupyter-ssh-base/AGENTS.md（本文件，项目路由入口）
       ├─ .agents/README.md           ← AI资产容器索引
       │   └─ rules/
       │       ├─ dockerfile.md       ← Dockerfile 多阶段构建规范
       │       ├─ entrypoint.md       ← 启动脚本规范
       │       ├─ services.md         ← 服务管理规范（supervisord+SSH+Jupyter）
       │       └─ build-test.md       ← 构建与测试流程
       ├─ Dockerfile           ← 多阶段构建定义（builder + runtime）
       ├─ entrypoint.sh        ← 容器启动脚本
       ├─ requirements.txt     ← Python 依赖包列表
       ├─ config/              ← 配置文件目录
       │   ├─ supervisord.conf ← supervisord 主配置
       │   ├─ sshd_config      ← SSH 服务配置
       │   ├─ jupyter_notebook_config.py ← Jupyter 基础配置
       │   └─ supervisor/      ← supervisord 配置
       │       └─ conf.d/      ← 服务配置文件
       ├─ scripts/             ← 辅助脚本
       │   ├─ build.sh         ← 一键构建脚本
       │   └─ healthcheck.sh   ← 健康检查脚本
       ├─ docker-compose.yml   ← Compose 编排示例
       ├─ README.md            ← 使用文档
       └─ .dockerignore        ← Docker构建忽略规则
```

**嵌套优先原则**：进入本目录后优先读取本文件；详细约束按主题加载 `.agents/rules/` 对应文件；未覆盖的规则回退到 SpecWeave 根 AGENTS.md。

## 上下文路由表

| 任务类型 | 必读入口 | 说明 |
|---------|---------|------|
| Dockerfile修改/构建优化 | [.agents/rules/dockerfile.md](.agents/rules/dockerfile.md) | BuildKit语法、多阶段构建、层缓存策略、安全规范、非root用户、可复用性 |
| supervisord/SSH/Jupyter服务配置 | [.agents/rules/services.md](.agents/rules/services.md) | 双服务管理配置、SSH安全设置、Jupyter认证、健康检查 |
| entrypoint.sh启动脚本 | [.agents/rules/entrypoint.md](.agents/rules/entrypoint.md) | 启动脚本规范、日志输出、信号处理、密码初始化、命令模式 |
| 镜像构建与测试 | [.agents/rules/build-test.md](.agents/rules/build-test.md) | docker build/run/test命令、验证流程、依赖管理、.dockerignore |
| AI资产容器索引 | [.agents/README.md](.agents/README.md) | .agents/目录结构、父级继承关系 |
| 全局规则（提交/代码风格/沟通） | [../../AGENTS.md](../../AGENTS.md) → [../../.agents/global-core-rules.md](../../.agents/global-core-rules.md) | 回退到父级工作区 |
| Skill使用 | [../../.agents/skills/](../../.agents/skills/) | 所有SpecWeave全局Skill可用 |
| 复盘/洞察/原子化/原子提交 | [../../.agents/commands/](../../.agents/commands/) | 七概念指令集，通过父级调用 |
| Dockerfile自动化测试 | [../../.agents/scripts/test-dockerfiles.ps1](../../.agents/scripts/test-dockerfiles.ps1) | 项目根目录测试脚本 |

## 核心规范入口

| 规范 | 入口 | 说明 |
|-----|------|------|
| 父级全局规则 | [../../AGENTS.md](../../AGENTS.md) | SpecWeave根工作区入口（启动协议必经之路） |
| 本文件入口 | AGENTS.md（本文件） | jupyter-ssh-base子项目路由入口 |
| AI资产容器 | [.agents/README.md](.agents/README.md) | .agents/目录索引与父级继承关系 |
| Docker构建规范 | [.agents/rules/dockerfile.md](.agents/rules/dockerfile.md) | BuildKit/多阶段/缓存/安全/非root/可复用性 |
| 入口点脚本规范 | [.agents/rules/entrypoint.md](.agents/rules/entrypoint.md) | 启动脚本日志/信号处理/密码/命令模式 |
| 服务管理规范 | [.agents/rules/services.md](.agents/rules/services.md) | supervisord/SSH/Jupyter/健康检查 |
| 构建测试规范 | [.agents/rules/build-test.md](.agents/rules/build-test.md) | 快速开始/验证清单/依赖管理 |
| Docker构建文件 | Dockerfile | 多阶段构建：builder(编译依赖) → runtime(最小运行时) |
| 入口点脚本 | entrypoint.sh | 容器启动逻辑，密码/密钥初始化、Jupyter动态配置、supervisord启动 |
| supervisord配置 | config/supervisor/conf.d/ | SSH和Jupyter双进程管理配置 |
| SSH配置 | config/sshd_config | ED25519优先、禁用root登录、密码+密钥认证 |
| Jupyter配置 | config/jupyter_notebook_config.py | 基础配置（0.0.0.0绑定、/workspace目录） |
| Python依赖 | requirements.txt | Jupyter及相关包，版本固定 |
| 辅助脚本 | scripts/ | build.sh（构建）、healthcheck.sh（健康检查） |
| Docker忽略规则 | .dockerignore | 排除.git/.trae/.agents/workspace/notebooks等非构建文件 |

## 引用父级 SpecWeave 规范

本项目完全遵循 SpecWeave 工作区发现协议：
- AGENTS.md 包含「启动协议」关键词
- 正确引用父级 `../../AGENTS.md`
- 遵循嵌套优先原则，未覆盖的规则回退到父级工作区
- 支持工作区发现协议的五步发现流程
- AI资产已原子化拆分至 `.agents/` 目录，遵循单一职责原则

## 变更日志

- 2026-08-07 | refactor | 原子化拆分AGENTS.md：详细约束迁移至.agents/rules/（4个主题文件），AGENTS.md精简为路由入口
- 2026-08-07 | feat | 为Dockerfile关键构建节点添加76条结构化日志（[INFO]/[OK]/版本验证）；新增自动化测试脚本test-dockerfiles.ps1
- 2026-08-07 | fix | 全面升级Dockerfile以完整兼容Docker BuildKit特性（syntax声明+缓存挂载+SHELL修复）
- 2026-07-24 | feat | 七概念方法论全流程落地：R事实采集→I第一性原理本质分析→E对抗评审→C洞察提炼→A修复闭环→F原子拆分→V验证；多阶段构建优化（builder/runtime分离）；健康检查增强（sshd+jupyter双服务检测）；安全增强（CORS同源默认、运行时配置注入、host key每次重建）；WORKDIR标准化为/workspace；AGENTS.md同步更新
- 2026-07-24 | feat | 初始化项目结构：AGENTS.md、目录结构config/supervisor/conf.d、.dockerignore、requirements.txt
