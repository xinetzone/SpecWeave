"""vendor 目录合规性检查包。

提供 vendor 目录的完整合规性检查功能，包括：
- .gitignore 规则检查
- 元数据文件完整性检查
- Git 子模块深度检查
- 非法导入检测
- 反向依赖检测
- pytest 配置隔离检查
"""

from __future__ import annotations

from .checks_base import _check_gitignore_rule, _check_lib_readme, _get_libs
from .checks_deps import (
    _check_pytest_excludes_vendor,
    _check_reverse_dependency,
    _find_pytest_configs,
)
from .checks_imports import _check_illegal_imports, _is_conditional_import
from .checks_submodule import (
    _check_branch_tracking,
    _check_submodule_clean,
    _check_submodule_initialized,
    _check_submodule_metadata,
)
from .cli import run
from .constants import (
    REQUIRED_LIB_FIELDS,
    REQUIRED_ROOT_FILES,
    VENDOR_LIB_README_TPL,
    VENDOR_README_TPL,
    VENDOR_VERSION_TPL,
)
from .git_ops import _is_submodule, _load_submodule_paths, _run_git
from .parser import (
    _extract_commit_from_version_entry,
    _get_submodule_type,
    _parse_version_md_for_submodule,
    _parse_version_md_table,
)
from .scanner import _scan_refs
from .templates import _create_templates

__all__ = [
    "REQUIRED_ROOT_FILES",
    "REQUIRED_LIB_FIELDS",
    "VENDOR_README_TPL",
    "VENDOR_VERSION_TPL",
    "VENDOR_LIB_README_TPL",
    "_check_gitignore_rule",
    "_load_submodule_paths",
    "_is_submodule",
    "_get_libs",
    "_check_lib_readme",
    "_scan_refs",
    "_parse_version_md_table",
    "_get_submodule_type",
    "_create_templates",
    "_run_git",
    "_check_submodule_initialized",
    "_check_submodule_clean",
    "_parse_version_md_for_submodule",
    "_extract_commit_from_version_entry",
    "_check_submodule_metadata",
    "_is_conditional_import",
    "_check_illegal_imports",
    "_check_reverse_dependency",
    "_check_branch_tracking",
    "_find_pytest_configs",
    "_check_pytest_excludes_vendor",
    "run",
]
