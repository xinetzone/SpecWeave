---
id: "jupyter-ssh-services-rules"
title: "服务管理规范（supervisord + SSH + Jupyter）"
source: "AGENTS.md#项目特有约束"
---
# 服务管理规范（jupyter-ssh-base）

## 服务管理方案

必须使用 **supervisord** 管理 sshd 和 jupyter notebook 双服务，确保两个进程都能正确启动、监控和自动重启。

- 主配置：`/etc/supervisor/supervisord.conf`
- 服务配置目录：`/etc/supervisor/conf.d/`
- 日志目录：`/var/log/supervisor/`

## SSH 服务配置

配置文件：`config/sshd_config`（复制到 `/etc/ssh/sshd_config`）

### 核心配置项

| 配置 | 值 | 说明 |
|------|-----|------|
| Port | 22 | 默认监听 22 端口 |
| PermitRootLogin | no | 默认禁用 root 登录（`ALLOW_ROOT_SSH=yes` 环境变量可启用） |
| PasswordAuthentication | yes | 支持密码认证 |
| PubkeyAuthentication | yes | 支持密钥认证 |
| HostKey /etc/ssh/ssh_host_ed25519_key | 优先 | ED25519 密钥优先（现代、安全、性能好） |
| HostKey /etc/ssh/ssh_host_rsa_key | 回退 | RSA 密钥作为兼容回退 |
| PermitEmptyPasswords | no | 禁止空密码 |
| ChallengeResponseAuthentication | no | 禁用挑战响应认证 |
| UsePAM | yes | 启用 PAM（用于 chpasswd 密码认证） |

### SSH 密钥安全

- Host keys **必须在容器启动时重新生成**（entrypoint.sh 中 `ssh-keygen -A`），不能打包到镜像中
- 支持用户通过 `-v ~/.ssh/authorized_keys:/home/jupyteruser/.ssh/authorized_keys` 挂载公钥
- 用户 `.ssh` 目录权限必须为 700，authorized_keys 权限必须为 600

## Jupyter Notebook 配置

配置文件：`config/jupyter_notebook_config.py`（基础配置）+ 运行时动态配置（entrypoint.sh 生成）

### 核心配置项

| 配置 | 值 | 说明 |
|------|-----|------|
| ip | '0.0.0.0' | 监听所有地址，允许外部访问 |
| port | 8888 | 默认端口 8888 |
| notebook_dir | '/workspace' | Notebook 工作目录 |
| allow_origin | '' | 默认 CORS 同源限制（`JUPYTER_ALLOW_ORIGIN` 可配置） |
| token | 环境变量 | 从 `JUPYTER_TOKEN` 读取（未设置则生成随机token） |
| password | 环境变量 | 从 `JUPYTER_PASSWORD` 读取（哈希后设置） |
| open_browser | False | 容器中不自动打开浏览器 |
| disable_check_xsrf | False | 启用 XSRF 保护 |

### 认证方式

- Token 认证：`JUPYTER_TOKEN=mysecret` → URL 访问 `/?token=mysecret`
- 密码认证：`JUPYTER_PASSWORD=mypassword` → 登录页面输入密码
- 无认证：不设置两者时生成随机 token，日志输出供首次访问使用

## Supervisord 服务配置

每个服务一个独立 `.conf` 文件放在 `config/supervisor/conf.d/`：

### sshd.conf

```ini
[program:sshd]
command=/usr/sbin/sshd -D
priority=10
autostart=true
autorestart=true
stopsignal=TERM
stopwaitsecs=5
stdout_logfile=/var/log/supervisor/sshd.log
stdout_logfile_maxbytes=10MB
stderr_logfile=/var/log/supervisor/sshd-error.log
```

### jupyter.conf

```ini
[program:jupyter]
command=/opt/venv/bin/jupyter notebook --config=/etc/jupyter/jupyter_notebook_config.py
priority=20
autostart=true
autorestart=true
stopsignal=TERM
stopwaitsecs=10
stdout_logfile=/var/log/supervisor/jupyter.log
stdout_logfile_maxbytes=10MB
stderr_logfile=/var/log/supervisor/jupyter-error.log
user=jupyteruser
directory=/workspace
```

### supervisord.conf 主配置

- nodaemon=true（前台运行，容器模式）
- logfile=/var/log/supervisor/supervisord.log
- pidfile=/var/run/supervisord.pid
- childlogdir=/var/log/supervisor/
- [include] files=/etc/supervisor/conf.d/*.conf

## 健康检查

健康检查脚本：`scripts/healthcheck.sh`，同时检查两个服务：

1. **sshd 检查**：
   - 进程检查：`pgrep sshd`
   - 端口检查：`nc -z localhost 22` 或 `ss -tlnp | grep :22`
2. **jupyter 检查**：
   - 进程检查：`pgrep -f "jupyter-notebook"`（以 jupyteruser 用户运行）
   - HTTP 检查：`curl -s -o /dev/null -w "%{http_code}" http://localhost:8888/api`
3. **退出码**：两个服务都健康返回 0，任一不健康返回 1

Dockerfile HEALTHCHECK 指令：
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh
```

## 验证清单

- [ ] `supervisorctl status` 显示 sshd 和 jupyter 都是 RUNNING 状态
- [ ] SSH 连接：`ssh -p 2222 jupyteruser@localhost` 可正常登录
- [ ] Jupyter 访问：浏览器打开 http://localhost:8888 可正常使用
- [ ] ED25519 host key 存在：`ls /etc/ssh/ssh_host_ed25519_key*`
- [ ] 健康检查脚本返回 0
- [ ] 容器重启后两个服务自动恢复
