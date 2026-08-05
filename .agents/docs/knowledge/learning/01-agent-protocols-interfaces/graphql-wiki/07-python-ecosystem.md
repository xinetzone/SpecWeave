---
id: "graphql-wiki-python-ecosystem"
title: "Python GraphQL 生态"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/01-agent-protocols-interfaces/graphql-wiki/07-python-ecosystem.toml"
source: "spec:create-graphql-wiki-tutorial"
category: "learning"
tags: ["graphql", "python", "graphene", "strawberry", "ariadne", "fastapi", "django", "flask", "gql-client", "graphql-core"]
date: "2026-08-05"
status: "stable"
author: "SpecWeave"
summary: "Python GraphQL 生态完整指南，涵盖主流服务端框架对比（Graphene、Strawberry、Ariadne）、Web 框架集成（FastAPI、Django、Flask）、客户端库（gql）、底层核心实现与测试工具，包含可运行的 Strawberry+FastAPI 服务端和 gql 客户端完整示例。"
---
# 第 7 章：Python GraphQL 生态

Python 拥有成熟且活跃的 GraphQL 生态系统，提供了从底层核心实现到高层 Web 框架集成的完整工具链。本章将系统介绍 Python 生态中主流的 GraphQL 服务端框架、客户端库、Web 框架集成方案以及相关工具，帮助开发者根据项目需求选择合适的技术栈。

## Python GraphQL 生态概述

Python GraphQL 生态经过多年发展，形成了多层次的工具体系：

- **底层核心**：GraphQL-core 3 提供了 GraphQL 规范的 Python 参考实现，是大多数上层框架的基础
- **服务端框架**：Graphene、Strawberry、Ariadne 三大主流框架，分别采用不同的 Schema 开发模式
- **Web 框架集成**：与 FastAPI、Django、Flask 等主流 Python Web 框架的深度集成
- **客户端库**：gql 等功能完善的 GraphQL 客户端，支持同步和异步操作
- **代码生成**：Ariadne Codegen 等工具可从 Schema 自动生成类型安全的客户端代码
- **测试工具**：提供便捷的 GraphQL API 测试工具和集成测试支持

**Schema First（模式优先）**：一种 GraphQL 开发范式，先使用 GraphQL SDL（Schema Definition Language，模式定义语言）编写类型定义，再为每个字段编写 Resolver 函数实现业务逻辑。Ariadne 是 Schema First 模式的代表。

**Code First（代码优先）**：另一种 GraphQL 开发范式，直接使用编程语言的类型系统和装饰器定义 Schema，无需单独编写 SDL 文件。Strawberry 是 Code First 模式的代表，充分利用 Python 类型注解（type hints）特性。

---

## 主流服务端框架对比

Python 生态中有三个主流的 GraphQL 服务端框架：Graphene、Strawberry 和 Ariadne，它们各有特点，适用于不同的场景。

### Graphene

**Graphene** 是 Python 生态中历史最悠久、最成熟的 GraphQL 框架之一，采用 Code First 开发模式，拥有丰富的生态系统。

**核心特点**：
- 成熟稳定，经过大规模生产环境验证
- 内置 Relay（GraphQL 客户端框架，用于构建数据驱动的 React 应用）支持
- 完善的 Django、SQLAlchemy、MongoEngine 集成
- 强大的类型系统和自定义标量支持
- 社区资源丰富，文档完善

**开发方式**：

Graphene 使用类定义和特殊字段类型来构建 Schema：

```python
import graphene

class Query(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="World"))

    def resolve_hello(self, info, name):
        return f"Hello {name}"

schema = graphene.Schema(query=Query)
result = schema.execute('{ hello }')
print(result.data['hello'])
```

**适用场景**：
- Django 项目（配合 graphene-django）
- 需要 Relay 支持的项目
- 追求稳定性和成熟度的企业级项目
- 已有 SQLAlchemy 等 ORM 的项目

### Strawberry

**Strawberry** 是一个现代的 Code First GraphQL 框架，基于 Python 3.7+ 的类型注解（type hints）设计，注重开发者体验和现代 Python 特性。

**核心特点**：
- 原生支持 Python 类型注解，代码简洁直观
- 完全支持异步（async/await）
- 内置 DataLoader（数据加载器，用于解决 N+1 查询问题）支持
- 与 FastAPI、Starlette、Django、Flask 无缝集成
- 内置支持订阅（Subscription）
- 提供 GraphQL Playground 等开发工具
- 活跃的开发和社区支持

**开发方式**：

Strawberry 使用装饰器和标准 Python 类型注解定义 Schema：

```python
import strawberry

@strawberry.type
class Query:
    @strawberry.field
    def hello(self, name: str = "World") -> str:
        return f"Hello {name}"

schema = strawberry.Schema(query=Query)
```

**适用场景**：
- 新项目优先选择，现代 Python 开发体验
- FastAPI/Starlette 异步项目
- 需要类型安全和良好 IDE 支持的项目
- 微服务架构和云原生应用

### Ariadne

**Ariadne** 是一个轻量级的 Schema First GraphQL 框架，设计理念是与框架无关、易于扩展，专注于提供简洁直观的 API。

**核心特点**：
- 纯 Schema First 开发模式，SDL 与业务逻辑分离
- 轻量级，无过度抽象
- 同时支持同步和异步 Resolver
- 与任何 Web 框架（ASGI/WSGI）兼容
- 内置查询成本验证、性能追踪等实用功能
- API 简单直观，易于扩展和定制

**开发方式**：

Ariadne 要求先定义 SDL，再通过装饰器绑定 Resolver：

```python
from ariadne import ObjectType, gql, make_executable_schema
from ariadne.asgi import GraphQL

type_defs = gql("""
    type Query {
        hello: String!
    }
""")

query_type = ObjectType("Query")

@query_type.field("hello")
def resolve_hello(*_):
    return "Hello world!"

schema = make_executable_schema(type_defs, query_type)
app = GraphQL(schema, debug=True)
```

**适用场景**：
- 偏好 Schema First 开发模式的团队
- 需要与多种 Web 框架集成的项目
- 追求轻量级和灵活性的项目
- 微服务和无服务器（Serverless）架构

### 框架对比表格

| 特性 | Graphene | Strawberry | Ariadne |
|------|----------|------------|---------|
| **开发模式** | Code First（类定义） | Code First（类型注解） | Schema First（SDL） |
| **Python 版本** | Python 3.6+ | Python 3.7+ | Python 3.6+ |
| **异步支持** | 有限支持 | 原生完全支持 | 同步/异步均支持 |
| **类型注解** | 部分使用 | 原生深度集成 | 不依赖 |
| **DataLoader** | 需额外配置 | 内置支持 | 需额外集成 |
| **订阅支持** | 需额外配置 | 原生支持 | 支持 |
| **FastAPI 集成** | 通过第三方库 | 官方原生支持 | ASGI 适配 |
| **Django 集成** | graphene-django（成熟） | strawberry-django | ariadne-django |
| **生态成熟度** | ⭐⭐⭐⭐⭐（最成熟） | ⭐⭐⭐⭐（快速成长） | ⭐⭐⭐（稳定） |
| **学习曲线** | 中等 | 平缓（类型注解友好） | 平缓（SDL 直观） |
| **适用场景** | Django/企业级项目 | 现代异步项目/FastAPI | Schema First 偏好/轻量级 |

---

## 集成框架

Python GraphQL 框架与主流 Web 框架有良好的集成，以下介绍最常用的几种组合。

### Strawberry + FastAPI 集成

**FastAPI** 是一个现代、高性能的 Python Web 框架，基于 Starlette 和 Pydantic，原生支持异步。Strawberry 提供了官方的 FastAPI 集成，是目前最推荐的组合之一。

**安装依赖**：

```bash
pip install strawberry-graphql[fastapi] uvicorn
```

**完整可运行示例（Strawberry + FastAPI）**：

以下是一个完整可运行的最小 GraphQL 服务示例，包含类型定义、Resolver、查询和变更操作：

```python
from typing import List, Optional
import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI

@strawberry.type
class Book:
    id: int
    title: str
    author: str
    year: int

books_db = [
    Book(id=1, title="GraphQL 实战", author="张三", year=2023),
    Book(id=2, title="Python 高级编程", author="李四", year=2022),
    Book(id=3, title="FastAPI 入门到精通", author="王五", year=2024),
]

@strawberry.type
class Query:
    @strawberry.field
    def books(self) -> List[Book]:
        return books_db

    @strawberry.field
    def book(self, id: int) -> Optional[Book]:
        return next((book for book in books_db if book.id == id), None)

@strawberry.type
class Mutation:
    @strawberry.mutation
    def add_book(self, title: str, author: str, year: int) -> Book:
        new_id = max(book.id for book in books_db) + 1 if books_db else 1
        new_book = Book(id=new_id, title=title, author=author, year=year)
        books_db.append(new_book)
        return new_book

schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql_router = GraphQLRouter(schema)

app = FastAPI(title="Python GraphQL 示例")
app.include_router(graphql_router, prefix="/graphql")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**运行服务**：

将代码保存为 `main.py`，执行：

```bash
python main.py
```

服务启动后，访问 `http://localhost:8000/graphql` 即可打开 GraphQL Playground 进行交互式查询测试。

**示例查询**：

```graphql
query GetBooks {
  books {
    id
    title
    author
    year
  }
}

query GetBook {
  book(id: 1) {
    title
    author
  }
}

mutation AddBook {
  addBook(title: "Strawberry 指南", author: "赵六", year: 2025) {
    id
    title
  }
}
```

### Graphene + Django（graphene-django）

**graphene-django** 是 Graphene 提供的 Django 集成包，能够自动将 Django ORM 模型转换为 GraphQL 类型，极大简化了 Django 项目的 GraphQL API 开发。

**特点**：
- 自动从 Django Model 生成 GraphQL 类型
- 内置 Django 权限系统集成
- 支持 Relay 规范的连接和分页
- 提供 Django 管理命令和调试视图
- 支持文件上传

**基本使用方式**：

安装：`pip install graphene-django`

在 `settings.py` 中添加：

```python
INSTALLED_APPS = [
    # ...
    'graphene_django',
]

GRAPHENE = {
    'SCHEMA': 'myproject.schema.schema'
}
```

定义 Schema（`schema.py`）：

```python
import graphene
from graphene_django import DjangoObjectType
from myapp.models import Book

class BookType(DjangoObjectType):
    class Meta:
        model = Book
        fields = ("id", "title", "author", "year")

class Query(graphene.ObjectType):
    all_books = graphene.List(BookType)
    book = graphene.Field(BookType, id=graphene.Int())

    def resolve_all_books(root, info):
        return Book.objects.all()

    def resolve_book(root, info, id):
        return Book.objects.get(pk=id)

schema = graphene.Schema(query=Query)
```

在 `urls.py` 中配置路由：

```python
from django.urls import path
from graphene_django.views import GraphQLView
from .schema import schema

urlpatterns = [
    path("graphql/", GraphQLView.as_view(graphiql=True, schema=schema)),
]
```

### Flask + Ariadne/Graphene 简介

Flask 作为轻量级 Python Web 框架，也可以方便地与 GraphQL 框架集成。

**Flask + Ariadne**：

Ariadne 提供了 WSGI 适配，可以直接与 Flask 集成：

```python
from flask import Flask
from ariadne import ObjectType, gql, make_executable_schema
from ariadne.constants import PLAYGROUND_HTML
from ariadne.explorer import ExplorerGraphiQL

type_defs = gql("""
    type Query {
        hello: String!
    }
""")

query_type = ObjectType("Query")

@query_type.field("hello")
def resolve_hello(*_):
    return "Hello from Flask + Ariadne!"

schema = make_executable_schema(type_defs, query_type)
app = Flask(__name__)

@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return PLAYGROUND_HTML, 200

@app.route("/graphql", methods=["POST"])
def graphql_server():
    from ariadne import graphql_sync
    from flask import request, jsonify

    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code

if __name__ == "__main__":
    app.run(debug=True)
```

**Flask + Graphene**：

使用 `flask-graphql` 包可以快速集成 Graphene：

```bash
pip install flask-graphql graphene
```

```python
from flask import Flask
from graphene import ObjectType, String, Schema
from flask_graphql import GraphQLView

class Query(ObjectType):
    hello = String(name=String(default_value="World"))

    def resolve_hello(self, info, name):
        return f"Hello {name} from Flask!"

schema = Schema(query=Query)

app = Flask(__name__)
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True)
)

if __name__ == "__main__":
    app.run(debug=True)
```

---

## 客户端库

Python 生态中有多个 GraphQL 客户端库，其中 `gql` 是功能最完善、最常用的选择。

### gql：主流 GraphQL 客户端

**gql** 是 Python 生态中最流行的 GraphQL 客户端库，功能全面，支持同步和异步操作，可与多种传输协议（HTTP、WebSocket、Apollo 协议）集成。

**核心特性**：
- 支持同步（requests）和异步（aiohttp、httpx）传输
- 支持 GraphQL 订阅（WebSocket 协议）
- 自动 Schema 验证和查询验证
- 支持文件上传
- 支持动态查询构建
- 与多种传输后端集成

**安装**：

```bash
pip install gql[all]
```

### python-graphql-client：简单轻量级客户端

**python-graphql-client** 是一个更简单、轻量级的 GraphQL 客户端，适合简单的查询场景，API 简洁直观。安装：`pip install python-graphql-client`

### gql 客户端使用示例

以下是一个完整的 gql 客户端示例，连接到前面创建的 Strawberry+FastAPI 服务进行查询和变更操作：

**同步客户端示例**：

```python
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql",
    verify=True,
    retries=3,
)

client = Client(transport=transport, fetch_schema_from_transport=True)

query_get_books = gql("""
    query GetBooks {
        books {
            id
            title
            author
            year
        }
    }
""")

result = client.execute(query_get_books)
print("所有书籍：")
for book in result["books"]:
    print(f"  [{book['id']}] {book['title']} - {book['author']} ({book['year']})")

query_get_book = gql("""
    query GetBook($bookId: Int!) {
        book(id: $bookId) {
            id
            title
            author
            year
        }
    }
""")

params = {"bookId": 1}
result = client.execute(query_get_book, variable_values=params)
if result["book"]:
    book = result["book"]
    print(f"\n查询书籍 ID=1：{book['title']} - {book['author']}")

mutation_add_book = gql("""
    mutation AddBook($title: String!, $author: String!, $year: Int!) {
        addBook(title: $title, author: $author, year: $year) {
            id
            title
            author
            year
        }
    }
""")

params = {
    "title": "GraphQL 客户端指南",
    "author": "测试作者",
    "year": 2026
}
result = client.execute(mutation_add_book, variable_values=params)
new_book = result["addBook"]
print(f"\n新增书籍：ID={new_book['id']}, {new_book['title']}")
```

**异步客户端示例**：

```python
import asyncio
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

async def main():
    transport = AIOHTTPTransport(url="http://localhost:8000/graphql")

    async with Client(
        transport=transport,
        fetch_schema_from_transport=True,
    ) as session:
        query = gql("""
            query GetBooks {
                books {
                    id
                    title
                    author
                }
            }
        """)

        result = await session.execute(query)
        print("异步查询结果：")
        for book in result["books"]:
            print(f"  {book['title']}")

asyncio.run(main())
```

**运行说明**：
1. 先启动前面的 Strawberry+FastAPI 服务（`python main.py`）
2. 将客户端代码保存为 `client.py`
3. 执行 `python client.py` 即可看到查询结果

---

## 其他工具

### GraphQL-core 3：底层 GraphQL 核心实现

**GraphQL-core 3** 是 GraphQL 规范在 Python 中的参考实现，是 Graphene、Ariadne、Strawberry 等上层框架的底层依赖。它提供了 GraphQL 的核心功能，包括查询解析、验证、执行等，但不直接提供 Web 框架集成或便捷的 Schema 定义 API。

**使用场景**：
- 构建自定义 GraphQL 框架或工具
- 需要精细控制 GraphQL 执行过程
- 研究 GraphQL 规范的实现细节

**基本使用示例**：

```python
from graphql import graphql_sync, build_schema

schema = build_schema("""
    type Query {
        hello: String
    }
""")

def resolve_hello(root, info):
    return "Hello from GraphQL-core!"

schema.query_type.fields["hello"].resolve = resolve_hello

result = graphql_sync(schema, "{ hello }")
print(result.data)
```

安装：`pip install graphql-core`

### Strawberry GraphQL 的集成工具

Strawberry 提供了一系列配套工具提升开发体验：

- **strawberry-django**：Django 深度集成，支持 ORM 类型自动映射
- **strawberry-fastapi**：FastAPI 官方集成（本章节示例使用）
- **strawberry-sqlalchemy**：SQLAlchemy ORM 集成
- **strawberry-cli**：命令行工具，支持代码生成和服务启动
- **strawberry-graphql-dataloader**：DataLoader 实现，解决 N+1 问题
- **strawberry-extensions**： Apollo Tracing、性能分析等扩展

**Ariadne Codegen**：Ariadne 提供的代码生成工具，可以从远程 GraphQL Schema 自动生成类型安全的 Python 客户端代码，避免手动编写查询和类型定义：

```bash
pip install ariadne-codegen
```

配置 `pyproject.toml`：

```toml
[ariadne-codegen]
queries_path = "queries.graphql"
remote_schema_url = "http://localhost:8000/graphql"
```

执行生成：

```bash
ariadne-codegen
```

### 测试工具

GraphQL API 的测试可以使用多种工具：

1. **GraphQL Playground / GraphiQL**：浏览器内置的交互式 IDE，可手动编写和测试查询，Strawberry 和 Ariadne 都内置支持
2. **pytest + 框架测试客户端**：使用 pytest 结合框架提供的测试工具编写集成测试
3. **schemathesis**：基于属性的 API 测试工具，可自动生成测试用例验证 GraphQL API
4. **gql 客户端**：在单元测试中直接使用 gql 客户端发起请求验证结果

**Strawberry 测试示例**：

```python
from strawberry.test import TestClient
from main import schema

client = TestClient(schema)

def test_get_books():
    query = """
        query {
            books {
                id
                title
            }
        }
    """
    result = client.execute(query)
    assert result.errors is None
    assert len(result.data["books"]) > 0
```

---

**上一章**：[GraphQL 服务端核心概念 ←](06-server-concepts.md)

**下一章**：[GraphQL 最佳实践 →](08-best-practices.md)
