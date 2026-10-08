"""Task 3 verify 验收与本地镜像冒烟测试：TR-3.1 / TR-3.2。

全部通过 fake_run_wsl mock 发行版调用，不产生任何真实 WSL/网络请求。
"""

import pytest

from okw import cli, podman

from conftest import make_result

SMOKE_IMAGE = "openkylin-local:3.0"
VALID_MAPPING = "openkylin:100000:65536\n"


def _verify_env(
    fr,
    *,
    list_version="2",
    user="openkylin",
    uid="1000",
    podman_version_result=None,
    subuid=VALID_MAPPING,
    subgid=VALID_MAPPING,
    unshare_result=None,
    info_result=None,
):
    """构造 verify 全通过骨架；各参数可注入单项失败。

    注意 script 按插入序做子串首匹配，"id -un" 必须先于 "id -u"。
    """
    fr.script["-l -v"] = make_result(
        stdout=f"""  NAME                   STATE           VERSION
* openKylin-3.0           Running         {list_version}
"""
    )
    fr.script["id -un"] = make_result(stdout=f"{user}\n")
    fr.script["id -u"] = make_result(stdout=f"{uid}\n")
    fr.script["podman --version"] = (
        podman_version_result
        if podman_version_result is not None
        else make_result(stdout="podman version 4.9.4\n")
    )
    fr.script["cat /etc/subuid"] = (
        subuid if hasattr(subuid, "ok") else make_result(stdout=subuid)
    )
    fr.script["cat /etc/subgid"] = (
        subgid if hasattr(subgid, "ok") else make_result(stdout=subgid)
    )
    fr.script["unshare --user"] = (
        unshare_result
        if unshare_result is not None
        else make_result(stdout="")
    )
    fr.script["podman info --format"] = (
        info_result
        if info_result is not None
        else make_result(stdout="true\n")
    )


def _run_verify(fr, *extra):
    return cli.main(["podman", "verify", "openKylin-3.0", *extra])


def _item_line(out: str, item_name: str) -> str:
    for line in out.splitlines():
        if item_name in line and ("PASS" in line or "FAIL" in line or "UNKNOWN" in line):
            return line
    raise AssertionError(f"报告中找不到检查项：{item_name}\n{out}")


def _all_probe_calls(fr):
    return [c for c in fr.calls if "--" in c]


# ----------------- TR-3.1 验收输出矩阵 -----------------

class TestTR31VerifyMatrix:
    def test_distro_missing_fails(self, fake_run_wsl, capsys):
        # 不配置任何 script：默认返回 distro_missing
        ret = _run_verify(fake_run_wsl)
        assert ret == 1
        out = capsys.readouterr().out
        assert "发行版存在" in out and "[FAIL" in out

    def test_wsl1_fails_but_continues_other_checks(self, fake_run_wsl, capsys):
        _verify_env(fake_run_wsl, list_version="1")
        ret = _run_verify(fake_run_wsl)
        assert ret == 1
        out = capsys.readouterr().out
        assert "[FAIL" in _item_line(out, "WSL 版本")
        # WSL1 不阻断后续只读探测，其余项仍应如实输出
        assert "[PASS" in _item_line(out, "rootless 状态")

    def test_identity_commands_fail_aborts(self, fake_run_wsl, capsys):
        _verify_env(fake_run_wsl)
        fake_run_wsl.script["id -un"] = make_result(
            ok=False, exit_code=1, stderr="id: command not found"
        )
        ret = _run_verify(fake_run_wsl)
        assert ret == 1
        out = capsys.readouterr().out
        assert "[FAIL" in _item_line(out, "默认用户非 root")
        calls = "\n".join(" ".join(c) for c in fake_run_wsl.calls)
        assert "podman info" not in calls

    def test_uid_not_integer_aborts(self, fake_run_wsl, capsys):
        _verify_env(fake_run_wsl, uid="not-a-number")
        ret = _run_verify(fake_run_wsl)
        assert ret == 1
        assert "UID 不是有效整数" in capsys.readouterr().out

    def test_root_identity_never_gets_rootless_pass(self, fake_run_wsl, capsys):
        # root 身份下即使 podman info 返回 true，rootless 项也必须强制 FAIL（AC-4）
        _verify_env(fake_run_wsl, user="root", uid="0", info_result=make_result(stdout="true\n"))
        ret = _run_verify(fake_run_wsl)
        assert ret == 1
        out = capsys.readouterr().out
        assert "[FAIL" in _item_line(out, "默认用户非 root")
        rootless_line = _item_line(out, "rootless 状态")
        assert "[FAIL" in rootless_line
        assert podman.ROOT_VERIFY_HINT[:12] in rootless_line

    def test_podman_missing_fails_with_install_hint(self, fake_run_wsl, capsys):
        _verify_env(
            fake_run_wsl,
            podman_version_result=make_result(
                ok=False, exit_code=127, stderr="podman: command not found"
            ),
        )
        ret = _run_verify(fake_run_wsl)
        assert ret == 1
        line = _item_line(capsys.readouterr().out, "podman 版本")
        assert "[FAIL" in line
        assert "okw podman install" in line

    def test_rootless_false_fails(self, fake_run_wsl, capsys):
        _verify_env(fake_run_wsl, info_result=make_result(stdout="false\n"))
        ret = _run_verify(fake_run_wsl)
        assert ret == 1
        line = _item_line(capsys.readouterr().out, "rootless 状态")
        assert "[FAIL" in line and "Rootless='false'" in line

    def test_podman_info_command_failure_fails(self, fake_run_wsl, capsys):
        _verify_env(
            fake_run_wsl,
            info_result=make_result(ok=False, exit_code=125, stderr="Error: cannot re-exec"),
        )
        ret = _run_verify(fake_run_wsl)
        assert ret == 1
        assert "podman info 失败" in capsys.readouterr().out

    @pytest.mark.parametrize(
        "subuid, subgid, bad_item",
        [
            ("garbage-line\n", VALID_MAPPING, "subuid 映射"),
            (VALID_MAPPING, "openkylin:100000:notint\n", "subgid 映射"),
            ("root:100000:65536\n", VALID_MAPPING, "subuid 映射"),
            ("openkylin:100000:1000\n", VALID_MAPPING, "subuid 映射"),
            (
                "other:100000:65536\nopenkylin:100000:65536\n",
                VALID_MAPPING,
                "subuid 映射",
            ),
            (VALID_MAPPING, "", "subgid 映射"),
        ],
    )
    def test_mapping_errors_fail(self, fake_run_wsl, capsys, subuid, subgid, bad_item):
        _verify_env(fake_run_wsl, subuid=subuid, subgid=subgid)
        ret = _run_verify(fake_run_wsl)
        assert ret == 1
        assert "[FAIL" in _item_line(capsys.readouterr().out, bad_item)

    def test_mapping_unreadable_is_unknown_exit_2(self, fake_run_wsl, capsys):
        _verify_env(
            fake_run_wsl,
            subuid=make_result(ok=False, exit_code=1, stderr="Permission denied"),
        )
        ret = _run_verify(fake_run_wsl)
        assert ret == 2  # 仅 UNKNOWN，无 FAIL
        line = _item_line(capsys.readouterr().out, "subuid 映射")
        assert "UNKNOWN" in line

    def test_unshare_failure_fails_with_hint(self, fake_run_wsl, capsys):
        _verify_env(
            fake_run_wsl,
            unshare_result=make_result(
                ok=False, exit_code=1, stderr="unshare: unshare failed: Operation not permitted"
            ),
        )
        ret = _run_verify(fake_run_wsl)
        assert ret == 1
        line = _item_line(capsys.readouterr().out, "unshare 用户命名空间")
        assert "[FAIL" in line
        assert "user namespace" in line

    def test_all_pass_matrix(self, fake_run_wsl, capsys):
        _verify_env(fake_run_wsl)
        ret = _run_verify(fake_run_wsl)
        assert ret == 0
        out = capsys.readouterr().out
        for item in (
            "WSL 版本",
            "默认用户非 root",
            "podman 版本",
            "subuid 映射",
            "subgid 映射",
            "unshare 用户命名空间",
            "rootless 状态",
        ):
            assert "[PASS" in _item_line(out, item), item
        assert "结论：rootless 验收通过" in out

    def test_probes_run_explicitly_as_default_user(self, fake_run_wsl):
        _verify_env(fake_run_wsl)
        _run_verify(fake_run_wsl)
        user_scoped = [
            c
            for c in fake_run_wsl.calls
            if any(x in c for x in ("podman", "unshare", "/etc/sub"))
        ]
        assert user_scoped, "应存在用户级探针调用"
        for call in user_scoped:
            joined = " ".join(call)
            assert "-u openkylin" in joined, f"探针未显式以默认用户执行：{joined}"


# ----------------- TR-3.2 默认不跑容器 / 冒烟禁拉取 / 无网络 -----------------

class TestTR32SmokeNoPull:
    NETWORK_FORBIDDEN_ARGS = ("pull", "docker://", "https://", "http://")

    def _assert_no_network(self, calls):
        for call in calls:
            for token in call:
                # 唯一允许出现 pull 字样的令牌是 --pull=never
                if "pull" in token and token != podman.SMOKE_PULL_POLICY:
                    raise AssertionError(f"出现拉取/网络语义：{call}")
                for forbidden in ("docker://", "https://", "http://"):
                    assert forbidden not in token, f"出现网络地址：{call}"
            assert "pull" not in [t for t in call if t != podman.SMOKE_PULL_POLICY and t in ("pull",)]

    def test_default_verify_runs_no_container(self, fake_run_wsl, capsys):
        _verify_env(fake_run_wsl)
        ret = _run_verify(fake_run_wsl)
        assert ret == 0
        joined_calls = [" ".join(c) for c in fake_run_wsl.calls]
        assert not any(" podman run " in f" {c} " for c in joined_calls)
        assert not any("image exists" in c for c in joined_calls)
        assert not any("container" in c for c in joined_calls)
        out = capsys.readouterr().out
        assert "未执行容器冒烟" in out

    def test_smoke_local_image_runs_with_pull_never(self, fake_run_wsl, capsys):
        _verify_env(fake_run_wsl)
        fake_run_wsl.script["podman image exists"] = make_result(stdout="")
        fake_run_wsl.script["podman run"] = make_result(stdout="")
        ret = _run_verify(fake_run_wsl, "--smoke-image", SMOKE_IMAGE)
        assert ret == 0
        out = capsys.readouterr().out
        assert "[PASS" in _item_line(out, "冒烟容器")

        run_calls = [c for c in fake_run_wsl.calls if "run" in c]
        assert len(run_calls) == 1
        args = run_calls[0]
        assert args == [
            "-d", "openKylin-3.0", "-u", "openkylin", "--",
            "podman", "run", "--rm", "--pull=never", SMOKE_IMAGE, "/bin/true",
        ]
        exists_calls = [c for c in fake_run_wsl.calls if "exists" in c]
        assert len(exists_calls) == 1
        assert SMOKE_IMAGE in exists_calls[0]
        self._assert_no_network(fake_run_wsl.calls)

    def test_smoke_missing_image_fails_without_run(self, fake_run_wsl, capsys):
        _verify_env(fake_run_wsl)
        fake_run_wsl.script["podman image exists"] = make_result(
            ok=False, exit_code=1, stderr=""
        )
        ret = _run_verify(fake_run_wsl, "--smoke-image", SMOKE_IMAGE)
        assert ret == 1
        out = capsys.readouterr().out
        line = _item_line(out, "冒烟容器")
        assert "[FAIL" in line
        assert "本地镜像" in line and "podman pull" in line
        assert not [c for c in fake_run_wsl.calls if "run" in c]
        self._assert_no_network(fake_run_wsl.calls)

    def test_smoke_image_check_other_error_fails_closed(self, fake_run_wsl, capsys):
        _verify_env(fake_run_wsl)
        fake_run_wsl.script["podman image exists"] = make_result(
            ok=False, exit_code=125, stderr="cannot stat storage"
        )
        ret = _run_verify(fake_run_wsl, "--smoke-image", SMOKE_IMAGE)
        assert ret == 1
        assert "[FAIL" in _item_line(capsys.readouterr().out, "冒烟容器")
        assert not [c for c in fake_run_wsl.calls if "run" in c]

    def test_smoke_run_failure_fails_with_repro_hint(self, fake_run_wsl, capsys):
        _verify_env(fake_run_wsl)
        fake_run_wsl.script["podman image exists"] = make_result(stdout="")
        fake_run_wsl.script["podman run"] = make_result(
            ok=False, exit_code=126, stderr="Error: runc create failed"
        )
        ret = _run_verify(fake_run_wsl, "--smoke-image", SMOKE_IMAGE)
        assert ret == 1
        line = _item_line(capsys.readouterr().out, "冒烟容器")
        assert "[FAIL" in line and "--pull=never" in line

    def test_smoke_skipped_when_prior_check_fails(self, fake_run_wsl, capsys):
        _verify_env(
            fake_run_wsl,
            podman_version_result=make_result(
                ok=False, exit_code=127, stderr="podman: command not found"
            ),
        )
        ret = _run_verify(fake_run_wsl, "--smoke-image", SMOKE_IMAGE)
        assert ret == 1
        line = _item_line(capsys.readouterr().out, "冒烟容器")
        assert "[FAIL" in line and "前置检查存在 FAIL" in line
        joined = "\n".join(" ".join(c) for c in fake_run_wsl.calls)
        assert "image exists" not in joined
        assert "podman run" not in joined

    def test_cli_verify_is_wired_no_placeholder(self, fake_run_wsl, capsys):
        """占位分支移除后，verify 直连 podman.cmd_verify。"""
        _verify_env(fake_run_wsl)
        ret = cli.main(["podman", "verify", "openKylin-3.0"])
        assert ret == 0
        captured = capsys.readouterr()
        assert "尚未实现" not in captured.out
        assert "尚未实现" not in captured.err
