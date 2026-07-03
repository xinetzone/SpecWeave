#!/usr/bin/env python3
"""generate-sg-dashboard.py — 阶段守卫日志聚合可视化仪表盘生成工具（入口垫片）。

实际实现在 sg_dashboard/ 包中，此文件仅作CLI入口转发。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sg_dashboard.cli import main

if __name__ == "__main__":
    sys.exit(main())
