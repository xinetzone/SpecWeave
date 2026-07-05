---
title: "10 - DLPack 集成"
date: 2026-07-05
source: "spec:create-tvm-ffi-wiki-tutorial"
tags: [tvm-ffi, ffi, python, cuda, jit, dlpack]
---

# DLPack 集成

DLPack 是一个开源的张量交换标准，定义了跨框架张量内存表示的中立协议。TVM FFI 的 `Tensor` 容器原生支持 DLPack 规范，实现与 NumPy、PyTorch、CuPy、TensorFlow 等主流框架的零拷贝张量交换。

## 什么是 DLPack

DLPack（Deep Learning Pack）是由 DMLC 社区发起的开放标准，提供：

- **稳定的内存布局**：标准化的 DLTensor 结构
- **设备无关**：支持 CPU、CUDA、ROCm、OpenCL 等多种设备
- **零拷贝交换**：共享数据指针，无需内存复制
- **生命周期管理**：引用计数机制管理张量内存
- **跨语言**：C 头文件定义，可被任意语言绑定

DLPack 是一种**协议（Protocol）**，而非 API 或 ABI——它定义了张量在内存中的标准布局约定。相关概念参见 [Interface/API/ABI/Protocol 教程 - Protocol 章节](../interface-api-abi-protocol-wiki/04-protocol.md)。

## 目录结构

```
container/
└── tensor.h          # Tensor 容器，DLPack 兼容实现

addons/
└── torch_c_dlpack_ext/  # PyTorch DLPack C 接口扩展
    ├── include/
    ├── src/
    └── python/
```

## DLTensor 核心结构

DLPack 的核心是 `DLTensor` 结构体，定义了张量的内存布局：

```c
// DLPack 标准结构（简化版）
typedef enum {
  kDLCPU = 1,
  kDLCUDA = 2,
  kDLCUDAHost = 3,
  kDLROCM = 10,
  kDLROCMHost = 11,
  kDLOpenCL = 4,
  kDLVulkan = 7,
  kDLMetal = 8,
  kDLVPI = 9,
  kDLExtDev = 12
} DLDeviceType;

typedef struct {
  DLDeviceType device_type;
  int device_id;
} DLDevice;

typedef enum {
  kDLInt = 0,
  kDLUInt = 1,
  kDLFloat = 2,
  kDLBfloat = 4
} DLDataTypeCode;

typedef struct {
  uint8_t code;       // DLDataTypeCode
  uint8_t bits;       // 位宽：8, 16, 32, 64
  uint16_t lanes;     // 向量通道数（通常为 1）
} DLDataType;

typedef struct {
  void* data;         // 数据指针
  DLDevice device;    // 设备信息
  int ndim;           // 维度数
  DLDataType dtype;   // 数据类型
  int64_t* shape;     // 形状数组
  int64_t* strides;   // 步长数组（NULL 表示紧凑行优先）
  uint64_t byte_offset; // 字节偏移
} DLTensor;
```

## TVM FFI Tensor 与 DLPack

TVM FFI 的 `Tensor` 类（定义于 `container/tensor.h`）直接封装 DLPack 兼容的内存布局，可以零拷贝导出为 DLTensor，也可以从 DLTensor 零拷贝导入。

**C++ 示例：创建 Tensor 并访问 DLTensor：**
```cpp
#include <tvm/ffi/container/tensor.h>
#include <tvm/ffi/ffi.h>
#include <vector>

using namespace tvm::ffi;

// 创建 CPU Tensor
void create_tensor_example() {
    // 创建形状为 [2, 3] 的 float32 CPU 张量
    std::vector<int64_t> shape = {2, 3};
    Tensor t = Tensor::Empty(shape, DLDataType{kDLFloat, 32, 1}, DLDevice{kDLCPU, 0});
    
    // 访问底层 DLTensor
    DLTensor* dl_tensor = t->operator->();
    
    // 通过 DLTensor 访问元数据
    std::cout << "ndim: " << dl_tensor->ndim << std::endl;
    std::cout << "device_type: " << dl_tensor->device.device_type << std::endl;
    std::cout << "dtype bits: " << (int)dl_tensor->dtype.bits << std::endl;
    
    // 访问数据指针
    float* data = static_cast<float*>(dl_tensor->data);
    for (int i = 0; i < 6; i++) {
        data[i] = static_cast<float>(i);
    }
}

// 从已有 DLTensor 包装（零拷贝）
void wrap_existing_dltensor() {
    // 假设已有外部创建的 DLTensor
    float raw_data[6] = {1, 2, 3, 4, 5, 6};
    int64_t shape[] = {2, 3};
    
    DLTensor dl_tensor;
    dl_tensor.data = raw_data;
    dl_tensor.device = {kDLCPU, 0};
    dl_tensor.ndim = 2;
    dl_tensor.dtype = {kDLFloat, 32, 1};
    dl_tensor.shape = shape;
    dl_tensor.strides = nullptr;  // 紧凑行优先
    dl_tensor.byte_offset = 0;
    
    // 零拷贝包装为 TVM FFI Tensor
    Tensor t = Tensor::FromDLPack(&dl_tensor);
    // 注意：此时 t 不拥有数据内存，生命周期需用户管理
}
```

## 设备类型

TVM FFI 支持的主要设备类型：

| 设备类型 | 枚举值 | 说明 |
|---------|--------|------|
| `kDLCPU` | 1 | 主机 CPU 内存 |
| `kDLCUDA` | 2 | NVIDIA GPU 全局内存 |
| `kDLCUDAHost` | 3 | CUDA 锁页主机内存 |
| `kDLROCM` | 10 | AMD GPU 内存 |
| `kDLOpenCL` | 4 | OpenCL 设备内存 |
| `kDLMetal` | 8 | Apple Metal 缓冲 |
| `kDLVulkan` | 7 | Vulkan 缓冲 |

**C++ 示例：在不同设备上创建 Tensor：**
```cpp
#include <tvm/ffi/container/tensor.h>
#include <tvm/ffi/extra/cuda/base.h>
#include <tvm/ffi/extra/cuda/device_guard.h>

using namespace tvm::ffi;

void create_tensor_on_devices() {
    // CPU 张量
    Tensor cpu_tensor = Tensor::Empty({1024}, {kDLFloat, 32, 1}, {kDLCPU, 0});
    
#ifdef TVM_FFI_USE_CUDA
    // CUDA 张量（设备 0）
    cuda::DeviceGuard guard(0);
    Tensor gpu_tensor = Tensor::Empty({1024, 1024}, {kDLFloat, 32, 1}, {kDLCUDA, 0});
    
    // CUDA 主机锁页内存
    Tensor pinned_tensor = Tensor::Empty({1024}, {kDLFloat, 32, 1}, {kDLCUDAHost, 0});
#endif
}
```

## Python 端 NumPy 互操作

Python 端 `Tensor` 自动实现 NumPy 的 `__array__` 协议，可以直接与 NumPy ndarray 零拷贝（CPU 张量）或自动拷贝（GPU 张量）转换。

**Python 示例：Tensor 与 NumPy 转换：**
```python
import numpy as np
from tvm_ffi import Tensor

# 从 NumPy 数组创建 Tensor（零拷贝，共享内存）
np_arr = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float32)
t = Tensor.from_numpy(np_arr)

# 修改 Tensor 会影响 NumPy 数组（因为共享内存）
t_data = t.numpy()
print(t_data)
# [[1. 2. 3.]
#  [4. 5. 6.]]

# 验证共享内存
np_arr[0, 0] = 100.0
print(t.numpy())
# [[100.   2.   3.]
#  [  4.   5.   6.]]

# 创建新 Tensor 并转为 NumPy
t2 = Tensor.empty((2, 3), dtype="float32", device="cpu")
t2.copy_from(np.ones((2, 3), dtype=np.float32))
print(t2.numpy())
# [[1. 1. 1.]
#  [1. 1. 1.]]

# 直接创建并初始化
t3 = Tensor.from_numpy(np.arange(10, dtype=np.int64))
print(t3.numpy())  # [0 1 2 3 4 5 6 7 8 9]
```

## PyTorch 集成（torch_c_dlpack_ext）

`addons/torch_c_dlpack_ext/` 提供 PyTorch 与 TVM FFI 之间的零拷贝张量交换扩展，使用 PyTorch 的 C 级 DLPack 接口（避免 Python GIL 开销）。

### 安装与配置

```bash
# 编译安装 PyTorch DLPack 扩展
cd addons/torch_c_dlpack_ext
pip install -e .

# 或通过主包的 extras
pip install -e ".[torch]"
```

### C++ API：PyTorch 张量互操作

**C++ 示例：与 PyTorch 张量交换：**
```cpp
#include <tvm/ffi/container/tensor.h>
#include <torch/extension.h>  // PyTorch C++ 扩展头
#include <torch/torch.h>

using namespace tvm::ffi;

// TVM FFI Tensor -> PyTorch Tensor（零拷贝）
torch::Tensor ffi_to_torch(Tensor ffi_tensor) {
    // 使用 DLPack 协议零拷贝转换
    DLManagedTensor* dlmt = ffi_tensor.ToDLPack();
    torch::Tensor torch_tensor = torch::fromDLPack(dlmt);
    return torch_tensor;
}

// PyTorch Tensor -> TVM FFI Tensor（零拷贝）
Tensor torch_to_ffi(torch::Tensor torch_tensor) {
    // 获取 DLPack 表示
    DLManagedTensor* dlmt = torch_tensor.toDLPack();
    // 包装为 TVM FFI Tensor（接管内存管理）
    return Tensor::FromDLPack(dlmt);
}

// 注册 FFI 函数供 Python 调用
TVM_FFI_REGISTER_GLOBAL("dlpack.torch_sin")
    .set_body([](TVM_FFI_ARGS args, TVM_FFI_RET rv) {
        Tensor input = args[0].cast<Tensor>();
        
        // 转为 PyTorch 张量（零拷贝）
        torch::Tensor t_in = ffi_to_torch(input);
        
        // 使用 PyTorch 算子
        torch::Tensor t_out = torch::sin(t_in);
        
        // 转回 TVM FFI Tensor（零拷贝）
        rv = torch_to_ffi(t_out);
    });
```

### Python API：零拷贝交换

**Python 示例：TVM FFI 与 PyTorch 互操作：**
```python
import torch
import numpy as np
from tvm_ffi import Tensor
from tvm_ffi.contrib.torch import from_torch, to_torch

# PyTorch -> TVM FFI（CPU 零拷贝）
torch_t = torch.randn(3, 4, dtype=torch.float32)
ffi_t = from_torch(torch_t)

# 验证零拷贝：修改 ffi_t 会影响 torch_t
ffi_data = ffi_t.numpy()
ffi_data[0, 0] = 42.0
print(torch_t[0, 0])  # tensor(42.) - 同一内存！

# TVM FFI -> PyTorch（零拷贝）
ffi_t2 = Tensor.from_numpy(np.ones((2, 2), dtype=np.float32))
torch_t2 = to_torch(ffi_t2)
print(torch_t2)
# tensor([[1., 1.],
#         [1., 1.]])

# GPU 张量零拷贝交换
if torch.cuda.is_available():
    torch_gpu = torch.randn(1024, device="cuda", dtype=torch.float32)
    ffi_gpu = from_torch(torch_gpu)
    
    # 验证设备类型
    print(ffi_gpu.device.device_type)  # 2 (kDLCUDA)
    print(ffi_gpu.device.device_id)    # 0
    
    # 转回 PyTorch（零拷贝）
    torch_gpu2 = to_torch(ffi_gpu)
    assert torch_gpu.data_ptr() == torch_gpu2.data_ptr()  # 同一指针！
```

**Python 示例：端到端混合框架处理：**
```python
import torch
import numpy as np
from tvm_ffi import get_global_func, Tensor
from tvm_ffi.contrib.torch import from_torch, to_torch

# 假设有 C++ 注册的 TVM FFI CUDA kernel
cuda_vector_add = get_global_func("cuda.vector_add")

# 在 PyTorch 中创建 GPU 张量
n = 1 << 20
a = torch.randn(n, device="cuda", dtype=torch.float32)
b = torch.randn(n, device="cuda", dtype=torch.float32)
c = torch.empty_like(a)

# 零拷贝转为 TVM FFI Tensor
ffi_a = from_torch(a)
ffi_b = from_torch(b)
ffi_c = from_torch(c)

# 调用 CUDA kernel（直接操作 PyTorch 分配的内存！）
cuda_vector_add(ffi_a, ffi_b, ffi_c, "./vector_add.cubin")

# c 已经被修改，无需拷贝回
torch.testing.assert_allclose(c, a + b, rtol=1e-6)
print("PyTorch <-> TVM FFI zero-copy CUDA interop passed!")
```

## CuPy 互操作

CuPy 原生支持 DLPack 协议，可与 TVM FFI CUDA 张量零拷贝交换。

**Python 示例：CuPy 互操作：**
```python
import cupy as cp
from tvm_ffi import Tensor

# CuPy -> TVM FFI（零拷贝）
cp_arr = cp.random.randn(1000, dtype=cp.float32)
ffi_t = Tensor.from_dlpack(cp_arr.toDlpack())

# TVM FFI -> CuPy（零拷贝）
dlpack_capsule = ffi_t.to_dlpack()
cp_arr2 = cp.fromDlpack(dlpack_capsule)

# 验证同一内存
cp_arr[0] = 999.0
print(cp_arr2[0])  # 999.0
```

## 零拷贝保证

### 何时零拷贝

满足以下条件时，张量交换为零拷贝：

| 条件 | 说明 |
|------|------|
| **同一设备** | CPU ↔ CPU，CUDA:0 ↔ CUDA:0 |
| **兼容 dtype** | 双方支持相同的数据类型（如 float32, int64） |
| **兼容布局** | 形状、步长兼容（通常行优先、无步长时最优） |
| **对齐要求** | 数据指针满足双方对齐要求 |

### 何时会发生拷贝

以下情况可能触发数据拷贝：

1. **设备间传输**：CPU ↔ GPU，或不同 GPU 设备之间
2. **dtype 不兼容**：如 float32 ↔ bfloat16 可能需要转换
3. **步长不兼容**：非紧凑张量转为要求紧凑布局的框架
4. **类型升级/降级**：如 int32 ↔ int64 转换

**C++ 示例：检查拷贝必要性：**
```cpp
#include <tvm/ffi/container/tensor.h>

using namespace tvm::ffi;

bool can_zero_copy(const DLTensor& a, const DLTensor& b) {
    // 同一设备
    if (a.device.device_type != b.device.device_type ||
        a.device.device_id != b.device.device_id) {
        return false;
    }
    // 相同 dtype
    if (a.dtype.code != b.dtype.code ||
        a.dtype.bits != b.dtype.bits ||
        a.dtype.lanes != b.dtype.lanes) {
        return false;
    }
    // 相同形状
    if (a.ndim != b.ndim) return false;
    for (int i = 0; i < a.ndim; i++) {
        if (a.shape[i] != b.shape[i]) return false;
    }
    return true;
}
```

## 生命周期与内存管理

DLPack 使用 `DLManagedTensor` 结构管理张量生命周期，包含 deleter 函数指针：

```c
typedef struct DLManagedTensor {
  DLTensor dl_tensor;    // 张量数据
  void* manager_ctx;     // 管理器上下文（如引用计数）
  void (*deleter)(struct DLManagedTensor* self);  // 析构函数
} DLManagedTensor;
```

**C++ 示例：使用 DLManagedTensor 管理生命周期：**
```cpp
#include <tvm/ffi/container/tensor.h>

using namespace tvm::ffi;

void lifecycle_example() {
    // 创建 Tensor（拥有内存）
    Tensor t = Tensor::Empty({1024, 1024}, {kDLFloat, 32, 1}, {kDLCPU, 0});
    
    {
        // 导出为 DLManagedTensor（所有权转移）
        DLManagedTensor* dlmt = t.ToDLPack();
        
        // 此时 dlmt 拥有数据内存，需手动 deleter
        // ... 使用 dlmt ...
        
        // 释放
        dlmt->deleter(dlmt);
    }
    
    // 从 DLManagedTensor 导入（接管所有权）
    // Tensor t2 = Tensor::FromDLPack(dlmt);
    // t2 析构时会自动调用 deleter
}
```

## 高级用法：自定义内存分配

可以通过自定义分配器创建 Tensor，使用外部已分配的内存。

**C++ 示例：使用自定义内存创建 Tensor：**
```cpp
#include <tvm/ffi/container/tensor.h>
#include <cstdlib>

using namespace tvm::ffi;

// 自定义 deleter：free 内存
void custom_deleter(DLManagedTensor* self) {
    free(self->dl_tensor.data);
    free(self->dl_tensor.shape);
    delete self;
}

Tensor create_tensor_with_custom_alloc(const std::vector<int64_t>& shape) {
    auto* dlmt = new DLManagedTensor();
    
    int64_t ndim = shape.size();
    int64_t numel = 1;
    for (auto s : shape) numel *= s;
    
    // 自定义分配（例如使用 cudaMalloc、AVX 对齐分配等）
    void* data = aligned_alloc(64, numel * sizeof(float));
    
    // 复制形状
    int64_t* shape_arr = new int64_t[ndim];
    std::copy(shape.begin(), shape.end(), shape_arr);
    
    dlmt->dl_tensor = {
        data,
        {kDLCPU, 0},
        static_cast<int>(ndim),
        {kDLFloat, 32, 1},
        shape_arr,
        nullptr,  // strides
        0         // byte_offset
    };
    dlmt->manager_ctx = nullptr;
    dlmt->deleter = custom_deleter;
    
    return Tensor::FromDLPack(dlmt);
}
```

## 数据类型映射表

TVM FFI dtype 与常见框架 dtype 对应：

| TVM FFI DLDataType | NumPy dtype | PyTorch dtype | CuPy dtype |
|-------------------|-------------|---------------|------------|
| `{kDLFloat, 32, 1}` | `np.float32` | `torch.float32` | `cp.float32` |
| `{kDLFloat, 64, 1}` | `np.float64` | `torch.float64` | `cp.float64` |
| `{kDLInt, 32, 1}` | `np.int32` | `torch.int32` | `cp.int32` |
| `{kDLInt, 64, 1}` | `np.int64` | `torch.int64` | `cp.int64` |
| `{kDLUInt, 8, 1}` | `np.uint8` | `torch.uint8` | `cp.uint8` |
| `{kDLFloat, 16, 1}` | `np.float16` | `torch.float16` | `cp.float16` |
| `{kDLBfloat, 16, 1}` | - | `torch.bfloat16` | `cp.bfloat16` |

**Python 示例：dtype 转换工具：**
```python
import numpy as np
from tvm_ffi import DataType

def numpy_dtype_to_dlpack(np_dtype):
    """NumPy dtype -> DLDataType"""
    if np_dtype == np.float32:
        return DataType("float32")
    elif np_dtype == np.float64:
        return DataType("float64")
    elif np_dtype == np.int32:
        return DataType("int32")
    elif np_dtype == np.int64:
        return DataType("int64")
    elif np_dtype == np.uint8:
        return DataType("uint8")
    elif np_dtype == np.float16:
        return DataType("float16")
    else:
        raise ValueError(f"Unsupported dtype: {np_dtype}")

# 使用
dt = numpy_dtype_to_dlpack(np.float32)
print(dt.code, dt.bits, dt.lanes)  # 2 32 1
```

## 跨框架流水线示例

**C++ 与 Python 混合：完整跨框架推理流水线：**

C++ 端（注册 CUDA 预处理核函数）：
```cpp
// preprocess_kernels.cc
#include <tvm/ffi/ffi.h>
#include <tvm/ffi/container/tensor.h>

using namespace tvm::ffi;

TVM_FFI_REGISTER_GLOBAL("preprocess.normalize")
    .set_body([](TVM_FFI_ARGS args, TVM_FFI_RET rv) {
        Tensor input = args[0].cast<Tensor>();
        Tensor output = args[1].cast<Tensor>();
        float mean = args[2].cast<float>();
        float std = args[3].cast<float>();
        
        // CUDA 归一化内核
        // launch_normalize_kernel(input, output, mean, std);
        
        rv = true;
    });
```

Python 端（跨框架流水线）：
```python
import torch
import numpy as np
from PIL import Image
from tvm_ffi import get_global_func
from tvm_ffi.contrib.torch import from_torch, to_torch
import torchvision.transforms as T

# 加载图像并使用 PyTorch 预处理
img = Image.open("input.jpg")
transform = T.Compose([
    T.Resize((224, 224)),
    T.ToTensor(),
])
input_tensor = transform(img).unsqueeze(0).cuda()

# 零拷贝转为 TVM FFI Tensor
ffi_input = from_torch(input_tensor)
ffi_output = from_torch(torch.empty_like(input_tensor))

# 调用 C++/CUDA 预处理（零拷贝）
normalize = get_global_func("preprocess.normalize")
normalize(ffi_input, ffi_output, 0.485, 0.229)

# 零拷贝转回 PyTorch 送入模型
model_input = to_torch(ffi_output)
with torch.no_grad():
    output = model(model_input)

# NumPy 后处理
result = output.cpu().numpy()
predictions = np.argmax(result, axis=1)
```

## 源码引用

- `container/tensor.h` - Tensor 容器，DLPack 实现
- `addons/torch_c_dlpack_ext/` - PyTorch C 接口 DLPack 扩展

## 参考

- [DLPack 官方规范](https://github.com/dmlc/dlpack)
- [Interface/API/ABI/Protocol 教程 - Protocol 章节](../interface-api-abi-protocol-wiki/04-protocol.md) - DLPack 作为协议的设计理念

---

**导航：**
- [上一章：09 - ORCJIT 扩展](09-orcjit-extension.md)
- [返回目录](README.md)
- 下一章：11 - 编译构建与项目集成
