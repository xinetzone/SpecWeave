#!/usr/bin/env python3
"""模式库成熟度分布统计脚本（薄包装层）。

此脚本已合并至 pattern-maturity.py stats 子命令。
保留此文件以维持向后兼容，所有参数透传至 pattern-maturity.py stats。

用法：
  python pattern-maturity-stats.py [base_dir] [--format text|json|markdown] [--check]
等价于：
  python pattern-maturity.py stats [base_dir] [--format text|json|markdown] [--check]
"""

import sys
import subprocess
from pathlib import Path


def main():
    script_dir = Path(__file__).resolve().parent
    target = script_dir / 'pattern-maturity.py'
    args = [sys.executable, str(target), 'stats'] + sys.argv[1:]
    result = subprocess.run(args)
    sys.exit(result.returncode)


if __name__ == '__main__':
    main()
