# WIN32 IMPORTED DLL 修复与 AssertHelper 断言验证 - Product Requirement Document

## Overview
- **Summary**: 在 Windows (MSVC) 平台上验证两项前期修复的正确性：(1) CMake WIN32 IMPORTED 库 DLL 复制反模式修复（`_caffe_ffi_resolve_imported_dll` 通用函数）；(2) 独立工具头文件 `assert_helper.hpp` 中的 IIFE+AssertHelper 流式断言宏（生产 CHECK 宏 + 测试 EXPECT 宏）。验证方式为 CMake 配置→全量编译→运行 C++ 单元测试。
- **Purpose**: 确认之前提交（a6036ad）中修复的 WIN32 IMPORTED DLL 复制问题和提取的流式断言工具头文件在实际编译和运行时均表现正常，无静默失败、编译错误或运行时异常。
- **Target Users**: caffe-ffi 开发者、CI 系统

## Goals
- G1: CMake configure 在 MSVC 环境下成功完成，无 ERROR，无 DLL 路径解析相关 WARNING
- G2: 全量编译（含 _caffe_ffi 库 + caffe_ffi_tests 测试可执行文件）成功，零编译错误
- G3: 构建输出目录中包含所有必要的运行时 DLL（tvm_ffi.dll、abseil DLLs、protobuf DLLs 等），无 DLL_NOT_FOUND (0xC0000135) 错误
- G4: 使用 EXPECT_*/ASSERT_* 流式断言的测试用例编译通过且运行时正确（断言成功不抛异常，断言失败时包含 << 追加的流式消息）
- G5: 生产代码 CAFFE_FFI_CHECK_* 宏在 assert_helper.hpp 中可被正确包含和使用（头文件自包含、零警告）

## Non-Goals (Out of Scope)
- 不修复 test_net.cpp / test_insert_splits.cpp 等已被 Tests.cmake 排除的预存编译错误
- 不运行 Python 测试（pytest），仅验证 C++ 构建和测试
- 不修改业务代码（Layers/Blob/Net 等），仅做构建和测试验证
- 不在 WSL/Linux 环境验证（本次仅验证 Windows MSVC 路径）
- 不新增 C++ 测试用例

## Background & Context
- **反模式 A1（WIN32 IMPORTED DLL）**: 之前 tvm_ffi-config.cmake 在 WIN32 下只设 `IMPORTED_IMPLIB`（.lib）不设 `IMPORTED_LOCATION`（.dll），导致 `$<TARGET_FILE>` 生成表达式为空，POST_BUILD `copy_if_different` 静默失败（日志显示 "Copying..." 但实际未复制），运行时出现 0xC0000135 (DLL_NOT_FOUND)。修复方案：新增 `_caffe_ffi_resolve_imported_dll()` 四层回退探测函数，`caffe_ffi_copy_target_dll()` 区分 IMPORTED vs 本地产物目标。
- **AssertHelper 提取**: 将 IIFE+AssertHelper 流式断言模式从 test_harness.hpp 提取到独立头文件 `include/caffe_ffi/utils/assert_helper.hpp`，包含生产代码 CHECK 宏和测试 EXPECT 宏共享的基础类/比较函数。test_harness.hpp 通过 `using` 声明复用。
- **构建环境**: Windows + MSVC 2022 + Ninja + conda py314 环境（提供 tvm_ffi、protobuf、abseil、OpenBLAS 等依赖）。已有 `scripts/p0_verify_build.ps1` 和 `scripts/verify_build.ps1` 作为构建验证参考脚本。
- **已知排除**: Tests.cmake 当前排除了 `test_net.cpp` 和 `test_insert_splits.cpp`（预存编译问题，与本次修复无关）。

## Functional Requirements
- **FR-1**: CMake configure 阶段成功生成 Ninja 构建系统，检测 tvm_ffi、Protobuf、BLAS 等依赖
- **FR-2**: CMake build 阶段成功编译 _caffe_ffi SHARED 库和 caffe_ffi_tests 可执行文件
- **FR-3**: 构建过程中 POST_BUILD 步骤正确复制 tvm_ffi.dll 等运行时 DLL 到输出目录
- **FR-4**: caffe_ffi_tests.exe 可直接运行（无 DLL 缺失错误），支持按名称过滤测试
- **FR-5**: 使用 EXPECT_EQ/NEAR/TRUE 等带 << 流式消息的测试用例运行时输出包含追加消息
- **FR-6**: assert_helper.hpp 头文件可独立被 #include 并使用 CAFFE_FFI_CHECK_* 宏

## Non-Functional Requirements
- **NFR-1**: 编译零错误（MSVC 下 /WX 将警告视为错误，因此也必须零警告）
- **NFR-2**: DLL 复制无静默失败——复制失败时必须有 CMake WARNING 而非无声跳过
- **NFR-3**: 测试框架过滤器功能正常（支持 suite 名或完整测试名过滤）

## Constraints
- **Technical**: Windows 平台，MSVC 编译器，Ninja 生成器，C++17；conda py314 环境提供依赖
- **Business**: 验证任务不修改代码（仅运行构建和测试，如遇问题定位后再修复）
- **Dependencies**: tvm_ffi >= 0.3.0、Protobuf >= 7、OpenBLAS（均通过 conda py314 提供）

## Assumptions
- MSVC 2022（或 Build Tools）已安装，vcvars64.bat 可在标准路径找到
- conda py314 环境已创建并包含所有必要依赖（tvm_ffi、protobuf、abseil-cpp、openblas）
- Ninja 构建工具可用
- CMake >= 3.26 已安装
- 之前排除的测试文件（test_net.cpp、test_insert_splits.cpp）确实不编译，保持排除状态

## Acceptance Criteria

### AC-1: CMake Configure 成功无 ERROR
- **Given**: 在 caffe-ffi 项目根目录，MSVC 环境已激活（vcvars64），py314 conda 环境在 PATH 中
- **When**: 执行 `cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCAFFE_FFI_BUILD_TESTS=ON`
- **Then**: CMake 配置成功，退出码为 0，输出中无 CMake Error；tvm_ffi::shared 被正确找到；caffe_ffi_tests 目标被创建
- **Verification**: `programmatic`

### AC-2: 全量编译零错误
- **Given**: CMake configure 已成功
- **When**: 执行 `cmake --build build --config Release`
- **Then**: 编译成功，退出码为 0，无编译错误（MSVC /WX 下也无警告升级为错误）
- **Verification**: `programmatic`

### AC-3: 运行时 DLL 正确复制
- **Given**: 编译成功
- **When**: 检查 build 输出目录
- **Then**: build/ 目录下存在 tvm_ffi.dll 以及必要的 abseil/protobuf/OpenBLAS DLLs；无 CMake WARNING 关于无法解析 IMPORTED 目标 DLL 路径
- **Verification**: `programmatic`

### AC-4: C++ 测试可执行文件启动无 DLL 错误
- **Given**: 编译和 DLL 复制完成
- **When**: 执行 `build\caffe_ffi_tests.exe`（不带参数或带 filter）
- **Then**: 测试框架正常启动，开始运行测试用例；不会因 0xC0000135/0xC0000139 立即崩溃
- **Verification**: `programmatic`

### AC-5: 流式断言宏编译且运行正常
- **Given**: 测试可执行文件成功启动
- **When**: 运行包含 EXPECT_EQ/NEAR 等带 << 消息的测试用例（如 Blob 相关测试）
- **Then**: 通过的测试正常标记 PASSED；若有测试失败，异常消息包含 << 追加的上下文信息；不会因 AssertHelper 移动/析构问题导致 double-free 或 terminate
- **Verification**: `programmatic`

### AC-6: assert_helper.hpp 头文件自包含验证
- **Given**: assert_helper.hpp 作为独立工具头文件
- **When**: 检查其 #include 依赖
- **Then**: 它仅依赖标准库头文件（sstream、stdexcept、string、type_traits、utility），不依赖 caffe-ffi 内部其他头文件；可被独立 include 编译
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否有其他尚未排除的测试文件也会遇到编译问题（如 test_neuron_layers.cpp、test_deconv_layer.cpp）？如果编译失败需要确认是否为预存问题
- [ ] 如果全量编译因预存问题失败，是否应改用增量编译（只编译 caffe_ffi_tests 相关目标）？
