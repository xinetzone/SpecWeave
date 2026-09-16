#!/usr/bin/env python3
"""xmnn-runtime 镜像守卫（构建期 root+devuser 双跑 / 栈运行时 smoke）。

与 xmnn-dev 的验证差异（消费侧语义）：
  - 本脚本直接用 base env 解释器导入 site-packages 中的 wheel（不是临时
    venv、不是 --no-deps），等价于真实客户机 `pip install xmnn-*.whl`
    后的首次启动；
  - 镜像内不存在 /workspace 源码树与 PYTHONPATH/TVM_LIBRARY_PATH（compose
    不注入），任何对 /workspace 或 /opt/xmnn-builder 的路径命中都意味着
    wheel 自包含性被破坏，必须失败；
  - tvm.build('llvm') 依赖的 libtvm.so / libLLVM 全部来自 wheel 的
    _libs/（patchelf RPATH=$ORIGIN），镜像不安装 LLVM 工具链。

检查项（任一 FAIL 最终 exit 1，镜像构建失败）：
  1. 解释器 ABI：/opt/conda/bin/python + cp314 GIL enabled
  2. import tvm / vta / xmnn，且 __file__ 落在 site-packages
  3. _libs 目录含 libtvm.so 与 libLLVM*
  4. 干净环境 ctypes RTLD_GLOBAL 加载 libtvm.so
  5. tvm.build('llvm') 向量乘 2 数值断言
  6. relay/std/prelude.rly 数据存在
  7. xmnn_bootstrap.pth 在 site-packages
  8. xmnn 数据三目录（autolibs/tools_cpp/fonts）
  9. xmnn-runtime Jupyter 内核已注册且 argv 指向 base python
 10. torch 为内置 CPU 构建（version.cuda is None，TorchScript/jit 可用）
"""
from __future__ import annotations

import ctypes
import json
import os
import subprocess
import sys
import sysconfig

PASS = 0
FAIL = 0

# 开发/构建路径黑名单：交付镜像中 wheel 模块绝不允许来自这些位置。
_FORBIDDEN_PREFIXES = ("/workspace/", "/opt/xmnn-builder")
_BASE_PYTHON = "/opt/conda/bin/python"
_MAIN_JUPYTER = "/opt/conda/envs/main/bin/jupyter"
_KERNEL_JSON = "/opt/conda/envs/main/share/jupyter/kernels/xmnn-runtime/kernel.json"
# 与 Containerfile ARG TORCH_VERSION 对齐（仅校验主版本一致，补丁号以镜像实际为准）
_EXPECTED_TORCH_MAJOR = "2."


def check(name: str, fn) -> None:
    global PASS, FAIL
    print(f"─── Test: {name}")
    try:
        fn()
    except Exception as exc:  # noqa: BLE001 - 守卫需要逐项跑完并汇总
        print(f"  FAIL: {type(exc).__name__}: {exc}")
        FAIL += 1
    else:
        print("  PASS")
        PASS += 1
    print("")


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def test_interpreter_abi() -> None:
    print(f"  sys.executable = {sys.executable}")
    print(f"  sys.version    = {sys.version.split()[0]}")
    _assert(sys.executable == _BASE_PYTHON, f"解释器必须是 {_BASE_PYTHON}")
    gil_disabled = sysconfig.get_config_var("Py_GIL_DISABLED")
    print(f"  Py_GIL_DISABLED = {gil_disabled}")
    _assert(gil_disabled in (0, None), "wheel 是 cp314 GIL ABI，不能运行在 free-threaded 解释器")
    if hasattr(sys, "_is_gil_enabled"):
        _assert(sys._is_gil_enabled() is True, "cp314 GIL 解释器应报告 GIL enabled")


def test_imports_from_site_packages() -> None:
    import tvm
    import vta
    import xmnn

    for mod in (tvm, vta, xmnn):
        path = os.path.abspath(mod.__file__)
        print(f"  {mod.__name__} -> {path}")
        _assert("site-packages" in path, f"{mod.__name__} 不来自 site-packages: {path}")
        for bad in _FORBIDDEN_PREFIXES:
            _assert(not path.startswith(bad), f"{mod.__name__} 命中开发路径 {bad}: {path}")


def test_libs_directory() -> None:
    import tvm

    libs_dir = os.path.normpath(os.path.join(os.path.dirname(tvm.__file__), "../_libs"))
    print(f"  _libs dir = {libs_dir}")
    _assert(os.path.isdir(libs_dir), "_libs 目录缺失")
    files = sorted(os.listdir(libs_dir))
    _assert(any(f == "libtvm.so" for f in files), "libtvm.so 缺失")
    llvm_libs = [f for f in files if "libLLVM" in f]
    _assert(bool(llvm_libs), f"libLLVM 缺失（实际条目：{files}）")
    print(f"  entries={len(files)}, libLLVM={llvm_libs}")


def test_ctypes_load_libtvm() -> None:
    import tvm

    libs_dir = os.path.normpath(os.path.join(os.path.dirname(tvm.__file__), "../_libs"))
    libtvm = os.path.join(libs_dir, "libtvm.so")
    print(f"  loading {libtvm} (RTLD_GLOBAL, 无 LD_LIBRARY_PATH 依赖)")
    ctypes.CDLL(libtvm, mode=ctypes.RTLD_GLOBAL)


def test_tvm_build_llvm() -> None:
    import numpy as np
    import tvm
    from tvm import te

    n = 1024
    A = te.placeholder((n,), name="A", dtype="float32")
    B = te.compute((n,), lambda i: A[i] * 2.0, name="B")
    s = te.create_schedule(B.op)
    f = tvm.build(s, [A, B], "llvm", name="vec_double")
    print(f"  tvm.build ok, entry={f.entry_name}")
    ctx = tvm.cpu(0)
    a = tvm.nd.array(np.random.uniform(size=n).astype("float32"), ctx)
    b = tvm.nd.array(np.zeros(n, dtype="float32"), ctx)
    f(a, b)
    np.testing.assert_allclose(b.asnumpy(), a.asnumpy() * 2.0, rtol=1e-5)
    print("  compute verified: A[i] * 2 == B[i]")


def test_relay_std_data() -> None:
    import tvm

    std_dir = os.path.join(os.path.dirname(tvm.__file__), "relay", "std")
    _assert(os.path.isdir(std_dir), f"relay/std 缺失: {std_dir}")
    files = os.listdir(std_dir)
    _assert("prelude.rly" in files, f"prelude.rly 缺失: {files}")
    print("  relay/std/prelude.rly present")


def test_bootstrap_pth() -> None:
    import site

    candidates = [os.path.join(sp, "xmnn_bootstrap.pth") for sp in site.getsitepackages()]
    found = [p for p in candidates if os.path.exists(p)]
    _assert(found, f"xmnn_bootstrap.pth 未找到（候选：{candidates}）")
    print(f"  {found[0]}")


def test_xmnn_data_dirs() -> None:
    import xmnn

    xmnn_dir = xmnn.__path__[0] if hasattr(xmnn, "__path__") else os.path.dirname(xmnn.__file__)
    required = ("autolibs", "tools_cpp", "fonts")
    for name in required:
        d = os.path.join(xmnn_dir, name)
        _assert(os.path.isdir(d), f"xmnn/{name} 缺失: {d}")
        print(f"  {name}/: {len(os.listdir(d))} entries")


def test_kernel_registered() -> None:
    _assert(os.path.isfile(_KERNEL_JSON), f"内核 spec 缺失: {_KERNEL_JSON}")
    spec = json.loads(open(_KERNEL_JSON, encoding="utf-8").read())
    argv = spec.get("argv", [])
    _assert(argv and argv[0] == _BASE_PYTHON, f"内核 argv 必须指向 {_BASE_PYTHON}: {argv}")
    env = spec.get("env", {})
    _assert("PYTHONPATH" not in env, "交付内核不得注入源码 PYTHONPATH")
    _assert("TVM_LIBRARY_PATH" not in env, "交付内核不得注入 TVM_LIBRARY_PATH")
    print(f"  kernel.json argv={argv}, display={spec.get('display_name')}")
    out = subprocess.run(
        [_MAIN_JUPYTER, "kernelspec", "list"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    _assert(out.returncode == 0, f"jupyter kernelspec list 失败: {out.stderr.strip()}")
    _assert("xmnn-runtime" in out.stdout, f"main env jupyter 看不到 xmnn-runtime 内核:\n{out.stdout}")
    print("  visible to main env jupyter")


def test_torch_cpu_build() -> None:
    import torch

    ver = torch.__version__
    print(f"  torch.__version__ = {ver}")
    print(f"  torch.version.cuda = {torch.version.cuda}")
    _assert(ver.startswith(_EXPECTED_TORCH_MAJOR), f"torch 主版本异常: {ver}")
    # CPU wheel 的 torch.version.cuda 为 None；CUDA 变体会返回 '13.x' 字符串
    _assert(torch.version.cuda is None,
            f"必须是 CPU 构建（torch.version.cuda 应为 None），实际 {torch.version.cuda}")
    # pytorch 前端 compile_api 依赖 torch.jit.load；确认 TorchScript 子模块在
    _assert(hasattr(torch, "jit") and hasattr(torch.jit, "load"), "torch.jit.load 不可用")
    # 设备面只应有 CPU（rootless 仿真镜像不带 nvidia 运行时）
    _assert(torch.cuda.is_available() is False, "CPU 镜像不应报告 CUDA 可用")
    # 轻量功能探针：张量算子走 CPU 正常
    x = torch.arange(6, dtype=torch.float32).reshape(2, 3)
    _assert(float(x.sum()) == 15.0, "torch CPU 张量算子异常")
    print("  CPU tensor ops OK")


def main() -> int:
    print("==========================================")
    print("  XMNN Runtime Smoke (installed wheel)")
    print("==========================================")
    print(f"Python: {sys.version.split()[0]} @ {sys.executable}")
    print(f"PYTHONPATH={os.environ.get('PYTHONPATH', '<unset>')}")
    print(f"TVM_LIBRARY_PATH={os.environ.get('TVM_LIBRARY_PATH', '<unset>')}")
    print("")

    check("1. cp314 GIL interpreter ABI", test_interpreter_abi)
    check("2. import tvm/vta/xmnn from site-packages", test_imports_from_site_packages)
    check("3. _libs directory (libtvm.so + libLLVM)", test_libs_directory)
    check("4. ctypes load libtvm.so (clean env)", test_ctypes_load_libtvm)
    check("5. tvm.build('llvm') vector compute", test_tvm_build_llvm)
    check("6. relay/std/prelude.rly data", test_relay_std_data)
    check("7. xmnn_bootstrap.pth installed", test_bootstrap_pth)
    check("8. xmnn data directories", test_xmnn_data_dirs)
    check("9. xmnn-runtime jupyter kernel", test_kernel_registered)
    check("10. torch CPU-only build (jit + tensor ops)", test_torch_cpu_build)

    print("==========================================")
    print(f"  SUMMARY: {PASS} passed, {FAIL} failed")
    print("==========================================")
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
