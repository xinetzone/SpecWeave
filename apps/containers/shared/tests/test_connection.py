"""connection（SDK 连接统一层）测试：全打桩，不触碰真实 daemon / wsl.exe / podman。"""
import platform as _platform
import types

import pytest
from invoke.exceptions import Exit

from jpman_common import connection as conn


IS_WINDOWS = _platform.system() == "Windows"


@pytest.fixture(autouse=True)
def _clear_caches():
    """每个用例前清空 lru_cache，避免用例间探测结果串扰。"""
    conn.wsl_distro_name.cache_clear()
    conn.machine_connection_uri.cache_clear()
    conn._wsl_user_uid.cache_clear()
    yield


# ── host_runtime_uid / socket 路径推导（C-I5 唯一事实源）─────────────────

def test_uid_explicit_env_wins(monkeypatch):
    monkeypatch.setenv("PODMAN_RUNTIME_UID", "4242")
    assert conn.host_runtime_uid() == "4242"
    assert conn.podman_sock_path() == "/run/user/4242/podman/podman.sock"
    assert conn.host_runtime_dir() == "/run/user/4242"


@pytest.mark.skipif(not IS_WINDOWS, reason="Windows 默认回落 1000 仅在 Windows 宿主验证")
def test_uid_windows_default_1000(monkeypatch):
    monkeypatch.delenv("PODMAN_RUNTIME_UID", raising=False)
    assert conn.host_runtime_uid() == "1000"


def test_uid_linux_xdg_then_getuid(monkeypatch):
    monkeypatch.delenv("PODMAN_RUNTIME_UID", raising=False)
    monkeypatch.setattr(conn.platform, "system", lambda: "Linux")
    monkeypatch.setenv("XDG_RUNTIME_DIR", "/run/user/1006")
    assert conn.host_runtime_uid() == "1006"
    monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)
    monkeypatch.setattr(conn.os, "getuid", lambda: 1007, raising=False)
    assert conn.host_runtime_uid() == "1007"


def test_bsock_guidance_mentions_uid_override(monkeypatch):
    monkeypatch.setenv("PODMAN_RUNTIME_UID", "1006")
    msg = conn.bsock_missing_guidance()
    assert "C-I5" in msg
    assert "/run/user/1006/podman/podman.sock" in msg
    assert "PODMAN_RUNTIME_UID" in msg


def test_bsock_guidance_appends_detail():
    msg = conn.bsock_missing_guidance("unit masked")
    assert "自动启动失败详情：unit masked" in msg


# ── sdk_strategy_from_env ────────────────────────────────────────────────

def test_strategy_whitelist_falls_back_auto(monkeypatch):
    monkeypatch.setenv(conn.SDK_STRATEGY_ENV, "bogus")
    assert conn.sdk_strategy_from_env() == "auto"
    monkeypatch.setenv(conn.SDK_STRATEGY_ENV, "wsl")
    assert conn.sdk_strategy_from_env() == "wsl"


# ── sdk_base_url_candidates ──────────────────────────────────────────────

def test_candidates_legacy_only_ignores_env(monkeypatch):
    monkeypatch.setenv("CONTAINER_HOST", "tcp://1.2.3.4:1")
    cands = conn.sdk_base_url_candidates("legacy")
    assert [c.source for c in cands] == ["legacy"]
    assert cands[0].base_url is None


@pytest.mark.skipif(not IS_WINDOWS, reason="WSL/Machine 分支仅在宿主 Windows 进入")
def test_candidates_windows_auto_order_with_env(monkeypatch):
    monkeypatch.delenv("WSL_DISTRO_NAME", raising=False)
    monkeypatch.setenv("CONTAINER_HOST", "tcp://127.0.0.1:9999")
    monkeypatch.setattr(conn, "wsl_distro_name", lambda: None)
    monkeypatch.setattr(conn, "machine_connection_uri", lambda: None)
    sources = [c.source for c in conn.sdk_base_url_candidates("auto")]
    assert sources == ["P0-env", "P2-machine"]
    # 非 legacy 且已有候选时不追加 legacy
    assert "legacy" not in sources


@pytest.mark.skipif(not IS_WINDOWS, reason="WSL9P 候选仅 Windows 生成")
def test_candidates_wsl_9p_url_uses_probed_uid(monkeypatch):
    monkeypatch.setenv("CONTAINER_HOST", "")
    monkeypatch.delenv("CONTAINER_HOST", raising=False)
    monkeypatch.setattr(conn, "wsl_distro_name", lambda: "Ubuntu")
    monkeypatch.setattr(conn, "_wsl_user_uid", lambda distro: 1007)
    monkeypatch.setattr(conn, "machine_connection_uri", lambda: None)
    cands = conn.sdk_base_url_candidates("auto")
    p1 = cands[0]
    assert p1.source == "P1-wsl-9p"
    assert p1.base_url == "unix:///mnt/wsl/Ubuntu/run/user/1007/podman/podman.sock"


@pytest.mark.skipif(not IS_WINDOWS, reason="强制 wsl 但探不到发行版的提示仅 Windows 验证")
def test_candidates_force_wsl_without_distro_hint(monkeypatch):
    monkeypatch.setattr(conn, "wsl_distro_name", lambda: None)
    cands = conn.sdk_base_url_candidates("wsl")
    assert len(cands) == 1
    assert cands[0].source == "P1-wsl-9p"
    assert cands[0].base_url is None
    assert "WSL_DISTRO_NAME" in cands[0].hint


@pytest.mark.skipif(not IS_WINDOWS, reason="UID 探测失败的占位候选仅 Windows 验证")
def test_candidates_wsl_uid_unavailable_placeholder(monkeypatch):
    monkeypatch.delenv("CONTAINER_HOST", raising=False)
    monkeypatch.setattr(conn, "wsl_distro_name", lambda: "Debian")
    monkeypatch.setattr(conn, "_wsl_user_uid", lambda distro: None)
    monkeypatch.setattr(conn, "machine_connection_uri", lambda: None)
    p1 = conn.sdk_base_url_candidates("auto")[0]
    assert p1.source == "P1-wsl-9p"
    assert p1.base_url is None
    assert "id -u" in p1.hint


def test_candidates_none_strategy_reads_env(monkeypatch):
    monkeypatch.setattr(conn.platform, "system", lambda: "Linux")
    monkeypatch.setenv(conn.SDK_STRATEGY_ENV, "legacy")
    assert conn.sdk_base_url_candidates(None)[0].source == "legacy"


def test_candidates_linux_no_machine_probe(monkeypatch):
    monkeypatch.setattr(conn.platform, "system", lambda: "Linux")
    monkeypatch.delenv("CONTAINER_HOST", raising=False)

    def _boom(*a, **k):
        raise AssertionError("Linux 不得探测 machine_connection_uri")

    monkeypatch.setattr(conn, "machine_connection_uri", _boom)
    cands = conn.sdk_base_url_candidates("auto")
    assert [c.source for c in cands] == ["P2-machine"]
    assert cands[0].base_url is None  # 走 SDK from_env/active_service


# ── wsl_distro_name / _wsl_user_uid ──────────────────────────────────────

class _FakeCP:
    def __init__(self, stdout="", returncode=0):
        self.stdout = stdout
        self.returncode = returncode


def test_wsl_distro_env_var(monkeypatch):
    monkeypatch.setenv("WSL_DISTRO_NAME", "my-distro")
    assert conn.wsl_distro_name() == "my-distro"


def test_wsl_distro_no_host_support(monkeypatch):
    monkeypatch.delenv("WSL_DISTRO_NAME", raising=False)
    monkeypatch.setattr(conn, "_has_wsl_host_support", lambda: False)
    assert conn.wsl_distro_name() is None


def test_wsl_distro_quiet_first_line(monkeypatch):
    monkeypatch.delenv("WSL_DISTRO_NAME", raising=False)
    monkeypatch.setattr(conn, "_has_wsl_host_support", lambda: True)
    monkeypatch.setattr(conn.subprocess, "run", lambda *a, **k: _FakeCP("Ubuntu-2404\r\n"))
    assert conn.wsl_distro_name() == "Ubuntu-2404"


def test_wsl_distro_subprocess_error_none(monkeypatch):
    monkeypatch.delenv("WSL_DISTRO_NAME", raising=False)
    monkeypatch.setattr(conn, "_has_wsl_host_support", lambda: True)

    def _raise(*a, **k):
        raise conn.subprocess.TimeoutExpired(cmd="wsl.exe", timeout=5)

    monkeypatch.setattr(conn.subprocess, "run", _raise)
    assert conn.wsl_distro_name() is None


def test_wsl_distro_verbose_no_running_none(monkeypatch):
    monkeypatch.delenv("WSL_DISTRO_NAME", raising=False)
    monkeypatch.setattr(conn, "_has_wsl_host_support", lambda: True)
    outputs = iter(
        [
            _FakeCP(""),
            _FakeCP("  NAME     STATE     VERSION\n  Ubuntu   Stopped   2\n"),
        ]
    )
    monkeypatch.setattr(conn.subprocess, "run", lambda *a, **k: next(outputs))
    assert conn.wsl_distro_name() is None


class _FakeMntPath:
    """替换 conn.Path：只服务 _has_wsl_host_support，避免全局 patch pathlib。"""

    def __init__(self, *_a, exists_value=True, raises=False):
        self._exists_value = exists_value
        self._raises = raises

    def exists(self):
        if self._raises:
            raise OSError("9p gone")
        return self._exists_value


def test_has_wsl_host_support_non_windows(monkeypatch):
    monkeypatch.setattr(conn.platform, "system", lambda: "Linux")
    assert conn._has_wsl_host_support() is False


def test_has_wsl_host_support_missing_exe(monkeypatch):
    monkeypatch.setattr(conn.shutil, "which", lambda name: None)
    assert conn._has_wsl_host_support() is False


def test_has_wsl_host_support_ok(monkeypatch):
    monkeypatch.setattr(conn.shutil, "which", lambda name: r"C:\Windows\System32\wsl.exe")
    monkeypatch.setattr(conn, "Path", lambda p: _FakeMntPath(exists_value=True))
    assert conn._has_wsl_host_support() is True


def test_has_wsl_host_support_oserror_false(monkeypatch):
    monkeypatch.setattr(conn.shutil, "which", lambda name: "wsl.exe")
    monkeypatch.setattr(conn, "Path", lambda p: _FakeMntPath(raises=True))
    assert conn._has_wsl_host_support() is False


def test_wsl_user_uid_empty_distro():
    assert conn._wsl_user_uid("") is None


def test_wsl_distro_verbose_running_fallback(monkeypatch):
    monkeypatch.delenv("WSL_DISTRO_NAME", raising=False)
    monkeypatch.setattr(conn, "_has_wsl_host_support", lambda: True)
    outputs = iter(
        [
            _FakeCP(""),  # --list --quiet 空
            _FakeCP("  NAME            STATE           VERSION\n  Ubuntu         Stopped         2\n  Debian         Running         2\n"),
        ]
    )
    monkeypatch.setattr(conn.subprocess, "run", lambda *a, **k: next(outputs))
    assert conn.wsl_distro_name() == "Debian"


def test_wsl_user_uid_parses(monkeypatch):
    monkeypatch.setattr(conn.subprocess, "run", lambda *a, **k: _FakeCP("1006\r\n"))
    assert conn._wsl_user_uid("Ubuntu") == 1006


def test_wsl_user_uid_garbage_none(monkeypatch):
    monkeypatch.setattr(conn.subprocess, "run", lambda *a, **k: _FakeCP("not-a-uid"))
    assert conn._wsl_user_uid("Ubuntu") is None


def test_wsl_user_uid_exception_none(monkeypatch):
    def _raise(*a, **k):
        raise OSError("wsl missing")

    monkeypatch.setattr(conn.subprocess, "run", _raise)
    assert conn._wsl_user_uid("Ubuntu") is None


# ── machine_connection_uri ───────────────────────────────────────────────

def test_machine_uri_non_windows_none(monkeypatch):
    monkeypatch.setattr(conn.platform, "system", lambda: "Linux")
    assert conn.machine_connection_uri() is None


def test_machine_uri_no_podman_cli(monkeypatch):
    monkeypatch.setattr(conn.shutil, "which", lambda name: None)
    assert conn.machine_connection_uri() is None


def test_machine_uri_picks_default(monkeypatch):
    monkeypatch.setattr(conn.shutil, "which", lambda name: r"C:\bin\podman.exe")
    payload = (
        '[{"Name":"other","URI":"ssh://x@h:1/a","Default":false},'
        '{"Name":"m","URI":"ssh://user@127.0.0.1:63851/run/user/1000/podman/podman.sock","Default":true}]'
    )
    monkeypatch.setattr(conn.subprocess, "run", lambda *a, **k: _FakeCP(payload))
    uri = conn.machine_connection_uri()
    assert uri and uri.startswith("ssh://user@127.0.0.1:63851")


def test_machine_uri_bad_json_none(monkeypatch):
    monkeypatch.setattr(conn.shutil, "which", lambda name: "podman")
    monkeypatch.setattr(conn.subprocess, "run", lambda *a, **k: _FakeCP("{not json"))
    assert conn.machine_connection_uri() is None


def test_machine_uri_rejects_unknown_scheme(monkeypatch):
    monkeypatch.setattr(conn.shutil, "which", lambda name: "podman")
    monkeypatch.setattr(
        conn.subprocess, "run",
        lambda *a, **k: _FakeCP('[{"Name":"m","URI":"npipe:////./pipe/x","Default":true}]'),
    )
    assert conn.machine_connection_uri() is None


def test_machine_uri_timeout_none(monkeypatch):
    monkeypatch.setattr(conn.shutil, "which", lambda name: "podman")

    def _raise(*a, **k):
        raise conn.subprocess.TimeoutExpired(cmd="podman", timeout=8)

    monkeypatch.setattr(conn.subprocess, "run", _raise)
    assert conn.machine_connection_uri() is None


def test_machine_uri_nonzero_rc_none(monkeypatch):
    monkeypatch.setattr(conn.shutil, "which", lambda name: "podman")
    cp = types.SimpleNamespace(returncode=125, stdout="", stderr="no machine")
    monkeypatch.setattr(conn.subprocess, "run", lambda *a, **k: cp)
    assert conn.machine_connection_uri() is None


def test_machine_uri_non_list_json_none(monkeypatch):
    monkeypatch.setattr(conn.shutil, "which", lambda name: "podman")
    monkeypatch.setattr(conn.subprocess, "run", lambda *a, **k: _FakeCP('{"connections": []}'))
    assert conn.machine_connection_uri() is None


# ── windows_diagnose_hint（C1 npipe 拒绝由 SDK 报错 + W-I2 翻译体现）──────

def test_hint_ci2_works_on_linux_too(monkeypatch):
    monkeypatch.setattr(conn.platform, "system", lambda: "Linux")
    msg = conn.windows_diagnose_hint(
        "PermissionError",
        "dial unix /run/user/1006/podman/podman.sock: connect: permission denied",
    )
    assert "C-I2" in msg


def test_hint_unmatched_empty_on_linux(monkeypatch):
    monkeypatch.setattr(conn.platform, "system", lambda: "Linux")
    assert conn.windows_diagnose_hint("ValueError", "totally unrelated") == ""


@pytest.mark.skipif(not IS_WINDOWS, reason="W-I* 提示仅在 Windows 平台守卫后返回")
@pytest.mark.parametrize(
    "etype,emsg,tag",
    [
        ("ConnectionError", "unsupported url scheme: npipe", "W-I2"),
        ("AttributeError", "module 'os' has no attribute 'getuid'", "W-I4"),
        ("FileNotFoundError", "/run/user/1000/podman/podman.sock: no such file or directory", "W-I1"),
        ("TimeoutExpired", "Waiting on /tmp/podman-forward-1.sock timed out", "W-I3"),
    ],
)
def test_hint_windows_known_pits(etype, emsg, tag):
    assert tag in conn.windows_diagnose_hint(etype, emsg)


# ── ensure_host_podman_socket（全部打桩）─────────────────────────────────

def test_ensure_socket_non_linux_passthrough():
    # 当前宿主即 Windows：直接放行
    ready, _, started = conn.ensure_host_podman_socket()
    assert ready is True and started is False


def test_ensure_socket_linux_env_marker_passthrough(monkeypatch):
    monkeypatch.setattr(conn.platform, "system", lambda: "Linux")
    monkeypatch.setenv("HOST_PODMAN_SOCK", "/run/user/1000/podman/podman.sock")
    ready, _, _ = conn.ensure_host_podman_socket()
    assert ready is True


def test_ensure_socket_linux_not_podman_passthrough(monkeypatch):
    monkeypatch.setattr(conn.platform, "system", lambda: "Linux")
    monkeypatch.delenv("HOST_PODMAN_SOCK", raising=False)

    def _raise():
        raise Exit("no runtime")

    monkeypatch.setattr(conn, "detect_runtime", _raise)
    assert conn.ensure_host_podman_socket()[0] is True


def test_ensure_socket_linux_docker_runtime_passthrough(monkeypatch):
    monkeypatch.setattr(conn.platform, "system", lambda: "Linux")
    monkeypatch.delenv("HOST_PODMAN_SOCK", raising=False)
    monkeypatch.setattr(conn, "detect_runtime", lambda: "docker")
    assert conn.ensure_host_podman_socket() == (True, "", False)


def test_ensure_socket_linux_systemctl_timeout(monkeypatch, tmp_path):
    _linux_no_socket_env(monkeypatch, tmp_path)
    monkeypatch.setattr(conn.shutil, "which", lambda name: "/usr/bin/systemctl")

    def _timeout(*a, **k):
        raise conn.subprocess.TimeoutExpired(cmd=a[0] if a else "systemctl", timeout=10)

    monkeypatch.setattr(conn.subprocess, "run", _timeout)
    ready, detail, started = conn.ensure_host_podman_socket()
    assert ready is False and started is False and "超时" in detail


def test_ensure_socket_linux_systemctl_oserror(monkeypatch, tmp_path):
    _linux_no_socket_env(monkeypatch, tmp_path)
    monkeypatch.setattr(conn.shutil, "which", lambda name: "/usr/bin/systemctl")

    def _oserror(*a, **k):
        raise OSError("exec format error")

    monkeypatch.setattr(conn.subprocess, "run", _oserror)
    ready, detail, started = conn.ensure_host_podman_socket()
    assert ready is False and started is False and "exec format error" in detail


def _linux_no_socket_env(monkeypatch, tmp_path, *, uid="1006"):
    """构造 Linux + podman + 临时 socket 路径的标准环境（默认文件不存在）。"""
    monkeypatch.setattr(conn.platform, "system", lambda: "Linux")
    monkeypatch.delenv("HOST_PODMAN_SOCK", raising=False)
    monkeypatch.setattr(conn, "detect_runtime", lambda: "podman")
    sock = tmp_path / f"run-user-{uid}.sock"
    monkeypatch.setattr(conn, "podman_sock_path", lambda: str(sock))
    return sock


def test_ensure_socket_linux_already_exists(monkeypatch, tmp_path):
    sock = _linux_no_socket_env(monkeypatch, tmp_path)
    sock.write_text("")
    assert conn.ensure_host_podman_socket() == (True, "", False)


def test_ensure_socket_linux_no_systemctl(monkeypatch, tmp_path):
    _linux_no_socket_env(monkeypatch, tmp_path)
    monkeypatch.setattr(conn.shutil, "which", lambda name: None)
    ready, detail, started = conn.ensure_host_podman_socket()
    assert ready is False and started is False and "systemctl" in detail


def test_ensure_socket_linux_started_then_appears(monkeypatch, tmp_path):
    sock = _linux_no_socket_env(monkeypatch, tmp_path)
    monkeypatch.setattr(conn.shutil, "which", lambda name: "/usr/bin/systemctl")

    def _start_unit(*a, **k):
        sock.write_text("")  # 模拟 systemctl 拉起后 socket 文件出现
        return _FakeCP("")

    monkeypatch.setattr(conn.subprocess, "run", _start_unit)
    assert conn.ensure_host_podman_socket() == (True, "", True)


def test_ensure_socket_linux_start_failed(monkeypatch, tmp_path):
    _linux_no_socket_env(monkeypatch, tmp_path)
    monkeypatch.setattr(conn.shutil, "which", lambda name: "/usr/bin/systemctl")
    monkeypatch.setattr(
        conn.subprocess, "run",
        lambda *a, **k: types.SimpleNamespace(returncode=1, stdout="", stderr="unit not found"),
    )
    ready, detail, started = conn.ensure_host_podman_socket()
    assert ready is False and "unit not found" in detail and started is False


# ── get_client（假 SDK，零网络）──────────────────────────────────────────

class _FakePodmanClient:
    def __init__(self, base_url=None, ping_result=True, ping_exc=None):
        self.base_url = base_url
        self._ping_result = ping_result
        self._ping_exc = ping_exc
        self.closed = False

    def ping(self):
        if self._ping_exc is not None:
            raise self._ping_exc
        return self._ping_result

    def close(self):
        self.closed = True


class _ExplodingClient(_FakePodmanClient):
    """close() 抛异常的客户端：验证 _close_safe 静默吞掉关闭错误。"""

    def close(self):
        self.closed = True
        raise RuntimeError("close failed")


def _fake_sdk(clients=None, from_env_client=None, from_env_exc=None, ctor_exc=None):
    """构造假 podman 模块；clients 为按序取出的显式 base_url 客户端列表。"""
    state = {"ctor": list(clients or []), "from_env_calls": 0, "ctor_calls": 0}

    class _FakeModule:
        @staticmethod
        def from_env():
            state["from_env_calls"] += 1
            if from_env_exc is not None:
                raise from_env_exc
            return from_env_client

        @staticmethod
        def PodmanClient(base_url=None):
            state["ctor_calls"] += 1
            if ctor_exc is not None:
                raise ctor_exc
            return state["ctor"].pop(0) if state["ctor"] else _FakePodmanClient(base_url)

    return _FakeModule, state


def test_get_client_sdk_unavailable_yields_none(monkeypatch):
    monkeypatch.setattr(conn, "_SDK_AVAILABLE", False)
    with conn.get_client() as client:
        assert client is None


def test_get_client_legacy_from_env_success(monkeypatch):
    monkeypatch.setattr(conn, "_SDK_AVAILABLE", True)
    monkeypatch.setenv(conn.SDK_STRATEGY_ENV, "legacy")
    fake = _FakePodmanClient()
    mod, state = _fake_sdk(from_env_client=fake)
    monkeypatch.setattr(conn, "_podman_sdk", mod)
    with conn.get_client() as client:
        assert client is fake
    assert state["from_env_calls"] == 1
    assert fake.closed is True  # 退出上下文后关闭


def test_get_client_explicit_base_url_success(monkeypatch):
    monkeypatch.setattr(conn, "_SDK_AVAILABLE", True)
    monkeypatch.setenv(conn.SDK_STRATEGY_ENV, "auto")
    monkeypatch.setenv("CONTAINER_HOST", "tcp://127.0.0.1:9999")
    monkeypatch.setattr(conn, "wsl_distro_name", lambda: None)
    monkeypatch.setattr(conn, "machine_connection_uri", lambda: None)
    mod, state = _fake_sdk()  # ctor 自建客户端并记录 base_url
    monkeypatch.setattr(conn, "_podman_sdk", mod)
    with conn.get_client() as client:
        assert client.base_url == "tcp://127.0.0.1:9999"
    assert state["ctor_calls"] == 1


def test_get_client_ping_false_treated_failure(monkeypatch):
    monkeypatch.setattr(conn, "_SDK_AVAILABLE", True)
    monkeypatch.setenv(conn.SDK_STRATEGY_ENV, "legacy")
    mod, _ = _fake_sdk(from_env_client=_FakePodmanClient(ping_result=False))
    monkeypatch.setattr(conn, "_podman_sdk", mod)
    with conn.get_client() as client:
        assert client is None


def test_get_client_all_candidates_fail_debug_log(monkeypatch, capsys):
    monkeypatch.setattr(conn, "_SDK_AVAILABLE", True)
    monkeypatch.setenv(conn.SDK_STRATEGY_ENV, "legacy")
    monkeypatch.setenv("PODMAN_CLIENT_LOG_LEVEL", "DEBUG")
    mod, _ = _fake_sdk(from_env_exc=ConnectionError("boom"))
    monkeypatch.setattr(conn, "_podman_sdk", mod)
    with conn.get_client() as client:
        assert client is None
    out = capsys.readouterr().out
    assert "降级" in out
    assert "SDK-DEBUG" in out and "boom" in out


def test_sdk_available_flag(monkeypatch):
    monkeypatch.setattr(conn, "_SDK_AVAILABLE", True)
    assert conn.sdk_available() is True
    monkeypatch.setattr(conn, "_SDK_AVAILABLE", False)
    assert conn.sdk_available() is False


def test_get_client_close_error_swallowed(monkeypatch):
    monkeypatch.setattr(conn, "_SDK_AVAILABLE", True)
    monkeypatch.setenv(conn.SDK_STRATEGY_ENV, "legacy")
    fake = _ExplodingClient()
    mod, _ = _fake_sdk(from_env_client=fake)
    monkeypatch.setattr(conn, "_podman_sdk", mod)
    with conn.get_client() as client:
        assert client is fake
    assert fake.closed is True  # close 被调用且异常被吞，未外泄


@pytest.mark.skipif(not IS_WINDOWS, reason="npipe→W-I2 提示仅 Windows 输出")
def test_get_client_debug_prints_known_pit_hint(monkeypatch, capsys):
    """失败候选的异常若命中已知坑（W-I2 npipe），DEBUG 输出含匹配提示段。"""
    monkeypatch.setattr(conn, "_SDK_AVAILABLE", True)
    monkeypatch.setenv(conn.SDK_STRATEGY_ENV, "auto")
    monkeypatch.setenv("CONTAINER_HOST", "npipe:////./pipe/docker_engine")
    monkeypatch.setattr(conn, "wsl_distro_name", lambda: None)
    monkeypatch.setattr(conn, "machine_connection_uri", lambda: None)
    mod, _ = _fake_sdk(
        ctor_exc=ConnectionError("unsupported url scheme: npipe"),
        from_env_exc=ConnectionError("unsupported url scheme: npipe"),
    )
    monkeypatch.setattr(conn, "_podman_sdk", mod)
    monkeypatch.setenv("PODMAN_CLIENT_LOG_LEVEL", "DEBUG")
    with conn.get_client() as client:
        assert client is None
    out = capsys.readouterr().out
    assert "W-I2" in out and "npipe" in out
