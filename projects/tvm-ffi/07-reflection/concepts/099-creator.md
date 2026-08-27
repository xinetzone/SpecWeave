---
type: Concept
title: "视角099：Creator 创建函数"
description: "解析反射创建机制：TVMFFIObjectCreator 签名、ObjectCreatorDefault/UnsafeInit、CreateEmptyObject 的 native creator 与 __ffi_new__ 回退、ObjectCreator 按字段映射构造，以及自定义分配器与 NPU 集成建议。"
tags:
  - reflection
  - creator
  - object-factory
  - npu
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-040, F-041, F-260
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/reflection/creator.h
    - include/tvm/ffi/reflection/registry.h
    - include/tvm/ffi/reflection/accessor.h
---

# 视角099：Creator 创建函数

## 概述

Creator（创建函数）是 TVM FFI 反射系统中负责分配空对象实例的工厂机制。C ABI 层以 `TVMFFIObjectCreator` 函数指针类型（`include/tvm/ffi/c_api.h:954`）表达，C++ 层通过 `ObjectCreatorDefault`/`ObjectCreatorUnsafeInit`（`registry.h:417-430`）提供默认实现，运行时通过 `CreateEmptyObject`（`creator.h:43`）分派到 native creator 或 `__ffi_new__` 类型属性。Creator 使得对象可在不了解 C++ 构造函数的情况下，仅凭类型键与字段映射被反射构造，是反序列化、Python `@c_class` 实例化、跨语言对象创建的基础。

## C ABI 层

### TVMFFIObjectCreator 类型

```c
typedef int (*TVMFFIObjectCreator)(TVMFFIObjectHandle* result);
```

定义在 `c_api.h:954`。Creator 接受一个输出句柄指针，返回 0 表示成功、非零表示错误。其契约是：分配一个零初始化的对象，但**不**负责字段的语义初始化——调用者必须随后通过字段 setter 逐字段填充，才能使对象进入有效状态（`c_api.h:1283-1286`）。

### TVMFFITypeMetadata.creator

Creator 存储在 `TVMFFITypeMetadata::creator` 字段（`c_api.h:1288`），通过 `TVMFFITypeRegisterMetadata`（`c_api.h:1420`）注册。为 NULL 表示该类型不支持反射创建。

### 自定义类分配器

C ABI 还提供更底层的自定义分配器接口：

- **`TVMFFISetCustomClassAllocator`**（`c_api.h:510`，事实 F-040）：为指定类型索引注册自定义的分配与释放函数（`TVMFFIObjectAllocFunc`/`TVMFFIObjectFreeFunc`），允许替换默认的 `new`/`delete` 路径，适用于内存池、共享内存、设备内存等特殊分配需求。
- **`TVMFFIObjectNew`**（`c_api.h:520`，事实 F-041）：按类型索引创建新对象句柄，内部调用已注册的自定义分配器或默认分配器。

## C++ 层默认 Creator

`ObjectDef<T>::RegisterExtraInfo`（`registry.h:983-987`）根据类型的可构造性自动选择 creator：

1. 若 `std::is_default_constructible_v<Class>`，使用 `ObjectCreatorDefault<Class>`（`registry.h:417`），内部调用 `make_object<Class>()`。
2. 否则若 `std::is_constructible_v<Class, UnsafeInit>`，使用 `ObjectCreatorUnsafeInit<Class>`（`registry.h:425`），调用 `make_object<Class>(UnsafeInit{})`，适用于需要跳过构造函数初始化、由反射 setter 逐字段填充的类型。
3. 两者皆不可时 creator 为 NULL。

`UnsafeInit` 是一个标签类型，告知构造函数不执行成员初始化，由反射层负责填充，避免默认构造与反射赋值的双重初始化开销。

## CreateEmptyObject 分派

`CreateEmptyObject`（`creator.h:43-67`）实现两级分派：

1. **快速路径**：若 `metadata->creator != nullptr`，直接调用 native creator，返回拥有的 `ObjectPtr<Object>`。这是 C++ 类型的常见路径。
2. **回退路径**：若 native creator 为 NULL，查找 `__ffi_new__` 类型属性列（`accessor.h:329`）。该列存储 Python `@py_class` 或其他动态语言定义类型的分配器。通过 `TVMFFIGetTypeAttrColumn`（`c_api.h:1434`）获取列，按类型索引偏移取出 `Function`，调用它得到 `ObjectRef`，再转为 `ObjectPtr`。
3. 两者均不可用时抛出 `RuntimeError`，说明类型不支持反射创建。

`HasCreator`（`creator.h:77-91`）提供只读检查，用于在构造前预判能力。

## ObjectCreator 字段填充

`reflection::ObjectCreator`（`creator.h:120-191`）是面向用户的高层工厂，接受类型键或 `TVMFFITypeInfo*`，提供 `operator()(const Map<String, Any>& fields)`：

1. 调用 `CreateEmptyObject` 分配空对象。
2. 通过 `ForEachFieldInfo`（`accessor.h:265`）遍历所有继承字段，对每个字段：
   - 若字段名在传入的 `fields` 映射中，调用 `CallFieldSetter`（`accessor.h:67`）设置值。
   - 否则若字段有默认值（`HasDefault` 标志），调用 `SetFieldToDefault`（`accessor.h:243`）填充默认值，对工厂默认值会调用工厂函数产生新实例。
   - 否则抛出 `TypeError`，报告必填字段缺失。
3. 校验传入字段数与匹配字段数一致。若有多余字段名，遍历字段表确认是否存在不存在的字段，抛出错误报告未知字段。
4. 返回填充完成的 `ObjectRef`。

这一流程完整实现了"按字段名反射构造"，等价于 Python 中 `MyClass(field1=val1, field2=val2)` 的语义。

## 与 __ffi_new__/__ffi_init__ 的关系

Creator 机制与 Python 集成的三个类型属性紧密相关：

- **`__ffi_new__`**：零参数分配器，是 creator 的动态语言回退形式。C++ native creator 也会在 `ObjectDef` 析构时被包装为 `__ffi_new__` 列（`registry.h:763-774`），供 Python 侧统一调用。
- **`__ffi_init__`**：打包构造函数，在 `__ffi_new__` 分配的空对象上执行初始化。显式 `init<Args...>()` 注册时，`__ffi_init__` 直接调用 C++ 构造函数；否则由 `ffi._RegisterFFIInit` 生成基于反射字段的默认 init，内部等价于调用 `ObjectCreator(fields)`。
- **`__ffi_shallow_copy__`**：浅拷贝工厂，通过拷贝构造分配新对象并复制所有反射字段值。

## NPU建议

在 NPU（神经网络处理单元）集成场景中，Creator 创建函数的设计需要关注以下方面：

1. **设备内存对象的自定义分配器**：NPU 张量、命令缓冲区、设备端句柄等对象通常需要分配在设备可访问内存（如 PCIe BAR 映射内存、片上 SRAM、DMA 一致内存）而非普通堆内存。建议为这类类型通过 `TVMFFISetCustomClassAllocator` 注册自定义 `TVMFFIObjectAllocFunc`/`TVMFFIObjectFreeFunc`，在 alloc 中调用 NPU 驱动的内存分配接口（如 `cuMemAlloc`、`hsa_amd_memory_pool_allocate` 或厂商 SDK 的 `NpuMalloc`），在 free 中调用对应释放接口。这样反射创建的对象天然位于正确内存域，无需事后迁移。

2. **Creator 与对象池集成**：NPU 编译流程中可能频繁创建和销毁小型描述符对象（如算子参数、调度原语）。建议为高频类型注册基于对象池（object pool）的 creator，从预分配的对象池中取空槽位而非每次 `new`。`TVMFFIObjectCreator` 的零参数契约与对象池的 `acquire()` 天然契合，释放时通过 `TVMFFIObjectFreeFunc` 归还池中而非 `delete`。

3. **设备特定类型的条件创建**：多 NPU 环境中，同一逻辑类型可能因设备型号不同而有不同的字段布局或创建约束。建议 creator 在分配时检查当前线程/上下文中的目标设备（通过 NPU 插件提供的 `npu.get_current_device()` 全局函数），选择对应的本地类型或初始化设备特定字段。也可注册设备特定子类（如 `"npu.vendorx.OpDesc"` vs `"npu.vendory.OpDesc"`），通过类型键路由到不同 creator。

4. **Creator 的线程安全与无锁化**：NPU 编译器可能多线程并行构造 IR。默认的 `make_object` 依赖全局 `new`，多线程下存在锁竞争。建议自定义分配器使用线程本地缓存（thread-local cache）或无锁自由列表分配反射对象，确保 `ObjectCreator` 在并行 lower/调度阶段不成为瓶颈。Creator 本身应保持无状态或仅持有不可变配置，避免在 creator 中加锁。

5. **异步资源的延迟初始化**：NPU 对象（如内核库句柄、流、事件）的创建可能涉及与驱动的同步通信，开销较大。建议 creator 仅分配壳对象并将设备句柄字段初始化为惰性句柄（lazy handle），真正的驱动资源在首次使用时通过字段 getter 触发创建。反射字段可使用 `DefaultFactory` 注册一个返回惰性占位符的工厂，避免反射构造路径阻塞。

6. **跨进程共享对象的 Creator**：NPU 编译服务可能采用多进程架构，编译结果（如序列化的算子图）需在进程间共享。建议为可共享对象注册基于共享内存的 creator，从已映射的共享内存段中构造对象而非堆分配。这类 creator 应禁用引用计数递减时的 `delete`，改为引用分离（detach）语义，由共享内存所有者统一释放。

7. **错误处理与设备状态回滚**：NPU creator 可能因设备内存不足、固件错误等原因失败。`TVMFFIObjectCreator` 返回非零错误码的契约允许 creator 通过 TLS 错误机制（`TVMFFICtxSetLastError`）报告设备特定错误。建议在 creator 失败时确保已分配的部分资源被正确释放，避免设备内存泄漏；`ObjectCreator` 高层接口会将错误码转为 C++ 异常，调用方可据此触发降级或重试。

## 设计分析

Creator 机制将"分配"与"初始化"干净分离：creator 只负责产生零初始化的内存壳，字段填充由反射层通用完成。这一分离带来三大好处：一是同一 creator 可服务于反序列化、Python 构造、拷贝等多种场景；二是 creator 的极简签名（零参数、一句柄输出）使任意语言都能实现，Python `@py_class` 与 C++ 类型在 ABI 层对等；三是自定义分配器钩子让框架核心不感知设备内存、内存池等特殊需求，通过组合而非修改核心代码满足 NPU 等异构场景。`UnsafeInit` 标签的引入承认了"反射构造会逐字段设置，默认构造的初始化是浪费"这一事实，为性能敏感类型提供了跳过冗余初始化的出口。整体设计在保持 ABI 最小化的同时，为内存管理定制保留了充分的扩展点。

## 相关概念

- [088 TypeMetadata](088-type-metadata.md)：creator 字段的宿主
- [090 ObjectDef 构建器](090-object-def-builder.md)：注册默认 creator 的入口
- [097 TypeAttr 类型属性](097-type-attr.md)：__ffi_new__ 回退机制
- [092 c_class Python 集成](092-c-class-python-integration.md)：消费 creator 的 Python 路径
