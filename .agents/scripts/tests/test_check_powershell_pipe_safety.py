"""check-powershell-pipe-safety.py 单元测试。"""

import importlib.util
import sys
from pathlib import Path


_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "check_powershell_pipe_safety", _SCRIPTS_DIR / "check-powershell-pipe-safety.py"
)
check_powershell_pipe_safety = importlib.util.module_from_spec(_spec)
sys.modules["check_powershell_pipe_safety"] = check_powershell_pipe_safety
_spec.loader.exec_module(check_powershell_pipe_safety)

from check_powershell_pipe_safety import collect_targets, is_risky_powershell_pipe, scan_file


def test_is_risky_powershell_pipe_for_readme_write() -> None:
    line = "python .agents/scripts/lib/__init__.py | Set-Content .agents/scripts/lib/README.md"
    assert is_risky_powershell_pipe(line) is True


def test_is_not_risky_without_python() -> None:
    line = "Get-Content input.txt | Set-Content output.txt"
    assert is_risky_powershell_pipe(line) is False


def test_is_not_risky_for_non_markdown_target() -> None:
    line = "python script.py | Set-Content output.txt"
    assert is_risky_powershell_pipe(line) is False


def test_scan_file_returns_finding(tmp_path: Path) -> None:
    script = tmp_path / "demo.ps1"
    script.write_text(
        "python .agents/scripts/lib/__init__.py | Set-Content .agents/scripts/lib/README.md\n",
        encoding="utf-8",
    )
    findings = scan_file(script, tmp_path)
    assert len(findings) == 1
    assert findings[0].line_number == 1
    assert "README.md" in findings[0].line_text


def test_collect_targets_filters_extensions(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("print('x')", encoding="utf-8")
    (tmp_path / "b.ps1").write_text("Write-Host hi", encoding="utf-8")
    (tmp_path / "c.sh").write_text("echo hi", encoding="utf-8")
    (tmp_path / "note.md").write_text("# note", encoding="utf-8")
    targets = collect_targets(tmp_path)
    names = [p.name for p in targets]
    assert names == ["a.py", "b.ps1", "c.sh"]
