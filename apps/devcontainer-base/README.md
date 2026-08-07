# DevContainer Base - 标准化开发容器基础镜像 (SSH + Docker + Podman + Jupyter)

> 基于 Ubuntu 26.04 的企业级全功能开发容器基础镜像，集成 OpenSSH Server、Docker DinD/DooD、Podman rootless 和 Jupyter Notebook/Lab 四大核心服务，通过 supervisord 统一进程管理，支持环境变量动态服务启停。

## ✨ 特性

- **基础环境**：Ubuntu 26.04 固定标签、中文 locale zh_CN.UTF-8、Asia/Shanghai 时区、Python 3 venv
- **四大服务**：SSH(22) + Docker DinD(2375) + Podman(rootless) + Jupyter(8888)，可独立启停
- **进程管理**：Supervisord 统一管理，服务自动重启、优先级调度
- **双容器运行时**：
  - Docker DinD 模式（--privileged，完全隔离）
  - Docker DooD 模式（挂载宿主 docker.sock，无需特权）
  - Podman rootless 模式（按需启动，无守护进程）
- **安全增强**：非 root 用户 devuser(UID 1000)、可选 NOPASSWD sudo、SSH ED25519 密钥、Jupyter Token/密码认证
- **灵活配置**：环境变量驱动、支持国内镜像源、运行时动态配置
- **多阶段构建**：Builder/runtime 分离、apt 缓存清理、最小化镜像
- **健康检查**：内置 HEALTHCHECK，按启用服务条件化检查
- **可组合性**：每个服务可独立启用/禁用，适合作为各类开发容器的 base image

## 🏗️ 项目结构

```
devcontainer-base/
├── Dockerfile                      # 主构建文件（多阶段构建）
├── entrypoint.sh                   # 容器启动脚本（服务动态启停）
├── requirements.txt                # Python 依赖版本固定
├── docker-compose.yml              # Compose 编排（3种profile）
├── .dockerignore                   # Docker 构建忽略文件
├── AGENTS.md                       # AI 协作者规范（SpecWeave）
├── config/
│   ├── supervisord.conf            # Supervisord 主配置
│   ├── sshd_config                 # SSH 服务完整配置
│   ├── jupyter_notebook_config.py  # Jupyter 基础配置
│   └── supervisor/
│       └── conf.d/
│           ├── sshd.conf           # SSH 进程配置
│           ├── dockerd.conf        # Docker daemon 进程配置
│           └── jupyter.conf        # Jupyter 进程配置
└── scripts/
    ├── build.sh                    # 一键构建脚本（支持--cn/--verify）
    ├── healthcheck.sh              # 容器健康检查脚本（条件化检测）
    └── lib/
        └── logging.sh              # 日志工具库
```

## 🚀 快速开始

### 构建镜像

```bash
# 方式1：直接 docker build
docker build -t devcontainer-base:1.0 .

# 方式2：使用构建脚本
bash scripts/build.sh

# 使用国内镜像源（apt/pip加速）
bash scripts/build.sh --cn

# 构建并验证（构建后自动启动临时容器验证服务）
bash scripts/build.sh --verify

# 使用国内镜像源构建并验证
bash scripts/build.sh --cn --verify
```

### Docker Compose（推荐）

提供 3 种 profile 适应不同场景：

```bash
# DinD模式：Docker-in-Docker（推荐，完全隔离，需--privileged）
docker compose --profile dind up -d

# DooD模式：Docker-out-of-Docker（使用宿主Docker，无需特权）
docker compose --profile dood up -d

# 仅SSH模式：最小化，无Docker/Jupyter
docker compose --profile ssh-only up -d

# 查看日志
docker compose logs -f

# 停止
docker compose down
```

### 手动运行容器

#### DinD模式（Docker-in-Docker，推荐用于开发环境）

```bash
docker run -d \
  --name devcontainer \
  --privileged \
  -p 2222:22 \
  -p 8888:8888 \
  -v $(pwd)/workspace:/workspace \
  -v docker-storage:/var/lib/docker \
  -e USER_PASSWORD=your_password \
  -e JUPYTER_TOKEN=your_token \
  -e GRANT_SUDO=yes \
  devcontainer-base:1.0
```

⚠️ **注意**: DinD模式必须使用 `--privileged`，否则Docker守护进程无法启动。

#### DooD模式（Docker-out-of-Docker，生产/CI环境）

```bash
docker run -d \
  --name devcontainer-dood \
  -p 2223:22 \
  -p 8889:8888 \
  -v $(pwd)/workspace:/workspace \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -e USER_PASSWORD=your_password \
  -e JUPYTER_TOKEN=your_token \
  devcontainer-base:1.0
```

DooD模式无需 `--privileged`，容器内 docker 命令直接操作宿主Docker。entrypoint 会自动检测宿主 socket 并禁用内部 dockerd。

#### 命令模式（调试/一次性任务）

```bash
docker run -it --rm devcontainer-base:1.0 bash
```

## 🔌 连接方式

> **注意**：以下端口为 `docker run` DinD示例。使用不同模式时请根据实际映射调整端口。

### SSH连接

```bash
ssh devuser@localhost -p 2222
```

### Jupyter Notebook

浏览器访问 http://localhost:8888/，使用 `JUPYTER_TOKEN` 或密码登录。

### Docker使用

容器内SSH登录后，devuser已在docker组，直接使用docker命令：

```bash
docker ps
docker run hello-world
docker build -t myapp .
```

### Podman使用（rootless，需ENABLE_PODMAN=yes）

```bash
podman ps
podman run --rm hello-world
```

## ⚙️ 环境变量配置

| 环境变量 | 默认值 | 说明 |
|---------|-------|------|
| `ENABLE_SSH` | `yes` | 启用SSH服务 |
| `ENABLE_DOCKER` | `yes` | 启用Docker（DinD模式；若检测到宿主socket则自动切换DooD） |
| `ENABLE_PODMAN` | `no` | 启用Podman rootless（与Docker同开时cgroupv2可能冲突） |
| `ENABLE_JUPYTER` | `yes` | 启用Jupyter Notebook/Lab |
| `USER_PASSWORD` | *(随机生成)* | devuser用户密码 |
| `ROOT_PASSWORD` | *(不设置)* | root密码，需 `ALLOW_ROOT_SSH=yes` |
| `JUPYTER_TOKEN` | *(随机生成)* | Jupyter访问令牌 |
| `JUPYTER_PASSWORD` | *(空)* | Jupyter密码（与Token二选一） |
| `GRANT_SUDO` | `no` | devuser免密sudo |
| `ALLOW_ROOT_SSH` | `no` | 允许root SSH登录 |
| `SSH_PUBLIC_KEY` | *(空)* | SSH公钥注入 |
| `JUPYTER_PORT` | `8888` | Jupyter端口 |
| `SSH_PORT` | `22` | SSH端口 |
| `TZ` | `Asia/Shanghai` | 时区 |
| `APT_MIRROR` | `official` | APT源（official/aliyun/tuna）- build-arg |
| `PIP_MIRROR` | `official` | PyPI源（official/aliyun/tuna）- build-arg |
| `DEBUG` | `0` | 调试模式 |

## 🔒 安全说明

1. **非root默认用户**：devuser（UID 1000），Jupyter以非root运行
2. **SSH安全配置**：
   - ED25519密钥优先
   - 禁用root登录（默认）
   - 禁用空密码
   - 严格模式
3. **Docker socket权限控制**：DooD模式挂载为 `ro` 只读
4. **Podman rootless模式**：无守护进程、用户命名空间隔离
5. **Jupyter认证**：Token/Password认证机制
6. **运行时SSH host keys生成**：容器启动时生成，避免密钥复用
7. ⚠️ **DinD模式--privileged安全警告**：特权模式赋予容器几乎所有宿主权限，仅用于可信开发环境；生产/CI环境推荐DooD模式或Podman

## 📋 服务管理 (supervisorctl)

```bash
# 查看所有服务状态
supervisorctl status

# 重启单个服务
supervisorctl restart sshd
supervisorctl restart dockerd
supervisorctl restart jupyter

# 查看服务日志
supervisorctl tail -f dockerd
supervisorctl tail -f jupyter
```

**Note**: Podman不通过supervisord管理，为rootless按需启动，无需守护进程。

## 🏗️ 作为基础镜像使用

```dockerfile
FROM devcontainer-base:1.0

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    your-package \
    && rm -rf /var/lib/apt/lists/*

USER devuser
# ENTRYPOINT保持不变，服务按环境变量自动启动
```

## 🔧 DinD vs DooD vs Podman 对比

| 特性 | DinD模式 | DooD模式 | Podman |
|------|---------|---------|--------|
| 需要--privileged | ✅ 是 | ❌ 否 | ❌ 否 |
| 容器隔离 | 完全隔离 | 共享宿主Docker | 用户命名空间隔离 |
| 性能 | 稍慢（嵌套） | 快（原生） | 快（无守护进程） |
| 安全性 | 较低（特权） | 中（共享socket） | 高（rootless） |
| 镜像持久化 | 需要volume | 宿主镜像共享 | 用户级存储 |
| docker-compose支持 | ✅ dind profile | ✅ dood profile | 手动启动 |

## 🩺 健康检查

内置 `healthcheck.sh`，条件化检查已启用服务：
- **SSH**: 端口监听检测
- **Docker**: dockerd进程 + docker.sock + docker info
- **Jupyter**: HTTP API检测（200/302/401/403为正常）

Docker HEALTHCHECK配置：
- `interval=30s`
- `timeout=10s`
- `start-period=60s`
- `retries=3`

## 📝 版本信息

- **版本**：1.0
- **基础镜像**：ubuntu:26.04
- **Python**：venv (/opt/venv)
- **Jupyter**: notebook 7.2.2, jupyterlab 4.2.5
- **Docker CE**：官方仓库最新稳定版
- **Podman**：Ubuntu 26.04官方源
- **OpenSSH**：Ubuntu 26.04官方包
- **Supervisor**：Ubuntu 26.04官方包

## 📄 许可证

遵循SpecWeave项目规范。

## 🤝 相关应用

- [jupyter-ssh-base](../jupyter-ssh-base/) - 基础镜像（SSH+Jupyter，无容器运行时）
- [docker-ssh-dind](../docker-ssh-dind/) - Docker DinD镜像（SSH+Docker，无Jupyter/Podman）
