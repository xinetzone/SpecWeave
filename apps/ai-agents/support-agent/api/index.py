"""Vercel Serverless 入口：导出 ASGI 应用 `app`。"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from support_agent.asgi import build_app  # noqa: E402

app = build_app()
