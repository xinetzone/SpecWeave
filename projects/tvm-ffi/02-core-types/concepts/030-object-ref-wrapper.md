---
type: Concept
title: "视角030：ObjectRef 包装器"
description: "分析 ObjectRef 作为 ObjectPtr<Object> 的语义化包装层，包括 defined/unique/use_count 生命周期查询、as/as_or_throw 类型安全向下转型、same_as/operator== 指针比较，以及左值/右值重载的移动优化。"
tags:
  - core-types
  - objectref
  - smart-pointer
  - downcast
  - raii
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-046, F-047, F-048, F-049, F-050, F-051, F-052, F-053, F-054, F-055, F-056, F-057, F-058, F-059, F-060, F-061, F-062, F-063
  - code:
    - include/tvm/ffi/object.h
---

# 视角030：ObjectRef 包装器

## 概述

`ObjectRef` 是所有 FFI 对象引用类型的基类，定义在 `include/tvm/ffi/object.h:791`。它在 `ObjectPtr<Object>` 智能指针之上提供了语义化的类型安全接口，包括空值检查、引用计数查询、向下转型和比较运算。`String`、`Array<T>`、`Map<K,V>`、`PackedFunc`、`Module` 等具体类型均继承自 `ObjectRef`，构成 FFI 对象系统的用户-facing 层。

## 类结构

```cpp
class ObjectRef {
 public:
  ObjectRef() = default;
  ObjectRef(const ObjectRef& other) = default;
  ObjectRef(ObjectRef&& other) noexcept;
  ObjectRef& operator=(const ObjectRef& other) = default;
  ObjectRef& operator=(ObjectRef&& other) noexcept;
  explicit ObjectRef(ObjectPtr<Object> data);
  explicit ObjectRef(UnsafeInit);

  bool defined() const;
  const Object* get() const;
  const Object* operator->() const;
  bool unique() const;
  int use_count() const;
  bool same_as(const ObjectRef& other) const;

  template <typename ObjectType>
  const ObjectType* as() const&;

  template <typename ObjectRefType>
  std::optional<ObjectRefType> as() const&;
  template <typename ObjectRefType>
  std::optional<ObjectRefType> as() &&;

  template <typename ObjectRefType>
  ObjectRefType as_or_throw() const&;
  template <typename ObjectRefType>
  ObjectRefType as_or_throw() &&;

  int32_t type_index() const;
  std::string GetTypeKey() const;

 protected:
  ObjectPtr<Object> data_;
};
```

## 数据成员

`ObjectRef` 仅包含一个 `protected` 成员 `data_`（`object.h:987`）：

```cpp
ObjectPtr<Object> data_;
```

`ObjectPtr<Object>` 是引用计数智能指针，负责 `IncRef`/`DecRef`。`ObjectRef` 本身不直接操作引用计数，而是通过 `ObjectPtr` 的 RAII 语义管理生命周期。这种组合优于继承的设计——`ObjectRef` 不是 `ObjectPtr` 的子类，而是在其之上构建领域语义。

## 生命周期查询

### defined()

```cpp
bool defined() const { return data_ != nullptr; }
```

检查引用是否指向有效对象。空 `ObjectRef`（默认构造）返回 false。这是判断引用是否有效的惯用方式，也支持与 `nullptr` 的隐式比较。

### unique()

```cpp
bool unique() const { return data_.unique(); }
```

委托给 `ObjectPtr::unique()`，检查强引用计数是否为 1。这是 copy-on-write 优化的关键——如果 `unique()` 返回 true，可以直接修改对象而无需创建副本。

### use_count()

```cpp
int use_count() const { return data_.use_count(); }
```

返回当前强引用计数。文档标注"for debug purposes"，因为在多线程环境中该值可能瞬时过时。

### get() 和 operator->()

```cpp
const Object* get() const { return data_.get(); }
const Object* operator->() const { return get(); }
```

返回 const 对象指针，不转移所有权。`operator->` 允许通过 `ref->method()` 语法直接访问对象方法。注意返回的是 `const Object*`，可变访问需要子类通过 `get_mutable()` 获取。

## 类型安全向下转型

### as<ObjectType>() — 返回裸指针

模板约束 `ObjectType` 必须是 `Object` 的子类（`object.h:861-868`）：

```cpp
template <typename ObjectType,
          typename = std::enable_if_t<std::is_base_of_v<Object, ObjectType>>>
const ObjectType* as() const& {
  if (data_ != nullptr && data_->IsInstance<ObjectType>()) {
    return static_cast<ObjectType*>(data_.get());
  } else {
    return nullptr;
  }
}
```

这是最直接的向下转型方式：
1. 检查 `data_` 非空。
2. 调用 `Object::IsInstance<ObjectType>()` 进行运行时类型检查。
3. 通过 `static_cast` 向下转型（而非 `dynamic_cast`，因为已手动验证类型）。
4. 失败返回 `nullptr`。

返回的裸指针不增加引用计数，调用者必须确保在 `ObjectRef` 存活期间使用。

### as<ObjectRefType>() const& — 返回 optional 引用

当模板参数是 `ObjectRef` 子类时（`object.h:879-901`），返回 `std::optional<ObjectRefType>`：

```cpp
template <typename ObjectRefType,
          typename = std::enable_if_t<std::is_base_of_v<ObjectRef, ObjectRefType>>>
std::optional<ObjectRefType> as() const& {
  if (data_ != nullptr) {
    TVMFFIAny any_data;
    any_data.type_index = data_->type_index();
    any_data.v_obj = reinterpret_cast<TVMFFIObject*>(const_cast<Object*>(data_.get()));
    if (TypeTraits<ObjectRefType>::CheckAnyStrict(&any_data)) {
      ObjectRefType result(UnsafeInit{});
      result.data_ = data_;  // 拷贝 ObjectPtr，增加引用计数
      return result;
    }
    return std::nullopt;
  }
  if constexpr (ObjectRefType::_type_is_nullable) {
    return ObjectRefType(UnsafeInit{});
  }
  return std::nullopt;
}
```

关键设计：通过构造临时 `TVMFFIAny` 复用 `TypeTraits<ObjectRefType>::CheckAnyStrict` 进行类型检查。这避免了为 `ObjectRef` 层次重复实现类型检查逻辑，统一了类型系统。

成功时：
1. 通过 `UnsafeInit` 构造函数创建目标类型（跳过正常的类型检查构造）。
2. 拷贝 `data_`（`ObjectPtr` 拷贝增加引用计数）。
3. 返回拥有新引用的 `ObjectRefType`。

空值处理：如果源为空且目标类型可为空（`_type_is_nullable == true`），返回空的目标类型引用；否则返回 `std::nullopt`。

### as<ObjectRefType>() && — 移动版本

右值版本（`object.h:914-937`）在转型成功时移动 `data_` 而非拷贝：

```cpp
template <typename ObjectRefType>
std::optional<ObjectRefType> as() && {
  if (data_ != nullptr) {
    // ... 类型检查 ...
    if (TypeTraits<ObjectRefType>::CheckAnyStrict(&any_data)) {
      ObjectRefType result(UnsafeInit{});
      result.data_ = std::move(data_);  // 移动 ObjectPtr，不增加引用计数
      data_ = nullptr;
      return result;
    }
    return std::nullopt;
  }
  // ...
}
```

移动后源 `ObjectRef` 变为空，避免不必要的引用计数原子操作。

### as_or_throw<ObjectRefType>()

`as_or_throw`（`object.h:945-960`）在转型失败时抛出 `TypeError` 而非返回 `nullopt`。同样提供 const& 和 && 两个版本。它在内部调用 `as()` 并在失败时生成包含类型键的详细错误消息。

## 比较运算

### same_as

```cpp
bool same_as(const ObjectRef& other) const { return data_ == other.data_; }
```

执行浅比较，比较内部 `ObjectPtr` 是否指向同一对象。对于两个内容相同但地址不同的对象，`same_as` 返回 false。

### operator== 和 operator!=

```cpp
bool operator==(const ObjectRef& other) const { return data_ == other.data_; }
bool operator!=(const ObjectRef& other) const { return data_ != other.data_; }
```

同样是指针比较，委托给 `ObjectPtr::operator==`。这与 `same_as` 行为一致。如果需要内容比较（结构性相等），应使用 `StructuralEqual` 或特定类型的等值运算符。

### operator<

```cpp
bool operator<(const ObjectRef& other) const { return data_.get() < other.data_.get(); }
```

按指针地址排序，主要用于在 `std::set`/`std::map` 中作为键使用。这是地址顺序而非语义顺序。

## 类型信息查询

### type_index()

```cpp
int32_t type_index() const {
  return data_ != nullptr ? data_->type_index() : TypeIndex::kTVMFFINone;
}
```

空引用返回 `kTVMFFINone`（0），非空返回对象的运行时类型索引。

### GetTypeKey()

```cpp
std::string GetTypeKey() const {
  return data_ != nullptr ? data_->GetTypeKey() : StaticTypeKey::kTVMFFINone;
}
```

空引用返回 `"nullptr"` 类型键，非空通过 `TVMFFIGetTypeInfo` 查询类型键字符串。此操作较慢，主要用于错误报告。

## 类型配置静态成员

`ObjectRef` 定义了子类可以覆盖的静态配置（`object.h:978-983`）：

```cpp
using ContainerType = Object;
static constexpr bool _type_container_is_exact = true;
static constexpr bool _type_is_nullable = true;
```

- `ContainerType`：此引用类型持有的对象 C++ 类。子类（如 `String`）覆盖为对应的 `StringObj`。
- `_type_container_is_exact`：`ContainerType` 是否精确描述可持有的对象类型。对于泛型容器（如 `Array<T>` 的基类），可能为 false。
- `_type_is_nullable`：引用是否可以为空。某些非空引用类型（如 `Arc<T>` 包装的）将此设为 false。

## UnsafeInit 标签

`UnsafeInit`（`object.h:783`）是一个标签类型，用于构造不进行类型检查的 `ObjectRef`：

```cpp
explicit ObjectRef(UnsafeInit) : data_(nullptr) {}
```

子类在 `as()` 转型成功后使用 `ObjectRefType(UnsafeInit{})` 构造空对象，然后直接赋值 `data_`。这避免了构造函数中的类型检查开销——因为类型检查已由 `as()` 完成。这是一个内部优化机制，用户代码通常不需要直接使用。

## 子类宏

具体 `ObjectRef` 子类通过 `TVM_FFI_DEFINE_OBJECT_REF_METHODS_NULLABLE` 或 `TVM_FFI_DEFINE_OBJECT_REF_METHODS_NOTNULLABLE` 宏生成标准方法。这些宏声明 `ContainerType`、构造函数和类型转换方法，确保子类遵循统一的接口约定。

## 设计分析

`ObjectRef` 的设计体现了以下原则：

1. **分层抽象**：`Object`（对象数据+引用计数原语）→ `ObjectPtr`（RAII 智能指针）→ `ObjectRef`（语义化引用类型），每层职责清晰。
2. **const 正确性**：`get()` 和 `operator->()` 返回 `const Object*`，防止意外修改共享对象。可变访问需要显式通过子类的 `get_mutable()` 或 COW 机制。
3. **统一类型检查**：通过临时 `TVMFFIAny` 复用 `TypeTraits::CheckAnyStrict`，避免了 `ObjectRef` 层次与 `Any` 类型系统的逻辑重复。
4. **移动优化**：右值 `as()` 移动 `ObjectPtr`，避免原子引用计数操作，在链式调用和函数返回时高效。
5. **指针语义**：`operator==` 比较的是对象身份（地址）而非内容，这与 Java/C# 的引用类型语义一致。内容比较需要显式使用结构相等。
6. **可空性配置**：`_type_is_nullable` 允许类型系统区分可空和非空引用，在 `as()` 转型时正确处理空值。

## 相关概念

- [027 TVMFFIObject 对象头](027-object-header.md)：Object 基类与头部
- [028 组合引用计数](028-combined-refcount.md)：ObjectPtr 的引用计数机制
- [029 对象继承模型](029-object-inheritance.md)：IsInstance 类型检查
- [023 TypeTraits 机制](023-type-traits.md)：CheckAnyStrict 类型检查
- [025 FFI 移动语义](025-ffi-move-semantics.md)：RValueRef 与 ObjectRef 的移动
