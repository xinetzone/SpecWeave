"""Vercel Python 运行时入口。

Vercel 会在项目根自动探测 app.py / index.py / main.py 等入口文件，
并要求其中存在顶层变量 `app`（ASGI 应用）。

之所以在这里做 sys.path 注入：Vercel 按依赖清单安装第三方包，
但不会把本项目自身安装为可导入包，故需把 src/ 显式加入模块搜索路径。
本地用 `uvicorn app:app` 启动时同样受益于这段引导。
"""

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from okfqa.server import app  # noqa: E402  —— 必须先完成 sys.path 引导

__all__ = ["app"]
