"""lib.checks.mermaid 单元测试。"""

import argparse
from pathlib import Path

import pytest

from lib.checks import mermaid as mm


@pytest.fixture
def args_default():
    return argparse.Namespace(path=None, exclude=[], fix=False, dry_run=False, json=False)


@pytest.fixture
def args_fix():
    return argparse.Namespace(path=None, exclude=[], fix=True, dry_run=False, json=False)


@pytest.fixture
def args_dryrun():
    return argparse.Namespace(path=None, exclude=[], fix=True, dry_run=True, json=False)


class TestLineFromOffset:
    """_line_from_offset 测试。"""

    def test_start_of_file(self):
        assert mm._line_from_offset("hello", 0) == 1

    def test_after_newlines(self):
        text = "line1\nline2\nline3\n"
        assert mm._line_from_offset(text, text.index("line2")) == 2
        assert mm._line_from_offset(text, text.index("line3")) == 3


class TestFindMdFiles:
    """_find_md_files 测试。"""

    def test_finds_md_files(self, tmp_path):
        (tmp_path / "doc.md").write_text("a", encoding="utf-8")
        (tmp_path / "sub").mkdir()
        (tmp_path / "sub" / "page.md").write_text("b", encoding="utf-8")
        files = mm._find_md_files(tmp_path, set())
        names = sorted(f.name for f in files)
        assert names == ["doc.md", "page.md"]

    def test_excludes_excluded_dirs(self, tmp_path):
        (tmp_path / "doc.md").write_text("a", encoding="utf-8")
        (tmp_path / "vendor").mkdir()
        (tmp_path / "vendor" / "lib.md").write_text("b", encoding="utf-8")
        (tmp_path / "__pycache__").mkdir()
        (tmp_path / "__pycache__" / "cache.md").write_text("c", encoding="utf-8")
        files = mm._find_md_files(tmp_path, set())
        names = [f.name for f in files]
        assert "doc.md" in names
        assert "lib.md" not in names
        assert "cache.md" not in names

    def test_excludes_custom_dirs(self, tmp_path):
        (tmp_path / "doc.md").write_text("a", encoding="utf-8")
        (tmp_path / "build").mkdir()
        (tmp_path / "build" / "out.md").write_text("b", encoding="utf-8")
        files = mm._find_md_files(tmp_path, {"build"})
        names = [f.name for f in files]
        assert "doc.md" in names
        assert "out.md" not in names


class TestFixBlock:
    """_fix_block 测试。"""

    def test_removes_blank_lines(self):
        block = "graph TD\n    A --> B\n\n    B --> C\n"
        fixed, fixes = mm._fix_block(block)
        assert "空行" in fixes
        assert "\n\n" not in fixed

    def test_quotes_chinese_node_labels(self):
        block = 'graph TD\n    A[开始节点] --> B[结束]\n'
        fixed, fixes = mm._fix_block(block)
        assert "节点引号" in fixes
        assert 'A["开始节点"]' in fixed
        assert 'B["结束"]' in fixed

    def test_does_not_double_quote(self):
        block = 'graph TD\n    A["开始"] --> B["结束"]\n'
        fixed, fixes = mm._fix_block(block)
        assert "节点引号" not in fixes

    def test_quotes_chinese_edge_labels(self):
        block = 'graph TD\n    A -->|是| B\n'
        fixed, fixes = mm._fix_block(block)
        assert '-->|"是"|' in fixed

    def test_converts_number_dot_pattern(self):
        block = "graph TD\n    1. 第一步\n"
        fixed, fixes = mm._fix_block(block)
        assert "数字点格式" in fixes
        assert "1：" in fixed

    def test_ascii_nodes_unchanged(self):
        block = "graph TD\n    start[Start] --> end_node[End]\n"
        fixed, fixes = mm._fix_block(block)
        assert "节点引号" not in fixes
        assert "start[Start]" in fixed

    def test_clean_block_no_fixes(self):
        block = 'graph TD\n    A["开始"] -->|"连接"| B["结束"]\n'
        fixed, fixes = mm._fix_block(block)
        assert fixes == []


class TestCheckBlock:
    """_check_block 测试。"""

    def test_clean_block(self):
        block = "graph TD\n    A --> B\n"
        issues = mm._check_block(block, 1)
        assert issues == []

    def test_blank_line_error(self):
        block = "graph TD\n    A --> B\n\n    B --> C\n"
        issues = mm._check_block(block, 1)
        assert len(issues) == 1
        assert issues[0][1] == "error"
        assert "空行" in issues[0][2]

    def test_chinese_subgraph_id(self):
        block = "flowchart TD\n    subgraph 模块A\n        A --> B\n    end\n"
        issues = mm._check_block(block, 1)
        assert len(issues) == 1
        assert "裸中文ID" in issues[0][2]
        assert "模块A" in issues[0][2]

    def test_valid_subgraph_quoted(self):
        block = 'flowchart TD\n    subgraph modA ["模块A"]\n        A --> B\n    end\n'
        issues = mm._check_block(block, 1)
        assert issues == []

    def test_line_number_calculation(self):
        block = "graph TD\n\n    A --> B\n"
        issues = mm._check_block(block, 10)
        assert issues[0][0] == 10


class TestProcessFile:
    """_process_file 测试。"""

    def test_clean_file(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Title\n\nSome text.\n", encoding="utf-8")
        issues, fixes = mm._process_file(md, tmp_path, fix=False, dry_run=False)
        assert issues == []
        assert fixes == 0

    def test_detects_mermaid_blank_lines(self, tmp_path):
        md = tmp_path / "test.md"
        content = "# Doc\n\n```mermaid\ngraph TD\n    A --> B\n\n    B --> C\n```\n"
        md.write_text(content, encoding="utf-8")
        issues, fixes = mm._process_file(md, tmp_path, fix=False, dry_run=False)
        assert len(issues) == 1
        assert "空行" in issues[0][2]

    def test_fix_mode_writes_file(self, tmp_path):
        md = tmp_path / "test.md"
        content = "# Doc\n\n```mermaid\ngraph TD\n    A --> B\n\n    B --> C\n```\n"
        md.write_text(content, encoding="utf-8")
        issues, fixes = mm._process_file(md, tmp_path, fix=True, dry_run=False)
        assert fixes >= 1
        new_content = md.read_text(encoding="utf-8")
        assert "\n\n" not in new_content.split("```mermaid")[1].split("```")[0]

    def test_dry_run_does_not_write(self, tmp_path):
        md = tmp_path / "test.md"
        content = "# Doc\n\n```mermaid\ngraph TD\n    A --> B\n\n    B --> C\n```\n"
        md.write_text(content, encoding="utf-8")
        issues, fixes = mm._process_file(md, tmp_path, fix=True, dry_run=True)
        assert fixes >= 1
        assert md.read_text(encoding="utf-8") == content

    def test_multiple_mermaid_blocks(self, tmp_path):
        md = tmp_path / "test.md"
        content = (
            "# Doc\n\n"
            "```mermaid\ngraph TD\n    A --> B\n```\n\n"
            "```mermaid\nflowchart TD\n    subgraph 中文ID\n        X --> Y\n    end\n```\n"
        )
        md.write_text(content, encoding="utf-8")
        issues, fixes = mm._process_file(md, tmp_path, fix=False, dry_run=False)
        assert len(issues) == 1
        assert "裸中文ID" in issues[0][2]


class TestRun:
    """run() 集成测试。"""

    def test_all_clean(self, tmp_path, args_default, capsys):
        (tmp_path / "doc.md").write_text(
            "# Doc\n\n```mermaid\ngraph TD\n    A --> B\n```\n", encoding="utf-8"
        )
        ret = mm.run(tmp_path, args_default)
        assert ret == 0
        out = capsys.readouterr().out
        assert "检查通过" in out

    def test_errors_detected(self, tmp_path, args_default, capsys):
        (tmp_path / "doc.md").write_text(
            "# Doc\n\n```mermaid\ngraph TD\n    A --> B\n\n    B --> C\n```\n", encoding="utf-8"
        )
        ret = mm.run(tmp_path, args_default)
        assert ret == 1
        out = capsys.readouterr().out
        assert "错误: 1" in out

    def test_dry_run_mode(self, tmp_path, args_dryrun, capsys):
        (tmp_path / "doc.md").write_text(
            "# Doc\n\n```mermaid\ngraph TD\n    A --> B\n\n    B --> C\n```\n", encoding="utf-8"
        )
        ret = mm.run(tmp_path, args_dryrun)
        out = capsys.readouterr().out
        assert "dry-run" in out
        assert "预览" in out
