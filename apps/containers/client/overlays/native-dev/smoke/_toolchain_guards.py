"""native-dev 叠加层工具链守卫（构建期 + podman run --rm 双路径，不依赖源码挂载）。

运行方式：/opt/conda/bin/python /opt/native-dev-smoke/_toolchain_guards.py

守卫集合：
  1. 双 ABI：脚本自身解释器（base env）必须为 cp314 GIL enabled；
     main env 必须为 cp314t free-threading 且 GIL disabled（conda 装工具链
     时 pin python=*=*cp314t，若被求解互换此处立即失败）；
  2. main env 工具链：llvm-config 22.1.x、clang、cmake>=3.18、ninja、
     ccache、patchelf、gdb 均可执行；
  3. base env 打包栈：nuitka==4.2.1、scikit-build-core、build、invoke；
     并断言运行解释器版本在 Nuitka 的 getSupportedPythonVersions() 内——
     Nuitka 对未列入版本的 python 会打 "only experimentally supported"
     警告，该警告是升级 python 后最易遗漏的构建期噪声；
  4. /opt/native-builder 打包资产齐全；
  5. LLVM 依赖库 7 个 glob 在 llvm-config --libdir 全部可命中并打印实际
     SONAME（SONAME 漂移的构建期硬拦截，对应 CMakeLists 的 glob 收集）；
  6. devuser 可读性（Containerfile 以 su 复跑间接保证）；
  7. 离线完备性（阶段一契约）：无网侧不能再补装任何依赖，故编译/打包前端
     与 pyproject [project].dependencies 声明的运行时依赖必须全部已在镜像内。
     守卫自身不联网、不装包（否则守卫成为新的离线缺口）。
  8. torch 形态（C18）：读镜像内标记文件 /opt/native-torch-flavor（由 Layer 2.5
     按 build-arg TORCH_FLAVOR 写入），断言「声明形态 == 实际形态」——空声明
     时 torch 必须缺席（默认镜像零 torch），cpu/cu130 时 version.cuda 必须
     分别为 None/非 None。声明与实物脱钩（如缓存串味、ARG 未透传）在此拦截。
  9. CUDA 编译器工具链（C25）：cu130 形态随包 nvcc（Layer 2.6）。三查——
    ① /opt/native-cuda-nvcc-version 标记版本 == `nvcc --version` 实测版本；
    ② /usr/local/cuda 农场布局（bin/include/lib64/nvvm + libcudart.so 短名）；
    ③ **真编译 + 真链接**一个最小 .cu（唯一能拦住 glibc/crt 头冲突与三包错版
    的判据——「nvcc 存在」不等于「编得过」）。非 cu130 形态反向断言 nvcc 缺席。
  10. GUI 客户端运行时（tkinter，Layer 4.5 恢复）：基底深度清理删除了 tk/tcl
     文件但保留 conda-meta 记录（腐坏态），Layer 4.5 以精确版本 tk=8.6.13 恢复
     （latest 为 tk 9.0，soname 不兼容，见 install-gui-libs.sh 头注）。本守卫
    **headless 可跑**：`import tkinter` 成功即同时证明 libtk8.6/libtcl8.6 与
    libX11 客户端库全部可解析（dlopen 任一缺失即 ImportError）；`tkinter.Tcl()`
    再证 tcl8.6 脚本目录（init.tcl 等）在位。不建 Tk 窗口（构建期无显示，属
    预期边界；弹窗链路由运行期 `up --gui` + WSLg socket 实测覆盖）。
  11. AST 启动钩子（Layer 5 install-ast-bootstrap.sh，2026-09-28）：CPython
     3.12+ 移除 ast.NameConstant/Num/Str/Bytes/Ellipsis，tvm 源码树的
     py_converter.py 在**导入期**引用它们，运行期补丁晚于导入——唯一注入位
     点是 site 初始化期 .pth 钩子。本守卫以「新解释器进程 hasattr」双端断言
     base/main 都已烤入（main 侧子进程**不带 -S**，否则跳过 site 处理恰好
     绕过被测对象）。

任何断言失败即以非零退出（构建期 RUN 失败、run --rm 冒烟失败）。
"""

import glob
import importlib.metadata as md
import os
import re
import shutil
import subprocess
import sys
import sysconfig
import tempfile
import tomllib
from pathlib import Path

MAIN_PREFIX = Path("/opt/conda/envs/main")
MAIN_PYTHON = MAIN_PREFIX / "bin" / "python"
BUILDER_DIR = Path("/opt/native-builder")

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
check("nuitka 4.2.1", rc == 0 and "4.2.1" in nuitka_ver, nuitka_ver[:80])

# 运行解释器必须落在 Nuitka 的支持列表内，否则每次打包都会打
# "The Python version '3.x' is only experimentally supported" 警告。
# 4.1.3 止于 3.13，升到 3.14 解释器后该警告即出现，故在此硬拦截。
try:
    from nuitka.PythonVersions import getSupportedPythonVersions

    running = "%d.%d" % sys.version_info[:2]
    supported = getSupportedPythonVersions()
    check(f"运行解释器 {running} 在 Nuitka 支持列表内", running in supported,
          "supported: " + ", ".join(supported))
except Exception as exc:  # noqa: BLE001
    check("读取 Nuitka 支持的 python 版本列表", False, str(exc))

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

print("\n== 4. /opt/native-builder 打包资产 ==")
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
    check(f"native-builder/{rel}", (BUILDER_DIR / rel).is_file())

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
print("  本脚本路径 /opt/native-dev-smoke/_toolchain_guards.py，chmod a+rX 烤入")

print("\n== 7. 离线完备性（阶段一契约：镜像自足，无网侧不得再补依赖）==")
# 判定基准：显式构造 build-tvm.sh / build-wheel.sh 实际建立的两段 PATH
# （main env 工具链 + base env），不依赖调用者继承的 PATH——本脚本要在
# root 与 devuser 两身份下给出同一结论（su 不带 - 会继承 root 的 PATH）。
probe_path = f"/opt/conda/bin:/opt/conda/envs/main/bin:{os.environ.get('PATH', '')}"

# 7a. 编译/打包前端：无网侧既无 apt 也无 pip，缺一项即意味着阶段二不可完成
for tool in ("gcc", "g++", "ccache", "cmake", "ninja", "make", "patchelf", "readelf"):
    resolved = shutil.which(tool, path=probe_path)
    check(f"离线必备 {tool}", resolved is not None,
          resolved or "NOT FOUND（无网侧无法补装，须回有网侧重建镜像）")

# 7b. 运行时依赖：单一事实源 = builder/pyproject.toml [project].dependencies
#     （不在此重复维护清单）；以发行版元数据判定「已装」，避免 dist→import
#     名映射（Pillow→PIL 等）引入第二份映射表。
declared: list[str] = []
try:
    _meta = tomllib.loads((BUILDER_DIR / "pyproject.toml").read_text(encoding="utf-8"))
    declared = list(_meta["project"]["dependencies"])
    check("读取 pyproject [project].dependencies", bool(declared), f"{len(declared)} 条")
except Exception as exc:  # noqa: BLE001
    check("读取 pyproject [project].dependencies", False, str(exc))

missing_deps: list[str] = []
for spec in declared:
    dist = re.split(r"[<>=!~\[; ]", spec.strip(), maxsplit=1)[0]
    try:
        md.version(dist)
    except md.PackageNotFoundError:
        missing_deps.append(dist)
check(f"pyproject 声明的 {len(declared)} 个运行时依赖全部已装",
      bool(declared) and not missing_deps,
      f"缺失：{', '.join(missing_deps)}" if missing_deps else "numpy/scipy 等齐备")

# 7c. 打包工具链（与 §3 的 import 断言互补：这里锁「发行版元数据已登记」，
#     覆盖 pip 不可见但 import 可用的构建后端边界）
for dist in ("nuitka", "scikit-build-core", "build", "wheel", "invoke", "ipykernel"):
    try:
        check(f"离线必备打包工具 {dist}", True, md.version(dist))
    except md.PackageNotFoundError:
        check(f"离线必备打包工具 {dist}", False, "未安装（无网侧 pip 无法补装）")

print("\n== 8. torch 形态（声明 vs 实物，C18）==")
# 标记文件由 Layer 2.5 写入（空串亦写，故文件必存在）；守卫读不到 LABEL，
# 标记文件是「本镜像声明的 torch 形态」在容器内的唯一载体。
FLAVOR_MARKER = Path("/opt/native-torch-flavor")
declared_flavor: str | None = None
if FLAVOR_MARKER.is_file():
    declared_flavor = FLAVOR_MARKER.read_text(encoding="utf-8").strip()
    check("读取 /opt/native-torch-flavor", declared_flavor in ("", "cpu", "cu130"),
          repr(declared_flavor))
else:
    check("读取 /opt/native-torch-flavor", False,
          "标记文件缺失（Layer 2.5 install-torch.sh 未执行）")

torch_installed = False
torch_cuda = None
try:
    import torch  # noqa: PLC0415

    torch_installed = True
    torch_cuda = getattr(torch.version, "cuda", None)
except Exception:  # noqa: BLE001  （ImportError 及其传递依赖缺失）
    torch_installed = False

if declared_flavor == "":
    check("声明空形态 → torch 必须缺席（默认镜像零 torch）", not torch_installed,
          "torch 意外存在（基底或缓存串味）" if torch_installed else "缺席（符合预期）")
elif declared_flavor == "cpu":
    check("声明 cpu → torch 已装且 version.cuda is None",
          torch_installed and torch_cuda is None,
          f"installed={torch_installed}, cuda={torch_cuda!r}")
elif declared_flavor == "cu130":
    check("声明 cu130 → torch 已装且 version.cuda 非空",
          torch_installed and torch_cuda is not None,
          f"installed={torch_installed}, cuda={torch_cuda!r}")
if torch_installed:
    print(f"  torch: {getattr(torch, '__version__', '?')} cuda={torch_cuda!r}")


print("\n== 9. CUDA 编译器工具链（cu130 形态随包 nvcc，C25：声明 vs 实物）==")


def nvcc_compile_probe(nvcc: str) -> tuple[bool, str]:
    """真编译 + 真链接一个最小 .cu（不运行——构建期无 GPU 设备，属预期边界）。

    「nvcc --version 可执行」不是充分条件：glibc/crt 头规格冲突（13.0 与
    glibc 2.43 的 rsqrt noexcept）与 nvcc/nvvm/crt 三包错版（cicc 产 PTX
    9.4、ptxas 只认 9.0）都只在编译期暴露，故守卫必须真编一个 .cu。
    """
    src = (
        "#include <cuda_runtime.h>\n"
        "__global__ void guard_add_one(int *p) { p[0] += 1; }\n"
        "int main() {\n"
        "    int h = 41; int *d = nullptr;\n"
        "    cudaMalloc(&d, sizeof(int));\n"
        "    cudaMemcpy(d, &h, sizeof(int), cudaMemcpyHostToDevice);\n"
        "    guard_add_one<<<1, 1>>>(d);\n"
        "    cudaMemcpy(&h, d, sizeof(int), cudaMemcpyDeviceToHost);\n"
        "    cudaFree(d);\n"
        "    return h == 42 ? 0 : 1;\n"
        "}\n"
    )

    def last_err(proc: subprocess.CompletedProcess) -> str:
        text = (proc.stderr or proc.stdout or "").strip()
        lines = [ln for ln in text.splitlines() if ln.strip()]
        return lines[-1][:160] if lines else "no output"

    try:
        with tempfile.TemporaryDirectory(prefix="nvcc-guard-") as td:
            cu = Path(td) / "guard_probe.cu"
            cu.write_text(src, encoding="utf-8")
            comp = subprocess.run(
                [nvcc, "-c", str(cu), "-o", str(Path(td) / "guard_probe.o")],
                capture_output=True, text=True, timeout=600,
            )
            if comp.returncode != 0:
                return False, f"compile rc={comp.returncode}: {last_err(comp)}"
            link = subprocess.run(
                [nvcc, str(cu), "-o", str(Path(td) / "guard_probe"), "-lcudart"],
                capture_output=True, text=True, timeout=600,
            )
            if link.returncode != 0:
                return False, f"link rc={link.returncode}: {last_err(link)}"
            return True, "compile + link OK（-c 与 -lcudart 双段；不运行）"
    except (OSError, subprocess.SubprocessError) as exc:
        return False, str(exc)


NVCC_MARKER = Path("/opt/native-cuda-nvcc-version")
nvcc_path = shutil.which("nvcc")
if declared_flavor == "cu130":
    declared_nvcc = (
        NVCC_MARKER.read_text(encoding="utf-8").strip() if NVCC_MARKER.is_file() else None
    )
    check("cu130 → nvcc 版本标记存在（Layer 2.6 已执行）", bool(declared_nvcc),
          repr(declared_nvcc))
    check("cu130 → nvcc 在 PATH 上可解析（/usr/local/bin wrapper）",
          nvcc_path is not None, nvcc_path or "NOT FOUND")
    if nvcc_path:
        rc, out = run_version(nvcc_path, "--version")
        rel = [ln for ln in out.splitlines() if "release" in ln]
        check("nvcc --version 可执行", rc == 0, rel[-1] if rel else out[:100])
        if declared_nvcc:
            check(f"nvcc 实测版本 == 标记版本 {declared_nvcc}", declared_nvcc in out,
                  "一致" if declared_nvcc in out else "版本漂移（pip 升级/缓存串味）")
        for rel_path in (
            "bin/nvcc",
            "include/cuda_runtime.h",
            "lib64/libcudart.so",
            "nvvm/libdevice",
        ):
            check(f"/usr/local/cuda/{rel_path}", Path("/usr/local/cuda", rel_path).exists())
        # 动态链接器登记（编译产物「开箱即跑」的必要条件）：无它则编译链接都过，
        # 但二进制运行期报 `libcudart.so.13: cannot open shared object file`——
        # 只在「运行」时才暴露，故必须在此断言 ldconfig 缓存已含 libcudart。
        rc, out = run_version("ldconfig", "-p")
        check("ldconfig 已登记 libcudart（编译产物可运行）",
              rc == 0 and "libcudart" in out,
              next((ln for ln in out.splitlines() if "libcudart" in ln), out[:80]).strip())
        ok, detail = nvcc_compile_probe(nvcc_path)
        check("nvcc 编译 + 链接最小 .cu（-lcudart）", ok, detail)
else:
    check(f"声明形态 {declared_flavor!r} → nvcc 必须缺席（默认隔离）",
          nvcc_path is None and not NVCC_MARKER.is_file(),
          f"which={nvcc_path}, marker_exists={NVCC_MARKER.is_file()}")

print("\n== 10. GUI 客户端运行时（tkinter，Layer 4.5 恢复）==")
# headless 断言（构建期无显示）：`import tkinter` 走 dlopen libtk8.6.so，能成功
# 即同时证明 libtcl8.6 + libX11 客户端库全部可解析（任一缺失即 ImportError）；
# `tkinter.Tcl()` 再证 tcl8.6 脚本目录（init.tcl 等）在位。
for rel in ("lib/libtk8.6.so", "lib/libtcl8.6.so", "lib/libX11.so.6"):
    check(f"/opt/conda/{rel}", Path("/opt/conda", rel).is_file())
try:
    import tkinter as tk  # noqa: PLC0415

    check("tkinter 可导入（libtk/libtcl/X11 客户端库齐备）", True,
          f"TkVersion={tk.TkVersion}")
    check("Tk 运行库为 8.6 系（与 _tkinter ABI 匹配）",
          str(tk.TkVersion) == "8.6", f"TkVersion={tk.TkVersion}")
    tcl_patchlevel = tk.Tcl().eval("info patchlevel")
    check("Tcl 脚本库在位（info patchlevel）", tcl_patchlevel.startswith("8.6"),
          tcl_patchlevel)
except Exception as exc:  # noqa: BLE001
    check("tkinter 可导入（libtk/libtcl/X11 客户端库齐备）", False, str(exc))

print("\n== 11. AST 启动钩子（xmnn_bootstrap.pth，import tvm 前置条件）==")
# CPython 3.14 移除 ast.NameConstant/Num/Str/Bytes/Ellipsis 五名，但
# _xmnn_bootstrap.py（与生态四份真源一致）只恢复前四名：Ellipsis 无运行时
# 消费者（tvm 上游测试主动 delattr 五名仍通过）；Index/ExtSlice 3.14 原生仍存。
# 故哨兵只用「stock 3.14 全缺、钩子运行后全有」的四名（2026-09-28 实证，
# sc-20260928-native-build-cu130）。tvm 源码树旧版 py_converter.py 在导入期
# `from ast import ..., NameConstant, Num, Str`——只有 site 初始化期 .pth 钩子
# 赶得在导入之前（Layer 5 install-ast-bootstrap.sh 烤入）。本守卫自身就是
# 「钩子生效后的新解释器进程」：能 import 到钩子模块 + 哨兵四名齐备即双证；
# 端到端 import tvm 由外层冒烟兜底，不在此重复。
_AST_SENTINELS = ("NameConstant", "Num", "Str", "Bytes")
try:
    import _xmnn_bootstrap  # noqa: F401,PLC0415

    check("_xmnn_bootstrap 可导入（base site-packages 就位）", True)
except Exception as exc:  # noqa: BLE001
    check("_xmnn_bootstrap 可导入（base site-packages 就位）", False, str(exc))
import ast as _ast  # noqa: PLC0415

check("base 启动期 ast 别名齐备",
      all(hasattr(_ast, n) for n in _AST_SENTINELS),
      f"ast 来自 {_ast.__file__}")
main_ast_code = (
    "import ast; "
    "assert all(hasattr(ast, n) for n in "
    f"({', '.join(repr(n) for n in _AST_SENTINELS)})), 'ast aliases missing'"
)
# 注意不带 -S：-S 跳过 site 处理，恰好绕过被测对象（.pth 不执行）
main_ast = subprocess.run(
    [str(MAIN_PYTHON), "-c", main_ast_code],
    capture_output=True, text=True, timeout=30,
)
main_ast_err = (main_ast.stderr or "").strip().splitlines()
check("main 启动期 ast 别名齐备", main_ast.returncode == 0,
      main_ast_err[-1][:120] if main_ast_err else "OK")

print("")
if failures:
    print(f"[FAIL] {len(failures)} 项守卫未通过：{failures}")
    sys.exit(1)
print("[OK] native-dev toolchain guards all passed "
      "(dual ABI + LLVM 22.1 toolchain + nuitka 4.2.1 + builder assets + SONAME "
      "+ offline self-sufficiency + torch flavor + cuda nvcc + tkinter GUI runtime)")
