#!/usr/bin/env python3
"""forum-bot.py — forum.trae.cn 论坛自动化操作工具（入口垫片）。

实际实现在 forum_bot/ 包中，此文件仅作CLI入口转发。
"""


# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from forum_bot.cli import main

if __name__ == "__main__":
    main()

