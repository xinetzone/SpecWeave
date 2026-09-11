---
id: "jupyter-toolbx-passthrough"
title: "Toolbx 透传开发模式"
source: "README.md#toolbx-透传开发模式"
---
# Toolbx 透传开发模式

本容器镜像满足 [Toolbx](https://containertoolbx.org/) 自定义镜像规范，吸收 Toolbx "透传优于隔离"（pass-through over isolation）的设计哲学，提供灵活的开发体验。

## Toolbx 是什么？

Toolbx 是一个用于 Linux 容器化开发环境的工具，让容器像在主机上一样无缝使用：
- 自动透传用户主目录（HOME）
- 自动透传当前工作目录
- 自动透传Wayland/X11显示
- 自动透传SSH agent
- 与主机共享用户UID/GID
- 可直接访问主机系统通过/run/host

## 镜像兼容标记

镜像内置以下 Toolbx 兼容特性，使其可被宿主 Toolbx 识别（实际 create/enter 请用下文 `:toolbx` 变体）：

| 兼容项 | 实现 |
|--------|------|
| LABEL 标记 | `com.github.containers.toolbox=true` |
| /run/host 挂载点 | 预创建目录，用于 bind-mount 主机根文件系统 |
| Marker 文件 | `/run/.toolboxenv` + `/run/.containerenv` |
| capsh 工具 | libcap2-bin 包提供能力边界工具 |
| flatpak-spawn | `flatpak-xdg-utils` 包 + `/usr/bin/flatpak-spawn` symlink（容器内二进制经 `flatpak-spawn --host` 转发回宿主执行的前提，官方镜像同款安装） |
| sudo NOPASSWD | devuser 无密码 sudo（`GRANT_SUDO=yes` 时启用） |
| UID 匹配 | devuser 固定 UID 1000（先删除基础镜像自带 ubuntu 账号；与 Linux 主机默认用户 UID 一致） |

## 宿主机 Toolbx 流程（`:toolbx` 变体，2026-09-11 实测）

> ⚠️ **普通 `:latest` 镜像不能直接 `toolbox create`**。Toolbx 只覆盖容器 Cmd
> （`toolbox init-container`，PATH 解析）而**不清镜像 ENTRYPOINT**，`:latest` 的
> tini+entrypoint.sh 启动链会抢先执行；其 HEALTHCHECK 在无 systemd 用户实例的
> podman machine 里也无法注册。宿主 Toolbx 必须使用专用薄变体 **`:toolbx`**
> （`Containerfile.toolbx`：`userdel devuser` 释放 UID1000 给宿主同名用户 +
> `HEALTHCHECK NONE` + `ENTRYPOINT []`，构建依据见该文件头注释）。

### 1. 构建两个镜像

```bash
cd apps/containers/jupyter-podman-rootless
invoke build          # 主镜像 :latest
invoke build-toolbx   # Toolbx 宿主薄变体 :toolbx（秒级；基底缺失会中文报错）
```

### 2. 宿主机前置：安装 toolbox

| 宿主 | 安装方式 |
|------|---------|
| Fedora（含 podman machine 默认 VM，Fedora 43） | `sudo dnf install toolbox p11-kit-server`（推荐；p11-kit-server 提供 CA 证书转发，缺失时仅警告不影响使用） |
| Ubuntu/Debian 物理机 | `sudo apt install toolbox` |
| 不想装系统包 | 从镜像提取已内嵌的同版本二进制：`podman create --name t localhost/jupyter-podman-rootless:latest cat && podman cp t:/usr/local/libexec/toolbox ~/.local/bin/toolbox && podman rm t && chmod +x ~/.local/bin/toolbox`。该二进制在 Debian 上构建，运行时 dlopen `libsubid.so.4.0.0`；Fedora 只有 `libsubid.so.5`（ABI 实测兼容），需补软链：`mkdir -p ~/.local/compat-lib && ln -s /lib64/libsubid.so.5 ~/.local/compat-lib/libsubid.so.4.0.0` |

### 3. 在 podman machine / WSL2 内执行（Windows 用户）

`toolbox create` 必须在 **podman 的 Linux 宿主**上发起（Windows 原生不支持）：

```powershell
wsl -d podman-machine-default
```

```bash
# WSL/podman machine 会话必需的环境修正（物理 Linux 终端通常无需）：
export HOME=/home/user
export XDG_RUNTIME_DIR=/run/user/1000
export CONTAINER_HOST=unix:///run/user/1000/podman/podman.sock   # 经 socket 服务通道，避开 VM 无 systemd 用户实例导致的 HEALTHCHECK 失败
export LD_LIBRARY_PATH=$HOME/.local/compat-lib:$LD_LIBRARY_PATH   # 仅"提取二进制"安装方式需要

toolbox create -i localhost/jupyter-podman-rootless:toolbx -c jupyter-dev
toolbox enter jupyter-dev
```

> ⚠️ **首次运行会执行 `podman system migrate`**（toolbox 版本迁移戳记，每台机器一次），
> 它会**停掉该用户下所有运行中容器**。请先 `podman ps` 确认并在事后重启业务容器；
> 迁移完成后写入 `~/.config/toolbox/podman-system-migrate`，后续不再触发。

### 4. 实测行为（podman machine Fedora 43，宿主 user UID 1000）

| 验证项 | 结果 |
|--------|------|
| `toolbox create` | Created container: jupyter-dev（退出码 0） |
| `toolbox run -c jupyter-dev id` | `uid=1000(user) gid=1000(user) groups=1000(user),27(sudo)` |
| HOME / cwd | 透传宿主 `/home/user`（Toolbx bind-mount 宿主家目录） |
| `/run/host` | 宿主完整根文件系统（afs/bin/boot/...） |
| `/opt/conda/bin/python --version` | Python 3.14.7（1000:1000 数字属主自动承接） |
| `sudo -n true` | 通过（变体 sudoers 按 `%sudo` 组 NOPASSWD） |
| 容器内 `podman --version` | 5.7.0 可用（toolbox `--privileged` 模式） |
| 幂等 | 二次 `toolbox create` 报 already exists（exit 1），容器与数据无损 |
| 组说明 | init-container 只加入 sudo 组（上游 `GetGroupForSudo` 语义）；不加入 docker 组属正常，DinP 非 toolbx 模式目标 |

### 5. 已知限制（WSL 精简 VM 环境天花板，非镜像缺陷）

- **`flatpak-spawn --host` 不可用**：报 `Portal call failed: The name is not activatable`——该命令走 Flatpak D-Bus 门户，podman machine 精简系统没有该门户。镜像中 flatpak-spawn 的装法与[上游 Ubuntu 26.04 官方镜像](../../../vendor/toolbox/images/ubuntu/26.04/Containerfile)完全一致（symlink 到 flatpak-xdg-utils），物理 Fedora Silverblue/Ubuntu Desktop 上正常。
- `sudo` 可能提示 `unable to resolve host toolbx`（不影响退出码）：上游镜像额外安装 `libnss-myhostname` 消除该提示，后续可评估引入。
- toolbx 容器以 `--privileged --network host --pid host --ipc host` 运行，透传优先、隔离弱化，仅用于可信开发场景。

### 6. 常用命令

```bash
toolbox list                    # 查看 toolbox 容器/镜像
toolbox run -c jupyter-dev <cmd> # 非交互执行（自动化/验证用）
toolbox enter jupyter-dev       # 交互式进入（exit 退出）
toolbox rm -f jupyter-dev       # 删除（需先 exit）
```

## 透传配置（compose.dev.yaml）

即使不用toolbox命令，`compose.dev.yaml` 也提供开箱即用的开发透传配置，覆盖以下主机资源：

| 透传资源 | 挂载方式 | 用途 |
|---------|---------|------|
| SSH agent socket | `$SSH_AUTH_SOCK` → `/tmp/ssh-auth.sock:ro` | 复用主机 SSH agent，容器内 git push/pull 不输密码 |
| Git 配置 | `~/.gitconfig` → `/home/devuser/.gitconfig:ro` | 复用主机 git 用户配置 |
| SSH 密钥 | `~/.ssh` → `/home/devuser/.ssh:ro` | 只读挂载 SSH 密钥 |
| X11 套接字 | `/tmp/.X11-unix:rw` | GUI 应用显示（matplotlib 交互式窗口、firefox 等） |
| Pip 缓存 | `~/.cache/pip` | 加速容器内 pip install |
| 文件描述符 | `ulimits nofile 65536` | 大型 ML 工作负载 |
| DISPLAY 环境变量 | `${DISPLAY:-:0}` | X11 显示 |
| XDG_RUNTIME_DIR | `/tmp/runtime-user` | Wayland/系统运行时 |

### 启用透传模式

```bash
# 叠加compose.dev.yaml，启用所有透传
podman-compose -f compose.yaml -f compose.dev.yaml up -d

# 透传模式 + 本地模型仓库
podman-compose -f compose.yaml -f compose.dev.yaml --profile registry up -d

# 验证SSH agent透传
podman-compose exec jupyter git clone git@github.com:your/repo.git
# 应无需输入密码即可克隆

# 验证X11透传（需主机运行X server）
podman-compose exec jupyter xclock
# 应弹出时钟窗口
```

## 可选透传（注释式 opt-in）

`compose.yaml` 中还以注释形式提供了更多可选透传配置，取消注释即可启用：

### Wayland 套接字

Wayland原生GUI应用支持：
```yaml
# - $XDG_RUNTIME_DIR/$WAYLAND_DISPLAY:/tmp/runtime-user/$WAYLAND_DISPLAY:rw
```

### /run/host 逃生口（高风险）

挂载主机完整根文件系统，容器内可直接访问主机所有文件：
```yaml
# - /:/run/host:rslave
```
> ⚠️ **警告**：这相当于容器内有主机root权限访问，仅在完全信任容器内进程时使用。

### Host 网络模式

共享主机网络栈，免端口映射：
```yaml
# network_mode: host
```
启用后 Jupyter 可直接通过 `localhost:8888` 访问，无需端口映射。

> ⚠️ **rootless Podman 下 SSH 不能走 22 端口**：容器 root 映射为宿主非特权 UID，绑定特权端口 22（<1024）会被拒绝（`Bind to port 22 on 0.0.0.0 failed: Permission denied`，sshd 随即退出）。因此主层覆盖文件把 sshd 端口改为非特权端口（`SSHD_PORT`，默认 `2222`），访问方式为 `localhost:2222`。

### GPU 透传

- Intel/AMD Mesa GPU：
  ```yaml
  # - /dev/dri:/dev/dri:rw
  ```
- NVIDIA GPU：使用CDI（Container Device Interface）设备规范

### USB 透传

```yaml
# - /dev/bus/usb:/dev/bus/usb:rw
```
用于USB设备调试（手机开发板、USB外设等）。

### D-Bus 会话总线

桌面系统集成：
```yaml
# - /run/user/1000/bus:/tmp/runtime-user/bus:rw
```
可发送桌面通知、访问系统设置等。

## 运行时透传叠加（compose.passthrough*.yaml）

上述注释式 opt-in 中有 5 项属于**运行时**透传（网络模式 / 设备节点 / 套接字挂载），无法烘焙进镜像内容。它们以**分层覆盖文件**的形式提供，按宿主实际具备的资源逐层叠加：

| 层 | 覆盖文件 | 开启项 | 宿主前置条件 |
|---|---------|-------|-------------|
| 主层 | `compose.passthrough.yaml` | ① Host 网络模式　④ D-Bus 会话总线 | 会话总线 socket 存在（systemd 用户会话下默认具备） |
| GUI | `compose.passthrough.gui.yaml` | ② Wayland 套接字 | 宿主运行 Wayland 会话 |
| GPU | `compose.passthrough.gpu.yaml` | ③ GPU `/dev/dri` | 宿主存在 `GPU_DEVICE`（默认 `/dev/dri`） |
| USB | `compose.passthrough.usb.yaml` | ⑤ USB `/dev/bus/usb` | 宿主存在 `USB_DEVICE`（默认 `/dev/bus/usb`） |

主层会把镜像切换为专用 tag `jupyter-podman-rootless:passthrough`（可用 `PASSTHROUGH_IMAGE_TAG` 覆盖），默认隔离栈继续使用 `:latest`。

### 为什么必须分层？

**podman 对缺失的挂载源/设备节点直接硬失败**（退出码 125），且**不会自动创建**该路径——`:ro`、`:rw`、裸挂载三种写法表现一致。若把 5 项写进同一个覆盖文件，在缺少任一资源的宿主（例如无 `/dev/dri` 的 WSL2 环境）上 `podman-compose up` 会直接启动失败。分层后每个开关都能独立启用与验证。

### 使用方式

```bash
# 主层：Host 网络 + D-Bus（先确认前置条件）
test -S "${XDG_RUNTIME_DIR:-/run/user/1000}/bus" && echo "D-Bus OK"
ss -lnt | grep -E ':(2222|8888) '   # 应为空：host 网络下容器直接占用这两个端口
                                    # 2222 = SSHD_PORT（rootless 下不能绑特权端口 22）
podman-compose -f compose.yaml -f compose.passthrough.yaml up -d

# 访问方式：ssh devuser@localhost -p 2222   /   http://localhost:8888

# 按宿主能力继续叠加（示例：图形会话 + GPU）
podman-compose -f compose.yaml \
               -f compose.passthrough.yaml \
               -f compose.passthrough.gui.yaml \
               -f compose.passthrough.gpu.yaml up -d
```

> ⚠️ **执行环境**：`podman-compose` 在 **Windows 原生宿主上是无效组合**（路径语义错配，非未安装）——它用 `ntpath` 预处理挂载源，把 `/run/user/1000/bus` 按当前盘符解析为 `D:\run\user\1000\bus`，并在 `assert_volume()` 中试图在宿主创建该目录，实测报 `PermissionError [WinError 5]` 与沙箱 `Not allow operate files: D:\run`。
> **工具层已拦截**：`compose_available()` 在 Windows 原生宿主恒返回 `False`，`invoke` 会自动降级到 SDK/CLI 后端（路径由远端 daemon 解析）；上述命令请在 WSL / `podman machine ssh` 内执行。详见 [09-three-tier-backend.md](09-three-tier-backend.md) 的「宿主兼容性」。
> **宿主源禁止自动创建**：所有宿主绝对路径挂载源均为 long syntax + `bind: {create_host_path: false}`，源缺失时显式报 `ValueError: ... bind source path does not exist: <path>`，而非在宿主 `mkdir` 出 `D:\run`、`D:\dev`、`D:\home` 之类的错误目录。因此首次使用 `compose.dev.yaml` 前请确认 `~/.gitconfig`、`~/.ssh`、`/tmp/.X11-unix` 存在，并 `mkdir -p ~/.cache/pip`（该缓存原先是自动创建的，现须宿主预先具备）。

> ⚠️ **Host 网络模式的前置条件**：容器将直接绑定宿主 `22`/`8888` 端口，与端口映射模式的容器互斥。启用前请先 `podman-compose down` 停掉占用这些端口的栈；覆盖文件已通过 `ports: !reset []` 清除基座的端口发布，否则与 host 网络冲突。

> ⚠️ **GPU 的 NVIDIA 场景**：`/dev/dri` 只覆盖 Intel/AMD Mesa。NVIDIA 走 **CDI**——宿主先 `nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml`，client 侧 `GPU_DEVICE=nvidia.com/gpu=all`（CDI 引用，原样透传，无需设备节点路径）。WSL2 下 CDI 自动选用 `/dev/dxg`（DXCore）与 `/usr/lib/wsl/lib/libcuda*`（实测容器内 `nvidia-smi` 输出 581.57/CUDA 13.0）。compose 模式仍用 `GPU_DEVICE` 指向 CDI 设备名（同 `--gpu` 语义，见 [.env.example](../.env.example)）。

各项变量（`DBUS_SESSION_BUS_PATH` / `HOST_XDG_RUNTIME_DIR` / `HOST_WAYLAND_DISPLAY` / `GPU_DEVICE` / `USB_DEVICE` / `PASSTHROUGH_IMAGE_TAG`）见 [.env.example](../.env.example)。

## 安全设计

透传功能遵循严格的安全原则：

1. **默认隔离**：所有透传均为 opt-in，默认 `compose.yaml` 配置保持完全隔离，不挂载任何主机敏感资源
2. **只读挂载**：SSH keys、gitconfig 等敏感资源默认以只读方式挂载，容器内无法修改
3. **无 secret 泄漏**：不挂载主机 credential store、GPG 密钥等高敏感资源
4. **/run/host 默认关闭**：主机文件系统逃生口需显式启用，并有明确警告
5. **SSH agent 转发而非复制**：挂载SSH agent socket而非私钥文件，私钥始终在主机上

Compose透传配置规范详见 [.agents/rules/compose.md](../.agents/rules/compose.md)。

## invoke 与透传模式

invoke的`run`命令默认不启用透传。如需使用透传模式，建议直接使用podman-compose命令叠加compose.dev.yaml：

```bash
# invoke方式（默认隔离）
invoke run

# compose透传方式（推荐开发时使用）
podman-compose -f compose.yaml -f compose.dev.yaml up -d

# 进入shell（透传模式下）
podman-compose exec jupyter bash
```
