# WIN32 IMPORTED DLL 修复与 AssertHelper 断言验证 - 实施计划

## [x] Task 1: 准备构建环境（MSVC + conda py314）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 检测可用的 vcvars64.bat 路径（VS 2022 Community/Professional/BuildTools/Insiders）
  - 导入 MSVC 环境变量（INCLUDE、LIB、PATH）到当前 shell
  - 检测 conda py314 环境位置，将其 Library/bin、Scripts、DLLs、tvm_ffi/lib 添加到 PATH
  - 验证 cmake、ninja、cl.exe 可用，kernel32.lib 在 LIB 路径中
- **Acceptance Criteria Addressed**: AC-1 (前置条件)
- **Test Requirements**:
  - `programmatic` TR-1.1: `where cmake` 和 `where ninja` 返回有效路径
  - `programmatic` TR-1.2: `cl.exe` 可被调用（不报错 "cl is not recognized"）
  - `programmatic` TR-1.3: `$env:LIB` 中包含 kernel32.lib 所在目录
  - `programmatic` TR-1.4: `$env:CONDA_PREFIX` 或 PATH 中包含 py314 环境
- **Notes**: 使用 scripts/p0_verify_build.ps1 中已有的环境检测逻辑作为参考

## [x] Task 2: CMake Configure（配置阶段验证）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 在 caffe-ffi 根目录执行 cmake configure：`cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCAFFE_FFI_BUILD_TESTS=ON`
  - 检查输出中无 CMake Error
  - 特别关注 WindowsDllCopy.cmake 相关的输出：无 "could not resolve DLL path" WARNING
  - 确认 tvm_ffi::shared 被正确 find_package 找到
  - 确认 caffe_ffi_tests 目标被创建
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-2.1: cmake 退出码为 0
  - `programmatic` TR-2.2: 输出中不包含 "CMake Error" 字符串
  - `programmatic` TR-2.3: 输出中不包含 "could not resolve DLL path" WARNING
  - `programmatic` TR-2.4: build/build.ninja 文件存在
  - `human-judgement` TR-2.5: CMake 输出中 tvm_ffi、Protobuf、BLAS 均被正确检测

## [x] Task 3: CMake Build（编译阶段验证）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 执行 `cmake --build build --config Release`
  - 编译 _caffe_ffi 库和 caffe_ffi_tests 测试可执行文件
  - 如果编译失败，区分是否为预存问题（test_neuron_layers.cpp/test_deconv_layer.cpp 等未排除文件的编译错误）
  - 如遇预存编译错误，更新 Tests.cmake 排除列表（仅限于与本次修复无关的预存问题）
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-3.1: 编译退出码为 0
  - `programmatic` TR-3.2: build/ 目录下存在 _caffe_ffi.dll（或 .lib for static）
  - `programmatic` TR-3.3: build/ 目录下存在 caffe_ffi_tests.exe
  - `programmatic` TR-3.4: 无 C4267/C4244 等警告被 /WX 升级为错误（除非为预存问题）

## [x] Task 4: 验证 DLL 复制（运行时依赖检查）
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 检查 build/ 输出目录中是否存在关键运行时 DLL：tvm_ffi.dll、abseil_*.dll、libprotobuf*.dll
  - 如果 DLL 缺失，检查 CMake 配置日志中是否有 WARNING 信息（而不是静默失败）
  - 必要时手动检查 POST_BUILD 复制命令是否在 build.ninja 中正确生成
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-4.1: build/tvm_ffi.dll 存在（或在 build/ 子目录中）
  - `programmatic` TR-4.2: build/ 目录中至少有一个 absl_*.dll
  - `programmatic` TR-4.3: build/ 目录中至少有一个 libprotobuf*.dll
  - `human-judgement` TR-4.4: 检查 CMake 输出，确认 DLL 复制使用了新的 IMPORTED 解析路径而非 fallback WARNING

## [x] Task 5: 运行 C++ 测试（全量）
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 直接运行 `build\caffe_ffi_tests.exe`（不带参数运行所有测试）
  - 确认测试可执行文件不会因 DLL 缺失而立即崩溃（0xC0000135/0xC0000139）
  - 收集测试结果：通过数、失败数、总耗时
  - 如有失败，区分是预存测试失败还是本次修复引入的问题
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-5.1: caffe_ffi_tests.exe 可启动并开始输出 "[ RUN      ]" 测试信息
  - `programmatic` TR-5.2: 不会立即崩溃（无 "DLL not found" 或 0xC0000135 错误）
  - `programmatic` TR-5.3: 至少有使用 EXPECT_EQ/EXPECT_NEAR 等流式断言的测试被执行
  - `human-judgement` TR-5.4: 如有测试失败，查看异常消息是否包含 << 追加的上下文信息（证明流式消息工作正常）

## [x] Task 6: 定向运行包含流式断言的测试用例
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 使用 test filter 功能运行特定的已知使用流式断言的测试（如 BlobTest、SoftmaxWithLossTest）
  - 命令：`build\caffe_ffi_tests.exe Blob` 或 `build\caffe_ffi_tests.exe Softmax`
  - 验证过滤功能工作正常
  - 验证 AssertHelper 在通过/失败场景下均表现正确
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-6.1: 带 filter 参数运行时仅执行匹配的测试
  - `programmatic` TR-6.2: 过滤的测试正常执行并输出结果
  - `programmatic` TR-6.3: 测试不会因 AssertHelper 移动构造/析构导致 terminate/double-free
  - `human-judgement` TR-6.4: 审查测试输出，确认流式消息功能正确（如测试失败时有完整错误消息）

## [x] Task 7: 验证 assert_helper.hpp 头文件独立性
- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 检查 assert_helper.hpp 仅依赖标准库头文件
  - 确认 test_harness.hpp 正确通过 `using` 声明复用 assert_helper.hpp 中的类型
  - 验证 CAFFE_FFI_CHECK_* 宏可在生产代码中使用（检查是否有现有源文件使用这些宏）
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-7.1: assert_helper.hpp 的 #include 仅包含 <sstream>、<stdexcept>、<string>、<type_traits>、<utility>
  - `programmatic` TR-7.2: test_harness.hpp 中 using 声明的类型在 assert_helper.hpp 中均存在
  - `human-judgement` TR-7.3: 代码审查确认 AssertHelper 类的移动构造函数正确处理 ostringstream 转移
