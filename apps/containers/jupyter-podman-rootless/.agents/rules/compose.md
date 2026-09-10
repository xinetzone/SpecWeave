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
- 运行时透传覆盖（分层 opt-in，按宿主资源能力逐层叠加）：`compose.passthrough.yaml`（Host 网络 + D-Bus）、`compose.passthrough.gui.yaml`（Wayland）、`compose.passthrough.gpu.yaml`（GPU）、`compose.passthrough.usb.yaml`（USB）
- 环境变量：`.env`文件（从`.env.example`复制）
- 三层后端自动降级：podman-compose → podman-py SDK → CLI fallback
- 默认隔离优先，所有透传均为opt-in
- 宿主绝对路径挂载源一律写 long syntax 并带 `bind: {create_host_path: false}`（禁止在宿主自动创建目录，缺失即显式报错；详见「分层硬约束」）

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
    image: registry:2
    profiles: ["registry"]
    container_name: ${CONTAINER_NAME:-jupyter-podman}-registry
    ports:
      - "${REGISTRY_PORT:-5000}:5000"
    volumes:
      - registry-data:/var/lib/registry
    environment:
      REGISTRY_STORAGE_DELETE_ENABLED: "true"
      REGISTRY_HTTP_ADDR: "0.0.0.0:5000"
    restart: unless-stopped

volumes:
  registry-data:
```

仅当使用`--profile registry`时启动，默认不启动（且该命令仅 WSL / podman machine 内可用，见「分层硬约束」）。

**跨平台等价替代**：`invoke registry.up` / `invoke registry.down`（`tasks/registry.py`）以 SDK→CLI 两层实现同一服务，不依赖 podman-compose，Windows 原生宿主同样可用。其容器名、数据卷名（`<project>_registry-data`，即 podman-compose 的 `<project>_<volume>` 生成规则）、端口、环境变量、重启策略均与本服务对齐，**两种启动方式共享同一份数据卷**。

> ⚠️ 修改本服务定义（镜像 / 卷名 / 端口 / 环境变量 / 重启策略）时必须同步 `tasks/registry.py` 顶部的「与 compose.yaml 保持同步的常量」，否则两条路径会各自启动一个互不相干的服务。

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

### 可选透传（分层覆盖文件 opt-in）

`compose.yaml` 中以注释形式列出、并由独立覆盖文件承载的可选透传：

- **Wayland套接字**：`$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY` → `compose.passthrough.gui.yaml`
- **/run/host逃生口**：`/:/run/host:rslave`（挂载主机完整根文件系统，高风险；保持注释式 opt-in）
- **Host网络模式**：`network_mode: host`（共享主机网络栈，免端口映射）→ `compose.passthrough.yaml`
- **GPU透传**：`/dev/dri`（Intel/AMD Mesa GPU）、NVIDIA CDI设备 → `compose.passthrough.gpu.yaml`
- **USB透传**：`/dev/bus/usb` → `compose.passthrough.usb.yaml`
- **D-Bus会话总线**：系统集成 → `compose.passthrough.yaml`

#### 分层硬约束（不可合并为单文件）

**podman 对缺失的挂载源/设备节点硬失败**（退出码 125），且不会自动创建该路径（`:ro`/`:rw`/裸挂载表现一致）。因此这 5 项必须按宿主资源能力分层叠加——合并为单文件时，缺少任一资源的宿主将无法 `up`。

- 各覆盖文件头部必须写明该项的前置检查命令（`test -S` / `test -e`）
- `network_mode: host` 与端口发布互斥：覆盖文件须用 `ports: !reset []` 清除基座端口映射（`!reset`/`!override` 由 podman-compose 原生支持）
- `network_mode: host` 下**不能沿用容器内 22 端口**：rootless Podman 容器 root 映射为宿主非特权 UID，绑定特权端口（<1024）被拒绝，sshd 会 FATAL 退出（实测 `Bind to port 22 on 0.0.0.0 failed: Permission denied`）。覆盖文件须设 `SSHD_PORT` 为非特权端口（默认 2222），Jupyter 的 8888 不受影响
- **执行环境硬约束（已下沉为工具层门禁）**：`podman-compose` 在 **Windows 原生宿主上是无效组合**，原因不是「未安装」而是「路径语义错配」——它是宿主进程内的路径处理器，会用 `ntpath` 预处理 compose 中的挂载源：`/run/user/1000/bus` 被按「当前盘符根」解析为 `D:\run\user\1000\bus`，随后 compose 内部 `assert_volume()` 见该路径不存在便 `os.makedirs()` 试图在宿主创建目录（实测 `PermissionError [WinError 5]` + 沙箱 `Not allow operate files: D:\run`；失败被 `except OSError: pass` 吞掉后 podman 仍收到被篡改的挂载源）。
  - **工具层已拦截**：`tasks/client.py::compose_available()` 在 Windows 原生宿主恒返回 `False`，三层降级自动落到 Tier 2 SDK / Tier 3 CLI——它们把 Linux 绝对路径原样交给 podman（Windows 上是远程客户端，路径由 machine 内 daemon 解析），因此路径语义一致
  - **宿主透传源禁止自动创建**：所有宿主绝对路径挂载源必须写 long syntax 并带 `bind: {create_host_path: false}`（该字段无法用 short syntax 表达——short syntax 下 podman-compose 只会填 `bind.propagation`，故必走 long syntax）。这样源缺失时是**显式报错**而非在宿主 `mkdir` 出错误目录：
    ```
    ValueError: invalid mount config for type 'bind': bind source path does not exist: <path>
    ```
    实测：加固前手敲 `podman-compose -f compose.yaml -f compose.dev.yaml up` 会在宿主留下 `D:\run`、`D:\dev`、`D:\home` 等错误目录；加固后同一命令直接抛上述 `ValueError`，宿主零残留。**代价**：原先依赖自动创建的源（尤指 `~/.cache/pip`）须由宿主预先具备，否则该报错会命中它
  - 手敲 `podman-compose` 仍须在 WSL / `podman machine ssh` 内执行：工具层门禁对绕过 invoke 的命令不生效，且 long syntax 只能防「污染宿主」，不能修正被 `ntpath` 篡改的挂载源
- 覆盖文件覆盖 `image` 时**不得复用 `${IMAGE_TAG}`**：应用会自动生成 `.env` 并写入 `IMAGE_TAG`，复用会导致覆盖静默失效（改用独立变量如 `PASSTHROUGH_IMAGE_TAG`）

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
- [ ] `podman-compose -f compose.yaml -f compose.passthrough.yaml config`叠加校验通过：`network_mode: host` 生效、`ports` 已被 `!reset` 清除、D-Bus 卷与 `DBUS_SESSION_BUS_ADDRESS`/`XDG_RUNTIME_DIR` 就位、`/dev/fuse` 未被覆盖、`image` 切换为 `PASSTHROUGH_IMAGE_TAG` 默认值
- [ ] 继续叠加设备层后 `devices` 为**追加**而非替换：`podman-compose -f compose.yaml -f compose.passthrough.yaml -f compose.passthrough.gpu.yaml config` 中同时包含 `/dev/fuse` 与 `${GPU_DEVICE:-/dev/dri}`
- [ ] 各分层覆盖文件头部的前置检查命令在宿主上实测结果与文档一致；缺资源的层不得叠加（podman 对缺失源硬失败，退出码 125）
- [ ] 每个宿主绝对路径挂载源都带 `bind: {create_host_path: false}`，且在 `config` 合并结果中**逐层保留**（含叠加设备层后）：`podman-compose -f compose.yaml -f compose.dev.yaml config` 等组合的每个 `type: bind` 条目下均有 `create_host_path: false`
- [ ] 源缺失时**零宿主残留**：`podman-compose --dry-run -f compose.yaml -f compose.dev.yaml up -d` 应以 `ValueError: ... bind source path does not exist: <path>` 退出（而非在宿主 mkdir 出 `D:\run`、`D:\dev`、`D:\home` 等错误目录）
- [ ] 默认模式启动后容器可正常运行，SSH/Jupyter可访问
- [ ] 透传模式下git push/pull可复用SSH agent（无需输入密码）
- [ ] 透传模式下xclock等GUI应用可显示
- [ ] pip install可命中缓存加速
- [ ] --profile registry启动后model-registry可访问（localhost:5000）
- [ ] 不挂载~/.ssh等敏感资源时容器正常运行（隔离模式）
