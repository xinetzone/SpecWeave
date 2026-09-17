"""release/ 客户独立交付包的 daemon-free 结构守卫。

验证随包骨架（compose / 控制脚本 / env 模板）满足"完全独立、面向客户、
离线、Podman+Docker 双兼容"契约：
  - 零仓库知识：无 extends、无 ../ 路径、release/ 内零 Python；
  - 离线：pull_policy never，镜像固定 localhost/ 前缀（归档内规范名，双运行时一致）；
  - 凭证最小注入：容器 environment 仅四变量（不使用 env_file）；
  - SSH host key 持久化；
  - 双端控制脚本命令同构，凭证生成加密学安全、字符集仅字母数字；
  - 厂商打包器 relpack 的纯函数（版本解析 / WSL 路径转换）正确。
"""

import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from jpman_client import relpack

CLIENT_ROOT = Path(__file__).resolve().parents[1]
RELEASE = CLIENT_ROOT / "overlays" / "xmnn-runtime" / "release"

TRACKED = [
    "README.md", "compose.yaml", "compose.podman.yaml", ".env.example",
    "xmnnctl", "xmnnctl.ps1", "artifacts/.gitignore", "workspace/.gitkeep",
]


@pytest.fixture(scope="module")
def main_compose() -> dict:
    with (RELEASE / "compose.yaml").open(encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.mark.parametrize("rel", TRACKED)
def test_tracked_skeleton_present(rel):
    assert (RELEASE / rel).is_file(), rel


def test_release_has_no_python_files():
    pys = [p for p in RELEASE.rglob("*.py")]
    assert pys == [], f"客户目录不应包含 Python 文件：{pys}"


def test_no_repo_knowledge_in_compose(main_compose):
    text = (RELEASE / "compose.yaml").read_text(encoding="utf-8")
    # 无 YAML extends 键（结构级断言，不靠注释文本）；无父目录相对路径
    assert "extends" not in main_compose["services"]["xmnnrt"]
    assert "../" not in text


def test_main_compose_contract(main_compose):
    assert main_compose["name"] == "xmnn-runtime"
    svc = main_compose["services"]["xmnnrt"]
    # localhost/ 规范名：podman 打包时裸名归一化进入归档，docker load 原样保留；
    # 裸名在 docker 下会被解析为 docker.io/xmnn-runtime 触发远程拉取。离线禁止拉取。
    assert svc["image"] == "localhost/xmnn-runtime:${XMNN_VERSION}"
    assert svc["pull_policy"] == "never"
    assert svc["network_mode"] == "bridge"
    assert svc["ports"] == [
        "${XMNN_SSH_PORT:-2225}:22",
        "${XMNN_JUPYTER_PORT:-8893}:8888",
    ]
    # 仅凭证四变量注入容器（无 env_file）
    assert "env_file" not in svc
    assert set(svc["environment"]) == {
        "USER_PASSWORD", "JUPYTER_TOKEN", "SSH_PUBLIC_KEY", "GRANT_SUDO",
    }
    # workspace bind + SSH host key named volume
    targets = [v.split(":")[1] for v in svc["volumes"]]
    assert targets == ["/workspace", "/var/lib/jpman/ssh-host-keys"]
    assert svc["restart"] == "unless-stopped"
    assert main_compose["volumes"] == {"xmnn-ssh-host-keys": {}}


def test_podman_override_rootless_essentials():
    doc = yaml.safe_load((RELEASE / "compose.podman.yaml").read_text(encoding="utf-8"))
    svc = doc["services"]["xmnnrt"]
    assert svc["devices"] == ["/dev/fuse:/dev/fuse"]
    assert svc["security_opt"] == ["label=disable"]
    assert svc["cgroupns"] == "host"
    assert "privileged" not in svc


def test_env_template_lf_only():
    data = (RELEASE / ".env.example").read_bytes()
    assert b"\r" not in data, ".env.example 必须 LF 换行（CRLF 会污染 bash/compose）"


def test_env_example_keys():
    keys = set()
    for line in (RELEASE / ".env.example").read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#") and "=" in line:
            keys.add(line.split("=", 1)[0])
    assert keys == {
        "XMNN_VERSION", "XMNN_CONTAINER_NAME", "XMNN_SSH_PORT",
        "XMNN_JUPYTER_PORT", "USER_PASSWORD", "JUPYTER_TOKEN",
        "SSH_PUBLIC_KEY", "GRANT_SUDO",
    }


@pytest.mark.parametrize("script", ["xmnnctl", "xmnnctl.ps1"])
def test_ctl_scripts_command_parity_and_security(script):
    text = (RELEASE / script).read_text(encoding="utf-8")
    for cmd in ("init", "load", "up", "down", "ps", "logs", "smoke"):
        assert cmd in text, (script, cmd)
    # smoke 一次性容器必须显式 --entrypoint（否则默认 entrypoint 命令模式失败）
    assert "--entrypoint /opt/conda/bin/python" in text
    # 凭证字符集仅字母数字（bash 区间 / pwsh 显式字符集）
    if script == "xmnnctl":
        assert "A-Za-z0-9" in text
    else:
        assert "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789" in text


def test_scripts_defend_against_crlf_env():
    bash = (RELEASE / "xmnnctl").read_text(encoding="utf-8")
    pwsh = (RELEASE / "xmnnctl.ps1").read_text(encoding="utf-8")
    # bash 读 .env 去 CR；pwsh 写 .env 强制 LF（WriteAllText + LF join）
    assert "tr -d '\\r'" in bash
    assert 'TrimEnd("`r")' in pwsh
    assert 'WriteAllText' in pwsh and '"`n"' in pwsh


def test_release_shebang_scripts_are_lf_only():
    # shebang 在解释器启动前由内核按字节解析（'bash\r' 无法启动），
    # 脚本内 tr -d '\r' 救不了自己的 shebang——随包 POSIX 脚本必须全 LF。
    assert relpack.find_crlf_shebang_scripts(RELEASE) == []


def test_find_crlf_shebang_scripts_detects_bad_and_skips(tmp_path):
    (tmp_path / "ctl").write_bytes(b"#!/usr/bin/env bash\r\necho hi\r\n")
    (tmp_path / "ok.sh").write_bytes(b"#!/bin/sh\ntrue\n")
    # .ps1 首行虽有 shebang，但规范行尾就是 CRLF，必须跳过
    (tmp_path / "ctl.ps1").write_bytes(
        b"#!/usr/bin/env pwsh\r\nWrite-Host 1\r\n"
    )
    # artifacts/ 内为镜像归档（大二进制），即使字节偶然命中也不扫描
    art = tmp_path / "artifacts"
    art.mkdir()
    (art / "image.tar.gz").write_bytes(b"#!/bin/sh\r\njunk\r\n")

    bad = relpack.find_crlf_shebang_scripts(tmp_path)

    assert [p.name for p in bad] == ["ctl"]


def test_loaded_image_uses_localhost_canonical_name():
    # 归档由 podman save 产出：打包机 tag 时裸名已归一化，tar 内 RepoTag 固定
    # localhost/xmnn-runtime:<ver>；docker load 原样保留（podman 会在解析裸名时
    # 隐式补 localhost/，docker 不会）。双端脚本的 load 后 inspect 与一次性
    # smoke run 必须统一使用 localhost/ 全称，且不得再按运行时做条件前缀分流。
    bash = (RELEASE / "xmnnctl").read_text(encoding="utf-8")
    pwsh = (RELEASE / "xmnnctl.ps1").read_text(encoding="utf-8")
    canonical = 'localhost/xmnn-runtime:$ver'
    # 每端恰好两处：load 后 inspect 引用 + smoke 一次性容器镜像引用
    assert bash.count(canonical) == 2
    assert pwsh.count(canonical) == 2
    assert f'img_ref="{canonical}"' in bash
    assert f'$imgRef = "{canonical}"' in pwsh
    # 禁止回退为按运行时条件加前缀的分流写法
    assert '[ "$RT" = "podman" ] && img_ref=' not in bash
    assert 'if ($Script:Rt -eq "podman") { $imgRef' not in pwsh


def test_bash_uses_urandom_pwsh_uses_crypto_rng():
    bash = (RELEASE / "xmnnctl").read_text(encoding="utf-8")
    pwsh = (RELEASE / "xmnnctl.ps1").read_text(encoding="utf-8")
    assert "/dev/urandom" in bash
    assert "RandomNumberGenerator" in pwsh
    assert "Get-Random" not in pwsh


def test_compose_preflight_user_dir_fallback_parity():
    # pipx/pip --user 安装的 compose 不在 PATH 时（WSL 非登录 shell / 最小化环境），
    # 两侧预检都必须回退用户级目录并给出可操作提示，而非直接判"缺少 compose"。
    bash = (RELEASE / "xmnnctl").read_text(encoding="utf-8")
    pwsh = (RELEASE / "xmnnctl.ps1").read_text(encoding="utf-8")
    assert "find_companion" in bash and "$HOME/.local/bin" in bash
    assert "Find-UserCompanion" in pwsh and ".local\\bin" in pwsh
    assert "pip install --user podman-compose" in bash
    assert "pip install --user podman-compose" in pwsh
    assert 'export PATH=' in bash
    # 回退命中须显式告知用户（自动启用），失败信息须可操作（安装命令 + PATH 自救）
    assert "已自动启用" in bash and "已自动启用" in pwsh


# 行为测试：xmnnctl 经 stdin 喂入（末行 main 调用用 sed 剥掉），在隔离 HOME/PATH
# 下 source 后直接调用 detect_runtime，stub podman 的 compose 子命令恒失败。
# 注意：脚本必须落盘后以 `bash <file>` 调用——WSL 互操作会重组 -c 内联参数，
# 多行/$()/反斜杠会被吞（本机 wsl.exe 实测），文件路径同样要传 /mnt 原生形式。
_BASH_POSITIVE = r"""
set -u
T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT
mkdir -p "$T/home/.local/bin" "$T/shim"
printf '%s\n' '#!/usr/bin/env bash' 'if [ "$1" = compose ]; then exit 1; fi' 'exit 0' \
    > "$T/shim/podman"
printf '%s\n' '#!/usr/bin/env bash' 'echo fake-podman-compose' \
    > "$T/home/.local/bin/podman-compose"
chmod +x "$T/shim/podman" "$T/home/.local/bin/podman-compose"
sed '$d' > "$T/lib.sh"
export HOME="$T/home"
export PATH="$T/shim:/usr/local/bin:/usr/bin:/bin"
. "$T/lib.sh"
detect_runtime
printf 'RESULT_RT=%s\n' "$RT"
printf 'RESULT_COMPOSE=%s\n' "${COMPOSE[*]}"
"""

_BASH_NEGATIVE = r"""
set -u
T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT
mkdir -p "$T/home" "$T/shim"
printf '%s\n' '#!/usr/bin/env bash' 'if [ "$1" = compose ]; then exit 1; fi' 'exit 0' \
    > "$T/shim/podman"
chmod +x "$T/shim/podman"
sed '$d' > "$T/lib.sh"
export HOME="$T/home"
export PATH="$T/shim:/usr/local/bin:/usr/bin:/bin"
. "$T/lib.sh"
detect_runtime
"""

_BASH_EXE = shutil.which("bash")
# System32/WindowsApps 下的 bash.exe 是 WSL 启动器（挂载点 /mnt/<drive>）；
# Git for Windows 的 bash 直接吃 D:/... 形式。
_IS_WSL = bool(_BASH_EXE and re.search(r"system32|windowsapps", _BASH_EXE.lower()))


def _bash_native_path(p: Path) -> str:
    win = str(p)
    if _IS_WSL and re.match(r"^[A-Za-z]:[\\/]", win):
        return f"/mnt/{win[0].lower()}/" + win[3:].replace("\\", "/")
    return p.as_posix()


def _run_bash_preflight(harness: str, tmp_path: Path) -> subprocess.CompletedProcess:
    # 以字节喂 stdin：Windows 文本管道会把 \n 翻成 \r\n，bash 将报
    # `pipefail\r: invalid option`（CRLF 注入，正是本交付包的头号天敌）。
    script = (RELEASE / "xmnnctl").read_bytes()
    harness_file = tmp_path / "preflight-harness.sh"
    harness_file.write_text(harness, encoding="utf-8", newline="\n")
    proc = subprocess.run(
        ["bash", _bash_native_path(harness_file)], input=script,
        capture_output=True, timeout=60,
    )
    proc.stdout = proc.stdout.decode("utf-8", errors="replace")
    proc.stderr = proc.stderr.decode("utf-8", errors="replace")
    return proc


@pytest.mark.skipif(shutil.which("bash") is None, reason="环境无 bash，跳过预检行为测试")
def test_bash_preflight_uses_user_local_companion(tmp_path):
    proc = _run_bash_preflight(_BASH_POSITIVE, tmp_path)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    lines = {l[len("RESULT_"):].split("=", 1)[0]: l.split("=", 1)[1]
             for l in proc.stdout.splitlines() if l.startswith("RESULT_")}
    assert lines.get("RT") == "podman"
    assert lines.get("COMPOSE", "").endswith("/.local/bin/podman-compose")
    # c_warn 走 stdout（脚本约定：仅 c_err 写 stderr）
    assert "已自动启用" in proc.stdout


@pytest.mark.skipif(shutil.which("bash") is None, reason="环境无 bash，跳过预检行为测试")
def test_bash_preflight_missing_compose_is_actionable(tmp_path):
    proc = _run_bash_preflight(_BASH_NEGATIVE, tmp_path)
    assert proc.returncode == 1
    merged = proc.stdout + proc.stderr
    assert "pip install --user podman-compose" in merged
    assert ".local/bin" in merged


# ── 运行时选择暴露（--runtime / XMNN_RUNTIME / auto）─────────────────────────


@pytest.mark.parametrize("script", ["xmnnctl", "xmnnctl.ps1"])
def test_runtime_selection_exposed_with_auto(script):
    # 运行时必须可经命令行选择：podman|docker|auto 三值、默认 auto 探测，
    # 旧的"仅二值"错误文案不得残留（防止回退为 env-only 设计）。
    text = (RELEASE / script).read_text(encoding="utf-8")
    assert "podman|docker|auto" in text
    assert "只允许 podman|docker（当前" not in text
    assert "auto" in text
    # 强制指定未安装的运行时时须 fail-fast，不得静默回退到另一个运行时
    assert "未安装或不在 PATH" in text
    if script == "xmnnctl":
        assert "parse_global_args" in text
        assert "--runtime" in text
        # 优先级链：CLI --runtime > 环境变量 XMNN_RUNTIME > auto
        assert '${CLI_RUNTIME:-${XMNN_RUNTIME:-auto}}' in text
    else:
        assert "Parse-GlobalArgs" in text
        assert "--runtime" in text and "$Script:CliRuntime" in text
        assert "$env:XMNN_RUNTIME" in text and '"auto"' in text


_BASH_PARSE_ARGS = r"""
set -u
T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT
sed '$d' > "$T/lib.sh"
. "$T/lib.sh"
fail() { printf 'FAIL: %s\n' "$1"; exit 1; }
parse_global_args --runtime docker up
[ "$CLI_RUNTIME" = docker ] || fail a1
[ "${REMAIN[*]}" = "up" ] || fail a2
parse_global_args up -r podman
[ "$CLI_RUNTIME" = podman ] || fail b1
[ "${REMAIN[*]}" = "up" ] || fail b2
parse_global_args init --force
[ -z "$CLI_RUNTIME" ] || fail c1
[ "${REMAIN[*]}" = "init --force" ] || fail c2
parse_global_args --runtime=auto -rdocker up
[ "$CLI_RUNTIME" = docker ] || fail d1
[ "${REMAIN[*]}" = "up" ] || fail d2
parse_global_args -- --runtime docker
[ -z "$CLI_RUNTIME" ] || fail e1
[ "${REMAIN[*]}" = "--runtime docker" ] || fail e2
printf 'PARSE_OK\n'
"""

_BASH_PARSE_MISSING_VALUE = r"""
set -u
T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT
sed '$d' > "$T/lib.sh"
. "$T/lib.sh"
parse_global_args up --runtime
"""

_BASH_RUNTIME_CHOICE = r"""
set -u
T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT
mkdir -p "$T/home/.local/bin" "$T/shim"
printf '%s\n' '#!/usr/bin/env bash' 'if [ "$1" = compose ]; then exit 1; fi' 'exit 0' \
    > "$T/shim/podman"
printf '%s\n' '#!/usr/bin/env bash' 'echo fake-podman-compose' \
    > "$T/home/.local/bin/podman-compose"
chmod +x "$T/shim/podman" "$T/home/.local/bin/podman-compose"
sed '$d' > "$T/lib.sh"
export HOME="$T/home"
export PATH="$T/shim:/usr/local/bin:/usr/bin:/bin"
. "$T/lib.sh"
fail() { printf 'FAIL: %s\n' "$1"; exit 1; }
# CLI=auto 必须覆盖 env=docker：走探测并命中 podman shim
CLI_RUNTIME=auto XMNN_RUNTIME=docker detect_runtime || fail p1rc
[ "$RT" = podman ] || fail p1
# env=auto（无 CLI）：同样探测 podman
CLI_RUNTIME= XMNN_RUNTIME=auto detect_runtime || fail p2rc
[ "$RT" = podman ] || fail p2
# 两者皆未提供：默认即 auto
unset CLI_RUNTIME XMNN_RUNTIME
detect_runtime || fail p3rc
[ "$RT" = podman ] || fail p3
printf 'CHOICE_OK\n'
"""

_BASH_RUNTIME_BAD_CHOICE = r"""
set -u
T="$(mktemp -d)"
ORIG_PATH="$PATH"
trap 'rc=$?; PATH="$ORIG_PATH"; rm -rf "$T"; exit $rc' EXIT
mkdir -p "$T/empty"
sed '$d' > "$T/lib.sh"
unset XMNN_RUNTIME || true
. "$T/lib.sh"
export PATH="$T/empty"   # source 后再隔离：任何容器运行时都不可见
CLI_RUNTIME=__CHOICE__ detect_runtime
"""


@pytest.mark.skipif(shutil.which("bash") is None, reason="环境无 bash，跳过运行时选择行为测试")
def test_bash_parse_global_args_matrix(tmp_path):
    proc = _run_bash_preflight(_BASH_PARSE_ARGS, tmp_path)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "PARSE_OK" in proc.stdout, proc.stdout + proc.stderr


@pytest.mark.skipif(shutil.which("bash") is None, reason="环境无 bash，跳过运行时选择行为测试")
def test_bash_runtime_flag_without_value_fails_fast(tmp_path):
    proc = _run_bash_preflight(_BASH_PARSE_MISSING_VALUE, tmp_path)
    assert proc.returncode == 1
    assert "需要参数" in proc.stdout + proc.stderr


@pytest.mark.skipif(shutil.which("bash") is None, reason="环境无 bash，跳过运行时选择行为测试")
def test_bash_runtime_choice_priority_and_auto(tmp_path):
    proc = _run_bash_preflight(_BASH_RUNTIME_CHOICE, tmp_path)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "CHOICE_OK" in proc.stdout, proc.stdout + proc.stderr


@pytest.mark.skipif(shutil.which("bash") is None, reason="环境无 bash，跳过运行时选择行为测试")
@pytest.mark.parametrize(
    "choice,expected",
    [
        ("docker", "未安装或不在 PATH"),
        ("podman", "未安装或不在 PATH"),
        ("lxc", "只允许 podman|docker|auto"),
        ("", "未找到 podman 或 docker"),
    ],
)
def test_bash_runtime_bad_choice_fails_fast(tmp_path, choice, expected):
    harness = _BASH_RUNTIME_BAD_CHOICE.replace(
        "CLI_RUNTIME=__CHOICE__", f"CLI_RUNTIME={choice}")
    proc = _run_bash_preflight(harness, tmp_path)
    assert proc.returncode == 1
    assert expected in proc.stdout + proc.stderr


_PWSH_PARSE_HARNESS = r"""
. "__LIB__"
function Check($cond, $msg) { if (-not $cond) { Write-Host "FAIL: $msg"; exit 1 } }
Parse-GlobalArgs @("--runtime", "docker", "up")
Check ($Script:CliRuntime -eq "docker") "a1"
Check (($Script:Remain -join ",") -eq "up") "a2"
Parse-GlobalArgs @("up", "-r", "podman")
Check ($Script:CliRuntime -eq "podman") "b1"
Check (($Script:Remain -join ",") -eq "up") "b2"
Parse-GlobalArgs @("init", "--force")
Check ($Script:CliRuntime -eq "") "c1"
Check (($Script:Remain -join "|") -eq "init|--force") "c2"
Parse-GlobalArgs @("-Runtime=auto", "-rdocker", "up")
Check ($Script:CliRuntime -eq "docker") "d1"
Check (($Script:Remain -join ",") -eq "up") "d2"
Parse-GlobalArgs @("--", "--runtime", "docker")
Check ($Script:CliRuntime -eq "") "e1"
Check (($Script:Remain -join "|") -eq "--runtime|docker") "e2"
Write-Host "PS_PARSE_OK"
"""

_PWSH_PARSE_MISSING_VALUE = r"""
. "__LIB__"
Parse-GlobalArgs @("up", "--runtime")
"""


def _run_pwsh_lib_harness(body: str, tmp_path: Path) -> subprocess.CompletedProcess:
    # 剥掉入口分发段后 dot-source：仅装载函数与 $Script: 状态，不触发命令分发。
    src = (RELEASE / "xmnnctl.ps1").read_text(encoding="utf-8")
    head = src.split("# ── 入口分发", 1)[0]
    lib = tmp_path / "xmnnctl-lib.ps1"
    lib.write_text(head, encoding="utf-8", newline="\n")
    harness = tmp_path / "harness.ps1"
    harness.write_text(body.replace("__LIB__", str(lib)), encoding="utf-8", newline="\n")
    proc = subprocess.run(
        ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(harness)],
        capture_output=True, timeout=60,
    )
    proc.stdout = proc.stdout.decode("utf-8", errors="replace")
    proc.stderr = proc.stderr.decode("utf-8", errors="replace")
    return proc


@pytest.mark.skipif(shutil.which("pwsh") is None, reason="环境无 pwsh，跳过 ps1 参数解析行为测试")
def test_pwsh_parse_global_args_matrix(tmp_path):
    proc = _run_pwsh_lib_harness(_PWSH_PARSE_HARNESS, tmp_path)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "PS_PARSE_OK" in proc.stdout, proc.stdout + proc.stderr


@pytest.mark.skipif(shutil.which("pwsh") is None, reason="环境无 pwsh，跳过 ps1 参数解析行为测试")
def test_pwsh_runtime_flag_without_value_fails_fast(tmp_path):
    proc = _run_pwsh_lib_harness(_PWSH_PARSE_MISSING_VALUE, tmp_path)
    assert proc.returncode == 1
    assert "需要参数" in proc.stdout + proc.stderr


def test_artifacts_gitignore_keeps_itself():
    text = (RELEASE / "artifacts" / ".gitignore").read_text(encoding="utf-8")
    assert "*" in text and "!.gitignore" in text


# ── relpack 纯函数 ──────────────────────────────────────────────────────────


def test_resolve_wheel_from_fake_dir(tmp_path):
    whl = tmp_path / "xmnn-9.9.9-cp314-cp314-linux_x86_64.whl"
    whl.write_bytes(b"x")
    info = relpack.resolve_wheel(tmp_path)
    assert info.version == "9.9.9"
    assert info.file == whl.name
    assert info.size_bytes == 1


def test_resolve_wheel_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        relpack.resolve_wheel(tmp_path)


def test_to_wsl_path():
    assert relpack.to_wsl_path(Path("D:/a/b")) == "/mnt/d/a/b"
