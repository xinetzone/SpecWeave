---
id: "devcontainer-entrypoint-rules"
title: "Entrypoint 启动脚本规范"
source: "AGENTS.md#项目特有约束"
---
# Entrypoint 启动脚本规范（devcontainer-base）

## 基础约定

- 使用 bash（`#!/bin/bash`），开头加 `set -e` 确保错误退出
- 支持 `DEBUG=1` 环境变量开启调试模式（`set -x`）
- 必须使用 tini 作为 init 进程（在 Dockerfile ENTRYPOINT 中指定：`ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]`）
- 日志使用统一格式（带时间戳、级别标记）
- 启动时输出 banner 和系统诊断信息

## 日志规范

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

## 启动流程

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

## 信号处理

- 使用 tini 作为 PID 1，正确处理僵尸进程
- supervisord 作为前台主进程管理所有子服务，接收 SIGTERM 时优雅关闭
- 不使用 `&` 后台启动主服务后 wait 的模式（信号传递不可靠）

## Docker DinD 初始化

若启用 DinD 模式（默认）：
- 确保 `/var/lib/docker` 目录存在（建议挂载 volume 持久化）
- 确保 `/etc/docker/daemon.json` 配置正确（storage-driver/iptables/log-opts）
- dockerd 由 supervisord 管理启动，startsecs=15 等待初始化
- 健康检查脚本验证 docker.sock 可访问

## 命令模式

```bash
# 如果传入了命令参数（非supervisord启动），直接exec
if [ $# -gt 0 ]; then
    exec "$@"
fi
```

支持 `docker run -it --rm devcontainer-base bash` 调试模式。

## 验证清单

- [ ] 脚本可执行权限（chmod +x）
- [ ] 启动日志清晰，包含 banner 和系统诊断信息
- [ ] Docker 启动失败时输出 dockerd.log 帮助诊断
- [ ] `docker exec` 进入容器执行 `su - devuser -c "docker ps"` 正常
- [ ] `docker exec` 进入容器执行 `su - devuser -c "sudo -n whoami"`（GRANT_SUDO=yes 时）
- [ ] Ctrl+C（docker stop）能优雅关闭容器
- [ ] SSH 密码/密钥认证均正常工作
- [ ] Jupyter token 通过环境变量正确注入
- [ ] 命令模式（传入 bash）直接进入 shell，不启动服务
