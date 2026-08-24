---
type: Concept
title: "视角057：Shape 形状对象"
description: "深入剖析 ShapeView/ShapeObj/Shape 形状对象的三层设计，包括非拥有视图、内联存储形状对象、Product 元素计数、StridesFromShape 步长推导以及与张量系统的协作。"
tags:
  - containers
  - shape
  - tensor
  - inplace-storage
  - npu
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-165, F-166
  - code:
    - include/tvm/ffi/container/shape.h
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/container/tensor.h
---

# 视角057：Shape 形状对象

## 概述

形状（Shape）是张量系统的基础元数据，描述张量各维度的大小。TVM FFI 采用三层设计表示形状：`ShapeView`（非拥有视图）、`ShapeObj`（引用计数的拥有对象）和 `Shape`（ObjectRef 智能句柄）。形状数据统一为 `int64_t` 数组，支持 `Product()` 计算元素总数、`StridesFromShape` 推导步长等核心操作。`Shape` 在可能时应优先使用 `ShapeView` 以避免内存分配，仅在需要托管引用时才使用 `Shape`。

## ShapeView：非拥有视图

`ShapeView` 定义在 `include/tvm/ffi/container/shape.h:41`，是一个轻量级的非拥有视图，内部仅持有一个 `TVMFFIShapeCell`（`shape.h:98`）：

```cpp
class ShapeView {
 public:
  ShapeView() : cell_{nullptr, 0} {}
  ShapeView(const int64_t* data, size_t size) : cell_{data, size} {}
  ShapeView(const std::initializer_list<int64_t>& other)
      : cell_{other.begin(), other.size()} {}
  const int64_t* data() const { return cell_.data; }
  size_t size() const { return cell_.size; }
  // ...
};
```

`TVMFFIShapeCell` 定义在 `include/tvm/ffi/c_api.h:368`，仅有两个字段：

```c
typedef struct {
  const int64_t* data;
  size_t size;
} TVMFFIShapeCell;
```

`ShapeView` 不分配内存、不持有引用，仅包装一个指针和长度，可以安全地按值传递（在 x86-64 上为 16 字节，可通过寄存器传递）。它提供 `operator[]`、`at`（带边界检查）、`begin`/`end`、`front`/`back`、`empty` 等只读访问方法。

`ShapeView` 的 `Product()` 方法（`shape.h:63`）遍历所有维度相乘：

```cpp
int64_t Product() const {
  int64_t product = 1;
  for (size_t i = 0; i < cell_.size; ++i) {
    product *= cell_.data[i];
  }
  return product;
}
```

对于空形状（size=0），`Product()` 返回 1（标量张量的元素数），这是 NumPy 和深度学习框架的惯例。

## ShapeObj：内联存储对象

`ShapeObj` 定义在 `shape.h:102`，继承自 `Object` 和 `TVMFFIShapeCell`：

```cpp
class ShapeObj : public Object, public TVMFFIShapeCell {
 public:
  using index_type = int64_t;
  int64_t Product() const {
    int64_t product = 1;
    for (size_t i = 0; i < this->size; ++i) {
      product *= this->data[i];
    }
    return product;
  }
  static constexpr const uint32_t _type_index = TypeIndex::kTVMFFIShape;
};
```

`ShapeObj` 的数据通过 `make_inplace_array_object` 内联分配（`shape.h:136`），即维度数据紧邻对象头之后存储：

```cpp
TVM_FFI_INLINE ObjectPtr<ShapeObj> MakeEmptyShape(size_t length,
                                                   int64_t** mutable_data) {
  ObjectPtr<ShapeObj> p = make_inplace_array_object<ShapeObj, int64_t>(length);
  static_assert(alignof(ShapeObj) % alignof(int64_t) == 0);
  static_assert(sizeof(ShapeObj) % alignof(int64_t) == 0);
  int64_t* data = reinterpret_cast<int64_t*>(
      reinterpret_cast<char*>(p.get()) + sizeof(ShapeObj));
  if (mutable_data) *mutable_data = data;
  p->data = data;
  p->size = length;
  return p;
}
```

两个静态断言（`shape.h:137-138`）确保 `ShapeObj` 的对齐和大小是 `alignof(int64_t)` 的倍数，保证内联数据的正确对齐。`MakeInplaceShape`（`shape.h:150`）从迭代器范围构造形状，`MakeStridesFromShape`（`shape.h:177`）从形状推导连续步长。

## Shape：托管句柄

`Shape` 定义在 `shape.h:194`，继承自 `ObjectRef`，是 `ShapeObj` 的智能句柄。它提供多种构造方式：

- 默认构造创建空形状（`shape.h:200`）。
- 从迭代器范围构造（`shape.h:209`），内部调用 `MakeInplaceShape`。
- 从 `Array<int64_t>` 构造（`shape.h:217`），复制数据内容。
- 从初始化列表构造（`shape.h:224`）。
- 从 `std::vector<int64_t>` 构造（`shape.h:231`），使用 `ShapeObjStdImpl`（`shape.h:124`）持有 vector。
- 从 `ShapeView` 构造（`shape.h:238`），复制数据。

`Shape` 隐式转换为 `ShapeView`（`shape.h:253`），使得接受 `ShapeView` 的函数可以直接传入 `Shape`。反向转换则是显式的——从 `ShapeView` 构造 `Shape` 需要复制数据。

`Shape` 被标记为不可为空（`TVM_FFI_DEFINE_OBJECT_REF_METHODS_NOTNULLABLE`，`shape.h:307`），即 `Shape` 始终持有有效的 `ShapeObj`，不存在 null 状态。这与 `Array`/`Map` 可为 null 形成对比。

## StridesFromShape 步长推导

`FillStridesFromShape`（`shape.h:164`）从形状推导 C 顺序（行主序）的连续步长：

```cpp
TVM_FFI_INLINE void FillStridesFromShape(ShapeView shape, int64_t* out_strides) {
  int64_t stride = 1;
  for (int64_t i = static_cast<int64_t>(shape.size()) - 1; i >= 0; --i) {
    out_strides[i] = stride;
    stride *= shape[i];
  }
}
```

从最后一维开始，步长初始为 1，每往前一维乘以该维度的大小。例如形状 `[2, 3, 4]` 的步长为 `[12, 4, 1]`。`Shape::StridesFromShape`（`shape.h:245`）返回一个新的 `Shape` 对象持有这些步长。

## 与 Tensor 的协作

`Tensor` 类（`tensor.h`）的 `shape()` 方法返回 `ShapeView`（`tensor.h:307`），直接引用 `TensorObj` 中内联存储的形状数据，零拷贝。`numel()` 方法（`tensor.h:358`）调用 `shape().Product()` 计算元素总数。`TensorObjFromNDAlloc`（`tensor.h:185`）在对象尾部内联分配形状和步长数组（`tensor.h:198-199`），与 `ShapeObj` 的内联存储模式一致。

## 类型特征

`TypeTraits<Shape>`（`shape.h:332`）继承自 `ObjectRefWithFallbackTraitsBase<Shape, Array<int64_t>>`，允许从 `Array<int64_t>` 自动转换为 `Shape`：

```cpp
template <>
struct TypeTraits<Shape>
    : public ObjectRefWithFallbackTraitsBase<Shape, Array<int64_t>> {
  static constexpr int32_t field_static_type_index = TypeIndex::kTVMFFIShape;
  TVM_FFI_INLINE static Shape ConvertFallbackValue(Array<int64_t> src) {
    return Shape(std::move(src));
  }
};
```

这使得函数参数声明为 `Shape` 时，可以接受 `Array<int64_t>` 类型的 `Any` 值，自动转换。注释（`shape.h:330`）明确指出只允许 `Array<int64_t>` → `Shape` 的单向转换，不允许反向。

## NPU建议

在 NPU（神经网络处理单元）环境中，形状对象的设计需要考虑以下优化方向：

1. **维度对齐**：NPU 硬件通常要求张量维度满足特定对齐约束（如 16 的倍数或 32 的倍数）以充分利用向量计算单元。建议在形状推导阶段引入对齐填充（padding），将 `Product()` 计算的原始元素数向上取整到硬件粒度。`Shape` 的内联存储设计使得在分配时一次性包含填充维度成为可能，无需后续修改。

2. **静态形状优先**：NPU 编译器倾向于在编译期确定形状以生成最优指令序列。建议在 NPU 编译流程中尽量使用 `ShapeView`（非拥有、栈上传递），避免在热路径中创建 `ShapeObj` 堆分配。对于动态形状场景，考虑使用固定容量的内联缓冲区（类似 `ShapeView` 的扩展）而非堆分配。

3. **步长与 NPU 内存布局**：NPU 通常使用特殊的内存布局（如 NC4HW4、FRACTAL_NM 等分块布局），其步长不一定是简单的连续行主序。建议扩展 `FillStridesFromShape` 以支持 NPU 特定布局的步长推导，或在 `ShapeObj` 中增加布局标签字段。当前的 `int64_t` 步长精度对于 NPU 的大张量地址偏移是足够的。

4. **形状缓存**：NPU 计算图中相同形状频繁出现。建议利用 `ShapeObj` 的引用计数特性，在编译期对形状进行去重和缓存，相同形状的多个张量共享同一 `ShapeObj` 实例，减少内存占用和比较开销。

5. **DMA 传输描述**：NPU 的 DMA 引擎需要形状和步长信息来描述多维数据传输。`ShapeView` 的 16 字节 POD 布局适合直接嵌入 DMA 描述符，建议在 NPU 运行时中直接使用 `TVMFFIShapeCell` 结构体与固件通信，避免序列化开销。

## 设计分析

1. **视图/对象分离**：`ShapeView` 和 `Shape` 的分离遵循了"非拥有视图优先"的设计原则。函数参数应声明为 `ShapeView` 以接受任意来源的形状数据（栈数组、`Shape` 对象、`Tensor` 内部数据），返回值在需要所有权时使用 `Shape`。这与 `AnyView`/`Any` 的设计模式一致。

2. **内联存储**：`ShapeObj` 使用 `make_inplace_array_object` 将维度数据与对象头连续分配，消除了一次指针解引用和独立堆分配。对于通常只有 4 个维度的张量形状，这种设计非常紧凑高效。

3. **不可为空语义**：`Shape` 标记为 NOTNULLABLE，简化了使用方的空值检查。空形状（0 维）用有效对象表示而非 null，语义更清晰。

4. **与 Array<int64_t> 的关系**：`Shape` 不继承自 `Array<int64_t>`，而是独立的类，但类型系统允许从 `Array<int64_t>` 自动转换。这种设计既保持了形状的类型独立性，又提供了与通用数组的互操作性。

## 相关概念

- [061 原地数组存储](061-inplace-array-storage.md)：ShapeObj 的内联分配机制
- [017 AnyView 非拥有语义](/02-core-types/concepts/017-anyview-non-owning.md)：视图/对象分离的设计模式
- [060 Tuple 类型化元组](060-tuple-container.md)：基于 ArrayObj 的定长类型化容器
- [051 Array 容器与写时复制](051-array-container.md)：Shape 可从 Array<int64_t> 转换
