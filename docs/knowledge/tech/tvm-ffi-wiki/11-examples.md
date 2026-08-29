---
id: "tvm-ffi-examples"
title: "实战案例"
tags: ["tvm-ffi", "examples", "tutorial", "kernel"]
date: "2026-07-28"
source: "spec:tvm-ffi-wiki-tutorial"
category: "tech"
---

> 📚 **TVM FFI Wiki 教程导航**：
> [首页](00-overview.md) | [目录结构](01-project-structure.md) | [Any类型](02-any-type.md) | [Object系统](03-object-system.md) | [Function](04-function-registry.md) | [容器](05-containers.md) | [反射](06-reflection.md) | [Module](07-module-system.md) | [C++指南](08-cpp-guide.md) | [Python指南](09-python-guide.md) | [构建打包](10-build-packaging.md) | [实战案例](11-examples.md) | [FAQ](12-faq.md) | [源码解析](13-source-analysis.md)

---

# 实战案例

本章通过实际案例演示TVM FFI的典型使用场景，涵盖从简单入门到CUDA Kernel、C ABI跨语言、Tensor互操作等常见开发需求。

## 案例1：Quickstart入门

### 场景
C++端注册计算函数，编译为动态库后Python端加载调用，支持NumPy/PyTorch/CuPy/Paddle等多种Tensor类型。

### C++端代码（add_one_cpu.cc）

```cpp
#include <tvm/ffi/tvm_ffi.h>

namespace tvm_ffi_example_cpu {
void AddOne(tvm::ffi::TensorView x, tvm::ffi::TensorView y) {
  int64_t n = x.size(0);
  float* xd = static_cast<float*>(x.data_ptr());
  float* yd = static_cast<float*>(y.data_ptr());
  for (int64_t i = 0; i < n; ++i) yd[i] = xd[i] + 1;
}
TVM_FFI_DLL_EXPORT_TYPED_FUNC(add_one_cpu, AddOne)
}
```

### CMakeLists.txt（关键部分）

```cmake
find_package(Python COMPONENTS Interpreter REQUIRED)
execute_process(
  COMMAND "${Python_EXECUTABLE}" -m tvm_ffi.config --cmakedir
  OUTPUT_VARIABLE tvm_ffi_ROOT OUTPUT_STRIP_TRAILING_WHITESPACE)
find_package(tvm_ffi CONFIG REQUIRED)

add_library(add_one_cpu SHARED compile/add_one_cpu.cc)
target_link_libraries(add_one_cpu PRIVATE tvm_ffi::header tvm_ffi::shared)
set_target_properties(add_one_cpu PROPERTIES PREFIX "" SUFFIX ".so")
```

### Python端调用

```python
import tvm_ffi, numpy as np
mod = tvm_ffi.load_module("build/add_one_cpu.so")
x = np.array([1,2,3,4,5], dtype=np.float32)
y = np.empty_like(x)
mod.add_one_cpu(x, y)
print(y)  # [2. 3. 4. 5. 6.]
```

### 运行步骤
```bash
mkdir build && cd build
cmake -DEXAMPLE_NAME=compile_cpu .. && cmake --build .
cd .. && python load/load_numpy.py
```

---

## 案例2：CUDA Kernel Library

### 场景
将CUDA Kernel打包为动态库，Python端加载调用，自动Stream同步。

### 核心代码

```cpp
// tvm_ffi_utils.h - 工具宏定义
#include <tvm/ffi/tvm_ffi.h>
#include <tvm/ffi/extra/cuda/device_guard.h>
constexpr DLDataType dl_float32 = DLDataType{kDLFloat, 32, 1};
#define CHECK_CUDA(x) TVM_FFI_CHECK((x).device().device_type == kDLCUDA, ValueError)
#define CHECK_CONTIGUOUS(x) TVM_FFI_CHECK((x).IsContiguous(), ValueError)
#define CHECK_INPUT(x) do { CHECK_CUDA(x); CHECK_CONTIGUOUS(x); } while(0)
inline cudaStream_t get_stream(DLDevice d) {
  return static_cast<cudaStream_t>(TVMFFIEnvGetStream(d.device_type, d.device_id));
}
```

```cpp
// scale_kernel.cu - CUDA Kernel
#include "tvm_ffi_utils.h"
template <typename T>
__global__ void ScaleKernel(T* out, const T* in, T factor, int64_t n) {
  int64_t i = blockIdx.x * blockDim.x + threadIdx.x;
  if (i < n) out[i] = in[i] * factor;
}

void Scale(TensorView output, TensorView input, double factor) {
  CHECK_INPUT(input); CHECK_INPUT(output);
  ffi::CUDADeviceGuard guard(input.device().device_id);
  cudaStream_t stream = get_stream(input.device());
  int64_t n = input.numel();
  int threads = 256, blocks = (n + threads - 1) / threads;
  ScaleKernel<<<blocks, threads, 0, stream>>>(
      static_cast<float*>(output.data_ptr()),
      static_cast<float*>(input.data_ptr()),
      static_cast<float>(factor), n);
}
TVM_FFI_DLL_EXPORT_TYPED_FUNC(scale, Scale);
```

```python
# load_scale.py - Python调用
import torch, tvm_ffi
mod = tvm_ffi.load_module("build/scale_kernel.so")
x = torch.randn(1024, device="cuda", dtype=torch.float32)
y = torch.empty_like(x)
mod.scale(y, x, 2.0)
assert torch.allclose(y, x * 2.0)
```

---

## 案例3：inline_module即时编译

### 场景
Python中直接写C++/CUDA代码，`load_inline`即时编译调用，无需CMake。

### 代码示例

```python
import torch, tvm_ffi.cpp
from tvm_ffi.module import Module

mod = tvm_ffi.cpp.load_inline(
    name="hello",
    cpp_sources=r"""
        void add_one_cpu(tvm::ffi::TensorView x, tvm::ffi::TensorView y) {
          for (int i = 0; i < x.size(0); ++i)
            static_cast<float*>(y.data_ptr())[i] =
                static_cast<float*>(x.data_ptr())[i] + 1;
        }
        void add_one_cuda(tvm::ffi::TensorView x, tvm::ffi::TensorView y);
    """,
    cuda_sources=r"""
        __global__ void AddOneKernel(float* x, float* y, int n) {
          int idx = blockIdx.x * blockDim.x + threadIdx.x;
          if (idx < n) y[idx] = x[idx] + 1;
        }
        void add_one_cuda(tvm::ffi::TensorView x, tvm::ffi::TensorView y) {
          int n = x.size(0), tb = 256, nb = (n+tb-1)/tb;
          cudaStream_t s = static_cast<cudaStream_t>(
              TVMFFIEnvGetStream(x.device().device_type, x.device().device_id));
          AddOneKernel<<<nb, tb, 0, s>>>(
              static_cast<float*>(x.data_ptr()),
              static_cast<float*>(y.data_ptr()), n);
        }
    """,
    functions=["add_one_cpu", "add_one_cuda"],
)

x = torch.tensor([1,2,3,4,5], dtype=torch.float32)
y = torch.empty_like(x)
mod.add_one_cpu(x, y)
torch.testing.assert_close(x + 1, y)
```

---

## 案例4：C ABI跨语言调用

### 场景
纯C ABI编写函数，无C++依赖，可被Python/Rust/C等语言调用。

### C端代码（add_one_cpu.c）

```c
#include <tvm/ffi/c_api.h>

TVM_FFI_DLL_EXPORT int __tvm_ffi_add_one_cpu(void* h, const TVMFFIAny* args,
                                             int32_t n, TVMFFIAny* r) {
  DLTensor* x = (args[0].type_index == kTVMFFIDLTensorPtr)
      ? (DLTensor*)args[0].v_ptr
      : (DLTensor*)(args[0].v_c_str + sizeof(TVMFFIObject));
  DLTensor* y = (args[1].type_index == kTVMFFIDLTensorPtr)
      ? (DLTensor*)args[1].v_ptr
      : (DLTensor*)(args[1].v_c_str + sizeof(TVMFFIObject));
  for (int64_t i = 0; i < x->shape[0]; ++i)
    ((float*)y->data)[i] = ((float*)x->data)[i] + 1.0f;
  return 0;
}
```

### C ABI基础操作

```c
// 创建int类型Any
TVMFFIAny AnyFromInt(int64_t v) {
  TVMFFIAny a = {0}; a.type_index = kTVMFFIInt; a.v_int64 = v; return a;
}
// 获取全局函数
TVMFFIObject* GetFunc(const char* name) {
  TVMFFIObject* out = NULL;
  TVMFFIByteArray n = {name, strlen(name)};
  TVMFFIFunctionGetGlobal(&n, (void**)&out);
  return out;
}
// 调用函数
int64_t Call(TVMFFIObject* f, int64_t x, int64_t y) {
  TVMFFIAny args[2] = {AnyFromInt(x), AnyFromInt(y)}, res = {0};
  TVMFFIFunctionCall(f, args, 2, &res);
  return res.v_int64;
}
```

---

## 案例5：Tensor零拷贝互操作

### 场景
NumPy/PyTorch Tensor零拷贝传递，基于DLPack跨框架共享。

### 代码示例

```cpp
// C++端
void ProcessTensor(tvm::ffi::TensorView in, tvm::ffi::Tensor out) {
  float* id = static_cast<float*>(in.data_ptr());
  float* od = static_cast<float*>(out.data_ptr());
  for (int64_t i = 0; i < in.numel(); ++i)
    od[i] = id[i] * 2.0f + 1.0f;
}
TVM_FFI_DLL_EXPORT_TYPED_FUNC(process, ProcessTensor);
```

```python
# Python端 - NumPy/PyTorch均支持
import numpy as np, tvm_ffi
mod = tvm_ffi.load_module("process.so")
x = np.random.randn(1000).astype(np.float32)
y = np.empty_like(x)
mod.process(x, y)  # 零拷贝DLPack转换
```

---

## 案例6：自定义Object反射

### 场景
定义Config对象，C++/Python双向访问字段。

### C++端

```cpp
#include <tvm/ffi/tvm_ffi.h>
#include <tvm/ffi/container/string.h>
namespace myapp {
class ConfigObj : public tvm::ffi::Object {
 public:
  int64_t batch_size; double lr; tvm::ffi::String name; bool use_gpu;
  TVM_FFI_DECLARE_OBJECT_INFO(ConfigObj, tvm::ffi::Object);
};
class Config : public tvm::ffi::ObjectRef<ConfigObj> {
 public:
  TVM_FFI_DEFINE_OBJECT_REF_METHODS(Config, ObjectRef, ConfigObj);
  TVM_FFI_DEFINE_FIELD(batch_size, ConfigObj);
  TVM_FFI_DEFINE_FIELD(lr, ConfigObj);
  TVM_FFI_DEFINE_FIELD(name, ConfigObj);
  TVM_FFI_DEFINE_FIELD(use_gpu, ConfigObj);
  static Config Create(int64_t bs, double lr, tvm::ffi::String n, bool g) {
    auto o = tvm::ffi::make_object<ConfigObj>();
    o->batch_size=bs; o->lr=lr; o->name=std::move(n); o->use_gpu=g;
    return Config(o);
  }
};
TVM_FFI_REGISTER_OBJECT(ConfigObj)
  .add_field("batch_size", &ConfigObj::batch_size)
  .add_field("lr", &ConfigObj::lr)
  .add_field("name", &ConfigObj::name)
  .add_field("use_gpu", &ConfigObj::use_gpu);
TVM_FFI_REGISTER_GLOBAL("myapp.ConfigCreate")
  .set_function([](int64_t bs, double lr, tvm::ffi::String n, bool g) {
    return Config::Create(bs, lr, std::move(n), g);
  });
}
```

```python
# Python端
import tvm_ffi
cfg = tvm_ffi.get_global_func("myapp.ConfigCreate")(32, 0.001, "resnet50", True)
print(cfg.batch_size, cfg.lr, cfg.name)  # 32 0.001 resnet50
cfg.batch_size = 64  # 可修改
```

---

## 案例7：Python回调函数

### 场景
C++中调用Python回调，实现算法灵活扩展。

### 代码示例

```cpp
// C++端
#include <tvm/ffi/tvm_ffi.h>
void ForEach(tvm::ffi::TensorView x, tvm::ffi::PackedFunc cb) {
  float* d = static_cast<float*>(x.data_ptr());
  for (int64_t i = 0; i < x.numel(); ++i)
    d[i] = cb(i, d[i]).cast<float>();
}
TVM_FFI_DLL_EXPORT_TYPED_FUNC(for_each, ForEach);
```

```python
# Python端
import numpy as np, tvm_ffi
mod = tvm_ffi.load_module("cb.so")
x = np.array([1.,2.,3.,4.,5.], dtype=np.float32)
def cb(idx, val):
    print(f"idx={idx}, val={val}")
    return val * 2 + 1
mod.for_each(x, cb)
print(x)  # [3. 5. 7. 9. 11.]
```

---

## 官方示例索引

| 目录 | 说明 | 关键文件 |
|------|------|----------|
| `quickstart/` | 入门：C++编译+Python加载 | `add_one_cpu.cc`, `load_numpy.py` |
| `kernel_library/` | CUDA Kernel库 | `scale_kernel.cu`, `load_scale.py` |
| `inline_module/` | 即时编译C++/CUDA | `main.py` |
| `stable_c_abi/` | 纯C ABI接口 | `add_one_cpu.c`, `load.c` |
| `abi_overview/` | C ABI完整API参考 | `example_code.c` |
| `cubin_launcher/` | CUDA Cubin加载 | `example_nvrtc_cubin.py` |
| `python_packaging/` | Python包打包 | `pyproject.toml`, `extension.cc` |

---

## 编译通用方式

```bash
# CMake项目
mkdir build && cd build && cmake .. && cmake --build . -j

# load_inline：Python内直接写代码，无需手动编译

# 纯C
gcc $(python -m tvm_ffi.config --cflags --ldflags) \
    -shared -fPIC code.c -o lib.so
```

---

← 上一页：[构建与打包](10-build-packaging.md) | 下一页 → [常见问题解答](12-faq.md)
