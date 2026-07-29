# XMNN Nuitka + scikit-build-core 打包系统 - 产品需求文档

## Overview
- **Summary**: 完善并修复 `external/xmhub/xmnn/` 下的 XMNN 打包系统，使用 Nuitka 将 tvm、vta、xmnn 三个 Python 包编译为原生 `.so` 扩展模块，通过 CMake + scikit-build-core + ninja 工具链打包为符合现代 Python 标准（PEP 517/518）的 wheel 分发包。系统支持两阶段构建（C++ TVM 编译 → Nuitka Python 编译 → wheel 打包），产出可 pip 安装、跨 Linux 平台兼容的二进制包。
- **Purpose**: 解决 XMNN 工具链的源码保护（编译为 .so）和分发包标准化问题，使客户可通过 pip install 一键安装完整工具链（含 TVM/VTA/XMNN），无需暴露源码。
- **Target Users**: XMNN 工具链开发人员、部署工程师、终端客户（通过 pip 或 Docker 镜像安装使用）

## Goals
- 修复现有 `xmpack` 工具包中的 bug（`compile_nuitka()` 缺失 `cache_dir` 参数、参数传递断裂等）
- 确保 Nuitka `--module` 模式正确编译 tvm、vta、xmnn 三个包为独立的 `.so` 扩展
- 通过 CMake + scikit-build-core 将 Nuitka 产物 + TVM C++ 原生库 + 数据文件（autolibs/fonts/tools_cpp/vta_hw）组装为标准 wheel
- 使用 ninja 作为 CMake 生成器加速构建
- 确保 wheel 可通过 `pip install` 正确安装，安装后 `import tvm/vta/xmnn` 功能完整
- 支持 Docker 容器内构建（已有 Containerfile.build），同时支持本地直接构建
- 整合现有 docker-runtime 运行时镜像与 xmpack wheel 打包流程，统一为一套标准构建流水线
- Python 版本支持与现有环境一致（3.13+/3.14）

## Non-Goals (Out of Scope)
- Windows/macOS 原生 wheel 构建（当前目标平台为 Linux x86_64）
- PyPI 公开发布流程
- TVM C++ 代码本身的编译优化（仅消费已有的 CMake 构建产物）
- Cython 作为替代方案的实现
- PyArmor 混淆集成
- 对 npu_tvm 原始 CMake 构建系统的修改（仅消费其输出）

## Background & Context

### 现有代码资产
项目在 `external/xmhub/xmnn/` 下已有较完善的打包脚手架：
- **xmpack 工具库** (`src/xmpack/`)：包含 `nuitka_compiler.py`（Nuitka 编译脚本生成器）、`wheel.py`（wheel 打包脚本生成器）、`docker.py`（Docker 容器编排）、`models.py`（数据模型）
- **packaging 配置** (`packaging/`)：包含顶层 `pyproject.toml`（xmnn 包元数据和依赖）、`CMakeLists.txt`（三组件 install 规则）、`tvm/` 和 `vta/` 子目录各自的 CMakeLists.txt 及 TVM 启动引导文件
- **Invoke 任务** (`tasks.py`)：定义了 `inv build`（C++编译）、`inv nuitka-compile`（Nuitka编译）、`inv nuitka-package`（wheel打包）、`inv nuitka`（一键流水线）、`inv image-build`、`inv client`、`inv export` 等命令
- **构建镜像** (`Containerfile.build`)：基于 miniconda3:llvm22，预装 nuitka、scikit-build-core、ninja、build-essential 等
- **客户端镜像** (`client/Containerfile`)：安装 wheel 后的轻量运行时镜像

### 已发现的 Bug
1. `docker.py` 的 `compile_nuitka()` 函数签名缺少 `cache_dir` 参数，但函数体内使用了 `cache_dir=cache_dir` 传递给脚本生成器
2. `build_nuitka()` 调用 `compile_nuitka()` 时未传递 `cache_dir` 参数
3. `packaging/pyproject.toml` 中 `requires-python = ">=3.13"` 但运行时镜像使用 Python 3.14，Nuitka 编译产物带 cpython ABI tag，需确保一致性
4. `npuusertools/xmnn/` 下的 xmnn 源码是否是最新完整版本需确认（与打包配置期望的源码布局对比）
5. TVM C++ 构建目录路径 `build_llvm22` 是否为实际输出目录需验证

### 源码位置
- **tvm Python 源码**: `external/xmhub/npu_tvm/python/tvm/` + `external/xmhub/npu_tvm/python/vta/`
- **xmnn Python 源码**: `external/xmhub/npuusertools/xmnn/`（包含 adaround/、autolibs/、fonts/、tools_cpp/ 等）
- **TVM C++ 源码**: `external/xmhub/npu_tvm/src/`、`external/xmhub/npu_tvm/include/`、`external/xmhub/npu_tvm/vta/`
- **TVM C++ 构建产物**: `external/xmhub/npu_tvm/build_llvm22/`（需验证是否存在）或 `build/`

## Functional Requirements
- **FR-1**: 修复 xmpack 工具库中的所有已知 bug（参数缺失、路径错误等），确保 Docker 编排模块可正常工作
- **FR-2**: Nuitka 编译阶段能够正确编译 tvm、vta、xmnn 三个 Python 包为 `.so` 扩展模块，正确处理动态导入（通过 `--include-module`/`--include-package`）
- **FR-3**: Nuitka 编译使用 `--static-libpython=no` 确保兼容 conda Python 环境
- **FR-4**: CMake 配置（scikit-build-core 后端）正确安装：(a) tvm/vta/xmnn 的 .so 文件 (b) libtvm.so/libtvm_runtime.so/libvta.so 原生库 (c) tvm/_libs 目录 (d) xmnn/autolibs, xmnn/fonts, xmnn/tools_cpp 数据目录 (e) vta_hw/config (f) _tvm_nuitka_init.py 和 tvm_nuitka_init.pth 引导文件
- **FR-5**: scikit-build-core 配置使用 ninja 作为 CMake generator（通过 `cmake.args` 设置 `-G Ninja`）
- **FR-6**: wheel 打包后通过 `pip install` 安装到新环境中，`import tvm/vta/xmnn` 可正常工作，包括动态导入的 API 模块（compile_api, infer_api 等）
- **FR-7**: TVM 运行时通过 `_tvm_nuitka_init.py` + `.pth` 文件在 Python 启动时自动设置 `LD_LIBRARY_PATH`/`TVM_LIBRARY_PATH`，无需用户手动配置环境变量
- **FR-8**: 支持增量编译：Nuitka 编译缓存目录持久化（挂载到宿主机），未修改时跳过重新编译
- **FR-9**: inv 命令行任务（build/nuitka-compile/nuitka-package/nuitka/image-build/client/export）均可正确执行
- **FR-10**: wheel 包含正确的 `install_requires` 依赖声明（numpy, ml_dtypes, cloudpickle, psutil, pytest, attrs, typing_extensions, Pillow 等）
- **FR-11**: 构建产物可被 docker-runtime 运行时镜像消费（统一两套打包方案）

## Non-Functional Requirements
- **NFR-1**: 构建性能：Nuitka 编译支持并行（`--jobs=$(nproc)`），CMake 使用 ninja 并行构建
- **NFR-2**: 源码保护：wheel 中不包含任何 `.py` 源码文件（除必要的 `__init__.py` 和 bootstrap `.py` 文件），仅包含 `.so` 二进制扩展和数据文件
- **NFR-3**: 可重现性：相同源码和依赖版本应产生相同的 wheel（排除时间戳因素）
- **NFR-4**: 错误处理：构建失败时提供清晰的错误信息，指出失败阶段（C++构建/Nuitka编译/wheel打包）和原因
- **NFR-5**: wheel 大小合理：不包含调试符号、编译中间产物、头文件等非运行时必需内容
- **NFR-6**: 符合 PEP 517/518/427/600 标准：wheel 文件名包含正确的 platform tag（如 `cp313-cp313-linux_x86_64`）

## Constraints
- **Technical**: Python >=3.13, Nuitka >= 2.4, scikit-build-core >= 0.10, CMake >= 3.17, ninja, GCC (C++17), conda 环境
- **Platform**: Linux x86_64（Docker 容器内构建）
- **Dependencies**: TVM C++ 构建产物（libtvm.so, libtvm_runtime.so 等）必须在 Nuitka 编译阶段之前已生成
- **No new dependencies**: 不引入 PyArmor、Cython 等额外保护/编译工具，仅使用已选定的工具链

## Assumptions
- TVM C++ 使用 LLVM 22 编译，构建目录为 `npu_tvm/build_llvm22/`（如不存在则创建符号链接指向 `build/`）
- npuusertools/xmnn/ 包含完整的 xmnn Python 源码（含 adaround 量化模块、autolibs、fonts、tools_cpp）
- Docker 构建镜像 `nuitka-gcc-llvm` 可正常构建（基于 Containerfile.build）
- Nuitka 对 Python 3.13/3.14 有良好的 `--module` 模式支持
- 用户在 Linux/WSL2 环境中使用 Docker 执行构建

## Acceptance Criteria

### AC-1: xmpack bug 修复完成
- **Given**: 当前 xmpack 源码存在 `cache_dir` 参数缺失等 bug
- **When**: 修复所有已知 bug 后
- **Then**: `compile_nuitka()` 和 `build_nuitka()` 函数签名正确，参数传递链路完整，无 NameError/TypeError
- **Verification**: `programmatic` — Python 静态检查 + 函数调用测试

### AC-2: Nuitka 编译阶段成功产出 .so 文件
- **Given**: TVM C++ 构建已完成（libtvm.so 存在）
- **When**: 在构建容器内执行 Nuitka 编译（inv nuitka-compile 或等价命令）
- **Then**: `.temp/` 目录下生成 `tvm/tvm.cpython-*.so`、`vta/vta.cpython-*.so`、`xmnn/xmnn.cpython-*.so` 三个文件；每个 .so 文件大小合理（tvm > 10MB, xmnn > 1MB）
- **Verification**: `programmatic` — 文件存在性检查 + 大小检查

### AC-3: wheel 打包成功产出标准 wheel 文件
- **Given**: Nuitka 编译产物已生成
- **When**: 执行 wheel 打包（inv nuitka-package 或等价命令）
- **Then**: `packaging/dist/` 下生成 `xmnn-<version>-cp<pyver>-cp<pyver>-linux_x86_64.whl` 文件；wheel 解包后包含 tvm/vta/xmnn 的 .so 文件、libtvm*.so、_tvm_nuitka_init.py、tvm_nuitka_init.pth、xmnn 数据目录
- **Verification**: `programmatic` — wheel 文件存在 + zipfile 内容检查

### AC-4: wheel 可 pip install 并正确导入
- **Given**: wheel 文件已生成
- **When**: 在干净的 Python 环境中 `pip install xmnn-*.whl`
- **Then**: `python -c "import tvm; import vta; import xmnn; from xmnn import compile_api, infer_api, accuracy_api"` 全部成功；tvm 能找到 libtvm.so（通过 .pth 自动引导）
- **Verification**: `programmatic` — Docker 容器内干净环境安装 + 导入测试

### AC-5: scikit-build-core 使用 ninja 构建
- **Given**: 打包配置正确
- **When**: 执行 pip wheel 构建
- **Then**: CMake 构建日志显示使用 Ninja generator（`-G Ninja`）；构建并行执行
- **Verification**: `programmatic` — 构建日志检查

### AC-6: 一键流水线完整运行
- **Given**: Docker 环境可用，源码完整
- **When**: 执行 `inv nuitka`（一键构建+编译+打包）
- **Then**: 全流程无报错，最终产出可安装的 wheel 文件
- **Verification**: `programmatic` — 命令退出码为 0 + wheel 存在

### AC-7: 源码保护验证
- **Given**: wheel 已安装
- **When**: 检查 site-packages 中的安装内容
- **Then**: 不包含 tvm/vta/xmnn 的 `.py` 源码文件（_tvm_nuitka_init.py 和 tvm_nuitka_init.pth 除外）
- **Verification**: `programmatic` — 文件扫描检查

### AC-8: 客户端 Docker 镜像构建成功
- **Given**: wheel 已生成
- **When**: 执行 `inv client`（构建客户端运行时镜像）
- **Then**: Docker 镜像构建成功，容器内可正常 import tvm/vta/xmnn 并运行基本功能
- **Verification**: `programmatic` — 镜像构建 + 容器内导入测试

## Open Questions
- [ ] TVM C++ 构建目录实际名称是 `build` 还是 `build_llvm22`？是否需要通过 CMake preset 统一？
- [ ] Python 版本锁定为 3.13 还是 3.14？（影响 wheel ABI tag 和 Nuitka 兼容性）
- [ ] npuusertools/xmnn 是否为完整的 xmnn 源码？还是需要从其他位置复制/链接？
- [ ] docker-runtime（npuusertools/docker-runtime/Dockerfile）与 xmpack client 镜像的关系——是否需要统一为一套方案？
