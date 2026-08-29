---
name: generate-api
description: 数据生成API，提供数据查询接口
version: 1.0.0
type: webapi
baseUrl: https://api.example.com/v1
title: "数据生成 API"
category: examples
source: "examples/mdi/generate-api.md"
authors:
  - SpecWeave Team
license: MIT
tags:
  - data
  - query
  - mdi-example
x-toml-ref: "../../../../../.meta/toml/.agents/docs/knowledge/mdi/examples/generate-api.toml"
---
# 数据生成 API

提供数据查询功能，根据ID获取对应的数据对象。

## 接口定义

```{endpoint} GET /data
:summary: 获取数据
:tags: data
:param id: string - 数据ID，必填
:param format?: string = json - 返回格式：json/xml
:response 200: DataResponse - 数据查询成功
:response 400: ErrorResponse - 请求参数错误
:response 401: ErrorResponse - 未授权
:error 404: DATA_NOT_FOUND - 数据不存在
```

根据传入的ID查询并返回对应的数据对象。

**请求示例：**

```bash
curl "https://api.example.com/v1/data?id=data_001" \
  -H "Authorization: Bearer <token>"
```

**响应示例：**

```json
{
  "id": "data_001",
  "name": "示例数据",
  "content": "这是数据内容",
  "created_at": "2024-01-15T08:30:00Z"
}
```

## 数据模型

### DataResponse 对象

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | string | 数据唯一标识 |
| name | string | 数据名称 |
| content | string | 数据内容 |
| created_at | string | 创建时间（ISO 8601） |

### ErrorResponse 对象

| 字段名 | 类型 | 说明 |
|--------|------|------|
| error.code | string | 错误码 |
| error.message | string | 错误描述 |
| error.details | object | 错误详细信息 |
