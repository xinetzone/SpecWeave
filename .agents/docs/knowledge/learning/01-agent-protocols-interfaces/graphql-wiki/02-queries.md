---
id: "graphql-wiki-queries"
title: "GraphQL 查询语言"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/01-agent-protocols-interfaces/graphql-wiki/02-queries.toml"
source: "spec:create-graphql-wiki-tutorial"
category: "learning"
tags: ["graphql", "api", "query-language", "fields", "arguments", "aliases", "fragments", "variables", "directives", "mutations"]
date: "2026-08-05"
status: "stable"
author: "SpecWeave"
summary: "GraphQL 查询语言完整指南，涵盖字段选择、参数、别名、片段、操作名称、变量、指令、变更操作和内联片段，每个语法点配有 Star Wars 主题的代码示例与 JSON 返回示例。"
---
# 第 2 章：GraphQL 查询语言

本章将系统介绍 GraphQL 查询语言的核心语法特性，通过《星球大战》（Star Wars）主题示例帮助你掌握如何编写精确、灵活且可复用的 GraphQL 查询。

## Fields（字段）

**字段（Field）**是 GraphQL 查询中数据获取的基本单位，客户端通过指定字段来声明需要哪些数据。GraphQL 查询的一个核心特性是：查询结构与返回的数据结构完全一致。

### 基本字段选择

最简单的查询是选择对象上的标量字段（**标量字段**：不可再分的基础数据类型字段，如字符串、数字、布尔值）。

```graphql
{
  hero {
    name
  }
}
```

这个查询表示："获取英雄（hero），并返回其名字（name）"。

**返回 JSON 示例：**

```json
{
  "data": {
    "hero": {
      "name": "R2-D2"
    }
  }
}
```

### 嵌套字段

GraphQL 查询可以嵌套，用于获取关联对象的数据。对象类型的字段可以选择其子字段，形成层级结构。

```graphql
{
  hero {
    name
    friends {
      name
    }
  }
}
```

这个查询不仅获取英雄的名字，还获取其朋友列表中每个朋友的名字。

**返回 JSON 示例：**

```json
{
  "data": {
    "hero": {
      "name": "R2-D2",
      "friends": [
        {
          "name": "Luke Skywalker"
        },
        {
          "name": "Han Solo"
        },
        {
          "name": "Leia Organa"
        }
      ]
    }
  }
}
```

> **注意**：查询结构与返回结构完全对应——`friends` 是一个数组，每个元素包含 `name` 字段。

## Arguments（参数）

**参数（Argument）**是附加在字段上的输入值，用于定制字段的返回结果，类似于函数调用时传递的参数。在 GraphQL 中，每一个字段（包括嵌套字段）都可以接收参数。

### 向字段传递参数

例如，我们可以通过参数指定查询哪一集的英雄：

```graphql
{
  hero(episode: EMPIRE) {
    name
  }
}
```

这里 `episode: EMPIRE` 是传递给 `hero` 字段的参数，`EMPIRE` 是一个枚举值（**枚举类型**：预定义的一组固定值的集合），表示《帝国反击战》。

**返回 JSON 示例：**

```json
{
  "data": {
    "hero": {
      "name": "Luke Skywalker"
    }
  }
}
```

### 在嵌套字段上使用参数

参数不仅可以用在根查询字段上，也可以用在任何嵌套字段上。例如，限制返回朋友的数量：

```graphql
{
  hero(episode: JEDI) {
    name
    friends(first: 2) {
      name
    }
  }
}
```

**返回 JSON 示例：**

```json
{
  "data": {
    "hero": {
      "name": "R2-D2",
      "friends": [
        {
          "name": "Luke Skywalker"
        },
        {
          "name": "Han Solo"
        }
      ]
    }
  }
}
```

参数可以用于多种用途：过滤、分页、排序、格式化输出等。在 REST API 中，你只能传递一组参数（通过查询字符串和 URL 参数），而在 GraphQL 中，每个字段都有自己的参数集，这使得查询表达能力大大增强。

## Aliases（别名）

**别名（Alias）**是为查询结果中的字段指定自定义名称的机制，用于解决同一字段在同一查询中多次使用时的命名冲突。

### 为什么需要别名

假设你需要在一个查询中同时获取两集的英雄：

```graphql
{
  hero(episode: EMPIRE) {
    name
  }
  hero(episode: JEDI) {
    name
  }
}
```

这个查询会产生冲突，因为两个字段都叫 `hero`，返回数据中无法区分。这时候就需要使用别名。

### 使用别名重命名字段

使用 `别名: 原字段名` 的语法为字段指定别名：

```graphql
{
  empireHero: hero(episode: EMPIRE) {
    name
  }
  jediHero: hero(episode: JEDI) {
    name
  }
}
```

**返回 JSON 示例：**

```json
{
  "data": {
    "empireHero": {
      "name": "Luke Skywalker"
    },
    "jediHero": {
      "name": "R2-D2"
    }
  }
}
```

返回结果使用别名作为键名，这样就可以在一次查询中获取同一字段的不同实例。别名可以用在任何字段上，不仅仅是根字段。

## Fragments（片段）

**片段（Fragment）**是可复用的字段集合单元，允许你定义一组字段，然后在多个查询中重复使用，避免重复编写相同的字段列表。

### 基本片段使用

假设我们在查询中需要多次获取角色的相同属性比较：

```graphql
{
  leftComparison: hero(episode: EMPIRE) {
    name
    appearsIn
    homePlanet
  }
  rightComparison: hero(episode: JEDI) {
    name
    appearsIn
    homePlanet
  }
}
```

两个字段选择集完全相同，可以提取为片段：

```graphql
{
  leftComparison: hero(episode: EMPIRE) {
    ...comparisonFields
  }
  rightComparison: hero(episode: JEDI) {
    ...comparisonFields
  }
}

fragment comparisonFields on Character {
  name
  appearsIn
  homePlanet
}
```

这里 `...comparisonFields` 是片段展开语法（类似 JavaScript 的展开运算符），`fragment comparisonFields on Character` 定义了一个名为 `comparisonFields` 的片段，应用于 `Character` 类型（**接口类型**：定义了一组字段契约，对象类型可以实现接口）。

**返回 JSON 示例：**

```json
{
  "data": {
    "leftComparison": {
      "name": "Luke Skywalker",
      "appearsIn": ["NEWHOPE", "EMPIRE", "JEDI"],
      "homePlanet": "Tatooine"
    },
    "rightComparison": {
      "name": "R2-D2",
      "appearsIn": ["NEWHOPE", "EMPIRE", "JEDI"],
      "homePlanet": null
    }
  }
}
```

### 在片段中使用变量

片段可以访问查询中定义的变量（变量将在下一节介绍）：

```graphql
query HeroComparison($first: Int = 3) {
  leftComparison: hero(episode: EMPIRE) {
    ...comparisonFields
  }
  rightComparison: hero(episode: JEDI) {
    ...comparisonFields
  }
}

fragment comparisonFields on Character {
  name
  friends(first: $first) {
    name
  }
}
```

**返回 JSON 示例：**

```json
{
  "data": {
    "leftComparison": {
      "name": "Luke Skywalker",
      "friends": [
        { "name": "Han Solo" },
        { "name": "Leia Organa" },
        { "name": "C-3PO" }
      ]
    },
    "rightComparison": {
      "name": "R2-D2",
      "friends": [
        { "name": "Luke Skywalker" },
        { "name": "Han Solo" },
        { "name": "Leia Organa" }
      ]
    }
  }
}
```

片段是 GraphQL 组合性的核心体现，帮助你构建可维护、不重复的查询。

## Operation Name（操作名称）

**操作名称（Operation Name）**是为查询或变更操作指定的显式名称，用于标识操作的目的，提高代码可读性和调试便利性。

### 匿名操作（不推荐）

之前的示例都省略了操作名称和操作类型，这被称为**匿名操作**：

```graphql
{
  hero {
    name
  }
}
```

匿名操作只适合简单的一次性查询，在生产代码中不推荐使用。

### 命名操作

显式指定操作类型（`query`/`mutation`/`subscription`）和操作名称：

```graphql
query HeroNameQuery {
  hero {
    name
  }
}
```

这里 `query` 是操作类型（表示这是一个查询操作），`HeroNameQuery` 是操作名称。

**操作类型**：GraphQL 支持三种操作类型：
- `query`：只读查询（默认值，可以省略）
- `mutation`：修改数据的变更操作
- `subscription`：实时订阅操作

### 多操作命名

当一个文档中包含多个操作时，必须为每个操作命名，以便服务器知道执行哪个：

```graphql
query HeroName {
  hero {
    name
  }
}

query HeroFriends {
  hero {
    friends {
      name
    }
  }
}
```

> **最佳实践**：始终为操作命名，就像给函数命名一样。这在调试服务端日志、使用 Apollo DevTools 等工具时非常有帮助，能够清晰地定位是哪个操作出了问题。

## Variables（变量）

**变量（Variable）**是查询中动态参数的占位符，允许你将动态值从查询语句中分离出来，避免手动字符串拼接，同时提高查询的可复用性。

### 为什么需要变量

没有变量时，你可能需要这样动态构建查询（非常不推荐）：

```javascript
// 反模式：手动拼接字符串，存在注入风险
const episode = "EMPIRE";
const query = `
  {
    hero(episode: ${episode}) {
      name
    }
  }
`;
```

这种方式存在安全风险（类似 SQL 注入），且无法被 GraphQL 客户端工具静态分析。

### 使用变量

正确的方式是使用变量，语法分为三部分：

1. 在查询中使用 `$变量名` 替代静态值
2. 在操作名称后声明变量接受的类型
3. 通过独立的变量字典传递实际值

```graphql
query HeroNameAndFriends($episode: Episode) {
  hero(episode: $episode) {
    name
    friends {
      name
    }
  }
}
```

**变量字典（JSON）：**

```json
{
  "episode": "JEDI"
}
```

**返回 JSON 示例：**

```json
{
  "data": {
    "hero": {
      "name": "R2-D2",
      "friends": [
        { "name": "Luke Skywalker" },
        { "name": "Han Solo" },
        { "name": "Leia Organa" }
      ]
    }
  }
}
```

### 变量声明规则

- 变量必须以 `$` 开头
- 变量声明格式：`$变量名: 类型`
- 类型后加 `!` 表示必填（如 `$episode: Episode!`）
- 可以指定默认值：`$episode: Episode = JEDI`

### 必填变量与默认值示例

```graphql
query HeroName($episode: Episode!, $first: Int = 2) {
  hero(episode: $episode) {
    name
    friends(first: $first) {
      name
    }
  }
}
```

- `$episode: Episode!`：`episode` 变量是必填的，类型为 `Episode` 枚举
- `$first: Int = 2`：`first` 变量可选，默认值为 2

## Directives（指令）

**指令（Directive）**是附加在字段或片段上的特殊注解，用于以声明方式影响查询的执行结果。GraphQL 内置两个核心指令：`@skip` 和 `@include`。

指令可以附加在字段或片段展开上，根据条件动态决定是否包含某个字段。

### @skip（跳过）

`@skip(if: Boolean)`：当 `if` 条件为 `true` 时，跳过该字段，不查询也不返回。

```graphql
query Hero($episode: Episode, $withFriends: Boolean!) {
  hero(episode: $episode) {
    name
    friends @skip(if: $withFriends) {
      name
    }
  }
}
```

**变量字典：**

```json
{
  "episode": "JEDI",
  "withFriends": true
}
```

**返回 JSON 示例（跳过 friends）：**

```json
{
  "data": {
    "hero": {
      "name": "R2-D2"
    }
  }
}
```

### @include（包含）

`@include(if: Boolean)`：当 `if` 条件为 `true` 时，才包含该字段。与 `@skip` 相反。

```graphql
query Hero($episode: Episode, $withFriends: Boolean!) {
  hero(episode: $episode) {
    name
    friends @include(if: $withFriends) {
      name
    }
  }
}
```

**变量字典：**

```json
{
  "episode": "JEDI",
  "withFriends": false
}
```

**返回 JSON 示例（不包含 friends）：**

```json
{
  "data": {
    "hero": {
      "name": "R2-D2"
    }
  }
}
```

### 指令的用途

指令提供了一种灵活的方式来根据条件调整查询返回的字段，而无需在客户端使用字符串操作来动态构建查询。常见使用场景：
- 根据 UI 状态显示/隐藏某些字段
- 根据用户权限返回不同粒度的数据
- A/B 测试不同的数据需求

## Mutations（变更）

**变更（Mutation）**是 GraphQL 中用于修改服务器端数据的操作类型，类似于 REST 中的 POST/PUT/PATCH/DELETE 请求。任何导致数据写入的操作都应该使用 Mutation 而非 Query。

### Mutation 与 Query 的区别

- Query 字段并行执行，而 Mutation 字段**按顺序执行**（保证操作的原子性和顺序性）
- Query 是只读的，Mutation 会产生副作用
- Mutation 执行后可以返回修改后的数据，方便客户端更新缓存

### 创建数据（Create）

假设我们要创建一个新的评论：

```graphql
mutation CreateReviewForEpisode($ep: Episode!, $review: ReviewInput!) {
  createReview(episode: $ep, review: $review) {
    stars
    commentary
  }
}
```

**变量字典：**

```json
{
  "ep": "JEDI",
  "review": {
    "stars": 5,
    "commentary": "This is a great movie!"
  }
}
```

**返回 JSON 示例：**

```json
{
  "data": {
    "createReview": {
      "stars": 5,
      "commentary": "This is a great movie!"
    }
  }
}
```

注意：Mutation 中通常使用**输入类型**（Input Type，专门用于传递复杂输入参数的类型）来传递结构化数据，如上面的 `ReviewInput`。

### 更新数据（Update）

```graphql
mutation UpdateHeroName($id: ID!, $newName: String!) {
  updateHero(id: $id, name: $newName) {
    id
    name
  }
}
```

**变量字典：**

```json
{
  "id": "1000",
  "newName": "R2-D2 (Updated)"
}
```

### 删除数据（Delete）

```graphql
mutation DeleteReview($id: ID!) {
  deleteReview(id: $id) {
    id
    success
  }
}
```

> **重要原则**：Mutation 操作应该总是返回被修改的数据，这样客户端可以直接使用返回值更新本地缓存，无需额外发起查询。

### 多个字段的 Mutation

一个 Mutation 可以包含多个字段，它们会按书写顺序依次执行：

```graphql
mutation MultipleOperations {
  createReview(episode: JEDI, review: { stars: 4 }) {
    stars
  }
  updateHero(id: "1000", name: "Artoo") {
    name
  }
}
```

在这个例子中，`createReview` 会先执行，完成后才执行 `updateHero`。

## Inline Fragments（内联片段）

**内联片段（Inline Fragment）**是直接在查询中定义的匿名片段，主要用于查询**联合类型**（Union Type，表示值可以是多种类型之一）或**接口类型**（Interface Type）的字段时，根据实际类型选择不同的字段。

### 为什么需要内联片段

在 Star Wars 示例中，`Character` 是一个接口，`Human` 和 `Droid` 是实现该接口的两种具体类型。`hero` 字段返回 `Character` 类型，但具体是 Human 还是 Droid 只有运行时才知道。

### 使用内联片段处理不同类型

如果要查询 Human 特有的 `homePlanet` 字段和 Droid 特有的 `primaryFunction` 字段，就需要使用内联片段：

```graphql
query HeroForEpisode($ep: Episode!) {
  hero(episode: $ep) {
    name
    ... on Droid {
      primaryFunction
    }
    ... on Human {
      homePlanet
      height
    }
  }
}
```

这里 `... on Droid { ... }` 和 `... on Human { ... }` 就是内联片段，语法为 `... on 类型名 { 字段选择 }`。

**变量字典：**

```json
{
  "ep": "EMPIRE"
}
```

**返回 JSON 示例（英雄是 Human 类型 Luke Skywalker）：**

```json
{
  "data": {
    "hero": {
      "name": "Luke Skywalker",
      "homePlanet": "Tatooine",
      "height": 1.72
    }
  }
}
```

**变量字典（查询 JEDI 集）：**

```json
{
  "ep": "JEDI"
}
```

**返回 JSON 示例（英雄是 Droid 类型 R2-D2）：**

```json
{
  "data": {
    "hero": {
      "name": "R2-D2",
      "primaryFunction": "Astromech"
    }
  }
}
```

可以看到，返回结果中只包含对应实际类型的特有字段——Luke 是 Human，所以有 `homePlanet`；R2-D2 是 Droid，所以有 `primaryFunction`。

### 内联片段与命名字段对比

| 特性 | 命名字段（普通片段） | 内联片段 |
|---|---|---|
| 定义位置 | 查询外部独立定义 | 直接在选择集内定义 |
| 复用性 | 可多处复用 | 仅在定义处使用一次 |
| 主要用途 | 复用重复字段集 | 处理接口/联合类型的条件字段 |
| 语法 | `fragment Name on Type { ... }` + `...Name` | `... on Type { ... }` |

### Meta 字段：__typename

GraphQL 提供了一个元字段 `__typename`，可以在任何查询中使用，用于获取对象的类型名称：

```graphql
{
  search(text: "an") {
    __typename
    ... on Human {
      name
      homePlanet
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

**返回 JSON 示例：**

```json
{
  "data": {
    "search": [
      {
        "__typename": "Human",
        "name": "Han Solo",
        "homePlanet": "Corellia"
      },
      {
        "__typename": "Human",
        "name": "Leia Organa",
        "homePlanet": "Alderaan"
      },
      {
        "__typename": "Starship",
        "name": "TIE Advanced x1",
        "length": 9.2
      }
    ]
  }
}
```

`__typename` 字段在客户端缓存中非常有用，它帮助客户端确定对象的具体类型，便于正确地归一化存储数据。

---

## 本章语法要点总结

| 语法特性 | 用途 | 关键语法 |
|---|---|---|
| Fields（字段） | 选择需要的数据 | 对象 { 子字段 } |
| Arguments（参数） | 定制字段返回结果 | 字段名(参数名: 值) |
| Aliases（别名） | 解决字段名冲突 | 别名: 字段名 |
| Fragments（片段） | 复用字段集合 | ...片段名 + fragment Name on Type |
| Operation Name | 命名操作便于调试 | query Name { ... } |
| Variables（变量） | 动态传递参数 | $var: Type |
| Directives（指令） | 条件包含字段 | @skip(if:) / @include(if:) |
| Mutations（变更） | 修改数据 | mutation Name { ... } |
| Inline Fragments | 处理接口/联合类型 | ... on Type { ... } |

---

**上一章**：[GraphQL 核心概念 ←](01-core-concepts.md)

**下一章**：[Schema 与类型系统 →](03-schema-types.md)
