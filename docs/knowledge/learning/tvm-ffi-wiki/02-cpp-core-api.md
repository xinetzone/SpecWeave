---
title: "02 - C++ 核心 API：Any、Object、Function、Tensor"
date: 2026-07-05
source: "spec:create-tvm-ffi-wiki-tutorial"
tags: [tvm-ffi, ffi, cpp, core-api]
---

# C++ 核心 API：Any、Object、Function、Tensor

本章介绍 TVM FFI C++ 层最核心的四个 API：`Any`（类型擦除值）、`Object`（引用计数对象）、`Function`（类型擦除可调用对象）和 `Tensor`（DLPack 兼容张量），以及配套的错误处理机制。所有头文件位于 `include/tvm/ffi/` 目录。

---

## 1. Any：类型擦除值

`Any` 是 TVM FFI 的基石，它通过一个 16 字节的 POD union（`TVMFFIAny`）实现类型擦除，能够承载 int、float、bool、string、Object 指针、Function、None 等值类型。`AnyView` 是其非持有版本（non-owning view），与 C ABI 直接兼容。

**源文件**：`include/tvm/ffi/any.h`

### 1.1 Any 与 AnyView 的关系

```cpp
#include <tvm/ffi/any.h>
using namespace tvm::ffi;

// AnyView 是 POD、trivially copyable，大小 == sizeof(TVMFFIAny) == 16
static_assert(sizeof(AnyView) == 16);
static_assert(sizeof(Any) == 16);
static_assert(std::is_trivially_copyable_v<AnyView>);
```

- `AnyView`：**非持有**视图，不管理生命周期，只做类型检查和值读取。
- `Any`：**持有**版本，析构时自动减少引用计数（对于 Object 类型）或释放堆内存（对于长字符串）。
- `Any` 可零开销转换为 `AnyView`（`operator AnyView()`）。

### 1.2 构造与赋值

`Any` 使用模板构造函数，通过 `TypeTraits<T>::MoveToAny` 将任意 FFI 支持的类型移入 union：

```cpp
Any a;                // None
Any b = 42;           // int
Any c = 3.14;         // double
Any d = true;         // bool
Any e = String("hello");  // FFI String
Any f = nullptr;      // None

// 也可以从 AnyView 构造
AnyView view = b;     // 零拷贝创建视图
Any g = view;         // 从视图构造 Any（会增加对象引用、拷贝字符串等）
```

### 1.3 类型检查与转换

提供三个层次的类型转换方法：

| 方法 | 行为 | 失败时 |
|------|------|--------|
| `as<T>()` | 严格匹配，不做隐式转换 | 返回 `std::nullopt`（Any 版本为移动语义） |
| `as_or_throw<T>()` | 严格匹配 | 抛出 `TypeError` |
| `cast<T>()` | 尝试兼容转换（如 int→float） | 抛出 `TypeError` |
| `try_cast<T>()` | 尝试兼容转换 | 返回 `std::nullopt` |

```cpp
Any x = 42;

// 严格类型检查
std::optional<int> i = x.as<int>();          // 42
std::optional<double> d = x.as<double>();    // nullopt（int ≠ double 严格匹配）

// 兼容转换
double d2 = x.cast<double>();                // 42.0（允许 int→double）

// 抛出异常版本
int i2 = x.as_or_throw<int>();

// 运行时类型查询
std::string key = x.GetTypeKey();            // "int"
int32_t tidx = x.type_index();               // TypeIndex::kTVMFFIInt

// nullptr 判断
bool is_none = (x == nullptr);               // false
```

对于 Object 子类，`as<T>()` 有特化版本直接返回 `const T*` 指针（类型不匹配返回 `nullptr`）：

```cpp
Any obj = /* some ObjectRef */;
if (const ArrayObj* arr = obj.as<ArrayObj>()) {
    // 是数组对象
}
```

### 1.4 AnyView 使用场景

`AnyView` 主要用于 FFI 函数调用边界，对应 C ABI 的 `const TVMFFIAny* args` 参数：

```cpp
// PackedFunc 调用约定
void MyPackedFunc(const AnyView* args, int32_t num_args, Any* rv) {
    for (int32_t i = 0; i < num_args; ++i) {
        std::optional<int> arg = args[i].as<int>();
        if (arg) { /* 处理 int 参数 */ }
    }
    *rv = Any(0);
}
```

### 1.5 AnyHash / AnyEqual

`AnyHash` 和 `AnyEqual` 是为字符串和自定义类型感知的哈希/比较仿函数，可直接用于 STL 容器：

```cpp
std::unordered_map<Any, int, AnyHash, AnyEqual> map;
map[Any(String("key"))] = 42;
```

---

## 2. Object：引用计数对象系统

TVM FFI 的对象系统采用**侵入式引用计数**（intrusive ref-counting），每个对象内部持有原子引用计数，`ObjectPtr<T>` 是智能指针，`ObjectRef` 是所有对象句柄的基类。

**源文件**：`include/tvm/ffi/object.h`

### 2.1 核心类层次

```
Object (含 TVMFFIObject 头部：ref_count + type_index + deleter)
  ├── FunctionObj
  ├── TensorObj (同时继承 DLTensor)
  ├── ArrayObj, MapObj, StringObj, ...
  └── 用户自定义 FooObj

ObjectRef (持有 ObjectPtr<Object>)
  ├── Function
  ├── Tensor
  ├── Array<T>, Map<K,V>, String, ...
  └── 用户自定义 Foo (对应 FooObj)
```

### 2.2 Object 基类关键字段

每个 `Object` 子类需声明以下静态常量（通过宏自动完成）：

- `_type_key`：全局唯一字符串标识，如 `"myproject.Foo"`
- `_type_index`：静态类型索引（或设为 `TypeIndex::kTVMFFIDynObject` 动态分配）
- `_type_final`：是否为终类（无子类），终类可优化 `IsInstance` 检查
- `_type_child_slots`：预留子类槽位数，用于快速类型检查
- `_type_mutable`：是否暴露非常量指针访问

### 2.3 声明宏

- `TVM_FFI_DECLARE_OBJECT_INFO(TypeKey, TypeName, ParentType)`：声明可继承对象信息（动态类型索引）。
- `TVM_FFI_DECLARE_OBJECT_INFO_FINAL(TypeKey, TypeName, ParentType)`：声明终类。
- `TVM_FFI_DECLARE_OBJECT_INFO_STATIC(TypeKey, TypeName, ParentType)`：使用静态类型索引（框架内置类型使用）。
- `TVM_FFI_DEFINE_OBJECT_REF_METHODS_NULLABLE(TypeName, ParentType, ObjectName)`：定义可空句柄方法。
- `TVM_FFI_DEFINE_OBJECT_REF_METHODS_NOTNULLABLE(TypeName, ParentType, ObjectName)`：定义非空句柄方法。

### 2.4 创建自定义对象

遵循 **FooObj + Foo** 模式：

```cpp
#include <tvm/ffi/object.h>
using namespace tvm::ffi;

// ---------- 对象数据类（FooObj） ----------
class MyVecObj : public Object {
public:
    double x, y, z;

    // 必须声明对象元信息
    static constexpr const char* _type_key = "demo.MyVec";
    static constexpr bool _type_final = false;
    static constexpr uint32_t _type_child_slots = 0;
    static constexpr bool _type_child_slots_can_overflow = true;
    static constexpr bool _type_mutable = false;
    TVM_FFI_DECLARE_OBJECT_INFO_PREDEFINED_TYPE_KEY(MyVecObj, Object);
};

// ---------- 对象句柄类（MyVec） ----------
class MyVec : public ObjectRef {
public:
    MyVec() = default;
    explicit MyVec(ObjectPtr<MyVecObj> n) : ObjectRef(std::move(n)) {}
    explicit MyVec(UnsafeInit tag) : ObjectRef(tag) {}
    TVM_FFI_DEFINE_DEFAULT_COPY_MOVE_AND_ASSIGN(MyVec)

    // 便捷访问器
    double x() const { return get()->x; }
    double y() const { return get()->y; }
    double z() const { return get()->z; }

    using ContainerType = MyVecObj;
    static constexpr bool _type_is_nullable = true;

private:
    const MyVecObj* get() const {
        return static_cast<const MyVecObj*>(ObjectRef::get());
    }
};

// ---------- 使用 ----------
MyVec make_vec(double x, double y, double z) {
    ObjectPtr<MyVecObj> obj = make_object<MyVecObj>();
    obj->x = x;
    obj->y = y;
    obj->z = z;
    return MyVec(std::move(obj));
}

void example() {
    MyVec v = make_vec(1.0, 2.0, 3.0);
    double len = std::sqrt(v.x()*v.x() + v.y()*v.y() + v.z()*v.z());

    // 类型检查
    if (v->IsInstance<MyVecObj>()) {
        // ...
    }

    // 引用计数查询
    int cnt = v.use_count();
}
```

### 2.5 make_object

`make_object<T>(args...)` 在堆上分配对象，设置 `type_index` 和 `deleter`，返回 `ObjectPtr<T>`：

```cpp
ObjectPtr<MyVecObj> obj = make_object<MyVecObj>();
// obj 已经持有引用计数 1
```

### 2.6 ObjectPtr 与 WeakObjectPtr

- `ObjectPtr<T>`：强引用智能指针，类似 `std::shared_ptr`，但使用侵入式计数（零额外开销）。
- `WeakObjectPtr<T>`：弱引用，需通过 `lock()` 提升为强引用：

```cpp
ObjectPtr<MyVecObj> strong = make_object<MyVecObj>();
WeakObjectPtr<MyVecObj> weak = strong;

if (ObjectPtr<MyVecObj> locked = weak.lock()) {
    // 对象仍然存活
}
```

### 2.7 ObjectRef 常用方法

```cpp
MyVec v = make_vec(1, 2, 3);

bool ok = v.defined();         // 是否非空
bool same = v.same_as(other);  // 指针相等（浅比较）
const MyVecObj* ptr = v.as<MyVecObj>();       // 向下转型，失败返回 nullptr
MyVec v2 = v.as_or_throw<MyVec>();            // 向下转型，失败抛异常
std::optional<MyVec> v3 = std::move(v).as<MyVec>();  // 移动语义转型
int idx = v.type_index();                     // 运行时类型索引
std::string key = v.GetTypeKey();             // 类型键字符串
```

---

## 3. Function：类型擦除可调用对象

`Function` 是 TVM FFI 的一等公民函数类型，底层 `FunctionObj` 封装任意可调用对象，通过统一的 packed 调用约定 `(const AnyView* args, int32_t num_args, Any* rv)` 进行调用。

**源文件**：`include/tvm/ffi/function.h`

### 3.1 函数注册与获取

使用 `register_global_func` 注册全局函数，`get_global_func` 获取：

```cpp
#include <tvm/ffi/function.h>
using namespace tvm::ffi;

// 注册一个普通函数
int Add(int a, int b) { return a + b; }

TVM_FFI_REGISTER_GLOBAL_FUNC("demo.add", Add);

// 注册 lambda
TVM_FFI_REGISTER_GLOBAL_FUNC("demo.mul", [](int a, int b) -> int {
    return a * b;
});

// 获取并调用
std::optional<Function> f = get_global_func("demo.add");
if (f) {
    Any result = (*f)(3, 4);       // 自动打包参数，返回 Any
    int sum = result.cast<int>();  // 7
}
```

### 3.2 operator() 可变参数调用

`Function::operator()` 支持可变参数模板，自动将 C++ 参数打包为 `AnyView` 数组：

```cpp
Function f = get_global_func("demo.add").value();
Any rv = f(1, 2);                  // 两参数
Any rv2 = f(Any(1), Any(2));       // 也可直接传 Any
```

返回值为 `Any`，需要通过 `cast<T>()` 解包。

### 3.3 PackedFunc 原始形式

最底层的调用签名直接对应 C ABI：

```cpp
using FPacked = void(*)(const AnyView* args, int32_t num_args, Any* rv);
```

直接使用此形式编写函数可避免模板展开开销：

```cpp
void MyPackedAdd(const AnyView* args, int32_t num_args, Any* rv) {
    TVM_FFI_ICHECK_EQ(num_args, 2);
    int a = args[0].cast<int>();
    int b = args[1].cast<int>();
    *rv = Any(a + b);
}

TVM_FFI_REGISTER_GLOBAL_FUNC("demo.packed_add",
    [](const AnyView* args, int32_t num_args, Any* rv) {
        MyPackedAdd(args, num_args, rv);
    });
```

### 3.4 C 导出安全宏

当需要从动态库导出 C ABI 函数给外部调用时，C++ 异常不能跨越 C 边界。使用 `TVM_FFI_SAFE_CALL_BEGIN` / `TVM_FFI_SAFE_CALL_END` 包裹函数体，自动捕获异常并通过 TLS 传递错误：

```cpp
#include <tvm/ffi/c_api.h>

extern "C" int TVMFFICallDemoAdd(TVMFFIAny* args, int32_t num_args, TVMFFIAny* rv) {
    TVM_FFI_SAFE_CALL_BEGIN();

    // 正常 C++ 代码，可以抛异常
    Function f = get_global_func("demo.add").value();
    Any result = f(AnyView::CopyFromTVMFFIAny(args[0]),
                   AnyView::CopyFromTVMFFIAny(args[1]));
    *rv = details::AnyUnsafe::MoveAnyToTVMFFIAny(std::move(result));

    TVM_FFI_SAFE_CALL_END();
}
```

- 宏展开为 `try { ... return 0; } catch (const Error&) { 设置错误; return -1; } catch (const std::exception&) { ... }`
- 返回 `0` 表示成功，`-1` 表示异常；调用方通过 `TVMFFIErrorMoveFromRaised` 获取错误对象。
- 配套宏 `TVM_FFI_CHECK_SAFE_CALL(func)` 检查返回码，失败则抛出从 TLS 取出的异常。

### 3.5 FunctionObj 内部机制

`FunctionObj` 同时继承 `Object` 和 `TVMFFIFunctionCell`，后者包含两个函数指针：

- `cpp_call`：快速路径，直接 C++ ABI 调用，异常可正常传播（用于同进程内 C++ 调用）。
- `safe_call`：安全路径，C 链接约定，返回错误码（用于跨语言/跨动态库调用）。

注册 lambda 或普通函数时，`FunctionObjImpl<TCallable>` 模板自动适配两种调用方式。

---

## 4. Tensor：DLPack 兼容张量

`Tensor` 是 DLPack 标准的 C++ 封装，底层 `TensorObj` 同时继承 `Object` 和 `DLTensor`，支持零拷贝与 PyTorch/NumPy/CUDA 等框架交互。

**源文件**：`include/tvm/ffi/container/tensor.h`

### 4.1 Tensor 的基本属性

```cpp
#include <tvm/ffi/container/tensor.h>
using namespace tvm::ffi;

// 访问张量属性（假设有一个 Tensor t）
void inspect(const Tensor& t) {
    void* data      = t.data_ptr();      // 数据指针
    DLDevice dev    = t.device();        // 设备（kDLCPU/kDLCUDA/...）
    int32_t ndim    = t.ndim();          // 维度数
    DLDataType dtype = t.dtype();        // 数据类型
    ShapeView shape = t.shape();         // 形状视图
    ShapeView strides = t.strides();     // 步长视图
    int64_t n       = t.numel();         // 元素总数
    uint64_t off    = t.byte_offset();   // 字节偏移
    bool contig     = t.IsContiguous();  // 是否连续存储
    int64_t d0      = t.size(0);         // 第0维大小（支持负数索引）
}
```

### 4.2 CPU 张量创建示例

通过 `FromNDAlloc` 自定义分配器创建张量：

```cpp
struct CPUAlloc {
    void AllocData(DLTensor* tensor) {
        size_t nbytes = GetDataSize(*tensor);
        tensor->data = std::malloc(nbytes);
    }
    void FreeData(DLTensor* tensor) {
        std::free(tensor->data);
        tensor->data = nullptr;
    }
};

void create_tensor_example() {
    // float32, shape [2, 3], on CPU
    DLDevice cpu{kDLCPU, 0};
    DLDataType dtype{kDLFloat, 32, 1};
    Shape shape({2, 3});

    Tensor t = Tensor::FromNDAlloc(CPUAlloc(), ShapeView(shape), dtype, cpu);

    // 写入数据
    float* ptr = static_cast<float*>(t.data_ptr());
    for (int i = 0; i < t.numel(); ++i) ptr[i] = static_cast<float>(i);
}
```

### 4.3 DLPack 互操作

```cpp
// 转出为 DLManagedTensor（交给其他框架）
DLManagedTensor* mgr = t.ToDLPack();
// 使用后由接收方调用 mgr->deleter(mgr) 释放

// 从 DLManagedTensor 导入
Tensor t2 = Tensor::FromDLPack(mgr);

// 版本化 DLPack（v1.0+）
DLManagedTensorVersioned* mgr2 = t.ToDLPackVersioned();
Tensor t3 = Tensor::FromDLPackVersioned(mgr2);
```

### 4.4 TensorView：非持有视图

`TensorView` 类似 `AnyView`，是 `DLTensor` 的非持有副本，用于函数参数避免不必要的引用计数增减：

```cpp
float SumAll(TensorView tv) {
    TVM_FFI_ICHECK(tv.dtype().code == kDLFloat && tv.dtype().bits == 32);
    const float* data = static_cast<const float*>(tv.data_ptr());
    float sum = 0;
    for (int64_t i = 0; i < tv.numel(); ++i) sum += data[i];
    return sum;
}

// 可以从 Tensor 隐式构造
Tensor t = /* ... */;
float s = SumAll(t);
```

### 4.5 as_strided 视图

```cpp
// 创建一个不共享数据的步长视图（零拷贝切片）
Tensor row0 = t.as_strided(ShapeView({3}),           // 形状
                           ShapeView({1}),           // 步长
                           /*element_offset=*/0);
```

---

## 5. 错误处理

### 5.1 Error 类

`Error` 继承自 `ObjectRef` 和 `std::exception`，包含：
- `kind()`：错误种类字符串（`"TypeError"`、`"ValueError"`、`"RuntimeError"`、`"InternalError"`、`"IndexError"` 等）
- `message()`：错误消息
- `backtrace()`：堆栈回溯
- `cause_chain()`：因果链（可选）
- `extra_context()`：附加上下文对象（可选）

### 5.2 TVM_FFI_THROW 宏

使用流语法抛出异常，自动附带文件名、行号、函数签名和 backtrace：

```cpp
#include <tvm/ffi/error.h>

void check_positive(int x) {
    if (x <= 0) {
        TVM_FFI_THROW(ValueError) << "Expected positive number, got " << x;
    }
}
```

常用错误种类：`TypeError`、`ValueError`、`RuntimeError`、`IndexError`、`OverflowError`、`InternalError`、`EnvErrorAlreadySet`。

### 5.3 TVM_FFI_CHECK 系列宏

类似 glog CHECK 的断言宏：

```cpp
TVM_FFI_CHECK(x > 0, ValueError) << "x must be positive";
TVM_FFI_CHECK_LT(i, size, IndexError) << "index out of range";
TVM_FFI_CHECK_EQ(a, b, RuntimeError) << "a != b";
TVM_FFI_CHECK_NOTNULL(ptr, InternalError) << "null pointer";

// InternalError 简写
TVM_FFI_ICHECK(x > 0);
TVM_FFI_ICHECK_NOTNULL(ptr);

// Debug 版本（release 中被剥离）
TVM_FFI_DCHECK(x > 0);
```

### 5.4 Expected<T>

`Expected<T>` 是一种 `T | Error` 的 sum type，用于在不抛异常的路径上返回错误：

```cpp
#include <tvm/ffi/expected.h>

Expected<int> safe_divide(int a, int b) {
    if (b == 0) {
        return Error("ValueError", "division by zero", "");
    }
    return a / b;
}

void use() {
    Expected<int> r = safe_divide(10, 0);
    if (!r) {
        Error e = r.error();
        std::cerr << e.message() << std::endl;
    } else {
        int v = r.value();
    }
}
```

---

## 本章 API 速查表

| 头文件 | 核心类型 | 主要功能 |
|--------|----------|----------|
| `any.h` | `Any`, `AnyView` | 类型擦除值、非持有视图、类型转换 |
| `object.h` | `Object`, `ObjectPtr<T>`, `ObjectRef`, `WeakObjectPtr<T>` | 侵入式引用计数、对象基类、智能指针 |
| `function.h` | `Function`, `FunctionObj` | 类型擦除可调用对象、全局注册、packed 调用 |
| `container/tensor.h` | `Tensor`, `TensorObj`, `TensorView` | DLPack 张量、设备无关 N 维数组 |
| `error.h` | `Error`, `TVM_FFI_THROW`, `TVM_FFI_CHECK` | 异常类、断言宏、堆栈回溯 |
| `expected.h` | `Expected<T>` | 错误返回值类型（不抛异常路径） |
| `c_api.h` | `TVMFFIAny`, `TVMFFIFunctionCell`, SAFE_CALL 宏 | C ABI 基础类型与安全调用 |

---

[上一章](01-architecture.md) | [下一章 →](03-type-system.md)
