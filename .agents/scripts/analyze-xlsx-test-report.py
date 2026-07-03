#!/usr/bin/env python3
"""解析 .xlsx 测试报告并导出 Markdown 报告。"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.analyze_xlsx import main

if __name__ == "__main__":
    sys.exit(main())
