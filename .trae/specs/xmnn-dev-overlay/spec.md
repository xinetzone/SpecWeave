# xmnn-dev 开发与打包叠加层（Podman rootless 谱系）- Product Requirements Document

> 方法论链路（seven-concepts 场景 5：创新突破 F→V→I→C）：
> F（第一性推导：工具链即产品 / 源码仅运行时挂载 / 打包内核随镜像自包含）
> → V（对抗审查，由 Spec Mode Review 阶段 fresh-context 独立审查承担）
> → I（洞察落地为文件级原子任务）→ C（按任务原子交付）。

## Overview
- **Summary**: 在 `apps/containers/client/overlays/xmnn-dev/` 新建一个正式（入库）工作负载叠加层：`FROM localhost/jupyter-podman-rootless:latest` 薄叠加，镜像内具备 **LLVM/Clang 22 + CMake/Ninja/ccache + Nuitka 4.1.3** 的 xmnn wheel 构建工具链；compose 栈在运行时把宿主源码 `external/chaos/npu_tvm` 与 `external/chaos/npuusertools`（及可选 models）bind mount 进容器，提供源码调试/开发环境（SSH + JupyterLab + xmnn-dev 内核 + PYTHONPATH 源码装配），并能在容器内一键执行 TVM C++ 编译与 **Nuitka 打包 `xmnn-*.whl`** 全流程，wheel 产物落到宿主可见目录。client 侧新增 opt-in `xmnn.*` invoke 命名空间（8 任务，podman-compose 子进程层，Windows 原生门禁）。
- **Purpose**: 既有 Docker 谱系 `external/chaos/ai/xmnn-whl-builder` 把"工具链 + 打包脚本 + 源码树 + BuildKit bind mount + 构建上下文耦合"绑死在 `external/chaos` 目录布局上（构建上下文必须是 chaos 根、COPY 带 `ai/` 前缀、运行需 privileged DinD），不可移动、不可在 rootless 谱系复现。本期按第一性原理把**可复现的工具链镜像**与**运行时挂载的源码**分离：镜像自包含全部打包知识（脚本/元数据/bootstrap），构建期零接触宿主源码；源码只在运行时按可配置路径挂载；调试与打包在同一栈内闭环，且不读取、不依赖 `external/chaos/ai`（仅以其为事实参考）。
- **Target Users**: 在 WSL2 `podman-machine-default`（rootless）上开发/调试 npu_tvm、xmnn（npuusertools）代码并需要产出 cp314 xmnn wheel 的单机开发者；与 onnx-quantized 叠加层、scratch xmnn-notebook 栈同一用户画像。

## Goals
- **G1（双态一体）**: 同一镜像 `localhost/xmnn-dev:latest` 同时支撑两种用法——①源码开发态：挂载源码后以 SSH/Jupyter（xmnn-dev 内核）调试 tvm/vta/xmnn 源码；②打包态：容器内执行脚本完成 `libtvm.so` 前置编译（可选）→ Nuitka 编译 tvm/vta/xmnn → scikit-build/CMake 组装 wheel，产物落宿主可见目录。
- **G2（对 ai 零依赖）**: 镜像的构建与运行路径中不存在任何对 `external/chaos/ai` 的引用：无 `ai/` COPY 前缀、无 chaos 根构建上下文、无 BuildKit `--mount=source=`、无 `CHAOS_ROOT`；打包所需 pyproject/CMakeLists/bootstrap/scripts 全部随 overlay 自包含并 COPY 进镜像。
- **G3（源码运行时挂载）**: npu_tvm、npuusertools、models 仅以 compose bind mount 在**运行时**出现于 `/workspace/npu_tvm`、`/workspace/npuusertools`、`/workspace/models`；宿主路径由插值变量提供（默认指向 `external/chaos/*`，可覆盖到 WSL 原生克隆）；镜像构建期不读取、不 COPY 任何源码。
- **G4（双 ABI 工具链事实固化）**: base env（`/opt/conda`，Python 3.14.7 **cp314 GIL enabled**，2026-09-14 机内实证）作为 Nuitka 编译解释器、wheel 安装/验证环境与 xmnn-dev 内核解释器；main env（cp314t free-threading）保持基底 Jupyter 服务定位不变，LLVM/Clang 22.1.8 工具链以 conda 装入 main env（pin `python=*=*cp314t` 防 ABI 互换，conda-llvm 变体内已实证的跨 env 布局）；构建期守卫固化双 ABI 与工具链版本断言。
- **G5（invoke 集成）**: client 新增 `xmnn.*` 命名空间（build/up/down/ps/logs/smoke/build-tvm/wheel 共 8 任务），遵循 C11 同族纪律（禁 `import podman`、Windows 原生门禁、三必需只走 compose 标准字段、禁 privileged、compose 层不回流根 run）。
- **G6（打包行为与已交付 wheel 等价）**: 移植的 build-wheel.sh 保持三次 Nuitka 的完整参数语义（dill-compat、jobs、交叉 nofollow、vta data-dir、tvm 串行→vta/xmnn 并行、AST PREAMBLE 注入/无条件还原）与 CMake  wheel 组装语义（3 个 .so + libtvm.so + LLVM 依赖库 `_libs/` + 数据目录 + .pth/bootstrap + patchelf `$ORIGIN`）；产物名 `xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl`，与 Docker 谱系产物 ABI/内容等价。

## Non-Goals
- **不做 wheel 消费型 notebook 镜像**：从预构建镜像 COPY wheel 直接运行的形态已由 scratch 栈 `.temp/notebook/xmnn-whl-builder`（spec `xmnn-overlay-rebuild`，Review PASS）覆盖；本期镜像是开发/打包端，默认不把 wheel pip install 进 base env（验证在临时 venv 内进行，避免污染源码调试链路）。
- **不在镜像构建期编译 TVM 或打包 wheel**（TVM 全量 10–30 分钟、Nuitka 5–15 分钟）：镜像构建保持"工具链装配 + 守卫"分钟级；编译动作只在容器运行时由任务/脚本显式触发。
- **不修改 `external/chaos/` 任何文件**（npu_tvm、npuusertools、ai、models 均为外部 git 仓库，只读/只挂载；AST 注入只在内存工作树临时发生且必须还原）。
- **不修改 onnx-quantized overlay 与 quant.\* 既有行为**（零回归对象）；不向根命名空间/`container.*`/`env.*` 回流。
- 不做硬件 GPU/NPU/CDI 透传与 VTA 硬件链路（本期工具链为 CPU/LLVM/VTA-sim 形态）；不提供 compose.gpu.yaml。
- 不做 linux x86_64/WSL2 以外平台；不做镜像远程推送/registry。
- 不自动 `git submodule update` npu_tvm 子模块（缺失时 build-tvm 文档与脚本输出可执行提示）。
- 不预装 torch/torchvision/onnx2pytork（wheel 的 optional `[torch]` extra；文档给出可选安装命令）。
- 不创建 git commit（除非用户明示）。

## Background & Context
- **模板范式（正式叠加层）**：`overlays/onnx-quantized/`（Containerfile.quantized 薄叠加、compose.yaml + opt-in gpu 覆盖、.env.example、smoke/、docs/、README）+ `.agents/rules/quant-overlay.md` + `src/jpman_client/tasks/quant.py`（6 任务：build/up/down/ps/logs/smoke，podman-compose 子进程，Windows 原生门禁，base 镜像存在性预检）。
- **rootless 基底事实（`apps/containers/jupyter-podman-rootless/`，2026-09-14 机内实证 + 构建文件静态证据）**：Ubuntu 26.04；Miniforge3 `/opt/conda`（mamba 可用，conda-forge + libmamba，构建期联网）；main env = Python 3.14.7 **cp314t**（PATH 顶端，Jupyter 服务经 `/opt/conda/envs/main/bin/jupyter` 由 supervisord 以 devuser 运行）；base env = Python 3.14.7 **cp314 GIL enabled**（`Py_GIL_DISABLED=0`、`sys._is_gil_enabled()=True`，spec xmnn-overlay-rebuild 实测）；final 镜像**无** gcc/clang/LLVM/cmake/ninja/ccache/patchelf/gdb；devuser UID/GID 1000、NOPASSWD sudo；entrypoint=tini→entrypoint.sh→supervisord（不可覆盖）；WORKDIR `/workspace`（777）；内核注册无现成约定，已验证路径为 main env 的 `share/jupyter/kernels/<name>/`（root 与 devuser 双可见）。
- **Docker 谱系打包链（仅事实参考）**：`external/chaos/ai/xmnn-whl-builder/`（3 阶段 Dockerfile：conda 升 base 为 cp314、BuildKit rw bind mount 两源码树、`scripts/build-wheel.sh`、pyproject.toml 19 依赖、CMakeLists.txt 收集 3 so + libtvm.so + 7 个 LLVM 依赖库 + 数据目录、`_xmnn_bootstrap.py`/`.pth`、verify-wheel.sh 10 项）；其 conda 工具链真源为 `apps/docker-images/devcontainer-base/variants/conda-llvm`（`llvmdev/clangdev/clang/lld=22.1.8` + cmake/ninja/make/ccache + libgcc/libstdcxx-ng，pin `python=*=*cp314t`）。rootless 基底无需"升 base Python"步骤（已是 3.14.7 cp314）。
- **源码侧事实**：npu_tvm 是 TVM 0.19.0 fork（CMake≥3.18、C++17、`inv config -f` 读 `LLVM_CONFIG` 环境变量生成 config.cmake、`inv make` 用 Ninja+ccache；`USE_EXAMPLE_TARGET_HOOKS=ON` 为打包前置补丁；当前宿主工作树 `build/libtvm.so` **已存在**可直接被打包消费，config.cmake 内 LLVM 路径为旧布局，build-tvm 会强制重配）；11 个 git 子模块中本地仅 cnpy/dlpack/rang 有内容（全量编译 TVM 前需 `git submodule update --init`）。npuusertools 提供 `xmnn` 包（无打包配置，源码消费方，import tvm/vta，含 tools_cpp/autolibs/fonts 数据目录与预编译二进制）；容器约定路径 `/workspace/npu_tvm`、`/workspace/npuusertools`（.coverage 内路径实证）。
- **已验证产物 ABI**：`xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl`（187,896,958 字节，2026-09-08，机内 `localhost/xmnn-whl-builder:latest` 的 `/opt/xmnn-dist/`）；requires-python>=3.14.6；Nuitka 4.1.3 在 cp314t 编译失败、cp314 GIL 成功（allocator.h:606 Spike 结论）。
- **同机网络实证（2026-09-14）**：未改动的 onnx 栈在该机以默认项目网络 `up` 同样触发 aardvark-dns「Failed to connect to user scope bus」（machine 无 systemd user bus），`network_mode: bridge` 可绕过；与镜像谱系无关。故新栈 compose 显式 `network_mode: bridge` 并附实证注释（对齐 scratch 栈 S1）。
- **产物增强点（相对移植源的有意改写，须在 V 审查中被覆盖）**：①SONAME 漂移防护——CMake 对 LLVM 依赖库改 glob 模式收集，构建期守卫对 7 个库在 `llvm-config --libdir` 的存在性做硬检查并打印实际 SONAME（移植源缺失仅 WARNING，会静默打出缺库 wheel）；②AST 注入补 `trap` 还原（异常 kill 不留 `.bak_*`）；③verify-wheel.sh 改在 `--system-site-packages` 临时 venv 内验证，base env 零污染；④所有路径环境变量化（TVM_ROOT/XMN_ROOT/NUITKA_OUT/DIST_DIR/CCACHE_DIR）。

## Functional Requirements
- **FR-1（叠加镜像 Containerfile.xmnn-dev）**: overlay 根目录新增 `Containerfile.xmnn-dev`，`ARG BASE_IMAGE=localhost/jupyter-podman-rootless:latest` 薄叠加：
  - `ARG PIP_MIRROR=official`、`ARG CONDA_MIRROR=official`（official/aliyun/tuna 三段幂等重设，pip 走 main env pip 的同构写法改为 base/main 各自需要的 env；CONDA_MIRROR 仅在非 official 时按基底 conda 镜像约定幂等写 `/opt/conda/.condarc` custom_channels）；
  - Layer 1（main env 工具链，pin ABI）：`mamba install -n main -c conda-forge --override-channels "python=*=*cp314t" llvmdev=22.1.8 clangdev=22.1.8 clang=22.1.8 lld=22.1.8 cmake ninja make ccache libgcc libstdcxx-ng`，随后 `conda clean -afy`；apt 层安装 `patchelf gdb`（`--no-install-recommends`，同层清 apt lists；apt 不可用不做 conda 回退之外的偏方——若 apt 失败以实际日志裁决）；
  - Layer 2（base env 打包栈，显式 `/opt/conda/bin/python -m pip`）：`nuitka==4.1.3 scikit-build-core>=0.10 build wheel invoke ipykernel` 及 pyproject 的 19 个核心运行时依赖（不含 torch extra），`--no-cache-dir`；
  - Layer 3：COPY `builder/` → `/opt/xmnn-builder/`、`smoke/` → `/opt/xmnn-dev-smoke/`、内核注册脚本；`chmod -R a+rX`；
  - Layer 4：注册 xmnn-dev 内核；构建期以 `/opt/conda/bin/python` 运行 `_toolchain_guards.py`（root），并以 devuser 身份复跑一次；完成横幅；
  - 全部 RUN 显式 `/bin/bash -lc`；不写 SHELL/HEALTHCHECK；不覆盖 ENTRYPOINT/CMD/WORKDIR；LABEL 仅 `org.specweave.*`（component=xmnn-dev、layer=xmnn-dev-toolchain、python-abis="base:cp314-gil,main:cp314t"、llvm=22.1.8、nuitka=4.1.3、base-image）。
- **FR-2（builder 打包内核自包含）**: `builder/` 目录移植并参数化以下资产，镜像内位于 `/opt/xmnn-builder/`：
  - `pyproject.toml`：name=xmnn、version=1.2.1-dev0、requires-python=>=3.14.6、scikit-build-core>=0.5 后端、19 依赖与 dev/examples/torch/full extras、wheel.install-dir="."、cmake>=3.18/ninja>=1.10/Release（与移植源一致）；
  - `CMakeLists.txt`：6 个 CACHE PATH 默认改为容器运行时布局（TVM_ROOT=/workspace/npu_tvm、TVM_BUILD=/workspace/npu_tvm/build、XMN_PYTHON_DIR=/workspace/npuusertools、NUITKA_OUT/XMN_NUITKA_OUT 默认 `/opt/xmnn-builder/build/nuitka...`、LLVM_LIB_DIR 默认取 `llvm-config --libdir` 实测值——脚本以 `-D` 注入）；FATAL 守卫（3 个 Nuitka .so、libtvm.so）、autolibs `cp -a`+占位、数据目录（autolibs/tools_cpp/fonts、vta_hw/config、relay/std .rly）、tools_cpp chmod、patchelf `$ORIGIN` 全部保留；LLVM 依赖库由硬编码 7 文件名改为**模式 glob + 逻辑名软链兜底**（libLLVM.so.22*、libz.so.*、libzstd.so.*、libxml2.so.*、libiconv.so.*、libicuuc.so.*、libicudata.so.*），glob 为空 FATAL_ERROR 并打印 libdir 实际候选；
  - `_xmnn_bootstrap.py`、`xmnn_bootstrap.pth`：语义照搬（_libs 解析、RTLD_GLOBAL 多轮预加载、6 个被删 AST 类补偿）；
  - `scripts/lib/logging.sh`：vendor 一份（移植源从 ai/scripts/lib 跨目录 COPY，本期不允许该耦合）。
- **FR-3（build-wheel.sh 移植与参数化）**: `builder/scripts/build-wheel.sh` 保持移植源流程（环境自检→pip 源→numpy/scipy 兜底→ccache 配置→tvm 串行 Nuitka→vta/xmnn 并行 Nuitka→`python -m build --wheel --no-isolation` + 6 个 cmake.define→产物校验），并满足：
  - 全部路径环境变量化：`TVM_ROOT`（默认 /workspace/npu_tvm）、`XMN_ROOT`（默认 /workspace/npuusertools）、`BUILDER_DIR=/opt/xmnn-builder`、`NUITKA_OUT`（默认 /opt/xmnn-builder/build/nuitka）、`DIST_DIR`（默认 /workspace/dist）、`CCACHE_DIR`（默认 /root/.ccache）、`LLVM_CONFIG`（默认 /opt/conda/envs/main/bin/llvm-config）、`NUITKA_JOBS`（默认 8）、`NOFOLLOW_IMPORTS`、`TVM_COMPILE_FLAGS`、`CLEAN_REBUILD`、`PIP_MIRROR`；
  - 跨 env 导出只在脚本进程内生效：PATH 以 `/opt/conda/bin` 为首、main/bin 补充；`CC/CXX` 绝对指向 main/bin/clang(++)；`LD_LIBRARY_PATH=<main/lib>:<base/lib>`；
  - AST PREAMBLE 注入/还原加 `trap` 兜底；三次 Nuitka 参数差异（交叉 nofollow、dill-compat、vta include-data-dir、jobs、--module）与退出码回传文件机制保持；
  - 启动前检查 `$TVM_ROOT/build/libtvm.so`，缺失则打印"先运行 build-tvm.sh / inv xmnn.build-tvm"并退出 2；wheel 产出后打印文件名/大小/落盘目录。
- **FR-4（build-tvm.sh 新增）**: `builder/scripts/build-tvm.sh`：导出 `LLVM_CONFIG` 与 PATH（base python + main 工具链）；`cd $TVM_ROOT`；检查 tasks.py 与 `3rdparty/dmlc-core`（缺失提示 `git submodule update --init` 并退出 2）；`/opt/conda/bin/python -m invoke config -f`；正则置 `USE_EXAMPLE_TARGET_HOOKS ON`（沿用移植源 regex 语义）；`invoke make`（ccache launcher、`-DUSE_LIBBACKTRACE=OFF` 由 npu_tvm tasks.py 既有逻辑负责）；结束断言 `build/libtvm.so` 存在并打印大小；幂等（已有有效 build/ 时增量编译）。
- **FR-5（verify-wheel.sh 隔离验证）**: `builder/scripts/verify-wheel.sh` 保留 10 项检查（import tvm/vta/xmnn、_libs 清单含 libtvm.so 与 libLLVM、RPATH $ORIGIN、干净环境 ctypes 加载 libtvm、tvm.build('llvm') 向量加、relay/prelude.rly、.pth 生效、xmnn 三数据目录）；安装目标改为**临时 venv**（`/opt/conda/bin/python -m venv --system-site-packages /tmp/xmnn-verify-venv`，`pip install --no-deps --force-reinstall <whl>`，用 venv python 执行全部检查），结束清理 venv；base env 不被安装/卸载污染；whl 路径参数化（默认 `$DIST_DIR` 最新 xmnn-*.whl）。
- **FR-6（compose 栈）**: `compose.yaml`：`name: xmnn-dev`；服务 `xmnn`；image `${XMNN_IMAGE_TAG:-localhost/xmnn-dev:latest}` 与内联 build（context `.`、dockerfile `Containerfile.xmnn-dev`、args BASE_IMAGE/PIP_MIRROR/CONDA_MIRROR）共存；`network_mode: bridge`（附 2026-09-14 aardvark-dns 实证注释）；端口 `${XMNN_SSH_PORT:-2223}:22`、`${XMNN_JUPYTER_PORT:-8890}:8888`；volumes 全部长语法 + `bind.create_host_path: true`：
  - `${XMNN_WORKSPACE:-../../workspace}` → `/workspace`；
  - `${NPU_TVM_PATH:-../../../../../external/chaos/npu_tvm}` → `/workspace/npu_tvm`；
  - `${NPUUSERTOOLS_PATH:-../../../../../external/chaos/npuusertools}` → `/workspace/npuusertools`；
  - `${MODELS_PATH:-../../../../../external/chaos/models}` → `/workspace/models`；
  - named volume `xmnn-ccache` → `/root/.ccache`（顶层 volumes 声明；down 默认保留，--volumes 删除）；
  - 三必需：devices `/dev/fuse`、security_opt `label=disable`、`cgroupns: host`（注释声明 podman-compose 1.6.0 对 cgroupns 空操作）；无 privileged；
  - environment：四凭证（USER_PASSWORD/JUPYTER_TOKEN/SSH_PUBLIC_KEY/GRANT_SUDO）、`PYTHONPATH=/workspace/npu_tvm/python:/workspace/npu_tvm/vta/python:/workspace/npuusertools`、`TVM_LIBRARY_PATH=/workspace/npu_tvm/build`、`LD_LIBRARY_PATH=/workspace/npu_tvm/build:/workspace/npu_tvm/build/vta:/opt/conda/envs/main/lib`、`NPU_TOOLS_ROOT=/workspace`、`XMNN_TOOLS_ROOT=/workspace/npuusertools`、`OMP_NUM_THREADS=${...:-4}`、`NUITKA_JOBS=${...:-8}`；labels `org.specweave.component=xmnn-dev`/`managed-by=jupyter-podman-client`；`restart: unless-stopped`；无 command/healthcheck 段。
  - **实现细化（2026-09-14 Implement 期修正，留痕待 V 审查）**：原设计拟不把 LD_LIBRARY_PATH 放入 compose 全局；实现确认非登录 `podman-compose exec` 不 source `/etc/profile.d`，而 libtvm.so 的 NEEDED（libLLVM 22.1 等）解析需要 main/lib——故 LD_LIBRARY_PATH 必须随 compose environment 注入（kernel env 同步携带，双路径一致）。main/lib 即 Jupyter 服务自身 conda env 的库目录，无新增冲突面；tvm build 目录仅含 libtvm/libvta 等专用库。
- **FR-7（overlay .env.example）**: 键集合与 compose 插值键严格一致：XMNN_IMAGE_TAG、XMNN_CONTAINER_NAME、XMNN_SSH_PORT(2223)、XMNN_JUPYTER_PORT(8890)、XMNN_WORKSPACE、NPU_TVM_PATH、NPUUSERTOOLS_PATH、MODELS_PATH、USER_PASSWORD、JUPYTER_TOKEN、SSH_PUBLIC_KEY、GRANT_SUDO、OMP_NUM_THREADS、NUITKA_JOBS、PIP_MIRROR、CONDA_MIRROR；头部注释优先级链（shell > root client .env > compose 默认；本文件仅供裸 podman-compose）与 Windows 门禁/WSL 路径说明。
- **FR-8（构建期/运行期 smoke 双脚本）**:
  - `smoke/_toolchain_guards.py`（构建期 + `podman run --rm` 双路径，不依赖挂载）：双 ABI 断言（base: Py_GIL_DISABLED=0 且 GIL enabled；main: cp314t 且 GIL disabled）；main/bin 工具链版本（llvm-config 22.1.x、clang、cmake≥3.18、ninja、ccache、patchelf、gdb）；base 模块（nuitka 4.1.3、skbuild、build、invoke）；/opt/xmnn-builder 资产齐；对 llvm-config --libdir 执行 7 库 glob 存在性硬检查并打印实际 SONAME；devuser 可执行；
  - `smoke/smoke_mounts.py`（栈运行路径）：断言三源码挂载点与关键子目录（npu_tvm/python/tvm、npuusertools/xmnn、models）可访问；libtvm.so 存在时 import tvm/vta/xmnn（打印 tvm.__file__ 证明来自 /workspace 挂载源码）并跑 tvm.build('llvm') 固定向量加断言；libtvm.so 不存在时跳过 import 段、输出 build-tvm 提示并不判失败（首次未编译是合法态）。
- **FR-9（xmnn-dev 内核）**: `scripts/register-kernel.sh`（构建期一次）：写 `/opt/conda/envs/main/share/jupyter/kernels/xmnn-dev/kernel.json`，argv[0]=`/opt/conda/bin/python`，display_name=`Python 3.14 (xmnn dev)`，env.PATH 以 /opt/conda/bin 为首，env 另携带 PYTHONPATH（三源码段）、TVM_LIBRARY_PATH、LD_LIBRARY_PATH（build 两目录 + /opt/conda/envs/main/lib）；root 与 devuser 双 `kernelspec list` 可见性断言。
- **FR-10（invoke xmnn.* 命名空间）**: 新增 `src/jpman_client/tasks/xmnn.py`（**禁 import podman**）并在 `tasks/__init__.py` 注册 `xmnn` Collection：
  - build（参数 --tag/--base-image/--pip-mirror/--conda-mirror/--no-cache；含 base 镜像存在性预检）、up（--skip-build）、down（--volumes）、ps、logs、smoke（栈运行→compose exec 两脚本；未运行→`podman run --rm` 仅跑 _toolchain_guards.py）；
  - `build-tvm`（`podman-compose exec -T xmnn bash /opt/xmnn-builder/scripts/build-tvm.sh`，pty）、`wheel`（exec build-wheel.sh，可选 `--jobs/--clean/--tvm-flags` 透传为对应环境变量；长任务 pty）；
  - 门禁/配置完全对齐 quant.py：`_gate_platform`（Windows 原生 Exit 1 + 双路径中文指引）、`_gate_compose_binary`、daemon 预检、`load_dotenv(override=False)`；`XMNN_WORKSPACE` 与三个源码路径解析为**绝对 POSIX 路径**注入子进程；源码路径不存在时 Exit 1 输出可执行中文指引（区分 TVM 缺失/工具缺失/子模块提示）；固定 project name= xmnn-dev，-f 绝对路径；
  - `__init__.py` 的 `ns.configure` 增加 xmnn 段（image_tag/base_image/container_name/ssh_port=2223/jupyter_port=8890）；模块 docstring 同步更新命名空间总数；
  - pyproject.toml 复用既有 `[compose]` extra，不新增依赖。
- **FR-11（client .env.example 追加）**: 根 `.env.example` 增加 `xmnn.*` 段（全键注释态，与 overlay .env.example 键集合一致，双向同步为强制检查）。
- **FR-12（AI 规则与路由登记）**: 新增 `.agents/rules/xmnn-overlay.md`（单一职责：架构三层边界、双门禁、双 ABI 工具链契约、源码仅运行时挂载、AST 注入/还原纪律、SONAME 守卫、ccache 卷语义、compose 三必需与 bridge 实证、标签接缝、冒烟双路径）；更新 `AGENTS.md`（项目概述命名空间四→五、嵌套路由树、上下文路由表新增 xmnn.* 与 overlay 两行、P0 速览新增 C12、变更日志 2026-09-14 条目）；更新 `.agents/README.md` 索引（若其列 rules 清单）；更新 `apps/AGENTS.md` client 行说明（含 xmnn-dev 叠加层）。
- **FR-13（overlay README）**: onnx 风格 README：定位、镜像/双 ABI/服务/端口表、前置条件（rootless 基底、源码路径、machine/WSL）、invoke 与裸 compose 两路径、开发调试会话（SSH/Jupyter/kernel/PYTHONPATH）、build-tvm→wheel→verify 操作手册（含资源建议 NUITKA_JOBS、9p 性能提示与 WSL 原生克隆替代路径）、.env 参数表、双冒烟说明、产物说明、与 onnx 叠加层/scratch notebook 栈/chaos ai 的关系表（"参考但不依赖"声明）、子模块与排障。

## Non-Functional Requirements
- **NFR-1（范式保真）**: 每条非平凡写法可指认 quant-overlay.md 条款或 OKF podman-compose 知识包（concepts/02/03/06/08/10）；仅 `network_mode: bridge` 与端口默认值两处偏差，均须带实证/用途注释。
- **NFR-2（对 ai 零依赖、对源码零修改）**: 功能性文件（Containerfile*、compose*.yaml、builder/**、scripts/**、smoke/**、xmnn.py）中不得出现 `external/chaos/ai`、`chaos/ai`、`--mount=type=bind`、`CHAOS_ROOT`、`xmnn-whl-builder`（镜像标签/目录名）；wheel 全流程后 npu_tvm/npuusertools 工作树 `git status` 干净且无 `*.bak_*` 残留。
- **NFR-3（rootless 安全）**: 无 privileged、无 docker.sock、无 host 网络；宿主端口 ≥1024（2223/8890）；三必需与 C11/C3 同源。
- **NFR-4（可清理/幂等）**: down 后项目容器/网络为零，源码与 workspace 绑定保留，ccache 命名卷默认保留（--volumes 删除）；重复 build/up/down 幂等。
- **NFR-5（真实可执行）**: 镜像构建、栈起停、wheel 打包均须在 podman-machine-default 内真实执行取证；编译类步骤失败按 blocked/重试处理，禁止以静态检查冒充运行证据；自动重试上限 4 次（环境/网络类），方法类失败直接回到 Implement 修正。
- **NFR-6（最小侵入）**: 主仓库改动仅限：overlay 新目录、client `src/jpman_client/tasks/{xmnn.py,__init__.py}`、client `.env.example`、client `.agents/rules/xmnn-overlay.md`、client `AGENTS.md`（必要处）、client README（必要小节）、apps/AGENTS.md 一行、`.trae/specs/xmnn-dev-overlay/`；onnx overlay、quant.py、external/ 零改动。

## Constraints
- **Technical**:
  - 仅在 WSL2 `podman-machine-default`（rootless、podman 5.7.1、podman-compose 1.6.0）内真实运行；Windows 原生 CPython 一律门禁；
  - 本地必须存在 `localhost/jupyter-podman-rootless:latest`（不得触发远程 pull）；
  - conda-forge 需可解出 llvmdev/clangdev/clang/lld 22.1.8（构建期联网；以实际求解为准，pin 不松）；
  - wheel ABI 固定 cp314 GIL：编译/验证解释器只能是 `/opt/conda/bin/python`；main env cp314t 不被 conda 求解互换（pin + 构建期双 ABI 守卫）；
  - 构建上下文 = overlay 目录自身（9p 小目录，仅脚本/元数据）；
  - OCI 纪律：RUN 显式 `/bin/bash -lc`、含引号逻辑固化脚本、无 SHELL/HEALTHCHECK、不覆盖入口链；
  - 资源：Nuitka jobs=8 建议 ≥8 GB RAM / ≥10 GB 磁盘，可经 NUITKA_JOBS 下调；TVM 全量编译显著更重，可用宿主既有 `build/libtvm.so` 跳过。
- **Business**: `external/chaos/*` 为外部仓库只读参考与运行时挂载对象；overlay 纳入主仓库版本控制；本期不做 git commit。
- **Dependencies**: 构建期需要 conda-forge 与 PyPI（经镜像源）网络；运行期打包消费挂载源码与其中既有 `build/libtvm.so`（或先 build-tvm）。

## Assumptions
- 机内 rootless 基底 base/main 双 env 版本与 2026-09-14 实证一致（3.14.7；构建期守卫会重新取证，不一致即失败不臆造）。
- conda-forge 当前仍提供 22.1.8 工具链且在 pin `python=*=*cp314t` 下不发生 main env ABI 互换；LLVM 依赖库 SONAME 可能漂移，由 glob + 守卫吸收。
- 宿主 `external/chaos/npu_tvm/build/libtvm.so` 与 main env 提供的 libLLVM 22.1 运行时 ABI 兼容（同为 22.1.8 谱系；AC-7 以 wheel 验证中 ctypes/tvm.build 实测裁决）。
- 2223/8890 端口空闲（与 onnx 2222/8888、scratch 栈可并行）。
- 空密码/token 沿用基底 entrypoint 自动生成契约。
- pip 镜像源可提供 cp314 GIL 全部 19 依赖 wheel（scratch 栈 2026-09-14 aliyun 实证同组依赖解析成功）。

## Acceptance Criteria

### AC-1: 对 ai 目录零依赖（静态门禁）
- **Type**: `rule`
- **Given**: overlay 目录与 client 新增/修改文件
- **When**: 对功能性文件（Containerfile*、compose*.yaml、.env.example、builder/**、scripts/**、smoke/**、src/jpman_client/tasks/xmnn.py）grep `external/chaos/ai|chaos/ai|--mount=type=bind|CHAOS_ROOT|xmnn-whl-builder|/builder/`
- **Then**: 0 命中（`.bak`/构建输出目录名 `build/nuitka` 中的 "/build/" 不算 `/builder/`；README 中"只读参考、不依赖"的事实性表述除外）；builder 资产文件集齐全（pyproject.toml、CMakeLists.txt、_xmnn_bootstrap.py、xmnn_bootstrap.pth、scripts/{build-wheel.sh,build-tvm.sh,verify-wheel.sh,lib/logging.sh}）
- **Pass Condition**: grep 0 命中且文件集齐全
- **Evidence**: grep 输出 + 目录树

### AC-2: compose 配置静态正确性
- **Type**: `rule`
- **Given**: machine 内 overlay 目录
- **When**: `podman-compose config` 退出码与输出
- **Then**: 退出码 0；恰好 1 服务 xmnn；image+build 共存（dockerfile=Containerfile.xmnn-dev）；network_mode=bridge；端口 2223/8890；bind 恰好 4 个（target /workspace、/workspace/npu_tvm、/workspace/npuusertools、/workspace/models）+ 1 named volume（/root/.ccache）；三必需字段各 1；environment 含四凭证与 PYTHONPATH/TVM_LIBRARY_PATH/NPU_TOOLS_ROOT/XMNN_TOOLS_ROOT；无 privileged、无 healthcheck、无 command
- **Pass Condition**: 逐项 grep/计数成立
- **Evidence**: config 输出摘要入 tasks.md

### AC-3: 叠加镜像真实构建与构建期守卫
- **Type**: `rule`
- **Given**: 本地 rootless 基底存在
- **When**: `invoke xmnn.build`（或裸 `podman build -f Containerfile.xmnn-dev`）
- **Then**: 退出码 0；构建日志含：main 工具链安装（llvmdev/clang 22.1.8）、base nuitka==4.1.3、root 身份 _toolchain_guards.py 全 PASS（含 7 库实际 SONAME 行）、devuser 复跑 PASS、完成横幅；`localhost/xmnn-dev:latest` 在 podman images；inspect Entrypoint=tini→entrypoint.sh、无 Healthcheck
- **Pass Condition**: 各项全成立
- **Evidence**: 构建日志关键行、images、inspect

### AC-4: 双 ABI 与工具链事实
- **Type**: `rule`
- **When**: 容器内分别执行 `/opt/conda/bin/python -c "sysconfig/sys._is_gil_enabled"` 与 `/opt/conda/envs/main/bin/python 同检`，并运行 llvm-config/clang/cmake/ninja/ccache/patchelf/gdb --version 与 `/opt/conda/bin/python -m nuitka --version`
- **Then**: base=cp314 GIL enabled（Py_GIL_DISABLED=0）；main=cp314t GIL disabled；llvm-config 主版本 22.1；nuitka=4.1.3；其余工具均可执行；main env python 仍为 *_cp314t（未被 conda 互换）
- **Pass Condition**: 断言逐项成立
- **Evidence**: exec 输出（守卫脚本日志已含则引用）

### AC-5: 栈 E2E 与内核/挂载可见
- **Type**: `rule`
- **When**: `invoke xmnn.up` 后等待服务；探测 2223/tcp、curl `http://127.0.0.1:8890/lab`；exec 检查 `/workspace/npu_tvm/python/tvm`、`/workspace/npuusertools/xmnn`、`/workspace/models`；以 main jupyter kernelspec list 查 xmnn-dev 并读 kernel.json
- **Then**: 2223 SSH banner 可达；/lab 返回 200/302；三挂载点存在且含预期文件；kernelspec 含 xmnn-dev，argv[0]=/opt/conda/bin/python，root 与 devuser 均可见，env 含源码 PYTHONPATH
- **Pass Condition**: 各项全成立
- **Evidence**: 端口/curl 输出、ls、kernel.json、kernelspec list

### AC-6: 源码调试链路（改动宿主源码→容器内即时生效）
- **Type**: `rule`
- **Given**: 栈运行且挂载源码（宿主 build/libtvm.so 存在）
- **When**: 容器内以 base python 执行 `import tvm, vta, xmnn; print(tvm.__file__)` 并跑 tvm.build('llvm') 固定向量加；再经 `inv xmnn.smoke` 跑 smoke_mounts.py
- **Then**: tvm.__file__ 位于 `/workspace/npu_tvm/python/tvm/__init__.py`（证明来自挂载源码而非 site-packages）；vta/xmnn 同样来自 /workspace；tvm.build 向量加断言通过；smoke_mounts.py 退出 0；在宿主侧对某源码文件做无害注释改动后容器内立即可见（可选附加取证）
- **Pass Condition**: 路径前缀断言 + 算例通过 + smoke 退出 0
- **Evidence**: exec 输出与 smoke 输出

### AC-7: Nuitka 打包真实闭环
- **Type**: `rule`
- **Given**: 栈运行，镜像工具链就绪，挂载源码 build/libtvm.so 就位
- **When**: 执行 `invoke xmnn.wheel`（容器内 build-wheel.sh 全流程）
- **Then**: 退出码 0；宿主可见目录（client/workspace/dist/ 或 XMNN_WORKSPACE/dist）出现 `xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl`（记录大小，量级 ≥100 MB）；容器内解包清单含 tvm/vta/xmnn 三个 .so、`_libs/libtvm.so` 与 libLLVM、xmnn/{autolibs,tools_cpp,fonts}、vta_hw/config、tvm/relay/std、_xmnn_bootstrap.py、xmnn_bootstrap.pth
- **Pass Condition**: whl 文件名/位置/内容清单全部成立
- **Evidence**: ls -l、unzip -l 清单、构建日志关键阶段行

### AC-8: wheel 隔离验证
- **Type**: `rule`
- **When**: 容器内执行 verify-wheel.sh（临时 venv，10 项）
- **Then**: 10 项全 PASS（含 unset LD_LIBRARY_PATH 的 libtvm ctypes 加载与 tvm.build 数值断言、RPATH $ORIGIN）；验证结束 `/tmp/xmnn-verify-venv` 已清理；base env `pip list` 中不出现 xmnn/tvm/vta 的 wheel 安装（源码 PYTHONPATH 链路不受污染）
- **Pass Condition**: 10 PASS + venv 清理 + base 未污染三项
- **Evidence**: verify 输出、venv 路径 ls、base pip list 摘要

### AC-9: 外部源码零修改与 AST 还原
- **Type**: `rule`
- **When**: AC-7 全程结束后对 `external/chaos/npu_tvm`、`external/chaos/npuusertools` 执行 `git status --porcelain` 并 find `*.bak_tvm|*.bak_vta|*.bak_xmnn`
- **Then**: 两仓库工作树无新增/修改（构建前既有未跟踪/已修改项先做基线快照，按快照差异裁决）；0 个 .bak 残留；脚本 trap 还原逻辑经代码审查确认（正常路径 + ERR/EXIT trap）
- **Pass Condition**: 前后快照一致 + 0 残留 + trap 审查通过
- **Evidence**: 前后 git status 快照、find 输出、脚本片段引用

### AC-10: 清理幂等与 ccache 卷语义
- **Type**: `rule`
- **When**: `invoke xmnn.down` 后列举项目标签容器/网络与 xmnn-ccache 卷；再执行一轮 up→ps→down
- **Then**: 容器/项目网络为零；xmnn-ccache 卷保留；源码/workspace 绑定文件保留；第二轮成功；`down --volumes` 后卷被删除（可在最后一轮验证）
- **Pass Condition**: 计数断言逐项成立
- **Evidence**: podman ps/network/volume 输出两轮记录

### AC-11: invoke 集成与键集合
- **Type**: `rule`
- **When**: 安装后 `invoke --list`；Windows 原生侧（静态审查 xmnn.py 门禁逻辑 + 如可行在 Windows python 实跑一次 `invoke xmnn.ps`）；diff overlay .env.example 键集合与 compose 插值键、root client .env.example 的 xmnn 段
- **Then**: --list 出现 xmnn.build/up/down/ps/logs/smoke/build-tvm/wheel 8 任务；Windows 原生门禁 Exit 1 且输出双路径中文指引；xmnn.py 无 `import podman`；两处 .env 键集合与 compose 插值键 diff 为空（注释态构建参数除外）
- **Pass Condition**: 四项成立
- **Evidence**: --list 输出、门禁运行/静态证据、键集合 diff

### AC-12: 零侵入与零回归
- **Type**: `rule`
- **When**: 主仓库 git status；onnx overlay 与 quant.py 工作树；`invoke quant.ps` 门禁行为（无栈时给出运行态提示而非导入错误）；import jpman_client.tasks 全包可加载
- **Then**: 改动文件全部落在 NFR-6 白名单；onnx overlay 零修改；quant 模块行为零回归；tasks 包 python -c import 成功
- **Pass Condition**: 白名单核对 + 零修改 + 导入成功
- **Evidence**: git status、文件清单、导入输出

### AC-13: 范式保真度
- **Type**: `rubric`
- **Dimension**: overlay 结构、Containerfile/compose 纪律、invoke 任务写法与 onnx-quantized/quant-overlay.md/OKF 知识包的对齐度
- **Scale**: 1-5
- **Anchors**: 1 = 引入 wrapper/特权/自定义 x-podman/短语法 bind 或回流根 run；3 = 可运行但 ≥2 处偏离无注释依据；5 = 除 bridge/端口两处（带实证注释）外与 onnx 范式一一对应，且双 ABI/跨 env 设计有 chaos 实证出处
- **Pass Threshold**: >= 4
- **Evidence**: reviewer 逐文件对照表

### AC-14: 产物原子性与文档一致性
- **Type**: `rubric`
- **Dimension**: 文件职责单一性、README/规则/AGENTS 与实现逐条一致性、相对链接可达、参数表与 compose/.env/任务参数三者一致
- **Scale**: 1-5
- **Anchors**: 1 = 文档与实现矛盾/坏链/键不一致；3 = 存在 1-2 处过时或冗余；5 = 三处参数一一对应、链接全通、每个文件单一职责
- **Pass Threshold**: >= 4
- **Evidence**: 链接检查 + reviewer 交叉核对

## Open Questions（实施后裁决）
- [x] Q1（端口默认值 2223/8890）：按默认落地，两轮 up 实测端口可用。
- [x] Q2（TVM build 目录）：按默认落在挂载源码树 `npu_tvm/build`；直接复用宿主 8 月 11 日构建的 libtvm.so 完成打包与 10 项验证（未跑全量 build-tvm，脚本已具备且 dmlc-core 守卫在位）；9p 性能替代已写入 README。
- [x] Q3（models 默认挂载）：保留四 bind 默认（external/chaos/models 存在，实测挂载可见）。
- [x] Q4（wheel 全流程 E2E）：已真实执行——镜像构建两轮、Nuitka 全流程一次（185MB whl）、verify 修正后 10/10 PASS；无 blocked。
- [x] Q5（提交）：未执行 git commit（遵守默认）。
- [x] 实施期两处细化（均留痕）：① LD_LIBRARY_PATH 改入 compose 全局环境（FR-6 注释）；② scikit-build-core 1.0 顶层包名为 scikit_build_core、Nuitka 无 __version__ 属性、patchelf/gdb 在 /usr/bin（守卫修正）；③ verify venv 须剥离 compose 注入的 PYTHONPATH/TVM_LIBRARY_PATH（脚本修正，对应客户无源码环境语义）。
