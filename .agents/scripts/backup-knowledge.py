#!/usr/bin/env python3
"""知识库备份/恢复/时光机 CLI 工具。

提供知识库的完整备份、恢复、Git 版本查询、批量损坏检测与修复功能。

用法：
  python backup-knowledge.py backup                    # 创建备份
  python backup-knowledge.py backup --dir /path/backup # 指定备份目录
  python backup-knowledge.py restore <backup_path>     # 从备份恢复
  python backup-knowledge.py restore <path> --dry-run  # 预览恢复
  python backup-knowledge.py list                      # 列出所有备份
  python backup-knowledge.py history <file>            # 查看文件 Git 历史
  python backup-knowledge.py show <file> <commit>      # 查看历史版本内容
  python backup-knowledge.py diff <file> <old> <new>   # 比较两个版本
  python backup-knowledge.py detect                    # 检测损坏条目
  python backup-knowledge.py repair                    # 批量修复
  python backup-knowledge.py repair --dry-run          # 预览修复
  python backup-knowledge.py precheck                  # 变更前检查
"""

import argparse
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.knowledge_backup import (
    backup_knowledge_base,
    restore_from_backup,
    list_all_backups,
    list_knowledge_history,
    get_knowledge_at_version,
    compare_knowledge_versions,
    detect_bulk_damage,
    bulk_repair,
    pre_change_check,
    KNOWLEDGE_BASE,
    DEFAULT_BACKUP_DIR,
)


def cmd_backup(args):
    """执行备份命令。"""
    ok, msg, path = backup_knowledge_base(
        backup_dir=args.dir,
        include_encrypted=not args.no_encrypted,
    )
    print(msg)
    if ok and path:
        print(f"  备份路径: {path}")
    return 0 if ok else 1


def cmd_restore(args):
    """执行恢复命令。"""
    ok, msg = restore_from_backup(
        args.backup_path,
        target_dir=args.target,
        dry_run=args.dry_run,
    )
    print(msg)
    return 0 if ok else 1


def cmd_list(args):
    """列出所有备份。"""
    ok, backups, msg = list_all_backups(args.dir)
    if not ok:
        print(msg)
        return 1

    if not backups:
        print("无备份记录")
        return 0

    print(f"备份列表 ({len(backups)} 个):")
    for b in backups:
        print(f"  {b['name']} | {b['total_files']} 文件 | {b['timestamp']}")
    return 0


def cmd_history(args):
    """查看文件 Git 历史。"""
    ok, commits, msg = list_knowledge_history(args.file)
    if not ok:
        print(msg)
        return 1

    if not commits:
        print("无历史记录")
        return 0

    print(f"历史版本 ({len(commits)} 个):")
    for c in commits:
        print(f"  {c['hash'][:8]} | {c['date'][:10]} | {c['author']} | {c['message']}")
    return 0


def cmd_show(args):
    """查看历史版本内容。"""
    ok, content, msg = get_knowledge_at_version(args.file, args.commit)
    if not ok:
        print(msg)
        return 1

    print(content)
    return 0


def cmd_diff(args):
    """比较两个版本。"""
    ok, diff, msg = compare_knowledge_versions(args.file, args.old, args.new)
    if not ok:
        print(msg)
        return 1

    if diff:
        print(diff)
    else:
        print(msg)
    return 0


def cmd_detect(args):
    """检测损坏条目。"""
    ok, damaged, msg = detect_bulk_damage(args.kb_dir)
    print(msg)
    if damaged:
        for d in damaged:
            print(f"  [DAMAGED] {d['file']}: {d['error']}")
    return 0 if ok else 1


def cmd_repair(args):
    """批量修复。"""
    ok, results, msg = bulk_repair(args.kb_dir, dry_run=args.dry_run)
    print(msg)
    if results:
        for r in results:
            status = r.get("repair_status", "?")
            if status == "repaired":
                print(f"  [REPAIRED] {r['file']}")
            elif status == "dry_run":
                print(f"  [WOULD_REPAIR] {r['file']}")
            else:
                print(f"  [FAILED] {r['file']}: {r.get('repair_error', '')}")
    return 0 if ok else 1


def cmd_precheck(args):
    """执行变更前检查。"""
    ok, info, msg = pre_change_check()
    print(msg)
    if info.get("has_git"):
        print(f"  Git 仓库: 是")
        print(f"  工作区: {'干净' if info['is_clean'] else '有变更'}")
        if info["pending_changes"]:
            for c in info["pending_changes"]:
                print(f"    {c}")
        if info["last_commit"]:
            print(f"  最近提交: {info['last_commit']}")
    return 0 if ok else 1


def main():
    parser = argparse.ArgumentParser(
        description="知识库备份/恢复/时光机 CLI 工具",
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # backup
    p_backup = subparsers.add_parser("backup", help="创建知识库备份")
    p_backup.add_argument("--dir", help="备份目标目录")
    p_backup.add_argument("--no-encrypted", action="store_true", help="排除加密文件")

    # restore
    p_restore = subparsers.add_parser("restore", help="从备份恢复知识库")
    p_restore.add_argument("backup_path", help="备份路径")
    p_restore.add_argument("--target", help="恢复目标目录")
    p_restore.add_argument("--dry-run", action="store_true", help="仅预览")

    # list
    p_list = subparsers.add_parser("list", help="列出所有备份")
    p_list.add_argument("--dir", help="备份目录")

    # history
    p_history = subparsers.add_parser("history", help="查看文件 Git 历史")
    p_history.add_argument("file", help="文件路径")

    # show
    p_show = subparsers.add_parser("show", help="查看历史版本内容")
    p_show.add_argument("file", help="文件路径")
    p_show.add_argument("commit", help="提交哈希")

    # diff
    p_diff = subparsers.add_parser("diff", help="比较两个版本")
    p_diff.add_argument("file", help="文件路径")
    p_diff.add_argument("old", help="旧版本提交哈希")
    p_diff.add_argument("new", help="新版本提交哈希")

    # detect
    p_detect = subparsers.add_parser("detect", help="检测损坏条目")
    p_detect.add_argument("--kb-dir", help="知识库目录")

    # repair
    p_repair = subparsers.add_parser("repair", help="批量修复损坏条目")
    p_repair.add_argument("--kb-dir", help="知识库目录")
    p_repair.add_argument("--dry-run", action="store_true", help="仅预览")

    # precheck
    subparsers.add_parser("precheck", help="变更前检查")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    commands = {
        "backup": cmd_backup,
        "restore": cmd_restore,
        "list": cmd_list,
        "history": cmd_history,
        "show": cmd_show,
        "diff": cmd_diff,
        "detect": cmd_detect,
        "repair": cmd_repair,
        "precheck": cmd_precheck,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())