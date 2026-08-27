# devcontainer-base 部署指南

> **版本**: v2.2 (conda-libmamba-ft) | **更新日期**: 2026-08-17
>
> 本文档涵盖从镜像构建到容器运行的完整部署流程，重点说明 UID/GID 动态映射机制（FixUID）、DooD/DinD 双模式运行、国内镜像源配置，以及部署验证与故障排查。

---

## 目录

1. [前置条件](#1-前置条件)
2. [环境配置 (.env)](#2-环境配置-env)
3. [镜像构建](#3-镜像构建)
4. [UID/GID 动态映射 (FixUID)](#4-uidgid-动态映射-fixuid)
5. [容器运行](#5-容器运行)
6. [部署验证](#6-部署验证)
7. [权限验证清单](#7-权限验证清单)
8. [故障排查](#8-故障排查)

---

## 1. 前置条件

| 组件 | 最低要求 | 说明 |
|------|---------|------|
| Docker | 24.0+ | 需支持 BuildKit（默认启用） |
| 操作系统 | Linux / WSL2 / macOS | Windows 需通过 WSL2 运行 dockerd |
| 磁盘空间 | ≥ 8GB | 镜像约 2.6GB，构建缓存额外约 3GB |
| 内存 | ≥ 4GB | 运行 Python/Jupyter 建议 8GB+ |
| 网络 | 可访问 Docker Hub / 国内镜像源 | 构建需下载 apt/pip/conda 包 |

**WSL2 注意事项**：在 WSL2 环境下需先启动 containerd 和 dockerd：

```bash
# 启动容器运行时
sudo containerd &>/tmp/containerd.log &
sudo dockerd &>/tmp/dockerd.log &

# 验证 Docker 可用
docker info --format "Server: {{.ServerVersion}}"
```

---

## 2. 环境配置 (.env)

`.env` 文件存储构建和运行时的环境变量，`scripts/build.sh` 和 `scripts/start.sh` 会自动加载。

### 2.1 快速配置

```bash
# 在项目根目录（apps/docker-images/devcontainer-base/）下
cp .env.example .env
```

### 2.2 国内镜像源（推荐配置）

以下配置已在 WSL2 Ubuntu 26.04 环境验证可用：

```bash
# ─── 运行模式 ──
PROFILE=dood                    # dood(DooD共享宿主机) | dind(DinD隔离) | ssh-only

# ─── Docker 镜像源 ──
DOCKER_REGISTRY_MIRROR=https://docker.m.daocloud.io

# ─── 国内构建源 ──
APT_MIRROR=aliyun               # apt 源: aliyun(推荐) | tuna(可能SSL错误) | bfsu | official
PIP_MIRROR=aliyun               # pip 源: aliyun(推荐) | tuna | bfsu | official
CONDA_MIRROR=tuna               # conda 源: tuna(推荐,aliyun conda已下线404) | bfsu | official
```

> ⚠️ **重要提示**：
> - **TUNA apt/pip 源在 WSL 环境下可能出现 SSL 证书验证失败**，推荐使用 aliyun
> - **aliyun 的 conda-forge 镜像已下线**（返回 404），conda 必须使用 tuna 或 bfsu
> - Docker Registry Mirror 推荐 daocloud（国内延迟最低，约 0.078s）

### 2.3 凭据与端口配置

```bash
# ─── 凭据 ──
USER_PASSWORD=devcontainer123   # SSH 密码（留空自动生成16位随机密码）
JUPYTER_TOKEN=devcontainer123   # Jupyter Token（留空自动生成32位随机token）
GRANT_SUDO=yes                  # 授予 devuser 免密 sudo: yes | no
ALLOW_ROOT_SSH=no               # 禁止 root SSH 登录

# ─── 端口（DooD模式避免与DinD冲突）──
SSH_PORT=2223                   # SSH 映射端口
JUPYTER_PORT=8889               # Jupyter 映射端口

# ─── 服务开关 ──
ENABLE_SSH=yes
ENABLE_DOCKER=yes
ENABLE_PODMAN=no                # Podman rootless（与Docker可能冲突，默认关闭）
ENABLE_JUPYTER=yes
```

### 2.4 FixUID 配置

```bash
# 手动指定 UID/GID（留空则自动检测）
# LOCAL_USER_ID=1000
# LOCAL_GROUP_ID=1000

# 工作目录 chown 模式
# WORKSPACE_CHOWN_MODE=auto     # auto(默认,仅named volume) | yes(含bind mount) | no | named-only
# FIXUID_DEBUG=0                # 设为1输出详细调试日志
```

---

## 3. 镜像构建

### 3.1 一键构建（推荐）

```bash
# 标准构建（使用 .env 中的镜像源配置）
bash scripts/build.sh

# 快速构建（跳过完整C扩展验证，开发阶段推荐）
bash scripts/build.sh --verify-mode fast

# 使用国内镜像源构建（等价于 .env 中设置 aliyun+tuna）
bash scripts/build.sh --cn

# 构建后自动运行冒烟测试
bash scripts/build.sh --verify

# 指定网络模式（WSL2环境推荐，加速下载）
bash scripts/build.sh --network-host --verify-mode fast

# 不使用缓存（全新构建）
bash scripts/build.sh --no-cache
```

### 3.2 构建参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--verify-mode fast` | 快速验证（仅Python+核心C扩展） | standard（19项验证） |
| `--verify-mode off` | 跳过构建时验证（最快，迭代开发用） | standard |
| `--cn` | 使用国内镜像源（apt=aliyun, pip=aliyun, conda=tuna） | 不使用 |
| `--network-host` | 构建时使用宿主机网络（WSL2推荐） | 默认桥接网络 |
| `--no-cache` | 不使用构建缓存 | 使用缓存 |
| `-t <tag>` | 指定镜像标签 | conda-libmamba-ft |
| `--apt-mirror <src>` | 指定 apt 源 | official |
| `--pip-mirror <src>` | 指定 pip 源 | official |
| `--conda-mirror <src>` | 指定 conda 源 | official |

> **CLI 参数优先级高于 .env 文件配置**。

### 3.3 WSL2 环境构建最佳实践

在 WSL2 环境中，直接从 `/mnt/d/`（Windows 文件系统）构建 I/O 性能较差。推荐将文件同步到 WSL 原生目录构建：

```bash
# 定义路径
WSL_DIR="$HOME/devcontainer-base-build"
SRC="/mnt/d/spaces/SpecWeave/apps/docker-images/devcontainer-base"

# 创建 WSL 构建目录（首次）
mkdir -p "$WSL_DIR"
rsync -a --delete "$SRC/" "$WSL_DIR/" --exclude ".git" --exclude "node_modules"

# 后续增量构建只需同步变更文件
cp "$SRC/entrypoint.sh" "$WSL_DIR/entrypoint.sh"
cp "$SRC/Dockerfile" "$WSL_DIR/Dockerfile"
cp "$SRC/.env" "$WSL_DIR/.env"

# 从 WSL 原生目录构建（速度更快）
cd "$WSL_DIR"
bash scripts/build.sh --network-host --verify-mode fast \
  --apt-mirror aliyun --pip-mirror aliyun --conda-mirror tuna
```

### 3.4 构建成功标志

构建完成后输出应包含：

```
  ✔  Quick smoke test passed!

┌─────────────────────────────────────────┐
│            结果汇总                      │
├─────────────────────────────────────────┤
│  状态: PASS
│  通过: 10 项
│  失败: 0 项
└─────────────────────────────────────────┘

  INFO  EVENT build_complete image=devcontainer-base:conda-libmamba-ft duration=xxx status=success
```

验证镜像存在：

```bash
docker images devcontainer-base:conda-libmamba-ft
# 预期输出：
# REPOSITORY           TAG                 IMAGE ID       CREATED          SIZE
# devcontainer-base    conda-libmamba-ft   xxxxxxxxxxxx   xx minutes ago   2.62GB
```

---

## 4. UID/GID 动态映射 (FixUID)

FixUID 是容器启动时自动解决 **bind mount 跨 UID 权限问题**的核心机制，已永久 bake 进镜像（entrypoint.sh 内置），无需额外挂载。

### 4.1 问题背景

Docker 容器内用户 UID 默认为 1000（devuser），而宿主机用户 UID 可能不同（如 Ubuntu 默认 1000、macOS 默认 501、其他 Linux 发行版可能不同）。当使用 bind mount 挂载宿主机目录时，UID 不匹配会导致"Permission denied"。

### 4.2 UID 来源优先级

FixUID 按以下优先级确定目标 UID/GID：

| 优先级 | 来源 | 环境变量 | 日志中 Source 显示 |
|:---:|------|---------|------------------|
| 1（最高） | 环境变量显式指定 | `LOCAL_USER_ID` / `LOCAL_GROUP_ID` | 环境变量(LOCAL_USER_ID) |
| 2 | 自动检测 /workspace 目录属主 | — | 自动检测(/workspace属主) |
| 3（默认） | 镜像内置默认值 (UID=1001) | — | 镜像默认 |
| （阻止） | 检测到 UID=0（root） | — | 安全阻止(UID=0不允许) |

### 4.3 安全保护机制

FixUID 内置多层安全保护：

1. **禁止 UID=0**：永远不会将 devuser 设置为 root（UID=0），检测到则回退并输出 WARN 日志
2. **数字验证**：UID/GID 必须为纯数字，无效值回退到当前值
3. **冲突处理**：目标 UID/GID 被其他用户/组占用时，自动将占用者移到 +1000 位置
4. **系统目录保护**：Jupyter 根目录为系统敏感目录（/home、/etc、/usr 等）时，强制跳过 chown
5. **Bind mount 安全**：默认模式下，bind mount 目录不执行 chown（防止修改宿主机文件权限）
6. **文件修复范围限定**：UID 调整后仅修复安全范围内的文件（/home/devuser、/tmp、/var/log/supervisor），跳过所有挂载点

### 4.4 启动日志示例

容器启动时，FixUID 输出醒目的 ═══ 横幅摘要：

```
[FixUID] ═════════════════════════════════════════
[FixUID]   User: devuser
[FixUID]   UID/GID mapping: 1001:1001 (no change)
[FixUID]   Source: default (env=环境变量 / auto=自动检测 / default=镜像默认 / blocked=安全阻止)
[FixUID] ═════════════════════════════════════════
```

UID 发生调整时：

```
[FixUID] Adjusting devuser UID: 1001 -> 501, GID: 1001 -> 20
[FixUID] ═════════════════════════════════════════
[FixUID]   User: devuser
[FixUID]   UID/GID mapping: 1001:1001 -> 501:20
[FixUID]   Source: env (env=环境变量 / auto=自动检测 / default=镜像默认 / blocked=安全阻止)
[FixUID] ═════════════════════════════════════════
```

"Container ready!" 横幅中同样显示 UID 映射信息：

```
============================================================
  Container ready! Services managed by supervisord

  User/UID mapping:
    User:  devuser (UID:GID = 1001:1001)
    Source: 镜像默认
  ...
============================================================
```

### 4.5 /workspace chown 模式

| 模式 | 行为 | 适用场景 |
|------|------|---------|
| `auto`（默认） | Named volume → chown；Bind mount → 跳过 chown 并输出 WARN | 通用场景（推荐） |
| `named-only` | 仅 Named volume 执行 chown | 与 auto 类似，更明确 |
| `yes` | 所有目录都 chown（**包括bind mount，会修改宿主机文件权限！**） | 一次性初始化开发环境 |
| `no` | 完全跳过 chown | 只读数据集目录、CI 环境 |

> ⚠️ **使用 `WORKSPACE_CHOWN_MODE=yes` 时需谨慎**：chown 会递归修改 bind mount 对应宿主机目录的文件属主，可能影响宿主机文件权限。

### 4.6 调试

设置 `FIXUID_DEBUG=1` 可输出详细调试日志：

```bash
docker run -d --name devcontainer-dood \
  -e FIXUID_DEBUG=1 \
  -e LOCAL_USER_ID=1000 \
  ... \
  devcontainer-base:conda-libmamba-ft

docker logs devcontainer-dood 2>&1 | grep FIXUID
```

---

## 5. 容器运行

### 5.1 运行模式对比

| 特性 | DinD（Docker-in-Docker） | DooD（Docker-out-of-Docker） |
|------|------------------------|---------------------------|
| 启动参数 | `--privileged` | 无（仅挂载 `-v /var/run/docker.sock`） |
| Docker 隔离 | 完全隔离（容器内独立 daemon） | 共享宿主机 Docker daemon |
| 性能 | 有额外开销 | 接近原生 |
| 安全性 | 需要特权模式（风险较高） | 无特权模式（较安全） |
| 镜像/容器 | 容器内独立 | 与宿主机共享 |
| 适用场景 | CI/CD、完全隔离的构建环境 | 开发环境、需要访问宿主机镜像 |
| 内部dockerd | 启动 | 自动禁用（检测到已挂载sock） |

### 5.2 DooD 模式启动（推荐开发用）

```bash
docker run -d --name devcontainer-dood \
  -p 2223:22 -p 8889:8888 \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v $(pwd)/workspace:/workspace \
  -e USER_PASSWORD=devcontainer123 \
  -e JUPYTER_TOKEN=devcontainer123 \
  -e ENABLE_DOCKER=yes \
  -e GRANT_SUDO=yes \
  devcontainer-base:conda-libmamba-ft
```

关键参数说明：
- `-v /var/run/docker.sock:/var/run/docker.sock:ro` — 挂载宿主机 Docker socket（只读推荐）
- **无需 `--privileged`**
- 脚本自动检测到已挂载 docker.sock → 切换到 DooD 模式，禁用内部 dockerd

### 5.3 DinD 模式启动（隔离环境）

```bash
docker run -d --name devcontainer-dind \
  --privileged \
  -p 2222:22 -p 8888:8888 \
  -v devcontainer-workspace:/workspace \
  -v devcontainer-docker:/var/lib/docker \
  -e USER_PASSWORD=devcontainer123 \
  -e JUPYTER_TOKEN=devcontainer123 \
  -e ENABLE_DOCKER=yes \
  devcontainer-base:conda-libmamba-ft
```

关键参数说明：
- `--privileged` — DinD 必需，否则内部 dockerd 无法启动
- `-v devcontainer-docker:/var/lib/docker` — 持久化 Docker 数据（推荐 Named Volume）

### 5.4 使用 start.sh 一键启动（推荐）

```bash
# DooD 模式启动（自动加载.env，自动健康检查）
bash scripts/start.sh --profile dood

# DinD 模式
bash scripts/start.sh --profile dind

# 查看状态
bash scripts/start.sh status

# 停止
bash scripts/start.sh stop

# 重启
bash scripts/start.sh restart
```

### 5.5 使用 --env-file 加载 .env

```bash
docker run -d --name devcontainer-dood \
  --env-file .env \
  -p 2223:22 -p 8889:8888 \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v $(pwd)/workspace:/workspace \
  devcontainer-base:conda-libmamba-ft
```

> 注意：`--env-file` 仅加载环境变量，不包含端口映射和 volume 挂载。

### 5.6 自定义 UID 映射启动

```bash
# 显式指定 UID/GID 匹配宿主机用户
docker run -d --name devcontainer-dood \
  -p 2223:22 -p 8889:8888 \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v /home/myuser/projects:/workspace \
  -e LOCAL_USER_ID=$(id -u) \
  -e LOCAL_GROUP_ID=$(id -g) \
  -e USER_PASSWORD=devcontainer123 \
  -e JUPYTER_TOKEN=devcontainer123 \
  devcontainer-base:conda-libmamba-ft
```

---

## 6. 部署验证

容器启动后，等待约 15-20 秒让服务初始化完成，然后按以下步骤验证。

### 6.1 容器健康状态

```bash
# 查看容器状态
docker ps --filter name=devcontainer-dood
# 预期输出: ... Up xx seconds (healthy) ...

# 查看健康检查详情
docker inspect --format='{{.State.Health.Status}}' devcontainer-dood
# 预期输出: healthy
```

### 6.2 查看启动日志

```bash
# 查看完整启动日志
docker logs devcontainer-dood

# 检查 FixUID 横幅（确认 UID 映射正常）
docker logs devcontainer-dood 2>&1 | grep -A6 "══════════"

# 确认无权限错误
docker logs devcontainer-dood 2>&1 | grep -iE "permission denied|operation not permitted|chown.*fail"
# 预期输出: 空（无匹配）

# 确认无 ERROR/FATAL 日志
docker logs devcontainer-dood 2>&1 | grep -iE "\[ERROR\]|\[FATAL\]|level=error"
# 预期输出: 空（无匹配）
```

### 6.3 关键日志确认项

启动日志中应出现以下关键信息：

| 日志项 | 预期值 | 说明 |
|--------|-------|------|
| FixUID ═══ 横幅 | User: devuser, UID/GID mapping: xxx:xxx | UID映射摘要 |
| Container ready! 横幅 | User/UID mapping + SSH + Jupyter 信息 | 启动完成 |
| supervisord started | pid 7 | 服务管理器启动 |
| sshd entered RUNNING | success | SSH 服务就绪 |
| jupyter entered RUNNING | success | Jupyter 服务就绪 |
| Docker socket permissions adjusted | （DooD模式） | docker.sock 权限正确 |

### 6.4 服务连通性验证

```bash
# JupyterLab HTTP 检查
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" \
  "http://localhost:8889/lab?token=devcontainer123"
# 预期: HTTP Status: 200

# SSH 端口检查
timeout 3 bash -c "echo > /dev/tcp/localhost/2223" && echo "SSH: OPEN" || echo "SSH: CLOSED"
# 预期: SSH: OPEN

# DooD Docker 访问检查
docker exec devcontainer-dood docker ps
# 预期: 显示容器列表（包括自身）
```

### 6.5 容器内部检查

```bash
# 检查 devuser UID/GID 和组
docker exec devcontainer-dood id devuser
# 预期: uid=1001(devuser) gid=1001(devuser) groups=1001(devuser),27(sudo),997(docker)

# 检查 home 目录权限
docker exec devcontainer-dood ls -la /home/devuser/
# 预期: 所有文件属主为 devuser:devuser

# 检查 /workspace 可写
docker exec devcontainer-dood touch /workspace/.write_test && echo "/workspace writable: OK" && docker exec devcontainer-dood rm /workspace/.write_test

# 检查 /tmp 可写
docker exec devcontainer-dood touch /tmp/.write_test && echo "/tmp writable: OK" && docker exec devcontainer-dood rm /tmp/.write_test

# 检查 sudo 权限
docker exec devcontainer-dood su - devuser -c "sudo -n whoami"
# 预期: root
```

---

## 7. 权限验证清单

部署完成后，逐项确认以下权限检查项均通过：

### 7.1 日志扫描

| 检查项 | 命令 | 通过标准 |
|--------|------|---------|
| Permission denied | `docker logs <name> \| grep -i "permission denied"` | 无输出 |
| Operation not permitted | `docker logs <name> \| grep -i "operation not permitted"` | 无输出 |
| chown 失败 | `docker logs <name> \| grep -iE "chown.*(fail|error|cannot)"` | 无输出 |
| sudo 错误 | `docker logs <name> \| grep -iE "sudo.*(error|denied)"` | 无输出 |
| UID/GID 冲突 | `docker logs <name> \| grep -iE "(uid|gid).*(mismatch|conflict|invalid)"` | 无输出 |
| ERROR/FATAL | `docker logs <name> \| grep -iE "\[ERROR\]|\[FATAL\]"` | 无输出 |

### 7.2 文件系统权限

| 检查项 | 命令 | 通过标准 |
|--------|------|---------|
| Home 目录属主 | `docker exec <name> ls -la /home/devuser/` | 所有文件 devuser:devuser |
| /workspace 访问 | `docker exec <name> ls -la /workspace` | 可访问，devuser 有 rwx |
| /workspace 写入 | `docker exec <name> touch /workspace/.test` | 写入成功 |
| /tmp 写入 | `docker exec <name> touch /tmp/.test` | 写入成功 |
| Docker socket | `docker exec <name> ls -la /var/run/docker.sock` | srw-rw---- root:docker |
| .ssh 目录权限 | `docker exec <name> ls -la /home/devuser/.ssh` | drwx------ |

### 7.3 服务功能

| 检查项 | 命令 | 通过标准 |
|--------|------|---------|
| JupyterLab | `curl -s -o /dev/null -w "%{http_code}" http://localhost:<port>/lab?token=<token>` | 200 |
| SSH | `ssh -p <port> devuser@localhost` | 可登录 |
| Docker (DooD) | `docker exec <name> docker ps` | 可访问宿主机Docker |
| sudo | `docker exec <name> su - devuser -c "sudo -n whoami"` | 返回 root |
| Python | `docker exec <name> su - devuser -c "python --version"` | Python 3.14.x |
| Conda | `docker exec <name> su - devuser -c "conda --version"` | conda 版本号 |

---

## 8. 故障排查

### 8.1 构建阶段

| 问题 | 症状 | 原因 | 解决方案 |
|------|------|------|---------|
| TUNA SSL 证书错误 | `SSL connection failed: certificate verify failed` | WSL 环境下 TUNA HTTPS 证书链不完整 | 使用 `--apt-mirror aliyun --pip-mirror aliyun` |
| Conda 404 | `PackagesNotFoundError` 或 HTTP 404 | aliyun conda-forge 镜像已下线 | conda 使用 `--conda-mirror tuna` |
| Docker pull 超时 | `context deadline exceeded` | Docker Hub 连接慢 | 配置 `DOCKER_REGISTRY_MIRROR` 为国内源 |
| apt 下载慢 | 构建卡在 apt-get update/install | 默认使用官方源 | 添加 `--cn` 或设置 `APT_MIRROR=aliyun` |
| buildx/runc 错误 | `exec: "runc": executable file not found` | WSL 中 dockerd 与 containerd 版本不匹配 | 完全重启：`sudo pkill -9 dockerd containerd; sudo containerd &; sudo dockerd &` |
| 构建缓存丢失 | 所有层重新构建 | Docker daemon 重启导致 BuildKit 缓存丢失 | 正常现象，等待重新构建完成即可 |

### 8.2 运行阶段

| 问题 | 症状 | 原因 | 解决方案 |
|------|------|------|---------|
| Permission denied | 容器内读写挂载目录报权限错误 | UID 不匹配，bind mount 跳过了 chown | 方案1: `-e LOCAL_USER_ID=$(id -u)` 手动指定<br>方案2: 宿主机执行 `sudo chown -R <uid>:<gid> <dir>`<br>方案3: `-e WORKSPACE_CHOWN_MODE=yes`（会修改宿主机文件） |
| 容器 Exited (255) | 容器非正常退出 | Docker daemon 重启导致所有容器停止 | `docker restart <name>`；WSL 中需确保 dockerd 稳定运行 |
| DooD 模式 docker 命令失败 | `Cannot connect to Docker daemon` | docker.sock 权限不正确或未挂载 | 检查 `-v /var/run/docker.sock:/var/run/docker.sock:ro`；确认 devuser 在 docker 组内 |
| DinD 模式启动失败 | dockerd 无法启动 | 缺少 `--privileged` | 添加 `--privileged` 参数启动 |
| Jupyter 无法访问 | HTTP 000 或 Connection refused | Jupyter 未完全启动或端口映射错误 | 等待10-15秒；检查 `-p` 端口映射；`docker logs` 确认 jupyter entered RUNNING |
| SSH 连接被拒 | `Connection refused` 或 `Permission denied` | sshd 未启动或密码错误 | `docker exec <name> pgrep sshd`；确认 USER_PASSWORD 设置正确 |
| FixUID 报 "occupied by" | 日志显示 GID/UID 冲突警告 | 目标 UID/GID 被系统用户占用 | 这是正常的自动处理，FixUID 会自动将冲突用户移走，无需干预 |
| supervisord CRIT 日志 | `Server 'unix_http_server' running without any HTTP authentication` | supervisord 默认配置无认证 | 正常现象，仅在内部使用 unix socket 通信，无需处理 |

### 8.3 WSL2 特有问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| dockerd 启动后消失 | WSL 会话结束时后台进程被回收 | 使用 `nohup ... & disown` 启动 dockerd；或在同一个 wsl 命令中完成所有操作 |
| /var/run/docker.sock 不存在 | dockerd 未启动或已崩溃 | 重新启动 containerd + dockerd（见 1.前置条件） |
| 构建速度极慢 | 从 /mnt/d/ (Windows FS) 构建 | 同步文件到 WSL 原生目录（~/）构建 |

### 8.4 快速诊断脚本

```bash
#!/bin/bash
# 一键诊断脚本 - 快速检查容器健康状态
NAME="${1:-devcontainer-dood}"

echo "=== Container Status ==="
docker ps --filter name=$NAME --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "=== Health ==="
docker inspect --format='{{.State.Health.Status}}' $NAME 2>/dev/null || echo "no healthcheck"

echo ""
echo "=== Service Status ==="
docker exec $NAME supervisorctl status 2>/dev/null

echo ""
echo "=== Permission Errors (last 100 lines) ==="
docker logs --tail 100 $NAME 2>&1 | grep -iE "permission denied|operation not permitted|chown.*fail|\[ERROR\]|\[FATAL\]" || echo "(none found)"

echo ""
echo "=== FixUID Summary ==="
docker logs $NAME 2>&1 | grep -A6 "══════════" | head -8

echo ""
echo "=== Connectivity ==="
JUPYTER_PORT=$(docker port $NAME 8888/tcp 2>/dev/null | head -1 | cut -d: -f2)
SSH_PORT=$(docker port $NAME 22/tcp 2>/dev/null | head -1 | cut -d: -f2)
[ -n "$JUPYTER_PORT" ] && curl -s -o /dev/null -w "Jupyter (port $JUPYTER_PORT): HTTP %{http_code}\n" "http://localhost:$JUPYTER_PORT/lab" || echo "Jupyter: port not mapped"
[ -n "$SSH_PORT" ] && timeout 2 bash -c "echo > /dev/tcp/localhost/$SSH_PORT" 2>/dev/null && echo "SSH (port $SSH_PORT): OPEN" || echo "SSH: CLOSED"
```

---

## 附录

### A. 服务端口一览

| 服务 | 容器内端口 | DinD 默认映射 | DooD 默认映射 |
|------|:--------:|:----------:|:----------:|
| SSH (sshd) | 22 | 2222 | 2223 |
| JupyterLab | 8888 | 8888 | 8889 |
| Docker (DinD) | unix socket | — | — |
| Docker (DooD) | 宿主机 sock | — | — |

### B. 核心文件位置

| 文件 | 容器内路径 | 说明 |
|------|----------|------|
| 入口脚本 | `/usr/local/bin/entrypoint.sh` | 容器启动入口（已bake进镜像） |
| Jupyter 配置 | `/home/devuser/.jupyter/jupyter_server_config.d/runtime.py` | 运行时生成 |
| Supervisord 配置 | `/etc/supervisor/conf.d/` | sshd/dockerd/jupyter 服务配置 |
| Docker 配置 (DinD) | `/etc/docker/daemon.json` | DinD 模式下自动创建 |
| Sudoers | `/etc/sudoers.d/devuser` | GRANT_SUDO=yes 时生成 |
| 健康检查脚本 | `/usr/local/bin/healthcheck.sh` | Docker HEALTHCHECK 调用 |

### C. 相关文档

- [构建与测试规范](../.agents/rules/build-test.md) — build.sh/start.sh 完整参数参考
- [Entrypoint 规范](../.agents/rules/entrypoint.md) — 启动流程和日志规范
- [服务配置规范](../.agents/rules/services.md) — sshd/dockerd/jupyter 配置细节
- [Dockerfile 规范](../.agents/rules/dockerfile.md) — 7-Stage 构建架构说明
- [最佳实践](best-practices.md) — Docker DinD 配置和性能优化
- [v2.2 构建流水线优化](v2.2-build-pipeline-optimization.md) — BuildKit 缓存和层优化
