"""MDI Markdown Interface Parser（薄入口垫片）。

三层架构实现已迁移至 parser_core/ 子包。
本文件为薄入口垫片（thin-entry-shim模式），保持外部import路径100%不变。
"""

# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_lib_parent = _Path(__file__).resolve().parent
while not (_lib_parent / "lib").is_dir():
    _lib_parent = _lib_parent.parent
_sys.path.insert(0, str(_lib_parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

from .parser_core import MDIParser

__all__ = ["MDIParser"]

