---
type: Concept
title: "视角164：test_container 覆盖"
description: "分析 Array、List、Map、Dict 等容器类型的 C++ 和 Python 测试覆盖，包括 COW 语义、迭代器、类型转换、共享变更、序列化等关键路径。"
tags:
  - testing
  - container
  - cow
  - coverage
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-153, F-154, F-155, F-156, F-157, F-158, F-159, F-160, F-161, F-162, F-163, F-164, F-165, F-166, F-167, F-168, F-169, F-170, F-171, F-172, F-173, F-174
  - code:
    - tests/cpp/test_array.cc
    - tests/cpp/test_map.cc
    - tests/cpp/test_dict.cc
    - tests/cpp/test_list.cc
    - tests/python/test_container.py
---

# 视角164：test_container 覆盖

## 概述

容器系统是 TVM FFI 的核心数据结构层，包含不可变的 `Array`/`Map` 和可变的 `List`/`Dict`。测试覆盖分为 C++ 单元测试（GoogleTest）和 Python 绑定测试（pytest）两层，本文档分析两层的覆盖深度和互补关系。

## C++ Array 测试（test_array.cc，17 个用例）

### 基础与 COW 测试

```cpp
TEST(Array, Basic) {
  Array<TInt> arr = {TInt(11), TInt(12)};
  TInt v1 = arr[0];
  EXPECT_EQ(v1->value, 11);
  EXPECT_EQ(v1.use_count(), 2);
}

TEST(Array, COWSet) {
  Array<TInt> arr = {TInt(11), TInt(12)};
  Array<TInt> arr2 = arr;
  EXPECT_EQ(arr.use_count(), 2);
  arr.Set(1, TInt(13));
  EXPECT_EQ(arr.use_count(), 1);
  EXPECT_EQ(arr[1]->value, 13);
  EXPECT_EQ(arr2[1]->value, 12);  // arr2 未受影响
}
```

关键验证：
- **引用计数**：`arr[0]` 返回的 `TInt` 引用计数为 2（Array 持有 + 局部变量持有）。
- **COW 触发**：`arr.Set()` 触发写时复制，`arr` 和 `arr2` 的 `use_count()` 均变为 1。
- **COW 不触发**：当对象唯一时（`unique() == true`），`Set` 直接原地修改，不分配新内存。

### 迭代器与算法

```cpp
TEST(Array, Iterator) {
  Array<int> arr = {1, 2, 3};
  int sum = 0;
  for (auto it = arr.begin(); it != arr.end(); ++it) {
    sum += *it;
  }
  EXPECT_EQ(sum, 6);
}

TEST(Array, Map) {
  Array<int> arr = {1, 2, 3};
  auto mapped = arr.Map([](int x) { return x * 2; });
  EXPECT_EQ(mapped[0], 2);
  EXPECT_EQ(mapped[1], 4);
  EXPECT_EQ(mapped[2], 6);
}
```

### 内存管理

```cpp
TEST(Array, ResizeReserveClear) {
  Array<int> arr;
  arr.Reserve(10);
  for (int i = 0; i < 5; ++i) arr.push_back(i);
  EXPECT_EQ(arr.size(), 5);
  EXPECT_EQ(arr.capacity(), 10);
  arr.Clear();
  EXPECT_EQ(arr.size(), 0);
}

TEST(Array, InsertErase) {
  Array<int> arr = {1, 2, 3};
  arr.Insert(1, 99);
  EXPECT_EQ(arr[1], 99);
  arr.Erase(1);
  EXPECT_EQ(arr.size(), 3);
}
```

## C++ Map 测试（test_map.cc，15 个用例）

### 基本操作

```cpp
TEST(Map, Basic) {
  Map<TInt, int> map0;
  TInt k0(0);
  map0.Set(k0, 1);
  EXPECT_EQ(map0.size(), 1);
  map0.Set(k0, 2);  // 更新现有键
  EXPECT_EQ(map0.size(), 1);
  auto it = map0.find(k0);
  EXPECT_TRUE(it != map0.end());
  EXPECT_EQ((*it).second, 2);
}
```

### 键类型多样性

```cpp
TEST(Map, PODKey) {
  Map<Any, Any> map0;
  map0.Set(1, 2);       // int 作为键
  map0.Set(1.1, 3);     // double 作为键（与 int 不同）
  EXPECT_EQ(map0.size(), 2);
}

TEST(Map, Str) {
  Map<String, int> map0;
  map0.Set(String("a"), 1);
  map0.Set(String("b"), 2);
  EXPECT_EQ(map0.at(String("a")), 1);
}
```

### 迭代器与顺序保持

```cpp
TEST(Map, MapInsertOrder) {
  Map<int, int> map0;
  map0.Set(3, 30);
  map0.Set(1, 10);
  map0.Set(2, 20);
  // 验证迭代顺序与插入顺序一致
  int i = 0;
  for (auto it = map0.begin(); it != map0.end(); ++it, ++i) {
    EXPECT_EQ(it->first, i + 1);
  }
}
```

## C++ Dict 测试（test_dict.cc，17 个用例）

### 基本 CRUD

```cpp
TEST(Dict, Basic) {
  Dict<String, int> d;
  d.Set("a", 1);
  d.Set("b", 2);
  EXPECT_EQ(d.size(), 2);
  EXPECT_EQ(d.at("a"), 1);
  EXPECT_EQ(d["b"], 2);
  EXPECT_EQ(d.count("a"), 1);
  EXPECT_EQ(d.count("c"), 0);
}
```

### 共享变更（Mutable 特性验证）

```cpp
TEST(Dict, SharedMutation) {
  Dict<String, int> d1;
  d1.Set("a", 1);
  Dict<String, int> d2 = d1;  // 共享同一底层对象
  d2.Set("a", 2);
  EXPECT_EQ(d1["a"], 2);  // d1 也看到变更
}
```

这与 `Array`/`Map` 的 COW 语义形成鲜明对比——`Dict` 是真正可变的，共享引用时修改可见。

### 与 Map 的互转

```cpp
TEST(Dict, CrossConvMapToDict) {
  Map<String, int> map = {{"a", 1}, {"b", 2}};
  Dict<String, int> dict = Any(map).cast<Dict<String, int>>();
  EXPECT_EQ(dict["a"], 1);
}

TEST(Dict, CrossConvDictToMap) {
  Dict<String, int> dict = {{"a", 1}, {"b", 2}};
  Map<String, int> map = Any(dict).cast<Map<String, int>>();
  EXPECT_EQ(map["a"], 1);
}
```

## Python 容器测试（test_container.py，50+ 函数）

### Array Python API

```python
def test_array():
    a = tvm_ffi.convert([1, 2, 3])
    assert isinstance(a, tvm_ffi.Array)
    assert len(a) == 3
    assert a[-1] == 3
    a_slice = a[-3:-1]
    assert isinstance(a_slice, list)  # 切片返回 Python list

def test_array_of_array_map():
    a = tvm_ffi.convert([[1, 2, 3], {"A": 5, "B": 6}])
    assert isinstance(a[0], tvm_ffi.Array)
    assert isinstance(a[1], tvm_ffi.Map)
```

### List Python API

```python
def test_list_basic():
    # ... append, pop, __len__, __getitem__

def test_list_mutation_methods():
    # ... push_back, pop

def test_list_slice_assignment_and_delete():
    # ... 切片赋值和删除操作

def test_list_pickle_roundtrip():
    # ... 序列化往返
```

### Dict Python API

```python
def test_dict_basic():
    d = tvm_ffi.Dict()
    d["a"] = 1
    d["b"] = 2
    assert len(d) == 2
    assert d["a"] == 1

def test_dict_shared_mutation():
    d1 = tvm_ffi.Dict()
    d1["a"] = 1
    d2 = d1
    d2["a"] = 2
    assert d1["a"] == 2  # 共享变更

def test_dict_keys_values_items():
    d = tvm_ffi.convert({"a": 1, "b": 2})
    assert tuple(d.keys()) == ("a", "b")
    assert tuple(d.values()) == (1, 2)
    assert tuple(d.items()) == (("a", 1), ("b", 2))
```

## 覆盖矩阵

| 容器 | C++ 用例数 | Python 用例数 | 核心验证点 |
|------|----------|-------------|----------|
| Array | 17 | 15+ | COW、迭代器、Map、类型转换 |
| List | - | 15+ | 可变性、共享变更、序列化 |
| Map | 15 | 10+ | 开放寻址哈希、顺序保持、类型转换 |
| Dict | 17 | 15+ | 可变性、与 Map 互转、迭代协议 |

## 设计分析

C++ 和 Python 测试的互补关系：

1. **C++ 侧重内存语义**：引用计数、COW 触发条件、原地修改优化等底层行为由 C++ 测试验证。
2. **Python 侧重 API 协议**：`__len__`、`__getitem__`、`__setitem__`、`__iter__` 等 Python 协议方法由 Python 测试验证。
3. **互转测试**：`CrossConv` 系列测试验证 Array ↔ List、Map ↔ Dict 的双向转换正确性。
4. **序列化测试**：Python 侧的 `test_serialization` 验证容器对象可被 pickle 序列化和反序列化。

## 扩展讨论

### 不可变 COW 与可变共享：两类存储的测试重心完全不同

`Array`/`Map` 走写时复制（COW）——测试必须精确断言"何时触发复制、何时原地修改"，如 `COWSet` 中 `use_count()` 从 2 跳到 1、共享的 `arr2` 不受影响；`List`/`Dict` 则是真正的可变共享——`SharedMutation` 断言 `d2` 的修改在 `d1` 中可见。这两类语义的测试取向是相反的：前者验证"副本隔离"，后者验证"变更传播"。测试把两种对立语义都覆盖到，就是为了明确区分"值语义"与"引用语义"，这也是容器系统设计的核心分界。

### 内存容量断言：把"避免频繁分配"从优化名词变成可验证契约

`Array/ResizeReserveClear` 断言构造 5 个元素后 `capacity() == 10`（来自先前的 `Reserve`），这是对"预分配避免反复扩容"这一性能意图的直接验证——若不预分配，`capacity` 会随 `push_back` 逐步增长而非保持 10；`Clear` 后 `size()==0` 则验证清空语义。这类容量断言把"关于性能的假设"显式键入测试，防止后续实现退化为一调用就重新分配的实现，对高频构造容器的 FFI 热路径意义重大。

### C++ 与 Python 双层覆盖的本质：同一契约的两个观察面

C++ 测试面向原生调用者，验证引用计数、COW、迭代器这类**不依赖解释器**的底层行为；Python 测试面向脚本调用者，验证 `__getitem__`、切片、pickle 这类**由绑定层转写**的协议方法。二者并非重复，而是把"底层保证"与"绑定层转写是否正确"分开问责——即使 C++ 容器正确，Python 绑定在转换 `Any`、映射切片语义、包装 iterable 时仍可能引入独立缺陷。双层每个断言只对应当层可决定的契约，共同构成从内存语义到脚本 API 的完整证据链。

## 相关概念

- [051 Array 不可变数组](/04-containers/concepts/051-array-container.md)
- [052 List 可变列表](/04-containers/concepts/052-list-container.md)
- [054 Map 不可变映射](/04-containers/concepts/054-map-container.md)
- [055 Dict 可变字典](/04-containers/concepts/055-dict-container.md)
- [061 原地数组存储](/04-containers/concepts/061-inplace-array-storage.md)
