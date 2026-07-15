---
title: "08 - CUDA 支持"
date: 2026-07-05
source: "spec:create-tvm-ffi-wiki-tutorial"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/01-agent-protocols-interfaces/tvm-ffi-wiki/08-cuda-support.toml"
tags: [tvm-ffi, ffi, python, cuda, jit, dlpack]
---
# CUDA 支持

TVM FFI 提供了原生 CUDA 支持，包括预编译 CUBIN 内核启动、设备上下文管理、流（Stream）集成等功能。CUDA 相关头文件位于 `extra/cuda/` 目录下，作为可选扩展模块提供。

## 前置条件

- CUDA Toolkit 11.0+
- NVIDIA GPU 驱动
- 编译时启用 CUDA 支持（CMake 选项 `TVM_FFI_USE_CUDA=ON`）
- C++17 或更高版本

## CUDA 架构概览

```
extra/cuda/
├── base.h           # CUDA 基础类型定义
├── device_guard.h   # RAII 设备上下文守卫
├── cubin_launcher.h # CUBIN 内核加载与启动
└── stream.h         # CUDA 流封装（可选）

internal/
└── unified_api.h    # 跨设备统一 API
```

## CUDA 基础类型（base.h）

`extra/cuda/base.h` 定义了与 CUDA 运行时 API 交互的基础类型和错误检查宏。

**C++ 示例：**
```cpp
#include <tvm/ffi/extra/cuda/base.h>
#include <cuda_runtime.h>

using namespace tvm::ffi;

// CUDA 错误检查
void check_cuda_error(cudaError_t err) {
    TVM_FFI_CUDA_CALL(err);  // 自动检查并抛出异常
}

// 设备属性查询
int get_device_count() {
    int count = 0;
    TVM_FFI_CUDA_CALL(cudaGetDeviceCount(&count));
    return count;
}
```

## Device Guard - 设备上下文管理

`extra/cuda/device_guard.h` 提供 RAII 风格的设备守卫，确保 CUDA 内核在正确的设备上执行，离开作用域时自动恢复原设备。

**C++ 示例：**
```cpp
#include <tvm/ffi/extra/cuda/device_guard.h>
#include <tvm/ffi/extra/cuda/cubin_launcher.h>
#include <cuda_runtime.h>

using namespace tvm::ffi;

// 在指定设备上执行操作
void run_on_device(int device_id) {
    // 构造时切换到 device_id，析构时自动恢复
    cuda::DeviceGuard guard(device_id);
    
    // 此时当前设备为 device_id
    int current_dev;
    cudaGetDevice(&current_dev);
    // current_dev == device_id
    
    // 分配设备内存
    float* d_data;
    cudaMalloc(&d_data, 1024 * sizeof(float));
    
    // 启动内核等操作...
    
    // guard 析构时自动恢复到之前的设备
}

// 嵌套设备切换
void nested_device_example() {
    cuda::DeviceGuard outer(0);  // 切换到设备 0
    
    {
        cuda::DeviceGuard inner(1);  // 切换到设备 1
        // 在设备 1 上操作
    }  // 恢复到设备 0
    
    // 回到设备 0 继续操作
}
```

**Python 示例：**
```python
from tvm_ffi.contrib.cuda import DeviceGuard
import pycuda.driver as cuda

# Python 侧设备守卫
with DeviceGuard(0):
    # 在设备 0 上分配内存、执行内核
    pass
# 自动恢复到之前的设备
```

## CUBIN Launcher - 预编译内核启动

`extra/cuda/cubin_launcher.h` 提供加载和启动预编译 CUDA 二进制（.cubin）文件的能力，支持网格/块/流配置。

### CUBIN 内核加载流程

1. 从磁盘加载 .cubin 文件
2. 按名称查找内核函数
3. 配置启动参数（gridDim, blockDim, sharedMem, stream）
4. 启动内核
5. 同步并检查错误

**C++ 示例：加载并启动 CUBIN 内核：**
```cpp
#include <tvm/ffi/extra/cuda/cubin_launcher.h>
#include <tvm/ffi/extra/cuda/device_guard.h>
#include <tvm/ffi/ffi.h>

using namespace tvm::ffi;

// CUDA 核函数（提前编译为 .cubin）
// __global__ void vector_add(float* a, float* b, float* c, int n) {
//     int idx = blockIdx.x * blockDim.x + threadIdx.x;
//     if (idx < n) c[idx] = a[idx] + b[idx];
// }

TVM_FFI_REGISTER_GLOBAL("cuda.launch_vector_add")
    .set_body([](TVM_FFI_ARGS args, TVM_FFI_RET rv) {
        // 参数解析
        float* d_a = static_cast<float*>(args[0].cast<void*>());
        float* d_b = static_cast<float*>(args[1].cast<void*>());
        float* d_c = static_cast<float*>(args[2].cast<void*>());
        int n = args[3].cast<int>();
        int device_id = args[4].cast<int>();
        std::string cubin_path = args[5].cast<std::string>();
        
        // 设置设备上下文
        cuda::DeviceGuard guard(device_id);
        
        // 加载 CUBIN 模块
        cuda::CubinLauncher launcher;
        launcher.Load(cubin_path);
        
        // 获取内核函数
        auto kernel = launcher.GetFunction("vector_add");
        
        // 启动配置
        int block_size = 256;
        int grid_size = (n + block_size - 1) / block_size;
        
        // 设置内核参数
        kernel.SetArgs(d_a, d_b, d_c, n);
        
        // 启动内核
        kernel.Launch(
            dim3(grid_size),   // gridDim
            dim3(block_size),  // blockDim
            0,                 // sharedMem bytes
            nullptr            // stream (默认流)
        );
        
        // 同步等待完成
        TVM_FFI_CUDA_CALL(cudaDeviceSynchronize());
        
        rv = true;
    });
```

**Python 示例：从 Python 调用 CUDA 内核启动：**
```python
import numpy as np
import pycuda.driver as cuda
import pycuda.autoinit
from tvm_ffi import get_global_func

# 编译 CUDA 内核为 CUBIN（提前用 nvcc 编译）
# nvcc -cubin -arch=sm_80 vector_add.cu -o vector_add.cubin

# 准备数据
n = 1024
a = np.random.rand(n).astype(np.float32)
b = np.random.rand(n).astype(np.float32)

# 分配设备内存
d_a = cuda.mem_alloc(a.nbytes)
d_b = cuda.mem_alloc(b.nbytes)
d_c = cuda.mem_alloc(a.nbytes)

cuda.memcpy_htod(d_a, a)
cuda.memcpy_htod(d_b, b)

# 调用 C++ 注册的 CUDA 启动函数
launch_vector_add = get_global_func("cuda.launch_vector_add")
launch_vector_add(
    int(d_a),      # 设备指针
    int(d_b),
    int(d_c),
    n,
    0,             # device_id
    "./vector_add.cubin"
)

# 取回结果
c = np.empty_like(a)
cuda.memcpy_dtoh(c, d_c)

# 验证
np.testing.assert_allclose(c, a + b)
print("CUDA kernel executed successfully!")
```

## CUDA Stream 集成

CUDA 流用于实现异步并行执行，CUBIN Launcher 支持传入自定义流。

**C++ 示例：使用流进行异步执行：**
```cpp
#include <tvm/ffi/extra/cuda/cubin_launcher.h>
#include <tvm/ffi/ffi.h>

using namespace tvm::ffi;

TVM_FFI_REGISTER_GLOBAL("cuda.launch_with_stream")
    .set_body([](TVM_FFI_ARGS args, TVM_FFI_RET rv) {
        cudaStream_t stream = static_cast<cudaStream_t>(args[0].cast<void*>());
        std::string cubin_path = args[1].cast<std::string>();
        
        cuda::CubinLauncher launcher;
        launcher.Load(cubin_path);
        
        auto kernel = launcher.GetFunction("my_kernel");
        
        // 配置参数
        float* d_input = static_cast<float*>(args[2].cast<void*>());
        float* d_output = static_cast<float*>(args[3].cast<void*>());
        int size = args[4].cast<int>();
        
        kernel.SetArgs(d_input, d_output, size);
        
        // 在指定流上启动内核（异步）
        kernel.Launch(
            dim3((size + 255) / 256),
            dim3(256),
            0,
            stream  // 使用自定义流
        );
        
        rv = true;
    });

// 多流并行示例
void multi_stream_example() {
    cuda::DeviceGuard guard(0);
    
    cudaStream_t stream1, stream2;
    cudaStreamCreate(&stream1);
    cudaStreamCreate(&stream2);
    
    cuda::CubinLauncher launcher;
    launcher.Load("./multi_kernel.cubin");
    
    auto kernel_a = launcher.GetFunction("kernel_a");
    auto kernel_b = launcher.GetFunction("kernel_b");
    
    // 在不同流上并行启动
    kernel_a.SetArgs(/* args */);
    kernel_a.Launch(dim3(10), dim3(256), 0, stream1);
    
    kernel_b.SetArgs(/* args */);
    kernel_b.Launch(dim3(10), dim3(256), 0, stream2);
    
    // 等待两个流完成
    cudaStreamSynchronize(stream1);
    cudaStreamSynchronize(stream2);
    
    cudaStreamDestroy(stream1);
    cudaStreamDestroy(stream2);
}
```

**Python 示例：使用 CUDA 流：**
```python
from tvm_ffi import get_global_func
import pycuda.driver as cuda

# 创建流
stream1 = cuda.Stream()
stream2 = cuda.Stream()

launch_fn = get_global_func("cuda.launch_with_stream")

# 在不同流上异步启动
launch_fn(int(stream1), "./kernel.cubin", d_in1, d_out1, size)
launch_fn(int(stream2), "./kernel.cubin", d_in2, d_out2, size)

# 异步内存拷贝与流同步
cuda.memcpy_htod_async(d_in1, h_in1, stream1)
stream1.synchronize()
stream2.synchronize()
```

## Unified API - 跨设备统一接口

`internal/unified_api.h` 提供跨 CPU/CUDA 设备的统一抽象层，简化异构编程。

**C++ 示例：统一设备接口：**
```cpp
#include <tvm/ffi/internal/unified_api.h>
#include <tvm/ffi/container/tensor.h>

using namespace tvm::ffi;

// 设备无关的张量处理
void process_tensor_unified(Tensor tensor) {
    auto device = tensor->device;
    
    if (device.device_type == kDLCPU) {
        // CPU 路径
        float* data = static_cast<float*>(tensor->data);
        // 直接在 CPU 上处理
    } else if (device.device_type == kDLCUDA) {
        // CUDA 路径
        cuda::DeviceGuard guard(device.device_id);
        // 启动 CUDA 内核处理
    }
}
```

## 与 FFI Function 集成

CUDA 操作可以注册为 FFI 全局函数，供 Python 端透明调用。

**完整 C++ 示例：CUDA 向量加法模块**
```cpp
// cuda_add_module.cc
#include <tvm/ffi/ffi.h>
#include <tvm/ffi/extra/cuda/base.h>
#include <tvm/ffi/extra/cuda/device_guard.h>
#include <tvm/ffi/extra/cuda/cubin_launcher.h>
#include <tvm/ffi/container/tensor.h>

using namespace tvm::ffi;

TVM_FFI_REGISTER_GLOBAL("cuda.vector_add")
    .set_body([](TVM_FFI_ARGS args, TVM_FFI_RET rv) {
        Tensor a = args[0].cast<Tensor>();
        Tensor b = args[1].cast<Tensor>();
        Tensor out = args[2].cast<Tensor>();
        std::string cubin_path = args[3].cast<std::string>();
        
        // 验证设备一致性
        TVM_FFI_CHECK(a->device.device_type == kDLCUDA);
        TVM_FFI_CHECK(a->device.device_id == b->device.device_id);
        
        cuda::DeviceGuard guard(a->device.device_id);
        
        cuda::CubinLauncher launcher;
        launcher.Load(cubin_path);
        auto kernel = launcher.GetFunction("vector_add");
        
        int n = 1;
        for (int i = 0; i < a->ndim; i++) n *= a->shape[i];
        int block = 256;
        int grid = (n + block - 1) / block;
        
        kernel.SetArgs(
            static_cast<float*>(a->data),
            static_cast<float*>(b->data),
            static_cast<float*>(out->data),
            n
        );
        
        kernel.Launch(dim3(grid), dim3(block), 0, nullptr);
        TVM_FFI_CUDA_CALL(cudaDeviceSynchronize());
    });
```

**Python 示例：端到端 CUDA 调用**
```python
import numpy as np
import cupy as cp
from tvm_ffi import get_global_func

# 使用 CuPy 分配 CUDA 张量（零拷贝通过 DLPack）
n = 1 << 20
a_cp = cp.random.rand(n, dtype=cp.float32)
b_cp = cp.random.rand(n, dtype=cp.float32)
out_cp = cp.empty_like(a_cp)

# 调用 FFI 注册的 CUDA 函数
cuda_vector_add = get_global_func("cuda.vector_add")
cuda_vector_add(a_cp, b_cp, out_cp, "./vector_add.cubin")

# 验证结果
cp.testing.assert_allclose(out_cp, a_cp + b_cp, rtol=1e-5)
print(f"CUDA vector add passed: {n} elements")
```

## 构建配置

**CMakeLists.txt 中启用 CUDA：**
```cmake
option(TVM_FFI_USE_CUDA "Build with CUDA support" ON)

if(TVM_FFI_USE_CUDA)
    enable_language(CUDA)
    find_package(CUDAToolkit REQUIRED)
    
    target_link_libraries(tvm_ffi INTERFACE CUDA::cudart)
    target_compile_definitions(tvm_ffi INTERFACE TVM_FFI_USE_CUDA=1)
endif()
```

**Python 包安装（含 CUDA 支持）：**
```bash
# 编辑模式安装
pip install -e ".[cuda]"

# 或通过 uv
uv pip install -e ".[cuda]"
```

## 常见问题

**Q: CUBIN 架构不匹配怎么办？**
A: 确保编译 CUBIN 时使用正确的 `-arch=sm_XX` 参数，与目标 GPU 架构匹配（如 sm_80 对应 A100，sm_89 对应 RTX 4090）。

**Q: 忘记设置 Device Guard 会怎样？**
A: 内核会在当前线程的当前设备上启动，可能导致在错误设备上执行或崩溃。始终使用 `DeviceGuard` RAII 守卫。

**Q: 如何处理 CUDA 错误？**
A: 使用 `TVM_FFI_CUDA_CALL` 宏包装所有 CUDA API 调用，出错时会自动抛出包含错误信息的 C++ 异常。

## 源码引用

- `extra/cuda/base.h` - CUDA 基础类型与错误检查
- `extra/cuda/device_guard.h` - RAII 设备上下文守卫
- `extra/cuda/cubin_launcher.h` - CUBIN 内核加载与启动
- `internal/unified_api.h` - 跨设备统一 API

---

**导航：**
- [上一章：07 - Python 绑定机制](07-python-bindings.md)
- [返回目录](README.md)
- [下一章：09 - ORCJIT 扩展](09-orcjit-extension.md)
