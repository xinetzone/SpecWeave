#!/usr/bin/env python3
"""sensitive-info-check: 敏感信息脱敏检查独立 CLI 工具。

用法:
    python check-sensitive-info.py                  # 默认扫描
    python check-sensitive-info.py --fix            # 自动修复可脱敏问题
    python check-sensitive-info.py --json           # JSON 格式输出
    python check-sensitive-info.py --help           # 查看完整帮助

底层调用 lib.checks.sensitive_info.main()。
"""


# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import sys
from pathlib import Path

script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))

from lib.checks.sensitive_info import main

if __name__ == "__main__":
    sys.exit(main())

