"""lib.frontmatter 单元测试。"""

from pathlib import Path

import pytest

from lib import frontmatter as fm


class TestParseTomlFrontmatter:

    def test_valid_frontmatter(self, tmp_path):
        p = tmp_path / "test.md"
        p.write_text("+++\nid = \"x\"\ntier = \"standard\"\n+++\n\n# Body\n", encoding="utf-8")
        result = fm.parse_toml_frontmatter(p)
        assert result is not None
        assert 'id = "x"' in result
        assert 'tier = "standard"' in result

    def test_no_frontmatter_returns_none(self, tmp_path):
        p = tmp_path / "test.md"
        p.write_text("# No frontmatter\n", encoding="utf-8")
        assert fm.parse_toml_frontmatter(p) is None

    def test_os_error_returns_none(self):
        assert fm.parse_toml_frontmatter("/nonexistent/path/file.md") is None

    def test_frontmatter_at_start(self, tmp_path):
        """frontmatter 必须从文件第一行开始。"""
        p = tmp_path / "test.md"
        p.write_text("# Title\n+++\nid = \"x\"\n+++\n", encoding="utf-8")
        assert fm.parse_toml_frontmatter(p) is None

    def test_strips_delimiters(self, tmp_path):
        p = tmp_path / "test.md"
        p.write_text("+++\nkey = \"val\"\n+++\n", encoding="utf-8")
        result = fm.parse_toml_frontmatter(p)
        assert result == 'key = "val"'


class TestExtractFrontmatterField:

    def test_quoted_value(self):
        text = 'id = "developer"\ntier = "standard"\n'
        assert fm.extract_frontmatter_field(text, "id") == "developer"
        assert fm.extract_frontmatter_field(text, "tier") == "standard"

    def test_unquoted_value(self):
        text = "validation_count = 3\nreuse_count = 1\n"
        assert fm.extract_frontmatter_field(text, "validation_count") == "3"
        assert fm.extract_frontmatter_field(text, "reuse_count") == "1"

    def test_missing_field_returns_none(self):
        text = 'id = "x"\n'
        assert fm.extract_frontmatter_field(text, "nonexistent") is None

    def test_mixed_quoted_and_unquoted(self):
        text = 'id = "test"\ncount = 5\nname = "hello"\n'
        assert fm.extract_frontmatter_field(text, "id") == "test"
        assert fm.extract_frontmatter_field(text, "count") == "5"
        assert fm.extract_frontmatter_field(text, "name") == "hello"

    def test_quoted_takes_priority(self):
        """带引号值优先于无引号值。"""
        text = 'tier = "co-founder"\n'
        assert fm.extract_frontmatter_field(text, "tier") == "co-founder"


class TestExtractAllFields:

    def test_extracts_all_fields(self):
        text = 'id = "dev"\ntier = "standard"\nvalidation_count = 2\n'
        result = fm.extract_all_fields(text)
        assert result["id"] == "dev"
        assert result["tier"] == "standard"
        assert result["validation_count"] == "2"

    def test_empty_frontmatter(self):
        assert fm.extract_all_fields("") == {}

    def test_mixed_formats(self):
        text = 'domain = "governance"\ncount = 10\n'
        result = fm.extract_all_fields(text)
        assert len(result) == 2
        assert result["domain"] == "governance"
        assert result["count"] == "10"


class TestParseTomlFrontmatterAsDict:

    def test_valid_file_returns_dict(self, tmp_path):
        p = tmp_path / "test.md"
        p.write_text('+++\nid = "x"\ntier = "standard"\ncount = 3\n+++\n\n# Body\n', encoding="utf-8")
        result = fm.parse_toml_frontmatter_as_dict(p)
        assert result is not None
        assert result["id"] == "x"
        assert result["tier"] == "standard"
        assert result["count"] == "3"

    def test_no_frontmatter_returns_none(self, tmp_path):
        p = tmp_path / "test.md"
        p.write_text("# No frontmatter\n", encoding="utf-8")
        assert fm.parse_toml_frontmatter_as_dict(p) is None

    def test_nonexistent_file_returns_none(self):
        assert fm.parse_toml_frontmatter_as_dict("/nonexistent/file.md") is None

    def test_equivalent_to_two_step(self, tmp_path):
        """便捷函数等价于 parse + extract_all_fields 两步调用。"""
        p = tmp_path / "test.md"
        p.write_text('+++\nid = "dev"\nvalidation_count = 4\n+++\n', encoding="utf-8")
        direct = fm.parse_toml_frontmatter_as_dict(p)
        two_step = fm.extract_all_fields(fm.parse_toml_frontmatter(p))
        assert direct == two_step


class TestParseYamlFrontmatter:

    def test_valid_frontmatter(self, tmp_path):
        p = tmp_path / "test.md"
        p.write_text("---\nsource: \"README.md#intro\"\ntitle: 测试\n---\n\n# Body\n", encoding="utf-8")
        result = fm.parse_yaml_frontmatter(p)
        assert result is not None
        assert 'source: "README.md#intro"' in result
        assert "title: 测试" in result

    def test_no_frontmatter_returns_none(self, tmp_path):
        p = tmp_path / "test.md"
        p.write_text("# No frontmatter\n", encoding="utf-8")
        assert fm.parse_yaml_frontmatter(p) is None

    def test_os_error_returns_none(self):
        assert fm.parse_yaml_frontmatter("/nonexistent/path/file.md") is None

    def test_frontmatter_at_start(self, tmp_path):
        """frontmatter 必须从文件第一行开始。"""
        p = tmp_path / "test.md"
        p.write_text("# Title\n---\nsource: x\n---\n", encoding="utf-8")
        assert fm.parse_yaml_frontmatter(p) is None

    def test_strips_delimiters(self, tmp_path):
        p = tmp_path / "test.md"
        p.write_text("---\nkey: val\n---\n", encoding="utf-8")
        result = fm.parse_yaml_frontmatter(p)
        assert result == "key: val"

    def test_does_not_match_toml(self, tmp_path):
        """YAML 解析器不应误识别 TOML frontmatter。"""
        p = tmp_path / "test.md"
        p.write_text('+++\nid = "x"\n+++\n', encoding="utf-8")
        assert fm.parse_yaml_frontmatter(p) is None


class TestExtractYamlField:

    def test_double_quoted_value(self):
        text = 'source: "README.md#intro"\n'
        assert fm.extract_yaml_field(text, "source") == "README.md#intro"

    def test_single_quoted_value(self):
        text = "source: 'README.md#intro'\n"
        assert fm.extract_yaml_field(text, "source") == "README.md#intro"

    def test_unquoted_scalar(self):
        text = "title: 测试标题\n"
        assert fm.extract_yaml_field(text, "title") == "测试标题"

    def test_missing_field_returns_none(self):
        text = 'source: "x"\n'
        assert fm.extract_yaml_field(text, "nonexistent") is None

    def test_mixed_quoted_styles(self):
        text = 'source: "a.md#x"\ntitle: \'标题\'\ncount: 5\n'
        assert fm.extract_yaml_field(text, "source") == "a.md#x"
        assert fm.extract_yaml_field(text, "title") == "标题"
        assert fm.extract_yaml_field(text, "count") == "5"

    def test_field_with_spaces_around_colon(self):
        text = 'source   :   "README.md"\n'
        assert fm.extract_yaml_field(text, "source") == "README.md"

    def test_field_with_trailing_spaces(self):
        text = 'source: "README.md"   \n'
        assert fm.extract_yaml_field(text, "source") == "README.md"


class TestExtractFrontmatterFieldFromFile:

    def test_toml_file(self, tmp_path):
        p = tmp_path / "test.md"
        p.write_text('+++\nsource = "README.md#toml"\n+++\n', encoding="utf-8")
        assert fm.extract_frontmatter_field_from_file(p, "source") == "README.md#toml"

    def test_yaml_file(self, tmp_path):
        p = tmp_path / "test.md"
        p.write_text('---\nsource: "README.md#yaml"\n---\n', encoding="utf-8")
        assert fm.extract_frontmatter_field_from_file(p, "source") == "README.md#yaml"

    def test_yaml_file_unquoted(self, tmp_path):
        p = tmp_path / "test.md"
        p.write_text("---\nsource: README.md#yaml-unquoted\n---\n", encoding="utf-8")
        assert fm.extract_frontmatter_field_from_file(p, "source") == "README.md#yaml-unquoted"

    def test_yaml_unquoted_hash_without_preceding_space_is_value(self):
        result = fm.extract_yaml_field("source: C#-lang\n", "source")
        assert result == "C#-lang"

    def test_yaml_unquoted_hash_with_preceding_space_is_comment(self):
        result = fm.extract_yaml_field("source: value # real comment\n", "source")
        assert result == "value"

    def test_yaml_unquoted_hash_mid_word_is_value(self):
        result = fm.extract_yaml_field("source: hello#world\n", "source")
        assert result == "hello#world"

    def test_yaml_unquoted_trailing_spaces_stripped(self):
        result = fm.extract_yaml_field("source: my-value   \n", "source")
        assert result == "my-value"

    def test_no_frontmatter_returns_none(self, tmp_path):
        p = tmp_path / "test.md"
        p.write_text("# No frontmatter\n", encoding="utf-8")
        assert fm.extract_frontmatter_field_from_file(p, "source") is None

    def test_no_target_field_returns_none(self, tmp_path):
        p = tmp_path / "test.md"
        p.write_text('+++\nother = "value"\n+++\n', encoding="utf-8")
        assert fm.extract_frontmatter_field_from_file(p, "source") is None

    def test_toml_takes_priority(self, tmp_path):
        """TOML 优先于 YAML（文件不可能同时有两种 frontmatter，此处仅验证优先级）。"""
        p = tmp_path / "test.md"
        p.write_text('+++\nsource = "from-toml"\n+++\n', encoding="utf-8")
        assert fm.extract_frontmatter_field_from_file(p, "source") == "from-toml"

    def test_nonexistent_file_returns_none(self):
        assert fm.extract_frontmatter_field_from_file("/nonexistent/file.md", "source") is None
