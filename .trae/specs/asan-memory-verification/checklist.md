# ASan 内存验证 Checklist

- [x] `examples/asan_demo.cpp` 存在且包含内存泄漏 + 堆越界写入两类错误
- [x] 使用 `-fsanitize=address` 编译并运行 `asan_demo.cpp`，ASan 成功捕获 `heap-buffer-overflow` 与 `LeakSanitizer` 泄漏（WSL g++ 13.3.0 实测）
- [x] `cmake/Options.cmake` 包含 `CAFFE_FFI_ENABLE_ASAN` 选项（默认 OFF）
- [x] `cmake/CompilerConfig.cmake` 的 `caffe_ffi_configure_target()` 在启用时追加 `-fsanitize=address`（或 MSVC `/fsanitize=address`）并输出构建日志
- [x] `-DCAFFE_FFI_ENABLE_ASAN=ON` 配置时标志正确；默认 OFF 时构建行为不受污染
- [x] `docs/setup/ASAN_REPORT_READING_GUIDE.md` 存在，解释报告核心字段与栈帧定位方法
- [x] 文档包含 1 份真实 ASan 报告示例（基于演示用例，实测捕获的真实输出）