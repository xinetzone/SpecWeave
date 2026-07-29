"""
Docker镜像五条红线自动化验证脚本（XMNN runtime适配版）
基于 test_docker_redlines.py，适配 conda 环境镜像（绕过entrypoint，使用conda python路径）
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

IMAGE = "xmnn-runtime-skeleton:test"
PY_CONDA = "/opt/conda/envs/tvm-build/bin/python"
CONDA_ENV = {"TVM_LIBRARY_PATH": "/opt/conda/envs/tvm-build/lib/python3.14/site-packages/tvm/_libs"}


def docker_py(script_content: str, user: str | None = None, timeout: int = 60,
              mounts: dict | None = None, extra_args: list | None = None) -> tuple[int, str, str]:
    """Run Python script in container via temp file mount. Returns (rc, stdout, stderr)."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(script_content)
        tmp_script = f.name
    try:
        cmd = ["docker", "run", "--rm", "--entrypoint", ""]
        for k, v in CONDA_ENV.items():
            cmd.extend(["-e", f"{k}={v}"])
        if extra_args:
            cmd.extend(extra_args)
        if mounts:
            for host_p, container_p in mounts.items():
                cmd.extend(["-v", f"{host_p}:{container_p}"])
        if user:
            cmd.extend(["-u", user])
        script_dir = str(Path(tmp_script).parent)
        cmd.extend(["-v", f"{script_dir}:/tmp/scripts:ro"])
        cmd.extend([IMAGE, PY_CONDA, f"/tmp/scripts/{Path(tmp_script).name}"])
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    finally:
        os.unlink(tmp_script)


class TestR1LddNoNotFound:
    def test_all_so_no_missing_deps(self):
        rc, stdout, stderr = docker_py("""
import subprocess, sys
from pathlib import Path
import site
sp = site.getsitepackages()[0]
missing = []
so_files = list(Path(sp).rglob("*.so"))
so_files += [f for f in Path(sp).rglob("*.so.*") if f.is_file() and ".so" in f.name]
for so in so_files:
    try:
        result = subprocess.run(["ldd", str(so)], capture_output=True, text=True, timeout=10)
        for line in result.stdout.splitlines():
            if "not found" in line:
                missing.append(f"{so.name}: {line.strip()}")
    except Exception as e:
        print(f"Warning: {so}: {e}", file=sys.stderr)
if missing:
    for m in missing: print(f"  {m}", file=sys.stderr)
    sys.exit(1)
print(f"R1 PASS: Checked {len(so_files)} .so files, no missing dependencies")
""", timeout=60)
        assert rc == 0, f"R1 FAIL:\n{stderr}\n{stdout}"

    def test_core_libs_resolvable(self):
        rc, stdout, stderr = docker_py("""
import subprocess, sys, site, glob, os
sp = site.getsitepackages()[0]
for lib in ["libtvm_runtime.so"]:
    for p in glob.glob(os.path.join(sp, "**", lib), recursive=True):
        result = subprocess.run(["ldd", p], capture_output=True, text=True, timeout=10)
        nf = [l for l in result.stdout.splitlines() if "not found" in l]
        if nf:
            print(f"FAIL: {p}: {nf}", file=sys.stderr); sys.exit(1)
print("R1-2 PASS: Core libraries resolvable")
""")
        assert rc == 0, f"R1-2 FAIL:\n{stderr}"


class TestR2CoreModuleImports:
    def test_core_modules_import(self):
        rc, stdout, stderr = docker_py("""
import sys, importlib
modules = ["tvm", "vta", "xmnn"]
failed = []
for mod in modules:
    try:
        importlib.import_module(mod)
        print(f"  [OK] import {mod}")
    except ImportError as e:
        failed.append(f"{mod}: {e}")
if failed:
    for f in failed: print(f, file=sys.stderr)
    sys.exit(1)
print(f"R2 PASS: All {len(modules)} core modules imported successfully")
""")
        assert rc == 0, f"R2 FAIL:\n{stderr}\n{stdout}"


class TestR3FunctionalTest:
    def test_tvm_te_compute(self):
        rc, stdout, stderr = docker_py("""
import sys
try:
    import tvm
    from tvm import te
    import numpy as np
    n = te.var("n")
    A = te.placeholder((n,), name="A")
    B = te.compute((n,), lambda i: A[i] * 2.0, name="B")
    s = te.create_schedule(B.op)
    mod = tvm.build(s, [A, B], "llvm", name="double_array")
    ctx = tvm.cpu(0)
    a = tvm.nd.array(np.array([1.0, 2.0, 3.0], dtype="float32"), ctx)
    b = tvm.nd.array(np.zeros(3, dtype="float32"), ctx)
    mod(a, b)
    result = b.numpy().tolist()
    expected = [2.0, 4.0, 6.0]
    assert result == expected, f"Expected {expected}, got {result}"
    print(f"R3-1 PASS: TVM TE compute result={result}")
except Exception as e:
    print(f"R3-1 FAIL: {e}", file=sys.stderr)
    import traceback; traceback.print_exc()
    sys.exit(1)
""", timeout=60)
        assert rc == 0, f"R3-1 FAIL:\n{stderr}\n{stdout}"

    def test_tvm_relay_build(self):
        rc, stdout, stderr = docker_py("""
import sys
try:
    import tvm
    from tvm import relay
    x = relay.var("x", shape=(1, 10), dtype="float32")
    y = relay.nn.relu(x)
    func = relay.Function([x], y)
    mod = tvm.IRModule.from_expr(func)
    with tvm.transform.PassContext(opt_level=2):
        lib = relay.build(mod, target="llvm")
    print("R3-2 PASS: Relay build OK")
except Exception as e:
    print(f"R3-2 FAIL: {e}", file=sys.stderr)
    import traceback; traceback.print_exc()
    sys.exit(1)
""", timeout=60)
        assert rc == 0, f"R3-2 FAIL:\n{stderr}\n{stdout}"


class TestR4NonRootUser:
    def test_nonroot_python_runs(self):
        rc, stdout, stderr = docker_py("""
import sys, os
print(f"uid={os.getuid()}, gid={os.getgid()}")
assert os.getuid() != 0, "Still running as root!"
print("R4-1 PASS: Running as non-root user")
""", user="65534:65534", timeout=30)
        assert rc == 0, f"R4-1 FAIL:\n{stderr}"

    def test_nonroot_workspace_writable(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            os.chmod(td, 0o777)
            rc, stdout, stderr = docker_py("""
import os, sys
test_file = "/workspace/_r4_write_test"
try:
    with open(test_file, "w") as f: f.write("ok")
    with open(test_file) as f: assert f.read() == "ok"
    os.remove(test_file)
    print(f"R4-2 PASS: /workspace writable as uid={os.getuid()}")
except Exception as e:
    print(f"R4-2 FAIL: {e}", file=sys.stderr); sys.exit(1)
""", user="1000:1000", timeout=30, mounts={td: "/workspace"})
            assert rc == 0, f"R4-2 FAIL:\n{stderr}\n{stdout}"


class TestR5PipInstallClean:
    def test_pip_check_no_conflicts(self):
        rc, stdout, stderr = docker_py("""
import subprocess, sys
result = subprocess.run([sys.executable, "-m", "pip", "check"],
                       capture_output=True, text=True, timeout=30)
output = result.stdout + result.stderr
if "No broken requirements" in output or result.returncode == 0:
    print("R5-1 PASS: pip check - no broken requirements")
else:
    print(f"R5-1 FAIL: {output}", file=sys.stderr); sys.exit(1)
""")
        assert rc == 0, f"R5-1 FAIL:\n{stderr}\n{stdout}"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"] + sys.argv[1:]))
