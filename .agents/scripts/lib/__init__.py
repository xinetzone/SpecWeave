""".agents/scripts/lib/ — 验证脚本共享工具库

提供项目路径解析、TOML frontmatter 解析、CLI 输出格式化等
跨脚本复用的基础函数。所有脚本均可通过：
    from lib.project import resolve_project_root
    from lib.frontmatter import parse_toml_frontmatter
    from lib.cli import print_pass, print_warn, print_error
等方式引用。
"""

from lib.project import resolve_project_root
from lib.frontmatter import parse_toml_frontmatter, extract_frontmatter_field
from lib.cli import (
    print_pass,
    print_warn,
    print_error,
    print_header,
    print_summary,
    add_common_args,
)

__all__ = [
    "resolve_project_root",
    "parse_toml_frontmatter",
    "extract_frontmatter_field",
    "print_pass",
    "print_warn",
    "print_error",
    "print_header",
    "print_summary",
    "add_common_args",
]
