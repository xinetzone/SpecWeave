#!/usr/bin/env python3
"""可信度标记统计工具。

扫描Markdown文件中的可信度标记（🟢🔵🟡🔴 + A/B/C/D等级）和异常标记（⚠️❓⚖️🔍），
生成统计报告。用于对抗性审查知识库等研究类文档的质量自检。

用法:
    python credibility-stats.py <directory>
    python credibility-stats.py docs/knowledge/learning/02-agent-engineering-methodology/adversarial-review-wiki/
    python credibility-stats.py <file.md>
    python credibility-stats.py <dir> --threshold 60  # 设置🟢A级占比阈值，低于则报错

标记格式说明:
    🟢A级 / 🟢A  — 多源交叉验证，高可信
    🔵B级 / 🔵B  — 单一权威来源，中可信
    🟡C级 / 🟡C  — 待验证，低可信
    🔴D级 / 🔴D  — 存疑/排除，不可信
    ⚠️  — 待验证标记
    ❓  — 存疑标记
    ⚖️  — 争议观点标记
    🔍  — 利益冲突标记
"""

import argparse
import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.cli import print_pass, print_warn, print_error, print_header

CREDIBILITY_PATTERNS = {
    '🟢A': re.compile(r'🟢\s*A[级]?'),
    '🔵B': re.compile(r'🔵\s*B[级]?'),
    '🟡C': re.compile(r'🟡\s*C[级]?'),
    '🔴D': re.compile(r'🔴\s*D[级]?'),
}

ANOMALY_PATTERNS = {
    '⚠️待验证': re.compile(r'⚠️'),
    '❓存疑': re.compile(r'❓'),
    '⚖️争议': re.compile(r'⚖️'),
    '🔍利益冲突': re.compile(r'🔍'),
}


def scan_file(file_path: Path) -> dict:
    """扫描单个文件，返回可信度标记统计。"""
    try:
        content = file_path.read_text(encoding='utf-8')
    except (OSError, UnicodeDecodeError):
        return None

    result = {
        'file': str(file_path),
        'counts': {k: 0 for k in CREDIBILITY_PATTERNS},
        'anomalies': {k: 0 for k in ANOMALY_PATTERNS},
        'total_credibility': 0,
    }

    for label, pattern in CREDIBILITY_PATTERNS.items():
        matches = pattern.findall(content)
        result['counts'][label] = len(matches)
        result['total_credibility'] += len(matches)

    for label, pattern in ANOMALY_PATTERNS.items():
        matches = pattern.findall(content)
        result['anomalies'][label] = len(matches)

    return result


def scan_directory(dir_path: Path) -> list[dict]:
    """递归扫描目录下所有Markdown文件。"""
    results = []
    for md_file in sorted(dir_path.rglob('*.md')):
        result = scan_file(md_file)
        if result:
            results.append(result)
    return results


def compute_totals(results: list[dict]) -> dict:
    """计算汇总统计。"""
    totals = {
        'total_files': len(results),
        'credibility': {k: 0 for k in CREDIBILITY_PATTERNS},
        'anomalies': {k: 0 for k in ANOMALY_PATTERNS},
        'total_credibility': 0,
        'files_with_marks': 0,
        'by_file': [],
    }

    for r in results:
        has_marks = r['total_credibility'] > 0 or any(v > 0 for v in r['anomalies'].values())
        if has_marks:
            totals['files_with_marks'] += 1
            totals['by_file'].append(r)

        for label, count in r['counts'].items():
            totals['credibility'][label] += count
            totals['total_credibility'] += count
        for label, count in r['anomalies'].items():
            totals['anomalies'][label] += count

    return totals


def print_report(totals: dict, threshold: int | None = None):
    """打印统计报告。"""
    print_header("可信度标记统计")
    print(f"  扫描文件: {totals['total_files']} 个")
    print(f"  含标记文件: {totals['files_with_marks']} 个")
    print()

    if totals['total_credibility'] == 0:
        print_warn("未检测到可信度标记（🟢🔵🟡🔴）")
        return

    print("【可信度分布】")
    total = totals['total_credibility']
    for label in ['🟢A', '🔵B', '🟡C', '🔴D']:
        count = totals['credibility'][label]
        pct = count / total * 100 if total > 0 else 0
        bar = '█' * int(pct / 2)
        print(f"  {label}级: {count:4d} ({pct:5.1f}%) {bar}")
    print(f"  合计:   {total:4d} (100.0%)")
    print()

    if threshold is not None:
        a_pct = totals['credibility']['🟢A'] / total * 100 if total > 0 else 0
        if a_pct < threshold:
            print_error(f"🟢A级占比{a_pct:.1f}%低于阈值{threshold}%，质量不达标")
        else:
            print_pass(f"🟢A级占比{a_pct:.1f}%达标（≥{threshold}%）")

        d_count = totals['credibility']['🔴D']
        if d_count > 0:
            print_error(f"存在🔴D级内容{d_count}处，必须排除")
        else:
            print_pass("无🔴D级内容")
    print()

    if any(v > 0 for v in totals['anomalies'].values()):
        print("【异常标记统计】")
        for label, count in totals['anomalies'].items():
            if count > 0:
                print(f"  {label}: {count} 处")
        print()

    if totals['by_file']:
        print("【各文件明细】")
        for r in totals['by_file']:
            name = Path(r['file']).name
            parts = []
            for label in ['🟢A', '🔵B', '🟡C', '🔴D']:
                c = r['counts'][label]
                if c > 0:
                    parts.append(f"{label}:{c}")
            anom_parts = []
            for label, count in r['anomalies'].items():
                if count > 0:
                    short = label.split('（')[0].split(':')[0]
                    anom_parts.append(f"{short}:{count}")
            detail = ' '.join(parts)
            if anom_parts:
                detail += f" | 异常:{' '.join(anom_parts)}"
            print(f"  {name:40s} {detail}")


def main():
    parser = argparse.ArgumentParser(
        description='可信度标记统计 - 扫描Markdown文件中的🟢🔵🟡🔴可信度标记和⚠️❓⚖️🔍异常标记',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s adversarial-review-wiki/
  %(prog)s docs/knowledge/ --threshold 60
        """
    )
    parser.add_argument('path', help='要扫描的文件或目录')
    parser.add_argument('--threshold', type=int, default=None,
                        help='🟢A级占比阈值（%%），低于此值返回非零退出码')
    args = parser.parse_args()

    target = Path(args.path)
    if not target.exists():
        print_error(f"路径不存在: {target}")
        return 1

    if target.is_file():
        results = [scan_file(target)]
        results = [r for r in results if r]
    else:
        results = scan_directory(target)

    if not results:
        print_warn("未找到可扫描的Markdown文件")
        return 0

    totals = compute_totals(results)
    print_report(totals, args.threshold)

    if args.threshold is not None and totals['total_credibility'] > 0:
        a_pct = totals['credibility']['🟢A'] / totals['total_credibility'] * 100
        d_count = totals['credibility']['🔴D']
        if a_pct < args.threshold or d_count > 0:
            return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
