---
id: "ffi-wiki-resources"
title: "术语表与参考资料"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/01-agent-protocols-interfaces/ffi-wiki/07-resources.toml"
source: "spec:create-ffi-wiki-tutorial"
category: "learning"
tags: ["ffi", "glossary", "references", "further-reading"]
date: "2026-07-04"
status: "stable"
author: "SpecWeave"
summary: "FFI 相关术语表（≥15条）、权威参考资料、分难度扩展阅读建议与项目内相关 wiki 交叉引用。"
---

# 术语表与参考资料

## 术语表 (Glossary)

以下术语表涵盖 FFI 领域最核心的概念，按主题分组排列。

| 术语 | 英文 | 定义 |
|---|---|---|
| 外部函数接口 | FFI (Foreign Function Interface) | 允许一种编程语言调用另一种语言编写的函数的机制，是现代多语言互操作的核心技术。 |
| 调用约定 | Calling Convention | 函数调用时参数传递顺序、寄存器使用、返回值处理和栈清理职责的底层规则集合。 |
| 名称修饰 | Name Mangling | C++ 编译器将函数名编码为包含命名空间、类名和参数类型信息的唯一符号名，以支持函数重载。 |
| 数据封送 | Marshalling | 将数据从一种语言的内部表示形式转换为另一种语言可理解的形式，是跨语言通信的关键步骤。 |
| 数据解封 | Unmarshalling | Marshalling 的逆过程，将跨语言传递后的数据还原为本语言的原生表示形式。 |
| 桩代码 | Stub | 自动生成的中间代码，负责在两种语言之间进行类型转换和调用转发，通常由绑定生成器产生。 |
| 跳板 | Trampoline | 一小段动态生成的代码，用于在运行时调整调用目标或调用约定，常见于 JIT 编译和动态 FFI 场景。 |
| 形式转换块 | Thunk | 在调用链中插入的适配代码段，完成参数或返回值的格式转换，是调用约定适配的常用手段。 |
| C 应用二进制接口 | C ABI | C 语言定义的二进制接口规范，规定了类型布局、调用约定和符号命名规则，是 FFI 的事实标准。 |
| 外部 C 链接 | extern "C" | C++ 关键字，指示编译器对声明的函数或变量使用 C 链接方式（不进行名称修饰），是实现 C++ 与 C 互操作的基础。 |
| 平台调用 | P/Invoke (Platform Invoke) | .NET/C# 中调用非托管 DLL 或共享库中函数的机制，通过 `DllImport` 属性声明外部函数。 |
| Java 本地接口 | JNI (Java Native Interface) | Java 中调用本地 C/C++ 代码的标准框架，需要在 Java 和本地侧分别编写代码。 |
| Java 本地访问 | JNA (Java Native Access) | 基于 libffi 的 Java FFI 库，只需在 Java 侧定义接口即可调用本地库，无需编写本地代码。 |
| Cgo | cgo | Go 语言内置的 C 互操作机制，通过在 Go 文件中使用特殊注释和 `import "C"` 实现。 |
| C 类型 | ctypes | Python 标准库中的 FFI 模块，基于 libffi 实现，可在运行时加载共享库并调用其中的函数。 |
| C FFI | cffi (C Foreign Function Interface) | Python 第三方 FFI 库，支持 ABI 级（运行时动态调用）和 API 级（编译时生成扩展）两种模式。 |
| 绑定生成器 | bindgen | Rust 生态中的核心工具，根据 C/C++ 头文件自动生成安全的 Rust FFI 绑定代码。 |
| Libffi | libffi | 可移植的 FFI 底层库，在运行时根据调用约定信息构造函数调用，是 Python ctypes、JNA 等众多工具的基础。 |
| 简化包装接口生成器 | SWIG (Simplified Wrapper and Interface Generator) | 多语言自动绑定生成工具，从 C/C++ 头文件生成 Python、Java、Ruby 等数十种语言的绑定代码。 |
| 动态链接 | Dynamic Linking | 运行时加载共享库（.so/.dll/.dylib）并解析符号地址，是 FFI 加载外部库的主要方式。 |
| 静态链接 | Static Linking | 编译时将库的目标代码直接嵌入可执行文件，无需运行时依赖外部库文件。 |

## 权威参考资料

### 语言官方文档

| 语言/平台 | FFI 机制 | 官方文档 |
|---|---|---|
| Python | ctypes | https://docs.python.org/3/library/ctypes.html |
| Python | cffi | https://cffi.readthedocs.io/ |
| Java | JNI | https://docs.oracle.com/javase/8/docs/technotes/guides/jni/ |
| Go | cgo | https://pkg.go.dev/cmd/cgo |
| Rust | FFI | https://doc.rust-lang.org/nomicon/ffi.html |
| Node.js | ffi-napi | https://github.com/node-ffi-napi/node-ffi-napi |
| C# | P/Invoke | https://learn.microsoft.com/en-us/dotnet/standard/native-interop/pinvoke |

### 通用参考

- **Wikipedia — Foreign Function Interface**: https://en.wikipedia.org/wiki/Foreign_function_interface
- **System V AMD64 ABI Specification**: x86-64 架构的权威 ABI 规范，定义了 C 调用约定、类型布局和栈帧结构
- **Calling Conventions (OSDev Wiki)**: https://wiki.osdev.org/Calling_Conventions — 涵盖 x86、x86-64、ARM 等多种架构的调用约定详解
- **libffi 官方**: https://sourceware.org/libffi/ — 可移植 FFI 底层库，众多高级 FFI 工具的基石
- **SWIG 官方**: https://www.swig.org/ — 多语言绑定生成工具，支持 C/C++ 到 Python、Java、Ruby 等数十种语言

## 扩展阅读（按难度分级）

### 入门

- 各语言官方 FFI 入门教程（Python ctypes 入门、Go cgo 教程、Rust FFI 入门）
- "How to call C from Python" 系列博客：从简单的函数调用到复杂结构体传递
- "How to call C from Rust" 系列博客：unsafe 块、绑定生成、内存安全实践

### 进阶

- **调用约定深入**：不同架构（x86 / x86-64 / ARM / RISC-V）的 ABI 规范对比，理解跨平台 FFI 的差异来源
- **绑定生成工具原理**：SWIG 的类型映射机制、bindgen 的 Clang libtooling 实现原理
- **跨语言异常处理**：C++ 异常如何跨越 FFI 边界传递，各语言的异常转换策略
- **内存管理策略**：跨语言内存所有权划分、RAII 与 GC 的协调、悬挂指针防范

### 高级

- **JIT 与 FFI 的结合**：动态生成 FFI 调用代码（如 Java Panama 项目的 MethodHandle 链路），消除反射开销
- **WebAssembly 跨语言互操作**：WASM 作为通用 FFI 中间层，实现浏览器内的跨语言组件调用
- **FFI 安全性形式化验证**：用类型系统或形式化方法证明 FFI 绑定的安全性，如 Rust 的 `unsafe` 边界验证
- **Project Panama（Java）**：OpenJDK 的下一代 FFI 方案，旨在替代 JNI，提供纯 Java 的外部函数与内存访问 API

## 项目内相关 wiki 交叉引用

- [interface-api-abi-protocol-wiki / ABI 章节](../interface-api-abi-protocol-wiki/03-abi.md) — 接口/API/ABI/协议四概念基础教程，其中 ABI 章节是理解 FFI 底层机制的关键前置知识
- [idl-wiki / IDL 定义与作用章节](../idl-wiki/01-what-is-idl.md) — IDL（接口定义语言）教程，与 FFI 共同构成跨语言互操作的两种互补路径：FFI 手动绑定 vs IDL 代码生成
- [idl-wiki/07-use-cases.md](../idl-wiki/07-use-cases.md) — IDL 应用案例，对比了 FFI 手动绑定与 IDL 代码生成在不同场景下的适用性

---

> **上一章**：[06-comparison.md](06-comparison.md)
> **返回目录**：[00-overview.md](00-overview.md)
> **教程已完成** 🎉