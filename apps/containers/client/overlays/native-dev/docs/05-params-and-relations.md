---
id: "native-dev-params-and-relations"
title: "参数表与相关栈/目录的关系"
source: "README.md#参数表compose-插值-env-键"
---
# 参数表与相关栈/目录的关系

## 参数表（compose 插值 / .env 键）

| 键 | 默认值 | 用途 |
|---|---|---|
| `NATIVE_IMAGE_TAG` | `localhost/native-dev:latest` | 镜像标签 |
| `NATIVE_CONTAINER_NAME` | `native-dev` | 容器名（project name 固定 native-dev） |
| `NATIVE_SSH_PORT` / `NATIVE_JUPYTER_PORT` | `2223` / `8890` | 宿主端口（与 onnx 2222/8888 错开） |
| `NATIVE_WORKSPACE` | `../../workspace` | 通用工作区 → /workspace（wheel 产物在其 dist/） |
| `NPU_TVM_PATH` | `../../../../../external/chaos/npu_tvm` | TVM 源码宿主路径 |
| `NPUUSERTOOLS_PATH` | `../../../../../external/containers/workspace/dev/npuusertools` | xmnn 源码宿主路径 |
| `MODELS_PATH` | `../../../../../external/chaos/models` | 模型目录宿主路径 |
| `USER_PASSWORD` / `JUPYTER_TOKEN` | 空（自动生成） | 登录凭证 |
| `SSH_PUBLIC_KEY` / `GRANT_SUDO` | 空 / `yes` | SSH 公钥 / devuser sudo |
| `OMP_NUM_THREADS` / `NUITKA_JOBS` | `4` / `8` | 线程与 Nuitka 并发 |
| `PIP_MIRROR` / `CONDA_MIRROR` | `official` | 构建期镜像源（official/aliyun/tuna）。**无前缀构建参数单一事实源（C15）**：`invoke native.build`、`native.up` 的 compose 内联 build、裸 `podman-compose build` 三处同键读取；`--pip-mirror/--conda-mirror` 旗标只覆盖单次 `build` |
| `BASE_IMAGE`（build args + invoke 同键） | `localhost/jupyter-podman-rootless:latest` | 基底镜像覆盖（同样被 `native.build`/`native.up` 读取，C15） |
| `TORCH_FLAVOR` | 空（不装） | torch 形态白名单 `空`/`cpu`/`cu130`（C15 无前缀键，compose build args + invoke 同键）。`invoke native.build --torch cu130` 只覆盖单次构建；改 `.env` 后需重建镜像。flavor 不参与镜像 tag，但**进归档名**（C20）并决定 `native.load` 选哪个归档。**cu130 形态同时提供 nvcc 编译器工具链**（13.4.92，`/usr/local/bin/nvcc` + `CUDA_HOME=/usr/local/cuda`，C25） |
| `GPU_DEVICE` | 未设 | GPU 设备双形态：`/` 开头=宿主机设备路径，否则=CDI 引用；**未设时自动探测 `NVIDIA CDI（规格+/dev/nvidiactl 双条件）→ /dev/dri → /dev/dxg`**（C19，纯 N 卡也注册 /dev/dri 故 CDI 必须前置；命中 NVIDIA 路径先做 nvidia-smi 驱动健康预检）。**仅 `up --gpu` 时生效**（默认零透传） |
| `NATIVE_OFFLINE` | `0`（关） | 离线总开关（**非 compose 插值键**，由 invoke 读取并经 `-e` 透传进容器）：开启后 `up` 强制跳过构建（`--no-build` 恒真，非离线亦然，C16）、`build` 直接 Exit(1)、容器内打包禁网兜底；等价 `invoke native.up --offline`，关闭用 `--no-offline` |
| `NATIVE_PASSTHROUGH_IMAGE_TAG` | `localhost/native-dev:passthrough` | 透传形态镜像 tag：内容与基础 tag 完全相同，缺失时自动 `podman tag`（零空间零构建）。**仅 `up --passthrough` 时生效** |
| `DBUS_SESSION_BUS_PATH` | `/run/user/1000/bus` | 只读 bind 进容器的会话 D-Bus socket；可改 `/run/dbus/system_bus_socket`（系统总线）。门禁 `test -S` 必须为 socket |
| `HOST_NET_SSHD_PORT` | `2223` | host 形态容器 SSH 直接绑定的宿主端口；Jupyter 固定 8888 不可换。门禁 `ss -lnt` 查 8888/此端口占用 |
| `USB_DEVICE` | `/dev/bus/usb` | USB 设备路径（可指 `/dev/bus/usb/001/002` 单设备）。**仅 `up --usb` 时生效**；WSL2 须先 usbipd-win attach 到 podman-machine-default，门禁 `test -e` |

## 与相关栈/目录的关系

| 维度 | 本叠加层（native-dev） | onnx-quantized 叠加层 | scratch xmnn-notebook 栈（.temp，不入库） | external/chaos/ai（Docker 谱系） |
|---|---|---|---|---|
| 定位 | **源码开发 + wheel 打包** | ONNX 量化分析 | wheel 消费型 Notebook | 旧一体化参考工程 |
| 源码 | 运行时 bind 挂载（可调试、零修改） | 不挂载 | 不挂载 | BuildKit rw bind + chaos 根构建上下文 |
| 工具链 | 镜像内 LLVM 22 + Nuitka 4.2.1 | ONNX 五包 | 仅 wheel 运行依赖 | Docker 多阶段 + DinD，privileged |
| 对 ai 依赖 | **无（打包内核自包含，仅事实参考）** | 无 | 依赖预构建镜像标签 | — |
| 驱动 | `invoke native.*` / 裸 compose | `invoke quant.*` / 裸 compose | 裸 compose（scratch） | docker compose + 自建 build.sh |
