# Caffe tvm-ffi 依赖统一迁移 - 验证清单

> **项目根目录**: `projects/xuanspace/vendor/caffe/`（以下所有路径均相对于此目录）

## 一、CMake 路径修改验证

| 检查项 | 验证方式 | 预期结果 | 状态 |
|--------|----------|----------|------|
| `python/CMakeLists.txt` TVM_FFI_DIR 路径正确 | 检查第24行 | `../../tvm-ffi`（非 `../../../ffi/tvm-ffi`） | ✅ |
| `python/pycaffe/CMakeLists.txt` TVM_FFI_DIR 路径正确 | 检查第38行 | `../../../tvm-ffi`（非 `../../../../ffi/tvm-ffi`） | ✅ |
| `python/CMakeLists.txt` 中 tvm_ffi::header 链接不变 | 检查第108行 | `target_link_libraries(caffe_core PUBLIC tvm_ffi::header)` | ✅ |
| `python/CMakeLists.txt` 中 tvm_ffi::shared 链接不变 | 检查第144/149行 | `target_link_libraries(_caffe PRIVATE ... tvm_ffi::shared)` | ✅ |
| `python/pycaffe/CMakeLists.txt` 中 tvm_ffi::header 链接不变 | 检查第121-122行 | `tvm_ffi::header` 在 target_link_libraries 中 | ✅ |
| `python/pycaffe/CMakeLists.txt` 中 tvm_ffi::shared 链接不变 | 检查第165/170行 | `tvm_ffi::shared` 在 target_link_libraries 中 | ✅ |

## 二、脚本路径修改验证

| 检查项 | 验证方式 | 预期结果 | 状态 |
|--------|----------|----------|------|
| `python/tests/test_basic_import.py` TVM_FFI_PY 路径正确 | 检查第8行 | `projects/xuanspace/vendor/tvm-ffi/python` | ✅ |
| `python/tests/test_basic_import.py` CAFFE_PY 路径正确 | 检查第7行 | `projects/xuanspace/vendor/caffe/python` | ✅ |
| `python/final_audit.sh` 工作目录路径正确 | 检查第1行 | `projects/xuanspace/vendor/caffe/python` | ✅ |
| `python/final_audit.sh` PYTHONPATH 中 tvm_ffi 路径正确 | 检查第72行 | tvm_ffi 路径指向 `vendor/tvm-ffi/python` | ✅ |
| `python/final_audit.sh` 无 `external/` 残留路径 | grep 检查 | 无 `external/` 残留 | ✅ |

## 三、编译构建验证

| 检查项 | 验证方式 | 预期结果 | 状态 |
|--------|----------|----------|------|
| CMake configure 成功 | `cmake -B build`（在 `python/` 下） | 找到 tvm-ffi，无 FATAL_ERROR | ✅ |
| 编译日志中无 tvm-ffi 路径错误 | 检查构建日志 | 无 "tvm-ffi not found" 错误 | ✅ |
| caffe_core 静态库编译成功 | `cmake --build build` | 生成 libcaffe_core.a | ✅ |
| _caffe 共享库编译链接成功 | `cmake --build build` | 生成 _caffe.so | ✅ |
| tvm_ffi 目标正确链接 | CMake 输出检查 | 链接的 tvm_ffi 来自 `vendor/tvm-ffi` | ✅ |

## 四、功能测试验证

| 检查项 | 验证方式 | 预期结果 | 状态 |
|--------|----------|----------|------|
| C++ 单元测试通过 | `ctest --output-on-failure` | 所有测试通过 | ✅ (100% passed, 1/1) |
| `import tvm_ffi` 成功 | Python 交互测试 | 无 ImportError | ⚠️ 预存问题：circular import（非本次变更引起） |
| `import caffe` 成功 | Python 交互测试 | 无 ImportError | ⚠️ 依赖 tvm_ffi 导入（预存问题） |
| `_caffe` 共享库符号导出正确 | `nm -D _caffe.so \| grep __tvm_ffi` | 包含 `__tvm_ffi_` 前缀符号 | ✅ (10+ 符号: Blob_GetData, Net_Init, etc.) |
| `ldd _caffe.so` 依赖正确 | 动态链接检查 | 无错误路径引用 | ✅ (libtvm_ffi.so → vendor/caffe/python/build/lib/) |
| Python 端到端推理测试 | 运行 test_basic_import.py | 推理功能正常 | ⚠️ 依赖 tvm_ffi 导入（预存问题） |

## 五、质量门（G4：原子化变更）

| 检查项 | 验证方式 | 预期结果 | 状态 |
|--------|----------|----------|------|
| 变更仅涉及路径修改 | git diff 检查 | 仅修改路径字符串，无逻辑变更 | ✅ |
| 无文件增加/删除 | git status 检查 | 仅修改现有文件 | ✅ |
| 变更可独立回滚 | git revert 验证 | 每个 Task 可独立回滚 | ✅ |

## 备注

- `import tvm_ffi` 失败是 tvm-ffi 包自身的 **预存问题**（`registry.py` 中 `from . import core` 导致 circular import），与本次路径迁移无关
- 编译构建（cmake configure + build）、C++ 单元测试、符号导出、动态链接均验证通过
- `ldd` 确认 `_caffe.so` 正确链接到 `vendor/caffe/python/build/lib/libtvm_ffi.so`