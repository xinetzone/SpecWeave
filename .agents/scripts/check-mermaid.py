#!/usr/bin/env python3
"""向后兼容包装：check-mermaid.py → repo-check.py mermaid。"""


# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import os
import subprocess
import sys
from pathlib import Path


def main():
    script_dir = Path(__file__).resolve().parent
    target = script_dir / 'repo-check.py'
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    args = [sys.executable, '-X', 'utf8', str(target), 'mermaid'] + sys.argv[1:]
    sys.exit(subprocess.run(args, env=env).returncode)


if __name__ == '__main__':
    main()

