""".agents/scripts/lib/ — 验证脚本共享工具库

提供项目路径解析、TOML frontmatter 解析、CLI 输出格式化等
跨脚本复用的基础函数。所有脚本均可通过：
    from lib.project import resolve_project_root
    from lib.frontmatter import parse_toml_frontmatter
    from lib.cli import print_pass, print_warn, print_error
    from lib.spec import parse_spec, parse_tasks, parse_checklist
等方式引用。
"""

from lib.project import resolve_project_root
from lib.frontmatter import parse_toml_frontmatter, extract_frontmatter_field, extract_all_fields
from lib.cli import (
    print_pass,
    print_warn,
    print_error,
    print_header,
    print_summary,
    add_common_args,
)
from lib.link_fixer import (
    LinkFix,
    fix_file_links,
    fix_directory_links,
    fix_link_url,
    find_file_in_project,
    compute_relative_path,
    apply_filename_mapping,
    apply_line_remap,
    print_fix_report,
    parse_file_url,
    is_code_fence_context,
    fix_broken_links,
)
from lib import spec
from lib import markdown
from lib.markdown import (
    find_markdown_files,
    extract_title,
    extract_description,
    parse_inline_links,
    update_marker_region,
)

__all__ = [
    "resolve_project_root",
    "parse_toml_frontmatter",
    "extract_frontmatter_field",
    "extract_all_fields",
    "print_pass",
    "print_warn",
    "print_error",
    "print_header",
    "print_summary",
    "add_common_args",
    "LinkFix",
    "fix_file_links",
    "fix_directory_links",
    "fix_link_url",
    "find_file_in_project",
    "compute_relative_path",
    "apply_filename_mapping",
    "apply_line_remap",
    "print_fix_report",
    "parse_file_url",
    "is_code_fence_context",
    "fix_broken_links",
    "spec",
    "markdown",
    "find_markdown_files",
    "extract_title",
    "extract_description",
    "parse_inline_links",
    "update_marker_region",
]
