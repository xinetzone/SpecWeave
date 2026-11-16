"""PEP 563 样板检测共享库。

判定 ``from __future__ import annotations`` 是否存在于首方 Python 文件，并给出
豁免判定（镜像技能 / 随附示例 / 非源码目录）。供 pytest 守护门禁与 pre-commit
钩子共用，避免两处各写一套扫描规则导致口径漂移。

豁免按性质划分：

* 镜像技能：``SKILL.md`` frontmatter 的 ``source`` 以「镜像自」开头的技能目录，
  改动会破坏镜像保真，只能随上游更新；
* 随附示例：路径含 ``references`` 的外部文档示例代码，非运行路径；
* 非源码目录：``.venv`` / ``build`` / ``site-packages`` / ``node_modules`` /
  ``dist`` / ``upstream``（vendored 上游）/ 缓存目录。
"""

import ast
from pathlib import Path

SKIP_DIR_NAMES = frozenset(
    {
        ".venv",
        "build",
        "site-packages",
        "__pycache__",
        "node_modules",
        ".temp",
        ".pytest_cache",
        "dist",
        "upstream",
    }
)


def is_mirror_skill(path: Path, repo_root: Path) -> bool:
    """判断文件所属技能是否为镜像导入（source 含「镜像自」）。"""
    for parent in path.parents:
        skill_md = parent / "SKILL.md"
        if skill_md.is_file():
            try:
                text = skill_md.read_text(encoding="utf-8", errors="replace")
            except OSError:
                return False
            for line in text.splitlines():
                if line.startswith("source:"):
                    return "镜像自" in line
            return False
        if parent.name == "skills" or parent == repo_root:
            return False
    return False


def is_exempt(path: Path, repo_root: Path) -> bool:
    """判断文件是否落在豁免范围内。"""
    if SKIP_DIR_NAMES & set(path.parts):
        return True
    if "references" in path.parts:
        return True
    return is_mirror_skill(path, repo_root)


def has_future_annotations(path: Path) -> bool:
    """AST 检测模块顶层是否存在 ``from __future__ import annotations``。"""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError):
        return False
    for node in tree.body:
        if not isinstance(node, ast.ImportFrom) or node.module != "__future__":
            continue
        if any(alias.name == "annotations" for alias in node.names):
            return True
    return False


def iter_first_party_py_files(repo_root: Path) -> list[Path]:
    """枚举首方 Python 文件（``.agents/`` 与 ``apps/``，已剔除豁免项）。"""
    files: list[Path] = []
    for root in (repo_root / ".agents", repo_root / "apps"):
        for path in sorted(root.rglob("*.py")):
            if SKIP_DIR_NAMES & set(path.parts):
                continue
            if is_exempt(path, repo_root):
                continue
            files.append(path)
    return files
