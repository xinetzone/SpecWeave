"""Markdown 链接修复工具包。

提供检测和修复 Markdown 文档中断链的能力，核心功能：
- 检测 file:/// 本地绝对路径链接
- 将绝对路径自动转换为正确的相对路径
- 修复相对路径深度错误（文件/目录重构后）
- 处理原子化目录引用（xxx.md → xxx/ 目录形式）
- 处理同文件自引用（简化为纯锚点）
- 支持文件名映射（文件重命名场景）
- 支持行号偏移映射（内容移位场景）
- 自动跳过代码块内的示例链接
- 自动跳过模板占位符链接
- Dry-run 模式预览变更不写入

典型用法：
    from lib.link_fixer import fix_directory_links

    rename_map = {"竹简悟道.html": "竹简悟道_完整版.html"}
    fixes = fix_directory_links(
        root_dir=Path("apps/zhujian-wudao"),
        project_root=Path("."),
        rename_map=rename_map,
        dry_run=True,
    )
"""

from .constants import (
    FILE_URL_RE,
    INLINE_LINK_RE,
    TEMPLATE_LINK_TEXTS,
    TEMPLATE_URL_PATTERNS,
)
from .models import LinkFix
from .utils import (
    apply_filename_mapping,
    apply_line_remap,
    compute_relative_path,
    extract_filename_from_url,
    is_code_fence_context,
    is_template_link,
    os_path_to_posix,
    parse_file_url,
)
from .finder import (
    _extract_search_terms,
    _find_all_matches,
    _is_excluded_path,
    _try_root_based_path,
    find_file_in_project,
    find_target_by_stem,
)
from .depth import try_adjust_relative_depth
from .resolver import fix_link_url
from .processor import fix_directory_links, fix_file_links
from .report import print_fix_report
from .cli import _infer_project_root, fix_broken_links, main

__all__ = [
    "FILE_URL_RE",
    "INLINE_LINK_RE",
    "TEMPLATE_LINK_TEXTS",
    "TEMPLATE_URL_PATTERNS",
    "LinkFix",
    "parse_file_url",
    "extract_filename_from_url",
    "os_path_to_posix",
    "compute_relative_path",
    "apply_filename_mapping",
    "apply_line_remap",
    "is_template_link",
    "is_code_fence_context",
    "find_file_in_project",
    "find_target_by_stem",
    "try_adjust_relative_depth",
    "fix_link_url",
    "fix_file_links",
    "fix_directory_links",
    "print_fix_report",
    "fix_broken_links",
    "main",
]
