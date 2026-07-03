from .helpers import _parse_doc, _make_graphql_doc_md
from mdi.profiles import GraphQLProfile

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
