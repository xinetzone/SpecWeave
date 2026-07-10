"""模式成熟度工具 - 评分计算与统计分析。"""

from typing import Any

from .constants import MATURITY_LEVELS
from .scanner import (
    analyze_distribution,
    build_upgrade_stats,
    classify_pattern,
    count_patterns,
    find_upgrade_candidates,
)


def calculate_distribution(patterns: list[dict[str, Any]]) -> dict[str, Any]:
    """计算成熟度分布统计。"""
    return analyze_distribution(patterns)


def calculate_upgrade_stats(patterns: list[dict[str, Any]]) -> dict[str, Any]:
    """计算升级候选统计。"""
    return build_upgrade_stats(patterns)


def build_report_data(patterns, issues):
    """构建统一报告数据（供 stats 子命令使用）。

    Returns:
        包含 total/maturity/domains/upgrade_candidates/patterns/issues 的字典。
    """
    stats, domain_stats = analyze_distribution(patterns)
    candidates = find_upgrade_candidates(patterns)

    return {
        'total': stats['total'],
        'maturity': {level: stats['maturity'].get(level, 0) for level in MATURITY_LEVELS},
        'domains': {
            domain: domain_stats.get(domain, {'total': 0, 'L1': 0, 'L2': 0, 'L3': 0, 'L4': 0})
            for domain in ['methodology', 'code', 'architecture']
        },
        'upgrade_candidates': {
            key: [p['id'] for p in value]
            for key, value in candidates.items()
        },
        'patterns': sorted(patterns, key=lambda x: (x.get('domain', ''), x.get('id', ''))),
        'issues': issues,
    }


def generate_report_data(patterns: list[dict[str, Any]], issues: list[dict[str, Any]]) -> dict[str, Any]:
    """生成完整报告数据。"""
    return build_report_data(patterns, issues)


def classify_pattern_status(pattern: dict[str, Any]) -> str:
    """分类模式状态（upgrade/anomaly/ok）。"""
    return classify_pattern(pattern)


def count_patterns_in_directory(directory) -> int:
    """统计目录中的模式文件数量。"""
    return count_patterns(directory)


def find_upgrade_candidates_list(patterns: list[dict[str, Any]]) -> dict[str, list[str]]:
    """查找待升级模式候选。"""
    return find_upgrade_candidates(patterns)


def calculate_summary_counts(
    total: int, upgrades: list[Any], anomalies: list[Any]
) -> tuple[int, int, int]:
    """计算 pass/warn/error 统计。"""
    warn_count = len(upgrades)
    error_count = len(anomalies)
    pass_count = total - warn_count - error_count
    return pass_count, warn_count, error_count
