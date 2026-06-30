#!/usr/bin/env python3
"""大文件提交粒度检查工具。

检查Git提交的变更规模，对过大的提交给出拆分建议，
遵循"建议而非强制"原则——不阻断提交，但提醒开发者考虑拆分。

用法:
    python check-commit-size.py                    # 检查最近一次提交
    python check-commit-size.py --commit HEAD~3    # 检查指定提交
    python check-commit-size.py --threshold 800    # 自定义阈值（默认1000行）
    python check-commit-size.py --all              # 检查最近N次提交
    python check-commit-size.py --demo             # 演示模式

阈值分级:
    - < 500行: 理想粒度，原子性好
    - 500-1000行: 可接受，建议关注
    - 1000-2000行: 警告，建议按子模块拆分
    - > 2000行: 严重警告，强烈建议拆分

相关规范:
    提交粒度建议见 docs/retrospective/patterns/methodology-patterns/governance-strategy/session-boundary-commit.md
"""

import argparse
import subprocess
import sys
from pathlib import Path
from dataclasses import dataclass

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.cli import print_pass, print_warn, print_error, print_header, print_summary, setup_safe_output


@dataclass
class CommitStats:
    commit_hash: str
    subject: str
    total_insertions: int
    total_deletions: int
    total_changes: int
    files_changed: int
    large_files: list


def run_git_command(args: list[str]) -> str:
    try:
        result = subprocess.run(
            ['git'] + args,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print_error(f"Git命令执行失败: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print_error("未找到git命令，请确保Git已安装并在PATH中")
        sys.exit(1)


def get_commit_stats(commit_ref: str, file_threshold: int = 300) -> CommitStats:
    show_output = run_git_command([
        'show', '--stat', '--format=%H%n%s', commit_ref
    ])

    lines = show_output.strip().split('\n')
    if len(lines) < 2:
        print_error(f"无法解析提交 {commit_ref} 的信息")
        sys.exit(1)

    commit_hash = lines[0].strip()
    subject = lines[1].strip()

    total_insertions = 0
    total_deletions = 0
    files_changed = 0
    large_files = []

    for line in lines[2:]:
        line = line.strip()
        if not line:
            continue
        if 'files changed' in line or 'file changed' in line:
            import re
            fm = re.search(r'(\d+) files? changed', line)
            insm = re.search(r'(\d+) insertions?\(\+\)', line)
            delm = re.search(r'(\d+) deletions?\(-\)', line)
            if fm:
                files_changed = int(fm.group(1))
            if insm:
                total_insertions = int(insm.group(1))
            if delm:
                total_deletions = int(delm.group(1))
        elif '|' in line:
            parts = line.split('|')
            if len(parts) >= 2:
                fname = parts[0].strip()
                changes_str = parts[1].strip()
                import re
                cm = re.match(r'(\d+)', changes_str)
                if cm:
                    changes = int(cm.group(1))
                    if changes >= file_threshold:
                        large_files.append((fname, changes))

    total_changes = total_insertions + total_deletions

    return CommitStats(
        commit_hash=commit_hash[:8],
        subject=subject,
        total_insertions=total_insertions,
        total_deletions=total_deletions,
        total_changes=total_changes,
        files_changed=files_changed,
        large_files=large_files
    )


def analyze_commit(stats: CommitStats, threshold: int) -> tuple[str, list[str]]:
    warnings = []
    level = 'PASS'

    if stats.total_changes > 2000:
        level = 'ERROR'
        warnings.append(f"提交规模过大: {stats.total_changes}行变更（+{stats.total_insertions}/-{stats.total_deletions}），强烈建议拆分为多个原子提交")
    elif stats.total_changes > threshold:
        level = 'WARN'
        warnings.append(f"提交规模较大: {stats.total_changes}行变更（+{stats.total_insertions}/-{stats.total_deletions}），建议检查是否可以按子模块拆分")
    elif stats.total_changes > 500:
        level = 'INFO'
        warnings.append(f"提交规模: {stats.total_changes}行，可接受粒度")

    if stats.files_changed > 20:
        warnings.append(f"变更文件数过多: {stats.files_changed}个文件，建议按功能模块拆分提交")

    if stats.large_files:
        for fname, changes in stats.large_files:
            if changes > 500:
                warnings.append(f"  大文件: {fname} 变更{changes}行，考虑是否可分步修改")
                if level == 'PASS':
                    level = 'WARN'

    if stats.total_changes < 500 and len(warnings) == 0:
        warnings.append(f"提交粒度良好: {stats.total_changes}行变更（+{stats.total_insertions}/-{stats.total_deletions}），{stats.files_changed}个文件")

    return level, warnings


def main():
    setup_safe_output()
    parser = argparse.ArgumentParser(description='大文件提交粒度检查工具')
    parser.add_argument('--commit', type=str, default='HEAD', help='要检查的提交引用（默认HEAD）')
    parser.add_argument('--threshold', type=int, default=1000, help='警告阈值行数（默认1000）')
    parser.add_argument('--all', type=int, metavar='N', help='检查最近N次提交')
    parser.add_argument('--demo', action='store_true', help='演示模式')
    args = parser.parse_args()

    if args.demo:
        print_header("提交粒度检查 [DEMO MODE]")
        demo_commits = [
            ("abc12345", "feat(capabilities): 新增能力注册中心", 1250, 320, 8, [("capability-registry.md", 680)]),
            ("def67890", "fix(mermaid): 修复换行问题 [governance-loop]", 45, 12, 2, []),
            ("ghi11223", "feat(security): 新增五层数据安全治理体系", 3200, 890, 15, [("data-classification.md", 850), ("data-masking.md", 720)]),
        ]
        warn_count = 0
        pass_count = 0
        for h, subj, ins, dele, files, large in demo_commits:
            total = ins + dele
            stats = CommitStats(h, subj, ins, dele, total, files, large)
            level, warnings = analyze_commit(stats, args.threshold)
            print(f"\n  [{stats.commit_hash}] {stats.subject}")
            for w in warnings:
                if level == 'ERROR':
                    print_error(f"    {w}")
                    warn_count += 1
                elif level == 'WARN':
                    print_warn(f"    {w}")
                    warn_count += 1
                else:
                    print_pass(f"    {w}")
                    pass_count += 1
        print_summary(pass_count=pass_count, warn_count=warn_count, error_count=0)
        return 0

    if args.all:
        print_header(f"提交粒度检查（最近{args.all}次提交）")
        warn_count = 0
        pass_count = 0
        error_count = 0
        for i in range(args.all):
            ref = f'HEAD~{i}' if i > 0 else 'HEAD'
            try:
                stats = get_commit_stats(ref)
                level, warnings = analyze_commit(stats, args.threshold)
                print(f"\n  [{stats.commit_hash}] {stats.subject}")
                for w in warnings:
                    if level == 'ERROR':
                        print_error(f"    {w}")
                        error_count += 1
                    elif level == 'WARN':
                        print_warn(f"    {w}")
                        warn_count += 1
                    else:
                        print_pass(f"    {w}")
                        pass_count += 1
            except SystemExit:
                continue
        print_summary(pass_count=pass_count, warn_count=warn_count, error_count=error_count)
        return 0

    print_header(f"提交粒度检查: {args.commit}")
    stats = get_commit_stats(args.commit)
    level, warnings = analyze_commit(stats, args.threshold)

    print(f"\n  提交: {stats.commit_hash}")
    print(f"  主题: {stats.subject}")
    print(f"  变更: +{stats.total_insertions}/-{stats.total_deletions} = {stats.total_changes}行")
    print(f"  文件: {stats.files_changed}个")
    print()

    for w in warnings:
        if level == 'ERROR':
            print_error(f"  {w}")
        elif level == 'WARN':
            print_warn(f"  {w}")
        else:
            print_pass(f"  {w}")

    print()
    if level == 'ERROR' or level == 'WARN':
        print_warn("  提示: 本检查为建议性质，不强制阻断提交。拆分建议：")
        print_warn("    1. 按功能模块拆分：规范文档/检查脚本/运行时拦截分不同提交")
        print_warn("    2. 按四层递进拆分：B1规范→B2检测→C1拦截→C2可视化分提交")
        print_warn("    3. 遵循会话边界原则：单次提交只包含当前会话的变更")
        return 0 if level == 'WARN' else 1

    print_pass("  提交粒度符合建议标准")
    return 0


if __name__ == '__main__':
    sys.exit(main())
