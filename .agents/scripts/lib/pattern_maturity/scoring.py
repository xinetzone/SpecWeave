"""模式成熟度工具 - 评分计算与统计分析。"""

from typing import Any, Dict, List, Tuple

from lib.patterns import (
    analyze_distribution,
    build_report_data,
    build_upgrade_stats,
    classify_pattern,
    count_patterns,
    find_upgrade_candidates,
)


def calculate_distribution(patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """计算成熟度分布统计。"""
    return analyze_distribution(patterns)


def calculate_upgrade_stats(patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """计算升级候选统计。"""
    return build_upgrade_stats(patterns)


def generate_report_data(patterns: List[Dict[str, Any]], issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    """生成完整报告数据。"""
    return build_report_data(patterns, issues)


def classify_pattern_status(pattern: Dict[str, Any]) -> str:
    """分类模式状态（upgrade/anomaly/ok）。"""
    return classify_pattern(pattern)


def count_patterns_in_directory(directory) -> int:
    """统计目录中的模式文件数量。"""
    return count_patterns(directory)


def find_upgrade_candidates_list(patterns: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """查找待升级模式候选。"""
    return find_upgrade_candidates(patterns)


def calculate_summary_counts(
    total: int, upgrades: List[Any], anomalies: List[Any]
) -> Tuple[int, int, int]:
    """计算 pass/warn/error 统计。"""
    warn_count = len(upgrades)
    error_count = len(anomalies)
    pass_count = total - warn_count - error_count
    return pass_count, warn_count, error_count
