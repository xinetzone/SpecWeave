#!/usr/bin/env python3
"""vendor-check: vendor 目录合规性检查独立 CLI 工具。

用法:
    python check-vendor.py                  # 默认检查（基础5项）
    python check-vendor.py --fix            # 自动创建缺失的标准模板文件
    python check-vendor.py --scan-refs      # 扫描代码中对 vendor/ 目录的引用
    python check-vendor.py --deep           # 子模块深度集成验证
    python check-vendor.py --json           # JSON 格式输出结果
    python check-vendor.py --help           # 查看完整帮助

底层调用 lib.checks.vendor.main()，保持与 repo-check.py vendor 子命令兼容。
"""

import sys
from pathlib import Path

script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))

from lib.checks.vendor import main

if __name__ == "__main__":
    sys.exit(main())
