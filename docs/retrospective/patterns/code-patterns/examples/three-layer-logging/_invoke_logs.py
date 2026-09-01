"""Helper script used by run_test.py / test_three_layer.py to invoke
the C++ logging functions in a subprocess (for reliable stdout/stderr capture).

Called as:
    python _invoke_logs.py <lib_path> <level>
Where <level> is 0-4 (TRACE through ERROR).

Prints captured output to stdout/stderr as appropriate.
Exit code 0 on success.
"""
from __future__ import annotations

import ctypes
import os
import platform
import sys
from pathlib import Path


def main():
    lib_path = Path(sys.argv[1])
    level = int(sys.argv[2])

    if platform.system() == "Windows":
        os.add_dll_directory(str(lib_path.parent))

    lib = ctypes.CDLL(str(lib_path))
    lib.myproj_set_log_level.argtypes = [ctypes.c_int]
    lib.myproj_set_log_level.restype = None
    lib.myproj_get_log_level.argtypes = []
    lib.myproj_get_log_level.restype = ctypes.c_int
    lib.myproj_test_logs.argtypes = []
    lib.myproj_test_logs.restype = None

    # Ensure stdout/stderr are line-buffered or unbuffered so C++ iostream
    # flushes immediately (important for subprocess pipe capture on Windows).
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(line_buffering=True)

    lib.myproj_set_log_level(level)
    sys.stdout.flush()
    sys.stderr.flush()
    lib.myproj_test_logs()
    sys.stdout.flush()
    sys.stderr.flush()

    # Also emit a Python-side marker so we can detect stdout/stderr separation
    # print("PY_STDOUT_MARKER", file=sys.stdout)
    # print("PY_STDERR_MARKER", file=sys.stderr)
    # sys.stdout.flush()
    # sys.stderr.flush()


if __name__ == "__main__":
    main()
