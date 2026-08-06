#!/usr/bin/env python3
"""Retrospective 体系索引一致性检查器（薄包装层）。

此脚本已合并至 pattern-maturity.py check-index 子命令。
保留此文件以维持向后兼容，所有参数透传至 pattern-maturity.py check-index。

用法:
    python check-retrospective-index.py              # 审计模式
    python check-retrospective-index.py --fix        # 修复模式
    python check-retrospective-index.py --verbose    # 详细模式
等价于:
    python pattern-maturity.py check-index [--fix] [--verbose]
"""


# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import sys
import subprocess
from pathlib import Path


def main():
    script_dir = Path(__file__).resolve().parent
    target = script_dir / 'pattern-maturity.py'
    args = [sys.executable, str(target), 'check-index'] + sys.argv[1:]
    result = subprocess.run(args)
    sys.exit(result.returncode)


if __name__ == "__main__":
    sys.exit(main())

