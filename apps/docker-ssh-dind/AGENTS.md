# docker-ssh-dind - AI协作者入口 (AGENTS Manifest)

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
> 本文件是 docker-ssh-dind 子项目的 AI 协作者入口。本项目是一个 Docker-in-Docker SSH 镜像构建项目，
> 所有全局规则（沟通语言、提交规范、上下文节省等）继承自 SpecWeave 根工作区，本文件仅定义
> 本项目特有的上下文路由与约束。

## 项目概述

- **项目类型**：Docker 镜像构建项目（Containerfile + entrypoint.sh）
- **基础镜像**：ubuntu:26.04
- **核心功能**：Docker-in-Docker (DinD) + OpenSSH Server，中文环境（zh_CN.UTF-8 / Asia/Shanghai）
- **非root用户**：ai (UID 1000)，docker组+免密sudo
- **父级工作区**：SpecWeave 根目录（`../../AGENTS.md`）— 全局规则、Skill、角色均以父级为准

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则、Skill、角色、团队）
  └─ apps/docker-ssh-dind/AGENTS.md（本文件，项目特有约束）
       ├─ Containerfile       ← 镜像构建定义
       ├─ entrypoint.sh       ← 容器启动脚本
       ├─ README.md           ← 使用文档
       ├─ docs/               ← 人类可读文档
       └─ .agents/            ← 本项目AI资产容器
            ├─ rules/         ← 项目特有规则
            ├─ roles/         ← 角色定义（预留）
            ├─ skills/        ← 技能（预留）
            ├─ scripts/       ← 自动化脚本（预留）
            ├─ workflows/     ← 工作流（预留）
            ├─ templates/     ← 模板（预留）
            └─ docs/          ← AI知识库（预留）
```

**嵌套优先原则**：进入本目录后优先读取本文件；本文件未覆盖的规则回退到 SpecWeave 根 AGENTS.md。

## 上下文路由表

| 任务类型 | 必读入口 | 说明 |
|---------|---------|------|
| Containerfile修改/构建优化 | [.agents/rules/containerfile.md](.agents/rules/containerfile.md) | Containerfile编写规范、多阶段构建、层缓存策略 |
| entrypoint.sh启动脚本 | [.agents/rules/entrypoint.md](.agents/rules/entrypoint.md) | 启动脚本规范、日志输出、错误处理、信号处理 |
| 镜像构建与测试 | [.agents/rules/build-test.md](.agents/rules/build-test.md) | docker build/run/test命令、验证流程 |
| 全局规则（提交/代码风格/沟通） | [../../AGENTS.md](../../AGENTS.md) → [../../.agents/global-core-rules.md](../../.agents/global-core-rules.md) | 回退到父级工作区 |
| Skill使用 | [../../.agents/skills/](../../.agents/skills/) | 所有SpecWeave全局Skill可用 |
| 复盘/洞察/原子化/原子提交 | [../../.agents/commands/](../../.agents/commands/) | 七概念指令集，通过父级调用 |

## 核心规范入口

| 规范 | 入口 | 说明 |
|-----|------|------|
| 父级全局规则 | [../../AGENTS.md](../../AGENTS.md) | SpecWeave根工作区入口（启动协议必经之路） |
| 本文件入口 | AGENTS.md（本文件） | docker-ssh-dind子项目路由 |
| Containerfile规则 | [.agents/rules/containerfile.md](.agents/rules/containerfile.md) | 镜像构建规范 |
| entrypoint规则 | [.agents/rules/entrypoint.md](.agents/rules/entrypoint.md) | 启动脚本规范 |
| 构建测试规则 | [.agents/rules/build-test.md](.agents/rules/build-test.md) | 构建与验证命令 |

## 项目特有约束

1. **中文环境**：容器内默认locale为`zh_CN.UTF-8`，时区`Asia/Shanghai`，构建注释使用英文（避免编码问题），运行时日志可使用中文
2. **基础镜像锁定**：固定使用`ubuntu:26.04`，除非用户明确要求变更
3. **非root用户**：固定用户名为`ai`，UID 1000，加入docker组，配置NOPASSWD sudo
4. **启动脚本**：必须使用tini作为init进程，entrypoint.sh必须包含详细日志输出和诊断信息
5. **构建日志**：Containerfile中关键步骤使用`echo "[BUILD] ..."`输出构建日志
6. **敏感信息**：禁止在Containerfile中硬编码密码/密钥，使用环境变量或build-arg注入
7. **镜像体积**：每个RUN指令后清理apt缓存（`rm -rf /var/lib/apt/lists/*`）

## 快速开始

构建并测试镜像：

```bash
# 构建
docker build -t dind-ssh -f Containerfile .

# 运行（需要--privileged）
docker run -d --privileged -p 2222:22 -v dind-data:/var/lib/docker \
  -e ROOT_PASSWORD=test123 --name dind-test dind-ssh

# 验证SSH
ssh -p 2222 root@localhost

# 验证Docker（容器内）
docker exec -it dind-test docker ps

# 验证ai用户sudo
docker exec dind-test su - ai -c "sudo -n whoami"
```

## 变更日志

- 2026-07-20 | feat | 初始化AGENTS.md + .agents骨架，基于七概念方法论F→V→A→C链路创建
