#!/usr/bin/env python3
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
