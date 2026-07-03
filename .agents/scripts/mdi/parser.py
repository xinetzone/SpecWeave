"""MDI Markdown Interface Parser（薄入口垫片）。

三层架构实现已迁移至 parser_core/ 子包。
本文件为薄入口垫片（thin-entry-shim模式），保持外部import路径100%不变。
"""
from .parser_core import MDIParser

__all__ = ["MDIParser"]
