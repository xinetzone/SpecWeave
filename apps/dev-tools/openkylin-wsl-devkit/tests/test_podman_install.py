"""Task 2 install 集成与单测：TR-2.1/2.2/2.3/2.4。

fake_run_wsl 按子串命中返回 CmdResult；map_snapshot fixture 仅验证纯函数不触 WSL。
"""

import re
import subprocess
import sys

import pytest

from okw import cli, podman

from conftest import make_result


# ----------------- TR-2.1 写入类命令必须在 --yes 之后 / 候选缺失不触发安装 --------

class TestTR21WriteSentinel:
    """TR-2.1：--yes 缺失 / 候选缺失场景下，调用链不出现写入类命令。"""

    WRITE_FORBIDDEN = (
        "apt update",
        "apt install",
        "tee /etc/subuid",
        "tee /etc/subgid",
        "python3 -c",              # 映射写入实现用的 python3 -c 原子脚本
        "mkstemp",                 # 若出现在 args 里也应禁止
        "chmod",
        "chown",
        "mv ",
        " -s ",                    # wsl -s 设置默认发行版
        "sed ",
        "echo ",
    )

    def _calls_joined(self, fake_run_wsl):
        return "\n".join(" ".join(c) for c in fake_run_wsl.calls)

    # — 缺 --yes：不触发任何写入，退出 2，打印副作用清单 4 条 —
    def test_missing_yes_no_writes(self, fake_run_wsl, capsys):
        # 不配置任何 script → 会触发 distro not exist，但 missing_yes 是第一层早返回
        ret = cli.main(["podman", "install", "openKylin-3.0"])
        assert ret == 2
        out = capsys.readouterr().out
        for line in podman.YES_SIDEEFFECTS_LINES:
            assert line.strip() in out
        calls = self._calls_joined(fake_run_wsl)
        for forb in self.WRITE_FORBIDDEN:
            assert forb not in calls

    # — 候选缺失：有 --yes，但 apt update 后 Candidate: (none) → 不触发 install 写入 —
    def test_candidate_missing_aborts_before_install(self, fake_run_wsl, capsys):
        TestInstallHelpers._install_env_base(fake_run_wsl)
        fake_run_wsl.script["apt update"] = make_result(stdout="Hit:1 archive ... Done\n")
        # 只有一个包 candidate (none) 就足够早返回
        fake_run_wsl.script["apt-cache policy podman"] = make_result(
            stdout="Package: podman\n  Candidate: (none)\n")
        fake_run_wsl.script["apt-cache policy uidmap"] = make_result(
            stdout="Package: uidmap\n  Candidate: 1:4.13\n")
        fake_run_wsl.script["apt-cache policy slirp4netns"] = make_result(
            stdout="Package: slirp4netns\n  Candidate: 1.3\n")
        fake_run_wsl.script["apt-cache policy fuse-overlayfs"] = make_result(
            stdout="Package: fuse-overlayfs\n  Candidate: 1.15\n")
        ret = cli.main(["podman", "install", "openKylin-3.0", "--yes"])
        assert ret == 1
        out = capsys.readouterr().out
        assert podman.APT_PKG_MISSING_LABEL in out
        calls = self._calls_joined(fake_run_wsl)
        # 不出现 apt install / 映射写入
        assert "apt install" not in calls
        assert "tee /etc/subuid" not in calls


# ----------------- TR-2.2 安装只针对目标发行版 + 不改软件源/默认版 -----------------

class TestTR22ScopeAndNoSideEffect:
    """TR-2.2：只改目标发行版；apt update 在 --yes 后；无软件源/wsl.conf/默认发行版修改。"""

    GLOBAL_FORBIDDEN = (
        "add-apt-repository",
        "tee /etc/apt/sources",
        "tee /etc/wsl.conf",
        " -s ",        # wsl -s 设置默认发行版
        "wslconfig",
    )

    def test_no_global_modifications_on_full_pass(self, fake_run_wsl):
        TestInstallHelpers._install_full_pass(fake_run_wsl)
        cli.main(["podman", "install", "openKylin-3.0", "--yes"])
        calls = "\n".join(" ".join(c) for c in fake_run_wsl.calls)
        for forb in self.GLOBAL_FORBIDDEN:
            assert forb not in calls, f"[TR-2.2] 出现全局性写入：{forb}\n{calls}"
        # apt update 必须在 --yes 分支（install_run 内）；这里只验证它确实被调用（有--yes）
        assert "apt update" in calls

    def test_apt_update_uses_root(self, fake_run_wsl):
        """install 流程中 apt update / apt install 必须以 root 身份执行（-u root 注入）。"""
        TestInstallHelpers._install_full_pass(fake_run_wsl)
        cli.main(["podman", "install", "openKylin-3.0", "--yes"])
        # fake_run_wsl 的 args 里包含 -u root（-d name 后面紧跟 -u）
        all_args = list(fake_run_wsl.calls)
        # 至少有一次 apt update 调用的 args 序列里存在 -u 和 "root"
        apt_updates = [a for a in all_args if "apt" in a and "update" in a]
        assert len(apt_updates) >= 1
        for args in apt_updates:
            joined = " ".join(args)
            assert "-u" in joined and "root" in joined, f"apt update 未使用 root：{joined}"


class TestInstallPreflightGate:
    """安装必须在任何 APT 写入前拦截发行版结构性前置条件失败。"""

    @pytest.mark.parametrize("failure", ["wsl1", "not-openkylin", "missing-apt"])
    def test_structural_preflight_failure_stops_before_apt_update(
        self, fake_run_wsl, failure
    ):
        TestInstallHelpers._install_env_base(fake_run_wsl)
        if failure == "wsl1":
            fake_run_wsl.script["-l -v"] = make_result(
                stdout="""  NAME                   STATE           VERSION
* openKylin-3.0           Running         1
"""
            )
        elif failure == "not-openkylin":
            fake_run_wsl.script["cat /etc/os-release"] = make_result(
                stdout="ID=debian\nVERSION_ID=12\n"
            )
        else:
            fake_run_wsl.script["apt-cache --version"] = make_result(
                ok=False, exit_code=127, stderr="apt-cache not found"
            )

        ret = cli.main(["podman", "install", "openKylin-3.0", "--yes"])

        assert ret != 0
        assert "apt update" not in "\n".join(
            " ".join(call) for call in fake_run_wsl.calls
        )

    def test_unknown_candidate_stops_before_install_or_mapping_write(
        self, fake_run_wsl
    ):
        TestInstallHelpers._install_env_base(fake_run_wsl)
        fake_run_wsl.script["apt update"] = make_result(stdout="Hit:1 archive ...\n")
        fake_run_wsl.script["apt-cache policy podman"] = make_result(
            stdout="Package: podman\n"
        )
        for package in podman.DIRECT_PACKAGES[1:]:
            fake_run_wsl.script[f"apt-cache policy {package}"] = make_result(
                stdout=f"Package: {package}\n  Candidate: 1.0\n"
            )

        ret = cli.main(["podman", "install", "openKylin-3.0", "--yes"])

        calls = "\n".join(" ".join(call) for call in fake_run_wsl.calls)
        assert ret != 0
        assert "apt install" not in calls
        assert "python3 -c" not in calls

    def test_failed_policy_command_stops_even_with_candidate_in_stdout(
        self, fake_run_wsl, capsys
    ):
        TestInstallHelpers._install_env_base(fake_run_wsl)
        fake_run_wsl.script["apt update"] = make_result(stdout="Hit:1 archive ...\n")
        fake_run_wsl.script["apt-cache policy podman"] = make_result(
            ok=False,
            exit_code=100,
            stdout="Package: podman\n  Candidate: 4.9.4\n",
            stderr="apt-cache returned an error after writing output",
        )

        ret = cli.main(["podman", "install", "openKylin-3.0", "--yes"])

        update_index = next(
            index
            for index, call in enumerate(fake_run_wsl.calls)
            if "apt update" in " ".join(call)
        )
        post_update_calls = "\n".join(
            " ".join(call) for call in fake_run_wsl.calls[update_index + 1 :]
        )
        assert ret != 0
        assert "apt-cache policy 命令失败" in capsys.readouterr().out
        assert "apt install" not in post_update_calls
        assert "apt-cache policy uidmap" not in post_update_calls
        assert "python3 -c" not in post_update_calls




class TestTR23MappingPaths:
    """TR-2.3：8 类纯函数路径覆盖 parse/判定/追加构造；写入失败类路径见 CLI 场景。"""

    @pytest.mark.parametrize(
        "text",
        [
            "broken:row\n",
            "openkylin:not-a-number:65536\n",
            "openkylin:100000:0\n",
            "open kylin:100000:65536\n",
        ],
    )
    def test_malformed_mapping_fails_closed(self, text):
        with pytest.raises(ValueError, match="映射"):
            podman.parse_subordinate_file(text)

    def test_preflight_reports_malformed_mapping_without_crashing(
        self, fake_run_wsl
    ):
        TestInstallHelpers._install_env_base(fake_run_wsl)
        fake_run_wsl.script["cat /etc/subuid"] = make_result(
            stdout="openkylin:bad:65536\n"
        )
        fake_run_wsl.script["cat /etc/subgid"] = make_result(stdout="")

        report = podman.preflight_check("openKylin-3.0")

        subuid = next(item for item in report.items if item.name == "subuid 映射")
        assert subuid.status == "FAIL"
        assert "格式" in subuid.detail

    def test_mapping_writer_appends_both_files_once_and_preserves_existing_bytes(
        self, tmp_path
    ):
        uid_path = tmp_path / "subuid"
        gid_path = tmp_path / "subgid"
        uid_original = b"# uid existing\r\nroot:165536:65536\r\n"
        gid_original = b"# gid existing\r\nroot:165536:65536\r\n"
        uid_path.write_bytes(uid_original)
        gid_path.write_bytes(gid_original)

        def run_writer():
            return subprocess.run(
                [
                    sys.executable,
                    "-c",
                    podman._mapping_writer_script(),
                    str(uid_path),
                    str(gid_path),
                    "openkylin",
                    "100000",
                    "65536",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

        first = run_writer()
        uid_expected = uid_original + b"openkylin:100000:65536\n"
        gid_expected = gid_original + b"openkylin:100000:65536\n"
        assert first.returncode == 0
        assert first.stdout.strip() == "APPENDED"
        assert uid_path.read_bytes() == uid_expected
        assert gid_path.read_bytes() == gid_expected

        second = run_writer()
        assert second.returncode == 0
        assert second.stdout.strip() == "ALREADY"
        assert uid_path.read_bytes() == uid_expected
        assert gid_path.read_bytes() == gid_expected

    @pytest.mark.parametrize(
        "uid_original,gid_original",
        [
            (b"invalid-row\n", b""),
            (b"root:100000:65536\n", b""),
            (b"openkylin:100000:1\n", b""),
            (b"openkylin:200000:1000\n", b""),
            (b"openkylin:200000:65536\nother:220000:1000\n", b""),
            (b"", b"other:100000:65536\n"),
        ],
    )
    def test_mapping_writer_rejects_invalid_or_conflicting_files_unchanged(
        self, tmp_path, uid_original, gid_original
    ):
        uid_path = tmp_path / "subuid"
        gid_path = tmp_path / "subgid"
        uid_path.write_bytes(uid_original)
        gid_path.write_bytes(gid_original)
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                podman._mapping_writer_script(),
                str(uid_path),
                str(gid_path),
                "openkylin",
                "100000",
                "65536",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode != 0
        assert uid_path.read_bytes() == uid_original
        assert gid_path.read_bytes() == gid_original

    def test_mapping_writer_rejects_invalid_utf8_without_changes(self, tmp_path):
        uid_path = tmp_path / "subuid"
        gid_path = tmp_path / "subgid"
        uid_original = b"\xff\xfe"
        gid_original = b"# gid\n"
        uid_path.write_bytes(uid_original)
        gid_path.write_bytes(gid_original)

        result = subprocess.run(
            [
                sys.executable,
                "-c",
                podman._mapping_writer_script(),
                str(uid_path),
                str(gid_path),
                "openkylin",
                "100000",
                "65536",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode != 0
        assert "UTF-8" in result.stderr
        assert uid_path.read_bytes() == uid_original
        assert gid_path.read_bytes() == gid_original

    def test_mapping_writer_rolls_back_partial_second_file_write(self, tmp_path):
        uid_path = tmp_path / "subuid"
        gid_path = tmp_path / "subgid"
        uid_original = b"# uid\n"
        gid_original = b"# gid\n"
        uid_path.write_bytes(uid_original)
        gid_path.write_bytes(gid_original)
        runner = """
import builtins
import os
import sys

script, *args = sys.argv[1:]
gid_path = os.path.abspath(args[1])
sys.argv = ["mapping-writer", *args]
real_open = builtins.open

class PartialWriteFailure:
    def __init__(self, stream):
        self.stream = stream
        self.failed = False

    def write(self, data):
        if not self.failed:
            self.failed = True
            self.stream.write(data[:3])
            self.stream.flush()
            raise OSError("injected partial write failure")
        return self.stream.write(data)

    def __getattr__(self, name):
        return getattr(self.stream, name)

def injected_open(path, mode="r", *open_args, **open_kwargs):
    stream = real_open(path, mode, *open_args, **open_kwargs)
    if os.path.abspath(os.fspath(path)) == gid_path and mode == "a+b":
        return PartialWriteFailure(stream)
    return stream

builtins.open = injected_open
exec(compile(script, "<mapping-writer>", "exec"), {"__name__": "__main__"})
"""

        result = subprocess.run(
            [
                sys.executable,
                "-c",
                runner,
                podman._mapping_writer_script(),
                str(uid_path),
                str(gid_path),
                "openkylin",
                "100000",
                "65536",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode != 0
        assert "MAPPING_WRITE_FAILED" in result.stderr
        assert "原文件已恢复" in result.stderr
        assert uid_path.read_bytes() == uid_original
        assert gid_path.read_bytes() == gid_original

    def test_mapping_writer_restores_files_when_flush_fails(self, tmp_path):
        uid_path = tmp_path / "subuid"
        gid_path = tmp_path / "subgid"
        uid_original = b"# uid\n"
        gid_original = b"# gid\n"
        uid_path.write_bytes(uid_original)
        gid_path.write_bytes(gid_original)
        runner = """
import builtins
import os
import sys

script, *args = sys.argv[1:]
gid_path = os.path.abspath(args[1])
sys.argv = ["mapping-writer", *args]
real_open = builtins.open

class FlushFailure:
    def __init__(self, stream):
        self.stream = stream

    def flush(self):
        raise OSError("injected flush failure")

    def __getattr__(self, name):
        return getattr(self.stream, name)

def injected_open(path, mode="r", *open_args, **open_kwargs):
    stream = real_open(path, mode, *open_args, **open_kwargs)
    if os.path.abspath(os.fspath(path)) == gid_path and mode == "a+b":
        return FlushFailure(stream)
    return stream

builtins.open = injected_open
exec(compile(script, "<mapping-writer>", "exec"), {"__name__": "__main__"})
"""

        result = subprocess.run(
            [
                sys.executable,
                "-c",
                runner,
                podman._mapping_writer_script(),
                str(uid_path),
                str(gid_path),
                "openkylin",
                "100000",
                "65536",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode != 0
        assert "MAPPING_WRITE_FAILED" in result.stderr
        assert uid_path.read_bytes() == uid_original
        assert gid_path.read_bytes() == gid_original

    def test_mapping_writer_close_failure_is_not_reported_as_success(
        self, tmp_path
    ):
        uid_path = tmp_path / "subuid"
        gid_path = tmp_path / "subgid"
        uid_original = b"# uid\n"
        gid_original = b"# gid\n"
        uid_path.write_bytes(uid_original)
        gid_path.write_bytes(gid_original)
        runner = """
import builtins
import os
import sys

script, *args = sys.argv[1:]
gid_path = os.path.abspath(args[1])
sys.argv = ["mapping-writer", *args]
real_open = builtins.open

class CloseFailure:
    def __init__(self, stream):
        self.stream = stream

    def close(self):
        self.stream.close()
        raise OSError("injected close failure")

    def __getattr__(self, name):
        return getattr(self.stream, name)

def injected_open(path, mode="r", *open_args, **open_kwargs):
    stream = real_open(path, mode, *open_args, **open_kwargs)
    if os.path.abspath(os.fspath(path)) == gid_path and mode == "a+b":
        return CloseFailure(stream)
    return stream

builtins.open = injected_open
exec(compile(script, "<mapping-writer>", "exec"), {"__name__": "__main__"})
"""

        result = subprocess.run(
            [
                sys.executable,
                "-c",
                runner,
                podman._mapping_writer_script(),
                str(uid_path),
                str(gid_path),
                "openkylin",
                "100000",
                "65536",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode != 0
        assert "MAPPING_WRITE_FAILED" in result.stderr
        assert uid_path.read_bytes() == uid_original
        assert gid_path.read_bytes() == gid_original

    def _entries(self, text):
        return podman.parse_subordinate_file(text)

    # 1. 已存在有效映射 → 无需追加
    def test_valid_mapping_skips_append(self):
        entries = self._entries("openkylin:100000:65536\nroot:165536:65536\n")
        assert podman.has_valid_mapping_for(entries, "openkylin") is True

    # 2. 缺映射 + 标准区间空闲 → 追加后应该正好一行
    def test_missing_plus_free_std_constructs_new_line(self):
        entries = self._entries("root:165536:65536\n")
        assert podman.has_valid_mapping_for(entries, "openkylin") is False
        # 其他映射与标准区间 [100000,165536) 无重叠
        std = podman.SubordinateMapEntry("__std__", podman.STANDARD_SUBUID_START, podman.STANDARD_SUBUID_COUNT)
        others = [e for e in entries if e.name != "openkylin"]
        assert all(not podman.ranges_overlap(e, std) for e in others)

    # 3. 连续执行两遍幂等：追加后再跑一遍 → 不会重复追加
    def test_idempotent_two_runs_no_dup(self):
        first_text = "openkylin:100000:65536\n"
        # 追加后不会再重复（因为 has_valid_mapping_for 已是 True）
        first_entries = self._entries(first_text)
        assert podman.has_valid_mapping_for(first_entries, "openkylin") is True
        # 同样的文本再加一遍不会出现第二行，说明幂等逻辑触发
        second_entries = self._entries(first_text)
        assert sum(1 for e in second_entries if e.name == "openkylin") == 1

    # 4. off-by-one：A.end == B.start 不重叠
    def test_off_by_one_touching_not_overlap(self):
        a = podman.SubordinateMapEntry("a", 100000, 65536)  # ends 165536
        b = podman.SubordinateMapEntry("b", 165536, 65536)  # starts 165536
        assert podman.ranges_overlap(a, b) is False
        # 且 b 不与标准区间 [100000,165536) 重叠（即 std_end=165536 不算）
        std = podman.SubordinateMapEntry("std", 100000, 65536)
        assert podman.ranges_overlap(b, std) is False

    # 5. 同名多行区间冲突 → has_valid_mapping_for 返回 False
    def test_same_user_two_overlapping_entries_invalid(self):
        entries = self._entries("openkylin:100000:65536\nopenkylin:150000:65536\n")
        assert podman.has_valid_mapping_for(entries, "openkylin") is False

    # 6. start/count 非正整数 → 无效条目被 parse_subordinate_file 丢弃
    def test_non_positive_start_or_count_rejects_file(self):
        with pytest.raises(ValueError, match="映射"):
            self._entries(
                "openkylin:0:65536\n"
                "openkylin:100000:-1\n"
                "openkylin:100000:0\n"
                "openkylin:100000:65536\n"
            )

    # 7. 畸形三列（字段数≠3 / name含空格）→ 拒绝整个映射文件
    def test_malformed_rows_reject_file(self):
        with pytest.raises(ValueError, match="映射"):
            self._entries(
                "only:two\n"
                "a:b:c:d\n"
                "open kylin:100000:65536\n"
                "openkylin:abc:65536\n"
                "root:165536:65536\n"
            )

    # 8. 只读文件 / 权限失败 → CLI 场景下实际写入 FAIL，保留原文件（调用失败后无第二次写）
    def test_write_permission_fail_via_cli_call(self, fake_run_wsl, capsys):
        TestInstallHelpers._install_env_base(fake_run_wsl)
        TestInstallHelpers._install_apt_pass(fake_run_wsl)
        # subuid 已存在（可解析为 0 行，即空），但 python3 -c 原子写入失败
        fake_run_wsl.script["cat /etc/subuid"] = make_result(stdout="")
        fake_run_wsl.script["cat /etc/subgid"] = make_result(stdout="")
        fake_run_wsl.script["python3 -c"] = make_result(ok=False, exit_code=1,
            stderr="PermissionError: [Errno 13] Permission denied\n")
        # podman --version 正常（模拟包安装完成）
        fake_run_wsl.script["podman --version"] = make_result(stdout="podman version 4.9.4\n")
        fake_run_wsl.script["podman info --format"] = make_result(stdout="true\n")
        ret = cli.main(["podman", "install", "openKylin-3.0", "--yes"])
        # subuid 写入失败应该 FAIL 退出 1 （因为 python3 执行失败）
        assert ret == 1
        capsys.readouterr()  # 排空输出，避免污染后续 capsys 断言
        # 注意：写入调用使用的是 python3 -c，实际 args 里包含 python3 与 -c 两项，它们是分开的
        all_args = [" ".join(c) for c in fake_run_wsl.calls]
        # 至多一次 python3 -c（只尝试一次 subuid 写入，失败即早返回；不尝试 subgid）
        python3_c_count = sum(1 for line in all_args if "python3" in line and "-c" in line)
        assert python3_c_count <= 1, f"权限失败后仍发起多次写入：{python3_c_count}\n{chr(10).join(all_args)}"


# ----------------- TR-2.4 APT 三分法标签互不相同（场景 CLI）--------------------

class TestTR24ThreeAPTErrorLabels:
    """TR-2.4：三类 APT 失败标签互不相同，文案中文且指向正确修复方向。"""

    def test_pkg_missing_label_and_hint(self, fake_run_wsl, capsys):
        TestInstallHelpers._install_env_base(fake_run_wsl)
        fake_run_wsl.script["apt update"] = make_result(stdout="Hit:1 archive ... Done\n")
        for p in podman.DIRECT_PACKAGES:
            fake_run_wsl.script[f"apt-cache policy {p}"] = make_result(
                stdout=f"Package: {p}\n  Candidate: (none)\n")
        ret = cli.main(["podman", "install", "openKylin-3.0", "--yes"])
        assert ret == 1
        out = capsys.readouterr().out
        assert podman.APT_PKG_MISSING_LABEL in out
        # 不出现另外两种标签（PKG_MISSING 早返回，NET/HASH 还没触发）
        assert podman.APT_NET_ERROR_LABEL not in out or "候选复查" in out

    @pytest.mark.parametrize(
        "stderr",
        [
            "Temporary failure resolving 'archive.openkylin.top'",
            "Could not connect to archive.openkylin.top: Connection timed out",
        ],
    )
    def test_network_error_label(self, fake_run_wsl, capsys, stderr):
        TestInstallHelpers._install_env_base(fake_run_wsl)
        fake_run_wsl.script["apt update"] = make_result(
            ok=False, exit_code=100, stderr=stderr
        )
        ret = cli.main(["podman", "install", "openKylin-3.0", "--yes"])
        assert ret == 1
        out = capsys.readouterr().out
        assert podman.APT_NET_ERROR_LABEL in out

    def test_hash_error_label_on_install(self, fake_run_wsl, capsys):
        TestInstallHelpers._install_env_base(fake_run_wsl)
        TestInstallHelpers._install_apt_pass(fake_run_wsl)
        # apt install 阶段哈希错误
        fake_run_wsl.script["apt install -y --no-install-recommends"] = make_result(
            ok=False, exit_code=1,
            stderr="E: Failed to fetch x.deb  Hash Sum mismatch\n    hashes of expected file didn't match\n")
        # 映射/验收（即使 install 失败也不再触发，这里仅以防万一）
        fake_run_wsl.script["cat /etc/subuid"] = make_result(stdout="")
        fake_run_wsl.script["cat /etc/subgid"] = make_result(stdout="")
        ret = cli.main(["podman", "install", "openKylin-3.0", "--yes"])
        assert ret == 1
        out = capsys.readouterr().out
        assert podman.APT_HASH_ERROR_LABEL in out

    def test_labels_all_distinct(self):
        labels = (podman.APT_PKG_MISSING_LABEL, podman.APT_NET_ERROR_LABEL, podman.APT_HASH_ERROR_LABEL)
        assert len(set(labels)) == 3, f"三分法标签重复：{labels}"


# ----------------- CLI Plumbing（--yes 副作用三行 / InstallReport exit 语义）--

class TestInstallPlumbing:
    """cmd_install 的退出码语义 + 全 PASS 场景 + verify 未实现占位回归。"""

    def test_missing_yes_prints_three_plus_lines_and_exit_2(self, capsys):
        """--yes 拒绝输出必须清晰包含每条副作用，便于肉眼扫描。"""
        ret = cli.main(["podman", "install", "ghost"])
        assert ret == 2
        out = capsys.readouterr().out
        # 副作用清单 4 条都出现 + 末尾给出重跑提示
        for line in podman.YES_SIDEEFFECTS_LINES:
            assert line.strip() in out
        assert "重跑" in out or "--yes" in out

    def test_report_exit_code_semantics(self):
        r_missing_yes = podman.InstallReport(distro_name="x", missing_yes=True)
        assert r_missing_yes.exit_code() == 2
        r_pass = podman.InstallReport(distro_name="x")
        r_pass.add("a", "PASS")
        assert r_pass.exit_code() == 0
        r_fail = podman.InstallReport(distro_name="x")
        r_fail.add("a", "FAIL")
        assert r_fail.exit_code() == 1
        r_unknown_only = podman.InstallReport(distro_name="x")
        r_unknown_only.add("a", "UNKNOWN")
        assert r_unknown_only.exit_code() == 2

    def test_full_install_success(self, fake_run_wsl, capsys):
        """全通过场景：结论写‘安装成功’，exit 0。"""
        TestInstallHelpers._install_full_pass(fake_run_wsl)
        ret = cli.main(["podman", "install", "openKylin-3.0", "--yes"])
        assert ret == 0
        out = capsys.readouterr().out
        assert "安装成功" in out
        # 状态栏格式与 preflight 一致（[STATUS  ] 宽 9）
        for m in re.finditer(r"\[(PASS|FAIL|UNKNOWN) {0,4}\]", out):
            assert len(m.group(0)) == 9, f"状态栏宽度不一致：{m.group(0)!r}"

    def test_unconfirmed_mapping_write_is_not_reported_as_pass(
        self, fake_run_wsl, capsys
    ):
        """写命令成功但映射状态无法确认时，安装不能宣称成功。"""
        TestInstallHelpers._install_full_pass(fake_run_wsl)
        fake_run_wsl.script["python3 -c"] = make_result(stdout="")

        ret = cli.main(["podman", "install", "openKylin-3.0", "--yes"])

        assert ret != 0
        out = capsys.readouterr().out
        assert "安装成功" not in out
        assert "[FAIL" in out


# ----------------- helper ------------------------------------------------

class TestInstallHelpers:
    """构造 fake_run_wsl 环境 script 的静态方法集合，测试按需复用。"""

    @staticmethod
    def _install_env_base(fr):
        """openKylin WSL2 + 默认用户非 root + apt/dpkg 可用骨架。"""
        fr.script["-l -v"] = make_result(stdout="""  NAME                   STATE           VERSION
* openKylin-3.0           Running         2
""")
        fr.script["cat /etc/os-release"] = make_result(stdout="ID=openkylin\nVERSION_ID=3.0\n")
        fr.script["id -un"] = make_result(stdout="openkylin\n")
        fr.script["id -u"] = make_result(stdout="1000\n")
        fr.script["dpkg --version"] = make_result(stdout="Debian dpkg 1.22.10\n")
        fr.script["apt-cache --version"] = make_result(stdout="apt 2.7.14 (amd64)\n")

    @staticmethod
    def _install_apt_pass(fr):
        """APT 全部通过的最小集合：update PASS + 4 个包 policy PASS。"""
        fr.script["apt update"] = make_result(stdout="Hit:1 archive ...\nReading package lists... Done\n")
        for pkg, ver in [("podman", "4.9.4"), ("uidmap", "1:4.13+20240101"),
                         ("slirp4netns", "1.3.0"), ("fuse-overlayfs", "1.15")]:
            fr.script[f"apt-cache policy {pkg}"] = make_result(
                stdout=f"Package: {pkg}\n  Candidate: {ver}\n  Installed: (none)\n")
        # apt install 调用的 args 里包含 "install"，这里把子串匹配改成看 "apt install"
        fr.script["apt install -y --no-install-recommends"] = make_result(
            stdout="Unpacking ... done\n")

    @staticmethod
    def _install_full_pass(fr):
        TestInstallHelpers._install_env_base(fr)
        TestInstallHelpers._install_apt_pass(fr)
        # 映射：初始空文件（干净系统尚未生成）→ 需写入然后验证
        fr.script["cat /etc/subuid"] = make_result(stdout="")
        fr.script["cat /etc/subgid"] = make_result(stdout="")
        # CLI 集成测试用明确结果模拟发行版内脚本；空输出由专门测试验证为失败。
        fr.script["python3 -c"] = make_result(stdout="APPENDED\n")
        # 验收项
        fr.script["podman --version"] = make_result(stdout="podman version 4.9.4\n")
        fr.script["podman info --format"] = make_result(stdout="true\n")


# ----------------- 尾部验收失败矩阵：不得宣称成功，保留已完成阶段 -----------------

class TestInstallTailFailures:
    """install 尾部（映射后 podman 版本/rootless 验收）失败分支。"""

    def test_podman_version_failure_aborts_without_claiming_success(
        self, fake_run_wsl, capsys
    ):
        TestInstallHelpers._install_full_pass(fake_run_wsl)
        fake_run_wsl.script["podman --version"] = make_result(
            ok=False, exit_code=127, stderr="podman: command not found"
        )
        ret = cli.main(["podman", "install", "openKylin-3.0", "--yes"])
        assert ret == 1
        out = capsys.readouterr().out
        assert "结论：安装成功" not in out
        assert "[PASS" in out  # 已完成阶段（apt/映射）仍如实列出
        assert "podman --version" in out

    def test_podman_info_failure_aborts(self, fake_run_wsl, capsys):
        TestInstallHelpers._install_full_pass(fake_run_wsl)
        fake_run_wsl.script["podman info --format"] = make_result(
            ok=False, exit_code=125, stderr="Error: cannot re-exec process"
        )
        ret = cli.main(["podman", "install", "openKylin-3.0", "--yes"])
        assert ret == 1
        out = capsys.readouterr().out
        assert "rootless 验收" in out and "[FAIL" in out

    def test_rootless_false_is_fail_not_pass(self, fake_run_wsl, capsys):
        """podman info 返回 false（如以 root 跑或映射未生效）必须 FAIL。"""
        TestInstallHelpers._install_full_pass(fake_run_wsl)
        fake_run_wsl.script["podman info --format"] = make_result(stdout="false\n")
        ret = cli.main(["podman", "install", "openKylin-3.0", "--yes"])
        assert ret == 1
        out = capsys.readouterr().out
        assert "Rootless='false'" in out

    def test_already_mapping_is_idempotent_pass(self, fake_run_wsl, capsys):
        """联合映射脚本返回 ALREADY 时安装通过并说明文件未修改。"""
        TestInstallHelpers._install_full_pass(fake_run_wsl)
        fake_run_wsl.script["python3 -c"] = make_result(stdout="ALREADY\n")
        ret = cli.main(["podman", "install", "openKylin-3.0", "--yes"])
        assert ret == 0
        out = capsys.readouterr().out
        assert "UID/GID 映射均有效，未修改文件" in out
        assert "仅追加缺失的" not in out

    def test_mapping_conflict_aborts_before_rootless_verification(
        self, fake_run_wsl, capsys
    ):
        """联合映射命令报告冲突时安装失败，且不继续 rootless 验收。"""
        TestInstallHelpers._install_full_pass(fake_run_wsl)
        fake_run_wsl.script["python3 -c"] = make_result(
            ok=False, exit_code=2,
            stderr="MAPPING_CONFLICT: 标准区间 [100000, 165536) 冲突：root:100000:65536\n",
        )
        ret = cli.main(["podman", "install", "openKylin-3.0", "--yes"])
        assert ret == 1
        calls = "\n".join(" ".join(c) for c in fake_run_wsl.calls)
        assert "podman --version" not in calls
        assert calls.count("python3 -c") == 1
        out = capsys.readouterr().out
        assert "MAPPING_CONFLICT" in out
        assert "请手动编辑 /etc/subuid 与 /etc/subgid" in out


# ----------------- install 阶段默认用户二次校验失败（preflight 后的防御分支）---------

def _structural_pass_report(name="openKylin-3.0"):
    """构造结构性 5 项全 PASS 的预检报告（其余候选/映射项省略不影响结构门禁）。"""
    report = podman.PreflightReport(distro_name=name)
    report.add("WSL 版本", "PASS")
    report.add("openKylin 身份", "PASS")
    report.add("默认用户非 root", "PASS")
    report.add("APT/dpkg 能力", "PASS")
    return report


class TestInstallDefaultUserRecheck:
    """install_run 在预检后再次读取默认用户；异常身份必须 fail-closed。"""

    @pytest.mark.parametrize(
        "user_out,uid_out,expect_fragment",
        [
            (make_result(ok=False, exit_code=1, stderr="id failed"),
             make_result(stdout="1000\n"), "默认用户非 root"),
            (make_result(stdout="openkylin\n"),
             make_result(stdout="not-a-number\n"), "UID 不是有效整数"),
            (make_result(stdout="root\n"),
             make_result(stdout="0\n"), "要求非 root 用户"),
        ],
    )
    def test_late_user_detection_failures(
        self, fake_run_wsl, monkeypatch, capsys, user_out, uid_out, expect_fragment
    ):
        TestInstallHelpers._install_env_base(fake_run_wsl)
        monkeypatch.setattr(
            podman, "preflight_check", lambda _name: _structural_pass_report()
        )
        fake_run_wsl.script["id -un"] = user_out
        fake_run_wsl.script["id -u"] = uid_out
        ret = cli.main(["podman", "install", "openKylin-3.0", "--yes"])
        assert ret == 1
        out = capsys.readouterr().out
        assert expect_fragment in out
        calls = "\n".join(" ".join(c) for c in fake_run_wsl.calls)
        assert "apt update" not in calls


# ----------------- TR-2.4 修复方向文案 + 未分类安装失败 -----------------

class TestTR24RepairHints:
    """三类失败各自携带可区分的中文修复方向；未分类失败不吞 stderr。"""

    def test_candidate_missing_carries_sources_list_hint(self, fake_run_wsl, capsys):
        TestInstallHelpers._install_env_base(fake_run_wsl)
        fake_run_wsl.script["apt update"] = make_result(stdout="Done\n")
        # apt-cache policy 对缺失包现实中退出 0 且 Candidate: (none)
        fake_run_wsl.script["apt-cache policy podman"] = make_result(
            stdout="Package: podman\n  Candidate: (none)\n"
        )
        ret = cli.main(["podman", "install", "openKylin-3.0", "--yes"])
        assert ret == 1
        out = capsys.readouterr().out
        assert podman.APT_PKG_MISSING_LABEL in out
        assert "禁止添加第三方源" in out
        assert "sources.list" in out

    def test_install_stderr_unable_to_locate_classified_missing(
        self, fake_run_wsl, capsys
    ):
        """apt install stderr 的 unable to locate 也归类为候选缺失（非内部错误）。"""
        TestInstallHelpers._install_env_base(fake_run_wsl)
        TestInstallHelpers._install_apt_pass(fake_run_wsl)
        fake_run_wsl.script["apt install -y --no-install-recommends"] = make_result(
            ok=False, exit_code=100,
            stderr="E: Unable to locate package fuse-overlayfs\n",
        )
        ret = cli.main(["podman", "install", "openKylin-3.0", "--yes"])
        assert ret == 1
        out = capsys.readouterr().out
        assert podman.APT_PKG_MISSING_LABEL in out
        assert "禁止添加第三方源" in out

    def test_install_unknown_failure_keeps_stderr(self, fake_run_wsl, capsys):
        """apt install 返回非三类网络/哈希/缺失错误：保留原始 stderr 片段。"""
        TestInstallHelpers._install_env_base(fake_run_wsl)
        TestInstallHelpers._install_apt_pass(fake_run_wsl)
        fake_run_wsl.script["apt install -y --no-install-recommends"] = make_result(
            ok=False, exit_code=100,
            stderr="E: Sub-process /usr/bin/dpkg returned an error code (1)\n",
        )
        ret = cli.main(["podman", "install", "openKylin-3.0", "--yes"])
        assert ret == 1
        out = capsys.readouterr().out
        assert "apt install 失败" in out
        assert "dpkg returned an error code" in out

    def test_three_hints_are_distinct_chinese_directions(self):
        hints = (podman.APT_PKG_MISSING_HINT, podman.APT_NET_ERROR_HINT,
                 podman.APT_HASH_ERROR_HINT)
        assert len(set(hints)) == 3
        for hint in hints:
            assert "修复方向" in hint

    def test_mapping_conflict_reports_manual_edit_guidance(
        self, fake_run_wsl, capsys
    ):
        TestInstallHelpers._install_full_pass(fake_run_wsl)
        fake_run_wsl.script["python3 -c"] = make_result(
            ok=False, exit_code=2,
            stderr=(
                "MAPPING_CONFLICT: 标准区间 [100000, 165536) 冲突："
                "bin:100000:65536, sys:120000:65536\n"
            ),
        )
        ret = cli.main(["podman", "install", "openKylin-3.0", "--yes"])
        assert ret == 1
        out = capsys.readouterr().out
        assert "bin:100000:65536" in out  # 冲突对比列出账户与区间
        assert "请手动编辑 /etc/subuid 与 /etc/subgid" in out

    @pytest.mark.parametrize(
        "stderr_marker,expect_fragment",
        [
            (
                "MAPPING_INVALID: 映射文件第2行不是三列",
                "请检查映射文件的三列格式、正整数值及目标用户映射有效性",
            ),
            (
                "MAPPING_WRITE_FAILED: 无法读写 /etc/subuid",
                "请检查映射文件权限与磁盘空间",
            ),
        ],
    )
    def test_invalid_and_write_failed_mapping_guidance(
        self, fake_run_wsl, capsys, stderr_marker, expect_fragment
    ):
        TestInstallHelpers._install_full_pass(fake_run_wsl)
        fake_run_wsl.script["python3 -c"] = make_result(
            ok=False, exit_code=2, stderr=stderr_marker + "\n"
        )
        ret = cli.main(["podman", "install", "openKylin-3.0", "--yes"])
        assert ret == 1
        assert expect_fragment in capsys.readouterr().out


class TestInstallRunDirect:
    """install_run 直调分支（CLI 无 --yes 时走 cmd_install 早返回，不经 install_run）。"""

    def test_install_run_without_yes_is_closed(self, fake_run_wsl):
        report = podman.install_run("openKylin-3.0", yes=False)
        assert report.missing_yes is True
        assert report.items == []
        assert report.exit_code() == 2
        assert fake_run_wsl.calls == []
