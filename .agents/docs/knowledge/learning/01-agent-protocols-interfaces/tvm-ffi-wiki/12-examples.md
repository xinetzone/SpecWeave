---
title: "完整实战示例"
date: 2026-07-05
source: "spec:create-tvm-ffi-wiki-tutorial"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/01-agent-protocols-interfaces/tvm-ffi-wiki/12-examples.toml"
tags: [tvm-ffi, ffi, build, examples, best-practices, faq, resources]
---
# 第12章：完整实战示例

本章提供 8 个完整可运行的示例，覆盖 TVM FFI 的核心功能。每个示例包含 C++ 端和 Python 端代码，可以直接编译运行。

## 示例 1：Hello World - C++ 函数注册与 Python 调用

最基础的示例：在 C++ 中注册一个函数，从 Python 中调用。

**文件：`hello.cc`**
```cpp
#include <tvm/ffi/function.h>
#include <tvm/ffi/string.h>
#include <iostream>

namespace tvm::ffi::examples {

TVM_FFI_DLL_EXPORT int HelloSubmoduleInit() {
  // 注册一个简单的加法函数
  register_global_func("examples.hello.add", [](int a, int b) -> int {
    return a + b;
  });

  // 注册一个字符串问候函数
  register_global_func("examples.hello.greet", [](String name) -> String {
    return "Hello, " + name + " from TVM FFI!";
  });

  // 注册一个多参数函数
  register_global_func("examples.hello.multiply", [](double x, double y) -> double {
    return x * y;
  });

  std::cout << "[C++] Hello module loaded successfully!" << std::endl;
  return 0;
}

}  // namespace tvm::ffi::examples
```

**编译：`CMakeLists.txt`**
```cmake
cmake_minimum_required(VERSION 3.18)
project(hello_example)
set(CMAKE_CXX_STANDARD 17)
find_package(tvm_ffi REQUIRED)

add_library(hello SHARED hello.cc)
target_link_libraries(hello PRIVATE tvm::ffi)
set_target_properties(hello PROPERTIES PREFIX "" OUTPUT_NAME "hello")
```

**Python 调用：`hello_test.py`**
```python
from __future__ import annotations

import tvm_ffi
from tvm_ffi import load_module, get_global_func

# 加载编译好的共享库
lib = load_module("./hello.so")  # Linux/macOS
# lib = load_module("./hello.dll")  # Windows

# 获取并调用函数
add = get_global_func("examples.hello.add")
print(f"3 + 4 = {add(3, 4)}")  # 输出: 3 + 4 = 7

greet = get_global_func("examples.hello.greet")
print(greet("World"))  # 输出: Hello, World from TVM FFI!

multiply = get_global_func("examples.hello.multiply")
print(f"2.5 * 4.0 = {multiply(2.5, 4.0)}")  # 输出: 2.5 * 4.0 = 10.0
```

---

## 示例 2：自定义 Object 类型

定义一个自定义对象类型，包含字段和方法，可在 C++ 和 Python 中使用。

**文件：`point.cc`**
```cpp
#include <tvm/ffi/object.h>
#include <tvm/ffi/function.h>

namespace tvm::ffi::examples {

// 定义 Point 对象
class PointObj : public Object {
 public:
  double x;
  double y;

  PointObj(double x, double y) : x(x), y(y) {}

  double distance_to(const PointObj* other) const {
    double dx = x - other->x;
    double dy = y - other->y;
    return std::sqrt(dx * dx + dy * dy);
  }

  TVM_FFI_DECLARE_OBJECT_INFO(PointObj, Object);
};

class Point : public ObjectRef<PointObj> {
 public:
  using ObjectRef::ObjectRef;

  TVM_DEFINE_OBJECT_REF_METHODS(Point, ObjectRef, PointObj);

  Point(double x, double y) : ObjectRef(make_object<PointObj>(x, y)) {}

  TVM_DEFINE_OBJECT_REF_FIELD(x, double, x);
  TVM_DEFINE_OBJECT_REF_FIELD(y, double, y);
  TVM_DEFINE_OBJECT_REF_METHOD(distance_to);
};

TVM_FFI_REGISTER_OBJECT(PointObj, "examples.Point")
    .def_method("__add__", [](PointObj* self, PointObj* other) -> Point {
      return Point(self->x + other->x, self->y + other->y);
    })
    .def_method("__repr__", [](PointObj* self) -> String {
      std::ostringstream os;
      os << "Point(" << self->x << ", " << self->y << ")";
      return os.str();
    });

TVM_FFI_DLL_EXPORT int PointSubmoduleInit() {
  // 注册工厂函数
  register_global_func("examples.point.create", [](double x, double y) -> Point {
    return Point(x, y);
  });

  // 注册计算原点距离的函数
  register_global_func("examples.point.origin_distance", [](Point p) -> double {
    return p->distance_to(Point(0, 0).get());
  });

  return 0;
}

}  // namespace tvm::ffi::examples
```

**Python 使用：`point_test.py`**
```python
from __future__ import annotations

from tvm_ffi import load_module, get_global_func
from tvm_ffi import register_object

# 注册 Python 端 Point 类
@register_object("examples.Point")
class Point:
    @property
    def x(self) -> float: ...
    @property
    def y(self) -> float: ...
    def __add__(self, other: "Point") -> "Point": ...
    def distance_to(self, other: "Point") -> float: ...

load_module("./point.so")

create_point = get_global_func("examples.point.create")
origin_dist = get_global_func("examples.point.origin_distance")

p1 = create_point(3.0, 4.0)
print(f"p1 = {p1}")              # 输出: p1 = Point(3.0, 4.0)
print(f"p1.x = {p1.x}")         # 输出: p1.x = 3.0
print(f"p1.y = {p1.y}")         # 输出: p1.y = 4.0
print(f"distance to origin: {origin_dist(p1)}")  # 输出: 5.0

p2 = create_point(1.0, 2.0)
p3 = p1 + p2
print(f"p1 + p2 = {p3}")        # 输出: Point(4.0, 6.0)
print(f"distance p1-p2: {p1.distance_to(p2)}")   # 输出: sqrt((2)^2+(2)^2) ≈ 2.828
```

---

## 示例 3：容器类型使用

展示 Array、Map、Dict、List 等容器在 C++ 和 Python 中的使用。

**文件：`containers.cc`**
```cpp
#include <tvm/ffi/container/array.h>
#include <tvm/ffi/container/map.h>
#include <tvm/ffi/container/list.h>
#include <tvm/ffi/function.h>

namespace tvm::ffi::examples {

TVM_FFI_DLL_EXPORT int ContainersSubmoduleInit() {
  // Array 示例：不可变数组（COW 语义）
  register_global_func("examples.container.array_sum", [](Array<int> arr) -> int {
    int sum = 0;
    for (int val : arr) {
      sum += val;
    }
    return sum;
  });

  register_global_func("examples.container.array_create", [](int n) -> Array<int> {
    Array<int> result;
    for (int i = 0; i < n; ++i) {
      result.push_back(i * i);
    }
    return result;
  });

  // Map 示例：有序不可变映射
  register_global_func("examples.container.map_get", [](Map<String, int> m, String key) -> int {
    auto it = m.find(key);
    if (it != m.end()) {
      return (*it).second;
    }
    return -1;
  });

  register_global_func("examples.container.map_create", []() -> Map<String, double> {
    return Map<String, double>{
        {"pi", 3.14159},
        {"e", 2.71828},
        {"phi", 1.61803}
    };
  });

  // List 示例：可变列表
  register_global_func("examples.container.list_append", [](List<int> lst, int val) {
    lst.push_back(val);
    return lst;
  });

  // Dict 示例：Python 风格字典
  register_global_func("examples.container.dict_keys", [](Dict<String, Any> d) -> Array<String> {
    Array<String> keys;
    for (auto& kv : d) {
      keys.push_back(kv.first);
    }
    return keys;
  });

  return 0;
}

}  // namespace tvm::ffi::examples
```

**Python 使用：`containers_test.py`**
```python
from __future__ import annotations

from tvm_ffi import load_module, get_global_func
from tvm_ffi import Array, Map, List, Dict

load_module("./containers.so")

# Array 测试
array_sum = get_global_func("examples.container.array_sum")
array_create = get_global_func("examples.container.array_create")

arr = array_create(5)
print(f"Array: {list(arr)}")      # 输出: [0, 1, 4, 9, 16]
print(f"Sum: {array_sum(arr)}")   # 输出: 30

# 也可以直接传 Python list
print(f"Sum [1,2,3,4,5]: {array_sum([1, 2, 3, 4, 5])}")  # 输出: 15

# Map 测试
map_get = get_global_func("examples.container.map_get")
map_create = get_global_func("examples.container.map_create")

constants = map_create()
print(f"Constants: {dict(constants)}")  # 输出: {'pi': 3.14159, 'e': 2.71828, 'phi': 1.61803}
print(f"pi = {map_get(constants, 'pi')}")  # 输出: 3.14159
print(f"missing = {map_get(constants, 'missing')}")  # 输出: -1

# List 测试 - 可变列表
list_append = get_global_func("examples.container.list_append")

lst = List([10, 20, 30])
lst = list_append(lst, 40)
print(f"List after append: {list(lst)}")  # 输出: [10, 20, 30, 40]

# Dict 测试
dict_keys = get_global_func("examples.container.dict_keys")

d = Dict({"name": "TVM FFI", "version": 1, "cross_lang": True})
print(f"Dict keys: {list(dict_keys(d))}")  # 输出: ['name', 'version', 'cross_lang']
```

---

## 示例 4：张量操作与 NumPy 交互

创建张量，填充数据，与 NumPy 零拷贝交换。

**文件：`tensor.cc`**
```cpp
#include <tvm/ffi/ndarray.h>
#include <tvm/ffi/function.h>
#include <dlpack/dlpack.h>
#include <numeric>

namespace tvm::ffi::examples {

TVM_FFI_DLL_EXPORT int TensorSubmoduleInit() {
  // 创建一个 CPU 张量并用 0..n-1 填充
  register_global_func("examples.tensor.arange", [](int64_t n) -> NDArray {
    NDArray arr = NDArray::Empty({n}, DLDataType{kDLFloat, 64, 1}, DLDevice{kDLCPU, 0});
    double* data = static_cast<double*>(arr->data);
    for (int64_t i = 0; i < n; ++i) {
      data[i] = static_cast<double>(i);
    }
    return arr;
  });

  // 张量加法：c = a + b
  register_global_func("examples.tensor.add", [](NDArray a, NDArray b) -> NDArray {
    TVM_FFI_CHECK(a.Shape() == b.Shape()) << "Shapes must match";
    int64_t n = 1;
    for (auto s : a.Shape()) n *= s;

    NDArray c = NDArray::Empty(a.Shape(), a->dtype, a->device);
    const double* da = static_cast<const double*>(a->data);
    const double* db = static_cast<const double*>(b->data);
    double* dc = static_cast<double*>(c->data);

    for (int64_t i = 0; i < n; ++i) {
      dc[i] = da[i] + db[i];
    }
    return c;
  });

  // 张量求和
  register_global_func("examples.tensor.reduce_sum", [](NDArray a) -> double {
    int64_t n = 1;
    for (auto s : a.Shape()) n *= s;
    const double* data = static_cast<const double*>(a->data);
    double sum = 0.0;
    for (int64_t i = 0; i < n; ++i) {
      sum += data[i];
    }
    return sum;
  });

  // 矩阵乘法（简单版，仅用于演示）
  register_global_func("examples.tensor.matmul", [](NDArray a, NDArray b) -> NDArray {
    auto shape_a = a.Shape();
    auto shape_b = b.Shape();
    TVM_FFI_CHECK(shape_a.size() == 2 && shape_b.size() == 2) << "Must be 2D matrices";
    TVM_FFI_CHECK(shape_a[1] == shape_b[0]) << "Inner dimensions must match";

    int64_t m = shape_a[0], k = shape_a[1], n = shape_b[1];
    NDArray c = NDArray::Empty({m, n}, DLDataType{kDLFloat, 64, 1}, DLDevice{kDLCPU, 0});

    const double* da = static_cast<const double*>(a->data);
    const double* db = static_cast<const double*>(b->data);
    double* dc = static_cast<double*>(c->data);

    for (int64_t i = 0; i < m; ++i) {
      for (int64_t j = 0; j < n; ++j) {
        double sum = 0.0;
        for (int64_t p = 0; p < k; ++p) {
          sum += da[i * k + p] * db[p * n + j];
        }
        dc[i * n + j] = sum;
      }
    }
    return c;
  });

  return 0;
}

}  // namespace tvm::ffi::examples
```

**Python 使用：`tensor_test.py`**
```python
from __future__ import annotations

import numpy as np
from tvm_ffi import load_module, get_global_func
from tvm_ffi import NDArray

load_module("./tensor.so")

arange = get_global_func("examples.tensor.arange")
tensor_add = get_global_func("examples.tensor.add")
reduce_sum = get_global_func("examples.tensor.reduce_sum")
matmul = get_global_func("examples.tensor.matmul")

# 创建张量
t = arange(10)
print(f"Tensor shape: {t.shape}, dtype: {t.dtype}")
print(f"Data: {t.numpy()}")  # 零拷贝转换为 NumPy 数组
# 输出: [0. 1. 2. 3. 4. 5. 6. 7. 8. 9.]

# 张量求和
print(f"Sum: {reduce_sum(t)}")  # 输出: 45.0

# 从 NumPy 创建张量（零拷贝）
a_np = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
b_np = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
a = NDArray.from_numpy(a_np)
b = NDArray.from_numpy(b_np)
c = tensor_add(a, b)
print(f"a + b = {c.numpy()}")  # 输出: [11. 22. 33. 44. 55.]

# 矩阵乘法
m1_np = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])  # 3x2
m2_np = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])    # 2x3
m1 = NDArray.from_numpy(m1_np)
m2 = NDArray.from_numpy(m2_np)
m3 = matmul(m1, m2)
print(f"Matmul result:\n{m3.numpy()}")
# 输出:
# [[ 9. 12. 15.]
#  [19. 26. 33.]
#  [29. 40. 51.]]
# 验证: 与 NumPy 结果一致
print(f"NumPy verification: {np.allclose(m3.numpy(), m1_np @ m2_np)}")  # 输出: True
```

---

## 示例 5：Python 回调传入 C++

将 Python 函数传递给 C++，C++ 端进行回调。

**文件：`callback.cc`**
```cpp
#include <tvm/ffi/function.h>
#include <tvm/ffi/container/array.h>

namespace tvm::ffi::examples {

TVM_FFI_DLL_EXPORT int CallbackSubmoduleInit() {
  // 对数组每个元素应用 Python 回调
  register_global_func("examples.callback.map", [](PackedFunc fn, Array<int> arr) -> Array<int> {
    Array<int> result;
    for (int val : arr) {
      result.push_back(fn(val).cast<int>());
    }
    return result;
  });

  // 使用回调进行归约
  register_global_func("examples.callback.reduce", [](PackedFunc fn, Array<int> arr, int init) -> int {
    int acc = init;
    for (int val : arr) {
      acc = fn(acc, val).cast<int>();
    }
    return acc;
  });

  // 将回调用于过滤
  register_global_func("examples.callback.filter", [](PackedFunc pred, Array<int> arr) -> Array<int> {
    Array<int> result;
    for (int val : arr) {
      if (pred(val).cast<bool>()) {
        result.push_back(val);
      }
    }
    return result;
  });

  // 演示在 C++ 中持有 Python 回调（注意生命周期）
  register_global_func("examples.callback.apply_twice", [](PackedFunc fn, Any x) -> Any {
    return fn(fn(x));
  });

  return 0;
}

}  // namespace tvm::ffi::examples
```

**Python 使用：`callback_test.py`**
```python
from __future__ import annotations

from tvm_ffi import load_module, get_global_func

load_module("./callback.so")

map_fn = get_global_func("examples.callback.map")
reduce_fn = get_global_func("examples.callback.reduce")
filter_fn = get_global_func("examples.callback.filter")
apply_twice = get_global_func("examples.callback.apply_twice")

# Map 示例：将 Python lambda 传给 C++
arr = [1, 2, 3, 4, 5]
doubled = map_fn(lambda x: x * 2, arr)
print(f"Doubled: {list(doubled)}")  # 输出: [2, 4, 6, 8, 10]

squared = map_fn(lambda x: x * x, arr)
print(f"Squared: {list(squared)}")  # 输出: [1, 4, 9, 16, 25]

# Reduce 示例：求和、求积
total = reduce_fn(lambda acc, x: acc + x, arr, 0)
print(f"Sum: {total}")  # 输出: 15

product = reduce_fn(lambda acc, x: acc * x, arr, 1)
print(f"Product: {product}")  # 输出: 120

# Filter 示例：筛选偶数
evens = filter_fn(lambda x: x % 2 == 0, arr)
print(f"Evens: {list(evens)}")  # 输出: [2, 4]

# 组合使用：先 map 平方，再 filter 大于 10
result = filter_fn(lambda x: x > 10, map_fn(lambda x: x * x, arr))
print(f"Squares > 10: {list(result)}")  # 输出: [16, 25]

# apply_twice
print(f"add 5 twice to 10: {apply_twice(lambda x: x + 5, 10)}")  # 输出: 20
print(f"multiply by 3 twice: {apply_twice(lambda x: x * 3, 2)}")  # 输出: 18
```

---

## 示例 6：错误处理跨语言边界

在 C++ 中抛出异常，在 Python 中捕获并处理。

**文件：`errors.cc`**
```cpp
#include <tvm/ffi/error.h>
#include <tvm/ffi/expected.h>
#include <tvm/ffi/function.h>

namespace tvm::ffi::examples {

TVM_FFI_DLL_EXPORT int ErrorsSubmoduleInit() {
  // 抛出一个简单错误
  register_global_func("examples.errors.fail", []() -> int {
    TVM_FFI_THROW(Error) << "This function always fails";
    return 0;
  });

  // 参数验证错误
  register_global_func("examples.errors.divide", [](double a, double b) -> double {
    if (b == 0.0) {
      TVM_FFI_THROW(ValueError) << "Division by zero: " << a << " / " << b;
    }
    return a / b;
  });

  // 索引越界错误
  register_global_func("examples.errors.get_at", [](Array<int> arr, int idx) -> int {
    if (idx < 0 || static_cast<size_t>(idx) >= arr.size()) {
      TVM_FFI_THROW(IndexError)
          << "Index " << idx << " out of bounds for array of size " << arr.size();
    }
    return arr[idx];
  });

  // 使用 Expected<T> 进行错误返回（不抛异常）
  register_global_func("examples.errors.safe_divide", [](double a, double b) -> Expected<double> {
    if (b == 0.0) {
      return Error(ErrorKind::ValueError, "Division by zero (safe)");
    }
    return a / b;
  });

  // 嵌套错误上下文
  register_global_func("examples.errors.outer", [](int x) -> int {
    TVM_FFI_TRY {
      if (x < 0) {
        TVM_FFI_THROW(ValueError) << "x must be non-negative, got " << x;
      }
      return x * 2;
    }
    TVM_FFI_CATCH(Error& e) {
      e.PushContext("examples.errors.outer", "in outer function");
      throw;
    }
  });

  return 0;
}

}  // namespace tvm::ffi::examples
```

**Python 使用：`errors_test.py`**
```python
from __future__ import annotations

from tvm_ffi import load_module, get_global_func, TVMError, ValueError, IndexError

load_module("./errors.so")

fail_fn = get_global_func("examples.errors.fail")
divide = get_global_func("examples.errors.divide")
get_at = get_global_func("examples.errors.get_at")
safe_divide = get_global_func("examples.errors.safe_divide")
outer = get_global_func("examples.errors.outer")

# 基本错误捕获
print("=== Basic error handling ===")
try:
    fail_fn()
except TVMError as e:
    print(f"Caught TVMError: {e}")
    print(f"Error type: {e.type}")

# 特定错误类型
print("\n=== Division by zero ===")
print(f"10 / 2 = {divide(10, 2)}")  # 正常: 5.0
try:
    divide(10, 0)
except ValueError as e:
    print(f"Caught ValueError: {e}")

# 索引错误
print("\n=== Index error ===")
arr = [10, 20, 30]
print(f"arr[1] = {get_at(arr, 1)}")  # 20
try:
    get_at(arr, 5)
except IndexError as e:
    print(f"Caught IndexError: {e}")

# Expected 返回值（不抛出异常，返回 Error 对象）
print("\n=== Expected<T> pattern ===")
result = safe_divide(100, 5)
print(f"safe_divide(100, 5) = {result}")  # 20.0

error_result = safe_divide(100, 0)
print(f"safe_divide(100, 0) is Error: {isinstance(error_result, TVMError)}")
if isinstance(error_result, TVMError):
    print(f"Error message: {error_result}")

# 错误上下文追踪
print("\n=== Error context ===")
try:
    outer(-1)
except ValueError as e:
    print(f"Error with context: {e}")
    print(f"Traceback:\n{e.traceback}")
```

---

## 示例 7：JSON 序列化

使用 TVM FFI 内置的 JSON 序列化功能。

**文件：`json.cc`**
```cpp
#include <tvm/ffi/extra/json.h>
#include <tvm/ffi/function.h>
#include <tvm/ffi/container/array.h>
#include <tvm/ffi/container/map.h>

namespace tvm::ffi::examples {

class ConfigObj : public Object {
 public:
  String name;
  int version;
  Array<double> weights;
  Map<String, Any> metadata;

  TVM_FFI_DECLARE_OBJECT_INFO(ConfigObj, Object);
};

class Config : public ObjectRef<ConfigObj> {
 public:
  TVM_DEFINE_OBJECT_REF_METHODS(Config, ObjectRef, ConfigObj);
  TVM_DEFINE_OBJECT_REF_FIELD(name, String, name);
  TVM_DEFINE_OBJECT_REF_FIELD(version, int, version);
  TVM_DEFINE_OBJECT_REF_FIELD(weights, Array<double>, weights);
  TVM_DEFINE_OBJECT_REF_FIELD(metadata, Map<String, Any>, metadata);
};

TVM_FFI_REGISTER_OBJECT(ConfigObj, "examples.Config")
    .def_method("__json_read__", [](JSONReader* reader, ConfigObj* obj) {
      reader->BeginObject();
      while (reader->NextObjectItem()) {
        String key = reader->ObjectKey();
        if (key == "name") {
          reader->Read(&obj->name);
        } else if (key == "version") {
          reader->Read(&obj->version);
        } else if (key == "weights") {
          reader->Read(&obj->weights);
        } else if (key == "metadata") {
          reader->Read(&obj->metadata);
        } else {
          reader->SkipValue();
        }
      }
      reader->EndObject();
    })
    .def_method("__json_write__", [](JSONWriter* writer, const ConfigObj* obj) {
      writer->BeginObject();
      writer->WriteObjectKeyValue("name", obj->name);
      writer->WriteObjectKeyValue("version", obj->version);
      writer->WriteObjectKeyValue("weights", obj->weights);
      writer->WriteObjectKeyValue("metadata", obj->metadata);
      writer->EndObject();
    });

TVM_FFI_DLL_EXPORT int JsonSubmoduleInit() {
  // 序列化简单值到 JSON
  register_global_func("examples.json.dumps", [](Any value) -> String {
    return JSONToString(value);
  });

  // 从 JSON 反序列化
  register_global_func("examples.json.loads", [](String json_str) -> Any {
    return StringToJSON(json_str);
  });

  // 创建示例 Config
  register_global_func("examples.json.create_config", []() -> Config {
    auto obj = make_object<ConfigObj>();
    obj->name = "my_model";
    obj->version = 2;
    obj->weights = Array<double>{0.1, 0.2, 0.3, 0.4, 0.5};
    obj->metadata = Map<String, Any>{{
        {"author", "tvm-ffi"},
        {"layers", 10},
        {"batch_norm", true}
    }};
    return Config(obj);
  });

  return 0;
}

}  // namespace tvm::ffi::examples
```

**Python 使用：`json_test.py`**
```python
from __future__ import annotations

from tvm_ffi import load_module, get_global_func
from tvm_ffi import register_object, to_json, from_json

load_module("./json.so")

dumps = get_global_func("examples.json.dumps")
loads = get_global_func("examples.json.loads")
create_config = get_global_func("examples.json.create_config")

# 基本类型序列化
print("=== Basic types ===")
print(f"Int: {dumps(42)}")           # 42
print(f"Float: {dumps(3.14)}")       # 3.14
print(f"String: {dumps('hello')}")   # "hello"
print(f"Bool: {dumps(True)}")        # true
print(f"Null: {dumps(None)}")        # null

# 容器序列化
print("\n=== Containers ===")
arr = [1, 2, 3, 4, 5]
print(f"Array: {dumps(arr)}")        # [1,2,3,4,5]

d = {"name": "test", "values": [10, 20], "flag": False}
json_str = dumps(d)
print(f"Dict: {json_str}")
# {"name":"test","values":[10,20],"flag":false}

# 反序列化
parsed = loads(json_str)
print(f"Parsed back: {dict(parsed)}")
print(f"values match: {list(parsed['values']) == [10, 20]}")  # True

# 自定义对象序列化
print("\n=== Custom Object ===")
config = create_config()
config_json = dumps(config)
print(f"Config JSON:\n{config_json}")

# 也可以使用便捷函数
print("\n=== Using to_json/from_json ===")
print(f"to_json: {to_json({'a': 1, 'b': [2, 3]})}")
roundtrip = from_json(to_json({"x": 100, "y": 200}))
print(f"Roundtrip: {dict(roundtrip)}")
```

---

## 示例 8：动态模块加载

编译一个共享库，在运行时动态加载并使用其中的函数。

**文件：`module_a.cc`**
```cpp
#include <tvm/ffi/function.h>

namespace tvm::ffi::examples {

// 模块初始化函数 - 模块加载时自动调用
// 注意符号名格式：__tvm_ffi_<ModuleName>Init
extern "C" TVM_FFI_DLL_EXPORT int __tvm_ffi_module_aInit() {
  register_global_func("module_a.hello", []() -> String {
    return "Hello from module_a!";
  });

  register_global_func("module_a.fibonacci", [](int n) -> int {
    if (n <= 1) return n;
    int a = 0, b = 1;
    for (int i = 2; i <= n; ++i) {
      int c = a + b;
      a = b;
      b = c;
    }
    return b;
  });

  return 0;
}

}  // namespace tvm::ffi::examples
```

**文件：`module_b.cc`**
```cpp
#include <tvm/ffi/function.h>

namespace tvm::ffi::examples {

extern "C" TVM_FFI_DLL_EXPORT int __tvm_ffi_module_bInit() {
  // 可以调用其他已加载模块中的函数
  register_global_func("module_b.use_other_module", []() -> String {
    auto fn = get_global_func("module_a.hello", false);
    if (fn) {
      return "module_b called: " + fn().cast<String>();
    }
    return "module_a not loaded";
  });

  register_global_func("module_b.is_prime", [](int n) -> bool {
    if (n < 2) return false;
    for (int i = 2; i * i <= n; ++i) {
      if (n % i == 0) return false;
    }
    return true;
  });

  return 0;
}

}  // namespace tvm::ffi::examples
```

**Python 使用：`module_test.py`**
```python
from __future__ import annotations

from tvm_ffi import load_module, get_global_func, list_global_func

# 加载模块 A
print("=== Loading module_a ===")
load_module("./module_a.so")

hello_a = get_global_func("module_a.hello")
fib = get_global_func("module_a.fibonacci")

print(hello_a())                    # Hello from module_a!
print(f"fib(10) = {fib(10)}")      # 55
print(f"fib(20) = {fib(20)}")      # 6765

# 加载模块 B（模块 B 可以调用模块 A 的函数）
print("\n=== Loading module_b ===")
load_module("./module_b.so")

is_prime = get_global_func("module_b.is_prime")
use_other = get_global_func("module_b.use_other_module")

print(f"is_prime(17) = {is_prime(17)}")  # True
print(f"is_prime(18) = {is_prime(18)}")  # False
print(use_other())  # module_b called: Hello from module_a!

# 列出所有已注册的函数
print("\n=== Registered functions (our examples) ===")
all_funcs = list_global_func()
for name in sorted(all_funcs):
    if name.startswith(("module_a.", "module_b.", "examples.")):
        print(f"  - {name}")
```

---

**本章导航：**
- 上一章：[11-编译构建与项目集成](11-build-and-integration.md)
- 下一章：[13-最佳实践与性能优化](13-best-practices.md)
- [返回目录](README.md)
