"""`python -m agent_monetize` 入口。

零安装兜底：当包尚未 `pip install -e .` 时，尝试将 src/ 加入 sys.path，
使 `python -m agent_monetize demo` 在仓库目录内可直接运行。
"""

from __future__ import annotations

import os
import sys

_PKG_DIR = os.path.dirname(os.path.abspath(__file__))  # .../src/agent_monetize
_SRC_DIR = os.path.dirname(_PKG_DIR)  # .../src
if _SRC_DIR not in sys.path and os.path.isdir(_SRC_DIR):
    sys.path.insert(0, _SRC_DIR)

from .cli import main  # noqa: E402

if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
