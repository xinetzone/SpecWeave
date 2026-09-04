"""spec_tool CLI 集成测试。

通过直接调用 cmd_check / cmd_format 函数，验证命令行参数解析和
端到端流程的正确性。重点覆盖：
- check --meta-only 的文本/JSON 输出
- format --fix-frontmatter 的 dry-run 和实际执行
- 退出码语义（0=通过, 1=有错误, 2=文件不存在等）
"""

import io
import json
import pytest
import sys
from pathlib import Path
from argparse import Namespace

from lib.spec_tool.check_cmd import cmd_check
from lib.spec_tool.format_cmd import cmd_format


# ============================================================
# helpers
# ============================================================

def _make_spec(tmp_path: Path, name: str, content: str, *, tasks: bool = True, review: bool = True) -> Path:
    """在 tmp_path 下创建一个 spec 目录，返回 spec.md 路径。"""
    d = tmp_path / name
    d.mkdir()
    (d / "spec.md").write_text(content, encoding="utf-8")
    if tasks:
        (d / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
    if review:
        (d / "review.md").write_text("# Review\n", encoding="utf-8")
    return d / "spec.md"


def _capture_stdout(func, *args, **kwargs):
    """捕获 stdout 输出。"""
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        rc = func(*args, **kwargs)
        output = sys.stdout.getvalue()
    finally:
        sys.stdout = old_stdout
    return rc, output


# ============================================================
# check --meta-only 集成测试
# ============================================================

class TestCheckMetaOnly:
    """check --meta-only 子命令集成测试。"""

    def test_clean_specs_exit_0(self, tmp_path: Path):
        """所有 spec 都合规时退出码为 0。"""
        _make_spec(tmp_path, "spec-a", "---\nstatus: draft\n---\n\n# A\n")
        _make_spec(tmp_path, "spec-b", "---\nstatus: completed\n---\n\n# B\n")

        args = Namespace(
            path=tmp_path,
            spec_dir=str(tmp_path),
            meta_only=True,
            json=False,
            match_threshold=70,
        )
        rc, output = _capture_stdout(cmd_check, args)
        assert rc == 0
        assert "Spec 元数据扫描报告" in output
        assert "扫描通过" in output

    def test_with_errors_exit_1(self, tmp_path: Path):
        """有错误时退出码为 1。"""
        _make_spec(tmp_path, "bad", "# No FM\n", review=False)

        args = Namespace(
            path=tmp_path,
            spec_dir=str(tmp_path),
            meta_only=True,
            json=False,
            match_threshold=70,
        )
        rc, output = _capture_stdout(cmd_check, args)
        assert rc == 1
        assert "发现" in output and "错误" in output

    def test_json_output(self, tmp_path: Path):
        """JSON 输出格式正确。"""
        _make_spec(tmp_path, "spec-a", "---\nstatus: draft\n---\n\n# A\n")

        args = Namespace(
            path=tmp_path,
            spec_dir=str(tmp_path),
            meta_only=True,
            json=True,
            match_threshold=70,
        )
        rc, output = _capture_stdout(cmd_check, args)
        assert rc == 0
        data = json.loads(output)
        assert data["total"] == 1
        assert "status_dist" in data
        assert "violations" in data
        assert data["error_count"] == 0

    def test_nonexistent_dir_exit_1(self, tmp_path: Path):
        """目录不存在时退出码为 1。"""
        args = Namespace(
            path=tmp_path,
            spec_dir=str(tmp_path / "nope"),
            meta_only=True,
            json=False,
            match_threshold=70,
        )
        rc, output = _capture_stdout(cmd_check, args)
        assert rc == 1
        assert "不存在" in output

    def test_single_spec_file(self, tmp_path: Path):
        """指定单个 spec.md 文件进行检查。"""
        spec = _make_spec(tmp_path, "mytest", "---\nstatus: in-progress\n---\n\n# Test\n")

        args = Namespace(
            path=tmp_path,
            spec_dir=str(spec),
            meta_only=True,
            json=True,
            match_threshold=70,
        )
        rc, output = _capture_stdout(cmd_check, args)
        assert rc == 0
        data = json.loads(output)
        assert data["total"] == 1
        assert data["status_dist"]["in-progress"] == 1


# ============================================================
# format --fix-frontmatter 集成测试
# ============================================================

class TestFormatFixFrontmatter:
    """format --fix-frontmatter 子命令集成测试。"""

    def test_dry_run_no_changes(self, tmp_path: Path):
        """dry-run 模式下文件不应被修改。"""
        spec = _make_spec(tmp_path, "nofm", "# My Title\n\nbody\n")
        original = spec.read_text(encoding="utf-8")

        args = Namespace(
            path=tmp_path,
            spec_dir=str(tmp_path),
            fix_frontmatter=True,
            dry_run=True,
            default_status="draft",
            add_date=False,
            format="text",
            json=False,
            verbose=False,
            check_all=False,
        )
        rc, output = _capture_stdout(cmd_format, args)
        assert rc == 0
        assert "预览模式" in output
        # 文件内容应不变
        assert spec.read_text(encoding="utf-8") == original

    def test_actual_add_frontmatter(self, tmp_path: Path):
        """实际新增 frontmatter。"""
        spec = _make_spec(tmp_path, "nofm", "# My Awesome Spec\n\nbody\n")

        args = Namespace(
            path=tmp_path,
            spec_dir=str(tmp_path),
            fix_frontmatter=True,
            dry_run=False,
            default_status="draft",
            add_date=False,
            format="text",
            json=False,
            verbose=False,
            check_all=False,
        )
        rc, output = _capture_stdout(cmd_format, args)
        assert rc == 0
        content = spec.read_text(encoding="utf-8")
        assert content.startswith("---\n")
        assert 'title: "My Awesome Spec"' in content
        assert 'status: "draft"' in content

    def test_json_output(self, tmp_path: Path):
        """JSON 输出格式正确。"""
        _make_spec(tmp_path, "nofm", "# Test\n")

        args = Namespace(
            path=tmp_path,
            spec_dir=str(tmp_path),
            fix_frontmatter=True,
            dry_run=True,
            default_status="draft",
            add_date=False,
            format="json",
            json=True,
            verbose=False,
            check_all=False,
        )
        rc, output = _capture_stdout(cmd_format, args)
        assert rc == 0
        data = json.loads(output)
        assert data["total"] == 1
        assert data["dry_run"] is True
        assert "stats" in data
        assert data["stats"]["would_add"] == 1
        assert "results" in data
        assert len(data["results"]) == 1

    def test_nonexistent_dir_exit_2(self, tmp_path: Path):
        """目录不存在时退出码为 2。"""
        args = Namespace(
            path=tmp_path,
            spec_dir=str(tmp_path / "nope"),
            fix_frontmatter=True,
            dry_run=True,
            default_status="draft",
            add_date=False,
            format="text",
            json=False,
            verbose=False,
            check_all=False,
        )
        rc, output = _capture_stdout(cmd_format, args)
        assert rc == 2

    def test_empty_dir(self, tmp_path: Path):
        """空目录返回 0 但提示未找到文件。"""
        empty = tmp_path / "empty"
        empty.mkdir()

        args = Namespace(
            path=tmp_path,
            spec_dir=str(empty),
            fix_frontmatter=True,
            dry_run=True,
            default_status="draft",
            add_date=False,
            format="text",
            json=False,
            verbose=False,
            check_all=False,
        )
        rc, output = _capture_stdout(cmd_format, args)
        assert rc == 0
        assert "未找到" in output

    def test_mixed_batch(self, tmp_path: Path):
        """批量处理混合场景（--fix-frontmatter 默认开启所有修复）。"""
        # 已有合法 status
        _make_spec(tmp_path, "good", "---\nstatus: draft\n---\n\n# Good\n")
        # 无 frontmatter
        _make_spec(tmp_path, "no-fm", "# No FM\n")
        # 缺 status
        _make_spec(tmp_path, "no-status", '---\ntitle: "Test"\n---\n\n# Test\n')
        # 非法 status（可归一化）
        _make_spec(tmp_path, "bad-status", "---\nstatus: complete\n---\n\n# Test\n")

        args = Namespace(
            path=tmp_path,
            spec_dir=str(tmp_path),
            fix_frontmatter=True,
            dry_run=True,
            default_status="draft",
            add_date=False,
            format="json",
            json=True,
            verbose=False,
            check_all=False,
        )
        rc, output = _capture_stdout(cmd_format, args)
        assert rc == 0
        data = json.loads(output)
        assert data["total"] == 4
        # --fix-frontmatter 默认开启所有修复：新增 + 补 status + 归一化
        assert data["stats"]["would_add"] == 1         # 无 frontmatter 的
        assert data["stats"]["would_add_status"] == 1  # 缺 status 的
        assert data["stats"]["would_normalize"] == 1   # 非法 status 的
        assert data["stats"]["skipped"] == 1           # 已有合法 status 的
