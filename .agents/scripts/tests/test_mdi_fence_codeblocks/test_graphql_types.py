from .helpers import _parse_doc, _make_graphql_doc_md
from mdi.profiles import GraphQLProfile

class TestGraphQLProfileTypeDetection:
    """测试GraphQLProfile对fence graphql code block中type定义的检测（Rule7）。"""

    def test_rule7_detects_types_in_graphql_fence(self, parser, graphql_profile):
        """Rule7应检测graphql code block中的type定义。"""
        md = _make_graphql_doc_md()
        doc = _parse_doc(parser, md)
        results = graphql_profile.validate(doc)

        typedef_result = next((r for r in results if r.name == "schema:typedef"), None)
        assert typedef_result is not None, "应有schema:typedef验证结果"
        assert typedef_result.passed is True, "有type定义时应通过"
        assert "2" in typedef_result.message
        assert "User" in typedef_result.message
        assert "Post" in typedef_result.message

    def test_rule7_warns_when_no_types(self, parser, graphql_profile):
        """Rule7在没有type定义时应给出info级提示。"""
        no_types_md = """---
name: empty-api
description: Empty API with no type definitions for testing warning.
endpoint: https://api.example.com/graphql
type: graphql
---

# Empty API

## Overview

This document has no GraphQL type definitions.

> **Why?** Testing purposes.

## Queries

```{query} ping
:returns String - pong
```
"""
        doc = _parse_doc(parser, no_types_md)
        results = graphql_profile.validate(doc)

        typedef_result = next((r for r in results if r.name == "schema:typedef"), None)
        assert typedef_result is not None, "应有schema:typedef验证结果"
        assert typedef_result.passed is False, "无type定义时应为未通过（info级）"
        assert typedef_result.severity == "info"



class TestRootTypeValidation:
    """测试Rule7新增的root type（Query/Mutation/Subscription）缺失警告功能。"""

    def test_rule7_warns_missing_query_root_type(self, parser, graphql_profile):
        """当frontmatter声明operations包含query但缺少Query类型时应警告。"""
        missing_query_md = """---
name: missing-query-api
description: API that declares query operation but missing Query root type.
endpoint: https://api.example.com/graphql
type: graphql
operations: [query]
---

# Missing Query API

## Schema

```graphql
type User { id: ID! name: String! }
type Post { id: ID! title: String! }
```
"""
        doc = _parse_doc(parser, missing_query_md)
        results = graphql_profile.validate(doc)

        root_type_warn = next((r for r in results if r.name == "schema:root-types"), None)
        assert root_type_warn is not None, "应产生root-types警告"
        assert root_type_warn.passed is False
        assert root_type_warn.severity == "warning"
        assert "Query" in root_type_warn.message

    def test_rule7_passes_when_all_root_types_present(self, parser, graphql_profile):
        """当声明的operations对应的root types都存在时不应警告。"""
        complete_md = """---
name: complete-api
description: Complete API with all required root types defined.
endpoint: https://api.example.com/graphql
type: graphql
operations: [query, mutation]
---

# Complete API

## Schema

```graphql
type User { id: ID! name: String! }
type Query { user(id: ID!): User }
type Mutation { createUser(name: String!): User }
```
"""
        doc = _parse_doc(parser, complete_md)
        results = graphql_profile.validate(doc)

        root_type_warn = [r for r in results if r.name == "schema:root-types" and not r.passed]
        assert len(root_type_warn) == 0, "所有root type存在时不应有警告"



class TestAdvancedTypeDefinitions:
    """测试GraphQL高级类型定义（input/enum/interface/union）的检测。"""

    def test_rule7_detects_input_enum_interface_union(self, parser, graphql_profile):
        """Rule7应检测input/enum/interface/union类型定义。"""
        advanced_types_md = """---
name: advanced-types-api
description: API with advanced GraphQL type definitions for full coverage.
endpoint: https://api.example.com/graphql
type: graphql
---

# Advanced Types API

## Schema

```graphql
interface Node {
  id: ID!
}

type User implements Node {
  id: ID!
  name: String!
  role: Role
}

enum Role {
  ADMIN
  USER
}

input UserFilter {
  name: String
}

union SearchResult = User | Post
```
"""
        doc = _parse_doc(parser, advanced_types_md)
        results = graphql_profile.validate(doc)

        typedef_result = next((r for r in results if r.name == "schema:typedef"), None)
        assert typedef_result is not None
        assert typedef_result.passed is True
        assert "5" in typedef_result.message, f"应检测到5个类型(Node/User/Role/UserFilter/SearchResult)，实际: {typedef_result.message}"
        assert "Node" in typedef_result.message
        assert "Role" in typedef_result.message
        assert "UserFilter" in typedef_result.message
        assert "SearchResult" in typedef_result.message



class TestDeeplyNestedGraphQLTypes:
    """测试深层嵌套子章节中的graphql type定义检测（Rule7）。"""

    def test_rule7_detects_types_in_deeply_nested_fence(self, parser, graphql_profile):
        """Rule7应能检测H4/H5深层嵌套子章节中的graphql type定义。"""
        nested_types_md = """---
name: nested-types-api
description: GraphQL API with type definitions in deeply nested subsections for testing coverage.
endpoint: https://api.example.com/graphql
type: graphql
---

# Nested Types API

## Schema

### Core Types

#### Domain Objects

```graphql
type User {
  id: ID!
  name: String!
}
```

#### Input Types

```graphql
input CreateUserInput {
  name: String!
  email: String
}
```

### Root Definitions

```graphql
type Query {
  user(id: ID!): User
}
type Mutation {
  createUser(input: CreateUserInput!): User
}
```
"""
        doc = _parse_doc(parser, nested_types_md)
        results = graphql_profile.validate(doc)

        typedef_result = next((r for r in results if r.name == "schema:typedef"), None)
        assert typedef_result is not None
        assert typedef_result.passed is True
        assert "4" in typedef_result.message, f"应检测到4个类型(User/CreateUserInput/Query/Mutation)，实际message: {typedef_result.message}"
        assert "User" in typedef_result.message
        assert "CreateUserInput" in typedef_result.message
        assert "Query" in typedef_result.message
        assert "Mutation" in typedef_result.message



class TestMultipleGraphQLFences:
    """测试同章节/跨章节多个graphql fence的类型合并统计。"""

    def test_rule7_merges_types_from_multiple_fences(self, parser, graphql_profile):
        """Rule7应合并多个graphql fence中检测到的type定义。"""
        multi_fence_md = """---
name: multi-fence-api
description: API with multiple graphql fences spread across sections for testing.
endpoint: https://api.example.com/graphql
type: graphql
---

# Multi Fence API

## Queries

```graphql
type Query {
  ping: String
}
```

## Mutations

```graphql
type Mutation {
  setPing(msg: String!): String
}
```

## Subscriptions

```graphql
type Subscription {
  onPing: String
}
```

## Types

```graphql
type User { id: ID! name: String! }
type Post { id: ID! title: String! }
enum Role { ADMIN USER }
```
"""
        doc = _parse_doc(parser, multi_fence_md)
        results = graphql_profile.validate(doc)

        typedef_result = next((r for r in results if r.name == "schema:typedef"), None)
        assert typedef_result is not None
        assert typedef_result.passed is True
        assert "6" in typedef_result.message, f"应检测到6个类型(Query/Mutation/Subscription/User/Post/Role)，实际message: {typedef_result.message}"
