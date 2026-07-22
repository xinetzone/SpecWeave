#!/usr/bin/env python3
"""Docker五条红线验证 - 无pytest依赖版"""
import subprocess, sys, os, tempfile, shutil
from pathlib import Path

IMAGE = "xmnn-runtime-skeleton:test"
PY_CONDA = "/opt/conda/envs/tvm-build/bin/python"
ENV = {"TVM_LIBRARY_PATH": "/opt/conda/envs/tvm-build/lib/python3.14/site-packages/tvm/_libs"}

RED = "\033[0;31m"; GREEN = "\033[0;32m"; NC = "\033[0m"
PASS = FAIL = 0

def result(name, ok, detail=""):
    global PASS, FAIL
    if ok:
        print(f"  {GREEN}[PASS]{NC} {name}")
        PASS += 1
    else:
        print(f"  {RED}[FAIL]{NC} {name}")
        if detail: print(f"         {detail[:500]}")
        FAIL += 1

def docker_py(script, user=None, timeout=60, mounts=None):
    work_dir = tempfile.mkdtemp(prefix="dkrtest_")
    os.chmod(work_dir, 0o755)
    tmp = os.path.join(work_dir, "test.py")
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(script)
    os.chmod(tmp, 0o644)
    try:
        cmd = ["docker", "run", "--rm", "--entrypoint", ""]
        for k, v in ENV.items():
            cmd.extend(["-e", f"{k}={v}"])
        if mounts:
            for h, c in mounts.items():
                cmd.extend(["-v", f"{h}:{c}"])
        if user:
            cmd.extend(["-u", user])
        cmd.extend(["-v", f"{work_dir}:/tmp/scripts:ro"])
        cmd.extend([IMAGE, PY_CONDA, "/tmp/scripts/test.py"])
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)

def docker_cmd(args, timeout=30):
    cmd = ["docker", "run", "--rm", "--entrypoint", ""]
    cmd.extend([IMAGE] + list(args))
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr

print("=" * 60)
print(f"Docker Red Lines Verification: {IMAGE}")
print("=" * 60)

# R1: ldd
print("\nR1: ldd check (no missing dependencies)")
rc, out, err = docker_py("""
import subprocess, sys
from pathlib import Path
import site
sp = site.getsitepackages()[0]
missing = []
so_files = list(Path(sp).rglob("*.so"))
so_files += [f for f in Path(sp).rglob("*.so.*") if f.is_file() and ".so" in f.name]
for so in so_files:
    try:
        r = subprocess.run(["ldd", str(so)], capture_output=True, text=True, timeout=10)
        for l in r.stdout.splitlines():
            if "not found" in l:
                missing.append(f"{so.name}: {l.strip()}")
    except: pass
if missing:
    for m in missing: print(f"  {m}", file=sys.stderr)
    sys.exit(1)
print(f"OK: {len(so_files)} .so files checked")
""", timeout=60)
result("R1-1: All .so files ldd clean (no not found)", rc == 0, err+out)

rc, out, err = docker_py("""
import subprocess, sys, site, glob, os
sp = site.getsitepackages()[0]
for p in glob.glob(os.path.join(sp, "**", "libtvm_runtime.so"), recursive=True):
    r = subprocess.run(["ldd", p], capture_output=True, text=True, timeout=10)
    nf = [l for l in r.stdout.splitlines() if "not found" in l]
    if nf: print(f"FAIL: {p}: {nf}", file=sys.stderr); sys.exit(1)
print("OK: libtvm_runtime.so resolvable")
""")
result("R1-2: Core libraries (libtvm_runtime.so) resolvable", rc == 0, err+out)

# R2: imports
print("\nR2: Core module imports")
rc, out, err = docker_py("""
import importlib, sys
for m in ["tvm", "vta", "xmnn"]:
    importlib.import_module(m)
    print(f"  [OK] import {m}")
print("OK: all imports")
""")
result("R2: tvm, vta, xmnn all import successfully", rc == 0, err+out)

# R3: functional
print("\nR3: Functional tests")
rc, out, err = docker_py("""
import sys
try:
    import tvm
    from tvm import te
    import numpy as np
    n = te.var("n")
    A = te.placeholder((n,), name="A")
    B = te.compute((n,), lambda i: A[i] * 2.0, name="B")
    s = te.create_schedule(B.op)
    mod = tvm.build(s, [A, B], "llvm")
    ctx = tvm.cpu(0)
    a = tvm.nd.array(np.array([1.0,2.0,3.0], dtype="float32"), ctx)
    b = tvm.nd.array(np.zeros(3, dtype="float32"), ctx)
    mod(a,b)
    r = b.numpy().tolist()
    assert r == [2.0,4.0,6.0], f"got {r}"
    print(f"OK: TE [1,2,3]*2={r}")
except Exception as e:
    import traceback; traceback.print_exc()
    sys.exit(1)
""", timeout=60)
result("R3-1: TVM TE compute (LLVM compile+run)", rc == 0, err+out)

rc, out, err = docker_py("""
import sys
try:
    import tvm
    from tvm import relay
    x = relay.var("x", shape=(1,10), dtype="float32")
    y = relay.nn.relu(x)
    func = relay.Function([x], y)
    mod = tvm.IRModule.from_expr(func)
    with tvm.transform.PassContext(opt_level=2):
        lib = relay.build(mod, target="llvm")
    print("OK: Relay build")
except Exception as e:
    import traceback; traceback.print_exc()
    sys.exit(1)
""", timeout=60)
result("R3-2: TVM Relay build (opt_level=2, llvm)", rc == 0, err+out)

# R4: non-root
print("\nR4: Non-root user execution")
rc, out, err = docker_py("""
import os, sys
assert os.getuid() != 0, f"uid={os.getuid()}"
print(f"OK: uid={os.getuid()}")
""", user="65534:65534")
result("R4-1: Runs as non-root (nobody uid=65534)", rc == 0, err+out)

td = tempfile.mkdtemp()
os.chmod(td, 0o777)
try:
    rc, out, err = docker_py("""
import os, sys
try:
    with open("/workspace/_w","w") as f: f.write("ok")
    with open("/workspace/_w") as f: assert f.read()=="ok"
    os.remove("/workspace/_w")
    print(f"OK: uid={os.getuid()} writable")
except Exception as e:
    print(e, file=sys.stderr); sys.exit(1)
""", user="1000:1000", mounts={td: "/workspace"})
    result("R4-2: Non-root user (1000:1000) can write to /workspace", rc == 0, err+out)
finally:
    shutil.rmtree(td, ignore_errors=True)

# R5: pip check
print("\nR5: pip install clean")
rc, out, err = docker_py("""
import subprocess, sys
r = subprocess.run([sys.executable, "-m", "pip", "check"], capture_output=True, text=True, timeout=30)
output = r.stdout + r.stderr
if "No broken requirements" in output or r.returncode == 0:
    print("OK: no broken requirements")
else:
    print(output, file=sys.stderr); sys.exit(1)
""")
result("R5-1: pip check - no dependency conflicts", rc == 0, err+out)

# Summary
print("\n" + "=" * 60)
print(f"Result: {GREEN}{PASS} passed{NC}, {RED}{FAIL} failed{NC}")
print("=" * 60)
sys.exit(1 if FAIL else 0)
