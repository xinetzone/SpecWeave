# XMNN 开发与 wheel 打包叠加层（Podman rootless + podman-compose）

> 一句话：在 `localhost/jupyter-podman-rootless:latest` 之上做一层工具链叠加，
> 运行时把 **npu_tvm / npuusertools / models 源码 bind 挂载进容器**，提供
> tvm/vta/xmnn 的源码调试环境（SSH + JupyterLab + xmnn-dev 内核），并在
> 容器内用 **LLVM/Clang 22 + Nuitka 4.2.1** 一键打出 cp314 的
> `xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl`。

- **镜像**：`localhost/xmnn-dev:latest`（薄叠加；含完整编译工具链，体积大于量化栈）
- **双 Python ABI**：base env `/opt/conda/bin/python` = **cp314 GIL enabled**
  （Nuitka 编译/打包/xmnn-dev 内核，3.14.7）；main env = **cp314t**
  （Jupyter 服务不变）；LLVM/Clang 22.1.8 工具链装在 main env
- **服务**：SSH（容器 22 → 宿主 **2223**）+ JupyterLab（**8890**），
  supervisord 托管，沿用基底 entrypoint
- **源码**：运行时挂载，容器内固定路径 `/workspace/npu_tvm`、
  `/workspace/npuusertools`、`/workspace/models`（镜像构建期零接触源码）
- **编排**：podman-compose（rootless、无 privileged）；AI 硬约束见
  [../../.agents/rules/xmnn-overlay.md](../../.agents/rules/xmnn-overlay.md)

## 包含什么

| 能力 | 实现 |
|---|---|
| C/C++ 工具链 | LLVM/Clang/lld 22.1.8、cmake、ninja、make、ccache（main env，conda-forge） |
| 系统工具 | patchelf（wheel RPATH）、gdb（源码调试） |
| Nuitka 打包栈（base env） | nuitka==4.2.1、scikit-build-core、build、wheel、invoke、ipykernel + pyproject 声明的全部 xmnn 运行时依赖 |
| 打包内核 | `/opt/xmnn-builder/`：pyproject.toml、CMakeLists.txt、bootstrap、build-wheel/build-tvm/verify-wheel 脚本（**自包含，不依赖 external/chaos/ai**） |
| Jupyter 内核 | `Python 3.14 (xmnn dev)`（argv=/opt/conda/bin/python，env 内嵌源码 PYTHONPATH） |
| 构建期守卫 | `/opt/xmnn-dev-smoke/_toolchain_guards.py`（双 ABI + 工具链 + LLVM 库 SONAME 实测 + §7 离线完备性） |

## 前置条件

1. podman machine（Windows 即 WSL2 后端）已运行；
2. 本地已有基底镜像，没有则先在 `apps/containers/client` 加载：
   ```bash
   invoke load        # localhost/jupyter-podman-rootless:latest
   ```
3. 宿主存在源码目录（默认仓库根 `external/chaos/`）：
   - `external/chaos/npu_tvm`（TVM 0.19.0 fork；若 `build/libtvm.so`
     已存在可直接打包，否则先 build-tvm——全量编译需先
     `git submodule update --init` 检出 dmlc-core 等子模块）
   - `external/chaos/npuusertools`（xmnn 包 + tools_cpp/autolibs/fonts 数据）
   - `external/chaos/models`（模型目录）
4. **Windows 原生自动桥接**：与 quant.* 相同，Windows 原生 CPython 执行时
   自动桥接到 WSL 发行版（默认 `podman-machine-default`——client 专用
   rootless 发行版，与 flapping 的 Podman Desktop 默认 machine 相互独立、
   镜像存储不互通；`COMPOSE_WSL_DISTRO` 可指定、`none` 关闭回退门禁）。也可手动二选一：
   - WSL2 发行版内（推荐）：
     ```bash
     wsl -d <发行版>
     cd /mnt/d/spaces/SpecWeave/apps/containers/client
     pip install -e ".[compose]"
     ```
   - 或 client 自举容器：`invoke env.run-cmd --cmd 'inv xmnn.up'`

## 路径一：invoke xmnn.*（推荐）

在 `apps/containers/client` 下（WSL2/Linux/macOS）：

```bash
# ── 过程一：镜像环境构建（有网侧，一次性）─────────────────────────────
invoke xmnn.build                         # 构建工具链镜像（构建期自动跑双 ABI/SONAME/离线完备性守卫）
                                         #   --pip-mirror/--conda-mirror tuna|aliyun 可加速
                                         #   --torch cpu|cu130 额外装 torch（默认不装，见「GPU 与 torch 可选能力」）
invoke xmnn.save                         # 导出镜像归档（tar.gz + manifest/SHA256）→ 携带到无网机器

# ── 过程二：启动开发环境并开发（有网/无网通用）────────────────────────
invoke xmnn.load --path <归档.tar.gz>    # 从归档导入镜像（完整性校验后导入，导入幂等）
invoke xmnn.up --offline                 # 离线启动：不构建、不起网络请求（参见「两个过程」）
invoke xmnn.up                           # 有网侧常规启动（默认随带构建；--skip-build 直接用本地镜像）
invoke xmnn.up --gpu                     # 【可选】透传 GPU 设备（默认零透传，见「GPU 与 torch 可选能力」）
invoke xmnn.ps                           # 服务状态
invoke xmnn.smoke                        # 工具链守卫 + 源码挂载检查（libtvm 缺席时跳过算例段）

invoke xmnn.build-tvm                    # 【可选】栈内编译 TVM（build/libtvm.so 已存在则无需）
invoke xmnn.wheel                        # Nuitka 打包 xmnn whl（tvm 串行→vta/xmnn 并行）
                                         #   --jobs 4 内存紧张时；--clean 禁 ccache 全量重编；
                                         #   --tvm-flags "..." 透传额外 Nuitka 参数
podman-compose -p xmnn-dev exec xmnn \
    bash /opt/xmnn-builder/scripts/verify-wheel.sh   # 10 项隔离验证（临时 venv，不污染源码环境）

invoke xmnn.logs                         # 跟踪日志（Ctrl+C 退出）
invoke xmnn.down                         # 停止清理（workspace/源码保留；ccache 卷保留）
invoke xmnn.down --volumes               # 连 xmnn-ccache 命名卷一起删除
```

启动后访问（凭证可由环境变量覆盖，见 `.env.example`）：

| 服务 | 地址 | 凭证 / 入口 |
|---|---|---|
| JupyterLab | http://localhost:8890 | `JUPYTER_TOKEN`（留空则自动生成）；内核选 **Python 3.14 (xmnn dev)** |
| SSH | `ssh -p 2223 devuser@localhost` | `USER_PASSWORD`（留空自动生成） |

## 路径二：裸 podman-compose

在本目录（`overlays/xmnn-dev/`）下，无需 invoke：

```bash
cp .env.example .env           # 按需修改源码路径/端口/凭证/镜像源
podman-compose up -d           # 首次自动构建
podman-compose exec xmnn bash /opt/xmnn-builder/scripts/build-tvm.sh    # 可选
podman-compose exec xmnn bash /opt/xmnn-builder/scripts/build-wheel.sh
podman-compose down
```

> **离线（裸 compose）**：invoke 侧的 `--offline` 只是帮你把下面两件事一起做了——
> 镜像已导入时加 `--no-build` 跳过构建（`podman-compose up -d --no-build`），
> 以及给容器内打包脚本注入离线段（`podman-compose exec -e XMNN_OFFLINE=1 xmnn
> bash /opt/xmnn-builder/scripts/build-wheel.sh`）。镜像归档的导出/导入仍建议用
> `invoke xmnn.save` / `invoke xmnn.load`（带 manifest 校验），裸 compose 无对应命令。

`compose.yaml` 已内置 rootless 三必需（`/dev/fuse`、`label=disable`、
`cgroupns: host`），四个 bind 全部长语法，**无特权容器**；
`network_mode: bridge` 是 2026-09-14 同机实证（machine 无 systemd user bus
时默认项目网络 aardvark-dns 失败），见 compose 文件头注释。

> ⚠️ **控制平面纪律（2026-09-15 实证）**：选定裸 compose 就长期在本目录用
> 裸 compose，**不要与 `invoke xmnn.*`（WSL 桥接，下发 `/mnt/d/...`）交替
> 操作同一栈**——两者给容器打的 `config_files` 标签原文不同（`D:\...` vs
> `/mnt/d/...`），交替执行会被 podman-compose 强制 recreate，并可能留下孤儿
> rootlessport 导致 `up -d` 报 2223/8890 `address already in use`。已经
> 交替翻车时直接 `invoke xmnn.up --skip-build`，编排层 preflight 三道自愈
> （残留 down / 跨平面优雅 down / 孤儿端口定点回收）自动恢复，详见
> [30 秒修复速查表 W-I10](../../docs/04-troubleshooting-guide.md)。

## 开发调试工作流

- **改代码即时生效**：tvm/vta/xmnn 经 `PYTHONPATH` 从 `/workspace` 挂载树
  导入（不是 site-packages），宿主侧改代码容器内立即生效；Jupyter 用
  `Python 3.14 (xmnn dev)` 内核，SSH 进去默认 main env，调试/打包请用
  `/opt/conda/bin/python`（或内核）。
- **TVM 库加载**：`TVM_LIBRARY_PATH=/workspace/npu_tvm/build` 与
  `LD_LIBRARY_PATH`（build、build/vta、main/lib）由 compose 注入，
  libtvm.so 及其 LLVM 依赖无需手工配置。
- **wheel 产物**：`/workspace/dist/`（即默认 `apps/containers/client/workspace/dist/`，
  宿主可见；该目录被 client `.gitignore` 忽略）。
- **编译缓存**：Nuitka C 编译缓存在命名卷 `xmnn-ccache`（/root/.ccache），
  重复打包自动命中；`--clean` 仅当次禁用 ccache，不清缓存。

## 性能提示（9p）

npu_tvm 全量 C++ 编译在 Windows 挂载盘（/mnt/d，9p）上较慢。需要频繁重编
TVM 时，推荐把源码克隆到 WSL 原生文件系统并用变量改挂载：

```bash
# WSL 内
git clone <npu_tvm 仓库> ~/build/npu_tvm && cd ~/build/npu_tvm
git submodule update --init
# client/.env
NPU_TVM_PATH=/root/build/npu_tvm
```

Nuitka 打包内存占用随 `--jobs` 近似线性（jobs=8 约 15GB 峰值）；
机器内存不足用 `invoke xmnn.wheel --jobs 4`。

## 冒烟测试

| 脚本 | 何时跑 | 内容 |
|---|---|---|
| `smoke/_toolchain_guards.py` | 镜像构建期（root+devuser）/ `xmnn.smoke` / `podman run --rm` | 双 ABI（base GIL on、main cp314t）、LLVM 22.1/clang/cmake/ninja/ccache/patchelf/gdb、nuitka 4.2.1 且运行解释器在 `getSupportedPythonVersions()` 内、builder 资产、7 个 LLVM 依赖库 SONAME 实测、**§7 离线完备性**（编译/打包前端可解析 + pyproject 声明的 19 依赖全部已装，守卫自身不联网） |
| `smoke/smoke_mounts.py` | 栈运行时（`xmnn.smoke`/compose exec） | 三挂载点可见；libtvm 存在时 import tvm/vta/xmnn 来自 /workspace + tvm.build('llvm') 向量加；缺席时跳过并 exit 0 |

## 两个过程：镜像构建（有网）→ 离线开发（无网）

本栈的开发流程显式拆为两个过程——**过程一必须有网、过程二完全不需要网**。
拆分的理由：镜像构建期的 apt / mamba / pip 三段绕不开网络，而日常的
`build-tvm` / `wheel` / 调试没有任何联网必要；分开建模后，无网机器只要携带
**一个镜像归档 + 源码目录**，就能完成全部编译与打包。

### 过程一：镜像环境构建（有网侧，一次性）

目标是产出**离线自足镜像**：把 numpy/scipy 等 `pyproject.toml` 声明的全部运行时依赖、Nuitka 打包栈、
系统 gcc/g++、LLVM/Clang 22、cmake/ninja/ccache、patchelf 等编译期依赖全部
烤进镜像，并由**构建期离线完备性守卫**（`smoke/_toolchain_guards.py` §7）逐项
实测断言。守卫在构建期 fail-fast，把缺口暴露在有网侧，而不是搬到无网机器后才炸。

```bash
invoke xmnn.build        # 构建镜像；Layer 5 自动跑「离线完备性守卫」
invoke xmnn.save         # 导出归档：tar.gz + manifest/SHA256
#   产物落在镜像缓存目录（默认 ./.image-cache/），形如
#   xmnn-dev-<tag>-<时间戳>.tar.gz + 同名 .manifest.json（含 SHA256 与 latest 软链）
```

携带到无网机器的是两样东西：① `.image-cache/` 里的镜像归档（tar.gz + manifest）；
② 源码目录（`npu_tvm` 含 `3rdparty` 子模块、`npuusertools`、`models`）——源码
不在镜像内，由使用者自备（路径见参数表 `NPU_TVM_PATH` 等）。

### 过程二：启动开发环境并开发（无网侧）

```bash
invoke xmnn.load --path /path/to/xmnn-dev-*.tar.gz   # manifest 完整性校验后导入
invoke xmnn.up --offline                             # 不构建、不起任何对外网络请求

# —— 以下开发活动全部离线可用（脚本内已无联网点）——
invoke xmnn.build-tvm      # invoke config + cmake + ninja + gcc，全本地
invoke xmnn.wheel          # Nuitka 本地编译 + python -m build --no-isolation
podman-compose -p xmnn-dev exec xmnn \
    bash /opt/xmnn-builder/scripts/verify-wheel.sh   # 10 项隔离验证，亦无联网点
```

无网侧**不补装任何依赖**：缺任何一项都说明过程一的镜像不自足，正确处置是回有网侧
重跑 `invoke xmnn.build && invoke xmnn.save` 后重新携带归档——这正是把守卫放在
构建期的意义（两个过程之间只有单向传递，过程二没有回补手段）。

### 离线开关语义

等价开关：**`XMNN_OFFLINE=1`**（写 `.env` 或 shell export 均可，经 WSL 桥接透传
进容器）。`invoke xmnn.up --offline` 与 `XMNN_OFFLINE=1` 效果相同；`.env` 里开了
想临时关掉用 `invoke xmnn.up --no-offline`。注意 `--offline` 是**全链路**语义，
不只是跳过构建。

**`--skip-build` ≠ `--offline`**：`--skip-build` 只声明「这一次 `up` 不构建」，
**不注入** `XMNN_OFFLINE`（只影响 `up` 一步，`build` / `wheel` / `build-tvm` 行为
不变）。在无网机器上 `invoke xmnn.up --skip-build && invoke xmnn.wheel` 能起栈成功，
但容器内打包仍会尝试联网兜底而失败。**无网环境请一律用 `--offline`**；
`--skip-build` 只用于有网环境下省一次构建。

| 环节 | 离线下的行为 |
|---|---|
| `xmnn.up` | 强制跳过构建（`skip_build=True`）；`--no-build` 现已**恒真**（C16，在线同理），离线禁网不再依赖该分叉；镜像不存在时 fail-fast Exit(1) |
| `xmnn.build` | 镜像构建在任何情况下都需要网络，离线判定为真时**立即 Exit(1)** 并给出离线三选一指引，不进入构建流程 |
| `xmnn.wheel` | 容器内不再 pip 兜底 numpy/scipy（缺失即 Exit 2）；Nuitka 去掉 `--assume-yes-for-downloads`；缺系统 gcc 也 Exit 2 |
| `build-wheel.sh` pip 镜像 | 离线不再改写 pip config（`PIP_MIRROR` 在无网侧无意义） |

设计原则是**硬失败 + 可执行中文指引**，不做静默降级——离线环境里"悄悄联网然后
超时"比直接报错难排查得多。

## GPU 与 torch 可选能力（默认全关，C18）

两项能力都**默认关闭**：不开时镜像体积、设备透传面与离线契约与改造前一致。

### GPU 透传：`invoke xmnn.up --gpu`

默认**零设备透传**（只继承基底的 `/dev/fuse`）。加 `--gpu` 才叠加 GPU 覆盖文件，
设备由 `GPU_DEVICE` 决定（与根 `invoke run --gpu` 同键同语义）：

| `GPU_DEVICE` 取值 | 效果 |
|---|---|
| 以 `/` 开头 | 该宿主机设备路径，如 `/dev/dri/renderD128`（内核预检存在性，缺失即 fail-fast） |
| 其他 | CDI 引用，如 `nvidia.com/gpu=all`（宿主先 `nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml`；内核预检 `/etc/cdi` 或 `/var/run/cdi` 下有 `*.yaml`） |
| 未设 / 空 | **自动探测**（C19）：按 `/dev/dri → /dev/dxg` 顺序取第一个存在的设备 |

```bash
invoke xmnn.up --gpu                                  # 自动探测设备形态
GPU_DEVICE=nvidia.com/gpu=all invoke xmnn.up --gpu    # NVIDIA CDI（.env 写同键亦可）
```

**设备形态 → 覆盖文件**（`overlay_core.resolve_gpu_device` 解析，`GPU_DEVICE`
解析结果回写环境后由 compose 插值消费，终端提示与容器实收同源）：

| 探测命中 | 形态 | 叠加文件 | 额外声明 |
|---|---|---|---|
| `/dev/dri`（Intel/AMD、NVIDIA 直通设备） | `generic` | [`compose.gpu.yaml`](compose.gpu.yaml) | `--device ${GPU_DEVICE:-/dev/dri}` |
| `/dev/dxg`（WSL2 GPU 半虚拟化） | `wsl` | [`compose.gpu.wsl.yaml`](compose.gpu.wsl.yaml) | `--device /dev/dxg` + 单文件 ro 挂载宿主 `/usr/lib/wsl/lib/libcuda.so.1` → `/usr/lib/libcuda.so.1` |

> **WSL2 为什么要额外挂 libcuda**（2026-09-20 实测）：WSL2 发行版里没有
> `/dev/dri`（只有 `/dev/dxg`），且 `/dev/dxg` 只是半虚拟化通道，libcuda 由
> WSL 宿主提供。仅 `--device /dev/dxg`、仅设 `LD_LIBRARY_PATH`、挂整目录
> `/usr/lib/wsl/lib` 三种做法都**不能**让容器内 `CDLL("libcuda.so.1")` 成功；
> 唯一最小组合是 `--device /dev/dxg` + 单文件挂载到 `/usr/lib`（基底默认库
> 搜索目录）。取舍：**刻意不设 `LD_LIBRARY_PATH`**——`environment` 是 mapping
> 替换语义，覆盖会冲掉本栈已声明的 TVM 库路径。

设备真的不存在时（如宿主未装驱动）`--gpu` 会 **fail-fast** 并打印中文指引，
而不是把 `Error: stat /dev/dri: no such file or directory`（exit 125）抛给 podman。

裸 compose 等价：`podman-compose -f compose.yaml -f compose.gpu.yaml up -d`
（WSL2 换成 `-f compose.gpu.wsl.yaml`；两者互斥，**不要同时加载**——devices 会重复）。
容器内验证：`podman-compose exec xmnn ls /dev/dri /dev/dxg` 或
`podman-compose exec xmnn /opt/conda/bin/python -c "import ctypes; ctypes.CDLL('libcuda.so.1')"`。

### torch 形态：`invoke xmnn.build --torch cpu|cu130`

默认镜像**不含 torch**。仅当 `--torch`（或 `.env` 写 `TORCH_FLAVOR=`）时才装
`torch==2.14.0`：`cpu` 走 CPU 索引，`cu130` 走 CUDA 13.0 索引
（`download.pytorch.org/whl/<flavor>`，装进 base env `/opt/conda`）。

```bash
invoke xmnn.build --torch cu130    # 装 CUDA 版 torch（构建期守卫 §8 断言形态）
invoke xmnn.up --skip-build --gpu  # 起栈并透传 GPU
podman-compose exec xmnn python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available())"
```

- **换 flavor 必须重建**：flavor **不参与镜像 tag**（沿用 `XMNN_IMAGE_TAG`），
  改 `.env` 后要 `invoke xmnn.build` 而非指望 `up` 增量刷新。
- **跨三处一致要写 `.env`**（C15）：`--torch` 旗标只覆盖单次 `build`，
  `up` 内联构建与裸 compose 读的是 `.env TORCH_FLAVOR`。
- **cu130 是当前唯一与 CPU 侧同 pin 的 CUDA 索引**（实测 cu129→2.13.0、
  cu128→2.11.0），换索引会引入版本漂移。
- torch 属可选依赖，**不进** `builder/pyproject.toml`，离线完备性守卫不受影响；
  空形态镜像仍离线自足。

## 参数表（compose 插值 / .env 键）

| 键 | 默认值 | 用途 |
|---|---|---|
| `XMNN_IMAGE_TAG` | `localhost/xmnn-dev:latest` | 镜像标签 |
| `XMNN_CONTAINER_NAME` | `xmnn-dev` | 容器名（project name 固定 xmnn-dev） |
| `XMNN_SSH_PORT` / `XMNN_JUPYTER_PORT` | `2223` / `8890` | 宿主端口（与 onnx 2222/8888 错开） |
| `XMNN_WORKSPACE` | `../../workspace` | 通用工作区 → /workspace（wheel 产物在其 dist/） |
| `NPU_TVM_PATH` | `../../../../../external/chaos/npu_tvm` | TVM 源码宿主路径 |
| `NPUUSERTOOLS_PATH` | `../../../../../external/chaos/npuusertools` | xmnn 源码宿主路径 |
| `MODELS_PATH` | `../../../../../external/chaos/models` | 模型目录宿主路径 |
| `USER_PASSWORD` / `JUPYTER_TOKEN` | 空（自动生成） | 登录凭证 |
| `SSH_PUBLIC_KEY` / `GRANT_SUDO` | 空 / `yes` | SSH 公钥 / devuser sudo |
| `OMP_NUM_THREADS` / `NUITKA_JOBS` | `4` / `8` | 线程与 Nuitka 并发 |
| `PIP_MIRROR` / `CONDA_MIRROR` | `official` | 构建期镜像源（official/aliyun/tuna）。**无前缀构建参数单一事实源（C15）**：`invoke xmnn.build`、`xmnn.up` 的 compose 内联 build、裸 `podman-compose build` 三处同键读取；`--pip-mirror/--conda-mirror` 旗标只覆盖单次 `build` |
| `BASE_IMAGE`（build args + invoke 同键） | `localhost/jupyter-podman-rootless:latest` | 基底镜像覆盖（同样被 `xmnn.build`/`xmnn.up` 读取，C15） |
| `TORCH_FLAVOR` | 空（不装） | torch 形态白名单 `空`/`cpu`/`cu130`（C15 无前缀键，compose build args + invoke 同键）。`invoke xmnn.build --torch cu130` 只覆盖单次构建；改 `.env` 后需重建镜像。flavor 不参与镜像 tag |
| `GPU_DEVICE` | 未设 | GPU 设备双形态：`/` 开头=宿主机设备路径，否则=CDI 引用；**未设时自动探测 `/dev/dri → /dev/dxg`**（C19）。**仅 `up --gpu` 时生效**（默认零透传） |
| `XMNN_OFFLINE` | `0`（关） | 离线总开关（**非 compose 插值键**，由 invoke 读取并经 `-e` 透传进容器）：开启后 `up` 强制跳过构建（`--no-build` 恒真，非离线亦然，C16）、`build` 直接 Exit(1)、容器内打包禁网兜底；等价 `invoke xmnn.up --offline`，关闭用 `--no-offline` |

## 与相关栈/目录的关系

| 维度 | 本叠加层（xmnn-dev） | onnx-quantized 叠加层 | scratch xmnn-notebook 栈（.temp，不入库） | external/chaos/ai（Docker 谱系） |
|---|---|---|---|---|
| 定位 | **源码开发 + wheel 打包** | ONNX 量化分析 | wheel 消费型 Notebook | 旧一体化参考工程 |
| 源码 | 运行时 bind 挂载（可调试、零修改） | 不挂载 | 不挂载 | BuildKit rw bind + chaos 根构建上下文 |
| 工具链 | 镜像内 LLVM 22 + Nuitka 4.2.1 | ONNX 五包 | 仅 wheel 运行依赖 | Docker 多阶段 + DinD，privileged |
| 对 ai 依赖 | **无（打包内核自包含，仅事实参考）** | 无 | 依赖预构建镜像标签 | — |
| 驱动 | `invoke xmnn.*` / 裸 compose | `invoke quant.*` / 裸 compose | 裸 compose（scratch） | docker compose + 自建 build.sh |

## 排障

| 现象 | 处理 |
|---|---|
| `invoke xmnn.*` Windows 原生报门禁 Exit(1) | 自动桥接不可用时回退（无 wsl.exe/发行版缺失/`COMPOSE_WSL_DISTRO=none`）；正常路径自动桥接 `podman-machine-default`，无需手动操作 |
| `up -d` 报 `conmon exited prematurely` + `address already in use`（exit 125，2223/8890），常发生在裸 compose 与 invoke 交替后 | **跨控制平面标签分歧 + 孤儿 rootlessport**（详见 W-I10）；`invoke xmnn.up --skip-build` 的 preflight 三道自动恢复（残留 down / 跨平面优雅 down / 孤儿端口定点 kill）；日常纪律是同一栈固定单一控制平面。仍失败才查宿主占用（`netstat -ano \| findstr 2223`）或改 `.env` 端口 |
| build-tvm 报 dmlc-core 缺失 | 宿主 npu_tvm 树执行 `git submodule update --init` 后重试；**该步需联网**，属过程一预备（源码随归档一起在联网侧备好），无网侧无法补齐 |
| build-tvm 之前报 `variable-sized object may not be initialized`（VTA FSIM 的 VLA） | 已由 2026-09-15 引入系统 gcc/g++ 作编译前端修复（Clang 22 拒 VLA+初始化器、GCC 允许）；env `CC`/`CXX` 可覆盖回退 clang |
| build-wheel 开头报 libtvm.so 缺失（exit 2） | 先 `invoke xmnn.build-tvm`，或把含 build/ 的完整 npu_tvm 挂到 NPU_TVM_PATH |
| Nuitka Killed / OOM | `invoke xmnn.wheel --jobs 4`，machine 分配 ≥8 GB 内存 |
| wheel CMake FATAL：LLVM dependency glob 空 | 守卫会打印 libdir 实际 SONAME；按提示核对 CMakeLists 7 个 glob（conda 库版本漂移） |
| up 后 aardvark-dns / user scope bus 报错 | 已用 `network_mode: bridge` 规避；若复现检查该行未被删除 |
| 裸 compose 后 `client/workspace/` 出现 npu_tvm/npuusertools/models 空目录 | podman-compose 1.6 对相对 source + create_host_path 的 host 端预创建副产物，**真实挂载不受影响**（冒烟以 `/workspace/...` 路径前缀断言）；down 后 `rmdir` 即可。用 `invoke xmnn.up`（注入绝对路径）不会产生 |
| Jupyter 保存 notebook 报 `[Errno 13] Permission denied: '/workspace/.ipynb_checkpoints/...'` | rootless + 9p/drvfs 下容器内 root 预建的 checkpoint 目录在容器视角为 0:0 755，而 Jupyter 以 devuser(1000) 运行无 w 位。`invoke xmnn.up`/`xmnn.build` 经编排层 `ensure_workspace_checkpoint_writable` 幂等 `chmod 777` 该**单一目录**（不改属主、不递归、不碰源码树）；手工救急：宿主侧 `chmod 777 apps/containers/client/workspace/.ipynb_checkpoints` |
| 打包后外部源码出现 `.bak_tvm/.bak_vta/.bak_xmnn` | 直接重跑 `build-wheel.sh` 即可：注入器有四态自愈（残留注入态/截断态配干净 `.bak` 会自动还原）；仅当报「已含 PREAMBLE 但备份缺失」（Exit 2）时才需按提示 `git checkout -- <file>` 人工还原。还原为原 inode 内容回写，源码文件属主/模式/ACL 不变；`.bak_tvm.tmp.<pid>` 陈旧暂存文件会在下次注入时自动清扫 |
| wheel 一启动就报 `cp: preserving permissions for '...bak_tvm.tmp...': Invalid argument`（exit 1） | 旧镜像内的打包脚本用 `cp -p`/`cp -a` 复制了源码树 POSIX ACL——rootless 下 ACL 含未映射宿主 UID（多机 pc/ai）时内核 setxattr 必 EINVAL。2026-09-18 起脚本改为字节备份 + `cp -R`，**重建叠加镜像即可**：`invoke xmnn.build && invoke xmnn.down && invoke xmnn.up --skip-build`（宿主源码树无需改动） |
| conda 求解慢/失败 | `--conda-mirror tuna`（或 aliyun）；pip 侧 `--pip-mirror tuna` |
| 离线 `up --offline` 报本地无镜像（Exit 1） | 无网侧确实没有镜像。到**有网侧**先 `invoke xmnn.save`，把 `.image-cache/` 里的归档（tar.gz + manifest）拷过来，再 `invoke xmnn.load --path <归档.tar.gz>`。归档自带 SHA256，拷贝损坏会在 load 步暴露而不是启动后诡异失败 |
| 离线 `xmnn.wheel` 报 numpy/scipy 缺失或缺 gcc（exit 2） | 离线**不允许** pip 兜底。需回有网侧把依赖补进镜像（基底 env 或 `PIP_MIRROR` 构建期安装）后重新 `xmnn.save`；不要在无网侧改镜像或手工 pip（无网必失败） |
| 离线 `up` 仍尝试构建镜像 | 检查开关是否真的生效：`--offline` 必须写在 `up` 之后（`invoke xmnn.up --offline`），或 `.env` 里 `XMNN_OFFLINE=1`；若同时写了 `--no-offline` 会覆盖 `.env` 的开启项 |
