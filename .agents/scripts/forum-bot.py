#!/usr/bin/env python3
"""forum-bot.py — forum.trae.cn 论坛自动化操作工具（入口垫片）。

实际实现在 forum_bot/ 包中，此文件仅作CLI入口转发。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from forum_bot.cli import main

if __name__ == "__main__":
    main()
