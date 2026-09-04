# Tasks

> 本清单由《XMNN Wheel 从零构建打包流程》教程（`external/chaos/ai/.agents/docs/xmnn-whl-build-workflow.md`）细化而来，吸收 run-build.sh 三阶段、verify-wheel.sh 9 项验证标准、CMake 打包原理与 AST 兼容层机制。所有文件自包含，禁止引用 `external/chaos/xmtools` 路径。

## Phase 0：环境准备（前置门禁）
- [ ] Task 0: 准备构建环境
  - [ ] 0.1 启动 WSL Ubuntu-26.04，持久化启动 dockerd（`setsid nohup dockerd`，避免 VM 回收中断）
  - [ ] 0.2 配置国内 DNS（`nameserver 223.5.5.5 / 114.114.114.114`）
  - [ ] 0.3 确认/构建基础镜像 `devcontainer-base:chaos-ai-npu`（依赖链 base→conda→conda-llvm→onnx-pytorch→onnx-quantized→chaos-ai-npu）
  - [ ] 0.4 容器内验证工具链：LLVM 22 六包族（llvm/llvmdev/clang/clangxx/lld/llvm-tools=22.1）、cmake≥4.4、ninja≥1.13、patchelf、Python≥3.14
  - 验证：`docker run --rm devcontainer-base:chaos-ai-npu bash -c "python -c 'import sys; print(sys.version)' && cmake --version && ninja --version"`

## Phase 1：目录骨架与自包含配置
- [x] Task 1: 创建打包器目录骨架
  - [x] 1.1 在 `external/chaos/ai/` 下新建 `xmnn-whl-builder/` 目录
  - [x] 1.2 从零编写 `pyproject.toml`：scikit-build-core（PEP 517），name=xmnn, requires-python>=3.14，19 个运行时依赖（numpy/scipy/pandas/matplotlib/Pillow/onnx/protobuf/openpyxl/tabulate/rich/tqdm/tomlkit/decorator/attrs/psutil/cloudpickle/typing_extensions/pytest/telnetlib3），optional-dependencies 提供 dev/examples/torch/full
  - [x] 1.3 从零编写 `CMakeLists.txt`：安装 `_libs/`（libtvm.so + libLLVM + 依赖库，install_real_lib 处理符号链接）、patchelf RPATH `$ORIGIN`、Nuitka .so、`tvm/relay/std/*.rly`、`vta_hw/config/*.py/*.json`、`xmnn/autolibs|tools_cpp|fonts` 数据目录、bootstrap 文件
  - [x] 1.4 从零编写 `_xmnn_bootstrap.py` + `xmnn_bootstrap.pth`：AST 兼容层（NameConstant/Num/Str/Bytes/Index/ExtSlice Monkey-patch）+ TVM 环境引导（TVM_LIBRARY_PATH/LD_LIBRARY_PATH/ctypes 预加载 libtvm.so）
  - 验证：目录内文件齐全，且 `grep -r "xmtools"` 无引用 ✅ (grep 无命中)

## Phase 2：多阶段 Dockerfile（源码隔离）
- [x] Task 2: 编写多阶段 Dockerfile
  - [x] 2.1 BUILD 阶段 `FROM devcontainer-base:chaos-ai-npu`，用 BuildKit `RUN --mount=type=bind` 挂载 npu_tvm/npuusertools 构建源
  - [x] 2.2 构建 wheel：`python -m build --wheel --no-isolation --outdir dist`，传入 `cmake.define.*` 配置（NUITKA_OUTPUT_DIR/TVM_BUILD_DIR/TVM_ROOT_DIR/XMN_PYTHON_DIR/XMN_NUITKA_OUT/LLVM_LIB_DIR）
  - [x] 2.3 FINAL 阶段仅 COPY wheel + 安装 + 验证，不 COPY 源码（最终镜像无 `.py` 可读源码）
  - 验证：`grep` 确认 Dockerfile 无 `xmtools` 引用 ✅；`docker build` 成功 ⏳（需实际构建）；FINAL 层无源码文件 ✅

## Phase 3：构建脚本 build-wheel.sh（容器内打包）
- [x] Task 3: 编写 build-wheel.sh
  - [x] 3.1 环境准备：`PATH=/opt/conda/bin:$PATH`、`PIP_USER=0`、`LD_LIBRARY_PATH=$CONDA_DIR/lib`、`LLVM_CONFIG`、`CC/CXX=clang`
  - [x] 3.2 配置 pip 清华镜像（可选，继承基础镜像）
  - [x] 3.3 pyproject.toml 系统 cmake/ninja 补丁（移除 build-system.requires 中 cmake/ninja，强制用系统工具）
  - [x] 3.4 注入 AST PREAMBLE 到 vta/xmnn `__init__.py` → Nuitka 编译（`--nofollow-import-to=tvm,vta,torch,torchvision,onnx2pytorch`）→ 还原
  - [x] 3.5 `python -m build --wheel --no-isolation --outdir dist` + `cmake.define.*`
  - 验证：脚本在容器内可执行并产出 `dist/xmnn-*.whl` ⏳（需实际构建）

## Phase 4：验证脚本 verify-wheel.sh（9 项检查）
- [x] Task 4: 编写 verify-wheel.sh
  - [x] 4.1 `pip install --no-deps --force-reinstall` 后执行 9 项：import tvm（v0.19.0）/ vta / xmnn、`_libs` 目录（libtvm.so + libLLVM.so.22.1 + 依赖）、libtvm.so 动态加载（ctypes RTLD_GLOBAL）、`tvm.build(llvm)` 计算验证（A[i]*2==B[i], n=1024, rtol=1e-5）、`relay/std` 数据文件、`xmnn_bootstrap.pth` 引导、xmnn 数据目录（autolibs/tools_cpp/fonts）
  - [ ] 4.2 auditwheel show 检查 (auditwheel 未预装，作为可选增强)
  - 验证：脚本运行 9 项全部 PASS 且 `FAIL=0` ⏳（需实际构建）

## Phase 5：一键脚本 build-and-test.sh
- [x] Task 5: 编写 build-and-test.sh
  - [x] 5.1 构建镜像 → bind-mount 挂载源码 → 打包 wheel → 安装 → verify-wheel.sh
  - [x] 5.2 支持 `--verify-only`、`--no-build`、`--cn` 参数（参照 chaos/ai build.sh 风格）
  - 验证：脚本可一键跑通全流程，退出码 0 ⏳（需实际构建）

## Phase 6：验证与交付
- [ ] Task 6: 全流程验证与原子提交
  - [ ] 6.1 逐项核对 checklist.md 全部通过
  - [ ] 6.2 通过 atomic-commit-cmd 原子提交（单一职责，docs/feat 类型）

# Task Dependencies
- [Task 0] 无依赖（环境准备）
- [Task 1] 依赖 [Task 0]（需基础镜像与工具链就绪）
- [Task 2] 依赖 [Task 1]（需自包含配置）
- [Task 3] 依赖 [Task 2]（需 Dockerfile 可构建镜像）
- [Task 4] 依赖 [Task 3]（需 wheel 产物）
- [Task 5] 依赖 [Task 3, Task 4]（需构建与验证脚本）
- [Task 6] 依赖 [Task 5]（需一键脚本跑通）