#!/usr/bin/env python3
"""混合关注点单文件拆分的确定性状态操作。

子命令：
  backup   把工作树文件字节复制到备份路径，并写出 sha256 边车文件
  revert   从当前工作树终态回退一类改动，构造只含另一类改动的中间态
  restore  用备份字节还原工作树终态，并校验 sha256

--pair 取值格式为 PRESENT|||REPLACEMENT|||EXPECTED，其中 PRESENT 是当前文件中
存在的文本，REPLACEMENT 是回退后应出现的文本，EXPECTED 是精确出现次数。
文本中的换行用字面 \\n 表示。

退出码：0 成功；2 参数或路径错误；3 替换次数与预期不符（不写文件）；4 备份或还原校验失败。
"""

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

PAIR_SEP = "|||"


class UsageError(Exception):
    pass


def sha256_of(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode_text(value):
    return value.replace("\\n", "\n")


def resolve_target(repo, rel):
    path = Path(repo) / rel
    if not path.is_file():
        raise UsageError(f"不是可读文件: {path}")
    return path


def parse_pairs(raw_pairs):
    pairs = []
    for raw in raw_pairs:
        parts = raw.split(PAIR_SEP)
        if len(parts) != 3:
            raise UsageError(f"--pair 需要三段 PRESENT|||REPLACEMENT|||EXPECTED: {raw}")
        try:
            expected = int(parts[2])
        except ValueError as exc:
            raise UsageError(f"--pair 的第三段不是整数: {raw}") from exc
        pairs.append((decode_text(parts[0]), decode_text(parts[1]), expected))
    return pairs


def cmd_backup(args):
    source = resolve_target(args.repo, args.file)
    backup = Path(args.backup)
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, backup)
    digest = sha256_of(backup)
    Path(str(backup) + ".sha256").write_text(digest + "\n", encoding="utf-8")
    print(json.dumps({"backup": str(backup), "sha256": digest}, ensure_ascii=False))
    return 0


def cmd_revert(args):
    target = resolve_target(args.repo, args.file)
    pairs = parse_pairs(args.pair)
    try:
        text = target.read_bytes().decode("utf-8")
    except UnicodeDecodeError as exc:
        raise UsageError(f"目标不是 UTF-8: {target}") from exc
    applied = []
    for present, replacement, expected in pairs:
        actual = text.count(present)
        if actual != expected:
            print(
                json.dumps(
                    {
                        "error": "occurrence-mismatch",
                        "present": present,
                        "expected": expected,
                        "actual": actual,
                        "written": False,
                    },
                    ensure_ascii=False,
                ),
                file=sys.stderr,
            )
            return 3
        text = text.replace(present, replacement)
        applied.append({"present": present, "replacement": replacement, "count": actual})
    if args.dry_run:
        print(json.dumps({"dry_run": True, "pairs": applied}, ensure_ascii=False))
        return 0
    target.write_bytes(text.encode("utf-8"))
    print(json.dumps({"file": str(target), "pairs": applied}, ensure_ascii=False))
    return 0


def cmd_restore(args):
    target = resolve_target(args.repo, args.file)
    backup = Path(args.backup)
    if not backup.is_file():
        raise UsageError(f"备份不存在: {backup}")
    sidecar = Path(str(backup) + ".sha256")
    if not sidecar.is_file():
        raise UsageError(f"缺少 sha256 边车文件: {sidecar}")
    expected = sidecar.read_text(encoding="utf-8").strip()
    actual = sha256_of(backup)
    if actual != expected:
        print(
            json.dumps({"error": "backup-hash-mismatch", "expected": expected, "actual": actual}, ensure_ascii=False),
            file=sys.stderr,
        )
        return 4
    shutil.copy2(backup, target)
    restored = sha256_of(target)
    if restored != expected:
        print(
            json.dumps({"error": "restore-hash-mismatch", "expected": expected, "actual": restored}, ensure_ascii=False),
            file=sys.stderr,
        )
        return 4
    print(json.dumps({"file": str(target), "sha256": restored}, ensure_ascii=False))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description="混合关注点单文件拆分的确定性状态操作")
    sub = parser.add_subparsers(dest="command", required=True)

    backup = sub.add_parser("backup", help="备份工作树文件字节并记录 sha256")
    backup.add_argument("--repo", required=True)
    backup.add_argument("--file", required=True)
    backup.add_argument("--backup", required=True)
    backup.set_defaults(func=cmd_backup)

    revert = sub.add_parser("revert", help="按精确次数回退另一类改动，构造中间态")
    revert.add_argument("--repo", required=True)
    revert.add_argument("--file", required=True)
    revert.add_argument("--pair", action="append", required=True)
    revert.add_argument("--dry-run", action="store_true", help="只报告替换次数，不写文件")
    revert.set_defaults(func=cmd_revert)

    restore = sub.add_parser("restore", help="用备份还原工作树终态并校验 sha256")
    restore.add_argument("--repo", required=True)
    restore.add_argument("--file", required=True)
    restore.add_argument("--backup", required=True)
    restore.set_defaults(func=cmd_restore)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except UsageError as exc:
        print(json.dumps({"error": "usage", "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
