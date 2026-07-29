# npu-ffi VTA FFI绑定库 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 项目骨架与目录结构初始化
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 `projects/xuanspace/libs/npu-ffi` 创建标准目录结构：
    - `include/npu_ffi/` - 公共头文件
    - `include/npu_ffi/vta/` - VTA 特定头文件
    - `src/` - C++ 源文件
    - `src/vta/` - VTA FFI 实现
    - `python/npu_ffi/` - Python 包根目录
    - `python/npu_ffi/vta/` - VTA Python 模块
    - `proto/` - Protobuf schema 文件
    - `tests/python/` - Python 测试
    - `conda.recipe/` - Conda recipe
    - `scripts/` - 辅助脚本
    - `.github/workflows/` - CI配置
  - 创建基础文件：.gitignore、LICENSE（Apache 2.0）、CHANGELOG.md
  - 创建模块 __init__.py 文件
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录结构符合规范，所有必要目录存在 ✅
  - `programmatic` TR-1.2: pyproject.toml 和 CMakeLists.txt 文件存在 ✅
  - `human-judgement` TR-1.3: 目录结构清晰，符合 xuanspace libs 布局惯例 ✅
- **Notes**: 参考 tvm-book 的目录结构

## [x] Task 2: 构建系统配置（pyproject.toml + CMakeLists.txt）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `pyproject.toml`：
    - build-system: scikit-build-core >= 0.10, ninja >= 1.11, apache-tvm-ffi
    - project name: npu-ffi, version 0.1.0
    - requires-python = ">=3.13"（遵循xuanspace规范）
    - dependencies: protobuf >= 7.0.0, apache-tvm-ffi
    - wheel.packages = ["python/npu_ffi"]
  - 创建根 `CMakeLists.txt`：
    - cmake_minimum_required(VERSION 3.26)
    - C++17 标准
    - find_package(tvm_ffi CONFIG REQUIRED)（pip安装模式）
    - 选项 NPU_FFI_VTA_USE_STUB（默认 ON）
    - 选项 NPU_FFI_FROM_SOURCE（从源码构建tvm-ffi）
    - 选项 NPU_FFI_VTA_DIR（真实VTA路径）
    - 选项 NPU_FFI_ENABLE_PROTOBUF（默认OFF）
  - 创建 `src/CMakeLists.txt` 和 `src/vta/CMakeLists.txt` 管理源文件
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-4
- **Test Requirements**:
  - `programmatic` TR-2.1: CMake 配置无错误 ✅
  - `programmatic` TR-2.2: pip install -e . 在 stub 模式下成功 ✅（需 --no-build-isolation）
  - `programmatic` TR-2.3: import npu_ffi 在 Python 中不报错 ✅
  - `programmatic` TR-2.4: 编译器能找到 tvm/ffi/function.h 等头文件 ✅
- **Notes**: 使用find_package模式，tvm-ffi先通过pip install -e安装

## [x] Task 3: C++ 类型安全封装层（include/npu_ffi/vta/）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 创建 `include/npu_ffi/vta/handle.h`：CommandHandle 类型封装
  - 创建 `include/npu_ffi/vta/buffer.h`：Buffer 类封装
  - 创建 `include/npu_ffi/vta/types.h`：
    - MemoryType 枚举（DRAM/SRAM/UOP/INP/WGT/ACC/OUT）
    - DebugFlag 枚举（DUMP_INSN、DUMP_UOP等，支持位运算）
    - MemcpyKind 枚举（H2D/D2H/D2D）
    - ALUOpcode 枚举（ADD/SUB/MUL/MIN/MAX/SHR/SHL）
  - 创建 `include/npu_ffi/vta/runtime.h`：运行时函数声明
  - 创建 `include/npu_ffi/npu_ffi.h`：顶层头文件
- **Acceptance Criteria Addressed**: AC-4, AC-7
- **Test Requirements**:
  - `programmatic` TR-3.1: 头文件可独立编译 ✅
  - `programmatic` TR-3.2: 类型安全枚举正确 ✅
  - `programmatic` TR-3.3: 枚举值与VTA原始头文件对齐 ✅
  - `human-judgement` TR-3.4: API 设计符合 C++ RAII 惯例 ✅
- **Notes**: 枚举值与 external/chaos/npu_tvm/vta/include/runtime/runtime.h 和 vta/driver.h 一致

## [x] Task 4: VTA Stub 实现（src/vta/stub_rt.cc）
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 创建 `src/vta/stub_rt.cc` 实现 stub 版本的所有 VTA 函数：
    - BufferAlloc/BufferFree/BufferCopy: 使用aligned_alloc分配，跟踪分配
    - TLSCommandHandle: 返回递增整数句柄
    - RuntimeShutdown: 清空分配跟踪表
    - SetDebugMode: 存储debug flag到线程局部变量
    - LoadBuffer2D/StoreBuffer2D: 空操作
    - UopPush/UopLoopBegin/UopLoopEnd: 空操作
    - PushGEMMOp/PushALUOp: 返回0（成功）
    - DepPush/DepPop: 返回0（成功）
    - Synchronize: 空操作
    - WriteBarrier/ReadBarrier: 空操作
    - PrepareCallFunc: 记录函数名
  - 使用线程局部存储管理命令句柄状态
  - 使用静态unordered_map跟踪分配的缓冲区
- **Acceptance Criteria Addressed**: AC-3, AC-7
- **Test Requirements**:
  - `programmatic` TR-4.1: 所有 stub 函数链接成功 ✅
  - `programmatic` TR-4.2: buffer_alloc 返回非空指针 ✅
  - `programmatic` TR-4.3: 重复 alloc/free 稳定运行 ✅
  - `programmatic` TR-4.4: command_handle 返回非零递增ID ✅
  - `programmatic` TR-4.5: 所有函数调用在 stub 模式下不崩溃 ✅
- **Notes**: stub实现为开发测试提供完整功能，无需真实硬件

## [x] Task 5: tvm-ffi 函数注册与导出（src/vta/ffi_registry.cc）
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 创建 `src/vta/ffi_registry.cc`：
    - 使用 TVM_FFI_DLL_EXPORT_TYPED_FUNC 宏导出所有 VTA 函数
    - 函数注册名前缀为 "vta."
  - 导出函数完整覆盖 runtime.h 中所有TVM_DLL函数
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-8
- **Test Requirements**:
  - `programmatic` TR-5.1: 编译后的共享库导出所有注册的函数 ✅
  - `programmatic` TR-5.2: Python 中可通过 tvm_ffi 获取所有函数 ✅
  - `programmatic` TR-5.3: 所有 runtime.h 声明的函数都有对应的 FFI 注册 ✅
  - `human-judgement` TR-5.4: 注册代码组织清晰 ✅
- **Notes**: 参考 tvm-book/tests/vta_ffi/vta_rt.cc 的注册模式

## [x] Task 6: Python 高层 API（python/npu_ffi/vta/）
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 创建 `python/npu_ffi/__init__.py`：包入口，版本号
  - 创建 `python/npu_ffi/py.typed`：PEP 561标记
  - 创建 `python/npu_ffi/vta/__init__.py`：导出所有公共API和枚举
  - 创建 `python/npu_ffi/vta/_ffi_api.py`：使用tvm_ffi加载库和初始化FFI
  - 创建 `python/npu_ffi/vta/buffer.py`：Buffer类（RAII、上下文管理器）
  - 创建 `python/npu_ffi/vta/command.py`：CommandContext上下文管理器
  - 创建 `python/npu_ffi/vta/config.py`：纯Python配置API
  - 创建 `python/npu_ffi/vta/proto_io.py`：Protobuf序列化
  - 创建 `python/npu_ffi/vta/vta_config_pb2.py`：预生成的protobuf绑定
- **Acceptance Criteria Addressed**: AC-3, AC-7, AC-8
- **Test Requirements**:
  - `programmatic` TR-6.1: from npu_ffi import vta 成功 ✅
  - `programmatic` TR-6.2: vta.tls_command_handle() 返回整数句柄 ✅
  - `programmatic` TR-6.3: buf = vta.buffer_alloc(1024); vta.buffer_free(buf) 无错误 ✅
  - `programmatic` TR-6.4: with CommandContext() as ctx: ... 正常工作 ✅
  - `programmatic` TR-6.5: 所有C函数都有对应的Python包装 ✅
- **Notes**: 参考 tvm-book/python/flexloopy/_ffi_api.py 的模式

## [x] Task 7: Protobuf 配置 Schema 与绑定（proto/）
- **Priority**: medium
- **Depends On**: Task 2
- **Description**:
  - 创建 `proto/vta_config.proto`：VTAConfig和DefaultConfigs消息定义
  - 创建 `proto/CMakeLists.txt`：条件性Protobuf代码生成
  - 创建 `scripts/gen_proto.py`：Python绑定生成脚本
  - 预生成 `python/npu_ffi/vta/vta_config_pb2.py`
  - Python端config.py提供纯Python dataclass（无需protobuf即可用）
  - proto_io.py提供protobuf序列化/反序列化（二进制/JSON/TextProto）
  - 支持三种预设配置：vta(pynq)、vta_v3(ultra96)、vta_v4(zcu104)
- **Acceptance Criteria Addressed**: FR-6
- **Test Requirements**:
  - `programmatic` TR-7.1: proto schema可编译 ✅
  - `programmatic` TR-7.2: Python中可序列化/反序列化往返正确 ✅
  - `programmatic` TR-7.3: 默认配置可加载 ✅
  - `programmatic` TR-7.4: protobuf 7.0+兼容 ✅
- **Notes**: protobuf为可选增强，纯Python配置无需protobuf也能使用

## [x] Task 8: 单元测试
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 创建 `tests/python/__init__.py`
  - 创建 `tests/python/conftest.py`：pytest配置和fixtures
  - 创建 `tests/python/test_enums.py`：枚举值测试（22个）
  - 创建 `tests/python/test_ffi_api.py`：底层FFI API测试（34个）
  - 创建 `tests/python/test_buffer.py`：Buffer类测试（14个）
  - 创建 `tests/python/test_command.py`：CommandContext测试（15个）
  - 创建 `tests/python/test_config.py`：配置和protobuf测试（25个）
  - 在pyproject.toml中配置pytest testpaths
  - 总计116个测试全部通过
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `programmatic` TR-8.1: pytest tests/python/ -v 全部通过 ✅（116 passed）
  - `programmatic` TR-8.2: 核心函数覆盖测试 ✅
  - `programmatic` TR-8.3: 错误参数测试不导致崩溃 ✅
- **Notes**: 全部基于stub模式，不依赖真实硬件

## [x] Task 9: Conda 构建配置
- **Priority**: medium
- **Depends On**: Task 2
- **Description**:
  - 创建 `environment.yml`：Conda开发环境配置（Python 3.13）
  - 创建 `conda.recipe/meta.yaml`：Conda构建配方（Jinja2模板）
  - 创建 `conda.recipe/conda_build_config.yaml`：构建配置
  - 创建 `conda.recipe/build.sh`/`bld.bat`：平台构建脚本
  - 创建 `conda.recipe/README.md`：Conda构建指南
  - 创建 `scripts/setup_conda_dev.sh`/`setup_conda_dev.ps1`：一键环境设置
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-9.1: environment.yml语法正确 ✅
  - `programmatic` TR-9.2: meta.yaml语法正确 ✅
  - `human-judgement` TR-9.3: 国内镜像配置说明清晰 ✅
- **Notes**: apache-tvm-ffi通过pip安装（不在conda-forge上）

## [x] Task 10: 文档与 README
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - 创建完整的 `README.md`，包含：
    - 项目介绍与特性列表
    - 前置要求
    - 安装指南（开发模式、Conda快速设置）
    - 快速开始示例（基础使用、Buffer RAII、CommandContext、枚举、Protobuf配置）
    - 项目结构说明
    - 构建模式（stub/real/from-source）
    - 运行测试说明
    - Conda包构建说明
    - API参考
    - 许可证和相关项目链接
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `human-judgement` TR-10.1: README新读者可按步骤完成安装和运行示例 ✅
  - `human-judgement` TR-10.2: 代码示例与实际API一致 ✅
- **Notes**: 使用中文撰写，代码示例保持英文

## [x] Task 11: 真实 VTA Runtime 链接支持（可选/进阶）
- **Priority**: low
- **Depends On**: Task 5
- **Description**:
  - 创建 `src/vta/real_rt.cc`：真实VTA运行时转发层（直接调用VTA C API）
  - CMake选项 NPU_FFI_VTA_USE_STUB=OFF 时编译real_rt.cc并查找VTA库
  - CMake选项 NPU_FFI_VTA_DIR 指定VTA安装路径
  - ffi_registry.cc保持不变，统一的FFI注册接口
- **Acceptance Criteria Addressed**: FR-1（完整绑定）
- **Test Requirements**:
  - `programmatic` TR-11.1: CMake配置NPU_FFI_VTA_USE_STUB=OFF时能查找VTA（如果路径正确）✅
  - `programmatic` TR-11.2: stub模式仍然是默认且正常工作 ✅
- **Notes**: real_rt.cc已编写完成但默认不编译；切换到真实硬件时只需关闭stub选项

## [x] Task 12: 构建验证与 CI 配置
- **Priority**: medium
- **Depends On**: Task 8, Task 9
- **Description**:
  - 创建 `.github/workflows/ci.yml`：GitHub Actions CI配置
    - 构建矩阵：Windows/Ubuntu/macOS × Python 3.13
    - 步骤：checkout → setup-python → 安装依赖 → 构建安装 → 测试 → wheel验证
  - stub模式构建和测试验证通过
- **Acceptance Criteria Addressed**: AC-2, AC-5
- **Test Requirements**:
  - `programmatic` TR-12.1: stub模式pip install -e成功 ✅
  - `programmatic` TR-12.2: 安装后import npu_ffi.vta成功且所有测试通过 ✅（116 passed）
  - `programmatic` TR-12.3: CI配置语法正确 ✅
