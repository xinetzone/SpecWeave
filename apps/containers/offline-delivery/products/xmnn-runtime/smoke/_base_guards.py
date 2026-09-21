#!/usr/bin/env python3
"""xmnn-runtime 底座镜像守卫（构建期 root + devuser 双跑 / 镜像内可复跑）。

底座 != 载荷（2026-09-21 起）：
  - 底座镜像（localhost/xmnn-runtime:base-<形态>）只承载 cp314 GIL base env +
    torch + 载荷 wheel 声明的无条件运行时依赖（/opt/xmnnrt-smoke/deps.txt）+
    ipykernel + 内核注册；
  - 底座**绝不**安装 xmnn wheel：载荷由交付侧派生时装入
    （release/payload/Dockerfile，`pip install --no-index --no-deps`），随即由
    随底座保留的载荷守卫 _runtime_smoke.py 验证；
  - 故本守卫的两条主线是：正向断言依赖面齐全（§2/§3）+ 反向断言载荷未混入（§6）。
    少了反向断言，"底座里混进 whl" 这类错版只会在交付侧派生时以「依赖被
    --no-deps 掩盖」的形式静默通过，故必须在此硬失败。

检查项（任一 FAIL 最终 exit 1，镜像构建失败）：
  1. 双 ABI 解释器：base env /opt/conda = cp314 GIL（enabled）；
     main env /opt/conda/envs/main = cp314t free-threading（GIL disabled）
  2. deps.txt 每条 Requirement 的发行版已在 base env 安装
  3. /opt/conda/bin/python -m pip check 无**新**冲突（基镜像既有债务
     conda↔ruamel-yaml 按逐行模式放行，见 _ALLOWED_PREEXISTING_CONFLICT）
  4. torch 形态与实物一致（marker vs version.cuda）
  5. "Python 3.14 (xmnn runtime)" 内核已注册且 root/devuser 双可见
  6. 反断言：载荷未安装——两个 env 的 `import xmnn` 必须失败，且 site-packages
     内无 xmnn / xmnn-*.dist-info / xmnn_bootstrap.pth 残留
"""

import json
import os
import re
import subprocess
import sys

PASS = 0
FAIL = 0

_BASE_PYTHON = "/opt/conda/bin/python"
_MAIN_PYTHON = "/opt/conda/envs/main/bin/python"
_MAIN_JUPYTER = "/opt/conda/envs/main/bin/jupyter"
_KERNEL_JSON = "/opt/conda/envs/main/share/jupyter/kernels/xmnn-runtime/kernel.json"
_KERNEL_NAME = "xmnn-runtime"
_KERNEL_DISPLAY = "Python 3.14 (xmnn runtime)"
# 形态标记由 scripts/install-torch.sh 写入（C26）；守卫读 marker 而非 LABEL
# （镜像内运行时读不到 LABEL），据此断言「声明形态 == 实物」。
_TORCH_FLAVOR_MARKER = "/opt/xmnnrt-torch-flavor"
# 与 Containerfile ARG TORCH_VERSION 对齐（仅校验主版本一致，补丁号以实物为准）
_EXPECTED_TORCH_MAJOR = "2."
# 底座依赖清单：Layer 2 安装后留在镜像内（供本守卫核验与镜像内溯源）。
# 可用环境变量覆盖，便于对任意清单复跑。
_DEPS_FILE = os.environ.get("XMNNRT_DEPS_FILE", "/opt/xmnnrt-smoke/deps.txt")
# 载荷痕迹前缀：site-packages 内以此开头的条目都算残留
# （xmnn 包目录 / xmnn-*.dist-info / xmnn_bootstrap.pth）。
_PAYLOAD_PREFIX = "xmnn"

# 基镜像自带、且底座层无法消除的既有依赖冲突（**已知债务放行**，不是关闭检查）：
# 基镜像里 conda 26.7.2 的元数据声明 ruamel-yaml<0.19，实测装的却是 0.19.1
# （ruamel.yaml 由基镜像经 pip 为 podman-compose 装入，降级会伤及 compose 能力，
# 故底座层不得「顺手修」；修法在基镜像侧，不属本产品）。该冲突与 deps.txt 无关
# 且改版前就已存在：2026-09-21 实测 localhost/jupyter-podman-rootless:latest 与
# localhost/xmnn-runtime:1.2.1.dev0 的 pip check 输出同一行。
# 放行规则刻意收窄到「owner=conda 且 dep=ruamel-yaml」这一族，其余冲突行照旧
# 硬失败——本项仍能拦住 deps.txt/载荷引入的新冲突。
_ALLOWED_PREEXISTING_CONFLICT = re.compile(r"^conda \S+ has requirement ruamel-yaml\b")

# 子进程 + `-S -c` 探测解释器事实：`-S` 跳过 site 导入，隔离 .pth 注入
# （载荷 bootstrap 会改 sys.path，必须在不加载它的前提下取 ABI 事实），
# `-c` 保证不落地临时文件——与 _runtime_smoke.py 的 ABI 断言手法一致。
_ABI_PROBE = (
    "import json, sys, sysconfig;"
    "print(json.dumps({"
    "'exe': sys.executable,"
    "'version': sys.version.split()[0],"
    "'gil_disabled': sysconfig.get_config_var('Py_GIL_DISABLED'),"
    "'gil_enabled': sys._is_gil_enabled() if hasattr(sys, '_is_gil_enabled') else None,"
    "'prefix': sys.prefix,"
    "'purelib': sysconfig.get_paths()['purelib']}))"
)

# `-I` 隔离（忽略 PYTHONPATH / 用户 site），仍正常导入 site，故能读到
# base env 的 dist-info——用于核验 deps.txt，与守卫自身运行身份无关。
_VERSIONS_PROBE = "\n".join(
    [
        "import importlib.metadata as md",
        "import json, sys",
        "out = {}",
        "for name in json.load(sys.stdin):",
        "    try:",
        "        out[name] = md.version(name)",
        "    except md.PackageNotFoundError:",
        "        out[name] = None",
        "print(json.dumps(out))",
    ]
)


def check(name: str, fn) -> None:
    global PASS, FAIL
    print(f"─── Test: {name}")
    try:
        fn()
    except Exception as exc:  # noqa: BLE001 - 守卫需要逐项跑完并汇总
        print(f"  [FAIL] {type(exc).__name__}: {exc}")
        FAIL += 1
    else:
        print("  [OK]")
        PASS += 1
    print("")


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def _probe(python: str) -> dict:
    """子进程探测解释器事实（不导入 site，避免载荷 .pth 干扰）。"""
    out = subprocess.run(
        [python, "-S", "-c", _ABI_PROBE],
        capture_output=True,
        text=True,
        timeout=60,
    )
    _assert(
        out.returncode == 0,
        f"解释器探测失败 {python}: {out.stderr.strip()}",
    )
    return json.loads(out.stdout.strip().splitlines()[-1])


def _whoami() -> str:
    try:
        import pwd

        return pwd.getpwuid(os.geteuid()).pw_name
    except Exception:  # noqa: BLE001 - 仅用于日志标签
        return str(os.geteuid())


def _requirement_name(line: str) -> str:
    """取 Requirement 文本的发行版名（处理 >=/==/[extra] 等写法）。

    名称必为行首连续匹配 `[A-Za-z0-9._-]` 的片段，其后紧跟版本区间、extras
    或 marker 分隔符；故 `numpy>=1.26` → `numpy`、`Pillow>=10.0` → `Pillow`、
    `typing_extensions>=4.8` → `typing_extensions`、`foo[extra]>=1.0` → `foo`、
    `foo == 1.0` → `foo`。
    """
    match = re.match(r"[A-Za-z0-9][A-Za-z0-9._-]*", line.strip())
    _assert(match is not None, f"无法从清单行解析依赖名: {line!r}")
    return match.group(0)


def _read_deps() -> list:
    """读 deps.txt，返回去重后的发行版名清单（保持文件顺序）。"""
    _assert(os.path.isfile(_DEPS_FILE), f"底座依赖清单缺失: {_DEPS_FILE}")
    names = []
    seen = set()
    with open(_DEPS_FILE, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            name = _requirement_name(line)
            key = name.lower().replace("_", "-").replace(".", "-")
            if key in seen:
                continue
            seen.add(key)
            names.append(name)
    _assert(bool(names), f"底座依赖清单为空: {_DEPS_FILE}")
    return names


def test_dual_abi() -> None:
    """§1 双 ABI 契约：base = cp314 GIL；main = cp314t（free-threading）。"""
    base = _probe(_BASE_PYTHON)
    print(f"  base: {base['exe']} -> Python {base['version']}, prefix={base['prefix']}")
    print(
        f"  base: Py_GIL_DISABLED={base['gil_disabled']}, "
        f"_is_gil_enabled()={base['gil_enabled']}"
    )
    _assert(base["prefix"] == "/opt/conda", f"base env 前缀异常: {base['prefix']}")
    _assert(base["version"].startswith("3.14"), f"base env 必须是 Python 3.14: {base['version']}")
    _assert(
        base["gil_disabled"] in (0, None),
        "base env 必须是 cp314 GIL ABI（载荷 wheel tag 为 cp314-cp314，load 目标即此 env）",
    )
    _assert(base["gil_enabled"] is True, "base env 是 cp314 GIL 解释器，应报告 GIL enabled")

    main = _probe(_MAIN_PYTHON)
    print(f"  main: {main['exe']} -> Python {main['version']}, prefix={main['prefix']}")
    print(
        f"  main: Py_GIL_DISABLED={main['gil_disabled']}, "
        f"_is_gil_enabled()={main['gil_enabled']}"
    )
    _assert(
        main["prefix"] == "/opt/conda/envs/main",
        f"main env 前缀异常: {main['prefix']}",
    )
    _assert(main["version"].startswith("3.14"), f"main env 必须是 Python 3.14: {main['version']}")
    _assert(
        main["gil_disabled"] == 1,
        "main env 必须是 cp314t free-threading（基底契约，底座层不得改动）",
    )
    _assert(main["gil_enabled"] is False, "main env 应报告 GIL disabled")


def test_deps_installed() -> None:
    """§2 deps.txt 逐条核验：wheel 声明的无条件运行时依赖必须全部已装。"""
    names = _read_deps()
    print(f"  manifest {_DEPS_FILE}: {len(names)} requirements")
    out = subprocess.run(
        [_BASE_PYTHON, "-I", "-c", _VERSIONS_PROBE],
        input=json.dumps(names),
        capture_output=True,
        text=True,
        timeout=120,
    )
    _assert(out.returncode == 0, f"依赖版本查询失败: {out.stderr.strip()}")
    versions = json.loads(out.stdout.strip().splitlines()[-1])

    missing = []
    for name in names:
        version = versions.get(name)
        print(f"  {'[OK]  ' if version else '[MISS]'} {name} -> {version or '<not installed>'}")
        if not version:
            missing.append(name)
    _assert(not missing, f"deps.txt 中未安装的发行版（底座依赖面不完整）: {missing}")


def test_pip_check() -> None:
    """§3 依赖区间自洽：除基镜像既有债务外，pip check 不得报告冲突。"""
    out = subprocess.run(
        [_BASE_PYTHON, "-m", "pip", "check"],
        capture_output=True,
        text=True,
        timeout=300,
    )
    lines = [line.strip() for line in out.stdout.splitlines() if line.strip()]
    allowed = [line for line in lines if _ALLOWED_PREEXISTING_CONFLICT.match(line)]
    blocking = [line for line in lines if not _ALLOWED_PREEXISTING_CONFLICT.match(line)]
    print(f"  pip check exit={out.returncode}, {len(lines)} line(s)")
    for line in allowed:
        print(f"  [INFO] 已知基镜像债务（放行）: {line}")
    for line in blocking:
        print(f"  [CONFLICT] {line}")
    if not lines:
        print("  no broken requirements found")
    _assert(
        out.returncode == 0 or bool(lines),
        f"pip check 非零退出且无诊断输出 ({out.returncode}): {out.stderr.strip()}",
    )
    _assert(
        not blocking,
        f"pip check 报告新冲突（非基镜像既有债务）: {blocking}",
    )


def test_torch_flavor_build() -> None:
    """§4 形态契约（C26）：marker 声明什么形态，实物就必须是什么形态。

    判据是**声明 vs 实物**的一致性：marker（install-torch.sh 写入）↔
    version.cuda。写死 CPU 断言会让 `--torch cu130` 在守卫处误报失败；
    只断言「能 import」又会放过「声明 cpu 却装了 CUDA 包」的错版。
    """
    flavor = "<missing>"
    try:
        with open(_TORCH_FLAVOR_MARKER, encoding="utf-8") as fh:
            flavor = fh.read().strip()
    except OSError:
        pass
    print(f"  marker {_TORCH_FLAVOR_MARKER} = {flavor!r}")
    _assert(
        flavor in ("", "cpu", "cu130"),
        f"torch 形态标记异常（应存在且 ∈ ''|cpu|cu130）: {flavor!r}",
    )

    if flavor == "":
        try:
            import torch  # noqa: F401
        except ImportError:
            print("  形态 ''（不装 torch）：镜像内无 torch")
            return
        raise AssertionError("形态声明为 ''（不装 torch），但镜像内可 import torch")

    import torch

    version = torch.__version__
    print(f"  torch.__version__ = {version}")
    print(f"  torch.version.cuda = {torch.version.cuda}")
    _assert(version.startswith(_EXPECTED_TORCH_MAJOR), f"torch 主版本异常: {version}")
    if flavor == "cu130":
        _assert(
            torch.version.cuda is not None,
            f"cu130 形态必须是 CUDA 构建，实际 torch.version.cuda={torch.version.cuda}",
        )
        print(f"  CUDA build OK (cuda {torch.version.cuda})")
    else:
        _assert(
            torch.version.cuda is None,
            f"cpu 形态必须是 CPU 构建（torch.version.cuda 应为 None），实际 {torch.version.cuda}",
        )
        _assert(torch.cuda.is_available() is False, "CPU 镜像不应报告 CUDA 可用")
        print("  CPU build OK")


def _kernelspec_list(cmd: list, label: str) -> None:
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    _assert(
        out.returncode == 0,
        f"{label} 的 jupyter kernelspec list 失败: {out.stderr.strip()}",
    )
    _assert(
        _KERNEL_NAME in out.stdout,
        f"{label} 看不到 {_KERNEL_NAME} 内核:\n{out.stdout}",
    )
    print(f"  visible to {label}")


def test_kernel_registered() -> None:
    """§5 内核：spec 合法 + 当前身份可见（root 轮再验 devuser 可见性）。"""
    _assert(os.path.isfile(_KERNEL_JSON), f"内核 spec 缺失: {_KERNEL_JSON}")
    with open(_KERNEL_JSON, encoding="utf-8") as fh:
        spec = json.loads(fh.read())
    argv = spec.get("argv", [])
    _assert(argv and argv[0] == _BASE_PYTHON, f"内核 argv 必须指向 {_BASE_PYTHON}: {argv}")
    _assert(
        spec.get("display_name") == _KERNEL_DISPLAY,
        f"内核 display_name 异常（期望 {_KERNEL_DISPLAY!r}）: {spec.get('display_name')!r}",
    )
    env = spec.get("env", {})
    _assert("PYTHONPATH" not in env, "底座内核不得注入源码 PYTHONPATH")
    _assert("TVM_LIBRARY_PATH" not in env, "底座内核不得注入 TVM_LIBRARY_PATH")
    print(f"  kernel.json argv={argv}, display={spec.get('display_name')}")

    me = _whoami()
    _kernelspec_list([_MAIN_JUPYTER, "kernelspec", "list"], f"当前身份 {me}")
    if os.geteuid() == 0:
        _kernelspec_list(
            ["su", "-s", "/bin/bash", "devuser", "-c", f"{_MAIN_JUPYTER} kernelspec list"],
            "devuser",
        )
    else:
        print("  [INFO] 当前非 root：跳过 su devuser 可见性检查（构建期 root 轮已覆盖该维度）")


def test_payload_absent() -> None:
    """§6 反断言（关键）：底座内不得有任何载荷（xmnn wheel）痕迹。

    两个 env 各查一次：`import xmnn` 必须以 ModuleNotFoundError 失败，且该 env
    的 site-packages 内不得出现 xmnn 目录 / xmnn-*.dist-info / xmnn_bootstrap.pth。
    载荷由交付侧派生安装（--no-index --no-deps）；底座若混入载荷，会绕过依赖
    解析并让「底座可复用」的定位失效。
    """
    for label, python in (("base", _BASE_PYTHON), ("main", _MAIN_PYTHON)):
        purelib = _probe(python)["purelib"]
        leftover = sorted(
            entry for entry in os.listdir(purelib) if entry.lower().startswith(_PAYLOAD_PREFIX)
        )
        print(f"  [{label}] {purelib} xmnn* entries: {leftover}")
        _assert(
            not leftover,
            f"[{label}] site-packages 残留载荷痕迹（应为纯底座）: {leftover}",
        )

        out = subprocess.run(
            [python, "-I", "-P", "-c", "import xmnn"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        detail = out.stderr.strip().splitlines()[-1] if out.stderr.strip() else "<no stderr>"
        print(f"  [{label}] python -I -P -c 'import xmnn' -> exit {out.returncode}: {detail}")
        _assert(
            out.returncode != 0,
            f"[{label}] 载荷 xmnn 已混入底座镜像（import 成功，应为未安装状态）",
        )
        _assert(
            "ModuleNotFoundError" in out.stderr,
            f"[{label}] import xmnn 失败但非 ModuleNotFoundError: {out.stderr.strip()}",
        )


def main() -> int:
    print("==========================================")
    print("  XMNN Runtime BASE Guards (no payload)")
    print("==========================================")
    print(f"Python: {sys.version.split()[0]} @ {sys.executable}")
    print(f"USER  : {_whoami()} (euid={os.geteuid()})")
    print(f"deps  : {_DEPS_FILE}")
    print("")

    check("1. dual ABI (base cp314 GIL / main cp314t)", test_dual_abi)
    check("2. deps.txt requirements installed", test_deps_installed)
    check("3. pip check (no new conflicts beyond base-image debt)", test_pip_check)
    check("4. torch flavor matches artifact (marker vs version.cuda)", test_torch_flavor_build)
    check("5. xmnn-runtime jupyter kernel", test_kernel_registered)
    check("6. payload NOT installed (import xmnn must fail)", test_payload_absent)

    print("==========================================")
    print(f"  SUMMARY: {PASS} passed, {FAIL} failed")
    print("==========================================")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())