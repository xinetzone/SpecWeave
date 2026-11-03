---
type: "Spec"
title: "npu-toolchain 远程后端：LLVM 22 供给与 Python 3.14 复用"
frontmatter_spec_version: "v2.1.0-draft"
status: "implemented-draft（阶段 0–4 已实施，2026-11-03 实测）"
owner: "未指定"
part_of: "09-npu-toolchain-windows-host.md"
---

# npu-toolchain 远程后端：LLVM 22 供给与 Python 3.14 复用

> **本篇职责**：记录 LLVM 22 的供给决策与 Python 3.14 环境复用判定，并附 py314 / LLVM 22 / 容器现状的事实卡。
> **本篇不负责**：预检基线与架构图见[架构与决策](09-1-backend-and-decision.md)；挂载与 UID 见[挂载与存储](09-2-mounts-uid-storage.md)；两库构建与验证命令见[构建与验证](09-4-build-and-verify.md)；A3 判定见[验收与实测](09-5-acceptance-and-evidence.md)。

## 3.3 LLVM 22 供给与 Python 3.14 环境复用（决策）

**事实**：
- 宿主 `py314` 环境已含 LLVM **22.1.2**（`llvm-config`、`libLLVM-22.so`、`include/llvm`、`lib/cmake/llvm`、clang/lld 22.1.2）。
- 容器内当前只有 `/opt/build/llvm20`（20.0.0）与 `/opt/build/llvm21`（21.0.0），**无 22**。
- 容器内 conda 通道已配置为 USTC conda-forge，网络可达；容器无外网 Docker 依赖。

**决策（LLVM 供给）**：**在容器内安装 conda-forge `llvmdev=22.1.*`，与宿主版本对齐**（优先级从高到低）：

1. **首选：容器内 conda 安装 llvmdev 22.1.2**（`conda install -c ... llvmdev=22.1.*`，通道已就绪）。理由：与容器自身工具链同源、路径自洽、可重复构建，且与宿主版本号一致便于证据对齐。
2. **备选：宿主 `podman cp` 复制宿主 llvm 22 的 conda 包进容器后离线安装**（宿主 conda 缓存已存在，可 `conda create --offline`/`conda install --offline` 复用包）。
3. **不推荐：bind mount 宿主 py314 的 LLVM 目录进容器**。理由：`llvm-config --prefix` 与 `LLVMConfig.cmake` 内嵌宿主绝对路径，容器内不存在该前缀，CMake 读取会断裂；且跨发行版 glibc 差异不可控。

**决策（Python 3.14 环境复用）**：**不把宿主 conda 环境整体挂载/复制进容器**，而是在容器内维持自有 `main` 环境（现为 3.14.10），仅补装缺失包。判定依据：

| 候选 | 结论 | 理由 |
|---|---|---|
| 整体 bind mount 宿主 py314 作为容器运行时 | ❌ 否决 | 环境前缀耦合（`sys.prefix` 指向宿主）、跨发行版 ABI/glibc 不可控、镜像不可重复 |
| 复制宿主 py314 目录进镜像层 | ❌ 否决 | 体积与许可负担、版本漂移不可追溯 |
| **容器内自建/自维持同版本环境** | ✅ 采纳 | 镜像可重复、与 `Containerfile` 一致；宿主 py314 保留为「宿主侧构建备用」 |
| 宿主 py314 直接构建 Python 包层 | ⚠️ 仅作兜底 | 与容器内 libtvm 的 ABI 可能不一致，需显式 `TVM_LIBRARY_PATH`，只在容器安装失败时使用 |

**ABI 一致性检查项（新增）**：`python -c "import sysconfig; print(sysconfig.get_config_var('SOABI'), sysconfig.get_config_var('Py_GIL_DISABLED'))"` 在宿主与容器均应返回 `cpython-314-x86_64-linux-gnu 0`；若出现 `cpython-314t-...` 或 `1`，立即停止并改用 GIL 版环境。

**Python 3.14 过新导致的构建风险与替代**：容器内 `pip 26.1.2` / `setuptools 83.0.0` 对新版本支持良好；但 `npuusertools` 的 `pyproject.toml` 要求 `scikit-build-core>=1.0` 与 `setuptools-scm>=8.0`，**当前均缺失**，且 `wheel`、`cython` 缺失。可行替代：pip 通过清华镜像安装构建后端；若某版本包在 3.14 下无 wheel 且源码构建失败，则改用宿主 `python3.10` 仅构建纯 Python 包层（不带 C 扩展），并在规格外单独记录。

## 附录 B：Python 3.14 与 LLVM 22 事实卡（供实施直接引用）

**py314 环境**

| 项 | 值 |
|---|---|
| 环境路径 | `/media/pc/data/lxw/envs/anaconda3a/envs/py314` |
| 解释器 | `.../py314/bin/python`（Python **3.14.6**） |
| ABI | `SOABI=cpython-314-x86_64-linux-gnu`，`Py_GIL_DISABLED=0` → **cp314（GIL 版）** |
| site-packages | `.../py314/lib/python3.14/site-packages` |
| 已装 | pip 26.1.2、setuptools 83.0.0、numpy 2.5.1、cmake 4.4.2、ninja 1.13.0 |
| 缺失 | wheel、cython、scikit-build-core、setuptools-scm、tvm、xmnn |
| 头文件 | `.../py314/include/python3.14/Python.h` |
| EXT_SUFFIX | `.cpython-314-x86_64-linux-gnu.so` |

**LLVM 22**

| 项 | 值 |
|---|---|
| `llvm-config` | `/media/pc/data/lxw/envs/anaconda3a/envs/py314/bin/llvm-config` |
| 版本 | **22.1.2**（`--shared-mode=shared`） |
| prefix / libdir | `.../envs/py314` / `.../envs/py314/lib` |
| includedir | `.../envs/py314/include`（含 `llvm`、`llvm-c`） |
| cmakedir | `.../envs/py314/lib/cmake/llvm` |
| 共享库 | `libLLVM-22.so`、`libLLVM.so`、`libLLVM.so.22.1` |
| clang/lld | clang、clang++ 22.1.2；52 个 clang 系列可执行文件 |
| 其他版本 | base conda = 21.1.8；系统 `/usr/lib/llvm-21` = 21.0.0；`/usr/lib/llvm-20` = 20.0.0；专用环境 `envs/llvm22` = 22.1.2；**无系统 llvm-22** |

**容器内现状**

| 项 | 值 |
|---|---|
| 镜像 | `localhost/openkylin-npu-toolchain:3.0`，ID `e7244a0cc7a3`，14 GB，2026-11-02 02:04 构建 |
| Python | 3.14.10（conda `main`，通道 USTC conda-forge） |
| LLVM | `/opt/build/llvm22`=**22.1.8**（conda-forge `llvmdev`/`clang`；G3 处置后前缀内仅余 22 系）、`/opt/build/llvm20`=20.0.0、`/opt/build/llvm21`=21.0.0 |
| 构建产物 | `/opt/build/npu_tvm/libtvm.so` 存在；`/opt/build/npuusertools` 存在 |
| Python 包 | `tvm`、`xmnn` **均未安装** |

> **注（G3 已处置，2026-11-03）**：`/opt/build/llvm22` 前缀内曾混装 conda-forge 23 系包——`libllvm23 23.1.4`、`lld 23.1.4`、`llvm-openmp 23.1.4`，其中 `bin/ld.lld` 实为 **LLD 23.1.4**，其 `NEEDED` 条目引用 `libLLVM.so.23.1`。处置采用**隔离式移除**（未用 `conda remove`）：整批 `mv` 至 `/opt/build/.llvm23-quarantine-20261103/`（268 MB / 48 文件），并同步迁出 `conda-meta/` 中对应 3 个包描述，`conda-meta/*.json` 由 28 条降为 **25 条**。`libLLVM.so -> libLLVM.so.22.1`、`libLLVM-22.so`、`llvm-config`、`include/`、`lib/cmake/llvm` 均未被触及；前缀内现已无 23 系构件（残留 `libgomp.so*` 属 `libgomp 16.2.0`，非 LLVM 组件）。回归证据见[验收与实测 §9.2 D7 与 §9.4](09-5-acceptance-and-evidence.md)。副作用：`clang-22 -fopenmp` 所需的 `libomp.so` 随 `llvm-openmp` 一并移出，22 系 `lld` 本未安装。隔离副本（268 MB / 48 文件）已于同日删除，XFS 可用字节 315,729,219,584 → 316,010,168,320（+280,948,736 B，约 268 MiB）；`mv` 回滚路径随之失效，如需恢复须自 conda 通道重新安装。

## 相关文档

- [入口索引](09-npu-toolchain-windows-host.md)
- [挂载与存储](09-2-mounts-uid-storage.md)
- [构建与验证](09-4-build-and-verify.md)
- [验收与实测证据](09-5-acceptance-and-evidence.md)