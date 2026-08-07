# devcontainer-base - AI协作者入口 (AGENTS Manifest)

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
> 本文件是 devcontainer-base 子项目的 AI 协作者入口。本项目是一个全功能开发容器基础镜像构建项目，
> 集成 SSH + Docker DinD + Podman(rootless) + Jupyter，通过 supervisord 管理多服务，
> 所有全局规则（沟通语言、提交规范、上下文节省等）继承自 SpecWeave 根工作区，本文件仅定义
> 本项目特有的上下文路由与约束。

## 项目概述

- **项目类型**：Docker 镜像构建项目（Ubuntu 26.04 + SSH + Docker DinD + Podman + Jupyter，supervisord 管理多服务）
- **基础镜像**：ubuntu:26.04
- **核心功能**：OpenSSH Server + Docker-in-Docker + Podman(rootless) + Jupyter Notebook/Lab，通过 supervisord 统一管理四服务
- **中文环境**：zh_CN.UTF-8 / Asia/Shanghai
- **非root用户**：devuser (UID 1000)，加入docker组，可选NOPASSWD sudo（通过GRANT_SUDO环境变量控制）
- **服务端口**：sshd(22) + dockerd(2375) + podman(rootless) + jupyter(8888)
- **父级工作区**：SpecWeave 根目录（`../../AGENTS.md`）— 全局规则、Skill、角色均以父级为准

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则、Skill、角色、团队）
  └─ apps/devcontainer-base/AGENTS.md（本文件，项目特有约束）
       ├─ Dockerfile           ← 多阶段构建定义（builder + runtime）
       ├─ entrypoint.sh        ← 容器启动脚本
       ├─ requirements.txt     ← Python 依赖包列表
       ├─ config/              ← 配置文件目录
       │   ├─ supervisord.conf ← supervisord 主配置
       │   ├─ sshd_config      ← SSH 服务配置
       │   ├─ jupyter_notebook_config.py ← Jupyter 基础配置
       │   └─ supervisor/      ← supervisord 配置
       │       └─ conf.d/      ← 服务配置文件（sshd/dockerd/podman/jupyter）
       ├─ scripts/             ← 辅助脚本
       │   ├─ lib/             ← 脚本共享库
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
| Dockerfile修改/构建优化 | 本文件 + Dockerfile | 镜像构建规范、多阶段构建、层缓存策略、supervisord集成、DinD配置 |
| supervisord配置 | config/supervisor/conf.d/ | sshd+dockerd+podman+jupyter四服务管理配置 |
| Docker DinD配置 | Dockerfile + entrypoint.sh | Docker-in-Docker特权模式配置、dockerd启动参数、存储驱动 |
| Podman rootless配置 | Dockerfile + config/ | rootless Podman配置、用户命名空间、cgroupv2支持 |
| entrypoint.sh启动脚本 | entrypoint.sh | 启动脚本规范、日志输出、错误处理、信号处理、用户切换、Docker/Podman初始化 |
| Python依赖管理 | requirements.txt | Jupyter及相关Python包依赖 |
| 镜像构建与测试 | 本文件「快速开始」章节 | docker build/run/test命令、验证流程、健康检查 |
| 全局规则（提交/代码风格/沟通） | [../../AGENTS.md](../../AGENTS.md) → [../../.agents/global-core-rules.md](../../.agents/global-core-rules.md) | 回退到父级工作区 |
| Skill使用 | [../../.agents/skills/](../../.agents/skills/) | 所有SpecWeave全局Skill可用 |
| 复盘/洞察/原子化/原子提交 | [../../.agents/commands/](../../.agents/commands/) | 七概念指令集，通过父级调用 |

## 核心规范入口

| 规范 | 入口 | 说明 |
|-----|------|------|
| 父级全局规则 | [../../AGENTS.md](../../AGENTS.md) | SpecWeave根工作区入口（启动协议必经之路） |
| 本文件入口 | AGENTS.md（本文件） | devcontainer-base子项目路由 |
| Docker构建文件 | Dockerfile | 多阶段构建：builder(编译依赖) → runtime(最小运行时)，集成Docker/Podman/Jupyter |
| 入口点脚本 | entrypoint.sh | 容器启动逻辑，密码/密钥初始化、Docker/Podman初始化、Jupyter动态配置、supervisord启动 |
| supervisord配置 | config/supervisor/conf.d/ | sshd、dockerd、podman、jupyter四进程管理配置 |
| SSH配置 | config/sshd_config | ED25519优先、禁用root登录、密码+密钥认证 |
| Jupyter配置 | config/jupyter_notebook_config.py | 基础配置（0.0.0.0绑定、/workspace目录） |
| Docker配置 | Dockerfile + entrypoint.sh | DinD配置、特权模式、docker组权限、dockerd启动参数 |
| Podman配置 | Dockerfile + config/ | rootless Podman、用户命名空间、cgroup配置 |
| Python依赖 | requirements.txt | Jupyter及相关包，版本固定 |
| 辅助脚本 | scripts/ | build.sh（构建）、healthcheck.sh（健康检查）、lib/（共享库） |
| Docker忽略规则 | .dockerignore | 排除.git/.trae/.agents/workspace/notebooks等非构建文件 |

## 项目特有约束

1. **中文环境**：容器内默认locale为`zh_CN.UTF-8`，时区`Asia/Shanghai`，构建注释使用英文（避免编码问题），运行时日志可使用中文
2. **基础镜像锁定**：固定使用`ubuntu:26.04`，除非用户明确要求变更
3. **非root用户**：固定用户名为`devuser`，UID优先1000（被占用时自动分配）；默认加入docker组；默认无sudo权限，通过`GRANT_SUDO=yes`环境变量启用NOPASSWD sudo；HOME目录为`/home/devuser`
4. **服务管理**：必须使用supervisord管理sshd、dockerd、podman、jupyter四服务，确保所有进程都能正确启动、监控和自动重启
5. **Docker DinD**：dockerd监听2375端口（仅内部访问），需要--privileged权限运行，使用vfs存储驱动或overlay2（取决于宿主机），docker数据目录`/var/lib/docker`建议挂载volume持久化
6. **Podman rootless**：以devuser身份运行rootless Podman，配置用户命名空间，支持cgroupv2，无需特权模式即可运行容器
7. **启动脚本**：entrypoint.sh必须包含详细日志输出、权限修复、信号处理、Docker/Podman初始化、命令模式支持
8. **构建日志**：Dockerfile中关键步骤使用`echo "[BUILD] ..."`输出构建日志
9. **敏感信息**：禁止在Dockerfile中硬编码密码/密钥，使用环境变量注入；密码哈希在entrypoint运行时动态生成；Docker socket不暴露到公网
10. **镜像优化**：多阶段构建（builder阶段含build-essential/python3-dev，runtime阶段仅保留运行时必需包）；每个RUN指令后清理apt缓存（`rm -rf /var/lib/apt/lists/*`）；pip安装使用--no-cache-dir；Docker/Podman客户端与服务端版本匹配
11. **Jupyter配置**：Python虚拟环境位于`/opt/venv`；默认监听0.0.0.0:8888；token/密码通过环境变量控制（JUPYTER_TOKEN/JUPYTER_PASSWORD）；Notebook工作目录为`/workspace`；默认CORS策略同源限制（`JUPYTER_ALLOW_ORIGIN`可配置）
12. **SSH配置**：默认监听22端口；默认禁用root登录（`ALLOW_ROOT_SSH=yes`可启用）；ED25519密钥优先；支持密码和密钥两种认证方式；host keys在容器启动时重新生成确保唯一性
13. **健康检查**：内置healthcheck.sh脚本，同时检查sshd进程/端口、dockerd进程/API、podman可用性、jupyter进程/HTTP响应
14. **可复用性**：WORKDIR设置为`/workspace`，ENTRYPOINT使用tini init，支持作为其他项目的基础镜像（FROM devcontainer-base）
15. **Docker与Podman共存**：确保Docker CLI与Podman CLI可同时使用，devuser可同时访问docker组（用于DinD）和podman rootless socket

## 快速开始

构建并测试镜像：

```bash
# 构建
docker build -t devcontainer-base .
# 或使用构建脚本
bash scripts/build.sh

# 运行（需要--privileged用于DinD，映射SSH 2222、Docker 2375、Jupyter 8888端口）
docker run -d --privileged -p 2222:22 -p 2375:2375 -p 8888:8888 \
  -e USER_PASSWORD=changeme \
  -e JUPYTER_TOKEN=mysecret \
  -e GRANT_SUDO=yes \
  -v devcontainer-workspace:/workspace \
  -v devcontainer-docker:/var/lib/docker \
  --name devcontainer-test devcontainer-base

# 验证SSH（使用devuser，root默认禁用）
ssh -p 2222 devuser@localhost

# 验证Jupyter（浏览器访问）
# http://localhost:8888/?token=mysecret

# 验证Docker DinD
docker exec -it devcontainer-test docker ps

# 验证Podman rootless
docker exec -it devcontainer-test su - devuser -c "podman ps"

# 验证supervisord服务状态
docker exec -it devcontainer-test supervisorctl status

# 验证sudo权限（需设置GRANT_SUDO=yes）
docker exec devcontainer-test su - devuser -c "sudo -n whoami"

# 调试模式（不启动服务，直接进入shell）
docker run -it --rm --privileged devcontainer-base bash
```

## 引用父级 SpecWeave 规范

本项目完全遵循 SpecWeave 工作区发现协议：
- AGENTS.md 包含「启动协议」关键词
- 正确引用父级 `../../AGENTS.md`
- 遵循嵌套优先原则，未覆盖的规则回退到父级工作区
- 支持工作区发现协议的五步发现流程

## 变更日志

- 2026-08-07 | feat | 初始化项目结构：AGENTS.md、目录结构config/supervisor/conf.d、scripts/lib/、.dockerignore、requirements.txt
