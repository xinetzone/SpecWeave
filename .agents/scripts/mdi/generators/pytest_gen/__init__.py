"""pytest测试骨架生成器。

为Web API Profile生成pytest测试文件，包含正常场景、边界值和错误场景三类测试用例。
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[3]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from .generator import PytestGenerator
from .context import _TestContext

__all__ = ["PytestGenerator"]
