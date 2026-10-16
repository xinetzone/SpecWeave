"""AST 守护：Python 源码禁止 `from __future__ import annotations`。

依据 SpecWeave Python 红线（AGENTS.md 开发规范）：PEP 563 是样板代码，
3.14 起 PEP 649 默认惰性注解，该导入冗余且语义有别。新建/修改 Python
项目须同步此守护测试，防止红线被无意引入。
"""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = (ROOT / "src", ROOT / "doc" / "conf.py", ROOT / "tests")


def _iter_python_files():
    for target in TARGETS:
        if target.is_file():
            yield target
            continue
        yield from sorted(target.rglob("*.py"))


def test_no_future_annotations() -> None:
    offenders: list[str] = []
    for path in _iter_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "__future__":
                names = {alias.name for alias in node.names}
                if "annotations" in names:
                    rel = path.relative_to(ROOT).as_posix()
                    offenders.append(f"{rel}:{node.lineno}")
    assert not offenders, "禁止 from __future__ import annotations：\n  - " + "\n  - ".join(offenders)


def test_guard_covers_source_tree() -> None:
    """守护本身要覆盖到源码，否则源文件搬家后守护会静默失效。"""
    files = list(_iter_python_files())
    assert any(p.parent.name == "info_butler" for p in files), "未覆盖 src/info_butler"
