# docker-ssh-dind - AI协作者入口 (AGENTS Manifest)

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
> 本文件是 docker-ssh-dind 子项目的 AI 协作者入口。本项目是一个 Docker-in-Docker SSH 镜像构建项目，
> 所有全局规则（沟通语言、提交规范、上下文节省等）继承自 SpecWeave 根工作区，本文件仅定义
> 本项目特有的上下文路由与约束入口。详细规则已原子化拆分至 `.agents/rules/` 目录。

## 项目概述

- **项目类型**：Docker 镜像构建项目（Containerfile + DinD + SSH）
- **基础镜像**：ubuntu:26.04
- **核心功能**：Docker-in-Docker (DinD) + OpenSSH Server，通过 tini init 管理
- **中文环境**：zh_CN.UTF-8 / Asia/Shanghai
- **非root用户**：ai (UID 1000)，docker组 + NOPASSWD sudo
- **父级工作区**：SpecWeave 根目录（`../../AGENTS.md`）— 全局规则、Skill、角色均以父级为准
- **AI资产容器**：`.agents/` 目录（本项目特有规则/脚本/模板）

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则、Skill、角色、团队）
  └─ apps/docker-images/docker-ssh-dind/AGENTS.md（本文件，项目路由入口）
       ├─ .agents/README.md          ← AI资产容器索引
       │   └─ rules/
       │       ├─ containerfile.md   ← Containerfile 编写规范
       │       ├─ entrypoint.md      ← 启动脚本规范
       │       └─ build-test.md      ← 构建与测试流程
       ├─ Containerfile       ← 镜像构建定义（7阶段）
       ├─ entrypoint.sh       ← 容器启动脚本
       ├─ docker-compose.yml ← Compose编排示例
       ├─ scripts/           ← 辅助脚本（dind.sh/dind.ps1/check-env.sh）
       ├─ docs/              ← 人类可读文档（决策记录/复盘）
       └─ .dockerignore      ← Docker构建忽略规则
```

**嵌套优先原则**：进入本目录后优先读取本文件；详细约束按主题加载 `.agents/rules/` 对应文件；未覆盖的规则回退到 SpecWeave 根 AGENTS.md。

## 上下文路由表

| 任务类型 | 必读入口 | 说明 |
|---------|---------|------|
| Containerfile修改/构建优化 | [.agents/rules/containerfile.md](.agents/rules/containerfile.md) | BuildKit语法、7阶段结构、层缓存策略、DinD daemon配置、安全规范 |
| entrypoint.sh启动脚本 | [.agents/rules/entrypoint.md](.agents/rules/entrypoint.md) | 6步启动流程、日志规范、信号处理、Docker就绪等待、系统诊断 |
| 镜像构建与测试 | [.agents/rules/build-test.md](.agents/rules/build-test.md) | docker build/run命令、7步验证流程、常见问题排查 |
| DinD决策记录 | [docs/decision-dind-vs-dood.md](docs/decision-dind-vs-dood.md) | DinD vs DooD架构选型决策 |
| AI资产容器索引 | [.agents/README.md](.agents/README.md) | .agents/目录结构、父级继承关系 |
| 全局规则（提交/代码风格/沟通） | [../../AGENTS.md](../../AGENTS.md) → [../../.agents/global-core-rules.md](../../.agents/global-core-rules.md) | 回退到父级工作区 |
| Skill使用 | [../../.agents/skills/](../../.agents/skills/) | 所有SpecWeave全局Skill可用 |
| 复盘/洞察/原子化/原子提交 | [../../.agents/commands/](../../.agents/commands/) | 七概念指令集，通过父级调用 |
| Dockerfile自动化测试 | [../../.agents/scripts/test-dockerfiles.ps1](../../.agents/scripts/test-dockerfiles.ps1) | 项目根目录测试脚本 |

## 核心规范入口

| 规范 | 入口 | 说明 |
|-----|------|------|
| 父级全局规则 | [../../AGENTS.md](../../AGENTS.md) | SpecWeave根工作区入口（启动协议必经之路） |
| 本文件入口 | AGENTS.md（本文件） | docker-ssh-dind子项目路由入口 |
| AI资产容器 | [.agents/README.md](.agents/README.md) | .agents/目录索引与父级继承关系 |
| Containerfile规范 | [.agents/rules/containerfile.md](.agents/rules/containerfile.md) | BuildKit/7阶段/缓存/安全/非root/DinD配置 |
| 入口点脚本规范 | [.agents/rules/entrypoint.md](.agents/rules/entrypoint.md) | 启动脚本6步流程/日志/信号/Docker等待/诊断 |
| 构建测试规范 | [.agents/rules/build-test.md](.agents/rules/build-test.md) | 构建/运行/验证命令/问题排查 |
| Containerfile构建文件 | Containerfile | 7阶段构建：环境→系统包→Docker Engine→非root用户→SSH→daemon→收尾 |
| 入口点脚本 | entrypoint.sh | 容器启动逻辑，密码初始化、SSH密钥、Docker启动、信号处理 |
| DinD辅助脚本 | scripts/ | dind.sh/dind.ps1/check-env.sh |
| Docker忽略规则 | .dockerignore | 排除.git/.trae/.agents/docs等非构建文件 |

## 项目约束速览

详细约束已按主题拆分到 `.agents/rules/` 下各文件，以下是核心约束索引：

| 约束主题 | 所在文件 |
|---------|---------|
| 中文环境（locale/timezone）、基础镜像锁定 | [containerfile.md](.agents/rules/containerfile.md#基础约定) |
| BuildKit语法、7阶段结构、层缓存优化 | [containerfile.md](.agents/rules/containerfile.md#结构规范) |
| 非root用户（ai/UID1000/docker组/sudo） | [containerfile.md](.agents/rules/containerfile.md#结构规范) |
| DinD daemon配置（overlay2/iptables/日志轮转） | [containerfile.md](.agents/rules/containerfile.md#结构规范) |
| 构建日志格式（[INFO]/[OK]/版本验证） | [containerfile.md](.agents/rules/containerfile.md#基础约定) |
| 敏感信息（禁止硬编码密码/密钥） | [containerfile.md](.agents/rules/containerfile.md#安全规范) |
| 镜像优化（--no-install-recommends/缓存清理） | [containerfile.md](.agents/rules/containerfile.md#体积优化) |
| tini init进程、6步启动流程 | [entrypoint.md](.agents/rules/entrypoint.md#基础约定) |
| 启动日志规范、信号处理、Docker就绪等待 | [entrypoint.md](.agents/rules/entrypoint.md#启动流程6步) |
| SSH配置（PermitRootLogin/主机密钥/公钥注入） | [entrypoint.md](.agents/rules/entrypoint.md#启动流程6步) |

## 快速开始

```bash
# 构建
docker build -t dind-ssh -f Containerfile .

# 运行（必须--privileged）
docker run -d --privileged -p 2222:22 \
  -e ROOT_PASSWORD=changeme -v dind-data:/var/lib/docker \
  --name dind-test dind-ssh

# 验证
docker exec dind-test docker version
ssh -p 2222 root@localhost
```

完整构建、运行、验证命令和常见问题排查见 [.agents/rules/build-test.md](.agents/rules/build-test.md)。

## 引用父级 SpecWeave 规范

本项目完全遵循 SpecWeave 工作区发现协议：
- AGENTS.md 包含「启动协议」关键词
- 正确引用父级 `../../AGENTS.md`
- 遵循嵌套优先原则，未覆盖的规则回退到父级工作区
- 支持工作区发现协议的五步发现流程
- AI资产已原子化拆分至 `.agents/` 目录，遵循单一职责原则

## 变更日志

- 2026-08-07 | refactor | AGENTS.md精简为路由入口，约束迁移至.agents/rules/（3个主题文件）；Containerfile规范补充BuildKit语法和缓存挂载
- 2026-07-20 | feat | 初始化AGENTS.md + .agents骨架，基于七概念方法论F→V→A→C链路创建
