from mdi.parser import MDIParser


class TestBoundaryCases:

    def test_empty_document_whitespace_only(self, parser):
        doc = parser.parse_text("   \n\n  \n  \n")
        assert doc is not None
        assert doc.title == ""
        assert doc.sections == []
        assert doc.frontmatter == {}

    def test_frontmatter_only_no_body(self, parser):
        text = '---\nname: test\nversion: 1.0.0\n---\n'
        doc = parser.parse_text(text)
        assert doc.frontmatter["name"] == "test"
        assert doc.title == ""
        assert doc.sections == []

    def test_heading_skip_level_h1_to_h3(self, parser):
        text = "# Title\n\n### Skipped H2\n\nContent under H3.\n"
        doc = parser.parse_text(text)
        assert doc.title == "Title"
        h1 = doc.sections[0]
        assert len(h1.subsections) == 1
        h3 = h1.subsections[0]
        assert h3.level == 3
        assert h3.title == "Skipped H2"

    def test_directive_with_code_block_inside(self, parser):
        p = MDIParser(profile_type="webapi")
        text = '''---
name: Test
type: webapi
baseUrl: https://api.example.com
---

# Test

```{endpoint} POST /items
:summary: Create item
:param name: string - Item name
```

```json example
{"name": "test", "id": 1}
```

- [ ] Verify 201 response
'''
        doc = p.parse_text(text)
        assert len(doc.interfaces) == 1
        iface = doc.interfaces[0]
        assert iface.method == "POST"
        assert iface.path == "/items"
        assert len(iface.examples) >= 1
        assert len(iface.check_items) == 1

    def test_directive_empty_body(self, parser):
        p = MDIParser(profile_type="webapi")
        text = '''---
name: Test
type: webapi
baseUrl: https://api.example.com
---

# Test

```{endpoint} GET /ping
```
'''
        doc = p.parse_text(text)
        assert len(doc.interfaces) == 1
        iface = doc.interfaces[0]
        assert iface.method == "GET"
        assert iface.path == "/ping"
        assert iface.summary == ""
        assert iface.parameters == []

    def test_parameter_with_generic_type(self, parser):
        p = MDIParser(profile_type="webapi")
        text = '''---
name: Test
type: webapi
baseUrl: https://api.example.com
---

# Test

```{endpoint} POST /batch
:summary: Batch create
:param items: array<string> - List of item names
:param config: object - Configuration map
```
'''
        doc = p.parse_text(text)
        iface = doc.interfaces[0]
        assert len(iface.parameters) == 2
        items_param = [pp for pp in iface.parameters if pp.name == "items"][0]
        assert items_param.type == "array<string>"
        config_param = [pp for pp in iface.parameters if pp.name == "config"][0]
        assert config_param.type == "object"

    def test_table_cell_with_pipe_escape(self, parser):
        text = "# API\n\n## Params\n\n| Name | Description |\n|------|-------------|\n| expr | Filter expr a\\|b |\n"
        doc = parser.parse_text(text)
        h2 = doc.sections[0].subsections[0]
        assert len(h2.tables) >= 1
        table = h2.tables[0]
        assert len(table["rows"]) >= 1

    def test_code_block_with_triple_backtick_inside(self, parser):
        text = "# Doc\n\n## Example\n\n````markdown\n```python\nprint('nested code block')\n```\n````\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        assert len(h1.subsections) == 1
        h2 = h1.subsections[0]
        assert len(h2.code_blocks) >= 1
        cb = h2.code_blocks[0]
        assert "nested code block" in cb.content

    def test_frontmatter_special_characters(self, parser):
        text = '---\nname: "测试:API/工具"\ndescription: "包含引号、冒号、斜杠/等特殊字符"\n---\n\n# 测试API\n'
        doc = parser.parse_text(text)
        assert doc.frontmatter["name"] == "测试:API/工具"
        assert "特殊字符" in doc.frontmatter["description"]
        assert doc.title == "测试API"

    def test_multiple_consecutive_blank_lines(self, parser):
        text = "# Title\n\n\n\n\n## Section\n\n\nContent with many gaps.\n\n\n\n## Another\n"
        doc = parser.parse_text(text)
        assert doc.title == "Title"
        h1 = doc.sections[0]
        assert len(h1.subsections) == 2
        assert h1.subsections[0].title == "Section"
        assert h1.subsections[1].title == "Another"

    def test_cli_endpoint_with_flags(self, parser):
        p = MDIParser(profile_type="clitool")
        text = '''---
name: Test CLI
type: clitool
description: CLI tool
---

# Test CLI

```{endpoint} CMD run --verbose --output <path>
:summary: Run with verbose output
:param verbose?: flag - Enable verbose mode
:param output: string - Output file path
```
'''
        doc = p.parse_text(text)
        assert len(doc.interfaces) == 1
        iface = doc.interfaces[0]
        assert iface.method == "CMD"
        assert "run" in iface.path
        assert len(iface.parameters) == 2

    def test_deeply_nested_sections_h4_h5(self, parser):
        text = "# Root\n\n## H2\n\n### H3\n\n#### H4\n\n##### H5\n\nDeep content.\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        h2 = h1.subsections[0]
        h3 = h2.subsections[0]
        h4 = h3.subsections[0]
        h5 = h4.subsections[0]
        assert h2.level == 2
        assert h3.level == 3
        assert h4.level == 4
        assert h5.level == 5
        assert h5.title == "H5"
        assert "Deep content" in h5.content

    def test_parameter_with_inline_code_in_description(self, parser):
        p = MDIParser(profile_type="webapi")
        text = '''---
name: Test
type: webapi
baseUrl: https://api.example.com
---

# Test

```{endpoint} POST /data
:param format: string - Output format: `json` or `csv`
```
'''
        doc = p.parse_text(text)
        iface = doc.interfaces[0]
        fmt_param = iface.parameters[0]
        assert fmt_param.name == "format"
        assert "json" in fmt_param.description

    def test_mixed_tabs_and_spaces_indentation(self, parser):
        text = "# Title\n\n## Section\n\n\t- Tab indented\n  - Space indented\n    - Nested\n"
        doc = parser.parse_text(text)
        h2 = doc.sections[0].subsections[0]
        assert len(h2.lists) >= 1
