"""测试公共 fixture：假 wsl 输出注入，不触发任何真实 WSL 调用。"""

from pathlib import Path
from types import SimpleNamespace

import pytest

from okw import distro

REPO_ROOT = Path(__file__).resolve().parents[4]  # D:\spaces\SpecWeave

def make_result(ok=True, exit_code=0, stdout="", stderr="", kind="ok") -> distro.CmdResult:
    return distro.CmdResult(ok, exit_code, stdout, stderr, kind)

def make_proc(returncode=0, stdout="", stderr=""):
    """模拟 subprocess.CompletedProcess（供 mock _run_subprocess 层使用）。"""
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)

@pytest.fixture
def fake_run(monkeypatch):
    """mock distro._run_subprocess：按谓词脚本返回 CompletedProcess 形状，记录调用。

    用法：script.append((lambda cmd: "-l -v" in cmd, make_proc(stdout="..."))).
    """
    calls: list[list[str]] = []
    script: list[tuple] = []

    def _fake(cmd, env, timeout):
        calls.append(cmd)
        for pred, result in script:
            if pred(cmd):
                return result
        return make_proc()

    monkeypatch.setattr(distro, "_run_subprocess", _fake)
    return SimpleNamespace(calls=calls, script=script)

@pytest.fixture
def fake_run_wsl(monkeypatch):
    """mock distro.run_wsl：按子串分支返回，记录调用（verify/cli 层用）。"""
    calls: list[list[str]] = []
    script: dict[str, distro.CmdResult] = {}

    def _run(args, timeout=60):
        calls.append(args)
        joined = " ".join(args)
        for key, result in script.items():
            if key in joined:
                return result
        return make_result(False, 1, "", "发行版不存在", "distro_missing")

    monkeypatch.setattr(distro, "run_wsl", _run)
    return SimpleNamespace(calls=calls, script=script)
