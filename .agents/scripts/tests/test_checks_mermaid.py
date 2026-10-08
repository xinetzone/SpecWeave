"""lib.checks.mermaid 单元测试。"""


# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_lib_parent = _Path(__file__).resolve().parent
while not (_lib_parent / "lib").is_dir():
    _lib_parent = _lib_parent.parent
_sys.path.insert(0, str(_lib_parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

from lib.checks import mermaid as mm
from lib.mermaid.baseline import _aggregate_findings, collect_findings, write_baseline

_repo_check_path = Path(__file__).resolve().parents[1] / "repo-check.py"
_repo_check_spec = importlib.util.spec_from_file_location(
    "repo_check_cli", _repo_check_path
)
repo_check_cli = importlib.util.module_from_spec(_repo_check_spec)
_repo_check_spec.loader.exec_module(repo_check_cli)


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

    def test_prunes_excluded_directories_before_inspecting_markdown(
        self, tmp_path, monkeypatch
    ):
        from lib.mermaid.scanner import FileScanner

        excluded_file = tmp_path / "vendor" / "lib.md"
        excluded_file.parent.mkdir()
        excluded_file.write_text("excluded", encoding="utf-8")
        visible_file = tmp_path / "docs" / "guide.md"
        visible_file.parent.mkdir()
        visible_file.write_text("visible", encoding="utf-8")

        scanner = FileScanner(tmp_path, set())
        inspected = []
        original_should_include = scanner._should_include

        def record_inspected(path):
            inspected.append(path)
            return original_should_include(path)

        monkeypatch.setattr(scanner, "_should_include", record_inspected)

        files = scanner.scan()

        assert visible_file in files
        assert excluded_file not in inspected

    def test_excludes_custom_dirs(self, tmp_path):
        (tmp_path / "doc.md").write_text("a", encoding="utf-8")
        (tmp_path / "build").mkdir()
        (tmp_path / "build" / "out.md").write_text("b", encoding="utf-8")
        files = mm._find_md_files(tmp_path, {"build"})
        names = [f.name for f in files]
        assert "doc.md" in names
        assert "out.md" not in names

    def test_excludes_non_worktree_prefixes(self, tmp_path):
        (tmp_path / "doc.md").write_text("a", encoding="utf-8")
        backup_file = tmp_path / ".meta" / "backup" / "docs" / "backup.md"
        backup_file.parent.mkdir(parents=True)
        backup_file.write_text("b", encoding="utf-8")
        external_file = tmp_path / "external" / "vendor" / "external.md"
        external_file.parent.mkdir(parents=True)
        external_file.write_text("c", encoding="utf-8")
        playground_file = tmp_path / "playground" / "reports" / "play.md"
        playground_file.parent.mkdir(parents=True)
        playground_file.write_text("d", encoding="utf-8")

        files = mm._find_md_files(tmp_path, set())

        names = sorted(f.name for f in files)
        assert names == ["doc.md"]

    def test_excludes_git_ignored_markdown_but_keeps_untracked_files(self, tmp_path):
        subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
        (tmp_path / ".gitignore").write_text("ignored/\n", encoding="utf-8")
        (tmp_path / "ignored").mkdir()
        (tmp_path / "visible").mkdir()
        (tmp_path / "ignored" / "local.md").write_text("ignored", encoding="utf-8")
        (tmp_path / "visible" / "new.md").write_text("untracked", encoding="utf-8")

        files = mm._find_md_files(tmp_path, set())

        assert [path.relative_to(tmp_path).as_posix() for path in files] == [
            "visible/new.md"
        ]


class TestFixFlowchart:
    """_fix_flowchart 测试。"""

    def test_removes_blank_lines(self):
        block = "graph TD\n    A --> B\n\n    B --> C\n"
        fixed, fixes = mm._fix_flowchart(block)
        assert "空行" in fixes
        assert "\n\n" not in fixed

    def test_quotes_chinese_node_labels(self):
        block = 'graph TD\n    A[开始节点] --> B[结束]\n'
        fixed, fixes = mm._fix_flowchart(block)
        assert any("节点引号" in f for f in fixes)
        assert 'A["开始节点"]' in fixed
        assert 'B["结束"]' in fixed

    def test_does_not_double_quote(self):
        block = 'graph TD\n    A["开始"] --> B["结束"]\n'
        fixed, fixes = mm._fix_flowchart(block)
        assert not any("节点引号" in f for f in fixes)

    def test_quotes_chinese_edge_labels(self):
        block = 'graph TD\n    A -->|是| B\n'
        fixed, fixes = mm._fix_flowchart(block)
        assert '-->|"是"|' in fixed

    def test_ascii_nodes_unchanged(self):
        block = "graph TD\n    start[Start] --> end_node[End]\n"
        fixed, fixes = mm._fix_flowchart(block)
        assert not any("节点引号" in f for f in fixes)
        assert "start[Start]" in fixed

    def test_clean_block_no_fixes(self):
        block = 'graph TD\n    A["开始"] -->|"连接"| B["结束"]\n'
        fixed, fixes = mm._fix_flowchart(block)
        assert fixes == []


class TestCheckFlowchart:
    """_check_flowchart 测试。"""

    def test_clean_block(self):
        block = "graph TD\n    A --> B\n"
        issues = mm._check_flowchart(block, 1)
        assert issues == []

    def test_blank_line_error(self):
        block = "graph TD\n    A --> B\n\n    B --> C\n"
        issues = mm._check_flowchart(block, 1)
        assert len(issues) == 1
        assert issues[0][1] == "error"
        assert "空行" in issues[0][2]

    def test_chinese_subgraph_id(self):
        block = "flowchart TD\n    subgraph 模块A\n        A --> B\n    end\n"
        issues = mm._check_flowchart(block, 1)
        assert len(issues) >= 1
        assert any("裸ID" in i[2] for i in issues)
        assert any("模块A" in i[2] for i in issues)

    def test_valid_subgraph_quoted(self):
        block = 'flowchart TD\n    subgraph modA ["模块A"]\n        A --> B\n    end\n'
        issues = mm._check_flowchart(block, 1)
        assert issues == []

    def test_line_number_calculation(self):
        block = "graph TD\n\n    A --> B\n"
        issues = mm._check_flowchart(block, 10)
        assert issues[0][0] == 10


class TestVscodeCompatibility:
    """VS Code 兼容规则的正反例与边界测试。"""

    def test_accepts_compatible_block_and_top_level_direction(self):
        block = (
            'flowchart TD\n'
            '    direction LR\n'
            '    subgraph group ["模块"]\n'
            '        A["开始"] --> B["结束"]\n'
            '    end\n'
        )

        assert mm._check_vscode_compat(block, 1) == []

    @pytest.mark.parametrize(
        ("line", "expected_severity", "message"),
        [
            ('A["one<br/>two"] --> B', "error", "<br/>"),
            ('A["① first"] --> B', "error", "带圈数字"),
            ('A["【first】"] --> B', "error", "中文方括号"),
            ('A["first"] -->|"→"| B', "warning", "Unicode箭头符号"),
        ],
    )
    def test_reports_vscode_incompatible_syntax(
        self, line, expected_severity, message
    ):
        issues = mm._check_vscode_compat(f"flowchart TD\n    {line}\n", 1)

        assert len(issues) == 1
        assert issues[0][1] == expected_severity
        assert message in issues[0][2]

    def test_ignores_vscode_markers_inside_comments(self):
        block = (
            'flowchart TD\n'
            '    %% <br/> ①【 →\n'
            '    A["clean"] --> B %% <br/> ①【 →\n'
        )

        assert mm._check_vscode_compat(block, 1) == []

    def test_only_flags_direction_inside_subgraph(self):
        block = (
            'flowchart TD\n'
            '    direction LR\n'
            '    subgraph group ["模块"]\n'
            '        direction TB\n'
            '        A --> B\n'
            '    end\n'
            '    direction RL\n'
        )

        issues = mm._check_vscode_compat(block, 20)

        assert len(issues) == 1
        assert issues[0][0] == 23
        assert "subgraph 内嵌套 direction" in issues[0][2]


class TestClassDiagram:
    """classDiagram 测试。"""

    def test_detect_classdiagram(self):
        block = "classDiagram\n    class Animal\n"
        assert mm._detect_diagram_type(block) == "classDiagram"

    def test_clean_classdiagram(self):
        block = (
            "classDiagram\n"
            "    class Animal {\n"
            "        +String name\n"
            "        +int age\n"
            "        +makeSound()\n"
            "    }\n"
            "    class Dog {\n"
            "        +String breed\n"
            "        +bark()\n"
            "    }\n"
            '    Animal <|-- Dog : "继承"\n'
        )
        issues = mm._check_classDiagram(block, 1)
        assert issues == []

    def test_blank_line_error(self):
        block = "classDiagram\n    class Animal\n\n    class Dog\n"
        issues = mm._check_classDiagram(block, 1)
        assert len(issues) >= 1
        assert issues[0][1] == "error"
        assert "空行" in issues[0][2]

    def test_class_name_chinese(self):
        block = "classDiagram\n    class 动物\n    class 狗\n    动物 <|-- 狗 : 继承\n"
        issues = mm._check_classDiagram(block, 1)
        assert len(issues) >= 1
        assert any("类名" in i[2] and "中文" in i[2] for i in issues if i[1] == "error")

    def test_class_name_english(self):
        block = "classDiagram\n    class Animal\n    class Dog\n    Animal <|-- Dog\n"
        issues = mm._check_classDiagram(block, 1)
        assert not any("类名" in i[2] for i in issues if i[1] == "error")

    def test_relation_label_chinese(self):
        block = 'classDiagram\n    class Animal\n    class Dog\n    Animal <|-- Dog : 继承\n'
        issues = mm._check_classDiagram(block, 1)
        assert any("关系标签" in i[2] for i in issues if i[1] == "error")

    def test_fix_quotes_chinese_class(self):
        block = "classDiagram\n    class 动物\n    class 狗\n    动物 <|-- 狗 : 继承\n"
        fixed, fixes = mm._fix_classDiagram(block)
        assert any("类名引号" in f for f in fixes)
        assert 'class "动物"' in fixed
        assert 'class "狗"' in fixed

    def test_fix_blank_lines(self):
        block = "classDiagram\n    class Animal\n\n    class Dog\n"
        fixed, fixes = mm._fix_classDiagram(block)
        assert "空行" in fixes
        assert "\n\n" not in fixed


class TestErDiagram:
    """erDiagram 测试。"""

    def test_detect_erdiagram(self):
        block = "erDiagram\n    CUSTOMER ||--o{ ORDER : places\n"
        assert mm._detect_diagram_type(block) == "erDiagram"

    def test_clean_erdiagram(self):
        block = (
            "erDiagram\n"
            "    CUSTOMER ||--o{ ORDER : places\n"
            "    CUSTOMER {\n"
            "        string name\n"
            "        int id\n"
            "    }\n"
            "    ORDER {\n"
            "        int order_id\n"
            "        string product\n"
            "    }\n"
        )
        issues = mm._check_erDiagram(block, 1)
        assert issues == []

    def test_blank_line_error(self):
        block = "erDiagram\n    CUSTOMER ||--o{ ORDER : places\n\n    CUSTOMER {\n        string name\n    }\n"
        issues = mm._check_erDiagram(block, 1)
        assert len(issues) >= 1
        assert issues[0][1] == "error"
        assert "空行" in issues[0][2]

    def test_entity_name_chinese(self):
        block = "erDiagram\n    客户 ||--o{ 订单 : 下单\n    客户 {\n        string 姓名\n    }\n"
        issues = mm._check_erDiagram(block, 1)
        assert len(issues) >= 1
        assert any("实体名" in i[2] for i in issues if i[1] == "error")

    def test_entity_name_uppercase(self):
        block = "erDiagram\n    CUSTOMER ||--o{ ORDER : places\n"
        issues = mm._check_erDiagram(block, 1)
        assert not any("实体名" in i[2] for i in issues if i[1] == "error")

    def test_relation_label_chinese(self):
        block = 'erDiagram\n    CUSTOMER ||--o{ ORDER : 下单\n'
        issues = mm._check_erDiagram(block, 1)
        assert any("关系标签" in i[2] for i in issues if i[1] == "error")

    def test_fix_quotes_chinese_entity(self):
        block = "erDiagram\n    客户 ||--o{ 订单 : 下单\n    客户 {\n        string 姓名\n    }\n"
        fixed, fixes = mm._fix_erDiagram(block)
        assert any("实体名引号" in f for f in fixes)
        assert '"客户"' in fixed
        assert '"订单"' in fixed

    def test_fix_blank_lines(self):
        block = "erDiagram\n    CUSTOMER ||--o{ ORDER : places\n\n    CUSTOMER {\n        string name\n    }\n"
        fixed, fixes = mm._fix_erDiagram(block)
        assert "空行" in fixes
        assert "\n\n" not in fixed


class TestProcessFile:
    """_process_file 测试。"""

    def test_clean_file(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("# Title\n\nSome text.\n", encoding="utf-8")
        issues, fixes, diffs = mm._process_file(md, tmp_path, fix=False, dry_run=False)
        assert issues == []
        assert fixes == 0
        assert diffs == []

    def test_detects_mermaid_blank_lines(self, tmp_path):
        md = tmp_path / "test.md"
        content = "# Doc\n\n```mermaid\ngraph TD\n    A --> B\n\n    B --> C\n```\n"
        md.write_text(content, encoding="utf-8")
        issues, fixes, diffs = mm._process_file(md, tmp_path, fix=False, dry_run=False)
        assert len(issues) == 1
        assert "空行" in issues[0][2]

    def test_fix_mode_writes_file(self, tmp_path):
        md = tmp_path / "test.md"
        content = "# Doc\n\n```mermaid\ngraph TD\n    A --> B\n\n    B --> C\n```\n"
        md.write_text(content, encoding="utf-8")
        issues, fixes, diffs = mm._process_file(md, tmp_path, fix=True, dry_run=False)
        assert fixes >= 1
        new_content = md.read_text(encoding="utf-8")
        assert "\n\n" not in new_content.split("```mermaid")[1].split("```")[0]

    def test_dry_run_does_not_write(self, tmp_path):
        md = tmp_path / "test.md"
        content = "# Doc\n\n```mermaid\ngraph TD\n    A --> B\n\n    B --> C\n```\n"
        md.write_text(content, encoding="utf-8")
        issues, fixes, diffs = mm._process_file(md, tmp_path, fix=True, dry_run=True)
        assert fixes >= 1
        assert len(diffs) >= 1
        assert md.read_text(encoding="utf-8") == content

    def test_multiple_mermaid_blocks(self, tmp_path):
        md = tmp_path / "test.md"
        content = (
            "# Doc\n\n"
            "```mermaid\ngraph TD\n    A --> B\n```\n\n"
            "```mermaid\nflowchart TD\n    subgraph 中文ID\n        X --> Y\n    end\n```\n"
        )
        md.write_text(content, encoding="utf-8")
        issues, fixes, diffs = mm._process_file(md, tmp_path, fix=False, dry_run=False)
        assert len(issues) >= 1
        assert any("裸ID" in i[2] for i in issues)


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

    def test_baseline_mode_scans_markdown_file_list_once(self, tmp_path, monkeypatch, capsys):
        (tmp_path / "doc.md").write_text("# No Mermaid diagrams\n", encoding="utf-8")
        baseline_path = tmp_path / "baseline.json"
        write_baseline(
            baseline_path,
            {"schema_version": 1, "revision": "abc123", "findings": []},
        )
        original_find_md_files = mm._find_md_files
        scan_calls = []

        def count_scans(root, exclude_dirs):
            scan_calls.append((root, exclude_dirs))
            return original_find_md_files(root, exclude_dirs)

        monkeypatch.setattr(mm, "_find_md_files", count_scans)
        args = argparse.Namespace(
            path=None,
            exclude=[],
            fix=False,
            dry_run=False,
            json=False,
            baseline=str(baseline_path),
        )

        assert mm.run(tmp_path, args) == 0
        capsys.readouterr()
        assert len(scan_calls) == 1

    def test_baseline_mode_reports_historical_findings_without_blocking(self, tmp_path, capsys):
        (tmp_path / "doc.md").write_text(
            '```mermaid\nflowchart TD\n    A["one<br/>two"] --> B\n```\n',
            encoding="utf-8",
        )
        baseline_path = tmp_path / "baseline.json"
        write_baseline(
            baseline_path,
            {
                "schema_version": 1,
                "revision": "abc123",
                "findings": [
                    {
                        "path": "doc.md",
                        "rule_id": collect_findings(tmp_path)[0]["rule_id"],
                        "source": 'A["one<br/>two"] --> B',
                        "count": 1,
                    }
                ],
            },
        )
        original_baseline = baseline_path.read_bytes()
        args = argparse.Namespace(
            path=None,
            exclude=[],
            fix=False,
            dry_run=False,
            json=False,
            baseline=str(baseline_path),
        )

        result = mm.run(tmp_path, args)

        assert result == 0
        assert baseline_path.read_bytes() == original_baseline
        output = capsys.readouterr().out
        assert "历史债务" in output
        assert "新增: 0" in output

    def test_baseline_mode_uses_repository_relative_paths_for_scoped_scan(
        self, tmp_path, capsys
    ):
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        doc = docs_root / "guide.md"
        doc.write_text(
            '```mermaid\nflowchart TD\n    A["one<br/>two"] --> B\n```\n',
            encoding="utf-8",
        )
        baseline_path = tmp_path / "baseline.json"
        write_baseline(
            baseline_path,
            {
                "schema_version": 1,
                "revision": "abc123",
                "findings": _aggregate_findings(collect_findings(tmp_path)),
            },
        )
        args = argparse.Namespace(
            path=str(docs_root),
            exclude=[],
            fix=False,
            dry_run=False,
            json=False,
            baseline=str(baseline_path),
        )

        result = mm.run(tmp_path, args)

        assert result == 0
        output = capsys.readouterr().out
        assert "已知历史债务: 1" in output
        assert "新增: 0" in output
        assert "已消除: 0" in output

    def test_repo_check_main_keeps_repository_relative_path_for_scoped_scan(
        self, tmp_path, monkeypatch, capsys
    ):
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        (docs_root / "guide.md").write_text(
            '```mermaid\nflowchart TD\n    A["one<br/>two"] --> B\n```\n',
            encoding="utf-8",
        )
        baseline_path = tmp_path / "baseline.json"
        write_baseline(
            baseline_path,
            {
                "schema_version": 1,
                "revision": "abc123",
                "findings": _aggregate_findings(collect_findings(tmp_path)),
            },
        )
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(
            repo_check_cli, "resolve_project_root", lambda _path: tmp_path
        )
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "repo-check.py",
                "mermaid",
                "--path",
                "docs",
                "--baseline",
                str(baseline_path),
            ],
        )

        result = repo_check_cli.main()
        output = capsys.readouterr().out

        assert result == 0
        assert "已知历史债务: 1" in output
        assert "新增: 0" in output
        assert "已消除: 0" in output

    def test_scoped_baseline_scan_only_reports_excess_occurrences(
        self, tmp_path, capsys
    ):
        docs_root = tmp_path / "docs"
        docs_root.mkdir()
        doc = docs_root / "guide.md"
        single_finding = '    A["one<br/>two"] --> B'
        doc.write_text(
            f"```mermaid\nflowchart TD\n{single_finding}\n```\n",
            encoding="utf-8",
        )
        baseline_path = tmp_path / "baseline.json"
        write_baseline(
            baseline_path,
            {
                "schema_version": 1,
                "revision": "abc123",
                "findings": _aggregate_findings(collect_findings(tmp_path)),
            },
        )
        doc.write_text(
            f"```mermaid\nflowchart TD\n{single_finding}\n"
            f"{single_finding}\n```\n",
            encoding="utf-8",
        )
        args = argparse.Namespace(
            path=str(docs_root),
            exclude=[],
            fix=False,
            dry_run=False,
            json=False,
            baseline=str(baseline_path),
        )

        result = mm.run(tmp_path, args)

        assert result == 1
        output = capsys.readouterr().out
        assert "已知历史债务: 1" in output
        assert "新增: 1" in output
        assert "已消除: 0" in output

    def test_baseline_mode_blocks_added_occurrence(self, tmp_path, capsys):
        (tmp_path / "doc.md").write_text(
            '```mermaid\nflowchart TD\n    A["one<br/>two"] --> B\n```\n',
            encoding="utf-8",
        )
        baseline_path = tmp_path / "baseline.json"
        write_baseline(
            baseline_path,
            {
                "schema_version": 1,
                "revision": "abc123",
                "findings": [
                    {
                        "path": "doc.md",
                        "rule_id": collect_findings(tmp_path)[0]["rule_id"],
                        "source": 'A["one<br/>two"] --> B',
                        "count": 1,
                    }
                ],
            },
        )
        (tmp_path / "doc.md").write_text(
            '```mermaid\nflowchart TD\n'
            '    A["one<br/>two"] --> B\n'
            '    A["one<br/>two"] --> C\n'
            '```\n',
            encoding="utf-8",
        )
        args = argparse.Namespace(
            path=None,
            exclude=[],
            fix=False,
            dry_run=False,
            json=False,
            baseline=str(baseline_path),
        )

        result = mm.run(tmp_path, args)

        assert result == 1
        output = capsys.readouterr().out
        assert "新增: 1" in output
        assert "doc.md" in output

    def test_baseline_mode_blocks_finding_in_new_markdown_file(self, tmp_path, capsys):
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "new.md").write_text(
            '```mermaid\nflowchart TD\n    A["new<br/>finding"] --> B\n```\n',
            encoding="utf-8",
        )
        baseline_path = tmp_path / "baseline.json"
        write_baseline(
            baseline_path,
            {"schema_version": 1, "revision": "abc123", "findings": []},
        )
        args = argparse.Namespace(
            path=None,
            exclude=[],
            fix=False,
            dry_run=False,
            json=False,
            baseline=str(baseline_path),
        )

        assert mm.run(tmp_path, args) == 1
        output = capsys.readouterr().out
        assert "新增: 1" in output
        assert "docs/new.md" in output

    def test_prune_baseline_cli_only_reduces_registered_findings(self, tmp_path, capsys):
        current_source = 'A["one<br/>two"] --> B'
        (tmp_path / "doc.md").write_text(
            f"```mermaid\nflowchart TD\n    {current_source}\n```\n",
            encoding="utf-8",
        )
        (tmp_path / "new.md").write_text(
            '```mermaid\nflowchart TD\n    C["new<br/>finding"] --> D\n```\n',
            encoding="utf-8",
        )
        baseline_path = tmp_path / "baseline.json"
        baseline = {
            "schema_version": 1,
            "revision": "abc123",
            "findings": [
                {
                    "path": "doc.md",
                    "rule_id": collect_findings(tmp_path)[0]["rule_id"],
                    "source": current_source,
                    "count": 2,
                },
                {
                    "path": "old.md",
                    "rule_id": "vscode.br_tag",
                    "source": 'Z["removed<br/>finding"] --> Y',
                    "count": 1,
                },
            ],
        }
        write_baseline(baseline_path, baseline)
        args = argparse.Namespace(
            path=None,
            exclude=[],
            fix=False,
            dry_run=False,
            json=False,
            prune_baseline=str(baseline_path),
        )

        result = mm.run(tmp_path, args)

        assert result == 0
        pruned = json.loads(baseline_path.read_text(encoding="utf-8"))
        assert pruned["findings"] == [
            {
                "path": "doc.md",
                "rule_id": baseline["findings"][0]["rule_id"],
                "source": current_source,
                "count": 1,
            }
        ]
        assert "新违规未加入基线" in capsys.readouterr().out

    def test_prune_baseline_rejects_scoped_scan_without_modifying_baseline(
        self, tmp_path, capsys
    ):
        scoped_root = tmp_path / "subset"
        scoped_root.mkdir()
        (scoped_root / "doc.md").write_text(
            '```mermaid\nflowchart TD\n    A["current<br/>finding"] --> B\n```\n',
            encoding="utf-8",
        )
        baseline_path = tmp_path / "baseline.json"
        write_baseline(
            baseline_path,
            {
                "schema_version": 1,
                "revision": "abc123",
                "findings": [
                    {
                        "path": "doc.md",
                        "rule_id": collect_findings(scoped_root)[0]["rule_id"],
                        "source": 'A["current<br/>finding"] --> B',
                        "count": 1,
                    },
                    {
                        "path": "other.md",
                        "rule_id": "mermaid.known",
                        "source": "B --> C",
                        "count": 1,
                    },
                ],
            },
        )
        original_baseline = baseline_path.read_bytes()
        args = argparse.Namespace(
            path=str(scoped_root),
            exclude=[],
            fix=False,
            dry_run=False,
            json=False,
            prune_baseline=str(baseline_path),
        )

        result = mm.run(tmp_path, args)

        assert result == 1
        assert baseline_path.read_bytes() == original_baseline
        assert "只能对仓库根目录执行" in capsys.readouterr().out

    def test_fix_flattens_backslash_newline_without_reintroducing_br(self, tmp_path):
        md = tmp_path / "doc.md"
        md.write_text(
            '```mermaid\nflowchart TD\n    A["one\\ntwo"] --> B\n```\n',
            encoding="utf-8",
        )

        issues, fixes, _ = mm._process_file(md, tmp_path, fix=True, dry_run=False)

        assert fixes == 1
        assert not [issue for issue in issues if issue[1] == "error"]
        assert 'A["one two"] --> B' in md.read_text(encoding="utf-8")
        assert "<br/>" not in md.read_text(encoding="utf-8")

    def test_check_mermaid_cli_fixes_backslash_newline_end_to_end(self, tmp_path):
        md = tmp_path / "doc.md"
        md.write_text(
            '```mermaid\nflowchart TD\n    A["one\\ntwo"] --> B\n```\n',
            encoding="utf-8",
        )
        check_mermaid_cli = _repo_check_path.with_name("check-mermaid.py")

        result = subprocess.run(
            [
                sys.executable,
                str(check_mermaid_cli),
                "--path",
                str(tmp_path),
                "--fix",
            ],
            cwd=_repo_check_path.parents[2],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

        fixed_content = md.read_text(encoding="utf-8")
        assert result.returncode == 0, result.stdout + result.stderr
        assert "所有 Mermaid 代码块检查通过" in result.stdout
        assert 'A["one two"] --> B' in fixed_content
        assert "<br/>" not in fixed_content

    def test_dry_run_mode(self, tmp_path, args_dryrun, capsys):
        (tmp_path / "doc.md").write_text(
            "# Doc\n\n```mermaid\ngraph TD\n    A --> B\n\n    B --> C\n```\n", encoding="utf-8"
        )
        ret = mm.run(tmp_path, args_dryrun)
        out = capsys.readouterr().out
        assert "dry-run" in out
        assert "预览" in out
