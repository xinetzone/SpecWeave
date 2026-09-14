# agent-monetize-dev 开发/原生编译打包叠加层 - Product Requirements Document

> 方法论链路：本需求由 **client-overlay-scaffold** 技能驱动（技能创建后的
> 首次实战 dogfood），形态判定为**形态 B（轻量工具链挂载栈）**——较
> xmnn-dev 更轻：单 C++ 文件 + tvm-ffi（apache-tvm-ffi pip wheel 自带
> 头/库），不需要 Nuitka、不需要编译整个 TVM、工具链用 apt clang 而非
> conda LLVM 22。全程 podman-compose 子进程层，遵循技能 SKILL.md 与
> delivery-checklist 的不可变纪律与四级验证链。

## Overview

- **Summary**: 在 `apps/containers/client/overlays/agent-monetize-dev/`
  新建 agent-monetize 的**源码调试 + tvm-ffi 原生 C++ 编译 + wheel 打包**
  薄叠加镜像 `localhost/agent-monetize-dev:latest`；运行时 bind 挂载
  `apps/agent-monetize` 源码，容器内 clang++ 编译 `native/score_opportunity.cc`
  为 `score_opportunity.so`（链接 pip 包 apache-tvm-ffi 自带的
  `libtvm_ffi.so`），Python 经 tvm-ffi 走原生 PackedFunc 打分；并能
  `python -m build` 打 agent-monetize wheel。client 侧新增 opt-in
  `monetize.*` 八任务命名空间。**对 agent-monetize 源码仅做 3 处最小
  跨平台适配**（.dll→按平台选 .so/.dylib），不改变其 Windows 既有路径。
- **Purpose**: agent-monetize 的原生 FFI 路径此前**只有 Windows/MSVC
  构建脚本**（`native/build.ps1`→`.dll`），Linux 下无法编译/加载原生
  模块，开发只能走纯 Python 参考降级。本栈补齐 Linux rootless 开发/编译/
  验证闭环，使"原生 tvm-ffi 打分"在 WSL2 容器内可开发可调试可复现。
- **Target Users**: 在 WSL2 rootless 上开发/调试 agent-monetize、
  验证 tvm-ffi 原生打分与纯 Python 参考实现一致性、需要在 Linux 出 wheel
  的开发者。

## Goals / 形态特征（相对 xmnn-dev 的轻量化）

- **G1 镜像+栈**: `overlays/agent-monetize-dev/` 薄叠加；compose 单服务
  + 2 bind（workspace + agent-monetize 源码）；`invoke monetize.*`
  8 任务（build/up/down/ps/logs/smoke/build-native/wheel）。
- **G2 apt clang 轻工具链（非 conda LLVM）**：编译单个 `.cc` 对 LLVM
  版本不敏感，apt `clang`（Ubuntu 26.04 自带）+ patchelf + gdb 即可；
  不装 conda LLVM 22（镜像显著小于 xmnn-dev）。tvm-ffi 的头与库全部
  来自 pip wheel `apache-tvm-ffi`。
- **G3 单一 cp314 GIL ABI**: apache-tvm-ffi 0.1.13.post3 只发布
  cp314-cp314（GIL）manylinux wheel——编译解释器、运行解释器、Jupyter
  内核全部用 base env `/opt/conda/bin/python`（3.14.7 GIL enabled）。
  main cp314t 不参与本栈（Jupyter 服务仍由 main 跑，内核进程用 base）。
- **G4 最小源码跨平台适配（3 处，apps/ 内可改）**：agent-monetize 的
  `ffi_bridge.py`/`cli.py` 路径无关，但原生库默认名写死 `.dll`
  （config.py 默认、config.yaml、tests/test_ffi.py）。按 `sys.platform`
  在 `.dll/.so/.dylib` 间选择，**Windows 行为保持不变**。
- **G5 纯 Python wheel（.so 不入库）**：wheel 用 setuptools 打纯 Python
  包（pyproject 现状），原生 `.so` 是挂载源码树 `native/build/` 的运行时
  产物（与 ffi_bridge 从文件路径加载的现有设计一致）；不改编译系统、
  不引入 scikit-build。

## Non-Goals

- 不做 Nuitka 编译（agent-monetize 无此需求，setuptools 纯 Python）。
- 不编译 TVM/libtvm（tvm-ffi 运行时由 pip wheel 提供，区别于 xmnn-dev）。
- 不把 `.so` 打进 wheel、不改 pyproject 构建后端/不加 ext_modules。
- 不修改/删除 `native/build.ps1` 与 Windows 文档（Windows 路径保持）。
- 不做 GPU（tvm-ffi 此处只做 CPU 结构化计算）。
- 不动 onnx-quantized/xmnn-dev 既有 overlay 与 quant/xmnn 任务模块。
- 不创建 git commit。

## Background / Context（已调研事实，2026-09-14）

- 目标源码 `apps/agent-monetize`（主仓 apps/，非 submodule，可直接改）：
  py314（requires-python>=3.14）、setuptools src 布局、依赖仅 PyYAML；
  `native/score_opportunity.cc` 经 `#include <tvm/ffi/tvm_ffi.h>` 用
  tvm-ffi 注册 `score_opportunity`/`risk_adjusted_net` PackedFunc；
  `core/ffi_bridge.py` 接受外部传入的库路径、`ctypes.CDLL(path)` 加载、
  失败优雅降级到同公式纯 Python 参考实现；`native/build.ps1` 是唯一
  构建脚本（MSVC→.dll，链接 tvm_ffi.lib）；`native/build/` 已 gitignore。
- 可行性实测：`apache-tvm-ffi==0.1.13.post3` 在 rootless 基底 base env
  可装，wheel 含 `tvm_ffi/include/tvm/ffi/*.h`、
  `tvm_ffi/lib/libtvm_ffi.so`、`tvm_ffi/core.cpython-314-*.so`、
  cmake config；ABI tag `cp314-cp314`（GIL）。
- rootless 基底同 xmnn-dev spec：Ubuntu 26.04；base=/opt/conda 3.14.7
  GIL、main=3.14.7 cp314t；entrypoint tini→supervisord；无
  build-apt 工具链（需自装 clang/patchelf/gdb）；OCI 构建纪律、
  podman-compose 1.6、machine 无 systemd user bus（bridge 实证）全部沿用。
- 范式与规则真源：`client-overlay-scaffold` 技能（SKILL.md §6-12、
  templates/、references/delivery-checklist.md）、
  `overlays/xmnn-dev/`（形态 B 参考）、`tasks/xmnn.py`（invoke 范式）、
  `.agents/rules/xmnn-overlay.md`（同族红线）。

## Constra

- **Technical**: WSL2 podman-machine-default、podman 5.7.1 rootless、
  podman-compose 1.6.0；本地必须存在
  `localhost/jupyter-podman-rootless:latest`；clang（apt，Ubuntu 26.04）
  编译 score_opportunity.cc 链接 libtvm_ffi.so 成功并在 base python 经
  tvm_ffi.get_global_func 取到函数；apache-tvm-ffi pin 0.1.13.post3。
- **Business**: 产出在主仓库版本控制；agent-monetize 源码 3 处适配
  必须 Windows 等价不回归（.dll 路径保留）。
- **NFR-1 范式保真**：每条非平凡写法可指认技能/xmnn 范式或带注释实证。
- **NFR-2 对 agent-monetize 零非预期改动**：仅允许 3 处跨平台适配
  （config.py/config.yaml/test_ffi.py）+ 可选 Linux 文档；构建/打包/
  运行不改动其业务代码；不产生未跟踪残留（native/build 已 gitignore）。
  附：client 共享模块 `tasks/manage.py` 的工作树存在一处**非本栈引入**
  的既有未提交改动（`_load_env_overrides` 空占位键不注入 os.environ，
  属 SDK/quant 域通用改进，67812663d 提交未含、本栈 monetize.py 不依赖
  其空值过滤——SRC/workspace 均显式解析）；本栈**不还原**该通用改进，
  在此显式登记，并以 quant/xmnn/monetize 三命名空间 Windows 门禁 +
  包导入回归确认其不破坏既有行为。
- **NFR-3 rootless 安全/真实可执行**：无 privileged/socket/host 网络。
- **Dependencies**: PyPI（apache-tvm-ffi/PyYAML/build 等，经镜像源）、
  apt（clang/patchelf/gdb）。

## Functional Requirements

- **FR-1 Containerfile.agent-monetize**（薄叠加）：
  - ARG BASE_IMAGE（rootless latest）、PIP_MIRROR；FROM 单阶段。
  - Layer apt：clang、patchelf、gdb（--no-install-recommends，同层清 lists）。
  - Layer pip（显式 `/opt/conda/bin/python -m pip`）：`apache-tvm-ffi==0.1.13.post3`、
    PyYAML、build、wheel、setuptools（>=68 与 pyproject 对齐）、
    ipykernel、pytest、ruff；PIP_MIRROR 三段幂等。
  - COPY builder/ scripts/ smoke/；内核注册脚本 + 构建期守卫
    （root 与 devuser 双身份）；全 RUN `/bin/bash -lc`、不覆盖
    ENTRYPOINT/CMD/WORKDIR/HEALTHCHECK；LABEL org.specweave.*。
  - 守卫断言：base python=cp314 且 GIL enabled（Py_GIL_DISABLED=0）、
    clang 可执行、tvm_ffi 可 import、`tvm_ffi/lib/libtvm_ffi.so` 存在、
    `tvm_ffi/include/tvm/ffi/tvm_ffi.h` 存在、patchelf/gdb 可执行、
    builder 资产齐。
- **FR-2 builder 资产（/opt/monetize-builder/，自包含）**：
  - `scripts/lib/logging.sh`：vendor（复用 xmnn-dev 的精简日志库，禁跨
    overlay COPY）。
  - `scripts/build-native.sh`：环境变量化（SRC_ROOT 默认
    /workspace/agent-monetize）；从 base python 动态取 site-packages →
    tvm_ffi include/lib；`clang++ -std=c++17 -shared -fPIC -O2
    -I<tvm_ffi/include> score_opportunity.cc -L<tvm_ffi/lib>
    -ltvm_ffi -o native/build/score_opportunity.so`；产物
    patchelf `--set-rpath` 到 tvm_ffi 的 lib 目录（$ORIGIN 不适用——
    库在 site-packages，用绝对 rpath 指向容器内 tvm_ffi/lib，使
    ctypes.CDLL 能解析 libtvm_ffi.so 依赖）；缺 .cc/tvm_ffi 时 Exit 2
    中文提示；前置检查不静默。
  - `scripts/build-wheel.sh`：cd $SRC_ROOT →
    `/opt/conda/bin/python -m build --wheel --no-isolation --outdir
    $DIST_DIR`（默认 /workspace/dist）；缺 build 依赖给提示；不触碰
    native/build（.so 不要求存在，纯 Python wheel）。
- **FR-3 compose 栈**（脚手架模板渲染）：
  - name agent-monetize-dev、服务 monetize、image+内联 build；
    network_mode bridge（实证注释）；端口 `${MONETIZE_SSH_PORT:-2224}:22`
    、`${MONETIZE_JUPYTER_PORT:-8892}:8888`。
  - volumes：workspace 长语法 bind→/workspace；
    `${MONETIZE_SRC_PATH:-../../../../agent-monetize}` 长语法 bind
    →/workspace/agent-monetize（相对 compose 文件：
    overlay/agent-monetize-dev → 上四级到 apps/，再 agent-monetize；
    实施时以 podman-compose config 绝对化解析核对）。
  - 三必需（devices /dev/fuse、security_opt label=disable、cgroupns
    host 注释空操作）；environment 四凭证 + PYTHONPATH（src）+
    TVM_FFI 相关（LD_LIBRARY_PATH 含 tvm_ffi/lib，使 ctypes 加载 .so
    可解析；TVM_FFI 无需自定义 env，走默认 site-packages）；
    labels org.specweave.*；restart unless-stopped；无 command/healthcheck。
- **FR-4 .env.example（键集合=compose 插值键）**：镜像/容器名、端口、
  workspace、SRC_PATH、四凭证、PIP_MIRROR、注释态 BASE_IMAGE；优先级链注释。
- **FR-5 invoke 命名空间 `monetize.*`（8 任务）**：禁 import podman；
  双门禁（Windows Exit 1 + 缺二进制提示 [compose] extra）；daemon 预检；
  SRC_PATH 绝对 POSIX 解析 + 存在性硬校验；build（基底存在预检+PIP_MIRROR）
  /up（--skip-build）/down（--volumes）/ps/logs/smoke（双路径：运行→
  compose exec guards+native 冒烟；未运行→run --rm 仅工具链守卫）/
  build-native（compose exec build-native.sh）/wheel（exec build-wheel.sh）；
  __init__.py 注册 + configure + docstring 六命名空间。
- **FR-6 内核**：register-kernel.sh 写
  main share/jupyter/kernels/agent-monetize-dev/kernel.json，argv[0]=
  /opt/conda/bin/python，env.PYTHONPATH=/workspace/agent-monetize/src、
  env.LD_LIBRARY_PATH 含 tvm_ffi/lib；root+devuser kernelspec 可见。
- **FR-7 agent-monetize 源码 3 处跨平台适配（仅这些）**：
  - `src/agent_monetize/config.py`：FFI 配置 native_lib 默认按
    `sys.platform` 选择（.dll Windows / .so Linux / .dylib macOS），
    保留原字段语义；显式配置仍优先。
  - `config.yaml`：native_lib 键改为空/删除（让代码平台默认生效），
    或平台中立注释——实施择一并保证 CLI 在 Linux 取到 .so、Windows
    仍取 .dll。
  - `tests/test_ffi.py`：NATIVE_LIB 按平台扩展；其原生断言在 Linux
    指向 native/build/score_opportunity.so。
  - 适配必须最小、不改打分业务逻辑；Windows build.ps1 与 .dll 路径不动。
- **FR-8 smoke 双脚本**：
  - `smoke/_toolchain_guards.py`：构建期+run --rm 双路径；不依赖挂载；
    subprocess 列表参数断言（无 shell=True）；含引号逻辑固化文件内。
  - `smoke/smoke_native.py`：栈运行态；三挂载/源码关键路径可见；
    build-native 产物存在时 FfiBridge 加载 .so 断言 backend=native、
    t vm_ffi_available True、score_opportunity 固定输入结果与参考实现
    `_reference_score_opportunity` 同值（容差 1e-9）并在合理区间；
    .so 缺席时跳过原生段但挂载点断言仍执行（首次未编译是合法态，给
    build-native 提示，exit 0）。
- **FR-9 规则与路由登记**：新建
  `.agents/rules/monetize-overlay.md`（技能红线 + 本栈特有：apt clang
  轻工具链、单一 GIL ABI、tvm-ffi rpath、3 处源码适配边界、.so 不入
  wheel）；client AGENTS/.agents README/apps AGENTS 按技能 §9 登记 +
  C13 P0；README 双层。
- **FR-10 overlay README**：定位/镜像/服务/前置（基底+apache-tvm-ffi
  由镜像装）/invoke 八任务/裸 compose/开发调试（改源码即时生效、原生
  backend vs reference）/build-native/wheel 手册/参数表/与 xmnn-dev
  关系（轻量变体）/排障。

## Acceptance Criteria

### AC-1: 对 ai/外部目录零依赖与 builder 资产（rule）
- **Given**: overlay 目录
- **When**: grep 功能性文件 `external/chaos/ai|chaos/ai|--mount=type=bind|CHAOS_ROOT|/builder/`
- **Then**: 0 命中（README 事实表述除外）；builder 资产（logging.sh、
  build-native.sh、build-wheel.sh）、smoke 两脚本、register-kernel.sh
  齐全；编译脚本不残留 /builder 等移植路径。
- **Evidence**: grep + 目录树。

### AC-2: compose 静态正确性（rule）
- **Given**: machine 内
- **When**: `podman-compose -f <abs>/compose.yaml config`
- **Then**: 退出 0；1 服务 monetize；image+build(dockerfile) 共存；
  network_mode bridge；端口 2224/8892；bind 恰好 2（workspace、
  agent-monetize→/workspace/agent-monetize，均长语法 create_host_path）；
  devices/security_opt/cgroupns 各 1；environment 含 PYTHONPATH 与
  LD_LIBRARY_PATH；无 privileged、无 healthcheck、无 command。
- **Evidence**: config 输出摘要。

### AC-3: 镜像真实构建与工具链守卫（rule）
- **Given**: 本地 rootless 基底
- **When**: invoke/Podman build（PIP_MIRROR aliyun）
- **Then**: 退出 0；日志含 apache-tvm-ffi 安装、clang/patchelf/gdb、
  root 守卫 [OK]（base GIL、tvm_ffi+libtvm_ffi.so+头、clang）与
  devuser 复跑 [OK]、横幅；镜像 inspect Entrypoint tini 链、无
  Healthcheck。
- **Evidence**: 构建日志、images、inspect。

### AC-4: 单一 GIL ABI 事实（rule）
- **When**: 容器内分别跑 base/main python 的 sysconfig 断言 +
  tvm_ffi import
- **Then**: base 3.14.7 Py_GIL_DISABLED=0/_is_gil_enabled=True 且
  `import tvm_ffi` 成功；（main cp314t 不要求 tvm_ffi，仅记录双 ABI）。
- **Evidence**: exec 输出。

### AC-5: 栈 E2E 与内核/挂载（rule）
- **When**: up 后等待服务
- **Then**: 2224 TCP 可连、127.0.0.1:8892/lab 返回 200/302；
  /workspace/agent-monetize/src/agent_monetize 可见；kernelspec 含
  agent-monetize-dev（argv base python、env 含 PYTHONPATH+LD_LIBRARY_PATH），
  root/devuser 双可见。
- **Evidence**: 端口/curl/ls/kernel.json/kernelspec。

### AC-6: 原生编译真实闭环（rule，核心）
- **Given**: 栈运行
- **When**: `invoke monetize.build-native`（或 exec build-native.sh）
- **Then**: 退出 0；挂载源码树 `native/build/score_opportunity.so`
  生成；clang++ 命令含 -I tvm_ffi/include、-ltvm_ffi；patchelf rpath
  指向 tvm_ffi/lib。
- **Evidence**: 日志、ls -la .so、readelf -d。

### AC-7: 原生 backend 打分链路（rule，核心）
- **Given**: .so 已编译
- **When**: exec smoke_native.py（root 与 devuser）
- **Then**: FfiBridge backend=native、tvm_ffi_available=True、
  score_opportunity 固定输入经原生 PackedFunc 的结果与纯 Python 参考
  实现逐位/容差 1e-9 一致且在 [0,100]；smoke 退出 0。
- **Evidence**: exec 输出。

### AC-8: wheel 打包闭环与纯 Python 可用性（rule）
- **When**: `invoke monetize.wheel`
- **Then**: 宿主 workspace/dist 出现
  `agent_monetize-0.1.0-py3-none-any.whl`（纯 Python wheel）；
  临时 venv（--system-site-packages，剥离 PYTHONPATH 模拟无源码）安装后
  `import agent_monetize` 与 CLI/参考打分可用（reference backend），
  venv 结束清理。
- **Evidence**: ls/unzip、venv 验证。

### AC-9: 源码 3 处适配与 Windows 不回归（rule）
- **When**: 审查 config.py/config.yaml/test_ffi.py diff + 平台逻辑
- **Then**: 仅 3 文件改；Linux 解析 .so、Windows 仍解析 .dll（按
  sys.platform 分支，无删 .dll 路径）；build.ps1 未改；其余业务代码
  零改动；`pytest tests/test_ffi.py` 的平台无关用例（降级/reference）
  在容器内通过。
- **Evidence**: git diff、容器内 pytest。

### AC-10: 清理幂等（rule）
- **When**: down / 再 up-smoke-down / down --volumes
- **Then**: 项目容器/网络 down 后为零；bind 保留；wheel 保留；第二轮
  幂等；--volumes 删命名卷（如有）。
- **Evidence**: ps/network/volume 计数两轮。

### AC-11: invoke 集成与键集合（rule）
- **When**: invoke --list / Windows 原生跑 monetize.ps / diff 键
- **Then**: --list 8 任务；Windows 门禁 Exit 1 双路径指引；xmnn 类比
  无 import podman；overlay .env 与 root .env 段键集合一致。
- **Evidence**: --list、门禁输出、键 diff。

### AC-12: 零侵入与零回归（rule）
- **When**: 主仓 git status + onnx/xmnn/quant 状态 + tasks 包导入
- **Then**: 改动在白名单（overlay 新目录、monetize.py、__init__.py、
  client/.env.example/AGENTS/README/.agents README/规则、apps/AGENTS、
  agent-monetize 3 文件、spec）；onnx/xmnn overlay、quant.py/xmnn.py
  零改；quant/xmnn 命名空间门禁不回归。
- **Evidence**: git status 白名单对照。

### AC-13: 范式保真度（rubric）
- **Dimension**: 脚手架/xmnn 对齐度
- **Scale 1-5**：1=引特权/手写/回流/无依据偏离；3=≥2 处无注释偏离；
  5=除「apt clang 替代 conda LLVM、单一 GIL、纯 Python wheel、3 处
  源码适配」等本栈形态差异（均有 apache-tvm-ffi 事实与本 spec 出处）
  外与技能红线逐一对齐。
- **Pass Threshold**: >= 4。**Evidence**: reviewer 对照。

### AC-14: 产物原子性与文档一致性（rubric）
- **Scale 1-5**：1=矛盾/坏链/键不一致；3=1-2 过时；5=键集合/任务名/
  参数/端口三处一致、链接全通、每文件单一职责、脚手架 12 件套齐。
- **Pass Threshold**: >= 4。**Evidence**: 链接检查+交叉核对。

## Open Questions
- Q1（SRC 相对路径层级）：overlay 在
  overlays/agent-monetize-dev，源码在 apps/agent-monetize，相对路径
  推断为 `../../../../agent-monetize`（上 4 级到 apps/）；以
  podman-compose config 绝对化 + 真实挂载可见为准（实施第一步核对）。
- Q2（rpath 形式）：libtvm_ffi.so 在 site-packages，计划用绝对 rpath
  指向容器内 tvm_ffi/lib；若 patchelf 绝对 rpath 不被接受，回退
  compose 注入 LD_LIBRARY_PATH（已在 environment 预置，双保险）。
- Q3（wheel 是否纯 Python）：默认纯 Python（.so 不入库）；若验证发现
  分发场景必须含 .so，再另立 spec（本期不做）。
- Q4（wheel 版本）：agent-monetize 0.1.0 纯 Python wheel 标签预期
  py3-none-any（setuptools src 布局无扩展）；以实际产物名为准。
