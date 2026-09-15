---
id: "jupyter-podman-client-passthrough"
title: "运行时透传"
source: "README.md#11-运行时透传对齐构建端docs07-toolbx-passthroughmd"
---
# 运行时透传（对齐构建端 `docs/07-toolbx-passthrough.md`）

构建端把 5 项运行时透传以 **compose 分层覆盖文件**交付；消费端没有 compose 层（SDK/CLI 编程式启动），
等价形态是 `invoke run` 的 **5 个独立布尔开关**，语义逐项对齐：

| # | 开关 | 等价覆盖文件 | 宿主前置条件 |
|---|------|-------------|-------------|
| ① | `--host-network` | `compose.passthrough.yaml`（Host 网络） | 宿主 `22`/`8888`（或 `<SSH_PORT>`/`8888`）未被占用 |
| ② | `--wayland` | `compose.passthrough.gui.yaml` | daemon 宿主存在 Wayland socket |
| ③ | `--gpu` | `compose.passthrough.gpu.yaml` | daemon 宿主存在 `GPU_DEVICE`（默认 `/dev/dri`） |
| ④ | `--dbus` | `compose.passthrough.yaml`（D-Bus） | daemon 宿主存在会话总线 socket |
| ⑤ | `--usb` | `compose.passthrough.usb.yaml` | daemon 宿主存在 `USB_DEVICE`（默认 `/dev/bus/usb`） |
| ⑥ | `--video` | —（client 扩展，usbipd 挂载后 UVC 字符设备） | daemon 宿主存在 `/dev/video0-3`（可用 `VIDEO_DEVICES` 指定） |

**默认全关（默认隔离）**：不带任何开关时生成的运行参数与旧版本完全一致（输出零变化），
rootless 三必需 `/dev/fuse + label=disable + cgroupns=host` 始终硬编码保留，**任何路径都不使用 `--privileged`**。

```bash
# 主层等价：Host 网络 + D-Bus
invoke run --host-network --dbus

# 按宿主能力叠加（示例：图形会话 + GPU）
invoke run --host-network --dbus --wayland --gpu
```

`--no-<开关>` 可**显式关闭** `.env` 中已开启的同名项，无需修改 `.env`：

```bash
# .env 里 PASSTHROUGH_GPU=yes 时，临时关闭 GPU 透传（例如切到无 /dev/dri 的宿主）
invoke run --no-gpu
```

同一对开关不可同时给出（`--gpu --no-gpu` 会报参数冲突）。

## Host 网络模式的端口语义

* 不发布端口映射（`--network host` 与 `-p` 互斥）
* SSH 走 `--ssh-port`（默认 2222）：rootless Podman 无法绑定特权端口 22，消费端会自动把
  `SSHD_PORT` 设为该值——基础镜像的 `entrypoint.sh` 支持该变量，而 `Containerfile.client`
  `FROM localhost/jupyter-podman-rootless:latest` 并继承其 ENTRYPOINT/CMD，故开箱可用
* Jupyter 固定为容器内 `8888`；此时 `--jupyter-port` 不生效，运行时会打印告警

## 缺资源时的行为（C-I3）

消费端**不做本机存在性预检**：透传资源由 daemon 宿主（WSL2 / Podman Machine）解析，而客户端
可能跑在 Windows 原生 CPython 上，本机 `Path.exists()` 对这些路径必然为假。podman 对缺失源
硬失败（退出码 125、不自动创建）后，消费端会把原生报错翻译为 **C-I3** 指引（见 [04-troubleshooting-guide.md](04-troubleshooting-guide.md)）：
给出缺失路径、可覆盖的变量名，以及 daemon 侧自检命令。

## 三大透传的宿主侧前置（2026-09-11 实测）

三项透传（Wayland / GPU / USB）的资源**都在 daemon 宿主**（podman machine / WSL2）侧，
消费端 `.env` 只负责把开关与路径转成 `invoke run` 参数。以下为各资源的宿主就绪方法。

**② Wayland（WSLg）**

```bash
# 关键：podman machine 的 Wayland socket 在 /mnt/wslg（WSLg），不在 /run/user/1000
# 必须把 HOST_XDG_RUNTIME_DIR 设为 /mnt/wslg/runtime-dir，client 才能拼出
# {xdg}/wayland-0 命中该 socket
ls /mnt/wslg/runtime-dir/wayland-0     # 应存在 srwxrwxrwx

# .env：
#   PASSTHROUGH_WAYLAND=yes
#   HOST_XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir
```

容器内验证：`printenv WAYLAND_DISPLAY`=wayland-0，`/tmp/runtime-user/wayland-0` 为可写 socket。

**③ GPU（NVIDIA → CDI）**

```bash
# NVIDIA 下 /dev/dri 不存在（那是 Intel/AMD Mesa 路径）；WSL2 NVIDIA 走
# /dev/dxg（DXCore）+ /usr/lib/wsl/lib/libcuda*，必须用 CDI 设备引用
sudo dnf install -y golang-github-nvidia-container-toolkit    # Fedora（VM 内）
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml

# .env：
#   PASSTHROUGH_GPU=yes
#   GPU_DEVICE=nvidia.com/gpu=all            # CDI 引用（原样透传）
#   # GPU_DEVICE=/dev/dri                    # Intel/AMD 时（映射容器内 /dev/dri）
```

容器内验证：`nvidia-smi` 显示真实 GPU（Driver/CUDA 版本）。

**⑤ USB（usbipd-win）**

```powershell
# Windows：安装 + 绑定（需管理员；绑定的设备在 attach 期间由 WSL 独占）
winget install --id Dorssel.usbipd-win
& "C:\Program Files\usbipd-win\usbipd.exe" bind --busid <BUSID>        # 一次
# Windows：挂载到目标 WSL 发行版（每次会话）
& "C:\Program Files\usbipd-win\usbipd.exe" attach --wsl podman-machine-default --busid <BUSID>
# 用毕归还 Windows
& "C:\Program Files\usbipd-win\usbipd.exe" detach --busid <BUSID>
```

```bash
# VM 内确认 + 安装排障工具（摄像头采集需 v4l2）
sudo dnf install -y v4l-utils usbutils
lsusb                                   # 应列出绑定的设备（如 Bison Integrated RGB Camera）
ls /dev/video*                          # 摄像头 → /dev/video0/1/2

# .env：
#   PASSTHROUGH_USB=yes
```

`usbipd list` 中设备 STATE 由 `Not shared` → `Shared` 即绑定成功；attach 后 VM 内
`/dev/bus/usb` 出现 001/002 目录。**注意**：attach 是一次性会话操作，VM/podman
machine 重启后需重新 attach。

> ✅ **Video 透传（2026-09-11 新增）**：`--video`（或 `.env` `PASSTHROUGH_VIDEO=yes`）把
> UVC 摄像头字符设备透传给容器——默认 `/dev/video0-3`，可用 `VIDEO_DEVICES=/dev/video0,/dev/video1`
> 精确指定。配合 `--usb`（USB 总线级）即可在容器内用 v4l2/OpenCV 直接采集摄像头。
> 前置：先完成上方 usbipd bind/attach 使摄像头在 daemon 宿主出现 `/dev/video*`；
> 缺失时 podman 硬失败（exit 125），走 C-I3 诊断。