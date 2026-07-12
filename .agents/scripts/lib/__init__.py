#!/usr/bin/env python3
"""lib/ — 验证脚本共享工具库

提供项目路径解析、TOML frontmatter 解析、CLI 输出格式化、Markdown 处理、
模式成熟度分析、链接修复、Spec 一致性检查、原子文件I/O、分阶段计时日志、
文件锁重试等跨脚本复用的基础函数。

## 使用方式

在 `.agents/scripts/` 下的脚本中直接导入：

```python
from lib.project import resolve_project_root
from lib.frontmatter import parse_toml_frontmatter, extract_frontmatter_field
from lib.cli import print_pass, print_warn, print_error, print_header, print_summary, add_common_args
from lib.markdown import find_markdown_files, extract_title, extract_description
from lib.link_fixer import fix_file_links, fix_directory_links, INLINE_LINK_RE
from lib.patterns import scan_patterns, find_upgrade_candidates, analyze_distribution
from lib.atomic_write import atomic_write_bytes, atomic_write_text, atomic_write_json, atomic_edit_text
from lib.io_safety import staged_timer, retry_on_lock, write_file_with_retry
from lib import spec
from lib import checks
```

**注意**：运行脚本时需确保工作目录或 sys.path 包含 `.agents/scripts/` 目录。
现有脚本通过在文件开头添加以下代码实现：
```python
import sys
from pathlib import Path
SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
```

## 模块索引
"""

import sys
import argparse
from pathlib import Path

if __package__ in (None, ""):
    SCRIPTS_DIR = Path(__file__).resolve().parents[1]
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))

from lib.project import resolve_project_root, resolve_agents_dir, resolve_scripts_dir
from lib.cli import print_pass, print_warn, print_error, print_header, print_summary, add_common_args
from lib.frontmatter import parse_toml_frontmatter, extract_frontmatter_field, extract_all_fields, parse_toml_frontmatter_as_dict, parse_yaml_frontmatter, extract_yaml_field, extract_frontmatter_field_from_file
from lib.markdown import find_markdown_files, extract_title, extract_description, parse_inline_links, update_marker_region
from lib.link_fixer import (
    LinkFix, fix_file_links, fix_directory_links, fix_link_url,
    find_file_in_project, compute_relative_path, apply_filename_mapping,
    apply_line_remap, print_fix_report, parse_file_url, is_code_fence_context,
    fix_broken_links, INLINE_LINK_RE,
)
from lib import patterns
from lib import spec
from lib import checks
from lib import rules
from lib import powershell
from lib import process
from lib import quality_rules
from lib import quality_report
from lib.api_docs import generate_api_docs, write_split_docs
from lib.atomic_write import (
    atomic_write_bytes, atomic_write_text, atomic_write_json, atomic_edit_text,
)
from lib.io_safety import staged_timer, retry_on_lock, write_file_with_retry
