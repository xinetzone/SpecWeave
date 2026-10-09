"""okw image build/verify 子命令测试（OQ-1 后续候选落地）。

全部通过 fake_run_wsl mock 发行版调用，不产生任何真实 WSL/网络请求。
覆盖：build 的发行版/WSL/podman/基底/上下文/构建矩阵与禁拉纪律；
verify 的镜像存在/静态探针/全量启动健康/服务探针/清理矩阵与 --no-boot。
"""


from conftest import make_result

from okw import cli, image

CTR_ID = "c0ffee0123456789abcdef0123456789abcdef0123456789abcdef0123456789"
SERVICE_OK = "SSH_OK\nJUPYTER_OK\nPORTS_OK\nJUPYTER_HTTP_200\n"


def _distro_env(fr, *, list_version="2"):
    fr.script["-l -v"] = make_result(
        stdout=f"""  NAME                   STATE           VERSION
* openKylin-3.0           Running         {list_version}
"""
    )


def _podman_env(fr, *, version_result=None, info_result=None):
    fr.script["podman --version"] = (
        version_result if version_result is not None else make_result(stdout="podman version 5.7.0\n")
    )
    fr.script["podman info"] = (
        info_result if info_result is not None else make_result(stdout="host info ok\n")
    )


def _join_calls(fr) -> str:
    return "\n".join(" ".join(c) for c in fr.calls)


# ----------------- build：门与基底 -----------------

class TestImageBuildGates:
    def test_distro_missing_fails(self, fake_run_wsl, capsys):
        ret = cli.main(["image", "build", "openKylin-3.0"])
        assert ret == 1
        out = capsys.readouterr().out
        assert "发行版存在" in out and "[FAIL" in out

    def test_wsl1_fails(self, fake_run_wsl, capsys):
        _distro_env(fake_run_wsl, list_version="1")
        ret = cli.main(["image", "build", "openKylin-3.0"])
        assert ret == 1
        assert "[FAIL" in capsys.readouterr().out

    def test_podman_missing_fails_with_install_hint(self, fake_run_wsl, capsys):
        _distro_env(fake_run_wsl)
        _podman_env(
            fake_run_wsl,
            version_result=make_result(
                ok=False, exit_code=127, stderr="podman: command not found"
            ),
        )
        ret = cli.main(["image", "build", "openKylin-3.0"])
        assert ret == 1
        line = next(
            ln for ln in capsys.readouterr().out.splitlines() if "podman 可用" in ln
        )
        assert "[FAIL" in line and "okw podman install" in line

    def test_podman_info_failure_fails(self, fake_run_wsl, capsys):
        _distro_env(fake_run_wsl)
        _podman_env(
            fake_run_wsl,
            info_result=make_result(ok=False, exit_code=125, stderr="cannot re-exec"),
        )
        ret = cli.main(["image", "build", "openKylin-3.0"])
        assert ret == 1
        assert "podman 后端" in capsys.readouterr().out


class TestImageBuildBasePullDiscipline:
    def test_base_missing_without_pull_base_fails_no_pull(self, fake_run_wsl, capsys):
        _distro_env(fake_run_wsl)
        _podman_env(fake_run_wsl)
        fake_run_wsl.script["image exists"] = make_result(ok=False, exit_code=1)
        ret = cli.main(["image", "build", "openKylin-3.0"])
        assert ret == 1
        out = capsys.readouterr().out
        line = next(ln for ln in out.splitlines() if "基镜像存在" in ln)
        assert "[FAIL" in line and "localhost/openkylin:3.0" in line
        joined = _join_calls(fake_run_wsl)
        assert " pull " not in f" {joined} "
        assert "podman build" not in joined

    def test_base_missing_with_pull_base_pulls(self, fake_run_wsl, capsys):
        _distro_env(fake_run_wsl)
        _podman_env(fake_run_wsl)
        fake_run_wsl.script["image exists"] = make_result(ok=False, exit_code=1)
        fake_run_wsl.script["podman pull"] = make_result(stdout="pulled\n")
        fake_run_wsl.script["cp -a"] = make_result(stdout="")
        fake_run_wsl.script["podman build"] = make_result(stdout="STEP 1/1: COMMIT\n")
        ret = cli.main(["image", "build", "openKylin-3.0", "--pull-base"])
        assert ret == 0
        joined = _join_calls(fake_run_wsl)
        assert "podman pull localhost/openkylin:3.0" in joined
        assert "podman build" in joined


class TestImageBuildRun:
    def _build_env(self, fr):
        _distro_env(fr)
        _podman_env(fr)
        fr.script["image exists"] = make_result(stdout="")
        fr.script["cp -a"] = make_result(stdout="")
        fr.script["podman build"] = make_result(stdout="STEP 1/1: COMMIT\n--> OK\n")

    def test_build_success_syncs_context_and_builds(self, fake_run_wsl, capsys):
        self._build_env(fake_run_wsl)
        ret = cli.main(["image", "build", "openKylin-3.0"])
        assert ret == 0
        out = capsys.readouterr().out
        assert "构建成功" in out and "localhost/openkylin-dev:3.0" in out
        joined = _join_calls(fake_run_wsl)
        # 上下文同步：Windows 盘符 → 发行版内 /mnt/d/...，且落 /tmp/okw-build-*/ctx
        assert "cp -a /mnt/d/" in joined
        assert "/tmp/okw-build-" in joined and "Containerfile" in joined
        # 构建命令：docker 格式 + 标签
        assert "podman build --format docker -t localhost/openkylin-dev:3.0" in joined
        # 全程以 root 身份（跳过 -l -v 列表探测）
        for call in fake_run_wsl.calls:
            if call[:2] == ["-l", "-v"]:
                continue
            assert "-u root" in " ".join(call), f"调用未以 root 身份执行：{call}"

    def test_build_with_tag_and_no_cache(self, fake_run_wsl, capsys):
        self._build_env(fake_run_wsl)
        ret = cli.main(["image", "build", "openKylin-3.0", "--tag", "3.1", "--no-cache"])
        assert ret == 0
        joined = _join_calls(fake_run_wsl)
        assert "localhost/openkylin-dev:3.1" in joined
        assert "--no-cache" in joined

    def test_build_context_missing_containerfile_fails(self, fake_run_wsl, capsys, tmp_path):
        _distro_env(fake_run_wsl)
        _podman_env(fake_run_wsl)
        fake_run_wsl.script["image exists"] = make_result(stdout="")
        empty = tmp_path / "empty-ctx"
        empty.mkdir()
        ret = cli.main(
            ["image", "build", "openKylin-3.0", "--context", str(empty)]
        )
        assert ret == 1
        out = capsys.readouterr().out
        assert "[FAIL" in out and "Containerfile" in out
        assert "cp -a" not in _join_calls(fake_run_wsl)
        assert "podman build" not in _join_calls(fake_run_wsl)

    def test_build_failure_reports_and_raw_log(self, fake_run_wsl, capsys):
        self._build_env(fake_run_wsl)
        fake_run_wsl.script["podman build"] = make_result(
            ok=False, exit_code=1, stdout="STEP 1/3: FROM localhost/openkylin:3.0\n",
            stderr="Error: build failed\n",
        )
        ret = cli.main(["image", "build", "openKylin-3.0"])
        assert ret == 1
        out = capsys.readouterr().out
        assert "podman build 输出" in out
        assert "构建未通过" in out

    def test_build_context_can_be_container_absolute(self, fake_run_wsl, capsys):
        _distro_env(fake_run_wsl)
        _podman_env(fake_run_wsl)
        fake_run_wsl.script["image exists"] = make_result(stdout="")
        fake_run_wsl.script["podman build"] = make_result(stdout="OK\n")
        ret = cli.main(
            ["image", "build", "openKylin-3.0", "--context", "/srv/okw-ctx"]
        )
        assert ret == 0
        joined = _join_calls(fake_run_wsl)
        assert "cp -a" not in joined  # 发行版内已有路径，不再同步
        assert "podman build --format docker -t localhost/openkylin-dev:3.0 /srv/okw-ctx" in joined


# ----------------- verify：门与镜像存在 -----------------

class TestImageVerifyGates:
    def test_distro_missing_fails(self, fake_run_wsl, capsys):
        ret = cli.main(["image", "verify", "openKylin-3.0"])
        assert ret == 1
        assert "发行版存在" in capsys.readouterr().out

    def test_wsl1_fails(self, fake_run_wsl, capsys):
        _distro_env(fake_run_wsl, list_version="1")
        ret = cli.main(["image", "verify", "openKylin-3.0"])
        assert ret == 1

    def test_image_missing_fails_without_run(self, fake_run_wsl, capsys):
        _distro_env(fake_run_wsl)
        _podman_env(fake_run_wsl)
        fake_run_wsl.script["image exists"] = make_result(ok=False, exit_code=1)
        ret = cli.main(["image", "verify", "openKylin-3.0"])
        assert ret == 1
        out = capsys.readouterr().out
        line = next(ln for ln in out.splitlines() if "镜像存在" in ln)
        assert "[FAIL" in line and "--pull=never" in line
        joined = _join_calls(fake_run_wsl)
        assert " podman run " not in f" {joined} "
        assert " pull " not in f" {joined} "


# ----------------- verify：静态探针与全量启动 -----------------

def _verify_env(fr, *, probe_result=None, run_result=None, inspect_result=None, exec_result=None, rm_result=None):
    _distro_env(fr)
    _podman_env(fr)
    fr.script["image exists"] = make_result(stdout="")
    fr.script["--entrypoint"] = (
        probe_result if probe_result is not None else make_result(stdout="P1..P8\nALL_PROBES_OK\n")
    )
    fr.script["run -d"] = (
        run_result if run_result is not None else make_result(stdout=CTR_ID + "\n")
    )
    fr.script["podman inspect"] = (
        inspect_result if inspect_result is not None else make_result(stdout="healthy\n")
    )
    fr.script["podman exec"] = (
        exec_result if exec_result is not None else make_result(stdout=SERVICE_OK)
    )
    fr.script["podman rm -f"] = (
        rm_result if rm_result is not None else make_result(stdout="")
    )


class TestImageVerifyRun:
    def test_all_pass_full_boot(self, fake_run_wsl, capsys, monkeypatch):
        monkeypatch.setattr(image, "HEALTHCHECK_WAIT_SLEEP", 0)
        _verify_env(fake_run_wsl)
        ret = cli.main(["image", "verify", "openKylin-3.0"])
        assert ret == 0
        out = capsys.readouterr().out
        for item in ("镜像存在", "静态探针", "容器健康", "服务探针", "容器清理"):
            line = next(ln for ln in out.splitlines() if item in ln and "PASS" in ln)
            assert item in line, item
        assert "验收全部通过" in out
        joined = _join_calls(fake_run_wsl)
        # 契约参数 + 禁拉
        assert "--device /dev/fuse" in joined
        assert "--security-opt label=disable" in joined
        assert "--cgroupns=host" in joined
        assert "podman run --rm --pull=never" in joined
        assert "podman run -d --pull=never" in joined
        assert "rm -f" in joined and CTR_ID[:12] in joined

    def test_all_probe_calls_are_root_scoped(self, fake_run_wsl, capsys, monkeypatch):
        monkeypatch.setattr(image, "HEALTHCHECK_WAIT_SLEEP", 0)
        _verify_env(fake_run_wsl)
        cli.main(["image", "verify", "openKylin-3.0"])
        scoped = [c for c in fake_run_wsl.calls if c[:2] != ["-l", "-v"]]
        assert scoped
        for call in scoped:
            assert "-u root" in " ".join(call), f"容器操作未以 root 身份执行：{call}"

    def test_static_probe_failure_fails(self, fake_run_wsl, capsys, monkeypatch):
        monkeypatch.setattr(image, "HEALTHCHECK_WAIT_SLEEP", 0)
        _verify_env(
            fake_run_wsl,
            probe_result=make_result(
                ok=False, exit_code=1, stdout="P1 sshd -t\nPROBE_FAIL: sshd -t\n"
            ),
        )
        ret = cli.main(["image", "verify", "openKylin-3.0"])
        assert ret == 1
        out = capsys.readouterr().out
        line = next(ln for ln in out.splitlines() if "静态探针" in ln)
        assert "[FAIL" in line

    def test_healthy_timeout_fails_and_cleanup(self, fake_run_wsl, capsys, monkeypatch):
        monkeypatch.setattr(image, "HEALTHCHECK_WAIT_SLEEP", 0)
        _verify_env(
            fake_run_wsl,
            inspect_result=make_result(stdout="starting\n"),
        )
        fake_run_wsl.script["podman logs"] = make_result(stdout="boot log tail\n")
        ret = cli.main(["image", "verify", "openKylin-3.0"])
        assert ret == 1
        out = capsys.readouterr().out
        assert "HEALTHCHECK 未达 healthy" in out
        assert "podman rm -f" in _join_calls(fake_run_wsl)

    def test_service_probe_incomplete_fails(self, fake_run_wsl, capsys, monkeypatch):
        monkeypatch.setattr(image, "HEALTHCHECK_WAIT_SLEEP", 0)
        _verify_env(
            fake_run_wsl,
            exec_result=make_result(stdout="SSH_OK\nJUPYTER_OK\n"),
        )
        ret = cli.main(["image", "verify", "openKylin-3.0"])
        assert ret == 1
        out = capsys.readouterr().out
        line = next(ln for ln in out.splitlines() if "服务探针" in ln)
        assert "[FAIL" in line

    def test_no_boot_skips_full_stack(self, fake_run_wsl, capsys):
        _verify_env(fake_run_wsl)
        ret = cli.main(["image", "verify", "openKylin-3.0", "--no-boot"])
        assert ret == 0
        out = capsys.readouterr().out
        assert "未启动服务栈" in out
        joined = _join_calls(fake_run_wsl)
        assert "run -d" not in joined
        assert "podman inspect" not in joined
        assert "podman exec" not in joined

    def test_cli_verify_is_wired(self, fake_run_wsl, capsys, monkeypatch):
        monkeypatch.setattr(image, "HEALTHCHECK_WAIT_SLEEP", 0)
        _verify_env(fake_run_wsl)
        ret = cli.main(["image", "verify", "openKylin-3.0"])
        assert ret == 0
        captured = capsys.readouterr()
        assert "尚未实现" not in captured.out + captured.err

    def test_custom_image_flag(self, fake_run_wsl, capsys, monkeypatch):
        monkeypatch.setattr(image, "HEALTHCHECK_WAIT_SLEEP", 0)
        _verify_env(fake_run_wsl)
        ret = cli.main(["image", "verify", "openKylin-3.0", "--image", "localhost/openkylin-dev:3.1"])
        assert ret == 0
        joined = _join_calls(fake_run_wsl)
        assert "localhost/openkylin-dev:3.1" in joined
