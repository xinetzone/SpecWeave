"""distro 模块测试：wsl 封装、列表解析、import/export/unregister/exec。"""

import gzip
import os
import subprocess
from pathlib import Path

import pytest

from okw import distro
from okw.distro import CmdResult, Distro, WslError

from conftest import make_proc, make_result

TABLE_OUTPUT = """  NAME                   STATE           VERSION
* openKylin-3.0           Running         2
  Ubuntu-22.04            Stopped         2
  kali-linux              Stopped         1
"""

LEGACY_OUTPUT = """Windows Subsystem for Linux Distributions:
openKylin-3.0 (默认)
  Running: 0
Ubuntu-22.04
  Stopped: 1
"""

class TestWslExe:
    def test_path_lookup(self, monkeypatch, tmp_path):
        fake = tmp_path / "wsl.exe"
        fake.write_bytes(b"x")
        monkeypatch.setattr(distro.shutil, "which", lambda name: str(fake))
        assert distro.wsl_exe() == str(fake)

    def test_windir_fallback(self, monkeypatch, tmp_path):
        fake = tmp_path / "System32" / "wsl.exe"
        fake.parent.mkdir(parents=True)
        fake.write_bytes(b"x")
        monkeypatch.setattr(distro.shutil, "which", lambda name: None)
        monkeypatch.setenv("WINDIR", str(tmp_path))
        assert distro.wsl_exe() == str(fake)

    def test_not_found(self, monkeypatch, tmp_path):
        monkeypatch.setattr(distro.shutil, "which", lambda name: None)
        monkeypatch.setenv("WINDIR", str(tmp_path))
        with pytest.raises(WslError):
            distro.wsl_exe()

class TestRunWsl:
    def test_ok_injects_utf8(self, fake_run):
        fake_run.script.append((lambda cmd: True, make_proc(stdout="hello")))
        res = distro.run_wsl(["-l", "-v"])
        assert res.ok and res.stdout == "hello" and res.kind == "ok"
        cmd = fake_run.calls[0]
        assert cmd[0].endswith("wsl.exe") or "wsl" in cmd[0]

    def test_distro_missing_classified(self, fake_run):
        fake_run.script.append(
            (lambda cmd: True, make_proc(1, "", "There is no distribution with the supplied name"))
        )
        res = distro.run_wsl(["-d", "nope", "--", "echo", "x"])
        assert not res.ok and res.kind == "distro_missing"

    def test_generic_failure(self, fake_run):
        fake_run.script.append((lambda cmd: True, make_proc(3, "", "boom")))
        res = distro.run_wsl(["x"])
        assert not res.ok and res.kind == "failed" and res.exit_code == 3

    def test_command_missing(self, monkeypatch):
        def _boom(cmd, env, timeout):
            raise FileNotFoundError(cmd[0])

        monkeypatch.setattr(distro, "_run_subprocess", _boom)
        res = distro.run_wsl(["x"])
        assert not res.ok and res.kind == "command_missing"

    def test_timeout(self, monkeypatch):
        def _boom(cmd, env, timeout):
            raise subprocess.TimeoutExpired(cmd[0], timeout)

        monkeypatch.setattr(distro, "_run_subprocess", _boom)
        res = distro.run_wsl(["x"])
        assert not res.ok and res.kind == "timeout"

class TestParseList:
    def test_table_form(self):
        ds = distro.parse_list_output(TABLE_OUTPUT)
        assert [d.name for d in ds] == ["openKylin-3.0", "Ubuntu-22.04", "kali-linux"]
        assert ds[0].is_default and ds[0].version == "2" and ds[0].state == "Running"
        assert not ds[1].is_default and ds[1].version == "2" and ds[1].state == "Stopped"
        assert ds[2].version == "1"

    def test_legacy_form(self):
        ds = distro.parse_list_output(LEGACY_OUTPUT)
        assert [d.name for d in ds] == ["openKylin-3.0", "Ubuntu-22.04"]

    def test_empty(self):
        assert distro.parse_list_output("") == []

    def test_drift_fails_fast(self):
        with pytest.raises(WslError):
            distro.parse_list_output("this is not a wsl output at all\nrandom lines\n")

    def test_table_without_rows_fails(self):
        with pytest.raises(WslError):
            distro.parse_list_output("  NAME  STATE  VERSION\n")

class TestImport:
    def _gzip_image(self, tmp_path) -> Path:
        p = tmp_path / "openKylin-3.0.wsl"
        with gzip.open(p, "wb") as fh:
            fh.write(b"fake tar content")
        return p

    def test_ok_constructs_command(self, tmp_path, fake_run):
        image = self._gzip_image(tmp_path)
        fake_run.script.append((lambda cmd: "--import" in cmd, make_proc()))
        res = distro.import_distro(str(image), "openKylin-3.0", r"D:\wsl\ok30", "2")
        assert res.ok
        cmd = fake_run.calls[0]
        assert "--import" in cmd and "openKylin-3.0" in cmd and "--version" in cmd and "2" in cmd

    def test_rejects_non_gzip(self, tmp_path):
        p = tmp_path / "bad.wsl"
        p.write_bytes(b"PK\x03\x04 not gzip")
        with pytest.raises(WslError):
            distro.import_distro(str(p), "n", "l", "2")

    def test_missing_image(self, tmp_path):
        with pytest.raises(WslError):
            distro.import_distro(str(tmp_path / "none.wsl"), "n", "l", "2")

class TestLifecycle:
    def test_unregister_requires_yes(self, fake_run):
        res = distro.unregister_distro("openKylin-3.0", yes=False)
        assert not res.ok
        assert fake_run.calls == []  # 未触发任何 wsl 调用

    def test_unregister_with_yes(self, fake_run):
        fake_run.script.append((lambda cmd: "--unregister" in cmd, make_proc()))
        res = distro.unregister_distro("openKylin-3.0", yes=True)
        assert res.ok and "--unregister" in fake_run.calls[0]

    def test_export_constructs(self, fake_run):
        fake_run.script.append((lambda cmd: "--export" in cmd, make_proc()))
        res = distro.export_distro("openKylin-3.0", r"D:\out\ok30.tar")
        assert res.ok
        cmd = fake_run.calls[0]
        assert "--export" in cmd and r"D:\out\ok30.tar" in cmd

    def test_exec_passthrough(self, fake_run):
        fake_run.script.append(
            (lambda cmd: "-l" in cmd and "-v" in cmd, make_proc(stdout=TABLE_OUTPUT))
        )
        fake_run.script.append(
            (lambda cmd: "-d" in cmd and "openKylin-3.0" in cmd, make_proc(stdout="ok"))
        )
        res = distro.exec_distro("openKylin-3.0", ["cat", "/etc/os-release"])
        assert res.ok
        assert fake_run.calls[-1][-2:] == ["cat", "/etc/os-release"]

    def test_exec_with_user_injects_wsl_u(self, fake_run):
        fake_run.script.append(
            (lambda cmd: "-l" in cmd and "-v" in cmd, make_proc(stdout=TABLE_OUTPUT))
        )
        fake_run.script.append(
            (lambda cmd: "-u root" in " ".join(cmd) and "-d openKylin-3.0" in " ".join(cmd),
             make_proc(stdout="root-ok"))
        )
        res = distro.exec_distro("openKylin-3.0", ["id"], user="root")
        assert res.ok and res.stdout == "root-ok"
        last = fake_run.calls[-1]
        assert "-u" in last and "root" in last
        u_idx = last.index("-u")
        assert last[u_idx + 1] == "root"
        # 顺序：-d <name> [-u <user>] -- <cmd>
        d_idx = last.index("-d")
        sep_idx = last.index("--")
        assert d_idx < u_idx < sep_idx < last.index("id")

    def test_exec_with_user_none_matches_legacy(self, fake_run):
        # user=None（默认）时 args 里不含 -u，保证向下兼容
        fake_run.script.append(
            (lambda cmd: "-l" in cmd and "-v" in cmd, make_proc(stdout=TABLE_OUTPUT))
        )
        fake_run.script.append(
            (lambda cmd: "-d openKylin-3.0" in " ".join(cmd), make_proc(stdout="ok"))
        )
        distro.exec_distro("openKylin-3.0", ["id"], user=None)
        last = fake_run.calls[-1]
        assert "-u" not in last

    def test_exec_unknown_distro(self, fake_run):
        # 列表可读但目标不在列 → distro_missing，不抛异常
        fake_run.script.append(
            (lambda cmd: "-l" in cmd and "-v" in cmd, make_proc(stdout=TABLE_OUTPUT))
        )
        res = distro.exec_distro("ghost", ["echo", "x"])
        assert not res.ok and res.kind == "distro_missing"

class TestDefault:
    def test_default_quiet_first_line(self, fake_run):
        fake_run.script.append(
            (lambda cmd: "--quiet" in cmd, make_proc(stdout="openKylin-3.0\nUbuntu-22.04\n"))
        )
        assert distro.default_distro_name() == "openKylin-3.0"

    def test_get_distro(self, fake_run):
        fake_run.script.append((lambda cmd: "-l" in cmd, make_proc(stdout=TABLE_OUTPUT)))
        assert distro.get_distro("openKylin-3.0").version == "2"
        assert distro.get_distro("ghost") is None
