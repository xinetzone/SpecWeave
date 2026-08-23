---
title: "09 - ORCJIT 扩展"
date: 2026-07-05
source: "spec:create-tvm-ffi-wiki-tutorial"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/01-agent-protocols-interfaces/tvm-ffi-wiki/09-orcjit-extension.toml"
tags: [tvm-ffi, ffi, python, cuda, jit, dlpack]
---
# ORCJIT 扩展

ORCJIT 扩展基于 LLVM 的 On-Request-Compilation（ORC）JIT 引擎，为 TVM FFI 提供运行时代码生成能力。它可以在程序运行时编译 C/C++/CUDA 源码，生成可执行代码并链接到 TVM FFI 函数系统，支持跨模块符号解析和动态优化。

## 什么是 ORCJIT

LLVM ORC JIT 是 LLVM 提供的新一代即时编译引擎，相比传统 MCJIT 具有以下优势：

- **惰性编译**：函数只在首次调用时编译
- **并发编译**：支持多线程并行编译
- **可组合性**：支持多层 JIT 栈（IR 变换 → 优化 → 代码生成）
- **动态链接**：支持运行时添加/移除模块、符号解析
- **错误恢复**：完善的错误处理机制

## 目录结构

```
addons/tvm_ffi_orcjit/
├── include/tvm/ffi/
│   └── addon/
│       └── orcjit/
│           ├── orcjit.h           # ORCJIT 引擎主接口
│           ├── memory_manager.h   # JIT 内存管理器
│           └── symbol_resolver.h  # 符号解析器
├── src/
│   ├── orcjit.cc                  # 核心实现
│   ├── memory_manager.cc
│   └── symbol_resolver.cc
├── CMakeLists.txt
└── python/
    └── tvm_ffi_orcjit/
        └── __init__.py            # Python 绑定
```

## JIT 编译工作流程

ORCJIT 扩展的典型编译执行流程：

```
C/C++/CUDA 源码
    ↓
Clang 前端编译 → LLVM IR
    ↓
LLVM 优化 Pass（可选）
    ↓
目标代码生成（x86_64 / CUDA PTX）
    ↓
JIT 链接（符号解析、重定位）
    ↓
获取函数指针 → 包装为 FFI Function
    ↓
像普通 FFI 函数一样调用
```

## 基础用法：JIT 编译 C 函数

### C++ API 示例

**简单 C 函数 JIT 编译：**
```cpp
#include <tvm/ffi/addon/orcjit/orcjit.h>
#include <tvm/ffi/ffi.h>

using namespace tvm::ffi;

void jit_basic_example() {
    // 创建 ORCJIT 实例
    auto jit = orcjit::OrcJIT::Create();
    TVM_FFI_CHECK(jit) << "Failed to create ORCJIT engine";
    auto& engine = *jit;
    
    // 定义 C 源码
    std::string c_source = R"(
        int add(int a, int b) {
            return a + b;
        }
        
        double multiply(double x, double y) {
            return x * y;
        }
        
        int fibonacci(int n) {
            if (n <= 1) return n;
            return fibonacci(n-1) + fibonacci(n-2);
        }
    )";
    
    // 编译源码
    auto err = engine.AddModuleFromSource(
        c_source,
        "example.c",     // 模块名（用于诊断）
        orcjit::SourceKind::C
    );
    TVM_FFI_CHECK(!err) << "Compilation failed: " << toString(std::move(err));
    
    // 查找并获取函数符号
    auto add_sym = engine.Lookup("add");
    TVM_FFI_CHECK(add_sym) << "Symbol not found";
    
    using AddFn = int(*)(int, int);
    auto add_fn = add_sym->toAddrAndCast<AddFn>();
    
    // 调用 JIT 编译的函数
    int result = add_fn(3, 5);
    std::cout << "3 + 5 = " << result << std::endl;  // 输出: 8
    
    // 获取其他函数
    auto multiply_sym = engine.Lookup("multiply");
    auto multiply_fn = multiply_sym->toAddrAndCast<double(*)(double, double)>();
    std::cout << "3.14 * 2.0 = " << multiply_fn(3.14, 2.0) << std::endl;
}
```

### Python API 示例

```python
from tvm_ffi_orcjit import OrcJIT

# 创建 JIT 引擎
jit = OrcJIT()

# 编译 C 源码
c_source = """
int add(int a, int b) {
    return a + b;
}

int factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
"""

jit.add_module_from_source(c_source, "math_ops.c", "c")

# 获取函数并调用
add = jit.get_function("add")
print(add(10, 20))  # 输出: 30

factorial = jit.get_function("factorial")
print(factorial(5))  # 输出: 120
```

## FFI Function 集成

ORCJIT 编译的函数可以自动包装为 FFI `Function` 对象，与 FFI 系统无缝集成。

**C++ 示例：注册 JIT 函数到 FFI 全局表：**
```cpp
#include <tvm/ffi/addon/orcjit/orcjit.h>
#include <tvm/ffi/ffi.h>

using namespace tvm::ffi;

TVM_FFI_REGISTER_GLOBAL("orcjit.compile_and_register")
    .set_body([](TVM_FFI_ARGS args, TVM_FFI_RET rv) {
        std::string source = args[0].cast<std::string>();
        std::string func_name = args[1].cast<std::string>();
        std::string register_name = args[2].cast<std::string>();
        
        static auto jit = orcjit::OrcJIT::Create().value();
        
        // 添加模块
        auto err = jit.AddModuleFromSource(source, "jit_module.c", orcjit::SourceKind::C);
        TVM_FFI_CHECK(!err);
        
        // 查找符号
        auto sym = jit.Lookup(func_name);
        TVM_FFI_CHECK(sym);
        
        // 将函数指针包装为 FFI Function（通过 FFI 类型系统）
        // 实际中会根据函数签名生成适配代码
        using JitFunc = int(*)(int, int);
        auto func_ptr = sym->toAddrAndCast<JitFunc>();
        
        // 注册为 FFI 全局函数
        TVM_FFI_REGISTER_GLOBAL(register_name)
            .set_body([func_ptr](TVM_FFI_ARGS args, TVM_FFI_RET ret) {
                int a = args[0].cast<int>();
                int b = args[1].cast<int>();
                ret = func_ptr(a, b);
            });
        
        rv = true;
    });
```

**Python 示例：动态编译并注册函数：**
```python
from tvm_ffi import get_global_func
from tvm_ffi_orcjit import OrcJIT

jit = OrcJIT()

# JIT 编译一个专用的矩阵乘法内核
matmul_source = """
void matmul_4x4(const float* A, const float* B, float* C) {
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            float sum = 0.0f;
            for (int k = 0; k < 4; k++) {
                sum += A[i*4 + k] * B[k*4 + j];
            }
            C[i*4 + j] = sum;
        }
    }
}
"""

jit.add_module_from_source(matmul_source, "matmul.c", "c")

# 获取 JIT 函数
matmul_4x4 = jit.get_function("matmul_4x4")

# 可以像普通 FFI 函数一样使用
import numpy as np
A = np.random.randn(4, 4).astype(np.float32)
B = np.random.randn(4, 4).astype(np.float32)
C = np.zeros((4, 4), dtype=np.float32)

# 通过 ctypes 传递指针
matmul_4x4(A.ctypes.data, B.ctypes.data, C.ctypes.data)

# 验证
np.testing.assert_allclose(C, A @ B, rtol=1e-6)
print("JIT matmul passed!")
```

## 外部符号解析

ORCJIT 支持在 JIT 编译的代码中调用宿主进程（host process）或其他 JIT 模块中定义的符号。

**C++ 示例：JIT 代码调用外部函数：**
```cpp
#include <tvm/ffi/addon/orcjit/orcjit.h>
#include <cmath>

using namespace tvm::ffi;

// 宿主进程中定义的函数，供 JIT 代码调用
extern "C" double host_sqrt(double x) {
    return std::sqrt(x);
}

extern "C" void host_printf(const char* msg) {
    std::cout << "[JIT] " << msg << std::endl;
}

void external_symbol_example() {
    auto jit = orcjit::OrcJIT::Create().value();
    
    // 注册外部符号供 JIT 模块使用
    jit.RegisterSymbol("host_sqrt", reinterpret_cast<void*>(&host_sqrt));
    jit.RegisterSymbol("host_printf", reinterpret_cast<void*>(&host_printf));
    
    // JIT 代码调用宿主函数
    std::string source = R"(
        extern double host_sqrt(double x);
        extern void host_printf(const char* msg);
        
        double compute_hypotenuse(double a, double b) {
            host_printf("Computing hypotenuse...");
            return host_sqrt(a*a + b*b);
        }
    )";
    
    jit.AddModuleFromSource(source, "external_demo.c", orcjit::SourceKind::C).value();
    
    auto hypotenuse = jit.Lookup("compute_hypotenuse")
        ->toAddrAndCast<double(*)(double, double)>();
    
    double result = hypotenuse(3.0, 4.0);
    std::cout << "hypotenuse(3, 4) = " << result << std::endl;  // 输出: 5.0
}
```

**C++ 示例：JIT 模块间相互调用：**
```cpp
void inter_module_example() {
    auto jit = orcjit::OrcJIT::Create().value();
    
    // 模块 1：基础工具函数
    std::string module1 = R"(
        int square(int x) { return x * x; }
    )";
    
    // 模块 2：调用模块 1 中的函数
    std::string module2 = R"(
        extern int square(int x);
        
        int sum_of_squares(int a, int b) {
            return square(a) + square(b);
        }
    )";
    
    jit.AddModuleFromSource(module1, "module1.c", orcjit::SourceKind::C).value();
    jit.AddModuleFromSource(module2, "module2.c", orcjit::SourceKind::C).value();
    
    auto sum_sq = jit.Lookup("sum_of_squares")
        ->toAddrAndCast<int(*)(int, int)>();
    
    std::cout << "3² + 4² = " << sum_sq(3, 4) << std::endl;  // 输出: 25
}
```

## C++ 源码支持

ORCJIT 支持编译 C++ 源码，可使用 C++ 标准库和特性。

**C++ 示例：JIT 编译 C++ 代码：**
```cpp
#include <tvm/ffi/addon/orcjit/orcjit.h>

using namespace tvm::ffi;

void jit_cpp_example() {
    auto jit = orcjit::OrcJIT::Create().value();
    
    std::string cpp_source = R"(
        #include <vector>
        #include <algorithm>
        #include <numeric>
        
        extern "C" double vector_sum(const double* data, int n) {
            std::vector<double> v(data, data + n);
            return std::accumulate(v.begin(), v.end(), 0.0);
        }
        
        extern "C" void vector_sort(double* data, int n) {
            std::sort(data, data + n);
        }
    )";
    
    // 指定为 C++ 源码
    jit.AddModuleFromSource(cpp_source, "cpp_module.cpp", orcjit::SourceKind::Cpp).value();
    
    auto vec_sum = jit.Lookup("vector_sum")
        ->toAddrAndCast<double(*)(const double*, int)>();
    
    double data[] = {3.0, 1.0, 4.0, 1.0, 5.0, 9.0};
    double sum = vec_sum(data, 6);
    std::cout << "Sum: " << sum << std::endl;  // 输出: 23.0
}
```

## CUDA 源码编译（需要 CUDA 支持）

当系统安装 CUDA Toolkit 时，ORCJIT 可以在运行时编译 CUDA 源码。

**C++ 示例：运行时编译 CUDA 内核：**
```cpp
#include <tvm/ffi/addon/orcjit/orcjit.h>
#include <tvm/ffi/extra/cuda/cubin_launcher.h>

using namespace tvm::ffi;

void jit_cuda_example() {
    auto jit = orcjit::OrcJIT::Create().value();
    
    // CUDA 内核源码
    std::string cuda_source = R"(
        __global__ void vector_add_kernel(const float* a, const float* b, float* c, int n) {
            int idx = blockIdx.x * blockDim.x + threadIdx.x;
            if (idx < n) {
                c[idx] = a[idx] + b[idx];
            }
        }
        
        // 主机端启动函数
        extern "C" void launch_vector_add(const float* a, const float* b, float* c, int n) {
            int block = 256;
            int grid = (n + block - 1) / block;
            vector_add_kernel<<<grid, block>>>(a, b, c, n);
            cudaDeviceSynchronize();
        }
    )";
    
    // 编译 CUDA 源码
    auto err = jit.AddModuleFromSource(
        cuda_source,
        "vector_add.cu",
        orcjit::SourceKind::CUDA
    );
    TVM_FFI_CHECK(!err) << "CUDA compilation failed";
    
    // 获取主机端启动函数
    auto launch_fn = jit.Lookup("launch_vector_add")
        ->toAddrAndCast<void(*)(const float*, const float*, float*, int)>();
    
    // 使用（需要先分配 CUDA 设备内存）
    // launch_fn(d_a, d_b, d_c, n);
}
```

**Python 示例：JIT 编译 CUDA 内核：**
```python
from tvm_ffi_orcjit import OrcJIT
import cupy as cp

jit = OrcJIT()

cuda_source = """
__global__ void saxpy_kernel(float a, const float* x, float* y, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        y[idx] = a * x[idx] + y[idx];
    }
}

extern "C" void saxpy(float a, const float* x, float* y, int n) {
    int block = 256;
    int grid = (n + block - 1) / block;
    saxpy_kernel<<<grid, block>>>(a, x, y, n);
    cudaDeviceSynchronize();
}
"""

jit.add_module_from_source(cuda_source, "saxpy.cu", "cuda")
saxpy = jit.get_function("saxpy")

# 使用 CuPy 数组
n = 1 << 20
a = 2.0
x = cp.random.rand(n, dtype=cp.float32)
y = cp.random.rand(n, dtype=cp.float32)
y_orig = y.copy()

saxpy(a, x.data.ptr, y.data.ptr, n)

# 验证
cp.testing.assert_allclose(y, a * x + y_orig, rtol=1e-6)
print("JIT CUDA saxpy passed!")
```

## 内存管理器

ORCJIT 扩展提供自定义内存管理器，控制 JIT 代码的内存分配和权限设置。

```cpp
#include <tvm/ffi/addon/orcjit/memory_manager.h>

// 创建带自定义内存管理器的 JIT
auto mem_mgr = std::make_unique<orcjit::SectionMemoryManager>();

// 配置内存权限（代码段可执行，数据段可写）
auto jit = orcjit::OrcJIT::Builder()
    .setMemoryManager(std::move(mem_mgr))
    .setOptLevel(orcjit::OptLevel::O3)  // 优化级别
    .create();
```

## 错误处理

ORCJIT 使用 LLVM 的 `Expected<T>` 模式进行错误处理，TVM FFI 将其封装为异常返回。

**C++ 示例：完善的错误处理：**
```cpp
#include <tvm/ffi/addon/orcjit/orcjit.h>

using namespace tvm::ffi;

void safe_jit_compile(const std::string& source) {
    auto jit = orcjit::OrcJIT::Create();
    if (!jit) {
        // JIT 引擎创建失败
        std::cerr << "Failed to create ORCJIT: "
                  << toString(jit.takeError()) << std::endl;
        return;
    }
    
    auto err = jit->AddModuleFromSource(source, "test.c", orcjit::SourceKind::C);
    if (err) {
        // 编译错误（含源码位置信息）
        std::cerr << "Compilation error:\n"
                  << toString(std::move(err)) << std::endl;
        return;
    }
    
    auto sym = jit->Lookup("my_function");
    if (!sym) {
        // 符号未找到
        std::cerr << "Symbol not found: "
                  << toString(sym.takeError()) << std::endl;
        return;
    }
    
    // 使用符号...
}
```

**Python 示例：异常捕获：**
```python
from tvm_ffi_orcjit import OrcJIT
import traceback

jit = OrcJIT()

# 有语法错误的源码
bad_source = """
int broken_func(int a, int b) {
    return a + b  // 缺少分号
}
"""

try:
    jit.add_module_from_source(bad_source, "bad.c", "c")
except Exception as e:
    print(f"Compilation failed as expected: {e}")

# 查找不存在的符号
try:
    jit.get_function("nonexistent")
except Exception as e:
    print(f"Symbol lookup failed as expected: {e}")
```

## 应用场景

ORCJIT 扩展特别适合以下场景：

| 场景 | 说明 |
|------|------|
| **内核特化** | 根据运行时参数生成专用计算内核（如循环展开、向量化） |
| **动态优化** | 基于性能分析结果，运行时重新编译热点函数 |
| **表达式编译** | 将用户 DSL/AST 编译为机器码（如 TVM Relay） |
| **算子融合** | 运行时融合多个算子，减少内核启动开销 |
| **模板元编程替代** | 避免 C++ 模板编译爆炸，运行时生成实例 |
| **脚本化扩展** | 用户可在 Python 中写 C 代码，即时编译运行 |

## 优化级别配置

ORCJIT 支持多种优化级别：

```cpp
orcjit::OptLevel::O0  // 无优化（最快编译，适合调试）
orcjit::OptLevel::O1  // 基础优化
orcjit::OptLevel::O2  // 标准优化（推荐）
orcjit::OptLevel::O3  // 激进优化（最快运行，最慢编译）
```

**C++ 配置：**
```cpp
auto jit = orcjit::OrcJIT::Builder()
    .setOptLevel(orcjit::OptLevel::O3)
    .setFastMath(true)        // 启用快速数学运算（浮点优化）
    .setVerbose(false)        // 关闭详细输出
    .create();
```

**Python 配置：**
```python
from tvm_ffi_orcjit import OrcJIT, OptLevel

jit = OrcJIT(opt_level=OptLevel.O3, fast_math=True)
```

## 源码引用

- `addons/tvm_ffi_orcjit/include/tvm/ffi/addon/orcjit/orcjit.h` - ORCJIT 主接口
- `addons/tvm_ffi_orcjit/include/tvm/ffi/addon/orcjit/memory_manager.h` - 内存管理器
- `addons/tvm_ffi_orcjit/include/tvm/ffi/addon/orcjit/symbol_resolver.h` - 符号解析器
- `addons/tvm_ffi_orcjit/src/orcjit.cc` - 核心实现

---

**导航：**
- [上一章：08 - CUDA 支持](08-cuda-support.md)
- [返回目录](README.md)
- [下一章：10 - DLPack 集成](10-dlpack-integration.md)
