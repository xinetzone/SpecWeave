"""CLI 集成测试：直接调用 main(argv)，不依赖已安装入口。"""

import gzip
from pathlib import Path

import pytest

from okw import cli
from okw import __version__

from conftest import make_result

class TestVersionAndHelp:
    def test_version(self, capsys):
        with pytest.raises(SystemExit) as exc:
            cli.main(["--version"])
        assert exc.value.code == 0
        assert f"okw {__version__}" in capsys.readouterr().out

    def test_no_command_prints_help(self, capsys):
        assert cli.main([]) == 2
        assert "usage:" in capsys.readouterr().out.lower()

    def test_unknown_command(self, capsys):
        with pytest.raises(SystemExit) as exc:
            cli.main(["frobnicate"])
        assert exc.value.code == 2

    @pytest.mark.parametrize("argv", [
        ["list"], ["status", "x"], ["import", "img", "--name", "n", "--location", "l"],
        ["export", "x", "--output", "o"], ["unregister", "x"],
        ["verify", "x"],
        ["scaffold", "deb"], ["scaffold", "dput"], ["ref"],
    ])
    def test_subcommand_help(self, argv):
        # argparse 的 -h 触发 SystemExit(0)
        with pytest.raises(SystemExit) as exc:
            cli.main([*argv, "--help"])
        assert exc.value.code == 0

    def test_exec_help(self):
        # exec 用 REMAINDER，--help 会被吞进命令；仅无参数时触发帮助
        with pytest.raises(SystemExit) as exc:
            cli.main(["exec", "--help"])
        assert exc.value.code == 0

class TestListCmd:
    def test_list_ok(self, fake_run_wsl, capsys):
        fake_run_wsl.script["-l -v"] = make_result(stdout="""  NAME                   STATE           VERSION
* openKylin-3.0           Running         2
  Ubuntu-22.04            Stopped         2
""")
        fake_run_wsl.script["--quiet"] = make_result(stdout="openKylin-3.0\n")
        assert cli.main(["list"]) == 0
        out = capsys.readouterr().out
        assert "openKylin-3.0" in out and "*" in out and "默认发行版" in out

    def test_list_error(self, fake_run_wsl, capsys):
        assert cli.main(["list"]) == 1
        assert "错误" in capsys.readouterr().err

class TestStatusCmd:
    def test_status_found(self, fake_run_wsl, capsys):
        fake_run_wsl.script["-l -v"] = make_result(stdout="""  NAME                   STATE           VERSION
* openKylin-3.0           Running         2
""")
        assert cli.main(["status", "openKylin-3.0"]) == 0
        out = capsys.readouterr().out
        assert "WSL2" in out and "（默认）" in out

    def test_status_missing(self, fake_run_wsl, capsys):
        assert cli.main(["status", "ghost"]) == 1
        assert "不存在" in capsys.readouterr().err

class TestImportCmd:
    def _gzip(self, tmp_path) -> Path:
        p = tmp_path / "ok.wsl"
        with gzip.open(p, "wb") as fh:
            fh.write(b"tar")
        return p

    def test_import_ok(self, tmp_path, fake_run_wsl, capsys):
        img = self._gzip(tmp_path)
        fake_run_wsl.script["--import"] = make_result()
        assert cli.main(["import", str(img), "--name", "openKylin-3.0",
                         "--location", str(tmp_path / "loc"), "--version", "2"]) == 0
        assert "导入成功" in capsys.readouterr().out

    def test_import_bad_magic(self, tmp_path, capsys):
        bad = tmp_path / "bad.wsl"
        bad.write_bytes(b"not gzip")
        assert cli.main(["import", str(bad), "--name", "n",
                         "--location", str(tmp_path)]) == 1
        assert "gzip" in capsys.readouterr().err

    def test_import_failure_tips(self, tmp_path, fake_run_wsl, capsys):
        img = self._gzip(tmp_path)
        fake_run_wsl.script["--import"] = make_result(False, 4294967295, "", "E_ABORT", "failed")
        assert cli.main(["import", str(img), "--name", "n",
                         "--location", str(tmp_path)]) != 0
        err = capsys.readouterr().err
        assert "排障三问" in err and "wsl --shutdown" in err

class TestUnregisterCmd:
    def test_without_yes_rejected(self, fake_run_wsl, capsys):
        assert cli.main(["unregister", "openKylin-3.0"]) == 2
        assert "破坏性" in capsys.readouterr().err

    def test_with_yes(self, fake_run_wsl, capsys):
        fake_run_wsl.script["--unregister"] = make_result()
        assert cli.main(["unregister", "openKylin-3.0", "--yes"]) == 0
        assert "已注销" in capsys.readouterr().out

class TestExecCmd:
    def test_exec_ok(self, fake_run_wsl, capsys):
        fake_run_wsl.script["-l -v"] = make_result(stdout="* openKylin-3.0 Running 2\n")
        fake_run_wsl.script["-d openKylin-3.0"] = make_result(stdout="hello\n")
        assert cli.main(["exec", "openKylin-3.0", "--", "echo", "hello"]) == 0
        out = capsys.readouterr().out
        assert "hello" in out
        # 参数透传：cmd 中不含 "--" 分隔符
        exec_call = next(c for c in fake_run_wsl.calls if "-d" in c and "openKylin-3.0" in c)
        assert exec_call[-2:] == ["echo", "hello"]

    def test_exec_empty(self, capsys):
        assert cli.main(["exec", "x", "--"]) == 2

class TestVerifyCmd:
    def test_verify_pass(self, fake_run_wsl, capsys):
        fake_run_wsl.script["-l -v"] = make_result(stdout="* openKylin-3.0 Running 2\n")
        fake_run_wsl.script["--quiet"] = make_result(stdout="openKylin-3.0\n")
        fake_run_wsl.script["cat /etc/os-release"] = make_result(stdout='ID=openkylin\nVERSION="3.0"\n')
        fake_run_wsl.script['echo "user=$(whoami) uid=$(id -u)"'] = make_result(stdout="user=openkylin uid=1000\n")
        fake_run_wsl.script["cat /etc/wsl.conf"] = make_result(stdout="[boot]\nsystemd=true\n\n[user]\ndefault=openkylin\n")
        fake_run_wsl.script["dpkg-query -W | wc -l"] = make_result(stdout="405\n")
        assert cli.main(["verify", "openKylin-3.0"]) == 0
        assert "全部通过" in capsys.readouterr().out

    def test_verify_fail_exit_1(self, fake_run_wsl, capsys):
        fake_run_wsl.script["-l -v"] = make_result(stdout="* openKylin-3.0 Running 2\n")
        fake_run_wsl.script["cat /etc/os-release"] = make_result(stdout="ID=debian\nVERSION=\"12\"\n")
        fake_run_wsl.script['echo "user=$(whoami) uid=$(id -u)"'] = make_result(stdout="user=openkylin uid=1000\n")
        fake_run_wsl.script["cat /etc/wsl.conf"] = make_result(stdout="[boot]\nsystemd=true\n\n[user]\ndefault=openkylin\n")
        fake_run_wsl.script["dpkg-query -W | wc -l"] = make_result(stdout="405\n")
        assert cli.main(["verify", "openKylin-3.0"]) == 1
        assert "1 项未通过" in capsys.readouterr().out

class TestScaffoldCmd:
    def test_deb_ok(self, tmp_path, capsys):
        assert cli.main(["scaffold", "deb", "--project", "demo", "--series", "huanghe",
                         "--version", "0.1.0", "--output-dir", str(tmp_path)]) == 0
        out = capsys.readouterr().out
        assert "已生成 debian/ 打包骨架" in out
        assert (tmp_path / "debian" / "changelog").exists()

    def test_deb_bad_series(self, tmp_path, capsys):
        assert cli.main(["scaffold", "deb", "--project", "demo", "--series", "foo",
                         "--version", "0.1.0", "--output-dir", str(tmp_path)]) == 1
        assert "未知系列代号" in capsys.readouterr().err

    def test_dput_ok(self, capsys):
        assert cli.main(["scaffold", "dput", "--openkylin-id", "myid"]) == 0
        out = capsys.readouterr().out
        assert "[okbs]" in out and "upload.build.openkylin.top:2121" in out

    def test_dput_write(self, tmp_path, capsys):
        out = tmp_path / "dput.cf"
        assert cli.main(["scaffold", "dput", "--openkylin-id", "myid", "--output", str(out)]) == 0
        assert out.exists() and "已写入" in capsys.readouterr().out

class TestRefCmd:
    def test_list_topics(self, capsys):
        assert cli.main(["ref"]) == 0
        out = capsys.readouterr().out
        for name in ("series", "wsl-troubleshoot", "okbs", "verify"):
            assert name in out

    def test_topic(self, capsys):
        assert cli.main(["ref", "series"]) == 0
        assert "huanghe" in capsys.readouterr().out

    def test_unknown(self, capsys):
        assert cli.main(["ref", "nope"]) == 2
        assert "未知主题" in capsys.readouterr().err
