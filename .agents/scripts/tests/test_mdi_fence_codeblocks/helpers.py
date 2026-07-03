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
