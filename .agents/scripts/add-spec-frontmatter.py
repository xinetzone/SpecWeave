"""批量为 spec.md 补全 frontmatter — 薄包装脚本（向后兼容）

已整合进 spec_tool 工具链，本脚本仅作为兼容入口保留。
推荐用法：
  python -m lib.spec_tool format --fix-frontmatter --dry-run
  python -m lib.spec_tool format --fix-frontmatter

新增非法 status 的归一化映射请到 lib/spec_tool/constants.py 的
STATUS_NORMALIZATION_MAP 中添加。
"""

# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310
enforce_python310()

import argparse
import json
from datetime import datetime
from pathlib import Path

from lib.spec_tool.frontmatter_fixer import process_spec_dir
from lib.spec_tool.constants import VALID_STATUSES

PROJ_ROOT = Path(__file__).resolve().parent.parent.parent
SPEC_ROOT = PROJ_ROOT / ".trae" / "specs"
LOG_DIR = PROJ_ROOT / ".temp"


def main():
    parser = argparse.ArgumentParser(
        description="Spec frontmatter 批量补全（兼容入口，推荐使用 spec_tool format --fix-frontmatter）"
    )
    parser.add_argument("--path", type=Path, default=None, help="spec 根目录（默认: .trae/specs）")
    parser.add_argument(
        "--status",
        default="draft",
        choices=sorted(VALID_STATUSES),
        help="默认 status 值（默认: draft）",
    )
    parser.add_argument("--add-date", action="store_true", help="添加 date 字段（取文件 mtime）")
    parser.add_argument("--fix-missing-status", action="store_true", help="补全已有 frontmatter 中缺失的 status")
    parser.add_argument("--normalize-status", action="store_true", help="归一化非法 status 值到合法值域")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不写入文件")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    args = parser.parse_args()

    spec_root = args.path or SPEC_ROOT

    if not spec_root.exists():
        print(f"错误: Spec 根目录不存在: {spec_root}", file=_sys.stderr)
        return 1

    # 开启所有修复开关的逻辑：如果用户没指定任何开关，默认只补"无 frontmatter"的文件
    # （与历史行为一致，避免破坏性变更）
    fix_missing = args.fix_missing_status
    normalize = args.normalize_status

    results = process_spec_dir(
        spec_root,
        default_status=args.status,
        add_date=args.add_date,
        fix_missing_status=fix_missing,
        normalize_status=normalize,
        dry_run=args.dry_run,
    )

    # 统计
    stats = {
        "added": sum(1 for r in results if r["action"] == "added"),
        "would_add": sum(1 for r in results if r["action"] == "would_add"),
        "status_added": sum(1 for r in results if r["action"] == "status_added"),
        "would_add_status": sum(1 for r in results if r["action"] == "would_add_status"),
        "normalized": sum(1 for r in results if r["action"] == "normalized"),
        "would_normalize": sum(1 for r in results if r["action"] == "would_normalize"),
        "skipped": sum(1 for r in results if r["action"] == "skipped"),
        "error": sum(1 for r in results if r["action"] == "error"),
    }
    total = len(results)

    if args.json:
        report = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": args.dry_run,
            "default_status": args.status,
            "add_date": args.add_date,
            "fix_missing_status": fix_missing,
            "normalize_status": normalize,
            "total": total,
            "stats": stats,
            "results": results,
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        sep = "=" * 60
        print(sep)
        print(f"Spec Frontmatter 批量补全{'（预览模式）' if args.dry_run else ''}")
        print(sep)
        print(f"扫描根: {spec_root}")
        print(f"发现 spec.md: {total} 个")
        print(f"默认 status: {args.status}")
        print(f"添加 date 字段: {'是' if args.add_date else '否'}")
        print(f"补全缺失 status: {'是' if fix_missing else '否'}")
        print(f"归一化非法 status: {'是' if normalize else '否'}")
        print()
        print("执行结果")
        print(sep)
        if args.dry_run:
            print(f"  将添加 frontmatter: {stats['would_add']} 个")
            print(f"  将补全 status: {stats['would_add_status']} 个")
            print(f"  将归一化 status: {stats['would_normalize']} 个")
        else:
            print(f"  已添加 frontmatter: {stats['added']} 个")
            print(f"  已补全 status: {stats['status_added']} 个")
            print(f"  已归一化 status: {stats['normalized']} 个")
        print(f"  跳过: {stats['skipped']} 个")
        print(f"  错误: {stats['error']} 个")
        print()

        errors = [r for r in results if r["action"] == "error"]
        if errors:
            print("-- 错误列表 --")
            for r in errors[:20]:
                print(f"  [E] {r['file']}: {r['reason']}")
            if len(errors) > 20:
                print(f"    ... 还有 {len(errors) - 20} 个")
            print()

        total_changed = (
            stats["would_add"] + stats["would_add_status"] + stats["would_normalize"]
            if args.dry_run
            else stats["added"] + stats["status_added"] + stats["normalized"]
        )
        if stats["error"] == 0:
            print(
                f"[PASS] 完成，{total_changed} 个文件已修改"
                f"（{stats['added']} 新增 + {stats['status_added']} 补 status + {stats['normalized']} 归一化）"
            )
        else:
            print("[WARN] 完成，但有部分文件出错")
        print()

    # 保存日志
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"add-spec-frontmatter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report = {
        "timestamp": datetime.now().isoformat(),
        "dry_run": args.dry_run,
        "default_status": args.status,
        "add_date": args.add_date,
        "fix_missing_status": fix_missing,
        "normalize_status": normalize,
        "total": total,
        "stats": stats,
        "results": results,
    }
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    if not args.json:
        print(f"日志已写入: {log_file}")

    return 0 if stats["error"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
