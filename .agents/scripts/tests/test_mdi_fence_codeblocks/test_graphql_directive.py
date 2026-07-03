from .helpers import _parse_doc, _make_graphql_doc_md

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
