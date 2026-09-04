#!/usr/bin/env python3
"""
批量迁移：将 .trae/specs 下历史 checklist.md 重命名为 review.md

规范依据：.agents/skills/TRAE-spec-mode/SKILL.md
三件套标准命名：spec.md + tasks.md + review.md

迁移策略：
- 直接重命名文件（内容结构保持不变）
- 若目标 review.md 已存在则跳过（不覆盖）
- 自动更新 checklist.md 正文内部自引用链接
- 生成迁移日志到 .temp/

用法：
  python migrate-checklist-to-review.py --dry-run    # 预览，不实际修改
  python migrate-checklist-to-review.py               # 执行迁移
"""

from __future__ import annotations

import argparse
import json
import sys
import re
from pathlib import Path
from datetime import datetime

# 版本校验：导入共享库
sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
from python310_version_check import enforce_python310
enforce_python310()

from lib.cli import print_header, print_pass, print_warn, print_error

PROJ_ROOT = Path(__file__).resolve().parent.parent.parent  # scripts → .agents → root
SPEC_ROOT = PROJ_ROOT / ".trae" / "specs"
LOG_DIR = PROJ_ROOT / ".temp"


def discover_checklist_files() -> list[Path]:
    """递归发现所有 .trae/specs/ 下含 spec.md 的目录中的 checklist.md

    规则：目录中存在 spec.md 才算 spec 目录，再检查其中是否有 checklist.md。
    支持任意深度的嵌套（如 theme/subtheme/spec-name/）。
    """
    if not SPEC_ROOT.exists():
        return []
    checklist_files = []
    for spec_md in sorted(SPEC_ROOT.rglob("spec.md")):
        spec_dir = spec_md.parent
        cl = spec_dir / "checklist.md"
        if cl.exists():
            checklist_files.append(cl)
    return checklist_files


def update_self_references(content: str, spec_dir_name: str) -> tuple[str, int]:
    """更新正文内部对 checklist.md 的自引用为 review.md

    只替换作为文件名/链接目标出现的 checklist.md，
    不替换出现在普通句子里的"checklist"词汇（避免语义错误）。

    返回 (更新后的内容, 替换次数)
    """
    count = 0
    # 模式1: Markdown 链接中的 checklist.md 目标
    # 例如 [验证清单](checklist.md) → [验证清单](review.md)
    new_content, n1 = re.subn(
        r'(\([^)]*?)\bchecklist\.md\b',
        r'\1review.md',
        content
    )
    count += n1
    content = new_content

    # 模式2: 代码/文件名引用（前后有空格/冒号/反引号等边界）
    # 例如 "checklist.md 本验证清单" → "review.md 本验证清单"
    # 例如 "spec.md / checklist.md" → "spec.md / review.md"
    # 精确匹配作为文件名的 checklist.md，避免普通句子误替换
    new_content, n2 = re.subn(
        r'(?<=[\s:："`\[\(（])checklist\.md(?=[\s\]）)）.，。、；:："`])',
        'review.md',
        content
    )
    count += n2

    return new_content, count


def migrate_one(checklist_path: Path, dry_run: bool) -> dict:
    """迁移单个 checklist.md，返回结果字典"""
    spec_dir = checklist_path.parent
    review_path = spec_dir / "review.md"
    rel = checklist_path.relative_to(PROJ_ROOT).as_posix()
    rel_review = review_path.relative_to(PROJ_ROOT).as_posix()

    result = {
        "spec_dir": spec_dir.name,
        "checklist_path": rel,
        "review_path": rel_review,
        "action": "skipped",
        "reason": "",
        "refs_updated": 0,
    }

    # 如果 review.md 已存在，跳过
    if review_path.exists():
        result["reason"] = "review.md 已存在，不覆盖"
        return result

    # 读取内容（用于自引用更新）
    try:
        content = checklist_path.read_text(encoding="utf-8")
    except Exception as e:
        result["action"] = "error"
        result["reason"] = f"读取失败: {e}"
        return result

    # 更新正文内的自引用
    new_content, ref_count = update_self_references(content, spec_dir.name)
    result["refs_updated"] = ref_count

    if dry_run:
        result["action"] = "would_rename"
        if ref_count > 0:
            result["reason"] = f"将重命名并更新 {ref_count} 处自引用"
        else:
            result["reason"] = "将重命名（无需内容修改）"
        return result

    # 执行迁移：先写新文件，再删旧文件（原子性更好）
    try:
        review_path.write_text(new_content, encoding="utf-8")
        checklist_path.unlink()
        result["action"] = "renamed"
        if ref_count > 0:
            result["reason"] = f"已重命名，更新 {ref_count} 处自引用"
        else:
            result["reason"] = "已重命名"
    except Exception as e:
        result["action"] = "error"
        result["reason"] = f"操作失败: {e}"
        # 回滚：如果新文件已写但旧文件删失败，尝试删掉新文件
        if review_path.exists():
            try:
                review_path.unlink()
            except Exception:
                pass
    return result


def main():
    parser = argparse.ArgumentParser(
        description="批量迁移 checklist.md → review.md（TRAE-spec-mode 规范）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不实际修改文件")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出报告")
    args = parser.parse_args()

    if not SPEC_ROOT.exists():
        print_error(f"Spec 根目录不存在: {SPEC_ROOT}")
        return 2

    # 发现文件
    checklist_files = discover_checklist_files()
    total = len(checklist_files)

    if total == 0:
        print("未发现任何 checklist.md 文件，无需迁移")
        return 0

    if not args.json:
        print_header(f"Checklist → Review 批量迁移{'（预览模式）' if args.dry_run else ''}")
        print(f"扫描根: {SPEC_ROOT}")
        print(f"发现 checklist.md: {total} 个")
        print()

    # 执行迁移
    results = []
    stats = {
        "renamed": 0,
        "would_rename": 0,
        "skipped": 0,
        "error": 0,
        "total_refs_updated": 0,
    }

    for cf in checklist_files:
        r = migrate_one(cf, args.dry_run)
        results.append(r)
        action = r["action"]
        if action in stats:
            stats[action] += 1
        stats["total_refs_updated"] += r["refs_updated"]

    # 输出结果
    if args.json:
        report = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": args.dry_run,
            "total": total,
            "stats": stats,
            "results": results,
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("=" * 60)
        print("迁移结果")
        print("=" * 60)
        if args.dry_run:
            print(f"  将重命名: {stats['would_rename']} 个")
        else:
            print(f"  已重命名: {stats['renamed']} 个")
        print(f"  跳过(已存在): {stats['skipped']} 个")
        print(f"  错误: {stats['error']} 个")
        print(f"  自引用更新: {stats['total_refs_updated']} 处")
        print()

        # 列出跳过和错误的
        skipped = [r for r in results if r["action"] == "skipped"]
        errors = [r for r in results if r["action"] == "error"]

        if skipped:
            print_warn(f"跳过 {len(skipped)} 个（review.md 已存在）:")
            for r in skipped[:10]:
                print(f"    - {r['checklist_path']}")
            if len(skipped) > 10:
                print(f"    ... 还有 {len(skipped) - 10} 个")
            print()

        if errors:
            print_error(f"错误 {len(errors)} 个:")
            for r in errors:
                print(f"    ✗ {r['checklist_path']}: {r['reason']}")
            print()

        if stats["error"] == 0 and stats["skipped"] == 0:
            if args.dry_run:
                print_pass(f"预览完成，{stats['would_rename']} 个文件将被迁移")
            else:
                print_pass(f"迁移完成，{stats['renamed']} 个文件已成功迁移")
        else:
            print_warn("迁移完成，但有部分文件被跳过或出错")
        print()

    # 保存日志
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"migrate-checklist-to-review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report = {
        "timestamp": datetime.now().isoformat(),
        "dry_run": args.dry_run,
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
    sys.exit(main())
