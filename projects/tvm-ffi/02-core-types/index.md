# 核心类型系统

> 分类编号：02-core-types | 视角数量：20 篇

## 概述

本分类深入剖析 TVM FFI 的核心类型系统，涵盖 TVMFFIAny 16字节布局、AnyView/Any 语义、TypeIndex 类型索引、Object/ObjectPtr/ObjectRef 引用计数模型、DataType/Device 以及类型转换机制。

## 概念文档

> 按视角编号排序，共 20 篇。

| 编号 | 标题 | 文件链接 |
|------|------|---------|
| 016 | TVMFFIAny 16字节布局 | [016-any-16-byte-layout.md](concepts/016-any-16-byte-layout.md) |
| 017 | AnyView 非拥有语义 | [017-anyview-non-owning.md](concepts/017-anyview-non-owning.md) |
| 018 | Any 拥有语义 | [018-any-owning.md](concepts/018-any-owning.md) |
| 019 | TypeIndex 类型索引 | [019-type-index.md](concepts/019-type-index.md) |
| 020 | 静态与动态类型索引 | [020-static-dynamic-type-index.md](concepts/020-static-dynamic-type-index.md) |
| 021 | 小字符串优化 | [021-small-string-optimization.md](concepts/021-small-string-optimization.md) |
| 022 | 小字节数组优化 | [022-small-bytes-optimization.md](concepts/022-small-bytes-optimization.md) |
| 023 | TypeTraits 机制 | [023-type-traits.md](concepts/023-type-traits.md) |
| 024 | cast/try_cast/as 类型访问 | [024-cast-try-cast-as.md](concepts/024-cast-try-cast-as.md) |
| 025 | FFI 移动语义 | [025-ffi-move-semantics.md](concepts/025-ffi-move-semantics.md) |
| 026 | 跨边界复制语义 | [026-cross-boundary-copy.md](concepts/026-cross-boundary-copy.md) |
| 027 | TVMFFIObject 对象头 | [027-object-header.md](concepts/027-object-header.md) |
| 028 | 组合引用计数 | [028-combined-refcount.md](concepts/028-combined-refcount.md) |
| 029 | 对象继承模型 | [029-object-inheritance.md](concepts/029-object-inheritance.md) |
| 030 | ObjectRef 包装器 | [030-object-ref-wrapper.md](concepts/030-object-ref-wrapper.md) |
| 031 | Deleter 析构机制 | [031-deleter.md](concepts/031-deleter.md) |
| 032 | 不透明对象 | [032-opaque-object.md](concepts/032-opaque-object.md) |
| 033 | Python 不透明对象 | [033-python-opaque-object.md](concepts/033-python-opaque-object.md) |
| 034 | FFI 右值引用 | [034-ffi-rvalue-ref.md](concepts/034-ffi-rvalue-ref.md) |
| 035 | 类型转换流水线 | [035-type-conversion-pipeline.md](concepts/035-type-conversion-pipeline.md) |

## 参考资源

- [信源清单](references/sources.md) - 本分类相关源码路径与API清单
- [变更日志](log.md) - 文档变更历史记录
