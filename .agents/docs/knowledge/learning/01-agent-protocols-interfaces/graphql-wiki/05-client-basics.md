---
id: "graphql-wiki-client-basics"
title: "GraphQL 客户端基础"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/01-agent-protocols-interfaces/graphql-wiki/05-client-basics.toml"
source: "spec:create-graphql-wiki-tutorial"
category: "learning"
tags: ["graphql", "api", "client", "apollo-client", "relay", "urql", "fetch", "curl", "graphiql", "caching"]
date: "2026-08-05"
status: "stable"
author: "SpecWeave"
summary: "GraphQL 客户端基础完整指南，涵盖客户端库对比、原生 HTTP 请求方法、请求头设置、GraphiQL IDE 使用、curl 和 fetch 示例，以及客户端缓存与本地状态管理基础。"
---
# 第 5 章：GraphQL 客户端基础

本章将介绍 GraphQL 客户端开发的基础知识，包括为什么需要专用客户端库、主流客户端库对比、如何使用原生 HTTP 发送 GraphQL 请求、交互式开发工具的使用，以及客户端缓存和本地状态管理的核心概念。掌握这些知识是构建 GraphQL 前端应用的第一步。

## GraphQL 客户端概述

在开始使用 GraphQL 构建前端应用时，首先需要理解：为什么需要专门的 GraphQL 客户端库，而不是直接使用原生的 `fetch` 或 `axios` 发送 HTTP 请求？

### 原生 fetch/axios 的局限

使用原生 HTTP 客户端（如浏览器内置的 `fetch` API 或 `axios` 库）虽然可以发送 GraphQL 请求，但在实际应用开发中会面临诸多问题：

1. **手动模板处理**：需要手动拼接查询字符串、处理变量传递，容易出错
2. **无缓存机制**：每次请求都需要重新获取数据，无法自动复用已获取的数据，导致重复网络请求
3. **手动更新 UI**：需要手动管理加载状态、错误状态，以及数据变更后更新 UI 的逻辑
4. **无乐观更新**：变更（Mutation）后需要等待服务器响应才能更新 UI，用户体验差
5. **状态管理分散**：数据获取逻辑分散在各个组件中，难以统一管理
6. **无类型安全**：需要手动定义 TypeScript 类型，无法与 Schema 自动同步

### 专用客户端库的优势

**GraphQL 客户端库**是专门为 GraphQL 设计的数据层工具，提供了一系列高级功能，解决了原生 HTTP 客户端的痛点：

| 功能 | 说明 |
|---|---|
| **声明式数据获取** | 通过组件与数据的绑定关系自动管理查询的发送与更新 |
| **规范化缓存** | 自动缓存查询结果，相同数据不重复请求，数据更新自动通知所有使用该数据的组件 |
| **加载/错误状态管理** | 自动追踪请求的加载状态和错误状态，简化 UI 状态处理 |
| **乐观 UI 更新** | Mutation 发送后立即更新界面，服务器响应后再确认或回滚，提升感知性能 |
| **分页支持** | 内置游标分页、偏移分页等多种分页模式的支持 |
| **本地状态管理** | 将远程数据与本地状态统一管理，无需额外引入 Redux/MobX 等状态管理库 |
| **类型安全** | 与 Schema 集成，自动生成 TypeScript 类型定义，提供编译时类型检查 |
| **开发工具集成** | 与浏览器 DevTools 集成，支持缓存查看、查询重放等调试功能 |

---

## 常用 GraphQL 客户端介绍

目前生态中有多种成熟的 GraphQL 客户端库，它们各有特点，适用于不同的场景和项目规模。

### Apollo Client

**Apollo Client** 是由 Apollo GraphQL 团队开发维护的最流行的 GraphQL 客户端，功能全面且社区活跃。

**核心特点**：
- 功能最全面，覆盖缓存、状态管理、分页、乐观更新、错误处理等所有场景
- 支持 React、Vue、Angular、Svelte 等所有主流前端框架，也支持原生 JavaScript
- 规范化缓存（Normalized Cache）实现成熟，自动数据去重和更新
- 支持本地状态管理（`@client` 指令），可完全替代 Redux 等状态管理库
- 丰富的生态系统：Apollo DevTools、Apollo Studio、代码生成工具等
- 学习曲线相对平缓，文档详尽，适合各种规模的项目

**适用场景**：大多数 GraphQL 项目的首选，特别是中大型应用、需要丰富功能和良好生态支持的项目。

### Relay

**Relay** 是 Facebook（Meta）官方开发的 GraphQL 客户端，与 React 深度集成，专为高性能、大规模应用设计。

**核心特点**：
- 由 GraphQL 的发明者 Facebook 开发，与 GraphQL 规范和 React 协同演进
- 强调性能和可扩展性，内置编译期优化（Relay Compiler），自动优化查询
- 严格的 colocation 原则：数据需求与组件定义放在同一文件，组件自给自足
- 强大的分页支持（`@connection` 指令）和数据预取能力
- 内置数据掩码（Data Masking），组件只能访问自己声明的数据，防止数据隐式依赖
- 学习曲线陡峭，概念多（Fragment、Container、Refetch Container 等），文档相对较难理解

**适用场景**：超大规模 React 应用（如 Facebook、Instagram 等），团队对性能要求极高且愿意投入学习成本的项目。

### urql

**urql**（发音为 "urkel"）是由 Formidable 团队开发的轻量级、高度可定制的 GraphQL 客户端，强调简洁和灵活性。

**核心特点**：
- 体积极小（核心库约 8KB gzipped），远小于 Apollo Client
- 插件化架构，所有高级功能（缓存、分页、重试等）通过 exchanges（插件）实现
- 默认使用文档缓存（Document Caching），简单高效；也可通过 `@urql/exchange-graphcache` 启用规范化缓存
- API 设计简洁，学习曲线低，容易上手
- 支持 React、Preact、Vue、Svelte 等框架
- 高度可定制，可以根据项目需求替换或扩展任何部分

**适用场景**：小型项目、对包体积敏感的应用、希望保持架构简洁灵活的团队、需要高度定制化数据层的场景。

### 客户端库对比总结

| 维度 | Apollo Client | Relay | urql |
|---|---|---|---|
| **包体积** | 较大（~35KB gzipped） | 中等（~25KB gzipped） | 极小（~8KB gzipped） |
| **学习曲线** | 平缓 | 陡峭 | 平缓 |
| **缓存策略** | 规范化缓存（默认） | 规范化缓存 | 文档缓存（默认）/规范化缓存（可选） |
| **框架支持** | 全框架支持 | 仅 React | 全框架支持 |
| **本地状态管理** | 内置支持 | 有限支持 | 插件支持 |
| **生态系统** | 最丰富 | Facebook 官方生态 | 轻量插件生态 |
| **定制灵活性** | 中等 | 低（约定大于配置） | 高（插件化架构） |
| **推荐场景** | 大多数项目 | 大规模 React 应用 | 轻量应用、高度定制场景 |

---

## 使用原生 HTTP 发送 GraphQL 请求

虽然专用客户端库有诸多优势，但理解如何使用原生 HTTP 发送 GraphQL 请求是掌握 GraphQL 通信协议的基础，在调试、脚本编写、简单场景中也非常有用。

### GraphQL 的 HTTP 协议约定

GraphQL 规范本身不绑定特定传输协议，但绝大多数 GraphQL 服务通过 HTTP 提供服务，并且遵循以下约定：

- 通常使用单个端点（如 `/graphql`、`/api/graphql`）处理所有 GraphQL 请求
- 支持 POST 请求（用于所有操作），多数实现也支持 GET 请求（仅用于查询）
- 请求体和响应体都是 JSON 格式

### POST 请求格式（推荐）

POST 是 GraphQL 请求的标准方式，支持查询（Query）、变更（Mutation）和订阅（Subscription，需结合 WebSocket）。

POST 请求的 JSON 请求体包含三个字段：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `query` | String | ✅ 是 | GraphQL 查询或变更的字符串 |
| `variables` | Object | ❌ 否 | 变量对象，包含查询中使用的变量值 |
| `operationName` | String | ❌ 否 | 操作名称，当查询文档包含多个操作时指定要执行哪个 |

**请求体示例**：

```json
{
  "query": "query GetHero($episode: Episode) { hero(episode: $episode) { name friends { name } } }",
  "variables": {
    "episode": "JEDI"
  },
  "operationName": "GetHero"
}
```

为了可读性，`query` 字段也可以使用格式化的多行字符串：

```json
{
  "query": "query GetHero($episode: Episode) {\n  hero(episode: $episode) {\n    name\n    friends {\n      name\n    }\n  }\n}",
  "variables": {
    "episode": "JEDI"
  }
}
```

### GET 请求用于查询

对于**幂等**（Idempotent，多次执行产生相同效果且无副作用）的查询操作，可以使用 GET 请求，将参数作为 URL 查询参数传递。这可以利用 HTTP 缓存机制（浏览器缓存、CDN 缓存）提升性能。

GET 请求参数与 POST 请求体字段相同，都作为 URL 查询参数传递：

| URL 参数 | 说明 |
|---|---|
| `query` | GraphQL 查询字符串（需要 URL 编码） |
| `variables` | 变量对象的 JSON 字符串（需要 URL 编码） |
| `operationName` | 操作名称 |

**GET 请求 URL 示例**：

```
/graphql?query=query%20GetHero(%24episode%3A%20Episode)%20%7B%20hero(episode%3A%20%24episode)%20%7B%20name%20%7D%20%7D&variables=%7B%22episode%22%3A%22JEDI%22%7D&operationName=GetHero
```

**注意事项**：
- GET 请求仅适用于 Query 操作，绝对不能用于 Mutation（违反 HTTP 语义，且可能被缓存导致重复执行）
- URL 有长度限制，复杂查询可能导致 URL 过长，此时应使用 POST
- 需要对参数进行正确的 URL 编码

---

## 请求头设置

发送 GraphQL HTTP 请求时，需要设置合适的 HTTP 请求头（Request Headers）来告知服务器如何处理请求。

### Content-Type（内容类型）

`Content-Type` 请求头是**必须设置**的，它告知服务器请求体的媒体类型。

对于标准的 JSON 请求体：

```
Content-Type: application/json
```

某些 GraphQL 实现还支持另一种格式：`application/graphql`。使用这种 Content-Type 时，可以直接将查询字符串作为请求体，无需包装成 JSON 对象：

```
Content-Type: application/graphql
```

请求体直接是查询字符串：
```graphql
query GetHero { hero { name } }
```

这种方式不支持传递变量和操作名称，因此很少使用，推荐始终使用 `application/json`。

### Authorization（授权）

当 GraphQL API 需要身份验证时，通常通过 `Authorization` 请求头传递凭证。最常见的是 **Bearer Token**（Bearer 令牌，一种 OAuth 2.0 认证方案，令牌以 "Bearer " 前缀开头）方式：

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

其他常见的认证方式：

| 认证方式 | 请求头示例 | 说明 |
|---|---|---|
| API Key | `X-API-Key: your-api-key-here` | 自定义请求头传递 API 密钥 |
| Basic Auth | `Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=` | Basic 认证，用户名密码 Base64 编码 |

### 其他常用请求头

| 请求头 | 示例值 | 说明 |
|---|---|---|
| `Accept` | `application/json` | 告知客户端期望接收 JSON 响应 |
| `X-Request-ID` | `req-abc-123` | 请求追踪 ID，用于日志和调试 |
| `Apollo-Require-Preflight` | `true` | Apollo 特定头，用于处理 CORS 预检请求 |

---

## GraphiQL / GraphQL Playground 交互式 IDE

**GraphiQL**（发音为 "graphical"）是 GraphQL 官方提供的浏览器内交互式 IDE（集成开发环境），是学习、调试和探索 GraphQL API 的必备工具。

### GraphiQL 的核心功能

GraphiQL 通常在开发环境中随 GraphQL 服务一起提供（如访问 `/graphql` 端点），提供以下功能：

1. **语法高亮编辑器**：支持 GraphQL 查询语法高亮、自动缩进、括号匹配
2. **自动补全**：通过内省查询自动获取 Schema，在输入时提供字段名、参数、类型的自动补全
3. **实时文档**：右侧内置文档浏览器，点击即可查看类型、字段、参数的描述信息，无需外部文档
4. **查询历史**：自动保存执行过的查询，方便快速重复执行
5. **变量编辑器**：单独的面板用于编辑变量，支持 JSON 格式验证
6. **HTTP 请求头设置**：可以设置 Authorization 等自定义请求头
7. **响应格式化**：返回的 JSON 响应自动格式化高亮，支持折叠展开
8. **错误提示**：查询语法错误或验证错误直接在编辑器中标记

### GraphQL Playground

**GraphQL Playground** 是另一个流行的 GraphQL IDE，由 Prisma 团队开发，基于 GraphiQL 增强，功能更丰富：

- 支持多标签页，可以同时编辑多个查询
- 内置查询历史收藏功能
- 支持配置多个 GraphQL 端点，快速切换
- 更美观的深色主题界面
- 支持订阅（Subscription）的 WebSocket 调试
- 可下载为桌面应用使用

现在许多服务端框架默认使用 GraphQL Playground 或其继任者 **Apollo Sandbox**。

### 使用场景

GraphiQL/Playground 在开发流程中有多种用途：

- **探索 API**：新接触一个 GraphQL API 时，通过文档浏览器快速了解可用的查询、类型和字段
- **调试查询**：在写入代码前先在 IDE 中调试查询语句，确保查询正确、返回预期数据
- **测试变更**：测试 Mutation 操作，验证参数和返回结果
- **性能分析**：配合 tracing 扩展查看各字段的执行时间，定位性能瓶颈
- **复现问题**：报告 Bug 时附上 GraphiQL 中可复现的查询，方便他人定位问题

> **生产环境注意**：默认情况下 GraphiQL/Playground 只应在开发环境启用，生产环境应禁用以防止 Schema 泄露和未授权访问。如果需要在生产环境提供给内部团队使用，应加上身份验证保护。

---

## curl 示例发送 GraphQL 请求

**curl** 是命令行下发送 HTTP 请求的常用工具，非常适合快速测试 GraphQL API 或在脚本中使用。

### 基础 curl 示例：简单查询

以下示例向 Star Wars GraphQL API 发送一个简单的英雄查询：

```bash
curl -X POST https://swapi-graphql.netlify.app/.netlify/functions/index \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ hero { name height } }"
  }'
```

**参数说明**：
- `-X POST`：指定使用 POST 方法
- `-H`：添加请求头，这里设置 Content-Type 为 application/json
- `-d`：指定请求体数据

### curl 示例：带变量的查询

使用变量可以使查询更具复用性：

```bash
curl -X POST https://swapi-graphql.netlify.app/.netlify/functions/index \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query GetHero($episode: Episode) { hero(episode: $episode) { name appearsIn } }",
    "variables": {
      "episode": "EMPIRE"
    }
  }'
```

### curl 示例：带 Authorization 头

需要认证的接口，添加 Authorization 头：

```bash
curl -X POST https://api.example.com/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "query": "query Me { me { id name email } }"
  }'
```

### curl 示例：格式化输出

默认 curl 输出的 JSON 是压缩的，可以通过管道传给 `jq` 工具格式化输出（需要安装 jq）：

```bash
curl -X POST https://swapi-graphql.netlify.app/.netlify/functions/index \
  -H "Content-Type: application/json" \
  -d '{ "query": "{ hero { name friends { name } } }" }' | jq
```

### curl 示例：GET 请求查询

使用 GET 方式发送查询：

```bash
curl -G https://swapi-graphql.netlify.app/.netlify/functions/index \
  --data-urlencode "query={ hero { name } }"
```

`-G` 参数指定使用 GET 方法，`--data-urlencode` 自动对参数进行 URL 编码。

---

## JavaScript fetch API 示例发送请求

浏览器内置的 **fetch API** 是现代浏览器原生提供的发送 HTTP 请求的接口，使用它发送 GraphQL 请求非常直接。

### 基础 fetch 示例：简单查询

```javascript
async function fetchHero() {
  const response = await fetch('https://swapi-graphql.netlify.app/.netlify/functions/index', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: `
        {
          hero {
            name
            height
          }
        }
      `
    })
  });

  const result = await response.json();
  console.log(result.data);
  return result.data;
}

fetchHero();
```

### fetch 示例：带变量和操作名称

```javascript
async function fetchHeroByEpisode(episode) {
  const query = `
    query GetHero($episode: Episode) {
      hero(episode: $episode) {
        name
        appearsIn
        friends {
          name
        }
      }
    }
  `;

  const variables = {
    episode: episode
  };

  const response = await fetch('https://swapi-graphql.netlify.app/.netlify/functions/index', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: query,
      variables: variables,
      operationName: 'GetHero'
    })
  });

  const result = await response.json();
  
  if (result.errors) {
    console.error('GraphQL errors:', result.errors);
    throw new Error(result.errors[0].message);
  }
  
  return result.data;
}

// 使用示例
fetchHeroByEpisode('JEDI')
  .then(data => console.log('Hero data:', data))
  .catch(error => console.error('Error:', error));
```

### fetch 示例：带认证 Token

从 localStorage 读取 Token 并添加到请求头：

```javascript
async function fetchCurrentUser() {
  const token = localStorage.getItem('auth_token');
  
  const response = await fetch('https://api.example.com/graphql', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : '',
    },
    body: JSON.stringify({
      query: `
        query Me {
          me {
            id
            name
            email
          }
        }
      `
    })
  });

  const result = await response.json();
  
  if (response.status === 401) {
    // 未授权，清除 Token 并跳转到登录页
    localStorage.removeItem('auth_token');
    window.location.href = '/login';
    return;
  }
  
  return result.data;
}
```

### fetch 示例：发送 Mutation 变更

发送创建评论的 Mutation：

```javascript
async function createReview(episode, stars, commentary) {
  const query = `
    mutation CreateReview($episode: Episode!, $review: ReviewInput!) {
      createReview(episode: $episode, review: $review) {
        id
        stars
        commentary
        createdAt
      }
    }
  `;

  const variables = {
    episode: episode,
    review: {
      stars: stars,
      commentary: commentary
    }
  };

  const response = await fetch('/graphql', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
    },
    body: JSON.stringify({ query, variables })
  });

  return response.json();
}
```

---

## 缓存基础概念

**缓存（Caching）**是客户端存储已获取数据副本、以避免重复请求的技术，是 GraphQL 客户端库最核心的功能之一，也是选择专用客户端而非原生 fetch 的主要原因。

### 为什么需要客户端缓存

1. **减少网络请求**：相同数据不重复发送请求，提升应用响应速度
2. **改善用户体验**：页面切换时立即显示缓存数据，无需等待加载
3. **降低服务器压力**：减少 API 请求次数，降低后端负载
4. **离线支持**：配合持久化缓存，可在离线时展示已缓存的数据
5. **数据一致性**：当数据更新时，自动更新所有使用该数据的 UI 组件

### 规范化缓存（Normalized Cache）

**规范化缓存**（Normalized Cache）是 Apollo Client 和 Relay 使用的高级缓存策略，将查询结果扁平化为按实体存储的记录。

其工作原理：

1. **扁平化存储**：每个对象根据其 `__typename` 和 `id`（或 `_id`）生成唯一缓存键（如 `Human:1000`），存储在扁平的查找表中
2. **引用替换**：对象之间的引用（如朋友关系）被替换为缓存键引用，而不是存储完整副本
3. **自动去重**：同一个对象在不同查询中出现时，只存储一份副本
4. **自动更新**：当 Mutation 返回更新后的对象时，缓存中对应的实体会被自动更新，所有引用该实体的查询结果自动更新

**示例**：两个查询获取到同一个人物对象：

```graphql
# 查询 1
{
  human(id: "1000") {
    id
    name
  }
}

# 查询 2
{
  hero(episode: EMPIRE) {
    id
    name
    height
  }
}
```

如果 hero 返回的是 id 为 "1000" 的 Luke，那么规范化缓存中只会存储一份 `Human:1000` 记录，包含 `id`、`name`、`height` 三个字段。之后如果 Mutation 更新了 Luke 的名字，两个查询都会看到更新后的名字。

### 文档缓存（Document Cache）

**文档缓存**（Document Cache）是 urql 默认使用的更简单的缓存策略，按查询文档整体存储结果。

其特点：
- 实现简单，性能开销小
- 缓存键是查询字符串 + 变量的哈希
- 无法自动跨查询更新数据：同一个实体在不同查询中被修改时，需要手动更新所有相关查询
- 适合小型应用或对缓存要求不高的场景

### 缓存策略配置

客户端库通常提供多种缓存策略供选择：

| 策略 | 说明 |
|---|---|
| `cache-first`（默认） | 优先使用缓存，缓存命中则不发请求；未命中则发送请求并缓存结果 |
| `network-only` | 不使用缓存，始终发送网络请求 |
| `cache-and-network` | 先返回缓存数据快速展示，同时发送网络请求获取最新数据更新缓存和 UI |
| `cache-only` | 只从缓存读取，不发送请求（缓存未命中则报错） |
| `no-cache` | 既不读取缓存，也不写入缓存 |

---

## 查询变更与本地状态管理简介

现代 GraphQL 客户端库不仅负责与服务器通信，还提供了本地状态管理能力，将远程数据和本地状态统一管理。

### 远程数据与本地状态

应用中的状态可以分为两类：

1. **远程数据（Remote Data）**：存储在服务器上、通过 GraphQL 查询获取的数据，如用户信息、文章列表、评论等
2. **本地状态（Local State）**：仅存在于客户端的状态，如侧边栏是否展开、表单输入的临时值、UI 主题、弹窗显示状态等

传统架构中，远程数据通过 HTTP 请求获取，本地状态通过 Redux、MobX 或 React useState 管理，导致两套状态管理系统并存，增加了复杂度。

### GraphQL 客户端的本地状态管理

Apollo Client 和 urql 都支持通过 GraphQL 统一管理本地状态：

- 使用 `@client` 指令标记本地字段，区分本地数据与远程数据
- 本地字段可以通过本地 Resolver 计算得出
- 可以直接在 GraphQL 查询中同时获取远程数据和本地状态
- Mutation 既可以用于修改服务器数据，也可以用于修改本地状态

**示例**：查询同时获取远程用户信息和本地的 UI 状态：

```graphql
query GetUserWithSidebarState($userId: ID!) {
  user(id: $userId) {
    id
    name
    email  # 远程字段，从服务器获取
  }
  isSidebarOpen @client  # 本地字段，从客户端缓存读取
  theme @client          # 本地字段
}
```

这样，组件只需要一个查询就能获取到渲染所需的所有数据，无论是远程的还是本地的，无需在组件中分别处理。

### 乐观更新（Optimistic UI）

**乐观更新**（Optimistic UI）是 Mutation 场景下的重要优化技术：当用户触发一个变更操作（如点赞、提交评论）时，UI 立即更新为预期的成功状态，而不是等待服务器响应回来后再更新。如果服务器返回失败，再回滚 UI 到之前的状态并显示错误。

乐观更新利用了客户端缓存，可以显著提升应用的感知性能，让用户感觉操作是即时响应的。

### 数据订阅（Subscription）简介

除了 Query（查询，获取数据）和 Mutation（变更，修改数据），GraphQL 还有第三种操作类型：**Subscription**（订阅）。Subscription 通过 WebSocket 等长连接技术，允许服务器在特定事件发生时主动向客户端推送数据，实现实时更新。

典型使用场景：
- 实时消息/聊天应用
- 实时通知
- 协作编辑
- 实时数据仪表盘

Subscription 通常需要 GraphQL 客户端配合 WebSocket 链接使用，主流客户端库都有对应的支持。

---

## 本章核心概念总结

| 概念 | 一句话解释 |
|---|---|
| GraphQL 客户端库 | 专为 GraphQL 设计的数据层工具，提供缓存、状态管理、UI 同步等高级功能 |
| Apollo Client | 功能最全面、生态最丰富的主流 GraphQL 客户端，适合大多数项目 |
| Relay | Facebook 开发的高性能 React 专用客户端，适合大规模应用 |
| urql | 轻量级、插件化架构的 GraphQL 客户端，体积小、灵活性高 |
| POST 请求 | GraphQL 标准请求方式，支持所有操作类型，请求体为含 query/variables/operationName 的 JSON |
| GET 请求 | 仅用于幂等查询，参数在 URL 中，可利用 HTTP 缓存 |
| Content-Type: application/json | GraphQL 请求的标准内容类型 |
| Authorization: Bearer <token> | 常用的认证方式，在请求头中传递访问令牌 |
| GraphiQL | GraphQL 官方交互式 IDE，提供自动补全、文档浏览、查询调试功能 |
| 规范化缓存 | 将查询结果按实体扁平化存储，自动去重和跨查询更新的高级缓存策略 |
| 文档缓存 | 按查询整体存储结果的简单缓存策略，实现简单但无法自动跨查询更新 |
| @client 指令 | 标记字段为本地状态，由客户端而非服务器解析 |
| 乐观更新 | Mutation 发起后立即更新 UI，服务器响应后再确认或回滚的性能优化技术 |
| Subscription | GraphQL 第三种操作类型，通过长连接实现服务器主动推送实时数据 |

---

**上一章**：[GraphQL 验证与执行 ←](04-validation-execution.md)

**下一章**：[GraphQL 服务端核心概念 →](06-server-concepts.md)
