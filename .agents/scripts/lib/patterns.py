"""模式成熟度共享工具库（薄入口垫片）。

三层架构实现已迁移至 pattern_maturity/ 子包。
本文件为薄入口垫片（thin-entry-shim模式），保持外部import路径100%不变。
"""

from lib.pattern_maturity.constants import (
    EXCLUDED_FILENAMES,
    MATURITY_LEVELS,
    PATTERN_DOMAINS,
    PATTERNS_DIR,
    README_INDEX_TABLE_RE,
    README_STATS_TABLE_RE,
    REQUIRED_FIELDS,
)
from lib.pattern_maturity.readme_ops import (
    check_stats_consistency,
    parse_readme_index_table,
    parse_readme_stats_table,
    update_readme_index_table,
)
from lib.pattern_maturity.scanner import (
    analyze_distribution,
    build_upgrade_stats,
    classify_pattern,
    count_patterns,
    find_upgrade_candidates,
    grep_maturity_per_directory,
    parse_pattern_frontmatter,
    scan_patterns,
)
from lib.pattern_maturity.scoring import build_report_data

__all__ = [
    "REQUIRED_FIELDS",
    "MATURITY_LEVELS",
    "PATTERN_DOMAINS",
    "EXCLUDED_FILENAMES",
    "PATTERNS_DIR",
    "README_STATS_TABLE_RE",
    "README_INDEX_TABLE_RE",
    "parse_pattern_frontmatter",
    "scan_patterns",
    "classify_pattern",
    "analyze_distribution",
    "find_upgrade_candidates",
    "build_upgrade_stats",
    "count_patterns",
    "grep_maturity_per_directory",
    "parse_readme_stats_table",
    "parse_readme_index_table",
    "check_stats_consistency",
    "update_readme_index_table",
    "build_report_data",
]
