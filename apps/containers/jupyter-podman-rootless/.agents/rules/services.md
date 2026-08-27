---
id: "jupyter-services-rules"
title: "服务配置规范"
source: "AGENTS.md#核心约束 + README.md#服务管理"
---
# 服务配置规范（jupyter-podman-rootless）

## supervisord配置

主配置文件：`config/supervisord.conf`

```ini
[supervisord]
nodaemon=true
logfile=/dev/stdout
logfile_maxbytes=0
pidfile=/run/supervisord.pid
user=root

[include]
files=/etc/supervisor/conf.d/*.conf
```

服务配置文件放在`config/supervisor/conf.d/`目录下。

### sshd服务配置（sshd.conf）

```ini
[program:sshd]
command=/usr/sbin/sshd -D
priority=100
autorestart=true
startretries=3
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
```

### jupyter服务配置（jupyter.conf）

Jupyter必须以devuser身份运行，使用su切换：

```ini
[program:jupyter]
command=su - devuser -c "cd /workspace && jupyter lab --config=/home/devuser/.jupyter/jupyter_server_config.py"
priority=200
autorestart=true
startretries=3
directory=/workspace
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
```

## SSH服务配置

配置文件：`config/sshd_config`

关键配置项：
- `Port 22`
- `PermitRootLogin no`（默认，由ALLOW_ROOT_SSH环境变量在entrypoint中覆盖）
- `PasswordAuthentication yes`（支持密码登录）
- `PubkeyAuthentication yes`（支持公钥认证）
- `AuthorizedKeysFile .ssh/authorized_keys`
- `ChallengeResponseAuthentication no`
- `UsePAM yes`
- `X11Forwarding yes`（支持X11 GUI透传）
- `PrintMotd no`
- `AcceptEnv LANG LC_*`（传递locale环境变量）

## Jupyter配置

基础配置文件：`config/jupyter_notebook_config.py`

运行时配置由entrypoint.sh在启动时生成，写入`/home/devuser/.jupyter/jupyter_server_config.d/runtime.py`：
- 端口：8888
- 根目录：/workspace
- ip：0.0.0.0（允许外部访问）
- 不自动打开浏览器
- token认证（优先）或密码认证
- CORS配置（允许跨域访问）

## Podman rootless配置

配置文件：`config/containers/storage.conf`

```toml
[storage]
driver = "fuse-overlayfs"
runroot = "/run/user/1000/containers"
graphroot = "/home/devuser/.local/share/containers"

[storage.options]
[storage.options.overlay]
mount_program = "/usr/bin/fuse-overlayfs"
```

关键配置：
- 存储驱动：fuse-overlayfs（rootless模式必需）
- runroot：`/run/user/1000`（XDG_RUNTIME_DIR）
- graphroot：devuser家目录下
- mount_program：fuse-overlayfs（需要宿主机传--device /dev/fuse）

## 目录与文件权限

容器内关键目录权限：

| 路径 | 所有者 | 权限 | 说明 |
|------|--------|------|------|
| /workspace | devuser:devuser | 755 | 工作目录（挂载点） |
| /home/devuser/.ssh | devuser:devuser | 700 | SSH配置目录 |
| /home/devuser/.ssh/authorized_keys | devuser:devuser | 600 | 授权公钥文件 |
| /home/devuser/.config/containers | devuser:devuser | 755 | Podman配置目录 |
| /run/user/1000 | devuser:devuser | 700 | XDG_RUNTIME_DIR |
| /etc/sudoers.d/devuser | root:root | 440 | sudo配置（GRANT_SUDO=yes时） |

## 端口说明

| 端口 | 协议 | 服务 | 说明 |
|------|------|------|------|
| 22 | TCP | sshd | SSH服务（映射到宿主机2222） |
| 8888 | TCP | jupyter | Jupyter Lab（映射到宿主机8888） |
| 5000 | TCP | model-registry | 本地OCI registry（仅profile: registry启动时） |

## 验证清单

服务配置修改后必须验证：
- [ ] `sshd -t`配置语法正确
- [ ] `supervisord -c config/supervisord.conf -t`配置验证通过
- [ ] sshd启动后可接受连接
- [ ] jupyter启动后可访问http://localhost:8888
- [ ] Podman在devuser下可运行（fuse-overlayfs正常）
- [ ] X11Forwarding启用（xclock等GUI应用可显示）
