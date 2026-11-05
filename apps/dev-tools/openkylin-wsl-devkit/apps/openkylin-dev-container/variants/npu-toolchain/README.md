# npu-toolchain 变体容器

在 openKylin 3.0 离线基线镜像（`localhost/openkylin:3.0`）之上，叠加 **conda Python 3.14 + 原生构建工具链（CMake / Ninja / GCC）**，用于在服务器上跑通 `/workspace/ai/notebook/libs/npu_tvm` 与 `/workspace/ai/notebook/libs/npuusertools`（后者 `requires-python = ">=3.14"`，`scikit-build-core` 后端需要 CMake ≥ 3.18 与 Ninja ≥ 1.10）。

## 目录结构

```
variants/npu-toolchain/
├── Containerfile           # 单阶段：基线 → Miniforge3 → conda 环境 → 元数据与版本门禁
├── compose.yaml            # 声明式入口（拓扑镜像；真实入口是 scripts/run.sh）
├── scripts/
│   ├── run.sh              # 主入口：预检 → 镜像检查 → 命名卷 → 起容器 → 挂载探针 → 汇总
│   ├── all-in-one.sh       # 一键可重放：镜像 → 容器 → 挂载门禁 → LLVM 21 → 两库构建与断言 → 洁净度
│   ├── build-image.sh      # 构建变体镜像 + 构建后版本门禁
│   └── verify.sh           # 宿主侧验收（容器 / 运行契约 / 版本 / 挂载）
└── README.md
```

## 前置条件

| 项 | 要求 |
|---|---|
| 宿主 | 服务器 `ai@10.16.11.3`，rootless Podman 5.6.2，宿主 uid=1006 |
| 基线镜像 | `localhost/openkylin:3.0`，由离线包 `/media/pc/data/ai/.agents/wsl-images/openKylin-3.0-desktop-wsl-amd64.wsl`（gzip 压缩的 rootfs tar）经 `podman import` 产生；rootfs 内已含 gcc/g++ 15 与 python3.12，**不含** cmake、ninja |
| 宿主 LLVM 21 | `/usr/lib/llvm-21` 与 `/usr/include/llvm-21`（含 `llvm-c-21`）必须存在：容器内既无 apt 源、conda-forge 的 llvmdev 大包也不可达，只能从宿主复制；**LLVM 20 不可用**，npu_tvm 源码依赖 LLVM 21 的 `Intrinsic::getOrInsertDeclaration` |
| 网络白名单 | 仅 `mirrors.ustc.edu.cn`（conda 频道与 Miniforge 安装包）与 `mirrors.aliyun.com`（pip）可达；openKylin 官方软件源、`pypi.org` 均不可达 |
| 工作区挂载 | 宿主 `/media/pc/data/ai` 以读写 bind 挂载到容器 `/workspace/ai` |
| 命名卷 | `npu-build` → `/opt/build`（由 `run.sh` 按需创建） |
| Podman 中转目录 | `/media/pc/data/ai/.temp/podman-image-tmp`（`image_copy_tmp_dir`，脚本按需创建，不改配置） |

## 四条命令

在服务器上执行（宿主路径可直接访问，无需远程跳板）：

```bash
cd /media/pc/data/ai/notebook/dev/libs/AI/apps/dev-tools/openkylin-wsl-devkit/apps/openkylin-dev-container/variants/npu-toolchain

# 1. 构建变体镜像（先断言基线镜像存在，构建后跑 python/cmake/ninja/sys.prefix 门禁）
bash scripts/build-image.sh

# 2. 预检 + 起容器 + 挂载探针（PASS/FAIL 汇总表，任一 FAIL 非零退出）
bash scripts/run.sh up

# 3. 宿主侧验收
bash scripts/verify.sh

# 4. 一键全链路（镜像已存在时加 --skip-build-image 省时；--full 追加 21 分钟端到端冒烟）
bash scripts/all-in-one.sh --skip-build-image
bash scripts/all-in-one.sh --full
```

`all-in-one.sh` 依次执行 S1 基线镜像 → S2 变体镜像构建 → S3 容器启动 → S4 挂载门禁 → S5 LLVM 21 供给 → S6 npu_tvm → S7 npuusertools → S8 端到端冒烟（仅 `--full`）→ S9 两库 git 洁净度，每步输出 `STEP <id> <name> ... PASS|FAIL|SKIP`，末尾打印汇总表。退出码语义：`0` 全部 PASS 或按参数 SKIP，`1` 至少一个 FAIL，`2` 参数错误或运行环境不可用（podman 缺失/不可达）。全量日志 `tee` 到 `/workspace/ai/.temp/npu-toolchain/logs/all-in-one-<YYYYmmdd-HHMMSS>.log`，末尾回显日志路径。其它开关：`--skip-tvm`、`-h/--help`。

脚本可重复执行（幂等）：LLVM 21 已就位则跳过宿主复制，容器已在运行不重复启动，`ninja` 无改动即 `no work to do`。

`run.sh` 其它子命令：`down`（删除容器，保留命名卷）、`shell`（进入容器）、`status`（容器/卷/镜像状态）。

## 与 compose.yaml 的关系

`compose.yaml` 只是同一拓扑的声明式镜像，便于审阅与工具化；**主入口是 `scripts/run.sh`**，因为起容器前需要断言工作区可读、镜像已存在、命名卷就绪，起容器后还要做挂载探针。

## 挂载契约

- 宿主 `/media/pc/data/ai` → 容器 `/workspace/ai`：读写 bind，`propagation=rshared`，挂载源缺失即报错（不自动创建空目录）。
- `--userns=keep-id`：容器内运行用户即宿主 uid 1006。
- 挂载探针写在 `/workspace/ai/.temp/npu-toolchain/.probe`：容器内 `stat -c '%a %u'` 必须为 `700 1006`，且该文件在宿主侧可见（写穿透）。
- 构建产物落命名卷 `/opt/build`，不写回工作区。

## 两库验收

两个库位于宿主 `/media/pc/data/ai/notebook/libs/`，经 bind 挂载为容器内 `/workspace/ai/notebook/libs/`；所有构建产物落命名卷 `/opt/build`，不写回工作区。

### npu_tvm

**陷阱**：仓库根**没有** `config.cmake`，`cmake/config.cmake` 不会被 include，所以 `USE_CODEGENC` / `USE_LLVM` 必须在命令行显式传入。漏传的典型症状是 `Attribute 'RelayToTIR' is not registered`（未注册 `ccompiler` target 与 `RelayToTIR` 属性表）或 `target.build.llvm is not enabled`（无 host codegen）。

```bash
cmake -G Ninja -S /workspace/ai/notebook/libs/npu_tvm -B /opt/build/npu_tvm \
  -DCMAKE_BUILD_TYPE=Release -DUSE_CODEGENC=ON -DUSE_LLVM=/opt/build/llvm21/bin/llvm-config
ninja -C /opt/build/npu_tvm tvm
```

产物 `/opt/build/npu_tvm/libtvm.so`（约 79 MB）。

LLVM 21 全部由宿主供给（容器内无 apt 源，conda-forge 的 llvmdev 大包不可达）：`llvm-config` 用 `podman cp` 复制为 `llvm-config.real`，`libLLVM*` / `lib/cmake` / 头文件用 `tar | podman exec tar -x` 分发到 `/opt/build/llvm21/{bin,lib,include}`，最后写一个 `llvm-config` 包装器把输出中的宿主前缀改写为容器内前缀。S5 幂等：`llvm-config --version` 已是 21.x 即整段跳过。

断言所需环境变量（S6 同时补 `LD_LIBRARY_PATH=/opt/build/llvm21/lib` 作为新建卷未带 rpath 时的兜底）：

```
PYTHONPATH=/workspace/ai/notebook/libs/npu_tvm/python:/workspace/ai/notebook/libs/npu_tvm/vta/python:/workspace/ai/notebook/libs/npuusertools
TVM_LIBRARY_PATH=/opt/build/npu_tvm
PYTHONUSERBASE=/opt/build/npuusertools/userbase
HOME=/tmp/tvmhome  MPLCONFIGDIR=/tmp/mplconfig
```

### npuusertools

系统 `site-packages` 只读，安装必须同时满足三件套：

```bash
cd /workspace/ai/notebook/libs/npuusertools
BUILD_DIR=/opt/build/npuusertools bash scripts/build.sh
PYTHONUSERBASE=/opt/build/npuusertools/userbase \
  python -m pip install --no-cache-dir --no-build-isolation --user -e . \
  --config-settings=build-dir=/opt/build/npuusertools
```

- `BUILD_DIR`：把 CMake / `scikit-build-core` 的构建目录重定向到命名卷；
- `PYTHONUSERBASE`：把 `--user` 的安装前缀从 `$HOME/.local` 改到卷内；
- `--user`：系统前缀只读，不能直接写入。

### 已验证结果

| 项 | 结果 |
|---|---|
| `import tvm` | 0.19.0；`tvm.target.Target("llvm")` 与 `Target("ccompiler")` 均可解析 |
| `import xmnn` | 指向 `/opt/build/npuusertools/userbase/lib/python3.14/site-packages/xmnn/__init__.py` |
| `onnx.yolov5s` 端到端 | `EXIT=0`，6/6 模型编译全部完成，1245.77 s |

## 已知边界

- **无软件包管理安装层**：openKylin 官方源不可达，工具链全部来自 conda-forge，`make` 与 `zlib` 也由 conda 提供以补齐 rootfs 缺失。
- **不发布任何端口**：基线 rootfs 不运行服务，容器仅作常驻构建环境，通过 `podman exec` 进入。
- **无远程登录服务**：基线不含 sshd，也不安装。
- **容器内冒烟不替代 npu_tvm 官方验证**：本镜像只证明 Python/工具链/挂载就绪；`npu_tvm` 的最终验证仍须在官方验证环境（`zhangzhenyu/tvm`，历史文档中曾误写为 `zhangchenyu/tvm`）的服务器上完成。
- **`two_inputs` 不可用（环境受限偏差）**：其 pytorch 前端需要 `import torch`，但可达频道上 torch 仅有 CUDA 13.2 构建，导入即报 `libcublasLt.so.*[0-9] not found`；CPU wheel 不在镜像网络白名单内。本流程不尝试安装 torch，只保留 ONNX 前端的 `onnx.yolov5s` 作为端到端证据。
- **`npu_tvm` 存在用户既存改动**：`vta/python/vta/export_xm.py` 在 `git status --porcelain` 中恒为 1 行（mtime 早于本流程），属用户既存改动，本流程只记录、不改不滚；`npuusertools` 必须为 0 行。
- **rootless 不使用提权模式**：仅使用 `/dev/fuse` + `label=disable` + `cgroupns host` + `userns keep-id`。

## 回滚

```bash
bash scripts/run.sh down          # 等价于 podman rm -f npu-toolchain
podman rmi localhost/openkylin-npu-toolchain:3.0
podman volume rm npu-build        # 需要保留构建产物时跳过
```

基线镜像 `localhost/openkylin:3.0` 不受本变体影响，无需回滚。