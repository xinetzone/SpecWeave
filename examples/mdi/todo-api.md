---
name: todo-api
version: 1.0.0
description: 一个简单的待办事项API，用于演示MDI example代码块功能。
type: webapi
baseUrl: https://jsonplaceholder.typicode.com
authors:
  - demo
license: MIT
tags:
  - todo
  - demo
x-toml-ref: "../../.meta/toml/examples/mdi/todo-api.toml"
---
# Todo API

一个简单的待办事项API，用于演示MDI example代码块功能。

## 接口列表

### 获取待办事项

获取单个待办事项。

```{endpoint} GET /todos/{id}
:param id: integer - 待办事项ID，必填
:param completed?: boolean - 是否已完成过滤，可选
:response 200: TodoResponse - 待办事项对象
:error 404: NOT_FOUND - 待办事项不存在
```

```json request
{"completed": true}
```

```json status=200
{
  "id": 1,
  "title": "delectus aut autem",
  "completed": false,
  "userId": 1
}
```

```json status=404
{
  "error": "NOT_FOUND",
  "message": "Todo not found"
}
```

```python example
response = api_client.get(f"{base_url}/todos/1")
assert response.status_code == 200
data = response.json()
assert data["id"] == 1
assert "title" in data
assert isinstance(data["completed"], bool)
```

### 创建待办事项

创建新待办事项。

```{endpoint} POST /todos
:param title: string - 待办标题，必填
:param userId: integer - 用户ID，必填
:param completed?: boolean = false - 是否已完成，可选
:response 201: TodoResponse - 创建成功
:error 400: MISSING_TITLE - 标题不能为空
```

```json request
{
  "title": "Buy milk",
  "userId": 1,
  "completed": false
}
```

```json status=201
{
  "id": 201,
  "title": "Buy milk",
  "userId": 1,
  "completed": false
}
```
