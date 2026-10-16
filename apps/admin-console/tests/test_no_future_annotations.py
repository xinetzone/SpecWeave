"""AST 守护：Python 红线——禁止 `from __future__ import annotations`。

参照 apps/dev-tools/zhihu-checkin-hub/tests/test_no_future_annotations.py，
PEP 563 样板在 3.14（PEP 649 默认惰性注解）下冗余且语义有别。
"""

import ast
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parent.parent / "src"
API_ROOT = Path(__file__).resolve().parent.parent / "api"
SCRIPTS_ROOT = Path(__file__).resolve().parent.parent / "scripts"


def _iter_python_files():
    for root in (SRC_ROOT, API_ROOT, SCRIPTS_ROOT):
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.py")):
            yield path


def test_no_future_imports():
    offenders = []
    for path in _iter_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "__future__":
                offenders.append(f"{path}:{node.lineno}")
    assert not offenders, f"发现 from __future__ 导入：{offenders}"


def test_sources_parse():
    files = list(_iter_python_files())
    assert files, "未找到任何源码文件"
    for path in files:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
