"""TR-1：CLI ``serve`` / ``check`` 与 ``python -m`` 入口。"""

import subprocess
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from zhihu_checkin_hub.cli import app

FIXTURE = Path(__file__).parent / "fixtures" / "tracker.md"
SRC = Path(__file__).resolve().parents[1] / "src"

runner = CliRunner()


@pytest.fixture()
def workbench(tmp_path: Path) -> Path:
    import shutil

    root = tmp_path / "zhihu-monetization"
    root.mkdir()
    shutil.copy(FIXTURE, root / "tracker.md")
    return root


def test_check_ok(workbench: Path) -> None:
    r = runner.invoke(app, ["check", "-w", str(workbench)])
    assert r.exit_code == 0, r.output
    assert "工作区校验通过" in r.output
    assert str(workbench) in r.output


def test_check_bad_workspace(tmp_path: Path) -> None:
    r = runner.invoke(app, ["check", "-w", str(tmp_path / "missing")])
    assert r.exit_code == 1
    assert "校验失败" in r.output


def test_serve_launches_uvicorn_loopback(workbench: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: dict[str, object] = {}

    def fake_run(app_obj, *, host: str, port: int, log_level: str) -> None:
        calls.update(host=host, port=port, log_level=log_level, app=app_obj)

    monkeypatch.setattr("uvicorn.run", fake_run)
    r = runner.invoke(app, ["serve", "-w", str(workbench), "-p", "8799"])
    assert r.exit_code == 0, r.output
    assert calls["host"] == "127.0.0.1"
    assert calls["port"] == 8799
    assert "访问地址" in r.output
    # 真实 serve 必须接线单实例锁：第二实例拿不到锁
    from zhihu_checkin_hub.errors import WorkspaceError
    from zhihu_checkin_hub.web.security import SingleInstanceLock

    svc = calls["app"].state.svc
    assert svc.lock is not None
    second = SingleInstanceLock(svc.cfg.workspace.local / ".serve.lock")
    with pytest.raises(WorkspaceError):
        second.acquire_nonblocking()


def test_serve_bad_workspace(tmp_path: Path) -> None:
    r = runner.invoke(app, ["serve", "-w", str(tmp_path / "missing")])
    assert r.exit_code == 1
    assert "启动失败" in r.output


def test_python_m_entrypoint_help() -> None:
    env = {**__import__("os").environ, "PYTHONPATH": str(SRC)}
    proc = subprocess.run(
        [sys.executable, "-m", "zhihu_checkin_hub", "--help"],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert "serve" in proc.stdout and "check" in proc.stdout
