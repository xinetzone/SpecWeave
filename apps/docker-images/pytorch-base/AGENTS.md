# pytorch-base - AI协作者入口 (AGENTS Manifest)

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
> 本文件是 pytorch-base 子项目的 AI 协作者入口。本项目是一个 PyTorch Docker 基础镜像构建项目，
> 基于 Miniconda3 + Python 3.14 + PyTorch，支持CPU/GPU双模式和离线构建，
> 所有全局规则（沟通语言、提交规范、上下文节省等）继承自 SpecWeave 根工作区，本文件仅定义
> 本项目特有的上下文路由与约束入口。详细规则已原子化拆分至 `.agents/rules/` 目录。

## 项目概述

- **项目类型**：Docker 镜像构建项目（PyTorch 基础开发环境）
- **基础镜像**：ubuntu:26.04
- **核心组件**：Miniconda3 + Python 3.14 + PyTorch
- **构建模式**：在线/离线双模式，CPU/GPU双版本
- **离线包支持**：`offline/` 目录统一存放离线资源
- **中文环境**：zh_CN.UTF-8 / Asia/Shanghai
- **非root用户**：ai (UID 1000)，NOPASSWD sudo
- **父级工作区**：SpecWeave 根目录（`../../AGENTS.md`）— 全局规则、Skill、角色均以父级为准
- **AI资产容器**：`.agents/` 目录（本项目特有规则/脚本/模板）

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则、Skill、角色、团队）
  └─ apps/docker-images/pytorch-base/AGENTS.md（本文件，项目路由入口）
       ├─ .agents/README.md       ← AI资产容器索引
       │   └─ rules/
       │       ├─ dockerfile.md   ← Dockerfile 7阶段构建规范
       │       ├─ entrypoint.md   ← 启动脚本规范
       │       └─ build-test.md   ← 构建与测试流程
       ├─ Dockerfile          ← 7阶段构建定义
       ├─ build.sh / build.ps1 ← 一键构建脚本（在线/离线/GPU/验证）
       ├─ entrypoint.sh       ← 容器入口点（conda激活+用户切换+横幅）
       ├─ environment.yml     ← Conda环境参考
       ├─ lib/logging.sh      ← 脚本共享库
       └─ offline/            ← 离线资源目录
            ├── miniconda/    ← Miniconda安装脚本
            ├── wheels/       ← pip wheel包
            └── conda-pkgs/   ← conda包缓存
```

**嵌套优先原则**：进入本目录后优先读取本文件；详细约束按主题加载 `.agents/rules/` 对应文件；未覆盖的规则回退到 SpecWeave 根 AGENTS.md。

## 上下文路由表

| 任务类型 | 必读入口 | 说明 |
|---------|---------|------|
| Dockerfile修改/构建优化 | [.agents/rules/dockerfile.md](.agents/rules/dockerfile.md) | BuildKit语法、7阶段构建、层缓存、conda环境、离线支持、网络容错、GPU支持 |
| entrypoint.sh启动脚本 | [.agents/rules/entrypoint.md](.agents/rules/entrypoint.md) | conda激活、gosu用户切换、横幅显示、错误处理、调试模式 |
| 构建脚本修改 | [.agents/rules/build-test.md](.agents/rules/build-test.md) | build.sh参数、离线准备/构建、GPU模式、13项验证、问题排查 |
| 离线包管理 | [.agents/rules/dockerfile.md#离线资源支持](.agents/rules/dockerfile.md#离线资源支持) | offline/目录结构、条件离线安装逻辑 |
| 镜像构建与测试 | [.agents/rules/build-test.md](.agents/rules/build-test.md) | 构建命令速查、运行验证、常见问题 |
| AI资产容器索引 | [.agents/README.md](.agents/README.md) | .agents/目录结构、父级继承关系 |
| 全局规则（提交/代码风格/沟通） | [../../AGENTS.md](../../AGENTS.md) → [../../.agents/global-core-rules.md](../../.agents/global-core-rules.md) | 回退到父级工作区 |
| Skill使用 | [../../.agents/skills/](../../.agents/skills/) | 所有SpecWeave全局Skill可用 |
| 复盘/洞察/原子化/原子提交 | [../../.agents/commands/](../../.agents/commands/) | 七概念指令集，通过父级调用 |
| Dockerfile自动化测试 | [../../.agents/scripts/test-dockerfiles.ps1](../../.agents/scripts/test-dockerfiles.ps1) | 项目根目录测试脚本 |

## 核心规范入口

| 规范 | 入口 | 说明 |
|-----|------|------|
| 父级全局规则 | [../../AGENTS.md](../../AGENTS.md) | SpecWeave根工作区入口（启动协议必经之路） |
| 本文件入口 | AGENTS.md（本文件） | pytorch-base子项目路由入口 |
| AI资产容器 | [.agents/README.md](.agents/README.md) | .agents/目录索引与父级继承关系 |
| Docker构建规范 | [.agents/rules/dockerfile.md](.agents/rules/dockerfile.md) | BuildKit/7阶段/conda/离线资源/网络容错/非root用户 |
| 入口点脚本规范 | [.agents/rules/entrypoint.md](.agents/rules/entrypoint.md) | conda激活/gosu/横幅/错误处理 |
| 构建测试规范 | [.agents/rules/build-test.md](.agents/rules/build-test.md) | build.sh参数/离线/GPU/13项验证/排查 |
| Docker构建文件 | Dockerfile | 7阶段构建：系统包→Miniconda→镜像源→PyTorch→用户→entrypoint→验证 |
| 构建脚本 | build.sh / build.ps1 | 一键构建，支持--gpu/--offline/--prepare-offline/--no-cache/--no-verify |
| 入口点脚本 | entrypoint.sh | 容器启动逻辑，conda环境激活、gosu用户切换、交互式横幅 |
| Conda环境参考 | environment.yml | conda环境定义参考 |
| 离线资源目录 | offline/ | 统一存放miniconda安装包、wheels、conda缓存 |
| Docker忽略规则 | .dockerignore | 排除.git/.trae/.agents等非构建文件（offline/必须保留） |

## 项目约束速览

详细约束已按主题拆分到 `.agents/rules/` 下各文件，以下是核心约束索引：

| 约束主题 | 所在文件 |
|---------|---------|
| 中文环境（locale/timezone）、基础镜像锁定 | [dockerfile.md](.agents/rules/dockerfile.md#基础约定) |
| BuildKit语法、7阶段构建结构 | [dockerfile.md](.agents/rules/dockerfile.md#7阶段结构runtime-logical-layering-v13) |
| BuildKit缓存（apt/conda/pip） | [dockerfile.md](.agents/rules/dockerfile.md#层缓存优化) |
| Conda环境（pytorch环境名、/opt/conda路径、自动激活） | [dockerfile.md](.agents/rules/dockerfile.md#conda环境规范) |
| 离线资源（offline/目录、条件安装、--prepare-offline） | [dockerfile.md](.agents/rules/dockerfile.md#离线资源支持) |
| 网络容错（apt/wget重试、conda fallback pip） | [dockerfile.md](.agents/rules/dockerfile.md#网络容错) |
| 非root用户（ai/UID1000/sudo） | [dockerfile.md](.agents/rules/dockerfile.md#非-root-用户规范) |
| Python版本（默认3.14，ARG可调） | [dockerfile.md](.agents/rules/dockerfile.md#构建参数) |
| GPU支持（USE_GPU=1、CUDA 12.6、nvidia-docker2） | [dockerfile.md](.agents/rules/dockerfile.md#构建参数) |
| 镜像源切换（apt/conda/pip国内源） | [dockerfile.md](.agents/rules/dockerfile.md#镜像源切换) |
| 入口点conda激活三层机制 | [entrypoint.md](.agents/rules/entrypoint.md#conda环境激活机制) |
| gosu用户切换、RUN_AS_USER | [entrypoint.md](.agents/rules/entrypoint.md#启动流程4步) |
| 构建脚本13项自动验证 | [build-test.md](.agents/rules/build-test.md#验证清单13项) |

## 快速开始

```bash
# 在线构建
./build.sh

# 离线构建（先prepare-offline下载资源）
./build.sh --prepare-offline && ./build.sh --offline

# 运行验证
docker run --rm pytorch-base:2.13.0-py3.14-cpu python -c "import torch; print(torch.__version__)"

# 交互式shell
docker run -it --rm pytorch-base:2.13.0-py3.14-cpu
```

完整构建参数、GPU模式、离线准备、运行命令和问题排查见 [.agents/rules/build-test.md](.agents/rules/build-test.md)。

## 引用父级 SpecWeave 规范

本项目完全遵循 SpecWeave 工作区发现协议：
- AGENTS.md 包含「启动协议」关键词
- 正确引用父级 `../../AGENTS.md`
- 遵循嵌套优先原则，未覆盖的规则回退到父级工作区
- 支持工作区发现协议的五步发现流程
- AI资产已原子化拆分至 `.agents/` 目录，遵循单一职责原则

## 变更日志

- 2026-08-07 | refactor | 原子化拆分AGENTS.md：详细约束迁移至.agents/rules/（3个主题文件），AGENTS.md精简为路由入口
- 2026-07-22 | feat | 重构离线资源管理：统一使用 offline/ 目录替代分散的 wheels/ 和 conda-cache/；build.sh 增加 --prepare-offline
- 2026-07-22 | feat | 初始化 pytorch-base 项目结构：AGENTS.md、Dockerfile、build.sh、entrypoint.sh、environment.yml
