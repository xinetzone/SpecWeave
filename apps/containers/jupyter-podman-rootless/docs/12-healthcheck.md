---
id: "jupyter-healthcheck"
title: "健康检查"
source: "README.md#健康检查"
---
# 健康检查

容器内置 HEALTHCHECK，每 30 秒自动检查一次各项服务状态。

## 检查项

健康检查脚本 `scripts/healthcheck.sh` 执行以下检查：

### 致命检查（失败则标记为unhealthy）

1. **sshd 进程检查**
   - 命令：`pgrep sshd`
   - 检查sshd守护进程是否在运行
   - 失败原因：sshd崩溃、配置错误、端口冲突

2. **sshd 端口检查**
   - 命令：TCP连接到127.0.0.1:22
   - 检查sshd是否在监听22端口
   - 失败原因：sshd启动失败、端口未监听

3. **Jupyter 进程检查**
   - 命令：`pgrep -f jupyter`
   - 检查Jupyter进程是否在运行
   - 失败原因：Jupyter崩溃、Python错误、token配置问题

4. **Jupyter HTTP检查**
   - 命令：HTTP请求http://127.0.0.1:8888/api
   - 期望返回码：200/302/401/403（任何正常HTTP响应）
   - 检查Jupyter HTTP服务是否响应
   - 失败原因：Jupyter未启动、端口未监听、内部错误

### 非致命检查（失败仅警告，不影响健康状态）

5. **Podman 可用性检查**
   - 命令：`podman --version`
   - 检查rootless Podman是否可用
   - 非致命：Podman不是核心服务，仅用于容器内运行容器（DinP）场景
   - 失败仅输出警告，不标记容器为unhealthy

## 手动执行健康检查

```bash
# 在宿主机上执行（Podman）
podman exec jupyter-podman /usr/local/bin/healthcheck.sh

# 在宿主机上执行（Docker）
docker exec jupyter-podman /usr/local/bin/healthcheck.sh

# 查看健康检查退出码（0=健康，非0=不健康）
podman exec jupyter-podman /usr/local/bin/healthcheck.sh; echo "Exit code: $?"
```

## 查看健康状态

### 使用容器运行时命令

```bash
# Podman - 查看容器健康状态
podman healthcheck run jupyter-podman

# 查看容器详情中的健康信息
podman inspect jupyter-podman --format '{{.State.Health.Status}}'
podman inspect jupyter-podman --format '{{.State.Health}}'

# Docker - 查看健康状态
docker inspect jupyter-podman --format '{{.State.Health.Status}}'
```

健康状态值：
- `starting`：容器启动中，还未完成第一次健康检查
- `healthy`：所有致命检查通过
- `unhealthy`：一个或多个致命检查失败
- `none`：未配置健康检查

### 使用invoke

```bash
# 查看容器状态（包含健康信息）
invoke status
```

## 健康检查日志

健康检查日志输出到容器日志（stdout/stderr）：

```bash
# 查看容器日志（包含健康检查输出）
podman logs jupyter-podman

# 持续跟踪日志
podman logs -f jupyter-podman

# 使用invoke
invoke logs --follow
```

健康检查日志格式：
```
[HEALTHCHECK] Starting health check...
[HEALTHCHECK] [OK] sshd process running
[HEALTHCHECK] [OK] sshd port 22 listening
[HEALTHCHECK] [OK] jupyter process running
[HEALTHCHECK] [OK] jupyter HTTP responding
[HEALTHCHECK] [OK] podman available
[HEALTHCHECK] All checks passed.
```

## 健康检查配置

HEALTHCHECK在Containerfile中定义：

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD /usr/local/bin/healthcheck.sh
```

参数说明：
- `--interval=30s`：每30秒执行一次检查
- `--timeout=10s`：单次检查超时时间10秒
- `--start-period=60s`：容器启动后60秒内检查失败不计入重试（给服务启动时间）
- `--retries=3`：连续3次失败才标记为unhealthy

## 常见健康失败排查

### sshd检查失败

```bash
# 查看sshd日志
podman logs jupyter-podman | grep sshd

# 检查sshd配置
podman exec jupyter-podman sshd -t

# 手动启动sshd查看错误
podman exec jupyter-podman /usr/sbin/sshd -D
```

常见原因：
- SSH host keys未生成（entrypoint步骤2失败）
- sshd_config配置错误
- 22端口被占用

### Jupyter检查失败

```bash
# 查看Jupyter日志
podman logs jupyter-podman | grep jupyter

# 手动检查Jupyter进程
podman exec jupyter-podman pgrep -af jupyter

# 手动测试HTTP端点
podman exec jupyter-podman curl -v http://localhost:8888/api
```

常见原因：
- Jupyter token/密码配置错误
- Python环境问题
- 8888端口被占用
- free-threading兼容性问题（可尝试切换到cp314构建）

### Podman检查失败（非致命）

```bash
# 检查fuse设备
podman exec jupyter-podman ls -la /dev/fuse

# 检查subuid/subgid配置
podman exec jupyter-podman cat /etc/subuid
podman exec jupyter-podman cat /etc/subgid

# 手动测试podman
podman exec -u devuser jupyter-podman podman info
```

常见原因：
- 未传`--device /dev/fuse`参数（invoke run自动添加，直接用podman run需手动添加）
- subuid/subgid配置缺失
- SELinux标签问题（需要`--security-opt label=disable`）

## 自定义健康检查

如需添加自定义检查项，可修改`scripts/healthcheck.sh`脚本。检查项分为：
- 致命检查：任何一个失败返回非0退出码
- 警告检查：失败仅输出[WARN]，不影响退出码

脚本结构：
```bash
#!/bin/bash
set -e

# 致命检查1
if ! pgrep sshd > /dev/null; then
    echo "[HEALTHCHECK] [FAIL] sshd process not found"
    exit 1
fi
echo "[HEALTHCHECK] [OK] sshd process running"

# ... 更多检查 ...

echo "[HEALTHCHECK] All checks passed."
exit 0
```
