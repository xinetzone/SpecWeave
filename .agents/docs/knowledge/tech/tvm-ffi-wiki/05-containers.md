---
id: "tvm-ffi-containers"
title: "Container 容器类型"
tags: ["tvm-ffi", "container", "array", "map", "tensor"]
date: "2026-07-28"
source: "spec:tvm-ffi-wiki-tutorial"
category: "tech"
---

> 📚 **TVM FFI Wiki 教程导航**：
> [首页](00-overview.md) | [目录结构](01-project-structure.md) | [Any类型](02-any-type.md) | [Object系统](03-object-system.md) | [Function](04-function-registry.md) | [容器](05-containers.md) | [反射](06-reflection.md) | [Module](07-module-system.md) | [C++指南](08-cpp-guide.md) | [Python指南](09-python-guide.md) | [构建打包](10-build-packaging.md) | [实战案例](11-examples.md) | [FAQ](12-faq.md) | [源码解析](13-source-analysis.md)

---

# Container 容器类型

## 概述

TVM FFI 提供了一组内置容器类型，用于在 C++、Python 和 Rust 之间存储和交换数据集合。所有容器都是堆分配、引用计数的 Object，可以存储在 `Any` 类型中并安全通过 FFI 边界。

容器的核心设计理念分为两大类：

- **不可变容器（Immutable）**：采用**写时复制（Copy-on-Write, COW）**语义。多个引用共享同一容器时，修改操作会先复制底层数据，确保原有引用不受影响。
- **可变容器（Mutable）**：采用**共享引用（Shared Reference）**语义。修改直接作用于底层共享对象，所有引用立即看到变更。

## 容器类型分类表

| 容器名称 | C++ 类型 | Python 类型 | 可变性 | 类比 Python 类型 | 头文件 |
|---------|---------|------------|-------|-----------------|--------|
| Array | `Array<T>` | `tvm_ffi.Array` | 不可变（COW） | `tuple` / 只读 `list` | [array.h](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/tvm-ffi/include/tvm/ffi/container/array.h) |
| Map | `Map<K,V>` | `tvm_ffi.Map` | 不可变（COW） | `frozendict` | [map.h](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/tvm-ffi/include/tvm/ffi/container/map.h) |
| String | `String` | `str` | 不可变 | `str` | string.h |
| Shape | `Shape` | `tuple` | 不可变 | 维度元组 | shape.h |
| Tuple | `Tuple<Ts...>` | - | 不可变 | 异构固定元组 | tuple.h |
| List | `List<T>` | `tvm_ffi.List` | 可变 | `list` | list.h |
| Dict | `Dict<K,V>` | `tvm_ffi.Dict` | 可变 | `dict` | dict.h |
| Tensor | `Tensor` | `tvm_ffi.Tensor` | - | `numpy.ndarray` | [tensor.h](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/tvm-ffi/include/tvm/ffi/container/tensor.h) |
| Variant | `Variant<T...>` | - | - | 类型安全联合 | variant.h |

---

## Array<T> 不可变数组

`Array<T>` 是同质不可变序列容器，底层由 `ArrayObj` 实现，采用写时复制语义。

### 创建与访问

```cpp
#include <tvm/ffi/container/array.h>
using namespace tvm::ffi;

Array<int> a = {1, 2, 3};                     // 初始化列表
Array<int> repeated = Array<int>::CreateRepeated(5, 0);

int first = a[0];                             // 下标访问
int64_t size = a.size();                      // 大小
for (int v : a) { /* 范围for迭代 */ }
```

```python
import tvm_ffi
a = tvm_ffi.Array([1, 2, 3])
print(a[0], len(a))
```

### 不可变语义（COW）

关键特性：**修改操作实际上创建新对象**

```cpp
Array<int> a = {1, 2, 3};
Array<int> b = a;        // b 和 a 共享同一个 ArrayObj

a.push_back(4);          // COW: a 获得新的底层存储
// a: [1, 2, 3, 4]
// b: [1, 2, 3] （不受影响）
```

> 当 Array 只有唯一引用时，`push_back` 可以原地修改，不会触发复制。

### 与 Python 互操作

- Python `list`/`tuple` 传入 FFI 时自动转换为 `Array`
- C++ `Array` 返回 Python 时包装为 `tvm_ffi.Array`（实现 `collections.abc.Sequence`）

---

## Map<K,V> 不可变映射

`Map<K,V>` 是同质不可变键值对容器，底层由 `MapObj` 实现，写时复制语义，**保持插入顺序**。

```cpp
#include <tvm/ffi/container/map.h>
using namespace tvm::ffi;

Map<String, int> m = {{"Alice", 100}, {"Bob", 95}};

int score = m["Alice"];                      // 下标访问
Optional<int> bob = m.Get("Bob");            // 安全访问
bool has = m.count("Charlie");               // 检查key存在

m.Set("Charlie", 88);                        // COW修改
```

```python
m = tvm_ffi.Map({"Alice": 100, "Bob": 95})
print(m["Alice"])
```

Python 端 `tvm_ffi.Map` 实现 `collections.abc.Mapping` 接口，支持 `keys()`/`values()`/`items()` 只读操作。

---

## List<T> 和 Dict<K,V> 可变容器

### 核心区别对比

| 特性 | Array/Map（不可变） | List/Dict（可变） |
|-----|-------------------|------------------|
| 语义 | 写时复制（COW） | 共享引用 |
| 修改影响范围 | 仅当前引用 | 所有共享引用 |
| 线程安全 | 只读安全 | 不安全 |
| 类比 | tuple / frozendict | list / dict |

### List<T> 示例

```cpp
#include <tvm/ffi/container/list.h>
using namespace tvm::ffi;

List<int> a = {1, 2, 3};
List<int> b = a;        // 共享 ListObj

a.push_back(4);         // 原地修改！
// a.size() == 4, b.size() == 4 （b 也看到变更）

a.Set(0, 100);
a.pop_back();
```

```python
lst = tvm_ffi.List([1, 2, 3])
lst.append(4)
lst[0] = 100
lst.pop()
```

### Dict<K,V> 示例

```cpp
#include <tvm/ffi/container/dict.h>
using namespace tvm::ffi;

Dict<String, int> d = {{"Alice", 100}};
d.Set("Bob", 95);       // 原地修改
d.erase("Alice");
```

```python
d = tvm_ffi.Dict({"Alice": 100})
d["Bob"] = 95
del d["Alice"]
```

### 使用场景

- **Array/Map**：函数参数、不可变配置、跨线程只读共享
- **List/Dict**：构建时频繁原地修改、累积结果、输出参数

---

## String 字符串

`String` 是不可变字符串，内置**小字符串优化（SSO）**，短字符串直接存储在对象内避免堆分配。

- 与 `std::string` 无缝互转
- 与 Python `str` 自动双向转换
- 支持 `std::string_view` 零拷贝访问

```cpp
#include <tvm/ffi/string.h>
using namespace tvm::ffi;

String s1 = "hello";
std::string std_str = "world";
String s2(std_str);

const char* cstr = s1.c_str();
std::string_view view = s1;  // 零拷贝视图
String s3 = s1 + " " + s2;   // 拼接返回新String
```

---

## Tensor 张量（重点）

`Tensor` 基于 **DLPack** 开放标准实现，支持与主流深度学习框架**零拷贝**互操作。

### DLPack 结构

```cpp
typedef struct {
    void* data;               // 数据指针
    DLDevice device;          // 设备类型/ID (CPU/CUDA/ROCM等)
    int32_t ndim;             // 维度数
    DLDataType dtype;         // 数据类型 (float32/int64等)
    int64_t* shape;           // 维度数组
    int64_t* strides;         // 步长 (nullptr=C连续)
    uint64_t byte_offset;     // 字节偏移
} DLTensor;
```

`TensorObj` 直接继承自 `DLTensor`，本身就是符合 DLPack 标准的张量对象。

### 零拷贝互操作

**核心优势**：无需复制数据，直接在不同框架间共享同一块内存。

支持框架：PyTorch、NumPy、JAX、CuPy、PaddlePaddle、MXNet 等所有 DLPack 兼容框架。

### C++ 示例

```cpp
#include <tvm/ffi/container/tensor.h>
using namespace tvm::ffi;

DLManagedTensor* dlmt = /* 从其他框架获得 */;
Tensor tensor = Tensor::FromDLPack(dlmt);        // 零拷贝导入
DLManagedTensor* exported = tensor.ToDLPack();   // 零拷贝导出

DLDevice device = tensor->device;
void* data = tensor->data;
bool contiguous = IsContiguous(*tensor);
size_t nbytes = GetDataSize(*tensor);
```

### Python 示例（重点）

```python
import tvm_ffi
import numpy as np
import torch

# NumPy → Tensor（零拷贝共享内存）
arr_np = np.random.randn(2, 3).astype(np.float32)
tensor = tvm_ffi.Tensor.from_numpy(arr_np)

# Tensor → NumPy（零拷贝）
arr_back = tensor.numpy()
# arr_back 和 arr_np 共享内存！修改一个影响另一个

# Tensor → PyTorch（零拷贝）
torch_tensor = tensor.to_torch()

# PyTorch → Tensor（零拷贝）
tensor2 = tvm_ffi.Tensor.from_torch(torch_tensor)

print(tensor.shape, tensor.dtype, tensor.device)
```

> **重要**：Tensor 通过引用计数管理生命周期，只要还有张量对象引用内存，数据就不会被释放。

---

## Shape 和 Tuple

### Shape

`Shape` 是表示张量维度的不可变容器，本质是 `Array<int64_t>` 的类型别名。

```cpp
#include <tvm/ffi/container/shape.h>
using namespace tvm::ffi;

Shape s = {2, 3, 4};
int64_t batch = s[0];
```

### Tuple<Ts...>

`Tuple<T1, T2, ...>` 是**异构固定大小**不可变序列，底层复用 `ArrayObj`，通过变参模板提供编译期类型安全。

```cpp
#include <tvm/ffi/container/tuple.h>
using namespace tvm::ffi;

Tuple<int, String, bool> t(42, "hello", true);
int x = t.get<0>();        // 42
String s = t.get<1>();     // "hello"
```

Python 端无独立 Tuple 类，Python `tuple` 传入 FFI 自动转为 `Array`。

---

## Variant<T...> 类型安全联合

`Variant<T...>` 是类型安全的标签联合，可存储指定类型集合中的任意一种值。

```cpp
#include <tvm/ffi/variant.h>
using namespace tvm::ffi;

Variant<int, String, float> v;
v = 42;
v = String("hello");
v = 3.14f;

if (v.is<int>()) {
    int x = v.as<int>();
}

v.match([](int x) { /* ... */ },
        [](const String& s) { /* ... */ },
        [](float f) { /* ... */ });
```

---

## 容器和 Object 的关系

所有容器本身都是 **Object**：

- `ArrayObj`、`MapObj`、`ListObj`、`DictObj`、`TensorObj`、`StringObj` 都继承自 `Object`
- 容器句柄（`Array<T>`、`Map<K,V>` 等）继承自 `ObjectRef`
- 所有容器可存储在 `Any` 中、通过 FFI 传递、使用引用计数管理生命周期

```cpp
Any any_val = Array<int>{1, 2, 3};
if (any_val.is<Array<int>>()) {
    Array<int> arr = any_val.as<Array<int>>();
}
```

---

## 常见陷阱

### 1. 不可变容器"修改"创建新对象

```cpp
Array<int> a = {1, 2, 3};
Array<int> b = a;
a.push_back(4);
// 陷阱：期望 b 也变成 [1,2,3,4]
// 实际：b 仍然是 [1,2,3]（COW语义）
```

需要所有引用看到修改，请使用 `List`。

### 2. Array 元素类型限制

`Array<T>` 的 `T` 必须满足 `storage_enabled_v<T>`：基本类型（int/float/bool）、`String`、或 ObjectRef 子类。

```cpp
// Array<std::string> bad;  // 错误
Array<String> good;         // 正确
```

### 3. Tensor 生命周期

零拷贝共享内存时，只要 `Tensor` 对象存在，关联内存就不会释放。TVM FFI 正确处理引用计数，避免悬垂指针。

### 4. 可变容器非线程安全

`List`/`Dict` 原地修改非线程安全，多线程访问需外部同步。`Array`/`Map` 只读访问线程安全。

---

← 上一页：[Function 函数与全局注册表](04-function-registry.md) | 下一页 → [Reflection 反射系统](06-reflection.md)
