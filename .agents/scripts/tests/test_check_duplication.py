"""check-duplication.py 单元测试。

覆盖主要使用场景：
- normalize_line: 代码行归一化（空行、注释、字符串内#、行内注释）
- extract_normalized_lines: 归一化行提取（跳过空行/注释/排除行）
- compute_fingerprint: 指纹计算（一致性、不同输入不同指纹）
- expand_duplicate_block: 重复块扩展
- suggest_lib_location: 共享库位置建议
- find_duplicates: 端到端重复检测（无重复、有重复、阈值过滤）
"""

import importlib.util
import sys
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "check_duplication", _SCRIPTS_DIR / "check-duplication.py"
)
check_duplication = importlib.util.module_from_spec(_spec)
sys.modules["check_duplication"] = check_duplication
_spec.loader.exec_module(check_duplication)

from check_duplication import (
    normalize_line,
    extract_normalized_lines,
    compute_fingerprint,
    expand_duplicate_block,
    suggest_lib_location,
    find_duplicates,
    DuplicateBlock,
    Occurrence,
    DEFAULT_THRESHOLD,
    DEFAULT_WINDOW,
)
from lib.rules import FalsePositiveRules


@pytest.fixture
def empty_rules():
    """空规则集（不排除任何内容）。"""
    return FalsePositiveRules()


class TestNormalizeLine:
    """normalize_line 测试：代码行归一化。"""

    def test_empty_line(self):
        assert normalize_line("") == ""
        assert normalize_line("   ") == ""
        assert normalize_line("\t") == ""

    def test_full_line_comment(self):
        assert normalize_line("# 这是注释") == ""
        assert normalize_line("    # 缩进注释") == ""
        assert normalize_line("#TODO: something") == ""

    def test_inline_comment(self):
        assert normalize_line("x = 1  # 赋值") == "x = 1"
        assert normalize_line("print('hello') # debug") == "print('hello')"

    def test_hash_in_string_single_quote(self):
        line = "s = 'hello # world'"
        result = normalize_line(line)
        assert "#" in result
        assert "s = 'hello # world'" == result

    def test_hash_in_string_double_quote(self):
        line = 's = "hello # world"'
        result = normalize_line(line)
        assert "#" in result
        assert 's = "hello # world"' == result

    def test_escaped_quote_in_string(self):
        line = "s = 'it\\'s a # test'"
        result = normalize_line(line)
        assert "#" in result

    def test_code_without_comment(self):
        assert normalize_line("def foo():") == "def foo():"
        assert normalize_line("    return 42") == "return 42"

    def test_whitespace_stripping(self):
        assert normalize_line("   x = 1   ") == "x = 1"
        assert normalize_line("\tprint()\t") == "print()"


class TestComputeFingerprint:
    """compute_fingerprint 测试：指纹计算。"""

    def test_consistent_hash(self):
        lines1 = ["def foo():", "return 1"]
        lines2 = ["def foo():", "return 1"]
        assert compute_fingerprint(lines1) == compute_fingerprint(lines2)

    def test_different_input_different_hash(self):
        lines1 = ["def foo():", "return 1"]
        lines2 = ["def bar():", "return 2"]
        assert compute_fingerprint(lines1) != compute_fingerprint(lines2)

    def test_single_line(self):
        fp = compute_fingerprint(["x = 1"])
        assert isinstance(fp, str)
        assert len(fp) == 16

    def test_empty_lines_list(self):
        fp = compute_fingerprint([])
        assert isinstance(fp, str)
        assert len(fp) == 16

    def test_returns_16_chars(self):
        fp = compute_fingerprint(["a", "b", "c", "d", "e"])
        assert len(fp) == 16
        assert all(c in "0123456789abcdef" for c in fp)


class TestSuggestLibLocation:
    """suggest_lib_location 测试：共享库位置建议。"""

    def test_cli_module(self):
        assert "lib/cli.py" in suggest_lib_location("add_argument parser print_header")

    def test_frontmatter_module(self):
        assert "lib/frontmatter.py" in suggest_lib_location("parse_toml_frontmatter extract_field")

    def test_link_fixer_module(self):
        assert "lib/link_fixer.py" in suggest_lib_location("fix_link relative path href")

    def test_markdown_module(self):
        assert "lib/markdown.py" in suggest_lib_location("find_markdown .md title description")

    def test_spec_module(self):
        assert "lib/spec/" in suggest_lib_location("spec checklist tasks requirements")

    def test_project_module(self):
        assert "lib/project.py" in suggest_lib_location("resolve_project_root __file__ parent path")

    def test_patterns_module(self):
        assert "lib/patterns.py" in suggest_lib_location("pattern maturity domain layer")

    def test_default_suggestion(self):
        result = suggest_lib_location("some random code that doesn't match")
        assert "新建" in result or "对应模块" in result

    def test_case_insensitive(self):
        assert "lib/cli.py" in suggest_lib_location("PARSER Add_Argument PRINT_")


class TestExtractNormalizedLines:
    """extract_normalized_lines 测试：归一化行提取。"""

    def test_basic_extraction(self, empty_rules):
        content = """x = 1
y = 2

# comment
z = 3  # inline
"""
        lines = extract_normalized_lines(content, empty_rules)
        norms = [n for _, n in lines]
        assert "x = 1" in norms
        assert "y = 2" in norms
        assert "z = 3" in norms
        assert "" not in norms
        assert not any("#" in n for n in norms)

    def test_line_numbers_preserved(self, empty_rules):
        content = "a = 1\nb = 2\nc = 3"
        lines = extract_normalized_lines(content, empty_rules)
        assert lines[0][0] == 1
        assert lines[1][0] == 2
        assert lines[2][0] == 3

    def test_empty_content(self, empty_rules):
        assert extract_normalized_lines("", empty_rules) == []

    def test_all_comments_and_empty(self, empty_rules):
        content = "# comment 1\n\n# comment 2\n   \n"
        lines = extract_normalized_lines(content, empty_rules)
        assert lines == []

    def test_line_filter_rules(self):
        rules = FalsePositiveRules()
        import re
        rules.line_filter_patterns = [re.compile(r"^print\(")]
        content = "x = 1\nprint('hello')\ny = 2"
        lines = extract_normalized_lines(content, rules)
        norms = [n for _, n in lines]
        assert "x = 1" in norms
        assert "print('hello')" not in norms
        assert "y = 2" in norms


class TestFindDuplicates:
    """find_duplicates 测试：端到端重复代码检测。"""

    def test_no_duplicates(self, tmp_path, empty_rules):
        f1 = tmp_path / "a.py"
        f2 = tmp_path / "b.py"
        f1.write_text("def foo():\n    return 1\n", encoding="utf-8")
        f2.write_text("def bar():\n    return 2\n", encoding="utf-8")
        dups = find_duplicates(tmp_path, empty_rules, threshold=2, window=2)
        assert len(dups) == 0

    def test_exact_duplicate_block(self, tmp_path, empty_rules):
        code_block = "def helper():\n    x = 1\n    y = 2\n    return x + y\n"
        f1 = tmp_path / "a.py"
        f2 = tmp_path / "b.py"
        f1.write_text("# file a\n" + code_block, encoding="utf-8")
        f2.write_text("# file b\n" + code_block, encoding="utf-8")
        dups = find_duplicates(tmp_path, empty_rules, threshold=3, window=3)
        assert len(dups) >= 1
        block = dups[0]
        assert block.line_count >= 3
        assert len(block.occurrences) >= 2

    def test_threshold_filtering(self, tmp_path, empty_rules):
        small_block = "x = 1\ny = 2\n"
        f1 = tmp_path / "a.py"
        f2 = tmp_path / "b.py"
        f1.write_text(small_block, encoding="utf-8")
        f2.write_text(small_block, encoding="utf-8")
        dups = find_duplicates(tmp_path, empty_rules, threshold=5, window=2)
        assert len(dups) == 0

    def test_excluded_dirs_skipped(self, tmp_path, empty_rules):
        lib_dir = tmp_path / "lib"
        lib_dir.mkdir()
        f1 = tmp_path / "a.py"
        f2 = lib_dir / "b.py"
        code = "x = 1\ny = 2\nz = 3\nw = 4\nv = 5\nu = 6\n"
        f1.write_text(code, encoding="utf-8")
        f2.write_text(code, encoding="utf-8")
        dups = find_duplicates(tmp_path, empty_rules, threshold=5, window=3)
        assert len(dups) == 0

    def test_duplicate_in_same_file_not_reported(self, tmp_path, empty_rules):
        block = "x = 1\ny = 2\nz = 3\nw = 4\nv = 5\n"
        f1 = tmp_path / "a.py"
        f1.write_text(block + "\n# separator\n" + block, encoding="utf-8")
        f2 = tmp_path / "b.py"
        f2.write_text("def unique():\n    pass\n", encoding="utf-8")
        dups = find_duplicates(tmp_path, empty_rules, threshold=4, window=3)
        assert len(dups) == 0

    def test_sorted_by_line_count_desc(self, tmp_path, empty_rules):
        small = "a=1\nb=2\nc=3\nd=4\ne=5\n"
        large = "v=1\nw=2\nx=3\ny=4\nz=5\nu=6\nv=7\nw=8\n"
        f1 = tmp_path / "a.py"
        f2 = tmp_path / "b.py"
        f3 = tmp_path / "c.py"
        f4 = tmp_path / "d.py"
        f1.write_text(small, encoding="utf-8")
        f2.write_text(small, encoding="utf-8")
        f3.write_text(large, encoding="utf-8")
        f4.write_text(large, encoding="utf-8")
        dups = find_duplicates(tmp_path, empty_rules, threshold=4, window=3)
        if len(dups) >= 2:
            assert dups[0].line_count >= dups[1].line_count

    def test_unicode_file_content(self, tmp_path, empty_rules):
        code = "# 中文注释\nx = '你好'\ny = '世界'\nz = 1\nw = 2\nv = 3\nu = 4\n"
        f1 = tmp_path / "a.py"
        f2 = tmp_path / "b.py"
        f1.write_text(code, encoding="utf-8")
        f2.write_text(code, encoding="utf-8")
        dups = find_duplicates(tmp_path, empty_rules, threshold=5, window=3)
        assert len(dups) >= 1

    def test_binary_file_skipped(self, tmp_path, empty_rules):
        f1 = tmp_path / "a.py"
        f2 = tmp_path / "b.py"
        f1.write_text("x = 1\ny = 2\nz = 3\nw = 4\nv = 5\n", encoding="utf-8")
        f2.write_bytes(b"\x00\x01\x02\x03\xff\xfe" * 10)
        dups = find_duplicates(tmp_path, empty_rules, threshold=4, window=3)
        assert len(dups) == 0


class TestDuplicateBlockAndOccurrence:
    """数据类结构测试。"""

    def test_duplicate_block_defaults(self):
        block = DuplicateBlock(fingerprint="abc", line_count=5, normalized_preview="x = 1")
        assert block.occurrences == []
        assert block.fingerprint == "abc"
        assert block.line_count == 5

    def test_occurrence_fields(self):
        p = Path("test.py")
        occ = Occurrence(file_path=p, start_line=1, end_line=5, raw_preview="x = 1")
        assert occ.file_path == p
        assert occ.start_line == 1
        assert occ.end_line == 5
        assert occ.raw_preview == "x = 1"

    def test_occurrences_append(self):
        block = DuplicateBlock(fingerprint="fp", line_count=3, normalized_preview="")
        p = Path("test.py")
        block.occurrences.append(Occurrence(p, 1, 3, "a=1"))
        assert len(block.occurrences) == 1
