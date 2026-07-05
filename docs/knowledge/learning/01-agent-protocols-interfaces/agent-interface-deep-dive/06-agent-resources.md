---
id: "agent-resources-chapter"
title: "参考资料与学习路径"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/01-agent-protocols-interfaces/agent-interface-deep-dive/06-agent-resources.toml"
source: "spec:agent-interface-deep-dive"
category: "learning"
tags: ["agent", "resources", "reference", "glossary", "learning-path"]
date: "2026-07-03"
status: "stable"
author: "SpecWeave"
summary: "Agent术语表、官方规范参考链接、三条进阶学习路径（Tool开发者/协议设计者/跨语言Runtime）"
---

# 参考资料与学习路径

## Agent术语表

| 术语 | 定义 |
|------|------|
| **Tool** | Agent可调用的外部能力单元，通过Interface（Schema）声明输入输出 |
| **Skill** | 可复用的Agent能力包，包含描述文件和实现逻辑 |
| **MCP Server** | 实现MCP协议、暴露Tool/Resource/Prompt的服务进程 |
| **MCP Client** | 连接MCP Server、发起JSON-RPC调用的客户端（通常是Agent Runtime） |
| **JSON-RPC 2.0** | Agent生态的API标准格式，轻量的远程过程调用协议 |
| **Agent Card** | A2A协议中Agent的能力声明文件，类似"Agent名片" |
| **Task** | A2A协议的核心单元，代表一次Agent间委派的工作单元 |
| **SSE** | Server-Sent Events，HTTP长连接技术，用于Agent流式响应 |
| **STDIO Transport** | MCP通过标准输入输出管道通信的本地传输方式 |
| **Tool Schema** | 即MCP Tool的`inputSchema`，用JSON Schema定义Tool参数契约 |
| **Agent Runtime** | 执行Agent逻辑、管理LLM调用、调度Tool的运行时环境 |
| **Tool Call** | LLM决定调用某个Tool并生成参数的动作（Function Calling） |
| **Function Calling** | LLM原生能力，根据Tool Schema生成结构化调用参数 |
| **ACP** | Agent Communication Protocol，本地应用内Agent间通信协议 |
| **A2A** | Agent-to-Agent Protocol，跨Agent协作的开放协议 |
| **ANP** | Agent Network Protocol，去中心化Agent网络协议（基于DID） |
| **JSON Schema** | 声明JSON数据结构的标准，Agent Interface的核心载体 |

## 官方规范参考

### MCP（Model Context Protocol）
- MCP官方规范：https://spec.modelcontextprotocol.io/
- MCP TypeScript SDK：https://github.com/modelcontextprotocol/typescript-sdk
- MCP Python SDK：https://github.com/modelcontextprotocol/python-sdk

### A2A（Agent-to-Agent）
- A2A官方文档：https://google.github.io/A2A/
- A2A规范GitHub：https://github.com/google/A2A

### 基础标准
- JSON-RPC 2.0规范：https://www.jsonrpc.org/specification
- JSON Schema规范：https://json-schema.org/specification
- JSON (RFC 8259)：https://datatracker.ietf.org/doc/html/rfc8259

## 进阶学习路径

### 路径1：Tool开发者路线
适合想要给Agent开发工具/插件的开发者：

1. **第一阶段：Interface理解**
   - 学习JSON Schema核心概念（类型、必填、描述、枚举）
   - 学习Zod（TypeScript）或Pydantic（Python）做Schema定义
   - 理解为什么Tool description对LLM正确性至关重要

2. **第二阶段：MCP Server开发**
   - 跟着MCP官方Quickstart构建第一个Server
   - 掌握Tool定义模式（name + description + inputSchema）
   - 学习Resource和Prompt两种扩展能力

3. **第三阶段：调试与优化**
   - 使用MCP Inspector调试Tool调用
   - 学习如何写好description减少LLM调用错误
   - 理解STDIO vs HTTP传输选择

### 路径2：协议设计者路线
适合想要深入Agent通信协议、设计Agent间协作方案的开发者：

1. **第一阶段：API与消息格式**
   - 深入理解JSON-RPC 2.0（请求/响应/通知/批量/错误码）
   - 研究MCP的生命周期（initialize → 操作 → shutdown）
   - 学习SSE流式响应设计模式

2. **第二阶段：协议分层与状态机**
   - 对比MCP/A2A/ACP/ANP的协议定位
   - 学习A2A Task生命周期状态机设计
   - 研究能力协商（capability negotiation）模式

3. **第三阶段：架构设计**
   - 设计多Agent协作协议
   - 学习错误恢复与重试机制设计
   - 研究安全认证与授权模型

### 路径3：跨语言Agent Runtime路线
适合想要开发Agent Runtime、MCP SDK、高性能Agent基础设施的开发者：

1. **第一阶段：ABI与序列化**
   - 深入理解JSON序列化在各语言中的类型映射
   - 对比JSON vs MessagePack vs Protobuf在Agent场景的trade-off
   - 学习STDIO管道和HTTP的底层通信机制

2. **第二阶段：SDK开发**
   - 从0实现一个简单的MCP Client/Server SDK
   - 处理JSON-RPC请求路由、响应匹配
   - 实现传输层抽象（可插拔STDIO/HTTP/SSE）

3. **第三阶段：前沿方向**
   - 研究WebAssembly作为Agent插件ABI边界
   - 探索WASI标准化的Agent沙箱
   - 参与ANP等去中心化协议设计

## 相关Wiki参考

| 主题 | 链接 |
|------|------|
| 通用Interface/API/ABI/Protocol基础概念 | [interface-api-abi-protocol-wiki](../interface-api-abi-protocol-wiki/00-overview.md) |
| Agent通信协议详解（MCP/A2A/ACP/ANP） | [agent-communication-protocols](../agent-communication-protocols/00-overview.md) |
| Agent Skills开发指南 | agent-skills-wiki（请参考知识库索引） |

## 章节导航

| 章节 | 链接 |
|------|------|
| 总览 | [00 - 总览](00-overview.md) |
| 上一章 | [05 - 对比分析](05-agent-comparison.md) |
| 对比分析 | [05 - 对比分析](05-agent-comparison.md) |
| 通用概念参考 | [通用Wiki总览](../interface-api-abi-protocol-wiki/00-overview.md) |
| 协议详解 | [agent-communication-protocols](../agent-communication-protocols/00-overview.md) |

---

**上一章**：[05 - 对比分析：Agent四层技术栈协同](05-agent-comparison.md) | **回到总览**：[00 - 总览](00-overview.md)
