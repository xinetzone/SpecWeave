# Docker-in-Docker SSH 镜像

基于 ubuntu:26.04 的 Docker-in-Docker (DinD) 镜像，内置 OpenSSH 服务端，支持中文环境。

## 前置条件

根据操作系统选择合适的运行时环境：

- **Linux / macOS**: 需要 Docker Engine
- **Windows**: 两种选择
  - Docker Desktop（推荐，支持完整 DinD 功能）
  - wslc.exe（预览版，仅支持 SSH 模式，无需安装 Docker Desktop）
- **WSL2**:
  - Docker Desktop WSL 集成（推荐）
  - 或原生 Docker Engine（需启用 systemd）

> **注意**: WSL1 不完全支持容器运行，请升级到 WSL2。

## 快速开始（使用管理脚本）

项目提供了一键式管理脚本，自动检测环境并适配 docker/wslc 运行时：

```bash
# 1. 环境检测（自动识别可用运行时）
bash scripts/check-env.sh

# 2. 构建镜像
bash scripts/dind.sh build

# 3. 启动容器（默认端口 2222）
bash scripts/dind.sh run

# 4. SSH 连接
bash scripts/dind.sh ssh

# 查看所有可用命令
bash scripts/dind.sh --help
```

脚本支持自定义参数：
```bash
# 指定端口和密码
bash scripts/dind.sh run --port=2222 --password=MySecret123

# 指定运行时
bash scripts/dind.sh run --runtime=wslc

# 以 ai 用户登录
bash scripts/dind.sh ssh ai
```

## 功能特性

- Ubuntu 26.04 LTS 基础镜像，zh_CN.UTF-8 语言环境，Asia/Shanghai 时区
- Docker Engine（docker-ce + containerd.io + buildx 插件）
- OpenSSH 服务端，支持密码认证和公钥认证
- 非root用户 `ai`（UID 1000），加入 docker 组，免密 sudo，可直接运行 docker 命令
- tini init 进程，正确处理信号传递和僵尸进程回收
- overlay2 存储驱动，json-file 日志轮转（10MB × 3个）
- 详细启动日志与系统诊断信息，便于故障排查
- 支持 `DEBUG=1` 开启 shell 调试模式（set -x）
- 支持 wslc.exe 预览版运行时（SSH-only 模式）
- 可通过环境变量灵活配置，支持自动运行时检测

## 构建镜像

```bash
# 使用 docker 构建
docker build -t dind-ssh -f Containerfile .

# 或使用管理脚本（自动选择运行时）
bash scripts/dind.sh build
```

## 运行容器

### Docker 模式（完整 DinD 功能）

```bash
# 随机 root 密码（查看容器日志获取密码）
docker run -d --privileged -p 2222:22 -v dind-data:/var/lib/docker --name dind-test dind-ssh

# 指定 root 密码
docker run -d --privileged -p 2222:22 -v dind-data:/var/lib/docker \
  -e ROOT_PASSWORD=mypassword --name dind-test dind-ssh

# 注入 SSH 公钥实现免密登录
docker run -d --privileged -p 2222:22 -v dind-data:/var/lib/docker \
  -e SSH_PUBLIC_KEY="$(cat ~/.ssh/id_rsa.pub)" --name dind-test dind-ssh

# 调试模式
docker run -d --privileged -p 2222:22 -v dind-data:/var/lib/docker \
  -e ROOT_PASSWORD=pass -e DEBUG=1 --name dind-test dind-ssh
```

> **注意**：DinD 必须使用 `--privileged` 标志才能正常运行。

### wslc SSH-only 模式（预览）

使用 wslc.exe 运行时，无需 Docker Desktop，仅支持 SSH 访问（不启动嵌套 Docker daemon）：

```bash
wslc run -d --publish 2222:22 \
  -e ROOT_PASSWORD=test123 \
  -e DIND_SKIP_DOCKER=1 \
  --name dind-test dind-ssh
```

> **重要**: wslc 模式下必须设置 `DIND_SKIP_DOCKER=1`，因为 DinD 需要 `--privileged` 权限，而 wslc 可能不支持此特性。设置后仅提供 SSH 服务，不启动 Docker daemon。

## SSH 连接

```bash
# root 用户（密码或密钥认证）
ssh -p 2222 root@localhost

# 非root用户 ai
ssh -p 2222 ai@localhost

# 或使用管理脚本
bash scripts/dind.sh ssh
bash scripts/dind.sh ssh ai
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| ROOT_PASSWORD | 随机生成 | root 密码；未设置时自动生成并打印到日志 |
| SSH_PUBLIC_KEY | 无 | SSH 公钥，注入到 root 和 ai 用户的 authorized_keys |
| DOCKER_OPTS | 空 | 额外的 dockerd 启动参数 |
| ALLOW_ROOT_SSH | yes | 是否允许 root 通过 SSH 登录（yes/no） |
| DEBUG | 0 | 设为 1 开启 shell 调试模式（set -x） |
| DIND_SKIP_DOCKER | 0 | 设为 1 跳过 dockerd 启动，仅启用 SSH 服务（适用于 wslc SSH-only 模式） |
| CONTAINER_RUNTIME | auto | 强制指定容器运行时：`wslc` 或 `docker`，覆盖自动检测 |

## WSL 环境使用指南

### 选项 1：Docker Desktop + WSL2 后端（推荐，完整 DinD 支持）

这是最稳定的方案，支持完整的 Docker-in-Docker 功能：

1. 安装 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
2. 启动 Docker Desktop
3. 进入 Settings > Resources > WSL Integration
4. 启用你使用的 WSL 发行版（如 Ubuntu）
5. 点击 Apply & Restart
6. 在 WSL 终端中直接运行 `docker` 命令即可使用

### 选项 2：wslc.exe（Windows 原生，预览，无需 Docker Desktop）

适用于快速 SSH 开发环境，不需要安装 Docker Desktop：

1. 在 PowerShell 中更新 WSL：
   ```powershell
   wsl --update
   ```
2. 在 WSL 中构建镜像（或使用 `wslc build`，注意：wslc 构建功能有限）
3. 运行容器时设置 `DIND_SKIP_DOCKER=1` 启用 SSH-only 模式：
   ```bash
   wslc run -d --publish 2222:22 \
     -e ROOT_PASSWORD=test123 \
     -e DIND_SKIP_DOCKER=1 \
     --name dind-test dind-ssh
   ```

### 选项 3：WSL2 中安装原生 Docker Engine

适用于不想使用 Docker Desktop 的用户，需要 systemd 支持：

1. 编辑 `/etc/wsl.conf` 启用 systemd：
   ```ini
   [boot]
   systemd=true
   ```
2. 在 PowerShell 中重启 WSL：
   ```powershell
   wsl --shutdown
   ```
3. 重新进入 WSL，按照 [Docker Engine 安装指南](https://docs.docker.com/engine/install/ubuntu/) 安装 Docker
4. 将用户加入 docker 组：
   ```bash
   sudo usermod -aG docker $USER
   ```
5. 启动 Docker 服务：
   ```bash
   sudo systemctl start docker
   ```

> **注意**: WSL1 不支持容器运行 - 请升级到 WSL2。检查 WSL 版本：
> ```powershell
> wsl -l -v
> ```
> 升级命令：
> ```powershell
> wsl --set-version <发行版名称> 2
> ```

## 日志与故障排查

容器启动时会输出详细的诊断信息：
- OS/内核/cgroup 版本
- Docker/Containerd/SSHD 版本
- 构建信息（日期、基础镜像、语言环境、时区）
- privileged 模式检查
- cgroup 挂载状态
- Docker 启动进度与超时警告
- SSH 配置验证结果
- 容器运行时检测（docker/wslc）

查看启动日志：
```bash
# docker
docker logs <容器名>

# wslc
wslc.exe logs <容器名>

# 或使用管理脚本
bash scripts/dind.sh logs
```

查看 dockerd 详细日志（Docker 启动失败时）：
```bash
# docker
docker exec <容器名> tail -50 /var/log/dockerd.log

# wslc
wslc.exe exec <容器名> tail -50 /var/log/dockerd.log
```

构建信息存储在容器内 `/etc/dind-build-info`：
```bash
docker exec <容器名> cat /etc/dind-build-info
```

## 在容器内使用 Docker

SSH 连接后可直接使用 docker 命令（仅 Docker 模式，wslc SSH-only 模式不支持）：

```bash
docker version
docker ps
docker run --rm hello-world
docker images
```

非root用户 `ai` 同样可以运行 docker 命令（docker 组成员，docker.sock 权限 666）。

## 管理脚本命令参考

`scripts/dind.sh` 提供以下命令：

| 命令 | 说明 |
|------|------|
| `check-env` | 运行环境检测，识别可用运行时（docker/wslc） |
| `build` | 构建容器镜像 |
| `run` | 启动容器（默认端口 2222） |
| `stop` | 停止并删除容器 |
| `ssh [user]` | SSH 连接到容器（默认用户：root） |
| `logs` | 查看容器日志（实时跟踪） |
| `status` | 显示容器状态和镜像信息 |
| `exec <cmd>` | 在容器内执行命令 |
| `clean` | 删除容器和镜像，清理检测缓存 |
| `help` / `--help` / `-h` | 显示帮助信息 |

可用选项：

| 选项 | 说明 |
|------|------|
| `--runtime=<docker\|wslc\|auto>` | 强制指定运行时（默认：自动检测） |
| `--port=<port>` | SSH 端口映射（默认：2222） |
| `--name=<name>` | 容器名称（默认：dind-test） |
| `--password=<pwd>` | root 用户密码（默认：自动生成） |
| `--ssh-key=<key>` | SSH 公钥，用于免密认证 |

使用示例：
```bash
bash scripts/dind.sh check-env
bash scripts/dind.sh build
bash scripts/dind.sh run --port=2222 --password=MySecret123
bash scripts/dind.sh ssh ai
bash scripts/dind.sh exec docker ps
bash scripts/dind.sh status
bash scripts/dind.sh stop
bash scripts/dind.sh clean
```

## 常见问题

**Q: Docker daemon 在容器内启动失败？**
A: 
- Docker 模式下确保使用了 `--privileged` 标志
- wslc 模式下请设置 `-e DIND_SKIP_DOCKER=1` 启用 SSH-only 模式
- 查看详细日志：`bash scripts/dind.sh logs` 或 `docker exec <容器名> tail -50 /var/log/dockerd.log`

**Q: WSL 中出现 "docker: unrecognized service"？**
A: 不要在 WSL 中使用 `service docker start`：
- 如果使用 Docker Desktop，确保 WSL 集成已启用（Settings > Resources > WSL Integration）
- 如果使用原生 Docker Engine，使用 `sudo systemctl start docker`（需先启用 systemd）

**Q: wslc 模式下容器启动了但无法通过 SSH 连接？**
A:
- 检查端口映射：wslc 使用 `--publish` 参数（注意不是 `-p` 简写，某些版本可能需要完整参数名）
- 确保 Windows 防火墙允许对应端口（如 2222）入站连接
- 检查容器日志确认 sshd 是否正常启动：`wslc.exe logs <容器名>`
- 确认 WSL 已更新到最新版本：在 PowerShell 运行 `wsl --update`

**Q: 如何知道当前使用的是哪个运行时？**
A:
- 运行 `bash scripts/check-env.sh` 查看环境检测结果
- 运行 `bash scripts/dind.sh status` 查看当前运行时和容器状态
- 管理脚本会在执行命令时打印检测到的运行时信息

**Q: WSL2 和 WSL1 有什么区别？应该用哪个？**
A:
- WSL1 使用转换层，不完全支持容器运行，不推荐使用
- WSL2 使用真正的 Linux 内核，完整支持 Docker 和容器
- 检查版本：在 PowerShell 运行 `wsl -l -v`
- 升级到 WSL2：`wsl --set-version <发行版名称> 2`
- 设置默认版本：`wsl --set-default-version 2`

**Q: 管理脚本检测不到 docker 或 wslc？**
A:
- 首先运行 `bash scripts/check-env.sh` 查看详细诊断信息
- Docker: 确保 Docker 服务正在运行，且当前用户有权限访问 docker.sock
- wslc: 在 PowerShell 运行 `wsl --update` 确保 WSL 版本最新
- WSL 中访问 wslc.exe 需要 WSL interop 正常工作（脚本会自动检测）

## 安全注意事项

1. 本镜像在 Docker 模式下需要 `--privileged` 权限，仅在可信环境中使用
2. wslc SSH-only 模式不需要 privileged 权限，安全性更高但功能有限
3. 生产环境建议使用 SSH 公钥认证而非密码认证
4. 挂载 `/var/lib/docker` 数据卷以保证数据持久化
5. 不要将 Docker daemon API 暴露到外部网络
6. SSH 主机密钥在容器首次启动时生成（不打包到镜像中）
