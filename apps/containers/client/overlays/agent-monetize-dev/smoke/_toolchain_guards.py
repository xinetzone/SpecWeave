"""agent-monetize-dev 叠加层工具链守卫（构建期 + podman run --rm 双路径）。

运行方式（固定 base env cp314 GIL 解释器，apache-tvm-ffi wheel 仅 cp314 GIL）：
  /opt/conda/bin/python /opt/agent-monetize-dev-smoke/_toolchain_guards.py

守卫集合：
  1. base 解释器 cp314 GIL enabled（Py_GIL_DISABLED=0 且 _is_gil_enabled）
  2. clang++ / patchelf / gdb 可执行（apt 层，走 PATH 不写死 /usr/bin）
  3. tvm_ffi 可 import、libtvm_ffi.so 与 tvm_ffi.h 就位
  4. /opt/monetize-builder 打包脚本资产齐全
任何断言失败即非零退出（构建期 RUN 失败、run --rm 冒烟失败）。
"""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import sysconfig
from pathlib import Path

MAIN_PYTHON = Path("/opt/conda/envs/main/bin/python")
SITE_PACKAGES = Path(sysconfig.get_paths()["purelib"])
TVM_FFI_INC = SITE_PACKAGES / "tvm_ffi" / "include"
TVM_FFI_LIB = SITE_PACKAGES / "tvm_ffi" / "lib"
BUILDER_DIR = Path("/opt/monetize-builder")

failures: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    mark = "  [OK]" if ok else "  [FAIL]"
    print(f"{mark} {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(name)


def run_version(binary: str, *args: str) -> str:
    try:
        proc = subprocess.run(
            [binary, *args], capture_output=True, text=True, timeout=30,
        )
        return (proc.stdout or proc.stderr).strip().splitlines()[0]
    except Exception as exc:  # noqa: BLE001
        return f"error: {exc}"


print("== 1. base 解释器 GIL ABI（apache-tvm-ffi wheel 为 cp314 GIL）==")
gil_disabled = sysconfig.get_config_var("Py_GIL_DISABLED")
check("base python: cp314 GIL enabled",
      gil_disabled == 0 and sys._is_gil_enabled() is True,
      f"Py_GIL_DISABLED={gil_disabled}, _is_gil_enabled={sys._is_gil_enabled()}")

# main env cp314t 存在性记录（不要求 tvm_ffi；Jupyter 服务由它跑）
if MAIN_PYTHON.exists():
    code = (
        "import sys,sysconfig;"
        "print(sys.version.split()[0], sysconfig.get_config_var('Py_GIL_DISABLED'))"
    )
    proc = subprocess.run(
        [str(MAIN_PYTHON), "-S", "-c", code],
        capture_output=True, text=True, timeout=30,
    )
    print(f"  (main cp314t 存在，仅记录: {proc.stdout.strip()})")

print("\n== 2. apt clang 原生工具链（走 PATH，不写死目录）==")
for tool in ("clang++", "patchelf", "gdb"):
    resolved = shutil.which(tool)
    first = run_version(resolved, "--version") if resolved else ""
    check(f"{tool} 可执行", bool(resolved), first)

print("\n== 3. apache-tvm-ffi（import + libtvm_ffi.so + tvm_ffi.h）==")
tvm_spec = importlib.util.find_spec("tvm_ffi")
check("tvm_ffi 可导入", tvm_spec is not None)
if tvm_spec:
    import tvm_ffi  # noqa: F401
    check("libtvm_ffi.so 就位",
          (TVM_FFI_LIB / "libtvm_ffi.so").is_file(),
          str(TVM_FFI_LIB / "libtvm_ffi.so"))
    check("tvm_ffi.h 头文件就位",
          (TVM_FFI_INC / "tvm" / "ffi" / "tvm_ffi.h").is_file(),
          str(TVM_FFI_INC / "tvm" / "ffi" / "tvm_ffi.h"))
    tvm_core = list((SITE_PACKAGES / "tvm_ffi").glob("core.cpython-*.so"))
    check("tvm_ffi Python 绑定 core.*.so 存在", bool(tvm_core),
          tvm_core[0].name if tvm_core else "")

print("\n== 4. /opt/monetize-builder 打包资产 ==")
required_assets = [
    "scripts/build-native.sh",
    "scripts/build-wheel.sh",
    "scripts/lib/logging.sh",
]
for rel in required_assets:
    check(f"monetize-builder/{rel}", (BUILDER_DIR / rel).is_file())

print("\n== 5. devuser 可读性由 Containerfile 同脚本 su 复跑保证 ==")

print("")
if failures:
    print(f"[FAIL] 工具链守卫未通过：{len(failures)} 项 — {failures}")
    sys.exit(1)
print("[OK] agent-monetize toolchain guards all passed (cp314 GIL + clang + tvm-ffi)")
