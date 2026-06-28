#!/usr/bin/env python3
"""向后兼容包装：check-mermaid.py → repo-check.py mermaid。"""

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
