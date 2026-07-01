import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SG = ROOT / "check-stage-guardrails.py"


def run_sg(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SG), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def test_demo_normal_exit_zero() -> None:
    r = run_sg("--demo")
    assert r.returncode == 0
    assert "[STRICT MODE]" not in (r.stdout or "")


def test_demo_strict_exit_one_with_header() -> None:
    r = run_sg("--demo", "--strict")
    assert r.returncode == 1
    assert "[STRICT MODE]" in (r.stdout or "")


def test_clean_log_strict_exit_zero() -> None:
    clean_log = (
        '[SG-LOG] | level=INFO | event=STAGE_ENTER | stage=S1 | role=developer | session=test | msg=enter S1 | ctx={"entry_condition":"ok","prev_stage":null}\n'
        '[PDR-LOG] | level=INFO | event=PDR_START | stage=S1 | role=developer | session=test | msg=start PDR | ctx={"required_count":1}\n'
        '[PDR-LOG] | level=INFO | event=PDR_DOC_READ | stage=S1 | role=developer | session=test | msg=read doc | ctx={"doc":"README.md","bytes":100,"key_points":["a"]}\n'
        '[PDR-LOG] | level=INFO | event=PDR_CONFIRM | stage=S1 | role=developer | session=test | msg=PDR done | ctx={"read_count":1,"missing_count":0,"missing_with_risk":0,"ready_to_proceed":true}\n'
        '[SG-LOG] | level=INFO | event=STAGE_EXIT | stage=S1 | role=developer | session=test | msg=exit S1 | ctx={"exit_criteria_met":["done"],"duration":"1min","output_artifacts":["x"],"next_stage":"S2"}\n'
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False, encoding="utf-8") as f:
        f.write(clean_log)
        tmpname = f.name
    try:
        r = run_sg("--log-file", tmpname, "--strict")
        assert r.returncode == 0
    finally:
        os.unlink(tmpname)


def test_warn_log_strict_exit_one() -> None:
    warn_log = (
        '[SG-LOG] | level=INFO | event=STAGE_ENTER | stage=S1 | role=developer | session=test | msg=enter S1 | ctx={"entry_condition":"ok","prev_stage":null}\n'
        '[SG-LOG] | level=INFO | event=STAGE_ENTER | stage=S4 | role=developer | session=test | msg=skip to S4 | ctx={"entry_condition":"direct","prev_stage":"S1"}\n'
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False, encoding="utf-8") as f:
        f.write(warn_log)
        tmpname = f.name
    try:
        r = run_sg("--log-file", tmpname, "--strict")
        assert r.returncode == 1
        assert "NO_PDR_FOR_STAGE" in (r.stdout or "")
    finally:
        os.unlink(tmpname)
