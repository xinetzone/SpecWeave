"""verify 模块测试：五步验收各场景（mock WSL 输出，不触真实发行版）。"""

from okw import distro, verify

from conftest import make_result

OS_RELEASE_OK = """ID=openkylin
VERSION="3.0"
VERSION_CODENAME=huanghe
"""

WSL_CONF_OK = """[boot]
systemd=true

[user]
default=openkylin
"""

def _seed_ok(script, table=True):
    if table:
        script["-l -v"] = make_result(stdout="""  NAME                   STATE           VERSION
* openKylin-3.0           Running         2
""")
    script["cat /etc/os-release"] = make_result(stdout=OS_RELEASE_OK)
    script["echo \"user=$(whoami) uid=$(id -u)\""] = make_result(stdout="user=openkylin uid=1000\n")
    script["cat /etc/wsl.conf"] = make_result(stdout=WSL_CONF_OK)
    script["dpkg-query -W | wc -l"] = make_result(stdout="405\n")

class TestVerify:
    def test_all_pass(self, fake_run_wsl):
        _seed_ok(fake_run_wsl.script)
        report = verify.verify("openKylin-3.0")
        assert report.all_passed
        assert len(report.checks) == 5
        labels = [c.label for c in report.checks]
        assert "发行版在列且 WSL2" in labels
        assert "/etc/os-release 版本与 ID" in labels
        assert "默认用户 / UID" in labels
        assert "wsl.conf 的 systemd 与默认用户" in labels
        assert "软件包计数" in labels

    def test_missing_systemd_does_not_stop(self, fake_run_wsl):
        _seed_ok(fake_run_wsl.script)
        fake_run_wsl.script["cat /etc/wsl.conf"] = make_result(stdout="[boot]\nsystemd=false\n")
        report = verify.verify("openKylin-3.0")
        assert not report.all_passed
        assert len(report.checks) == 5  # 单项失败不中断
        wsl_conf = next(c for c in report.checks if c.key == "wsl.conf")
        assert not wsl_conf.passed

    def test_user_uid_mismatch(self, fake_run_wsl):
        _seed_ok(fake_run_wsl.script)
        fake_run_wsl.script['echo "user=$(whoami) uid=$(id -u)"'] = make_result(stdout="user=root uid=0\n")
        report = verify.verify("openKylin-3.0")
        user_check = next(c for c in report.checks if c.key == "user")
        assert not user_check.passed
        assert user_check.actual == "user=root uid=0"

    def test_bad_package_count(self, fake_run_wsl):
        _seed_ok(fake_run_wsl.script)
        fake_run_wsl.script["dpkg-query -W | wc -l"] = make_result(stdout="not-a-number\n")
        report = verify.verify("openKylin-3.0")
        pkg = next(c for c in report.checks if c.key == "packages")
        assert not pkg.passed

    def test_distro_missing(self, fake_run_wsl):
        # 列表可读但目标不在列 → 仅 1 项 FAIL（发行版不存在），不抛异常
        fake_run_wsl.script["-l -v"] = make_result(stdout="""  NAME                   STATE           VERSION
* Ubuntu-22.04            Stopped         2
""")
        report = verify.verify("ghost")
        assert not report.all_passed
        assert len(report.checks) == 1
        assert report.checks[0].key == "listed"

    def test_default_star_protected(self, fake_run_wsl, monkeypatch):
        _seed_ok(fake_run_wsl.script)
        monkeypatch.setattr(distro, "default_distro_name", lambda: "Ubuntu-22.04")
        report = verify.verify("openKylin-3.0", default_before="openKylin-3.0")
        listed = report.checks[0]
        assert not listed.passed
        assert "默认已变" in listed.actual

    def test_format_report(self, fake_run_wsl):
        _seed_ok(fake_run_wsl.script)
        report = verify.verify("openKylin-3.0")
        text = verify.format_report(report)
        assert "PASS" in text and "全部通过" in text
        assert "openKylin WSL 环境验收：openKylin-3.0" in text

    def test_exec_failure_reports_evidence(self, fake_run_wsl):
        # 实测故障：stderr 为空时原实现拼出"读取失败: "空串，零证据；
        # 修复后必须带 exit/kind 与"无输出"占位，且附探活指引
        _seed_ok(fake_run_wsl.script)
        fake_run_wsl.script["cat /etc/os-release"] = make_result(
            ok=False, exit_code=1, stdout="", stderr="", kind="failed")
        report = verify.verify("openKylin-3.0")
        osr = next(c for c in report.checks if c.key == "os-release")
        assert not osr.passed
        assert "exit=1" in osr.actual and "kind=failed" in osr.actual
        assert "无输出" in osr.actual
        assert "探活" in osr.note

    def test_exec_failure_prefers_stderr_then_stdout(self, fake_run_wsl):
        _seed_ok(fake_run_wsl.script)
        fake_run_wsl.script["dpkg-query -W | wc -l"] = make_result(
            ok=False, exit_code=-1, stdout="boot failed", stderr="", kind="failed")
        report = verify.verify("openKylin-3.0")
        pkg = next(c for c in report.checks if c.key == "packages")
        assert "exit=-1" in pkg.actual and "boot failed" in pkg.actual

    def test_wsl_conf_read_failure_not_reported_as_config_absent(self, fake_run_wsl):
        # 读取失败≠配置缺失：原实现把读失败解析成"systemd 未启用 / default=缺失"假结论
        _seed_ok(fake_run_wsl.script)
        fake_run_wsl.script["cat /etc/wsl.conf"] = make_result(
            ok=False, exit_code=1, stdout="", stderr="", kind="failed")
        report = verify.verify("openKylin-3.0")
        conf = next(c for c in report.checks if c.key == "wsl.conf")
        assert not conf.passed
        assert "读取失败" in conf.actual
        assert "未启用" not in conf.actual and "缺失" not in conf.actual
        assert "exit=1" in conf.actual

    def test_wsl_conf_empty_file_reports_config_absent(self, fake_run_wsl):
        # 对照：读成功但文件无配置 → 仍如实报缺失（读失败分支不掩盖真缺失）
        _seed_ok(fake_run_wsl.script)
        fake_run_wsl.script["cat /etc/wsl.conf"] = make_result(stdout="")
        report = verify.verify("openKylin-3.0")
        conf = next(c for c in report.checks if c.key == "wsl.conf")
        assert not conf.passed
        assert "未启用" in conf.actual and "缺失" in conf.actual
