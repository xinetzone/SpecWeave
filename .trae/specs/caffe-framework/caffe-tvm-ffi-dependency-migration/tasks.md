# Caffe tvm-ffi 依赖统一迁移 - 实现计划

> **方法论链路**: I→F→A→C（场景3：重构优化）
> **I-Phase**: 已完成（见 spec.md 依赖引用全景图）
> **项目根目录**: `projects/xuanspace/vendor/caffe/`（以下所有路径均相对于此目录）

---

## Task 1: 修改 python/CMakeLists.txt 中 tvm-ffi 路径 ✅

- **Priority**: critical
- **Depends On**: None
- **Description**:
  - 修改 `python/CMakeLists.txt` 第24行：
    - 旧值: `set(TVM_FFI_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../../ffi/tvm-ffi")`
    - 新值: `set(TVM_FFI_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../tvm-ffi")`
  - 路径计算：`python/` → `../../` → `vendor/` → `../../tvm-ffi` = `vendor/tvm-ffi` ✅
  - 其余 `tvm_ffi::header` 和 `tvm_ffi::shared` 的 target_link_libraries 引用无需修改（target 名称不变）
- **Acceptance Criteria**: CMake configure 时能成功找到 `vendor/tvm-ffi/CMakeLists.txt`

## Task 2: 修改 python/pycaffe/CMakeLists.txt 中 tvm-ffi 路径 ✅

- **Priority**: critical
- **Depends On**: None
- **Description**:
  - 修改 `python/pycaffe/CMakeLists.txt` 第38行：
    - 旧值: `set(TVM_FFI_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../../../ffi/tvm-ffi")`
    - 新值: `set(TVM_FFI_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../../tvm-ffi")`
  - 路径计算：`python/pycaffe/` → `../../../` → `vendor/` → `../../../tvm-ffi` = `vendor/tvm-ffi` ✅
  - 其余 tvm_ffi target_link_libraries 引用无需修改
- **Acceptance Criteria**: pycaffe 的 CMake configure 能成功找到 tvm-ffi

## Task 3: 更新测试脚本中的路径引用 ✅

- **Priority**: high
- **Depends On**: None
- **Description**:
  - 修改 `python/tests/test_basic_import.py`：
    - 第7行 CAFFE_PY：将 `external/chaos/caffe/python` 替换为 `projects/xuanspace/vendor/caffe/python`
    - 第8行 TVM_FFI_PY：将 `external/ffi/tvm-ffi/python` 替换为 `projects/xuanspace/vendor/tvm-ffi/python`
- **Acceptance Criteria**: 测试脚本中的路径指向正确的 vendor 目录

## Task 4: 更新审计脚本中的路径引用 ✅

- **Priority**: medium
- **Depends On**: None
- **Description**:
  - 修改 `python/final_audit.sh` 中所有硬编码的 `/mnt/d/spaces/SpecWeave/external/` 路径：
    - `external/chaos/caffe/python` → `projects/xuanspace/vendor/caffe/python`
    - `external/ffi/tvm-ffi/python` → `projects/xuanspace/vendor/tvm-ffi/python`
  - 涉及行：第1行（cd）、第70行（cd）、第72行（PYTHONPATH）、第73行（LD_LIBRARY_PATH）、第82行（proto 路径）
- **Acceptance Criteria**: 审计脚本中所有路径指向正确的 vendor 目录

## Task 5: 编译构建验证 ✅

- **Priority**: critical
- **Depends On**: Task 1, Task 2
- **Description**:
  - 在 WSL 环境中，在 `python/` 目录下执行完整编译构建流程：
    - 清理旧的 build 目录
    - 运行 `cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release`
    - 运行 `cmake --build build`
  - 验证产出物：
    - `caffe_core` 静态库编译成功
    - `_caffe` 共享库编译链接成功
    - 链接的 tvm_ffi 目标来自 `vendor/tvm-ffi`
  - 检查编译日志中无 tvm-ffi 路径错误
- **Acceptance Criteria**: 完整编译通过，0 errors

## Task 6: 功能测试与兼容性验证 ✅

- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 运行 C++ 单元测试：`ctest --output-on-failure`
  - 运行 Python 导入测试：验证 `import tvm_ffi` 和 `import caffe` 成功
  - 运行 Python 端到端推理测试（如有可用的 prototxt + caffemodel）
  - 验证 `_caffe` 共享库能正确导出 `__tvm_ffi_` 前缀符号
  - 验证 `ldd _caffe.so` 不包含错误的 tvm_ffi 路径引用
- **Acceptance Criteria**: 所有测试通过，推理功能正常

## Task Dependencies

- Task 5 depends on Task 1, Task 2
- Task 6 depends on Task 5
- Task 1, Task 2, Task 3, Task 4 can run in parallel