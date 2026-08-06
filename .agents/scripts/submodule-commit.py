#!/usr/bin/env python3
"""Git 子模块原子提交工具。

自动化子模块开发的两步提交流程：
1. 在子模块仓库内执行原子提交（代码变更）
2. 返回主仓库提交子模块指针更新（gitlink）

解决的问题：
- 子模块内提交后忘记在主仓库更新指针
- Windows 中文 commit message 乱码（复用 UTF-8 bytes 通道）
- 手动 cd/push 多仓库操作容易遗漏步骤

用法:
    python submodule-commit.py projects/xuanspace -m "fix(caffe-ffi): 修复xxx"
    python submodule-commit.py projects/xuanspace -m "feat: 新功能" --push
    python submodule-commit.py projects/xuanspace -F msg.txt --dry-run
    python submodule-commit.py projects/xuanspace -m "fix: 修复" -m "预防措施说明" file1.py file2.py
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.python310_version_check import enforce_python310

enforce_python310()

import argparse

from lib.cli import (
    print_pass,
    print_warn,
    print_error,
    print_header,
    print_summary,
    setup_safe_output,
)
from constants import ANSI_GREEN, ANSI_YELLOW, ANSI_RED, ANSI_RESET


def is_tty(stream=sys.stdout) -> bool:
    isatty = getattr(stream, "isatty", None)
    if isatty is None or not callable(isatty):
        return False
    try:
        return bool(isatty())
    except Exception:
        return False


def color(msg: str, code: str, stream=sys.stdout) -> str:
    if not is_tty(stream):
        return msg
    return f"{code}{msg}{ANSI_RESET}"


def contains_non_ascii(text: str) -> bool:
    try:
        text.encode("ascii")
        return False
    except UnicodeEncodeError:
        return True


def run_git(args: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    """执行 git 命令并返回结果。"""
    result = subprocess.run(
        ["git"] + args,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and result.returncode != 0:
        print_error(f"git {' '.join(args)} 失败 (cwd={cwd}):")
        if result.stderr:
            print(f"    {result.stderr.strip()}")
        sys.exit(1)
    return result


def get_status_short(cwd: Path) -> str:
    """获取 --short 状态输出。"""
    result = run_git(["status", "--short"], cwd=cwd, check=False)
    return result.stdout.strip()


def get_changed_files(cwd: Path) -> list[str]:
    """获取所有变更文件（包括untracked），排除子模块自身的变更。"""
    result = run_git(["status", "--porcelain"], cwd=cwd, check=False)
    files = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        # XY filename 格式；跳过子模块变更行（M在第二列表示子模块脏）
        status = line[:2]
        filename = line[3:]
        # 处理重命名（R）情况：filename -> newname
        if " -> " in filename:
            filename = filename.split(" -> ")[-1]
        files.append(filename.strip())
    return files


def is_submodule(repo_root: Path, sub_path: str) -> bool:
    """验证指定路径是否为 gitlink 子模块。"""
    result = run_git(["ls-files", "--stage", sub_path], cwd=repo_root, check=False)
    # gitlink 的 mode 是 160000
    return "160000" in result.stdout


def get_submodule_root(repo_root: Path, sub_path: str) -> Path:
    """获取子模块的 git 工作目录根（处理 .git 文件指向的情况）。"""
    sub_git = repo_root / sub_path / ".git"
    if sub_git.is_file():
        # git submodule 使用 .git 文件指向实际 git 目录
        content = sub_git.read_text(encoding="utf-8").strip()
        if content.startswith("gitdir:"):
            gitdir_rel = content.split("gitdir:", 1)[1].strip()
            return repo_root / sub_path
    return repo_root / sub_path


def commit_via_bytes(message: str, cwd: Path, extra_args: list[str] | None = None) -> int:
    """通过 stdin bytes 通道提交（UTF-8 安全模式）。"""
    args = ["commit", "-F", "-"] + (extra_args or [])
    proc = subprocess.Popen(
        ["git"] + args,
        cwd=str(cwd),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate(input=message.encode("utf-8"))
    if stdout:
        sys.stdout.buffer.write(stdout)
    if stderr:
        sys.stderr.buffer.write(stderr)
    return proc.returncode


def commit_via_normal(message: str, cwd: Path, extra_args: list[str] | None = None) -> int:
    """普通模式提交（纯 ASCII 快速路径）。"""
    args = ["commit", "-m", message] + (extra_args or [])
    result = subprocess.run(
        ["git"] + args,
        cwd=str(cwd),
        capture_output=True,
    )
    if result.stdout:
        sys.stdout.buffer.write(result.stdout)
    if result.stderr:
        sys.stderr.buffer.write(result.stderr)
    return result.returncode


def get_head_sha(cwd: Path, short: bool = True) -> str:
    """获取 HEAD 的 SHA。"""
    args = ["rev-parse", "--short", "HEAD"] if short else ["rev-parse", "HEAD"]
    result = run_git(args, cwd=cwd)
    return result.stdout.strip()


def get_head_subject(cwd: Path) -> str:
    """获取 HEAD 的提交主题（第一行）。"""
    result = run_git(["log", "-1", "--format=%s"], cwd=cwd)
    return result.stdout.strip()


def guess_scope(sub_path: str) -> str:
    """从子模块路径猜测 commit scope。"""
    name = Path(sub_path).name
    return name


def generate_main_message(sub_path: str, sub_sha: str, sub_subject: str) -> str:
    """自动生成主仓库指针更新的 commit message。"""
    scope = guess_scope(sub_path)
    return (
        f"chore({scope}): 更新子模块指针至{sub_sha[:7]}\n\n"
        f"包含变更：{sub_subject}"
    )


def read_message_from_file(filepath: Path) -> str:
    """从文件读取 commit message，自动检测编码。"""
    encodings = ["utf-8", "utf-8-sig", "gbk", "gb2312", "cp936"]
    for enc in encodings:
        try:
            return filepath.read_text(encoding=enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    print_error(f"无法解码文件 {filepath}，尝试的编码: {', '.join(encodings)}")
    sys.exit(1)


def validate_conventional_commits(message: str) -> None:
    """检查 commit message 是否符合 Conventional Commits 格式（仅警告不阻止）。"""
    first_line = message.split("\n", 1)[0].strip()
    cc_pattern = r"^(feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert)(\(.+\))?: .+"
    if not re.match(cc_pattern, first_line):
        print_warn(f"主题行可能不符合Conventional Commits格式: {first_line[:70]}")
        print_warn("  期望格式: type(scope): subject（如 feat(auth): 添加JWT认证）")


def main() -> int:
    setup_safe_output()
    parser = argparse.ArgumentParser(
        description="Git 子模块原子提交工具 - 自动化子模块提交+主仓库指针更新两步流程",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s projects/xuanspace -m "fix(caffe-ffi): 修复Pooling CEIL模式bug"
  %(prog)s projects/xuanspace -m "feat: 新功能" -m "详细说明" --push
  %(prog)s projects/xuanspace -F commit-msg.txt file1.py file2.py
  %(prog)s projects/xuanspace -m "fix: 修复" --main-msg "chore: 更新指针" --dry-run
        """,
    )
    parser.add_argument(
        "submodule",
        type=str,
        help="子模块路径（如 projects/xuanspace）",
    )
    parser.add_argument(
        "-m",
        "--message",
        action="append",
        type=str,
        help="子模块commit message（可多次指定，多段用空行分隔）",
    )
    parser.add_argument(
        "-F",
        "--file",
        type=Path,
        help="从文件读取子模块commit message",
    )
    parser.add_argument(
        "--main-msg",
        type=str,
        default=None,
        help="主仓库指针更新的commit message（默认自动生成）",
    )
    parser.add_argument(
        "--main-msg-file",
        type=Path,
        default=None,
        help="从文件读取主仓库指针更新的commit message",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅显示将要执行的操作，不实际提交",
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="提交后推送（先推子模块，再推主仓库）",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="要在子模块中add的文件（不指定则add所有变更文件）",
    )

    args = parser.parse_args()

    # ── 定位仓库根目录 ──
    repo_root = Path.cwd()
    # 向上查找 .git 目录确定根目录
    while not (repo_root / ".git").exists():
        parent = repo_root.parent
        if parent == repo_root:
            print_error("未找到Git仓库根目录，请在SpecWeave仓库内运行此脚本")
            return 1
        repo_root = parent

    sub_path = args.submodule.replace("\\", "/").rstrip("/")

    # ── 验证子模块 ──
    if not (repo_root / sub_path).exists():
        print_error(f"子模块路径不存在: {sub_path}")
        return 1
    if not is_submodule(repo_root, sub_path):
        print_error(f"路径 {sub_path} 不是gitlink子模块（mode != 160000）")
        return 1

    sub_cwd = get_submodule_root(repo_root, sub_path)

    # ── 构建子模块 commit message ──
    msg_sources = sum([bool(args.message), bool(args.file)])
    if msg_sources == 0:
        print_error("必须指定子模块commit message来源：-m/--message 或 -F/--file")
        parser.print_help()
        return 1
    if msg_sources > 1:
        print_error("只能指定一种子模块message来源：-m 或 -F")
        return 1

    if args.message:
        sub_message = "\n\n".join(m.strip() for m in args.message if m and m.strip())
    else:
        sub_message = read_message_from_file(args.file)

    sub_message = sub_message.strip()
    if not sub_message:
        print_error("子模块commit message不能为空")
        return 1

    validate_conventional_commits(sub_message)

    # ── 步骤0：检查子模块变更 ──
    print_header("子模块原子提交", width=60)
    print(f"  仓库根: {repo_root}")
    print(f"  子模块: {sub_path}")

    sub_status = get_status_short(sub_cwd)
    if not sub_status:
        print_warn(f"子模块 {sub_path} 工作区干净，没有变更需要提交")
        return 0

    print(f"\n  子模块变更文件:")
    for line in sub_status.splitlines():
        print(f"    {line}")

    # ── 确定要 add 的文件 ──
    if args.files:
        files_to_add = args.files
        print(f"\n  指定提交文件: {len(files_to_add)} 个")
    else:
        files_to_add = get_changed_files(sub_cwd)
        # 过滤掉 .git 等特殊文件
        files_to_add = [f for f in files_to_add if not f.startswith(".git")]
        print(f"\n  自动检测变更文件: {len(files_to_add)} 个")

    if not files_to_add:
        print_error("没有可提交的文件")
        return 1

    # ── Dry Run 模式 ──
    if args.dry_run:
        print(f"\n{color('[DRY RUN]', ANSI_YELLOW)} 将要执行以下操作:\n")
        print(f"  步骤1: cd {sub_path} && git add {' '.join(files_to_add)}")
        first_line = sub_message.split("\n", 1)[0][:60]
        print(f"  步骤2: cd {sub_path} && git commit -m \"{first_line}...\"")
        print(f"  步骤3: cd {repo_root} && git add {sub_path}")
        main_msg_preview = args.main_msg or f"chore({guess_scope(sub_path)}): 更新子模块指针至<sha>"
        print(f"  步骤4: git commit -m \"{main_msg_preview[:60]}\"")
        if args.push:
            print(f"  步骤5: cd {sub_path} && git push")
            print(f"  步骤6: cd {repo_root} && git push")
        print()
        print_summary(pass_count=1, warn_count=0, error_count=0)
        return 0

    # ── 步骤1：子模块 git add ──
    print_header("步骤1: 子模块 git add", width=60)
    result = run_git(["add"] + files_to_add, cwd=sub_cwd)
    print_pass(f"已 add {len(files_to_add)} 个文件")

    # 验证暂存区非空
    staged = run_git(["diff", "--cached", "--name-only"], cwd=sub_cwd).stdout.strip()
    if not staged:
        print_error("暂存区为空，没有文件被add（检查文件路径是否正确）")
        return 1

    # ── 步骤2：子模块 commit ──
    print_header("步骤2: 子模块 commit", width=60)
    use_bytes = contains_non_ascii(sub_message)
    print(f"  提交模式: {'UTF-8 bytes通道' if use_bytes else '普通快速路径'}")
    first_line = sub_message.split("\n", 1)[0][:70]
    print(f"  主题: {first_line}")

    if use_bytes:
        rc = commit_via_bytes(sub_message, cwd=sub_cwd)
    else:
        rc = commit_via_normal(sub_message, cwd=sub_cwd)

    if rc != 0:
        print_error("子模块commit失败")
        return 1

    sub_sha = get_head_sha(sub_cwd, short=True)
    sub_subject = get_head_subject(sub_cwd)
    print_pass(f"子模块提交成功: {sub_sha}")

    # ── 步骤3：主仓库 git add 子模块指针 ──
    print_header("步骤3: 主仓库更新子模块指针", width=60)
    result = run_git(["add", sub_path], cwd=repo_root)
    print_pass(f"已 add 子模块指针: {sub_path}")

    # 检查主仓库暂存区确认只有gitlink变更
    staged_main = run_git(["diff", "--cached", "--name-only"], cwd=repo_root).stdout.strip()
    if sub_path not in staged_main:
        print_warn(f"警告: 暂存区中未检测到 {sub_path}，子模块可能已在最新commit")

    # ── 步骤4：主仓库 commit ──
    print_header("步骤4: 主仓库 commit（指针更新）", width=60)
    if args.main_msg_file:
        main_message = read_message_from_file(args.main_msg_file).strip()
    elif args.main_msg:
        main_message = args.main_msg.strip()
    else:
        main_message = generate_main_message(sub_path, sub_sha, sub_subject)

    validate_conventional_commits(main_message)
    main_first_line = main_message.split("\n", 1)[0][:70]
    print(f"  主题: {main_first_line}")

    use_bytes_main = contains_non_ascii(main_message)
    if use_bytes_main:
        rc = commit_via_bytes(main_message, cwd=repo_root)
    else:
        rc = commit_via_normal(main_message, cwd=repo_root)

    if rc != 0:
        print_error("主仓库commit失败")
        return 1

    main_sha = get_head_sha(repo_root, short=True)
    print_pass(f"主仓库提交成功: {main_sha}")

    # ── 步骤5（可选）：push ──
    if args.push:
        print_header("步骤5: 推送至远程", width=60)

        print(f"  推送子模块 {sub_path}...")
        result = run_git(["push"], cwd=sub_cwd, check=False)
        if result.returncode != 0:
            print_error(f"子模块push失败: {result.stderr.strip()}")
            return 1
        print_pass("子模块推送成功")

        print(f"  推送主仓库...")
        result = run_git(["push"], cwd=repo_root, check=False)
        if result.returncode != 0:
            print_error(f"主仓库push失败: {result.stderr.strip()}")
            return 1
        print_pass("主仓库推送成功")

    # ── 结果摘要 ──
    print()
    print_header("提交结果摘要", width=60)
    print(f"  子模块 {color(sub_path, ANSI_GREEN)}:")
    print(f"    Commit: {color(sub_sha, ANSI_GREEN)}")
    print(f"    主题:   {sub_subject[:60]}")
    print(f"  主仓库 {color('SpecWeave', ANSI_GREEN)}:")
    print(f"    Commit: {color(main_sha, ANSI_GREEN)}")
    print(f"    指针:   → {sub_sha}")
    if args.push:
        print(f"  推送: {color('已推送至远程', ANSI_GREEN)}")
    else:
        print(f"  推送: {color('未推送（使用--push启用）', ANSI_YELLOW)}")
    print()
    print_summary(pass_count=2 if not args.push else 3, warn_count=0, error_count=0)

    return 0


if __name__ == "__main__":
    sys.exit(main())
