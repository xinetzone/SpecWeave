"""docgen.py 单元测试。

覆盖主要使用场景：
- _dash_parse_yaml_simple: YAML frontmatter 简单解析
- _dash_scan_spec: Spec 任务状态扫描（completed/pending/in_progress）
- ThemeStatus/SpecStatus 数据类属性
- _nav_generate_table/_apps_generate_table/_dash_generate_table: 表格生成
- _nav_extract_title/_nav_extract_description: 文档元信息提取
- _apps_extract_title/_apps_extract_desc: 应用元信息提取
- _apps_update_compat: 兼容模式章节更新
"""

import pytest
from pathlib import Path
from argparse import Namespace

from docgen import (
    _dash_parse_yaml_simple,
    _dash_scan_spec,
    _dash_generate_table,
    _dash_scan_themes,
    _nav_extract_title,
    _nav_extract_description,
    _nav_scan_docs,
    _nav_generate_table,
    _apps_extract_title,
    _apps_extract_desc,
    _apps_scan,
    _apps_generate_table,
    _apps_update_compat,
    SpecStatus,
    ThemeStatus,
    UNCHECKED_LIST_RE,
    CHECKED_LIST_RE,
    UNCHECKED_HEADING_RE,
    CHECKED_HEADING_RE,
    COMPLETED_STATUSES,
)


class TestDashParseYamlSimple:
    """_dash_parse_yaml_simple 测试：简单 YAML frontmatter 解析。"""

    def test_empty_content(self):
        assert _dash_parse_yaml_simple("") == {}

    def test_no_frontmatter(self):
        content = "# Title\nSome content here."
        assert _dash_parse_yaml_simple(content) == {}

    def test_basic_frontmatter(self):
        content = "---\nstatus: completed\ntitle: Test\n---\n# Body"
        result = _dash_parse_yaml_simple(content)
        assert result["status"] == "completed"
        assert result["title"] == "Test"

    def test_quoted_values(self):
        content = '---\nstatus: "in progress"\ntitle: \'My Spec\'\n---\n'
        result = _dash_parse_yaml_simple(content)
        assert result["status"] == "in progress"
        assert result["title"] == "My Spec"

    def test_values_with_colons(self):
        content = "---\ndesc: this: has: colons\n---\n"
        result = _dash_parse_yaml_simple(content)
        assert result["desc"] == "this: has: colons"

    def test_whitespace_handling(self):
        content = "---\n  status  :  done  \n  priority : high\n---\n"
        result = _dash_parse_yaml_simple(content)
        assert result["status"] == "done"
        assert result["priority"] == "high"


class TestCheckboxRegex:
    """复选框正则测试。"""

    def test_unchecked_list(self):
        text = "- [ ] task 1\n- [x] task 2\n- [ ] task 3"
        assert len(UNCHECKED_LIST_RE.findall(text)) == 2

    def test_checked_list(self):
        text = "- [ ] task 1\n- [x] done\n- [X] DONE"
        assert len(CHECKED_LIST_RE.findall(text)) == 2

    def test_unchecked_heading(self):
        text = "## [ ] Section\n### [x] Done Section\n## [ ] Another"
        assert len(UNCHECKED_HEADING_RE.findall(text)) == 2

    def test_checked_heading_case_insensitive(self):
        text = "## [x] Done\n### [X] Also Done"
        assert len(CHECKED_HEADING_RE.findall(text)) == 2


class TestSpecStatus:
    """SpecStatus 数据类测试。"""

    def test_basic_creation(self):
        s = SpecStatus(name="test-spec", completed=False, total_tasks=5, done_tasks=2)
        assert s.name == "test-spec"
        assert s.completed is False
        assert s.total_tasks == 5
        assert s.done_tasks == 2


class TestThemeStatus:
    """ThemeStatus 数据类属性测试。"""

    def test_empty_theme(self):
        t = ThemeStatus(name="empty", specs=[])
        assert t.total == 0
        assert t.completed_count == 0
        assert t.in_progress_count == 0
        assert t.pending_count == 0
        assert t.progress == 100

    def test_all_completed(self):
        specs = [
            SpecStatus("a", True, 3, 3),
            SpecStatus("b", True, 5, 5),
        ]
        t = ThemeStatus(name="done", specs=specs)
        assert t.total == 2
        assert t.completed_count == 2
        assert t.in_progress_count == 0
        assert t.pending_count == 0
        assert t.progress == 100

    def test_mixed_status(self):
        specs = [
            SpecStatus("done", True, 3, 3),
            SpecStatus("ip", False, 5, 2),
            SpecStatus("pending", False, 4, 0),
        ]
        t = ThemeStatus(name="mixed", specs=specs)
        assert t.total == 3
        assert t.completed_count == 1
        assert t.in_progress_count == 1
        assert t.pending_count == 1
        assert t.progress == 33

    def test_all_pending(self):
        specs = [
            SpecStatus("a", False, 0, 0),
            SpecStatus("b", False, 0, 0),
        ]
        t = ThemeStatus(name="pending", specs=specs)
        assert t.completed_count == 0
        assert t.progress == 0


class TestDashScanSpec:
    """_dash_scan_spec 测试：Spec 目录任务状态扫描。"""

    def test_no_tasks_file(self, tmp_path):
        spec_dir = tmp_path / "my-spec"
        spec_dir.mkdir()
        status = _dash_scan_spec(spec_dir)
        assert status.name == "my-spec"
        assert status.completed is False
        assert status.total_tasks == 0

    def test_all_unchecked(self, tmp_path):
        spec_dir = tmp_path / "spec1"
        spec_dir.mkdir()
        tasks = spec_dir / "tasks.md"
        tasks.write_text("""# Tasks
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3
""", encoding="utf-8")
        status = _dash_scan_spec(spec_dir)
        assert status.total_tasks == 3
        assert status.done_tasks == 0
        assert status.completed is False

    def test_all_checked(self, tmp_path):
        spec_dir = tmp_path / "spec2"
        spec_dir.mkdir()
        tasks = spec_dir / "tasks.md"
        tasks.write_text("""# Tasks
- [x] Task 1
- [x] Task 2
""", encoding="utf-8")
        status = _dash_scan_spec(spec_dir)
        assert status.total_tasks == 2
        assert status.done_tasks == 2
        assert status.completed is True

    def test_partial_done(self, tmp_path):
        spec_dir = tmp_path / "spec3"
        spec_dir.mkdir()
        tasks = spec_dir / "tasks.md"
        tasks.write_text("""# Tasks
- [x] Done
- [ ] Not done
- [x] Also done
""", encoding="utf-8")
        status = _dash_scan_spec(spec_dir)
        assert status.total_tasks == 3
        assert status.done_tasks == 2
        assert status.completed is False

    def test_status_from_toml_frontmatter(self, tmp_path):
        spec_dir = tmp_path / "spec4"
        spec_dir.mkdir()
        tasks = spec_dir / "tasks.md"
        tasks.write_text("""---
status: completed
---
# Tasks
- [ ] Remaining
""", encoding="utf-8")
        status = _dash_scan_spec(spec_dir)
        assert status.completed is True
        assert status.done_tasks == status.total_tasks

    def test_status_from_yaml_frontmatter(self, tmp_path):
        spec_dir = tmp_path / "spec5"
        spec_dir.mkdir()
        tasks = spec_dir / "tasks.md"
        tasks.write_text("""---
status: done
---
# Tasks
- [ ] Still open
""", encoding="utf-8")
        status = _dash_scan_spec(spec_dir)
        assert status.completed is True

    def test_code_blocks_ignored(self, tmp_path):
        spec_dir = tmp_path / "spec6"
        spec_dir.mkdir()
        tasks = spec_dir / "tasks.md"
        tasks.write_text("""# Tasks
- [x] Real task

```markdown
- [ ] This is in code block
- [x] Also code
```

- [ ] Another real task
""", encoding="utf-8")
        status = _dash_scan_spec(spec_dir)
        assert status.total_tasks == 2
        assert status.done_tasks == 1

    def test_heading_checkboxes_counted(self, tmp_path):
        spec_dir = tmp_path / "spec7"
        spec_dir.mkdir()
        tasks = spec_dir / "tasks.md"
        tasks.write_text("""## [x] Phase 1
- [x] Task A
## [ ] Phase 2
- [ ] Task B
""", encoding="utf-8")
        status = _dash_scan_spec(spec_dir)
        assert status.total_tasks == 4
        assert status.done_tasks == 2


class TestDashGenerateTable:
    """_dash_generate_table 测试：看板表格生成。"""

    def test_all_completed_themes(self):
        themes = [
            ThemeStatus("core", [SpecStatus("a", True, 3, 3), SpecStatus("b", True, 2, 2)]),
        ]
        table = _dash_generate_table(themes)
        assert "100%" in table
        assert "🎉" in table
        assert "✅" in table

    def test_zero_progress(self):
        themes = [
            ThemeStatus("new", [SpecStatus("a", False, 0, 0)]),
        ]
        table = _dash_generate_table(themes)
        assert "0%" in table
        assert "📋" in table

    def test_partial_progress(self):
        themes = [
            ThemeStatus("wip", [
                SpecStatus("done", True, 3, 3),
                SpecStatus("ip", False, 5, 2),
            ]),
        ]
        table = _dash_generate_table(themes)
        assert "🔧" in table
        assert "50%" in table

    def test_empty_themes_list(self):
        table = _dash_generate_table([])
        assert "0/0" in table
        assert "0%" in table
        assert "🎉" in table

    def test_table_structure(self):
        themes = [ThemeStatus("test", [SpecStatus("a", True, 1, 1)])]
        table = _dash_generate_table(themes)
        assert "| 主题 |" in table
        assert "| Spec 数 |" in table
        assert "test" in table


class TestNavExtractTitle:
    """_nav_extract_title 测试。"""

    def test_with_h1(self, tmp_path):
        f = tmp_path / "doc.md"
        f.write_text("# My Document\nSome content", encoding="utf-8")
        assert _nav_extract_title(f) == "My Document"

    def test_without_h1_uses_stem(self, tmp_path):
        f = tmp_path / "my-doc.md"
        f.write_text("No title here\nJust content", encoding="utf-8")
        assert _nav_extract_title(f) == "my-doc"

    def test_h1_with_special_chars(self, tmp_path):
        f = tmp_path / "guide.md"
        f.write_text("# Guide: Part 1 — Intro\n", encoding="utf-8")
        assert "Guide" in _nav_extract_title(f)


class TestNavExtractDescription:
    """_nav_extract_description 测试。"""

    def test_manual_description_takes_priority(self, tmp_path):
        f = tmp_path / "project-overview.md"
        f.write_text("# Project\nWrong desc", encoding="utf-8")
        desc = _nav_extract_description(f)
        assert "项目定位" in desc

    def test_extracted_description_truncated(self, tmp_path):
        f = tmp_path / "long.md"
        long_desc = "A" * 100
        f.write_text(f"# Long\n\n{long_desc}", encoding="utf-8")
        desc = _nav_extract_description(f)
        assert len(desc) <= 60
        assert desc.endswith("...")

    def test_falls_back_to_title(self, tmp_path):
        f = tmp_path / "empty.md"
        f.write_text("# Just A Title", encoding="utf-8")
        desc = _nav_extract_description(f)
        assert "Just A Title" in desc or desc == "empty"


class TestNavGenerateTable:
    """_nav_generate_table 测试。"""

    def test_basic_table(self):
        entries = [
            ("Doc A", "a.md", "Description A", False),
            ("Doc B", "b.md", "Description B", False),
        ]
        table = _nav_generate_table(entries, "docs/", "")
        assert "| 文档 | 说明 |" in table
        assert "[Doc A](docs/a.md)" in table
        assert "[Doc B](docs/b.md)" in table
        assert "Description A" in table

    def test_root_file_prefix(self):
        entries = [("Root", "README.md", "Root doc", True)]
        table = _nav_generate_table(entries, "docs/", "")
        assert "[Root](README.md)" in table

    def test_empty_entries(self):
        table = _nav_generate_table([], "docs/", "")
        assert "| 文档 | 说明 |" in table
        assert "|------|------|" in table


class TestAppsExtractTitle:
    """_apps_extract_title 测试。"""

    def test_no_readme(self, tmp_path):
        app_dir = tmp_path / "myapp"
        app_dir.mkdir()
        assert _apps_extract_title(app_dir / "README.md", "myapp") == "myapp"

    def test_readme_with_title(self, tmp_path):
        app_dir = tmp_path / "coolapp"
        app_dir.mkdir()
        readme = app_dir / "README.md"
        readme.write_text("# Cool Application\nDesc here", encoding="utf-8")
        assert _apps_extract_title(readme, "coolapp") == "Cool Application"

    def test_readme_without_title(self, tmp_path):
        app_dir = tmp_path / "util"
        app_dir.mkdir()
        readme = app_dir / "README.md"
        readme.write_text("Just some text without title", encoding="utf-8")
        assert _apps_extract_title(readme, "util") == "util"


class TestAppsExtractDesc:
    """_apps_extract_desc 测试。"""

    def test_no_readme(self, tmp_path):
        readme = tmp_path / "nonexistent" / "README.md"
        desc = _apps_extract_desc(readme, "myapp")
        assert "myapp" in desc
        assert "应用" in desc

    def test_description_truncated(self, tmp_path):
        app_dir = tmp_path / "longapp"
        app_dir.mkdir()
        readme = app_dir / "README.md"
        long_desc = "B" * 200
        readme.write_text(f"# Long\n{long_desc}", encoding="utf-8")
        desc = _apps_extract_desc(readme, "longapp")
        assert len(desc) <= 80

    def test_falls_back_to_title(self, tmp_path):
        app_dir = tmp_path / "plain"
        app_dir.mkdir()
        readme = app_dir / "README.md"
        readme.write_text("# Plain App", encoding="utf-8")
        desc = _apps_extract_desc(readme, "plain")
        assert "Plain App" in desc or "plain" in desc


class TestAppsGenerateTable:
    """_apps_generate_table 测试。"""

    def test_basic_table(self):
        entries = [
            ("app1", "App One", "First application", True),
            ("app2", "App Two", "Second application", True),
        ]
        table = _apps_generate_table(entries)
        assert "| 应用 | 说明 | 入口 |" in table
        assert "`app1/`" in table
        assert "First application" in table
        assert "[README.md](app1/README.md)" in table

    def test_no_readme_uses_backtick(self):
        entries = [("no-readme", "No Readme App", "App without README", False)]
        table = _apps_generate_table(entries)
        assert "`no-readme/`（暂无 README）" in table
        assert "[README.md](no-readme/README.md)" not in table

    def test_empty_entries(self):
        table = _apps_generate_table([])
        assert "| 应用 | 说明 | 入口 |" in table


class TestAppsUpdateCompat:
    """_apps_update_compat 测试：兼容模式章节替换。"""

    def test_no_section_found(self):
        content = "# README\nSome content without apps section"
        result = _apps_update_compat(content, "| new table |")
        assert result is None

    def test_section_with_table(self):
        content = """# Main
Some text

### 2.3 应用清单

| 应用 | 说明 | 入口 |
|---|---|---|
| old/ | Old app | [README](old/README.md) |

## Next Section
More content
"""
        new_table = "| 应用 | 说明 | 入口 |\n|---|---|---|\n| new/ | New | [README](new/README.md) |"
        result = _apps_update_compat(content, new_table)
        assert result is not None
        assert "new/" in result
        assert "New" in result
        assert "## Next Section" in result
        assert "old/" not in result

    def test_section_at_end_of_file(self):
        content = """# Main
### 2.3 应用清单

Old content here
No more sections after this
"""
        new_table = "| new table |"
        result = _apps_update_compat(content, new_table)
        assert result is not None
        assert "new table" in result


class TestCompletedStatuses:
    """完成状态关键词测试。"""

    def test_known_completed_statuses(self):
        assert "completed" in COMPLETED_STATUSES
        assert "done" in COMPLETED_STATUSES
        assert "finished" in COMPLETED_STATUSES
        assert "complete" in COMPLETED_STATUSES

    def test_case_insensitive_matching(self):
        for s in ["Completed", "DONE", "Finished", "COMPLETE"]:
            assert s.lower() in COMPLETED_STATUSES
