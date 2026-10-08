"""podman preflight 集成与单测：TR-1.1 场景全覆盖 / TR-1.2 只读哨兵 / TR-1.3 标签区分。

fake_run_wsl 按子串命中返回，构造多个发行版共用同一套 script 键。
所有场景都直接测试 CLI（cli.main），保证真实调用路径。
"""

import re

from okw import cli, podman

from conftest import make_result


# --- TR-1.2 只读哨兵：preflight 不得触发任何写入类 wsl 命令 -------------------

class TestPreflightReadonlySentinel:
    # 若 preflight 调用了以下写入类命令 -> 直接失败
    FORBIDDEN_SUBSTRINGS = (
        "apt update",
        "apt install",
        "apt-get ",
        "tee /etc/subuid",
        "tee /etc/subgid",
        "echo ",       # 禁止任何回写文件的 shell 序列（若包含 >> 或 sudo）
        " -s ",        # wsl -s 设置默认发行版
        "podman pull",
        "podman run",
        "mount",
    )

    def _all_run_calls(self, fake_run_wsl):
        return [" ".join(c) for c in fake_run_wsl.calls]

    def test_no_write_on_full_pass_scenario(self, fake_run_wsl, capsys):
        """最严格：全通过场景下，调用链中不得出现写入类命令。"""
        self._install_full_pass(fake_run_wsl)
        ret = cli.main(["podman", "preflight", "openKylin-3.0"])
        assert ret == 0
        calls_joined = "\n".join(self._all_run_calls(fake_run_wsl))
        for forb in self.FORBIDDEN_SUBSTRINGS:
            assert forb not in calls_joined, f"[TR-1.2] 检测到写入类命令：{forb}\n{calls_joined}"

    def test_no_apt_update_on_missing_index(self, fake_run_wsl):
        """UNKNOWN APT 索引场景下也不得触发 apt update（预检承诺不 update）。"""
        self._install_apt_unknown(fake_run_wsl)
        cli.main(["podman", "preflight", "openKylin-3.0"])
        calls_joined = "\n".join(self._all_run_calls(fake_run_wsl))
        assert "apt update" not in calls_joined

    # -- helper: 构造 preflight 调用环境的公共场景 script ---------------------------
    @staticmethod
    def _install_full_pass(fr):
        """11 项全 PASS：发行版存在+WSL2+openKylin+默认非root+APT完好+4包候选有版本+映射完好。"""
        fr.script["-l -v"] = make_result(stdout="""  NAME                   STATE           VERSION
* openKylin-3.0           Running         2
""")
        fr.script["cat /etc/os-release"] = make_result(stdout="ID=openkylin\nVERSION_ID=3.0\n")
        fr.script["id -un"] = make_result(stdout="openkylin\n")
        fr.script["id -u"] = make_result(stdout="1000\n")
        fr.script["dpkg --version"] = make_result(stdout="Debian dpkg 1.22.10\n")
        fr.script["apt-cache --version"] = make_result(stdout="apt 2.7.14 (amd64)\n")
        for pkg, ver in [("podman", "4.9.4"), ("uidmap", "1:4.13+20240101"),
                         ("slirp4netns", "1.3.0"), ("fuse-overlayfs", "1.15")]:
            fr.script[f"apt-cache policy {pkg}"] = make_result(
                stdout=(f"Package: {pkg}\n  Candidate: {ver}\n  Installed: (none)\n"))
        # 映射：openkylin 一条标准区间，其它用户也一条不冲突区间
        fr.script["cat /etc/subuid"] = make_result(
            stdout="root:100000:65536\nopenkylin:165536:65536\n")
        fr.script["cat /etc/subgid"] = make_result(
            stdout="root:100000:65536\nopenkylin:165536:65536\n")

    @staticmethod
    def _install_apt_unknown(fr):
        """APT 索引缺失：所有包 Candidate 行空、stderr 空 -> UNKNOWN。"""
        TestPreflightReadonlySentinel._install_os(fr)
        for pkg in podman.DIRECT_PACKAGES:
            # 没有 Candidate 行 -> UNKNOWN
            fr.script[f"apt-cache policy {pkg}"] = make_result(
                stdout=f"N: Unable to locate package {pkg}\n", stderr="")
        fr.script["cat /etc/subuid"] = make_result(ok=False, exit_code=1, stderr="No such file")
        fr.script["cat /etc/subgid"] = make_result(ok=False, exit_code=1, stderr="No such file")

    @staticmethod
    def _install_os(fr):
        fr.script["-l -v"] = make_result(stdout="""  NAME                   STATE           VERSION
* openKylin-3.0           Running         2
""")
        fr.script["cat /etc/os-release"] = make_result(stdout="ID=openkylin\nVERSION_ID=3.0\n")
        fr.script["id -un"] = make_result(stdout="openkylin\n")
        fr.script["id -u"] = make_result(stdout="1000\n")
        fr.script["dpkg --version"] = make_result(stdout="Debian dpkg 1.22.10\n")
        fr.script["apt-cache --version"] = make_result(stdout="apt 2.7.14 (amd64)\n")


# --- TR-1.1 场景全覆盖 ------------------------------------------------------------------

class TestPreflightScenarios:
    # — 发行版不存在：必须 FAIL 第一项就早返回，不触发后续调用 —
    def test_distro_not_exist(self, fake_run_wsl, capsys):
        # fake_run_wsl 默认对所有未命中键返回发行版不存在
        ret = cli.main(["podman", "preflight", "ghost-distro"])
        assert ret == 1
        out = capsys.readouterr().out
        assert "ghost-distro 未注册" in out
        assert "[FAIL   ]" in out
        # 早返回：调用列表里不该有 /etc/os-release 等后续探测
        calls = [" ".join(c) for c in fake_run_wsl.calls]
        # 仅 -l -v（get_distro 探测）；无 cat /etc/os-release 等后续
        assert any("-l -v" in c for c in calls)
        assert not any("/etc/os-release" in c for c in calls)

    # — WSL1 -> FAIL —
    def test_wsl1(self, fake_run_wsl, capsys):
        fake_run_wsl.script["-l -v"] = make_result(stdout="""  NAME        STATE     VERSION
  openKylin-3.0 Running   1
""")
        ret = cli.main(["podman", "preflight", "openKylin-3.0"])
        assert ret == 1
        captured = capsys.readouterr().out
        assert "WSL1" in captured and "要求 WSL2" in captured

    # — 非 openKylin -> FAIL —
    def test_non_openkylin(self, fake_run_wsl, capsys):
        fake_run_wsl.script["-l -v"] = make_result(stdout="""  NAME        STATE     VERSION
  Ubuntu-24.04 Running   2
""")
        fake_run_wsl.script["cat /etc/os-release"] = make_result(stdout="ID=ubuntu\nVERSION_ID=24.04\n")
        # 其余探测照样回，就看我们能识别 ID != openkylin
        fake_run_wsl.script["id -un"] = make_result(stdout="ubuntu\n")
        fake_run_wsl.script["id -u"] = make_result(stdout="1000\n")
        fake_run_wsl.script["dpkg --version"] = make_result(stdout="Debian dpkg 1.22\n")
        fake_run_wsl.script["apt-cache --version"] = make_result(stdout="apt 2.7\n")
        for pkg in podman.DIRECT_PACKAGES:
            fake_run_wsl.script[f"apt-cache policy {pkg}"] = make_result(stdout=f"Package: {pkg}\n  Candidate: 1.0\n")
        fake_run_wsl.script["cat /etc/subuid"] = make_result(stdout="ubuntu:100000:65536\n")
        fake_run_wsl.script["cat /etc/subgid"] = make_result(stdout="ubuntu:100000:65536\n")
        ret = cli.main(["podman", "preflight", "Ubuntu-24.04"])
        assert ret == 1
        captured = capsys.readouterr().out
        assert "不是 openKylin" in captured or "不是 openkylin" in captured

    # — 默认用户 root -> FAIL —
    def test_default_user_is_root(self, fake_run_wsl, capsys):
        TestPreflightReadonlySentinel._install_full_pass(fake_run_wsl)
        fake_run_wsl.script["id -un"] = make_result(stdout="root\n")
        fake_run_wsl.script["id -u"] = make_result(stdout="0\n")
        ret = cli.main(["podman", "preflight", "openKylin-3.0"])
        assert ret == 1
        out = capsys.readouterr().out
        assert "默认用户=root" in out

    # — APT/dpkg 不可用 -> FAIL（包管理器损坏的干净系统）—
    def test_no_apt_dpkg(self, fake_run_wsl, capsys):
        fake_run_wsl.script["-l -v"] = make_result(stdout="""  NAME        STATE     VERSION
  openKylin-3.0 Running 2
""")
        fake_run_wsl.script["cat /etc/os-release"] = make_result(stdout="ID=openkylin\n")
        fake_run_wsl.script["id -un"] = make_result(stdout="openkylin\n")
        fake_run_wsl.script["id -u"] = make_result(stdout="1000\n")
        fake_run_wsl.script["dpkg --version"] = make_result(ok=False, exit_code=127, stderr="dpkg: command not found\n")
        fake_run_wsl.script["apt-cache --version"] = make_result(ok=False, exit_code=127, stderr="apt-cache: command not found\n")
        for pkg in podman.DIRECT_PACKAGES:
            fake_run_wsl.script[f"apt-cache policy {pkg}"] = make_result(ok=False, exit_code=1, stderr="No apt")
        fake_run_wsl.script["cat /etc/subuid"] = make_result(ok=False, exit_code=1, stderr="No")
        fake_run_wsl.script["cat /etc/subgid"] = make_result(ok=False, exit_code=1, stderr="No")
        ret = cli.main(["podman", "preflight", "openKylin-3.0"])
        assert ret == 1
        err_out = capsys.readouterr().out + ""
        assert "apt-cache 不可用" in err_out or "dpkg 不可用" in err_out

    # — APT 索引未知（UNKNOWN）-> exit_code=2，给出中文行动建议 —
    def test_apt_index_unknown(self, fake_run_wsl, capsys):
        TestPreflightReadonlySentinel._install_apt_unknown(fake_run_wsl)
        ret = cli.main(["podman", "preflight", "openKylin-3.0"])
        assert ret == 2
        out = capsys.readouterr().out
        assert podman.APT_UNKNOWN_LABEL in out or "APT索引未知" in out
        # 行动建议出现
        assert "sudo apt update" in out

    # — APT 三分法失败：候选缺失 / 网络错误 / 哈希错误 —
    def test_apt_candidate_missing(self, fake_run_wsl, capsys):
        TestPreflightReadonlySentinel._install_os(fake_run_wsl)
        for pkg in podman.DIRECT_PACKAGES:
            # Candidate: (none) -> 候选缺失
            fake_run_wsl.script[f"apt-cache policy {pkg}"] = make_result(
                stdout=f"Package: {pkg}\n  Candidate: (none)\n")
        fake_run_wsl.script["cat /etc/subuid"] = make_result(stdout="openkylin:100000:65536\n")
        fake_run_wsl.script["cat /etc/subgid"] = make_result(stdout="openkylin:100000:65536\n")
        ret = cli.main(["podman", "preflight", "openKylin-3.0"])
        assert ret == 1
        out = capsys.readouterr().out
        assert podman.APT_PKG_MISSING_LABEL in out

    def test_apt_network_error(self, fake_run_wsl, capsys):
        TestPreflightReadonlySentinel._install_os(fake_run_wsl)
        for pkg in podman.DIRECT_PACKAGES:
            fake_run_wsl.script[f"apt-cache policy {pkg}"] = make_result(
                ok=False,
                exit_code=100,
                stdout="",
                stderr=(
                    f"Err:1 https://archive.openkylin.top {pkg}\n"
                    f"  Temporary failure resolving 'archive.openkylin.top'\n"
                ),
            )
        fake_run_wsl.script["cat /etc/subuid"] = make_result(stdout="openkylin:100000:65536\n")
        fake_run_wsl.script["cat /etc/subgid"] = make_result(stdout="openkylin:100000:65536\n")
        ret = cli.main(["podman", "preflight", "openKylin-3.0"])
        assert ret == 1
        assert podman.APT_NET_ERROR_LABEL in capsys.readouterr().out

    def test_apt_hash_mismatch(self, fake_run_wsl, capsys):
        TestPreflightReadonlySentinel._install_os(fake_run_wsl)
        for pkg in podman.DIRECT_PACKAGES:
            fake_run_wsl.script[f"apt-cache policy {pkg}"] = make_result(
                ok=False,
                exit_code=1,
                stdout="",
                stderr="E: Hash Sum mismatch\n    hashes of expected file didn't match\n",
            )
        fake_run_wsl.script["cat /etc/subuid"] = make_result(stdout="openkylin:100000:65536\n")
        fake_run_wsl.script["cat /etc/subgid"] = make_result(stdout="openkylin:100000:65536\n")
        ret = cli.main(["podman", "preflight", "openKylin-3.0"])
        assert ret == 1
        assert podman.APT_HASH_ERROR_LABEL in capsys.readouterr().out

    # — 全 PASS：exit 0，且含结论 + install 提示 —
    def test_full_pass(self, fake_run_wsl, capsys):
        TestPreflightReadonlySentinel._install_full_pass(fake_run_wsl)
        ret = cli.main(["podman", "preflight", "openKylin-3.0"])
        assert ret == 0
        out = capsys.readouterr().out
        assert "预检全部通过" in out
        assert "okw podman install" in out
        # 11 项检查全部 PASS
        pass_count = len(re.findall(r"\[PASS   \]", out))
        assert pass_count >= 10

    # — 映射冲突：FAIL 且详情给出将拒绝追加的说明 —
    def test_subuid_conflict_with_other_user(self, fake_run_wsl, capsys):
        TestPreflightReadonlySentinel._install_full_pass(fake_run_wsl)
        # 另一个用户区间覆盖 openkylin 的候选标准区间 [100000,165536) -> 冲突
        fake_run_wsl.script["cat /etc/subuid"] = make_result(
            stdout=(
                "root:100000:65536\n"
                "evil:120000:100000\n"        # overlaps with [100000,165536)
            )
        )
        fake_run_wsl.script["cat /etc/subgid"] = make_result(stdout="root:100000:65536\n")
        ret = cli.main(["podman", "preflight", "openKylin-3.0"])
        assert ret == 1
        out = capsys.readouterr().out
        assert "拒绝自动追加" in out or "存在重叠" in out


# --- TR-1.3 文案/标签：三分法标签 + 状态栏格式一致 —

class TestPreflightLabels:
    def test_label_formats_present(self, fake_run_wsl, capsys):
        """混合场景：一个包缺失 + 一个包网络错误 + 一个包 UNKNOWN -> 三种标签同时出现在输出里。"""
        TestPreflightReadonlySentinel._install_os(fake_run_wsl)
        packs = list(podman.DIRECT_PACKAGES)
        # 0: 候选缺失
        fake_run_wsl.script[f"apt-cache policy {packs[0]}"] = make_result(
            stdout=f"Package: {packs[0]}\n  Candidate: (none)\n")
        # 1: 网络错误
        fake_run_wsl.script[f"apt-cache policy {packs[1]}"] = make_result(
            ok=False, exit_code=100, stderr="Temporary failure resolving archive\n")
        # 2: APT 索引未知（无 Candidate 行且 stderr 空）
        fake_run_wsl.script[f"apt-cache policy {packs[2]}"] = make_result(
            stdout=f"N: Unable to locate package {packs[2]}\n")
        # 3: PASS
        fake_run_wsl.script[f"apt-cache policy {packs[3]}"] = make_result(
            stdout=f"Package: {packs[3]}\n  Candidate: 1.2.3\n")
        # subuid 读不到 -> UNKNOWN（干净系统）
        fake_run_wsl.script["cat /etc/subuid"] = make_result(
            ok=False, exit_code=1, stderr="No such file")
        fake_run_wsl.script["cat /etc/subgid"] = make_result(stdout="openkylin:100000:65536\n")
        cli.main(["podman", "preflight", "openKylin-3.0"])
        out = capsys.readouterr().out
        for tag in (podman.APT_PKG_MISSING_LABEL, podman.APT_NET_ERROR_LABEL,
                    podman.APT_UNKNOWN_LABEL):
            assert tag in out, f"[TR-1.3] 缺失标签：{tag}\n{out}"

    def test_status_columns_aligned(self, fake_run_wsl, capsys):
        """三种状态标签格式宽度一致，便于肉眼比较。"""
        TestPreflightReadonlySentinel._install_full_pass(fake_run_wsl)
        cli.main(["podman", "preflight", "openKylin-3.0"])
        out = capsys.readouterr().out
        # 每行都使用 7 字宽的 [STATUS]，匹配 [PASS   ] / [FAIL   ] / [UNKNOWN]
        for m in re.finditer(r"\[(PASS|FAIL|UNKNOWN) {0,4}\]", out):
            assert len(m.group(0)) == 9, f"状态栏宽度不一致：{m.group(0)!r}"


# --- CLI 层：podman 空子组 + install/verify 未实现占位返回 exit 2 —

class TestPodmanCliPlumbing:
    def test_podman_no_cmd_prints_help_and_exit_2(self, capsys):
        ret = cli.main(["podman"])
        assert ret == 2
        assert "preflight" in capsys.readouterr().out

    def test_install_is_connected_returns_fail_on_missing_distro(self, fake_run_wsl, capsys):
        """install 子命令已实现，直连 podman.cmd_install；默认 fake 环境发行版不存在 → FAIL exit 1。"""
        ret = cli.main(["podman", "install", "openKylin-3.0", "--yes"])
        assert ret == 1
        out = capsys.readouterr().out
        # 不再是"尚未实现"占位，确实调用了真实 install 流程（输出报告头）
        assert "okw podman install" in out

    def test_verify_is_connected_returns_fail_on_missing_distro(self, fake_run_wsl, capsys):
        """verify 子命令已实现，直连 podman.cmd_verify；默认 fake 环境发行版不存在 → FAIL exit 1。"""
        ret = cli.main(["podman", "verify", "openKylin-3.0"])
        assert ret == 1
        out = capsys.readouterr().out
        # 不再是"尚未实现"占位，确实调用了真实 verify 流程（输出报告头）
        assert "okw podman verify" in out
        assert "尚未实现" not in out

    # — preflight 通过 podman.cmd_preflight 返回，直测 report.exit_code 语义 —
    def test_report_exit_code_semantics(self):
        r_pass = podman.PreflightReport(distro_name="x")
        r_pass.add("a", "PASS")
        assert r_pass.exit_code() == 0

        r_unknown_only = podman.PreflightReport(distro_name="x")
        r_unknown_only.add("a", "UNKNOWN")
        assert r_unknown_only.exit_code() == 2

        r_fail_plus = podman.PreflightReport(distro_name="x")
        r_fail_plus.add("a", "FAIL")
        r_fail_plus.add("b", "UNKNOWN")
        assert r_fail_plus.exit_code() == 1
