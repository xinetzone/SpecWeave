"""okw ai 领域模块单测：preflight/install/verify 全分支 + 解析器 + 只读/离线哨兵。

fake_run_wsl 按子串命中返回；ai preflight 用单条批量 policy，install 的候选
复查用单包 policy，二者用不同 script 键区分。所有命令均不触网、不写系统。
"""

import pytest

from okw import ai, cli, podman

from conftest import make_result

NAME = "openKylin-3.0"

# 组件 → 全通过场景的候选版本
CANDIDATES = {
    "libkylin-ai-base-dev": "2.0.0.0-ok1.0",
    "libkylin-ai-base2": "2.0.0.0-ok1.0",
    "tesseract-ocr": "5.3.4-1",
    "tesseract-ocr-chi-sim": "1:5.3.4-1",
    "tesseract-ocr-eng": "1:5.3.4-1",
    "kylin-ai-model-manager": "0.0.0.1-ok7",
    "libkysdk-genai-nlp0": "1.1.0.1-ok1.6",
    "kylin-ai-engine-plugins": "1.1.0.1-ok1.5",
    "kylin-ondevice-nlp-engine": "1.0.0.0-ok0.2",
    "kytensor-server": "2.49.0.6-0ok11",
}
INSTALLED = {"libkysdk-genai-nlp0": "1.1.0.1-ok1.6"}


# --------------------------- 场景搭建 helper ---------------------------

def install_os(fr):
    """结构：发行版在列 WSL2、openKylin、dpkg/apt 可用。"""
    fr.script["-l -v"] = make_result(
        stdout="  NAME            STATE     VERSION\n  openKylin-3.0   Running   2\n"
    )
    fr.script["cat /etc/os-release"] = make_result(
        stdout='NAME="openKylin"\nID=openkylin\nVERSION_ID="3.0"\n'
    )
    fr.script["dpkg --version"] = make_result(stdout="Debian dpkg 1.22.10\n")
    fr.script["apt-cache --version"] = make_result(stdout="apt 2.7.14\n")


def policy_section(pkg, installed, candidate):
    return (
        f"{pkg}:\n"
        f"  Installed: {installed}\n"
        f"  Candidate: {candidate}\n"
        f"  Version table:\n"
    )


def batched_policy_output(missing=(), candidate_none=()):
    """构造单批 apt-cache policy 输出；missing 不出段，candidate_none 候选 (none)。"""
    blocks = []
    for component in ai.COMPONENTS:
        pkg = component.package
        if pkg in missing:
            continue
        installed = INSTALLED.get(pkg, "(none)")
        if pkg in candidate_none:
            candidate = "(none)"
        else:
            candidate = CANDIDATES.get(pkg, "(none)")
        blocks.append(policy_section(pkg, installed, candidate))
    return "".join(blocks)


def install_preflight_full(fr, **kwargs):
    install_os(fr)
    fr.script["apt-cache policy libkylin-ai-base-dev libkylin-ai-base2"] = make_result(
        stdout=batched_policy_output(**kwargs)
    )


def joined_calls(fr):
    return [" ".join(c) for c in fr.calls]


# --------------------------- 解析器单测 ---------------------------

class TestParsePolicyBatch:
    def test_full_output(self):
        out = (
            "libkylin-ai-base-dev:\n"
            "  Installed: (none)\n"
            "  Candidate: 2.0.0.0-ok1.0\n"
            "  Version table:\n"
            "tesseract-ocr:\n"
            "  Installed: 5.3.4-1\n"
            "  Candidate: 5.3.4-1\n"
        )
        parsed = ai.parse_policy_batch(out)
        assert parsed["libkylin-ai-base-dev"] == {
            "installed": "(none)", "candidate": "2.0.0.0-ok1.0"
        }
        assert parsed["tesseract-ocr"]["installed"] == "5.3.4-1"

    def test_zhcn_markers(self):
        out = "tesseract-ocr:\n  已安装：(无)\n  候选： 5.3.4-1\n"
        parsed = ai.parse_policy_batch(out)
        assert parsed["tesseract-ocr"]["candidate"] == "5.3.4-1"
        assert parsed["tesseract-ocr"]["installed"] == "(无)"

    def test_unknown_header_ignored(self):
        out = "some-stranger:\n  Candidate: 9.9\nlibkylin-ai-base2:\n  Candidate: 2.0\n"
        parsed = ai.parse_policy_batch(out)
        assert "some-stranger" not in parsed
        assert parsed["libkylin-ai-base2"]["candidate"] == "2.0"

    def test_empty(self):
        assert ai.parse_policy_batch("") == {}


class TestComponentPolicyItem:
    def test_required_installed(self):
        c = ai._BY_PACKAGE["libkylin-ai-base2"]
        item = ai._component_policy_item(c, {"installed": "2.0", "candidate": "2.0"})
        assert item.status == "PASS" and "已装 2.0" in item.detail

    def test_required_candidate_pass(self):
        c = ai._BY_PACKAGE["libkylin-ai-base-dev"]
        item = ai._component_policy_item(c, {"installed": "(none)", "candidate": "2.0"})
        assert item.status == "PASS" and "候选 2.0" in item.detail

    def test_required_missing_section_unknown(self):
        c = ai._BY_PACKAGE["libkylin-ai-base-dev"]
        item = ai._component_policy_item(c, None)
        assert item.status == "UNKNOWN" and podman.APT_UNKNOWN_LABEL in item.detail

    def test_required_candidate_none_fail(self):
        c = ai._BY_PACKAGE["tesseract-ocr"]
        item = ai._component_policy_item(c, {"installed": "(none)", "candidate": "(none)"})
        assert item.status == "FAIL" and podman.APT_PKG_MISSING_LABEL in item.detail

    def test_optional_present_pass(self):
        c = ai._BY_PACKAGE["kylin-ai-model-manager"]
        item = ai._component_policy_item(c, {"installed": "(none)", "candidate": "0.0.0.1"})
        assert item.status == "PASS"

    def test_optional_absent_unknown_note(self):
        c = ai._BY_PACKAGE["kylin-ai-model-manager"]
        item = ai._component_policy_item(c, {"installed": "(none)", "candidate": "(none)"})
        assert item.status == "UNKNOWN" and "手动 sudo apt install" in item.detail

    def test_ollama_absent_special_note(self):
        c = ai._BY_PACKAGE["ollama"]
        item = ai._component_policy_item(c, {"installed": "(none)", "candidate": "(none)"})
        assert item.status == "UNKNOWN" and "curl|sh" in item.detail


# --------------------------- preflight 场景 ---------------------------

class TestPreflight:
    def test_distro_not_exist_early_return(self, fake_run_wsl, capsys):
        ret = cli.main(["ai", "preflight", "ghost"])
        assert ret == 1
        out = capsys.readouterr().out
        assert "ghost 未注册" in out
        calls = joined_calls(fake_run_wsl)
        assert not any("/etc/os-release" in c for c in calls)

    def test_wsl1(self, fake_run_wsl, capsys):
        install_os(fake_run_wsl)
        fake_run_wsl.script["-l -v"] = make_result(
            stdout=f"  NAME            STATE     VERSION\n  {NAME}    Running   1\n"
        )
        ret = cli.main(["ai", "preflight", NAME])
        assert ret == 1
        assert "要求 WSL2" in capsys.readouterr().out

    def test_non_openkylin(self, fake_run_wsl, capsys):
        install_os(fake_run_wsl)
        fake_run_wsl.script["cat /etc/os-release"] = make_result(stdout="ID=ubuntu\n")
        ret = cli.main(["ai", "preflight", NAME])
        assert ret == 1
        assert "ID 不是 openkylin" in capsys.readouterr().out

    def test_apt_missing(self, fake_run_wsl, capsys):
        install_os(fake_run_wsl)
        fake_run_wsl.script["dpkg --version"] = make_result(
            ok=False, exit_code=127, stderr="dpkg: not found\n"
        )
        ret = cli.main(["ai", "preflight", NAME])
        assert ret == 1
        assert "dpkg 不可用" in capsys.readouterr().out

    def test_network_error(self, fake_run_wsl, capsys):
        install_os(fake_run_wsl)
        fake_run_wsl.script["apt-cache policy libkylin-ai-base-dev libkylin-ai-base2"] = make_result(
            ok=False, exit_code=100, stdout="",
            stderr="Temporary failure resolving 'archive.openkylin.top'\n",
        )
        ret = cli.main(["ai", "preflight", NAME])
        assert ret == 1
        out = capsys.readouterr().out
        assert "网络错误" in out and podman.APT_NET_ERROR_HINT in out

    def test_policy_command_fail_no_stdout(self, fake_run_wsl, capsys):
        install_os(fake_run_wsl)
        fake_run_wsl.script["apt-cache policy libkylin-ai-base-dev libkylin-ai-base2"] = make_result(
            ok=False, exit_code=1, stdout="", stderr="boom\n"
        )
        ret = cli.main(["ai", "preflight", NAME])
        assert ret == 1
        assert "apt-cache policy 命令失败" in capsys.readouterr().out

    def test_full_pass_exit0_despite_optional_unknown(self, fake_run_wsl, capsys):
        # ollama 候选 (none) → 可选 UNKNOWN；其余必选/可选有候选 → 门控仍 0
        install_preflight_full(fake_run_wsl, candidate_none=("ollama",))
        ret = cli.main(["ai", "preflight", NAME])
        assert ret == 0
        out = capsys.readouterr().out
        assert "预检全部通过" in out
        assert "[UNKNOWN]" in out  # ollama 仍如实显示
        assert "curl|sh" in out

    def test_required_missing_section_exit2(self, fake_run_wsl, capsys):
        # 安装目标整段缺失（索引过期）→ UNKNOWN → exit 2 + apt update 建议
        install_preflight_full(fake_run_wsl, missing=("libkylin-ai-base-dev",))
        ret = cli.main(["ai", "preflight", NAME])
        assert ret == 2
        out = capsys.readouterr().out
        assert "sudo apt update" in out

    def test_required_candidate_none_exit1(self, fake_run_wsl, capsys):
        install_preflight_full(fake_run_wsl, candidate_none=("tesseract-ocr",))
        ret = cli.main(["ai", "preflight", NAME])
        assert ret == 1
        assert podman.APT_PKG_MISSING_LABEL in capsys.readouterr().out

    def test_single_batched_policy_call_and_readonly(self, fake_run_wsl):
        install_preflight_full(fake_run_wsl)
        assert cli.main(["ai", "preflight", NAME]) == 0
        policy_calls = [c for c in joined_calls(fake_run_wsl) if "apt-cache policy" in c]
        # 仅一条批量 policy（apt-cache --version 不算 policy）
        assert len(policy_calls) == 1
        joined = "\n".join(joined_calls(fake_run_wsl))
        for forb in ("apt update", "apt install", " -s ", "podman run"):
            assert forb not in joined
        # C locale 前缀
        assert "env LC_ALL=C LANGUAGE=C apt-cache policy" in joined


# --------------------------- tesseract 探针 ---------------------------

class TestTesseractProbes:
    def test_parse_version(self):
        assert ai.parse_tesseract_version("tesseract 5.3.4\n leptonica-1.82\n") == "5.3.4"
        assert ai.parse_tesseract_version("no version") == ""

    def test_parse_langs(self):
        text = "List of available languages (3):\neng\nchi_sim\nosd\n"
        assert ai.parse_tesseract_langs(text) == {"eng", "chi_sim", "osd"}

    def test_add_checks_pass(self, fake_run_wsl):
        install_os(fake_run_wsl)
        fake_run_wsl.script["tesseract --version"] = make_result(stdout="tesseract 5.3.4\n")
        fake_run_wsl.script["tesseract --list-langs"] = make_result(
            stdout="eng\nchi_sim\n", stderr="List of available languages\n"
        )
        report = ai.PreflightReport(distro_name=NAME)
        ai.add_tesseract_checks(report, NAME)
        assert report.all_passed()

    def test_add_checks_missing_lang(self, fake_run_wsl):
        install_os(fake_run_wsl)
        fake_run_wsl.script["tesseract --version"] = make_result(stdout="tesseract 5.3.4\n")
        fake_run_wsl.script["tesseract --list-langs"] = make_result(stdout="eng\n")
        report = ai.PreflightReport(distro_name=NAME)
        ai.add_tesseract_checks(report, NAME)
        lang_item = [i for i in report.items if i.name == "tesseract 语言包"][0]
        assert lang_item.status == "FAIL" and "chi_sim" in lang_item.detail

    def test_add_checks_binary_missing(self, fake_run_wsl):
        install_os(fake_run_wsl)
        fake_run_wsl.script["tesseract --version"] = make_result(
            ok=False, exit_code=127, stderr="tesseract: not found\n"
        )
        fake_run_wsl.script["tesseract --list-langs"] = make_result(
            ok=False, exit_code=127, stderr="tesseract: not found\n"
        )
        report = ai.PreflightReport(distro_name=NAME)
        ai.add_tesseract_checks(report, NAME)
        assert report.exit_code() == 1


# --------------------------- install 场景 ---------------------------

def install_full(fr, tesseract_ok=True):
    """完整成功安装链：apt update ok、候选复查 ok、install ok、tesseract ok。"""
    install_os(fr)
    fr.script["apt update"] = make_result(stdout="Reading package lists... Done\n")
    # 候选复查（单包 policy）
    fr.script["apt-cache policy libkylin-ai-base-dev"] = make_result(
        stdout="libkylin-ai-base-dev:\n  Installed: (none)\n  Candidate: 2.0.0.0-ok1.0\n"
    )
    fr.script["apt install"] = make_result(stdout="Setting up libkylin-ai-base-dev ...\n")
    if tesseract_ok:
        fr.script["tesseract --version"] = make_result(stdout="tesseract 5.3.4\n")
        fr.script["tesseract --list-langs"] = make_result(stdout="eng\nchi_sim\n")


class TestInstall:
    def test_no_yes_zero_write_exit2(self, fake_run_wsl, capsys):
        ret = cli.main(["ai", "install", NAME])
        assert ret == 2
        out = capsys.readouterr().out
        assert "未提供 --yes" in out
        # 零 WSL 写调用：除 get_distro 的 -l -v 外无其它
        assert not any("apt" in " ".join(c) for c in fake_run_wsl.calls)

    def test_full_success(self, fake_run_wsl, capsys):
        install_full(fake_run_wsl)
        ret = cli.main(["ai", "install", NAME, "--yes"])
        assert ret == 0
        out = capsys.readouterr().out
        assert "安装并验收通过" in out

    def test_structural_fail_aborts(self, fake_run_wsl, capsys):
        # 默认 fake：发行版不存在
        ret = cli.main(["ai", "install", NAME, "--yes"])
        assert ret == 1
        assert not any("apt update" in " ".join(c) for c in fake_run_wsl.calls)

    def test_apt_update_network_fail(self, fake_run_wsl, capsys):
        install_os(fake_run_wsl)
        fake_run_wsl.script["apt update"] = make_result(
            ok=False, exit_code=100,
            stdout="", stderr="Temporary failure resolving 'archive.openkylin.top'\n",
        )
        ret = cli.main(["ai", "install", NAME, "--yes"])
        assert ret == 1
        assert podman.APT_NET_ERROR_LABEL in capsys.readouterr().out
        assert not any("apt install" in " ".join(c) for c in fake_run_wsl.calls)

    def test_apt_update_hash_fail(self, fake_run_wsl, capsys):
        install_os(fake_run_wsl)
        fake_run_wsl.script["apt update"] = make_result(
            ok=False, exit_code=1, stdout="", stderr="E: Hash Sum mismatch\n"
        )
        ret = cli.main(["ai", "install", NAME, "--yes"])
        assert ret == 1
        assert podman.APT_HASH_ERROR_LABEL in capsys.readouterr().out

    def test_candidate_recheck_missing(self, fake_run_wsl, capsys):
        install_os(fake_run_wsl)
        fake_run_wsl.script["apt update"] = make_result(stdout="Done\n")
        fake_run_wsl.script["apt-cache policy libkylin-ai-base-dev"] = make_result(
            stdout="libkylin-ai-base-dev:\n  Installed: (none)\n  Candidate: (none)\n"
        )
        ret = cli.main(["ai", "install", NAME, "--yes"])
        assert ret == 1
        assert not any("apt install" in " ".join(c) for c in fake_run_wsl.calls)

    def test_apt_install_fail(self, fake_run_wsl, capsys):
        install_os(fake_run_wsl)
        fake_run_wsl.script["apt update"] = make_result(stdout="Done\n")
        fake_run_wsl.script["apt-cache policy libkylin-ai-base-dev"] = make_result(
            stdout="libkylin-ai-base-dev:\n  Candidate: 2.0.0.0\n"
        )
        fake_run_wsl.script["apt install"] = make_result(
            ok=False, exit_code=100,
            stderr="E: Unable to locate package libkylin-ai-base-dev\n",
        )
        ret = cli.main(["ai", "install", NAME, "--yes"])
        assert ret == 1
        assert podman.APT_PKG_MISSING_LABEL in capsys.readouterr().out

    def test_install_uses_root_and_no_install_recommends(self, fake_run_wsl):
        install_full(fake_run_wsl)
        assert cli.main(["ai", "install", NAME, "--yes"]) == 0
        joined = "\n".join(joined_calls(fake_run_wsl))
        assert "-u root" in joined
        assert "apt install -y --no-install-recommends libkylin-ai-base-dev" in joined
        # 不触碰源/wsl.conf/默认发行版/模型/ollama
        for forb in ("sources.list", "wsl.conf", " -s ", "ollama", "model"):
            assert forb not in joined

    def test_install_tesseract_fail_reports(self, fake_run_wsl, capsys):
        install_full(fake_run_wsl, tesseract_ok=False)
        # tesseract 未命中键 → fake 默认发行版不存在 → 探针失败
        ret = cli.main(["ai", "install", NAME, "--yes"])
        assert ret == 1
        out = capsys.readouterr().out
        assert "tesseract" in out


# --------------------------- verify 场景 ---------------------------

def dpkg_output(installed_packages):
    """构造 dpkg-query -s 输出：installed_packages 中的包生成 install ok installed 块。"""
    blocks = []
    for component in ai.COMPONENTS:
        pkg = component.package
        if pkg in installed_packages:
            ver = CANDIDATES.get(pkg, "1.0")
            blocks.append(
                f"Package: {pkg}\nStatus: install ok installed\nVersion: {ver}"
            )
    return "\n\n".join(blocks)


OCR_FULL = {
    "libkylin-ai-base-dev", "libkylin-ai-base2",
    "tesseract-ocr", "tesseract-ocr-chi-sim", "tesseract-ocr-eng",
    "libkysdk-genai-nlp0",
}


def install_verify_env(fr, installed=OCR_FULL, tesseract_ok=True):
    install_os(fr)
    fr.script["dpkg-query"] = make_result(stdout=dpkg_output(installed))
    if tesseract_ok:
        fr.script["tesseract --version"] = make_result(stdout="tesseract 5.3.4\n")
        fr.script["tesseract --list-langs"] = make_result(stdout="eng\nchi_sim\n")


class TestVerify:
    def test_distro_not_exist(self, fake_run_wsl):
        assert cli.main(["ai", "verify", "ghost"]) == 1

    def test_full_pass_optional_unknown(self, fake_run_wsl, capsys):
        # 可选层（模型管理器/引擎/ollama 等）未装 → UNKNOWN 不阻断
        install_verify_env(fake_run_wsl)
        ret = cli.main(["ai", "verify", NAME])
        assert ret == 0
        out = capsys.readouterr().out
        assert "OCR 验收通过" in out
        assert "[UNKNOWN]" in out

    def test_missing_runtime_fail_hint(self, fake_run_wsl, capsys):
        installed = OCR_FULL - {"libkylin-ai-base2"}
        install_verify_env(fake_run_wsl, installed=installed)
        ret = cli.main(["ai", "verify", NAME])
        assert ret == 1
        out = capsys.readouterr().out
        assert "okw ai install" in out

    def test_missing_lang_fail(self, fake_run_wsl, capsys):
        install_verify_env(fake_run_wsl)
        fake_run_wsl.script["tesseract --list-langs"] = make_result(stdout="eng\n")
        ret = cli.main(["ai", "verify", NAME])
        assert ret == 1
        assert "chi_sim" in capsys.readouterr().out

    def test_tesseract_binary_missing_fail(self, fake_run_wsl):
        install_verify_env(fake_run_wsl, tesseract_ok=False)
        ret = cli.main(["ai", "verify", NAME])
        assert ret == 1

    def test_ollama_unknown_note(self, fake_run_wsl, capsys):
        install_verify_env(fake_run_wsl)
        cli.main(["ai", "verify", NAME])
        out = capsys.readouterr().out
        assert "ollama" in out and "curl|sh" in out


class TestSmokeOcr:
    def test_default_no_recognition(self, fake_run_wsl):
        install_verify_env(fake_run_wsl)
        assert cli.main(["ai", "verify", NAME]) == 0
        # 未冒烟：不应出现 tesseract <图片> stdout（仅 --version/--list-langs）
        assert not any("stdout -l" in " ".join(c) for c in fake_run_wsl.calls)

    def test_smoke_success(self, fake_run_wsl, capsys):
        install_verify_env(fake_run_wsl)
        image_in_distro = "/tmp/sample.png"
        fake_run_wsl.script[f"test -f {image_in_distro}"] = make_result(stdout="")
        fake_run_wsl.script[f"tesseract {image_in_distro} stdout"] = make_result(
            stdout="麒麟软件 有限公司\n"
        )
        ret = cli.main(["ai", "verify", NAME, "--smoke-ocr", image_in_distro])
        assert ret == 0
        out = capsys.readouterr().out
        assert "离线识别成功" in out
        joined = "\n".join(joined_calls(fake_run_wsl))
        assert "stdout -l chi_sim+eng" in joined

    def test_smoke_image_missing(self, fake_run_wsl, capsys):
        install_verify_env(fake_run_wsl)
        image_in_distro = "/tmp/missing.png"
        fake_run_wsl.script[f"test -f {image_in_distro}"] = make_result(
            ok=False, exit_code=1, stderr=""
        )
        ret = cli.main(["ai", "verify", NAME, "--smoke-ocr", image_in_distro])
        assert ret == 1
        assert "找不到图片" in capsys.readouterr().out

    def test_smoke_empty_result_fail(self, fake_run_wsl, capsys):
        install_verify_env(fake_run_wsl)
        image_in_distro = "/tmp/blank.png"
        fake_run_wsl.script[f"test -f {image_in_distro}"] = make_result(stdout="")
        fake_run_wsl.script[f"tesseract {image_in_distro} stdout"] = make_result(
            stdout="   \n"
        )
        ret = cli.main(["ai", "verify", NAME, "--smoke-ocr", image_in_distro])
        assert ret == 1
        assert "识别失败或结果为空" in capsys.readouterr().out

    def test_smoke_skipped_when_prior_fail(self, fake_run_wsl, capsys):
        install_verify_env(fake_run_wsl, tesseract_ok=False)
        ret = cli.main(["ai", "verify", NAME, "--smoke-ocr", "/tmp/x.png"])
        assert ret == 1
        out = capsys.readouterr().out
        assert "未执行图片识别" in out

    def test_smoke_windows_path_converts(self, fake_run_wsl, capsys):
        install_verify_env(fake_run_wsl)
        win_image = r"C:\Users\me\sample.png"
        distro_path = "/mnt/c/Users/me/sample.png"
        fake_run_wsl.script[f"test -f {distro_path}"] = make_result(stdout="")
        fake_run_wsl.script[f"tesseract {distro_path} stdout"] = make_result(
            stdout="识别文本\n"
        )
        ret = cli.main(["ai", "verify", NAME, "--smoke-ocr", win_image])
        assert ret == 0
        assert distro_path in "\n".join(joined_calls(fake_run_wsl))


# --------------------------- parse_dpkg_status ---------------------------

class TestParseDpkgShow:
    def test_installed_block(self):
        out = "Package: libkylin-ai-base2\nStatus: install ok installed\nVersion: 2.0.0.0\n"
        parsed = ai.parse_dpkg_show(out)
        assert parsed["libkylin-ai-base2"] == {"installed": True, "version": "2.0.0.0"}

    def test_not_installed_block(self):
        out = "Package: ollama\nStatus: unknown ok not-installed\n"
        parsed = ai.parse_dpkg_show(out)
        assert parsed["ollama"]["installed"] is False
        assert parsed["ollama"]["version"] == ""

    def test_garbage_block_ignored(self):
        out = (
            "noise without labels\n\n"
            "Package: x\nStatus: install ok installed\nVersion: 1\n"
        )
        parsed = ai.parse_dpkg_show(out)
        assert "noise" not in parsed
        assert parsed["x"]["installed"] is True

    def test_empty(self):
        assert ai.parse_dpkg_show("") == {}


# --------------------------- 空子组与格式化 ---------------------------

class TestCliPlumbing:
    def test_ai_no_cmd_prints_help_exit2(self, capsys):
        ret = cli.main(["ai"])
        assert ret == 2
        assert "preflight" in capsys.readouterr().out

    def test_format_functions_run(self, fake_run_wsl):
        install_full(fake_run_wsl)
        report = ai.install_run(NAME, yes=True)
        text = ai.format_install(report)
        assert "okw ai install" in text

    def test_ref_ai_stack_topic(self, capsys):
        ret = cli.main(["ref", "ai-stack"])
        assert ret == 0
        out = capsys.readouterr().out
        assert "AI 三层体系" in out
        assert "05-ai-stack.md" in out
        assert "红线" in out

    def test_ref_list_includes_ai_stack(self, capsys):
        assert cli.main(["ref"]) == 0
        out = capsys.readouterr().out
        assert "ai-stack" in out
