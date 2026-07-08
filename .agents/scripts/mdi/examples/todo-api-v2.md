---
name: todo-api
version: "1.1.0"
description: Simple Todo API v1.1
baseUrl: https://api.example.com
title: "Todo API v1.1"
x-toml-ref: "../../../../.meta/toml/.agents/scripts/mdi/examples/todo-api-v2.toml"
---
# Todo API v1.1

Simple todo management API with create support.

## Interfaces

```{endpoint} GET /todos
:summary: List all todos
:query page: integer - Page number
:query limit: integer - Items per page
:query completed: boolean? - Filter by completion status
:response 200: TodoList - Success
```

```{endpoint} GET /todos/{id}
:summary: Get todo by ID
:path id: string - Todo unique identifier
:response 200: Todo - Success
:error 404: NotFound - Todo not found
```

```{endpoint} POST /todos
:summary: Create a new todo
:body title: string - Todo title
:body completed: boolean? - Initial completion status
:response 201: Todo - Created
:error 400: BadRequest - Invalid input
```
