---
id: "devcontainer-services-rules"
title: "服务管理规范"
source: "AGENTS.md#项目特有约束"
---
# 服务管理规范（devcontainer-base）

<a id="总体原则"></a>
## 总体原则

- **必须使用 supervisord 管理所有服务**：sshd、dockerd、podman(rootless)、jupyter 四服务统一由 supervisord 管理
- 每个服务有独立的配置文件（`config/supervisor/conf.d/*.conf`）
- 服务配置 `autostart=true`、`autorestart=true`，确保异常退出后自动重启
- `startsecs` 根据服务特性设置：dockerd=15（需时间初始化存储驱动），sshd=5，jupyter=10，podman=5

<a id="ssh-服务sshd"></a>
## SSH 服务（sshd）

**配置文件**：[config/sshd_config](../../config/sshd_config)、[config/supervisor/conf.d/sshd.conf](../../config/supervisor/conf.d/sshd.conf)

- 默认监听 22 端口
- 默认禁用 root 登录（`ALLOW_ROOT_SSH=yes` 可启用）
- ED25519 密钥优先，支持密码和密钥两种认证方式
- host keys 在容器启动时重新生成（entrypoint.sh 中处理）
- `PasswordAuthentication yes`（开发环境便利优先）
- `PermitRootLogin no`（默认，通过环境变量可覆盖）

<a id="docker-dind-服务dockerd"></a>
## Docker DinD 服务（dockerd）

**配置文件**：[config/supervisor/conf.d/dockerd.conf](../../config/supervisor/conf.d/dockerd.conf)、`/etc/docker/daemon.json`（Dockerfile 中创建）

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
## Podman Rootless 服务

- 以 devuser 身份运行 rootless Podman
- 配置用户命名空间（subuid/subgid: 100000-165535）
- 支持 cgroupv2
- 无需特权模式即可运行容器
- Podman socket 位于 `/run/user/<uid>/podman/podman.sock`（uid 由 FixUID 动态解析，非硬编码 1000）
- **XDG_RUNTIME_DIR 环境配置**：entrypoint.sh 自动创建 `/etc/profile.d/podman-runtime.sh`，为所有 login shell（SSH/`su -`/`bash -l`）导出 `XDG_RUNTIME_DIR=/run/user/$UID`（容器内无 systemd-logind，需手动设置，否则 rootless podman 无法定位运行时目录）
- Docker CLI 和 Podman CLI 可同时使用（共存模式）

<a id="jupyter-服务"></a>
## Jupyter 服务

**配置文件**：[config/jupyter_notebook_config.py](../../config/jupyter_notebook_config.py)、[config/supervisor/conf.d/jupyter.conf](../../config/supervisor/conf.d/jupyter.conf)

- Python 环境位于 `/opt/conda`（Miniforge3 + Python 3.14.6 cp314t free-threading），JupyterLab 安装在 conda 环境中
- 默认监听 `0.0.0.0:8888`
- Notebook 工作目录为 `/workspace`
- token 通过 `JUPYTER_TOKEN` 环境变量控制（默认 `devcontainer123`）
- password 通过 `JUPYTER_PASSWORD` 环境变量控制（可选）
- 默认 CORS 策略同源限制（`JUPYTER_ALLOW_ORIGIN` 可配置）
- 以 devuser 身份运行（非 root）
- 支持 Notebook 和 Lab 两种界面

<a id="健康检查"></a>
## 健康检查

**脚本**：[scripts/healthcheck.sh](../../scripts/healthcheck.sh)

- Dockerfile 中配置 `HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3`
- **设计原则：功能探测 > 存在检查**（进程/socket存在不代表服务可用，进程可能挂起/僵尸）
- **超时预算**（总超时10s，预留1s开销，9s用于探测）：SSH 2s + Docker 5s(ps 3s+info 2s) + Podman 3s + Jupyter 2s
- healthcheck.sh 按条件检查启用的服务：
  - SSH：pgrep sshd 进程 + `/dev/tcp/127.0.0.1/${SSH_PORT}` 端口探测（timeout=2s，不依赖 nc/netcat）
  - Docker：`pgrep -x dockerd` 检测 DinD/DooD 模式 → 检查 `/var/run/docker.sock` 存在且可读写 → `timeout 3 docker ps` 最小功能探测（证明 daemon 可响应请求）→ `timeout 2 docker info` 附带版本信息（失败不判定不健康）
  - Podman：检查 binary 存在 → `timeout 3 su - <NON_ROOT_USER> -c "XDG_RUNTIME_DIR=/run/user/<uid> podman ps"` 最小功能探测（rootless 模式，显式设置 XDG_RUNTIME_DIR 避免容器内无 systemd-logind 导致路径解析失败）
  - Jupyter：pgrep jupyter 进程 + `curl --max-time 2` HTTP API 检测（接受 200/302/401/403）
- 通过 `ENABLE_SSH`、`ENABLE_DOCKER`、`ENABLE_PODMAN`、`ENABLE_JUPYTER` 环境变量控制检查哪些服务（Podman 默认 `no`，rootless 按需模式）
- 所有阻塞调用均设显式 timeout，防止 curl/docker/podman 挂起导致 HEALTHCHECK 被 Docker SIGKILL 中断而丢失诊断信息
- DinD/DooD 自动检测：dockerd 进程存在→DinD；socket 存在但 dockerd 不在→DooD（宿主 socket 挂载）
- 输出结构化日志 `[HEALTHCHECK] service (mode): OK/FAILED (detail)`，最终输出 `STATUS: HEALTHY/UNHEALTHY`

## supervisord 主配置

**配置文件**：[config/supervisord.conf](../../config/supervisord.conf)

- nodaemon=true（前台运行，作为容器主进程）
- logfile=/var/log/supervisor/supervisord.log
- pidfile=/var/run/supervisord.pid
- 包含 `/etc/supervisor/conf.d/*.conf` 子配置
- 所有服务日志输出到 `/var/log/supervisor/`

## 端口映射参考

| 服务 | 容器内端口 | 宿主机映射（默认） | 说明 |
|------|-----------|-------------------|------|
| SSH | 22 | 2222 | SSH 远程连接 |
| Jupyter | 8888 | 8888 | Notebook/Lab Web界面 |
| Docker | unix socket | - | DinD socket 不暴露端口 |
| Podman | unix socket | - | Rootless socket 不暴露端口 |

## 服务启动顺序约束

1. dockerd 必须先启动（startsecs=15），其他服务不依赖 Docker 启动顺序
2. sshd 和 jupyter 可并行启动
3. podman 以 devuser 身份启动，需在用户创建后启动
