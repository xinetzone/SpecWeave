---
name: graphql-blog-cn
version: "1.0.0"
description: 博客平台GraphQL API中文示例，演示文章、评论、用户管理及实时订阅功能，包含完整Schema定义和操作示例
endpoint: https://api.example.com/graphql
schemaPath: inline
type: graphql
title: "博客平台 GraphQL API"
x-toml-ref: "../../.meta/toml/examples/mdi/graphql-blog-cn.toml"
authors:
  - SpecWeave Team
license: MIT
tags:
  - graphql
  - blog
  - api
---
# 博客平台 GraphQL API

基于 GraphQL 的博客平台接口，提供文章发布、评论互动、用户认证、实时订阅等完整功能。

## 概述

本 API 遵循标准 GraphQL 规范：
- 单一端点：`/graphql`
- Query 用于数据读取
- Mutation 用于数据写入
- Subscription 用于实时更新
- 使用 JWT Bearer Token 进行身份认证

### 认证方式

所有 Mutation 和受保护的 Query 需要携带有效的 JWT Token：

```
Authorization: Bearer <jwt_token>
```

公开查询（getPost、listPosts）无需认证。

### 错误码说明

错误遵循标准 GraphQL 错误格式，通过 `extensions.code` 提供机器可读的错误类型：

| 错误码 | 含义 |
|--------|------|
| UNAUTHORIZED | 缺少或无效的 JWT Token |
| FORBIDDEN | 权限不足 |
| NOT_FOUND | 请求的资源不存在 |
| VALIDATION_ERROR | 输入参数验证失败 |
| RATE_LIMITED | 请求过于频繁 |

## Schema 类型定义

### 核心类型定义

```graphql
type User {
  id: ID!
  username: String!
  email: String!
  displayName: String
  avatarUrl: String
  createdAt: String!
  posts: [Post!]!
}

type Post {
  id: ID!
  title: String!
  content: String!
  excerpt: String
  author: User!
  published: Boolean!
  tags: [String!]!
  comments: [Comment!]!
  createdAt: String!
  updatedAt: String
}

type Comment {
  id: ID!
  content: String!
  author: User!
  post: Post!
  createdAt: String!
}
```

### 认证与输入类型

```graphql
type AuthPayload {
  token: String!
  user: User!
}

input PostInput {
  title: String!
  content: String!
  excerpt: String
  tags: [String!]
  published: Boolean
}

input CommentInput {
  content: String!
}
```

## 接口定义

### Query（查询操作）

#### 获取单篇文章

根据文章 ID 获取文章详情，包含作者和评论信息。

```{query} getPost
:arg id: ID! - 文章唯一标识
:returns Post - 文章对象
:error NOT_FOUND: 文章不存在
```

查询示例：

```graphql
query GetPost($id: ID!) {
  getPost(id: $id) {
    id
    title
    content
    author {
      username
      displayName
    }
    comments {
      id
      content
      author {
        username
      }
    }
    createdAt
  }
}
```

响应示例：

```json
{
  "data": {
    "getPost": {
      "id": "post_123",
      "title": "GraphQL 入门指南",
      "content": "GraphQL 是一种用于 API 的查询语言...",
      "author": {
        "username": "zhang_san",
        "displayName": "张三"
      },
      "comments": [],
      "createdAt": "2026-07-01T10:00:00Z"
    }
  }
}
```

#### 获取文章列表

分页获取文章列表，支持标签和作者筛选。

```{query} listPosts
:arg page?: Int = 1 - 页码
:arg limit?: Int = 10 - 每页数量（最大50）
:arg tag?: String - 按标签筛选
:arg authorId?: ID - 按作者ID筛选
:returns [Post!]! - 分页文章列表
```

查询示例：

```graphql
query ListPosts($page: Int, $limit: Int, $tag: String) {
  listPosts(page: $page, limit: $limit, tag: $tag) {
    id
    title
    excerpt
    author {
      username
    }
    tags
    published
    createdAt
  }
}
```

#### 获取当前用户信息

获取当前已认证用户的个人资料。

```{query} me
:returns User - 当前用户信息
:error UNAUTHORIZED: 未登录
```

### Mutation（变更操作）

#### 用户登录

验证用户名密码并返回 JWT Token。

```{mutation} login
:arg username: String! - 用户名或邮箱
:arg password: String! - 密码
:returns AuthPayload! - JWT Token 和用户信息
:error INVALID_CREDENTIALS: 用户名或密码错误
:error TOO_MANY_REQUESTS: 请求频率限制
```

请求示例：

```graphql
mutation Login($username: String!, $password: String!) {
  login(username: $username, password: $password) {
    token
    user {
      id
      username
      email
      displayName
    }
  }
}
```

变量示例：

```json
{
  "username": "zhang_san",
  "password": "my_secure_password"
}
```

响应示例：

```json
{
  "data": {
    "login": {
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "user": {
        "id": "user_789",
        "username": "zhang_san",
        "email": "zhangsan@example.com",
        "displayName": "张三"
      }
    }
  }
}
```

#### 创建文章

创建新的博客文章（需要认证）。

```{mutation} createPost
:arg input: PostInput! - 文章数据
:returns Post! - 创建的文章
:error UNAUTHORIZED: 未登录
:error VALIDATION_ERROR: 输入数据无效
```

请求示例：

```graphql
mutation CreatePost($input: PostInput!) {
  createPost(input: $input) {
    id
    title
    content
    author {
      username
    }
    published
    createdAt
  }
}
```

变量示例：

```json
{
  "input": {
    "title": "MDI 快速入门",
    "content": "MDI (Markdown Interface) 是一种新型的API定义方式...",
    "excerpt": "MDI 概念介绍",
    "tags": ["api", "markdown", "mdi"],
    "published": true
  }
}
```

#### 添加评论

为文章添加评论（需要认证）。

```{mutation} addComment
:arg postId: ID! - 评论的目标文章ID
:arg input: CommentInput! - 评论内容
:returns Comment! - 创建的评论
:error UNAUTHORIZED: 未登录
:error NOT_FOUND: 文章不存在
```

### Subscription（订阅操作）

#### 新评论实时通知

订阅指定文章的新评论实时推送。

```{subscription} onNewComment
:arg postId: ID! - 订阅的文章ID
:returns Comment! - 新添加的评论
```

订阅示例：

```graphql
subscription OnNewComment($postId: ID!) {
  onNewComment(postId: $postId) {
    id
    content
    author {
      username
      displayName
    }
    createdAt
  }
}
```

## 测试检查清单

- [x] 登录 mutation 使用正确凭据返回有效 JWT Token
- [x] 登录 mutation 使用错误密码返回 INVALID_CREDENTIALS 错误
- [x] getPost 使用有效ID返回文章数据
- [x] getPost 使用不存在的ID返回 NOT_FOUND 错误
- [x] listPosts 默认分页返回文章数组
- [x] createPost 需要认证
- [x] createPost 空标题返回 VALIDATION_ERROR
- [x] me 查询未携带Token返回 UNAUTHORIZED
- [ ] 订阅实时功能验证
- [ ] 频率限制验证
- [ ] 复杂嵌套查询性能测试
