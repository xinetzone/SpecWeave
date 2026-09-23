"""WSL 透明桥接与 rootless 运行时自愈的 daemon-free 单测。

覆盖 2026-09-16 session sc-20260916-xmnn-build-shell 两个修复点：
  1. 桥接必须使用**非登录** ``bash -c``（登录 shell 的 enterns.sh 会
     ``su -l $USER`` 把任务劫持成交互 shell）；
  2. WSL VM 回收后 /run/user/<uid> 缺失时 ensure_wsl_rootless_runtime
     的平台判定、幂等与 sudo -n 兜底行为。
"""
import os
import subprocess
import sys
from types import SimpleNamespace

import pytest

from jpman_client.tasks import utils


@pytest.fixture
def bridge_harness(monkeypatch):
    """在 Windows 上截获 wsl.exe 调用，返回 (argv, env) 供断言。"""
    captured = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = argv
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(
        utils, "platform", SimpleNamespace(system=lambda: "Windows")
    )
    monkeypatch.setattr(utils, "_wsl_distro_available", lambda name: True)
    monkeypatch.setenv(utils.COMPOSE_WSL_DISTRO_ENV, "podman-machine-default")
    monkeypatch.setattr(subprocess, "run", fake_run)
    return captured


def test_bridge_uses_non_login_bash(bridge_harness):
    """回归：bash -lc 登录会话被 enterns su -l 劫持成交互 shell。"""
    distro = utils.run_in_wsl_bridge(argv=["native.build", "--pip-mirror", "tuna"])
    assert distro == "podman-machine-default"
    argv = bridge_harness["argv"]
    assert argv[:4] == ["wsl.exe", "-d", "podman-machine-default", "--"]
    assert argv[4] == "bash"
    assert "-c" in argv
    assert "-lc" not in argv
    assert "--login" not in argv
    script = argv[-1]
    # 非登录会话不读 profile，PATH/LANG 必须显式注入
    assert '$HOME/.local/bin:$PATH' in script
    assert 'LANG' in script
    # cwd 切换与原任务逐字保留（shlex.join 的 join 形式）
    assert "invoke native.build --pip-mirror tuna" in script


def test_bridge_empty_argv_does_not_enter_shell(monkeypatch, bridge_harness):
    """无任务参数（argv 缺省回退 sys.argv[1:] 为空）时返回 None，不裸开 shell。"""
    monkeypatch.setattr(sys, "argv", ["invoke"])
    assert utils.run_in_wsl_bridge(argv=None) is None
    assert "argv" not in bridge_harness


def test_bridge_failure_propagates_exit_code(monkeypatch):
    """桥接子进程非 0 必须上抛 Exit(rc)，防假成功。"""
    import invoke.exceptions

    monkeypatch.setattr(
        utils, "platform", SimpleNamespace(system=lambda: "Windows")
    )
    monkeypatch.setattr(utils, "_wsl_distro_available", lambda name: True)
    monkeypatch.setenv(utils.COMPOSE_WSL_DISTRO_ENV, "podman-machine-default")
    monkeypatch.setattr(
        subprocess, "run", lambda argv, **kw: SimpleNamespace(returncode=42)
    )
    with pytest.raises(invoke.exceptions.Exit) as ei:
        utils.run_in_wsl_bridge(argv=["native.ps"])
    assert ei.value.code == 42


# ---------------------------------------------------------------------------
# _wsl_probe / wsl_bridge_diagnosis
# 回归来源（2026-09-20，session sc-20260920-wsl-probe-stderr）：发行版状态
# Running 但 VM 层 execvpe(/bin/true) I/O error（wsl.exe exit 11），探测把
# stderr 吞掉后门禁只能提示 `wsl -l -v`——一个**看似健康**的死胡同。
# ---------------------------------------------------------------------------


def _probe_run(returncode: int, stderr: bytes):
    def fake_run(argv, **kwargs):
        return SimpleNamespace(returncode=returncode, stderr=stderr)

    return fake_run


def test_probe_surfaces_wsl_stderr_reason(monkeypatch):
    """探测失败必须带出 wsl.exe 的 stderr（UTF-16LE 诊断）原文。"""
    utils._wsl_probe.cache_clear()
    msg = "<3>WSL (176308 - Relay) ERROR: CreateProcessCommon:813: "
    msg += "execvpe(/bin/true) failed: I/O error"
    stderr = ("\ufeff" + msg + "\r\n").encode("utf-16-le")
    monkeypatch.setattr(subprocess, "run", _probe_run(11, stderr))
    ok, reason = utils._wsl_probe("probe-stderr-distro")
    assert ok is False
    assert "execvpe(/bin/true) failed: I/O error" in reason


def test_probe_utf8_stderr_fallback(monkeypatch):
    """stderr 无 NUL 时按 UTF-8 解（发行版不存在等宿主侧报错）。"""
    utils._wsl_probe.cache_clear()
    monkeypatch.setattr(subprocess, "run", _probe_run(1, b"no such distro\r\n"))
    ok, reason = utils._wsl_probe("probe-utf8-distro")
    assert ok is False
    assert reason == "no such distro"


def test_probe_without_stderr_falls_back_to_returncode(monkeypatch):
    utils._wsl_probe.cache_clear()
    monkeypatch.setattr(subprocess, "run", _probe_run(11, b""))
    ok, reason = utils._wsl_probe("probe-silent-distro")
    assert ok is False
    assert "11" in reason


def test_probe_wsl_missing_does_not_raise(monkeypatch):
    """无 wsl.exe（裸 Linux CI）必须返回原因而非抛 FileNotFoundError。"""
    utils._wsl_probe.cache_clear()

    def raise_fnf(argv, **kwargs):
        raise FileNotFoundError("wsl.exe")

    monkeypatch.setattr(subprocess, "run", raise_fnf)
    ok, reason = utils._wsl_probe("probe-missing-exe")
    assert ok is False
    assert "wsl.exe" in reason


def test_distro_available_is_bool_projection_and_cached(monkeypatch):
    """_wsl_distro_available 是布尔投影，且探测结果进程内缓存（只跑一次）。"""
    utils._wsl_probe.cache_clear()
    calls = []

    def fake_run(argv, **kwargs):
        calls.append(argv)
        return SimpleNamespace(returncode=0, stderr=b"")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert utils._wsl_distro_available("probe-cached-distro") is True
    assert utils._wsl_distro_available("probe-cached-distro") is True
    assert len(calls) == 1


def test_bridge_diagnosis_none_sentinel(monkeypatch):
    """COMPOSE_WSL_DISTRO=none 是显式关闭而非故障，但仍须说明。"""
    monkeypatch.setattr(utils.platform, "system", lambda: "Windows")
    monkeypatch.setenv(utils.COMPOSE_WSL_DISTRO_ENV, "none")
    assert "none" in utils.wsl_bridge_diagnosis()


def test_bridge_diagnosis_non_windows_empty(monkeypatch):
    monkeypatch.setattr(utils.platform, "system", lambda: "Linux")
    assert utils.wsl_bridge_diagnosis() == ""


def test_bridge_diagnosis_empty_when_bridge_ok(monkeypatch):
    monkeypatch.setattr(utils.platform, "system", lambda: "Windows")
    monkeypatch.delenv(utils.COMPOSE_WSL_DISTRO_ENV, raising=False)
    utils._wsl_probe.cache_clear()
    monkeypatch.setattr(subprocess, "run", _probe_run(0, b""))
    assert utils.wsl_bridge_diagnosis() == ""


def test_bridge_diagnosis_returns_probe_reason(monkeypatch):
    monkeypatch.setattr(utils.platform, "system", lambda: "Windows")
    monkeypatch.delenv(utils.COMPOSE_WSL_DISTRO_ENV, raising=False)
    utils._wsl_probe.cache_clear()
    monkeypatch.setattr(subprocess, "run", _probe_run(11, b"boom\r\n"))
    assert utils.wsl_bridge_diagnosis() == "boom"


# ---------------------------------------------------------------------------
# ensure_wsl_rootless_runtime
# ---------------------------------------------------------------------------


@pytest.fixture
def linux_wsl(monkeypatch):
    """模拟 WSL2 Linux：platform、/proc/version、os.getuid 均打桩。"""
    monkeypatch.setattr(utils.platform, "system", lambda: "Linux")
    monkeypatch.setattr(os, "getuid", lambda: 1000, raising=False)
    orig_read_text = utils.Path.read_text

    def fake_read_text(self, *a, **k):
        # WindowsPath('/proc/version') 的 str 是 '\proc\version'，用 as_posix 判定
        if self.as_posix() == "/proc/version":
            return "Linux version 6.6 (microsoft-standard-WSL2)"
        return orig_read_text(self, *a, **k)

    monkeypatch.setattr(utils.Path, "read_text", fake_read_text)
    sudo_calls = []

    def fake_run(cmd, **kwargs):
        sudo_calls.append(cmd)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    return sudo_calls


def test_ensure_runtime_non_linux_noop(monkeypatch):
    monkeypatch.setattr(
        utils.platform, "system", lambda: "Windows"
    )
    utils.ensure_wsl_rootless_runtime()  # 不抛、不触达 /proc


def test_ensure_runtime_non_wsl_linux_noop(monkeypatch):
    monkeypatch.setattr(utils.platform, "system", lambda: "Linux")
    monkeypatch.setattr(os, "getuid", lambda: 1000, raising=False)
    orig_read_text = utils.Path.read_text

    def fake_read_text(self, *a, **k):
        if self.as_posix() == "/proc/version":
            return "Linux version 6.6.0-generic (gcc@x86_64)"
        return orig_read_text(self, *a, **k)

    monkeypatch.setattr(utils.Path, "read_text", fake_read_text)
    called = []
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: called.append(a))
    monkeypatch.setattr(os.path, "isdir", lambda p: False)
    utils.ensure_wsl_rootless_runtime()
    assert called == []  # 裸 Linux 绝不 sudo 建目录


def test_ensure_runtime_existing_dir_idempotent(linux_wsl, monkeypatch):
    monkeypatch.setattr(os.path, "isdir", lambda p: True)
    utils.ensure_wsl_rootless_runtime()
    assert linux_wsl == []  # 目录在 → 不调 sudo


def test_ensure_runtime_creates_missing_dir(linux_wsl, monkeypatch):
    monkeypatch.setattr(os.path, "isdir", lambda p: False)
    utils.ensure_wsl_rootless_runtime()
    assert len(linux_wsl) == 1
    cmd = linux_wsl[0]
    assert "sudo -n mkdir -p /run/user/1000" in cmd
    assert "chown 1000:1000" in cmd
    assert "chmod 700" in cmd


def test_ensure_runtime_sudo_failure_warns_not_raises(linux_wsl, monkeypatch, capsys):
    monkeypatch.setattr(os.path, "isdir", lambda p: False)

    def fail(cmd, **kwargs):
        return SimpleNamespace(returncode=1, stderr="sudo: a password is required")

    monkeypatch.setattr(subprocess, "run", fail)
    utils.ensure_wsl_rootless_runtime()  # 不抛
    out = capsys.readouterr().out
    assert "/run/user/1000" in out
    assert "手工修复" in out


def test_ensure_runtime_xdg_fallback_when_empty(linux_wsl, monkeypatch):
    monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)
    monkeypatch.setattr(os.path, "isdir", lambda p: True)  # 含 wslg 与 run dir
    monkeypatch.setattr(os, "access", lambda p, m: True)
    utils.ensure_wsl_rootless_runtime()
    assert os.environ["XDG_RUNTIME_DIR"] == "/mnt/wslg/runtime-dir"
