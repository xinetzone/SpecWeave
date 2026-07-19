import pytest
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from check_markdown_duplication import (
    normalize_markdown_line,
    extract_normalized_md_lines,
    compute_fingerprint,
    find_markdown_duplicates,
    DuplicateBlock,
    strip_frontmatter,
    is_code_fence,
)


def _write_md(path: Path, content: str):
    path.write_text(content, encoding="utf-8")


class TestStripFrontmatter:
    def test_strips_yaml_frontmatter(self, tmp_path):
        content = "---\ntitle: test\n---\n# Hello\nWorld\n"
        result = strip_frontmatter(content)
        assert "# Hello" in result
        assert "title: test" not in result

    def test_no_frontmatter_returns_original(self, tmp_path):
        content = "# Hello\nWorld\n"
        assert strip_frontmatter(content) == content

    def test_empty_frontmatter(self, tmp_path):
        content = "---\n---\n# Hello\n"
        result = strip_frontmatter(content)
        assert "# Hello" in result


class TestNormalizeMarkdownLine:
    def test_empty_line_returns_empty(self):
        assert normalize_markdown_line("") == ""
        assert normalize_markdown_line("   ") == ""

    def test_strips_heading_markers(self):
        norm = normalize_markdown_line("## 核心发现")
        assert "核心发现" in norm
        assert norm.startswith("核心发现") or norm.strip() == "核心发现"

    def test_strips_list_markers(self):
        norm = normalize_markdown_line("- 列表项")
        assert "列表项" in norm

    def test_strips_bold_italic(self):
        norm = normalize_markdown_line("这是**粗体**和*斜体*")
        assert "**" not in norm
        assert "*" not in norm

    def test_strips_links_keeps_text(self):
        norm = normalize_markdown_line("参见[链接文本](http://example.com)")
        assert "链接文本" in norm
        assert "http://" not in norm

    def test_code_fence_line(self):
        assert is_code_fence("```python") is True
        assert is_code_fence("```") is True
        assert is_code_fence("普通文本") is False

    def test_strips_html_tags(self):
        norm = normalize_markdown_line("<div>文本</div>")
        assert "<div>" not in norm
        assert "文本" in norm


class TestExtractNormalizedMdLines:
    def test_skips_code_blocks(self, tmp_path):
        content = "# Title\n\n```python\nprint('hello')\nprint('world')\n```\n\n正文段落\n"
        lines = extract_normalized_md_lines(content)
        text_only = " ".join(norm for _, norm in lines)
        assert "print" not in text_only
        assert "正文段落" in text_only

    def test_returns_line_number_and_norm(self, tmp_path):
        content = "第一行\n\n第二行\n"
        lines = extract_normalized_md_lines(content)
        assert len(lines) >= 2
        for ln, norm in lines:
            assert isinstance(ln, int)
            assert isinstance(norm, str)
            assert norm

    def test_skips_frontmatter(self):
        content = "---\ntitle: test\nid: x\n---\n# Hello\n正文\n"
        lines = extract_normalized_md_lines(content)
        text = " ".join(n for _, n in lines)
        assert "title: test" not in text
        assert "Hello" in text


class TestFindMarkdownDuplicates:
    def test_finds_duplicate_paragraphs(self, tmp_path):
        f1 = tmp_path / "a.md"
        f2 = tmp_path / "b.md"
        para = "这是一段重复的内容，用于测试重复检测功能是否正常工作。"
        _write_md(f1, f"# 文件A\n\n{para}\n\n独有内容A\n")
        _write_md(f2, f"# 文件B\n\n{para}\n\n独有内容B\n")
        dups = find_markdown_duplicates(tmp_path, threshold=1, window=1)
        assert len(dups) >= 1
        assert len(dups[0].occurrences) >= 2

    def test_no_duplicates_in_unique_content(self, tmp_path):
        f1 = tmp_path / "a.md"
        f2 = tmp_path / "b.md"
        _write_md(f1, "# Alpha\n\n苹果香蕉橙子\n")
        _write_md(f2, "# Beta\n\n汽车火车飞机\n")
        dups = find_markdown_duplicates(tmp_path, threshold=1, window=1)
        assert len(dups) == 0

    def test_respects_threshold(self, tmp_path):
        f1 = tmp_path / "a.md"
        f2 = tmp_path / "b.md"
        _write_md(f1, "# A\n\n短句\n\n长句A\n")
        _write_md(f2, "# B\n\n短句\n\n长句B\n")
        dups = find_markdown_duplicates(tmp_path, threshold=10, window=1)
        assert len(dups) == 0

    def test_returns_duplicate_block_dataclass(self, tmp_path):
        f1 = tmp_path / "a.md"
        f2 = tmp_path / "b.md"
        para = "相同段落内容测试。"
        _write_md(f1, f"# A\n\n{para}\n")
        _write_md(f2, f"# B\n\n{para}\n")
        dups = find_markdown_duplicates(tmp_path, threshold=1, window=1)
        if dups:
            block = dups[0]
            assert isinstance(block, DuplicateBlock)
            assert hasattr(block, 'fingerprint')
            assert hasattr(block, 'line_count')
            assert hasattr(block, 'occurrences')
            assert len(block.occurrences) >= 2
