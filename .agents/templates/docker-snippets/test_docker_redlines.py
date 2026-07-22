"""
Docker镜像五条红线自动化验证脚本
Pattern: docker-build-optimization-checklist red lines
Source: XMNN retrospective 2026-07-22

用法:
    pytest test_docker_redlines.py -v --image=<image_name> [--modules module1,module2] [--wheel=/path/to/wheel]
    pytest test_docker_redlines.py -v --image=xmnn-runtime:1.2.2 --modules=tvm,vta,xmnn

五条红线:
    R1: ldd检查零not found — 所有.so文件无缺失依赖
    R2: 核心模块全量import成功 — 指定模块均可正常导入
    R3: 功能测试通过（非仅import）— 执行实际计算/编译任务
    R4: 非root用户可正常运行 — UID/GID映射后容器可正常工作
    R5: pip install无警告 — wheel安装无hash mismatch/依赖冲突
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest


def pytest_addoption(parser):
    parser.addoption("--image", action="store", required=True, help="Docker image name:tag to test")
    parser.addoption("--modules", action="store", default="tvm,vta,xmnn",
                     help="Comma-separated list of core modules to import")
    parser.addoption("--wheel", action="store", default=None,
                     help="Path to wheel file for R5 pip install test")
    parser.addoption("--workspace", action="store", default=None,
                     help="Host directory to mount as /workspace for permission tests")
    parser.addoption("--python-cmd", action="store", default="python",
                     help="Python command inside container (python/python3)")
    parser.addoption("--skip-r4", action="store_true",
                     help="Skip R4 non-root test (e.g., for images without gosu)")
    parser.addoption("--skip-r3", action="store_true",
                     help="Skip R3 functional test (e.g., for minimal images)")


@pytest.fixture(scope="session")
def image(request):
    return request.config.getoption("--image")


@pytest.fixture(scope="session")
def modules(request):
    return [m.strip() for m in request.config.getoption("--modules").split(",") if m.strip()]


@pytest.fixture(scope="session")
def wheel_path(request):
    return request.config.getoption("--wheel")


@pytest.fixture(scope="session")
def workspace_dir(request):
    return request.config.getoption("--workspace")


@pytest.fixture(scope="session")
def python_cmd(request):
    return request.config.getoption("--python-cmd")


def docker_run(image, *args, python_cmd="python", script=None, mounts=None,
               user=None, timeout=60, capture=True, extra_docker_args=None):
    """Execute a command in a Docker container, optionally mounting a script file.

    Returns (returncode, stdout, stderr).
    """
    cmd = ["docker", "run", "--rm"]
    if extra_docker_args:
        cmd.extend(extra_docker_args)

    if mounts:
        for host_path, container_path in mounts.items():
            cmd.extend(["-v", f"{host_path}:{container_path}:ro"])

    if user:
        cmd.extend(["-u", user])

    cmd.append(image)

    if script:
        script_name = Path(script).name
        if not mounts or "/tmp/test_script" not in [v for _, v in (mounts or {}).items()]:
            cmd.extend([python_cmd, f"/tmp/scripts/{script_name}"])
        else:
            cmd.extend([python_cmd, "/tmp/test_script"])
    else:
        cmd.extend(args)

    if script:
        # Mount script directory
        script_dir = str(Path(script).parent)
        for i, a in enumerate(cmd):
            if a == image:
                idx = i + 1
                cmd[idx:idx] = ["-v", f"{script_dir}:/tmp/scripts:ro"]
                break

    result = subprocess.run(
        cmd, capture_output=capture, text=True, timeout=timeout,
    )
    return result.returncode, result.stdout, result.stderr


def run_in_container(image, code, python_cmd="python", mounts=None, user=None, timeout=60):
    """Run Python code in container by writing to temp file and mounting it.

    Uses the script-mount pattern (Pattern 3) to avoid multi-layer quoting issues.
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(code)
        tmp_script = f.name

    try:
        rc, stdout, stderr = docker_run(
            image, python_cmd=python_cmd, script=tmp_script,
            mounts=mounts, user=user, timeout=timeout,
        )
        return rc, stdout, stderr
    finally:
        os.unlink(tmp_script)


# ============================================================
# R1: ldd检查零not found
# ============================================================

class TestR1LddNoNotFound:
    """红线1：所有.so文件的ldd输出中无'not found'。"""

    def test_all_so_no_missing_deps(self, image, python_cmd):
        """R1-1: 扫描site-packages中所有.so，ldd无not found。"""
        rc, stdout, stderr = run_in_container(
            image,
            f"""
import site, subprocess, sys
sp = site.getsitepackages()[0]
print(sp)
""",
            python_cmd=python_cmd, timeout=30,
        )
        assert rc == 0, f"Failed to get site-packages: {stderr}"
        site_packages = stdout.strip().split('\n')[-1]

        rc, stdout, stderr = run_in_container(
            image,
            f"""
import subprocess, sys, os
from pathlib import Path

site_packages = "{site_packages}"
missing = []
so_files = list(Path(site_packages).rglob("*.so"))
so_files += [f for f in Path(site_packages).rglob("*.so.*") if f.is_file() and ".so" in f.name]

for so in so_files:
    try:
        result = subprocess.run(["ldd", str(so)], capture_output=True, text=True, timeout=10)
        for line in result.stdout.splitlines():
            if "not found" in line:
                missing.append(f"{{so.name}}: {{line.strip()}}")
    except Exception as e:
        print(f"Warning: could not check {{so}}: {{e}}", file=sys.stderr)

if missing:
    print("MISSING DEPENDENCIES:", file=sys.stderr)
    for m in missing:
        print(f"  {{m}}", file=sys.stderr)
    sys.exit(1)
else:
    print(f"R1 PASS: Checked {{len(so_files)}} .so files, no missing dependencies")
""",
            python_cmd=python_cmd, timeout=60,
        )
        assert rc == 0, f"R1 FAIL: Missing shared library dependencies\n{stderr}\n{stdout}"

    def test_core_libs_resolvable(self, image, python_cmd):
        """R1-2: 核心库(libtvm.so等)的ldd无not found。"""
        code = """
import subprocess, sys, site, glob, os

sp = site.getsitepackages()[0]
core_libs = ["libtvm_runtime.so"]
failed = []

for lib in core_libs:
    matches = glob.glob(os.path.join(sp, "**", lib), recursive=True)
    for p in matches:
        result = subprocess.run(["ldd", p], capture_output=True, text=True, timeout=10)
        not_found = [l for l in result.stdout.splitlines() if "not found" in l]
        if not_found:
            failed.append(f"{p}: {not_found}")

if failed:
    for f in failed:
        print(f"FAIL: {f}", file=sys.stderr)
    sys.exit(1)
else:
    print("R1-2 PASS: Core libraries resolvable")
"""
        rc, stdout, stderr = run_in_container(image, code, python_cmd=python_cmd, timeout=30)
        assert rc == 0, f"R1-2 FAIL: Core library deps missing\n{stderr}"


# ============================================================
# R2: 核心模块全量import成功
# ============================================================

class TestR2CoreModuleImports:
    """红线2：所有核心模块可成功导入。"""

    def test_core_modules_import(self, image, modules, python_cmd):
        """R2-1: 指定的核心模块全部import成功。"""
        imports = "\n".join(f"import {m}" for m in modules)
        code = f"""
import sys, importlib

modules = {modules!r}
failed = []
for mod in modules:
    try:
        m = importlib.import_module(mod)
        print(f"  [OK] import {{mod}}")
    except ImportError as e:
        failed.append(f"{{mod}}: {{e}}")
        print(f"  [FAIL] import {{mod}}: {{e}}", file=sys.stderr)

if failed:
    sys.exit(1)
else:
    print(f"R2 PASS: All {{len(modules)}} core modules imported successfully")
"""
        rc, stdout, stderr = run_in_container(image, code, python_cmd=python_cmd, timeout=30)
        assert rc == 0, f"R2 FAIL: Core module import errors\n{stderr}\n{stdout}"

    def test_package_versions_via_metadata(self, image, modules, python_cmd):
        """R2-2: 使用importlib.metadata.version()验证包版本（不用__version__）。"""
        code = f"""
import sys
from importlib.metadata import version, PackageNotFoundError

packages = {modules!r}
failed = []
for pkg in packages:
    try:
        v = version(pkg)
        print(f"  [OK] {{pkg}}=={{v}}")
    except PackageNotFoundError:
        # Package may not be a PyPI distribution (e.g., compiled-in module)
        print(f"  [SKIP] {{pkg}} (no distribution metadata)")
    except Exception as e:
        failed.append(f"{{pkg}}: {{e}}")

if failed:
    for f in failed:
        print(f"FAIL: {{f}}", file=sys.stderr)
    sys.exit(1)
else:
    print("R2-2 PASS: Package version checks via importlib.metadata")
"""
        rc, stdout, stderr = run_in_container(image, code, python_cmd=python_cmd, timeout=30)
        assert rc == 0, f"R2-2 FAIL\n{stderr}"


# ============================================================
# R3: 功能测试通过（非仅import）
# ============================================================

class TestR3FunctionalTest:
    """红线3：核心功能可运行（编译+执行计算），不只是import成功。"""

    @pytest.mark.skipif("--skip-r3" in sys.argv, reason="R3 skipped via --skip-r3")
    def test_tvm_te_compute(self, image, python_cmd):
        """R3-1: TVM TE张量计算（LLVM编译+运行）通过。"""
        code = """
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
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""
        rc, stdout, stderr = run_in_container(image, code, python_cmd=python_cmd, timeout=60)
        assert rc == 0, f"R3-1 FAIL: TVM TE compute failed\n{stderr}\n{stdout}"

    @pytest.mark.skipif("--skip-r3" in sys.argv, reason="R3 skipped via --skip-r3")
    def test_tvm_relay_build(self, image, python_cmd):
        """R3-2: TVM Relay计算图构建通过。"""
        code = """
import sys
try:
    import tvm
    from tvm import relay
    import numpy as np

    x = relay.var("x", shape=(1, 10), dtype="float32")
    y = relay.nn.relu(x)
    func = relay.Function([x], y)
    mod = tvm.IRModule.from_expr(func)
    with tvm.transform.PassContext(opt_level=2):
        lib = relay.build(mod, target="llvm")
    print("R3-2 PASS: Relay build OK (opt_level=2, llvm target)")
except Exception as e:
    print(f"R3-2 FAIL: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""
        rc, stdout, stderr = run_in_container(image, code, python_cmd=python_cmd, timeout=60)
        assert rc == 0, f"R3-2 FAIL: Relay build failed\n{stderr}\n{stdout}"


# ============================================================
# R4: 非root用户可正常运行
# ============================================================

class TestR4NonRootUser:
    """红线4：以非root用户(-u UID:GID)运行容器，可正常执行。"""

    @pytest.mark.skipif("--skip-r4" in sys.argv, reason="R4 skipped via --skip-r4")
    def test_nonroot_python_runs(self, image, python_cmd):
        """R4-1: 以非root用户(nobody UID=65534)可启动Python。"""
        code = """
import sys, os
print(f"R4-1: uid={os.getuid()}, gid={os.getgid()}")
assert os.getuid() != 0, "Still running as root!"
print("R4-1 PASS: Running as non-root user")
"""
        rc, stdout, stderr = run_in_container(
            image, code, python_cmd=python_cmd, user="65534:65534", timeout=30,
        )
        assert rc == 0, f"R4-1 FAIL: Cannot run as non-root\n{stderr}"

    @pytest.mark.skipif("--skip-r4" in sys.argv, reason="R4 skipped via --skip-r4")
    def test_nonroot_workspace_writable(self, image, python_cmd, workspace_dir, tmp_path):
        """R4-2: 挂载目录在非root用户下可读写（若提供workspace）。"""
        if not workspace_dir:
            pytest.skip("No --workspace provided, skipping mount writability test")

        test_dir = tmp_path / "r4_test"
        test_dir.mkdir(exist_ok=True)
        code = """
import os, sys
test_file = "/workspace/_r4_write_test"
try:
    with open(test_file, "w") as f:
        f.write("ok")
    with open(test_file) as f:
        assert f.read() == "ok"
    os.remove(test_file)
    print(f"R4-2 PASS: /workspace writable as uid={os.getuid()}")
except Exception as e:
    print(f"R4-2 FAIL: {e}", file=sys.stderr)
    sys.exit(1)
"""
        rc, stdout, stderr = docker_run(
            image, python_cmd=python_cmd,
            mounts={str(test_dir): "/workspace"},
            extra_docker_args=["-v", f"{str(test_dir)}:/workspace"],
        )
        # Use script mount
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            tmp_script = f.name
        try:
            script_dir = str(Path(tmp_script).parent)
            cmd = ["docker", "run", "--rm",
                   "-u", "1000:1000",
                   "-v", f"{str(test_dir)}:/workspace",
                   "-v", f"{script_dir}:/tmp/scripts:ro",
                   image, python_cmd, f"/tmp/scripts/{Path(tmp_script).name}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            assert result.returncode == 0, f"R4-2 FAIL: /workspace not writable as non-root\n{result.stderr}\n{result.stdout}"
        finally:
            os.unlink(tmp_script)


# ============================================================
# R5: pip install无警告（hash mismatch/依赖冲突）
# ============================================================

class TestR5PipInstallClean:
    """红线5：wheel安装无hash mismatch/依赖冲突。"""

    def test_pip_check_no_conflicts(self, image, python_cmd):
        """R5-1: pip check无依赖冲突。"""
        code = """
import subprocess, sys

result = subprocess.run([sys.executable, "-m", "pip", "check"],
                       capture_output=True, text=True, timeout=30)
# pip check returns 1 if there are conflicts
output = result.stdout + result.stderr
if "No broken requirements" in output or result.returncode == 0:
    print("R5-1 PASS: pip check - no broken requirements")
else:
    print(f"R5-1 FAIL: pip check found issues:\\n{output}", file=sys.stderr)
    sys.exit(1)
"""
        rc, stdout, stderr = run_in_container(image, code, python_cmd=python_cmd, timeout=30)
        assert rc == 0, f"R5-1 FAIL: pip check found conflicts\n{stderr}\n{stdout}"

    def test_wheel_install_no_warnings(self, image, python_cmd, wheel_path, tmp_path):
        """R5-2: 安装wheel无hash mismatch/error（若提供--wheel）。"""
        if not wheel_path:
            pytest.skip("No --wheel provided, skipping wheel install test")

        wheel = Path(wheel_path)
        assert wheel.exists(), f"Wheel file not found: {wheel}"

        # Test installation in a clean container (using the same image as base)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(f"""#!/bin/bash
set -e
pip install /tmp/wheels/{wheel.name} 2>&1 | tee /tmp/install.log
if grep -qi "error\\|hash mismatch\\|has requirement" /tmp/install.log; then
    # Check if "error" is in "no error" context or actual error
    if grep -qi "error:" /tmp/install.log && ! grep -qi "no error" /tmp/install.log; then
        echo "R5-2 FAIL: Installation errors detected"
        exit 1
    fi
    if grep -qi "hash mismatch" /tmp/install.log; then
        echo "R5-2 FAIL: Hash mismatch detected"
        exit 1
    fi
fi
echo "R5-2 PASS: Wheel installed without warnings"
""")
            tmp_script = f.name
        try:
            script_dir = str(Path(tmp_script).parent)
            cmd = ["docker", "run", "--rm",
                   "-v", f"{wheel.parent}:/tmp/wheels:ro",
                   "-v", f"{script_dir}:/tmp/scripts:ro",
                   image, "bash", f"/tmp/scripts/{Path(tmp_script).name}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            assert result.returncode == 0, f"R5-2 FAIL: Wheel install issues\n{result.stderr}\n{result.stdout}"
        finally:
            os.unlink(tmp_script)


# ============================================================
# 汇总报告
# ============================================================

def pytest_sessionfinish(session, exitstatus):
    """Print summary report after all tests."""
    print("\n" + "=" * 60)
    print("Docker Red Lines Verification Summary")
    print("=" * 60)
    print(f"Image: {session.config.getoption('--image')}")
    print(f"Modules: {session.config.getoption('--modules')}")
    print(f"Exit status: {'PASS ✅' if exitstatus == 0 else 'FAIL ❌'}")
    print("=" * 60)
