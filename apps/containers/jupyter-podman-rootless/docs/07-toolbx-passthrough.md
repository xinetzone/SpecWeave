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

镜像内置以下 Toolbx 兼容特性，使其可直接被 `toolbox create/enter` 命令识别和使用：

| 兼容项 | 实现 |
|--------|------|
| LABEL 标记 | `com.github.containers.toolbox=true` |
| /run/host 挂载点 | 预创建目录，用于 bind-mount 主机根文件系统 |
| Marker 文件 | `/run/.toolboxenv` + `/run/.containerenv` |
| capsh 工具 | libcap2-bin 包提供能力边界工具 |
| flatpak-spawn | `flatpak-xdg-utils` 包 + `/usr/bin/flatpak-spawn` symlink（容器内二进制经 `flatpak-spawn --host` 转发回宿主执行的前提，官方镜像同款安装） |
| sudo NOPASSWD | devuser 无密码 sudo（`GRANT_SUDO=yes` 时启用） |
| UID 匹配 | devuser 固定 UID 1000（与 Linux 主机默认用户 UID 一致） |

### 使用 Toolbx 管理容器

```bash
# 使用已构建的镜像创建Toolbx容器
toolbox create -i jupyter-podman-rootless:latest -c jupyter-dev

# 进入Toolbx容器（自动透传HOME/cwd/Wayland/X11/SSH agent等）
toolbox enter jupyter-dev

# 退出
exit
```

进入Toolbx容器后，你会发现：
- 当前工作目录与主机相同
- 主目录文件可直接访问
- 可运行GUI应用（xclock、firefox等）
- git push/pull复用SSH agent，无需输入密码

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
使用后可直接通过`localhost:22`、`localhost:8888`访问，无需端口映射。

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
