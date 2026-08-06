---
id: "graphql-wiki-schema-types"
title: "GraphQL Schema 与类型系统"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/01-agent-protocols-interfaces/graphql-wiki/03-schema-types.toml"
source: "spec:create-graphql-wiki-tutorial"
category: "learning"
tags: ["graphql", "api", "schema", "type-system", "scalar-types", "object-types", "enums", "interfaces", "unions", "input-types", "lists", "non-null"]
date: "2026-08-05"
status: "stable"
author: "SpecWeave"
summary: "GraphQL Schema 与类型系统完整指南，涵盖标量类型、对象类型、根类型、枚举、接口、联合类型、输入类型、列表与非空修饰符，每个类型配有 Star Wars 主题的 SDL 代码示例。"
---
# 第 3 章：GraphQL Schema 与类型系统

本章将深入讲解 GraphQL 的 Schema 定义语言（Schema Definition Language，SDL）与类型系统。类型系统是 GraphQL 的核心基石，它定义了 API 所能提供的数据结构、查询能力和数据契约。

## 类型系统（Type System）概述

**类型系统（Type System）** 是 GraphQL 中用于定义数据结构、字段关系和操作契约的一套规则体系。GraphQL 是强类型语言，每一个数据点都有明确的类型定义。

### 为什么 GraphQL 需要强类型

1. **自文档化**：Schema 本身就是 API 的完整文档，客户端可以通过内省（Introspection）查询获取完整的类型信息
2. **提前验证**：查询在执行前就可以根据 Schema 进行语法和语义验证，错误在开发阶段就能发现
3. **工具生态**：强类型使得 IDE 自动补全、代码生成、类型检查等工具成为可能
4. **契约明确**：服务端与客户端之间有明确的数据契约，减少沟通成本和集成错误

### Schema 定义语言（SDL）

**Schema 定义语言（Schema Definition Language，SDL）** 是用于定义 GraphQL Schema 的简洁语法，独立于具体编程语言。

例如，定义一个简单的对象类型：

```graphql
type Character {
  name: String!
  appearsIn: [Episode!]!
}
```

这个定义表示：`Character` 是一个对象类型，它有 `name`（非空字符串）和 `appearsIn`（非空的 Episode 枚举数组）两个字段。

## 标量类型（Scalar Types）

**标量类型（Scalar Type）** 是 GraphQL 中最基础的类型，代表不可再分的原子数据值，类似于编程语言中的基本类型。标量类型的字段没有子字段，查询时直接返回具体值。

GraphQL 内置五种标量类型：

| 类型 | 描述 | 示例值 |
|---|---|---|
| `Int` | 32 位有符号整数 | `42`, `-1`, `0` |
| `Float` | 双精度浮点数 | `3.14`, `-0.5`, `1.0` |
| `String` | UTF-8 字符序列 | `"Luke Skywalker"`, `"R2-D2"` |
| `Boolean` | 布尔值（true/false） | `true`, `false` |
| `ID` | 唯一标识符，序列化为字符串 | `"1000"`, `"2001"` |

### 标量类型使用示例

```graphql
type Human {
  id: ID!
  name: String!
  age: Int
  height: Float
  isJedi: Boolean!
}
```

### 自定义标量类型（Custom Scalars）

除了内置标量，你还可以定义自定义标量类型来表示特定格式的数据，如日期时间、JSON、邮箱地址等。自定义标量需要在服务端实现序列化、解析和验证逻辑。

```graphql
scalar DateTime
scalar JSON
scalar EmailAddress

type Review {
  id: ID!
  createdAt: DateTime!
  metadata: JSON
  authorEmail: EmailAddress
}
```

## 对象类型（Object Types）与字段

**对象类型（Object Type）** 是 GraphQL 中最常用的类型，代表一个有具体结构的实体，由一组命名字段组成。你可以把对象类型理解为面向对象编程中的"类"。

### 定义对象类型

以 Star Wars 主题为例：

```graphql
type Human {
  id: ID!
  name: String!
  homePlanet: String
  height: Float
  mass: Float
  friends: [Character!]
  appearsIn: [Episode!]!
  starships: [Starship!]
}

type Droid {
  id: ID!
  name: String!
  primaryFunction: String
  friends: [Character!]
  appearsIn: [Episode!]!
}

type Starship {
  id: ID!
  name: String!
  length: Float
  crew: [Human!]
}
```

### 字段参数

对象类型的字段可以接收参数，这使得字段更加灵活：

```graphql
type Human {
  id: ID!
  name: String!
  height(unit: LengthUnit = METER): Float
  friends(first: Int, after: ID): [Character!]
}
```

这里 `height` 字段接收一个 `unit` 参数（长度单位），`friends` 字段接收 `first`（数量限制）和 `after`（游标分页）参数。

## Query、Mutation、Subscription 根类型

**根类型（Root Type）** 是 Schema 的入口点，定义了 API 支持的所有操作。GraphQL 有三种根类型：

- `Query`：**查询根类型**，定义所有只读查询操作（类似 REST 的 GET）
- `Mutation`：**变更根类型**，定义所有修改数据的操作（类似 REST 的 POST/PUT/PATCH/DELETE）
- `Subscription`：**订阅根类型**，定义实时推送操作（类似 WebSocket 消息推送）

### 根类型定义示例

```graphql
type Query {
  hero(episode: Episode): Character
  human(id: ID!): Human
  droid(id: ID!): Droid
  search(text: String!): [SearchResult!]!
}

type Mutation {
  createReview(episode: Episode!, review: ReviewInput!): Review
  updateHuman(id: ID!, name: String, homePlanet: String): Human
  deleteReview(id: ID!): Boolean!
}

type Subscription {
  reviewAdded(episode: Episode): Review
  heroAppeared(episode: Episode!): Character
}

schema {
  query: Query
  mutation: Mutation
  subscription: Subscription
}
```

> **注意**：如果根类型的命名恰好是 `Query`、`Mutation`、`Subscription`，可以省略 `schema { }` 块，GraphQL 会自动识别。但显式声明更清晰，特别是当你需要自定义根类型名称时。

### 根类型与普通对象类型的区别

根类型本质上也是对象类型，区别仅在于它们是 Schema 的入口点。客户端发起的操作必须从根类型的字段开始。

## 枚举类型（Enum Types）

**枚举类型（Enum Type，Enumeration Type）** 是一种特殊的标量类型，其值被限制在预定义的一组固定字符串常量中。枚举类型适合表示分类、状态、选项等有限集合的值。

### 定义枚举类型

```graphql
enum Episode {
  NEWHOPE
  EMPIRE
  JEDI
}

enum LengthUnit {
  METER
  FOOT
}

enum ReviewStars {
  ONE
  TWO
  THREE
  FOUR
  FIVE
}

enum Role {
  JEDI
  SITH
  REBEL
  IMPERIAL
  BOUNTY_HUNTER
}
```

### 枚举类型使用示例

```graphql
type Query {
  hero(episode: Episode!): Character
  heroesByRole(role: Role!): [Character!]!
}

type Human {
  id: ID!
  name: String!
  role: Role!
}
```

枚举值在查询中直接使用，不加引号：

```graphql
{
  hero(episode: EMPIRE) {
    name
    role
  }
}
```

## 接口（Interfaces）与实现

**接口（Interface）** 是一种抽象类型，定义了一组字段契约，要求所有实现该接口的对象类型都必须包含这些字段。接口类似于面向对象编程中的"接口"概念，用于描述类型之间的共同特征。

### 定义接口

在 Star Wars 示例中，`Human` 和 `Droid` 有许多共同字段（id、name、friends、appearsIn），可以提取为 `Character` 接口：

```graphql
interface Character {
  id: ID!
  name: String!
  friends: [Character!]
  appearsIn: [Episode!]!
}
```

### 实现接口

对象类型使用 `implements` 关键字来声明实现某个接口，并必须包含接口定义的所有字段：

```graphql
type Human implements Character {
  id: ID!
  name: String!
  friends: [Character!]
  appearsIn: [Episode!]!
  homePlanet: String
  height(unit: LengthUnit = METER): Float
  mass: Float
  starships: [Starship!]
}

type Droid implements Character {
  id: ID!
  name: String!
  friends: [Character!]
  appearsIn: [Episode!]!
  primaryFunction: String
}
```

### 接口作为字段返回类型

接口可以作为字段的返回类型，这意味着该字段可以返回任何实现了该接口的对象类型：

```graphql
type Query {
  hero(episode: Episode): Character
  search(text: String!): [Character!]!
}
```

当查询返回接口类型的字段时，需要使用内联片段（`... on TypeName`）来查询具体实现类型的特有字段（参考第 2 章内联片段部分）。

### 实现多个接口

一个对象类型可以实现多个接口：

```graphql
interface Node {
  id: ID!
}

interface Timestamped {
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Review implements Node & Timestamped {
  id: ID!
  createdAt: DateTime!
  updatedAt: DateTime!
  stars: ReviewStars!
  commentary: String
}
```

## 联合类型（Union Types）

**联合类型（Union Type）** 表示一个值可以是多种不同对象类型中的某一种，但不需要这些类型共享任何公共字段。联合类型与接口的区别在于：接口要求实现类型拥有共同字段，而联合类型不要求。

### 定义联合类型

```graphql
union SearchResult = Human | Droid | Starship
```

这表示 `SearchResult` 类型的值可以是 `Human`、`Droid` 或 `Starship` 中的任意一种。

### 联合类型使用示例

```graphql
type Query {
  search(text: String!): [SearchResult!]!
}
```

### 查询联合类型字段

由于联合类型的成员不要求共享字段，查询时必须使用内联片段来指定每个类型需要的字段：

```graphql
{
  search(text: "an") {
    __typename
    ... on Human {
      name
      homePlanet
      height
    }
    ... on Droid {
      name
      primaryFunction
    }
    ... on Starship {
      name
      length
    }
  }
}
```

### 接口 vs 联合类型

| 特性 | 接口（Interface） | 联合类型（Union） |
|---|---|---|
| 公共字段要求 | 必须包含接口定义的所有字段 | 不要求成员类型有公共字段 |
| 字段查询 | 可以直接查询公共字段，特有字段用内联片段 | 必须为每个成员类型使用内联片段 |
| 关系类型 | "是一个"（is-a）关系 | "可以是之一"关系 |
| 典型场景 | 有共同特征的实体（如 Character） | 异构搜索结果、不相关类型的聚合 |

## 输入类型（Input Types）

**输入类型（Input Type）** 是专门用于传递复杂输入参数的对象类型，主要用于 Mutation 操作中传递结构化数据。输入类型与普通对象类型的区别在于：输入类型只能包含标量、枚举、其他输入类型和列表/非空修饰符，**不能包含字段参数，也不能包含普通对象类型或接口/联合类型**。

### 为什么需要输入类型

假设我们要创建一条评论，需要传递多个字段（stars、commentary、episode 等）。如果不使用输入类型，每个字段都要作为单独的参数传递，非常繁琐：

```graphql
type Mutation {
  createReview(
    episode: Episode!
    stars: Int!
    commentary: String
  ): Review
}
```

使用输入类型可以将相关参数组织在一起：

### 定义输入类型

输入类型使用 `input` 关键字定义：

```graphql
input ReviewInput {
  stars: ReviewStars!
  commentary: String
  episode: Episode!
  favoriteCharacters: [ID!]
}

input HumanInput {
  name: String!
  homePlanet: String
  height: Float
  mass: Float
}
```

### 使用输入类型

```graphql
type Mutation {
  createReview(review: ReviewInput!): Review
  createHuman(human: HumanInput!): Human
  updateHuman(id: ID!, patch: HumanInput!): Human
}
```

对应的 Mutation 操作：

```graphql
mutation CreateReview($review: ReviewInput!) {
  createReview(review: $review) {
    id
    stars
    commentary
  }
}
```

变量字典：

```json
{
  "review": {
    "stars": "FIVE",
    "commentary": "This is a great movie!",
    "episode": "JEDI",
    "favoriteCharacters": ["1000", "2001"]
  }
}
```

### 输入类型 vs 输出类型（Object Type）

| 特性 | 输入类型（input） | 对象类型（type） |
|---|---|---|
| 用途 | 传递输入参数 | 返回输出数据 |
| 字段参数 | 不允许 | 允许 |
| 字段类型 | 仅标量、枚举、输入类型、列表/非空 | 标量、枚举、对象类型、接口、联合、列表/非空 |
| 典型位置 | Mutation 参数 | Query/Mutation/Subscription 返回值 |

## 列表类型（Lists）与非空（Non-Null）修饰符

**类型修饰符（Type Modifier）** 是应用在类型上的特殊标记，用于改变类型的语义。GraphQL 有两种类型修饰符：列表（List）和非空（Non-Null）。

### 列表类型（List）

**列表类型（List Type）** 表示该字段的值是一个数组，包含指定类型的多个元素。列表类型通过在类型外面包裹方括号 `[Type]` 来表示。

```graphql
type Human {
  id: ID!
  name: String!
  appearsIn: [Episode]
  friends: [Character]
  starships: [Starship]
}
```

- `[Episode]`：Episode 枚举数组，可以为 null，数组中的元素也可以为 null
- `[Character]`：Character 对象数组，可以为 null，数组中的元素也可以为 null

### 非空修饰符（Non-Null）

**非空修饰符（Non-Null Modifier）** 表示该字段的值不能为 null，服务端必须始终返回一个非空值。如果返回 null，将触发 GraphQL 执行错误。非空修饰符通过在类型后面加感叹号 `!` 来表示。

```graphql
type Human {
  id: ID!
  name: String!
  age: Int
}
```

- `id: ID!`：id 字段是非空 ID，必须返回值
- `name: String!`：name 字段是非空字符串，必须返回值
- `age: Int`：age 字段可以为 null（表示年龄未知）

### 非空参数

非空修饰符也可以用在参数上，表示该参数是必填的：

```graphql
type Query {
  human(id: ID!): Human
  droid(id: ID!): Droid
}
```

这里 `id` 参数是必填的，如果不传递将导致验证错误。

## 类型修饰符组合

列表和非空修饰符可以组合使用，形成更精确的类型约束。理解修饰符的组合顺序非常重要——修饰符的应用顺序是**从左到右，从外到内**。

### 组合类型示例

```graphql
type Example {
  myField: [String!]!
  anotherField: [String]!
  yetAnotherField: [String!]
  nullableNullable: [String]
}
```

让我们逐一解析：

| 类型定义 | 含义 | 是否可 null | 数组元素是否可 null |
|---|---|---|---|
| `[String!]!` | 非空的非空字符串数组 | ❌ 不可 | ❌ 不可 |
| `[String]!` | 非空的字符串数组（元素可 null） | ❌ 不可 | ✅ 可以 |
| `[String!]` | 字符串数组（数组本身可 null），元素非空 | ✅ 可以 | ❌ 不可 |
| `[String]` | 字符串数组（数组和元素都可 null） | ✅ 可以 | ✅ 可以 |

### Star Wars 完整示例

```graphql
type Human implements Character {
  id: ID!
  name: String!
  friends: [Character!]
  appearsIn: [Episode!]!
  homePlanet: String
  height(unit: LengthUnit = METER): Float
  starships: [Starship!]!
}
```

解析：
- `id: ID!`：id 非空
- `name: String!`：name 非空
- `friends: [Character!]`：friends 数组可以为 null（无朋友），但如果有朋友，每个朋友都不能是 null
- `appearsIn: [Episode!]!`：appearsIn 数组非空，数组中每个 Episode 值都非空
- `homePlanet: String`：homePlanet 可以为 null（如角色没有母星信息）
- `starships: [Starship!]!`：starships 数组非空，每艘星舰都非空（即使是没有星舰的角色，也返回空数组而非 null）

### 输入类型中的修饰符组合

修饰符在输入类型中的语义与输出类型一致：

```graphql
input ReviewInput {
  stars: ReviewStars!
  commentary: String
  episode: Episode!
  tags: [String!]
  favoriteCharacters: [ID!]!
}
```

- `tags: [String!]`：tags 参数可以省略（为 null），但如果提供，标签字符串不能为 null
- `favoriteCharacters: [ID!]!`：favoriteCharacters 必须提供（非空），数组中的每个 ID 都非空

---

## 本章类型系统总结

| 类型类别 | 关键字 | 用途 | 示例 |
|---|---|---|---|
| 标量类型 | `scalar`（自定义）/ 内置 | 原子数据值 | `Int`, `String`, `ID`, `DateTime` |
| 对象类型 | `type` | 结构化实体 | `Human`, `Droid`, `Starship` |
| 根类型 | `type Query/Mutation/Subscription` | API 入口点 | `Query.hero`, `Mutation.createReview` |
| 枚举类型 | `enum` | 固定选项集合 | `Episode`, `LengthUnit`, `Role` |
| 接口类型 | `interface` | 字段契约、抽象类型 | `Character`, `Node` |
| 联合类型 | `union` | 异构类型聚合 | `SearchResult = Human \| Droid \| Starship` |
| 输入类型 | `input` | 复杂输入参数 | `ReviewInput`, `HumanInput` |
| 列表修饰符 | `[Type]` | 数组类型 | `[Character]`, `[Episode!]!` |
| 非空修饰符 | `Type!` | 不可为 null | `String!`, `[String!]!` |

---

**上一章**：[GraphQL 查询语言 ←](02-queries.md)

**下一章**：[验证与执行 →](04-validation-execution.md)
