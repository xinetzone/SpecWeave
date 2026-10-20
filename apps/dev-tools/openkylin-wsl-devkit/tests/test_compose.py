"""okw compose 纯函数与判定矩阵测试：安装源三分类、路径归一化、
版本/uv 输出解析、网络错误分类、脚本构造、报告退出码与许可证声明。

全部不触 WSL；流程级（fake_run_wsl）测试见 test_compose_flow.py。
"""

import pytest

from okw import compose


# ----------------- 安装源三分类 -----------------

class TestClassifySource:
    @pytest.mark.parametrize(
        "source",
        [
            r"D:\sandbox\libs\xuan-compose",
            "d:/sandbox/libs/xuan-compose",
            "/home/openkylin/xuan-compose",
            "./xuan-compose",
            "../libs/xuan-compose",
            "~/projects/xuan-compose",
        ],
    )
    def test_local_sources(self, source):
        assert compose.classify_source(source) == "local"

    @pytest.mark.parametrize(
        "source",
        [
            "git+https://github.com/xuanspace/xuan-compose.git",
            "https://github.com/xuanspace/xuan-compose/archive/main.tar.gz",
            "ssh://git@git.example.com/libs/xuan-compose.git",
            "git@github.com:xuanspace/xuan-compose.git",
            "xuan-compose.git",
        ],
    )
    def test_url_sources(self, source):
        assert compose.classify_source(source) == "url"

    @pytest.mark.parametrize(
        "source",
        [
            "xuan-compose",
            "xuan-compose==1.6.0",
            "xuan-compose[extras]>=0.1",
            "xc_lib",
        ],
    )
    def test_package_sources(self, source):
        assert compose.classify_source(source) == "package"

    @pytest.mark.parametrize("source", ["", "   ", "bad name!", "xuan compose", "什么包"])
    def test_malformed_raises(self, source):
        with pytest.raises(ValueError):
            compose.classify_source(source)


class TestToDistroPath:
    # 注：这里的字面量是 to_distro_path 函数规格的逐字断言（输入→输出契约），
    # 属测试本职；样本一律使用中性虚拟路径，不引用任何本机真实目录布局。
    def test_windows_drive_to_mnt(self):
        assert compose.to_distro_path(
            r"D:\sandbox\libs\xuan-compose"
        ) == "/mnt/d/sandbox/libs/xuan-compose"

    def test_windows_forward_slash(self):
        assert compose.to_distro_path("C:/tmp/x") == "/mnt/c/tmp/x"

    def test_posix_path_unchanged(self):
        assert compose.to_distro_path("/home/openkylin/x") == "/home/openkylin/x"


# ----------------- 版本与 uv 输出解析 -----------------

class TestParseVersionToken:
    def test_plain_version(self):
        assert compose.parse_version_token("1.6.0+xuan.1\n") == "1.6.0+xuan.1"

    def test_version_embedded(self):
        assert compose.parse_version_token("xuan-compose 0.1.0") == "0.1.0"

    @pytest.mark.parametrize("text", ["", "garbage", "no digits here"])
    def test_no_version(self, text):
        assert compose.parse_version_token(text) is None


class TestParseUvPythonList:
    def test_installed(self):
        stdout = (
            "cpython-3.12.2-linux-x86_64-gnu    /usr/bin/python3.12\n"
            "cpython-3.14.0-linux-x86_64-gnu    "
            "/home/openkylin/.local/share/uv/python/cpython-3.14.0-x86_64-unknown-linux-gnu/bin/python3.14\n"
        )
        assert compose.parse_uv_python_list(stdout) == "installed"

    def test_download_available(self):
        stdout = (
            "cpython-3.12.2-linux-x86_64-gnu    /usr/bin/python3.12\n"
            "cpython-3.14.0-linux-x86_64-gnu    <download available>\n"
        )
        assert compose.parse_uv_python_list(stdout) == "available"

    def test_absent(self):
        stdout = "cpython-3.12.2-linux-x86_64-gnu    /usr/bin/python3.12\n"
        assert compose.parse_uv_python_list(stdout) == "absent"

    def test_freethreaded_build_not_counted(self):
        # 仅 free-threaded 3.14 可用不等于标准 GIL 构建已安装
        stdout = (
            "cpython-3.14.0+freethreaded-linux-x86_64-gnu    <download available>\n"
            "cpython-3.12.2-linux-x86_64-gnu    /usr/bin/python3.12\n"
        )
        assert compose.parse_uv_python_list(stdout) == "absent"


class TestToolListed:
    def test_installed_entry(self):
        stdout = "xuan-compose v1.6.0+xuan.1 - Installed 2 executables: xc, xuan-compose\n"
        assert compose.tool_is_listed(stdout) is True

    def test_local_editable_entry(self):
        stdout = "black v24.1.0\nxuan-compose v0.1.0\n"
        assert compose.tool_is_listed(stdout) is True

    def test_not_installed(self):
        assert compose.tool_is_listed("black v24.1.0\nruff v0.9.0\n") is False
        assert compose.tool_is_listed("") is False
        # 子串出现在路径行中不得误判为已登记工具
        assert compose.tool_is_listed("/tmp/xuan-compose-snapshot/x\n") is False


# ----------------- 网络错误分类 -----------------

class TestIsNetworkError:
    @pytest.mark.parametrize(
        "text",
        [
            "curl: (6) Could not resolve host: astral.sh",
            "error: failed to download: network is unreachable",
            "error sending request for url (https://pypi.org/simple/pyyaml/)",
            "tls handshake failed",
            "Connection timed out after 30s",
        ],
    )
    def test_network_markers(self, text):
        assert compose.is_network_error(text) is True

    @pytest.mark.parametrize(
        "text",
        [
            "error: failed to build wheel for package",
            "Permission denied: '/home/devuser/.local/bin/xc'",
            "Python 3.14 is required but 3.12 found",
        ],
    )
    def test_non_network_errors(self, text):
        assert compose.is_network_error(text) is False


# ----------------- shell 脚本构造（base64 透传实践） -----------------

class TestScripts:
    def test_smoke_script_is_isolated_and_non_mutating(self):
        script = compose.smoke_script()
        # 临时目录前缀、compose 文件名、config 子命令均为产品契约常量，
        # 测试不得另写一份字面量（防两处漂移）。
        assert f"mktemp -d {compose.SMOKE_TMP_PREFIX}" in script
        assert "trap 'rm -rf" in script
        # 端到端探活只做配置解析（xc 内部仅触达 podman info），不起容器不拉镜像
        assert compose.SMOKE_COMPOSE_FILE in script
        assert " ".join(compose.SMOKE_CONFIG_ARGS) in script
        for forbidden in ("podman pull", " podman run", " up ", " down", "--pull="):
            assert forbidden not in script, f"冒烟脚本出现变更性操作：{forbidden}"

    def test_installer_script_default_url(self):
        script = compose.installer_script(compose.UV_INSTALLER_URL_DEFAULT)
        assert "curl -LsSf" in script
        assert compose.UV_INSTALLER_URL_DEFAULT in script
        assert script.rstrip().endswith("| sh")

    def test_installer_script_quotes_metacharacters(self):
        url = "https://mirror.example.com/uv.sh?token=a&b=c;d"
        script = compose.installer_script(url)
        # 含 & 与 ; 的镜像 URL 必须被单引号包裹，杜绝 shell 注入/截断
        assert "'https://mirror.example.com/uv.sh?token=a&b=c;d'" in script


# ----------------- 报告退出码语义 -----------------

class TestReportExitCodes:
    def test_preflight_all_pass(self):
        report = compose.PreflightReport("ok")
        report.add("a", "PASS")
        report.add("b", "PASS")
        assert report.exit_code() == 0

    def test_preflight_only_unknown_is_2(self):
        report = compose.PreflightReport("ok")
        report.add("a", "PASS")
        report.add("b", "UNKNOWN")
        assert report.exit_code() == 2

    def test_preflight_fail_is_1(self):
        report = compose.PreflightReport("ok")
        report.add("a", "PASS")
        report.add("b", "UNKNOWN")
        report.add("c", "FAIL")
        assert report.exit_code() == 1

    def test_install_missing_yes_is_2(self):
        report = compose.InstallReport("ok", missing_yes=True)
        assert report.exit_code() == 2

    def test_verify_all_pass_is_0(self):
        report = compose.VerifyReport("ok")
        report.add("a", "PASS")
        assert report.exit_code() == 0


# ----------------- GPL 边界声明（许可证红线） -----------------

class TestLicenseNotice:
    def test_notice_declares_gpl_and_no_redistribution(self):
        notice = compose.LICENSE_NOTICE
        assert "GPL-2.0-only" in notice
        assert "xuan-compose" in notice
        # 语义：okw 不分发 xc、不链接其源码，仅在用户发行版内引导安装
        assert ("不随 okw" in notice) or ("不随本工具" in notice) or ("不分发" in notice)
