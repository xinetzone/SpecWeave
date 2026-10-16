"""Python 3.14 红线：禁止 __future__ 导入（PEP 649 已默认惰性注解）。"""

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "doocs_md_py"


def test_no_future_imports():
    offenders = []
    for py_file in sorted(SRC.rglob("*.py")):
        tree = ast.parse(py_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "__future__":
                offenders.append(str(py_file))
    assert offenders == [], f"发现 __future__ 导入：{offenders}"


def test_redline_sample_is_caught(tmp_path):
    """红线有效性自检：含 __future__ 导入的样例必须能被检测到。"""
    sample = tmp_path / "sample.py"
    sample.write_text("from __future__ import annotations\n", encoding="utf-8")
    tree = ast.parse(sample.read_text(encoding="utf-8"))
    found = [n for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module == "__future__"]
    assert len(found) == 1
