---
id: "graphql-wiki-best-practices"
title: "GraphQL 最佳实践"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/01-agent-protocols-interfaces/graphql-wiki/08-best-practices.toml"
source: "spec:create-graphql-wiki-tutorial"
category: "learning"
tags: ["graphql", "best-practices", "schema-design", "performance", "security", "error-handling", "anti-patterns"]
date: "2026-08-05"
status: "stable"
author: "SpecWeave"
summary: "GraphQL 全面最佳实践指南，涵盖 Schema 设计、性能优化、安全防护、错误处理、开发工具链以及常见反模式，包含 SDL 代码对比示例和可落地的工程实践建议。"
---
# 第 8 章：GraphQL 最佳实践

本章系统梳理 GraphQL 在生产环境中的工程最佳实践，从 Schema 设计、性能优化、安全防护、错误处理到开发体验，同时指出常见反模式并提供正确的实现方案。掌握这些实践将帮助你构建健壮、高效且可维护的 GraphQL 服务。

---

## Schema 设计最佳实践

Schema 是 GraphQL API 的契约，良好的 Schema 设计直接影响 API 的可用性、可维护性和演进能力。

### 命名约定

统一的命名约定是 API 可读性的基础。GraphQL 社区已形成广泛接受的命名规范：

| 元素 | 命名风格 | 示例 |
|------|----------|------|
| 字段名 | camelCase | `userName`, `createdAt`, `isActive` |
| 类型名 | PascalCase | `User`, `Post`, `UserConnection` |
| 参数名 | camelCase | `first`, `after`, `userId` |
| 枚举值 | ALL_CAPS | `ACTIVE`, `PENDING`, `DELETED` |
| 输入类型名 | PascalCase + Input 后缀 | `CreateUserInput`, `UpdatePostInput` |
| 接口名 | PascalCase（通常为形容词或名词） | `Node`, `Error`, `Timestamped` |

**SDL 示例**：

```graphql
type User {
  id: ID!
  fullName: String!
  email: String!
  status: UserStatus!
  createdAt: DateTime!
}

enum UserStatus {
  ACTIVE
  INACTIVE
  SUSPENDED
}

input CreateUserInput {
  fullName: String!
  email: String!
  password: String!
}
```

### 字段设计原则

#### 避免过于通用的字段名

通用字段名（如 `data`、`info`、`value`）会降低 API 的自文档化能力，应使用描述性更强的名称。

**反模式**：
```graphql
type User {
  data: String  # data 是什么？姓名？邮箱？
  info: String  # info 是什么？简介？地址？
}
```

**正确做法**：
```graphql
type User {
  fullName: String!
  email: String!
  bio: String
  avatarUrl: String
}
```

#### 使用具体而非抽象的类型

避免过度抽象的通用类型，应根据业务领域定义具体类型。虽然 JSON 标量在某些场景下有用，但过度使用会丧失 GraphQL 的类型安全优势。

**反模式**：
```graphql
type Mutation {
  updateEntity(id: ID!, data: JSON!): Entity!  # 丢失类型信息
}
```

**正确做法**：
```graphql
type Mutation {
  updateUser(id: ID!, input: UpdateUserInput!): UpdateUserPayload!
  updatePost(id: ID!, input: UpdatePostInput!): UpdatePostPayload!
}

input UpdateUserInput {
  fullName: String
  email: String
  bio: String
}
```

#### 合理使用 Non-Null（!）

Non-Null 类型表示字段永远不会返回 null。过度使用 Non-Null 会限制 API 的演进能力——一旦字段标记为 Non-Null，就永远不能在不破坏客户端的情况下让它返回 null（例如某个字段的数据暂时不可用时）。

**使用建议**：
- 真正的主键/标识符（如 `id`）应标记为 Non-Null
- 业务上保证存在的字段标记为 Non-Null
- 可能因数据缺失或权限原因无法返回的字段使用 Nullable
- 列表本身可以是 Non-Null，但列表元素是否 Non-Null 需要谨慎

```graphql
type User {
  id: ID!                     # 用户 ID 一定存在
  fullName: String!           # 姓名一定存在
  email: String!              # 邮箱一定存在
  bio: String                 # 简介可能为空
  phoneNumber: String         # 手机号可能未提供
  posts: [Post!]!             # posts 字段本身不会为 null，但可能是空数组
}
```

### 分页设计

当返回列表数据时，必须考虑分页。一次性返回所有数据会导致性能问题和网络传输瓶颈。

#### 为什么需要分页

- 数据库层面：避免全表扫描和大量数据加载
- 网络层面：减少单次响应体大小，提升加载速度
- 用户体验：支持渐进式加载（无限滚动）
- 服务稳定性：防止恶意请求大量数据拖垮服务

#### Connections/Relay 风格分页

Relay 风格的游标分页（Cursor-based Pagination）是 GraphQL 社区推荐的分页模式，提供了强大的分页能力：

```graphql
type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

type UserEdge {
  node: User!
  cursor: String!
}

type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int
}

type Query {
  users(first: Int, after: String, last: Int, before: String): UserConnection!
}
```

**核心概念**：
- **Connection**：分页结果的包装类型，包含边列表、分页信息和总数
- **Edge**：边类型，包装单个节点和对应的游标
- **Cursor（游标）**：不透明的字符串，标记列表中的特定位置，客户端不应解析其内容
- **PageInfo**：分页元信息，告知是否有下一页/上一页

**查询示例**：
```graphql
{
  users(first: 10) {
    edges {
      node {
        id
        fullName
      }
      cursor
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

#### 简单 Offset/Limit 分页

对于简单场景或内部 API，也可以使用 offset/limit 风格，但灵活性和性能不如游标分页：

```graphql
type UserList {
  items: [User!]!
  total: Int!
  page: Int!
  pageSize: Int!
}

type Query {
  users(page: Int = 1, pageSize: Int = 20): UserList!
}
```

**Offset 分页的缺点**：
- 数据变动时（新增/删除）会导致重复或跳过数据
- 大 offset 时数据库查询性能差（需要扫描前面所有行）

### 版本演进

GraphQL 的强类型系统支持平滑的 API 演进，无需版本号（如 `/v1`、`/v2`）。

#### 使用 @deprecated 指令废弃字段

废弃旧字段时，使用内置的 `@deprecated` 指令标记，并提供 `reason` 说明迁移路径。

**SDL 示例**：

```graphql
type User {
  id: ID!
  fullName: String!
  firstName: String @deprecated(reason: "请使用 fullName 字段")
  lastName: String @deprecated(reason: "请使用 fullName 字段")
  email: String!
}

type Query {
  user(id: ID!): User
  getUsers: [User!]! @deprecated(reason: "请使用 users(first: Int, after: String) 分页查询")
}
```

**@deprecated 指令**：GraphQL 内置指令，用于标记已废弃的字段、枚举值或参数，告知客户端该元素仍可用但将在未来版本移除。GraphiQL 等工具会对废弃字段进行特殊显示。

**废弃流程**：
1. 添加新字段，将旧字段标记为 `@deprecated` 并说明原因
2. 监控客户端使用情况，通知使用旧字段的客户端迁移
3. 等待足够长的过渡期后，在下一个大版本中移除旧字段

#### 不做破坏性变更

以下变更属于**破坏性变更**，应避免：
- 删除字段或类型
- 将 Non-Null 字段改为 Nullable（客户端已预期一定有值）
- 更改字段的参数或类型
- 删除枚举值
- 改变字段的语义含义

**安全的变更包括**：
- 添加新字段、新类型、新参数
- 将 Nullable 字段改为 Non-Null（前提是所有现有数据都有值）
- 添加新的枚举值
- 标记字段为 `@deprecated`

### 输入类型 vs 多个参数

对于 Mutation，推荐使用输入类型（Input Type）而非多个独立参数。输入类型具有更好的可扩展性——未来添加新字段时不会改变 Mutation 签名，避免破坏性变更。

**反模式（多个参数）**：
```graphql
type Mutation {
  createUser(
    firstName: String!
    lastName: String!
    email: String!
    password: String!
    bio: String
    avatarUrl: String
    phoneNumber: String
  ): User!
}
```

**正确做法（输入类型）**：
```graphql
input CreateUserInput {
  firstName: String!
  lastName: String!
  email: String!
  password: String!
  bio: String
  avatarUrl: String
  phoneNumber: String
}

type CreateUserPayload {
  user: User!
  success: Boolean!
}

type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
}
```

**输入类型（Input Type）**：GraphQL 专用类型，仅用于参数传递（不能作为字段返回类型），与普通类型的区别是使用 `input` 关键字而非 `type`。输入类型的字段可以包含其他输入类型，但不能包含普通类型。

此外，建议使用 Payload 模式包装 Mutation 返回值，便于未来扩展：
```graphql
type CreateUserPayload {
  user: User           # 创建成功时返回用户
  errors: [Error!]     # 失败时返回业务错误（见错误处理章节）
  clientMutationId: String  # 可选：用于客户端追踪请求
}
```

---

## 性能最佳实践

GraphQL 的灵活性伴随着性能挑战。客户端可以任意嵌套查询，如果不加以控制，很容易导致性能问题。

### N+1 问题详解与解决

N+1 问题是 GraphQL 中最常见的性能问题，尤其在使用"每个字段独立解析"的 naive Resolver 实现时。

#### 什么是 N+1 问题

**N+1 问题**：一种数据库查询性能反模式，执行 1 次查询获取列表数据后，对列表中的 N 条记录各执行 1 次额外查询，总共产生 N+1 次查询。在 GraphQL 中，由于每个 Resolver 独立执行，这一问题尤为突出。

**示例场景**：查询所有用户及其文章

```graphql
{
  users {
    id
    fullName
    posts {
      id
      title
    }
  }
}
```

**naive Resolver 实现（伪代码）**：
```python
def resolve_users(root, info):
    return db.query("SELECT * FROM users")  # 第 1 次查询

def resolve_posts(user, info):
    return db.query("SELECT * FROM posts WHERE author_id = ?", user.id)
    # 对每个 user 执行 1 次，共 N 次
}
```

如果有 100 个用户，总共执行 1 + 100 = 101 次数据库查询——这就是 N+1 问题。

#### DataLoader 模式解决 N+1

**DataLoader**：由 Facebook 发明的通用工具模式，通过批处理（batching）和缓存（caching）机制解决 N+1 问题。核心原理是在单次事件循环中收集所有独立的加载请求，合并为一次批量查询。

**DataLoader 工作流程**：
1. 每个 Resolver 调用 `loader.load(key)` 请求数据，而非直接查询数据库
2. DataLoader 在当前事件循环 tick 内收集所有 key
3. 事件循环结束前，DataLoader 调用批处理函数一次性加载所有 key
4. 将结果分发给对应的调用方

**DataLoader 代码示例（Python）**：
```python
from promise import Promise
from dataloader import DataLoader

class PostLoader(DataLoader):
    def batch_load_fn(self, user_ids):
        # 一次性查询所有用户的文章
        posts = db.query(
            "SELECT * FROM posts WHERE author_id IN (?)",
            user_ids
        )
        # 按 user_id 分组
        posts_by_user = {}
        for post in posts:
            if post.author_id not in posts_by_user:
                posts_by_user[post.author_id] = []
            posts_by_user[post.author_id].append(post)
        # 返回与 user_ids 顺序一致的结果
        return Promise.resolve([
            posts_by_user.get(uid, []) for uid in user_ids
        ])

# 在 Context 中创建每个请求的 DataLoader 实例
def create_context():
    return {
        "post_loader": PostLoader()
    }

# Resolver 使用 DataLoader
def resolve_posts(user, info):
    return info.context["post_loader"].load(user.id)
```

**DataLoader 的关键要点**：
- 每个 HTTP 请求应创建新的 DataLoader 实例（请求级缓存，避免跨请求数据泄漏）
- 批处理函数必须保持返回结果顺序与传入 keys 顺序一致
- DataLoader 会在单次请求内缓存已加载的 key，避免重复查询
- DataLoader 也适用于微服务调用、REST API 请求等任何 I/O 场景

### 查询深度限制与复杂度限制

GraphQL 允许客户端任意嵌套查询，恶意或无意的深层查询会消耗大量服务器资源，甚至导致拒绝服务。

#### 查询深度限制

**查询深度**：嵌套查询的层级数。例如 `user { posts { comments { author { ... } } } }` 的深度为 4。

通过限制最大查询深度，可以阻止过深的嵌套查询。

**深度限制配置示例（graphql-core）**：
```python
from graphql import validate, parse, build_schema
from graphql.validation import NoSchemaIntrospectionCustomRule

class DepthLimitRule(ValidationRule):
    def __init__(self, max_depth: int):
        self.max_depth = max_depth

    def enter_OperationDefinition(self, node, *args):
        depth = self._compute_depth(node)
        if depth > self.max_depth:
            raise GraphQLError(
                f"查询深度 {depth} 超过限制 {self.max_depth}",
                node
            )
```

#### 查询复杂度限制

深度限制只考虑层级数，但一个浅层查询也可能请求大量数据（如一个根字段返回 10000 条记录，每条记录有 100 个字段）。复杂度限制为每个字段分配"成本"，计算整个查询的总复杂度。

**复杂度评分规则示例**：
- 标量字段：1 点复杂度
- 对象字段：1 + 子字段复杂度之和
- 分页连接字段：`first`/`limit` 参数 × 子字段复杂度
- 数据库密集字段：更高权重（如 10 点）

**复杂度计算示例**：
```graphql
{
  users(first: 10) {        # 10 个用户 × 子字段复杂度
    id                      # 1
    fullName                # 1
    posts(first: 5) {       # 每个用户 5 篇文章 × 子字段复杂度
      id                    # 1
      title                 # 1
    }
  }
}
# 总复杂度：10 × (1 + 1 + 5 × (1 + 1)) = 10 × 12 = 120
```

通常设置一个合理的复杂度上限（如 1000-5000），超过则拒绝查询。

### 持久化查询（Persisted Queries）

**持久化查询（Persisted Queries）**：一种优化机制，客户端在构建时将查询语句发送到服务器并生成哈希 ID，运行时只发送哈希 ID 和变量而非完整查询语句。服务器通过哈希 ID 查找预先存储的查询。

**持久化查询的优势**：
- 减少网络传输：大查询只需发送短哈希值
- 提升安全性：服务器可以只允许执行白名单中的查询，阻止任意查询
- CDN 缓存：GET 请求配合哈希 ID 可以被 CDN 缓存
- 性能优化：服务器可以预解析和验证持久化的查询

**工作流程**：
1. 构建时：客户端生成查询 → 计算 SHA-256 哈希 → 发送到服务器注册
2. 运行时：客户端发送 `{ "id": "<hash>", "variables": {...} }` → 服务器查表执行

### 字段级权限控制

并非所有用户都能访问所有字段。例如普通用户不应能查看其他用户的邮箱或密码哈希。

**在 Resolver 层面进行权限检查**：
```python
def resolve_email(user, info):
    current_user = info.context["current_user"]
    if not current_user or current_user.id != user.id:
        return None  # 或抛出权限错误
    return user.email

def resolve_role(user, info):
    current_user = info.context["current_user"]
    if not current_user or not current_user.is_admin:
        raise PermissionError("需要管理员权限")
    return user.role
```

**使用 Schema Directive 简化权限控制**：
```graphql
directive @auth(requires: Role = USER) on FIELD_DEFINITION | OBJECT

enum Role {
  USER
  ADMIN
  SUPER_ADMIN
}

type User {
  id: ID!
  fullName: String!
  email: String! @auth(requires: USER)
  role: Role! @auth(requires: ADMIN)
}
```

### 批处理与缓存

#### 请求批处理

**查询批处理（Query Batching）**：将多个独立的 GraphQL 查询合并到一个 HTTP 请求中发送，减少网络往返次数。大多数 GraphQL 客户端和服务器都支持批处理。

**注意**：批处理不等于 DataLoader 的批处理。HTTP 批处理是合并多个独立查询，DataLoader 是在单个查询内合并数据加载请求。两者互补。

#### 多层缓存策略

GraphQL 适合分层缓存：

1. **HTTP 层缓存**：对于 GET 请求（配合持久化查询），利用 CDN 和浏览器缓存
2. **服务端响应缓存**：基于查询哈希和变量缓存整个响应
3. **Resolver 级缓存**：使用 DataLoader 的请求级缓存，或使用 Redis 等分布式缓存
4. **客户端缓存**：Apollo Client、Relay 等客户端库维护规范化缓存（Normalized Cache）

**规范化缓存（Normalized Cache）**：客户端缓存策略，将查询结果扁平化存储为以类型+ID 为主键的记录，实现跨查询的实体共享和自动更新。例如查询 `user(id:1)` 和 `post(id:2){author}` 返回同一用户时，缓存中只存储一份用户数据。

---

## 安全最佳实践

GraphQL 的灵活性要求我们更加重视安全防护。

### 认证与授权

#### 在 Context 中传递用户信息

认证（Authentication，验证用户身份）应在 HTTP 层（如中间件）完成，解析出的用户信息通过 Context 传递给 Resolver。

**Context**：GraphQL 执行时传递给所有 Resolver 的共享上下文对象，包含请求信息、数据库连接、已认证用户、DataLoader 实例等。Context 是连接 HTTP 层与 GraphQL 执行层的桥梁。

**FastAPI 中间件示例**：
```python
from fastapi import Request, Depends
from strawberry.fastapi import GraphQLRouter

async def get_context(request: Request):
    auth_header = request.headers.get("Authorization", "")
    current_user = None
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        current_user = verify_jwt_token(token)
    return {
        "request": request,
        "current_user": current_user,
        "post_loader": PostLoader(),
    }

router = GraphQLRouter(schema, context_getter=get_context)
```

#### Resolver 级权限检查

授权（Authorization，验证用户是否有权限执行操作）在 Resolver 层或 Schema Directive 层执行，不要在字段解析前做全局粗粒度授权。

- 认证（你是谁）在 HTTP 中间件处理
- 授权（你能做什么）在 Resolver/Directive 处理

### 防止恶意查询

#### 深度限制 + 复杂度限制 + 速率限制

三层防护机制：
1. **深度限制**：阻止过深嵌套
2. **复杂度限制**：阻止计算成本过高的查询
3. **速率限制（Rate Limiting）**：限制单个客户端在时间窗口内的请求次数或总复杂度消耗

推荐基于**复杂度**而非请求数进行速率限制，因为不同查询的成本差异巨大——一个复杂查询的成本可能是简单查询的 1000 倍。

### 禁用内省（生产环境可选）

**内省（Introspection）**：GraphQL 内置功能，允许客户端通过发送特殊查询获取完整的 Schema 信息（类型、字段、参数等）。GraphiQL/Playground 依赖内省来提供文档和自动补全。

在生产环境中，禁用内省可以防止攻击者轻松获取 API 结构，但这不是深度防御——攻击者仍可通过猜测或其他方式探索 API。建议：

- **开发环境**：启用内省和 GraphiQL
- **公开 API**：保留内省（便于开发者使用），配合其他安全措施
- **内部/敏感 API**：考虑禁用内省
- **最佳实践**：即使启用内省，也必须实施深度/复杂度限制和权限控制

**禁用内省配置（graphql-core）**：
```python
from graphql.validation import NoSchemaIntrospectionCustomRule

result = graphql_sync(
    schema,
    query,
    validation_rules=[NoSchemaIntrospectionCustomRule]
)
```

### HTTPS 传输

GraphQL 与 REST 一样，生产环境必须使用 HTTPS 传输：
- 防止中间人攻击窃取认证 Token 和数据
- 防止查询和响应被窃听或篡改
- 配合 HSTS 等安全头增强保护

### 输入验证

GraphQL 的类型系统提供了基础验证（类型是否匹配、必填字段是否提供），但业务逻辑层面的输入验证仍然必要：

- 字符串长度限制
- 邮箱、手机号格式验证
- 数值范围验证
- 枚举值白名单（GraphQL 已自动处理）
- SQL 注入防护：使用参数化查询，不要拼接 SQL 字符串

**注意**：GraphQL 本身不受 SQL 注入直接影响，但 Resolver 中如果拼接 SQL 字符串仍存在风险。使用 ORM 或参数化查询可以避免。

---

## 错误处理最佳实践

GraphQL 的错误处理机制与 REST 有显著区别。REST 使用 HTTP 状态码（200/400/404/500）表示整体请求状态，而 GraphQL 通常始终返回 200 OK，错误通过响应中的 `errors` 数组返回。

### 错误分类

将错误分为两大类，处理方式不同：

| 错误类型 | 说明 | 示例 | errors 数组 |
|----------|------|------|-------------|
| **用户错误（User Error）** | 由用户操作导致的预期内错误，客户端需要处理并展示给用户 | 邮箱已存在、密码错误、权限不足、输入验证失败 | 可以使用，但推荐 Union/Interface |
| **系统错误（System Error）** | 意外的服务端错误，用户无法解决，不应展示详细信息给用户 | 数据库连接失败、内部服务超时、代码 bug | 使用 errors 数组，隐藏细节 |

### 错误信息格式

`errors` 数组中的每个错误对象包含：
- `message`：错误描述（面向开发者）
- `locations`：错误在查询中的位置（行、列）
- `path`：错误在响应中的路径（如 `["users", 0, "email"]`）
- `extensions`：扩展信息（错误码、详细信息等）

**推荐使用 extensions.code 传递机器可读的错误码**：
```json
{
  "errors": [
    {
      "message": "未提供认证令牌",
      "locations": [{ "line": 2, "column": 3 }],
      "path": ["createPost"],
      "extensions": {
        "code": "UNAUTHENTICATED",
        "timestamp": "2026-08-05T10:00:00Z"
      }
    }
  ],
  "data": null
}
```

**常见错误码**：`UNAUTHENTICATED`、`FORBIDDEN`、`NOT_FOUND`、`BAD_USER_INPUT`、`INTERNAL_SERVER_ERROR`、`TOO_MANY_REQUESTS`

### 使用 Union/Interface 处理业务错误

对于业务错误（用户错误），推荐使用 Union 类型将成功结果和错误类型都作为返回类型的一部分，而非依赖 `errors` 数组。这种模式让错误成为 Schema 的显式部分，客户端能清楚地知道哪些操作可能产生哪些错误。

**Union 类型（Union Type）**：GraphQL 类型，表示一个值可以是多个类型中的一种，类似于其他语言中的联合类型。使用 `__typename` 字段区分实际返回的类型。

**SDL 示例**：
```graphql
type Mutation {
  createUser(input: CreateUserInput!): CreateUserResult!
}

union CreateUserResult = CreateUserSuccess | UserAlreadyExistsError | ValidationError | PasswordTooWeakError

type CreateUserSuccess {
  user: User!
}

type UserAlreadyExistsError implements Error {
  message: String!
  email: String!
}

type ValidationError implements Error {
  message: String!
  field: String!
  invalidValue: String
}

type PasswordTooWeakError implements Error {
  message: String!
  minLength: Int!
  requirements: [String!]!
}

interface Error {
  message: String!
}
```

**客户端查询**：
```graphql
mutation {
  createUser(input: { email: "xLi5@MJwnU6R.6dQ", password: "123" }) {
    __typename
    ... on CreateUserSuccess {
      user { id fullName }
    }
    ... on UserAlreadyExistsError {
      message
      email
    }
    ... on ValidationError {
      message
      field
    }
    ... on PasswordTooWeakError {
      message
      requirements
    }
  }
}
```

**这种模式的优势**：
- 错误是 Schema 的显式部分，工具和类型系统能感知
- 每个错误类型可以包含特定的字段（如 `requirements`）
- 客户端必须通过 `__typename` 显式处理每种结果
- 不依赖解析 `errors` 数组中的字符串 message

---

## 工具与开发体验

良好的工具链能显著提升开发效率和代码质量。

### 使用 GraphiQL/Playground 开发调试

**GraphiQL**：GraphQL 官方的浏览器内 IDE，提供交互式文档浏览、查询编辑、语法高亮、自动补全、查询历史等功能。

**GraphQL Playground**：功能更丰富的 GraphQL IDE，基于 GraphiQL 增强，支持多 Tab、HTTP 头配置、查询历史持久化、深色模式等。

开发环境默认开启 GraphiQL/Playground，生产环境可按需关闭。访问地址通常为 `/graphql` 端点的 GET 请求。

### Schema 校验与 Lint

- **构建时校验**：确保 SDL 文件语法正确、没有引用不存在的类型
- **Schema Lint**：使用 `graphql-eslint` 等工具强制执行命名约定、避免反模式、保持 Schema 一致性
- **Schema 差异检查（Schema Diffing）**：在 CI 中检测破坏性变更

### 测试策略

GraphQL 测试分为三个层次：

1. **Resolver 单元测试**：
   - 测试单个 Resolver 的业务逻辑
   - Mock 数据库和外部服务
   - 覆盖各种边界情况

2. **集成测试**：
   - 使用真实（或测试）数据库
   - 通过 HTTP 或直接调用 `graphql()` 函数执行完整查询
   - 测试权限、DataLoader、错误处理等

3. **端到端测试**：
   - 客户端到服务端的完整流程
   - 测试认证、网络、缓存等完整链路

**Python 集成测试示例（strawberry + pytest）**：
```python
from strawberry.test import TestClient

def test_create_user():
    client = TestClient(schema)
    query = """
        mutation {
            createUser(input: { email: "test@example.com", fullName: "Test", password: "secure123" }) {
                __typename
                ... on CreateUserSuccess {
                    user { id email }
                }
            }
        }
    """
    response = client.post("/graphql", json={"query": query})
    data = response.json()
    assert data["data"]["createUser"]["__typename"] == "CreateUserSuccess"
```

### 文档化实践

GraphQL Schema 本身就是自文档化的，但仍需补充额外信息：

- **字段描述**：使用字符串字面量为类型、字段、参数添加描述
- **示例查询**：在文档中提供常用查询和变更的示例
- **迁移指南**：废弃字段时提供清晰的迁移路径
- **认证说明**：说明如何获取和使用认证 Token

**带描述的 SDL 示例**：
```graphql
"""系统用户，表示平台的注册账户。"""
type User {
  """用户唯一标识符，UUID v4 格式。"""
  id: ID!

  """用户全名，显示名称。"""
  fullName: String!

  """用户邮箱地址，登录凭证，全局唯一。"""
  email: String!
}

"""创建新用户的输入参数。"""
input CreateUserInput {
  """用户全名，长度 2-50 个字符。"""
  fullName: String!

  """邮箱地址，必须符合 RFC 5322 格式。"""
  email: String!

  """登录密码，长度至少 8 位，包含字母和数字。"""
  password: String!
}
```

GraphiQL 和 Playground 会自动将这些描述显示在文档面板中。

---

## 常见反模式（Anti-patterns）

以下是 GraphQL 开发中需要避免的常见反模式。

### 反模式 1：过于细粒度的 Resolver 导致 N+1

为每个字段都写一个独立查询数据库的 Resolver，忽视 N+1 问题。

**反模式**：
```python
def resolve_user(root, info, id):
    return db.query("SELECT * FROM users WHERE id = ?", id)

def resolve_posts(user, info):
    return db.query("SELECT * FROM posts WHERE author_id = ?", user.id)

def resolve_comments(post, info):
    return db.query("SELECT * FROM comments WHERE post_id = ?", post.id)
# 查询 { user(id:1) { posts { comments { ... } } } }
# 产生 1 + N + N*M 次查询！
```

**正确做法**：使用 DataLoader 批量加载数据，或使用 ORM 的 eager loading（预加载）机制。

### 反模式 2：将 GraphQL 当作数据库查询语言直接暴露

直接将数据库模型映射为 GraphQL 类型，允许客户端任意查询和关联数据，绕过业务逻辑层。

**反模式**：
```graphql
type Query {
  user(id: ID!): User
  post(id: ID!): Post
  comment(id: ID!): Comment
  table(name: String!): [JSON!]!  # 直接暴露数据库表查询
}
```

**问题**：
- 绕过业务逻辑和权限校验
- 内部数据结构直接暴露，难以演进
- 客户端可能查询到不应暴露的敏感字段
- 无法优化特定查询路径

**正确做法**：
- GraphQL 层作为应用层，不应直接映射数据库表
- 围绕业务用例设计 Query 和 Mutation，而非围绕数据模型
- 在 Resolver 中封装业务逻辑，不直接透传数据库操作

### 反模式 3：忽略缓存策略

完全不做缓存，所有请求都穿透到数据库，导致高并发下数据库成为瓶颈。

**问题**：
- 重复查询相同数据浪费资源
- 响应延迟高
- 数据库连接池耗尽
- 无法应对流量峰值

**正确做法**：
- 使用 DataLoader 进行请求级缓存
- 对热点数据使用 Redis 等分布式缓存
- 客户端使用规范化缓存
- 启用 HTTP/CDN 缓存（配合持久化查询）

### 反模式 4：过度抽象导致 Schema 难以理解

为了"DRY"或"通用性"过度使用接口、联合类型和泛型，导致 Schema 复杂难懂。

**反模式**：
```graphql
interface Node {
  id: ID!
}

interface Entity {
  id: ID!
  attributes: JSON!
  relationships: [Relationship!]!
}

type Relationship {
  type: String!
  target: Entity!
}

type GenericEntity implements Node & Entity {
  id: ID!
  type: String!
  attributes: JSON!
  relationships: [Relationship!]!
}
# 所有实体都变成了 GenericEntity + attributes JSON
# 客户端不知道有哪些可用字段，完全丧失类型安全
```

**问题**：
- Schema 失去自文档化能力
- 客户端无法利用类型系统
- 所有字段变成 JSON 操作，代码维护困难
- GraphiQL 文档毫无帮助

**正确做法**：
- 为每个业务对象定义明确的类型
- 接口用于真正的多态场景（如 `Node`、`Error`），而非为了抽象而抽象
- 优先具体而非通用
- 记住：Schema 是给客户端开发者用的，不是给服务端开发者炫技的

### 反模式 5：返回 200 OK 但在 errors 数组中放所有错误

即使请求完全失败（如语法错误、认证失败）也返回 200，迫使客户端解析 `errors` 数组判断是否成功。部分服务器甚至对每个字段错误都放入 errors，导致 errors 数组充满噪音。

**正确做法**：
- 解析失败（语法错误、验证失败）：返回 400 Bad Request
- 认证失败：返回 401 Unauthorized
- 业务错误（用户输入错误、权限不足）：使用 Union 类型作为 data 返回
- 系统错误：返回 200 + errors 数组（隐藏内部细节），并记录日志

实际上许多 GraphQL 实现默认始终返回 200，这种实践在社区中仍有争议。更实用的做法是：使用 HTTP 状态码表示请求级别错误，使用 Union/errors 数组表示业务/字段级别错误。

---

**上一章**：[Python GraphQL 生态 ←](07-python-ecosystem.md)

**下一章**：[GraphQL 术语表与参考资料 →](11-glossary.md)
