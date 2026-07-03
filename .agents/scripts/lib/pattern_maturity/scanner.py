"""模式成熟度工具 - 模式扫描、分类与分布统计。"""

from collections import defaultdict
from pathlib import Path

from lib.cli import print_warn
from lib.frontmatter import parse_frontmatter_unified

from .constants import (
    EXCLUDED_FILENAMES,
    MATURITY_LEVELS,
    PATTERN_DOMAINS,
    REQUIRED_FIELDS,
)


def parse_pattern_frontmatter(filepath: str | Path) -> dict | None:
    """解析模式文件的 frontmatter，返回结构化字典。

    自动识别 TOML(+++) 和 YAML(---) + x-toml-ref 格式。

    Args:
        filepath: .md 文件路径。

    Returns:
        包含 string 字段和 int 字段的字典；无 frontmatter 时返回 None。
    """
    fields = parse_frontmatter_unified(filepath)
    if not fields:
        return None

    result = {}

    string_fields = ['id', 'domain', 'layer', 'maturity', 'documentation_level', 'source']
    for field in string_fields:
        value = fields.get(field)
        if value is not None:
            result[field] = str(value)

    int_fields = ['validation_count', 'reuse_count']
    for field in int_fields:
        value = fields.get(field)
        if value is not None:
            try:
                result[field] = int(str(value))
            except (ValueError, TypeError):
                result[field] = 0

    return result


def scan_patterns(base_dir):
    """扫描指定目录下所有模式文件，返回统一的模式列表和问题列表。

    此函数统一了原 pattern-maturity-stats.py 和 scan-maturity-upgrades.py
    中各自实现的 scan_patterns()，消除重复代码。
    支持递归扫描子目录（methodology-patterns 下按主题分7个子目录）。

    Args:
        base_dir: 模式文件根目录（包含三个子域目录）。

    Returns:
        (patterns, issues) 元组：
        - patterns: [{"filepath": str, "domain": str, "id": str, "maturity": str,
                      "validation_count": int, "reuse_count": int, ...}, ...]
        - issues: [{"type": str, "path": str, "message": str, "fields"?: list}, ...]
    """
    patterns = []
    issues = []
    base_path = Path(base_dir)

    for domain_dir in PATTERN_DOMAINS:
        domain_path = base_path / domain_dir
        if not domain_path.is_dir():
            issues.append({
                'type': 'missing_directory',
                'path': str(domain_path),
                'message': '模式目录不存在',
            })
            continue

        for md_path in sorted(domain_path.rglob('*.md')):
            filepath = str(md_path)
            if md_path.name in EXCLUDED_FILENAMES or md_path.name == 'CATEGORIES.md':
                continue

            fm = parse_pattern_frontmatter(filepath)
            if not fm:
                issues.append({
                    'type': 'missing_frontmatter',
                    'path': filepath,
                    'message': '缺少 frontmatter',
                })
                continue

            missing_fields = [f for f in REQUIRED_FIELDS if f not in fm]
            if missing_fields:
                issues.append({
                    'type': 'missing_fields',
                    'path': filepath,
                    'message': f"缺少字段: {', '.join(missing_fields)}",
                    'fields': missing_fields,
                })

            fm['filepath'] = filepath
            fm['domain'] = domain_dir.replace('-patterns', '')
            fm['file'] = str(md_path.relative_to(base_path))
            patterns.append(fm)

    return patterns, issues


def classify_pattern(pattern):
    """根据 auto-generate-threshold 规则分类单个模式的状态。

    Args:
        pattern: scan_patterns 返回的单个模式字典。

    Returns:
        "upgrade": 应升级（validation_count >= 2 且 maturity = L1）
        "anomaly": 异常（validation_count = 1 但 maturity >= L2）
        "ok": 状态一致
    """
    vc = pattern.get('validation_count', 0)
    maturity = pattern.get('maturity', 'unknown')

    if vc >= 2 and maturity == 'L1':
        return 'upgrade'
    elif vc == 1 and maturity in ('L2', 'L3', 'L4'):
        return 'anomaly'
    else:
        return 'ok'


def analyze_distribution(patterns):
    """分析模式成熟度分布。

    Args:
        patterns: scan_patterns 返回的模式列表。

    Returns:
        (stats, domain_stats) 元组。
    """
    stats = {
        'maturity': defaultdict(int),
        'domain': defaultdict(int),
        'total': 0,
    }
    domain_stats = defaultdict(lambda: {'total': 0, 'L1': 0, 'L2': 0, 'L3': 0, 'L4': 0})

    for pattern in patterns:
        maturity = pattern.get('maturity', 'unknown')
        domain = pattern.get('domain', 'unknown')

        stats['maturity'][maturity] += 1
        stats['domain'][domain] += 1
        stats['total'] += 1

        domain_stats[domain]['total'] += 1
        if maturity in MATURITY_LEVELS:
            domain_stats[domain][maturity] += 1

    return stats, domain_stats


def find_upgrade_candidates(patterns):
    """找出待升级模式。

    L1 且 validation_count >= 2 → 应升级到 L2
    L2 且 reuse_count >= 1 → 应升级到 L3

    Args:
        patterns: scan_patterns 返回的模式列表。

    Returns:
        {'L1_to_L2': [...], 'L2_to_L3': [...]}
    """
    candidates = {
        'L1_to_L2': [],
        'L2_to_L3': [],
    }

    for pattern in patterns:
        maturity = pattern.get('maturity', '')
        validation_count = pattern.get('validation_count', 0)
        reuse_count = pattern.get('reuse_count', 0)

        if maturity == 'L1' and validation_count >= 2:
            candidates['L1_to_L2'].append(pattern)
        elif maturity == 'L2' and reuse_count >= 1:
            candidates['L2_to_L3'].append(pattern)

    return candidates


def build_upgrade_stats(patterns):
    """构建偏差扫描统计（来自 scan-maturity-upgrades 的 build_stats）。

    Returns:
        {'total': int, 'maturity_counts': dict, 'validation_total': int,
         'avg_validation': float, 'upgrades': [...], 'anomalies': [...]}
    """
    total = len(patterns)
    maturity_counts = {}
    validation_total = 0
    upgrades = []
    anomalies = []

    for p in patterns:
        m = p.get('maturity', 'unknown')
        maturity_counts[m] = maturity_counts.get(m, 0) + 1
        validation_total += p.get('validation_count', 0)

        status = classify_pattern(p)
        if status == 'upgrade':
            upgrades.append(p)
        elif status == 'anomaly':
            anomalies.append(p)

    return {
        'total': total,
        'maturity_counts': maturity_counts,
        'validation_total': validation_total,
        'avg_validation': round(validation_total / total, 1) if total > 0 else 0,
        'upgrades': upgrades,
        'anomalies': anomalies,
    }


def count_patterns(dir_path):
    """统计目录中除 README.md/CATEGORIES.md 外的 .md 文件数（递归扫描子目录）。"""
    if not dir_path.exists():
        return 0
    return len([
        f for f in dir_path.rglob('*.md')
        if f.name not in EXCLUDED_FILENAMES and f.name != 'CATEGORIES.md'
    ])


def grep_maturity_per_directory(patterns_root):
    """遍历模式目录，从各文件 frontmatter 中统计 maturity 字段并按目录汇总。
    支持递归扫描子目录（methodology-patterns 下按主题分7个子目录）。

    Args:
        patterns_root: patterns/ 目录的 Path 对象。

    Returns:
        {"architecture-patterns": {"L1": N, "L2": N, "L3": N, "L4": N, "_total": N}, ...}
    """
    dir_maturity = {}

    for dir_name in PATTERN_DOMAINS:
        dir_path = patterns_root / dir_name
        if not dir_path.is_dir():
            continue

        counts = {f'L{i}': 0 for i in range(1, 5)}
        pattern_count = 0

        for md_file in sorted(dir_path.rglob('*.md')):
            if md_file.name in EXCLUDED_FILENAMES or md_file.name == 'CATEGORIES.md':
                continue
            fields = parse_frontmatter_unified(md_file)
            if not fields:
                continue
            level = fields.get('maturity')
            if level is not None:
                level = str(level)
            if level in counts:
                counts[level] += 1
                pattern_count += 1

        counts['_total'] = pattern_count
        dir_maturity[dir_name] = counts

    return dir_maturity
