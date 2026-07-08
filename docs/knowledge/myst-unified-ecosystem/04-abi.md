---
version: 1.0
id: myst-unified-ecosystem-abi
title: "04、ABI：应用程序二进制接口"
category: knowledge
source: "spec:myst-unified-interface-ecosystem"
x-toml-ref: "../../../.meta/toml/docs/knowledge/myst-unified-ecosystem/04-abi.toml"
---
# 04、ABI：应用程序二进制接口

## 概念模板

| 字段 | 内容 |
|------|------|
| **名称** | ABI（Application Binary Interface） |
| **分类层** | 设计抽象层 (Design) |
| **核心定义** | 二进制级的兼容性约定，定义"如何链接" |
| **解决的问题** | 确保不同编译器/语言/运行时编译的模块能够互相调用 |
| **关键属性** | `data_format`、`encoding`、`serialization`、`calling_convention`、`transport` |
| **关系** | constrains → Implementation；depends-on → 无；described-by → IDL；carried-by → MDI |
| **MyST Directive** | `{abi} format="..." encoding="..."` |
| **MDI 示例** | `{abi} format="JSON" encoding="UTF-8"` 包裹序列化格式与传输约定 |

## 核心定义

ABI 是连接"设计抽象"到"具体实现"的**兼容性约束层**。传统 ABI 定义寄存器使用、栈布局、字节序、内存对齐、名称修饰等底层约定；Agent 生态中的 ABI 则是**标准化的序列化格式与传输层抽象**，确保不同语言实现的 Agent 组件能在进程边界之外安全通信。

ABI 在概念体系中承担"约束"角色：它不依赖任何其他概念，但它约束 Implementation（constrains → Implementation）。这意味着任何 Implementation 必须遵守其声明的 ABI 约定，否则无法与其他模块互操作。

## ABI 在传统软件 vs Agent 生态中的体现

### 传统软件 ABI

| 维度 | 传统系统 ABI（C/C++） | Agent ABI（JSON + STDIO/HTTP） |
|------|---------------------|----------------------------|
| **边界位置** | 同一进程内 | 进程/机器边界 |
| **兼容单位** | 内存布局、寄存器、调用栈 | JSON 文本格式 |
| **内存共享** | 共享地址空间 | 完全隔离 |
| **错误影响** | ABI 违规可导致段错误 | 最多 JSON 解析失败 |
| **语言绑定** | 需要为每种语言写绑定 | 任何语言都能解析 JSON |
| **版本演化** | 极其困难（ABI 破裂即不兼容） | 容易（JSON 字段可增量添加） |

### Agent ABI 的核心选择

Agent 生态不试图解决传统 ABI 的兼容性问题，而是**绕过它们**。MCP 的设计选择是：所有通信都走 JSON + STDIO/HTTP，不同语言的 Server 和 Client 是独立进程，只通过标准输入输出或 HTTP 交换 JSON 文本，完全不涉及进程内的函数调用和内存共享。

这本质上是把"ABI 兼容问题"转化为"JSON 序列化/反序列化问题"——而 JSON 解析在所有主流语言中都有成熟稳定的实现。

## JSON/STDIO/HTTP 作为 Agent ABI 的选择理由

### 为什么选择 JSON 作为数据格式

| 理由 | 说明 |
|------|------|
| **语言无关** | 所有主流语言都有成熟的 JSON 解析器，无需额外绑定 |
| **人类可读** | 调试友好，开发者可以直接阅读通信内容 |
| **生态成熟** | JSON Schema 配套完善，支持类型校验和自动生成 |
| **类型最小公分母** | `string`、`number`、`boolean`、`null`、`array`、`object` 六种类型足够表达 Agent Tool 调用的所有参数 |
| **安全隔离** | JSON 解析失败不会导致进程崩溃，错误可控 |

### 为什么选择 STDIO/HTTP 作为传输层

| 传输方式 | 选择理由 | 适用场景 |
|---------|---------|---------|
| **STDIO** | 零网络开销，天然进程隔离，无需端口管理 | 本地 MCP Server（IDE 插件中的工具） |
| **HTTP** | 防火墙友好，生态成熟，支持负载均衡和反向代理 | 远程 MCP Server、跨网络调用 |
| **SSE** | 原生服务器推送，适配 LLM token-by-token 流式输出 | 流式响应、A2A 任务进度推送 |

### 跨语言类型映射

JSON 的类型系统足够简单，充当了跨语言的"最小公分母" ABI：

| Python 类型 | JSON 类型 | JavaScript/TypeScript 类型 |
|-----------|---------|--------------------------|
| `int` / `float` | `number` | `number` |
| `str` | `string` | `string` |
| `bool` | `true` / `false` | `boolean` |
| `None` | `null` | `null` |
| `list` / `tuple` | `array` | `Array` |
| `dict` | `object` | `Object` |

## 章节导航

| 章节 | 内容 |
|------|------|
| [00 - 总览](00-overview.md) | 可行性分析、架构图、关系全景 |
| [01 - IDL](01-idl.md) | 接口描述语言：元概念层定义 |
| [02 - Interface](02-interface.md) | 接口：行为契约的抽象声明 |
| [03 - API](03-api.md) | 应用程序编程接口：可调用方法端点 |
| [04 - ABI](04-abi.md) | 应用程序二进制接口：二进制兼容约定（当前章节） |
| [05 - Protocol](05-protocol.md) | 协议：完整通信规则集 |
| [06 - Implementation](06-implementation.md) | 实现：接口/协议的具体编码 |
| [07 - MCP](07-mcp.md) | Model Context Protocol：Agent↔Tool 连接 |
| [08 - ACP](08-acp.md) | Agent Communication Protocol：本地 P2P |
| [09 - A2A](09-a2a.md) | Agent-to-Agent：跨组织协作 |
| [10 - ANP](10-anp.md) | Agent Network Protocol：去中心化网络 |
| [11 - MDI](11-mdi.md) | Markdown Document Interface：载体层 |
| [12 - 关系全景](12-relationships.md) | 7 类关系定义、关系矩阵、交互场景 |

<!-- changelog -->
- 2026-07-04 | spec | 初始创建：ABI 二进制兼容约定定义与 Agent 生态映射