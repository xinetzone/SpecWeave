# devcontainer-base 最佳实践

> 本文档记录构建多服务开发容器（SSH + Docker DinD + Jupyter + Podman）过程中踩过的坑与可复用模式。

---

## 1. Docker DinD supervisord 无冲突配置

### 问题描述

在容器内通过 supervisord 管理 dockerd 时，若命令行参数与 `/etc/docker/daemon.json` 同时指定相同配置项，dockerd 会直接崩溃并反复重启：

```
unable to configure the Docker daemon with file /etc/docker/daemon.json:
the following directives are specified both as a flag and in the configuration file:
iptables: (from flag: false, from file: false),
storage-driver: (from flag: overlay2, from file: overlay2),
userland-proxy: (from flag: false, from file: false)
```

即使值相同也不行——Docker 严格禁止重复配置。

### 正确做法：daemon.json 作为唯一配置源

**supervisord 配置 (`config/supervisor/conf.d/dockerd.conf`)：**

```ini
[program:dockerd]
user=root
command=/usr/bin/dockerd --log-level=error
directory=/
autorestart=true
startretries=5
startsecs=15
priority=150
stopsignal=SIGTERM
stopwaitsecs=30
```

**daemon.json 承载所有配置：**

```json
{
  "storage-driver": "overlay2",
  "iptables": false,
  "userland-proxy": false,
  "log-level": "error",
  "hosts": ["unix:///var/run/docker.sock", "tcp://0.0.0.0:2375"]
}
```

### 反模式

```ini
# ❌ 错误：与 daemon.json 重复
command=/usr/bin/dockerd --iptables=false --storage-driver=overlay2 --userland-proxy=false --log-level=error
```

### 检查清单

- [ ] dockerd 命令行仅使用 `--log-level` 等非冲突参数
- [ ] storage-driver、iptables、userland-proxy、hosts 等全部放入 daemon.json
- [ ] supervisord 的 `startsecs` 设置为 15s（给 dockerd 足够初始化时间）
- [ ] 健康检查在 supervisord 报告 RUNNING 后再验证 docker socket

---

## 2. Docker Compose 环境变量覆盖模式

### 问题描述

在 `docker-compose.yml` 中使用硬编码赋值语法 `- KEY=value` 时，宿主机 shell 设置的同名环境变量无法覆盖该值：

```yaml
# ❌ 错误：硬编码值，无法被外部环境变量覆盖
environment:
  - USER_PASSWORD=changeme      # USER_PASSWORD=xxx docker compose up 不生效！
```

### 正确做法：变量替换语法 + YAML 锚点

```yaml
# 公共环境变量块（YAML 锚点）
x-common-env: &common-env
  TZ: ${TZ:-Asia/Shanghai}
  LANG: ${LANG:-zh_CN.UTF-8}
  USER_PASSWORD: ${USER_PASSWORD:-changeme}
  JUPYTER_TOKEN: ${JUPYTER_TOKEN:-devcontainer123}
  GRANT_SUDO: ${GRANT_SUDO:-yes}

services:
  myservice:
    image: myimage:latest
    ports:
      - "${SSH_PORT:-2222}:22"        # 端口也支持变量覆盖
      - "${JUPYTER_PORT:-8888}:8888"
    environment:
      <<: *common-env                 # 引用公共块
      ENABLE_DOCKER: ${ENABLE_DOCKER:-yes}   # 服务特有变量
```

### 语法说明

| 语法 | 含义 |
|------|------|
| `${VAR}` | 使用环境变量 VAR 的值，未设置则为空字符串 |
| `${VAR:-default}` | 使用 VAR 的值，未设置则使用 default |
| `${VAR:?error}` | VAR 必须设置，否则报错退出 |
| `<<: *anchor` | YAML 锚点展开，合并映射 |

### 使用示例

```bash
# 使用默认值
docker compose --profile dind up -d

# 覆盖密码和端口
USER_PASSWORD=mypassword SSH_PORT=2200 docker compose --profile dind up -d

# 通过 .env 文件自动加载（推荐）
cp .env.example .env
# 编辑 .env 后直接 docker compose up
```

### 检查清单

- [ ] 所有可配置项使用 `${VAR:-default}` 语法
- [ ] 公共环境变量提取为 `x-common-env` YAML 锚点
- [ ] 端口映射同样使用变量替换
- [ ] 提供 `.env.example` 模板文件
- [ ] `.env` 加入 `.gitignore`（防止凭据泄露）

---

## 3. 多阶段构建镜像源切换模式

### 问题描述

国内环境拉取 Ubuntu apt 包和 PyPI 包速度慢或超时，需要在构建时快速切换到国内镜像源。

### 正确做法：build-arg + sed 条件替换

**Dockerfile 中的模式（builder 和 runtime 双阶段都要配置）：**

```dockerfile
ARG APT_MIRROR=official
ARG PIP_MIRROR=official

# ── Builder 阶段 ──
FROM ubuntu:26.04 AS builder
ARG APT_MIRROR
ARG PIP_MIRROR

RUN if [ "${APT_MIRROR}" = "aliyun" ]; then \
        sed -i 's|http://archive.ubuntu.com|http://mirrors.aliyun.com|g; s|http://security.ubuntu.com|http://mirrors.aliyun.com|g' /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null || \
        sed -i 's|http://archive.ubuntu.com|http://mirrors.aliyun.com|g; s|http://security.ubuntu.com|http://mirrors.aliyun.com|g' /etc/apt/sources.list 2>/dev/null || true; \
    elif [ "${APT_MIRROR}" = "tuna" ]; then \
        sed -i 's|http://archive.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g; s|http://security.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null || true; \
    fi && \
    apt-get update && apt-get install -y ...

# PyPI 镜像
RUN if [ "${PIP_MIRROR}" = "aliyun" ]; then \
        pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/; \
    elif [ "${PIP_MIRROR}" = "tuna" ]; then \
        pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/; \
    fi && \
    pip install --no-cache-dir -r requirements.txt

# ── Runtime 阶段（同样需要配置 APT_MIRROR） ──
FROM ubuntu:26.04
ARG APT_MIRROR
# ... 同样的 sed 替换逻辑
```

**构建脚本封装：**

```bash
# 一键国内镜像
bash scripts/build.sh --cn

# 分别指定
bash scripts/build.sh --apt-mirror tuna --pip-mirror aliyun

# .env 文件配置
echo "APT_MIRROR=aliyun" >> .env
echo "PIP_MIRROR=aliyun" >> .env
bash scripts/build.sh   # 自动加载 .env
```

### 支持的镜像源

| 选项 | APT 源 | PyPI 源 |
|------|--------|---------|
| `official` | archive.ubuntu.com | pypi.org |
| `aliyun` | mirrors.aliyun.com | mirrors.aliyun.com/pypi/simple |
| `tuna` | mirrors.tuna.tsinghua.edu.cn | pypi.tuna.tsinghua.edu.cn/simple |

### 关键点

- builder 和 runtime **两个阶段**都必须配置 APT 镜像源（两个 FROM 指令需要各自 ARG）
- Ubuntu 24.04+ 使用 `ubuntu.sources`（DEB822格式），旧版使用 `sources.list`，sed 需兼容两种格式
- `2>/dev/null || true` 确保其中一种文件不存在时不报错

---

## 4. 容器健康检查与等待策略

### 问题描述

容器启动后服务需要时间初始化（dockerd 约15s，Jupyter 约5-10s），立即验证会失败。

### 正确做法：分层等待 + 轮询健康状态

```bash
# 1. Docker healthcheck（在 Dockerfile/Compose 中定义）
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh

# 2. 启动脚本轮询（start.sh）
local waited=0
while [ $waited -lt $TIMEOUT ]; do
    health=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER" 2>/dev/null)
    case "$health" in
        healthy)    log_ok "All services healthy (${waited}s)"; break ;;
        unhealthy)  log_fatal "Services unhealthy! Check logs." ;;
    esac
    sleep 3
    waited=$((waited + 3))
done

# 3. 健康检查脚本内部（条件化检查）
# 仅检查 ENABLE_*=yes 的服务
```

### 时间参数参考

| 服务 | 启动时间 | start_period | startsecs(supervisor) |
|------|---------|-------------|----------------------|
| sshd | 1-2s | 20s | 1s |
| Jupyter | 5-10s | 45s | 10s |
| dockerd | 15-20s | 60s | 15s |

---

## 5. 非 root 开发用户模式

### 模式要点

```dockerfile
# 创建固定 UID 的开发用户
RUN groupadd -g 1000 devuser && \
    useradd -m -s /bin/bash -u 1000 -g 1000 -G docker,sudo devuser && \
    echo "devuser ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/devuser && \
    chmod 0440 /etc/sudoers.d/devuser

# 确保 docker socket 权限
RUN usermod -aG docker devuser

# entrypoint 中运行时权限修复
# 当挂载宿主目录时，可能需要 chown
if [ "$(stat -c %u /workspace)" != "$(id -u devuser)" ]; then
    chown -R devuser:devuser /workspace
fi
```

### 关键原则

- 用户名为 `devuser`，UID/GID 优先 1000
- 默认加入 `docker` 组（访问 DinD socket）
- sudo 权限通过 `GRANT_SUDO` 环境变量控制，默认开启
- 禁止 root SSH 登录（`ALLOW_ROOT_SSH=yes` 可启用）
- host keys 在容器启动时重新生成（确保唯一性）
