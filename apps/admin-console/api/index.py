"""Vercel Serverless 入口：导出 ASGI 应用。

Vercel Python Runtime 会查找模块级可调用对象（app / handler / 单参数 ASGI 可调用）。
此处显式导出 `app`，并把仓库根目录加入 sys.path 以便导入 src/ 下的包。
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
for _candidate in (_ROOT / "src", _ROOT):
    _path = str(_candidate)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from admin_console.asgi import build_app  # noqa: E402

app = build_app()
