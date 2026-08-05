---
id: "graphql-wiki-core-concepts"
title: "GraphQL 核心概念"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/01-agent-protocols-interfaces/graphql-wiki/01-core-concepts.toml"
source: "spec:create-graphql-wiki-tutorial"
category: "learning"
tags: ["graphql", "api", "query-language", "core-concepts", "sdl", "resolver", "schema"]
date: "2026-08-05"
status: "stable"
author: "SpecWeave"
summary: "GraphQL 核心概念详解，涵盖查询语言与运行时组成、Schema Definition Language (SDL)、三种操作类型、字段与参数、解析器机制、设计原则及核心术语通俗解释。"
---
# 第 1 章：GraphQL 核心概念

本章将系统介绍 GraphQL 的核心组成部分和基础概念，帮助你建立对 GraphQL 工作机制的整体认知。

## GraphQL 的组成

GraphQL 并非单一技术，而是由两个核心部分构成的完整体系：

### 1. 查询语言（Query Language）

**查询语言**是客户端与 API 交互的语法规范。它定义了客户端如何向服务器请求数据、如何指定需要的字段、如何传递参数，以及如何描述变更操作。与 REST API 中通过不同 URL 和 HTTP 方法表达意图不同，GraphQL 使用统一的查询语法来表达所有数据需求。

查询语言的特点：
- 声明式：客户端描述"想要什么"，而非"如何获取"
- 层级化：查询结构与返回的数据结构完全对应
- 可组合：支持片段、变量等复用机制

### 2. 运行时（Runtime）

**运行时**是服务端负责执行查询的引擎。它接收客户端发来的查询语句，根据预定义的类型系统进行验证，然后调用相应的函数获取数据，最终按照查询指定的形状组装结果并返回。

运行时的核心职责：
- 查询解析与验证：确保查询语法正确且只请求已定义的字段
- 字段解析：为每个字段调用对应的数据获取函数
- 结果组装：按照查询结构将获取的数据组装成响应
- 错误处理：在执行过程中捕获并格式化错误信息

> **关键理解**：GraphQL 不绑定任何特定数据库或存储引擎——它的运行时可以连接任何数据源（关系型数据库、NoSQL、REST API、微服务、第三方服务等），数据获取逻辑完全由开发者定义。

## Schema Definition Language (SDL)

**Schema Definition Language（模式定义语言，简称 SDL）**是 GraphQL 用于定义数据模型和 API 能力的专用语法。通过 SDL，开发者可以清晰地描述 API 支持哪些类型的数据、数据之间有什么关系、以及可以执行哪些操作。

SDL 是 GraphQL 强类型特性的体现——整个 API 的契约都通过 Schema 明确规定，这使得工具能够在开发阶段就发现错误，而不是等到运行时。

### SDL 示例：Person 类型

让我们通过一个简单的例子来认识 SDL。假设我们要定义一个"人"（Person）的类型：

```graphql
type Person {
  id: ID!
  name: String!
  age: Int
  email: String
  isActive: Boolean!
}
```

让我们逐行解释这个定义：

- `type Person`：声明一个名为 `Person` 的对象类型（**对象类型**：可以包含多个字段的复合类型，是 GraphQL Schema 中最常用的类型）
- `id: ID!`：定义名为 `id` 的字段，类型是 `ID`，末尾的 `!` 表示该字段**非空**（即查询时一定会返回值）
  - **ID 类型**：GraphQL 内置的标量类型，表示唯一标识符，序列化为字符串
- `name: String!`：姓名字段，`String` 是内置标量类型（UTF-8 字符串），非空
- `age: Int`：年龄字段，`Int` 是内置标量类型（32位整数），没有 `!` 表示可以为空
- `email: String`：邮箱字段，`String` 类型，可为空
- `isActive: Boolean!`：是否激活字段，`Boolean` 是内置标量类型（true/false），非空

### Query 类型示例

定义了数据类型后，我们还需要定义客户端可以执行的查询入口。这通过特殊的 `Query` 类型来实现：

```graphql
type Query {
  person(id: ID!): Person
  allPersons: [Person!]!
}
```

这个 `Query` 类型定义了两个查询字段：

- `person(id: ID!): Person`：根据 ID 获取单个 Person
  - `(id: ID!)` 是**参数**（Argument，用于向字段传递过滤条件或配置的输入值）
  - 返回类型是 `Person`（可以返回 null，表示找不到对应的人）
- `allPersons: [Person!]!`：获取所有人的列表
  - `[Person!]` 表示这是一个列表（**列表类型**：用方括号 `[]` 包裹，表示返回一组同类型数据）
  - 列表内的元素是非空的 `Person!`（不会有 null 元素）
  - 整个列表本身是非空的 `!`（一定会返回列表，即使是空列表）

### 完整的 Schema 示例

将上面两部分组合起来，就构成了一个最小但完整的 GraphQL Schema：

```graphql
type Person {
  id: ID!
  name: String!
  age: Int
  email: String
  isActive: Boolean!
}

type Query {
  person(id: ID!): Person
  allPersons: [Person!]!
}
```

这个 Schema 完整描述了：
- 有哪些数据类型（Person）
- 每种类型有哪些字段、字段是什么类型
- 客户端可以执行哪些查询（获取单个 Person 或获取全部 Person）
- 查询需要什么参数、返回什么数据

## 三种操作类型

GraphQL 支持三种基本的**操作类型**（Operation Type，即客户端可以对 API 执行的操作类别），分别对应数据的读取、修改和实时更新。

### 1. Query（查询）

**Query** 用于读取数据，类似于 REST 中的 GET 请求。这是最常用的操作类型，所有数据获取都通过 Query 完成。

Query 的特点：
- 只读操作，不会修改服务器上的数据
- 可以在单个请求中查询多个字段和关联资源
- 支持嵌套查询，遍历数据关系图

示例查询：

```graphql
query GetPerson {
  person(id: "1") {
    id
    name
    email
  }
}
```

### 2. Mutation（变更）

**Mutation** 用于修改服务器上的数据，类似于 REST 中的 POST/PUT/PATCH/DELETE 请求。当需要创建、更新或删除数据时，使用 Mutation。

Mutation 的特点：
- 会产生副作用（修改数据）
- 执行后可以返回修改后的数据（方便客户端更新缓存）
- 按顺序执行（一个 Mutation 中的多个字段会按顺序执行，而 Query 的字段是并行执行的）

示例 Mutation（需要先在 Schema 中定义）：

```graphql
type Mutation {
  createPerson(name: String!, email: String!): Person!
}
```

```graphql
mutation CreateNewPerson {
  createPerson(name: "张三", email: "zhangsan@example.com") {
    id
    name
    email
    isActive
  }
}
```

### 3. Subscription（订阅）

**Subscription** 用于实时获取数据更新，是 GraphQL 实现实时功能的方式。当服务器上的数据发生变化时，客户端会自动接收到推送消息。

Subscription 的特点：
- 基于长连接（通常使用 WebSocket）
- 服务器主动向客户端推送消息
- 适合实时应用场景（聊天、通知、实时数据仪表盘等）

示例 Subscription：

```graphql
type Subscription {
  personAdded: Person!
}
```

```graphql
subscription OnPersonAdded {
  personAdded {
    id
    name
    email
  }
}
```

## 字段与参数

### 字段（Field）

**字段**是 GraphQL 中数据获取的基本单位。每个字段都指向一个具体的数据值，客户端通过在查询中指定字段来声明需要哪些数据。

字段的关键特性：

1. **层级嵌套**：对象类型的字段可以是另一个对象类型，形成层级结构
2. **精确控制**：客户端只选择需要的字段，服务器不会返回多余数据
3. **独立解析**：每个字段都有自己的数据获取逻辑（即解析器函数）

例如，假设我们扩展 Person 类型增加地址信息：

```graphql
type Address {
  city: String!
  street: String
}

type Person {
  id: ID!
  name: String!
  address: Address
}
```

客户端可以这样查询嵌套字段：

```graphql
{
  person(id: "1") {
    name
    address {
      city
    }
  }
}
```

### 参数（Argument）

**参数**是附加在字段上的输入值，用于定制字段的返回结果，类似于 REST URL 中的查询参数或路径参数。

参数的作用：
- 过滤数据（如 `person(id: "1")` 按 ID 过滤）
- 分页（如 `limit`、`offset` 参数）
- 排序（如 `sortBy`、`order` 参数）
- 传递输入数据（如 Mutation 中创建对象的数据）

参数可以出现在任何字段上（不仅是 Query 的根字段），这是 GraphQL 非常灵活的一个特性。例如：

```graphql
type Query {
  person(id: ID!): Person
}

type Person {
  id: ID!
  name: String!
  friends(limit: Int): [Person!]!
}
```

查询时可以在嵌套字段上使用参数：

```graphql
{
  person(id: "1") {
    name
    friends(limit: 10) {
      name
    }
  }
}
```

## 解析器（Resolver）

**解析器**是 GraphQL 服务器中负责为单个字段获取数据的函数。它是 GraphQL 运行时与实际数据源之间的桥梁——每个字段都对应一个解析器函数，当执行查询时，运行时会为查询中出现的每个字段调用对应的解析器。

### 解析器的通俗理解

可以把解析器想象成餐厅里的厨师：

- **Schema** 是菜单——告诉顾客（客户端）有哪些菜（字段）可以点
- **查询**是顾客的订单——具体点了哪些菜，需要什么口味（参数）
- **解析器**是厨师——接到订单后，去厨房（数据库/其他服务）取食材并烹饪（处理逻辑），最后上菜（返回数据）

就像不同的菜由不同的厨师负责一样，不同的字段也由不同的解析器负责。

### 解析器的工作方式

解析器接收四个核心参数（不需要记忆具体名称，理解概念即可）：

1. **父对象**：上一个字段返回的结果，用于嵌套字段获取父级数据
2. **参数**：查询中传递给该字段的参数值
3. **上下文**：所有解析器共享的信息，如当前登录用户、数据库连接、请求信息等
4. **信息**：关于查询执行状态的元数据（较少使用）

### 解析器的执行流程

让我们通过一个具体例子理解解析器如何协作。假设执行以下查询：

```graphql
{
  person(id: "1") {
    name
    address {
      city
    }
  }
}
```

解析器的调用顺序和过程：

1. 首先调用 `Query.person` 解析器，传入参数 `id: "1"`
   - 这个解析器可能去数据库查询 ID 为 1 的用户记录
   - 返回 Person 对象（如 `{ id: "1", name: "张三", addressId: "100" }`）

2. 拿到 person 结果后，并行调用两个字段的解析器：
   - `Person.name`：通常简单返回父对象的 name 属性即可（"张三"）
   - `Person.address`：从父对象获取 addressId，可能去地址表查询 ID 为 100 的地址
     - 返回 Address 对象（如 `{ city: "北京", street: "长安街" }`）

3. 拿到 address 结果后，调用 `Address.city` 解析器：
   - 返回父对象的 city 属性（"北京"）

4. 运行时按照查询结构组装所有结果，返回给客户端

> **重要特性**：解析器是独立的、可组合的。每个解析器只关心如何获取自己字段的数据，不需要知道整体查询结构。这种设计使得 GraphQL 能够灵活地组装来自不同数据源的数据——`name` 可能来自关系型数据库，`address` 可能来自外部 API，`friends` 可能来自图数据库，而客户端对此完全无感知。

## GraphQL 的设计原则

GraphQL 的设计遵循一系列核心原则，这些原则塑造了它的独特优势：

### 1. 产品为中心，客户端驱动

GraphQL 从前端开发者和产品需求的视角出发设计 API。客户端最清楚视图需要什么数据，因此应该由客户端控制数据获取的粒度和形状，而不是由服务器预设固定的数据结构。

### 2. 层级结构与数据图

GraphQL 将数据视为**图**（Graph）而非资源集合——数据之间通过关系相互连接，查询可以沿着这些关系遍历。查询本身也是层级化的，自然地映射到产品 UI 的树状结构。

### 3. 强类型契约

所有 API 操作都基于强类型 Schema，Schema 既是服务器实现的依据，也是客户端查询的依据。类型系统在编译时和运行时都提供验证保障，减少集成错误。

### 4. 单一端点，灵活表达

与 REST 为每种资源设计多个端点不同，GraphQL 通常只暴露一个端点，所有数据需求都通过查询语句表达。这避免了端点膨胀和版本管理问题。

### 5. 渐进式演进

GraphQL API 可以在不破坏现有客户端的情况下持续演进：
- 新增字段不影响旧查询
- 废弃字段使用 `@deprecated` 指令标记
- 不需要创建 API 版本（如 `/v1`、`/v2`）

### 6. 存储无关性

GraphQL 不规定数据如何存储。你可以将 GraphQL 层放在任何现有系统之上——无论是新应用还是遗留系统，无论是数据库、微服务还是第三方 API——它只关心如何调用解析器获取数据，而不关心数据来自哪里。

## 核心术语通俗解释

| 术语 | 一句话通俗解释 |
|---|---|
| **GraphQL** | 一种让客户端精确索要所需数据的 API 查询语言和运行时引擎 |
| **Schema（模式）** | API 的"合同"或"菜单"，定义了有哪些数据、可以做什么操作 |
| **SDL** | 写 Schema 的专用语法，就像用特定格式写合同条款 |
| **类型（Type）** | 数据的种类，如"人"、"文章"、"评论"，定义了这类数据有哪些属性 |
| **字段（Field）** | 数据的具体属性，如人的"姓名"、"年龄" |
| **标量类型（Scalar Type）** | 不可再分的基础数据类型，如字符串、数字、布尔值 |
| **对象类型（Object Type）** | 由多个字段组成的复合类型，如"人"类型包含姓名、年龄等字段 |
| **Query（查询）** | 读数据的操作，相当于"我要查..." |
| **Mutation（变更）** | 改数据的操作（增删改），相当于"我要修改..." |
| **Subscription（订阅）** | 实时监听数据变化，相当于"有新情况时通知我" |
| **参数（Argument）** | 给字段传的"条件"或"配置"，如"查ID为1的人"中的ID |
| **解析器（Resolver）** | 真正去"找数据"的函数，每个字段都有一个对应的解析器 |
| **非空（!）** | 字段标记 `!` 表示"一定有值，不会为空" |
| **列表（[]）** | 用方括号表示返回一组数据，即数组 |
| **指令（Directive）** | 给 GraphQL 的额外指示，如 `@deprecated` 表示字段已过时 |
| **片段（Fragment）** | 可复用的字段集合，避免重复写相同的字段列表 |
| **变量（Variable）** | 查询中动态变化的值，让查询可以复用 |

---

**上一章**：[GraphQL 教程总览 ←](00-overview.md)

**下一章**：[查询（Query）→](02-queries.md)
