#!/usr/bin/env python3

# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

from lib.check_hardcode import (
    main,
    scan_python_file,
    collect_python_files,
    HardcodeIssue,
    FileReport,
    HardcodeVisitor,
)

if __name__ == "__main__":
    main()

