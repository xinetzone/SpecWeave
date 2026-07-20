---
id: "dind-entrypoint-rules"
title: "Entrypoint 启动脚本规范"
---
# Entrypoint 启动脚本规范（docker-ssh-dind）

## 基础约定

- 使用bash（`#!/bin/bash`），开头加`set -e`确保错误退出
- 支持`DEBUG=1`环境变量开启调试模式（`set -x`）
- 必须使用tini作为init进程（在Containerfile ENTRYPOINT中指定）
- 日志使用带时间戳的统一格式

## 日志规范

```bash
log_info()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO]  $*"; }
log_warn()  { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARN]  $*" >&2; }
log_error() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $*" >&2; }
```

- 关键步骤必须输出INFO日志
- 错误条件输出ERROR日志并exit 1
- 非致命问题输出WARN日志
- 构建时注释用英文（避免编码问题），运行时日志可用中文或英文

## 启动流程（6步）

按以下顺序执行，每步有明确的日志标记`[Step N/6]`：

1. **setup_root_password**：配置root密码（ROOT_PASSWORD环境变量或随机生成）
2. **generate_host_keys**：生成SSH主机密钥（若不存在）
3. **configure_sshd**：配置sshd（PermitRootLogin可通过ALLOW_ROOT_SSH切换），验证语法
4. **setup_ssh_keys**：注入SSH_PUBLIC_KEY到root和ai用户的authorized_keys
5. **start_docker**：启动dockerd，等待就绪（最多60秒），失败时输出dockerd.log
6. **start_sshd**：前台启动sshd -D -e（exec替换进程，确保信号正确传递）

## 错误处理

- Docker启动失败时：输出dockerd.log最后30行，列出常见原因（privileged/cgroup/overlay2），exit 1
- SSH配置错误时：输出sshd -T详细错误，exit 1
- 捕获SIGTERM/SIGINT信号，优雅关闭Docker daemon
- 等待Docker就绪时每10秒输出进度，20秒后开始输出最近日志帮助诊断

## 系统诊断（启动时必执行）

在所有步骤之前执行`diagnose_system()`，收集：
- OS/kernel/arch/timezone/locale/user信息
- cgroup版本（v1/v2）
- Docker/Containerd/SSHD版本
- 构建信息（/etc/dind-build-info）
- privileged权限检查（dummy接口创建测试）
- cgroup挂载检查（未挂载则尝试mount）

## 信号处理

```bash
cleanup() {
    log_info "Received shutdown signal, stopping services..."
    if [ -n "$DOCKER_PID" ]; then
        kill -TERM "$DOCKER_PID" 2>/dev/null || true
        wait "$DOCKER_PID" 2>/dev/null || true
    fi
    exit 0
}
trap cleanup SIGTERM SIGINT
```

## 验证清单

- [ ] 脚本可执行权限（chmod +x）
- [ ] 启动日志清晰，包含banner和步骤标记
- [ ] Docker启动失败时输出诊断信息
- [ ] docker exec进入容器执行`su - ai -c "docker ps"`正常
- [ ] Ctrl+C（docker stop）能优雅关闭容器
