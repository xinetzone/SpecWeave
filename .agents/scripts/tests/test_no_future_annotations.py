"""守护门禁：禁止 ``from __future__ import annotations``（PEP 563 样板）。

Python 3.14 起 PEP 649 默认惰性求值注解，该 future import 属冗余且语义有别；
代码生成与模板复制有语料惯性反复加回，故在测试层硬阻断——任何首方文件加回即红。

扫描口径与豁免判定统一由 ``lib.future_annotations`` 提供，与 pre-commit 钩子共用，
避免两处规则漂移。豁免范围（镜像技能 / 随附示例 / 非源码目录）见该模块 docstring。

检测基于 AST（只认真实 ``ImportFrom`` 节点），注释、文档字符串与本守护自身的
字符串常量均不误报。
"""

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPTS_DIR = _REPO_ROOT / ".agents" / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from lib.future_annotations import (  # noqa: E402
    has_future_annotations,
    iter_first_party_py_files,
)


@pytest.mark.parametrize(
    "path",
    iter_first_party_py_files(_REPO_ROOT),
    ids=lambda p: p.relative_to(_REPO_ROOT).as_posix(),
)
def test_no_future_annotations(path: Path) -> None:
    assert not has_future_annotations(path), (
        f"{path.relative_to(_REPO_ROOT).as_posix()} 含冗余的 PEP 563 future import；"
        "Python 3.14+ 已默认 PEP 649 惰性注解，直接删除该行"
        "（若注解引用后置定义的名字，改为字符串注解）"
    )


def test_exemption_does_not_swallow_first_party() -> None:
    """豁免机制自检：确保它不会把首方代码整体吃掉。"""
    scanned = iter_first_party_py_files(_REPO_ROOT)
    assert len(scanned) > 100, f"扫描面异常偏小（{len(scanned)}），豁免判定可能过宽"
    samples = {p.relative_to(_REPO_ROOT).as_posix() for p in scanned}
    assert ".agents/scripts/lib/frontmatter.py" in samples
    assert "apps/agent-monetize/src/agent_monetize/config.py" in samples
    assert not any(
        s.startswith(".agents/skills/") and "/local-" in s for s in samples
    )
