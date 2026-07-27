# npu-ffi VTA FFI绑定库 - Product Requirement Document

## Overview
- **Summary**: 在 `projects/xuanspace/libs/npu-ffi` 下创建一个基于 tvm-ffi 的 VTA（Versatile Tensor Accelerator）运行时 FFI 绑定库，为 NPU 深度学习加速器提供类型安全的 Python/C++ 跨语言调用接口。项目采用 CMake + Ninja + scikit-build-core 构建系统，支持 Python 3.14+、Conda 包管理，依赖 protobuf 7.0.0+。
- **Purpose**: 替代原始 C 风格的 ctypes/cffi 绑定，利用 tvm-ffi 提供的类型化函数注册、容器支持、内存管理机制，构建可维护、可测试、类型安全的 VTA Python API 层。该库作为 NPU 软件栈的基础组件，向上支撑编译器、runtime、工具链等上层模块。
- **Target Users**: NPU 编译器开发者、VTA runtime 集成开发者、深度学习加速器研究人员、需要在 Python 中直接调用 VTA 指令的工程师。

## Goals
- 使用 tvm-ffi 机制注册所有 VTA runtime C API 函数
- 构建符合 xuanspace 规范的 C++ 原生扩展库（CMake + Ninja + scikit-build-core）
- 支持 Python 3.14 及以上版本（含 free-threaded 3.14t）
- 提供完整的 Conda 构建和安装流程
- 集成 protobuf 7.0.0+ 用于 VTA 配置序列化/反序列化
- 模块化设计：核心 FFI 层与 VTA 特定绑定分离，预留扩展其他 NPU 后端能力
- 提供 stub 实现模式，支持无硬件环境下的开发测试
- 包含基础单元测试和使用文档

## Non-Goals (Out of Scope)
- 不重新实现 VTA runtime 硬件驱动逻辑（链接已有的 VTA driver 实现）
- 不实现完整的 VTA 编译器栈（仅提供 runtime FFI 绑定）
- 不提供 FPGA 比特流生成或硬件仿真功能
- 不绑定 TVM Relay/Relax 编译器部分（只做 runtime FFI）
- 不包含 PyTorch/TensorFlow 等框架集成（上层框架集成在后续项目）
- 不提供 GUI 或可视化工具

## Background & Context
- **现有参考**: `external/chaos/npu_tvm/vta/` 包含原始 VTA runtime 实现（C API 定义在 `include/runtime/runtime.h`）
- **tvm-ffi 依赖**: `projects/xuanspace/vendor/tvm-ffi/` 提供类型安全的 FFI 机制，已被 tvm-book 项目验证可行
- **示例实现**: `projects/xuanspace/libs/tvm-book/tests/vta_ffi/` 包含一个简单的 stub 实现原型，展示了 `TVM_FFI_DLL_EXPORT_TYPED_FUNC` 的用法
- **项目规范**: xuanspace 要求所有 `libs/` 下原生扩展使用 CMake+Ninja+scikit-build-core，requires-python>=3.13（本项目提升到 3.14+）
- **原型位置**: 用户指定目标目录 `projects/xuanspace/libs/npu-ffi`（当前不存在，需新建）

## Functional Requirements
- **FR-1**: VTA Runtime C API 完整绑定
  - 绑定 `VTABufferAlloc`/`VTABufferFree`/`VTABufferCopy`/`VTABufferCPUPtr` 缓冲区管理函数
  - 绑定 `VTATLSCommandHandle`/`VTARuntimeShutdown`/`VTASetDebugMode` 命令句柄与生命周期函数
  - 绑定 `VTALoadBuffer2D`/`VTAStoreBuffer2D` 二维数据传输函数
  - 绑定 `VTAUopPush`/`VTAUopLoopBegin`/`VTAUopLoopEnd` 微操作指令函数
  - 绑定 `VTAPushGEMMOp`/`VTAPushALUOp` GEMM/ALU 内核推送函数
  - 绑定 `VTADepPush`/`VTADepPop` 依赖管理函数
  - 绑定 `VTASynchronize`/`VTAWriteBarrier`/`VTAReadBarrier` 同步与屏障函数
  - 绑定 `VTAPrepareCallFunc` 扩展调用准备函数
  - 所有函数通过 tvm-ffi 的 `TVM_FFI_DLL_EXPORT_TYPED_FUNC` 或 `TVM_FFI_REGISTER_GLOBAL` 导出

- **FR-2**: 类型安全的 C++ 接口层
  - 对原始 `void*` 命令句柄封装为类型安全的 `CommandHandle` 类
  - 对原始 `void*` 缓冲区指针封装为 `Buffer` 类，利用 tvm::ffi 内存管理
  - 支持 `ffi::TensorView` 类型用于张量数据传递
  - 错误码转换为 tvm::ffi 异常类型

- **FR-3**: Python 高层 API
  - Python 包 `npu_ffi.vta` 提供所有 VTA 函数的 Pythonic 封装
  - 自动类型转换（Python int ↔ C uint32_t/int64_t，Python bytes ↔ 缓冲区）
  - 上下文管理器支持（CommandHandle 自动生命周期管理）
  - 调试标志位的 Python 枚举封装

- **FR-4**: 构建系统
  - CMake 配置正确引用 vendor/tvm-ffi 的头文件和库
  - scikit-build-core 配置生成可安装 wheel
  - 支持 editable 安装（`pip install -e .`）
  - 支持 Release/Debug 构建类型切换
  - Windows/Linux/macOS 跨平台兼容（MSVC/GCC/Clang）

- **FR-5**: Conda 支持
  - 提供 conda recipe（meta.yaml）
  - 提供构建脚本（build.sh/bld.bat）
  - Conda 环境包含 LLVM、cmake、ninja、Python 3.14、protobuf 等依赖
  - 支持北外镜像源配置（国内环境）

- **FR-6**: Protobuf 集成
  - 提供 VTA 硬件配置（vta_config.json 等价物）的 protobuf schema
  - protobuf 版本 >= 7.0.0
  - 支持配置序列化/反序列化
  - Python 绑定生成（通过 betterproto 或官方 protobuf 编译器）

- **FR-7**: Stub/模拟模式
  - 提供不依赖真实 VTA 硬件的 stub 实现（类似现有 NotLinked() 模式但可用）
  - Stub 模式下记录函数调用，用于单元测试
  - 通过 CMake 选项 `NPU_FFI_VTA_USE_STUB` 切换 stub/真实链接模式

- **FR-8**: 测试框架
  - C++ 层单元测试（使用 tvm-ffi 自带测试框架或 GTest）
  - Python 层 pytest 测试
  - 测试覆盖核心 API 的导入、调用、错误处理
  - Stub 模式下的回归测试

## Non-Functional Requirements
- **NFR-1**: 构建性能
  - 增量构建时间 < 30秒（无改动时秒级返回）
  - 完整构建时间 < 5分钟（Release 模式，8核机器）
  - Ninja 构建系统并行编译
- **NFR-2**: 兼容性
  - Python 版本：3.14、3.14t（free-threaded）
  - 编译器：GCC 13+、Clang 18+、MSVC 2022+
  - C++ 标准：C++17（与 tvm-ffi 一致）
  - CMake 版本：>= 3.26
- **NFR-3**: 代码质量
  - 遵循现有 tvm-ffi 代码风格
  - 所有公共 API 有文档注释（doxygen 风格）
  - 无编译器警告（Warning level 4 on MSVC, -Wall -Wextra on GCC/Clang）
- **NFR-4**: 可维护性
  - 模块化目录结构，每个模块职责单一
  - 函数注册集中管理，新增 API 修改点单一
  - 头文件自包含，不依赖包含顺序

## Constraints
- **Technical**:
  - 必须使用 tvm-ffi 作为 FFI 机制，禁止使用 pybind11/cython 作为主绑定方式（可作为内部实现细节但不暴露）
  - 构建系统必须是 CMake + Ninja + scikit-build-core（禁止 setuptools）
  - 依赖路径：tvm-ffi 头文件在 `projects/xuanspace/vendor/tvm-ffi/include`，容器在 `include/tvm/ffi/container/`，内存在 `include/tvm/ffi/memory.h`
  - Python 版本严格 >= 3.14
  - protobuf >= 7.0.0
- **Business**:
  - 项目位于 xuanspace libs 区域，遵循 xuanspace 子项目规范
  - vendor/tvm-ffi 是第三方依赖，禁止本地修改（只能通过 CMake 链接）
  - external/chaos/npu_tvm/vta 是参考实现，禁止直接修改（通过头文件引用或链接其库）
- **Dependencies**:
  - 核心依赖：tvm-ffi（vendor 子模块）、Python 3.14+ Development headers
  - 构建依赖：cmake >= 3.26、ninja >= 1.11、scikit-build-core >= 0.10
  - 可选依赖：protobuf >= 7.0.0（配置序列化）、Doxygen（文档生成）

## Assumptions
- tvm-ffi 已正确初始化为 git submodule（路径 `projects/xuanspace/vendor/tvm-ffi` 存在且完整）
- 用户环境中已安装 Conda（用于 Conda 构建流程验证，但 pip 构建不需要 Conda）
- 开发环境有可用的 C++17 编译器（MSVC 2022+/GCC 13+/Clang 18+）
- VTA runtime 的真实硬件驱动库（libvta_runtime.so/dll）在链接真实模式时由外部提供（本项目不构建 driver）
- `projects/xuanspace/libs/npu-ffi` 目录当前不存在，是全新创建

## Acceptance Criteria

### AC-1: 项目骨架创建完成
- **Given**: 空的 `projects/xuanspace/libs/npu-ffi` 目录
- **When**: 完成项目初始化
- **Then**: 包含正确的目录结构（src/、python/、include/、cmake/、tests/、conda/），pyproject.toml 和 CMakeLists.txt 存在且语法正确
- **Verification**: `programmatic`
- **Notes**: 使用 `xs new --type native` 类似的模板结构，但针对 npu-ffi 定制

### AC-2: 可成功构建并安装 wheel
- **Given**: 正确配置的 CMake 和 pyproject.toml
- **When**: 执行 `pip install -e .` 或 `pip wheel .`
- **Then**: 编译成功无错误，生成 `npu_ffi` Python 包，可在 Python 中 `import npu_ffi.vta`
- **Verification**: `programmatic`

### AC-3: Stub 模式下核心 API 可调用
- **Given**: Stub 模式构建（默认）
- **When**: 在 Python 中调用 `npu_ffi.vta.command_handle()`、`buffer_alloc()`、`uop_push()` 等函数
- **Then**: 函数调用不崩溃，返回合理的 stub 值（如句柄返回0，分配返回非空指针）
- **Verification**: `programmatic`

### AC-4: tvm-ffi 头文件正确引用
- **Given**: C++ 源文件
- **When**: 编译包含 `#include <tvm/ffi/function.h>`、`#include <tvm/ffi/container/tensor.h>`、`#include <tvm/ffi/memory.h>`
- **Then**: 编译成功，找不到头文件错误不存在
- **Verification**: `programmatic`

### AC-5: Python 3.14 兼容性验证
- **Given**: Python 3.14 环境
- **When**: 安装 wheel 并运行测试
- **Then**: 所有测试通过，无版本相关错误
- **Verification**: `programmatic`

### AC-6: Conda 构建流程完整
- **Given**: Conda 环境配置文件
- **When**: 执行 conda build 或使用提供的环境创建脚本
- **Then**: Conda 环境可创建，包可通过 Conda 安装
- **Verification**: `programmatic`

### AC-7: 类型安全的句柄封装
- **Given**: Python 层 API
- **When**: 向需要 CommandHandle 的函数传递错误类型（如整数、字符串）
- **Then**: 抛出明确的类型错误，而非段错误或未定义行为
- **Verification**: `programmatic`

### AC-8: 所有 VTA C API 函数已注册
- **Given**: runtime.h 中声明的所有 TVM_DLL 函数
- **When**: 检查 Python `npu_ffi.vta` 模块
- **Then**: 每个 C API 函数都有对应的 Python 绑定
- **Verification**: `programmatic`（通过函数列表比对）

### AC-9: 单元测试通过
- **Given**: 完整构建（stub 模式）
- **When**: 执行 `pytest tests/`
- **Then**: 所有测试用例通过，覆盖率 > 70%
- **Verification**: `programmatic`

### AC-10: 文档完整
- **Given**: README.md 和代码注释
- **When**: 新开发者阅读文档
- **Then**: 能够理解项目结构、成功构建、运行示例代码
- **Verification**: `human-judgment`

## Open Questions
- [ ] VTA 配置 protobuf schema 是否需要完全复现 vta_config.py 的所有字段？还是先提供最小必要子集？
- [ ] 真实硬件链接模式（非 stub）需要链接的具体库名和路径是什么？是否需要提供 FindVTA.cmake 模块？
- [ ] 是否需要在第一版中包含 VTA v2/v3/v4 多版本支持，还是先只支持默认版本？
- [ ] Conda 构建是产出 conda package 还是只提供 environment.yml 开发环境？
- [ ] protobuf Python 绑定使用官方 google.protobuf 还是 betterproto？
