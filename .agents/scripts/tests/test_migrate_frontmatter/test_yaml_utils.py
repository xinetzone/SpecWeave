from .conftest import mf


class TestEscapeYamlString:
    def test_plain_string(self):
        assert mf.escape_yaml_string("hello") == '"hello"'

    def test_string_with_colon(self):
        assert mf.escape_yaml_string("a:b") == '"a:b"'

    def test_string_with_hash(self):
        assert mf.escape_yaml_string("text # comment") == '"text # comment"'

    def test_string_with_double_quotes(self):
        result = mf.escape_yaml_string('he said "hi"')
        assert '\\"' in result
        assert result == '"he said \\"hi\\""'

    def test_string_with_backslash(self):
        result = mf.escape_yaml_string("path\\to\\file")
        assert "\\\\" in result

    def test_chinese_characters(self):
        result = mf.escape_yaml_string("中文标题")
        assert result == '"中文标题"'


class TestGenerateYamlFrontmatter:
    def test_basic_with_id(self):
        result = mf.generate_yaml_frontmatter(
            {"id": "test-001"}, ".meta/toml/test.toml"
        )
        assert result.startswith("---\n")
        assert result.endswith("---\n")
        assert 'id: "test-001"' in result
        assert 'x-toml-ref: ".meta/toml/test.toml"' in result

    def test_with_source_field(self):
        result = mf.generate_yaml_frontmatter(
            {"id": "x", "source": "lib/foo.py"}, "ref.toml"
        )
        assert 'source: "lib/foo.py"' in result

    def test_without_id(self):
        result = mf.generate_yaml_frontmatter({"tier": "standard"}, "ref.toml")
        assert "id:" not in result
        assert 'x-toml-ref: "ref.toml"' in result

    def test_always_has_toml_ref(self):
        result = mf.generate_yaml_frontmatter({}, "some/path.toml")
        assert 'x-toml-ref: "some/path.toml"' in result

    def test_format_uses_triple_dash(self):
        result = mf.generate_yaml_frontmatter({"id": "a"}, "r.toml")
        lines = result.strip().split("\n")
        assert lines[0] == "---"
        assert lines[-1] == "---"
