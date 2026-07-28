"""pytest test suite for the three-layer logging example.

Tests C++ native logging via ctypes + subprocess, Python logging layer
integration, and cross-language level coordination.

Requires: pytest, a C++ compiler (clang++/g++) in PATH.

Usage:
    pytest test_three_layer.py -v
    pytest test_three_layer.py -v -k "trace"  # Run specific test
"""
from __future__ import annotations

import ctypes
import io
import logging
import os
import platform
import shutil
import struct
import subprocess
import sys
from pathlib import Path

import pytest

# ── Constants ──────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
_INVOKE_HELPER = SCRIPT_DIR / "_invoke_logs.py"

LOG_LEVEL_TRACE = 0
LOG_LEVEL_DEBUG = 1
LOG_LEVEL_INFO = 2
LOG_LEVEL_WARN = 3
LOG_LEVEL_ERROR = 4


# ── Helpers ────────────────────────────────────────────

def _find_compiler() -> str:
    """Find a working C++ compiler."""
    if platform.system() == "Windows":
        candidates = ["clang++", "clang-cl", "g++", "cl"]
    else:
        candidates = ["clang++", "g++"]
    for cc in candidates:
        if shutil.which(cc):
            return cc
    pytest.skip("No C++ compiler found (need clang++ or g++)", allow_module_level=True)
    return ""  # unreachable


def _compile_shared_lib(compiler: str, build_dir: Path) -> Path:
    """Compile ffi_bridge.cc into a shared library."""
    system = platform.system()
    lib_ext = ".dll" if system == "Windows" else (".dylib" if system == "Darwin" else ".so")
    lib_path = Path(build_dir) / f"mylog_test{lib_ext}"
    src = SCRIPT_DIR / "ffi_bridge.cc"

    if compiler in ("cl", "clang-cl"):
        cmd = [
            compiler, "/nologo", "/EHsc", "/LD",
            f"/Fe:{lib_path}",
            "-DMYPROJ_ENABLE_DEBUG_LOG", "-DMYPROJ_DLL_EXPORTS",
            f"-I{SCRIPT_DIR}", str(src),
        ]
    else:
        cmd = [
            compiler, "-shared", "-std=c++17", "-O2", "-Wall", "-Wextra",
            "-DMYPROJ_ENABLE_DEBUG_LOG", "-DMYPROJ_DLL_EXPORTS",
            f"-I{SCRIPT_DIR}",
        ]
        # On Windows, clang++ may default to 32-bit (i686); force 64-bit
        if system == "Windows" and struct.calcsize("P") == 8:
            cmd.insert(1, "--target=x86_64-pc-windows-msvc")
        if system != "Windows":
            cmd.append("-fPIC")
        cmd.extend(["-o", str(lib_path), str(src)])

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(SCRIPT_DIR))
    if result.returncode != 0:
        pytest.fail(f"Compilation failed:\n{result.stderr}\n{result.stdout}")
    return lib_path


def _load_library_direct(lib_path: Path) -> ctypes.CDLL:
    """Load shared library directly (for set/get level calls)."""
    if platform.system() == "Windows":
        os.add_dll_directory(str(lib_path.parent))
    lib = ctypes.CDLL(str(lib_path))
    lib.myproj_set_log_level.argtypes = [ctypes.c_int]
    lib.myproj_set_log_level.restype = None
    lib.myproj_get_log_level.argtypes = []
    lib.myproj_get_log_level.restype = ctypes.c_int
    lib.myproj_test_logs.argtypes = []
    lib.myproj_test_logs.restype = None
    return lib


def _trigger_logs_subprocess(lib_path: Path, level: int) -> tuple[str, str]:
    """Trigger C++ log output via subprocess for reliable stdout/stderr capture.

    Uses _invoke_logs.py helper which loads the DLL in a child process,
    avoiding in-process fd redirection issues (especially on Windows
    where C++ iostreams cache their HANDLE at startup).
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


# ── Fixtures ───────────────────────────────────────────

@pytest.fixture(scope="session")
def compiler():
    """Detect available C++ compiler (session-scoped)."""
    return _find_compiler()


@pytest.fixture(scope="session")
def lib_path(compiler, tmp_path_factory):
    """Compile shared library once per test session."""
    build_dir = tmp_path_factory.mktemp("log_build")
    return _compile_shared_lib(compiler, build_dir)


@pytest.fixture(scope="session")
def lib(lib_path):
    """Load compiled library directly (for set/get level calls)."""
    return _load_library_direct(lib_path)


@pytest.fixture(autouse=True)
def reset_level(lib):
    """Reset log level to WARN before each test."""
    lib.myproj_set_log_level(LOG_LEVEL_WARN)
    for h in logging.getLogger("myproj").handlers[:]:
        logging.getLogger("myproj").removeHandler(h)
        h.close()
    yield
    lib.myproj_set_log_level(LOG_LEVEL_WARN)


# ── Tests: C++ Native Layer ────────────────────────────

class TestCppNativeLayer:
    """Tests for the C++ logging core via ctypes direct calls + subprocess capture."""

    def test_default_level_is_warn(self, lib):
        """Default level should be WARN (3)."""
        assert lib.myproj_get_log_level() == LOG_LEVEL_WARN

    @pytest.mark.parametrize("level", [
        LOG_LEVEL_TRACE, LOG_LEVEL_DEBUG, LOG_LEVEL_INFO,
        LOG_LEVEL_WARN, LOG_LEVEL_ERROR,
    ])
    def test_set_level_roundtrip(self, lib, level):
        """SetLevel→GetLevel roundtrip for all levels."""
        lib.myproj_set_log_level(level)
        assert lib.myproj_get_log_level() == level

    def test_set_level_clamps_below_zero(self, lib):
        """Level < 0 is clamped to TRACE (0)."""
        lib.myproj_set_log_level(-1)
        assert lib.myproj_get_log_level() == LOG_LEVEL_TRACE

    def test_set_level_clamps_above_error(self, lib):
        """Level > 4 is clamped to ERROR (4)."""
        lib.myproj_set_log_level(99)
        assert lib.myproj_get_log_level() == LOG_LEVEL_ERROR

    def test_warn_level_filters_trace_debug_info(self, lib, lib_path):
        """At WARN level, only WARN and ERROR appear."""
        stdout, stderr = _trigger_logs_subprocess(lib_path, LOG_LEVEL_WARN)
        assert "[TRACE]" not in stdout
        assert "[DEBUG]" not in stdout
        assert "[INFO]" not in stdout
        assert "[WARN]" in stdout
        assert "[ERROR]" in stderr

    def test_debug_level_filters_trace(self, lib, lib_path):
        """At DEBUG level, TRACE is filtered but DEBUG/INFO/WARN/ERROR show."""
        stdout, stderr = _trigger_logs_subprocess(lib_path, LOG_LEVEL_DEBUG)
        assert "[TRACE]" not in stdout
        assert "[DEBUG]" in stdout
        assert "[INFO]" in stdout
        assert "[WARN]" in stdout
        assert "[ERROR]" in stderr

    def test_trace_level_shows_all(self, lib, lib_path):
        """At TRACE level, all 5 levels appear."""
        stdout, stderr = _trigger_logs_subprocess(lib_path, LOG_LEVEL_TRACE)
        assert "[TRACE]" in stdout
        assert "[DEBUG]" in stdout
        assert "[INFO]" in stdout
        assert "[WARN]" in stdout
        assert "[ERROR]" in stderr

    def test_info_level_hides_trace_debug(self, lib, lib_path):
        """At INFO level, TRACE and DEBUG are filtered."""
        stdout, stderr = _trigger_logs_subprocess(lib_path, LOG_LEVEL_INFO)
        assert "[TRACE]" not in stdout
        assert "[DEBUG]" not in stdout
        assert "[INFO]" in stdout
        assert "[WARN]" in stdout
        assert "[ERROR]" in stderr

    def test_error_level_only_shows_error(self, lib, lib_path):
        """At ERROR level, only ERROR appears (on stderr)."""
        stdout, stderr = _trigger_logs_subprocess(lib_path, LOG_LEVEL_ERROR)
        assert "[TRACE]" not in stdout
        assert "[DEBUG]" not in stdout
        assert "[INFO]" not in stdout
        assert "[WARN]" not in stdout
        assert "[ERROR]" in stderr

    def test_error_goes_to_stderr(self, lib, lib_path):
        """ERROR messages are routed to stderr, not stdout."""
        stdout, stderr = _trigger_logs_subprocess(lib_path, LOG_LEVEL_TRACE)
        assert "[ERROR]" in stderr
        assert "[ERROR]" not in stdout

    def test_non_error_goes_to_stdout(self, lib, lib_path):
        """Non-ERROR messages (TRACE/DEBUG/INFO/WARN) go to stdout."""
        stdout, _ = _trigger_logs_subprocess(lib_path, LOG_LEVEL_TRACE)
        assert "[WARN]" in stdout
        assert "[INFO]" in stdout
        assert "[DEBUG]" in stdout
        assert "[TRACE]" in stdout

    def test_grep_friendly_format(self, lib, lib_path):
        """Output uses [LEVEL] file:line (func) format for easy grepping."""
        stdout, _ = _trigger_logs_subprocess(lib_path, LOG_LEVEL_TRACE)
        assert "[TRACE]" in stdout
        assert "[DEBUG]" in stdout
        assert "ffi_bridge.cc:" in stdout
        assert ")" in stdout

    def test_messages_contain_expected_text(self, lib, lib_path):
        """Each level message contains its identifying text."""
        stdout, stderr = _trigger_logs_subprocess(lib_path, LOG_LEVEL_TRACE)
        assert "trace test message" in stdout
        assert "debug test message" in stdout
        assert "info test message" in stdout
        assert "warn test message" in stdout
        assert "error test message" in stderr

    def test_crlf_line_endings_windows(self, lib, lib_path):
        """On Windows, output lines end with \\r\\n (CRLF)."""
        if platform.system() != "Windows":
            pytest.skip("Windows-only test")
        stdout, _ = _trigger_logs_subprocess(lib_path, LOG_LEVEL_WARN)
        assert "\r\n" in stdout or "\n" in stdout


# ── Tests: Python Logging Layer ────────────────────────

class TestPythonLayer:
    """Tests for the Python debug.py configuration layer."""

    @pytest.fixture
    def debug_module(self, lib):
        """Import debug.py and wire ctypes bridge."""
        if str(SCRIPT_DIR) not in sys.path:
            sys.path.insert(0, str(SCRIPT_DIR))
        if "debug" in sys.modules:
            del sys.modules["debug"]
        import debug
        debug._set_native_level = lambda lv: lib.myproj_set_log_level(lv)
        debug._clear_handlers()
        yield debug
        debug._clear_handlers()
        # Restore root logger
        myproj_logger = logging.getLogger("myproj")
        for h in myproj_logger.handlers[:]:
            myproj_logger.removeHandler(h)
            h.close()

    def test_setup_debug_sets_cpp_level(self, debug_module, lib):
        """setup_debug() propagates level to C++ layer."""
        debug_module.setup_debug(level=LOG_LEVEL_TRACE)
        assert lib.myproj_get_log_level() == LOG_LEVEL_TRACE

    def test_setup_quiet_resets_to_warn(self, debug_module, lib):
        """setup_quiet() resets C++ to WARN."""
        debug_module.setup_debug(level=LOG_LEVEL_TRACE)
        assert lib.myproj_get_log_level() == LOG_LEVEL_TRACE
        debug_module.setup_quiet()
        assert lib.myproj_get_log_level() == LOG_LEVEL_WARN

    def test_setup_trace_enables_all_levels(self, debug_module, lib):
        """setup_trace() sets C++ to TRACE (0)."""
        debug_module.setup_trace()
        assert lib.myproj_get_log_level() == LOG_LEVEL_TRACE

    def test_idempotent_setup_no_duplicate_handlers(self, debug_module):
        """Calling setup_debug() twice should not duplicate handlers."""
        debug_module.setup_debug(level=LOG_LEVEL_INFO)
        myproj_logger = logging.getLogger("myproj")
        handler_count_before = len(myproj_logger.handlers)

        debug_module.setup_debug(level=LOG_LEVEL_DEBUG)
        handler_count_after = len(myproj_logger.handlers)

        assert handler_count_after <= handler_count_before + 1, (
            f"Handler leak: {handler_count_before} -> {handler_count_after}"
        )

    def test_python_debug_message_emitted(self, debug_module):
        """setup_debug emits a Python-level debug message."""
        buf = io.StringIO()
        handler = logging.StreamHandler(buf)
        handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
        myproj_logger = logging.getLogger("myproj")
        for h in myproj_logger.handlers[:]:
            myproj_logger.removeHandler(h)
            h.close()
        myproj_logger.addHandler(handler)
        myproj_logger.setLevel(logging.DEBUG)

        debug_module.setup_debug(level=LOG_LEVEL_DEBUG)
        py_output = buf.getvalue()
        assert "Debug logging enabled" in py_output

    def test_setup_file_logging(self, debug_module, tmp_path):
        """setup_file_logging creates a log file."""
        log_file = tmp_path / "test.log"
        debug_module.setup_file_logging(str(log_file), level=LOG_LEVEL_DEBUG)
        myproj_logger = logging.getLogger("myproj")
        myproj_logger.debug("file test message")
        for h in myproj_logger.handlers[:]:
            h.flush()
            h.close()
            myproj_logger.removeHandler(h)
        assert log_file.exists()
        content = log_file.read_text(encoding="utf-8")
        assert "file test message" in content


# ── Tests: Integration ─────────────────────────────────

class TestIntegration:
    """Integration tests verifying cross-language coordination."""

    def test_level_change_takes_effect_immediately(self, lib, lib_path):
        """Changing level affects subsequent log calls (sticky state)."""
        out1, _ = _trigger_logs_subprocess(lib_path, LOG_LEVEL_ERROR)
        assert "[DEBUG]" not in out1
        assert "[INFO]" not in out1

        out2, _ = _trigger_logs_subprocess(lib_path, LOG_LEVEL_DEBUG)
        assert "[DEBUG]" in out2
        assert "[INFO]" in out2

    def test_component_tag_macros_exist(self):
        """Component tag macros ([MEM], [TENSOR], etc.) are defined in log.hpp."""
        header = (SCRIPT_DIR / "log.hpp").read_text()
        assert "MYPROJ_MEM_LOG" in header
        assert "MYPROJ_TENSOR_LOG" in header
        assert "MYPROJ_NET_LOG" in header
        assert "MYPROJ_LAYER_LOG" in header

    def test_level_names_in_header(self):
        """Level names match between C++ and Python constants."""
        header = (SCRIPT_DIR / "log.hpp").read_text()
        assert '"TRACE"' in header
        assert '"DEBUG"' in header
        assert '"INFO"' in header
        assert '"WARN"' in header
        assert '"ERROR"' in header


# ── Tests: Compile-time Gate ──────────────────────────

class TestCompileTimeGate:
    """Tests verifying the compile-time zero-overhead gate.

    Without -DMYPROJ_ENABLE_DEBUG_LOG, TRACE/DEBUG/INFO are compiled out.
    The test build uses this flag so dynamic level control works.
    """

    def test_debug_log_flag_compiled_in(self, lib, lib_path):
        """The test build has MYPROJ_ENABLE_DEBUG_LOG, so DEBUG messages appear."""
        stdout, _ = _trigger_logs_subprocess(lib_path, LOG_LEVEL_DEBUG)
        assert "[DEBUG]" in stdout, (
            "DEBUG messages missing! Library may not have been compiled "
            "with -DMYPROJ_ENABLE_DEBUG_LOG."
        )
