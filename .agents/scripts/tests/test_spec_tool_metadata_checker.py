"""spec_tool.metadata_checker 单元测试。

覆盖 check_spec_metadata / scan_spec_metadata / format_terminal_report 三个核心函数。
使用临时目录构造各种 spec 场景，验证元数据校验逻辑的正确性。
"""

import pytest
from pathlib import Path

from lib.spec_tool.metadata_checker import (
    check_spec_metadata,
    scan_spec_metadata,
    format_terminal_report,
)
from lib.spec_tool.constants import VALID_STATUSES


# ============================================================
# fixtures
# ============================================================

@pytest.fixture
def spec_dir(tmp_path: Path) -> Path:
    """创建一个空的 spec 目录（无任何文件）。"""
    d = tmp_path / "my-spec"
    d.mkdir()
    return d


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


# ============================================================
# check_spec_metadata — 三件套完整性
# ============================================================

class TestCheckSpecMetadataTriad:
    """三件套完整性检查（spec.md + tasks.md + review.md）。"""

    def test_all_three_present(self, spec_dir: Path, tmp_path: Path):
        _write(spec_dir / "spec.md", "---\nstatus: draft\n---\n\n# Test\n")
        _write(spec_dir / "tasks.md", "# Tasks\n")
        _write(spec_dir / "review.md", "# Review\n")
        r = check_spec_metadata(spec_dir / "spec.md", tmp_path)
        assert not any(v["type"] == "missing_triad" for v in r["violations"])

    def test_missing_review(self, spec_dir: Path, tmp_path: Path):
        _write(spec_dir / "spec.md", "---\nstatus: draft\n---\n\n# Test\n")
        _write(spec_dir / "tasks.md", "# Tasks\n")
        r = check_spec_metadata(spec_dir / "spec.md", tmp_path)
        missing = [v for v in r["violations"] if v["type"] == "missing_triad"]
        assert len(missing) == 1
        assert "review.md" in missing[0]["message"]
        assert missing[0]["severity"] == "error"

    def test_missing_tasks_and_review(self, spec_dir: Path, tmp_path: Path):
        _write(spec_dir / "spec.md", "---\nstatus: draft\n---\n\n# Test\n")
        r = check_spec_metadata(spec_dir / "spec.md", tmp_path)
        missing = [v for v in r["violations"] if v["type"] == "missing_triad"]
        assert len(missing) == 1
        assert "tasks.md" in missing[0]["message"]
        assert "review.md" in missing[0]["message"]


# ============================================================
# check_spec_metadata — frontmatter 存在性
# ============================================================

class TestCheckSpecMetadataFrontmatter:
    """frontmatter 存在性检查。"""

    def test_no_frontmatter(self, spec_dir: Path, tmp_path: Path):
        _write(spec_dir / "spec.md", "# Just a title\n\nNo frontmatter here.\n")
        _write(spec_dir / "tasks.md", "")
        _write(spec_dir / "review.md", "")
        r = check_spec_metadata(spec_dir / "spec.md", tmp_path)
        assert r["has_frontmatter"] is False
        assert any(v["type"] == "no_frontmatter" for v in r["violations"])
        no_fm = [v for v in r["violations"] if v["type"] == "no_frontmatter"][0]
        assert no_fm["severity"] == "error"

    def test_yaml_frontmatter(self, spec_dir: Path, tmp_path: Path):
        _write(spec_dir / "spec.md", "---\nstatus: draft\n---\n\n# Test\n")
        _write(spec_dir / "tasks.md", "")
        _write(spec_dir / "review.md", "")
        r = check_spec_metadata(spec_dir / "spec.md", tmp_path)
        assert r["has_frontmatter"] is True

    def test_toml_frontmatter(self, spec_dir: Path, tmp_path: Path):
        _write(spec_dir / "spec.md", "+++\nstatus = \"draft\"\n+++\n\n# Test\n")
        _write(spec_dir / "tasks.md", "")
        _write(spec_dir / "review.md", "")
        r = check_spec_metadata(spec_dir / "spec.md", tmp_path)
        assert r["has_frontmatter"] is True


# ============================================================
# check_spec_metadata — status 校验
# ============================================================

class TestCheckSpecMetadataStatus:
    """status 字段存在性与合法性校验。"""

    def test_missing_status(self, spec_dir: Path, tmp_path: Path):
        _write(spec_dir / "spec.md", "---\ntitle: \"Test\"\n---\n\n# Test\n")
        _write(spec_dir / "tasks.md", "")
        _write(spec_dir / "review.md", "")
        r = check_spec_metadata(spec_dir / "spec.md", tmp_path)
        assert r["status"] is None
        assert any(v["type"] == "missing_status" for v in r["violations"])
        ms = [v for v in r["violations"] if v["type"] == "missing_status"][0]
        assert ms["severity"] == "warning"

    def test_valid_status_draft(self, spec_dir: Path, tmp_path: Path):
        _write(spec_dir / "spec.md", "---\nstatus: draft\n---\n\n# Test\n")
        _write(spec_dir / "tasks.md", "")
        _write(spec_dir / "review.md", "")
        r = check_spec_metadata(spec_dir / "spec.md", tmp_path)
        assert r["status"] == "draft"
        assert not any(v["type"] == "invalid_status" for v in r["violations"])

    def test_all_valid_statuses(self, spec_dir: Path, tmp_path: Path):
        """所有合法 status 都应该通过校验。"""
        _write(spec_dir / "tasks.md", "")
        _write(spec_dir / "review.md", "")
        for status in VALID_STATUSES:
            _write(spec_dir / "spec.md", f"---\nstatus: {status}\n---\n\n# Test\n")
            r = check_spec_metadata(spec_dir / "spec.md", tmp_path)
            assert r["status"] == status
            assert not any(v["type"] == "invalid_status" for v in r["violations"]), \
                f"status '{status}' should be valid"

    def test_invalid_status(self, spec_dir: Path, tmp_path: Path):
        _write(spec_dir / "spec.md", "---\nstatus: complete\n---\n\n# Test\n")
        _write(spec_dir / "tasks.md", "")
        _write(spec_dir / "review.md", "")
        r = check_spec_metadata(spec_dir / "spec.md", tmp_path)
        assert r["status"] == "complete"
        assert any(v["type"] == "invalid_status" for v in r["violations"])
        inv = [v for v in r["violations"] if v["type"] == "invalid_status"][0]
        assert inv["severity"] == "error"
        assert "complete" in inv["message"]

    def test_status_with_quotes(self, spec_dir: Path, tmp_path: Path):
        """带引号的 status 值应被正确解析。"""
        _write(spec_dir / "spec.md", '---\nstatus: "draft"\n---\n\n# Test\n')
        _write(spec_dir / "tasks.md", "")
        _write(spec_dir / "review.md", "")
        r = check_spec_metadata(spec_dir / "spec.md", tmp_path)
        # parse_frontmatter_unified 去掉引号后返回纯值
        assert r["status"] == "draft"

    def test_toml_status(self, spec_dir: Path, tmp_path: Path):
        _write(spec_dir / "spec.md", '+++\nstatus = "in-progress"\n+++\n\n# Test\n')
        _write(spec_dir / "tasks.md", "")
        _write(spec_dir / "review.md", "")
        r = check_spec_metadata(spec_dir / "spec.md", tmp_path)
        assert r["status"] == "in-progress"
        assert not any(v["type"] == "invalid_status" for v in r["violations"])


# ============================================================
# scan_spec_metadata — 批量扫描
# ============================================================

class TestScanSpecMetadata:
    """批量扫描功能。"""

    def _make_spec(self, root: Path, name: str, *, fm: str = "---\nstatus: draft\n---\n", has_tasks: bool = True, has_review: bool = True):
        d = root / name
        d.mkdir()
        (d / "spec.md").write_text(fm + "\n# Test\n", encoding="utf-8")
        if has_tasks:
            (d / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
        if has_review:
            (d / "review.md").write_text("# Review\n", encoding="utf-8")
        return d

    def test_empty_dir(self, tmp_path: Path):
        """空目录返回全零统计。"""
        r = scan_spec_metadata(tmp_path / "nonexistent", tmp_path)
        assert r["total"] == 0
        assert r["error_count"] == 0
        assert r["warning_count"] == 0
        assert r["no_frontmatter"] == 0
        assert r["status_dist"] == {}

    def test_nonexistent_dir(self, tmp_path: Path):
        """不存在的目录返回全零统计（不抛异常）。"""
        r = scan_spec_metadata(tmp_path / "does-not-exist", tmp_path)
        assert r["total"] == 0

    def test_multiple_specs(self, tmp_path: Path):
        """多个 spec 正确统计总数和 status 分布。"""
        self._make_spec(tmp_path, "spec-a", fm="---\nstatus: draft\n---\n")
        self._make_spec(tmp_path, "spec-b", fm="---\nstatus: completed\n---\n")
        self._make_spec(tmp_path, "spec-c", fm="---\nstatus: draft\n---\n")
        r = scan_spec_metadata(tmp_path, tmp_path)
        assert r["total"] == 3
        assert r["status_dist"]["draft"] == 2
        assert r["status_dist"]["completed"] == 1
        assert r["error_count"] == 0
        assert r["warning_count"] == 0

    def test_nested_specs(self, tmp_path: Path):
        """嵌套目录下的 spec.md 也能被发现。"""
        (tmp_path / "theme1").mkdir()
        (tmp_path / "theme1" / "sub").mkdir(parents=True)
        (tmp_path / "theme2").mkdir()
        self._make_spec(tmp_path / "theme1", "spec-a")
        self._make_spec(tmp_path / "theme1" / "sub", "spec-b")
        self._make_spec(tmp_path / "theme2", "spec-c")
        r = scan_spec_metadata(tmp_path, tmp_path)
        assert r["total"] == 3

    def test_mixed_violations(self, tmp_path: Path):
        """混合违规场景的统计。"""
        # 正常
        self._make_spec(tmp_path, "good", fm="---\nstatus: draft\n---\n")
        # 无 frontmatter
        self._make_spec(tmp_path, "no-fm", fm="")
        # 缺 status
        self._make_spec(tmp_path, "no-status", fm="---\ntitle: Foo\n---\n")
        # 非法 status
        self._make_spec(tmp_path, "bad-status", fm="---\nstatus: foo-bar\n---\n")
        # 缺 review.md
        self._make_spec(tmp_path, "no-review", fm="---\nstatus: draft\n---\n", has_review=False)

        r = scan_spec_metadata(tmp_path, tmp_path)
        assert r["total"] == 5
        assert r["no_frontmatter"] == 1
        assert r["error_count"] >= 3  # no_fm + bad_status + no_review 至少 3 个错误
        assert r["warning_count"] >= 1  # missing_status 至少 1 个警告


# ============================================================
# format_terminal_report
# ============================================================

class TestFormatTerminalReport:
    """终端报告格式化。"""

    def test_clean_report(self, tmp_path: Path):
        report = {
            "total": 2,
            "no_frontmatter": 0,
            "error_count": 0,
            "warning_count": 0,
            "violations": [],
            "status_dist": {"draft": 2},
            "per_file": {},
        }
        text = format_terminal_report(report, tmp_path)
        assert "Spec 元数据扫描报告" in text
        assert "总计 spec.md 数: 2" in text
        assert "扫描通过" in text
        assert "draft" in text

    def test_report_with_errors(self, tmp_path: Path):
        report = {
            "total": 1,
            "no_frontmatter": 1,
            "error_count": 1,
            "warning_count": 0,
            "violations": [{
                "type": "no_frontmatter",
                "file": "test/spec.md",
                "message": "无 frontmatter",
                "severity": "error",
            }],
            "status_dist": {"(none)": 1},
            "per_file": {},
        }
        text = format_terminal_report(report, tmp_path)
        assert "发现 1 个错误" in text
        assert "no_frontmatter" in text
        assert "test/spec.md" in text
