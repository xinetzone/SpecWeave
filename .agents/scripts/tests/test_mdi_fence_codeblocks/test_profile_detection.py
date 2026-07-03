from .helpers import _parse_doc, _make_graphql_doc_md
from mdi.profiles import detect_profile_type

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
