"""xmnn-dev 叠加层工具链守卫（构建期 + podman run --rm 双路径，不依赖源码挂载）。

运行方式：/opt/conda/bin/python /opt/xmnn-dev-smoke/_toolchain_guards.py

守卫集合：
  1. 双 ABI：脚本自身解释器（base env）必须为 cp314 GIL enabled；
     main env 必须为 cp314t free-threading 且 GIL disabled（conda 装工具链
     时 pin python=*=*cp314t，若被求解互换此处立即失败）；
  2. main env 工具链：llvm-config 22.1.x、clang、cmake>=3.18、ninja、
     ccache、patchelf、gdb 均可执行；
  3. base env 打包栈：nuitka==4.1.3、scikit-build-core、build、invoke；
  4. /opt/xmnn-builder 打包资产齐全；
  5. LLVM 依赖库 7 个 glob 在 llvm-config --libdir 全部可命中并打印实际
     SONAME（SONAME 漂移的构建期硬拦截，对应 CMakeLists 的 glob 收集）。

任何断言失败即以非零退出（构建期 RUN 失败、run --rm 冒烟失败）。
"""

import glob
import os
import shutil
import subprocess
import sys
import sysconfig
from pathlib import Path

MAIN_PREFIX = Path("/opt/conda/envs/main")
MAIN_PYTHON = MAIN_PREFIX / "bin" / "python"
BUILDER_DIR = Path("/opt/xmnn-builder")

failures: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    mark = "  [OK]" if ok else "  [FAIL]"
    print(f"{mark} {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(name)


def run_version(binary: str, *args: str) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            [binary, *args], capture_output=True, text=True, timeout=30
        )
        return proc.returncode, (proc.stdout or proc.stderr).strip()
    except (OSError, subprocess.SubprocessError) as exc:
        return 127, str(exc)


print("== 1. 双 ABI 断言 ==")
gil_disabled = sysconfig.get_config_var("Py_GIL_DISABLED")
gil_enabled = sys._is_gil_enabled()  # type: ignore[attr-defined]
print(f"  base python: {sys.version.split()[0]} {sysconfig.get_config_var('SOABI')}")
print(f"  Py_GIL_DISABLED={gil_disabled}, _is_gil_enabled()={gil_enabled}")
check("base env 为 cp314 GIL enabled", gil_disabled == 0 and gil_enabled is True)

# main env ABI 经子进程断言（列表参数，不经 shell，规避 OCI 引号问题）
main_code = (
    "import sys, sysconfig; "
    "assert sysconfig.get_config_var('Py_GIL_DISABLED') == 1; "
    "assert sys._is_gil_enabled() is False; "
    "print(sys.version.split()[0], sysconfig.get_config_var('SOABI'))"
)
main_proc = subprocess.run(
    [str(MAIN_PYTHON), "-S", "-c", main_code],
    capture_output=True, text=True, timeout=30,
)
print(f"  main python: {main_proc.stdout.strip() or main_proc.stderr.strip()}")
check("main env 为 cp314t GIL disabled", main_proc.returncode == 0)

print("\n== 2. main env 原生工具链（conda）+ 系统工具（apt） ==")
rc, out = run_version(str(MAIN_PREFIX / "bin" / "llvm-config"), "--version")
llvm_ver = out.splitlines()[0] if out else ""
check("llvm-config 22.1.x", rc == 0 and llvm_ver.startswith("22.1"), llvm_ver)

rc, out = run_version(str(MAIN_PREFIX / "bin" / "clang"), "--version")
clang_ver = out.splitlines()[0] if out else ""
check("clang 可执行", rc == 0 and "clang" in clang_ver, clang_ver)

rc, out = run_version(str(MAIN_PREFIX / "bin" / "cmake"), "--version")
cmake_ver = out.splitlines()[0].replace("cmake version ", "") if out else ""
try:
    cmake_tuple = tuple(int(x) for x in cmake_ver.split(".")[:2])
except ValueError:
    cmake_tuple = (0, 0)
check("cmake >= 3.18", rc == 0 and cmake_tuple >= (3, 18), cmake_ver)

# ninja/ccache 由 conda 装入 main/bin；patchelf/gdb 由 apt 装入 /usr/bin
# （一律走 PATH 解析，不写死目录；rootless 系统 PATH 两段都覆盖）
for tool in ("ninja", "ccache", "patchelf", "gdb"):
    resolved = shutil.which(tool)
    rc, out = run_version(resolved, "--version") if resolved else (127, "")
    first = out.splitlines()[0] if out else ""
    check(f"{tool} 可执行 ({resolved or 'NOT FOUND'})", rc == 0 and bool(first), first[:80])

print("\n== 3. base env 打包栈 ==")
# Nuitka 不在包对象上暴露 __version__，以 `python -m nuitka --version` 为准
rc, out = run_version(sys.executable, "-m", "nuitka", "--version")
nuitka_ver = out.splitlines()[0] if out else ""
check("nuitka 4.1.3", rc == 0 and "4.1.3" in nuitka_ver, nuitka_ver[:80])

# scikit-build-core 1.x 顶层包名为 scikit_build_core（0.x 时代为 skbuild）
for mod, label in (
    ("scikit_build_core", "scikit-build-core"),
    ("build", "build"),
    ("invoke", "invoke"),
):
    try:
        m = __import__(mod)
        check(f"{label} 可导入", True, getattr(m, "__version__", "ok"))
    except Exception as exc:  # noqa: BLE001
        check(f"{label} 可导入", False, str(exc))

print("\n== 4. /opt/xmnn-builder 打包资产 ==")
required_assets = [
    "pyproject.toml",
    "CMakeLists.txt",
    "_xmnn_bootstrap.py",
    "xmnn_bootstrap.pth",
    "scripts/build-wheel.sh",
    "scripts/build-tvm.sh",
    "scripts/verify-wheel.sh",
    "scripts/lib/logging.sh",
]
for rel in required_assets:
    check(f"xmn-builder/{rel}", (BUILDER_DIR / rel).is_file())

print("\n== 5. LLVM 依赖库 SONAME 实测（llvm-config --libdir）==")
rc, libdir = run_version(str(MAIN_PREFIX / "bin" / "llvm-config"), "--libdir")
libdir = libdir.strip()
check("llvm-config --libdir 可用", rc == 0 and os.path.isdir(libdir), libdir)

# 与 CMakeLists.txt install_llvm_deps 的 7 个 glob 一一对应
llvm_globs = {
    "LLVM runtime": "libLLVM.so.22*",
    "zlib": "libz.so.*",
    "zstd": "libzstd.so.*",
    "libxml2": "libxml2.so.*",
    "iconv": "libiconv.so.*",
    "ICU uc": "libicuuc.so.*",
    "ICU data": "libicudata.so.*",
}
if os.path.isdir(libdir):
    for label, pattern in llvm_globs.items():
        hits = sorted(
            p for p in glob.glob(os.path.join(libdir, pattern))
            if os.path.isfile(p)
        )
        names = [os.path.basename(p) for p in hits]
        check(f"LLVM 依赖 {label} ({pattern})", bool(hits), ", ".join(names[:4]))

print("\n== 6. devuser 可读性（由 Containerfile 以 su 复跑整个脚本间接保证）==")
print("  本脚本路径 /opt/xmnn-dev-smoke/_toolchain_guards.py，chmod a+rX 烤入")

print("")
if failures:
    print(f"[FAIL] {len(failures)} 项守卫未通过：{failures}")
    sys.exit(1)
print("[OK] xmnn-dev toolchain guards all passed "
      "(dual ABI + LLVM 22.1 toolchain + nuitka 4.1.3 + builder assets + SONAME)")
