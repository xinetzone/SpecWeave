---
id: "caffe-tvm-ffi-dependency-graph"
title: "tvm-ffi 在 Caffe 中的依赖关系图谱"
source: "specs/caffe-tvm-ffi-dependency-migration/spec.md"
---

# tvm-ffi 在 Caffe 中的依赖关系图谱

> 项目根目录：`projects/xuanspace/vendor/caffe/`，tvm-ffi 位于 `../tvm-ffi`（即 `vendor/tvm-ffi/`）

```mermaid
flowchart TB
    subgraph VENDOR_TVM ["1：vendor/tvm-ffi（依赖目标）"]
        TVM_CMAKE["CMakeLists.txt<br/>定义 tvm_ffi::header<br/>定义 tvm_ffi::shared"]
        TVM_INCLUDE["include/tvm/ffi/<br/>C++ 头文件"]
        TVM_SRC["src/ffi/<br/>C++ 源码实现"]
        TVM_PYTHON["python/tvm_ffi/<br/>Python 包"]
    end
    subgraph CMAKE_LAYER ["2：CMake 路径配置层"]
        PY_CMAKE["python/CMakeLists.txt<br/>TVM_FFI_DIR = ../../tvm-ffi"]
        PYC_CMAKE["python/pycaffe/CMakeLists.txt<br/>TVM_FFI_DIR = ../../../tvm-ffi"]
    end
    subgraph CMAKE_TARGETS ["3：CMake 目标层"]
        TVM_HEADER["tvm_ffi::header<br/>（仅头文件）"]
        TVM_SHARED["tvm_ffi::shared<br/>（动态库）"]
        CAFFE_CORE["caffe_core<br/>（静态库）"]
    end
    subgraph CPP_SRC ["4：C++ 源码引用层"]
        CAFFE_CPP["python/src/caffe/_caffe.cpp<br/>#include tvm/ffi/...<br/>TVM_FFI_DLL_EXPORT_TYPED_FUNC"]
        PYC_CPP["python/pycaffe/.../pycaffe/_caffe.cpp<br/>#include tvm/ffi/...<br/>TVM_FFI_DLL_EXPORT_TYPED_FUNC"]
    end
    subgraph PYTHON_LAYER ["5：Python 导入层"]
        INIT_PY["python/caffe/__init__.py<br/>import tvm_ffi"]
        TEST_PY["tests/test_basic_import.py<br/>sys.path.insert TVM_FFI_PY"]
        AUDIT_SH["final_audit.sh<br/>PYTHONPATH + LD_LIBRARY_PATH"]
    end
    subgraph BUILD_OUT ["6：构建产出层"]
        LIBTVM["libtvm_ffi.so"]
        CAFFE_SO["_caffe.so<br/>（FFI 共享库）"]
        TEST_BIN["test_caffe_slim<br/>（C++ 单元测试）"]
    end
    PY_CMAKE -->|"add_subdirectory"| TVM_CMAKE
    PYC_CMAKE -->|"add_subdirectory"| TVM_CMAKE
    TVM_INCLUDE --> TVM_HEADER
    TVM_SRC --> TVM_SHARED
    TVM_CMAKE --> TVM_HEADER
    TVM_CMAKE --> TVM_SHARED
    CAFFE_CPP -->|"include"| TVM_INCLUDE
    PYC_CPP -->|"include"| TVM_INCLUDE
    TVM_HEADER -->|"target_link PUBLIC"| CAFFE_CORE
    CAFFE_CORE -->|"target_link"| CAFFE_SO
    CAFFE_CPP -->|"编译为"| CAFFE_SO
    PYC_CPP -->|"编译为"| CAFFE_SO
    TVM_SHARED -->|"target_link PRIVATE"| CAFFE_SO
    TVM_SHARED --> LIBTVM
    CAFFE_SO -->|"ldd 链接"| LIBTVM
    CAFFE_CORE --> TEST_BIN
    INIT_PY -->|"sys.path"| TVM_PYTHON
    TEST_PY -->|"sys.path"| TVM_PYTHON
    AUDIT_SH -->|"PYTHONPATH"| TVM_PYTHON
    style VENDOR_TVM fill:#e8f5e9,stroke:#4caf50
    style CMAKE_LAYER fill:#e3f2fd,stroke:#2196f3
    style CMAKE_TARGETS fill:#fff3e0,stroke:#ff9800
    style CPP_SRC fill:#fce4ec,stroke:#e91e63
    style PYTHON_LAYER fill:#f3e5f5,stroke:#9c27b0
    style BUILD_OUT fill:#e0f7fa,stroke:#00bcd4
```

## 依赖关系说明

| 层级 | 文件 | 引用方式 | 说明 |
|------|------|---------|------|
| **CMake 路径** | `python/CMakeLists.txt` | `add_subdirectory(../../tvm-ffi)` | 从 `python/` 向上两级到 `vendor/` 进入 tvm-ffi |
| **CMake 路径** | `python/pycaffe/CMakeLists.txt` | `add_subdirectory(../../../tvm-ffi)` | 从 `python/pycaffe/` 向上三级到 `vendor/` |
| **CMake 目标** | `python/CMakeLists.txt` | `tvm_ffi::header` (PUBLIC) | caffe_core 通过 target_link_libraries 引用 |
| **CMake 目标** | `python/CMakeLists.txt` | `tvm_ffi::shared` (PRIVATE) | _caffe 通过 target_link_libraries 引用 |
| **C++ 源码** | `python/src/caffe/_caffe.cpp` | `#include <tvm/ffi/...>` | 头文件路径由 CMake include dirs 控制 |
| **C++ 源码** | `python/pycaffe/.../pycaffe/_caffe.cpp` | `#include <tvm/ffi/...>` | 同上 |
| **Python** | `python/caffe/__init__.py` | `import tvm_ffi` | 依赖 sys.path 找到 tvm_ffi 包 |
| **Python** | `tests/test_basic_import.py` | sys.path 插入 TVM_FFI_PY | 硬编码路径指向 vendor/tvm-ffi/python |
| **Shell** | `final_audit.sh` | PYTHONPATH + LD_LIBRARY_PATH | 环境变量指向 vendor/tvm-ffi |
| **运行时** | `_caffe.so` | `ldd` → `libtvm_ffi.so` | 动态链接到 vendor/caffe/python/build/lib/ |

## 关键路径验证

- **CMake configure**：`python/CMakeLists.txt` → `../../tvm-ffi` → `vendor/tvm-ffi/CMakeLists.txt` ✅
- **编译产物**：`libtvm_ffi.so` + `libcaffe_core.a` + `_caffe.so` → 87/87 targets ✅
- **符号导出**：`nm -D _caffe.so | grep __tvm_ffi` → 10+ 符号（Blob_GetData, Net_Init, Net_Forward...）✅
- **动态链接**：`ldd _caffe.so | grep tvm` → `libtvm_ffi.so → vendor/caffe/python/build/lib/` ✅
- **C++ 测试**：`ctest` → 100% passed (1/1) ✅