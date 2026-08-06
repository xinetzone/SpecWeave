"""pytest测试骨架生成器。

为Web API Profile生成pytest测试文件，包含正常场景、边界值和错误场景三类测试用例。
"""

from __future__ import annotations


# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_lib_parent = _Path(__file__).resolve().parent
while not (_lib_parent / "lib").is_dir():
    _lib_parent = _lib_parent.parent
_sys.path.insert(0, str(_lib_parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[3]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from .generator import PytestGenerator
from .context import _TestContext

__all__ = ["PytestGenerator"]
