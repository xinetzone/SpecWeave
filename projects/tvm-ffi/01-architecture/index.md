# 架构与设计哲学

> 分类编号：01-architecture | 视角数量：15 篇

## 概述

本分类从宏观视角解读 TVM FFI 的架构设计哲学，包括分层设计、类型擦除模式、ABI 稳定性、最小核心原则、插件扩展架构等核心设计决策。

## 概念文档

> 按视角编号排序，共 15 篇。

| 编号 | 标题 | 文件链接 |
|------|------|---------|
| 001 | TVM FFI 整体架构总览 | [001-overview-architecture.md](concepts/001-overview-architecture.md) |
| 002 | 分层设计（C ABI → C++ API → 语言绑定） | [002-layered-design.md](concepts/002-layered-design.md) |
| 003 | 类型擦除模式 | [003-type-erasure-pattern.md](concepts/003-type-erasure-pattern.md) |
| 004 | 值语义与引用语义 | [004-value-vs-reference-semantics.md](concepts/004-value-vs-reference-semantics.md) |
| 005 | ABI 稳定性策略 | [005-abi-stability-strategy.md](concepts/005-abi-stability-strategy.md) |
| 006 | 最小核心设计哲学 | [006-minimal-core-philosophy.md](concepts/006-minimal-core-philosophy.md) |
| 007 | 核心数据结构 | [007-core-data-structures.md](concepts/007-core-data-structures.md) |
| 008 | 模块系统与动态加载 | [008-module-system-dynamic-loading.md](concepts/008-module-system-dynamic-loading.md) |
| 009 | 扩展点与插件机制 | [009-extension-points-plugin-mechanism.md](concepts/009-extension-points-plugin-mechanism.md) |
| 010 | 函数注册表 | [010-function-registry.md](concepts/010-function-registry.md) |
| 011 | 跨语言边界设计 | [011-cross-language-boundary.md](concepts/011-cross-language-boundary.md) |
| 012 | 异步流与设备管理 | [012-async-stream-device-management.md](concepts/012-async-stream-device-management.md) |
| 013 | 内存所有权模型 | [013-memory-ownership-model.md](concepts/013-memory-ownership-model.md) |
| 014 | 错误处理与异常安全 | [014-error-handling-exception-safety.md](concepts/014-error-handling-exception-safety.md) |
| 015 | 版本演进与兼容性 | [015-version-evolution-compatibility.md](concepts/015-version-evolution-compatibility.md) |

## 参考资源

- [信源清单](references/sources.md) - 本分类相关源码路径与API清单
- [变更日志](log.md) - 文档变更历史记录
