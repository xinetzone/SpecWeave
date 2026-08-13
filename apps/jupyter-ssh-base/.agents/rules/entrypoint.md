---
id: "jupyter-ssh-entrypoint-rules"
title: "Entrypoint 启动脚本规范"
source: "AGENTS.md#项目特有约束"
---
# Entrypoint 启动脚本规范（jupyter-ssh-base）

## 基本职责

entrypoint.sh 是容器的入口点（PID 1 通过 tini 管理），负责初始化环境、启动服务、处理信号。

## 必须包含的功能

1. **详细日志输出**：每个关键步骤输出 `[INFO]/[OK]/[WARN]/[ERROR]` 前缀日志，便于排查启动问题
2. **权限修复**：确保 `/workspace` 和 `/home/jupyteruser` 目录权限正确（属于 jupyteruser）
3. **信号处理**：正确处理 SIGTERM/SIGINT 信号，优雅关闭 supervisord 管理的所有服务
4. **密码初始化**：
   - 从 `USER_PASSWORD` 环境变量读取密码
   - 未设置时生成随机密码并输出到日志
   - 使用 `chpasswd` 动态设置，禁止硬编码密码到镜像
5. **SSH 主机密钥生成**：容器启动时重新生成 ED25519/RSA host keys，确保每个容器实例密钥唯一
6. **Jupyter 动态配置**：根据环境变量（JUPYTER_TOKEN/JUPYTER_PASSWORD/JUPYTER_ALLOW_ORIGIN）生成运行时配置
7. **命令模式支持**：如果传入命令（如 `bash`），直接 exec 该命令，不启动 supervisord 服务
8. **sudo 权限配置**：`GRANT_SUDO=yes` 时动态添加 jupyteruser 到 sudoers（NOPASSWD）

## 日志规范

启动脚本日志使用中文（运行时日志，无编码问题）：
```bash
echo "[INFO] 初始化 SSH 主机密钥..."
echo "[OK] SSH 主机密钥已生成"
echo "[INFO] 设置用户密码..."
echo "[WARN] 未设置 USER_PASSWORD，已生成随机密码: xxxxxx"
```

## 信号处理

```bash
cleanup() {
    echo "[INFO] 接收到终止信号，正在关闭服务..."
    supervisorctl stop all
    exit 0
}
trap cleanup SIGTERM SIGINT
```

## 执行顺序

1. 输出启动 banner 和构建信息
2. 生成/验证 SSH host keys
3. 设置用户密码（从环境变量或随机生成）
4. 配置 sudo 权限（如启用）
5. 修复目录权限（/workspace、/home/jupyteruser）
6. 生成 Jupyter 运行时配置
7. 如果有命令参数 → exec 命令
8. 否则 → exec tini -- supervisord -n -c /etc/supervisor/supervisord.conf

## 反模式

- ❌ 不要在 entrypoint.sh 中执行 apt-get install 或其他耗时的构建操作
- ❌ 不要在 entrypoint.sh 中硬编码密码或密钥
- ❌ 不要用 `&` 后台启动服务然后 `wait`（必须使用 supervisord 管理）
- ❌ 不要忽略 exec（直接调用 supervisord 而不 exec，会导致 tini 无法正确转发信号）
