class TestCodeBlocks:

    def test_code_block_with_language_and_purpose(self, parser):
        text = "# Doc\n\n## Example\n\n```python example\ndef hello():\n    print('hello')\n```\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        h2 = h1.subsections[0]
        assert len(h2.code_blocks) == 1
        cb = h2.code_blocks[0]
        assert cb.language == "python"
        assert cb.purpose == "example"
        assert "hello" in cb.content

    def test_code_block_with_meta_schema(self, parser):
        text = "# Doc\n\n```json schema\n{\"type\": \"object\"}\n```\n"
        doc = parser.parse_text(text)
        cb = doc.sections[0].code_blocks[0]
        assert cb.language == "json"
        assert cb.meta == "schema"
        assert cb.purpose == "schema"

    def test_code_block_no_language(self, parser):
        text = "# Doc\n\n```\nplain text\n```\n"
        doc = parser.parse_text(text)
        cb = doc.sections[0].code_blocks[0]
        assert cb.language == ""
        assert cb.purpose == ""
