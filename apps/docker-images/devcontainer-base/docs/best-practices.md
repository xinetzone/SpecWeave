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

---

## 6. Docker Socket 挂载的安全风险与使用边界

### 问题描述

DooD (Docker-out-of-Docker) 模式通过挂载 `/var/run/docker.sock` 让容器直接操作宿主机 Docker，但这**等价于授予容器对宿主机的 root 级访问权限**。许多开发者误以为只读挂载 (`:ro`) 或非 root 用户运行可以降低风险，实际并非如此。

### 为什么挂载 Docker Socket = Root 权限？

**1. Docker Daemon 默认以 root 运行**

dockerd 进程在宿主机上以 root 用户运行，通过 socket 发来的任何 API 请求都会以 root 身份执行，容器内用户权限等级不影响 dockerd 的执行权限。

**2. 容器可以通过 socket 轻松逃逸**

容器内只要能访问 socket，就能调用 Docker API 创建特权容器并挂载宿主机根目录：

```bash
# 容器内执行：直接拿到宿主机 root shell
docker run -it --privileged --pid=host -v /:/host ubuntu chroot /host bash
```

这条命令看似"在容器里运行容器"，但实际效果是：
- 通过 socket 指示宿主机 dockerd 创建一个新容器
- 新容器挂载宿主机 `/` 到 `/host`
- chroot 进去后获得宿主机完整 root 权限，可读写任意文件、窃取密钥、安装后门

**3. 容器内可执行的危险操作**

```bash
docker ps                    # 查看宿主机所有容器
docker inspect <container>   # 获取其他容器环境变量（含数据库密码、API密钥）
docker run -v /:/host ...     # 挂载宿主机根目录实现逃逸
docker restart ...           # 重启宿主机上任意容器
docker network ...           # 修改宿主机网络配置
```

**4. `:ro` 只读挂载并不安全**

即使使用 `-v /var/run/docker.sock:/var/run/docker.sock:ro`，**仍然不安全**：
- `ro` 只限制了对 socket 文件本身的写操作
- API 调用是"通过 socket 发送请求"而非"写 socket 文件"，只读挂载不阻止 API 调用
- 你仍然可以发 `docker run`、`docker exec` 等所有修改性指令

### DinD vs DooD 模式安全对比

| 特性 | DinD模式 (`--privileged`) | DooD模式 (挂载socket) |
|------|--------------------------|----------------------|
| 是否需要特权 | ✅ 是 | ❌ 否 |
| 容器隔离 | 完全隔离（嵌套dockerd） | ⚠️ 共享宿主Docker，影响宿主 |
| 安全性 | 中等（特权风险但隔离） | 🔴 低（容器≈宿主root） |
| 镜像持久化 | 需要volume | 宿主镜像共享 |
| 性能 | 稍慢（嵌套） | 快（原生） |
| 适用场景 | 开发环境、需完全隔离的CI | 生产/CI（仅信任容器） |

### 使用场景判定

✅ **可以挂载 socket 的场景**：
- 完全信任容器内运行的代码和用户
- CI 环境（容器本身是受控的构建环境）
- 个人开发机上自己使用
- 容器镜像经过审计、内容确定

❌ **绝对禁止挂载 socket 的场景**：
- 运行不可信代码/第三方镜像（多租户环境）
- 公网可访问的服务容器
- 用户上传/执行任意代码的场景
- 未审计的社区镜像

### 缓解方案

如果必须使用 DooD 模式，可采取以下措施降低风险：

1. **不要加 `--privileged`**：DooD 模式不需要特权标志，这是 DinD 才需要的
2. **使用非 root 用户运行容器**：降低容器内误操作风险，但不能阻止逃逸
3. **使用 Docker Authorization Plugin**：限制 socket 可调用的 API 范围
4. **使用 rootless Docker**：dockerd 本身不以 root 运行，逃逸后权限受限
5. **考虑 Podman 替代**：天然 rootless 架构，无守护进程，无单一 socket 攻击面
6. **镜像最小化**：容器内不装额外工具，减少攻击面

### 反模式

```bash
# ❌ 错误1：公网服务容器挂载宿主docker.sock
docker run -d -p 8080:80 -v /var/run/docker.sock:/var/run/docker.sock my-webapp

# ❌ 错误2：以为ro挂载就安全了
docker run -v /var/run/docker.sock:/var/run/docker.sock:ro my-image  # 仍可逃逸！

# ❌ 错误3：多租户环境中给所有容器挂载socket
# （任何租户都能控制宿主机）
```

### 正确做法

```bash
# ✅ 开发环境使用DinD（完全隔离）
docker compose --profile dind up -d

# ✅ CI中DooD仅用于可信构建镜像
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd):/workspace \
  -w /workspace \
  docker:26-cli \
  docker build -t my-image .

# ✅ 优先使用Podman rootless（无daemon无socket风险）
podman run -d -p 8080:80 my-webapp  # 无需挂载socket，天然安全
```

### 检查清单

- [ ] 已确认容器内运行的代码/镜像是完全可信的
- [ ] DooD 模式**没有**使用 `--privileged` 标志
- [ ] 公网服务容器没有挂载 docker.sock
- [ ] 多租户/共享环境中禁用 DooD，改用 DinD 或 Podman
- [ ] 已考虑 rootless Docker/Podman 作为替代方案
- [ ] docker.sock 挂载权限正确（不向不可信用户开放）
- [ ] README/文档中已明确标注 DooD 的安全风险

---

## 7. 挂载目录权限问题分层解决方案

### 问题描述

Docker 挂载宿主目录时最常见的问题：
- 容器内普通用户对挂载目录无写权限（Permission denied）
- 容器内 root 创建的文件在宿主机显示为 `root` 或 `nobody`，宿主机普通用户无法删除/修改
- 网上搜到的解决方案通常是 `chmod 777` 或 `--privileged`，但这都是安全反模式

**根因**：Linux 内核权限检查基于 **UID/GID 数字**而非用户名，容器内外 UID 环境不一致导致"身份错位"——这不是"有没有 root 密码"的问题，而是"数字 ID 映射断层"。

### 诊断先行（30秒定位问题）

遇到权限问题时，**先诊断再动手**，不要直接上 sudo/chmod 777：

```bash
# 在容器内执行
id                              # 查看当前用户的 UID/GID 数字
stat -c '%u %g %n' /workspace    # 查看挂载目录的属主 UID/GID（数字）
ls -ln /workspace               # 用数字 ID 显示文件属主（不解析用户名）
mount | grep /workspace         # 检查是否是只读挂载（带 (ro, ...)）

# 在宿主机执行
ls -ld /host/path               # 查看宿主目录权限和属主
```

如果 UID 数字不匹配 → 属主问题；如果 UID 匹配但仍无权限 → 检查权限位或只读挂载。

### 分层解决方案（按优先级 P0-P5）

根据场景选择对应方案，优先级从高到低：

#### 🥇 P0（首选）：运行时 UID 对齐（零侵入）

**适用场景**：个人开发机、单用户环境、可写挂载

```bash
# 核心命令：用当前用户 UID/GID 运行容器
docker run --rm -it \
  -v $(pwd):/workspace \
  -w /workspace \
  --user $(id -u):$(id -g) \
  ubuntu:26.04 bash

# docker-compose.yml 示例
services:
  dev:
    image: my-dev-image
    user: ${UID:-1000}:${GID:-1000}
    volumes:
      - ./:/workspace
    working_dir: /workspace
```

**优点**：零镜像修改、安全、无启动延迟、容器内创建的文件自动匹配宿主机属主
**注意事项**：
- 镜像中工作目录需要允许 other 用户读写（Dockerfile 中 `chmod 777 /workspace` 或 `chmod 1777` 粘滞位）
- Mac 用户 UID 通常是 501，Linux 通常是 1000，`$(id -u)` 自动适配
- 容器内该 UID 可能没有对应用户名、没有 home 目录，开发镜像需提前配置

#### 🥈 P1：Entrypoint 条件 chown（透明无感）

**适用场景**：可控 dev 镜像、单用户开发容器、非网络文件系统

在现有第5节基础上增强容错：

```dockerfile
# entrypoint.sh（增强版）
#!/bin/bash
set -e

USER_NAME=devuser
WORKSPACE_DIR=/workspace

# 仅当 UID 不匹配时才 chown，避免无意义 IO
HOST_UID=$(stat -c %u "$WORKSPACE_DIR" 2>/dev/null || echo "0")
CONTAINER_UID=$(id -u "$USER_NAME")

if [ "$HOST_UID" != "0" ] && [ "$HOST_UID" != "$CONTAINER_UID" ]; then
    echo "Adjusting workspace ownership to UID=$HOST_UID..."
    # || true 容错：NFS/CIFS 等网络文件系统可能不支持 chown
    chown -R "$HOST_UID:$HOST_UID" "$WORKSPACE_DIR" 2>/dev/null || true
    # 更新容器内用户 UID/GID 匹配宿主机
    usermod -u "$HOST_UID" "$USER_NAME" 2>/dev/null || true
    groupmod -g "$HOST_UID" "$USER_NAME" 2>/dev/null || true
fi

# 切换到非 root 用户执行后续命令
exec gosu "$USER_NAME" "$@"
```

**优点**：透明无感，用户体验好
**注意事项**：
- 大目录（如 node_modules 几十万个文件）chown 可能耗时 5-30 秒，拖慢启动
- **网络文件系统（NFS/CIFS）必须加 `|| true` 容错**，否则 chown 报错卡住
- 生产环境禁用：chown 可能覆盖宿主机设置的安全权限

#### 🥉 P2：容器已启动应急方案

容器已经启动了才发现有权限问题，不需要删除重建：

```bash
# 方案1：临时以 root 身份进入容器操作
docker exec -u root -it my-container bash

# 方案2：一次性修复挂载目录权限
docker exec -u root my-container chown -R 1000:1000 /workspace

# 方案3：从宿主机直接操作（终极方案，需 root）
# 找到容器进程 PID，然后 nsenter 进入
PID=$(docker inspect --format '{{.State.Pid}}' my-container)
sudo nsenter -t "$PID" -m -u -i -n -p chown -R 1000:1000 /workspace
```

#### 🏅 P3：Named Volume（持久化数据首选）

**适用场景**：数据库数据、构建产物、不需要宿主直接浏览的内容

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:16
    volumes:
      - pgdata:/var/lib/postgresql/data  # named volume，不是 bind mount
volumes:
  pgdata:  # Docker 自动管理属主和权限
```

**优点**：属主自动正确、性能好、Docker 生命周期管理
**陷阱**：named volume 只在**首次为空时**从镜像复制内容，后续镜像更新不会同步——适合"运行时生成"数据，不适合"随镜像更新"的配置/代码

#### 🎖️ P4：Rootless 模式（面向未来）

Podman 原生支持 `--userns=keep-id`，自动映射 UID：

```bash
# Podman（推荐，天然 rootless）
podman run --rm -it -v $(pwd):/workspace:Z --userns=keep-id ubuntu bash

# Docker rootless（需要 daemon 配置）
# 参考：https://docs.docker.com/engine/security/rootless/
```

VS Code Dev Container / GitHub Codespaces 已标准化此模式，是未来趋势。

#### ⚠️ P5（慎用）：精准 capability 提权

**仅限 CI 临时构建场景**，禁止用于长期运行服务：

```bash
# 比 --privileged 安全很多，但仍有风险
docker run --rm -it --cap-add=FOWNER -v $(pwd):/workspace my-builder
```

`CAP_FOWNER` 允许进程绕过属主检查，但不授予其他 root 特权。

### 只读挂载场景

只读挂载（`:ro`）本身就是安全特性，**不要试图修改它**。正确做法是双挂载：

```bash
# 源码只读挂载，编译输出单独可写挂载
docker run --rm \
  -v $(pwd)/src:/src:ro \
  -v $(pwd)/build:/build \
  my-builder
```

### 反模式（绝对禁止）

❌ **反模式1：chmod 777 暴力解**
```bash
# ❌ 错误：权限模型完全失效，任意用户可篡改代码
chmod -R 777 /workspace
```
生产环境 777 是高危漏洞，会被安全扫描标记为 Critical。

❌ **反模式2：--privileged 特权模式**
```bash
# ❌ 错误：容器获得宿主机全部 root 权限，等价于裸奔
docker run --privileged ...
```
除 DinD（Docker-in-Docker）真需要嵌套 Docker 外，任何场景都不应加 `--privileged`。

❌ **反模式3：无脑 chown -R（不判断）**
```bash
# ❌ 错误：每次启动都 chown，大目录浪费几十秒启动时间
# entrypoint.sh
chown -R devuser:devuser /workspace  # 不判断属主直接 chown
```
必须加 `stat` 条件判断，仅当 UID 不匹配时才执行。

❌ **反模式4：以为 ro 挂载 Docker Socket 就安全**
（见第6节详细说明）只读挂载 docker.sock 仍然可以通过 API 逃逸。

### 跨环境速查

| 环境 | 推荐方案 |
|------|---------|
| 个人 Linux 开发机 | P0 `--user $(id -u)` 或 P1 entrypoint chown |
| Mac/Windows Docker Desktop | P1 entrypoint chown（文件共享层自动处理部分映射） |
| VS Code Dev Container | P1 + `remoteUser` 配置（Dev Container 规范自动处理） |
| CI/CD 构建（GitHub Actions/Jenkins） | P0 或 P5（临时容器） |
| 生产环境持久化数据 | P3 named volume |
| 生产环境无状态服务 | 构建时固定 UID，不挂载宿主目录 |
| 多租户/高安全环境 | P4 Podman/rootless Docker |
| K8s | securityContext.runAsUser + initContainer chown |

### 检查清单

- [ ] 遇到权限问题先执行 `id` / `stat` / `ls -ln` 诊断，而非直接敲 sudo
- [ ] **没有**使用 `chmod 777`（grep 验证）
- [ ] **没有**使用 `--privileged`（DinD 除外）
- [ ] entrypoint chown 有条件判断 + NFS 容错（`|| true`）
- [ ] 大目录使用 named volume 或 `--user`，避免启动时 chown
- [ ] 只读挂载场景采用"源码ro + 输出目录rw"双挂载方案
- [ ] docker-compose.yml 中 `user:` 参数支持环境变量覆盖（`${UID:-1000}`）
- [ ] 生产环境未使用 entrypoint chown（会覆盖宿主安全配置）
