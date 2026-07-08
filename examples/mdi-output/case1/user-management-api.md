---
name: user-management-api
description: 用户管理RESTful API，提供用户的增删改查接口，支持分页查询、条件筛选和批量操作
version: 1.0.0
type: webapi
baseUrl: https://api.example.com/v1
authors:
  - SpecWeave Team
license: MIT
tags:
  - user
  - crud
x-toml-ref: "../../../.meta/toml/examples/mdi-output/case1/user-management-api.toml"
---
# 用户管理 API

提供完整的用户生命周期管理功能，包括用户注册、信息查询、资料更新和账号删除。

# 用户管理 API

提供完整的用户生命周期管理功能，包括用户注册、信息查询、资料更新和账号删除。

## 接口概览

本 API 遵循 RESTful 设计规范，所有接口返回 JSON 格式数据，使用标准 HTTP 状态码表示请求结果。

### 通用说明

- 所有请求需携带 `Authorization: Bearer <token>` 头进行认证
- 请求和响应均使用 `application/json` 格式
- 时间字段统一使用 ISO 8601 格式（如 `2024-01-01T12:00:00Z`）
- 分页接口使用 `page` 和 `page_size` 参数控制

### 错误响应格式

所有错误响应统一格式：

```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "用户不存在",
    "details": {}
  }
}
```

## 接口定义

分页查询用户列表，支持关键词搜索、状态筛选和排序。
**请求示例：**
**响应示例：**
根据用户ID获取单个用户的详细信息。
**响应示例：**
创建新用户账号。创建成功后返回用户完整信息。
**请求示例：**
更新指定用户的信息。仅可修改本人信息，管理员可修改所有用户信息。支持部分更新，仅传递需要修改的字段。
**请求示例：**
删除指定用户账号。此操作不可逆，请谨慎操作。非强制删除时，如果用户有关联数据（如发布的内容、订单等），将返回 409 错误。

```bash
curl "https://api.example.com/v1/users?page=1&page_size=10&status=active" \
  -H "Authorization: Bearer <token>"
```

```json
{
  "total": 156,
  "page": 1,
  "page_size": 10,
  "items": [
    {
      "id": "usr_001",
      "name": "张三",
      "email": "zhangsan@example.com",
      "status": "active",
      "created_at": "2024-01-15T08:30:00Z"
    }
  ]
}
```

```json
{
  "id": "usr_001",
  "name": "张三",
  "email": "zhangsan@example.com",
  "avatar": "https://cdn.example.com/avatars/usr_001.jpg",
  "status": "active",
  "role": "user",
  "bio": "这是用户的个人简介",
  "created_at": "2024-01-15T08:30:00Z",
  "updated_at": "2024-06-01T10:20:00Z"
}
```

```json
{
  "name": "李四",
  "email": "lisi@example.com",
  "password": "SecurePass123",
  "role": "user"
}
```

```json
{
  "name": "李四（已认证）",
  "bio": "更新后的个人简介"
}
```

```directive:endpoint GET /users

```

```directive:endpoint GET /users/{user_id}

```

```directive:endpoint POST /users

```

```directive:endpoint PUT /users/{user_id}

```

```directive:endpoint DELETE /users/{user_id}

```

## 数据模型

### User 对象

| 字段名        | 类型     | 说明                          |
| ---------- | ------ | --------------------------- |
| id         | string | 用户唯一标识，格式：`usr_{随机字符串}`     |
| name       | string | 用户姓名                        |
| email      | string | 邮箱地址                        |
| avatar     | string | 头像URL                       |
| status     | string | 账号状态：active/inactive/banned |
| role       | string | 用户角色：user/admin/moderator   |
| bio        | string | 个人简介                        |
| created_at | string | 创建时间（ISO 8601）              |
| updated_at | string | 更新时间（ISO 8601）              |

### UserListResponse 对象

| 字段名       | 类型          | 说明        |
| --------- | ----------- | --------- |
| total     | integer     | 符合条件的总用户数 |
| page      | integer     | 当前页码      |
| page_size | integer     | 每页数量      |
| items     | array<User> | 用户列表数据    |

### ErrorResponse 对象

| 字段名           | 类型     | 说明     |
| ------------- | ------ | ------ |
| error.code    | string | 错误码    |
| error.message | string | 错误描述   |
| error.details | object | 错误详细信息 |

## API 接口

### `GET /users` /users

**获取用户列表**

#### 参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| page | integer | 否 | 页码，从1开始 |
| page_size | integer | 否 | 每页数量，最大100 |
| keyword | string | 否 | 搜索关键词（用户名/邮箱模糊匹配） |
| status | string | 否 | 用户状态筛选：active/inactive/banned |
| sort_by | string | 否 | 排序字段：created_at/updated_at/name |
| sort_order | string | 否 | 排序方向：asc/desc |

#### 响应

| 状态码 | 描述 |
|--------|------|
| 200 | 用户列表查询成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 权限不足 |

#### 错误码

| 错误码 | 消息 | 描述 |
|--------|------|------|
| 400 |  | 请求参数错误 |
| 401 |  | 未授权 |
| 403 |  | 权限不足 |

```bash
curl "https://api.example.com/v1/users?page=1&page_size=10&status=active" \
  -H "Authorization: Bearer <token>"
```

```json
{
  "total": 156,
  "page": 1,
  "page_size": 10,
  "items": [
    {
      "id": "usr_001",
      "name": "张三",
      "email": "zhangsan@example.com",
      "status": "active",
      "created_at": "2024-01-15T08:30:00Z"
    }
  ]
}
```

### `GET /users/{user_id}` /users/{user_id}

**获取用户详情**

#### 参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| user_id | string | 是 | 用户ID，路径参数 |

#### 响应

| 状态码 | 描述 |
|--------|------|
| 200 | 用户详情查询成功 |
| 401 | 未授权 |
| 403 | 权限不足 |

#### 错误码

| 错误码 | 消息 | 描述 |
|--------|------|------|
| 404 | USER_NOT_FOUND | 用户不存在 |
| 401 |  | 未授权 |
| 403 |  | 权限不足 |

```json
{
  "id": "usr_001",
  "name": "张三",
  "email": "zhangsan@example.com",
  "avatar": "https://cdn.example.com/avatars/usr_001.jpg",
  "status": "active",
  "role": "user",
  "bio": "这是用户的个人简介",
  "created_at": "2024-01-15T08:30:00Z",
  "updated_at": "2024-06-01T10:20:00Z"
}
```

### `POST /users` /users

**创建新用户**

#### 参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| name | string | 是 | 用户姓名，2-50个字符 |
| email | string | 是 | 邮箱地址，需唯一 |
| password | string | 是 | 密码，至少8位，包含大小写字母和数字 |
| avatar | string | 否 | 头像URL |
| role | string | 否 | 用户角色：user/admin/moderator |
| bio | string | 否 | 个人简介，最多200字 |

#### 响应

| 状态码 | 描述 |
|--------|------|
| 201 | 用户创建成功 |
| 400 | 请求参数错误（如邮箱格式错误、密码强度不足） |
| 401 | 未授权 |
| 403 | 权限不足（仅管理员可创建用户） |

#### 错误码

| 错误码 | 消息 | 描述 |
|--------|------|------|
| 409 | EMAIL_ALREADY_EXISTS | 邮箱已被注册 |
| 400 |  | 请求参数错误（如邮箱格式错误、密码强度不足） |
| 401 |  | 未授权 |
| 403 |  | 权限不足（仅管理员可创建用户） |

```json
{
  "name": "李四",
  "email": "lisi@example.com",
  "password": "SecurePass123",
  "role": "user"
}
```

### `PUT /users/{user_id}` /users/{user_id}

**更新用户信息**

#### 参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| user_id | string | 是 | 用户ID，路径参数 |
| name | string | 否 | 用户姓名 |
| email | string | 否 | 邮箱地址 |
| avatar | string | 否 | 头像URL |
| bio | string | 否 | 个人简介 |
| status | string | 否 | 用户状态（仅管理员可修改） |

#### 响应

| 状态码 | 描述 |
|--------|------|
| 200 | 用户信息更新成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 权限不足 |

#### 错误码

| 错误码 | 消息 | 描述 |
|--------|------|------|
| 404 | USER_NOT_FOUND | 用户不存在 |
| 409 | EMAIL_ALREADY_EXISTS | 邮箱已被其他用户使用 |
| 400 |  | 请求参数错误 |
| 401 |  | 未授权 |
| 403 |  | 权限不足 |

```json
{
  "name": "李四（已认证）",
  "bio": "更新后的个人简介"
}
```

### `DELETE /users/{user_id}` /users/{user_id}

**删除用户**

#### 参数

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| user_id | string | 是 | 用户ID，路径参数 |
| force | boolean | 否 | 是否强制删除（跳过二次确认） |

#### 响应

| 状态码 | 描述 |
|--------|------|
| 204 | 用户删除成功（无响应体） |
| 401 | 未授权 |
| 403 | 权限不足 |

#### 错误码

| 错误码 | 消息 | 描述 |
|--------|------|------|
| 404 | USER_NOT_FOUND | 用户不存在 |
| 409 | USER_HAS_DEPENDENCIES | 用户有关联数据无法删除（需先处理关联资源） |
| 401 |  | 未授权 |
| 403 |  | 权限不足 |
