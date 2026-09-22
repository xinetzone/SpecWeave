---
id: "native-dev-gpu-and-torch"
title: "GPU 透传与 torch 可选能力"
source: "README.md#gpu-与-torch-可选能力默认全关c18c19c20"
---
# GPU 透传与 torch 可选能力（默认全关，C18·C19·C20）

两项能力都**默认关闭**：不开时镜像体积、设备透传面与离线契约与改造前一致。

## GPU 透传：`invoke native.up --gpu`

默认**零设备透传**（只继承基底的 `/dev/fuse`）。加 `--gpu` 才叠加 GPU 覆盖文件，
设备由 `GPU_DEVICE` 决定（与根 `invoke run --gpu` 同键同语义）：

| `GPU_DEVICE` 取值 | 效果 |
|---|---|
| 以 `/` 开头 | 该宿主机设备路径，如 `/dev/dri/renderD128`（内核预检存在性，缺失即 fail-fast） |
| 其他 | CDI 引用，如 `nvidia.com/gpu=all`（宿主先 `nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml`；内核预检 `/etc/cdi` 或 `/var/run/cdi` 下有 `*.yaml`） |
| 未设 / 空 | **自动探测**（C19）：按 `NVIDIA CDI（CDI 规格 + /dev/nvidiactl 双条件）→ /dev/dri → /dev/dxg` 取第一个命中的形态 |

```bash
invoke native.up --gpu                                  # 自动探测设备形态
GPU_DEVICE=nvidia.com/gpu=all invoke native.up --gpu    # NVIDIA CDI（.env 写同键亦可）
```

**设备形态 → 覆盖文件**（`overlay_core.resolve_gpu_device` 解析，`GPU_DEVICE`
解析结果回写环境后由 compose 插值消费，终端提示与容器实收同源）：

| 探测命中 | 形态 | 叠加文件 | 额外声明 |
|---|---|---|---|
| `nvidia.com/gpu=all`（显式 CDI，或自动探测：`/etc/cdi`·`/var/run/cdi` 下有规格**且** `/dev/nvidiactl` 存在） | `generic` | [`compose.gpu.yaml`](../compose.gpu.yaml) | `--device nvidia.com/gpu=all`（CDI 同时注入计算节点、libcuda 与 nvidia-smi）；up 前跑宿主 `nvidia-smi` 健康预检 |
| `/dev/dri`（Intel/AMD；或无 CDI 规格的 N 卡 DRM 形态） | `generic` | [`compose.gpu.yaml`](../compose.gpu.yaml) | `--device ${GPU_DEVICE:-/dev/dri}` |
| `/dev/dxg`（WSL2 GPU 半虚拟化） | `wsl` | [`compose.gpu.wsl.yaml`](../compose.gpu.wsl.yaml) | `--device /dev/dxg` + 三条 ro 挂载：宿主 `/usr/lib/wsl/lib/libcuda.so.1` → `/usr/lib/libcuda.so.1`、`libdxcore.so` → `/usr/lib/libdxcore.so`、目录 `/usr/lib/wsl/drivers` → 同路径 |

> **WSL2 为什么要额外挂库与驱动目录**（2026-09-20 两轮实测）：WSL2 发行版里没有
> `/dev/dri`（只有 `/dev/dxg`），且 `/dev/dxg` 只是半虚拟化通道，libcuda 由
> WSL 宿主提供。第一轮判据是 `CDLL("libcuda.so.1")` 能否加载，只测出「挂单文件
> `libcuda.so.1` 即可」；装 cu130 torch 复核时才发现 **「库能加载」≠「设备可见」**
> ——只挂 libcuda 时 `cuInit()` 返 `100`(CUDA_ERROR_NO_DEVICE)、
> `torch.cuda.is_available()` 恒 `False`。逐项差分后最小充分条件是**三条 bind
> 齐备**：`libcuda.so.1`（缺则 CDLL 直接失败）+ `libdxcore.so`（DXCore 桥接库）
> + `/usr/lib/wsl/drivers`（Windows 驱动库目录，libcuda 初始化时扫描）。仅
> `--device /dev/dxg`、仅设 `LD_LIBRARY_PATH`、挂整目录 `/usr/lib/wsl/lib`
> 都**不**能让 CUDA 可用；`--cap-add SYS_ADMIN`、`seccomp=unconfined` 无效，
> `--privileged` 有效但**非必要**（本形态零特权）。取舍：**刻意不设
> `LD_LIBRARY_PATH`**——`environment` 是 mapping 替换语义，覆盖会冲掉本栈已声明的
> TVM 库路径；三条挂载点都在基底默认搜索路径上，无需改环境变量。

设备真的不存在时（如宿主未装驱动）`--gpu` 会 **fail-fast** 并打印中文指引，
而不是把 `Error: stat /dev/dri: no such file or directory`（exit 125）抛给 podman。

> **纯 N 卡宿主为什么 CDI 必须前置于 /dev/dri**（2026-09-20 实测）：NVIDIA 驱动
> 加载 `nvidia_drm` 后同样注册 `/dev/dri/card*` 与 `/dev/dri/renderD*`，旧探测顺序
> （/dev/dri → /dev/dxg）会把纯 N 卡误判成 DRM 形态：只挂渲染节点，CDI 注入的
> `libcuda.so` 与 `nvidia-smi` 全部缺席，容器内 `torch.cuda.is_available()` 恒
> `False` 且无任何设备节点。新顺序用「CDI 规格存在 **且** `/dev/nvidiactl` 存在」
> 双条件识别 NVIDIA 形态；两个条件缺一（如 Intel 宿主恰好装了 nvidia-container-toolkit
> 但无 N 卡）仍安全回退 `/dev/dri`，Intel/AMD/WSL 路径零行为变化。
>
> **NVIDIA 驱动健康预检**：选中 NVIDIA 路径（显式 CDI 或自动命中）后，先在宿主跑
> `nvidia-smi`。最常见的损坏是**驱动升级后内核模块未重载**——`/proc/driver/nvidia/version`
> 的模块版本旧于 dpkg 里的用户态库版本，宿主自己 `nvidia-smi` 都报
> `Failed to initialize NVML: Driver/library version mismatch`。此时继续 up 只会
> 得到一个设备齐全但 CUDA 初始化失败的容器，故直接 fail-fast，中文指引给出
> `sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml`（用 `/etc/cdi`
> 持久路径，勿用重启即失的 tmpfs `/var/run/cdi`）与重启/模块重载命令。CDI 规格
> 过期（内部 `host-driver-version` 停留在旧驱动）的症状相同，重建规格即可。

裸 compose 等价：`podman-compose -f compose.yaml -f compose.gpu.yaml up -d`
（WSL2 换成 `-f compose.gpu.wsl.yaml`；两者互斥，**不要同时加载**——devices 会重复）。
容器内验证**要看设备枚举而非只看库能否加载**（只验 `CDLL` 会把 NO_DEVICE 误判为成功）：

```bash
podman-compose exec native /opt/conda/bin/python -c \
  "import ctypes; l=ctypes.CDLL('libcuda.so.1'); n=ctypes.c_int(0); \
   print('cuInit=', l.cuInit(0), 'count=', (l.cuDeviceGetCount(ctypes.byref(n)), n.value)[1])"
# cuInit= 0 count= 1 才算通（100 = CUDA_ERROR_NO_DEVICE，仍是驱动库/目录缺失）
```

**GPU 归运行期维度，故没有 `build --gpu`**：透传只改 compose 文件集（`--device`
+ 三条只读 bind），**不动镜像内容**，构建期没有 GPU 相关对象可改——镜像里唯一与
GPU 相关的差异是 torch 形态，已由 `build --torch` 承担（见下节）。两个维度可自由
组合，`invoke native.up --gpu --offline` **实测可用**（离线只禁构建，与设备探测零耦合；
见 [docs/11 离线契约](../../../docs/11-native-overlay.md)）。

## torch 形态：`invoke native.build --torch cpu|cu130`

默认镜像**不含 torch**。仅当 `--torch`（或 `.env` 写 `TORCH_FLAVOR=`）时才装
`torch==2.14.0`：`cpu` 走 CPU 索引，`cu130` 走 CUDA 13.0 索引
（`download.pytorch.org/whl/<flavor>`，装进 base env `/opt/conda`）。

```bash
invoke native.build --torch cu130    # 装 CUDA 版 torch（构建期守卫 §8 断言形态）
invoke native.down && invoke native.up --skip-build --gpu   # 重建容器并透传 GPU
podman-compose exec native python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available())"
```

> **改 flavor 后必须「重建镜像 + 重建容器」两步**：`up` 恒 `up -d --no-build`，
> 且 podman-compose 的配置哈希**不含镜像 digest**——只跑 `up` 会让容器继续绑在旧
> 镜像上，静默不生效（追问「装了 torch 但 `import torch` 仍报 ModuleNotFoundError」
> 多半卡在这里）。判据：`up` 横幅的凭证（entrypoint 首启 `pwgen` 生成）逐字未变即
> 说明容器**没有**被重建。
>
> **离线侧组合**（两阶段）：有网机 `invoke native.build --torch cu130 && invoke native.save`
> → 无网机 `invoke native.load --path <归档>` → `invoke native.up --gpu --offline`。
> CUDA 版 torch 属**镜像内容**，离线侧不补装（`--offline` 只禁构建，与 GPU 透传正交）。

- **换 flavor 必须重建**：flavor **不参与镜像 tag**（沿用 `NATIVE_IMAGE_TAG`），
  改 `.env` 后要 `invoke native.build` 而非指望 `up` 增量刷新。
- **跨三处一致要写 `.env`**（C15）：`--torch` 旗标只覆盖单次 `build`，
  `up` 内联构建与裸 compose 读的是 `.env TORCH_FLAVOR`。
- **cu130 是当前唯一与 CPU 侧同 pin 的 CUDA 索引**（实测 cu129→2.13.0、
  cu128→2.11.0），换索引会引入版本漂移。
- torch 属可选依赖，**不进** `builder/pyproject.toml`，离线完备性守卫不受影响；
  空形态镜像仍离线自足。
- **cu130 形态同时提供 CUDA 编译器工具链（nvcc，C25）**：容器内可直接
  `nvcc -V` 与编译/链接/运行 `.cu`——命令是 `/usr/local/bin/nvcc`（包装器），
  `CUDA_HOME=/usr/local/cuda` 已由镜像 ENV 提供（`torch.utils.cpp_extension`
  等生态工具可直接用），`/etc/ld.so.conf.d/` 已登记农场 `lib64`（**产物开箱即跑，
  无需设 `LD_LIBRARY_PATH`**）。**编译器版本 13.4.92**，与 torch 的 CUDA 13.0 运行时
  **不同轨**：这是基座约束（Ubuntu 26.04 / glibc 2.43 与 CUDA 13.0 的 crt 头
  规格冲突，13.0 系实测编不过），不是可选偏好；`""`/`cpu` 形态**零 CUDA 编译器**。
  镜像构建期守卫 §9 会**真编译 + 真链接**一个最小 `.cu`（只看 `nvcc -V` 不算数）。

  ```bash
  # 验证（栈运行时）
  podman-compose exec native nvcc -V      # → Cuda compilation tools, release 13.4, V13.4.92
  # 最小算例（仅编译，无需 GPU 设备；链接用 -lcudart，运行需 up --gpu 透传设备）
  podman-compose exec native bash -lc 'printf "#include <cuda_runtime.h>\n__global__ void k(int*p){p[0]+=1;}\n" > /tmp/k.cu && nvcc -c /tmp/k.cu -o /tmp/k.o && echo COMPILE-OK'
  ```

  > **本机 GPU 提示（2026-09-20 实测）**：本机为 **RTX 5050 Laptop（cc 12.0 /
  > sm_120）**，而 nvcc 缺省 `-arch` 是 sm_75——缺省产物**能编能链、启动期报**
  > `the provided PTX was compiled with an unsupported toolchain`（PTX JIT 被驱动
  > 拒绝）。编译时加 `-arch=native`（设备可见时）或 `-arch=sm_120` 即可正常运行
  > （实测 `result=42`）。镜像**刻意不预设 arch**：`-arch=native` 需要编译期可见
  > 设备（构建期无 GPU），预设还会把产物绑死本机。

## 归档可辨识：形态进归档名（C20）

cpu 与 cu130 两份镜像 **tag 相同**（`localhost/native-dev:latest`），形态只在镜像内
LABEL 里。若归档名不携带形态，两者同族同名、共用同一个 `-latest` 软链，无网侧
`load` 会**静默导入错形态**（直到容器内 `torch.cuda` 为空才暴露）。故 `save`
会把 LABEL 形态写进归档名：

```bash
invoke native.save    # → .image-cache/localhost-native-dev-latest-torch-cu130-<id12>-<时间戳>.tar.gz
invoke native.load    # 按 .env TORCH_FLAVOR 形态挑归档；形态不符直接 Exit(1)
```

| 场景 | `load` 行为 |
|---|---|
| 未给 `--path`，`.env TORCH_FLAVOR=cu130` | 只在标注 `-torch-cu130-` 的归档里取最新；无匹配则 Exit(1) |
| 未给 `--path`，`TORCH_FLAVOR` 为空 | 不过滤，取最新（历史语义），但仍打印归档形态供核对 |
| `--path` 点名归档，形态与 `TORCH_FLAVOR` 不符 | **Exit(1)**（校验先于导入），提示改 `.env` 或换归档 |
| `--path` 点是 C20 之前的旧归档（无形态标注） | 打印提示但**不拦截** |

缺形态时归档名**不带** `-torch-` 段（与历史产物逐字一致）；形态段必须带
`-torch-` 标记，否则会与镜像 tag 自带的 `-latest` 段互相冒充。
