"""CLI 测试：serve/check 子命令、回环守卫、单实例锁、帮助输出（TR-1.2）。"""

import subprocess
import sys
from pathlib import Path

import yaml

from travel_planner import cli
from travel_planner.lock import InstanceLock

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_cli_help():
    proc = subprocess.run(
        [sys.executable, "-m", "travel_planner", "--help"],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
        env={**__import__("os").environ, "PYTHONPATH": str(PROJECT_ROOT / "src")},
    )
    assert proc.returncode == 0
    assert "serve" in proc.stdout and "check" in proc.stdout


def test_check_reports_unconfigured(tmp_path, capsys):
    data_dir = tmp_path / "data"
    code = cli.main(["check", "--data-dir", str(data_dir)])
    out = capsys.readouterr().out
    assert code == 0
    assert "数据目录" in out
    assert "行程数量：0" in out
    assert "LLM 未配置" in out


def test_check_reports_configured(tmp_path, capsys):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "config.yaml").write_text(
        yaml.safe_dump(
            {"llm": {"base_url": "http://x/v1", "api_key": "sk-f", "model": "m", "timeout": 90}}
        ),
        encoding="utf-8",
    )
    code = cli.main(["check", "--data-dir", str(data_dir)])
    out = capsys.readouterr().out
    assert code == 0
    assert "LLM 已配置" in out and "m @ http://x/v1" in out


def test_check_rejects_root_direct_child(capsys):
    code = cli.main(["check", "--data-dir", "D:/tp-cli-child"])
    assert code == 1
    assert "磁盘根" in capsys.readouterr().out


def test_serve_rejects_non_loopback(capsys):
    code = cli.main(["serve", "--host", "0.0.0.0", "--data-dir", "unused"])
    assert code == 1
    assert "非回环" in capsys.readouterr().err


def test_serve_happy_path_and_lock_release(tmp_path, capsys, monkeypatch):
    import uvicorn

    calls = []
    monkeypatch.setattr(uvicorn, "run", lambda app, **kw: calls.append(kw))
    data_dir = tmp_path / "data"
    code = cli.main(["serve", "--data-dir", str(data_dir), "--port", "8799"])
    out = capsys.readouterr().out
    assert code == 0
    assert "已就绪" in out and "127.0.0.1" in out
    assert calls and calls[0]["host"] == "127.0.0.1" and calls[0]["port"] == 8799
    # serve 结束后锁已释放，可再次获取
    lock = InstanceLock(data_dir)
    lock.acquire_nowait()
    lock.release()


def test_serve_blocked_by_existing_instance(tmp_path, capsys):
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True)
    lock = InstanceLock(data_dir)
    lock.acquire_nowait()
    try:
        code = cli.main(["serve", "--data-dir", str(data_dir)])
        assert code == 1
        assert "已有 travel-planner 实例" in capsys.readouterr().err
    finally:
        lock.release()
