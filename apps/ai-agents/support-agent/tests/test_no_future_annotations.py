"""AST 守护：禁止 `from __future__ import annotations`（PEP 563 样板）。"""

import ast
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent.parent / "src"


def _python_files():
    return sorted(SRC_DIR.rglob("*.py"))


def test_source_tree_exists():
    assert _python_files(), "未找到源码文件，检查 src/ 目录"


def test_no_future_annotations_import():
    offenders = []
    for path in _python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "__future__":
                names = {alias.name for alias in node.names}
                if "annotations" in names:
                    offenders.append(f"{path}:{node.lineno}")
    assert not offenders, f"发现 PEP 563 样板导入：{offenders}"
