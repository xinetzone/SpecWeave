# XMNN Nuitka Wheel 包构建系统 - 产品需求文档（v2）

## Overview
- **总结**：在 `external/chaos/xmtools/` 目录中构建一个基于 **scikit-build-core + CMake + Nuitka + Ninja** 工具链的 xmnn whl 打包系统，将 npuusertools/xmnn 及其依赖的 npu_tvm Python 模块（tvm、vta）打包为一个标准的可安装 wheel 包，不使用任何 setuptools 组件或 setup.py 文件。
- **目的**：
  - 使用 CMake 驱动的现代 Python 构建系统（scikit-build-core）替代传统 setuptools
  - 通过 Nuitka 将 TVM/VTA 的 Python 代码编译为原生扩展模块（.so），提供代码保护和性能提升
  - 将 TVM C++ 原生库（libtvm.so、libtvm_runtime.so 等）与编译后的 Python 模块整合到单一 wheel 包中
  - 确保 relay/std 和 vta_hw/config 等数据文件被正确包含
- **目标用户**：XMNN 部署和集成开发者

## Goals
- G1: 使用 scikit-build-core 作为唯一 build-backend，零 setuptools 依赖
- G2: 通过 CMakeLists.txt 的 install 规则精确控制 wheel 包内容
- G3: Nuitka 将 tvm 包编译为单个 `tvm.so` 扩展模块，并包含 relay/std 数据文件
- G4: Nuitka 将 vta 包编译为单个 `vta.so` 扩展模块，并包含 vta_hw/config 配置文件
- G5: 打包前通过 `inv config -f` 和 `inv make` 构建 TVM C++ 原生库
- G6: 生成的 whl 文件符合 PEP 427 规范，可通过 `pip install` 正确安装
- G7: 通过 invoke tasks.py 提供一键构建入口

## Non-Goals (Out of Scope)
- 不在 Windows 上构建原生库（构建环境为 WSL/Linux，脚本可在 Windows 编写）
- 不修改 npu_tvm 和 npuusertools/xmnn 的源代码
- 不发布到 PyPI
- 不支持交叉编译
- 不处理 GPU/CUDA 相关构建
- 不创建 setup.py 或 MANIFEST.in（已废弃）

## Background & Context
- npu_tvm 是 TVM 的 NPU 定制版本，位于 `external/chaos/npu_tvm/`
  - Python 包路径：`npu_tvm/python/tvm/`（需要 Nuitka 编译）
  - VTA Python 包路径：`npu_tvm/vta/python/vta/`（需要 Nuitka 编译）
  - 数据文件：`npu_tvm/python/tvm/relay/std/*.rly`、`npu_tvm/vta/vta_hw/config/*.json`
  - C++ 构建系统：使用 invoke 任务（tasks.py）驱动 CMake + Ninja
- xmnn 是用户工具包，位于 `external/chaos/npuusertools/xmnn/`
- 构建输出目录：`external/chaos/xmtools/`（即本项目根目录）
- 旧方案使用 setuptools + setup.py + MANIFEST.in，现废弃，改用纯 CMake 方案
- scikit-build-core 通过调用 `cmake --install` 将安装文件打包进 wheel

## Functional Requirements
- **FR-1**: pyproject.toml 声明 scikit-build-core 为唯一 build-backend
- **FR-2**: CMakeLists.txt 定义项目构建规则，包括：
  - 查找 Python 解释器和开发包
  - 自定义目标调用 Nuitka 编译 tvm 和 vta（可选前置）
  - install(DIRECTORY) 安装 xmnn 纯 Python 源码
  - install(FILES) 安装 Nuitka 编译产物（tvm.so、vta.so 及其 .pyi 文件）
  - install(FILES) 安装 TVM C++ 共享库（libtvm.so、libtvm_runtime.so 等）
  - install(DIRECTORY) 安装数据文件（relay/std、vta_hw/config）
- **FR-3**: invoke tasks.py 提供构建任务：
  - `init`/`check_deps`/`clean`：环境管理
  - `build-tvm`：执行 `inv config -f && inv make` 构建 C++ 库
  - `nuitka-tvm`：调用 Nuitka 编译 tvm 包
  - `nuitka-vta`：调用 Nuitka 编译 vta 包
  - `build-wheel`：调用 `python -m build --wheel` 生成 whl
  - `build-all`：一键构建完整流程
- **FR-4**: Nuitka 编译 tvm 时使用 `--include-data-dir` 包含 relay/std 目录
- **FR-5**: Nuitka 编译 vta 时使用 `--include-data-dir` 包含 vta_hw/config 目录
- **FR-6**: Nuitka 编译使用 `--module` 模式生成标准 Python 扩展模块
- **FR-7**: 解决 Nuitka 编译后 `__file__` 路径变化导致的数据文件/原生库加载问题

## Non-Functional Requirements
- **NFR-1（正确性）**: 生成的 whl 能在干净虚拟环境中 `pip install` 并 `import tvm`、`import vta`、`import xmnn` 成功
- **NFR-2（可重现性）**: 构建流程脚本化，一键命令可重复执行
- **NFR-3（兼容性）**: 兼容 Python 3.8+，manylinux 标准（Linux x86_64）
- **NFR-4（无 setuptools 残留）**: pyproject.toml、CMakeLists.txt、源码中均不出现 setuptools 引用，不生成 setup.py/MANIFEST.in

## Constraints
- **技术约束**:
  - 构建工具链：Nuitka、CMake ≥ 3.18、Ninja、GCC/G++（Linux）
  - 构建后端：scikit-build-core ≥ 0.5（不依赖 setuptools）
  - 构建环境：Linux/WSL（CMake/Ninja/Nuitka 编译需要 Unix 工具链）
  - Python 依赖：numpy、decorator、attrs、psutil、cloudpickle 等 TVM 运行时依赖
- **路径约束**:
  - xmtools 目录必须位于 `external/chaos/xmtools/`
  - 引用 npu_tvm 和 npuusertools 使用相对路径

## Assumptions
- 构建环境已安装 CMake ≥ 3.18、Ninja、Python 开发头文件、GCC/G++
- 构建环境已安装 Nuitka（`pip install nuitka`）
- 构建环境已安装 scikit-build-core 和 build（`pip install scikit-build-core build`）
- npu_tvm 作为 git submodule 已正确初始化
- npuusertools/xmnn 目录存在且包含有效的 Python 包结构
- Nuitka 编译需要的 Python 依赖（numpy 等）在构建环境中可用
- 直接 `pip install .` 在有网络和完整构建环境下也能工作（CMake 自定义目标可调用 Nuitka）

## Acceptance Criteria

### AC-1: 无 setuptools 依赖
- **Given**: xmtools 目录下的所有配置文件
- **When**: 检查 pyproject.toml、CMakeLists.txt 等文件
- **Then**: 不包含 setuptools 相关配置，没有 setup.py 和 MANIFEST.in 文件
- **Verification**: `programmatic`

### AC-2: CMakeLists.txt 正确配置
- **Given**: xmtools/CMakeLists.txt 文件
- **When**: cmake -S . -B build 配置成功
- **Then**: CMake 配置无错误，install 规则正确声明
- **Verification**: `programmatic`

### AC-3: TVM C++ 库构建
- **Given**: npu_tvm 已初始化且 CMake/Ninja/GCC 可用
- **When**: 执行 `inv build-tvm`
- **Then**: npu_tvm/build/ 目录生成 libtvm.so、libtvm_runtime.so 等共享库
- **Verification**: `programmatic`

### AC-4: Nuitka 编译 tvm 模块
- **Given**: TVM C++ 库已构建，Nuitka 已安装
- **When**: 执行 `inv nuitka-tvm`
- **Then**: build/nuitka/ 目录生成 tvm.so（或 tvm.pyd）、tvm.pyi、tvm.data/ 目录包含 relay/std
- **Verification**: `programmatic`

### AC-5: Nuitka 编译 vta 模块
- **Given**: TVM C++ 库已构建，Nuitka 已安装
- **When**: 执行 `inv nuitka-vta`
- **Then**: build/nuitka/ 目录生成 vta.so、vta.pyi、vta.data/ 目录包含 vta_hw/config
- **Verification**: `programmatic`

### AC-6: Wheel 生成
- **Given**: Nuitka 编译完成，scikit-build-core 和 build 已安装
- **When**: 执行 `inv build-wheel`
- **Then**: dist/ 目录生成 `xmnn-0.1.0-cp3X-cp3X-linux_x86_64.whl`
- **Verification**: `programmatic`

### AC-7: Wheel 可安装并导入
- **Given**: 已生成 whl 文件
- **When**: 在干净 Python 环境中执行 `pip install xmnn-*.whl` 并尝试 import
- **Then**: `import tvm`、`import vta`、`import xmnn` 均成功，tvm.relay.std 模块可访问
- **Verification**: `programmatic`

### AC-8: relay/std 数据文件可用
- **Given**: 已安装 whl 的环境
- **When**: 导入 tvm 并尝试访问 relay.std 相关功能
- **Then**: .rly 数据文件能被正确定位和加载
- **Verification**: `programmatic`

### AC-9: vta_hw/config 配置文件可用
- **Given**: 已安装 whl 的环境
- **When**: 导入 vta 并访问配置
- **Then**: .json 配置文件能被正确定位和加载
- **Verification**: `programmatic`

### AC-10: C++ 原生库可加载
- **Given**: 已安装 whl 的环境
- **When**: 导入 tvm 并调用 TVM 运行时函数
- **Then**: libtvm.so 和 libtvm_runtime.so 能被正确加载
- **Verification**: `programmatic`

### AC-11: 一键构建
- **Given**: 完整 Linux 构建环境
- **When**: 在 xmtools 目录执行 `inv build-all`
- **Then**: 整个流程自动完成（构建 TVM→Nuitka 编译→wheel 组装），最终在 dist/ 生成 whl
- **Verification**: `programmatic`

## Open Questions
- [ ] Nuitka 编译后 `__file__` 路径变化的具体解决方案：通过设置 `TVM_LIBRARY_PATH` 环境变量、rpath，还是包内置路径修复代码？
- [ ] 是否需要在 CMakeLists.txt 中直接调用 Nuitka（通过 add_custom_target）实现 `pip install .` 端到端可用，还是通过 invoke 预编译再 cmake install？
- [ ] vta_hw/config 的精确路径确认（相对于 vta Python 包的访问方式）
