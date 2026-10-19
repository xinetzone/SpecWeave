"""check-spec-output-archive.py 单元测试。

覆盖 spec 目录产出物归档检查的两侧契约：

- 过程件白名单放行：规划三件套（spec.md/tasks.md/review.md）、工作流声明过程件
  （facts.md/insights.md）与 seven-concepts-comprehensive-retro 复盘流程过程件
  （e-stage-pattern.md 的 E 阶段模式萃取、v-adversarial-review.md 的 V 对抗审查）；
- 真实产出物仍检出：analysis-report.md、article-content.md、task*-*.md 等最终交付物
  必须判为产出物并触发违规。

白名单是"放行哪类过程留痕"的契约，不能因为放行而丧失对真实交付物的检出能力。
"""


# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_lib_parent = _Path(__file__).resolve().parent
while not (_lib_parent / "lib").is_dir():
    _lib_parent = _lib_parent.parent
_sys.path.insert(0, str(_lib_parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import importlib.util
import sys
from pathlib import Path

import pytest

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "check_spec_output_archive",
    _SCRIPTS_DIR / "check-spec-output-archive.py",
)
csoa = importlib.util.module_from_spec(_spec)
sys.modules["check_spec_output_archive"] = csoa
_spec.loader.exec_module(csoa)


class TestWhitelistContract:
    """白名单契约：过程件应放行，废止命名仅作存量兼容。"""

    def test_spec_mode_triplet_allowed(self):
        for name in ("spec.md", "tasks.md", "review.md"):
            assert name in csoa.SPEC_ALLOWED_FILES

    def test_workflow_process_files_allowed(self):
        for name in ("facts.md", "insights.md"):
            assert name in csoa.SPEC_ALLOWED_FILES

    def test_seven_concepts_process_files_allowed(self):
        """seven-concepts-comprehensive-retro 约定的复盘过程件必须放行。"""
        for name in ("e-stage-pattern.md", "v-adversarial-review.md"):
            assert name in csoa.SPEC_ALLOWED_FILES

    def test_deprecated_checklist_only_tolerated(self):
        """checklist.md 为已废止命名，仅兼容存量，不得视为产出物违规。"""
        assert "checklist.md" in csoa.SPEC_ALLOWED_FILES


class TestOutputDetection:
    """产出物模式识别：正则命中即违规，与白名单互不干扰。"""

    @pytest.mark.parametrize(
        "name",
        [
            "analysis-report.md",
            "article-content.md",
            "cleaned-article.md",
            "task1-implementation.md",
            "prd-summary.md",
            "execution-retrospective.md",
            "core-insights.md",
            "learning-notes.md",
        ],
    )
    def test_real_output_detected(self, name):
        assert csoa.is_output_file(name) is True

    @pytest.mark.parametrize(
        "name", ["e-stage-pattern.md", "v-adversarial-review.md"]
    )
    def test_process_file_not_matched_as_output_pattern(self, name):
        assert csoa.is_output_file(name) is False


def _build_spec_dir(root: Path, files: list[str]) -> Path:
    """构造最小 spec 目录：含已完成的三件套任务状态。"""
    spec_dir = (
        root
        / ".trae"
        / "specs"
        / "retrospectives-insights"
        / "demo-comprehensive-retrospective-export"
    )
    spec_dir.mkdir(parents=True)
    (spec_dir / "spec.md").write_text("# demo spec\n", encoding="utf-8")
    (spec_dir / "tasks.md").write_text(
        "## [x] Task 1: demo\n\n- [x] **Status**: `completed`\n",
        encoding="utf-8",
    )
    for name in files:
        (spec_dir / name).write_text("demo\n", encoding="utf-8")
    return spec_dir


class TestScanSpec:
    """scan_spec 的目录级判定：白名单放行与违规标记的合成行为。"""

    def test_process_files_kept_as_allowed(self, tmp_path):
        spec_dir = _build_spec_dir(
            tmp_path, ["e-stage-pattern.md", "v-adversarial-review.md"]
        )
        result = csoa.scan_spec(spec_dir, tmp_path)

        assert set(result["allowed_files"]) >= {
            "spec.md",
            "tasks.md",
            "e-stage-pattern.md",
            "v-adversarial-review.md",
        }
        assert result["output_files"] == []
        assert result["has_violations"] is False

    def test_real_output_still_flagged_alongside_process_files(self, tmp_path):
        spec_dir = _build_spec_dir(
            tmp_path, ["e-stage-pattern.md", "analysis-report.md"]
        )
        result = csoa.scan_spec(spec_dir, tmp_path)

        assert "e-stage-pattern.md" in result["allowed_files"]
        assert result["output_files"] == ["analysis-report.md"]
        assert result["has_violations"] is True

    def test_unlisted_markdown_treated_as_output(self, tmp_path):
        """未列入白名单的 .md 落入兜底分支，仍判为产出物。"""
        spec_dir = _build_spec_dir(tmp_path, ["migration-plan.md"])
        result = csoa.scan_spec(spec_dir, tmp_path)

        assert "migration-plan.md" in result["output_files"]
        assert result["has_violations"] is True

    def test_non_markdown_categorized_as_other(self, tmp_path):
        spec_dir = _build_spec_dir(tmp_path, ["notes.txt"])
        result = csoa.scan_spec(spec_dir, tmp_path)

        assert "notes.txt" in result["other_files"]
        assert result["output_files"] == []
