"""desktop 子组：领域判定 + CLI 编排（假 wsl 输出注入，不触真实 WSL）。"""

import pytest

from okw import cli, desktop

from conftest import make_result

PROBE_OK = "\n".join([
    "okw_xrdp_bin=yes",
    "okw_xrdp_active=active",
    "okw_sesman_active=active",
    "okw_port_listen=1",
    "okw_user=openkylin",
    "okw_uid=1000",
    "okw_xsession=ok",
]) + "\n"

PROBE_BLACK_SCREEN = PROBE_OK.replace("okw_xsession=ok", "okw_xsession=missing")

DESKTOP = "openKylin-3.0-desktop"


def _prime_ok(fake_run_wsl, probe: str = PROBE_OK):
    fake_run_wsl.script["-l -v"] = make_result(stdout=f"* {DESKTOP} Running 2\n")
    fake_run_wsl.script["os-release"] = make_result(stdout='ID=openkylin\nVERSION="3.0"\n')
    fake_run_wsl.script["wsl.conf"] = make_result(stdout="[boot]\nsystemd=true\n\n[user]\ndefault=openkylin\n")
    fake_run_wsl.script["okw_xrdp_bin"] = make_result(stdout=probe)


# ----------------- 领域单元 -----------------

def test_parse_runtime_probe_extracts_labeled_lines():
    parsed = desktop.parse_runtime_probe(PROBE_OK + "noise\n")
    assert parsed["xrdp_bin"] == "yes"
    assert parsed["port_listen"] == "1"
    assert parsed["xsession"] == "ok"


def test_watchdog_script_contains_markers_and_session_handoff():
    assert "XDG_RUNTIME_DIR" in desktop.XSESSION_WATCHDOG
    assert "kwin_x11" in desktop.XSESSION_WATCHDOG
    assert "exec ukui-session" in desktop.XSESSION_WATCHDOG


def test_patch_script_backs_up_and_marks_unchanged():
    script = desktop._xsession_patch_script()
    assert ".xsession.bak-" in script
    assert "OKW_XSESSION_EOF" in script
    assert "unchanged" in script


def test_default_port_is_documented_3390():
    assert desktop.DEFAULT_PORT == 3390


def test_generated_scripts_avoid_nested_quotes_in_substitution():
    # Windows wsl.exe 桥接会把 $() 内的双引号转义吞掉（2026-10-13 实测）；
    # 探针与补齐脚本均须避免在命令替换内嵌双引号。
    for script in (desktop._RUNTIME_PROBE, desktop._xsession_patch_script()):
        assert '"$HOME' not in script
        assert '$(test -f "' not in script


# ----------------- CLI：preflight -----------------

class TestDesktopPreflight:
    def test_preflight_pass(self, fake_run_wsl, capsys):
        _prime_ok(fake_run_wsl)
        assert cli.main(["desktop", "preflight", DESKTOP]) == 0
        assert "已就绪" in capsys.readouterr().out

    def test_preflight_black_screen_fail(self, fake_run_wsl, capsys):
        _prime_ok(fake_run_wsl, probe=PROBE_BLACK_SCREEN)
        assert cli.main(["desktop", "preflight", DESKTOP]) == 1
        out = capsys.readouterr().out
        assert "首登黑屏看门狗" in out and "FAIL" in out

    def test_preflight_missing_distro(self, fake_run_wsl, capsys):
        fake_run_wsl.script["-l -v"] = make_result(stdout="  NAME STATE VERSION\n")
        assert cli.main(["desktop", "preflight", "ghost"]) == 1
        assert "未注册" in capsys.readouterr().out

    def test_group_without_subcommand_returns_2(self, capsys):
        assert cli.main(["desktop"]) == 2
        assert "okw desktop" in capsys.readouterr().out


# ----------------- CLI：install -----------------

class TestDesktopInstall:
    def test_install_without_yes_zero_write(self, fake_run_wsl, capsys):
        assert cli.main(["desktop", "install", DESKTOP]) == 2
        out = capsys.readouterr().out
        assert "未提供 --yes" in out
        assert fake_run_wsl.calls == []  # 零写入、零探测

    def test_install_missing_xrdp(self, fake_run_wsl, capsys):
        _prime_ok(fake_run_wsl, probe=PROBE_OK.replace("okw_xrdp_bin=yes", "okw_xrdp_bin=no"))
        assert cli.main(["desktop", "install", DESKTOP, "--yes"]) == 1
        assert "xrdp" in capsys.readouterr().out

    def test_install_happy_path(self, fake_run_wsl, capsys):
        _prime_ok(fake_run_wsl)
        fake_run_wsl.script["systemctl enable --now"] = make_result()
        fake_run_wsl.script["OKW_XSESSION_EOF"] = make_result(stdout="patched\n")
        assert cli.main(["desktop", "install", DESKTOP, "--yes"]) == 0
        out = capsys.readouterr().out
        assert "已补齐" in out
        # 确实执行了 root 启用与 .xsession 补齐
        joined = [" ".join(c) for c in fake_run_wsl.calls]
        assert any("systemctl enable --now" in j for j in joined)
        assert any("OKW_XSESSION_EOF" in j for j in joined)

    def test_install_idempotent_watchdog(self, fake_run_wsl, capsys):
        _prime_ok(fake_run_wsl)
        fake_run_wsl.script["systemctl enable --now"] = make_result()
        fake_run_wsl.script["OKW_XSESSION_EOF"] = make_result(stdout="unchanged\n")
        assert cli.main(["desktop", "install", DESKTOP, "--yes"]) == 0
        assert "保持不变" in capsys.readouterr().out

    def test_install_systemd_disabled_stops(self, fake_run_wsl, capsys):
        fake_run_wsl.script["-l -v"] = make_result(stdout=f"* {DESKTOP} Running 2\n")
        fake_run_wsl.script["os-release"] = make_result(stdout='ID=openkylin\nVERSION="3.0"\n')
        fake_run_wsl.script["wsl.conf"] = make_result(stdout="[user]\ndefault=openkylin\n")
        assert cli.main(["desktop", "install", DESKTOP, "--yes"]) == 1
        assert "systemd" in capsys.readouterr().out


# ----------------- CLI：verify -----------------

class TestDesktopVerify:
    def test_verify_pass(self, fake_run_wsl, monkeypatch, capsys):
        _prime_ok(fake_run_wsl)
        monkeypatch.setattr(desktop, "probe_windows_port", lambda port, timeout=2.0: True)
        assert cli.main(["desktop", "verify", DESKTOP]) == 0
        assert "验收通过" in capsys.readouterr().out

    def test_verify_windows_port_unreachable(self, fake_run_wsl, monkeypatch, capsys):
        _prime_ok(fake_run_wsl)
        monkeypatch.setattr(desktop, "probe_windows_port", lambda port, timeout=2.0: False)
        assert cli.main(["desktop", "verify", DESKTOP]) == 1
        assert "不可达" in capsys.readouterr().out

    def test_verify_custom_port_reflected(self, fake_run_wsl, monkeypatch, capsys):
        _prime_ok(fake_run_wsl)
        seen = {}
        monkeypatch.setattr(
            desktop, "probe_windows_port",
            lambda port, timeout=2.0: seen.setdefault("port", port) or True,
        )
        assert cli.main(["desktop", "verify", DESKTOP, "--port", "3389"]) == 0
        assert seen["port"] == 3389
        assert "localhost:3389" in capsys.readouterr().out


# ----------------- 分支覆盖：结构/运行时/端口/IP 幂等 -----------------

PROBE_ALL_BAD = "\n".join([
    "okw_xrdp_bin=no",
    "okw_xrdp_active=inactive",
    "okw_sesman_active=unknown",
    "okw_port_listen=0",
    "okw_user=root",
    "okw_uid=0",
    "okw_xsession=missing",
]) + "\n"


class TestDesktopBranches:
    def test_structural_wsl_unavailable(self, fake_run_wsl, capsys):
        fake_run_wsl.script["-l -v"] = make_result(False, 1, "", "wsl boom", "failed")
        assert cli.main(["desktop", "preflight", DESKTOP]) == 1
        assert "未注册" in capsys.readouterr().out

    def test_structural_distro_absent(self, fake_run_wsl, capsys):
        fake_run_wsl.script["-l -v"] = make_result(stdout="  NAME STATE VERSION\n* other Running 2\n")
        assert cli.main(["desktop", "preflight", DESKTOP]) == 1
        assert "未注册" in capsys.readouterr().out

    def test_structural_wsl1(self, fake_run_wsl, capsys):
        fake_run_wsl.script["-l -v"] = make_result(stdout=f"* {DESKTOP} Running 1\n")
        assert cli.main(["desktop", "preflight", DESKTOP]) == 1
        assert "WSL2" in capsys.readouterr().out

    def test_structural_os_release_unreadable(self, fake_run_wsl, capsys):
        _prime_ok(fake_run_wsl)
        fake_run_wsl.script["os-release"] = make_result(False, 1, "", "cat boom", "failed")
        assert cli.main(["desktop", "preflight", DESKTOP]) == 1
        assert "os-release" in capsys.readouterr().out

    def test_structural_not_openkylin(self, fake_run_wsl, capsys):
        _prime_ok(fake_run_wsl)
        fake_run_wsl.script["os-release"] = make_result(stdout='ID=debian\nVERSION="12"\n')
        assert cli.main(["desktop", "preflight", DESKTOP]) == 1
        assert "不是 openkylin" in capsys.readouterr().out

    def test_structural_wsl_conf_unreadable(self, fake_run_wsl, capsys):
        _prime_ok(fake_run_wsl)
        fake_run_wsl.script["wsl.conf"] = make_result(False, 1, "", "cat boom", "failed")
        assert cli.main(["desktop", "preflight", DESKTOP]) == 1
        assert "wsl.conf 读取失败" in capsys.readouterr().out

    def test_runtime_probe_no_output(self, fake_run_wsl, capsys):
        _prime_ok(fake_run_wsl, probe="")
        assert cli.main(["desktop", "preflight", DESKTOP]) == 1
        assert "探针无输出" in capsys.readouterr().out

    def test_runtime_all_bad_marks_every_fail(self, fake_run_wsl, capsys):
        _prime_ok(fake_run_wsl, probe=PROBE_ALL_BAD)
        rc = cli.main(["desktop", "preflight", DESKTOP])
        assert rc == 1
        out = capsys.readouterr().out
        for label in ("xrdp 已安装", "xrdp 服务", "xrdp-sesman 服务", "端口 3390 监听", "默认用户 / UID", "首登黑屏看门狗"):
            assert label in out
        assert "未找到 xrdp" in out
        assert "无法判定" in out

    def test_install_enable_failure(self, fake_run_wsl, capsys):
        _prime_ok(fake_run_wsl)
        fake_run_wsl.script["systemctl enable --now"] = make_result(False, 1, "", "enable boom", "failed")
        assert cli.main(["desktop", "install", DESKTOP, "--yes"]) == 1
        assert "systemctl 失败" in capsys.readouterr().out

    def test_install_patch_failure(self, fake_run_wsl, capsys):
        _prime_ok(fake_run_wsl)
        fake_run_wsl.script["systemctl enable --now"] = make_result()
        fake_run_wsl.script["OKW_XSESSION_EOF"] = make_result(False, 1, "", "write boom", "failed")
        assert cli.main(["desktop", "install", DESKTOP, "--yes"]) == 1
        assert "写入失败" in capsys.readouterr().out

    def test_verify_stops_on_structural_fail(self, fake_run_wsl, capsys):
        fake_run_wsl.script["-l -v"] = make_result(stdout="  NAME STATE VERSION\n* other Running 2\n")
        assert cli.main(["desktop", "verify", DESKTOP]) == 1
        out = capsys.readouterr().out
        assert "未注册" in out
        assert "Windows 侧" not in out  # 结构失败即返回，不进入运行时/端口探测

    def test_fail_evidence_both_branches(self):
        from okw.distro import CmdResult

        assert "无输出" in desktop._fail_evidence(CmdResult(False, 1, "", "", "failed"))
        assert "boom" in desktop._fail_evidence(CmdResult(False, 1, "", "boom", "failed"))

    def test_probe_windows_port_closed(self):
        import socket

        sock = socket.socket()
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
        sock.close()
        assert desktop.probe_windows_port(port, timeout=0.3) is False

    def test_probe_windows_port_open(self):
        import socket

        server = socket.socket()
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        port = server.getsockname()[1]
        try:
            assert desktop.probe_windows_port(port, timeout=1.0) is True
        finally:
            server.close()
