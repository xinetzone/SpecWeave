---
title: "03 - 类型系统：DType、Enum、Optional、String"
date: 2026-07-05
source: "spec:create-tvm-ffi-wiki-tutorial"
tags: [tvm-ffi, ffi, cpp, core-api]
---

# 类型系统：DType、Enum、Optional、String

TVM FFI 在 Any 的基础上构建了一组专用类型用于处理数据类型描述、枚举、可空值和字符串。本章介绍这些核心类型以及底层的 TypeTraits 映射机制和字节序工具。

**相关头文件**：
- `include/tvm/ffi/dtype.h`：数据类型（DLDataType 封装）
- `include/tvm/ffi/enum.h`：FFI 注册枚举
- `include/tvm/ffi/optional.h`：可空包装
- `include/tvm/ffi/string.h`：FFI 字符串与字节串
- `include/tvm/ffi/type_traits.h`：类型特征模板
- `include/tvm/ffi/endian.h`：字节序工具

---

## 1. DType：数据类型描述

`DLDataType`（来自 DLPack）是 TVM FFI 中描述张量元素类型的 POD 结构，包含三个字段：

| 字段 | 类型 | 含义 |
|------|------|------|
| `code` | `uint8_t` | 类型类别：`kDLInt`/`kDLUInt`/`kDLFloat`/`kDLBfloat`/`kDLBool`/float8 变体等 |
| `bits` | `uint8_t` | 位宽：8/16/32/64 等 |
| `lanes` | `uint16_t` | 向量通道数（标量为 1） |

DType 本身就是 `DLDataType`，它是一个值类型（非 Object），可直接放入 `Any`。

### 1.1 直接构造

```cpp
#include <tvm/ffi/dtype.h>
#include <dlpack/dlpack.h>
using namespace tvm::ffi;

// 手动构造
DLDataType fp32{kDLFloat, 32, 1};
DLDataType int8{kDLInt, 8, 1};
DLDataType vec4f32{kDLFloat, 32, 4};  // 4 路向量
DLDataType bf16{kDLBfloat, 16, 1};
DLDataType bool_t{kDLBool, 1, 1};     // 注意 bool 存储为 1 bit，但通常按 1 字节对齐
```

### 1.2 字符串构造

`StringToDLDataType` 支持 NumPy 风格的字符串，`DLDataTypeToString` 反向转换：

```cpp
DLDataType t1 = StringToDLDataType(String("float32"));   // kDLFloat/32/1
DLDataType t2 = StringToDLDataType(String("int8"));      // kDLInt/8/1
DLDataType t3 = StringToDLDataType(String("bfloat16"));  // kDLBfloat/16/1
DLDataType t4 = StringToDLDataType(String("uint64"));    // kDLUInt/64/1
DLDataType t5 = StringToDLDataType(String("float32x4")); // kDLFloat/32/4 (SIMD)
DLDataType t6 = StringToDLDataType(String("bool"));      // kDLBool/1/1

String s = DLDataTypeToString(fp32);   // "float32"
```

在 Any 中也支持字符串到 DType 的隐式转换：

```cpp
Any a = Any(String("float16"));
DLDataType t = a.cast<DLDataType>();   // 通过 TryCastFromAnyView 自动转换
```

### 1.3 类型代码字符串映射

| code | code 常量 | 字符串前缀 |
|------|-----------|-----------|
| 0 | `kDLInt` | `int` |
| 1 | `kDLUInt` | `uint` |
| 2 | `kDLFloat` | `float` |
| 3 | `kDLBfloat`（经 DLExtDataTypeCode=16 处理） | `bfloat` |
| 4 | `kDLBool` | `bool` |
| 5 | `kDLOpaqueHandle` | `handle` |
| float8 变体 | `kDLFloat8_e4m3fn` 等 | `float8_e4m3fn` 等 |

### 1.4 Any 中的 DType

`TypeTraits<DLDataType>` 直接把 `DLDataType` 塞入 `TVMFFIAny::v_dtype` 字段（POD 拷贝），不走对象引用计数：

```cpp
Any a = DLDataType{kDLFloat, 32, 1};
std::optional<DLDataType> t = a.as<DLDataType>();  // 严格匹配
```

`operator<<` 和 `operator==`/`operator!=` 在全局命名空间提供：

```cpp
std::cout << fp32 << std::endl;  // "float32"
bool eq = (fp32 == DLDataType{kDLFloat, 32, 1});  // true
```

---

## 2. Enum：FFI 注册枚举

TVM FFI 的枚举不是 C++ `enum class`，而是通过**单例对象**实现的。每个枚举值是一个进程唯一的 `EnumObj` 实例，通过反射注册，可跨语言访问并携带附加字段。

**源文件**：`include/tvm/ffi/enum.h`、`include/tvm/ffi/reflection/enum_def.h`

### 2.1 EnumObj 基类

每个枚举实例包含两个内置字段：
- `_value`：密集序号（int64_t，注册时按顺序分配）
- `_name`：名称字符串（String）

```cpp
class EnumObj : public Object {
public:
    int64_t _value;
    String _name;
    // ...
};
```

Enum 类型标记为 `kTVMFFISEqHashKindUniqueInstance`，即两个 Enum 相等当且仅当它们指向同一个单例对象（指针比较）。

### 2.2 自定义枚举

使用 `TVM_FFI_ENUM_ADD` 宏（配合反射的 `EnumDef`）注册枚举值。典型用法：

```cpp
// 在头文件声明
class OpKindObj;
class OpKind : public Enum {
public:
    TVM_FFI_DEFINE_OBJECT_REF_METHODS_NULLABLE(OpKind, Enum, OpKindObj);
};

class OpKindObj : public EnumObj {
public:
    static constexpr const char* _type_key = "demo.OpKind";
    TVM_FFI_DECLARE_OBJECT_INFO_FINAL("demo.OpKind", OpKindObj, EnumObj);
};

// 在 cc 文件通过反射注册
TVM_FFI_REGISTER_ENUM(OpKindObj)
    .add("Add")
    .add("Sub")
    .add("Mul")
    .add("Div");
```

### 2.3 查找和使用

通过 `EnumObj::Get<T>(name)` 按名称查找：

```cpp
Enum add = EnumObj::Get<OpKindObj>(String("Add"));
// add 是单例，多次 Get 返回同一对象
Enum add2 = EnumObj::Get<OpKindObj>(String("Add"));
assert(add.same_as(add2));  // 指针相等
```

枚举类型被 `Dict<String, ObjectRef>` 存储在类型属性列 `__ffi_enum_entries__` 中，查找时直接从表中取。

### 2.4 Python 集成

注册后的枚举在 Python 端自动暴露为同名类，属性访问返回单例：

```python
import tvm_ffi
OpKind = tvm_ffi.Enum("demo.OpKind")
print(OpKind.Add)        # demo.OpKind.Add
print(int(OpKind.Add))   # 0 (dense ordinal)
print(OpKind.Add.name)   # "Add"
```

枚举字段（declared fields）会通过反射自动暴露为 Python 属性；通过 `def_attr`（C++）/`def_attr`（Python）可以附加不修改 C++ 类定义的扩展属性。

---

## 3. Optional\<T\>：可空包装

`Optional<T>` 是 TVM FFI 的可空值类型，对不同的 T 有特化实现：

- **ObjectRef 子类**：用 `nullptr` 表示 nullopt，直接复用 `ObjectPtr` 存储空间（零额外开销）。
- **String / Bytes**：内部通过空状态表示 nullopt。
- **其他值类型**：退化为 `std::optional<T>` 封装。

**源文件**：`include/tvm/ffi/optional.h`

### 3.1 基本用法

```cpp
#include <tvm/ffi/optional.h>
using namespace tvm::ffi;

// ObjectRef 版本（零开销）
Optional<Tensor> maybe_tensor;        // 空
Optional<Tensor> t = Tensor(...);     // 有值
Optional<Tensor> n = nullptr;         // 显式置空

if (t) {                              // operator bool
    Tensor raw = t.value();           // 取值（空则抛异常）
    int64_t n = t->numel();           // operator->
}

Tensor raw2 = t.value_or(Tensor());   // 带默认值
```

### 3.2 值类型版本

```cpp
Optional<int> maybe_int;
maybe_int = 42;
if (maybe_int.has_value()) {
    int v = maybe_int.value();
}
int v2 = maybe_int.value_or(0);
int v3 = *maybe_int;                  // 仅在确认有值后使用
```

### 3.3 Any 互操作

`Optional<T>` 可直接放入 `Any`：空值映射为 `None`（nullptr），非空值直接按 T 的方式存储：

```cpp
Any a = Optional<int>(42);     // 存为 int
Any b = Optional<int>();       // 存为 None

Optional<int> x = b.cast<Optional<int>>();  // 自动从 None 恢复为空
```

### 3.4 Monadic 风格操作

```cpp
// 直接与底层值比较
Optional<Tensor> t = /* ... */;
if (t == some_tensor) { /* ... */ }
if (t != nullptr) { /* ... */ }
```

注意：目前 Optional 不提供 `map`/`and_then` 等函数式操作，但通过 `value_or` 和 `operator bool` 可以方便组合。

---

## 4. String：FFI 字符串类型

`String` 是 TVM FFI 的 UTF-8 字符串类型，底层 `StringObj` 继承自 `BytesObjBase`（Object + TVMFFIByteArray）。它采用**小字符串优化（SSO）**：短字符串直接内联在 `TVMFFIAny` 的 16 字节内（`kTVMFFISmallStr`），长字符串堆分配为 `StringObj`（`kTVMFFIStr`）。

**源文件**：`include/tvm/ffi/string.h`

### 4.1 构造与转换

```cpp
#include <tvm/ffi/string.h>
using namespace tvm::ffi;

String s1;                         // 空字符串
String s2("hello");                // 从 C 字符串构造
String s3 = String("world");       // 显式构造
std::string std_s = "from std";
String s4(std_s);                  // 从 std::string 构造（拷贝）
String s5(std::move(std_s));       // 从 std::string 移动构造（零拷贝）

// 转换回 std::string / string_view
std::string sv = s2;                        // 隐式转换为 std::string
std::string_view view = s2.string_view();   // string_view（零拷贝）
const char* cstr = s2.c_str();              // C 字符串（以 '\0' 结尾）
size_t len = s2.size();                     // 长度（字节）
const char* data = s2.data();               // 数据指针
bool empty = s2.empty();
```

### 4.2 小字符串优化

Any 中长度足够小的字符串不分配堆内存，直接存在 `TVMFFIAny::v_bytes` 中。`AnyHash` 和 `AnyEqual` 自动处理 `kTVMFFIStr`/`kTVMFFISmallStr` 两种表示之间的等价性：

```cpp
Any a = String("hi");     // 大概率是 SmallStr
Any b = String("hello world this is a longer string that exceeds the inline buffer");
// 两者比较时 AnyEqual 会正确处理跨表示相等
```

小字符串阈值在 `TVMFFIAny` union 的内联字节区大小决定（通常 7-12 字节，含长度字段）。

### 4.3 Bytes：原始字节串

`Bytes` 是与 `String` 并列的字节容器，语义类似 Python `bytes`：

```cpp
Bytes b1("raw\x00\x01data", 9);
Bytes b2 = b1;
const uint8_t* p = b1.data();
size_t n = b1.size();
```

`Bytes` 和 `String` 类型索引不同（`kTVMFFIBytes` vs `kTVMFFIStr`），但底层结构相同。

### 4.4 常用操作

```cpp
// 拼接、比较（通过 String 类方法）
String s = String("hello") + String(" world");
bool eq = (s == String("hello world"));

// 放入 Any
Any a = s;
String back = a.cast<String>();
std::optional<String> maybe = a.as<String>();   // 严格匹配
```

---

## 5. TypeTraits\<T\>：C++ 类型到 Any 的映射

`TypeTraits<T>` 是所有能放入 `Any` 的 C++ 类型必须特化的模板，它定义了类型擦除/恢复的所有操作。

**源文件**：`include/tvm/ffi/type_traits.h`

### 5.1 TypeTraits 必须提供的静态方法

```cpp
template <typename T>
struct TypeTraits : public TypeTraitsBase {
    // 字段：静态类型索引（用于 AnyView::CopyToAnyView 直接设置 type_index）
    static constexpr int32_t field_static_type_index = /* ... */;

    // 是否支持 MoveToAny（存储到 Any）
    static constexpr bool storage_enabled = true;
    // 是否支持 CopyToAnyView（构造 AnyView）
    static constexpr bool convert_enabled = true;

    // 拷贝到 AnyView（不转移所有权）
    static void CopyToAnyView(const T& src, TVMFFIAny* result);
    // 移动到 Any（转移所有权）
    static void MoveToAny(T src, TVMFFIAny* result);
    // 严格类型检查
    static bool CheckAnyStrict(const TVMFFIAny* src);
    // 检查后拷贝出来（const& 版本）
    static T CopyFromAnyViewAfterCheck(const TVMFFIAny* src);
    // 检查后移动出来（&& 版本）
    static T MoveFromAnyAfterCheck(TVMFFIAny* src);
    // 尝试兼容转换（包括隐式转换路径）
    static std::optional<T> TryCastFromAnyView(const TVMFFIAny* src);
    // 类型字符串（用于错误信息）
    static std::string TypeStr();
    // 类型 Schema（JSON，用于反射/存根生成）
    static std::string TypeSchema();
    // 类型不匹配时的错误描述
    static std::string GetMismatchTypeInfo(const TVMFFIAny* src);
};
```

### 5.2 内置类型的映射

| C++ 类型 | Any 类型索引 | 存储方式 |
|----------|-------------|----------|
| `std::nullptr_t` | `kTVMFFINone` | 空值 |
| `int` / `int64_t` | `kTVMFFIInt` | `v_int64` |
| `double` | `kTVMFFIFloat` | `v_float64` |
| `bool` | `kTVMFFIBool` | `v_int64`（0/1） |
| `String` | `kTVMFFIStr`/`kTVMFFISmallStr` | 堆对象 / 内联 |
| `Bytes` | `kTVMFFIBytes`/`kTVMFFISmallBytes` | 堆对象 / 内联 |
| `DLDataType` | `kTVMFFIDataType` | `v_dtype` POD |
| `ObjectRef` 子类 | 对应对象 RuntimeTypeIndex | `v_obj`（引用计数） |
| `Function` | `kTVMFFIFunction` | `v_obj`（FunctionObj） |
| `Tensor` | `kTVMFFITensor` | `v_obj`（TensorObj） |
| `DLTensor*` / `TensorView` | `kTVMFFIDLTensorPtr` | `v_ptr`（非持有） |
| `void*`（opaque） | `kTVMFFIOpaquePtr` | `v_ptr` |

### 5.3 为自定义值类型扩展 TypeTraits

不通过 Object 系统的值类型（POD 或小对象）可以自定义 TypeTraits 特化，但通常推荐将复杂类型注册为 Object 以获得自动反射、生命周期管理和跨语言支持。

---

## 6. Endian 字节序工具

`endian.h` 提供跨平台字节序转换工具。

**源文件**：`include/tvm/ffi/endian.h`

```cpp
#include <tvm/ffi/endian.h>
using namespace tvm::ffi;

// 判断本机字节序
constexpr bool is_little = Endian::kLittle;
constexpr bool is_big = Endian::kBig;

// 字节序转换
uint16_t a = Endian::Swap16(0x1234);          // 0x3412
uint32_t b = Endian::Swap32(0x12345678);      // 0x78563412
uint64_t c = Endian::Swap64(0x0123456789ABCDEFULL);

// 按本机到小端/大端
uint32_t le = Endian::ToLittle32(0x12345678);
uint32_t be = Endian::ToBig32(0x12345678);
uint32_t back = Endian::FromLittle32(le);
```

这些函数在小端机器上是 no-op，在大端机器上执行交换，便于二进制协议的序列化/反序列化。

---

## 本章小结

| 类型 | 头文件 | 语义 |
|------|--------|------|
| `DLDataType`（DType） | `dtype.h` | POD 描述符：code + bits + lanes |
| `String`/`Bytes` | `string.h` | 引用计数字符串/字节串，SSO 优化 |
| `Enum`/`EnumObj` | `enum.h` | 反射注册枚举单例，跨语言可见 |
| `Optional<T>` | `optional.h` | ObjectRef 零开销可空，值类型封装 std::optional |
| `TypeTraits<T>` | `type_traits.h` | C++ 类型到 Any 的双向映射 |
| `Endian` | `endian.h` | 字节序检测与交换 |

DType、String、Enum、Optional 共同构成了 TVM FFI 的类型描述层，是后续容器、反射和序列化章节的基础。

---

[上一章](02-cpp-core-api.md) | [下一章 →](04-containers.md)
