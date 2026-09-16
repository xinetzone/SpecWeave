"""agent-monetize 源码挂载 + 原生 tvm-ffi 链路冒烟（栈运行路径）。

运行方式（栈在运行时，compose 已注入 PYTHONPATH=/workspace/agent-monetize/src）：
  /opt/conda/bin/python /opt/agent-monetize-dev-smoke/smoke_native.py

语义：
  - 始终断言挂载点与源码包关键路径可访问（独立于 .so 是否编译——首次未
    编译是合法态，挂载失败不得被 libtvm 缺席分支掩盖）。
  - score_opportunity.so 存在：FfiBridge 加载，断言 backend=native、
    tvm_ffi_available、固定输入原生结果 == 纯 Python 参考（容差 1e-9）。
  - .so 不存在：跳过原生段并提示先 build-native，整体仍 exit 0。
"""

import math
import os
import sys
from pathlib import Path

failures: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    mark = "  [OK]" if ok else "  [FAIL]"
    print(f"{mark} {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(name)


ROOT = Path("/workspace/agent-monetize")
SRC_PKG = ROOT / "src" / "agent_monetize"
NATIVE_SO = ROOT / "native" / "build" / "score_opportunity.so"

print("== 1. 挂载点与源码包 ==")
check("agent-monetize 根挂载", ROOT.is_dir())
check("pyproject.toml 可见", (ROOT / "pyproject.toml").is_file())
check("agent_monetize 包可见", (SRC_PKG / "__init__.py").is_file())
check("ffi_bridge.py 可见", (SRC_PKG / "core" / "ffi_bridge.py").is_file())
check("score_opportunity.cc 可见", (ROOT / "native" / "score_opportunity.cc").is_file())
print("  PYTHONPATH =", os.environ.get("PYTHONPATH"))
print("  LD_LIBRARY_PATH =", os.environ.get("LD_LIBRARY_PATH"))

if not SRC_PKG.parent.is_dir():
    print(f"[FAIL] 源码 src 目录不可见，停止：{SRC_PKG.parent}")
    sys.exit(1)

print("\n== 2. 纯 Python 参考实现（不依赖 .so）==")
from agent_monetize.core.ffi_bridge import (  # noqa: E402
    FfiBridge,
    _reference_score_opportunity,
)

REF_INPUTS = (100.0, 0.8, 1.5, 20.0)
ref_value = _reference_score_opportunity(*REF_INPUTS)
print(f"  reference score{REF_INPUTS} = {ref_value:.6f}")
check("参考打分在 [0,100]", 0.0 <= ref_value <= 100.0, f"{ref_value}")

if not NATIVE_SO.is_file():
    print("\n[SKIP] score_opportunity.so 尚未编译（首次使用的合法态）")
    print("       编译后重跑本冒烟：invoke monetize.build-native && invoke monetize.smoke")
    print("       当前后端将是 reference（纯 Python 降级，功能正常）")
else:
    print(f"\n== 3. 原生 tvm-ffi backend（{NATIVE_SO}，{NATIVE_SO.stat().st_size} B）==")
    bridge = FfiBridge(fallback_to_reference=False)
    backend = bridge.initialize(native_lib_paths=[str(NATIVE_SO)])
    check("tvm_ffi_available", bridge.tvm_ffi_available)
    check("backend == native", backend == "native", f"backend={backend}, "
          f"load_error={bridge.load_error}")
    check("native_lib_path 指向挂载 .so",
          bool(bridge.native_lib_path) and Path(bridge.native_lib_path) == NATIVE_SO,
          bridge.native_lib_path or "")

    if backend == "native":
        native_value = float(bridge.score_opportunity(*REF_INPUTS))
        print(f"  native    score{REF_INPUTS} = {native_value:.9f}")
        print(f"  reference score{REF_INPUTS} = {ref_value:.9f}")
        check("原生结果在 [0,100]", 0.0 <= native_value <= 100.0, f"{native_value}")
        check("原生 == 参考（容差 1e-9）",
              math.isclose(native_value, ref_value, rel_tol=0.0, abs_tol=1e-9),
              f"diff={abs(native_value - ref_value):.3e}")

print("")
if failures:
    print(f"[FAIL] 原生/挂载冒烟未通过：{len(failures)} 项 — {failures}")
    sys.exit(1)
print("[OK] agent-monetize mounts + native smoke passed")
