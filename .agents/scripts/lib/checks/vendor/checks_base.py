"""vendor 基础检查模块。

.gitignore规则检查、依赖库列表获取、README元数据检查等基础功能。
"""

from __future__ import annotations

from pathlib import Path

from .constants import REQUIRED_LIB_FIELDS
from .git_ops import _is_submodule, _load_submodule_paths


def _check_gitignore_rule(project_root: Path) -> bool:
    """检查 .gitignore 是否已配置 vendor/ 忽略规则。"""
    gi = project_root / ".gitignore"
    if not gi.exists():
        return False
    content = gi.read_text(encoding="utf-8")
    return "vendor/" in content or "vendor/*" in content


def _get_libs(vendor_dir: Path, submodule_paths: set[str] | None = None) -> list[Path]:
    """获取 vendor 目录下手动管理的依赖库列表（排除子模块）。"""
    if not vendor_dir.exists():
        return []
    project_root = vendor_dir.parent
    if submodule_paths is None:
        submodule_paths = _load_submodule_paths(project_root)
    libs = []
    for p in sorted(vendor_dir.iterdir(), key=lambda p: p.name):
        if not p.is_dir() or p.name.startswith("."):
            continue
        if _is_submodule(p, project_root, submodule_paths):
            continue
        libs.append(p)
    return libs


def _check_lib_readme(lib_dir: Path) -> tuple[bool, list[str]]:
    """检查单个依赖库的 README.md 元数据完整性。"""
    readme = lib_dir / "README.md"
    issues = []
    if not readme.exists():
        return False, ["缺少 README.md 元数据文件"]
    content = readme.read_text(encoding="utf-8")
    for field in REQUIRED_LIB_FIELDS:
        if field not in content:
            issues.append(f"README.md 缺少必需字段：{field}")
    return len(issues) == 0, issues
