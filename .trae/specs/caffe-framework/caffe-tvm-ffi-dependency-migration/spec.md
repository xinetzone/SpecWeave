# Caffe tvm-ffi 依赖统一迁移 Spec

> **方法论**: 场景3：重构优化（I→F→A→C）
> **洞察（I）已执行**: 见 [I-phase 洞察报告](#i-phase-洞察报告)
> **项目根目录**: `projects/xuanspace/vendor/caffe/`（以下所有路径均相对于此目录）

---

## Why

当前 `python/CMakeLists.txt` 中 tvm-ffi 的引用路径为 `../../../ffi/tvm-ffi`，该路径解析为 `projects/xuanspace/ffi/tvm-ffi`，**该目录不存在**。而实际的 tvm-ffi 库位于 `projects/xuanspace/vendor/tvm-ffi`。此外，caffe 中还存在 Python 层对 tvm_ffi 模块的隐式导入路径依赖。需要将所有直接/间接依赖统一指向 `../tvm-ffi`（即 `vendor/tvm-ffi`）。

## I-Phase 洞察报告

### 现象
- 当前 `python/CMakeLists.txt` 第24行：`set(TVM_FFI_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../../ffi/tvm-ffi")` 指向 `projects/xuanspace/ffi/tvm-ffi`（**不存在**）
- 实际 tvm-ffi 库位于 `projects/xuanspace/vendor/tvm-ffi`（存在，含完整 CMake + Python 包）
- 如果构建时路径不存在，`CMakeLists.txt` 第25-27行会直接 `FATAL_ERROR`

### 根因
- 之前的 `caffe-cpp-slim-tvm-ffi` 项目在配置 tvm-ffi 路径时，使用了相对路径 `../../../ffi/tvm-ffi`，但这指向了一个不存在的 `ffi/` 目录
- 正确的 tvm-ffi 位置应该在 `vendor/tvm-ffi` 下

### 影响
- 现有构建配置**无法工作**（路径不存在会导致 CMake 配置失败）
- Python 层 `import tvm_ffi` 依赖 `sys.path` 中能找到 tvm_ffi 包，但未显式配置路径

### 建议
- 将所有 tvm-ffi 引用统一指向 `vendor/tvm-ffi`（相对于 caffe 目录为 `../tvm-ffi`）
- 使用基于 CMake `CMAKE_CURRENT_SOURCE_DIR` 的相对路径

## What Changes

- 修改 `python/CMakeLists.txt` 中 `TVM_FFI_DIR` 路径，指向 `../../tvm-ffi`
- 修改 `python/pycaffe/CMakeLists.txt` 中 `TVM_FFI_DIR` 路径，指向 `../../../tvm-ffi`
- 更新 `python/tests/test_basic_import.py` 中的硬编码路径
- 更新 `python/final_audit.sh` 中的硬编码路径
- 检查 `python/python/caffe/__init__.py` 中的 `tvm_ffi` 导入路径（当前为 `import tvm_ffi`，依赖 sys.path，无需修改但需确认）
- 检查 `python/src/caffe/_caffe.cpp` 和 `python/pycaffe/python/pycaffe/_caffe.cpp` 中的头文件引用（`#include <tvm/ffi/...>` 由 CMake include dirs 控制，无需修改）
- 验证编译构建流程
- 执行功能测试与兼容性验证

## Impact

- Affected specs: 无直接依赖
- Affected code:
  - `python/CMakeLists.txt`
  - `python/pycaffe/CMakeLists.txt`
  - `python/python/caffe/__init__.py`
  - `python/tests/test_basic_import.py`
  - `python/final_audit.sh`

## ADDED Requirements

### Requirement: TVM-FFI 路径统一指向 vendor/tvm-ffi
所有 caffe 项目中对 tvm-ffi 的引用（CMake 构建路径、Python 导入路径、脚本路径）SHALL 统一指向 `vendor/tvm-ffi`（相对于 caffe 目录为 `../tvm-ffi`）。

#### Scenario: CMake 配置路径正确
- **WHEN** 执行 `cmake -B build` 在 `python/` 目录下
- **THEN** CMake 成功找到 `../tvm-ffi/CMakeLists.txt` 并通过 `add_subdirectory` 引入
- **THEN** 不再出现 `FATAL_ERROR: tvm-ffi not found`

#### Scenario: Python 导入路径正确
- **WHEN** 在 Python 中执行 `import tvm_ffi` 或通过 `tvm_ffi.load_module` 加载 `_caffe`
- **THEN** tvm_ffi 模块能被正确导入，且路径指向 `vendor/tvm-ffi/python/tvm_ffi/`

### Requirement: 构建系统完整性
修改后的 CMake 配置 SHALL 能够完成完整的编译构建流程，生成 `caffe_core` 静态库和 `_caffe` 共享库。

#### Scenario: 完整编译通过
- **WHEN** 执行 `cmake --build build` 在 `python/` 目录下
- **THEN** `caffe_core` 静态库编译成功
- **THEN** `_caffe` 共享库编译链接成功
- **THEN** 链接的 `tvm_ffi::header` 和 `tvm_ffi::shared` 目标来自正确的 `vendor/tvm-ffi` 路径

### Requirement: 功能测试通过
修改后的依赖配置 SHALL 不会导致功能退化，现有测试用例 SHALL 通过。

#### Scenario: C++ 单元测试通过
- **WHEN** 运行 `ctest` 或 `test_caffe_slim`
- **THEN** 所有测试用例通过

#### Scenario: Python 端到端测试通过
- **WHEN** 运行 `python tests/test_basic_import.py` 或 `test_inference.py`
- **THEN** 测试通过，推理功能正常

## MODIFIED Requirements

### Requirement: CMake tvm-ffi 路径
`python/CMakeLists.txt` 中 `TVM_FFI_DIR` 变量 SHALL 从 `"${CMAKE_CURRENT_SOURCE_DIR}/../../../ffi/tvm-ffi"` 修改为 `"${CMAKE_CURRENT_SOURCE_DIR}/../../tvm-ffi"`（即从 `python/` 向上两级到 `vendor/`，再进入 `tvm-ffi/`）。

`python/pycaffe/CMakeLists.txt` 中 `TVM_FFI_DIR` 变量 SHALL 从 `"${CMAKE_CURRENT_SOURCE_DIR}/../../../../ffi/tvm-ffi"` 修改为 `"${CMAKE_CURRENT_SOURCE_DIR}/../../../tvm-ffi"`（即从 `python/pycaffe/` 向上三级到 `vendor/`，再进入 `tvm-ffi/`）。

#### Scenario: 路径解析正确（python/CMakeLists.txt）
- **WHEN** `CMAKE_CURRENT_SOURCE_DIR` 为 `python/` 目录
- **THEN** `../../tvm-ffi` 解析为 `vendor/tvm-ffi`
- **THEN** `EXISTS("${TVM_FFI_DIR}/CMakeLists.txt")` 返回 TRUE

#### Scenario: 路径解析正确（pycaffe/CMakeLists.txt）
- **WHEN** `CMAKE_CURRENT_SOURCE_DIR` 为 `python/pycaffe/` 目录
- **THEN** `../../../tvm-ffi` 解析为 `vendor/tvm-ffi`
- **THEN** `EXISTS("${TVM_FFI_DIR}/CMakeLists.txt")` 返回 TRUE

## 依赖引用全景图（I-Phase 产出）

| # | 文件（相对 caffe 根目录） | 行号 | 引用类型 | 当前值 | 是否需要修改 |
|---|------|------|---------|--------|------------|
| 1 | `python/CMakeLists.txt` | 24 | CMake 路径变量 | `../../../ffi/tvm-ffi` | ✅ 改为 `../../tvm-ffi` |
| 2 | `python/CMakeLists.txt` | 28 | CMake add_subdirectory | 使用 `TVM_FFI_DIR` | ❌ 无需修改 |
| 3 | `python/CMakeLists.txt` | 108 | CMake target_link | `tvm_ffi::header` | ❌ 无需修改 |
| 4 | `python/CMakeLists.txt` | 144,149,171,176 | CMake target_link | `tvm_ffi::shared` | ❌ 无需修改 |
| 5 | `python/src/caffe/_caffe.cpp` | 全文件 | C++ include | `#include <tvm/ffi/...>` | ❌ 无需修改 |
| 6 | `python/pycaffe/python/pycaffe/_caffe.cpp` | 全文件 | C++ include | `#include <tvm/ffi/...>` | ❌ 无需修改 |
| 7 | `python/python/caffe/__init__.py` | 28 | Python import | `import tvm_ffi` | ⚠️ 需检查 sys.path |
| 8 | `python/tests/test_basic_import.py` | 7-8 | Python 路径 | 含旧路径 `external/ffi/` | ✅ 需更新 |
| 9 | `python/final_audit.sh` | 多处 | Shell 脚本 | 含旧路径 `external/` | ✅ 需更新 |
| 10 | `python/pycaffe/CMakeLists.txt` | 38 | CMake 路径变量 | `../../../../ffi/tvm-ffi` | ✅ 改为 `../../../tvm-ffi` |
| 11 | `caffex/cmake/Dependencies.cmake` | 全文件 | CMake 依赖 | 无 tvm-ffi 引用（仅 boost/glog） | ❌ 无需修改 |