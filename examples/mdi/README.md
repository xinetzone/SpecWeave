# MDI 示例文档集合

本目录包含 Markdown Interface Specification（MDI）规范的完整示例文档，覆盖 Skill、WebApi、CliTool、GraphQL 四种 Profile 类型。每个示例均可直接通过 MDI 工具链进行解析、验证和代码生成。

## 快速开始

使用 MDI CLI 验证任意示例文档：

```bash
cd .agents/scripts
python -m mdi validate ../../examples/mdi/<filename>.md -v
```

批量验证所有示例：

```bash
python -m mdi validate ../../examples/mdi/ --score
```

## 示例索引

### RESTful API（WebApi Profile）

| 文件 | 名称 | 说明 |
|------|------|------|
| [user-api.md](user-api.md) | 用户管理 API | 完整的用户 CRUD RESTful API 示例，包含分页查询、条件筛选、错误码定义 |
| [todo-api.md](todo-api.md) | 待办事项 API | 待办事项管理接口示例 |
| [generate-api.md](generate-api.md) | 生成服务 API | 内容生成服务接口示例 |

### CLI 工具（CliTool Profile）

| 文件 | 名称 | 说明 |
|------|------|------|
| [file-cli.md](file-cli.md) | 文件操作 CLI | 跨平台文件管理命令行工具示例，支持文件列出、复制、删除等操作 |

### GraphQL API（GraphQL Profile）

| 文件 | 语言 | 名称 | 说明 |
|------|------|------|------|
| [graphql-blog.md](graphql-blog.md) | English | Blog GraphQL API | 博客平台 GraphQL API，包含 Query/Mutation/Subscription 完整示例 |
| [graphql-blog-cn.md](graphql-blog-cn.md) | 中文 | 博客平台 GraphQL API | 博客平台 GraphQL API 中文版，演示完整 Schema 定义和操作规范 |

## GraphQL Profile 使用指南

GraphQL Profile 用于定义基于 GraphQL 的 API 接口文档，支持以下核心特性：

### 1. Frontmatter 配置

```yaml
---
name: my-graphql-api
version: "1.0.0"
description: API功能描述
endpoint: https://api.example.com/graphql
type: graphql
authors:
  - Your Name
license: MIT
tags:
  - graphql
---
```

### 2. Schema 类型定义

使用 `` ```graphql `` fence 定义 GraphQL 类型：

````markdown
## Schema 类型定义

### 用户类型

```graphql
type User {
  id: ID!
  username: String!
  email: String!
  createdAt: String!
}
```

### 输入类型

```graphql
input CreateUserInput {
  username: String!
  email: String!
}
```
````

支持的类型关键字：`type`、`input`、`enum`、`interface`、`union`

### 3. 操作定义

使用 directive fence 定义 Query/Mutation/Subscription 操作：

**Query（查询）：**

````markdown
### 获取用户

```{query} getUser
:arg id: ID! - 用户ID
:returns User - 用户对象
:error NOT_FOUND: 用户不存在
```

查询示例：

```graphql
query GetUser($id: ID!) {
  getUser(id: $id) {
    id
    username
    email
  }
}
```
````

**Mutation（变更）：**

````markdown
### 创建用户

```{mutation} createUser
:arg input: CreateUserInput! - 用户数据
:returns User! - 创建的用户
:error UNAUTHORIZED: 未登录
:error VALIDATION_ERROR: 输入无效
```
````

**Subscription（订阅）：**

````markdown
### 用户更新订阅

```{subscription} onUserUpdated
:arg userId: ID! - 订阅的用户ID
:returns User! - 更新后的用户
```
````

### 4. 验证规则

MDI Validator 对 GraphQL Profile 执行以下检查：

| 规则 | 级别 | 说明 |
|------|------|------|
| GQL_frontmatter:name | INFO | 必须设置 name 字段 |
| GQL_frontmatter:description | INFO | 必须设置 description 字段 |
| GQL_frontmatter:endpoint | WARN | 建议设置 endpoint 字段 |
| GQL_section:schema | PASS | 需要包含 Schema 章节 |
| GQL_schema:typedef | PASS | 需要定义 GraphQL 类型（type/input/enum/interface/union） |
| Rule5（Directive命名） | ERROR | 操作名必须符合 GraphQL 命名规范 `^[A-Za-z_][A-Za-z0-9_]*$` |

### 5. 验证结果示例

对 [graphql-blog-cn.md](graphql-blog-cn.md) 执行验证：

```text
[PASS] graphql-blog-cn.md  (91分 profile=graphql)
  ✅ GQL_section:schema: Schema章节已存在
  ✅ GQL_schema:typedef: 检测到 6 个GraphQL类型定义: User, Post, Comment, AuthPayload, PostInput, CommentInput
  ✅ Rule5: 7个directive（3 queries + 3 mutations + 1 subscription），0个命名错误
  ⚠️ W001: 缺少推荐frontmatter字段: 'schemaPath'
```

### 6. 嵌套章节支持

GraphQL Profile 支持任意层级的嵌套章节，验证器会递归遍历所有子章节中的 code blocks：

````markdown
## API 参考

### Schema

#### 核心类型

##### 用户相关

```graphql
type User { id: ID! name: String! }
```

### Operations

#### Queries

##### 文章查询

```{query} getPost
:arg id: ID! - 文章ID
:returns Post - 文章对象
```
````

以上嵌套结构中的 `type` 定义和 `{query}` directive 均可被正确识别和验证。

## 相关资源

- MDI 规范文档：[mdi-spec-v1.0.md](../../docs/knowledge/mdi-spec-v1.0.md)
- MDI 研究报告：[mdi-research/](../../docs/knowledge/mdi-research/)
- MDI 工具源码：[.agents/scripts/mdi/](../../.agents/scripts/mdi/)
- 单元测试：[.agents/scripts/tests/](../../.agents/scripts/tests/)
