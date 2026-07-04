---
title: "TVM FFI 完整学习教程"
source: "spec:create-tvm-ffi-wiki-tutorial"
tags: [tvm, ffi, abi, cross-language, cpp, python, dlpack, cuda, orcjit, reflection]
date: 2026-07-04
---

# TVM FFI 完整学习教程

TVM FFI（Foreign Function Interface）是 Apache TVM 项目提供的跨语言 C++/Python/Rust 互操作框架。它通过稳定的 C ABI 实现零拷贝类型擦除值传递，支持对象系统、反射、序列化、容器类型、CUDA 支持和 ORCJIT 扩展。

## 统计摘要

- **总章节数**：16（含导航入口）
- **覆盖语言**：C / C++ / Python / Rust
- **源码基础**：`external/ffi/tvm-ffi/` + `https://tvm.apache.org/ffi/`

## 阅读路径

### 入门路径（新手推荐）
1. [00 - 概述与定位](00-overview.md)
2. [01 - 系统架构与设计理念](01-architecture.md)
3. [11 - 编译构建与项目集成](11-build-and-integration.md)
4. [12 - 完整实战示例](12-examples.md)

### 核心概念路径（深入理解）
1. [02 - C++ 核心 API](02-cpp-core-api.md)
2. [03 - 类型系统](03-type-system.md)
3. [04 - 容器类型](04-containers.md)
4. [05 - 反射与注册机制](05-reflection.md)
5. [06 - 序列化](06-serialization.md)

### 高级功能路径（进阶开发）
1. [07 - Python 绑定机制](07-python-bindings.md)
2. [08 - CUDA 支持](08-cuda-support.md)
3. [09 - ORCJIT 扩展](09-orcjit-extension.md)
4. [10 - DLPack 集成](10-dlpack-integration.md)

### 参考路径（速查）
1. [13 - 最佳实践与性能优化](13-best-practices.md)
2. [14 - 常见问题解答](14-faq.md)
3. [15 - 参考资料与学习路径](15-resources.md)

## 关联知识

- [Interface/API/ABI/Protocol 四层技术栈教程](../interface-api-abi-protocol-wiki/00-overview.md)
- [IDL 接口定义语言完整教程](../idl-wiki/00-overview.md)
- [Agent ABI：跨语言边界层](../agent-interface-deep-dive/03-agent-abi.md)