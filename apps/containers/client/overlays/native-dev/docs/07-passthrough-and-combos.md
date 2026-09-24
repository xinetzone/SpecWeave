---
id: "native-dev-passthrough-and-combos"
title: "透传、GPU、torch-gpu、GUI、USB 组合指南"
source: "README.md#运行时组合叠加层opt-in正交维度"
---
# 运行时组合：透传、GPU、torch-gpu、GUI、USB

五维能力中 **torch 是构建期维度**（改镜像内容，须 `native.build`），
**GPU / 透传 / USB / 离线是运行期维度**（只改 compose 文件集，零重建）。
除 torch 外四个运行期维度**全部正交**，可任意组合；组合只叠加覆盖文件，
镜像内容不变（透传形态仅以 `podman tag` 复制同镜像 ID，零额外空间）。

## 维度速查

| 维度 | 开关 | 叠加文件 | 默认 |
|---|---|---|---|
| GPU | `up --gpu` | [`compose.gpu.yaml`](../compose.gpu.yaml) 或 [`compose.gpu.wsl.yaml`](../compose.gpu.wsl.yaml)（**互斥，内核按形态二选一**） | 关（零设备透传，仅基底 `/dev/fuse`） |
| 透传 | `up --passthrough` | [`compose.passthrough.yaml`](../compose.passthrough.yaml) | 关（bridge 网络 + 端口映射） |
| USB | `up --usb` | [`compose.passthrough.usb.yaml`](../compose.passthrough.usb.yaml) | 关 |
| torch | `build --torch cpu\|cu130` | 镜像内容（build args） | 关（不含 torch） |
| GUI | **无栈内开关** | — | **无叠加层**（见下文「GUI」节） |

## 组合矩阵

`up` 恒 `up -d --no-build`；文件加载顺序固定为 **base → GPU → 透传 → USB**
（内核 `compose_config_files_label()` 生成文件集标签，preflight 精确比对）：

| 命令 | 实际文件集 | 网络形态 | 端口 |
|---|---|---|---|
| `invoke native.up` | compose.yaml | bridge | SSH 2223 / Jupyter 8890 |
| `invoke native.up --gpu` | compose + gpu/.gpu.wsl | bridge | 2223 / 8890 |
| `invoke native.up --passthrough` | compose + passthrough | **host** | SSH 2223 / **Jupyter 固定 8888** |
| `invoke native.up --usb` | compose + usb | bridge | 2223 / 8890 |
| `invoke native.up --gpu --usb` | compose + gpu/.gpu.wsl + usb | bridge | 2223 / 8890 |
| `invoke native.up --passthrough --usb` | compose + passthrough + usb | host | 2223 / 8888 |
| `invoke native.up --passthrough --gpu` | compose + passthrough + gpu/.gpu.wsl | host | 2223 / 8888 |
| `invoke native.up --passthrough --gpu --usb` | 全家桶 | host | 2223 / 8888 |
| 上述任一 `+ --offline` | 同左 | 同左 | 离线只禁构建，与设备探测零耦合 |

- **透传与 GPU 正交**：passthrough 层写 `network_mode: host` + `ports: !reset []`，
  GPU/USB 层写 `devices`/`volumes` 追加，字段不重叠，合并不冲突。
- **GPU 与 USB 正交**：两者均为 `devices` 追加合并（podman-compose 多文件 list
  语义），不同设备路径互不干扰；基座 `/dev/fuse` 自动保留。
- **GPU 三形态内部互斥**：`compose.gpu.yaml` 与 `compose.gpu.wsl.yaml` 不可同载
  （devices 重复），由 `resolve_gpu_device` 按探测结果单选。详见
  [04 GPU 与 torch](04-gpu-and-torch.md)。

## 组合 A：torch-gpu（cu130 镜像 + GPU 透传）

> torch 装进**镜像**（base env `/opt/conda`），设备透传是**运行期**动作，
> 两步都要做，缺一不可。

```bash
# ① 构建期：cu130 形态镜像（含 torch 2.14.0 + nvcc 13.4.92 工具链）
invoke native.build --torch cu130
# ② 运行期：起栈并透传 GPU（WSL2 自动 compose.gpu.wsl.yaml 三 bind）
invoke native.down && invoke native.up --gpu
# ③ 验证：看设备枚举，而非只看库加载
podman-compose exec native /opt/conda/bin/python -c \
  "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available())"
# → 2.14.0 13.0 True
```

要点（详见 [04](04-gpu-and-torch.md)）：

- **WSL2 最小充分条件 = 三条 bind 齐备**：`/dev/dxg` + `libcuda.so.1` +
  `libdxcore.so` + `/usr/lib/wsl/drivers` 缺一即 `cuInit=100`
  （CUDA_ERROR_NO_DEVICE）；只验 `CDLL("libcuda.so.1")` 会把 NO_DEVICE 误判为成功。
- **改 flavor 后必须「重建镜像 + 重建容器」两步**：`up` 恒 `--no-build` 且
  podman-compose 配置哈希不含镜像 digest，只跑 `up` 会静默绑定旧镜像。
- **nvcc 与 torch 不同轨**（C25）：编译器 13.4.92 vs torch CUDA 13.0 运行时，
  系 Ubuntu 26.04 基座约束；`-arch` 需按设备指（本机 RTX 5050 Laptop，sm_120）。
- **离线组合**（两阶段）：有网 `native.build --torch cu130 && native.save` →
  无网 `native.load --path <归档>` → `native.up --gpu --offline`。归档名带
  `-torch-cu130-` 形态段（C20），`load` 按形态过滤防导错。

## 组合 B：透传（host 网络 + D-Bus）

```bash
invoke native.up --passthrough        # host 网络 + D-Bus 会话总线（只读）
invoke native.up --passthrough --usb  # 主层 + USB
```

- **端口变化**：host 形态无端口映射——Jupyter **固定 8888**（`ports: !reset []`），
  SSH 经 `HOST_NET_SSHD_PORT`（默认 2223）。
- **镜像切换**：透传栈用 `NATIVE_PASSTHROUGH_IMAGE_TAG`
  （`:passthrough` tag），内核以 `podman tag` 确保就位（同镜像 ID 零空间）。
- **门禁**（invoke 已前置为中文 fail-fast）：`test -S` D-Bus socket；
  `ss -lnt` 查 8888/2223 占用；资源缺失即 fail-fast，不会得到启动后诡异的容器。
- **与 GPU 组合**：`--passthrough --gpu` 正交可用；WSL2 下 GPU 仍自动走
  `compose.gpu.wsl.yaml`（host 网络不改设备形态判定）。

## 组合 C：USB

```bash
invoke native.up --usb                # bridge 网络 + USB（USB 可单独用）
invoke native.up --passthrough --usb  # host 网络 + USB
```

- **WSL2 前提**：宿主默认无 `/dev/bus/usb`，先在 Windows 管理员 PowerShell 把设备
  转发进 podman-machine-default。`usbipd list` 若报 `The service is currently not
  running`，先 `sc.exe start usbipd`（依赖内核驱动 VBoxUsbMon 由 usbipd-win
  安装包自带、随服务自动加载；重启亦可恢复）：

  ```powershell
  usbipd list
  usbipd bind --busid <BUSID>       # 一次；需管理员，装有火绒安全时加 --force（未知过滤器 hrdevmon）
  usbipd attach --wsl podman-machine-default --busid <BUSID>   # 每次会话；不需管理员
  ```

- **门禁**：`test -e /dev/bus/usb`；可用 `USB_DEVICE=/dev/bus/usb/001/002`
  收敛到单设备。与 GPU 叠加时 USB 与 GPU 设备互不冲突。

## 组合 D：全家桶

```bash
invoke native.up --passthrough --gpu --usb
```

host 网络 + D-Bus + GPU（WSL2 三 bind）+ USB 一次到位；镜像仍是同一个
（透传 tag 由 `podman tag` 派生）。`--offline` 可与上述任意组合叠加。

## GUI：现状与可用路径

**本栈当前没有 GUI（X11/Wayland）转发叠加层**——透传四组可选能力
（GPU/透传/USB/torch）不含 GUI，`compose.*.yaml` 无 X11 socket 挂载，
invoke 侧无 GUI 旗标。现有可用路径：

| 需求 | 现状路径 |
|---|---|
| 图形工作台 | **JupyterLab 即 GUI**：bridge 形态 8890 / host 形态 8888，浏览器即用，无需额外透传 |
| 桌面集成（通知、系统设置） | 透传层的 D-Bus 会话总线（`--passthrough`，只读挂载）已覆盖 |
| X11 原生 GUI（如 xterm/GL 视窗） | 本栈未提供；裸 compose 可自行扩展：挂 `/tmp/.X11-unix` + `-e DISPLAY`（物理 Linux 宿主）；WSL2 经 WSLg（`/mnt/wslg/runtime-dir`）同理由调用方自行叠加——**均需自行确认安全边界后再加** |
| Wayland 原生 GUI | 根 `invoke run --wayland` 有该能力（`PASSTHROUGH_WAYLAND`），但**未下沉到 native 叠加栈**；本栈内请以上述路径替代 |

> 若 native 栈的 GUI 需求固化（高频/多用户），可仿 USB 层新增
> `compose.gui.yaml` 叠加文件 + invoke 旗标——属能力扩展，非现有契约。

## 组合排障

| 现象 | 处理 |
|---|---|
| `--passthrough` 后浏览器连 8890 无响应 | host 形态 Jupyter **固定 8888**，8890 不发布 |
| `--passthrough` 起栈报端口占用（exit 125） | `ss -lnt` 查 8888/2223；invoke 门禁已前置，裸 compose 需自查 |
| 重复 `up --passthrough` 报「端口已被占用：8888, 2223」 | **不是冲突**——占用者就是本栈正在运行的 host 形态容器。invoke 门禁（`resolve_passthrough`）识别此幂等场景后放行，交 podman-compose 处理（文件集无变化=no-op，组合旗标变化=自动 recreate）；强制重建用 `invoke native.down && invoke native.up --passthrough ...`。若仍被拦说明占用者是其他进程，按上一行处理 |
| D-Bus 挂载报源不存在 / 门禁报「未探测到会话总线 socket」 | invoke 已按 `$DBUS_SESSION_BUS_ADDRESS`(unix:path=) → `$XDG_RUNTIME_DIR/bus` → `/run/user/$(id -u)/bus` 自动探测（**UID 随宿主而变，未必是 1000**）；仍失败时把宿主会话总线实际路径写 `DBUS_SESSION_BUS_PATH`，或改用系统总线 `/run/dbus/system_bus_socket`（socket 类源**绝不自动创建**，`create_host_path: false`） |
| `--usb` 报 `/dev/bus/usb` 不存在 | WSL2 先 usbipd-win attach（见组合 C）；物理机 `lsusb` 核对 |
| `usbipd list` 报 `service not running` + `Unknown USB filter 'hrdevmon'` | 两个独立根因：**服务未启动**——管理员 PowerShell 执行 `sc.exe start usbipd`（依赖驱动 VBoxUsbMon 由 usbipd-win 自带、随服务自动加载，重启亦可恢复；无需装 VirtualBox）；**hrdevmon**——火绒安全（Huorong）设备监控过滤器挂在 USB 设备类，对 list 无害，`usbipd bind --busid <BUSID> --force` 即可绕过 |
| `--gpu` 容器内 `torch.cuda.is_available()` 恒 False | 先跑 04 文档的设备枚举验证（`cuInit`/`cuDeviceGetCount`）区分库缺失与 NO_DEVICE；WSL2 核对三条 bind 是否齐备 |
| 镜像装过 torch 但容器内 `import torch` 失败 | 改 flavor 后只跑了 `up` 没重建镜像/容器，见组合 A「两步」 |
| 多平面交替后端口冲突 | 见 [06 排障速查](06-troubleshooting.md) W-I10 行；日常纪律：同一栈固定单一控制平面 |

## 相关文档

- [04 GPU 与 torch](04-gpu-and-torch.md)：GPU 三形态细节、torch 形态与 nvcc 工具链
- [05 参数与栈关系](05-params-and-relations.md)：全部 compose 插值/.env 键定义
- [06 排障速查](06-troubleshooting.md)：单维能力排障总表
- [03 离线交付](03-offline-delivery.md)：`--offline` 语义与两阶段归档流程
