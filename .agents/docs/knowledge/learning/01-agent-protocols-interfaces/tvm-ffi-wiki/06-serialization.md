---
title: "06 - 序列化：JSON、Base64、结构相等与哈希"
date: 2026-07-05
source: "spec:create-tvm-ffi-wiki-tutorial"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/01-agent-protocols-interfaces/tvm-ffi-wiki/06-serialization.toml"
tags: [tvm-ffi, ffi, cpp, core-api]
---
# 序列化：JSON、Base64、结构相等与哈希

TVM FFI 在核心 Any/Object/容器系统之上提供了一套序列化与结构比较工具，让任意 FFI 值都能：

- 序列化为 JSON 字符串（`extra/json.h`）
- 二进制数据 Base64 编码/解码（`extra/base64.h`）
- 做深度结构相等比较（`extra/structural_equal.h`）
- 计算结构哈希（`extra/structural_hash.h`），用于做 Map/Set 的 key
- 通过访问者模式（Visitor）遍历对象图（`extra/structural_visit.h`）
- 与 Python dataclass 互操作（`extra/dataclass.h`）
- 出错时通过访问路径生成更友好的错误信息（`extra/visit_error_context.h`）

这些工具都依赖反射系统：能序列化/比较的类型必须已经通过 `TVM_FFI_REGISTER_OBJECT` 注册字段和 schema。

---

## 1. JSON 支持（extra/json.h）

TVM FFI 直接复用 `Any` 作为 JSON 值类型，`Map<Any,Any>` 作为 JSON 对象，`Array<Any>` 作为 JSON 数组，无需引入额外的 DOM 类型。

### 1.1 核心 API

```cpp
#include <tvm/ffi/extra/json.h>
using namespace tvm::ffi;

// 解析 JSON 字符串 → Any
json::Value json::Parse(const String& json_str, String* error_msg = nullptr);

// Any → JSON 字符串
String json::Stringify(const json::Value& value, Optional<int> indent = std::nullopt);
```

类型别名：

```cpp
using json::Value  = Any;             // JSON 值
using json::Object = Map<Any, Any>;   // JSON 对象（键实际为 String）
using json::Array  = Array<Any>;      // JSON 数组
```

除了标准 JSON 语法，解析器还支持：
- JavaScript 风格的 `Infinity` / `NaN`
- `int64` 整数值（不溢出为 double）

### 1.2 序列化示例

```cpp
#include <tvm/ffi/extra/json.h>
#include <tvm/ffi/container/map.h>
#include <tvm/ffi/container/array.h>
#include <tvm/ffi/string.h>
using namespace tvm::ffi;

// 构建一个 JSON 对象
json::Object obj;
obj.Set(String("name"), String("TVM"));
obj.Set(String("version"), 1);
obj.Set(String("tags"), json::Array{String("compiler"), String("ffi")});
obj.Set(String("active"), true);
obj.Set(String("score"), 3.14);
obj.Set(String("nothing"), nullptr);  // None

// 紧凑输出
String s = json::Stringify(obj);
// {"name":"TVM","version":1,"tags":["compiler","ffi"],"active":true,"score":3.14,"nothing":null}

// 美化输出（2 空格缩进）
String pretty = json::Stringify(obj, 2);
```

### 1.3 反序列化示例

```cpp
String text = R"({"x":1,"y":[2,3,4],"name":"demo"})";
String err;
json::Value v = json::Parse(text, &err);
if (!err.empty()) {
    // 解析失败
}

// 通过 as<T> 访问
std::optional<Map<Any,Any>> obj = v.as<Map<Any,Any>>();
Any x = (*obj)[String("x")];            // 1
Array<Any> y = (*obj)[String("y")].cast<Array<Any>>();
String name = (*obj)[String("name")].cast<String>();
```

### 1.4 自定义 Object 的 JSON 序列化

任何通过反射注册的 Object（即已 `def_field` 列出字段）都会被自动处理。序列化器按字段名递归写入 JSON 对象，反序列化时按字段名回填：

```cpp
// MyVec（见上一章的反射示例）
MyVec v = make_vec(1.0, 2.0, 3.0);
String json = json::Stringify(v);
// {"x":1.0,"y":2.0,"z":3.0}

MyVec back = json::Parse(json).cast<MyVec>();
```

未在反射中注册的字段不会被序列化，符合"schema 即合约"的设计。

---

## 2. Base64 编码/解码（extra/base64.h）

`extra/base64.h` 提供标准 Base64 编解码工具，用于在 JSON 这种纯文本通道里嵌入二进制数据（如张量 raw bytes、模型权重片段）。

### 2.1 核心 API

```cpp
#include <tvm/ffi/extra/base64.h>
namespace tvm::ffi {

// 编码：原始字节 → Base64 字符串
String Base64Encode(std::string_view data);

// 解码：Base64 字符串 → 原始字节
std::string Base64Decode(const String& input);

// 流式编码/解码支持（Encrypt/Decrypt 风格）
struct Base64Encoder { /* ... */ };
struct Base64Decoder { /* ... */ };

}  // namespace tvm::ffi
```

### 2.2 使用示例

```cpp
#include <tvm/ffi/extra/base64.h>
#include <tvm/ffi/string.h>
using namespace tvm::ffi;

// 编码
std::string_view raw = "binary data \x00\x01\x02";
String encoded = Base64Encode(raw);
// "YmluYXJ5IGRhdGEgAAEC"

// 解码
std::string decoded = Base64Decode(encoded);
// "binary data \0\1\2"

// 常见用法：把张量数据打包进 JSON
float data[] = {1.0f, 2.0f, 3.0f};
std::string_view bytes(reinterpret_cast<const char*>(data), sizeof(data));
String b64 = Base64Encode(bytes);

json::Object payload;
payload.Set(String("dtype"), String("float32"));
payload.Set(String("shape"), Array<int64_t>{3});
payload.Set(String("data"), b64);
String msg = json::Stringify(payload);
```

---

## 3. 结构相等（extra/structural_equal.h）

普通的 `==` 对 ObjectRef 只比较指针（同一对象才相等）。`structural_equal` 提供**深度值比较**：递归比较字段、容器元素、基本类型值，等价于 Python 的 `==` 语义。

### 3.1 核心 API

```cpp
#include <tvm/ffi/extra/structural_equal.h>
namespace tvm::ffi {

bool StructuralEqual(const Any& a, const Any& b, bool assert_mode = false);

// Object 子类版本
template <typename T>
bool StructuralEqual(const T& a, const T& b, bool assert_mode = false);

// EqualHandler 可扩展：为自定义类型注册特殊比较逻辑
class StructuralEqualHandler;

}  // namespace tvm::ffi
```

- `assert_mode=true` 时：不相等则抛异常并携带访问路径（借助 `VisitErrorContext`），便于调试。
- 基本类型（int/float/bool/String/None）按值比较。
- 容器（Array/Map/Dict/List/Tuple）递归比较元素。
- 反射注册的 Object：按基类到派生类顺序逐个字段比较。
- 未注册反射的 Object：退化为指针比较。

### 3.2 使用示例

```cpp
#include <tvm/ffi/extra/structural_equal.h>
#include <tvm/ffi/container/array.h>
using namespace tvm::ffi;

Array<int> a{1, 2, 3};
Array<int> b{1, 2, 3};
Array<int> c{1, 2, 4};

bool eq1 = (a == b);                 // false（不同对象，指针不同）
bool eq2 = StructuralEqual(a, b);   // true  （深度相等）
bool eq3 = StructuralEqual(a, c);   // false

// assert_mode 下不相等时抛异常，错误消息带路径
try {
    StructuralEqual(a, c, /*assert_mode=*/true);
} catch (const Error& e) {
    // 错误消息类似："StructuralEqual check failed at [2]: 3 vs 4"
}
```

---

## 4. 结构哈希（extra/structural_hash.h）

`structural_hash` 与 `structural_equal` 配套，计算稳定的深度哈希值，可用于把容器/Object 放入 Map/Dict 作为 key。

### 4.1 核心 API

```cpp
#include <tvm/ffi/extra/structural_hash.h>
namespace tvm::ffi {

uint64_t StructuralHash(const Any& a);
uint64_t StructuralHash(const ObjectRef& a);

// 哈希处理器（可扩展）
class StructuralHashHandler;

// 同时比较+哈希的 key 类型（用于 STL 无序容器）
struct StructuralHashKey;

}  // namespace tvm::ffi
```

满足不变式：`StructuralEqual(a,b) ⇒ StructuralHash(a) == StructuralHash(b)`。

### 4.2 使用示例

```cpp
#include <tvm/ffi/extra/structural_hash.h>
#include <tvm/ffi/container/map.h>
using namespace tvm::ffi;

// 把 Array<int> 作为 key 做缓存
std::unordered_map<Array<int>, String, StructuralHash, StructuralEqual> cache;
cache[Array<int>{1, 2, 3}] = String("cached-1");

// FFI 容器内置
Map<Array<int>, String> ffi_cache;
ffi_cache.Set(Array<int>{1, 2, 3}, String("cached-1"));
```

---

## 5. 结构访问（extra/structural_visit.h）

`structural_visit.h` 定义了 Visitor 模式，是 JSON 序列化、结构相等、结构哈希的共同基础。用户可以实现自己的 Visitor 完成任意对象图遍历任务。

### 5.1 核心抽象

```cpp
#include <tvm/ffi/extra/structural_visit.h>
namespace tvm::ffi {

// 访问者基类：为不同 Any 类型提供钩子
class Visitor {
public:
    virtual void VisitNull();
    virtual void VisitInt(int64_t v);
    virtual void VisitUInt(uint64_t v);
    virtual void VisitFloat(double v);
    virtual void VisitBool(bool v);
    virtual void VisitString(const String& v);
    virtual void VisitObject(const ObjectRef& obj);
    virtual void VisitArray(Array<Any> arr);
    virtual void VisitMap(Map<Any,Any> map);
    // ...其他 Any 类型钩子
};

// 访问者调度入口
void StructuralVisit(const Any& v, Visitor* visitor);
void StructuralVisit(const ObjectRef& obj, Visitor* visitor);

}  // namespace tvm::ffi
```

### 5.2 自定义 Visitor 示例：统计对象数量

```cpp
class CountVisitor : public Visitor {
public:
    int64_t objects = 0;
    int64_t arrays = 0;

    void VisitObject(const ObjectRef& obj) override {
        objects++;
        // 继续遍历 Object 字段
        Visitor::VisitObject(obj);
    }
    void VisitArray(Array<Any> arr) override {
        arrays++;
        Visitor::VisitArray(arr);
    }
};

Any v = json::Parse(some_json);
CountVisitor cv;
StructuralVisit(v, &cv);
// cv.objects, cv.arrays 即为统计结果
```

所有内建工具（JSON/Equal/Hash）都通过这套 Visitor 机制实现，新容器或自定义类型若要支持这些能力，需要在 Visitor 上注册扩展点（通过 `SetVisitationFunction`）。

---

## 6. 访问错误上下文（extra/visit_error_context.h）

深度遍历中出错时，单纯一个错误消息无法告诉用户"错误发生在哪"。`VisitErrorContext` 以 RAII 方式在栈上记录当前访问的字段/下标，异常抛出时把整条路径拼接到错误消息。

### 6.1 用法

```cpp
#include <tvm/ffi/extra/visit_error_context.h>
using namespace tvm::ffi;

// 在自定义 Visitor 中：
void VisitArray(Array<Any> arr) override {
    for (int i = 0; i < arr.size(); ++i) {
        // 进入数组下标
        VisitErrorContext ctx(String("[" + std::to_string(i) + "]"));
        // 访问 arr[i] 时若抛异常，消息会带上 "[i]" 路径
        StructuralVisit(arr[i], this);
    }
}

void VisitObject(const ObjectRef& obj) override {
    // 按反射字段遍历
    for (const auto& f : GetFields(obj)) {
        VisitErrorContext ctx("." + f.name);  // 如 ".x"
        // ...递归访问字段值
    }
}
```

抛出的异常消息形如：

```
ValueError at path .layers[0].weight: expected Tensor, got None
```

JSON 解析器、`StructuralEqual(assert_mode=true)`、dataclass 验证等所有深度遍历工具都自动带上路径信息。

---

## 7. Dataclass 支持（extra/dataclass.h）

`extra/dataclass.h` 让 C++ 反射注册的 Object 类与 Python `@dataclass` 无缝互操作，典型用法：
- Python 侧用 dataclass 定义 schema；
- C++ 侧通过反射读取/构造对应 Object；
- 跨语言调用时自动做构造/字段校验/默认值填充。

### 7.1 主要能力

- **字段默认值**：结合 `DefaultValue` metadata，Python 端构造缺省时自动填充。
- **类型校验**：调用前按字段类型 schema 校验参数，不匹配抛带路径的 ValueError。
- **转换为 dict**：把 Object 递归转成 `Dict`/JSON 兼容结构，便于与纯 Python 代码交互。
- **从 dict 构造**：从 Python dict/kwargs 构造 C++ Object，等价于 dataclass 构造器。

### 7.2 C++ 侧配合

不需要额外 API，使用反射注册即可：

```cpp
TVM_FFI_REGISTER_OBJECT(MyVecObj)
    .def_field<&MyVecObj::x>("x", DefaultValue(0.0))
    .def_field<&MyVecObj::y>("y", DefaultValue(0.0))
    .def_field<&MyVecObj::z>("z", DefaultValue(0.0))
    .def_creator([](double x, double y, double z) -> MyVec {
        MyVec v = make_object<MyVecObj>();
        v->x = x; v->y = y; v->z = z;
        return v;
    });
```

### 7.3 Python 端

```python
from dataclasses import dataclass
import tvm_ffi

@tvm_ffi.dataclass
class MyVec:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

v = MyVec(x=1, y=2)              # z 默认 0.0
print(v.x, v.y, v.z)             # 1.0 2.0 0.0
d = v.to_dict()                  # {'x':1.0,'y':2.0,'z':0.0}
v2 = MyVec.from_dict({'x':3})    # x=3, y/z 取默认值
```

dataclass 装饰器在内部连接反射 schema，完成字段校验、默认值填充和跨语言对象映射。

---

## 8. 端到端示例：序列化→传输→反序列化

```cpp
#include <tvm/ffi/extra/json.h>
#include <tvm/ffi/extra/base64.h>
#include <tvm/ffi/extra/structural_equal.h>
#include <tvm/ffi/extra/structural_hash.h>
#include <tvm/ffi/container/array.h>
#include <tvm/ffi/container/map.h>
#include <tvm/ffi/string.h>
using namespace tvm::ffi;

// 1. 构造数据
Map<String, Any> msg;
msg.Set(String("op"), String("add"));
msg.Set(String("args"), Array<Any>{1, 2, 3, 4});
msg.Set(String("meta"), Map<String, Any>{
    {String("user"), String("alice")},
    {String("ts"), 1700000000},
});

// 2. 序列化为 JSON
String payload = json::Stringify(msg, 2);

// 3. 反序列化
Any parsed = json::Parse(payload);

// 4. 结构相等验证
bool ok = StructuralEqual(msg, parsed, /*assert_mode=*/true);  // true

// 5. 计算哈希，用于缓存键
uint64_t h1 = StructuralHash(msg);
uint64_t h2 = StructuralHash(parsed);
assert(h1 == h2);

// 6. 附带二进制数据：float 权重通过 base64 嵌入
float weights[] = {0.1f, 0.2f, 0.3f};
std::string_view wb(reinterpret_cast<const char*>(weights), sizeof(weights));
msg.Set(String("weights"), Base64Encode(wb));
String with_bin = json::Stringify(msg);

// 接收方解码
Any recv = json::Parse(with_bin);
String wb64 = recv.as<Map<Any,Any>>()->at(String("weights")).cast<String>();
std::string wbytes = Base64Decode(wb64);
assert(wbytes.size() == sizeof(weights));
```

---

## 9. 序列化相关 API 速查表

| 功能 | 头文件 | 关键 API |
|------|--------|---------|
| JSON 解析 | `extra/json.h` | `json::Parse(str, &err)` |
| JSON 序列化 | `extra/json.h` | `json::Stringify(val, indent)` |
| Base64 编码 | `extra/base64.h` | `Base64Encode(bytes)` |
| Base64 解码 | `extra/base64.h` | `Base64Decode(str)` |
| 结构相等 | `extra/structural_equal.h` | `StructuralEqual(a, b, assert_mode)` |
| 结构哈希 | `extra/structural_hash.h` | `StructuralHash(v)` |
| 结构访问 | `extra/structural_visit.h` | `StructuralVisit(v, visitor)`、`Visitor` 基类 |
| 访问错误路径 | `extra/visit_error_context.h` | `VisitErrorContext` RAII |
| Python dataclass | `extra/dataclass.h` | 配合 `DefaultValue`、creator 使用 |
| 扩展 key 行为 | `extra/structural_key.h` | `StructuralHashKey` |

---

## 10. 实现要点回顾

- **JSON 零额外 DOM**：直接复用 Any/Array/Map，避免双重类型转换开销。
- **结构语义与身份语义分离**：`==` 保持身份（指针）语义，`StructuralEqual` 提供值语义，避免"不同对象但内容相等"场景下的歧义。
- **反射驱动**：所有深度操作（序列化/相等/哈希/visit）通过反射字段表遍历，未注册类型自然退化到安全默认（JSON 报错、Equal 退化为指针比较）。
- **可扩展 Visitor**：新类型可以通过 handler 机制注入自定义访问逻辑，不修改核心代码即可扩展序列化行为。
- **错误可定位**：`VisitErrorContext` 让所有递归遍历都能返回带路径的错误，大幅提升跨语言调试体验。

到此 C++ 端的核心 API、类型系统、容器、反射、序列化五大主题都已覆盖。下一章可以进一步阅读 C ABI 层（`c_api.h`）、Python 绑定（`python/tvm_ffi/`）、线程/异步模型和错误恢复等高级主题。

---

[上一章](05-reflection.md) | [下一章 →](07-python-bindings.md)
