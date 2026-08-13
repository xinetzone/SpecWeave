---
title: "Hermes Agent 安装方案 - Docker 容器化部署指南"
chapter: 5
source:
  - external/libs/hermes-agent/Dockerfile
  - external/libs/hermes-agent/docker-compose.yml
  - external/libs/hermes-agent/docker-compose.windows.yml
  - external/libs/hermes-agent/.dockerignore
  - external/libs/hermes-agent/.env.example
  - external/libs/hermes-agent/docker/entrypoint.sh
  - external/libs/hermes-agent/docker/entrypoint-dispatch.sh
  - external/libs/hermes-agent/docker/main-wrapper.sh
  - external/libs/hermes-agent/docker/stage2-hook.sh
  - external/libs/hermes-agent/docker/tini-shim.sh
  - external/libs/hermes-agent/docker/hermes-exec-shim.sh
  - external/libs/hermes-agent/docker/s6-rc.d/main-hermes/run
  - external/libs/hermes-agent/docker/s6-rc.d/dashboard/run
  - external/libs/hermes-agent/docker/s6-rc.d/dashboard/finish
  - external/libs/hermes-agent/docker/SOUL.md
---

# 5. Docker 容器化部署指南

本章详细说明如何使用 Docker 构建、部署和运维 Hermes Agent 容器。内容涵盖 Docker 镜像构建方法、`docker-compose.yml` 配置说明、卷挂载与权限配置、s6-overlay 进程管理机制、常用 `docker compose` 命令、环境变量传递方式、Dashboard 安全提示、镜像分层结构以及网络模式。所有信息均以项目源码中的 `Dockerfile`、`docker-compose.yml` 及 `docker/` 目录下的脚本为准。

> Docker 容器化部署适用于：希望快速启动且不污染主机环境的用户、NAS / 自托管服务器、需要隔离运行时的生产环境，以及 CI/CD 流水线。容器基于 Debian 13（trixie），使用 s6-overlay 进行进程管理，默认以非 root 用户运行。容器内**不支持** `hermes update`，版本更新需拉取新镜像。

---

## 5.1 Docker 镜像构建方法

### 5.1.1 前置要求

构建镜像前，请确保已安装：

- **Docker** 20.10+（推荐 24+，需支持 BuildKit）
- **Docker Compose** v2（`docker compose` 插件形式）
- 至少 8 GB 可用磁盘空间（镜像含 Python venv、Node.js、Playwright Chromium）
- 网络连接（构建过程需从 PyPI、npm、GitHub Releases、sqlite.org 等下载依赖）

验证 Docker 可用性：

```bash
docker --version
docker compose version
docker buildx version
```

### 5.1.2 从源码构建（推荐）

在项目根目录（即 `Dockerfile` 所在目录）执行：

```bash
# 克隆仓库（若尚未克隆）
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent

# 构建镜像（启用 BuildKit）
DOCKER_BUILDKIT=1 docker build -t hermes-agent:latest .
```

构建过程约 15–45 分钟（取决于网络和 CPU 性能），主要耗时在 Python 依赖编译和 Playwright Chromium 下载。

### 5.1.3 带构建参数的构建

`Dockerfile` 支持以下构建参数（`ARG`）：

| 参数 | 默认值 | 说明 |
|---|---|---|
| `SQLITE_AUTOCONF_VERSION` | `3530400` | SQLite 编译版本（3.53.4） |
| `SQLITE_SHA256` | （内置） | SQLite 源码包 SHA256 校验值 |
| `S6_OVERLAY_VERSION` | `3.2.3.0` | s6-overlay 版本 |
| `HERMES_GIT_SHA` | （空） | 构建时的 Git commit SHA，用于版本溯源 |
| `TARGETARCH` | （BuildKit 自动填充） | 目标架构：`amd64` 或 `arm64` |

传入 Git SHA 的构建示例（CI 场景）：

```bash
docker build \
  --build-arg HERMES_GIT_SHA=$(git rev-parse HEAD) \
  -t hermes-agent:$(git rev-parse --short HEAD) \
  .
```

`HERMES_GIT_SHA` 会被写入镜像内 `/opt/hermes/.hermes_build_sha`，运行时 `hermes dump` 和启动横幅会读取该值显示版本信息。

### 5.1.4 多架构构建

`Dockerfile` 通过 BuildKit 的 `TARGETARCH` 自动适配 `amd64` 和 `arm64`：

```bash
# 创建多架构构建器（首次使用）
docker buildx create --name hermes-builder --use

# 构建并推送多架构镜像
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t your-registry/hermes-agent:latest \
  --push .
```

s6-overlay 的架构相关 tarball 会根据 `TARGETARCH` 自动选择 `x86_64`（amd64）或 `aarch64`（arm64）版本，并通过 SHA256 校验完整性。

### 5.1.5 构建上下文与 .dockerignore

项目根目录的 `.dockerignore` 文件排除了以下内容以减小构建上下文、加速构建并避免缓存失效：

- Git 元数据（`.git`、`.gitignore`、`.gitmodules`）
- Python 缓存与虚拟环境（`__pycache__`、`.venv`、`venv/`、`*.egg-info/`）
- Node.js 依赖（`node_modules`，各层级均排除）
- 构建产物（`ui-tui/dist/`、`dist/`、`build/`）
- 环境文件（`.env`、`.env.*`）
- IDE 配置（`.vscode/`、`.idea/`）
- 测试套件（`tests/`）
- 文档（`*.md`、`docs/`、`website/`）
- 桌面应用源码（`apps/`，但保留 `apps/shared/`，因其被 web workspace 引用）
- Nix/打包元数据（`nix/`、`flake.nix`、`packaging/`）
- 运行时数据（`data/`、`.hermes-docker/`、`hermes-config/`、`runtime/`）

> **注意**：`.dockerignore` 排除了 `*.md`，但 `pyproject.toml` 的 `readme =` 字段引用了 `README.md`。`Dockerfile` 在 Python 依赖安装层通过 `touch ./README.md` 创建空占位文件以满足 uv 的构建前端需求，真正的 README 在后续 `COPY . .` 层恢复。

### 5.1.6 使用预构建镜像

若不需要从源码构建，可直接拉取官方镜像（docker-compose.windows.yml 中使用的镜像名）：

```bash
docker pull nousresearch/hermes-agent:latest
```

---

## 5.2 docker-compose.yml 配置说明

项目根目录提供两个 Compose 文件：

| 文件 | 适用平台 | 网络模式 |
|---|---|---|
| `docker-compose.yml` | Linux / macOS / WSL2 | `network_mode: host` |
| `docker-compose.windows.yml` | Windows Docker Desktop | 端口映射（`ports`） |

### 5.2.1 服务总览

`docker-compose.yml` 定义了两个服务：

| 服务 | 容器名 | 命令 | 职责 |
|---|---|---|---|
| `gateway` | `hermes` | `gateway run` | Hermes 主网关进程，处理消息平台、定时任务、Agent 会话 |
| `dashboard` | `hermes-dashboard` | `dashboard --host 127.0.0.1 --no-open` | Web 管理界面，默认仅监听本地回环 |

两个服务共享同一个数据卷 `~/.hermes:/opt/data`，因此配置、认证信息和会话数据互通。

### 5.2.2 gateway 服务详解

```yaml
services:
  gateway:
    build: .
    image: hermes-agent
    container_name: hermes
    restart: unless-stopped
    network_mode: host
    volumes:
      - ~/.hermes:/opt/data
    environment:
      - HERMES_UID=${HERMES_UID:-10000}
      - HERMES_GID=${HERMES_GID:-10000}
    command: ["gateway", "run"]
```

关键字段说明：

- **`build: .`**：从当前目录的 `Dockerfile` 构建镜像。首次执行 `docker compose up` 时自动构建。
- **`image: hermes-agent`**：构建后标记的镜像名。`dashboard` 服务复用同一镜像，无需重复构建。
- **`restart: unless-stopped`**：容器退出时自动重启，除非被手动停止。适合长期运行的网关服务。
- **`network_mode: host`**：使用主机网络模式（详见 5.10 节）。
- **`volumes`**：将主机的 `~/.hermes` 挂载到容器内 `/opt/data`，实现数据持久化。
- **`command`**：覆盖镜像默认 CMD，启动网关主进程。

### 5.2.3 dashboard 服务详解

```yaml
  dashboard:
    image: hermes-agent
    container_name: hermes-dashboard
    restart: unless-stopped
    network_mode: host
    depends_on:
      - gateway
    volumes:
      - ~/.hermes:/opt/data
    environment:
      - HERMES_UID=${HERMES_UID:-10000}
      - HERMES_GID=${HERMES_GID:-10000}
    command: ["dashboard", "--host", "127.0.0.1", "--no-open"]
```

关键字段说明：

- **`depends_on: gateway`**：dashboard 在 gateway 之后启动。注意这仅控制启动顺序，不等待 gateway 健康检查通过。
- **`--host 127.0.0.1`**：Dashboard 仅绑定本地回环地址，外部网络无法直接访问（安全措施，详见 5.8 节）。
- **`--no-open`**：启动时不自动打开浏览器（容器内无桌面环境，必须指定）。
- Dashboard 默认监听端口 **9119**，主机网络模式下可通过 `http://127.0.0.1:9119` 访问。

### 5.2.4 可选的环境变量配置

`docker-compose.yml` 中以注释形式提供了多种可选集成的环境变量模板，取消注释并填入值即可启用：

```yaml
environment:
  - HERMES_UID=${HERMES_UID:-10000}
  - HERMES_GID=${HERMES_GID:-10000}
  # OpenAI 兼容 API 服务器（需同时设置 HOST 和 KEY）
  # - API_SERVER_HOST=0.0.0.0
  # - API_SERVER_KEY=${API_SERVER_KEY}
  # Microsoft Teams 网关
  # - TEAMS_CLIENT_ID=${TEAMS_CLIENT_ID}
  # - TEAMS_CLIENT_SECRET=${TEAMS_CLIENT_SECRET}
  # - TEAMS_TENANT_ID=${TEAMS_TENANT_ID}
  # - TEAMS_ALLOWED_USERS=${TEAMS_ALLOWED_USERS}
  # - TEAMS_PORT=${TEAMS_PORT:-3978}
  # Google Chat 网关
  # - GOOGLE_CHAT_PROJECT_ID=${GOOGLE_CHAT_PROJECT_ID}
  # - GOOGLE_CHAT_SUBSCRIPTION_NAME=${GOOGLE_CHAT_SUBSCRIPTION_NAME}
  # - GOOGLE_CHAT_SERVICE_ACCOUNT_JSON=${GOOGLE_CHAT_SERVICE_ACCOUNT_JSON}
  # - GOOGLE_CHAT_ALLOWED_USERS=${GOOGLE_CHAT_ALLOWED_USERS}
```

> **安全提示**：`API_SERVER_HOST=0.0.0.0` 会将 API 服务器暴露到所有网络接口，必须同时设置 `API_SERVER_KEY` 进行认证。在面向互联网的主机上启用前，请参阅官方 API 服务器文档。

### 5.2.5 Windows Docker Desktop 配置

Windows 上 Docker Desktop 不支持 `network_mode: host`，因此使用 `docker-compose.windows.yml`：

```yaml
services:
  gateway:
    image: nousresearch/hermes-agent:latest
    container_name: hermes
    restart: unless-stopped
    volumes:
      - ${USERPROFILE}/.hermes:/opt/data
    environment:
      - HERMES_UID=10000
      - HERMES_GID=10000
    command: ["gateway", "run"]

  dashboard:
    image: nousresearch/hermes-agent:latest
    container_name: hermes-dashboard
    restart: unless-stopped
    depends_on:
      - gateway
    volumes:
      - ${USERPROFILE}/.hermes:/opt/data
    environment:
      - HERMES_UID=10000
      - HERMES_GID=10000
      - HERMES_DASHBOARD_HOST=0.0.0.0
    ports:
      - "127.0.0.1:9119:9119"
    command: ["dashboard", "--host", "0.0.0.0", "--port", "9119", "--no-open", "--insecure"]
```

主要差异：

- 使用 `${USERPROFILE}/.hermes` 代替 `~/.hermes`（Windows 路径）；
- 通过 `ports: "127.0.0.1:9119:9119"` 映射端口，且仅绑定主机回环地址；
- Dashboard 在容器内绑定 `0.0.0.0`（Docker Desktop 的 NAT 网络要求），但端口映射层限制了外部访问；
- 使用预构建镜像而非本地构建；
- UID/GID 固定为 `10000`（Windows 文件系统的权限模型不同，无需主机 UID 匹配）。

启动方式：

```powershell
docker compose -f docker-compose.windows.yml up -d
```

---

## 5.3 卷挂载说明

### 5.3.1 数据卷映射

Hermes 容器将所有持久化数据存储在 `/opt/data`（由 `ENV HERMES_HOME=/opt/data` 指定），并通过 `VOLUME ["/opt/data"]` 声明为 Docker 卷。Compose 文件中将其映射到主机目录：

```yaml
volumes:
  - ~/.hermes:/opt/data
```

| 主机路径（Linux/macOS） | 容器路径 | 用途 |
|---|---|---|
| `~/.hermes` | `/opt/data` | Hermes 配置、认证、会话、日志、技能等全部持久化数据 |

| 主机路径（Windows） | 容器路径 | 用途 |
|---|---|---|
| `%USERPROFILE%\.hermes` | `/opt/data` | 同上 |

### 5.3.2 /opt/data 目录结构

容器首次启动时，`stage2-hook.sh` 会以 `hermes` 用户身份在 `/opt/data` 下创建以下标准子目录：

| 子目录 | 用途 |
|---|---|
| `backups/` | 数据库备份 |
| `cron/` | 定时任务状态（`jobs.json`） |
| `sessions/` | Agent 会话记录 |
| `logs/` | 运行日志 |
| `logs/gateways/` | 各网关实例日志 |
| `hooks/` | 自定义钩子脚本 |
| `memories/` | 记忆数据 |
| `skills/` | 已安装技能 |
| `skins/` | 界面皮肤 |
| `plans/` | 计划文件 |
| `workspace/` | Agent 工作区 |
| `home/` | 用户主目录数据 |
| `profiles/` | 多配置文件网关数据 |
| `pairing/` | 设备配对数据 |
| `platforms/pairing/` | 平台配对数据（新布局） |
| `lazy-packages/` | 懒加载可选后端 SDK（详见下文） |

### 5.3.3 配置文件初始化

首次启动时（数据卷中不存在对应文件），容器会自动从镜像内复制种子配置：

| 容器内目标路径 | 镜像内源路径 | 说明 |
|---|---|---|
| `/opt/data/.env` | `/opt/hermes/.env.example` | 环境变量配置（API 密钥等），权限设为 `0600` |
| `/opt/data/config.yaml` | `/opt/hermes/cli-config.yaml.example` | Hermes 主配置，权限设为 `0640` |
| `/opt/data/SOUL.md` | `/opt/hermes/docker/SOUL.md` | Agent 人格定义 |

`.env` 文件在每次启动时都会被强制 `chmod 600` 和 `chown hermes:hermes`，即使它是在主机上编辑的，以防止 API 密钥泄露。

### 5.3.4 只读安装树与可写数据卷

容器内 `/opt/hermes` 是**只读**的安装树（root 所有，`go-w` 权限），包含：

- Python 虚拟环境（`.venv/`）
- Node.js 依赖（`node_modules/`）
- 前端构建产物（`web/dist/`、`ui-tui/dist/`）
- 应用源码
- Playwright 浏览器（`/opt/hermes/.playwright/`，由 `PLAYWRIGHT_BROWSERS_PATH` 指定，避免被数据卷覆盖）

这意味着运行时**不能**在容器内通过 `pip install` 或 `npm install` 修改核心依赖。可选后端（Firecrawl、Exa、飞书等）的 SDK 安装会被重定向到 `/opt/data/lazy-packages/`（由 `HERMES_LAZY_INSTALL_TARGET` 指定），该目录位于可写数据卷上，且追加到 `sys.path` 末尾，不会覆盖核心模块。

### 5.3.5 Docker Socket 挂载（可选）

若需要在容器内使用 `docker` 终端后端（让 Hermes 在兄弟容器中执行命令），可额外挂载 Docker socket：

```yaml
volumes:
  - ~/.hermes:/opt/data
  - /var/run/docker.sock:/var/run/docker.sock
```

`stage2-hook.sh` 会在启动时自动检测 socket 的 GID，将 `hermes` 用户加入对应组，确保容器内的 `docker` CLI 有权限访问主机 Docker 守护进程。

> **安全警告**：挂载 Docker socket 等同于授予容器对主机的 root 权限。仅在信任容器内工作负载时使用。

---

## 5.4 权限配置（HERMES_UID / HERMES_GID）

### 5.4.1 为什么需要 UID/GID 映射

容器内的 `hermes` 用户默认 UID 为 `10000`。当主机的 `~/.hermes` 目录由其他 UID 的用户所有时（例如 Linux 桌面用户通常是 UID `1000`），容器内进程写入的文件在主机上会显示为 `10000:10000` 所有，导致主机端 Hermes 安装或用户无法读写。

`HERMES_UID` 和 `HERMES_GID` 环境变量在容器启动时通过 `usermod`/`groupmod` 将内部 `hermes` 用户重映射到指定 UID/GID，使容器写入的文件与主机用户所有权一致。

### 5.4.2 设置方法

**Linux/macOS（推荐方式）：**

```bash
# 使用当前主机用户的 UID/GID 启动
HERMES_UID=$(id -u) HERMES_GID=$(id -g) docker compose up -d
```

或在 `.env` 文件中设置（与 `docker-compose.yml` 同目录）：

```bash
# .env
HERMES_UID=1000
HERMES_GID=1000
```

然后正常启动：

```bash
docker compose up -d
```

**NAS 用户（Synology / unRAID / UGOS）：**

支持 LinuxServer.io 风格的 `PUID`/`PGID` 别名：

```bash
docker run -e PUID=$(id -u) -e PGID=$(id -g) hermes-agent
```

当 `HERMES_UID` 和 `PUID` 同时设置时，`HERMES_UID` 优先。

### 5.4.3 有效值范围

- UID/GID 必须为纯数字，范围 `1`–`65534`（不含 root 的 `0`）；
- 不允许使用 `--user` 参数直接指定任意 UID（见下文）；
- GID 允许非唯一（`groupmod -o`），以兼容 macOS 上 GID 20（`staff`）等可能与容器内已有组冲突的情况。

### 5.4.4 禁止使用 docker run --user

容器**不支持**通过 `docker run --user <uid>:<gid>` 指定任意 UID 启动。`stage2-hook.sh` 和 `main-wrapper.sh` 均包含检测逻辑，若发现容器以非 root、非 hermes 的任意 UID 启动，会直接报错退出：

```
[stage2] ERROR: container started with --user 1000 (an arbitrary, non-hermes UID).

This is not supported under the s6-overlay image. The container bootstrap
(UID remap, data-volume ownership, config seeding) needs to start as root...
```

原因是 s6-overlay 的引导过程（UID 重映射、数据卷 chown、配置初始化）需要 root 权限。正确方式是以 root 启动（镜像默认），通过 `HERMES_UID`/`HERMES_GID` 传递目标 UID/GID。

### 5.4.5 数据卷权限修复

`stage2-hook.sh` 在每次启动时执行以下权限修复（以 root 身份）：

1. **顶层目录**：若 `/opt/data` 的所有者不是 hermes，对目录本身执行 `chown hermes:hermes`（不递归，避免破坏主机挂载的无关文件）；
2. **hermes 专属子目录**：对 `cron/`、`sessions/`、`logs/`、`profiles/`、`skills/`、`lazy-packages/` 等执行递归 chown（这些目录由 hermes 独占管理）；
3. **顶层状态文件**：对 `auth.json`、`state.db`、`gateway.lock`、`.env`、`config.yaml` 等关键文件单独 chown；
4. **符号链接防护**：拒绝通过符号链接路径执行 chown，防止 TOCTOU 攻击（CWE-59/367）；
5. **每次启动必修复**：`profiles/`、`cron/`、`platforms/pairing/`、`logs/gateways/` 以及 `config.yaml`、`.env` 的权限在每次启动时都会重新校正，以自愈 `docker exec`（默认以 root 执行）可能写入的 root 所有文件。

---

## 5.5 s6-overlay 进程管理说明

### 5.5.1 为什么使用 s6-overlay

容器使用 [s6-overlay](https://github.com/just-containers/s6-overlay) v3.2.3.0 作为 PID 1 进程管理器，替代了早期版本的 tini。s6-overlay 提供：

- **僵尸进程回收**：PID 1（`s6-svscan`）在 `SIGCHLD` 时非阻塞地回收孤儿进程（MCP stdio 子进程、git、bun 等）；
- **服务监管**：自动重启崩溃的服务（dashboard、per-profile 网关）；
- **初始化脚本**：在服务启动前执行 `cont-init.d` 脚本完成引导；
- **优雅关闭**：容器停止时按依赖关系逆序关闭服务。

### 5.5.2 启动流程

容器入口点为 `entrypoint-dispatch.sh`，它根据是否拥有 PID 1 选择不同路径：

```
容器启动
  │
  ├─ PID == 1 ?（正常 Docker/Podman）
  │    │
  │    └─ exec /init（s6-overlay 的 s6-svscan）
  │         │
  │         ├─ 运行 /etc/cont-init.d/ 脚本（按文件名顺序）
  │         │    ├─ 01-hermes-setup → stage2-hook.sh
  │         │    │    （UID/GID 重映射、卷 chown、配置初始化、技能同步）
  │         │    ├─ 015-supervise-perms
  │         │    └─ 02-reconcile-profiles
  │         │         （重建 per-profile 网关 s6 服务槽位）
  │         │
  │         ├─ 启动 s6-rc 用户服务
  │         │    ├─ main-hermes（占位服务，sleep infinity）
  │         │    └─ dashboard（若 HERMES_DASHBOARD 为真则启动）
  │         │
  │         └─ exec main-wrapper.sh（作为 /init 的"主程序"）
  │              └─ 执行 Docker CMD（如 gateway run、dashboard、chat 等）
  │
  └─ PID != 1 ?（Fly Machines、docker run --init、某些调度器）
       │
       └─ 直接运行 stage2-hook.sh（引导）
          └─ exec main-wrapper.sh（执行 CMD，无监管树）
```

### 5.5.3 cont-init.d 初始化脚本

| 脚本 | 执行顺序 | 职责 |
|---|---|---|
| `01-hermes-setup` | 1 | 调用 `stage2-hook.sh`：UID/GID 重映射、数据卷 chown、配置文件种子、技能同步、Chromium 路径发现 |
| `015-supervise-perms` | 2 | 监管目录权限设置 |
| `02-reconcile-profiles` | 3 | 容器重启后从 `/opt/data/profiles/` 重建 per-profile 网关的 s6 服务槽位（`/run/service/` 是 tmpfs，重启后清空） |

### 5.5.4 s6-rc 用户服务

静态声明的服务位于 `/etc/s6-overlay/s6-rc.d/`：

**main-hermes 服务**：
- 当前为占位服务（`exec sleep infinity`）；
- 存在的原因是 s6-rc 的 "user" bundle 至少需要一个用户服务才有效；
- 用户实际的 CMD（如 `gateway run`）通过 `/init` 的"主程序"机制运行，而非作为 s6 监管服务，这样可以保留容器退出码语义和交互式 TTY 支持。

**dashboard 服务**：
- 由环境变量 `HERMES_DASHBOARD` 控制（接受 `1`/`true`/`yes` 等真值）；
- 若 `HERMES_DASHBOARD` 未设置，`run` 脚本立即退出，`finish` 脚本返回 `125`（s6 的"永久失败，不重启"标记），服务槽位显示为 down；
- 若 `HERMES_DASHBOARD` 为真，以 `hermes` 用户运行 `hermes dashboard --host 0.0.0.0 --port 9119 --no-open`，崩溃后自动重启。

> **注意**：`docker-compose.yml` 中的 dashboard 服务通过 `command: ["dashboard", "--host", "127.0.0.1", "--no-open"]` 直接启动 dashboard 子命令（走主程序路径），而非通过 `HERMES_DASHBOARD` 环境变量启用 s6 监管服务。两种方式均可，但 Compose 方式将 dashboard 作为独立容器运行。

### 5.5.5 权限降级机制

每个监管服务的 `run` 脚本以及 `main-wrapper.sh` 都通过 `s6-setuidgid hermes` 降级到非 root 用户运行：

- 容器以 root 启动（引导需要 root）；
- `stage2-hook.sh` 完成 UID 重映射和 chown 后，服务通过 `s6-setuidgid hermes` 降级；
- `main-wrapper.sh` 中的 `drop()` 函数负责对用户命令执行权限降级；
- `hermes-exec-shim.sh`（位于 `/opt/hermes/bin/hermes`）确保 `docker exec` 进入的命令也自动降级到 hermes 用户，防止写入 root 所有的文件。

设置 `HERMES_DOCKER_EXEC_AS_ROOT=1` 可临时保留 root 权限（仅用于诊断）。

### 5.5.6 向后兼容垫片

`docker/tini-shim.sh` 安装为 `/usr/bin/tini`，为仍引用旧 tini 入口点的编排模板（如 Hostinger 的 Hermes WebUI 目录、旧版 NAS Compose 项目）提供向后兼容。它会剥离 tini 的 CLI 参数（如 `-g`），然后转发到 `/init`，避免启动循环。

`docker/entrypoint.sh` 也保留为弃用垫片，会输出警告并转发到 `stage2-hook.sh`。

---

## 5.6 常用 docker compose 命令

### 5.6.1 启动服务

```bash
# 构建（首次）并后台启动
HERMES_UID=$(id -u) HERMES_GID=$(id -g) docker compose up -d

# 仅启动 gateway
docker compose up -d gateway

# 前台启动（查看实时日志，Ctrl+C 停止）
docker compose up

# 强制重新构建后启动
docker compose up -d --build
```

### 5.6.2 查看日志

```bash
# 查看所有服务的实时日志
docker compose logs -f

# 仅查看 gateway 日志
docker compose logs -f gateway

# 仅查看 dashboard 日志
docker compose logs -f dashboard

# 查看最近 100 行日志
docker compose logs --tail=100 gateway

# 查看带时间戳的日志
docker compose logs -f --timestamps
```

### 5.6.3 进入容器执行命令

```bash
# 在 gateway 容器中启动交互式 shell
docker compose exec gateway bash

# 在 gateway 容器中运行 hermes 命令
docker compose exec gateway hermes status
docker compose exec gateway hermes doctor
docker compose exec gateway hermes login

# 以 hermes 用户执行（默认已通过 shim 自动降级，显式指定更安全）
docker compose exec --user hermes gateway hermes chat -q "hello"

# 在 dashboard 容器中执行
docker compose exec dashboard bash
```

> `docker compose exec` 默认以 root 进入容器，但 `/opt/hermes/bin/hermes`（PATH 最前端）的 `hermes-exec-shim.sh` 会自动将 `hermes` 命令降级到 hermes 用户执行，确保写入 `/opt/data` 的文件所有权正确。

### 5.6.4 停止与移除

```bash
# 停止服务（保留容器和数据卷）
docker compose stop

# 停止并移除容器（数据卷 ~/.hermes 不受影响）
docker compose down

# 停止并移除容器 + 镜像（谨慎使用）
docker compose down --rmi local

# 停止并移除容器 + 匿名卷（不影响绑定挂载的 ~/.hermes）
docker compose down -v
```

### 5.6.5 重启服务

```bash
# 重启所有服务
docker compose restart

# 仅重启 gateway
docker compose restart gateway

# 仅重启 dashboard
docker compose restart dashboard
```

### 5.6.6 其他常用命令

```bash
# 查看服务状态
docker compose ps

# 查看服务使用的镜像
docker compose images

# 拉取最新镜像（使用预构建镜像时）
docker compose pull

# 验证 Compose 文件语法
docker compose config

# 暂停/恢复服务（不停止进程）
docker compose pause
docker compose unpause
```

### 5.6.7 直接使用 docker run

若不使用 Compose，可直接用 `docker run`：

```bash
# 构建镜像后运行 gateway
docker run -d \
  --name hermes \
  --restart unless-stopped \
  --network host \
  -e HERMES_UID=$(id -u) \
  -e HERMES_GID=$(id -g) \
  -v ~/.hermes:/opt/data \
  hermes-agent:latest gateway run

# 运行交互式聊天
docker run --rm -it \
  --network host \
  -e HERMES_UID=$(id -u) \
  -e HERMES_GID=$(id -g) \
  -v ~/.hermes:/opt/data \
  hermes-agent:latest
```

---

## 5.7 环境变量传递方法

### 5.7.1 通过 docker-compose.yml 的 environment 字段

直接在 Compose 文件中声明：

```yaml
environment:
  - HERMES_UID=${HERMES_UID:-10000}
  - HERMES_GID=${HERMES_GID:-10000}
  - FIREWORKS_API_KEY=${FIREWORKS_API_KEY}
```

`${VARIABLE:-default}` 语法表示：若主机环境中未设置 `VARIABLE`，则使用 `default`。

### 5.7.2 通过 .env 文件

在 `docker-compose.yml` 同目录创建 `.env` 文件，Docker Compose 会自动加载：

```bash
# .env 文件
HERMES_UID=1000
HERMES_GID=1000
FIREWORKS_API_KEY=fw_xxxxxxxxxxxx
OPENROUTER_API_KEY=sk-or-xxxxxxxxxxxx
TEAMS_CLIENT_ID=your-client-id
TEAMS_CLIENT_SECRET=your-client-secret
```

然后在 `docker-compose.yml` 中通过 `${VARIABLE_NAME}` 引用。

> **注意**：`.env` 文件中的变量会替换 Compose 文件中的 `${...}` 占位符，但**不会自动**传递到容器内部——必须在 `environment` 字段中显式声明每个需要传入容器的变量。

### 5.7.3 通过命令行 -e 传递

```bash
# docker run
docker run -e FIREWORKS_API_KEY=fw_xxx hermes-agent

# docker compose
HERMES_UID=1000 FIREWORKS_API_KEY=fw_xxx docker compose up -d
```

### 5.7.4 通过数据卷中的 .env 文件

容器启动时，`stage2-hook.sh` 会自动将镜像内的 `.env.example` 复制到 `/opt/data/.env`（即主机 `~/.hermes/.env`）。Hermes 运行时通过 `python-dotenv` 自动加载该文件。

这是传递 API 密钥等敏感配置的**推荐方式**：

```bash
# 首次启动后编辑
nano ~/.hermes/.env

# 填入 API 密钥
# FIREWORKS_API_KEY=fw_xxxxxxxxxxxx
# OPENROUTER_API_KEY=sk-or-xxxxxxxxxxxx

# 重启使配置生效
docker compose restart
```

`~/.hermes/.env` 的权限在每次容器启动时自动设为 `0600`（仅所有者可读写），防止密钥泄露。

### 5.7.5 容器内置环境变量

`Dockerfile` 在构建时设置了以下容器内置环境变量：

| 变量 | 值 | 说明 |
|---|---|---|
| `PYTHONUNBUFFERED` | `1` | Python stdout 不缓冲，日志实时输出 |
| `PYTHONDONTWRITEBYTECODE` | `1` | 不写 `.pyc` 文件（安装树只读） |
| `PLAYWRIGHT_BROWSERS_PATH` | `/opt/hermes/.playwright` | Playwright 浏览器路径（在安装树内，不受数据卷覆盖影响） |
| `HERMES_HOME` | `/opt/data` | Hermes 数据目录 |
| `HERMES_WRITE_SAFE_ROOT` | `/opt/data` | 文件写入安全根目录 |
| `HERMES_DISABLE_LAZY_INSTALLS` | `1` | 禁用向只读 venv 的懒安装 |
| `HERMES_LAZY_INSTALL_TARGET` | `/opt/data/lazy-packages` | 可选后端 SDK 安装目标（数据卷上，可写且持久） |
| `HERMES_WEB_DIST` | `/opt/hermes/hermes_cli/web_dist` | Dashboard 前端构建产物路径 |
| `HERMES_TUI_DIR` | `/opt/hermes/ui-tui` | TUI 预构建 bundle 路径 |
| `npm_config_install_links` | `false` | npm `file:` 依赖使用符号链接而非拷贝 |
| `PATH` | `/opt/hermes/bin:/opt/hermes/.venv/bin:/opt/data/.local/bin:...` | 包含 venv 和 hermes 可执行文件 |

### 5.7.6 引导专用环境变量

以下环境变量仅在容器首次启动（数据卷为空）时生效：

| 变量 | 说明 |
|---|---|
| `HERMES_AUTH_JSON_BOOTSTRAP` | 首次启动时写入 `auth.json` 的 Nous 认证 JSON（不覆盖已有文件） |
| `HERMES_AUTH_JSON_REBOOTSTRAP` | 当已有 session 处于 terminal 失效状态时，替换 Nous 认证条目 |
| `HERMES_GATEWAY_BOOTSTRAP_STATE` | 设为 `running` 时，首次启动自动将网关设为运行状态 |
| `HERMES_SKIP_CONFIG_MIGRATION` | 设为 `1` 跳过配置架构迁移 |

---

## 5.8 Dashboard 安全提示

### 5.8.1 默认仅绑定 127.0.0.1

`docker-compose.yml` 中 dashboard 的启动命令为：

```yaml
command: ["dashboard", "--host", "127.0.0.1", "--no-open"]
```

Dashboard **仅监听本地回环地址 `127.0.0.1`**，绑定端口为默认的 `9119`。这意味着：

- 主机本身上的浏览器可通过 `http://127.0.0.1:9119` 访问；
- 局域网或互联网上的其他设备**无法**直接访问；
- Dashboard 存储 API 密钥，未经认证暴露到网络极不安全。

### 5.8.2 远程访问方式

若需要从远程访问 Dashboard，**不要**修改 `--host` 为 `0.0.0.0` 并直接暴露端口。推荐以下安全方式：

**方式一：SSH 隧道（推荐）**

```bash
# 在远程机器上执行，将本地 9119 转发到服务器的 9119
ssh -L 9119:localhost:9119 user@your-server

# 然后在远程机器的浏览器中访问
# http://127.0.0.1:9119
```

**方式二：反向代理 + 认证**

在反向代理（Nginx、Caddy、Traefik）后面部署 Dashboard，由代理层添加 TLS 和认证（Basic Auth、OAuth 等），代理到 `127.0.0.1:9119`。

### 5.8.3 非回环绑定的认证要求

若确实需要将 Dashboard 绑定到非回环地址（如 `0.0.0.0`），Dashboard 的认证网关会自动启用，**必须**配置以下认证提供者之一：

| 认证方式 | 环境变量 | 说明 |
|---|---|---|
| 密码认证 | `HERMES_DASHBOARD_BASIC_AUTH_USERNAME` + `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD` | 内置 Basic Auth 提供者，无需外部 IDP |
| OAuth | `HERMES_DASHBOARD_OAUTH_CLIENT_ID` | 内置 Nous OAuth 提供者 |

> **重要**：`HERMES_DASHBOARD_INSECURE=1` 已不再能禁用认证网关（2026 年 6 月安全加固后，未认证的公开 Dashboard 曾被用于 MCP 配置持久化攻击）。该变量仍会被接受但会被忽略，并输出迁移警告。

### 5.8.4 Windows Docker Desktop 的端口绑定

Windows Compose 文件中端口映射为：

```yaml
ports:
  - "127.0.0.1:9119:9119"
```

`127.0.0.1:9119:9119` 的格式表示：仅将主机的 `127.0.0.1:9119` 映射到容器的 `9119`。即使容器内 Dashboard 绑定 `0.0.0.0`（Docker Desktop NAT 网络要求），主机层面仍然只接受本地连接。

### 5.8.5 API 服务器安全

若启用 OpenAI 兼容 API 服务器（`API_SERVER_HOST=0.0.0.0`），**必须**同时设置 `API_SERVER_KEY`。在面向互联网的主机上，还应配合防火墙规则和反向代理使用。

---

## 5.9 镜像分层说明

`Dockerfile` 采用多阶段构建和精心排序的分层策略，以最大化 Docker 构建缓存命中率。以下按 `Dockerfile` 中的出现顺序说明各层。

### 5.9.1 多阶段构建概览

| 阶段 | 基础镜像 | 用途 | 是否进入最终镜像 |
|---|---|---|---|
| `sqlite_build` | `debian:13.4` | 编译修复版 SQLite 3.53.4 | 仅复制 `.so` 文件 |
| `uv_source` | `ghcr.io/astral-sh/uv:0.11.6-python3.13-trixie` | 提供预编译的 `uv`/`uvx` 二进制 | 仅复制二进制 |
| `node_source` | `node:26-bookworm-slim` | 提供 Node.js 26 和 npm | 仅复制 node + npm |
| 最终阶段 | `debian:13.4` | 运行时镜像 | 是 |

### 5.9.2 最终镜像分层详解

**第 1 层：SQLite 编译（sqlite_build 阶段）**

Debian 13 (trixie) 自带的 SQLite 3.46.1 存在上游 WAL-reset 损坏 bug（SQLite 官方公告）。镜像从源码编译 SQLite 3.53.4（`SQLITE_AUTOCONF_VERSION=3530400`），启用以下编译选项：

- FTS3/FTS4/FTS5（全文搜索，含 trigram 分词器）
- RTREE、GEOPOLY（空间索引）
- COLUMN_METADATA、UNLOCK_NOTIFY
- DBSTAT_VTAB、DBPAGE_VTAB
- MATH_FUNCTIONS、PREUPDATE_HOOK、SESSION
- SECURE_DELETE、THREADSAFE=1
- MAX_VARIABLE_NUMBER=250000

编译后的 `libsqlite3.so.3.53.4` 被复制到最终镜像的 `/usr/local/lib/`，并通过 `ldconfig` 替换系统自带版本。构建时还执行了自测（版本检查 + FTS5 trigram 查询测试）。

**第 2 层：uv 二进制**

从 `ghcr.io/astral-sh/uv:0.11.6-python3.13-trixie` 镜像复制 `uv` 和 `uvx` 到 `/usr/local/bin/`。uv 是 Rust 编写的高性能 Python 包管理器，镜像使用其 Python 3.13 变体（最终镜像系统 Python 为 Debian 自带的 Python 3，uv 会创建独立的 3.13 venv）。

**第 3 层：Node.js 26**

从 `node:26-bookworm-slim` 复制：
- `/usr/local/bin/node` → 最终镜像
- `/usr/local/lib/node_modules/npm` → 最终镜像
- 重新创建 `npm` 和 `npx` 符号链接

使用 Bookworm 基础镜像是因为其 glibc 2.36 编译的二进制可在 Debian 13（glibc 2.41）上兼容运行。不包含 Corepack（Node 26 已上游移除）。

**第 4 层：系统依赖**

安装运行时所需的系统包（单条 `apt-get install`，清理 APT 缓存）：

| 包 | 用途 |
|---|---|
| `python3`、`python-is-python3` | 系统 Python |
| `gcc`、`g++`、`make`、`cmake` | 原生扩展编译（部分 Python 包需要） |
| `python3-dev`、`python3-venv`、`libffi-dev` | Python 开发头文件和 venv |
| `libolm-dev` | Matrix E2EE 依赖 |
| `libatomic1` | 原子操作库 |
| `ripgrep` | 代码搜索工具 |
| `ffmpeg` | 音视频处理（TTS/STT） |
| `git`、`openssh-client` | Git 操作和 SSH |
| `docker-cli` | Docker 终端后端（兄弟容器控制） |
| `procps` | 进程查看工具 |
| `curl`、`ca-certificates` | 网络请求和证书 |
| `iputils-ping` | 网络诊断 |
| `xz-utils` | s6-overlay tarball 解压 |

**第 5 层：s6-overlay**

下载并安装 s6-overlay v3.2.3.0，包含三个 tarball：

- `s6-overlay-noarch.tar.xz`（架构无关）
- `s6-overlay-<arch>.tar.xz`（`x86_64` 或 `aarch64`，根据 `TARGETARCH` 选择）
- `s6-overlay-symlinks-noarch.tar.xz`（符号链接）

所有 tarball 均通过 SHA256 校验。使用 `curl --retry 3` 而非 `ADD` 指令下载，以避免 CDN 瞬时故障导致 15–45 分钟的构建失败。

**第 6 层：npm 依赖安装**

利用分层缓存，先只复制包清单文件：

- `package.json`、`package-lock.json`（根目录）
- `web/package.json`
- `ui-tui/package.json`
- `ui-tui/packages/hermes-ink/`（完整目录，因被 `file:` workspace 依赖引用）
- `apps/shared/`（完整目录，因被 web 引用为 `file:` 依赖）

然后执行 `npm install --prefer-offline --no-audit` 和 `npx playwright install --with-deps chromium --only-shell`（带 3 次重试）。此层仅在 lockfile 变化时重新执行。

此外，Photon iMessage sidecar 的 Node 依赖（`plugins/platforms/photon/sidecar/`）单独一层安装，因为其安装树在运行时不可变（`/opt/hermes` 只读）。

**第 7 层：Python 依赖安装**

先只复制 `pyproject.toml` 和 `uv.lock`，创建空 `README.md` 占位文件（因 `.dockerignore` 排除了 `*.md`），然后执行：

```bash
uv sync --frozen --no-install-project \
  --extra all --extra messaging --extra otlp \
  --extra anthropic --extra bedrock --extra azure-identity \
  --extra hindsight --extra matrix
```

各 extra 的选择理由：

| Extra | 理由 |
|---|---|
| `all` | 策划的生产功能子集（CLI、MCP、Web、Google 等） |
| `messaging` | Telegram + Discord + Slack 消息平台 |
| `otlp` | OpenTelemetry 监控导出 SDK |
| `anthropic`、`bedrock`、`azure-identity` | 容器环境常无法访问 PyPI 懒加载，预置提供商 SDK |
| `hindsight` | 记忆提供者，懒安装路径在镜像更新时丢失 |
| `matrix` | `python-olm` 需从源码编译，预置原生 libolm 和工具链 |

**不使用 `--all-extras`**，因为那会拉入 `[rl]`（torch 等大体积包）、`[yc-bench]`、`[termux-all]` 等不适合生产容器的依赖。

**第 8 层：前端构建**

独立于 Python 源码的构建层，先复制前端源码树（`web/`、`ui-tui/`、`apps/shared/`），然后：

```bash
cd web && npm run build       # Vite + React Dashboard 构建
cd ../ui-tui && npm run build # esbuild 打包 TUI 入口
```

此层仅在前端源码变化时失效，Python-only 的提交不会触发前端重建。

**第 9 层：源码复制**

使用 `COPY --link --chmod=a+rX,go-w . .` 复制全部源码：
- `--link`：将此层与父层解耦，优化缓存；
- `--chmod=a+rX,go-w`：在复制时即设置只读权限（非 root 用户可读可遍历但不可写），避免后续对约 3 万个文件执行单独的 `chmod -R`（amd64 上节省 21 秒，arm64 上节省 222 秒）；
- `.dockerignore` 排除的文件不会进入此层。

随后执行 `uv pip install --no-cache-dir --no-deps -e "."` 创建对自身的可编辑安装链接。

**第 10 层：运行时配置与 s6 服务接线**

- 安装 `hermes-exec-shim.sh` 到 `/opt/hermes/bin/hermes`；
- 写入 `/opt/hermes/.install_method`（内容为 `docker`）；
- 复制 s6-rc 服务定义到 `/etc/s6-overlay/s6-rc.d/`；
- 创建 cont-init.d 脚本（`01-hermes-setup`、`015-supervise-perms`、`02-reconcile-profiles`）；
- 设置运行时环境变量（`HERMES_HOME`、`PATH` 等）；
- 声明 `VOLUME ["/opt/data"]`；
- 设置 `ENTRYPOINT` 和 `CMD`。

### 5.9.3 分层缓存策略总结

```
源码变更 → 仅失效第 9-10 层（秒级）
前端变更 → 失效第 8-10 层
Python 依赖变更（pyproject.toml/uv.lock）→ 失效第 7-10 层（约 4-5 分钟）
npm 依赖变更（package-lock.json）→ 失效第 6-10 层
系统依赖变更 → 失效第 4-10 层
基础镜像/编译工具链变更 → 全部重建
```

---

## 5.10 网络模式说明

### 5.10.1 host 网络模式

`docker-compose.yml` 中两个服务均使用：

```yaml
network_mode: host
```

**host 网络模式**下，容器共享主机的网络命名空间，不创建独立的网络接口、不进行 NAT 转换、不需要端口映射。容器内进程监听的端口直接在主机上可用。

选择 host 模式的原因：

1. **网关需要监听多个端口**：Hermes 网关可能同时监听消息平台 webhook 端口（如 Teams 的 3978、Telegram webhook 的 8443）、Dashboard 的 9119、API 服务器等，host 模式避免了逐个端口映射的繁琐；
2. **性能**：host 模式无 Docker 代理层 NAT 开销，网络吞吐量更高、延迟更低；
3. **本地服务发现**：容器内进程可直接访问主机上运行的其他服务（如本地 Ollama、本地数据库），通过 `localhost` 即可；
4. **mDNS/广播**：某些消息平台或设备发现功能依赖广播/mDNS，桥接网络下可能不工作。

### 5.10.2 host 模式下的端口

容器内服务监听的端口直接绑定在主机网络接口上：

| 服务 | 默认端口 | 绑定地址 | 说明 |
|---|---|---|---|
| Dashboard | `9119` | `127.0.0.1`（Compose 配置） | Web 管理界面 |
| API 服务器 | （需启用） | `127.0.0.1`（默认） | OpenAI 兼容 API |
| Teams webhook | `3978` | （需配置） | Microsoft Teams |
| Telegram webhook | `8443` | （需配置） | Telegram webhook 模式 |

> 即使在 host 模式下，Dashboard 仍然只绑定 `127.0.0.1`（由 `--host 127.0.0.1` 参数控制），host 网络模式不会改变应用层的绑定地址。

### 5.10.3 平台兼容性

| 平台 | host 网络支持 | 说明 |
|---|---|---|
| Linux | ✅ 完全支持 | 原生网络命名空间共享 |
| Windows Docker Desktop | ❌ 不支持 | 使用 `docker-compose.windows.yml` 的端口映射模式 |
| macOS Docker Desktop | ⚠️ 有限支持 | Docker Desktop for Mac 通过 VM 实现，host 模式实际连接到 VM 内部网络而非主机，需使用 `host.docker.internal` 访问主机服务 |
| Rootless Podman | ✅ 支持 | 使用 `--network host` |

### 5.10.4 Windows Docker Desktop 的替代方案

在 Windows 上，`docker-compose.windows.yml` 使用桥接网络 + 端口映射：

```yaml
ports:
  - "127.0.0.1:9119:9119"
```

这等价于在 Linux 上使用：

```yaml
ports:
  - "127.0.0.1:9119:9119"
```

而非 host 模式。若需要在 Linux 上使用桥接网络而非 host 模式，可参考 Windows Compose 文件的方式，手动映射所需端口。

### 5.10.5 容器间通信

在 `docker-compose.yml` 中，`gateway` 和 `dashboard` 是两个独立容器，但由于使用 `network_mode: host`，它们通过主机的 `localhost` 互相访问，无需 Docker 内部 DNS 或容器网络。两个容器共享同一个数据卷（`~/.hermes:/opt/data`），通过文件系统协调状态（如 `gateway_state.json`）。

### 5.10.6 访问主机服务

在 host 网络模式下，容器内通过 `localhost` / `127.0.0.1` 即可访问主机上运行的服务（如本地 Ollama `http://localhost:11434`）。

在桥接网络模式下（如 Windows），需要使用特殊的 DNS 名称 `host.docker.internal` 来访问主机：

```bash
# 在容器内访问主机上的 Ollama
curl http://host.docker.internal:11434
```

---

## 5.11 完整部署流程示例

### 5.11.1 Linux 快速部署

```bash
# 1. 克隆仓库
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent

# 2. 构建镜像
DOCKER_BUILDKIT=1 docker build -t hermes-agent:latest .

# 3. 创建数据目录（首次）
mkdir -p ~/.hermes

# 4. 启动服务（使用当前用户的 UID/GID）
HERMES_UID=$(id -u) HERMES_GID=$(id -g) docker compose up -d

# 5. 查看日志确认启动成功
docker compose logs -f gateway

# 6. 配置 API 密钥
nano ~/.hermes/.env

# 7. 重启使配置生效
docker compose restart

# 8. 访问 Dashboard
# 浏览器打开 http://127.0.0.1:9119
```

### 5.11.2 使用预构建镜像部署

若不从源码构建，可修改 `docker-compose.yml` 将 `build: .` 替换为 `image: nousresearch/hermes-agent:latest`，然后：

```bash
docker compose pull
HERMES_UID=$(id -u) HERMES_GID=$(id -g) docker compose up -d
```

### 5.11.3 验证清单

部署完成后，逐项验证：

- [ ] `docker compose ps` 显示两个服务均为 `running` 状态
- [ ] `docker compose logs gateway` 无致命错误，显示网关启动成功
- [ ] `docker compose exec gateway hermes --version` 正常输出版本号
- [ ] `docker compose exec gateway hermes doctor` 无严重错误
- [ ] `docker compose exec gateway hermes status` 显示配置状态
- [ ] 浏览器访问 `http://127.0.0.1:9119` 能打开 Dashboard
- [ ] `ls -la ~/.hermes/` 显示文件所有者为当前主机用户（非 `10000`）
- [ ] `~/.hermes/.env` 权限为 `-rw-------`（0600）
- [ ] `docker compose exec gateway id hermes` 显示的 UID 与主机用户 UID 一致

---

## 5.12 小结

Docker 容器化部署为 Hermes Agent 提供了隔离、可复现、易于运维的运行方式，核心要点如下：

- **镜像构建**：基于 Debian 13 的多阶段构建，编译修复版 SQLite、引入 uv 和 Node.js 26、安装 s6-overlay、分层缓存 Python/Node 依赖和前端产物，支持 amd64/arm64 多架构。
- **Compose 服务**：`gateway`（主网关）和 `dashboard`（Web 界面）两个服务共享数据卷，Linux 使用 host 网络，Windows 使用端口映射。
- **数据持久化**：`~/.hermes:/opt/data` 是唯一需要持久化的卷，包含全部配置、认证、会话和日志；`/opt/hermes` 安装树只读不可变。
- **权限模型**：以 root 启动执行引导，通过 `HERMES_UID`/`HERMES_GID`（或 `PUID`/`PGID`）重映射内部 hermes 用户，服务降级到非 root 运行；禁止使用 `--user` 任意 UID。
- **进程管理**：s6-overlay 作为 PID 1，提供僵尸回收、服务监管、初始化脚本和优雅关闭；`entrypoint-dispatch.sh` 兼容非 PID 1 运行时。
- **Dashboard 安全**：默认仅绑定 `127.0.0.1`，远程访问应使用 SSH 隧道或带认证的反向代理；非回环绑定必须配置认证提供者。
- **环境变量**：通过 Compose `environment`、`.env` 文件、命令行 `-e` 或数据卷中的 `~/.hermes/.env` 传递，敏感配置推荐使用后者（权限自动设为 0600）。
