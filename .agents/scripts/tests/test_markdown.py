"""lib.markdown 单元测试。"""

from pathlib import Path

import pytest

from lib import markdown as md


class TestFindMarkdownFiles:

    def test_finds_md_files(self, tmp_path):
        (tmp_path / "a.md").write_text("# A\n", encoding="utf-8")
        (tmp_path / "b.md").write_text("# B\n", encoding="utf-8")
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "c.md").write_text("# C\n", encoding="utf-8")
        files = md.find_markdown_files(tmp_path)
        names = sorted(f.name for f in files)
        assert names == ["a.md", "b.md", "c.md"]

    def test_excludes_default_dirs(self, tmp_path):
        (tmp_path / "keep.md").write_text("# K\n", encoding="utf-8")
        for d in [".git", "vendor", "__pycache__", ".temp", "node_modules", ".venv"]:
            bad = tmp_path / d
            bad.mkdir()
            (bad / "bad.md").write_text("# bad\n", encoding="utf-8")
        files = md.find_markdown_files(tmp_path)
        assert len(files) == 1
        assert files[0].name == "keep.md"

    def test_excludes_non_worktree_prefixes(self, tmp_path):
        (tmp_path / "keep.md").write_text("# K\n", encoding="utf-8")
        backup_dir = tmp_path / ".meta" / "backup" / "docs"
        backup_dir.mkdir(parents=True)
        (backup_dir / "backup.md").write_text("# backup\n", encoding="utf-8")
        external_dir = tmp_path / "external" / "vendor-docs"
        external_dir.mkdir(parents=True)
        (external_dir / "external.md").write_text("# external\n", encoding="utf-8")
        playground_dir = tmp_path / "playground" / "reports"
        playground_dir.mkdir(parents=True)
        (playground_dir / "playground.md").write_text("# playground\n", encoding="utf-8")

        files = md.find_markdown_files(tmp_path)

        names = sorted(f.name for f in files)
        assert names == ["keep.md"]

    def test_extra_exclude_dirs(self, tmp_path):
        (tmp_path / "keep.md").write_text("# K\n", encoding="utf-8")
        hidden = tmp_path / "drafts"
        hidden.mkdir()
        (hidden / "x.md").write_text("# x\n", encoding="utf-8")
        files = md.find_markdown_files(tmp_path, exclude_dirs=["drafts/"])
        assert len(files) == 1
        assert files[0].name == "keep.md"

    def test_no_md_files(self, tmp_path):
        (tmp_path / "a.txt").write_text("text\n", encoding="utf-8")
        assert md.find_markdown_files(tmp_path) == []


class TestExtractTitle:

    def test_extracts_h1(self, tmp_path):
        p = tmp_path / "doc.md"
        p.write_text("# Hello World\n\nSome content.\n", encoding="utf-8")
        assert md.extract_title(p) == "Hello World"

    def test_takes_first_h1(self, tmp_path):
        p = tmp_path / "doc.md"
        p.write_text("# First\n\n## Second\n\n# Third\n", encoding="utf-8")
        assert md.extract_title(p) == "First"

    def test_no_h1_returns_empty(self, tmp_path):
        p = tmp_path / "doc.md"
        p.write_text("## No H1\n\nContent.\n", encoding="utf-8")
        assert md.extract_title(p) == ""


class TestExtractDescription:

    def test_extracts_first_paragraph(self, tmp_path):
        p = tmp_path / "doc.md"
        p.write_text("# Title\n\n这是第一个段落。这是更多内容。\n", encoding="utf-8")
        desc = md.extract_description(p)
        assert "这是第一个段落" in desc

    def test_skips_blockquotes(self, tmp_path):
        p = tmp_path / "doc.md"
        p.write_text("# Title\n\n> A quote\n\n实际描述文字。更多内容。\n", encoding="utf-8")
        desc = md.extract_description(p)
        assert "实际描述文字" in desc

    def test_no_description_returns_empty(self, tmp_path):
        p = tmp_path / "doc.md"
        p.write_text("# Title\n", encoding="utf-8")
        assert md.extract_description(p) == ""

    def test_stops_at_period_followed_by_space(self, tmp_path):
        """中文句号后须跟空白才分句。"""
        p = tmp_path / "doc.md"
        p.write_text("# Title\n\n第一句。 第二句。第三句。\n", encoding="utf-8")
        desc = md.extract_description(p)
        assert desc == "第一句"


class TestParseInlineLinks:

    def test_finds_links(self):
        content = "See [the docs](doc.md) and [other](path/to/file.md)."
        links = md.parse_inline_links(content)
        assert len(links) == 2
        assert links[0] == ("the docs", "doc.md")
        assert links[1] == ("other", "path/to/file.md")

    def test_no_links(self):
        assert md.parse_inline_links("Just plain text.") == []

    def test_strips_url_whitespace(self):
        content = "[click](  page.md  )"
        links = md.parse_inline_links(content)
        assert links[0] == ("click", "page.md")


class TestUpdateMarkerRegion:

    def test_replaces_marker_content(self, tmp_path):
        p = tmp_path / "doc.md"
        p.write_text(
            "Before\n<!-- START -->\nold content\n<!-- END -->\nAfter\n",
            encoding="utf-8",
        )
        md.update_marker_region(p, "<!-- START -->", "<!-- END -->", "new content")
        result = p.read_text(encoding="utf-8")
        assert "new content" in result
        assert "old content" not in result
        assert "Before" in result
        assert "After" in result

    def test_missing_start_marker_raises(self, tmp_path):
        p = tmp_path / "doc.md"
        p.write_text("<!-- END -->\nx\n", encoding="utf-8")
        with pytest.raises(ValueError, match="未找到标记"):
            md.update_marker_region(p, "<!-- START -->", "<!-- END -->", "new")

    def test_missing_end_marker_raises(self, tmp_path):
        p = tmp_path / "doc.md"
        p.write_text("<!-- START -->\nx\n", encoding="utf-8")
        with pytest.raises(ValueError, match="未找到标记"):
            md.update_marker_region(p, "<!-- START -->", "<!-- END -->", "new")
