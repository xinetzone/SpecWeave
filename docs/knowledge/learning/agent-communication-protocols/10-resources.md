---
version: "1.0"
source: "../agent-communication-protocols-wiki.md#10-资源与参考链接"
id: "resources"
title: "10、资源与参考链接"
---
# 10、资源与参考链接

## 10.1 说明

本章按类别整理了Agent通信协议学习和开发所需的官方资源、SDK、论文、工具、标准等参考资料。所有链接均为官方渠道或权威来源，建议读者按需查阅。

阅读建议：
- 初学者建议先从**官方规范与文档**入手
- 开发者重点关注**GitHub仓库与SDK**
- 深入研究者可参考**学术论文**
- 实际开发时使用**工具与调试器**提升效率
- 跨协议对比时查阅**相关标准**理解底层技术

---

## 10.2 官方规范与文档

### MCP（模型上下文协议）

- [MCP官方网站](https://modelcontextprotocol.io) - Anthropic发起的MCP协议官方主页，包含入门介绍、文档导航和最新动态
- [MCP规范文档](https://spec.modelcontextprotocol.io) - MCP协议的正式技术规范，定义了所有消息格式、传输方式和原语语义
- [MCP官方入门指南](https://modelcontextprotocol.io/introduction) - 面向新手的MCP快速上手指南，包含核心概念讲解和简单示例

### ACP（Agent通信协议）

- [ACP官方网站](https://agentcommunicationprotocol.dev) - IBM/BeeAI发起的ACP协议官方网站，介绍协议设计理念和核心特性
- [ACP GitHub仓库](https://github.com/i-am-bee/acp) - ACP协议的规范文档、设计说明和讨论区
- [BeeAI框架](https://github.com/i-am-bee/beeai-framework) - BeeAI官方Agent框架，内置ACP协议支持，可参考实现

### A2A（Agent间通信协议）

- [A2A官方网站](https://a2a-protocol.org) - Google发起的A2A协议官方主页，介绍协议愿景和厂商支持情况
- [A2A规范仓库](https://github.com/a2aproject/A2A) - A2A协议规范、SDK和示例代码的官方GitHub组织
- [Google开发者博客](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/) - Google官方发布的A2A协议介绍文章，阐述设计背景和目标

### ANP（Agent网络协议）

ANP目前暂无统一官方规范，主要基于以下W3C标准构建：
- [W3C DID核心规范](https://www.w3.org/TR/did-core/) - 去中心化标识符标准，ANP自主身份的基础
- [JSON-LD官方网站](https://json-ld.org/) - 链接数据格式，ANP语义互操作的核心技术

---

## 10.3 GitHub仓库与SDK

### MCP SDK与工具

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - Python官方SDK，快速构建MCP Server和Client
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) - TypeScript/JavaScript官方SDK，Node.js和浏览器环境支持
- [MCP官方Servers集合](https://github.com/modelcontextprotocol/servers) - 官方维护的MCP Server参考实现集合，包含文件系统、GitHub、数据库等常用Server

### ACP SDK与工具

- [ACP Python SDK](https://github.com/i-am-bee/acp-sdk-python) - Python SDK，支持ACP Agent开发
- [ACP TypeScript SDK](https://github.com/i-am-bee/acp-sdk-ts) - TypeScript SDK，Node.js环境ACP支持
- 注：ACP设计为零SDK依赖，也可直接使用HTTP/OpenAPI原生集成

### A2A SDK与工具

- [A2A官方仓库](https://github.com/a2aproject/A2A) - A2A规范、SDK和示例的主仓库
- 支持语言：Python、TypeScript/JavaScript、Java、Kotlin、Swift等多语言SDK（详见官方仓库）

---

## 10.4 学术论文

以下论文从学术角度分析Agent通信协议的设计和现状：

- [arXiv:2505.02279](https://arxiv.org/abs/2505.02279) - 《How Agents Talk: A Survey on Inter-Agent Communication Protocols and Languages》，Agent间通信协议与语言的综述论文，系统梳理了各类协议
- [arXiv:2505.03864](https://arxiv.org/abs/2505.03864) - 《Demystifying MCP and A2A for Multi-Agentic AI Workflows》，专门解析MCP和A2A在多Agent工作流中的应用与对比
- [arXiv:2503.16417](https://arxiv.org/abs/2503.16417) - ACP相关学术论文（如可获取），介绍本地优先Agent通信的设计思路

建议在arXiv搜索关键词：`agent communication protocol`、`multi-agent system`、`MCP protocol`、`A2A protocol`获取最新研究。

---

## 10.5 工具与调试器

### 协议调试工具

- **MCP Inspector** - MCP官方调试工具，可连接MCP Server、查看工具列表、测试工具调用、监控消息流，是MCP开发必备工具（随MCP SDK提供）
- **A2A Inspector** - A2A调试工具，用于测试A2A Agent发现、Task提交、状态跟踪、SSE流接收等功能（详见A2A官方仓库）
- **Claude Desktop / Claude Code** - Anthropic官方MCP Client实现，可作为MCP Server集成测试的参考客户端

### 通用开发工具

- 网络抓包工具：Wireshark、Charles、mitmproxy - 调试HTTP/HTTPS通信
- JSON-RPC调试器：Postman、curl - 手动构造和发送JSON-RPC请求
- mDNS浏览器：Bonjour Browser、dns-sd - 发现局域网内ACP Agent服务

---

## 10.6 文章与解读

由于Agent通信协议领域发展迅速，建议通过以下渠道获取最新中文解读和实践经验：

### 推荐资源类别

- **中文社区文章**：知乎、掘金、CSDN、微信公众号等平台的技术解读文章
- **厂商技术博客**：Anthropic、Google、IBM、字节跳动、阿里、腾讯等厂商的技术博客
- **GitHub讨论区**：各协议仓库的Issues和Discussions区，有大量实践问题和解决方案
- **技术会议分享**：AI Agent相关会议和Meetup的演讲视频和 slides

### 推荐搜索关键词

- 中文：`MCP协议详解`、`A2A vs MCP`、`ACP agent protocol`、`Agent通信协议对比`、`MCP开发教程`、`A2A接入指南`
- 英文：`Model Context Protocol tutorial`、`Agent-to-Agent protocol`、`BeeAI ACP guide`、`MCP vs A2A comparison`

> 提示：技术文章时效性强，建议优先查看3个月内发布的内容，以适配协议最新版本。

---

## 10.7 相关标准

四大Agent通信协议均建立在成熟的互联网标准之上，理解这些底层标准有助于深入掌握协议设计：

### 基础通信协议

- [JSON-RPC 2.0规范](https://www.jsonrpc.org/specification) - 轻量级远程过程调用协议，MCP和A2A的消息格式基础
- [Server-Sent Events规范](https://html.spec.whatwg.org/multipage/server-sent-events.html) - HTML标准定义的服务器推送技术，MCP和A2A流式通信的基础
- [OAuth 2.1草案](https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/) - 最新授权框架标准，MCP和A2A安全认证的基础

### 语义与身份标准

- [W3C DID Core规范](https://www.w3.org/TR/did-core/) - 去中心化标识符标准，ANP自主身份的核心
- [JSON-LD 1.1规范](https://www.w3.org/TR/json-ld11/) - JSON链接数据标准，ANP语义互操作的基础
- [Verifiable Credentials规范](https://www.w3.org/TR/vc-data-model/) - 可验证凭证标准，ANP信任体系的组成部分

### API描述标准

- [OpenAPI 3.x规范](https://spec.openapis.org/oas/latest.html) - REST API描述标准，ACP接口定义和零SDK集成的基础

---

## 10.8 章节导航

| 导航 | 链接 |
|------|------|
| 返回总览 | [Agent通信协议总览](../agent-communication-protocols-wiki.md) |
| 上一章 | [09、术语表](./09-glossary.md) |
| **下一章** | [11、快速参考](./11-quick-reference.md) |
