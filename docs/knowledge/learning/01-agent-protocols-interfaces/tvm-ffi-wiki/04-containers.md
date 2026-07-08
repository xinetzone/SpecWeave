---
title: "04 - 容器类型：Array、Map、Dict、List、Tuple、Shape、Variant"
date: 2026-07-05
source: "spec:create-tvm-ffi-wiki-tutorial"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/01-agent-protocols-interfaces/tvm-ffi-wiki/04-containers.toml"
tags: [tvm-ffi, ffi, cpp, core-api]
---
# 容器类型：Array、Map、Dict、List、Tuple、Shape、Variant

TVM FFI 提供了一组经过精心设计的容器类型，所有容器都基于 Object 系统实现（引用计数管理），可以自由放入 `Any`、在 C++/Python/Rust 之间传递，并与反射/序列化系统无缝配合。

容器按可变性和同构性分为两类：
- **不可变容器（写时复制 COW）**：`Array<T>`、`Map<K,V>`
- **可变容器**：`List<T>`、`Dict`
- **专用容器**：`Tuple`（异构定长）、`Shape`（张量形状）、`Variant<T...>`（标签联合）

**头文件**位于 `include/tvm/ffi/container/`。

---

## 1. Array\<T\>：不可变数组（COW）

`Array<T>` 是 TVM FFI 最常用的顺序容器。底层 `ArrayObj` 使用连续内存存储 `Any`，通过**写时复制（Copy-on-Write）**实现逻辑上的不可变语义：当数组引用计数大于 1 时，所有"修改"操作都会先拷贝一份再修改。

**源文件**：`include/tvm/ffi/container/array.h`、`seq_base.h`

### 1.1 基本用法

```cpp
#include <tvm/ffi/container/array.h>
using namespace tvm::ffi;

// 默认构造空数组
Array<int> a;

// 初始化列表
Array<int> b{1, 2, 3, 4};

// push_back（COW 语义：若引用计数 > 1 则先拷贝）
a.push_back(10);
a.push_back(20);

// 下标访问（const 引用）
int x = a[0];             // 10
int y = a.at(1);          // 20（带边界检查）

// 大小和容量
int64_t n = a.size();
bool empty = a.empty();

// 迭代
for (int v : b) {
    // ...
}
for (auto it = b.begin(); it != b.end(); ++it) {
    // *it 返回 const T&
}
```

### 1.2 写时复制行为

```cpp
Array<int> a{1, 2, 3};
Array<int> b = a;          // b 和 a 共享底层 ArrayObj（引用计数 2）
a.push_back(4);            // 触发 COW：a 现在持有一个新拷贝，b 保持不变
// b 仍然是 [1,2,3]，a 是 [1,2,3,4]
```

由于 COW，`operator[]` 只返回 const 引用；如需修改元素请使用 `Set(idx, value)`（同样 COW）：

```cpp
Array<int> a{1, 2, 3};
a.Set(1, 99);              // a 变为 [1, 99, 3]
```

### 1.3 与 STL 互操作

```cpp
// 从 STL 容器构造
std::vector<int> vec{1, 2, 3};
Array<int> a(vec.begin(), vec.end());

// 转换回 std::vector
std::vector<int> out(a.begin(), a.end());
```

### 1.4 异构数组（Array\<Any\>）

`Array<Any>` 是类型擦除数组，可以存放任意 FFI 类型，类似 Python list：

```cpp
Array<Any> mixed;
mixed.push_back(42);
mixed.push_back(String("hello"));
mixed.push_back(Array<int>{1, 2, 3});
```

### 1.5 seq_base.h 内部机制

`SeqBaseObj` 是 `ArrayObj`/`ListObj` 等顺序容器的共同基类，采用**对象头+内联数组**的内存布局：对象后面紧跟连续的 `Any` 槽位，避免额外指针解引用。元素从 `Begin()` 开始，通过 inplace new 构造，析构时调用 `Any` 析构。

---

## 2. List\<T\>：可变列表

`List<T>` 是**可变**顺序容器，底层实现与 Array 类似，但不做 COW 检查，所有修改操作都在原对象上进行。适用于构建期需要频繁增删元素的场景。

**源文件**：`include/tvm/ffi/container/list.h`

### 2.1 基本用法

```cpp
#include <tvm/ffi/container/list.h>
using namespace tvm::ffi;

List<int> lst;
lst.push_back(1);
lst.push_back(2);
lst.push_back(3);

int x = lst[0];           // 1
lst.Set(1, 42);           // 原地修改
lst.erase(0);             // 删除第一个元素
int64_t n = lst.size();

// 迭代
for (int v : lst) { /* ... */ }
```

### 2.2 何时用 Array vs List

| 维度 | Array\<T\> | List\<T\> |
|------|-----------|-----------|
| 可变性 | 逻辑不可变（COW） | 可变 |
| 跨共享安全性 | 安全：拷贝引用不会互相影响 | 不安全：所有引用看到相同修改 |
| 性能（读多写少） | 更好（COW 减少拷贝） | 略差（每次修改都影响所有持有者） |
| 推荐场景 | IR/AST 节点、公共数据、Python 暴露 | 构建期暂存、局部使用 |

经验法则：**公共 API 优先用 Array**，局部构建过程用 List。

---

## 3. Map\<K,V\>：不可变有序映射（COW）

`Map<K,V>` 是不可变有序映射，键值类型都必须是 FFI 可存储类型。底层使用开放寻址哈希表，同样采用 COW 语义。

**源文件**：`include/tvm/ffi/container/map.h`、`map_base.h`

### 3.1 基本用法

```cpp
#include <tvm/ffi/container/map.h>
#include <tvm/ffi/string.h>
using namespace tvm::ffi;

Map<String, int> m;

// 插入（COW：若引用计数 > 1 则先拷贝）
m.Set(String("a"), 1);
m.Set(String("b"), 2);

// 查找
std::optional<int> v = m.Get(String("a"));   // 1
int v2 = m[String("b")];                      // 2（存在时返回值，不存在抛异常）
bool has = m.Count(String("c"));             // false

// 删除
m.erase(String("a"));

// 大小
int64_t n = m.size();

// 迭代（顺序不保证）
for (const auto& kv : m) {
    String key = kv.first;
    int value = kv.second;
}
```

### 3.2 operator[] 注意事项

`Map::operator[]` 是**只读**访问（与 STL map 不同，不会在键不存在时插入默认值）。键不存在时会抛异常。要安全地获取可选值请用 `Get()`。

### 3.3 map_base.h 内部

`MapBaseObj` 使用开放寻址线性探测哈希表，内联存储键值对。Set/erase 操作先检查 `unique()`（引用计数 == 1），若不唯一则触发 COW 复制整个哈希表，然后在新副本上修改。

---

## 4. Dict：可变异构字典

`Dict` 是类型擦除的**可变**字典，键和值都是 `Any`，相当于 Python `dict`。不使用 COW，所有修改直接作用于底层对象。

**源文件**：`include/tvm/ffi/container/dict.h`

### 4.1 基本用法

```cpp
#include <tvm/ffi/container/dict.h>
using namespace tvm::ffi;

Dict d;
d.Set(String("name"), String("TVM"));
d.Set(String("version"), 1);
d.Set(42, String("int key works too"));   // 键可以是任意 FFI 类型

// 访问
Any name = d[String("name")];            // Any(String("TVM"))
std::optional<Any> v = d.Get(String("x")); // nullopt
bool has = d.Contains(String("name"));   // true

int64_t n = d.size();
d.erase(String("version"));

// 迭代
for (const auto& kv : d) {
    Any key = kv.first;
    Any val = kv.second;
}
```

### 4.2 Map vs Dict 选择

- 需要**类型安全**且键值类型固定 → `Map<K,V>`
- 需要**异构键值**（模拟 Python dict）或在脚本边界使用 → `Dict`
- 需要**跨模块共享**且不想担心意外修改 → `Map<K,V>`（COW）
- 本地临时聚合数据 → `Dict`

---

## 5. Tuple：异构定长元组

`Tuple<Ts...>` 是类型安全的异构定长元组，类似 `std::tuple`，但作为 Object 子类可放入 `Any` 和 FFI 系统。

**源文件**：`include/tvm/ffi/container/tuple.h`

### 5.1 基本用法

```cpp
#include <tvm/ffi/container/tuple.h>
using namespace tvm::ffi;

// 构造
Tuple<int, String, double> t(42, String("hi"), 3.14);

// 访问（通过 get<N>）
int a = t.get<0>();          // 42
String b = t.get<1>();       // "hi"
double c = t.get<2>();       // 3.14

// 通过 Any 传递
Any any_t = t;
auto back = any_t.cast<Tuple<int, String, double>>();
```

Tuple 在反射系统中有完整的 schema（每个元素的类型信息），Python 端自动映射为 Python tuple。

---

## 6. Shape：张量形状容器

`Shape` 是 `Array<int64_t>` 的语义别名，底层使用 `std::vector<int64_t>` 存储，代表张量维度，是 Tensor 的核心属性。另外提供 `ShapeView` 作为非持有视图（类似 `AnyView` 与 `Any` 的关系）。

**源文件**：`include/tvm/ffi/container/shape.h`

### 6.1 基本用法

```cpp
#include <tvm/ffi/container/shape.h>
using namespace tvm::ffi;

// 构造
Shape s({2, 3, 4});
Shape s2 = {1, 28, 28};

// 访问
int64_t d0 = s[0];             // 2
int64_t ndim = s.size();       // 3
int64_t total = s.Product();   // 2*3*4 = 24（元素总数）

// ShapeView：非持有视图（从指针+长度构造）
int64_t dims[] = {1, 3, 224, 224};
ShapeView view(dims, 4);
int64_t n = view[2];           // 224
int64_t p = view.Product();

// 从 Shape 隐式转换为 ShapeView
ShapeView v2 = s;

// STL 兼容迭代
for (int64_t d : s) { /* ... */ }
```

### 6.2 在 Tensor API 中的使用

`Tensor::shape()` 返回 `ShapeView`（不持有底层数组），`Tensor::FromNDAlloc` 接受 `ShapeView`：

```cpp
Tensor t = Tensor::FromNDAlloc(alloc, ShapeView({2, 3}), dtype, device);
ShapeView sh = t.shape();
```

---

## 7. Variant\<T...\>：标签联合

`Variant<T1, T2, ...>` 是类型安全的标签联合（tagged union），同一时刻持有其中一种类型的值。类似 `std::variant`，但作为 ObjectRef 可以放入 FFI 系统。

**源文件**：`include/tvm/ffi/container/variant.h`

### 7.1 基本用法

```cpp
#include <tvm/ffi/container/variant.h>
#include <tvm/ffi/string.h>
using namespace tvm::ffi;

// 定义可持有 int 或 String 的类型
using IntOrStr = Variant<int, String>;

IntOrStr a = 42;
IntOrStr b = String("hello");

// 类型检查
if (a.is<int>()) {
    int v = a.get<int>();          // 42
}
if (auto s = b.try_get<String>()) {
    // *s 是 String("hello")
}

// 访问失败会抛异常
int bad = b.get<int>();            // 抛 TypeError

// 通过 Any 传递
Any any = a;
IntOrStr back = any.cast<IntOrStr>();
```

### 7.2 访问者模式

`Variant` 支持通过函数对象 visit：

```cpp
struct Visitor {
    void operator()(int i) const { /* 处理 int */ }
    void operator()(const String& s) const { /* 处理字符串 */ }
};

IntOrStr v = 42;
v.visit(Visitor{});
```

Variant 在反射系统中自动生成 schema（描述可选类型列表），Python 端根据实际持有类型返回对应 Python 对象。

---

## 8. 容器细节：seq_base.h / map_base.h

### 8.1 Inplace Array 布局

`SeqBaseObj` 和 `ArrayObj` 使用 `make_inplace_array_object` 分配内存：在对象头后直接存储 N 个 `Any` 槽位，避免额外间接指针：

```
[ArrayObj header (TVMFFIObject + size/capacity/data ptr)]
[Any[0]] [Any[1]] [Any[2]] ... [Any[cap-1]]
```

这种布局使得访问元素只需一次指针偏移，缓存友好。

### 8.2 COW 触发条件

所有"修改"方法（push_back/pop_back/Set/erase）开头都有类似逻辑：

```cpp
if (!unique()) {
    *this = CopyOnWrite();   // 拷贝一份
}
// 在唯一持有的副本上修改...
```

### 8.3 容器与 Any 的关系

所有容器都是 ObjectRef 子类，`TypeTraits<Array<T>>` 等会自动特化，使得容器可以直接放入 `Any`、作为 PackedFunc 参数/返回值：

```cpp
TVM_FFI_REGISTER_GLOBAL_FUNC("demo.sum_array",
    [](const Array<int>& arr) -> int {
        int s = 0;
        for (int v : arr) s += v;
        return s;
    });

// 调用
Function f = get_global_func("demo.sum_array").value();
int sum = f(Array<int>{1, 2, 3, 4}).cast<int>();  // 10
```

---

## 9. 容器 API 速查表

| 容器 | 可变性 | 元素类型 | 主要源文件 |
|------|--------|---------|-----------|
| `Array<T>` | 不可变（COW） | 同构 T | `container/array.h` |
| `List<T>` | 可变 | 同构 T | `container/list.h` |
| `Map<K,V>` | 不可变（COW） | 固定 K, V | `container/map.h` |
| `Dict` | 可变 | 异构 Any/Any | `container/dict.h` |
| `Tuple<Ts...>` | 不可变 | 异构、定长 | `container/tuple.h` |
| `Shape` / `ShapeView` | Shape 不可变、View 非持有 | `int64_t` | `container/shape.h` |
| `Variant<Ts...>` | 赋值可变 | 异构、择一 | `container/variant.h` |

### 通用方法（大部分容器支持）

| 方法 | 说明 |
|------|------|
| `size()` | 元素个数 |
| `empty()` | 是否为空 |
| `begin()` / `end()` | STL 风格迭代器 |
| 容器作为 ObjectRef | `defined()`、`use_count()`、`same_as()`、`as<T>()` |

---

## 10. 典型用法示例

### 10.1 构建嵌套结构

```cpp
Map<String, Any> config;
config.Set(String("layers"), Array<int>{64, 128, 256});
config.Set(String("activation"), String("relu"));
config.Set(String("dropout"), 0.5);
config.Set(String("input_shape"), Array<int64_t>{1, 3, 224, 224});

// 通过 Any 传给 Python 函数
Any result = some_python_func(config);
```

### 10.2 使用 Dict 模拟 kwargs

```cpp
Dict kwargs;
kwargs.Set(String("dtype"), String("float32"));
kwargs.Set(String("device"), String("cuda"));

Function create_tensor = get_global_func("demo.create").value();
Tensor t = create_tensor(ShapeView({2, 3}), kwargs).cast<Tensor>();
```

### 10.3 Variant 作为函数返回类型

```cpp
using Result = Variant<Tensor, String>;

Result Run(bool ok) {
    if (ok) return some_tensor;
    else return String("error message");
}
```

---

容器是 TVM FFI 中最常用的 API，下一章介绍的反射机制能让容器和自定义类型自动获得 Python 绑定能力。

---

[上一章](03-type-system.md) | [下一章 →](05-reflection.md)
