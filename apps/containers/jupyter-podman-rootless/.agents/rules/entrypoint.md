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
- 确保PasswordAuthentication启用（支持密码登录，公钥登录优先）
- 配置AuthorizedKeysFile路径
- 执行`sshd -t`验证配置语法正确性

### [4/7] setup_podman() — 初始化rootless Podman环境

仅当devuser首次启动容器时执行：

- 确保`/dev/fuse`设备权限正确（需要宿主机传`--device /dev/fuse`）
- 创建devuser的Podman配置目录：`~/.config/containers/`
- 写入storage.conf（fuse-overlayfs存储驱动配置）
- 设置XDG_RUNTIME_DIR环境变量：`/run/user/1000`
- 创建XDG_RUNTIME_DIR并设置正确权限
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
| sshd | root | 100 | 22 | SSH守护进程 |
| jupyter | root | 200 | 8888 | Jupyter Lab（通过su切换到devuser运行） |

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
