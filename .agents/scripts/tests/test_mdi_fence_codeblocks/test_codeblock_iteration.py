from .helpers import _parse_doc, _make_graphql_doc_md

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
