---
type: Concept
title: "视角167：test_shape_tuple_variant 覆盖"
description: "分析 Shape、Tuple、Variant 三种容器/组合类型的测试覆盖，包括形状构造、元组类型安全、变体类型擦除、COW 语义等。"
tags:
  - testing
  - shape
  - tuple
  - variant
  - coverage
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-186, F-187, F-188, F-192, F-193, F-194, F-195
  - code:
    - tests/cpp/test_shape.cc
    - tests/cpp/test_tuple.cc
    - tests/cpp/test_variant.cc
    - tests/cpp/test_tensor.cc
---

# 视角167：test_shape_tuple_variant 覆盖

## 概述

Shape、Tuple、Variant 是 TVM FFI 中用于组合和结构化数据的三种类型。Shape 表示张量的维度信息，Tuple 提供编译期类型安全的异构集合，Variant 提供运行期类型选择的值。测试覆盖验证了它们的核心行为和互操作性。

## Shape 测试（test_shape.cc，3 个用例）

### 基本构造与访问

```cpp
TEST(Shape, Basic) {
  Shape shape = Shape({1, 2, 3});
  EXPECT_EQ(shape.size(), 3);
  EXPECT_EQ(shape[0], 1);
  EXPECT_EQ(shape[1], 2);
  EXPECT_EQ(shape[2], 3);

  Shape shape2 = Shape(Array<int64_t>({4, 5, 6, 7}));
  EXPECT_EQ(shape2.size(), 4);

  std::vector<int64_t> vec = {8, 9, 10};
  Shape shape3 = Shape(std::move(vec));
  EXPECT_EQ(shape3.size(), 3);
  EXPECT_EQ(shape3.Product(), 8 * 9 * 10);

  Shape shape4 = Shape();
  EXPECT_EQ(shape4.size(), 0);
  EXPECT_EQ(shape4.Product(), 1);  // 空形状乘积为 1
}
```

关键验证：
- **多源构造**：支持 initializer_list、Array<int64_t>、std::vector<int64_t> 三种构造方式。
- **移动语义**：`std::move(vec)` 后 vec 被清空，Shape 接管数据。
- **Product()**：空形状的乘积为 1（幺元），非空形状返回各维度乘积。
- **内联存储**：Shape 使用内联存储（`shape_storage_[kTVMFFI_CONTAINER_ALIGNED_SHAPE_DIMS]`），小形状无需堆分配。

### Any 转换

```cpp
TEST(Shape, AnyConvert) {
  Shape shape0 = Shape({1, 2, 3});
  Any any0 = shape0;
  auto shape1 = any0.cast<Shape>();
  EXPECT_EQ(shape1.size(), 3);
  EXPECT_EQ(shape1[0], 1);
}
```

验证 Shape 可通过 Any 进行类型擦除和恢复。

### ShapeView

```cpp
TEST(Shape, ShapeView) {
  // 验证 ShapeView 作为非持有视图的行为
  ...
}
```

## Tuple 测试（test_tuple.cc，7 个用例）

### 基本类型安全操作

```cpp
TEST(Tuple, Basic) {
  Tuple<int, float> tuple0(1, 2.0f);
  EXPECT_EQ(tuple0.get<0>(), 1);
  EXPECT_EQ(tuple0.get<1>(), 2.0f);

  Tuple<int, float> tuple1 = tuple0;
  EXPECT_EQ(tuple0.use_count(), 2);

  // COW 验证
  tuple1.Set<0>(3);
  EXPECT_EQ(tuple0.get<0>(), 1);  // 原始不变
  EXPECT_EQ(tuple1.get<0>(), 3);  // 副本已修改
  EXPECT_EQ(tuple0.use_count(), 1);
  EXPECT_EQ(tuple1.use_count(), 1);
}
```

关键验证：
- **编译期类型安全**：`Tuple<int, float>` 的每个位置在编译期确定类型，`get<0>()` 返回 `int`，`get<1>()` 返回 `float`。
- **COW 语义**：Tuple 继承 Array 的 COW 机制——共享时修改触发复制。
- **唯一性优化**：当 `use_count() == 1` 时，`Set` 直接原地修改，不触发复制。

### Any 转换与 Upcast

```cpp
TEST(Tuple, AnyConvert) {
  Tuple<int, float> tuple = {1, 2.0f};
  Any any = tuple;
  auto tuple2 = any.cast<Tuple<int, float>>();
  EXPECT_EQ(tuple2.get<0>(), 1);
}

TEST(Tuple, Upcast) {
  Tuple<TInt, TFloat> tuple = {make_object<TIntObj>(1), make_object<TFloatObj>(2.0)};
  // Upcast 到 Tuple<Any, Any>
  ...
}
```

### 迭代器转发

```cpp
TEST(Tuple, ArrayIterForwarding) {
  Tuple<int, float, String> tuple(1, 2.0f, String("hello"));
  // 验证 Tuple 可被当作 Array 迭代
  ...
}
```

## Variant 测试（test_variant.cc，7 个用例）

### 基本类型选择

```cpp
TEST(Variant, Basic) {
  Variant<int, float> v1 = 1;
  EXPECT_EQ(v1.get<int>(), 1);

  Variant<int, float> v2 = 2.0f;
  EXPECT_EQ(v2.get<float>(), 2.0f);
  v2 = v1;
  EXPECT_EQ(v2.get<int>(), 1);
}
```

Variant 在编译期枚举可选类型，运行期持有其中一个。`get<T>()` 在类型不匹配时抛异常。

### Any 转换

```cpp
TEST(Variant, AnyConvert) {
  Variant<int, TInt> v = 1;
  AnyView view0 = v;
  EXPECT_EQ(view0.as<int>().value(), 1);

  Any any0 = 1;
  auto v1 = any0.cast<Variant<TPrimExpr, Array<TPrimExpr>>>();
  EXPECT_EQ(v1.get<TPrimExpr>()->value, 1);
}
```

Variant 可隐式转换为 AnyView，从 Any 转换时需要显式指定模板参数。

### 对象指针哈希与相等

```cpp
TEST(Variant, ObjectPtrHashEqual) {
  Variant<TInt, TFloat> v1 = TInt(1);
  Variant<TInt, TFloat> v2 = TInt(1);
  // 验证 Variant 的相等比较委托给内部值的结构相等
  EXPECT_EQ(v1, v2);
}
```

### 全 ObjectRef 变体

```cpp
TEST(Variant, AllObjectRef) {
  // Variant 所有可选类型均为 ObjectRef 子类时的行为
  Variant<TInt, TFloat> v = make_object<TIntObj>(1);
  ...
}
```

## Tensor Shape 测试（test_tensor.cc 中的 Shape 相关）

```cpp
TEST(Tensor, Basic) {
  Shape shape = {2, 3, 4};
  DLDataType dtype = DLDataType{kDLFloat, 32, 1};
  DLDevice device = {kDLCPU, 0};
  Tensor tensor = Tensor::Make(shape, dtype, device, ...);
  EXPECT_EQ(tensor->ndim, 3);
  EXPECT_EQ(tensor->shape[0], 2);
  EXPECT_EQ(tensor->dtype.code, kDLFloat);
}
```

Tensor 的 shape 通过 `TensorObj::shape_storage_` 内联存储，支持最多 `kTVMFFI_CONTAINER_ALIGNED_SHAPE_DIMS`（4）维。

## 覆盖矩阵

| 类型 | C++ 用例数 | 核心验证点 |
|------|----------|----------|
| Shape | 3 | 多源构造、内联存储、Product()、Any 转换 |
| Tuple | 7 | 类型安全、COW、Any 转换、Upcast、迭代器 |
| Variant | 7 | 类型选择、Any 转换、哈希相等、ObjectRef 混合 |
| Tensor Shape | 部分 | 内联 shape/stride 存储、DLPack 转换 |

## 设计分析

Shape、Tuple、Variant 三者的测试设计有共同特点：

1. **内联存储优化**：Shape 和 Tensor 使用固定大小的内联数组存储小数据，避免频繁堆分配。测试通过空形状、小维度张量等用例验证这一优化。
2. **COW 一致性**：Tuple 继承 Array 的 COW 机制，测试验证了共享/修改/引用计数的一致性。
3. **Any 互转**：三种类型都支持通过 Any 进行类型擦除，测试覆盖成功转换和类型不匹配的异常路径。
4. **类型安全与灵活性的平衡**：Tuple 在编译期提供类型安全，Variant 在运行期提供类型灵活性，测试分别验证了两者的 API 契约。

## 扩展讨论

### Shape 内联存储：测试如何守护"避免堆分配"的承诺

`Shape({1,2,3})` 与 `Shape(std::move(vec))` 两类构造被同样测试，价值在于证明内联存储（`shape_storage_[kTVMFFI_CONTAINER_ALIGNED_SHAPE_DIMS]`）能在小维度下不依赖 `std::vector` 的堆分配。空形状 `Product()==1` 这个断言尤其耐人寻味——它锁定"空乘积的幺元"语义，这对张量形状计算（如逐步归约 shape）的正确性至关重要：任何一侧在归约到空维度时都必须把累积值视为 1，否则形状推导会产生系统性偏差。内联 + 幺元语义这两个看似不起眼的断言，恰是 Shape 层"零分配 + 数学正确"双重承诺的守卫。

### Tuple 的 COW 与 Array 同源：继承语义的测试复用

`Tuple::Set<0>(3)` 后 `tuple0` 不变、`tuple1` 已改、两者 `use_count()` 各自回落为 1，这是 Tuple 复用 Array 写时复制机制的实证。测试这样写的好处是"不重复证明 COW 本身"（已由 test_array 覆盖），而只强调"Tuple 这一组合类型确实继承了该语义"——一旦未来 Tuple 改用独立存储而不再写时复制，这里会立即暴露共享副本被意外改动，从而防止组合类型打破底层容器的既定承诺。

### Variant 的编译期清单 + 运行期选择：灵活性与安全性的边界

`Variant<int, float>` 在编译期枚举可选类型（任何不在此清单的类型都无法构造），运行期持有其中一个。测试既覆盖"基本类型选择"（`get<int>`/`get<float>`、赋值换型），也覆盖"Any 转换需显式指定模板参数"——这一方能自动锁死清单，防止任意类型悄然混入。它揭示了组合类型的取舍：Tuple 以编译期固定类型换取强类型安全检查，Variant 以运行期类型选择换取表达灵活，而测试分别锁死两者的契约边界，使调用者能按需信任其安全承诺。

## 相关概念

- [057 Shape 形状对象](/04-containers/concepts/057-shape-object.md)
- [060 Tuple 元组](/04-containers/concepts/060-tuple-container.md)
- [062 Variant 变体类型](/04-containers/concepts/062-variant-container.md)
- [066 Tensor 对象设计](/05-tensor-dlpack/concepts/066-tensor-object-design.md)
