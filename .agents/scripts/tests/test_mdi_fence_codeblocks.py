"""MDI Fence Code Block 场景单元测试。

覆盖以下场景：
1. BaseProfile.get_full_text() 正确包含fence header（language+meta）
2. BaseProfile.get_section_content() 正确包含fence header
3. BaseProfile.iter_code_blocks() 正确递归遍历所有code blocks（含子章节）
4. GraphQLProfile Rule5 正确从fence directive code block检测query/mutation/subscription
5. GraphQLProfile Rule5 正确报告命名不规范的directive
6. GraphQLProfile Rule7 正确检测graphql code block中的type定义
7. Profile自动检测能通过fence内容特征识别graphql类型
8. 嵌套子章节中的directive和code block也能被正确遍历
"""

import pytest
from pathlib import Path

from mdi.parser import MDIParser
from mdi.validator import MDIValidator
from mdi.profiles import (
    BaseProfile,
    SkillProfile,
    WebApiProfile,
    CliToolProfile,
    GraphQLProfile,
    detect_profile_type,
    get_profile,
)


@pytest.fixture
def parser():
    return MDIParser()


@pytest.fixture
def validator():
    return MDIValidator()


@pytest.fixture
def graphql_profile():
    return GraphQLProfile()


def _parse_doc(parser, md_text, source_path="<test>"):
    """Helper: parse markdown text and set source_path on doc."""
    doc = parser.parse_text(md_text)
    if source_path:
        doc.source_path = Path(source_path) if source_path != "<test>" else None
    return doc


def _make_graphql_doc_md(
    name: str = "test-graphql-api",
    description: str = "Test GraphQL API for unit testing with enough description length.",
    extra_fm: str = "",
    body: str = "",
) -> str:
    """生成GraphQL MDI文档markdown字符串。"""
    fm = f"""---
name: {name}
version: "1.0.0"
description: "{description}"
endpoint: "https://api.example.com/graphql"
type: graphql
{extra_fm}
---

# {name}

## 1. Overview

This is a test GraphQL API document.

> **Why?** For testing purposes.

## 2. Schema Types

```graphql
type User {{
  id: ID!
  name: String!
  email: String
}}

type Post {{
  id: ID!
  title: String!
  author: User!
}}
```

## 3. Queries

### Get User

```{{query}} getUser
:arg id: ID! - User ID
:returns User - The requested user
```

```graphql
{{{{
  user(id: "123") {{{{
    id
    name
    email
  }}}}
}}}}
```

### List Posts

```{{query}} listPosts
:arg limit: Int - Max posts to return
:returns [Post] - List of posts
```

## 4. Mutations

### Create Post

```{{mutation}} createPost
:arg title: String! - Post title
:arg authorId: ID! - Author user ID
:returns Post - The created post
```

## 5. Subscriptions

### New Post

```{{subscription}} onNewPost
:returns Post - Newly published post
```
"""
    return fm + body


class TestBaseProfileFenceReconstruction:
    """测试BaseProfile的fence重建和code block遍历功能。"""

    def test_get_full_text_includes_directive_fence_header(self, parser, graphql_profile):
        """get_full_text()应包含directive fence的header行，如`{query} getUser`。"""
        md = _make_graphql_doc_md()
        doc = _parse_doc(parser, md)
        full_text = graphql_profile.get_full_text(doc)

        assert "{query} getUser" in full_text, "directive fence header {query} getUser 应出现在full_text中"
        assert "{query} listPosts" in full_text, "directive fence header {query} listPosts 应出现在full_text中"
        assert "{mutation} createPost" in full_text, "directive fence header {mutation} createPost 应出现在full_text中"
        assert "{subscription} onNewPost" in full_text, "directive fence header {subscription} onNewPost 应出现在full_text中"

    def test_get_full_text_includes_graphql_code_block(self, parser, graphql_profile):
        """get_full_text()应包含graphql code block的fence header和内容。"""
        md = _make_graphql_doc_md()
        doc = _parse_doc(parser, md)
        full_text = graphql_profile.get_full_text(doc)

        assert "```graphql" in full_text, "graphql fence header应出现在full_text中"
        assert "type User {" in full_text, "type User 定义应出现在full_text中"
        assert "type Post {" in full_text, "type Post 定义应出现在full_text中"

    def test_get_full_text_wraps_code_blocks_with_fences(self, parser, graphql_profile):
        """get_full_text()应用```包裹code block内容。"""
        md = _make_graphql_doc_md()
        doc = _parse_doc(parser, md)
        full_text = graphql_profile.get_full_text(doc)

        fence_count = full_text.count("```")
        assert fence_count >= 6, f"至少应有6个```标记，实际{fence_count}个"

    def test_get_section_content_includes_fences(self, parser, graphql_profile):
        """get_section_content()应包含fence header和内容。"""
        md = _make_graphql_doc_md()
        doc = _parse_doc(parser, md)
        schema_content = graphql_profile.get_section_content(doc, "schema")

        assert "```graphql" in schema_content, "Schema章节内容应包含graphql fence header"
        assert "type User {" in schema_content, "Schema章节应包含type User定义"

    def test_iter_code_blocks_yields_all_blocks(self, parser, graphql_profile):
        """iter_code_blocks()应遍历所有章节的code blocks（包括子章节中的）。"""
        md = _make_graphql_doc_md()
        doc = _parse_doc(parser, md)

        blocks = list(graphql_profile.iter_code_blocks(doc))
        languages = [cb.language for _, cb in blocks]

        assert len(blocks) >= 5, f"至少应有5个code blocks，实际{len(blocks)}个"
        assert "directive:query" in languages, "应包含directive:query code blocks"
        assert "directive:mutation" in languages, "应包含directive:mutation code blocks"
        assert "directive:subscription" in languages, "应包含directive:subscription code blocks"
        assert "graphql" in languages, "应包含graphql code blocks"

    def test_iter_code_blocks_in_subsections(self, parser, graphql_profile):
        """iter_code_blocks()应递归遍历子章节中的code blocks。"""
        md = _make_graphql_doc_md()
        doc = _parse_doc(parser, md)

        blocks = list(graphql_profile.iter_code_blocks(doc))
        directive_blocks = [(s.title, cb) for s, cb in blocks if cb.language and cb.language.startswith("directive:")]

        query_blocks = [(s, cb) for s, cb in directive_blocks if cb.language == "directive:query"]
        assert len(query_blocks) == 2, f"应找到2个query directive（getUser, listPosts），实际{len(query_blocks)}个"

        mutation_blocks = [(s, cb) for s, cb in directive_blocks if cb.language == "directive:mutation"]
        assert len(mutation_blocks) == 1, f"应找到1个mutation directive（createPost），实际{len(mutation_blocks)}个"

        subscription_blocks = [(s, cb) for s, cb in directive_blocks if cb.language == "directive:subscription"]
        assert len(subscription_blocks) == 1, f"应找到1个subscription directive（onNewPost），实际{len(subscription_blocks)}个"

    def test_format_fence_header_directive(self, graphql_profile):
        """_format_fence_header()应正确格式化directive fence header。"""
        from mdi.models import CodeBlock

        cb = CodeBlock(
            language="directive:query",
            meta="getUser id: ID!",
            content=":arg id: ID!\n:returns User",
            purpose="directive",
        )
        header = graphql_profile._format_fence_header(cb)
        assert header == "{query} getUser id: ID!", f"directive header应为{{query}} getUser id: ID!，实际{header}"

    def test_format_fence_header_plain_code(self, graphql_profile):
        """_format_fence_header()应正确格式化普通code block fence header。"""
        from mdi.models import CodeBlock

        cb = CodeBlock(
            language="graphql",
            meta="",
            content="type User { id: ID! }",
            purpose="example",
        )
        header = graphql_profile._format_fence_header(cb)
        assert header == "graphql", f"plain code header应为'graphql'，实际'{header}'"

    def test_format_fence_header_with_meta(self, graphql_profile):
        """_format_fence_header()应正确格式化带meta的code block。"""
        from mdi.models import CodeBlock

        cb = CodeBlock(
            language="python",
            meta='linenums="true"',
            content="print('hello')",
            purpose="example",
        )
        header = graphql_profile._format_fence_header(cb)
        assert header == 'python linenums="true"', f"带meta的header应为'python linenums=\"true\"'，实际'{header}'"


class TestGraphQLProfileDirectiveValidation:
    """测试GraphQLProfile对fence directive code block的验证逻辑（Rule5）。"""

    def test_rule5_detects_all_directive_types(self, parser, graphql_profile):
        """Rule5应正确统计query/mutation/subscription directive数量。"""
        md = _make_graphql_doc_md()
        doc = _parse_doc(parser, md)
        results = graphql_profile.validate(doc)

        directive_errors = [r for r in results if not r.passed and r.name.startswith("directive:")]
        assert len(directive_errors) == 0, f"命名规范的directive不应有错误，实际{len(directive_errors)}个错误"

    def test_rule5_reports_invalid_directive_names(self, parser, graphql_profile):
        """Rule5应报告不符合GraphQL命名规范的directive名称。"""
        bad_md = """---
name: bad-api
description: Bad API with invalid directive names for testing.
endpoint: https://api.example.com/graphql
type: graphql
---

# Bad API

## Queries

```{query} 123get-user
:arg id: ID!
:returns String
```

```{query} get-user
:returns String
```
"""
        doc = _parse_doc(parser, bad_md)
        results = graphql_profile.validate(doc)

        directive_errors = [r for r in results if not r.passed and r.name.startswith("directive:")]
        assert len(directive_errors) >= 2, f"应有至少2个命名错误（123get-user、get-user含连字符），实际{len(directive_errors)}个"

        error_names = [r.name for r in directive_errors]
        assert any("123get-user" in n for n in error_names), "应报告以数字开头的命名"

    def test_rule5_valid_camelcase_names_pass(self, parser, graphql_profile):
        """Rule5应让符合规范的camelCase/下划线名称通过。"""
        good_md = """---
name: good-api
description: Good API with valid GraphQL directive names for testing.
endpoint: https://api.example.com/graphql
type: graphql
---

# Good API

## Queries

```{query} getUser
:returns String
```

```{query} list_all_posts
:returns [String]
```

```{query} _internalQuery
:returns String
```
"""
        doc = _parse_doc(parser, good_md)
        results = graphql_profile.validate(doc)

        directive_errors = [r for r in results if not r.passed and r.name.startswith("directive:")]
        assert len(directive_errors) == 0, f"camelCase/下划线名称应通过验证，实际有{len(directive_errors)}个错误"


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


class TestProfileDetectionWithFenceContent:
    """测试Profile自动检测对fence code block内容特征的识别。"""

    def test_p4_content_detection_graphql_types(self, parser):
        """P4优先级：内容中包含type Query {/type Mutation {应识别为graphql。"""
        content_md = """---
name: detected-api
description: GraphQL API detected by content features without explicit type.
---

# Detected API

## Schema

```graphql
type Query {
  ping: String
}

type Mutation {
  setMessage(msg: String!): String
}
```

## Queries

```{query} ping
:returns String
```
"""
        doc = _parse_doc(parser, content_md, source_path="test-api.md")
        detected = detect_profile_type(doc, source_path="test-api.md")
        assert detected == "graphql", f"包含type Query/Mutation的文档应检测为graphql，实际为{detected}"

    def test_p1_explicit_type_overrides_content(self, parser):
        """P1优先级：frontmatter.type显式声明应优先于内容特征。"""
        md = """---
name: explicit-skill
description: A skill document with some graphql content.
type: skill
argument-hint: "[test]"
---

# Explicit Skill

Some content that mentions `type Query {` but this is a skill doc.
"""
        doc = _parse_doc(parser, md, source_path="skill-with-graphql-mention.md")
        detected = detect_profile_type(doc, source_path="skill-with-graphql-mention.md")
        assert detected == "skill", "explicit type: skill应优先于内容特征"

    def test_p3_filename_graphql_detection(self, parser):
        """P3优先级：文件名含graphql应识别为graphql。"""
        md = """---
name: file-detected
description: API detected by filename.
---

# File Detected

Some content.
"""
        doc = _parse_doc(parser, md, source_path="graphql-schema.md")
        detected = detect_profile_type(doc, source_path="graphql-schema.md")
        assert detected == "graphql", f"文件名含graphql应检测为graphql，实际为{detected}"


class TestValidatorEndToEndWithFenceBlocks:
    """端到端测试：validator + parser + GraphQLProfile 完整链路验证fence code block场景。"""

    def test_validator_calls_graphql_profile_validate(self, parser, validator):
        """validator应调用GraphQLProfile.validate()并将结果加入report。"""
        md = _make_graphql_doc_md()
        doc = _parse_doc(parser, md, source_path="test_graphql_e2e.md")
        report = validator.validate_document(doc, source_path="test_graphql_e2e.md")

        assert report.profile_type == "graphql", f"应检测为graphql profile，实际为{report.profile_type}"
        assert report.score >= 60, f"完整文档评分应>=60，实际{report.score}"

        gql_issues = [i for i in report.issues if i.code.startswith("GQL_")]
        assert len(gql_issues) > 0, "report中应包含GraphQLProfile验证产生的GQL_*问题"

        gql_pass = [i for i in gql_issues if i.severity == "info"]
        assert len(gql_pass) > 0, "应有info级的GQL_通过项"

    def test_validator_graphql_directives_counted(self, parser, validator):
        """validator端到端验证应正确统计directive数量（通过结果间接验证）。"""
        md = _make_graphql_doc_md()
        doc = _parse_doc(parser, md, source_path="test_directives.md")
        report = validator.validate_document(doc, source_path="test_directives.md")

        assert report.profile_type == "graphql"
        assert report.score > 0, "验证应能正常完成"

    def test_nested_subsection_directives_found(self, parser):
        """嵌套子章节中的directive应被遍历到并验证。"""
        nested_md = """---
name: nested-api
description: GraphQL API with directives in nested subsections for testing.
endpoint: https://api.example.com/graphql
type: graphql
---

# Nested API

## Operations

### Query Operations

#### Get Single Item

```{query} getItem
:arg id: ID!
:returns String
```

### Mutation Operations

#### Create Item

```{mutation} createItem
:arg name: String!
:returns String
```

#### Delete Item

```{mutation} deleteItem
:arg id: ID!
:returns Boolean
```

#### Deep Sub

##### Subscription Deep

```{subscription} onItemCreated
:returns String
```
"""
        doc = _parse_doc(parser, nested_md, source_path="nested-graphql.md")
        profile = GraphQLProfile()
        blocks = list(profile.iter_code_blocks(doc))
        directive_blocks = [cb for _, cb in blocks if cb.language and cb.language.startswith("directive:")]

        assert len(directive_blocks) == 4, f"嵌套子章节中应有4个directive，实际{len(directive_blocks)}个"

        directive_types = [cb.language for cb in directive_blocks]
        assert directive_types.count("directive:query") == 1
        assert directive_types.count("directive:mutation") == 2
        assert directive_types.count("directive:subscription") == 1

        results = profile.validate(doc)
        directive_errors = [r for r in results if not r.passed and r.name.startswith("directive:")]
        assert len(directive_errors) == 0, "所有directive命名都应符合规范"


class TestBackwardCompatibility:
    """确保get_full_text()的fence重建不破坏其他Profile的现有验证。"""

    def test_skill_doc_still_validates(self, parser, validator):
        """Skill profile文档应继续正常验证（不受fence重建影响）。"""
        md = """---
name: test-skill
version: "1.0.0"
description: "当用户提到测试时使用本技能。这是一个足够长的描述用于验证测试。"
argument-hint: "[test]"
user-invocable: true
paths: []
---

# test-skill

## 1. 功能描述

这是测试技能的功能描述。

> **为什么需要此功能？** 为了测试。

## 2. 何时使用

当用户需要测试时使用。

## 3. 核心步骤

1. 步骤一：准备
2. 步骤二：执行
3. 步骤三：**必须**验证结果

> **为什么步骤三必须验证？** 确保操作成功。
"""
        doc = _parse_doc(parser, md, source_path="test-skill.md")
        report = validator.validate_document(doc, source_path="test-skill.md")
        assert report.profile_type == "skill"
        assert report.score > 0, "Skill文档评分应>0"

    def test_webapi_doc_get_full_text_includes_fences(self, parser):
        """WebApiProfile的get_full_text也应包含fence header（一致性测试）。"""
        from mdi.profiles.webapi_profile import WebApiProfile

        md = """---
name: test-api
version: "1.0.0"
description: "Test REST API with enough description for validation."
baseUrl: "https://api.example.com"
type: webapi
---

# Test API

## 1. 概述

Test API overview.

> **为什么？** Testing.

## 2. Endpoints

### Get User

```http
GET /users/{id}
```

```json
{"id": "1", "name": "Test"}
```
"""
        doc = _parse_doc(parser, md, source_path="test-api.md")
        profile = WebApiProfile()
        full_text = profile.get_full_text(doc)

        assert "```http" in full_text, "WebApiProfile的full_text也应包含http fence header"
        assert "GET /users" in full_text, "full_text应包含http请求内容"
        assert "```json" in full_text, "full_text应包含json fence header"


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


class TestDirectiveEdgeCases:
    """测试directive验证的边界情况。"""

    def test_rule5_reports_missing_operation_name(self, parser, graphql_profile):
        """Rule5应报告directive后缺少操作名的情况。"""
        no_name_md = """---
name: no-name-api
description: API with directive that has no operation name for edge case testing.
endpoint: https://api.example.com/graphql
type: graphql
---

# No Name API

## Queries

```{query}
:returns String
```
"""
        doc = _parse_doc(parser, no_name_md)
        results = graphql_profile.validate(doc)

        directive_errors = [r for r in results if not r.passed and r.name.startswith("directive:")]
        assert len(directive_errors) >= 1, "缺少操作名应报告错误"

    def test_rule5_underscore_prefix_allowed(self, parser, graphql_profile):
        """GraphQL允许下划线开头的名称（如_internalQuery）。"""
        underscore_md = """---
name: underscore-api
description: API with underscore-prefixed operation name which is valid GraphQL.
endpoint: https://api.example.com/graphql
type: graphql
---

# Underscore API

## Queries

```{query} _internalQuery
:returns String
```
"""
        doc = _parse_doc(parser, underscore_md)
        results = graphql_profile.validate(doc)

        directive_errors = [r for r in results if not r.passed and r.name.startswith("directive:")]
        assert len(directive_errors) == 0, f"下划线开头的名称应符合GraphQL规范，实际有{len(directive_errors)}个错误"


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


class TestProfileDetectionNestedContent:
    """测试Profile自动检测对嵌套子章节中fence内容的识别。"""

    def test_p4_detects_graphql_in_nested_subsection(self, parser):
        """P4检测应能识别深层嵌套子章节中的graphql type定义。"""
        nested_content_md = """---
name: nested-detected-api
description: GraphQL API with types in nested subsection detected by content.
---

# Detected API

## API Reference

### Schema Definitions

#### Core Schema

```graphql
type Query {
  ping: String
}
```
"""
        doc = _parse_doc(parser, nested_content_md, source_path="nested-detect.md")
        detected = detect_profile_type(doc, source_path="nested-detect.md")
        assert detected == "graphql", f"嵌套子章节中的type Query {{应识别为graphql，实际为{detected}}}"


class TestCliToolBackwardCompat:
    """测试CliToolProfile的fence处理向后兼容性。"""

    def test_clitool_get_full_text_includes_fences(self, parser):
        """CliToolProfile的get_full_text也应包含fence header（一致性测试）。"""
        md = """---
name: test-cli
version: "1.0.0"
description: "Test CLI tool with enough description for validation testing."
type: clitool
---

# Test CLI

## 1. 概述

Test CLI tool.

> **为什么？** Testing.

## 2. 用法

### 基本命令

```bash
mycli run --help
```

```bash
mycli init
```
"""
        doc = _parse_doc(parser, md, source_path="test-cli.md")
        profile = CliToolProfile()
        full_text = profile.get_full_text(doc)

        assert "```bash" in full_text, "CliToolProfile的full_text应包含bash fence header"
        assert "mycli run --help" in full_text, "full_text应包含命令内容"


class TestValidatorReconstructContent:
    """测试validator._reconstruct_content正确包含嵌套code blocks。"""

    def test_reconstruct_content_includes_nested_fences(self, parser, validator):
        """_reconstruct_content应递归包含嵌套子章节中的code blocks。"""
        nested_md = """---
name: reconstruct-test
description: Testing content reconstruction with nested code blocks.
type: graphql
endpoint: https://api.example.com/graphql
---

# Reconstruct Test

## Level1

### Level2

#### Level3

```{query} deepQuery
:returns String
```

```graphql
type DeepType { value: String }
```
"""
        doc = _parse_doc(parser, nested_md, source_path="reconstruct.md")
        reconstructed = validator._reconstruct_content(doc)

        assert "{query} deepQuery" in reconstructed, "重建内容应包含directive fence header"
        assert "```graphql" in reconstructed, "重建内容应包含graphql fence"
        assert "type DeepType" in reconstructed, "重建内容应包含graphql type定义"
        assert "deepQuery" in reconstructed, "重建内容应包含directive内容"


class TestCodeBlockInSubsectionIteration:
    """测试iter_code_blocks遍历普通code block（非directive、非graphql）在嵌套章节。"""

    def test_iter_all_language_types_in_nested_sections(self, parser, graphql_profile):
        """iter_code_blocks应遍历所有类型的code blocks（包括普通python/json等）。"""
        mixed_md = """---
name: mixed-blocks
description: Document with various code block types in nested sections.
endpoint: https://api.example.com/graphql
type: graphql
---

# Mixed Blocks

## Main

### Python Example

```python
def hello():
    print("hello")
```

### JSON Example

```json
{"key": "value"}
```

### Plain Code

```
plain text code block
```
"""
        doc = _parse_doc(parser, mixed_md)
        blocks = list(graphql_profile.iter_code_blocks(doc))

        languages = {(cb.language or "<none>") for _, cb in blocks}
        assert "python" in languages, "应遍历到python code block"
        assert "json" in languages, "应遍历到json code block"
        assert "<none>" in languages, "应遍历到无language的code block"

    def test_empty_code_block_handled(self, parser, graphql_profile):
        """空code block（无内容）也应被遍历到且不报错。"""
        empty_cb_md = """---
name: empty-cb
description: Document with empty code blocks for edge case testing.
endpoint: https://api.example.com/graphql
type: graphql
---

# Empty CB

## Tests

```
```

```graphql
```
"""
        doc = _parse_doc(parser, empty_cb_md)
        blocks = list(graphql_profile.iter_code_blocks(doc))
        assert len(blocks) >= 2, f"应遍历到至少2个空code blocks，实际{len(blocks)}个"
        results = graphql_profile.validate(doc)
        assert any(r.name == "schema:typedef" for r in results), "空graphql fence不应导致崩溃"
