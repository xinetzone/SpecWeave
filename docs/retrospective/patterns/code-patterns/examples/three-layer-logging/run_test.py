#!/usr/bin/env python3
"""Quick validation script for the three-layer logging example.

Compiles the C++ code into a shared library, loads it via ctypes,
and runs 6 validation checks covering the README checklist.

Usage:
    python run_test.py          # Auto-detect compiler
    python run_test.py clang++  # Force specific compiler
    python run_test.py --clean  # Remove build artifacts and exit
"""
from __future__ import annotations

import ctypes
import io
import os
import platform
import shutil
import struct
import subprocess
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

# ── ANSI colors ──────────────────────────────────────────
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

SCRIPT_DIR = Path(__file__).resolve().parent
BUILD_DIR = SCRIPT_DIR / "build_test"

# Level constants matching C++ enum
LOG_LEVEL_TRACE = 0
LOG_LEVEL_DEBUG = 1
LOG_LEVEL_INFO = 2
LOG_LEVEL_WARN = 3
LOG_LEVEL_ERROR = 4

LEVEL_NAMES = {0: "TRACE", 1: "DEBUG", 2: "INFO", 3: "WARN", 4: "ERROR"}


def log_info(msg: str) -> None:
    print(f"{CYAN}[INFO]{RESET} {msg}")


def log_ok(msg: str) -> None:
    print(f"  {GREEN}✅ {msg}{RESET}")


def log_fail(msg: str) -> None:
    print(f"  {RED}❌ {msg}{RESET}")


def log_warn(msg: str) -> None:
    print(f"  {YELLOW}⚠️  {msg}{RESET}")


# ── Platform detection ──────────────────────────────────
def get_lib_ext() -> tuple[str, str]:
    """Return (shared_lib_extension, bin_subdir)."""
    system = platform.system()
    if system == "Windows":
        return ".dll", "Scripts"
    elif system == "Darwin":
        return ".dylib", "bin"
    else:
        return ".so", "bin"


def find_compiler(preferred: str | None = None) -> str | None:
    """Find a working C++ compiler."""
    candidates = []
    if preferred:
        candidates.append(preferred)
    if platform.system() == "Windows":
        candidates.extend(["clang++", "g++", "clang-cl", "cl"])
    else:
        candidates.extend(["clang++", "g++"])

    for cc in candidates:
        path = shutil.which(cc)
        if path:
            return cc
    return None


def get_compile_cmd(compiler: str, src: Path, dst: Path) -> list[str]:
    """Build platform-appropriate compile command."""
    system = platform.system()
    defines = ["-DMYPROJ_ENABLE_DEBUG_LOG", "-DMYPROJ_DLL_EXPORTS"]
    includes = [f"-I{SCRIPT_DIR}"]

    if compiler in ("cl", "clang-cl"):
        # MSVC-style flags
        return [
            compiler, "/nologo", "/EHsc", "/LD",
            f"/Fe:{dst}", *defines, *includes, str(src),
        ]
    else:
        # GCC/Clang-style flags
        cmd = [compiler, "-shared", "-std=c++17", "-O2", "-Wall", "-Wextra",
               *defines, *includes]
        # On Windows, clang++ may default to 32-bit (i686); force 64-bit
        # if Python is 64-bit (which is the common case)
        if system == "Windows" and struct.calcsize("P") == 8:
            cmd.insert(1, "--target=x86_64-pc-windows-msvc")
        if system != "Windows":
            cmd.append("-fPIC")
        cmd.extend(["-o", str(dst), str(src)])
        return cmd


# ── Build ───────────────────────────────────────────────
def clean_build() -> None:
    """Remove build directory. On Windows, DLLs loaded by ctypes cannot
    be deleted until the process exits, so failures are silently ignored."""
    if not BUILD_DIR.exists():
        return
    try:
        shutil.rmtree(BUILD_DIR)
        log_info(f"Cleaned {BUILD_DIR}")
    except (PermissionError, OSError):
        # DLL is locked by current process; will be overwritten on next build
        log_info("Build dir kept (DLL locked by process, cleaned on next run)")


def build_library(compiler: str) -> Path:
    """Compile ffi_bridge.cc into a shared library. Returns path to .dll/.so."""
    lib_ext, _ = get_lib_ext()
    lib_name = f"mylog_test{lib_ext}"

    BUILD_DIR.mkdir(exist_ok=True)
    lib_path = BUILD_DIR / lib_name

    src = SCRIPT_DIR / "ffi_bridge.cc"
    cmd = get_compile_cmd(compiler, src, lib_path)

    log_info(f"Compiling with {compiler}...")
    log_info(f"  Command: {' '.join(str(c) for c in cmd)}")

    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=str(SCRIPT_DIR),
    )
    if result.returncode != 0:
        print(f"{RED}Compilation failed!{RESET}")
        print(result.stderr)
        if result.stdout:
            print(result.stdout)
        sys.exit(1)

    if result.stderr:
        # Warnings only (returncode == 0)
        for line in result.stderr.splitlines():
            if line.strip():
                log_warn(f"Compiler warning: {line.strip()}")

    log_ok(f"Build successful: {lib_path.name}")
    return lib_path


# ── Load library ────────────────────────────────────────
def load_library(lib_path: Path) -> ctypes.CDLL:
    """Load the compiled shared library and set up function signatures."""
    system = platform.system()
    if system == "Windows":
        # Add build dir to DLL search path on Windows
        os.add_dll_directory(str(BUILD_DIR))
        lib = ctypes.CDLL(str(lib_path))
    else:
        lib = ctypes.CDLL(str(lib_path))

    # Set function signatures
    lib.myproj_set_log_level.argtypes = [ctypes.c_int]
    lib.myproj_set_log_level.restype = None
    lib.myproj_get_log_level.argtypes = []
    lib.myproj_get_log_level.restype = ctypes.c_int
    lib.myproj_test_logs.argtypes = []
    lib.myproj_test_logs.restype = None

    return lib


# ── Capture C++ stdout/stderr ───────────────────────────
# We use a subprocess helper (_invoke_logs.py) because in-process
# fd-level redirection (dup2) doesn't work reliably with C++ iostreams
# on Windows (cout/cerr cache their underlying HANDLE at startup).
# Running in a child process lets us use subprocess.PIPE natively.

_INVOKE_HELPER = SCRIPT_DIR / "_invoke_logs.py"


def set_level_and_capture(lib: ctypes.CDLL, level: int, lib_path: Path) -> tuple[str, str]:
    """Set C++ log level, trigger test logs via subprocess, return (stdout, stderr).

    Note: lib parameter is accepted for API compatibility but we use subprocess.
    """
    result = subprocess.run(
        [sys.executable, str(_INVOKE_HELPER), str(lib_path), str(level)],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(SCRIPT_DIR),
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    return result.stdout, result.stderr


# ── Python layer integration ────────────────────────────
def setup_python_debug(lib: ctypes.CDLL, level: int) -> None:
    """Configure Python logging layer and wire it to control C++ level."""
    # Add the example directory to path so we can import debug.py
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))

    # Monkey-patch debug._set_native_level to use ctypes
    import debug
    def _ctypes_set_level(lv: int) -> None:
        lib.myproj_set_log_level(lv)
    debug._set_native_level = _ctypes_set_level

    debug.setup_debug(level=level)


def capture_python_logs(lib: ctypes.CDLL, level: int) -> tuple[str, str]:
    """Setup Python logging, trigger test logs, capture all output."""
    # Reset root logger state first
    import logging
    root = logging.getLogger()
    for h in root.handlers[:]:
        root.removeHandler(h)
        h.close()

    buf_out = io.StringIO()
    buf_err = io.StringIO()

    # Monkey-patch native level setter
    setup_python_debug(lib, level)

    # Replace myproj logger's stream handler to capture to our buffer
    myproj_logger = logging.getLogger("myproj")
    for h in myproj_logger.handlers[:]:
        myproj_logger.removeHandler(h)
        h.close()
    handler = logging.StreamHandler(buf_out)
    handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    myproj_logger.addHandler(handler)
    myproj_logger.setLevel(logging.DEBUG)

    with CppOutputCapture() as cap:
        lib.myproj_test_logs()

    return buf_out.getvalue() + cap.stdout, cap.stderr


# ── Validation checks ──────────────────────────────────
class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.failures: list[str] = []

    def ok(self, msg: str):
        self.passed += 1
        log_ok(msg)

    def fail(self, msg: str):
        self.failed += 1
        self.failures.append(msg)
        log_fail(msg)

    def warn(self, msg: str):
        self.warnings += 1
        log_warn(msg)


def run_checks(lib: ctypes.CDLL, lib_path: Path) -> TestResult:
    r = TestResult()
    print(f"\n{BOLD}Running validation checks...{RESET}\n")

    # ── Check 1: Default WARN level ──────────────────────
    stdout, stderr = set_level_and_capture(lib, LOG_LEVEL_WARN, lib_path)
    has_trace = "[TRACE]" in stdout
    has_debug = "[DEBUG]" in stdout
    has_info = "[INFO]" in stdout
    has_warn = "[WARN]" in stdout
    has_error = "[ERROR]" in stderr  # ERROR goes to stderr

    if not has_trace and not has_debug and not has_info and has_warn and has_error:
        r.ok("Check 1: Default WARN level filters correctly (WARN+ERROR only)")
    else:
        r.fail(
            f"Check 1: Default WARN level incorrect — "
            f"TRACE={has_trace} DEBUG={has_debug} INFO={has_info} "
            f"WARN={has_warn} ERROR(stderr)={has_error}"
        )
        if stdout:
            print(f"    stdout: {stdout!r}")
        if stderr:
            print(f"    stderr: {stderr!r}")

    # ── Check 2: DEBUG level shows DEBUG+INFO+WARN+ERROR ─
    stdout, stderr = set_level_and_capture(lib, LOG_LEVEL_DEBUG, lib_path)
    has_trace = "[TRACE]" in stdout
    has_debug = "[DEBUG]" in stdout
    has_info = "[INFO]" in stdout
    has_warn = "[WARN]" in stdout
    has_error = "[ERROR]" in stderr

    if not has_trace and has_debug and has_info and has_warn and has_error:
        r.ok("Check 2: DEBUG level shows DEBUG/INFO/WARN/ERROR (TRACE filtered)")
    else:
        r.fail(
            f"Check 2: DEBUG level incorrect — "
            f"TRACE={has_trace} DEBUG={has_debug} INFO={has_info} "
            f"WARN={has_warn} ERROR(stderr)={has_error}"
        )

    # ── Check 3: TRACE level shows all 5 levels ─────────
    stdout, stderr = set_level_and_capture(lib, LOG_LEVEL_TRACE, lib_path)
    levels_found = {
        "TRACE": "[TRACE]" in stdout,
        "DEBUG": "[DEBUG]" in stdout,
        "INFO": "[INFO]" in stdout,
        "WARN": "[WARN]" in stdout,
        "ERROR": "[ERROR]" in stderr,
    }
    if all(levels_found.values()):
        r.ok("Check 3: TRACE level shows all 5 levels (TRACE→ERROR)")
    else:
        missing = [k for k, v in levels_found.items() if not v]
        r.fail(f"Check 3: TRACE level missing: {missing}")
        if stdout:
            print(f"    stdout: {stdout!r}")
        if stderr:
            print(f"    stderr: {stderr!r}")

    # ── Check 4: ERROR goes to stderr ────────────────────
    stdout, stderr = set_level_and_capture(lib, LOG_LEVEL_ERROR, lib_path)
    if "[ERROR]" in stderr and "[ERROR]" not in stdout:
        r.ok("Check 4: ERROR messages correctly routed to stderr")
    else:
        r.fail(
            f"Check 4: ERROR routing wrong — "
            f"in_stderr={'[ERROR]' in stderr}, in_stdout={'[ERROR]' in stdout}"
        )

    # ── Check 5: Grep-friendly format ────────────────────
    stdout, stderr = set_level_and_capture(lib, LOG_LEVEL_TRACE, lib_path)
    all_output = stdout + stderr
    has_brackets = "[TRACE]" in all_output and "[WARN]" in all_output
    has_file_line = "ffi_bridge.cc:" in all_output
    if has_brackets and has_file_line:
        r.ok("Check 5: Grep-friendly format ([LEVEL] file:line pattern)")
    else:
        r.fail(
            f"Check 5: Format issue — brackets={has_brackets}, file:line={has_file_line}"
        )

    # ── Check 6: myproj_get_log_level roundtrip ─────────
    lib.myproj_set_log_level(LOG_LEVEL_DEBUG)
    got = lib.myproj_get_log_level()
    if got == LOG_LEVEL_DEBUG:
        r.ok("Check 6: GetLogLevel roundtrip (set→get consistent)")
    else:
        r.fail(f"Check 6: GetLogLevel roundtrip failed (set=1, got={got})")

    return r


# ── Main ────────────────────────────────────────────────
def main():
    # Handle --clean
    if "--clean" in sys.argv:
        clean_build()
        return

    preferred = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else None

    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}  Three-Layer Logging — Quick Validation{RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}\n")

    log_info(f"Platform: {platform.system()} {platform.machine()}")
    log_info(f"Python: {sys.version.split()[0]}")

    # Find compiler
    compiler = find_compiler(preferred)
    if not compiler:
        print(f"\n{RED}Error: No C++ compiler found!{RESET}")
        print("Please install clang++ or g++ and ensure it's in PATH.")
        sys.exit(1)
    log_info(f"Compiler: {compiler}")

    # Build
    lib_path = build_library(compiler)

    # Load
    log_info("Loading shared library via ctypes...")
    lib = load_library(lib_path)
    log_ok("Library loaded successfully")

    # Verify default level is WARN
    default_level = lib.myproj_get_log_level()
    if default_level == LOG_LEVEL_WARN:
        log_ok(f"Default level is WARN ({default_level})")
    else:
        log_warn(f"Default level is {LEVEL_NAMES.get(default_level, default_level)}, expected WARN")

    # Run checks
    result = run_checks(lib, lib_path)

    # ── Summary ─────────────────────────────────────────
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  Results: {GREEN}{result.passed} passed{RESET}", end="")
    if result.failed:
        print(f", {RED}{result.failed} failed{RESET}", end="")
    if result.warnings:
        print(f", {YELLOW}{result.warnings} warnings{RESET}", end="")
    print(f"\n{BOLD}{'='*60}{RESET}\n")

    if result.failures:
        print(f"{RED}Failures:{RESET}")
        for f in result.failures:
            print(f"  • {f}")
        print()

    # Cleanup build artifacts (keep on failure for debugging)
    if result.failed == 0:
        clean_build()
        log_info("Build artifacts cleaned up")
    else:
        log_warn(f"Build artifacts kept at {BUILD_DIR} for debugging")
        sys.exit(1)


if __name__ == "__main__":
    main()
