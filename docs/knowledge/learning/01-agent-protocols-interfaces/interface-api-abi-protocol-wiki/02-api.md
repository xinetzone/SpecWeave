---
id: "api-concept"
title: "三、API（应用编程接口）：源码与服务级契约"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/02-api.toml"
source: "spec:create-tech-interface-wiki-tutorial"
category: "learning"
tags: ["api", "rest", "graphql", "soap", "grpc", "web-api", "microservices"]
date: "2026-07-03"
status: "stable"
author: "SpecWeave"
summary: "API的精确定义、REST/GraphQL/SOAP/gRPC类型对比、核心特征、应用场景与主流案例"
---

# API（应用编程接口）：源码与服务级契约

## 精确定义

### Application Programming Interface

API（Application Programming Interface，应用编程接口）是软件系统之间交互的**定义明确的编程契约**。它规定了软件组件如何相互调用、传递数据、返回结果以及处理错误。API 隐藏了内部实现细节，仅暴露标准化的交互方式，使不同系统、不同语言编写的模块能够无缝协作。

### API 与 Interface 的层次关系

Interface 是**语言级**的行为抽象概念，通常局限于单一编程语言的类型系统内部；而 API 是更广泛的**跨模块/跨进程/跨网络**编程契约，涵盖范围包括：

- **库 API**：编程语言标准库、第三方库暴露的函数/类/方法接口
- **服务 API**：分布式系统中微服务间的远程调用接口
- **操作系统 API**：操作系统内核向用户态程序提供的系统调用接口（如 POSIX API、Win32 API）
- **Web API**：基于 HTTP 协议的网络服务接口

简单来说：Interface 是语言内部的契约，API 是跨越边界的契约。

## API 类型对比

| 类型 | 传输协议 | 数据格式 | 核心特点 | 适用场景 |
|------|---------|---------|---------|---------|
| **REST API** | HTTP/HTTPS | JSON/XML | 资源导向、无状态、CRUD 操作、统一接口 | Web 服务、公开 API、前后端分离 |
| **GraphQL** | HTTP/HTTPS | JSON | 查询语言、按需获取、单端点、强类型 Schema | 复杂数据查询、BFF 层、移动端 |
| **SOAP** | HTTP/SMTP/TCP | XML | WS-* 标准、企业级、高安全性、ACID 事务 | 金融、电信、企业级系统集成 |
| **gRPC** | HTTP/2 | Protobuf | 高性能、双向流、代码生成、多语言支持 | 微服务通信、高性能 RPC、服务网格 |
| **库 API** | 进程内调用 | 语言原生类型 | 直接函数调用、无网络开销、同步执行 | SDK、标准库、框架扩展 |

### 1. REST API

REST（Representational State Transfer，表述性状态转移）是目前最主流的 Web API 设计风格。它以资源为核心，使用 HTTP 方法（GET/POST/PUT/DELETE）映射 CRUD 操作，具有无状态、可缓存、统一接口等特性。

### 2. GraphQL

GraphQL 是 Facebook 开源的 API 查询语言。客户端可以精确指定需要的数据结构，单次请求获取多个资源，避免 REST 常见的"过度获取"或"多次请求"问题。使用强类型 Schema 定义数据模型，支持内省。

### 3. SOAP

SOAP（Simple Object Access Protocol）是 W3C 推荐的 XML 协议标准。它内置 WS-Security、WS-AtomicTransaction 等企业级规范，支持事务、安全、可靠性等高级特性，但报文冗余度高、性能较低。

### 4. gRPC

gRPC 是 Google 开源的高性能 RPC 框架，基于 HTTP/2 多路复用和 Protocol Buffers 二进制序列化，支持双向流式通信、自动代码生成，性能远超传统 REST/JSON，是云原生微服务通信的首选方案。

### 5. 库 API

库 API 是进程内的函数调用接口，如 Python 标准库 `os` 模块、React Hooks `useState`、Java JDBC 接口等。这是最直接、最高效的 API 形式，调用方与被调用方运行在同一进程地址空间。

## 核心特征

### 调用方式

- **同步调用**：调用方阻塞等待响应，适用于简单请求-响应场景
- **异步调用**：调用方不阻塞，通过回调/Future/Promise 获取结果，适用于高并发场景
- **消息队列**：通过 MQ（Kafka/RabbitMQ）解耦，异步可靠，适用于事件驱动架构

### 数据格式

- **JSON**：轻量级、人类可读、Web 标准，REST API 首选
- **XML**：可扩展、支持 Schema 验证，SOAP 和遗留系统使用
- **Protobuf**：二进制、体积小、序列化快，gRPC 标准格式
- **MessagePack**：二进制 JSON，比 JSON 更小更快

### 传输协议

- **HTTP/HTTPS**：Web 标准，防火墙友好，REST/GraphQL/SOAP 均支持
- **TCP**：底层传输协议，自定义 RPC 场景使用
- **WebSocket**：全双工通信，实时推送、聊天室、游戏等场景

### 版本控制

- **URI 版本**：`/api/v1/users`、`/api/v2/users`，简单直观
- **Header 版本**：`Accept: application/vnd.myapi.v2+json`，URI 保持整洁
- **语义化版本**：遵循 SemVer（MAJOR.MINOR.PATCH），库 API 常用

### 认证授权

- **API Key**：简单密钥，适合服务端到服务端调用
- **OAuth2**：授权框架，支持第三方应用授权登录
- **JWT**：JSON Web Token，无状态、自包含，适合分布式系统

## 应用场景

- **系统集成**：企业内部 ERP、CRM、OA 等系统互联
- **微服务通信**：分布式架构下服务间的远程调用
- **第三方开放平台**：构建开发者生态，如微信开放平台、阿里云 API
- **操作系统调用**：用户态程序通过系统调用 API 访问内核资源
- **SDK 与库调用**：应用开发中使用各类开源库和 SDK

## 主流 API 案例

### 案例 1：GitHub REST API

GitHub 提供了完善的 REST API，是业界设计标杆之一：

```bash
curl -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/users/octocat
```

响应结构：

```json
{
  "login": "octocat",
  "id": 583231,
  "node_id": "MDQ6VXNlcjU4MzIzMQ==",
  "avatar_url": "https://avatars.githubusercontent.com/u/583231?v=4",
  "name": "The Octocat",
  "public_repos": 8,
  "followers": 14218,
  "following": 9,
  "created_at": "2011-01-25T18:44:36Z"
}
```

### 案例 2：Stripe 支付 API

Stripe API 以其优秀的设计著称：

- **幂等性**：通过 `Idempotency-Key` 头保证重试安全
- **错误处理**：标准化错误码和详细错误信息
- **版本控制**：Header 中指定 API 版本，向后兼容性极佳
- **SDK 优先**：官方提供多语言 SDK，封装签名和重试逻辑

```bash
curl https://api.stripe.com/v1/charges \
  -u sk_test_xxx: \
  -d amount=2000 \
  -d currency=usd \
  -d source=tok_visa \
  -H "Idempotency-Key: order_12345"
```

### 案例 3：GitHub GraphQL API

GraphQL 按需获取数据的优势：同样获取 octocat 的登录名和前 3 个仓库名，REST 需要多次请求，GraphQL 一次完成：

```graphql
query {
  user(login: "octocat") {
    login
    name
    repositories(first: 3) {
      edges {
        node {
          name
          stargazerCount
        }
      }
    }
  }
}
```

## 代码示例

### JavaScript fetch 调用 REST API

```javascript
async function fetchUser(username) {
  const response = await fetch(`https://api.github.com/users/${username}`, {
    headers: {
      'Accept': 'application/vnd.github.v3+json',
      'User-Agent': 'SpecWeave-App'
    }
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
}

fetchUser('octocat').then(user => {
  console.log(`用户名: ${user.login}, 公开仓库: ${user.public_repos}`);
});
```

---

**上一章**：[01 - Interface：语言级行为抽象](01-interface.md)  
**下一章**：[03 - ABI：二进制兼容约定](03-abi.md)
