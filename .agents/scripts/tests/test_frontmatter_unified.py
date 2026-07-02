"""lib.frontmatter 统一入口与 x-toml-ref 功能单元测试。"""

import logging
import warnings
from pathlib import Path

import pytest

from lib import frontmatter as fm


class TestExtractAllYamlFields:

    def test_double_quoted_strings(self):
        text = 'source: "README.md#intro"\ntitle: "测试标题"\n'
        result = fm.extract_all_yaml_fields(text)
        assert result["source"] == "README.md#intro"
        assert result["title"] == "测试标题"

    def test_single_quoted_strings(self):
        text = "source: 'README.md#intro'\ntitle: '测试标题'\n"
        result = fm.extract_all_yaml_fields(text)
        assert result["source"] == "README.md#intro"
        assert result["title"] == "测试标题"

    def test_unquoted_scalars(self):
        text = "count: 42\nenabled: true\nname: hello\n"
        result = fm.extract_all_yaml_fields(text)
        assert result["count"] == "42"
        assert result["enabled"] == "true"
        assert result["name"] == "hello"

    def test_inline_list(self):
        text = 'tags: ["a", "b", "c"]\n'
        result = fm.extract_all_yaml_fields(text)
        assert result["tags"] == ["a", "b", "c"]

    def test_inline_list_single_quotes(self):
        text = "tags: ['x', 'y']\n"
        result = fm.extract_all_yaml_fields(text)
        assert result["tags"] == ["x", "y"]

    def test_empty_inline_list(self):
        text = "items: []\n"
        result = fm.extract_all_yaml_fields(text)
        assert result["items"] == []

    def test_chinese_and_special_chars(self):
        text = 'title: "标题：包含冒号"\ndescription: "测试#符号"\n'
        result = fm.extract_all_yaml_fields(text)
        assert result["title"] == "标题：包含冒号"
        assert result["description"] == "测试#符号"

    def test_comments_ignored(self):
        text = 'source: "value"  # 这是注释\ncount: 5 # number\n'
        result = fm.extract_all_yaml_fields(text)
        assert result["source"] == "value"
        assert result["count"] == "5"

    def test_empty_lines_and_comment_lines_skipped(self):
        text = 'source: "a"\n\n# 整行注释\ntitle: "b"\n'
        result = fm.extract_all_yaml_fields(text)
        assert len(result) == 2
        assert result["source"] == "a"
        assert result["title"] == "b"

    def test_mixed_formats(self):
        text = 'source: "doc.md"\ntier: standard\ncount: 3\ntags: ["t1", "t2"]\n'
        result = fm.extract_all_yaml_fields(text)
        assert result["source"] == "doc.md"
        assert result["tier"] == "standard"
        assert result["count"] == "3"
        assert result["tags"] == ["t1", "t2"]


class TestLoadExternalToml:

    def test_load_valid_toml(self, tmp_path):
        toml_file = tmp_path / "meta.toml"
        toml_file.write_text(
            'id = "test-001"\ncategory = "governance"\nversion = 1\n',
            encoding="utf-8"
        )
        result = fm.load_external_toml("meta.toml", tmp_path)
        assert result is not None
        assert result["id"] == "test-001"
        assert result["category"] == "governance"
        assert result["version"] == "1"

    def test_file_not_exist_warning(self, tmp_path, caplog):
        caplog.set_level(logging.WARNING)
        result = fm.load_external_toml("nonexistent.toml", tmp_path)
        assert result is None
        assert "不存在" in caplog.text

    def test_invalid_toml_warning(self, tmp_path, caplog):
        caplog.set_level(logging.WARNING)
        bad_toml = tmp_path / "bad.toml"
        bad_toml.write_text("this is not valid toml = = =\n", encoding="utf-8")
        result = fm.load_external_toml("bad.toml", tmp_path)
        assert result is None
        assert "失败" in caplog.text

    def test_windows_backslash_path(self, tmp_path):
        subdir = tmp_path / "sub"
        subdir.mkdir()
        toml_file = subdir / "meta.toml"
        toml_file.write_text('id = "win-test"\n', encoding="utf-8")
        md_file = tmp_path / "doc.md"
        result = fm.load_external_toml("sub\\meta.toml", tmp_path)
        assert result is not None
        assert result["id"] == "win-test"

    def test_relative_path_deep(self, tmp_path):
        level1 = tmp_path / "a"
        level2 = level1 / "b"
        level2.mkdir(parents=True)
        toml_file = level2 / "meta.toml"
        toml_file.write_text('key = "deep-value"\n', encoding="utf-8")
        result = fm.load_external_toml("a/b/meta.toml", tmp_path)
        assert result is not None
        assert result["key"] == "deep-value"

    def test_list_values_in_toml(self, tmp_path):
        toml_file = tmp_path / "list.toml"
        toml_file.write_text(
            'tags = ["a", "b", "c"]\n',
            encoding="utf-8"
        )
        result = fm.load_external_toml("list.toml", tmp_path)
        assert result is not None
        assert result["tags"] == ["a", "b", "c"]


class TestMergeMetadata:

    def test_yaml_overrides_toml(self):
        yaml_meta = {"id": "yaml-id", "title": "YAML Title"}
        toml_meta = {"id": "toml-id", "category": "gov"}
        result = fm.merge_metadata(yaml_meta, toml_meta)
        assert result["id"] == "yaml-id"
        assert result["title"] == "YAML Title"
        assert result["category"] == "gov"

    def test_toml_none_returns_yaml(self):
        yaml_meta = {"key": "value"}
        result = fm.merge_metadata(yaml_meta, None)
        assert result == {"key": "value"}

    def test_returns_new_dict_no_mutation(self):
        yaml_meta = {"a": "1"}
        toml_meta = {"b": "2"}
        result = fm.merge_metadata(yaml_meta, toml_meta)
        result["c"] = "3"
        assert "c" not in yaml_meta
        assert "c" not in toml_meta

    def test_all_yaml_takes_priority(self):
        yaml_meta = {"x": "yaml-x", "y": "yaml-y"}
        toml_meta = {"x": "toml-x", "y": "toml-y", "z": "toml-z"}
        result = fm.merge_metadata(yaml_meta, toml_meta)
        assert result["x"] == "yaml-x"
        assert result["y"] == "yaml-y"
        assert result["z"] == "toml-z"


class TestParseFrontmatterUnified:

    def test_yaml_no_ref(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            '---\nsource: "README.md"\ntitle: 测试文档\n---\n\n正文\n',
            encoding="utf-8"
        )
        result = fm.parse_frontmatter_unified(md)
        assert result is not None
        assert result["source"] == "README.md"
        assert result["title"] == "测试文档"

    def test_yaml_with_toml_ref(self, tmp_path):
        toml_file = tmp_path / "meta.toml"
        toml_file.write_text(
            'id = "doc-001"\ncategory = "knowledge"\nversion = 2\n',
            encoding="utf-8"
        )
        md = tmp_path / "test.md"
        md.write_text(
            '---\nx-toml-ref: "meta.toml"\ntitle: "覆盖标题"\n---\n\n正文\n',
            encoding="utf-8"
        )
        result = fm.parse_frontmatter_unified(md)
        assert result is not None
        assert result["id"] == "doc-001"
        assert result["category"] == "knowledge"
        assert result["version"] == "2"
        assert result["title"] == "覆盖标题"

    def test_yaml_field_overrides_toml(self, tmp_path):
        toml_file = tmp_path / "meta.toml"
        toml_file.write_text(
            'id = "toml-id"\ntitle = "TOML标题"\ncategory = "test"\n',
            encoding="utf-8"
        )
        md = tmp_path / "test.md"
        md.write_text(
            '---\nx-toml-ref: "meta.toml"\ntitle: "YAML标题"\n---\n\n正文\n',
            encoding="utf-8"
        )
        result = fm.parse_frontmatter_unified(md)
        assert result is not None
        assert result["id"] == "toml-id"
        assert result["title"] == "YAML标题"
        assert result["category"] == "test"

    def test_ref_file_not_exist_returns_yaml(self, tmp_path, caplog):
        caplog.set_level(logging.WARNING)
        md = tmp_path / "test.md"
        md.write_text(
            '---\nx-toml-ref: "missing.toml"\ntitle: "仅YAML"\n---\n\n正文\n',
            encoding="utf-8"
        )
        result = fm.parse_frontmatter_unified(md)
        assert result is not None
        assert result["title"] == "仅YAML"
        assert "不存在" in caplog.text

    def test_ref_toml_invalid_returns_yaml(self, tmp_path, caplog):
        caplog.set_level(logging.WARNING)
        bad_toml = tmp_path / "bad.toml"
        bad_toml.write_text("= invalid toml =", encoding="utf-8")
        md = tmp_path / "test.md"
        md.write_text(
            '---\nx-toml-ref: "bad.toml"\ntitle: "仅YAML"\n---\n\n正文\n',
            encoding="utf-8"
        )
        result = fm.parse_frontmatter_unified(md)
        assert result is not None
        assert result["title"] == "仅YAML"
        assert "失败" in caplog.text

    def test_old_toml_frontmatter_deprecation_warning(self, tmp_path):
        md = tmp_path / "old.md"
        md.write_text(
            '+++\nid = "old-style"\ntier = "standard"\n+++\n\n正文\n',
            encoding="utf-8"
        )
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = fm.parse_frontmatter_unified(md)
            assert result is not None
            assert result["id"] == "old-style"
            assert result["tier"] == "standard"
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "废弃" in str(w[0].message)

    def test_no_frontmatter_returns_none(self, tmp_path):
        md = tmp_path / "plain.md"
        md.write_text("# 普通文档\n\n没有 frontmatter。\n", encoding="utf-8")
        result = fm.parse_frontmatter_unified(md)
        assert result is None

    def test_nonexistent_file_returns_none(self):
        result = fm.parse_frontmatter_unified("/nonexistent/path/file.md")
        assert result is None

    def test_yaml_with_inline_list_and_ref(self, tmp_path):
        toml_file = tmp_path / "meta.toml"
        toml_file.write_text(
            'id = "list-test"\ntags = ["a", "b"]\n',
            encoding="utf-8"
        )
        md = tmp_path / "test.md"
        md.write_text(
            '---\nx-toml-ref: "meta.toml"\nextra_tags: ["c", "d"]\n---\n\n正文\n',
            encoding="utf-8"
        )
        result = fm.parse_frontmatter_unified(md)
        assert result is not None
        assert result["id"] == "list-test"
        assert result["tags"] == ["a", "b"]
        assert result["extra_tags"] == ["c", "d"]

    def test_relative_path_subdirectory(self, tmp_path):
        sub = tmp_path / "docs"
        sub.mkdir()
        toml_file = tmp_path / "shared.toml"
        toml_file.write_text('project = "SpecWeave"\n', encoding="utf-8")
        md = sub / "guide.md"
        md.write_text(
            '---\nx-toml-ref: "../shared.toml"\ntitle: "指南"\n---\n\n正文\n',
            encoding="utf-8"
        )
        result = fm.parse_frontmatter_unified(md)
        assert result is not None
        assert result["project"] == "SpecWeave"
        assert result["title"] == "指南"


class TestBackwardCompatibility:

    def test_existing_functions_still_work(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text('+++\nid = "compat"\ntier = "standard"\n+++\n\n正文\n', encoding="utf-8")
        fm_text = fm.parse_toml_frontmatter(md)
        assert fm_text is not None
        assert fm.extract_frontmatter_field(fm_text, "id") == "compat"
        assert fm.extract_all_fields(fm_text)["tier"] == "standard"
        assert fm.parse_toml_frontmatter_as_dict(md)["id"] == "compat"

    def test_existing_yaml_functions_still_work(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text('---\nsource: "yaml-test"\n---\n\n正文\n', encoding="utf-8")
        yaml_text = fm.parse_yaml_frontmatter(md)
        assert yaml_text is not None
        assert fm.extract_yaml_field(yaml_text, "source") == "yaml-test"
        assert fm.extract_frontmatter_field_from_file(md, "source") == "yaml-test"
