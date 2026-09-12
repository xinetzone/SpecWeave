---
id: "jupyter-entrypoint-rules"
title: "Entrypoint 启动脚本规范"
source: "README.md#7步启动流程"
---
# Entrypoint 启动脚本规范（jupyter-podman-rootless）

## 基础约定

- 入口脚本：`entrypoint.sh`，使用bash编写，开头必须有`set -euo pipefail`
- PID 1：tini作为init进程处理信号转发和僵尸进程回收
- 日志格式：使用彩色日志库`scripts/lib/logging.sh`，输出`[INFO]/[OK]/[WARN]/[ERROR]`前缀
- DEBUG模式：`DEBUG=1`时启用`set -x`调试输出
- 启动完成后exec supervisord -n（nodaemon模式），接管PID 1

## 7步启动流程

### [1/7] setup_passwords() — 配置用户密码

- devuser密码：优先使用`USER_PASSWORD`环境变量，未设置则自动生成16位随机密码
- root密码：仅当`ALLOW_ROOT_SSH=yes`时设置，优先使用`ROOT_PASSWORD`，未设置则随机生成
- 密码通过`chpasswd`设置
- 密码生成后打印到日志（仅首次启动，生产环境建议通过SSH公钥认证）

### [2/7] generate_host_keys() — 生成SSH host keys

- 清理镜像中预装的SSH主机密钥（安全要求，不使用预生成密钥）
- 生成ed25519和rsa类型的host key：
  ```bash
  ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -N "" -q
  ssh-keygen -t rsa -b 4096 -f /etc/ssh/ssh_host_rsa_key -N "" -q
  ```
- 设置正确的权限（600）

### [3/7] configure_sshd() — 配置sshd

- 根据`ALLOW_ROOT_SSH`环境变量设置`PermitRootLogin`（yes/no）
- 根据`SSHD_PORT`环境变量设置监听端口（默认`22`，非法值直接报错退出）：`config/sshd_config` 中的 `Port` 仅为默认值，启动时由 entrypoint 重写。**host 网络模式下必须设 >=1024**——rootless Podman 中容器 root 映射为宿主非特权 UID，绑定特权端口 22 会被拒绝（`Bind to port 22 ... Permission denied`，sshd 随即 FATAL）
- 确保PasswordAuthentication启用（支持密码登录，公钥登录优先）
- 配置AuthorizedKeysFile路径
- 执行`sshd -t`验证配置语法正确性

### [4/7] setup_podman() — 初始化rootless Podman环境

仅当devuser首次启动容器时执行，分两条分支：

**B-scheme（宿主 socket 直通，优先）**：当宿主 `/run/user/<host-uid>/podman/podman.sock` 已 bind-mount 进容器同路径时，复用宿主 daemon，绕过 WSL 三层 userns 嵌套（自建 daemon 会触发 `newuidmap: write to uid_map failed: Operation not permitted`）：

- 在 devuser 可控目录建符号链接指向宿主 socket，导出 `CONTAINER_HOST` / `XDG_RUNTIME_DIR`
- **独立 shell 桥接（Containerfile Layer 3 烘焙，2026-09-12）**：entrypoint 的 `export CONTAINER_HOST` 只进入 supervisord→jupyter 进程子树；SSH 登录 / `podman exec` / Jupyter·IDE 终端等**独立 shell** 只继承容器配置 env 里的 `HOST_PODMAN_SOCK`，会静默落回容器内 rootless 并撞 `newuidmap ... Operation not permitted`。故镜像必须同时提供：① `/etc/profile.d/80-podman-host-socket.sh`（登录 shell，条件：`CONTAINER_HOST` 未显式设置 + `HOST_PODMAN_SOCK` 非空 + 是 socket 文件 → `export CONTAINER_HOST=unix://$HOST_PODMAN_SOCK`）；② devuser `~/.bashrc` source 同一文件（Jupyter 终端是非登录交互 shell，不读 profile.d）；③ `ENV BASH_ENV=/etc/profile.d/80-podman-host-socket.sh` 覆盖非交互非登录 bash（`podman exec ... bash -c` / cron / 脚本，两者都不读）。守卫语义：显式 `CONTAINER_HOST`（tcp/远程 daemon）优先；`HOST_PODMAN_SOCK= <cmd>` 可强制回退本地；socket 缺失时 no-op，回退分支不受影响
- **独立 shell 的注入式 XDG_RUNTIME_DIR 属主（2026-09-12）**：GUI 透传经容器配置注入 `XDG_RUNTIME_DIR=/tmp/runtime-user`，该挂载点父目录由 podman 自动建为 root:0755；独立 shell 不继承 entrypoint 导出的 `/run/user/<uid>`，devuser 在其中 `mkdir libpod` 会被拒（`Failed to obtain podman configuration: mkdir /tmp/runtime-user/libpod: permission denied`）。entrypoint 必须在导出 XDG 前对 inherited XDG 目录（存在且不等于 `${podman_run_dir}`）**只 chown 目录本身**——严禁 `-R`（内含 wayland-0 单文件 bind-mount，与 podman.sock 穿透同红线）
- **socket 属组衔接（EACCES 修复 · 见 `apps/containers/client/README.md §5.4 C-I2`）**：宿主 socket（宿主 `<uid>:<gid>` 0660）经 userns 映射进容器后呈现为 `root:root 0660`，devuser 是非 root UID（固定 1000，≠0）且未入组 → `socket.connect()` 直接 EACCES。故用 `stat -Lc %G`（空/UNKNOWN 回退 `%g`）解析 socket 属组并 `usermod -aG <组> ${NON_ROOT_USER}`；`stat` 失败必须 `log_warn`，禁止静默
- **时机关键**：`usermod` 必须在 `exec supervisord` **之前**完成——supervisord 4.3.0 `drop_privileges()` 在 spawn 子进程时按该时刻 `/etc/group` 成员关系 `os.setgroups()`；已在运行的 jupyter 进程补充组已固定，不受影响
- **自验证**：以 devuser 身份实测 socket 可读写（`su - ${NON_ROOT_USER} -c "test -r ... && test -w ..."`），失败仅 `log_warn` 不阻断启动
- **红线**：严禁 `chmod 666` / `chown` 宿主 socket（会破坏宿主侧权限）；入组会扩大 devuser 组权限，属可接受代价

**回退分支（无宿主 socket）**：容器内自建 rootless daemon：

- 确保`/dev/fuse`设备权限正确（需要宿主机传`--device /dev/fuse`）
- 创建devuser的Podman配置目录：`~/.config/containers/`
- 写入storage.conf（fuse-overlayfs存储驱动配置）
- 设置 XDG_RUNTIME_DIR 为 `id -u ${NON_ROOT_USER}` 派生的 `/run/user/<uid>`（devuser 固定 UID 1000，但脚本仍以用户名动态计算、**不写死数值**），并创建目录、设置正确权限，同时导出 `CONTAINER_HOST` / `XDG_RUNTIME_DIR` 供 supervisord 子进程经 `%(ENV_x)s` 继承
- **socket 挂载点 chown 禁令**（2026-09-11 事故）：B-scheme 单文件 bind-mount 的宿主 `podman.sock` 位于 `${XDG_RUNTIME_DIR}/podman/` 下，对 `${podman_run_dir}` 或该 podman 目录执行 `chown -R` 会穿透挂载点把**宿主 socket inode** 改成 subuid 映射属主（实测 525287:525287），sshd 转发随即拒连、Windows podman CLI 全断。只能 chown/chmod 目录本身，子树白名单仅 `libpod/` 可递归；ln 链接须先判 source==target 幂等跳过
- 执行`podman info`触发Podman首次初始化（拉取pause镜像等）
- 验证Podman可在rootless模式下运行

### [5/7] setup_ssh_keys() — 注入SSH公钥

- 如果设置了`SSH_PUBLIC_KEY`环境变量，追加到devuser的`~/.ssh/authorized_keys`
- 设置正确的权限：.ssh目录700，authorized_keys文件600
- 如果设置了`GRANT_SUDO=yes`，配置devuser无密码sudo（写入/etc/sudoers.d/devuser）

### [6/7] setup_jupyter() — 生成Jupyter运行时配置

- 优先使用`JUPYTER_TOKEN`环境变量，未设置则自动生成32位随机token
- 如果设置了`JUPYTER_PASSWORD`，生成密码hash并配置密码认证
- 配置Jupyter端口（默认8888）、根目录（/workspace）、CORS设置
- 将运行时配置写入`/home/devuser/.jupyter/jupyter_server_config.d/`
- 确保配置文件所有者为devuser

### [7/7] print_access_info() — 打印访问信息

启动完成后打印彩色访问信息：
- SSH连接命令：`ssh -p <port> devuser@localhost`
- Jupyter Lab URL：`http://localhost:<port>/lab?token=<token>`
- 如果启用了sudo，提示sudo已授予
- Podman可用性状态
- ML工具（omlmd/olot）可用性提示
- 如果设置了REGISTRY_PORT，提示本地模型仓库地址

最后执行：
```bash
exec supervisord -n -c /etc/supervisor/supervisord.conf
```

## 服务管理（supervisord）

supervisord配置在`config/supervisord.conf`，管理以下服务：

| 服务 | 用户 | 优先级 | 端口 | 说明 |
|------|------|--------|------|------|
| sshd | root | 100 | 22（由`SSHD_PORT`覆盖） | SSH守护进程 |
| jupyter | devuser | 200 | 8888 | Jupyter Lab（`jupyter.conf` 的 `user=devuser`；`CONTAINER_HOST`/`XDG_RUNTIME_DIR` 经 `%(ENV_x)s` 继承 entrypoint 动态导出值） |

- 服务异常自动重启：`autorestart=true`，`startretries=3`
- 日志输出到stdout/stderr（nodaemon模式）
- supervisord本身由tini管理，接收SIGTERM/SIGINT信号时优雅关闭

## 健康检查脚本

健康检查脚本：`scripts/healthcheck.sh`，每30秒执行一次：

1. **sshd进程检查**：`pgrep sshd`（致命）
2. **sshd端口检查**：TCP连接到127.0.0.1:22（致命）
3. **Jupyter进程检查**：`pgrep -f jupyter`（致命）
4. **Jupyter HTTP检查**：请求http://127.0.0.1:8888/api，期望200/302/401/403（致命）
5. **Podman可用性检查**：`podman --version`（非致命，仅警告）

检查失败时返回非0退出码，Docker/Podman标记容器为unhealthy。

## 信号处理

- tini作为PID 1，负责转发SIGTERM/SIGINT信号给supervisord
- supervisord接收到信号后优雅关闭sshd和jupyter
- 禁止使用`kill -9`强制终止，避免数据丢失和僵尸进程

## 验证清单

entrypoint.sh修改后必须验证：
- [ ] `bash -n entrypoint.sh`语法检查通过
- [ ] 启动日志有清晰的[1/7]-[7/7]步骤标记
- [ ] SSH可连接，密码/公钥认证正常
- [ ] Jupyter可访问，token/密码认证正常
- [ ] devuser下podman可运行（podman info成功）
- [ ] GRANT_SUDO=yes时sudo无需密码
- [ ] ALLOW_ROOT_SSH=yes时root可SSH登录
- [ ] DEBUG=1时有set -x调试输出
- [ ] 健康检查脚本可正常执行
