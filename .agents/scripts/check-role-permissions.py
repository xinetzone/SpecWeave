#!/usr/bin/env python3
"""向后兼容包装：check-role-permissions.py → repo-check.py roles。"""

import subprocess
import sys
from pathlib import Path


def main():
    script_dir = Path(__file__).resolve().parent
    target = script_dir / 'repo-check.py'
    args = [sys.executable, str(target), 'roles'] + sys.argv[1:]
    sys.exit(subprocess.run(args).returncode)


if __name__ == '__main__':
    main()
