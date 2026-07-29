---
id: "tvm-ffi-cpp-guide"
title: "C++ 开发指南"
tags: ["tvm-ffi", "cpp", "guide", "cmake", "build"]
date: "2026-07-28"
source: "spec:tvm-ffi-wiki-tutorial"
category: "tech"
---

> 📚 **TVM FFI Wiki 教程导航**：
> [首页](00-overview.md) | [目录结构](01-project-structure.md) | [Any类型](02-any-type.md) | [Object系统](03-object-system.md) | [Function](04-function-registry.md) | [容器](05-containers.md) | [反射](06-reflection.md) | [Module](07-module-system.md) | [C++指南](08-cpp-guide.md) | [Python指南](09-python-guide.md) | [构建打包](10-build-packaging.md) | [实战案例](11-examples.md) | [FAQ](12-faq.md) | [源码解析](13-source-analysis.md)

---

# C++ 开发指南

本指南介绍如何在 C++ 项目中使用 TVM-FFI，包括环境配置、构建集成、API 使用和最佳实践。

## 环境准备

### 编译器要求

TVM-FFI 需要 C++17 支持：

- **GCC**: ≥ 7.0，**Clang**: ≥ 5.0，**MSVC**: ≥ 2019
- **CMake**: ≥ 3.18（推荐 3.20+）
- **Python**: ≥ 3.9（可选，用于获取编译配置）

安装 TVM-FFI：

```bash
pip install --reinstall --upgrade apache-tvm-ffi
```

## 集成方式

### 方式 1：find_package（推荐）

```cmake
cmake_minimum_required(VERSION 3.20)
project(my_project LANGUAGES CXX)

find_package(Python COMPONENTS Interpreter REQUIRED)
execute_process(
  COMMAND "${Python_EXECUTABLE}" -m tvm_ffi.config --cmakedir
  OUTPUT_STRIP_TRAILING_WHITESPACE OUTPUT_VARIABLE tvm_ffi_ROOT)
find_package(tvm_ffi CONFIG REQUIRED)

add_library(my_ext SHARED my_ext.cc)
tvm_ffi_configure_target(my_ext)
```

### 方式 2：FetchContent（源码集成）

```cmake
include(FetchContent)
FetchContent_Declare(tvm_ffi
  GIT_REPOSITORY https://github.com/apache/tvm-ffi.git GIT_TAG main)
FetchContent_MakeAvailable(tvm_ffi)

add_library(my_ext SHARED my_ext.cc)
tvm_ffi_configure_target(my_ext)
```

### 方式 3：add_subdirectory（本地源码）

```cmake
add_subdirectory(third_party/tvm-ffi)
add_library(my_ext SHARED my_ext.cc)
target_link_libraries(my_ext PRIVATE tvm_ffi::header tvm_ffi::shared)
```

### 方式 4：命令行直接编译

```bash
g++ -shared -O3 my_ext.cc -fPIC -fvisibility=hidden \
    $(tvm-ffi-config --cxxflags) $(tvm-ffi-config --ldflags) \
    $(tvm-ffi-config --libs) -o my_ext.so
```

## 头文件引入

一键引入核心 API：

```cpp
#include <tvm/ffi/tvm_ffi.h>
```

额外头文件：

```cpp
#include <tvm/ffi/extra/module.h>      // 动态库加载
#include <tvm/ffi/extra/dataclass.h>   // 深拷贝/repr/hash
#include <tvm/ffi/extra/c_env_api.h>   // 环境 API
```

## 基本使用（Hello World）

### 导出函数（共享库）

```cpp
// add_one_cpu.cc
#include <tvm/ffi/tvm_ffi.h>

namespace my_example {
void AddOne(tvm::ffi::TensorView x, tvm::ffi::TensorView y) {
  int64_t n = x.size(0);
  float* xd = static_cast<float*>(x.data_ptr());
  float* yd = static_cast<float*>(y.data_ptr());
  for (int64_t i = 0; i < n; ++i) yd[i] = xd[i] + 1;
}
TVM_FFI_DLL_EXPORT_TYPED_FUNC(add_one_cpu, my_example::AddOne)
}
```

### 创建本地函数

```cpp
#include <tvm/ffi/tvm_ffi.h>
void ExampleFunc() {
  namespace ffi = tvm::ffi;
  ffi::Function add1 = ffi::Function::FromTyped(
    [](int a) -> int { return a + 1; });
  int r = add1(41).cast<int>();  // 42
}
```

### 注册全局函数

```cpp
#include <tvm/ffi/reflection/registry.h>

TVM_FFI_STATIC_INIT_BLOCK() {
  namespace ffi = tvm::ffi;
  ffi::reflection::GlobalDef()
    .def("my.add", [](int a, int b){ return a + b; });
}

// 调用
ffi::Function add = ffi::Function::GetGlobalRequired("my.add");
int sum = add(1, 2).cast<int>();  // 3
```

### CMake 构建配置

```cmake
add_library(add_one_cpu SHARED add_one_cpu.cc)
tvm_ffi_configure_target(add_one_cpu)
set_target_properties(add_one_cpu PROPERTIES PREFIX "" SUFFIX ".so")
```

构建：

```bash
cmake . -B build -DCMAKE_BUILD_TYPE=RelWithDebInfo
cmake --build build
```

### 加载并调用共享库

```cpp
#include <tvm/ffi/extra/module.h>
#include <iostream>

int main() {
  namespace ffi = tvm::ffi;
  ffi::Module mod = ffi::Module::LoadFromFile("build/add_one_cpu.so");
  ffi::Function f = mod->GetFunction("add_one_cpu").value();

  // 分配测试张量
  auto alloc = [](std::initializer_list<float> d) -> ffi::Tensor {
    struct A { void AllocData(DLTensor* t){ t->data=malloc(t->shape[0]*4); }
              void FreeData(DLTensor* t){ free(t->data); } };
    int64_t n = d.size(); DLDataType ft={kDLFloat,32,1}; DLDevice cpu={kDLCPU,0};
    ffi::Tensor t = ffi::Tensor::FromNDAlloc(A(), {n}, ft, cpu);
    float* p = static_cast<float*>(t.data_ptr());
    for (float v : d) *p++ = v; return t;
  };

  ffi::Tensor x = alloc({1,2,3,4,5}), y = alloc({0,0,0,0,0});
  f(x, y);
  const float* yp = static_cast<const float*>(y.data_ptr());
  for (int i=0;i<5;i++) std::cout << yp[i] << " ";  // 2 3 4 5 6
}
```

## 创建自定义 Object

### 定义 Obj 和 Ref 类

```cpp
#include <tvm/ffi/object.h>
#include <tvm/ffi/memory.h>

class IntPairObj : public tvm::ffi::Object {
 public:
  int64_t a, b;
  IntPairObj(int64_t a_, int64_t b_) : a(a_), b(b_) {}
  int64_t Sum() const { return a + b; }
  TVM_FFI_DECLARE_OBJECT_INFO_FINAL("my.IntPair", IntPairObj, tvm::ffi::Object);
};

class IntPair : public tvm::ffi::ObjectRef {
 public:
  IntPair(int64_t a, int64_t b) { data_ = tvm::ffi::make_object<IntPairObj>(a,b); }
  TVM_FFI_DEFINE_OBJECT_REF_METHODS_NULLABLE(IntPair, tvm::ffi::ObjectRef, IntPairObj);
};
```

### 反射注册（跨语言访问）

```cpp
TVM_FFI_STATIC_INIT_BLOCK() {
  namespace refl = tvm::ffi::reflection;
  refl::ObjectDef<IntPairObj>()
    .def(refl::init<int64_t, int64_t>())
    .def_ro("a", &IntPairObj::a)
    .def_ro("b", &IntPairObj::b)
    .def("sum", &IntPairObj::Sum);
}
```

使用：

```cpp
IntPair p(10, 20);
int s = p->Sum();  // 30
tvm::ffi::Any any = p;  // 可跨语言传递
```

## 使用容器类型

### Array/Map/String/Tensor

```cpp
#include <tvm/ffi/container/array.h>
#include <tvm/ffi/container/map.h>
#include <tvm/ffi/string.h>

void Containers() {
  namespace ffi = tvm::ffi;
  ffi::Array<int> nums = {1,2,3};
  ffi::Map<ffi::String,int> scores = {{"Alice",95}};
  ffi::String s = "hello";
  std::string stds = s;

  ffi::List<int> lst = {1,2}; lst.push_back(3);  // 可变
  ffi::Dict<ffi::String,int> dict; dict.Set("k",1);
}
```

### Tensor 分配

```cpp
#include <tvm/ffi/container/tensor.h>
struct CPUAlloc {
  void AllocData(DLTensor* t){ t->data=std::malloc(tvm::ffi::GetDataSize(*t)); }
  void FreeData(DLTensor* t){ std::free(t->data); }
};
ffi::Tensor t = ffi::Tensor::FromNDAlloc(CPUAlloc(), {2,3},
  DLDataType{kDLFloat,32,1}, DLDevice{kDLCPU,0});
```

## 编写动态库模块

使用 `TVM_FFI_STATIC_INIT_BLOCK()` 在库加载时自动注册：

```cpp
// my_module.cc
#include <tvm/ffi/reflection/registry.h>
namespace m { int Add(int a,int b){return a+b;} }

TVM_FFI_STATIC_INIT_BLOCK() {
  tvm::ffi::reflection::GlobalDef().def("m.add", m::Add);
}
```

CMake：

```cmake
add_library(my_module SHARED my_module.cc)
tvm_ffi_configure_target(my_module)
```

加载使用：

```cpp
#include <tvm/ffi/extra/module.h>
ffi::Module::LoadFromFile("my_module.so");
auto f = ffi::Function::GetGlobalRequired("m.add");
int r = f(3,4).cast<int>();  // 7
```

## 反射注册高级用法

### 字段注册方法

| 方法 | 用途 |
|------|------|
| `.def_ro(name, ptr, traits...)` | 只读字段 |
| `.def_rw(name, ptr, traits...)` | 可写字段 |
| `.def(name, func)` | 实例方法 |
| `.def_static(name, func)` | 静态方法 |
| `.def(init<Args...>())` | 显式构造函数 |

### 字段特性

```cpp
refl::ObjectDef<MyObj>()
  .def_rw("lr", &MyObj::lr, refl::default_(0.001))
  .def_rw("items", &MyObj::items,
    refl::default_factory([]{return ffi::List<ffi::String>();}))
  .def_rw("device", &MyObj::device, refl::kw_only(true))
  .def_rw("_cache", &MyObj::_cache, refl::init(false))
  .def_rw("secret", &MyObj::secret, refl::repr(false));
```

### 访问权限

- **def_ro**：Python 端只读
- **def_rw**：Python 端可读写
- **frozen**：Python 端 `@c_class(frozen=True)` 使所有字段只读

## 编译选项

### CMake 编译选项

| 选项 | 默认 | 说明 |
|------|------|------|
| `TVM_FFI_ENABLE_PYTHON` | OFF | 启用 Python 绑定 |
| `TVM_FFI_USE_LIBBACKTRACE` | ON | 友好回溯 |
| `TVM_FFI_HIDE_PRIVATE_SYMBOLS` | ON | 隐藏私有符号 |
| `TVM_FFI_EXCEPTION_ENABLE_BACKTRACE` | ON | 异常含回溯 |
| `TVM_FFI_DLL_EXPORT_INCLUDE_METADATA` | OFF | 导出函数元数据 |

### tvm_ffi_configure_target 参数

```cmake
tvm_ffi_configure_target(target
  [LINK_SHARED ON|OFF]   # 链接共享库（默认 ON）
  [LINK_HEADER ON|OFF]   # 链接头文件（默认 ON）
  [DEBUG_SYMBOL ON|OFF]  # 调试符号（默认 ON）
  [MSVC_FLAGS ON|OFF]    # MSVC 兼容（默认 ON）
)
```

## 最佳实践

### 1. 优先使用 Function::FromTyped

```cpp
auto add = ffi::Function::FromTyped([](int a,int b){return a+b;});  // 推荐
```

### 2. 使用 ObjectRef 而非裸 ObjectPtr

```cpp
IntPair p(1,2);  // 推荐，自动管理内存
```

### 3. AnyView 参数 / Any 返回值

- 参数用 `AnyView`（无所有权）
- 返回值用 `Any`（管理引用计数）

### 4. 错误处理

```cpp
#include <tvm/ffi/error.h>
TVM_FFI_THROW(ValueError) << "Invalid value: " << x;

try {
  func();
} catch (const ffi::Error& e) {
  std::cerr << e.kind() << ": " << e.message() << "\n";
}
```

### 5. Tensor 零拷贝交互

使用 `TensorView` 接收参数，零拷贝对接 DLPack 框架（PyTorch/NumPy 等）。

## 常见编译错误

| 错误 | 解决方法 |
|------|----------|
| `undefined symbol: __tvm_ffi_xxx` | 使用 `TVM_FFI_DLL_EXPORT_TYPED_FUNC`，加 `-fvisibility=hidden` |
| `find_package(tvm_ffi)` 失败 | `-Dtvm_ffi_ROOT=$(python -m tvm_ffi.config --cmakedir)` |
| `cannot open shared object` | 加 `-Wl,-rpath,$(tvm-ffi-config --libdir)` |
| C++17 错误 | 设置 `CMAKE_CXX_STANDARD 17`，升级编译器 |
| CUDA `invalid device function` | 使用正确的 `-arch=sm_XX` |
| `TypeError` 类型转换 | 检查参数类型与函数签名匹配 |

## 关键引用

- [tvm_ffi.h](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/tvm-ffi/include/tvm/ffi/tvm_ffi.h)
- [examples/quickstart/](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/tvm-ffi/examples/quickstart)
- [cpp_lang_guide.md](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/tvm-ffi/docs/guides/cpp_lang_guide.md)
- [cpp_tooling.rst](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/tvm-ffi/docs/packaging/cpp_tooling.rst)

---

← 上一页：[Module 模块系统](07-module-system.md) | 下一页 → [Python 开发指南](09-python-guide.md)
