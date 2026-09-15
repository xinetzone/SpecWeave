# xmnn-dev 开发与打包叠加层 - Implementation Plan

> Review R1（fresh-context）裁决 **fail**：13 CP 中 12 pass，1 个 actionable
> （F-1/CP-R8）+ 若干 advisory。修复项见文末「Review Issues」区（I-1~I-7），
> 修复后进入 Review R2。

> 方法链路：F（双 ABI/运行时挂载/自包含打包内核，见 spec Background）→ V（Review R1 fresh-context 对抗审查）
> → I（本文件文件级任务）→ C（按任务原子收尾，不自动 git commit）。
> 所有容器/构建命令在 WSL2 `podman-machine-default` 内执行；宿主工作区 `d:\spaces\SpecWeave`。
> 移植真源（只读参考，禁止依赖）：`external/chaos/ai/xmnn-whl-builder/`、`external/chaos/ai/sdk/tasks/`。
> 范式真源：`apps/containers/client/overlays/onnx-quantized/`、`apps/containers/client/src/jpman_client/tasks/quant.py`。

## Task 1: overlay 骨架与 builder 打包元数据资产
- **Status**: `completed`
- **Completion Evidence**: builder/ 五资产落盘（pyproject.toml、CMakeLists.txt[7 glob+FATAL]、_xmnn_bootstrap.py、xmnn_bootstrap.pth、scripts/lib/logging.sh vendor）；T9 静态门禁全过；构建期资产 8 项守卫 [OK]（含 install-build-deps.py 共 9 文件）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 新建目录 `apps/containers/client/overlays/xmnn-dev/{builder/scripts/lib,smoke,scripts}`。
  - 从 `external/chaos/ai/xmnn-whl-builder/` 移植到 `builder/`（内容语义照搬，路径/收集逻辑按 FR-2 改写）：
    - `pyproject.toml`：xmnn 1.2.1-dev0 / requires-python>=3.14.6 / scikit-build-core>=0.5 / 19 依赖 + dev/examples/torch/full extras / cmake>=3.18 ninja>=1.10 Release / wheel.install-dir="."；
    - `CMakeLists.txt`：6 CACHE PATH 默认容器运行时布局（TVM_ROOT `/workspace/npu_tvm`、TVM_BUILD `/workspace/npu_tvm/build`、XMN_PYTHON_DIR `/workspace/npuusertools`、NUITKA_OUT `/opt/xmnn-builder/build/nuitka`、XMN_NUITKA_OUT 其子目录、LLVM_LIB_DIR 不写死由命令行 -D 注入）；保留 3-so FATAL 守卫、libtvm.so FATAL、VTA fsim 可选 glob、autolibs `cp -a`+`.xmnn_autolibs_keep` 占位、数据三目录、relay/std、patchelf `$ORIGIN`、tools_cpp chmod；LLVM 7 依赖改**文件名 glob + 真实名/逻辑名软链**（libLLVM.so.22*、libz.so.*、libzstd.so.*、libxml2.so.*、libiconv.so.*、libicuuc.so.*、libicudata.so.*），glob 空 → FATAL_ERROR 并 message 打印 `${LLVM_LIB_DIR}` 候选列表；
    - `_xmnn_bootstrap.py`、`xmnn_bootstrap.pth`：语义原样（_libs 解析、RTLD_GLOBAL 多轮、libtvm 末位加载、6 AST 类 hasattr 守卫）；
    - `scripts/lib/logging.sh`：从 ai 版 vendor（自包含，后续脚本 source 它；内容只保留本栈需要的日志函数）。
- **Acceptance Criteria Addressed**: AC-1, G2, G6
- **Test Requirements**:
  - `rule` TR-1.1: 五资产存在于 overlay builder/ 且 grep 不到 `external/chaos/ai|chaos/ai|/builder/dist|/builder/build`（镜像内路径应为 /opt/xmnn-builder；引用 ai 路径 0 命中）
  - `rule` TR-1.2: CMakeLists.txt 含 7 个 glob 收集项与 glob 空 FATAL_ERROR；含 libtvm.so 与三个 Nuitka .so 的 FATAL 守卫；含 patchelf $ORIGIN 段
  - `rule` TR-1.3: `_xmnn_bootstrap.py` 经 `/opt/conda/bin/python -m py_compile`（本地可用任意 python3 做语法级 py_compile）通过；.pth 内容恰为 `import _xmnn_bootstrap`

## Task 2: builder 三脚本（build-wheel / build-tvm / verify-wheel）
- **Status**: `completed`
- **Completion Evidence**: 三脚本落盘；`bash -n` 全过（WSL 实测 OK1-OK5）；参数化（TVM_ROOT/XMN_ROOT/DIST_DIR 默认 /workspace/dist、CCACHE_DIR、NUITKA_JOBS 等）、trap 还原（父 EXIT + 双子 shell EXIT/ERR）、六 cmake.define、libtvm 前置 exit 2；verify-wheel.sh 临时 venv（/tmp/xmnn-verify-venv，--system-site-packages，trap 清理）10 项保留
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - `builder/scripts/build-wheel.sh`（FR-3）：移植 ai 版 412 行流程——env 自探（CONDA_PREFIX 用 /opt/conda）、LLVM_CONFIG 与 CCACHE 配置（CCACHE_DIR 默认 /root/.ccache、NUITKA_CCACHE_BINARY 用法保持）、pip 镜像段、numpy/scipy 兜底、AST PREAMBLE 注入（标记 `# === XMNN BOOTSTRAP ===`，6 类纯 AST 补丁）与**无条件 restore + `trap ... ERR/EXIT` 兜底**、tvm 串行 Nuitka（PYTHONPATH=npu_tvm/python、nofollow vta/xmnn）、vta/xmnn 后台并行（`.vta_exit/.xmnn_exit` 回传；vta 带 `--include-data-dir=.../vta_hw/config=vta_hw/config`；xmnn PYTHONPATH 三段）、`python -m build --wheel --no-isolation` 六 cmake.define（NUITKA_OUTPUT_DIR/TVM_BUILD_DIR/TVM_ROOT_DIR/XMN_PYTHON_DIR/XMN_NUITKA_OUT/LLVM_LIB_DIR，LLVM_LIB_DIR 取 `$LLVM_CONFIG --libdir`）；全路径变量化（TVM_ROOT/XMN_ROOT/NUITKA_OUT/DIST_DIR 默认 /workspace/dist）；开头 libtvm.so 缺失 exit 2 + 中文提示 build-tvm；结尾打印 whl 名/大小/落盘目录；
  - `builder/scripts/build-tvm.sh`（FR-4）：set -euo pipefail；export LLVM_CONFIG=/opt/conda/envs/main/bin/llvm-config、PATH base 优先 + main/bin；检查 tasks.py 与 3rdparty/dmlc-core（缺失 exit 2 给 `git submodule update --init` 提示）；cd $TVM_ROOT；`/opt/conda/bin/python -m invoke config -f`；regex 置 USE_EXAMPLE_TARGET_HOOKS ON；`/opt/conda/bin/python -m invoke make`；断言 build/libtvm.so 并打印 MB；
  - `builder/scripts/verify-wheel.sh`（FR-5）：移植 10 项；改为创建 `/opt/conda/bin/python -m venv --system-site-packages /tmp/xmnn-verify-venv`，venv pip `install --no-deps --force-reinstall` 最新 `$DIST_DIR/xmnn-*.whl`，全部检查用 venv python；末尾 rm -rf venv；whl 路径参数化（`$1` 或 $DIST_DIR）；保留段首 unset LD_LIBRARY_PATH 干净环境检查。
- **Acceptance Criteria Addressed**: AC-1, AC-7, AC-8, G6
- **Test Requirements**:
  - `rule` TR-2.1: 三脚本 `bash -n` 全部通过；grep 不到 `external/chaos/ai|CHAOS_ROOT|--mount=type`
  - `rule` TR-2.2: build-wheel.sh 含三次 nuitka 调用且参数差异齐全（dill-compat、jobs、交叉 nofollow、include-data-dir、.module）、trap 还原、六 cmake.define、libtvm 前置 exit 2；DIST_DIR 默认 /workspace/dist
  - `rule` TR-2.3: build-tvm.sh 含 LLVM_CONFIG 导出、inv config -f、USE_EXAMPLE_TARGET_HOOKS regex、inv make、dmlc-core 子模块 exit 2 提示
  - `rule` TR-2.4: verify-wheel.sh 含 venv 创建/使用/清理三段，10 个检查计数点保留（import×3、_libs、RPATH、ctypes 干净加载、tvm.build、prelude.rly、.pth、数据三目录）

## Task 3: smoke 双脚本与内核注册脚本
- **Status**: `completed`
- **Completion Evidence**: _toolchain_guards.py（subprocess 列表参数断言 main cp314t、PATH 解析工具、Nuitka --version、scikit_build_core 1.x 包名修正、7 SONAME glob）、smoke_mounts.py（libtvm 缺席 exit 0 分支）、scripts/register-kernel.sh（xmnn-dev 内核 argv=/opt/conda/bin/python + 源码 env）；py_compile/bash -n 通过；构建期 root+devuser 双跑 PASS，kernelspec 双可见
- **Priority**: high
- **Depends On**: None
- **Description**:
  - `smoke/_toolchain_guards.py`（FR-8）：双 ABI（以脚本自身解释器断言 base：Py_GIL_DISABLED=0 且 _is_gil_enabled；另以 `/opt/conda/envs/main/bin/python -S -c` 子进程方式断言 main cp314t 且 GIL disabled——含引号逻辑必须写在脚本文件内的辅助函数中，用 subprocess 列表参数避免 shell 分词）；shutil.which 版本检查（/opt/conda/envs/main/bin 下 llvm-config 22.1.x、clang、cmake≥3.18、ninja、ccache、patchelf、gdb）；import nuitka(==4.1.3)、skbuild、build、invoke；/opt/xmnn-builder 资产清单；执行 `llvm-config --libdir` 后对 7 个 glob（libLLVM.so.22*、libz.so.*、libzstd.so.*、libxml2.so.*、libiconv.so.*、libicuuc.so.*、libicudata.so.*）逐一断言并打印实际 SONAME；
  - `smoke/smoke_mounts.py`（FR-8）：三挂载点与关键子目录存在断言；libtvm.so 分支：存在则 sys.path 断言 PYTHONPATH 前缀（/workspace/npu_tvm/python 等在 sys.path）、import tvm/vta/xmnn 并断言 `tvm.__file__` 以 /workspace/npu_tvm 开头、tvm.build('llvm') 向量加（n=4，×2 期望 [2,4,6,8]）；不存在则打印 build-tvm 提示并 exit 0；
  - `scripts/register-kernel.sh`（FR-9）：写 main env share/jupyter/kernels/xmnn-dev/kernel.json（argv /opt/conda/bin/python、display_name `Python 3.14 (xmnn dev)`、env.PATH base 优先、PYTHONPATH 三源码段、TVM_LIBRARY_PATH、LD_LIBRARY_PATH 含 build、build/vta、/opt/conda/envs/main/lib）；root+devuser kernelspec list 双可见断言。
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-3.1: 两 py 脚本 `python -m py_compile` 通过；register-kernel.sh `bash -n` 通过
  - `rule` TR-3.2: _toolchain_guards.py 覆盖双 ABI/7 工具/4 模块/7 glob/资产清单五段；subprocess 调用使用列表参数（grep 不到 `shell=True`）
  - `rule` TR-3.3: smoke_mounts.py 的 libtvm 缺失分支 exit 0 且存在分支含路径前缀与向量加断言

## Task 4: Containerfile.xmnn-dev
- **Status**: `completed`
- **Completion Evidence**: 五 Layer（apt patchelf/gdb → mamba main 22.1.8 pin cp314t → COPY builder + install-build-deps.py 装 59 包[19 依赖+工具] → COPY smoke/scripts → register-kernel+双守卫+横幅）；无 SHELL/HEALTHCHECK/USER/ENTRYPOINT；grep 禁项 0 命中；真实构建退出 0（见 Task 10）
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3
- **Description**:
  - overlay 根新建 `Containerfile.xmnn-dev`（FR-1）：全局 ARG（BASE_IMAGE/PIP_MIRROR/CONDA_MIRROR）置顶；FROM rootless 薄叠加；LABEL org.specweave.* 六键；
  - Layer 1 apt（patchelf gdb，--no-install-recommends，同层清 lists；PIP/APT 镜像仅在 build-arg 非 official 时幂等设置）；
  - Layer 2 main env mamba 工具链（pin `python=*=*cp314t` + llvmdev/clangdev/clang/lld=22.1.8 + cmake/ninja/make/ccache + libgcc/libstdcxx-ng，conda clean -afy）；CONDA_MIRROR 非 official 时按基底 .condarc 约定幂等写 custom_channels（tuna/aliyun），official 继承；
  - Layer 3 base env pip（显式 /opt/conda/bin/python -m pip；nuitka==4.1.3、scikit-build-core>=0.10、build、wheel、invoke、ipykernel + 19 依赖；PIP_MIRROR 三段；清缓存）；
  - Layer 4 COPY builder→/opt/xmnn-builder、smoke→/opt/xmnn-dev-smoke、scripts/register-kernel.sh→/opt/xmnn-scripts/；chmod a+rX；
  - Layer 5 bash register-kernel.sh + base python 跑 _toolchain_guards.py + devuser 复跑 + 横幅；
  - 全部 RUN `/bin/bash -lc`；无 SHELL/HEALTHCHECK/USER；不覆盖 ENTRYPOINT/CMD/WORKDIR。
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-4, AC-13
- **Test Requirements**:
  - `rule` TR-4.1: grep 不到 `SHELL \[|HEALTHCHECK|ENTRYPOINT|^USER |--privileged|external/chaos`；FROM 恰为一个 `${BASE_IMAGE}`（单阶段薄叠加，dist 镜像不需要）
  - `rule` TR-4.2: mamba 行同时含 22.1.8 四包与 `python=*=*cp314t` pin；pip 行含 nuitka==4.1.3 且解释器为 /opt/conda/bin/python
  - `rubric` TR-4.3: 与 Containerfile.quantized 的 OCI/分层/标签纪律对齐度；scale 1-5；anchors 1=内联嵌套引号/覆盖入口/工具装错 env；3=可构建但 ≥2 处无注释偏离；5=四段分层、镜像源幂等、守卫固化、标签完整与 onnx 一一对应；threshold >= 4；evidence=逐段对照

## Task 5: compose.yaml 与 overlay .env.example
- **Status**: `completed`
- **Completion Evidence**: `podman-compose config` 退出 0 且 AC-2 断言逐项成立（1 服务/build 内联/bridge/2223/8890/4 长语法 bind/1 named volume/三必需/环境键/无 command-healthcheck）；键集合 17 与两处 .env 三方 diff 空；实现细化 LD_LIBRARY_PATH 入环境已回写 spec FR-6 留痕
- **Priority**: high
- **Depends On**: None
- **Description**:
  - `compose.yaml`（FR-6）：name xmnn-dev、服务 xmnn、container_name/image 插值、内联 build（args 三 ARG）、network_mode bridge（实证注释）、两端口 2223/8890、四 bind 长语法（workspace/npu_tvm/npuusertools/models，create_host_path true）+ named volume xmnn-ccache→/root/.ccache + 顶层 volumes 声明、三必需（cgroupns 1.6.0 空操作注释）、environment（四凭证 + PYTHONPATH + TVM_LIBRARY_PATH + NPU_TOOLS_ROOT + XMNN_TOOLS_ROOT + OMP_NUM_THREADS + NUITKA_JOBS；不放 LD_LIBRARY_PATH）、labels、restart、无 command/healthcheck；头注释引用 OKF concepts 与 xmnn-overlay 规则；
  - `.env.example`（FR-7）：16 键全量带注释，默认值与 compose `${VAR:-default}` 一致（端口 2223/8890；源码相对路径五级 `../../../../../external/chaos/...`；workspace `../../workspace`）。
- **Acceptance Criteria Addressed**: AC-2, AC-11, AC-13
- **Test Requirements**:
  - `rule` TR-5.1: machine 内（或 WSL）`podman-compose -f compose.yaml config` 退出 0 且满足 AC-2 全断言
  - `rule` TR-5.2: .env.example 生效键集合 == compose 插值键集合（shell 手工/脚本 diff，注释态除外）
  - `rule` TR-5.3: 所有 bind 为长语法且 create_host_path: true；无短语法；无 privileged

## Task 6: invoke xmnn.* 命名空间（xmnn.py + 注册 + configure）
- **Status**: `completed`
- **Completion Evidence**: xmnn.py 落盘（无 import podman，双门禁/daemon 预检/四路径绝对 POSIX+存在性硬校验/build 基底预检/build-tvm+wheel exec/-e 透传 NUITKA_JOBS 等/smoke 双路径）；`invoke --list` 实测 8 任务齐全；Windows 原生 `inv xmnn.ps` 实测 Exit 1 + 双路径中文指引；__init__.py 注册 + configure xmnn 段 + docstring 五命名空间
- **Priority**: high
- **Depends On**: Task 4, Task 5
- **Description**:
  - 新建 `src/jpman_client/tasks/xmnn.py`（FR-10）：以 quant.py 为范式（常量 PROJECT_NAME=xmnn-dev/SERVICE_NAME=xmnn/DEFAULT_IMAGE_TAG/MAIN? base python 路径常量 BASE_PYTHON=/opt/conda/bin/python/SMOKE_DIR=/opt/xmnn-dev-smoke）；门禁双门（平台/二进制）+ daemon 预检；`_prepare_env` 解析 XMNN_WORKSPACE（mkdir + to_posix_path）与 NPU_TVM_PATH/NPUUSERTOOLS_PATH/MODELS_PATH（默认值取 client 根的 ../../external/chaos/*——invoke cwd 在 client，故 `root/external/chaos/npu_tvm`；解析绝对 POSIX，**存在性硬校验**，缺失 Exit 1 中文指引区分路径）；build/up/down/ps/logs/smoke 六任务同构 quant；smoke 双路径（运行→compose exec 依次跑 _toolchain_guards.py + smoke_mounts.py（base python）；未运行→podman run --rm 仅 guards）；新增 build-tvm（compose exec -T xmnn bash /opt/xmnn-builder/scripts/build-tvm.sh）、wheel（help 含 --jobs/--clean/--tvm-flags，映射 NUITKA_JOBS/CLEAN_REBUILD/TVM_COMPILE_FLAGS 环境变量后 exec build-wheel.sh）；**禁止 import podman**；
  - 改 `tasks/__init__.py`：import xmnn、注册 Collection("xmnn") 8 任务、configure 增加 xmnn 段（image_tag/base_image/container_name/ssh_port 2223/jupyter_port 8890）；模块与包 docstring 更新（五命名空间）。
- **Acceptance Criteria Addressed**: AC-11, AC-12, G5
- **Test Requirements**:
  - `rule` TR-6.1: `python -c "import jpman_client.tasks"`（py314 环境）成功；`invoke --list` 含 8 个 xmnn.* 任务名
  - `rule` TR-6.2: xmnn.py grep 不到 `import podman|from podman`；含 _gate_platform/_gate_compose_binary 且 Windows 分支 raise Exit(1)
  - `rule` TR-6.3: 三源码路径解析为绝对 POSIX 且不存在时 Exit 1（可用临时不存在路径单测/手工验证）；build 含基底镜像存在性预检

## Task 7: client 集成（.env.example 段 + xmnn-overlay.md 规则）
- **Status**: `completed`
- **Completion Evidence**: root .env.example xmnn 段 17 键（含注释态 BASE_IMAGE）三方 diff 空；.agents/rules/xmnn-overlay.md 九节落盘（边界/双门禁/双 ABI/运行时挂载/打包内核/三必需 bridge/标签/双冒烟/选型边界）
- **Priority**: high
- **Depends On**: Task 5, Task 6
- **Description**:
  - client 根 `.env.example` 追加 `xmnn.*` 段（FR-11，全键注释态，与 overlay .env.example 同键集合，头部注明 Windows 门禁与优先级链）；
  - 新建 `.agents/rules/xmnn-overlay.md`（FR-12，单一职责仿 quant-overlay.md 九节）：架构边界（三层 + xmnn.* 为 compose 子进程层，禁 import podman、不回流根 run）、双门禁、双 ABI 工具链契约（base cp314 GIL 打包/main cp314t 服务 + LLVM 22.1.8 装 main 且 pin 不互换 + Nuitka 4.1.3 仅 cp314）、源码仅运行时挂载（四 bind + 存在性校验 + build 树 9p 提示）、打包内核契约（/opt/xmnn-builder 自包含、AST 注入/还原 trap、SONAME glob+守卫、ccache 卷语义、DIST 落 /workspace/dist）、compose 三必需/bridge 实证/标签接缝、冒烟双路径（guards 双路径、mounts 仅运行态）、选型依据（OKF concept 10）。
- **Acceptance Criteria Addressed**: AC-11, AC-13, AC-14
- **Test Requirements**:
  - `rule` TR-7.1: root .env.example xmnn 段键集合与 overlay .env.example 生效键 diff 为空（脚本列键比较）
  - `rule` TR-7.2: xmnn-overlay.md 含双 ABI/SONAME/AST trap/ccache/bridge/门禁六要素，且相对链接（quant-overlay.md、OKF bundle、overlay README）真实可达

## Task 8: 文档与路由登记（overlay README + client AGENTS/README + apps AGENTS）
- **Status**: `completed`
- **Completion Evidence**: overlay README（定位/双 ABI/两路径/八任务/性能/参数表/关系表/排障）、client README §13、client AGENTS.md（概述/路由树/路由表×2/规范入口/C12/CHANGELOG）、.agents/README（4→5 rules、资产表、对应表、changelog）、apps/AGENTS（路由行+边界表）；相对 .md 链接 Test-Path 全通
- **Priority**: medium
- **Depends On**: Task 7
- **Description**:
  - `overlays/xmnn-dev/README.md`（FR-13）：定位一句话、镜像/双 ABI/服务/端口表、前置（基底镜像、源码路径、machine、资源建议）、invoke 路径八任务、裸 compose 路径、开发调试会话（SSH 2223/Jupyter 8890/xmnn-dev 内核/PYTHONPATH/改源码即时生效）、打包手册（build-tvm 可选→wheel→产物→verify venv；NUITKA_JOBS/CLEAN_REBUILD/TVM_COMPILE_FLAGS；9p 慢→WSL 原生克隆替代）、双冒烟、参数表、与 onnx/scratch notebook/chaos ai 关系表（参考不依赖声明）、子模块/排障；
  - client `AGENTS.md`：概述命名空间四→五（xmnn.* 八任务）、嵌套路由树加 overlays/xmnn-dev 与 rules/xmnn-overlay.md、上下文路由表两行（xmnn.* 任务、overlay 镜像/打包）、P0 速览加 C12（xmnn.* 同 C11 子进程纪律 + 双 ABI 不互换 + 源码运行时挂载）、变更日志 2026-09-14 条目；
  - `.agents/README.md` 若列 rules 文件清单则同步；`apps/AGENTS.md` client 路由行补 xmnn-dev 叠加层（一行）；client 根 README 增加最小 xmnn.* 小节（与 quant 节同级，简短指向 overlay README）。
- **Acceptance Criteria Addressed**: AC-12, AC-14
- **Test Requirements**:
  - `rule` TR-8.1: 全部新增/修改 md 的相对链接 Test-Path/check-links 可达；无 file:/// 绝对链接
  - `rule` TR-8.2: README 参数表（.env 键/invoke 参数/compose 插值）三处一致；八任务名与 xmnn.py 实际注册名逐字一致
  - `rubric` TR-8.3: 文档-实现一致性；scale 1-5；anchors 1=描述与实现矛盾/残留 ai 路径依赖措辞；3=主要一致但有 1-2 处过时；5=逐条一致、关系表清晰、排障可执行；threshold >= 4

## Task 9: 静态门禁汇总（实施期门）
- **Status**: `completed`
- **Completion Evidence**: 6 个 py 文件 py_compile 退出 0；5 个 shell 脚本 bash -n OK1-OK5；AC-1 功能性文件 grep 禁项 0 命中（仅 README 2 处允许的事实表述、xmnn.py 1 处禁项注释）；podman-compose config AC-2 全断言；invoke --list 8 任务；Windows 门禁 Exit 1；三文件 md 链接全通
- **Priority**: high
- **Depends On**: Task 6, Task 7, Task 8
- **Description**:
  - 汇总执行 AC-1 grep 门禁、AC-2 config 断言、TR-1~TR-8 静态项（py_compile/bash -n/键集合 diff/invoke --list/grep 禁项）；输出固化为本任务完成证据；任何失败回对应任务修复后重跑。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-11
- **Test Requirements**:
  - `rule` TR-9.1: 全部静态检查命令退出 0 且输出归档（grep 0 命中、config 断言清单、键 diff 空、--list 8 任务、语法检查全过）

## Task 10: 真实镜像构建取证
- **Status**: `completed`
- **Completion Evidence**: 首次构建在守卫层拦截 4 项探测错误（patchelf/gdb 误查 main/bin[实为 /usr/bin]、nuitka 无 __version__、scikit-build-core 1.0 顶层包名是 scikit_build_core 非 skbuild）→ 修守卫后缓存重建退出 0；`localhost/xmnn-dev:latest` 4.43 GB；构建日志：mamba LLVM 22.1.8 pin 求解成功、pip 59 包（nuitka-4.1.3-cp314/scikit-build-core-1.0.3/19 依赖）、root 守卫全 PASS（双 ABI + clang/cmake/ninja/ccache + patchelf 0.18/gdb 17.1 + 7 SONAME 实测 libLLVM.so.22.1/libxml2.so.16/libicuuc.so.78/libicudata.so.78/libz.so.1/libzstd.so.1/libiconv.so.2 与移植快照零漂移）+ devuser 复跑 PASS + 横幅；独立复跑双 ABI：base 3.14.7 Py_GIL_DISABLED=0/_is_gil_enabled=True、main 3.14.7 =1/False；inspect Entrypoint=[tini -- entrypoint.sh]、Cmd=[]、Config 无 Healthcheck 键；kernelspec xmnn-dev 双身份可见
- **Priority**: high
- **Depends On**: Task 9
- **Description**:
  - machine 内执行 `invoke xmnn.build`（或裸 podman build）；观察 conda 求解（22.1.8 + cp314t pin）与 pip 解析；若 conda-forge 临时不可用/求解失败，按 NFR-5 自动重试（上限 4，网络/镜像源类：切 tuna/aliyun），方法类失败回 Implement；
  - 取证 AC-3/AC-4：守卫日志（双 ABI、7 库 SONAME 实值）、devuser 复跑、images、inspect（入口链/无 Healthcheck）、main python build string 复核。
- **Acceptance Criteria Addressed**: AC-3, AC-4
- **Test Requirements**:
  - `rule` TR-10.1: 构建退出 0；AC-3/4 各断言逐项有日志佐证（含 SONAME 行、nuitka 4.1.3、main cp314t 未互换）
  - `rule` TR-10.2: 镜像 inspect Entrypoint=tini→/usr/local/bin/entrypoint.sh、Healthcheck=<nil>、Workdir=/workspace

## Task 11: 栈 E2E（起停/端口/内核/挂载/源码调试链路）
- **Status**: `completed`
- **Completion Evidence**: podman-compose up -d 容器 Up（pasta dbus warning 不阻止，bridge 生效）；2223/8890 映射就位、curl /lab=302；三挂载点可见（libtvm.so 81,650,176B 在位）；kernelspec xmnn-dev（root+devuser 双可见，kernel.json argv=/opt/conda/bin/python 且 env 携带 PYTHONPATH/TVM_LIBRARY_PATH/LD_LIBRARY_PATH 源码三段）；smoke_mounts root 与 devuser 双身份均 PASS（tvm/vta/xmnn __file__ 全部来自 /workspace 挂载源码、tvm.build llvm 向量加 [2,4,6,8]）；workspace bind 探针宿主写→容器即时读到→已清理。同时证明挂载树 libtvm.so 与新装 main LLVM 22.1.8 运行时 ABI 兼容（消解 Assumptions 最大风险）
- **Priority**: high
- **Depends On**: Task 10
- **Description**:
  - `invoke xmnn.up`（如遇 aardvark 错误复核 bridge 是否生效，不得加 x-podman 偏方）；AC-5 全项（2223、8890/lab、三挂载、kernelspec xmnn-dev argv/env、双身份可见）；
  - AC-6：base python import tvm/vta/xmnn 路径前缀断言 + tvm.build 向量加；`invoke xmnn.smoke` 双脚本；宿主侧无害改动即时可见取证（在 npuusertools 某 .py 加注释→容器内 grep 到，随后还原）。
- **Acceptance Criteria Addressed**: AC-5, AC-6
- **Test Requirements**:
  - `rule` TR-11.1: AC-5 各项有命令输出佐证；kernel.json env 含三源码 PYTHONPATH 段
  - `rule` TR-11.2: tvm.__file__ 前缀 == /workspace/npu_tvm；向量加 [2,4,6,8]；smoke_mounts 退出 0；宿主改动容器可见且已还原

## Task 12: wheel 打包闭环 + 隔离验证 + 源码零修改
- **Status**: `completed`
- **Completion Evidence**: ① `podman exec build-wheel.sh` 退出 0（8 clang 满载，tvm 串行→vta/xmnn 并行→scikit-build 组装），产物 `/workspace/dist/xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl` 193,456,300B（185MB，旧谱系 187,896,958B 同量级），宿主 `client/workspace/dist/` 可见；② whl 清单 158 项：tvm/vta/xmnn 三 cp314 .so、_libs 14 项（libtvm.so+libLLVM.so.22.1 软链+6 依赖真实文件与 SONAME 软链）、_xmnn_bootstrap.py/.pth、autolibs 17(含占位)/tools_cpp 89/fonts 1、vta_hw/config 25、relay/std 4 .rly（含 prelude.rly）；③ verify-wheel.sh 首跑暴露 venv 仍继承 compose PYTHONPATH/TVM_LIBRARY_PATH（源码遮蔽 wheel）→ 脚本开头 unset 三变量（LD_LIBRARY_PATH/PYTHONPATH/TVM_LIBRARY_PATH）修正后 **10/10 PASS**（含 13 libs RPATH 全 $ORIGIN、干净环境 ctypes 加载 libtvm、tvm.build 数值断言、.pth、数据目录）；④ venv 已自动清理（/tmp 0 残留）、base pip list 无 xmnn/tvm/vta、base python import tvm 仍指向源码树（零污染）；⑤ AC-9：三 __init__.py md5 与打包前基线逐字一致、M 计数 14820/99 不变、0 个 .bak 残留、日志三处 [RESTORE]；⑥ 修正版脚本经镜像重建（c5fc1967d7b4，4.43GB，守卫复跑 PASS）收口入交付镜像
- **Priority**: high
- **Depends On**: Task 11
- **Description**:
  - 打包前基线：npu_tvm/npuusertools `git status --porcelain` 快照 + find .bak；
  - `invoke xmnn.wheel`（宿主 build/libtvm.so 已存在，跳过 build-tvm；资源紧张时 --jobs 4）；取证 AC-7（whl 名/大小/unzip -l 清单）；
  - 容器内 verify-wheel.sh（venv 隔离）取证 AC-8；
  - 打包后快照比对 + find .bak 取证 AC-9；trap 逻辑代码审查（正常/异常两路）；
  - 若 libtvm.so 与新 main env LLVM 运行时不兼容导致验证失败：回 Implement 评估 `invoke xmnn.build-tvm` 重编（先子模块检查），在证据中记录决策，禁止绕过验证项。
- **Acceptance Criteria Addressed**: AC-7, AC-8, AC-9
- **Test Requirements**:
  - `rule` TR-12.1: whl 文件名/位置/大小/内容清单满足 AC-7；build-wheel.sh 退出 0
  - `rule` TR-12.2: verify 10 项全 PASS、venv 已清理、base pip list 无 xmnn/tvm/vta wheel
  - `rule` TR-12.3: 两仓库前后 git status 快照一致、.bak 0 个、脚本含 trap 还原

## Task 13: 清理幂等、零侵入与收尾证据
- **Status**: `completed`
- **Completion Evidence**: ① 第二轮 up（新镜像）后守卫/挂载 smoke/HTTP 302 全过（幂等）；② plain down 后 `xmnn-dev_xmnn-ccache` 卷保留；`down --volumes` 后项目标签容器 0、卷已删、无 xmnn 项目网络；bind 数据保留（wheel 仍在 workspace/dist）；③ 裸 compose 在 client/workspace 预创建的 npu_tvm/npuusertools/models 三个空目录 rmdir 成功（确认为空，行为已文档化至 xmnn-overlay.md §4 + README 排障，invoke 绝对路径不产生）；④ AC-12：主仓改动恰为白名单 10 项（6 改：apps/AGENTS、client AGENTS/README/.agents README/.env.example/tasks __init__；4 新：spec 目录、xmnn-overlay.md、overlays/xmnn-dev/、xmnn.py），onnx overlay 与 quant.py 0 改动，external/ 不被主仓追踪且两外部仓 hash/计数零变化；quant 门禁行为实测保持（零回归）；tasks 包 invoke --list 正常
- **Priority**: medium
- **Depends On**: Task 12
- **Description**:
  - AC-10：down→容器/网络零残留、ccache 卷保留、第二轮 up/down、--volumes 删卷；
  - AC-12：主仓库 git status 对照 NFR-6 白名单、onnx overlay 与 quant.py 零改动、tasks 包导入、quant 命名空间可列示；
  - 汇总全部 Completion Evidence 入本文件，准备 Review R1 交接包（spec/tasks 绝对路径、运行环境、关键命令、证据索引）。
- **Acceptance Criteria Addressed**: AC-10, AC-12
- **Test Requirements**:
  - `rule` TR-13.1: down/卷/两轮幂等计数断言全过
  - `rule` TR-13.2: git status 改动文件全部在 NFR-6 白名单；external/chaos 与 onnx overlay clean；quant 零回归
  - `rubric` TR-13.3: 证据完整性；scale 1-5；anchors 1=关键 AC 缺运行证据/证据不可复查；3=证据齐但分散；5=每 AC 可按证据独立复查且命令可重放；threshold >= 4

---

# Review Issues（R1 fail 后物化，修复后请 Review R2 复审）

## Issue I-1: AST 注入的 SIGKILL/OOM 路径缺口与重跑污染（R1 F-1，actionable）
- **Status**: `completed`
- **Completion Evidence**: 新增 `builder/scripts/lib/ast_inject.sh`（原子备份 tmp.$$+mv；注入前状态机：含 PREAMBLE 且 bak 在→自愈还原、含 PREAMBLE 无 bak→Exit 2 要求 git checkout 绝不覆盖；ast_restore 信息走 stderr 保护 `$(ast_inject)` stdout 契约——该 stdout 污染是自测 B 场景实测发现的次生 bug）；build-wheel.sh 全程 `_restore_all` EXIT trap（确定性 .bak 路径覆盖三对）+ 子 shell 注入失败写 exit 2；容器内四场景故障注入实测 A/B/C/D 全 PASS（正常 md5 一致/残留自愈/无 bak 拒动/幂等 no-op）；R3 真实打包后三 __init__.py md5 仍与基线逐字一致
- **Priority**: high
- **Depends On**: None
- **Discovered By**: Review R1（CP-R8 fail）
- **Description**:
  - build-wheel.sh 的 vta/xmnn 并行子 shell 被 SIGKILL（OOM，jobs=8 约 15GB 峰值，README 自己标注的场景）时 bash trap 不触发；父 shell 的 EXIT trap 在 tvm 段后已 `trap - EXIT`，无统一还原兜底。
  - `inject_ast_preamble()` 无条件 `cp init backup` 先于 marker 检查：上次若残留「init 已注入 + .bak 干净」（注入完成后被杀），重跑会用污染版覆盖干净备份，restore 后工作树被静默持续污染（只能 git checkout 恢复），反证 spec「零修改」承诺。
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `rule` TR-I-1.1: AST 注入/还原函数提取到 `builder/scripts/lib/ast_inject.sh` 可 source；注入前做状态机检查（init 含 marker 且 .bak 在 → 先自愈还原再继续；含 marker 但 .bak 缺失 → Exit 2 明确报 `git checkout` 路径，禁止覆盖任何文件）；备份写临时文件后原子 mv。
  - `rule` TR-I-1.2: build-wheel.sh 注册**全程统一**的 `_restore_all` EXIT trap（tvm/vta/xmnn 三对 init/backup 幂等还原，正常路径还原后清空）；子 shell 局部 trap 保留，父 wait 后任一退出码非零也能在 EXIT 统一兜底。
  - `rule` TR-I-1.3: 在 /tmp 构造假包目录做自愈故障注入实测：①注入态+.bak 在→重跑自动还原并成功；②注入态无 .bak→Exit 2 不覆盖；③正常路径备份/注入/还原后文件与原始逐字一致（md5）。
  - `rubric` TR-I-1.4: 外部源码保护强度；scale 1-5；anchors 1=可被 SIGKILL+重演变成持续污染；3=有 trap 但重跑不安全；5=KILL 不可捕获的物理边界外全部路径幂等自愈且明确报错；threshold >= 4。

## Issue I-2: CMake 把 SONAME 软链解引用复制为重复常规文件（R1 F-2，advisory 采纳）
- **Status**: `completed`
- **Completion Evidence**: install_llvm_deps 重写为「软链 dest 去引用 cp -L 为短名单副本 + 被指向的长名真实文件跳过 + 无链真实文件原名装」单副本算法；修复过程实证两个真问题：① CMake 4.4 仅认 `REMOVE_DUPLICATES`（复数，3.x 接受单数，移植源旧拼写 FATAL）；② dest 为同名绝对路径时漏取 basename 致 cp 目标非法且 execute_process 静默吞错（加 RESULT_VARIABLE FATAL）。最终 wheel `_libs` 8 项（libLLVM.so.22.1 187MB 原名装 + libtvm.so + 6 个短名单副本），无重复长名；wheel 177,764,212B（原 193,456,300B，-8%；libLLVM 占大头压缩后差异有限）；verify 10 项 PASS（8 entries、7 other libs RPATH 全 $ORIGIN、干净环境 ctypes 加载、tvm.build 数值断言）
- **Priority**: medium
- **Depends On**: None
- **Discovered By**: Review R1（CP-R6，附 finding）
- **Description**: wheel `_libs` 14 项实际 0 软链：install(FILES) 对 glob 命中的 SONAME 软链解引用复制为常规文件，install(CODE) 的 `ln` 因逻辑名已存在而跳过——功能可用但 6 库各冗余一份（约 40MB，ICU 占大头），且未来 libLLVM glob 命中双版本会膨胀约 197MB；与「真实文件+逻辑名软链」设计语义不符，文档/证据表述漂移。
- **Acceptance Criteria Addressed**: AC-7, AC-14
- **Test Requirements**:
  - `rule` TR-I-2.1: CMakeLists 改为只对 REALPATH 去重后的真实文件 install(FILES)；所有「逻辑名≠真实名」一律 install(CODE) `ln -sfn <real> <logical>`（无条件，覆盖误装同名常规文件）；重打 wheel 后 _libs 中 SONAME 条目为符号链接（unzip 无法表达链接？改用 `python zipfile + ZipInfo.external_attr` 或 `bsdtar/unzip -l` 无法验证；以构建日志 `Created symlink` + 容器安装后 `ls -l _libs` 实测为证据）。
  - `rule` TR-I-2.2: 重打 wheel 的 verify 10 项仍全 PASS（重点 test 5 干净环境 ctypes 加载，证明软链语义可被动态加载器解析）；whl 体积较 193,456,300B 明显下降（记录新值）。

## Issue I-3: 交付镜像烤入宿主 cpython-313 pyc（R1 F-7，advisory 采纳）
- **Status**: `completed`
- **Completion Evidence**: 新增 overlay `.dockerignore`（__pycache__/、*.py[cod]、*.bak_*、*.tmp.*、.env、pytest/mypy/ruff cache）；清除宿主树 3 个 __pycache__；最终镜像 5cab67f04104 `find /opt/xmnn-builder /opt/xmnn-dev-smoke -name '*.pyc' -o -name __pycache__` 计数 0
- **Priority**: medium
- **Depends On**: None
- **Discovered By**: Review R1
- **Description**: 宿主 Windows Python 3.13 py_compile/T9 静态检查在 overlay 树内生成 `__pycache__/*.cpython-313.pyc`，被 `COPY builder/ smoke/ scripts/` 带入交付镜像（4 个，777），属错误 ABI 的构建卫生问题。
- **Acceptance Criteria Addressed**: AC-3, AC-13
- **Test Requirements**:
  - `rule` TR-I-3.1: overlay 新增 `.dockerignore`（`__pycache__/`、`*.pyc/*.pyo`、`.bak_*`、`.env`、`.pytest_cache`）；清掉宿主树内现存 __pycache__；重建镜像后 `podman run --rm --entrypoint find <img> /opt/xmnn-builder /opt/xmnn-dev-smoke -name '*.pyc' -o -name __pycache__` 输出为空。

## Issue I-4: verify-wheel.sh set -e 中止与 4b 不 assert（R1 F-3/F-4，advisory 采纳）
- **Status**: `completed`
- **Completion Evidence**: tests 4-9 全部改走 check()（失败计 FAIL 不中止，结尾必出 SUMMARY）；4b 对 libtvm.so 自身 RPATH 非 $ORIGIN 直接 assert FAIL（其他库保留 informational 统计）；实测 10 passed/0 failed（4b：libtvm RPATH $ORIGIN + 7 other libs 全 $ORIGIN/0 without）
- **Priority**: low
- **Depends On**: None
- **Discovered By**: Review R1
- **Description**: tests 4-9 裸 python 调用在 `set -e` 下失败即整脚本退出，SUMMARY/计数失效；test 4b 对缺失 RPATH 仅 WARN 不计数失败。
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `rule` TR-I-4.1: tests 4-9 改为 check() 式捕获（失败计入 FAIL 不中止），结尾始终输出 SUMMARY；4b 对「libtvm 自身 RPATH 非 $ORIGIN」直接判 FAIL（其余第三方库保留 WARN 计数展示）；bash -n 通过并在容器内重跑 10 项全 PASS。

## Issue I-5: build 任务的镜像源 env 口径注释（R1 F-5，advisory 采纳）
- **Status**: `completed`
- **Completion Evidence**: xmnn.py build 的 --pip-mirror/--conda-mirror help 注明「独立 build 只认参数；.env 经 xmnn.up 内联 build 插值生效」；overlay README 参数表 PIP_MIRROR/CONDA_MIRROR 行同步该口径
- **Priority**: low
- **Depends On**: None
- **Discovered By**: Review R1
- **Description**: `invoke xmnn.build` 独立运行不读 .env 的 PIP_MIRROR/CONDA_MIRROR（与 quant 同族；.env 值只在 `xmnn.up` 的 compose 内联 build 插值时生效），缺显式说明易误用。
- **Acceptance Criteria Addressed**: AC-14
- **Test Requirements**:
  - `rule` TR-I-5.1: xmnn.py build/up help 与 overlay README 参数表注明该口径（独立 build 用命令行参数；.env 经 up 内联 build 生效）。

## Issue I-6: 键数口径 16/17 不一致（R1 F-6，trivial 采纳）
- **Status**: `completed`
- **Completion Evidence**: spec FR-7 改写为「17 键=16 生效+注释态 BASE_IMAGE」；client AGENTS 嵌套树、.agents/README 资产表统一 17 键表述；grep 无「xmnn 栈 16」残留
- **Priority**: low
- **Depends On**: None
- **Discovered By**: Review R1
- **Description**: spec FR-7 与部分文档写「16 键」，实际含注释态 BASE_IMAGE 为 17 键。
- **Acceptance Criteria Addressed**: AC-11, AC-14
- **Test Requirements**:
  - `rule` TR-I-6.1: spec/规则/README 中键数表述统一为 17（16 生效 + 1 注释态 BASE_IMAGE），grep 不到「16 键/16 项」矛盾表述。

## Issue I-7: build 命令 -f 路径未 shlex（R1 F-8，trivial 采纳）
- **Status**: `completed`
- **Completion Evidence**: xmnn.py build 的 `-f` 改 `shlex.quote(str(containerfile))`；py_compile 通过
- **Priority**: low
- **Depends On**: None
- **Discovered By**: Review R1
- **Description**: xmnn.py build 的 `-f {containerfile}` 未走 shlex.quote（路径含空格时会断）。
- **Acceptance Criteria Addressed**: AC-11
- **Test Requirements**:
  - `rule` TR-I-7.1: `-f` 与 context 路径均经 shlex.quote；py_compile 通过。
