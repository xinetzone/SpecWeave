---
title: "常见问题解答 (FAQ)"
date: 2026-07-05
source: "spec:create-tvm-ffi-wiki-tutorial"
tags: [tvm-ffi, ffi, build, examples, best-practices, faq, resources]
---

# 第14章：常见问题解答 (FAQ)

本章收集 TVM FFI 开发中最常见的问题和解决方案。遇到问题时先在这里查找答案。

---

## Q: 如何注册一个函数让 Python 可以调用？

在 C++ 中使用 `register_global_func` 注册函数：

```cpp
#include <tvm/ffi/function.h>

// 在模块初始化或程序启动时注册
void RegisterMyFunctions() {
  using namespace tvm::ffi;

  register_global_func("mymodule.add", [](int a, int b) {
    return a + b;
  });

  register_global_func("mymodule.greet", [](String name) -> String {
    return "Hello, " + name;
  });
}
```

Python 端通过 `get_global_func` 获取并调用：

```python
from tvm_ffi import get_global_func

add = get_global_func("mymodule.add")
result = add(3, 4)  # 7

greet = get_global_func("mymodule.greet")
print(greet("World"))  # "Hello, World"
```

**参见：** [12-示例1：Hello World](12-examples.md#示例-1hello-world---c-函数注册与-python-调用)

---

## Q: 如何将 Python 回调函数传给 C++？

C++ 端将参数声明为 `PackedFunc` 类型：

```cpp
#include <tvm/ffi/function.h>

register_global_func("mymodule.apply", [](PackedFunc callback, int x) {
  // 调用 Python 回调
  Any result = callback(x * 2);
  return result;
});
```

Python 端直接传入函数或 lambda：

```python
from tvm_ffi import get_global_func

apply = get_global_func("mymodule.apply")

# 传入 lambda
result = apply(lambda x: x + 1, 5)
print(result)  # (5*2) + 1 = 11

# 传入命名函数
def my_callback(x):
    return x * x

result = apply(my_callback, 5)
print(result)  # (10)^2 = 100
```

**参见：** [12-示例5：Python回调](12-examples.md#示例-5python-回调传入-c)

---

## Q: 为什么出现 "type_index not registered" 错误？

这个错误表示使用了未注册到类型系统的自定义 Object 类型。常见原因：

1. **忘记 `TVM_FFI_DECLARE_OBJECT_INFO` 宏**

```cpp
// ❌ 错误：缺少宏
class MyObj : public Object {
 public:
  int value;
  // 缺少 TVM_FFI_DECLARE_OBJECT_INFO！
};

// ✅ 正确
class MyObj : public Object {
 public:
  int value;
  TVM_FFI_DECLARE_OBJECT_INFO(MyObj, Object);  // 必须添加
};
```

2. **忘记使用 `TVM_FFI_REGISTER_OBJECT` 注册**

```cpp
// 在全局作用域执行注册（不要放在函数体内）
TVM_FFI_REGISTER_OBJECT(MyObj, "mymodule.MyObj");
```

3. **C++ 端和 Python 端的类型名称不匹配**

```cpp
// C++ 注册名为 "mymodule.MyObj"
TVM_FFI_REGISTER_OBJECT(MyObj, "mymodule.MyObj");
```

```python
# Python 端必须使用完全相同的名称
@register_object("mymodule.MyObj")  # 名称必须完全一致
class MyObj:
    pass
```

4. **包含自定义类型的共享库未加载**

确保在使用类型前调用 `load_module()` 加载了包含注册代码的共享库。

---

## Q: 如何创建自定义 Object 类型？

按照 `FooObj + Foo` 配对模式定义：

```cpp
#include <tvm/ffi/object.h>

namespace tvm::ffi::mymodule {

// 1. 实现类（继承 Object）
class CounterObj : public Object {
 public:
  int count = 0;

  void increment() { count++; }
  int get() const { return count; }

  TVM_FFI_DECLARE_OBJECT_INFO(CounterObj, Object);
};

// 2. 引用句柄类（继承 ObjectRef）
class Counter : public ObjectRef<CounterObj> {
 public:
  TVM_DEFINE_OBJECT_REF_METHODS(Counter, ObjectRef, CounterObj);

  Counter() : ObjectRef(make_object<CounterObj>()) {}

  TVM_DEFINE_OBJECT_REF_METHOD(increment);
  TVM_DEFINE_OBJECT_REF_METHOD(get);

  // 或字段访问
  TVM_DEFINE_OBJECT_REF_FIELD(count, int, count);
};

// 3. 注册到类型系统
TVM_FFI_REGISTER_OBJECT(CounterObj, "mymodule.Counter");

}  // namespace tvm::ffi::mymodule
```

**参见：** [12-示例2：自定义Object](12-examples.md#示例-2自定义-object-类型)

---

## Q: Array 和 List 有什么区别？

| 特性 | `Array<T>` | `List<T>` |
|------|------------|-----------|
| 可变性 | 逻辑不可变（COW） | 可变 |
| 拷贝开销 | O(1)（COW 引用） | O(n) 元素拷贝 |
| 内存布局 | 连续内存 | 节点式结构 |
| 随机访问 | O(1) | O(n) |
| 迭代性能 | 快（连续内存） | 较慢 |
| 适用场景 | 数据传递、配置、只读数据 | 需要频繁修改的列表 |

```cpp
// Array：适合传递数据，拷贝便宜
Array<int> create_data() {
  Array<int> data;
  for (int i = 0; i < 100; ++i) data.push_back(i);
  return data;  // 返回时只是移动，无拷贝
}

void process(Array<int> data) {
  auto copy = data;  // O(1) 拷贝
  // copy.push_back(999);  // 修改时才触发实际拷贝（COW）
}

// List：适合需要频繁原地修改的场景
List<int> build_list() {
  List<int> lst;
  for (int i = 0; i < 100; ++i) {
    lst.push_back(i);  // 原地追加，高效
  }
  return lst;
}
```

---

## Q: Map 和 Dict 有什么区别？

| 特性 | `Map<K, V>` | `Dict<K, V>` |
|------|-------------|--------------|
| 可变性 | 逻辑不可变（COW） | 可变 |
| 键顺序 | 有序（按键排序） | 插入顺序 |
| 拷贝开销 | O(1)（COW 引用） | O(n) 元素拷贝 |
| 查找性能 | O(log n) 二分查找 | O(1) 哈希表 |
| 适用场景 | 配置元数据、跨语言传递 | 高频查找/修改的字典 |

```cpp
// Map：有序、COW，适合传递配置
Map<String, int> get_config() {
  return Map<String, int>{
    {"batch_size", 32},
    {"epochs", 100},
    {"lr", 0.001}
  };
}

// Dict：哈希表，适合高频操作
Dict<String, Any> build_dynamic_dict() {
  Dict<String, Any> d;
  d["loss"] = 0.5;
  d["step"] = 42;
  return d;
}
```

---

## Q: TVM FFI 如何实现 ABI 稳定性？

TVM FFI 通过以下机制保证跨编译器/版本的 ABI 稳定性：

1. **C ABI 作为边界：** 所有跨语言调用通过稳定的 C 函数接口进行
2. **类型擦除的 `Any` 值：** 使用 `TVM_FFI_Any` 结构（16字节）传递任意类型，其布局固定：
   ```c
   typedef struct {
     union {
       int64_t v_int64;
       double v_float64;
       void* v_handle;
     };
     int32_t type_code;
     int32_t padding;
   } TVM_FFI_Any;
   ```
3. **对象通过 vtable 访问：** Object 的方法通过稳定的 vtable 偏移访问，不依赖 C++ 名称修饰
4. **不暴露 STL 类型：** 公共 API 中不出现 `std::string`、`std::vector` 等布局不稳定的类型
5. **明确的版本控制：** 核心数据结构保持向后兼容

这意味着：用 GCC 编译的共享库可以被 MSVC 编译的程序加载，Python 和 C++ 之间的类型传递不依赖于特定编译器实现。

---

## Q: 可以不用 Python，只使用 C++ 版 TVM FFI 吗？

**完全可以！** TVM FFI 是一个独立的 C++ 库，Python 绑定只是可选组件。

```cmake
# CMake 中禁用 Python 绑定
set(TVM_FFI_BUILD_PYTHON OFF CACHE BOOL "" FORCE)
add_subdirectory(3rdparty/tvm-ffi)
```

纯 C++ 使用示例：

```cpp
#include <tvm/ffi/function.h>
#include <tvm/ffi/container/array.h>
#include <iostream>

int main() {
  using namespace tvm::ffi;

  // 注册函数
  register_global_func("fib", [](int n) -> int {
    if (n <= 1) return n;
    int a = 0, b = 1;
    for (int i = 2; i <= n; ++i) {
      int c = a + b;
      a = b;
      b = c;
    }
    return b;
  });

  // 调用
  auto fib = get_global_func("fib");
  std::cout << "fib(10) = " << fib(10).cast<int>() << std::endl;  // 55

  // 使用容器
  Array<int> arr{1, 2, 3, 4, 5};
  int sum = 0;
  for (int x : arr) sum += x;
  std::cout << "sum = " << sum << std::endl;  // 15

  return 0;
}
```

---

## Q: 如何从共享库导出 C API？

使用 `extern "C"` + `TVM_FFI_DLL_EXPORT` 标记导出函数，并使用 `TVM_FFI_SAFE_CALL_BEGIN/END` 保证异常安全：

```cpp
#include <tvm/ffi/function.h>
#include <tvm/ffi/error.h>

#ifdef __cplusplus
extern "C" {
#endif

// 导出的 C API
TVM_FFI_DLL_EXPORT int MyLibraryAdd(int a, int b, int* out_result) {
  TVM_FFI_SAFE_CALL_BEGIN();

  if (out_result == nullptr) {
    TVM_FFI_THROW(ValueError) << "out_result must not be null";
  }
  *out_result = a + b;
  return 0;

  TVM_FFI_SAFE_CALL_END();
}

TVM_FFI_DLL_EXPORT int MyLibraryCallFunc(
    const char* name,
    const TVM_FFI_Any* args,
    int num_args,
    TVM_FFI_Any* out_ret
) {
  TVM_FFI_SAFE_CALL_BEGIN();

  auto fn = tvm::ffi::get_global_func(name);
  tvm::ffi::Any result = fn.ApplyArray(
      tvm::ffi::Any(args, num_args));
  *out_ret = result.MoveTo<TVM_FFI_Any>();
  return 0;

  TVM_FFI_SAFE_CALL_END();
}

// 获取错误信息
TVM_FFI_DLL_EXPORT const char* MyLibraryGetLastError() {
  return TVM_FFIGetLastError();
}

#ifdef __cplusplus
}
#endif
```

---

## Q: 如何跨 FFI 边界处理错误？

有三种模式：

1. **C++ 异常 → Python 异常（自动）：**
   ```cpp
   // C++ 端抛出
   register_global_func("div", [](double a, double b) -> double {
     if (b == 0) TVM_FFI_THROW(ValueError) << "Division by zero";
     return a / b;
   });
   ```
   ```python
   # Python 端自动转为 Python 异常
   try:
       div(1, 0)
   except ValueError as e:
       print(f"Error: {e}")
   ```

2. **Expected<T>（不抛异常，显式检查）：**
   ```cpp
   Expected<double> safe_div(double a, double b) {
     if (b == 0) return Error(ErrorKind::ValueError, "div by zero");
     return a / b;
   }
   ```

3. **C API 错误码（最底层）：**
   ```cpp
   // 返回 0 成功，非 0 失败，通过 TVM_FFIGetLastError 获取消息
   ```

**参见：** [12-示例6：错误处理](12-examples.md#示例-6错误处理跨语言边界)

---

## Q: 如何在 FFI 类型和 STL 类型之间转换？

TVM FFI 的 `extra/stl_interop.h` 提供了 STL 互操作支持：

```cpp
#include <tvm/ffi/extra/stl_interop.h>

// STL 容器自动转换为 FFI 容器
std::vector<int> std_vec{1, 2, 3};
Array<int> ffi_arr = Array<int>::FromSTL(std_vec);
// 或隐式转换：Array<int> ffi_arr = std_vec;

// FFI 容器转回 STL
std::vector<int> std_vec2 = ffi_arr.ToSTL();

// std::map -> Map
std::map<std::string, int> std_map{{"a", 1}, {"b", 2}};
Map<String, int> ffi_map = std_map;

// std::string <-> String
std::string std_str = "hello";
String ffi_str = std_str;
std::string std_str2 = ffi_str;
```

**注意：** 转换涉及数据拷贝，不要在热路径中频繁转换。

---

## Q: 如何与 PyTorch/NumPy 交换张量数据？

TVM FFI 的 NDArray 遵循 DLPack 标准，可以与 NumPy、PyTorch、TensorFlow 等零拷贝转换：

```python
from tvm_ffi import NDArray
import numpy as np

# NumPy -> NDArray（零拷贝，共享内存）
np_arr = np.array([1.0, 2.0, 3.0], dtype=np.float64)
tvm_arr = NDArray.from_numpy(np_arr)

# 修改 NDArray 会影响 NumPy 数组！
tvm_arr.numpy()[0] = 999.0
print(np_arr[0])  # 999.0（同一内存）

# NDArray -> NumPy（零拷贝）
np_arr2 = tvm_arr.numpy()

# PyTorch 互操作（通过 DLPack）
import torch

# PyTorch -> NDArray
torch_tensor = torch.tensor([1.0, 2.0, 3.0])
tvm_arr = NDArray.from_dlpack(torch_tensor)

# NDArray -> PyTorch
torch_tensor2 = torch.from_dlpack(tvm_arr)
```

C++ 端通过 `DLTensor*` 指针访问原始数据：
```cpp
NDArray arr = NDArray::Empty({n}, DLDataType{kDLFloat, 64, 1}, DLDevice{kDLCPU, 0});
double* data = static_cast<double*>(arr->data);  // 直接读写数据指针
```

**参见：** [12-示例4：张量操作](12-examples.md#示例-4张量操作与-numpy-交互)、[10-DLPack集成](10-dlpack-integration.md)

---

## Q: 修改 C++ 代码后如何重新构建？

根据安装方式选择：

```bash
# 1. Python 可编辑安装（最常用）
uv pip install --force-reinstall -e .

# 2. 纯 C++ 构建
cmake --build build_cpp --target tvm_ffi_shared

# 3. 如果改了 CMake 配置，先清理再重建
rm -rf build/ build_cpp/
uv pip install --force-reinstall -e .
```

| 修改内容 | 需要的操作 |
|----------|------------|
| Python `.py` 文件 | 无（立即生效） |
| C++ `.h`/`.cc` 文件 | 重新运行 `uv pip install -e .` |
| Cython `.pyx` 文件 | 重新运行 `uv pip install -e .` |
| `CMakeLists.txt` | 删除 build 目录后重新安装 |

---

## Q: 为什么会出现链接器错误（linker errors）？

常见链接错误及解决方案：

### 错误：undefined reference to `register_global_func...`

**原因：** 没有链接到 tvm_ffi 库

**解决：** CMake 中添加：
```cmake
target_link_libraries(your_target PRIVATE tvm::ffi)
```

### 错误：undefined reference to `__tvm_ffi_xxxInit`

**原因：** 模块初始化函数未被导出（尤其在 Windows 上）

**解决：** 添加 `TVM_FFI_DLL_EXPORT` 宏：
```cpp
extern "C" TVM_FFI_DLL_EXPORT int __tvm_ffi_mymodInit() { ... }
```

### 错误：multiple definition / ODR violation

**原因：** `TVM_FFI_REGISTER_OBJECT` 等宏写在头文件中被多次包含

**解决：** 注册宏放在 `.cc` 文件中，头文件只放类声明。

### Windows 特有：unresolved external symbol

**原因：** Windows DLL 需要显式标记导出符号

**解决：** 使用 `TVM_FFI_DLL_EXPORT`，确保使用正确的运行时库（/MD 而非 /MT）。

---

## Q: 如何调试 FFI 崩溃问题？

### 1. 启用 Debug 构建

```bash
cmake . -B build -DCMAKE_BUILD_TYPE=Debug
# Debug 构建包含断言和调试符号，更容易定位问题
```

### 2. 使用 GDB/LLDB 附加调试器

```bash
# Linux
gdb --args python your_script.py
(gdb) run
(gdb) bt  # 崩溃时打印堆栈

# macOS
lldb -- python your_script.py
(lldb) run
(lldb) bt
```

### 3. 检查常见崩溃原因

| 崩溃场景 | 可能原因 | 检查点 |
|----------|----------|--------|
| cast 时崩溃 | 类型不匹配 | 使用 `as<T>()` 前先 `is_type<T>()` 检查 |
| 访问对象字段崩溃 | 对象已释放或类型错误 | 检查引用是否有效、类型注册是否正确 |
| 回调调用时崩溃 | 回调函数已被 GC | C++ 持有 PackedFunc 期间确保 Python 端有引用 |
| DLL 加载崩溃 | 符号未导出/初始化函数崩溃 | 检查 `__tvm_ffi_<name>Init` 是否正确导出 |

### 4. 使用 AddressSanitizer 检测内存问题

```bash
# 用 ASAN 构建
CXX=clang++ cmake . -B build_asan -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_CXX_FLAGS="-fsanitize=address -fno-omit-frame-pointer"
cmake --build build_asan
```

### 5. 启用 TVM FFI 错误上下文

```cpp
// 使用 TVM_FFI_TRY/CATCH 添加上下文
TVM_FFI_TRY {
  risky_call();
} TVM_FFI_CATCH(Error& e) {
  e.PushContext("your_function", "additional info");
  throw;
}
```

---

## Q: TVM FFI 有 Rust 支持吗？

是的，TVM FFI 提供三层 Rust 支持：

| Crate | 层级 | 说明 |
|-------|------|------|
| `tvm-ffi-sys` | 原始 C 绑定 | 直接的 `extern "C"` 绑定，unsafe |
| `tvm-ffi-macros` | 过程宏 | `#[tvm_ffi::function]` 等属性宏 |
| `tvm-ffi` | 高层安全 API | 封装好的安全 Rust API |

```rust
// 使用高层 Rust API
use tvm_ffi::{register_global_func, get_global_func, Array};

fn main() {
    // 注册函数
    register_global_func("rust.add", |a: i32, b: i32| -> i32 {
        a + b
    });

    // 调用函数
    let add = get_global_func("rust.add").unwrap();
    let result: i32 = add.call((2, 3)).unwrap();
    println!("2 + 3 = {}", result);  // 5

    // 使用容器
    let arr = Array::from_vec(vec![1, 2, 3, 4, 5]);
    let sum: i32 = arr.iter().sum();
}
```

```bash
# 运行 Rust 测试
cd rust/
cargo test
```

---

## Q: TVM FFI 可以用于非机器学习用途吗？

**当然可以！** 虽然 TVM FFI 最初为 Apache TVM（机器学习编译器）设计，但它是一个**通用的跨语言 FFI 框架**，适用于任何需要高性能 C++/Python/Rust 互操作的场景。

适用场景包括：
- 高性能计算库的 Python 绑定
- 游戏引擎脚本层
- 插件/扩展系统
- 跨语言数据序列化
- 动态模块加载系统
- 需要稳定 ABI 的 C++ API

不适合的场景：
- 只需 C++ 内部使用，无跨语言需求（直接用 C++ 即可）
- 对启动时间极度敏感（函数注册有少量开销）

---

## Q: 如何添加自定义类型转换？

可以为你的自定义类型注册自动转换规则：

```cpp
#include <tvm/ffi/type_convert.h>

// 方式1：为自定义类型定义 Any 转换特化
namespace tvm::ffi {

template<>
struct TypeConverter<MyCustomType, Any> {
  static Any Convert(const MyCustomType& val) {
    // 将 MyCustomType 转为 Any
    return Map<String, Any>{
      {"value", val.value},
      {"name", val.name}
    };
  }
};

template<>
struct TypeConverter<Any, MyCustomType> {
  static MyCustomType Convert(const Any& val) {
    // 将 Any 转为 MyCustomType
    auto m = val.cast<Map<String, Any>>();
    return MyCustomType{
      m["value"].cast<int>(),
      m["name"].cast<String>()
    };
  }
};

}  // namespace tvm::ffi
```

Python 端通过 `register_object` 注册类型映射：

```python
from tvm_ffi import register_object

@register_object("mymodule.MyType")
class MyType:
    # 定义属性和方法
    pass
```

---

**本章导航：**
- 上一章：[13-最佳实践与性能优化](13-best-practices.md)
- 下一章：[15-参考资料与学习路径](15-resources.md)
- [返回目录](README.md)
