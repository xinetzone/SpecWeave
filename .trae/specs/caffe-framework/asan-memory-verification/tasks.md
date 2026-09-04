# Tasks

## [x] Task 1: 创建 ASan 演示 C++ 测试用例
创建自包含的 `examples/asan_demo.cpp`，包含内存泄漏（`new`/`new[]` 后未释放）与堆越界写入（访问越界索引）两类错误，并验证 ASan 可捕获。

- [x] 1.1 编写 `examples/asan_demo.cpp`：定义 `leak_demo()`（`new` 后不 `delete`）与 `heap_overflow_demo()`（越界写入数组）
- [x] 1.2 提供 standalone 编译运行说明（`g++ -fsanitize=address -g -O0`），确保 ASan 捕获两类错误（已在 WSL g++ 13.3 实测：`heap-buffer-overflow` + `LeakSanitizer` 均捕获）
- [x] 1.3 在 `tests/cpp/` 增加 `test_asan_demo.cpp`（受 `CAFFE_FFI_ENABLE_ASAN` 守卫，暴露子程序避免单进程框架崩溃）

## [x] Task 2: CMake 集成 ASan 编译选项
在 caffe-ffi 的 CMake 模块中加入 `CAFFE_FFI_ENABLE_ASAN` 开关，并在 `caffe_ffi_configure_target()` 内统一追加 ASan 编译/链接标志。

- [x] 2.1 `cmake/Options.cmake`：新增 `option(CAFFE_FFI_ENABLE_ASAN ... OFF)`（已存在，描述文本对齐）
- [x] 2.2 `cmake/CompilerConfig.cmake`：在 `caffe_ffi_configure_target()` 内，当 `CAFFE_FFI_ENABLE_ASAN` 为 ON 时追加 `-fsanitize=address`（GCC/Clang）或 `/fsanitize=address`（MSVC），并输出构建日志（已实现并静态验证）
- [x] 2.3 验证：`-DCAFFE_FFI_ENABLE_ASAN=ON` 配置时编译/链接标志正确、默认 OFF 不污染构建

## [x] Task 3: 编写 ASan 报告堆栈解读文档
新增 `docs/setup/ASAN_REPORT_READING_GUIDE.md`，解释 ASan 报告结构与定位越界写入的方法。

- [x] 3.1 解释报告核心字段：`WRITE of size N`、`0x...` 地址、`heap-buffer-overflow`、`#0..#N` 栈帧、redzone
- [x] 3.2 演示如何用 `-g` 符号 + `addr2line` 定位到精确源码行
- [x] 3.3 附 1 份真实 ASan 输出示例（基于 Task 1 的演示用例，实测捕获的真实输出）

# Task Dependencies
- [Task 2] depends on [Task 1]（CMake 演示用例需先存在以验证选项生效）
- [Task 3] depends on [Task 1]（文档需引用 Task 1 的 ASan 输出示例）