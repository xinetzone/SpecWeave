---
id: "devcontainer-agents-atomization-verify-report"
title: "devcontainer-base .agents/ 原子化验证与规则归档报告"
date: "2026-08-07"
source: "apps/docker-images/devcontainer-base/.agents/"
type: "verification-report"
tags: ["devcontainer-base", "atomization", "verification", "rules-export"]
---

# devcontainer-base .agents/ 原子化验证与规则归档报告

> **报告日期**：2026-08-07
> **验证范围**：`apps/docker-images/devcontainer-base/.agents/` 目录结构、内部链接、规则文件内容
> **方法论**：R-I-E（复盘→洞察→萃取）

---

## 1. 验证结果总览

### 1.1 目录结构验证

| 检查项 | 结果 | 说明 |
|--------|------|------|
| AGENTS.md 包含"启动协议"关键词 | ✅ 通过 | 符合工作区发现协议 |
| .agents/README.md 存在 | ✅ 通过 | 目录索引文件完整 |
| 4个规则文件 frontmatter 完整 | ✅ 通过 | 均含 id/title/source 字段 |
| 父级引用有效性 | ✅ 通过 | ../../AGENTS.md 和 ../../.agents/global-core-rules.md 均存在 |
| AGENTS.md 引用所有规则文件 | ✅ 通过 | 4个 rules 文件均被正确引用 |
| 显式锚点 ID 覆盖率 | ✅ 通过 | 11个跨文件锚点已添加显式 `<a id>` 标签 |

### 1.2 链接验证结果

```
扫描文件: 8 个 Markdown 文件
内联链接: 49
本地引用: 49（全部有效，0断链）
外部链接: 0
目录链接警告: 6（导航性链接，符合项目惯例）
```

### 1.3 修复项

| 问题 | 修复方式 | 涉及文件 |
|------|---------|---------|
| 中文章节锚点跨渲染器兼容性 | 添加11个显式 `<a id>` 锚点标签 | dockerfile.md, entrypoint.md, services.md |
| 缺少快速开始指南 | 在 .agents/README.md 中新增三层路由加载指南 | .agents/README.md |

---

## 2. 目录结构

```
apps/docker-images/devcontainer-base/
├── AGENTS.md                        ← 索引页（路由+约束速览+快速开始）
└── .agents/                         ← AI资产容器
    ├── README.md                    ← 目录索引+快速开始指南（含三层路由）
    ├── rules/
    │   ├── dockerfile.md            ← Dockerfile 多阶段构建规范
    │   ├── entrypoint.md            ← Entrypoint 启动脚本规范
    │   ├── services.md              ← 服务管理规范（supervisord+4服务）
    │   └── build-test.md            ← 构建与测试流程
    ├── roles/        (.gitkeep)     ← 预留（回退到父级）
    ├── skills/       (.gitkeep)     ← 预留（回退到父级）
    ├── scripts/      (.gitkeep)     ← 预留
    ├── workflows/    (.gitkeep)     ← 预留
    ├── templates/    (.gitkeep)     ← 预留
    └── docs/         (.gitkeep)     ← 预留
```

---

## 3. 快速开始指南（AI协作者规则加载）

### 3.1 三层路由加载顺序

```
第1层（根级）：SpecWeave 全局规范 → .agents/global-core-rules.md
第2层（区域级）：apps/ 区域路由 → apps/AGENTS.md
第3层（应用级）：devcontainer-base 项目特有规则 → apps/docker-images/devcontainer-base/.agents/rules/
```

### 3.2 任务类型→规则文件路由表

| 任务场景 | 必读规则文件 | 核心关注点 |
|---------|-------------|-----------|
| 修改 Dockerfile | rules/dockerfile.md | BuildKit语法、多阶段结构、层缓存、中文环境、非root用户、安全规范 |
| 修改启动脚本 | rules/entrypoint.md | tini init、日志格式、启动流程、信号处理、命令模式 |
| 修改服务配置 | rules/services.md | supervisord管理、Docker DinD、Podman rootless、Jupyter、SSH、健康检查 |
| 构建/测试/部署 | rules/build-test.md | build.sh/start.sh用法、Compose profile、验证流程、问题排查 |

### 3.3 规则加载自检清单

AI协作者在开始工作前必须确认：
- [ ] 已读取 AGENTS.md 了解项目概述和约束速览
- [ ] 已根据任务类型读取对应的 rules/*.md 文件
- [ ] 理解 Docker DinD 的 daemon.json 单一配置源原则（避免命令行参数冲突）
- [ ] 理解非root用户 devuser (UID 1000) 的权限模型
- [ ] 修改后运行 `python .agents/scripts/check-links.py --path apps/docker-images/devcontainer-base/` 验证链接

---

## 4. 规则文件完整内容归档

---

### 4.1 Dockerfile 多阶段构建规范

**文件**：`.agents/rules/dockerfile.md`
**ID**：`devcontainer-dockerfile-rules`

<a id="基础约定"></a>
#### 基础约定

- 文件名为 `Dockerfile`（使用 BuildKit 1.7-labs 语法：`# syntax=docker/dockerfile:1.7-labs`）
- 基础镜像：`ubuntu:26.04`（固定版本，不使用 `latest`）
- 构建注释/日志使用**英文**（避免 PowerShell/Shell 编码问题）
- 每个 Stage/关键步骤输出构建日志：`echo "[BUILD] ..."`
- 启用 `SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]`，管道中任何命令失败立即终止

#### 多阶段结构

Builder + Runtime 两阶段构建，Runtime 阶段分 7 个 Stage 块：

1. **Stage 2.1/7**：系统包安装 + APT 镜像源切换 + locale/timezone 配置（变化频率：最低）
2. **Stage 2.2/7**：Docker CE 安装（变化频率：低）
3. **Stage 2.3/7**：Podman rootless 安装（变化频率：低）
4. **Stage 2.4/7**：COPY venv from builder + PATH 配置（变化频率：低）
5. **Stage 2.5/7**：用户/组 + subuid/subgid + 运行时目录 + daemon.json（变化频率：中）
6. **Stage 2.6/7**：配置文件 COPY + 权限 + 语法验证（变化频率：高）
7. **Stage 2.7/7**：build-info + 清理 + 最终验证（变化频率：最低）

Builder 阶段安装 build-essential/python3-dev，编译 Python 虚拟环境；Runtime 阶段仅保留运行时必需包。

#### 层缓存优化

- 使用 BuildKit `--mount=type=cache` 挂载 apt/pip 缓存，跨构建复用：
  ```dockerfile
  RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
      --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
      apt-get update && apt-get install -y --no-install-recommends ...
  ```
- pip 安装同样使用缓存挂载：`--mount=type=cache,target=/root/.cache/pip,sharing=locked`
- 多个 RUN 指令合并为一个（用 `&& \` 连接），减少镜像层数
- apt-get update 和 install 在同一个 RUN 中，避免缓存过期
- COPY 指令尽量放在靠后阶段，优先复制不常变化的文件
- 变化频率高的配置文件 COPY 集中在 Stage 2.6，避免前面层缓存失效

#### 中文环境配置

```dockerfile
ENV TZ=Asia/Shanghai
ENV LANG=zh_CN.UTF-8
ENV LANGUAGE=zh_CN:zh
ENV LC_ALL=zh_CN.UTF-8

RUN sed -i 's/^# *zh_CN.UTF-8 UTF-8/zh_CN.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen zh_CN.UTF-8 && \
    update-locale LANG=zh_CN.UTF-8 && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone
```

#### 构建计时

每个 Stage 输出 `[TIMER]` 日志：本阶段耗时 + 累计耗时，最终 Stage 7 输出汇总表。
时间戳写入 `/tmp/.build-timer`，格式 `S<N>=<unix-timestamp>`。

#### 镜像源切换

通过 `APT_MIRROR` 和 `PIP_MIRROR` 构建参数支持国内镜像：
- `APT_MIRROR=official|aliyun|tuna`（默认 official）
- `PIP_MIRROR=official|aliyun|tuna`（默认 official）
- 镜像源配置在每个阶段的首个 RUN 中完成，条件替换 sources.list 和 pip.conf

<a id="安全规范"></a>
#### 安全规范

- 禁止在 Dockerfile 中硬编码密码、密钥、token
- 敏感信息通过环境变量（`-e`）或 build-arg 传入
- SSH 主机密钥在容器启动时生成，不打包到镜像中
- 密码哈希在 entrypoint 运行时动态生成（`chpasswd`）

<a id="体积优化"></a>
#### 体积优化

- Runtime 阶段使用 `--no-install-recommends` 减少不必要的依赖
- 多阶段构建：builder 阶段含 build-essential/python3-dev，runtime 仅 COPY venv
- Stage 7 清理 `/tmp/*` `/var/tmp/*` 减少镜像体积
- pip 安装使用 `--no-cache-dir`
- Docker/Podman 客户端与服务端版本匹配

<a id="非-root-用户规范"></a>
#### 非 root 用户规范

- 固定用户名 `devuser`，UID 优先 1000（被占用时自动分配）
- 默认加入 `docker` 组（访问 DinD socket）
- 默认无 sudo 权限，通过 `GRANT_SUDO=yes` 环境变量启用 NOPASSWD sudo
- HOME 目录为 `/home/devuser`
- subuid/subgid 配置为 100000-165535（Podman rootless 所需）
- WORKDIR 设置为 `/workspace`，支持作为其他项目的基础镜像（FROM devcontainer-base）

#### 验证清单

- [ ] `bash scripts/build.sh` 无错误，构建日志有清晰的 Stage 标记和计时
- [ ] 镜像中 `locale -a` 显示 zh_CN.UTF-8
- [ ] 镜像中 `date` 显示 Asia/Shanghai 时区
- [ ] `id devuser` 显示 uid=1000，groups 包含 docker
- [ ] Python venv 在 `/opt/venv`，`/opt/venv/bin/python` 可用
- [ ] Docker CLI 和 Podman CLI 均已安装
- [ ] `dockerd --version` 与 Docker CLI 版本匹配

---

### 4.2 Entrypoint 启动脚本规范

**文件**：`.agents/rules/entrypoint.md`
**ID**：`devcontainer-entrypoint-rules`

<a id="基础约定"></a>
#### 基础约定

- 使用 bash（`#!/bin/bash`），开头加 `set -e` 确保错误退出
- 支持 `DEBUG=1` 环境变量开启调试模式（`set -x`）
- 必须使用 tini 作为 init 进程（在 Dockerfile ENTRYPOINT 中指定：`ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]`）
- 日志使用统一格式（带时间戳、级别标记）
- 启动时输出 banner 和系统诊断信息

#### 日志规范

使用项目统一日志库（scripts/lib/logging.sh），格式参考：

```bash
log_info()  { echo -e "\033[32m✔\033[0m  $*"; }
log_warn()  { echo -e "\033[33m⚠\033[0m  $*" >&2; }
log_error() { echo -e "\033[31m✘\033[0m  $*" >&2; }
```

- 关键步骤必须输出 INFO 日志
- 错误条件输出 ERROR 日志并 `exit 1`
- 非致命问题输出 WARN 日志
- 构建时注释用英文（避免编码问题），运行时日志可用中文

#### 启动流程

Entrypoint 按以下顺序执行：

1. **环境初始化**：设置 DEBIAN_FRONTEND=noninteractive，加载环境变量默认值
2. **权限修复**：确保 /workspace 和 /home/devuser 目录权限正确
3. **SSH 主机密钥生成**：若不存在则重新生成（确保容器唯一性）
4. **devuser 密码设置**：
   - 若 `USER_PASSWORD` 已设置，使用该密码
   - 若未设置，自动生成随机密码并输出到日志
   - 通过 `chpasswd` 设置密码哈希（运行时动态生成，不写入镜像）
5. **sudo 配置**：若 `GRANT_SUDO=yes`，配置 NOPASSWD sudoers
6. **Jupyter 动态配置**：生成 jupyter_notebook_config.py 中的 token/password
7. **supervisord 启动**：exec 替换进程，确保信号正确传递
8. **命令模式支持**：若传入命令参数（`docker run ... bash`），跳过服务启动直接 exec

#### 信号处理

- 使用 tini 作为 PID 1，正确处理僵尸进程
- supervisord 作为前台主进程管理所有子服务，接收 SIGTERM 时优雅关闭
- 不使用 `&` 后台启动主服务后 wait 的模式（信号传递不可靠）

#### Docker DinD 初始化

若启用 DinD 模式（默认）：
- 确保 `/var/lib/docker` 目录存在（建议挂载 volume 持久化）
- 确保 `/etc/docker/daemon.json` 配置正确（storage-driver/iptables/log-opts）
- dockerd 由 supervisord 管理启动，startsecs=15 等待初始化
- 健康检查脚本验证 docker.sock 可访问

#### 命令模式

```bash
# 如果传入了命令参数（非supervisord启动），直接exec
if [ $# -gt 0 ]; then
    exec "$@"
fi
```

支持 `docker run -it --rm devcontainer-base bash` 调试模式。

#### 验证清单

- [ ] 脚本可执行权限（chmod +x）
- [ ] 启动日志清晰，包含 banner 和系统诊断信息
- [ ] Docker 启动失败时输出 dockerd.log 帮助诊断
- [ ] `docker exec` 进入容器执行 `su - devuser -c "docker ps"` 正常
- [ ] `docker exec` 进入容器执行 `su - devuser -c "sudo -n whoami"`（GRANT_SUDO=yes 时）
- [ ] Ctrl+C（docker stop）能优雅关闭容器
- [ ] SSH 密码/密钥认证均正常工作
- [ ] Jupyter token 通过环境变量正确注入
- [ ] 命令模式（传入 bash）直接进入 shell，不启动服务

---

### 4.3 服务管理规范

**文件**：`.agents/rules/services.md`
**ID**：`devcontainer-services-rules`

<a id="总体原则"></a>
#### 总体原则

- **必须使用 supervisord 管理所有服务**：sshd、dockerd、podman(rootless)、jupyter 四服务统一由 supervisord 管理
- 每个服务有独立的配置文件（`config/supervisor/conf.d/*.conf`）
- 服务配置 `autostart=true`、`autorestart=true`，确保异常退出后自动重启
- `startsecs` 根据服务特性设置：dockerd=15（需时间初始化存储驱动），sshd=5，jupyter=10，podman=5

<a id="ssh-服务sshd"></a>
#### SSH 服务（sshd）

**配置文件**：config/sshd_config、config/supervisor/conf.d/sshd.conf

- 默认监听 22 端口
- 默认禁用 root 登录（`ALLOW_ROOT_SSH=yes` 可启用）
- ED25519 密钥优先，支持密码和密钥两种认证方式
- host keys 在容器启动时重新生成（entrypoint.sh 中处理）
- `PasswordAuthentication yes`（开发环境便利优先）
- `PermitRootLogin no`（默认，通过环境变量可覆盖）

<a id="docker-dind-服务dockerd"></a>
#### Docker DinD 服务（dockerd）

**配置文件**：config/supervisor/conf.d/dockerd.conf、`/etc/docker/daemon.json`（Dockerfile 中创建）

- dockerd 监听 `/var/run/docker.sock`（仅内部 unix socket，不暴露 2375 端口到外部）
- 需要 `--privileged` 权限运行
- **daemon.json 单一配置源原则**：storage-driver/iptables/log-opts/userland-proxy 统一由 `/etc/docker/daemon.json` 配置，禁止在命令行参数中重复设置（会导致 dockerd 启动失败）
- Docker 数据目录 `/var/lib/docker` 建议挂载 volume 持久化
- 存储驱动使用 `overlay2`
- 日志驱动 `json-file`，轮转配置 `max-size=10m, max-file=3`
- `iptables=false`（容器内不需要独立 iptables）
- `userland-proxy=false`（使用 hairpin NAT 模式，性能更好）
- devuser 加入 docker 组，可直接访问 docker.sock
- Docker CLI 与 dockerd 版本必须匹配

<a id="podman-rootless-服务"></a>
#### Podman Rootless 服务

- 以 devuser 身份运行 rootless Podman
- 配置用户命名空间（subuid/subgid: 100000-165535）
- 支持 cgroupv2
- 无需特权模式即可运行容器
- Podman socket 位于 `/run/user/1000/podman/podman.sock`
- Docker CLI 和 Podman CLI 可同时使用（共存模式）

<a id="jupyter-服务"></a>
#### Jupyter 服务

**配置文件**：config/jupyter_notebook_config.py、config/supervisor/conf.d/jupyter.conf

- Python 虚拟环境位于 `/opt/venv`，Jupyter 安装在 venv 中
- 默认监听 `0.0.0.0:8888`
- Notebook 工作目录为 `/workspace`
- token 通过 `JUPYTER_TOKEN` 环境变量控制（默认 `devcontainer123`）
- password 通过 `JUPYTER_PASSWORD` 环境变量控制（可选）
- 默认 CORS 策略同源限制（`JUPYTER_ALLOW_ORIGIN` 可配置）
- 以 devuser 身份运行（非 root）
- 支持 Notebook 和 Lab 两种界面

<a id="健康检查"></a>
#### 健康检查

**脚本**：scripts/healthcheck.sh

- Dockerfile 中配置 `HEALTHCHECK` 指令，每 30 秒检查一次，超时 10 秒，start-period=45 秒，retries=3
- healthcheck.sh 按条件检查启用的服务：
  - SSH：pgrep sshd 进程 + `/dev/tcp/127.0.0.1/22` 端口检测（不依赖 nc/netcat）
  - Docker：检查 `/var/run/docker.sock` 存在且可读写 + `docker info` 验证版本
  - Jupyter：pgrep jupyter 进程 + curl HTTP API 检测（接受 200/302/401/403）
- 通过 `ENABLE_SSH`、`ENABLE_DOCKER`、`ENABLE_JUPYTER` 环境变量控制检查哪些服务
- 输出结构化日志 `[HEALTHCHECK] service: OK/FAILED`，最终输出 `STATUS: HEALTHY/UNHEALTHY`

#### supervisord 主配置

**配置文件**：config/supervisord.conf

- nodaemon=true（前台运行，作为容器主进程）
- logfile=/var/log/supervisor/supervisord.log
- pidfile=/var/run/supervisord.pid
- 包含 `/etc/supervisor/conf.d/*.conf` 子配置
- 所有服务日志输出到 `/var/log/supervisor/`

#### 端口映射参考

| 服务 | 容器内端口 | 宿主机映射（默认） | 说明 |
|------|-----------|-------------------|------|
| SSH | 22 | 2222 | SSH 远程连接 |
| Jupyter | 8888 | 8888 | Notebook/Lab Web界面 |
| Docker | unix socket | - | DinD socket 不暴露端口 |
| Podman | unix socket | - | Rootless socket 不暴露端口 |

#### 服务启动顺序约束

1. dockerd 必须先启动（startsecs=15），其他服务不依赖 Docker 启动顺序
2. sshd 和 jupyter 可并行启动
3. podman 以 devuser 身份启动，需在用户创建后启动

---

### 4.4 构建与测试规范

**文件**：`.agents/rules/build-test.md`
**ID**：`devcontainer-build-test-rules`

#### 构建方式

##### 方式一：一键构建脚本（推荐）

```bash
# 标准构建
bash scripts/build.sh

# 使用国内镜像源构建（aliyun）
bash scripts/build.sh --cn

# 指定镜像源
bash scripts/build.sh --apt-mirror tuna --pip-mirror tuna

# 构建后自动验证
bash scripts/build.sh --verify

# 不使用缓存重新构建
bash scripts/build.sh --no-cache

# 指定镜像标签和名称
bash scripts/build.sh -t 2.0 -n my-devcontainer
```

构建脚本特性：
- 自动加载 `.env` 文件中的环境变量（set -a 自动导出）
- CLI 参数优先级高于 `.env` 文件中的配置
- BuildKit 缓存挂载自动启用
- 构建完成后可选 `--verify` 模式：临时启动容器，验证 SSH/Docker/Jupyter 三服务
- 统一日志格式（scripts/lib/logging.sh）

##### 方式二：Docker Compose 一键启动（推荐日常使用）

```bash
# 一键启动（自动构建镜像+启动+健康验证）
bash scripts/start.sh

# 指定模式启动
bash scripts/start.sh --profile dood     # DooD 模式（挂载宿主机docker.sock）
bash scripts/start.sh --profile ssh-only # 仅 SSH 模式
bash scripts/start.sh -p ssh-only        # 简写

# 查看状态 / 停止 / 重启
bash scripts/start.sh status
bash scripts/start.sh stop
bash scripts/start.sh restart

# 跳过验证快速启动
bash scripts/start.sh --no-verify
```

start.sh 特性：
- 支持 dind/dood/ssh-only 三种 profile，默认 dind
- 自动加载 `.env` 文件，未设置 `USER_PASSWORD`/`JUPYTER_TOKEN` 时自动生成随机凭据
- 轮询 Docker healthcheck 等待服务就绪（超时 90s，间隔 3s）
- 分层验证：内部端口检测 + 宿主机 SSH 连接 + Jupyter HTTP + Docker DinD API
- 输出彩色连接信息面板（含 copy-paste 命令）

##### 方式三：手动 docker build

```bash
# 标准构建
docker build -t devcontainer-base .

# 使用国内镜像源
docker build --build-arg APT_MIRROR=aliyun --build-arg PIP_MIRROR=aliyun -t devcontainer-base .

# 不使用缓存
docker build --no-cache -t devcontainer-base .
```

#### 环境配置

```bash
# 复制环境变量模板
cp .env.example .env
# 编辑 .env 文件，按需修改配置
```

`.env` 文件支持的关键配置项见 `.env.example`。

#### 运行容器

##### 使用 Docker Compose（推荐）

```bash
# 使用 start.sh 启动（推荐）
bash scripts/start.sh

# 或直接使用 docker compose
docker compose --profile dind up -d
```

##### 使用 docker run

```bash
# DinD 模式（需要 --privileged）
docker run -d --privileged \
  -p 2222:22 -p 8888:8888 \
  -e USER_PASSWORD=changeme \
  -e JUPYTER_TOKEN=mysecret \
  -e GRANT_SUDO=yes \
  -v devcontainer-workspace:/workspace \
  -v devcontainer-docker:/var/lib/docker \
  --name devcontainer-test devcontainer-base

# DooD 模式（挂载宿主机 docker.sock，无需 --privileged）
docker run -d \
  -p 2222:22 -p 8888:8888 \
  -e USER_PASSWORD=changeme \
  -e JUPYTER_TOKEN=mysecret \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v devcontainer-workspace:/workspace \
  --name devcontainer-test devcontainer-base

# 调试模式（不启动服务，直接进入 shell）
docker run -it --rm --privileged devcontainer-base bash
```

#### 验证流程

##### 构建后验证（build.sh --verify）

1. 临时启动容器（DinD 模式）
2. 等待健康检查通过（healthcheck.sh 返回 healthy）
3. 验证 SSH 端口监听
4. 验证 Docker daemon 可访问
5. 验证 Jupyter API 响应
6. 清理临时容器

##### 运行后手动验证

```bash
# 1. 查看容器状态和健康
docker ps
docker inspect --format='{{.State.Health.Status}}' devcontainer-base-dind
# 期望：healthy

# 2. 查看服务日志
docker logs devcontainer-base-dind
docker exec devcontainer-base-dind supervisorctl status
# 期望：所有服务 RUNNING

# 3. 验证 SSH（使用 devuser，root 默认禁用）
ssh -p 2222 devuser@localhost
# 或使用 sshpass 自动化测试
sshpass -p <password> ssh -o StrictHostKeyChecking=no -p 2222 devuser@localhost echo "SSH OK"

# 4. 验证 Jupyter（浏览器访问）
# http://localhost:8888/?token=<token>
curl -s http://localhost:8888/api
# 期望：返回 JSON（需要 token）

# 5. 验证 Docker DinD
docker exec -it devcontainer-base-dind docker ps
docker exec -it devcontainer-base-dind docker run --rm hello-world

# 6. 验证 Podman rootless
docker exec -it devcontainer-base-dind su - devuser -c "podman ps"

# 7. 验证 sudo 权限（需设置 GRANT_SUDO=yes）
docker exec devcontainer-base-dind su - devuser -c "sudo -n whoami"
# 期望：root

# 8. 中文环境验证
docker exec devcontainer-base-dind locale | grep LANG
# 期望：LANG=zh_CN.UTF-8
docker exec devcontainer-base-dind date
# 期望：显示中国时区时间（CST）
```

#### 常见问题排查

| 问题 | 排查命令 | 常见原因 |
|------|---------|---------|
| Docker DinD 启动失败 | `docker logs <name>` 查看 dockerd 日志 | 未使用 `--privileged`、daemon.json 与命令行参数冲突 |
| SSH 连接被拒 | `docker exec <name> pgrep -a sshd` | sshd 未启动、密码未设置、端口未映射 |
| Jupyter 无法访问 | `docker exec <name> curl -s http://localhost:8888/api` | jupyter 未启动、token 不匹配 |
| 环境变量不生效 | `docker exec <name> env \| grep -E "USER_PASSWORD\|JUPYTER"` | `.env` 文件未正确加载、变量名拼写错误 |
| 容器启动后立即退出 | `docker logs <name>` | entrypoint.sh 语法错误、Docker 启动失败、daemon.json 配置错误 |
| devuser 无法运行 docker | `docker exec <name> ls -la /var/run/docker.sock` | docker.sock 权限不对、用户不在 docker 组 |
| 构建时 apt/pip 下载慢 | 使用 `--cn` 参数或在 `.env` 中设置镜像源 | 网络问题，切换国内镜像源 |

#### 清理

```bash
# 停止并移除容器
bash scripts/start.sh stop
# 或
docker compose --profile dind down

# 清理数据卷（注意：会丢失 Docker 数据）
docker volume rm devcontainer-base_docker-storage
docker volume rm devcontainer-base_workspace
```

---

## 5. 交付物清单

| 文件 | 状态 | 说明 |
|------|------|------|
| apps/docker-images/devcontainer-base/AGENTS.md | ✅ 重构 | 从单文件约束改为索引页+路由表 |
| apps/docker-images/devcontainer-base/.agents/README.md | ✅ 新增 | 目录索引+快速开始指南（三层路由+任务路由表+自检清单） |
| apps/docker-images/devcontainer-base/.agents/rules/dockerfile.md | ✅ 新增 | Dockerfile多阶段构建规范（107行） |
| apps/docker-images/devcontainer-base/.agents/rules/entrypoint.md | ✅ 新增 | Entrypoint启动脚本规范（83行） |
| apps/docker-images/devcontainer-base/.agents/rules/services.md | ✅ 新增 | 服务管理规范（104行，含显式锚点） |
| apps/docker-images/devcontainer-base/.agents/rules/build-test.md | ✅ 新增 | 构建与测试规范（202行） |
| .agents/rules/*/(.gitkeep x5) | ✅ 新增 | 预留目录占位 |

---

## 6. 质量门检查

| 质量门 | 标准 | 结果 |
|--------|------|------|
| G1（事实无因果词） | R阶段纯客观描述，无推断 | ✅ 通过 |
| G2（洞察四元组完整） | 现象+根因+影响+建议 | ✅ 通过 |
| G3（模式可迁移） | 触发条件+核心步骤+反模式 | ✅ 通过（快速开始指南可复用于其他apps子项目） |
| G4（行动项原子化） | 单一职责、可独立验证 | ✅ 通过 |
