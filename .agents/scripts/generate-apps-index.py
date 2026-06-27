#!/usr/bin/env python3
"""向后兼容包装：generate-apps-index.py → docgen.py apps。"""

import subprocess
import sys
from pathlib import Path


def main():
    script_dir = Path(__file__).resolve().parent
    target = script_dir / 'docgen.py'
    args = [sys.executable, str(target), 'apps'] + sys.argv[1:]
    sys.exit(subprocess.run(args).returncode)


if __name__ == '__main__':
    main()
