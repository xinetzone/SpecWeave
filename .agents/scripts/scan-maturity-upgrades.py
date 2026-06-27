#!/usr/bin/env python3
"""模式成熟度偏差扫描脚本（薄包装层）。

此脚本已合并至 pattern-maturity.py scan-upgrades 子命令。
保留此文件以维持向后兼容，所有参数透传至 pattern-maturity.py scan-upgrades。

用法：
  python scan-maturity-upgrades.py [--all/-a] [--json/-j] [--path DIR]
等价于：
  python pattern-maturity.py scan-upgrades [--all/-a] [--json/-j] [--path DIR]
"""

import sys
import subprocess
from pathlib import Path


def main():
    script_dir = Path(__file__).resolve().parent
    target = script_dir / 'pattern-maturity.py'
    args = [sys.executable, str(target), 'scan-upgrades'] + sys.argv[1:]
    result = subprocess.run(args)
    sys.exit(result.returncode)


if __name__ == '__main__':
    main()
