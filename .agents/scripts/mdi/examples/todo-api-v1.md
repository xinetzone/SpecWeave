---
name: todo-api
version: "1.0.0"
description: Simple Todo API v1
baseUrl: https://api.example.com
title: "Todo API v1"
x-toml-ref: "../../../../.meta/toml/.agents/scripts/mdi/examples/todo-api-v1.toml"
---
# Todo API v1

Simple todo management API.

## Interfaces

```{endpoint} GET /todos
:summary: List todos
:query page: integer - Page number
:query limit: integer - Items per page
:response 200: TodoList - Success
```

```{endpoint} GET /todos/{id}
:summary: Get todo by ID
:path id: string - Todo ID
:response 200: Todo - Success
:error 404: NotFound - Todo not found
```
