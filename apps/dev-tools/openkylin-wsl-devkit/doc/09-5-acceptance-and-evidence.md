---
type: "Spec"
title: "npu-toolchain 远程后端：验收标准与实测证据"
frontmatter_spec_version: "v2.1.0-draft"
status: "implemented-draft（阶段 0–4 已实施，2026-11-03 实测）"
owner: "未指定"
part_of: "09-npu-toolchain-windows-host.md"
---

# npu-toolchain 远程后端：验收标准与实测证据

> **本篇职责**：先给出 A1–A9 可测量验收标准，再给出 2026-11-03 的实施结果与实测证据（判定表、偏差 D1–D6、容器内配置与产物、遗留问题）。
> **本篇不负责**：目标与非目标见[入口索引](09-npu-toolchain-windows-host.md)；验证方案与命令见[构建与验证](09-4-build-and-verify.md)；风险与回滚见[风险与待办](09-6-risks-todos-changelog.md)。

## 1.3 可测量的验收标准（A1–A9，替换 v1.x 中与 WSL/CIFS 绑定的条目）

| # | 标准 | 可观测证据 | 失败判定 |
|---|------|-----------|---------|
| A1 | SSH 免密可登录 | `ssh -o BatchMode=yes -o ConnectTimeout=8 ai@10.16.11.3 'whoami'` 返回 `ai` 且 exit 0 | 出现口令提示或 exit ≠ 0 |
| A2 | 远程 rootless + overlay + 非 CIFS graphroot | `podman info --format '{{.Host.Security.Rootless}} {{.Store.GraphDriverName}} {{.Store.GraphRoot}}'` 输出 `true overlay /home/ai/.local/share/containers/storage`；`findmnt -T <graphroot>` 显示 `xfs` 的 `/dev/sda1` | 驱动为 `vfs`，或 graphroot 落在 `cifs`/`fuse` 挂载 |
| A3 | LLVM 22 实测可用 | 宿主 `py314/bin/llvm-config --version` 返回 `22.1.2`；容器内 `llvm-config --version` 返回 `22.x`（`LLVM_CONFIG` 指向容器内 22 路径） | 返回 < 22 或命令不存在 |
| A4 | npu_tvm 构建通过 | `ninja -C /opt/build/npu_tvm tvm` exit 0 且 `libtvm.so` 存在；容器内 `python -c "import tvm; print(tvm.__version__)"` 成功 | exit ≠ 0 或 import 失败 |
| A5 | npuusertools 构建与导入通过 | `BUILD_DIR=/opt/build/npuusertools bash scripts/build.sh` exit 0；`pip install -e .` exit 0；`import xmnn` 成功 | 任一步 exit ≠ 0 |
| A6 | rootless 运行契约 | `podman inspect` 显示 `Privileged=false`、`CgroupMode=host`、`UsernsMode=keep-id`（或 `private` 且 UID 对齐）、`SecurityOpt` 含 `label=disable`；需要嵌套 podman 时含 `--device /dev/fuse` | 出现 `--privileged` 或缺少三必需 |
| A7 | 端口发布与 Windows 可达 | 发布容器端口后，Windows `Test-NetConnection -ComputerName 10.16.11.3 -Port <port>` 返回 True，且容器 `podman port` 显示 `0.0.0.0:<port>` | Windows 不可达或端口冲突 |
| A8 | 路径与属主一致性 | 容器内 `stat -c '%a %u:%g' /workspace/ai/notebook/libs/npu_tvm/CMakeLists.txt` 与宿主一致；容器内 `touch /workspace/ai/.temp/.probe` 后宿主可见该文件 | 写入失败或属主错乱 |
| A9 | 磁盘余量门禁 | `df -hT /media/pc/data` 的 `Avail` ≥ 50 GB（当前 298 GB） | 低于阈值，禁止启动构建 |

> **A3 版本区间的源码依据（延续 v1.x 结论）**：`cmake/utils/FindLLVM.cmake:229` 仅对 `< 40` FATAL；`cmake/modules/LLVM.cmake:32` 对 `< 60` FATAL；`src/target/llvm/llvm_compat.h` 的 `static_assert(TVM_LLVM_VERSION <= 229)` 使 **22.x 在允许区间内**（22.1.2 → 宏值 220 ≤ 229）；无任何 `>= 220` 特判，22 复用 21+ 代码路径。

## 9. 实施结果与实测证据（2026-11-03）

> 本节记录 v2 方案的落地结果。所有操作均在 Windows 侧经 SSH 与 `podman --remote`（或 `podman exec` 在容器内）执行；执行日志留存在工作区临时目录，按保留期自动清理，故本文档不引用其路径。

### 9.1 验收结果表（A1–A9）

| # | 判定 | 实测证据（命令 → 输出摘要） | 备注 |
|---|------|---------------------------|------|
| A1 | **PASS** | `ssh -o BatchMode=yes ai@10.16.11.3 whoami` → `ai`，exit 0 | 免密成立，无口令交互 |
| A2 | **PASS** | `podman --remote --connection remote-ai info` → `5.6.2`、`rootless=true`、`driver=overlay`、`os=ubuntu`；graphroot `/home/ai/.local/share/containers/storage`（软链落点 XFS `/dev/sda1`） | `--connection` 客户端缺陷已修复（偏差 D1），默认连接仍未切换 |
| A3 | **PASS** | 宿主 `py314/bin/llvm-config --version` → `22.1.2`；容器内 `/opt/build/llvm22/bin/llvm-config --version` → **`22.1.8`**；`--libdir`/`--includedir`/`--cmakedir` 指向路径均可达；`libLLVM-22.so`、`LLVMConfig.cmake`、`clang-22` 齐备（prefix 内原 `lld`/`ld.lld` 实为 23.1.4，已于 2026-11-03 隔离移除，见 D7；22 系 `lld` 未曾安装） | 前缀被重写为 `/var/opt/build/llvm22/...`（偏差 D3） |
| A4 | **PASS** | 第二轮以 `-DUSE_LLVM=/opt/build/llvm22/bin/llvm-config` 重编：`ninja -C /opt/build/npu_tvm tvm` rc=0（854 个目标，2026-11-03 10:24）；新 `libtvm.so` 79,226,112 B，`ldd` → `libLLVM.so.22.1 => /var/opt/build/llvm22/lib/libLLVM.so.22.1`；`import tvm` → `0.19.0`，`Target("llvm")` → `llvm -keys=cpu -mtriple=x86_64-conda-linux-gnu`，`Target("ccompiler")` → `ccompiler` | 旧产物备份为 `libtvm.so.bak-llvm21`（该备份已于同日清理，见 §9.4 第 4 条）；Python 层仍走最小安装（偏差 D2） |
| A5 | **PASS** | `pip install -e .` 成功；`import xmnn` → `1.0.1.dev120`，`xmnn.__file__=/opt/conda/envs/main/lib/python3.14/site-packages/xmnn/__init__.py` | `project(... LANGUAGES NONE)` 纯 Python，无需 C++ 编译 |
| A6 | **PASS** | `podman inspect` → `Privileged=false`、`CgroupMode=host`、`SecurityOpt=[label=disable]`、`UsernsMode=private`，而容器内 `id` → `uid=1006(ai) gid=1006(ai)` | 无 `--privileged`；未加 `--device /dev/fuse`（无嵌套 podman 需求） |
| A7 | **N/A（默认关闭）** | `podman port npu-toolchain` → 空输出 | 按 §1.1 目标 6 默认不发布端口；Q4 已选定 8888→8888（备用 8894）并完成占用双检，启用时须重建容器加 `-p 0.0.0.0:8888:8888`（容器端口不可后加），届时本项可转 PASS |
| A8 | **PASS** | 容器内 `id` → `uid=1006(ai) gid=1006(ai)`；容器内以该 uid 在 `/workspace/ai` 下创建探针文件成功且宿主可见；`/opt/build` 下 `llvm20`、`llvm21`、`llvm22`、`npu_tvm`、`npuusertools` 全部在位 | bind `/media/pc/data/ai:/workspace/ai` 与 volume `npu-build:/opt/build` 均正常 |
| A9 | **PASS** | `df -hT /media/pc/data` → `/dev/sda1 xfs 15T 15T **293G** 99% /media/pc/data` | 293 GB ≥ 50 GB 门禁 |

### 9.2 偏差与处置

| # | 偏差 | 现象 | 处置 |
|---|------|------|------|
| D1 | `podman --connection remote-ai` 无法解析主机 | `--log-level=debug` 显示 `ssh_config alias found: 10.16.11.3` 后报 `dial tcp :22`（主机名丢失）。属 podman 5.8.1 Windows 客户端在 `--connection`/`CONTAINER_HOST` 路径解析 `~/.ssh/config` 别名时的缺陷 | **已修复**：将 `~/.ssh/config` 中 `Host 10.16.11.3` 改为 `Match host 10.16.11.3`，podman 不再命中该块、主机得以保留，OpenSSH 行为不变；原配置备份为 `~/.ssh/config.bak-20261103-split`。根因与隔离实验见[架构与决策 §4.1](09-1-backend-and-decision.md) |
| D2 | npu_tvm Python 层未走 `pip install .` | `pip install .` 在 “Preparing metadata” 阶段长时间无进展（`setup.py` 需复制整个 3rdparty 后建 wheel） | 终止该进程；改用最小安装：site-packages 下 `.pth` 指向源码 `python/` 目录 + `/etc/profile.d/tvm.sh` 设置 `TVM_LIBRARY_PATH` 与 `TEST_DATA_ROOT_PATH`，FFI 走 ctypes 回退（无需 cython 扩展）。C++ 层已于第二轮按 LLVM 22 重编（见 A4）。**未修改 npu_tvm 源码** |
| D3 | LLVM 22 conda 前缀重写 | `llvm-config --libdir/--includedir/--cmakedir` 返回 `/var/opt/build/llvm22/...`，而包安装于 `/opt/build/llvm22` | 经核实 `/opt/build` 与 `/var/opt/build` 在容器内等价可达，路径无需修补；构建时以 `-DUSE_LLVM=/opt/build/llvm22/bin/llvm-config` 显式指定 |
| D4 | 容器内直连国内 conda 镜像失败 | USTC `HTTP 000`、tuna/bfsu `403`、aliyun `404`、nju 超时；根因为容器 IPv6 无路由而解析优先 AAAA | 以 `podman exec -u 0` 向 `/etc/gai.conf` 追加 `precedence ::ffff:0:0/96 100`；大文件仍 302 跳转失败，改由 **Windows 侧 `curl.exe`** 下载并发到共享目录，再以 `@EXPLICIT` 清单 + `--offline`（配合 `CONDA_PKGS_DIRS`、`HOME` 重定向）完成 `conda create` |
| D5 | `podman system df` 报 infra-container 缺失 | `lstat /run/user/1006/libpod/tmp/infra-container: no such file`；`podman ps -a` 可见 `1595a496d0b9` 为 `Created` 状态的 `9514ffe234c3-infra` | 未修复（属 podman 5.6.2 已知瑕疵，不影响构建）；容量核算以 `df`/`du` 替代 |
| D6 | D: 盘清理（原 v1.x 遗留） | 删除前可用 **8.82 GB**，三个待删文件均无进程占用（`UNLOCKED`） | 删除 `ok3.tar`、`fresh.tar`、`openKylin.wsl` 与两个 `WSL-import*.ps1`；删除后可用 **34.01 GB**（回收 25.19 GB）；保留 `libs\podman-machine-default.tar`（0.89 GB）与 `podman-machine-wsl`（1.81 GB） |
| D7 | `llvm22` 前缀混装 LLVM 23 构件（G3 缺口） | `conda list -p` 显示同 prefix 内 `libllvm23 23.1.4`、`lld 23.1.4`、`llvm-openmp 23.1.4`；`bin/ld.lld` 实为 LLD 23.1.4，`objdump -p` 的 `NEEDED` 引用 `libLLVM.so.23.1`；22 系包（`clang-22`/`libclang-cpp22.1`/`llvm-tools-22`/`llvmdev`）只依赖 `libllvm22`，无任何包依赖 `lld` 或 `llvm-openmp` | **已处置（隔离式移除，未用 `conda remove`）**：整批 `mv` 至 `/opt/build/.llvm23-quarantine-20261103/`（268 MB / 48 文件），同步迁出 3 个 `conda-meta` JSON，`conda-meta/*.json` 由 28 条降为 **25 条**；回归全绿——`llvm-config --version` 仍 `22.1.8`、`--libs` 正常，`ldd libtvm.so` 的 `libLLVM.so.22.1 => /var/opt/build/llvm22/lib/...` 不变，codegen 探针 + `Target("llvm")`/`Target("ccompiler")` + `import xmnn`、CMake `find_package(LLVM 22.1 CONFIG)` 探针、`verify.sh`（13 PASS / 1 N/A / 0 FAIL）全部通过；隔离目录（268 MB / 48 文件）已于 2026-11-03 删除，XFS 可用字节 315,729,219,584 → 316,010,168,320（+280,948,736 B，约 268 MiB） |

### 9.3 容器内配置与产物

| 项 | 值 |
|---|---|
| 容器运行参数 | `--userns=keep-id --cgroupns=host --security-opt label=disable`，`-v /media/pc/data/ai:/workspace/ai`，`-v npu-build:/opt/build`，`-w /workspace`，`--name npu-toolchain`，镜像 `localhost/openkylin-npu-toolchain:3.0`，命令 `sleep infinity`；**未发布端口** |
| LLVM 22 | `/opt/build/llvm22`（conda-forge `llvmdev`/`clang`，`llvmdev=22.1.8`；G3 处置后前缀内不再含 `lld`/`ld.lld`/`llvm-openmp`，见 D7） |
| Python 构建后端 | `cython 3.3.1`、`scikit-build-core 1.1.1`、`setuptools-scm 10.3.4`、`wheel 0.48.0`、`setuptools 84.2.1` |
| Python 运行时依赖 | `numpy 2.5.4`、`scipy 1.18.1`、`pandas 3.1.0`、`matplotlib 3.11.2`、`onnx 1.23.2`、`protobuf 7.36.2`、`pytest 9.2.0`、`openpyxl`、`tabulate`、`rich`、`tqdm`、`tomlkit`、`decorator 5.3.1`、`attrs 26.1.0`、`psutil`、`typing_extensions`、`cloudpickle`、`ml_dtypes` |
| tvm 安装方式 | `site-packages/tvm_src.pth` → 源码 `python/`；`/etc/profile.d/tvm.sh` 导出 `TVM_LIBRARY_PATH=/opt/build/npu_tvm`、`TEST_DATA_ROOT_PATH=/opt/build/tvm_test_data`（`bash -lc` 自动生效） |
| xmnn 安装方式 | `pip install -e .`（editable，约 41 MB），落点 `/opt/conda/envs/main/lib/python3.14/site-packages/xmnn` |
| 源码洁净性 | npu_tvm 仅 `python/tvm/3rdparty/` 一项未跟踪（2026-07-30 既存）；`3rdparty/cutlass/docs` 的删除为既存状态；npuusertools 4 项改动（`xmnn/tools/workflow.py`、两个 `xm_autotools*` 二进制、`old/`）为既存工作树。**本轮未改动两库源码** |

### 9.4 仍未解决的问题

1. **`podman system df` 的 infra-container 瑕疵**未修复（podman 5.6.2 已知问题，不影响构建）。
2. **Q3/Q4 已决**（详见[风险与待办 §8](09-6-risks-todos-changelog.md)）：Q3 保持不切默认连接，用 `--connection remote-ai` 显式调用；Q4 选定宿主 8888 → 容器 8888（备用 8894），双检通过（远程仅 8890/8892 在听，Windows 侧 8888/8889/8894 均空闲），但按目标 6 仍不发布端口。
3. **`libtvm.so` 运行期依赖 conda LLVM 22 运行库**：`ldd` 显示 `libLLVM.so.22.1`、`libstdc++`、`libxml2`、`libicuuc` 均解析到 `/var/opt/build/llvm22/lib`（rpath）。删除或替换 `/opt/build/llvm22` 会使 `import tvm` 失败。
4. **临时产物与旧库备份已清理**：删除 `.temp/npu-toolchain-run`（6,904 文件 / 3,001,480,000 B）、`.temp/npu-toolchain-spec-v2`（2 文件 / 97,370 B）、Windows 侧 `~/.ssh/config.bak-20261103-split`（596 B）、拆分中间脚本 `.temp/doc09-atomize/split-doc09.ps1`（19,711 B）与容器内 `libtvm.so.bak-llvm21`（79,231,568 B，删前 `sha256=9dfa9a66…61b2a`）；删后复验 `import tvm`（0.19.0 + 两个 Target）与 `xmnn 1.0.1.dev120` 均 rc=0。XFS 可用字节 316,398,936,064 → **316,478,189,568**（+79,253,504 B）。**保留并随后归档** `.temp/doc09-atomize/original-backup.md`（1171 行 / 106,206 B，拆分前 09 原文整档副本）——2026-11-03 已迁入 `.agents/archive/doc09-atomize-20261103/`（`cmp` + sha256 一致后删源，凭证见该目录 `README.md`）。
5. **G3（LLVM 23 混装）已处置，隔离目录已删除**：`/opt/build/.llvm23-quarantine-20261103/` 删除前含 `libLLVM-23.so`、`libLLVM.so.23.1`、`libLTO.so.23.1`、`libRemarks.so.23.1`、6 个 `liblld*.a`、`libomp*` 与 `libiomp5.so`、`bin/{lld,ld.lld,ld64.lld,lld-link,wasm-ld}`、`include/lld/` 与 `include/omp*.h`、`lib/cmake/{lld,openmp}`，合计 **268 MB / 48 文件**。该隔离副本已于 2026-11-03 删除（删前 `grep` 确认 `llvm22` 内无文件引用该路径），XFS 可用字节 315,729,219,584 → 316,010,168,320（+280,948,736 B，约 268 MiB）。删除后 `mv` 回滚路径失效，如需恢复须自 conda 通道重新安装。副作用：`clang-22 -fopenmp` 依赖的 `libomp.so` 已移出 prefix；22 系从未安装 `lld`，故构建与运行不依赖二者。

## 相关文档

- [入口索引](09-npu-toolchain-windows-host.md)
- [构建与验证](09-4-build-and-verify.md)
- [风险与待办](09-6-risks-todos-changelog.md)