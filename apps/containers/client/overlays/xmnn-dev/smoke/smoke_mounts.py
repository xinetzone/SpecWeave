"""xmnn-dev 运行期冒烟：源码挂载可见性 + tvm/vta/xmnn 源码调试链路。

运行方式（栈在运行时）：
  podman-compose exec -T xmnn /opt/conda/bin/python /opt/xmnn-dev-smoke/smoke_mounts.py
  invoke xmnn.smoke

语义：
  - 始终断言三个 bind 挂载点与关键子目录可访问；
  - /workspace/npu_tvm/build/libtvm.so 不存在（首次未编译）时跳过 import
    段并以退出码 0 通过——未编译是合法的首次状态，给出 build-tvm 提示；
  - libtvm.so 存在时导入 tvm/vta/xmnn，断言模块来自 /workspace 挂载源码
    （而非 site-packages），并跑 tvm.build('llvm') 固定向量加。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

TVM_ROOT = Path("/workspace/npu_tvm")
XMN_ROOT = Path("/workspace/npuusertools")
MODELS_ROOT = Path("/workspace/models")

failures: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    mark = "  [OK]" if ok else "  [FAIL]"
    print(f"{mark} {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(name)


print("== 1. 挂载点与关键子目录 ==")
check("npu_tvm 根挂载", TVM_ROOT.is_dir())
check("npu_tvm/python/tvm 包", (TVM_ROOT / "python" / "tvm" / "__init__.py").is_file())
check("npu_tvm/vta/python/vta 包", (TVM_ROOT / "vta" / "python" / "vta" / "__init__.py").is_file())
check("npuusertools 根挂载", XMN_ROOT.is_dir())
check("npuusertools/xmnn 包", (XMN_ROOT / "xmnn" / "__init__.py").is_file())
check("models 挂载", MODELS_ROOT.is_dir())

print("\n  PYTHONPATH =", os.environ.get("PYTHONPATH", "<unset>"))
print("  TVM_LIBRARY_PATH =", os.environ.get("TVM_LIBRARY_PATH", "<unset>"))

libtvm = TVM_ROOT / "build" / "libtvm.so"

if not libtvm.is_file():
    print("\n[SKIP] libtvm.so 尚未构建（", libtvm, "）")
    print("       首次环境的合法状态。编译 TVM：inv xmnn.build-tvm")
    print("       随后打包 wheel：inv xmnn.wheel")
    if failures:
        print(f"\n[FAIL] 挂载点断言 {len(failures)} 项未通过：{failures}")
        sys.exit(1)
    print("\n[OK] 挂载点全部可见；import/算例段因 libtvm.so 缺席跳过")
    sys.exit(0)

print("\n== 2. tvm/vta/xmnn 来自挂载源码（非 site-packages）==")
import tvm  # noqa: E402
import vta  # noqa: E402
import xmnn  # noqa: E402

print("  tvm :", tvm.__file__)
print("  vta :", vta.__file__)
print("  xmnn:", xmnn.__file__)
check("tvm 来自 /workspace/npu_tvm", str(tvm.__file__).startswith(str(TVM_ROOT / "python")), str(tvm.__file__))
check("vta 来自 /workspace/npu_tvm", str(vta.__file__).startswith(str(TVM_ROOT / "vta")), str(vta.__file__))
check("xmnn 来自 /workspace/npuusertools", str(xmnn.__file__).startswith(str(XMN_ROOT)), str(xmnn.__file__))

print("\n== 3. tvm.build('llvm') 固定向量加（n=4, A*2 == B）==")
import numpy as np  # noqa: E402
from tvm import te  # noqa: E402

n = 4
A = te.placeholder((n,), name="A", dtype="float32")
B = te.compute((n,), lambda i: A[i] * 2.0, name="B")
s = te.create_schedule(B.op)
f = tvm.build(s, [A, B], "llvm", name="vec_double")
a_np = np.arange(n, dtype="float32") + 1.0
a = tvm.nd.array(a_np, tvm.cpu(0))
b = tvm.nd.array(np.zeros(n, dtype="float32"), tvm.cpu(0))
f(a, b)
got = b.asnumpy().tolist()
print("  A =", a_np.tolist(), " B =", got)
check("向量加结果 [2.0, 4.0, 6.0, 8.0]", got == [2.0, 4.0, 6.0, 8.0], str(got))

print("")
if failures:
    print(f"[FAIL] {len(failures)} 项未通过：{failures}")
    sys.exit(1)
print("[OK] xmnn source mounts + imports + tvm.build smoke passed")
