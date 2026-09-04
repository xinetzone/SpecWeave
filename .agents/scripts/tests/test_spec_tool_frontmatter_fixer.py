"""spec_tool.frontmatter_fixer 单元测试。

覆盖 frontmatter 解析、status 提取/替换、新增 frontmatter、批量处理等核心功能。
重点验证：
1. YAML / TOML 两种格式的 frontmatter 解析
2. status 字段的提取（含引号/不含引号）
3. status 归一化（STATUS_NORMALIZATION_MAP）
4. 新增 frontmatter（从 H1 提取 title）
5. dry-run 模式不写入文件
6. 闭合分隔符粘连 bug 回归测试
"""

import pytest
from pathlib import Path

from lib.spec_tool.frontmatter_fixer import (
    parse_frontmatter_info,
    extract_status_value,
    extract_h1_title,
    clean_title,
    insert_status_into_body,
    replace_status_in_body,
    build_yaml_frontmatter,
    process_spec_file,
    process_spec_dir,
)
from lib.spec_tool.constants import STATUS_NORMALIZATION_MAP


# ============================================================
# 解析层测试
# ============================================================

class TestParseFrontmatterInfo:
    """frontmatter 解析函数测试。"""

    def test_yaml_simple(self):
        content = "---\nstatus: draft\n---\n\n# Title\n"
        info = parse_frontmatter_info(content)
        assert info is not None
        assert info["format"] == "yaml"
        assert info["has_status"] is True
        assert "status: draft" in info["body"]

    def test_yaml_no_status(self):
        content = "---\ntitle: \"Test\"\n---\n\n# Title\n"
        info = parse_frontmatter_info(content)
        assert info is not None
        assert info["format"] == "yaml"
        assert info["has_status"] is False

    def test_yaml_empty_body(self):
        content = "---\n---\n\n# Title\n"
        info = parse_frontmatter_info(content)
        assert info is not None
        assert info["format"] == "yaml"
        assert info["has_status"] is False

    def test_toml_simple(self):
        content = '+++\nstatus = "draft"\n+++\n\n# Title\n'
        info = parse_frontmatter_info(content)
        assert info is not None
        assert info["format"] == "toml"
        assert info["has_status"] is True

    def test_toml_no_status(self):
        content = '+++\ntitle = "Test"\n+++\n\n# Title\n'
        info = parse_frontmatter_info(content)
        assert info is not None
        assert info["format"] == "toml"
        assert info["has_status"] is False

    def test_no_frontmatter(self):
        content = "# Just a title\n\nNo frontmatter.\n"
        info = parse_frontmatter_info(content)
        assert info is None

    def test_no_closing_delimiter(self):
        """只有起始分隔符，没有闭合分隔符 → 不算 frontmatter。"""
        content = "---\nstatus: draft\n\n# Title\n"
        info = parse_frontmatter_info(content)
        assert info is None

    def test_frontmatter_with_crlf(self):
        """CRLF 换行的 frontmatter 应正确解析。"""
        content = "---\r\nstatus: draft\r\n---\r\n\r\n# Title\r\n"
        info = parse_frontmatter_info(content)
        assert info is not None
        assert info["format"] == "yaml"
        assert info["has_status"] is True

    def test_leading_whitespace(self):
        """开头有空白字符时应能正确解析。"""
        content = "\n\n---\nstatus: draft\n---\n\n# Title\n"
        info = parse_frontmatter_info(content)
        assert info is not None
        assert info["format"] == "yaml"


class TestExtractStatusValue:
    """从 frontmatter body 提取 status 值。"""

    def test_yaml_plain(self):
        assert extract_status_value("status: draft", "yaml") == "draft"

    def test_yaml_double_quoted(self):
        assert extract_status_value('status: "draft"', "yaml") == "draft"

    def test_yaml_single_quoted(self):
        assert extract_status_value("status: 'draft'", "yaml") == "draft"

    def test_yaml_with_indent(self):
        assert extract_status_value("  status: draft", "yaml") == "draft"

    def test_yaml_compound_value(self):
        assert extract_status_value("status: in-progress", "yaml") == "in-progress"

    def test_toml_double_quoted(self):
        assert extract_status_value('status = "draft"', "toml") == "draft"

    def test_toml_single_quoted(self):
        assert extract_status_value("status = 'draft'", "toml") == "draft"

    def test_no_status(self):
        assert extract_status_value("title: Test", "yaml") is None


class TestExtractH1Title:
    """从 Markdown 正文提取 H1 标题。"""

    def test_simple_h1(self):
        assert extract_h1_title("# Hello World\n\nbody") == "Hello World"

    def test_h1_with_trailing_spaces(self):
        assert extract_h1_title("# Hello   \n\nbody") == "Hello"

    def test_no_h1(self):
        assert extract_h1_title("## Subtitle\n\nbody") is None

    def test_h1_after_other_content(self):
        assert extract_h1_title("some text\n# Real Title\nmore") == "Real Title"


class TestCleanTitle:
    """标题中 YAML 特殊字符转义。"""

    def test_no_quotes(self):
        assert clean_title("Hello World") == "Hello World"

    def test_double_quotes(self):
        assert clean_title('Say "Hello"') == 'Say \\"Hello\\"'


# ============================================================
# 操作层测试
# ============================================================

class TestInsertStatusIntoBody:
    """在 frontmatter body 中插入 status 行。"""

    def test_yaml_insert(self):
        body = "title: \"Test\"\n"
        result = insert_status_into_body(body, "yaml", "draft")
        assert result.startswith('status: "draft"\n')
        assert "title: \"Test\"" in result

    def test_toml_insert(self):
        body = 'title = "Test"\n'
        result = insert_status_into_body(body, "toml", "draft")
        assert result.startswith('status = "draft"\n')
        assert 'title = "Test"' in result


class TestReplaceStatusInBody:
    """替换 frontmatter 中的 status 值。"""

    def test_yaml_plain_value(self):
        body = "status: draft\n"
        result = replace_status_in_body(body, "yaml", "completed")
        assert 'status: "completed"' in result

    def test_yaml_double_quoted(self):
        body = 'status: "draft"\n'
        result = replace_status_in_body(body, "yaml", "completed")
        assert 'status: "completed"' in result
        # 验证引号风格保留
        assert 'status: "completed"' in result

    def test_yaml_single_quoted(self):
        body = "status: 'draft'\n"
        result = replace_status_in_body(body, "yaml", "completed")
        assert "status: 'completed'" in result

    def test_toml_double_quoted(self):
        body = 'status = "draft"\n'
        result = replace_status_in_body(body, "toml", "completed")
        assert 'status = "completed"' in result

    def test_preserves_other_lines(self):
        """替换 status 时不应影响其他行。"""
        body = 'title: "Test"\nstatus: draft\nauthor: me\n'
        result = replace_status_in_body(body, "yaml", "completed")
        assert 'title: "Test"' in result
        assert "author: me" in result
        assert "draft" not in result

    def test_closing_delimiter_not_stuck(self):
        """回归测试：替换 status 后，闭合分隔符不应粘连到 status 行。
        
        历史 bug：正则用 \s*$ 匹配行尾，吃掉换行符，导致 --- 被粘连。
        修复：改用 [ \\t]*$ 只匹配水平空白。
        """
        full = "---\nstatus: complete\n---\n\n# Title\n"
        info = parse_frontmatter_info(full)
        assert info is not None
        new_body = replace_status_in_body(info["body"], "yaml", "completed")
        # 重新组合
        new_content = full[:info["body_start"]] + new_body + full[info["body_end"]:]
        # 闭合分隔符应该单独占一行
        assert "\n---\n" in new_content
        assert '"completed"---' not in new_content


class TestBuildYamlFrontmatter:
    """构造 YAML frontmatter 字符串。"""

    def test_basic(self):
        fm = build_yaml_frontmatter("My Spec", "draft")
        assert fm.startswith("---\n")
        assert 'title: "My Spec"' in fm
        assert 'status: "draft"' in fm
        assert fm.endswith("---\n\n")

    def test_with_date(self):
        fm = build_yaml_frontmatter("My Spec", "draft", "2026-01-15")
        assert "date: 2026-01-15" in fm


# ============================================================
# 高层 API — process_spec_file
# ============================================================

class TestProcessSpecFile:
    """单文件处理（dry-run 为主，实际写入场景也覆盖）。"""

    def _write(self, path: Path, content: str):
        path.write_text(content, encoding="utf-8")

    def test_skip_with_status(self, tmp_path: Path):
        """已有合法 status 的文件应被跳过。"""
        spec = tmp_path / "spec.md"
        self._write(spec, "---\nstatus: draft\n---\n\n# Test\n")
        r = process_spec_file(spec)
        assert r["action"] == "skipped"
        assert "已有 frontmatter 且含 status" in r["reason"]

    def test_add_frontmatter_dry_run(self, tmp_path: Path):
        """无 frontmatter 文件在 dry-run 下返回 would_add。"""
        spec = tmp_path / "spec.md"
        self._write(spec, "# My Awesome Spec\n\nbody content\n")
        r = process_spec_file(spec, dry_run=True)
        assert r["action"] == "would_add"
        assert r["title"] == "My Awesome Spec"
        assert r["new_status"] == "draft"
        # dry-run 不应修改文件
        assert spec.read_text(encoding="utf-8") == "# My Awesome Spec\n\nbody content\n"

    def test_add_frontmatter_actual(self, tmp_path: Path):
        """实际写入 frontmatter。"""
        spec = tmp_path / "spec.md"
        self._write(spec, "# My Spec\n\nbody\n")
        r = process_spec_file(spec, dry_run=False)
        assert r["action"] == "added"
        content = spec.read_text(encoding="utf-8")
        assert content.startswith("---\n")
        assert 'title: "My Spec"' in content
        assert 'status: "draft"' in content
        assert "# My Spec" in content

    def test_add_frontmatter_with_date(self, tmp_path: Path):
        """新增时带 date 字段。"""
        spec = tmp_path / "spec.md"
        self._write(spec, "# Test\n\nbody\n")
        r = process_spec_file(spec, add_date=True, dry_run=False)
        assert r["action"] == "added"
        content = spec.read_text(encoding="utf-8")
        assert "date:" in content

    def test_no_h1_title_error(self, tmp_path: Path):
        """没有 H1 标题时返回错误。"""
        spec = tmp_path / "spec.md"
        self._write(spec, "## Only H2\n\nNo H1 here.\n")
        r = process_spec_file(spec, dry_run=True)
        assert r["action"] == "error"
        assert "未找到 H1 标题" in r["reason"]

    def test_insert_status_dry_run(self, tmp_path: Path):
        """已有 frontmatter 但缺 status，dry-run 返回 would_add_status。"""
        spec = tmp_path / "spec.md"
        self._write(spec, '---\ntitle: "Test"\n---\n\n# Test\n')
        r = process_spec_file(spec, fix_missing_status=True, dry_run=True)
        assert r["action"] == "would_add_status"
        assert r["new_status"] == "draft"
        assert r["mode"] == "fix_status"

    def test_insert_status_actual_yaml(self, tmp_path: Path):
        """YAML frontmatter 中实际插入 status。"""
        spec = tmp_path / "spec.md"
        self._write(spec, '---\ntitle: "Test"\n---\n\n# Test\n')
        r = process_spec_file(spec, fix_missing_status=True, dry_run=False)
        assert r["action"] == "status_added"
        content = spec.read_text(encoding="utf-8")
        assert 'status: "draft"' in content

    def test_insert_status_actual_toml(self, tmp_path: Path):
        """TOML frontmatter 中实际插入 status。"""
        spec = tmp_path / "spec.md"
        self._write(spec, '+++\ntitle = "Test"\n+++\n\n# Test\n')
        r = process_spec_file(spec, fix_missing_status=True, dry_run=False)
        assert r["action"] == "status_added"
        content = spec.read_text(encoding="utf-8")
        assert 'status = "draft"' in content

    def test_no_insert_without_flag(self, tmp_path: Path):
        """未启用 fix_missing_status 时，缺 status 的文件被跳过。"""
        spec = tmp_path / "spec.md"
        self._write(spec, '---\ntitle: "Test"\n---\n\n# Test\n')
        r = process_spec_file(spec, fix_missing_status=False, dry_run=False)
        assert r["action"] == "skipped"
        assert "未启用 fix_missing_status" in r["reason"]

    def test_normalize_status_dry_run(self, tmp_path: Path):
        """非法 status 在 dry-run 下归一化预览。"""
        spec = tmp_path / "spec.md"
        self._write(spec, "---\nstatus: complete\n---\n\n# Test\n")
        r = process_spec_file(spec, normalize_status=True, dry_run=True)
        assert r["action"] == "would_normalize"
        assert r["old_status"] == "complete"
        assert r["new_status"] == "completed"

    def test_normalize_status_actual(self, tmp_path: Path):
        """实际归一化 status。"""
        spec = tmp_path / "spec.md"
        self._write(spec, "---\nstatus: complete\n---\n\n# Test\n")
        r = process_spec_file(spec, normalize_status=True, dry_run=False)
        assert r["action"] == "normalized"
        content = spec.read_text(encoding="utf-8")
        assert "complete" not in content.split("---")[1] or '"completed"' in content
        assert r["old_status"] == "complete"
        assert r["new_status"] == "completed"

    def test_normalization_map_coverage(self, tmp_path: Path):
        """验证 STATUS_NORMALIZATION_MAP 中所有映射都能正确工作。"""
        for old, new in STATUS_NORMALIZATION_MAP.items():
            spec = tmp_path / "spec.md"
            self._write(spec, f"---\nstatus: {old}\n---\n\n# Test\n")
            r = process_spec_file(spec, normalize_status=True, dry_run=True)
            assert r["action"] == "would_normalize", f"'{old}' should normalize to '{new}'"
            assert r["old_status"] == old
            assert r["new_status"] == new

    def test_already_valid_no_normalize_flag(self, tmp_path: Path):
        """已有合法 status 且未开 normalize 时，跳过。"""
        spec = tmp_path / "spec.md"
        self._write(spec, "---\nstatus: draft\n---\n\n# Test\n")
        r = process_spec_file(spec, normalize_status=False, dry_run=False)
        assert r["action"] == "skipped"

    def test_invalid_status_not_in_map(self, tmp_path: Path):
        """不在归一化映射表中的非法 status，跳过（不猜）。"""
        spec = tmp_path / "spec.md"
        self._write(spec, "---\nstatus: totally-invalid-xyz\n---\n\n# Test\n")
        r = process_spec_file(spec, normalize_status=True, dry_run=False)
        assert r["action"] == "skipped"
        assert "不在归一化映射表中" in r["reason"]


# ============================================================
# 高层 API — process_spec_dir
# ============================================================

class TestProcessSpecDir:
    """批量处理。"""

    def _make_spec(self, root: Path, name: str, content: str):
        d = root / name
        d.mkdir()
        (d / "spec.md").write_text(content, encoding="utf-8")
        return d / "spec.md"

    def test_empty_dir(self, tmp_path: Path):
        results = process_spec_dir(tmp_path / "empty")
        assert results == []

    def test_multiple_mixed(self, tmp_path: Path):
        """混合场景：正常的 + 需新增 frontmatter 的。"""
        self._make_spec(tmp_path, "good", "---\nstatus: draft\n---\n\n# Good\n")
        self._make_spec(tmp_path, "no-fm", "# No FM\n\nbody\n")
        self._make_spec(tmp_path, "no-fm-2", "# Also No FM\n\nbody\n")

        results = process_spec_dir(tmp_path, dry_run=True)
        assert len(results) == 3
        actions = [r["action"] for r in results]
        assert actions.count("skipped") == 1
        assert actions.count("would_add") == 2

    def test_nested_directories(self, tmp_path: Path):
        """嵌套目录中的 spec.md 也应被处理。"""
        (tmp_path / "a").mkdir()
        (tmp_path / "a" / "b").mkdir(parents=True)
        self._make_spec(tmp_path / "a", "spec1", "# A\n")
        self._make_spec(tmp_path / "a" / "b", "spec2", "# B\n")

        results = process_spec_dir(tmp_path, dry_run=True)
        assert len(results) == 2
