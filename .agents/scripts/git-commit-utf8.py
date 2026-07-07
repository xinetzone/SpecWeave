#!/usr/bin/env python3
"""Windows Git UTF-8 提交工具。

解决Windows简体中文环境下GBK终端通过`git commit -m "中文"`
产生乱码的问题。核心原理：通过stdin bytes通道传递commit message，
完全绕过shell和Git命令行参数的编码转换。

用法:
    python git-commit-utf8.py -m "feat: 新增功能"           # 提交已暂存文件
    python git-commit-utf8.py -F commit-msg.txt            # 从文件读取message
    python git-commit-utf8.py -m "修复Bug" file1.py file2.py  # add+commit指定文件
    python git-commit-utf8.py --auto -m "纯英文"           # 自动检测（纯ASCII走普通路径）
    echo "feat: xxx" | python git-commit-utf8.py --stdin   # 从stdin读取

设计原则:
    1. 安全优先：不绕过任何Git钩子或权限检查
    2. 自动检测：非ASCII字符自动走bytes通道，纯ASCII走普通路径（零开销）
    3. 文件隔离：指定files时只提交这些文件，不混入其他已暂存变更
    4. 向后兼容：支持所有git commit的常见参数(-a, --amend等透传)
    5. 诊断友好：错误时输出详细的编码诊断信息

相关规范:
    docs/retrospective/patterns/methodology-patterns/development/git-utf8-commit.md
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.cli import print_pass, print_warn, print_error, print_header, setup_safe_output


def contains_non_ascii(text: str) -> bool:
    """检测文本是否包含非ASCII字符。"""
    try:
        text.encode('ascii')
        return False
    except UnicodeEncodeError:
        return True


def read_message_from_file(filepath: Path) -> str:
    """从文件读取commit message，自动检测编码。"""
    encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'cp936']
    for enc in encodings:
        try:
            return filepath.read_text(encoding=enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    print_error(f"无法解码文件 {filepath}，尝试的编码: {', '.join(encodings)}")
    sys.exit(1)


def read_message_from_stdin() -> str:
    """从stdin读取commit message（字节模式）。"""
    raw = sys.stdin.buffer.read()
    for enc in ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']:
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    print_error("无法解码stdin输入，请确保使用UTF-8编码")
    sys.exit(1)


def run_git_add(files: list[str]) -> None:
    """执行git add，将指定文件（包括untracked新文件）加入暂存区。"""
    if not files:
        return
    result = subprocess.run(
        ['git', 'add'] + files,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    if result.returncode != 0:
        print_error(f"git add 失败: {result.stderr}")
        sys.exit(1)


def check_staged_matches(files: list[str]) -> bool:
    """检查暂存区是否只包含指定文件，无其他预存暂存变更。"""
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only'],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    if result.returncode != 0:
        return False
    staged = set(f for f in result.stdout.strip().split('\n') if f)
    expected = set(files)
    return staged == expected


def commit_via_bytes(message: str, extra_args: list[str]) -> int:
    """通过stdin bytes通道提交（UTF-8安全模式）。

    使用`git commit -F -`从stdin读取message，通过stdin.buffer.write
    写入原始UTF-8字节，完全绕过shell和Git命令行的编码层。
    调用前需确保暂存区只包含本次要提交的文件（已通过git add）。
    """
    commit_args = ['git', 'commit', '-F', '-'] + extra_args
    proc = subprocess.Popen(
        commit_args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate(input=message.encode('utf-8'))

    if stdout:
        sys.stdout.buffer.write(stdout)
    if stderr:
        sys.stderr.buffer.write(stderr)
    return proc.returncode


def commit_via_normal(message: str, extra_args: list[str]) -> int:
    """普通模式提交（纯ASCII message直接走-m参数，零开销）。
    调用前需确保暂存区只包含本次要提交的文件。
    """
    result = subprocess.run(
        ['git', 'commit', '-m', message] + extra_args,
        capture_output=True
    )
    if result.stdout:
        sys.stdout.buffer.write(result.stdout)
    if result.stderr:
        sys.stderr.buffer.write(result.stderr)
    return result.returncode


def get_staged_files() -> list[str]:
    """获取已暂存文件列表。"""
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only'],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    if result.returncode == 0:
        files = [f for f in result.stdout.strip().split('\n') if f]
        return files
    return []


def get_commit_changed_files() -> list[str]:
    """获取最新提交（HEAD）变更的文件列表。提交后调用以验证非空。"""
    result = subprocess.run(
        ['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    if result.returncode == 0:
        files = [f for f in result.stdout.strip().split('\n') if f]
        return files
    return []


def main():
    setup_safe_output()
    parser = argparse.ArgumentParser(
        description='Windows Git UTF-8 提交工具 - 解决中文commit message乱码问题',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s -m "fix: 修复中文乱码问题"
  %(prog)s -m "feat: 新功能" file1.py docs/*.md  # add+commit
  %(prog)s -F commit-msg.txt --amend
  %(prog)s --stdin < commit-msg.txt
  %(prog)s --auto -m "fix bug"  # 纯ASCII自动走快速路径
        """
    )
    parser.add_argument('-m', '--message', type=str, help='commit message内容')
    parser.add_argument('-F', '--file', type=Path, help='从文件读取commit message')
    parser.add_argument('--stdin', action='store_true', help='从stdin读取commit message')
    parser.add_argument('--auto', action='store_true', default=True,
                        help='自动检测编码：非ASCII走bytes通道，纯ASCII走快速路径（默认启用）')
    parser.add_argument('--force-bytes', action='store_true',
                        help='强制使用bytes通道提交（即使纯ASCII）')
    parser.add_argument('files', nargs='*', help='要add的文件（可选）')
    parser.add_argument('--dry-run', action='store_true', help='仅显示将要执行的操作，不实际提交')
    parser.add_argument('--allow-empty', action='store_true',
                        help='允许空提交（默认拒绝：暂存区为空时提交会报错）')

    args, unknown_args = parser.parse_known_args()

    message_sources = sum([bool(args.message), bool(args.file), args.stdin])
    if message_sources == 0:
        print_error("必须指定commit message来源：-m/--message, -F/--file, 或 --stdin")
        parser.print_help()
        return 1
    if message_sources > 1:
        print_error("只能指定一种message来源：-m, -F, 或 --stdin")
        return 1

    if args.message:
        message = args.message
    elif args.file:
        message = read_message_from_file(args.file)
    else:
        message = read_message_from_stdin()

    message = message.strip()
    if not message:
        print_error("commit message不能为空")
        return 1

    use_bytes = args.force_bytes or (args.auto and contains_non_ascii(message))

    print_header("Git UTF-8 提交")
    print(f"  模式: {'UTF-8 bytes通道' if use_bytes else '普通快速路径'}")
    first_line = message.split('\n')[0][:60]
    if len(message.split('\n')[0]) > 60:
        first_line += '...'
    print(f"  主题: {first_line}")

    if args.files:
        pre_staged = get_staged_files()
        if pre_staged:
            pre_staged_set = set(pre_staged)
            files_set = set(args.files)
            extra = pre_staged_set - files_set
            if extra:
                print_error(f"检测到其他已暂存文件（不在指定列表中），为避免混入无关变更，请先处理这些文件：")
                for f in sorted(extra):
                    print(f"    - {f}")
                print(f"\n  可使用 'git reset HEAD <file>' 取消暂存，或分别提交。")
                return 1

        run_git_add(args.files)

        if not check_staged_matches(args.files):
            print_error("git add后暂存区文件与指定列表不一致，请检查")
            return 1

        print(f"  指定文件: {len(args.files)} 个")
        for f in args.files[:5]:
            print(f"    - {f}")
        if len(args.files) > 5:
            print(f"    ... 及其他 {len(args.files) - 5} 个文件")
    else:
        staged = get_staged_files()
        if not staged:
            if args.allow_empty:
                print_warn("暂存区为空，因指定--allow-empty将创建空提交")
            else:
                print_error("暂存区为空，没有可提交的文件。请先 git add 需要提交的文件，或使用 --allow-empty 显式创建空提交。")
                return 1
        print(f"  暂存: {len(staged)} 个文件")
        for f in staged[:5]:
            print(f"    - {f}")
        if len(staged) > 5:
            print(f"    ... 及其他 {len(staged) - 5} 个文件")
    print()

    if args.dry_run:
        print_warn("[DRY RUN] 不实际执行提交")
        return 0

    if use_bytes:
        print_pass("使用UTF-8 bytes通道提交（安全模式）")
        rc = commit_via_bytes(message, unknown_args)
    else:
        print_pass("纯ASCII message，使用快速路径提交")
        rc = commit_via_normal(message, unknown_args)

    if rc == 0:
        changed = get_commit_changed_files()
        if not changed and not args.allow_empty:
            print_warn("提交成功但未检测到文件变更（可能是空提交），建议检查 git log -1 --stat")
        elif not changed and args.allow_empty:
            print_pass("空提交创建成功（--allow-empty）")
        else:
            print_pass(f"提交成功，{len(changed)} 个文件变更")
    else:
        print_error(f"提交失败 (exit code: {rc})")

    return rc


if __name__ == '__main__':
    sys.exit(main())
