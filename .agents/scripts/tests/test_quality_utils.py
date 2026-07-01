import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from lib.quality_report import ResultGroupMixin, issue_list, score_to_ansi
from lib.quality_rules import count_file_urls


@dataclass
class DummyResult:
    name: str
    passed: bool
    severity: str
    message: str


@dataclass
class DummyReport(ResultGroupMixin):
    results: list[DummyResult]


def test_count_file_urls() -> None:
    content = "[a](file:///C:/x/y.md) <file:///D:/a/b.md>"
    assert count_file_urls(content) == 2


def test_result_group_mixin_classifies() -> None:
    report = DummyReport(
        results=[
            DummyResult(name="a", passed=False, severity="error", message="e"),
            DummyResult(name="b", passed=False, severity="warn", message="w"),
            DummyResult(name="c", passed=True, severity="warn", message="p"),
        ]
    )
    assert [r.name for r in report.errors] == ["a"]
    assert [r.name for r in report.warnings] == ["b"]
    assert [r.name for r in report.passes] == ["c"]


def test_issue_list() -> None:
    items = [DummyResult(name="x", passed=False, severity="error", message="m")]
    assert issue_list(items) == [{"name": "x", "message": "m"}]


def test_score_to_ansi() -> None:
    assert score_to_ansi(80) == "\033[92m"
    assert score_to_ansi(60) == "\033[93m"
    assert score_to_ansi(59) == "\033[91m"


def test_lib_init_can_run_as_script() -> None:
    lib_init = Path(__file__).resolve().parents[1] / "lib" / "__init__.py"
    result = subprocess.run(
        [sys.executable, str(lib_init)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert result.returncode == 0
    stdout = result.stdout or ""
    assert "# .agents/scripts/lib/ API" in stdout
    assert "lib.project" in stdout
