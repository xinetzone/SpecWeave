"""`bin/relpack`（bash）与 `bin/relpack.ps1`（pwsh7）的不变量守卫（静态为主，
含 smoke 步骤契约的真实 bash 行为用例）。

daemon-free：不调用 podman、不触容器守护进程；只读文件、跑 `bash -n`（有
bash 或可用 WSL 发行版时）与 pwsh 参数解析（有 pwsh 时）。覆盖：
  - 自包含约束：`bin/` 内零 `jpman` / `invoke ` / `pip install` / `client/` /
    `overlays/_shared` 引用（本应用禁依赖 client 与 shared）；
  - 命令面与选项面齐全（`version|stage|build|pack|smoke` + `--help`；
    pwsh 侧同名子命令与 `-Product/-Version/-Wheel/-Torch/-BaseImage/-PipMirror/-NoCache`）；
  - 关键机制静态存在：`podman save`、`gzip -t`、原子 `mv`、CRLF shebang 守卫
    （且在导出归档**之前**）、torch 标签双键回退、形态白名单 `cpu|cu130`、
    `product.env` 必需键校验；
  - 产品常量唯一性：`product.env` 是唯一来源，CLI 内不得内嵌产品字面量
    （仅允许 `--product` 默认值声明处出现默认产品名）；
  - smoke 步骤调用契约：`run_smoke_step` / `smoke_hint` 实现在 `bin/lib/pipeline.sh`，
    调用点不得把骨架目录混进命令参数（曾致 `... release: Is a directory` / exit 126）；
    另有真实 bash 行为用例验证「命令被真实执行 + 第一参数 + 工作目录」。
"""

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

# product.env 必需键（与 bin/lib/common.sh::load_product_env 的校验清单一致）
REQUIRED_ENV_KEYS = {
    "PRODUCT", "IMAGE_NAME", "CONTAINERFILE", "WHEEL_GLOB", "WHEEL_PREFIX",
    "WHEEL_DIST", "BASE_IMAGE_DEFAULT", "TORCH_DEFAULT", "RELEASE_DIR",
}

# 自包含约束：这些字面量在 bin/ 内必须零命中（CLI 零 Python、零 client/shared 依赖）
FORBIDDEN_IN_BIN = ["jpman", "invoke ", "pip install", "client/", "overlays/_shared"]

COMMANDS = ["version", "stage", "build", "pack", "smoke"]

# WSL 发行版优先级（与 bin/relpack.ps1::Get-WslDistro 一致）
_WSL_DISTRO_ENV = ("OFFLINE_DELIVERY_WSL_DISTRO", "XMNN_WSL_DISTRO", "COMPOSE_WSL_DISTRO")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _cluster(bin_dir: Path) -> dict:
    """bin/ 下全部 CLI 源文件 → {"relpack"/"lib/x.sh": 文本}（POSIX 形式键）。"""
    files = [bin_dir / "relpack", bin_dir / "relpack.ps1", *sorted((bin_dir / "lib").glob("*.sh"))]
    return {p.relative_to(bin_dir).as_posix(): _read(p) for p in files}


# ── 语法检查：`bash -n`（无 bash / 无可用 WSL 发行版时跳过）──────────────────


def _posix(path: Path, wsl_style: bool) -> str:
    """Windows 盘符路径 → `bash` 可识别的形式（WSL 启动器需 /mnt/<盘> 形式）。"""
    text = str(path)
    if wsl_style and re.match(r"^[A-Za-z]:[\\/]", text):
        return f"/mnt/{text[0].lower()}/" + text[3:].replace("\\", "/")
    return path.as_posix()


def _bash_n_runner():
    """返回 (argv 前缀, 是否需 /mnt 路径)；无 bash 且无 wsl.exe 时返回 None。

    Windows 原生通常无 POSIX bash；System32/WindowsApps 下的 `bash.exe` 是 WSL
    启动器（挂载点 /mnt/<drive>），而 Git for Windows 的 bash 直接吃 D:/… 形式。
    两者皆不可用时退化为 `wsl.exe -d <发行版> -- bash`。
    """
    exe = shutil.which("bash")
    if exe:
        return [exe], bool(re.search(r"system32|windowsapps", exe.lower()))
    wsl = shutil.which("wsl")
    if wsl:
        distro = next((os.environ[k] for k in _WSL_DISTRO_ENV if os.environ.get(k)),
                      "podman-machine-default")
        return [wsl, "-d", distro, "--", "bash"], True
    return None


@pytest.fixture(scope="module")
def bash_prefix():
    """返回 (argv 前缀, 是否需 /mnt 路径)；无 bash 且无 wsl.exe / bash 不可用时 skip。"""
    runner = _bash_n_runner()
    if runner is None:
        pytest.skip("环境无 bash 且无 wsl.exe，跳过 bash 相关用例")
    prefix, wsl_style = runner
    probe = subprocess.run([*prefix, "-c", "exit 0"], capture_output=True, timeout=120)
    if probe.returncode != 0:
        detail = (probe.stdout + probe.stderr).decode("utf-8", errors="replace").strip()
        pytest.skip(f"bash 不可用（{' '.join(prefix)}）：{detail[:200]}")
    return prefix, wsl_style


@pytest.fixture(scope="module")
def bash_n(bash_prefix):
    """返回 `run(path) -> CompletedProcess` 的 `bash -n` 调用器。"""
    prefix, wsl_style = bash_prefix

    def run(path: Path) -> subprocess.CompletedProcess:
        return subprocess.run([*prefix, "-n", _posix(path, wsl_style)],
                              capture_output=True, timeout=120)

    return run


def test_bash_scripts_are_syntactically_valid(bin_dir, bash_n):
    """`bash -n` 通过：bin/relpack 与 bin/lib/*.sh（只解析，不执行）。"""
    files = [bin_dir / "relpack", *sorted((bin_dir / "lib").glob("*.sh"))]
    assert [p.name for p in files] == ["relpack", "common.sh", "log.sh", "pipeline.sh"]
    for f in files:
        proc = bash_n(f)
        out = (proc.stdout + proc.stderr).decode("utf-8", errors="replace").strip()
        assert proc.returncode == 0, f"bash -n {f.name} 失败：{out}"


def test_cli_scripts_are_lf_with_shebang(bin_dir):
    # 无扩展名的 shebang 脚本一旦被 CRLF 检出，Linux/WSL 首行即报
    # `'/usr/bin/env: bash\r'`；.ps1 的规范行尾本就是 CRLF，不在判据内。
    for name in ["relpack", "lib/log.sh", "lib/common.sh", "lib/pipeline.sh"]:
        data = (bin_dir / name).read_bytes()
        assert b"\r" not in data, f"{name} 必须 LF 换行（CRLF shebang 无法启动）"
    assert (bin_dir / "relpack").read_bytes().startswith(b"#!/usr/bin/env bash\n")


# ── 自包含约束（零 Python / 禁依赖 client 与 shared）────────────────────────


def test_bin_has_no_foreign_references(bin_dir):
    for name, text in _cluster(bin_dir).items():
        for needle in FORBIDDEN_IN_BIN:
            assert needle not in text, f"{name} 不应出现 {needle!r}（自包含约束）"


# ── 命令面 / 选项面 ────────────────────────────────────────────────────────


def test_bash_command_and_option_surface(bin_dir):
    text = _read(bin_dir / "relpack")
    # 命令分发：version|stage|build|pack|smoke 一次性匹配
    assert re.search(r"(?m)^\s*version\|stage\|build\|pack\|smoke\)", text)
    for cmd in COMMANDS:
        assert cmd in text, cmd
    # 帮助入口
    assert "-h|--help|help)" in text and "usage()" in text
    # 选项面
    assert "-p|--product)" in text
    for opt in ("--wheel", "--version", "--torch", "--base-image", "--pip-mirror", "--no-cache"):
        assert opt in text, opt
    # 产品名默认值与 product.env 查找路径
    assert re.search(r'(?m)^PRODUCT_DEFAULT="[^"]+"', text)
    common = _read(bin_dir / "lib" / "common.sh")
    assert "%s/products/%s" in common and "$dir/product.env" in common


def test_pwsh_command_and_option_surface(bin_dir):
    text = _read(bin_dir / "relpack.ps1")
    # 与 bash 版同名子命令
    assert re.search(r"\$Commands\s*=\s*@\(([^)]*)\)", text)
    for cmd in COMMANDS:
        assert f"'{cmd}'" in text, cmd
    # 选项键与 Windows 原生参数名
    for key in ("'p'", "'product'", "'version'", "'wheel'", "'torch'",
                "'base-image'", "'pip-mirror'", "'no-cache'"):
        assert key in text, key
    for flag in ("-Product", "-Version", "-Wheel", "-Torch", "-BaseImage", "-PipMirror", "-NoCache"):
        assert flag in text, flag
    # 容器命令统一经 wsl.exe 桥接 bash 版（不做逻辑分叉）
    assert "wsl.exe" in text and "bridgeArgs" in text


def test_command_option_matrix_parity(bin_dir):
    """两端「命令 × 允许选项」矩阵同构（各自解析源内声明后逐项对比）。"""
    expected = {
        "version": [],
        "stage": ["wheel"],
        "build": ["wheel", "torch", "base-image", "pip-mirror", "no-cache"],
        "pack": ["version"],
        "smoke": ["version"],
    }
    bash = _read(bin_dir / "relpack")
    # bash：命令分发处的 allow_opts "<允许的选项名>"
    bash_map = {
        cmd: (opts.split() if opts else [])
        for cmd, opts in re.findall(r'(?m)^\s*(\w+)\)\s*allow_opts "([^"]*)"', bash)
    }
    pwsh = _read(bin_dir / "relpack.ps1")
    # pwsh：$Allow 哈希表的 <命令> = @('选项', ...)
    allow_block = pwsh.split("$Allow = @{", 1)[1].split("}", 1)[0]
    pwsh_map = {
        cmd: re.findall(r"'([^']+)'", opts)
        for cmd, opts in re.findall(r"(\w+)\s*=\s*(@\([^)]*\))", allow_block)
    }
    assert bash_map == expected, bash_map
    assert pwsh_map == expected, pwsh_map


# ── 关键机制静态存在 ───────────────────────────────────────────────────────


def test_archive_export_mechanisms(bin_dir):
    text = _read(bin_dir / "relpack")
    # 形态感知双 tag（形态 + :latest 别名）
    assert '-t "$IMAGE_NAME:$FLAVOR" -t "$IMAGE_NAME:latest"' in text
    # 导出链：podman save → gzip -1 → gzip -t 校验 → 原子 mv
    assert 'podman save "$IMAGE_NAME:$ver" | gzip -1 > "$tmp"' in text
    assert 'gzip -t "$tmp"' in text
    assert 'mv -f "$tmp" "$artifacts/$archive"' in text
    # 归档名与临时文件同目录同版本（只可能留下临时文件，绝不留下截断归档）
    assert 'archive="${IMAGE_NAME##*/}-$ver.tar.gz"' in text
    assert 'tmp="$artifacts/.tmp-$ver.tar.gz"' in text
    # 归档与清单的 sha256 / 字节数取自校验后的最终文件
    assert 'sha256sum "$artifacts/$archive"' in text
    assert "write_release_manifest" in _read(bin_dir / "lib" / "pipeline.sh")


def test_crlf_guard_runs_before_archive_export(bin_dir):
    pack = _read(bin_dir / "relpack")
    pipeline = _read(bin_dir / "lib" / "pipeline.sh")
    # 守卫实现：扫 shebang 脚本、排除 artifacts/ 与 Windows 原生脚本，给出唯一修法
    assert "guard_crlf_shebang() {" in pipeline
    assert "$RELEASE_DIR/artifacts/*" in pipeline
    assert "! -name '*.ps1'" in pipeline
    assert "git add --renormalize ." in pipeline
    # pack 内守卫必须先于导出归档（绝不先打包再报错）
    body = pack.split("cmd_pack() {", 1)[1].split("\n}", 1)[0]
    assert body.index("guard_crlf_shebang") < body.index("podman save")


def test_delivery_version_and_flavor_rules(bin_dir, product_env):
    text = _read(bin_dir / "relpack")
    # 形态白名单与 pip 镜像源白名单
    assert 'FLAVORS="cpu|cu130"' in text
    assert 'MIRRORS="official|tuna|aliyun"' in text
    assert 'check_enum "$FLAVOR" "$FLAVORS"' in text
    # 覆盖优先级：CLI 旗标 > 环境变量 > product.env 默认值
    assert "${OPT_TORCH:-${TORCH_FLAVOR:-$TORCH_DEFAULT}}" in text
    assert "${OPT_BASE:-${BASE_IMAGE:-$BASE_IMAGE_DEFAULT}}" in text
    assert "${OPT_MIRROR:-${PIP_MIRROR:-official}}" in text
    assert "TORCH_DEFAULT" in product_env and "BASE_IMAGE_DEFAULT" in product_env
    assert product_env["TORCH_DEFAULT"] in text.split('FLAVORS="', 1)[1].split('"', 1)[0].split("|")
    # 交付版本：默认取暂存 wheel 版本，`--version` 可显式覆盖
    assert 'ver="${OPT_VERSION:-$wheel_ver}"' in text


def test_torch_label_dual_key_fallback(bin_dir):
    text = _read(bin_dir / "relpack")
    # 新键优先、缺失回退旧键；两者皆缺记 null 并告警（不得臆测）
    assert text.index("org.specweave.torch-version") < text.index("org.specweave.torch-cpu")
    assert '"org.specweave.torch-version"' in text
    assert '"org.specweave.torch-cpu"' in text
    assert 'torch_json="null"' in text and "镜像缺 torch LABEL" in text


def test_product_env_keys_are_validated(bin_dir, product_env):
    common = _read(bin_dir / "lib" / "common.sh")
    assert "load_product_env() {" in common
    # 必需键校验清单与 product.env 实际键一致（缺键即 die）
    declared = set(re.findall(r"\b([A-Z][A-Z0-9_]+)\b", common.split("for key in", 1)[1].split("; do", 1)[0]))
    assert declared == REQUIRED_ENV_KEYS, declared
    assert 'die "product.env 缺少必需键 $key' in common
    # 目录名与 PRODUCT 一致性校验
    assert '[ "$PRODUCT" != "$name" ]' in common
    assert REQUIRED_ENV_KEYS <= set(product_env), sorted(REQUIRED_ENV_KEYS - set(product_env))


# ── 产品常量唯一性（product.env 是唯一事实源）───────────────────────────────


def test_no_product_literals_in_cli(bin_dir, product_env):
    """`bin/` 内不得内嵌产品字面量：默认产品名只允许出现在默认值声明处，
    其余出现（帮助文案）必须在注释行内。"""
    product = product_env["PRODUCT"]
    for name, text in _cluster(bin_dir).items():
        # 镜像名（含 localhost/ 前缀）绝不允许内嵌
        assert f"localhost/{product}" not in text, name
        for line in text.splitlines():
            if product not in line:
                continue
            allowed = line.lstrip().startswith("#") or re.match(
                r'^\s*[A-Z_]+\s*=\s*"' + re.escape(product) + r'"', line)
            assert allowed, f"{name}: 产品字面量出现在非默认值/注释位置：{line.strip()}"
        # 去掉默认产品名后，不得残留产品前缀（如 WHEEL_PREFIX 的 xmnn-）
        residual = text.replace(product, "")
        assert "xmnn-" not in residual, f"{name}: 残留产品前缀 {residual.count('xmnn-')} 处"


def test_product_diff_comes_from_product_env(bin_dir, product_env):
    """产品差异项一律经变量从 product.env 读取（CLI 内零内嵌字面量）。"""
    cluster = _cluster(bin_dir)
    combined = "\n".join(cluster.values())
    for var in ("$PRODUCT", "$IMAGE_NAME", "$CONTAINERFILE", "$WHEEL_GLOB",
                "$WHEEL_PREFIX", "$WHEEL_DIST", "$BASE_IMAGE_DEFAULT",
                "$TORCH_DEFAULT", "$RELEASE_DIR", "$RELEASE_NAME"):
        assert var in combined, var
    # bash 入口：以 PRODUCT_DEFAULT 作 `--product` 默认值，随后 load_product_env 覆盖
    assert 'PRODUCT="$PRODUCT_DEFAULT"' in cluster["relpack"]
    assert "load_product_env \"$PRODUCT\"" in cluster["relpack"]
    # pipeline.sh 消费的具体产品项
    pipeline = cluster["lib/pipeline.sh"]
    for var in ("$WHEEL_PREFIX", "$WHEEL_GLOB", "$WHEEL_STAGE", "$DIST_DIR", "$PRODUCT"):
        assert var in pipeline, var
    # pwsh 版只做桥接（不复制任何产品差异项，故不含上述变量）
    assert "$WHEEL_GLOB" not in cluster["relpack.ps1"]
    assert product_env["WHEEL_GLOB"] == f"{product_env['WHEEL_PREFIX']}*.whl"


def test_product_env_matches_disk_layout(product_dir, product_env):
    assert product_env["PRODUCT"] == product_dir.name
    assert (product_dir / product_env["CONTAINERFILE"]).is_file()
    assert (product_dir / product_env["RELEASE_DIR"]).is_dir()
    assert product_env["IMAGE_NAME"].startswith("localhost/")
    assert product_env["TORCH_DEFAULT"] in ("cpu", "cu130")
    assert product_env["WHEEL_DIST"].startswith("../")


# ── smoke 步骤调用契约（回归守卫：目录不得混进命令参数）──────────────────────
#
# 缺陷复盘：`run_smoke_step` 的签名是「$1=步骤名，其余=骨架内命令」，实现内
# `shift` 掉步骤名后 `(cd "$RELEASE_DIR" && "$@")`；三个调用点却多传了一个
# `"$RELEASE_DIR"`，于是子 shell 去执行**目录本身**，smoke 第一步即
# `... /products/<产品>/release: Is a directory`（exit 126）。故机制实现移入
# `bin/lib/pipeline.sh` 复用，调用点一律只传「步骤名 + 骨架内命令」。


def test_smoke_step_calls_pass_command_only(bin_dir):
    """静态：调用点不得把骨架目录混进 `run_smoke_step` 的命令参数列表。"""
    relpack = _read(bin_dir / "relpack")
    pipeline = _read(bin_dir / "lib" / "pipeline.sh")
    # 实现已移入共享片段，CLI 内不再重复定义（避免两处签名漂移）
    assert "run_smoke_step() {" in pipeline
    assert "smoke_hint() {" in pipeline
    assert "run_smoke_step() {" not in relpack
    assert "smoke_hint() {" not in relpack
    # 骨架目录只作为公共变量（`cmd_smoke` 与 trap 收尾仍在用）
    assert "(cd \"$RELEASE_DIR\" && \"$@\")" in pipeline
    assert 'trap smoke_final_down EXIT' in relpack
    # 三个调用点：`run_smoke_step <步骤名> ./xmnnctl <步骤名>`
    calls = re.findall(r"(?m)^\s*run_smoke_step\s+(.+?)\s*$", relpack)
    assert len(calls) == 3, calls
    for call in calls:
        assert '"$RELEASE_DIR"' not in call, f"目录被当作命令传入：{call}"
        assert re.fullmatch(r"(up|smoke|down) \./xmnnctl \1 \|\| rc=\$\?", call), call


# 行为用例：在真实 bash（Windows 优先 WSL 启动器）内 source `bin/lib/pipeline.sh`，
# 构造临时骨架目录（假 xmnnctl 把自己的 cwd / argc / argv 写进骨架内 record.txt），
# 断言命令被真实执行且签名正确。骨架目录由 mktemp 建在 bash 自己的文件系统内，
# 避免 Windows drvfs 上的执行位不确定；harness 以**文件**路径交给 bash（不经
# `-c` 传多行脚本，规避 wsl.exe 的命令行重组风险）。

_SMOKE_STEP_PREAMBLE = r'''
set -u
. "__LOG__"
. "__PIPELINE__"
SB="$(mktemp -d)"
cat > "$SB/xmnnctl" <<'SH'
#!/usr/bin/env bash
{
  printf 'RECORD_CWD=%s\n' "$PWD"
  printf 'RECORD_ARGC=%s\n' "$#"
  i=0
  for a in "$@"; do
    i=$((i + 1))
    printf 'RECORD_ARG%s=%s\n' "$i" "$a"
  done
} > record.txt
exit 0
SH
chmod +x "$SB/xmnnctl"
printf 'SKELETON=%s\n' "$SB"
'''

_SMOKE_STEP_OK = _SMOKE_STEP_PREAMBLE + r'''
RELEASE_DIR="$SB"
run_smoke_step up ./xmnnctl up
printf 'SMOKE_RC=%s\n' "$?"
cat "$SB/record.txt" 2>/dev/null || printf 'RECORD_MISSING=1\n'
'''

# 命令不存在时：必须是「命令找不到」（127），不得退化为执行目录（126 / Is a directory）
_SMOKE_STEP_MISSING_CMD = _SMOKE_STEP_PREAMBLE + r'''
RELEASE_DIR="$SB"
run_smoke_step up ./no-such-cmd up
printf 'SMOKE_RC=%s\n' "$?"
'''


def _run_bash_script(bash_prefix, tmp_path: Path, script: str, name: str) -> subprocess.CompletedProcess:
    prefix, wsl_style = bash_prefix
    harness = tmp_path / name
    harness.write_text(script, encoding="utf-8", newline="\n")
    proc = subprocess.run([*prefix, _posix(harness, wsl_style)], capture_output=True, timeout=300)
    proc.stdout = proc.stdout.decode("utf-8", errors="replace")
    proc.stderr = proc.stderr.decode("utf-8", errors="replace")
    return proc


def _field(text: str, key: str) -> str:
    m = re.search(rf"(?m)^{re.escape(key)}=(.*)$", text)
    return m.group(1).strip() if m else ""


def test_run_smoke_step_invokes_skeleton_command(bin_dir, bash_prefix, tmp_path):
    """行为：`run_smoke_step up ./xmnnctl up` → 假 xmnnctl 被调用、第一参数为 up、
    工作目录为骨架目录，且 info 文案保持「【up】./xmnnctl up」。"""
    prefix, wsl_style = bash_prefix
    script = (_SMOKE_STEP_OK
              .replace("__LOG__", _posix(bin_dir / "lib" / "log.sh", wsl_style))
              .replace("__PIPELINE__", _posix(bin_dir / "lib" / "pipeline.sh", wsl_style)))
    proc = _run_bash_script(bash_prefix, tmp_path, script, "smoke_step_ok.sh")
    out = proc.stdout + proc.stderr
    assert _field(proc.stdout, "SMOKE_RC") == "0", out
    assert "【up】./xmnnctl up" in proc.stdout, out
    assert "RECORD_MISSING" not in proc.stdout, f"假 xmnnctl 未被调用：{out}"
    skeleton = _field(proc.stdout, "SKELETON")
    assert skeleton, out
    assert _field(proc.stdout, "RECORD_CWD") == skeleton, f"工作目录应为骨架目录：{out}"
    assert _field(proc.stdout, "RECORD_ARGC") == "1", out
    assert _field(proc.stdout, "RECORD_ARG1") == "up", out
    assert "Is a directory" not in out, out


def test_run_smoke_step_missing_command_fails_clean(bin_dir, bash_prefix, tmp_path):
    """行为：骨架内命令不存在 → 非零退出（127），且不出现「Is a directory」
    这一「目录被当命令执行」的缺陷签名。"""
    prefix, wsl_style = bash_prefix
    script = (_SMOKE_STEP_MISSING_CMD
              .replace("__LOG__", _posix(bin_dir / "lib" / "log.sh", wsl_style))
              .replace("__PIPELINE__", _posix(bin_dir / "lib" / "pipeline.sh", wsl_style)))
    proc = _run_bash_script(bash_prefix, tmp_path, script, "smoke_step_missing.sh")
    out = proc.stdout + proc.stderr
    assert _field(proc.stdout, "SMOKE_RC") == "127", out
    assert "Is a directory" not in out, out
    assert "no-such-cmd" in proc.stderr, out