---
id: "jupyter-compose-rules"
title: "Compose编排与透传配置规范"
source: "README.md#compose服务架构 + README.md#Toolbx透传开发模式"
---
# Compose编排与透传配置规范（jupyter-podman-rootless）

## 基础约定

- 编排文件使用Podman Compose规范（兼容Docker Compose Spec）
- 主文件：`compose.yaml`（默认隔离配置）
- 开发透传覆盖：`compose.dev.yaml`（opt-in，叠加使用）
- 环境变量：`.env`文件（从`.env.example`复制）
- 三层后端自动降级：podman-compose → podman-py SDK → CLI fallback
- 默认隔离优先，所有透传均为opt-in

## compose.yaml服务定义

### jupyter服务（默认启用）

```yaml
services:
  jupyter:
    build:
      context: .
      containerfile: Containerfile
    image: jupyter-podman-rootless:latest
    container_name: jupyter-podman
    ports:
      - "${SSH_PORT:-2222}:22"
      - "${JUPYTER_PORT:-8888}:8888"
    volumes:
      - ./workspace:/workspace
    devices:
      - /dev/fuse
    security_opt:
      - label=disable
    cgroupns: host
    environment:
      - USER_PASSWORD=${USER_PASSWORD:-}
      - JUPYTER_TOKEN=${JUPYTER_TOKEN:-}
      - GRANT_SUDO=${GRANT_SUDO:-no}
    restart: unless-stopped
```

关键配置：
- 必须挂载`/dev/fuse`设备（fuse-overlayfs需要）
- `security_opt: label=disable`（禁用SELinux标签，避免FUSE权限问题）
- `cgroupns: host`（rootless Podman需要）
- 工作目录挂载：`./workspace:/workspace`

### model-registry服务（profile: registry）

本地OCI registry服务，用于OMLMD/OLOT开发测试：

```yaml
  model-registry:
    profiles: ["registry"]
    image: ghcr.io/project-zot/zot-linux-amd64:latest
    container_name: model-registry
    ports:
      - "${REGISTRY_PORT:-5000}:5000"
    volumes:
      - registry-data:/var/lib/registry
    restart: unless-stopped

volumes:
  registry-data:
```

仅当使用`--profile registry`时启动，默认不启动。

## compose.dev.yaml透传配置（Toolbx风格）

`compose.dev.yaml`遵循Toolbx"透传优于隔离"的设计哲学，提供开箱即用的开发透传：

```yaml
services:
  jupyter:
    volumes:
      # SSH agent透传：复用主机SSH agent，git push/pull不输密码
      - ${SSH_AUTH_SOCK:-/dev/null}:/tmp/ssh-auth.sock:ro
      # Git配置透传：复用主机git用户配置
      - ~/.gitconfig:/home/devuser/.gitconfig:ro
      # SSH密钥透传：只读挂载SSH密钥
      - ~/.ssh:/home/devuser/.ssh:ro
      # X11套接字透传：GUI应用显示
      - /tmp/.X11-unix:/tmp/.X11-unix:rw
      # Pip缓存透传：加速容器内pip install
      - ~/.cache/pip:/home/devuser/.cache/pip
    environment:
      - SSH_AUTH_SOCK=/tmp/ssh-auth.sock
      - DISPLAY=${DISPLAY:-:0}
      - XDG_RUNTIME_DIR=/tmp/runtime-user
    ulimits:
      nofile:
        soft: 65536
        hard: 65536
```

### 透传资源说明

| 透传资源 | 挂载方式 | 用途 | 安全级别 |
|---------|---------|------|---------|
| SSH agent socket | `$SSH_AUTH_SOCK` → `/tmp/ssh-auth.sock:ro` | 复用主机SSH agent | 安全（只读） |
| Git配置 | `~/.gitconfig` → `/home/devuser/.gitconfig:ro` | 复用主机git用户配置 | 安全（只读） |
| SSH密钥 | `~/.ssh` → `/home/devuser/.ssh:ro` | 只读挂载SSH密钥 | 安全（只读） |
| X11套接字 | `/tmp/.X11-unix:rw` | GUI应用显示 | 中等（需要主机X11授权） |
| Pip缓存 | `~/.cache/pip` | 加速pip install | 安全（缓存文件） |
| 文件描述符 | `ulimits nofile 65536` | 大型ML工作负载 | 安全 |
| DISPLAY环境变量 | `${DISPLAY:-:0}` | X11显示 | 配合X11套接字 |
| XDG_RUNTIME_DIR | `/tmp/runtime-user` | Wayland/系统运行时 | 配合Wayland透传 |

### 可选透传（注释式opt-in）

`compose.yaml`中还以注释形式提供了更多可选透传配置，取消注释即可启用：

- **Wayland套接字**：`$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY`
- **/run/host逃生口**：`/:/run/host:rslave`（挂载主机完整根文件系统，高风险）
- **Host网络模式**：`network_mode: host`（共享主机网络栈，免端口映射）
- **GPU透传**：`/dev/dri`（Intel/AMD Mesa GPU）、NVIDIA CDI设备
- **USB透传**：`/dev/bus/usb`
- **D-Bus会话总线**：系统集成

## 环境变量配置

`.env.example`模板：

```bash
# 服务端口
SSH_PORT=2222
JUPYTER_PORT=8888
REGISTRY_PORT=5000

# 认证（留空则自动生成）
USER_PASSWORD=
JUPYTER_TOKEN=
JUPYTER_PASSWORD=
SSH_PUBLIC_KEY=

# 权限控制
GRANT_SUDO=no
ALLOW_ROOT_SSH=no

# 镜像源
APT_MIRROR=official
CONDA_MIRROR=official
PIP_MIRROR=official

# ML模型仓库
REGISTRY_URL=localhost:5000
REGISTRY_PLAIN_HTTP=true

# 调试
DEBUG=0
```

## 使用方式

### 默认隔离模式（invoke封装，推荐）

```bash
# invoke自动处理三层后端选择、路径转换、密码生成
invoke build --apt-mirror tuna
invoke run
```

### 标准Compose模式

```bash
cp .env.example .env
# 编辑.env设置密码、端口等
podman-compose up -d --build
podman-compose ps
podman-compose logs -f
podman-compose exec jupyter bash
podman-compose down
```

### 开发透传模式

```bash
# 叠加compose.dev.yaml，启用SSH/GUI/pip缓存透传
podman-compose -f compose.yaml -f compose.dev.yaml up -d

# 同时启动本地模型仓库
podman-compose -f compose.yaml -f compose.dev.yaml --profile registry up -d
```

### Toolbx模式

```bash
# 使用已构建的镜像创建Toolbx容器
toolbox create -i jupyter-podman-rootless:latest -c jupyter-dev
# 进入容器（自动透传HOME/cwd/Wayland/X11/SSH agent等）
toolbox enter jupyter-dev
```

## 安全设计原则

1. **默认隔离**：`compose.yaml`默认配置保持完全隔离，不挂载任何主机敏感资源
2. **opt-in透传**：所有透传功能都需要显式叠加`compose.dev.yaml`或取消注释
3. **只读挂载**：SSH keys、gitconfig等敏感资源默认以只读方式挂载
4. **无secret泄漏**：不挂载主机credential store、GPG密钥等高敏感资源
5. **/run/host默认关闭**：主机文件系统逃生口需显式启用
6. **自动生成密码**：默认自动生成随机密码和token，不使用硬编码默认密码

## 验证清单

compose配置修改后必须验证：
- [ ] `podman-compose -f compose.yaml config`语法验证通过
- [ ] `podman-compose -f compose.yaml -f compose.dev.yaml config`透传配置验证通过
- [ ] 默认模式启动后容器可正常运行，SSH/Jupyter可访问
- [ ] 透传模式下git push/pull可复用SSH agent（无需输入密码）
- [ ] 透传模式下xclock等GUI应用可显示
- [ ] pip install可命中缓存加速
- [ ] --profile registry启动后model-registry可访问（localhost:5000）
- [ ] 不挂载~/.ssh等敏感资源时容器正常运行（隔离模式）
