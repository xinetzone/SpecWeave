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
> 本项目特有的上下文路由与约束。

## 项目概述

- **项目类型**：Docker 镜像构建项目（SSH + Jupyter Notebook 基础镜像）
- **基础镜像**：ubuntu:26.04
- **核心功能**：OpenSSH Server + Jupyter Notebook，通过 supervisord 管理双服务
- **中文环境**：zh_CN.UTF-8 / Asia/Shanghai
- **非root用户**：jupyteruser (UID 1000)
- **父级工作区**：SpecWeave 根目录（`../../AGENTS.md`）— 全局规则、Skill、角色均以父级为准

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则、Skill、角色、团队）
  └─ apps/jupyter-ssh-base/AGENTS.md（本文件，项目特有约束）
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

**嵌套优先原则**：进入本目录后优先读取本文件；本文件未覆盖的规则回退到 SpecWeave 根 AGENTS.md。

## 上下文路由表

| 任务类型 | 必读入口 | 说明 |
|---------|---------|------|
| Dockerfile修改/构建优化 | 本文件 + Dockerfile | 镜像构建规范、多阶段构建、层缓存策略、supervisord集成 |
| supervisord配置 | config/supervisor/conf.d/ | SSH与Jupyter双服务管理配置 |
| entrypoint.sh启动脚本 | entrypoint.sh | 启动脚本规范、日志输出、错误处理、信号处理、用户切换 |
| Python依赖管理 | requirements.txt | Jupyter及相关Python包依赖 |
| 镜像构建与测试 | 本文件「快速开始」章节 | docker build/run/test命令、验证流程 |
| 全局规则（提交/代码风格/沟通） | [../../AGENTS.md](../../AGENTS.md) → [../../.agents/global-core-rules.md](../../.agents/global-core-rules.md) | 回退到父级工作区 |
| Skill使用 | [../../.agents/skills/](../../.agents/skills/) | 所有SpecWeave全局Skill可用 |
| 复盘/洞察/原子化/原子提交 | [../../.agents/commands/](../../.agents/commands/) | 七概念指令集，通过父级调用 |

## 核心规范入口

| 规范 | 入口 | 说明 |
|-----|------|------|
| 父级全局规则 | [../../AGENTS.md](../../AGENTS.md) | SpecWeave根工作区入口（启动协议必经之路） |
| 本文件入口 | AGENTS.md（本文件） | jupyter-ssh-base子项目路由 |
| Docker构建文件 | Dockerfile | 多阶段构建：builder(编译依赖) → runtime(最小运行时) |
| 入口点脚本 | entrypoint.sh | 容器启动逻辑，密码/密钥初始化、Jupyter动态配置、supervisord启动 |
| supervisord配置 | config/supervisor/conf.d/ | SSH和Jupyter双进程管理配置 |
| SSH配置 | config/sshd_config | ED25519优先、禁用root登录、密码+密钥认证 |
| Jupyter配置 | config/jupyter_notebook_config.py | 基础配置（0.0.0.0绑定、/workspace目录） |
| Python依赖 | requirements.txt | Jupyter及相关包，版本固定 |
| 辅助脚本 | scripts/ | build.sh（构建）、healthcheck.sh（健康检查） |
| Docker忽略规则 | .dockerignore | 排除.git/.trae/.agents/workspace/notebooks等非构建文件 |

## 项目特有约束

1. **中文环境**：容器内默认locale为`zh_CN.UTF-8`，时区`Asia/Shanghai`，构建注释使用英文（避免编码问题），运行时日志可使用中文
2. **基础镜像锁定**：固定使用`ubuntu:26.04`，除非用户明确要求变更
3. **非root用户**：固定用户名为`jupyteruser`，UID优先1000（被占用时自动分配）；默认无sudo权限，通过`GRANT_SUDO=yes`环境变量启用NOPASSWD sudo；HOME目录为`/home/jupyteruser`
4. **服务管理**：必须使用supervisord管理sshd和jupyter notebook双服务，确保两个进程都能正确启动、监控和自动重启
5. **启动脚本**：entrypoint.sh必须包含详细日志输出、权限修复、信号处理、命令模式支持
6. **构建日志**：Dockerfile中关键步骤使用`echo "[BUILD] ..."`输出构建日志
7. **敏感信息**：禁止在Dockerfile中硬编码密码/密钥，使用环境变量注入；密码哈希在entrypoint运行时动态生成
8. **镜像优化**：多阶段构建（builder阶段含build-essential/python3-dev，runtime阶段仅保留运行时必需包）；每个RUN指令后清理apt缓存（`rm -rf /var/lib/apt/lists/*`）；pip安装使用--no-cache-dir；最终镜像不含编译工具链
9. **Jupyter配置**：Python虚拟环境位于`/opt/venv`；默认监听0.0.0.0:8888；token/密码通过环境变量控制（JUPYTER_TOKEN/JUPYTER_PASSWORD）；Notebook工作目录为`/workspace`；默认CORS策略同源限制（`JUPYTER_ALLOW_ORIGIN`可配置）
10. **SSH配置**：默认监听22端口；默认禁用root登录（`ALLOW_ROOT_SSH=yes`可启用）；ED25519密钥优先；支持密码和密钥两种认证方式；host keys在容器启动时重新生成确保唯一性
11. **健康检查**：内置healthcheck.sh脚本，同时检查sshd进程/端口和jupyter进程/HTTP响应
12. **可复用性**：WORKDIR设置为`/workspace`，ENTRYPOINT使用tini init，支持作为其他项目的基础镜像（FROM jupyter-ssh-base）

## 快速开始

构建并测试镜像：

```bash
# 构建
docker build -t jupyter-ssh-base .
# 或使用构建脚本
bash scripts/build.sh

# 运行（映射SSH 2222和Jupyter 8888端口）
docker run -d -p 2222:22 -p 8888:8888 \
  -e USER_PASSWORD=changeme \
  -e JUPYTER_TOKEN=mysecret \
  -v jupyter-workspace:/workspace \
  --name jupyter-test jupyter-ssh-base

# 验证SSH（使用jupyteruser，root默认禁用）
ssh -p 2222 jupyteruser@localhost

# 验证Jupyter（浏览器访问）
# http://localhost:8888/?token=mysecret

# 验证jupyteruser用户
docker exec -it jupyter-test supervisorctl status

# 调试模式（不启动服务，直接进入shell）
docker run -it --rm jupyter-ssh-base bash
```

## 引用父级 SpecWeave 规范

本项目完全遵循 SpecWeave 工作区发现协议：
- AGENTS.md 包含「启动协议」关键词
- 正确引用父级 `../../AGENTS.md`
- 遵循嵌套优先原则，未覆盖的规则回退到父级工作区
- 支持工作区发现协议的五步发现流程

## 变更日志

- 2026-07-24 | feat | 七概念方法论全流程落地：R事实采集→I第一性原理本质分析→E对抗评审→C洞察提炼→A修复闭环→F原子拆分→V验证；多阶段构建优化（builder/runtime分离）；健康检查增强（sshd+jupyter双服务检测）；安全增强（CORS同源默认、运行时配置注入、host key每次重建）；WORKDIR标准化为/workspace；AGENTS.md同步更新
- 2026-07-24 | feat | 初始化项目结构：AGENTS.md、目录结构config/supervisor/conf.d、.dockerignore、requirements.txt
