#!/usr/bin/env python3
"""Spec工作目录清理脚本——任务完成后归档中间产物，保持spec目录精简。

功能:
  - 扫描spec目录中的中间产物文件（子代理输出、临时文件、已归档的最终报告）
  - 默认dry-run预览模式，显式 --execute 才执行操作
  - 归档而非删除：中间产物移动到 .trae/specs/_archive/<spec-name>/ 目录
  - 白名单保护：核心规划文件和最终交付物永不动
  - 支持单目录清理或批量扫描所有specs

用法:
  # 预览当前spec目录（默认dry-run）
  python spec-cleanup.py

  # 预览指定spec目录
  python spec-cleanup.py -d .trae/specs/retrospectives-insights/analyze-workbuddy-harness-seven-concepts

  # 执行清理（归档中间产物）
  python spec-cleanup.py -d <path> --execute

  # 执行清理并删除（不归档，谨慎使用）
  python spec-cleanup.py -d <path> --execute --delete

  # 批量扫描所有specs，列出可清理的目录
  python spec-cleanup.py --scan-all

  # 批量清理所有可清理的specs
  python spec-cleanup.py --scan-all --execute

白名单（KEEP）—— 以下文件永不动:
  spec.md, tasks.md, checklist.md  (规划三件套)
  retrospective.md, retro.md       (复盘报告)
  team-briefing.md, briefing.md     (团队简报)
  article-content.md, source.md, raw-content.md, cleaned-content.md, web-content.md, extracted-content.md (原文/SSOT)
  README.md                         (目录索引)
  .gitignore                        (git配置)
  plan.md, migration-plan.md        (计划文档)

可清理模式（MATCH）—— 匹配以下模式的文件将被归档:
  task*-output.md, task*-analysis.md, task*-*.md  (子代理中间产物)
  ~*.md, *.tmp, *.bak                               (临时/备份文件)
  _article_*.md, _scratch_*.md                      (临时草稿)

条件归档（CONDITIONAL）—— 满足条件时提示归档:
  analysis-report.md —— 若该报告已在docs/knowledge/中存在归档副本，则归档原文件
"""

from __future__ import annotations

import argparse
import fnmatch
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SPECS_DIR = PROJECT_ROOT / ".trae" / "specs"
ARCHIVE_ROOT = SPECS_DIR / "_archive"

KEEP_FILES = frozenset({
    "spec.md", "tasks.md", "checklist.md",
    "retrospective.md", "retro.md",
    "team-briefing.md", "briefing.md",
    "article-content.md", "source.md", "raw-content.md",
    "cleaned-content.md", "web-content.md", "extracted-content.md",
    "readme.md", ".gitignore",
    "plan.md", "migration-plan.md",
})

KEEP_PREFIXES = ("00-", "01-", "02-", "03-", "04-", "05-",
                 "06-", "07-", "08-", "09-", "10-",
                 "00_", "01_", "02_", "03_", "04_", "05_",
                 "06_", "07_", "08_", "09_", "10_")

CLEAN_PATTERNS = [
    "task*-output*.md",
    "task*-analysis*.md",
    "task*-f-*.md", "task*-r-*.md", "task*-i-*.md",
    "task*-e-*.md", "task*-c-*.md", "task*-a-*.md", "task*-v-*.md",
    "task*-layer-*.md", "task*-mapping-*.md", "task*-insights*.md",
    "task*.json",
    "~*.md", "*.tmp", "*.bak",
    "_article_*.md", "_scratch_*.md",
]

CONDITIONAL_PATTERNS = [
    "analysis-report.md",
    "final-report.md",
]


@dataclass
class CleanupResult:
    """单个spec目录的清理结果。"""
    spec_dir: Path
    keep_files: list[Path] = field(default_factory=list)
    to_archive: list[Path] = field(default_factory=list)
    to_delete: list[Path] = field(default_factory=list)
    conditional: list[tuple[Path, str]] = field(default_factory=list)
    skipped_dirs: list[Path] = field(default_factory=list)
    archived_count: int = 0
    deleted_count: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def spec_name(self) -> str:
        return self.spec_dir.name

    @property
    def total_to_clean(self) -> int:
        return len(self.to_archive) + len(self.to_delete)

    @property
    def has_work(self) -> bool:
        return self.total_to_clean > 0 or len(self.conditional) > 0


def matches_any(name: str, patterns: list[str]) -> bool:
    """检查文件名是否匹配任意glob模式。"""
    return any(fnmatch.fnmatch(name, p) for p in patterns)


def is_keep_file(path: Path) -> bool:
    """判断文件是否在白名单中。"""
    name_lower = path.name.lower()
    if name_lower in KEEP_FILES:
        return True
    if name_lower.startswith(KEEP_PREFIXES):
        return True
    return False


def is_nested_spec_dir(path: Path) -> bool:
    """判断目录是否包含嵌套的spec（有自己的spec.md），不应深入清理。"""
    return (path / "spec.md").exists()


def find_archived_report(report_path: Path, spec_name: str) -> Optional[Path]:
    """检查最终报告是否已在docs/knowledge/中归档。"""
    knowledge_base = PROJECT_ROOT / "docs" / "knowledge"
    if not knowledge_base.exists():
        return None
    name_stem = report_path.stem
    for candidate in knowledge_base.rglob(f"{name_stem}*.md"):
        if candidate.is_file() and candidate.stat().st_size > 1000:
            return candidate
    for candidate in knowledge_base.rglob(f"*{spec_name}*analysis*.md"):
        if candidate.is_file() and candidate.stat().st_size > 1000:
            return candidate
    return None


def analyze_spec_dir(spec_dir: Path) -> CleanupResult:
    """分析单个spec目录，分类所有文件。"""
    result = CleanupResult(spec_dir=spec_dir)

    if not spec_dir.is_dir():
        result.errors.append(f"目录不存在: {spec_dir}")
        return result

    if not (spec_dir / "spec.md").exists():
        result.errors.append(f"不是有效的spec目录（缺少spec.md）: {spec_dir}")
        return result

    for item in sorted(spec_dir.iterdir()):
        if item.is_dir():
            if is_nested_spec_dir(item):
                sub_result = analyze_spec_dir(item)
                result.keep_files.append(item)
                result.skipped_dirs.append(item)
            else:
                result.keep_files.append(item)
            continue

        if is_keep_file(item):
            result.keep_files.append(item)
            continue

        if matches_any(item.name, CLEAN_PATTERNS):
            result.to_archive.append(item)
            continue

        if matches_any(item.name, CONDITIONAL_PATTERNS):
            archived = find_archived_report(item, spec_dir.name)
            if archived:
                result.to_archive.append(item)
                result.conditional.append((item, f"已归档至 {archived.relative_to(PROJECT_ROOT)}"))
            else:
                result.keep_files.append(item)
                result.conditional.append((item, "保留（未在docs/knowledge/中找到归档副本）"))
            continue

        result.keep_files.append(item)

    return result


def execute_cleanup(result: CleanupResult, delete_mode: bool = False,
                    verbose: bool = True) -> CleanupResult:
    """执行清理操作。"""
    archive_dir = ARCHIVE_ROOT / result.spec_name

    if result.to_archive and not delete_mode:
        archive_dir.mkdir(parents=True, exist_ok=True)

    for fpath in result.to_archive:
        try:
            if delete_mode:
                fpath.unlink()
                result.deleted_count += 1
                if verbose:
                    print(f"  🗑️  已删除: {fpath.name}")
            else:
                dest = archive_dir / fpath.name
                if dest.exists():
                    stem = dest.stem
                    suffix = dest.suffix
                    from datetime import datetime
                    ts = datetime.now().strftime("%Y%m%d%H%M%S")
                    dest = archive_dir / f"{stem}_{ts}{suffix}"
                shutil.move(str(fpath), str(dest))
                result.archived_count += 1
                if verbose:
                    print(f"  📦 已归档: {fpath.name} -> _archive/{result.spec_name}/{dest.name}")
        except Exception as e:
            result.errors.append(f"处理 {fpath.name} 失败: {e}")

    for fpath in result.to_delete:
        try:
            fpath.unlink()
            result.deleted_count += 1
            if verbose:
                print(f"  🗑️  已删除: {fpath.name}")
        except Exception as e:
            result.errors.append(f"删除 {fpath.name} 失败: {e}")

    return result


def print_preview(result: CleanupResult) -> None:
    """打印清理预览。"""
    print(f"\n{'='*60}")
    print(f"📂 Spec目录: {result.spec_dir.relative_to(PROJECT_ROOT)}")
    print(f"{'='*60}")

    if result.errors:
        for err in result.errors:
            print(f"  ⚠️  {err}")
        if not result.has_work and not result.keep_files:
            return

    print(f"\n  📋 保留文件（{len(result.keep_files)}个）:")
    for f in sorted(result.keep_files, key=lambda x: x.name.lower()):
        rel = f.relative_to(result.spec_dir)
        print(f"     ✅ {rel}")

    if result.to_archive:
        print(f"\n  📦 待归档文件（{len(result.to_archive)}个）:")
        for f in sorted(result.to_archive, key=lambda x: x.name.lower()):
            reason = ""
            for cond_f, cond_reason in result.conditional:
                if cond_f == f:
                    reason = f"  ← {cond_reason}"
                    break
            size_kb = f.stat().st_size / 1024
            print(f"     📄 {f.name} ({size_kb:.0f}KB){reason}")

    if result.skipped_dirs:
        print(f"\n  📁 嵌套spec子目录（跳过，单独处理）:")
        for d in result.skipped_dirs:
            print(f"     📂 {d.name}/")

    if not result.has_work:
        print(f"\n  ✨ 该目录无需清理，结构已精简。")
    else:
        action = "删除" if False else "归档至 _archive/"
        print(f"\n  💡 运行 --execute 以执行{action}操作。")
        print(f"     加 --delete 直接删除而不归档（不可逆）。")


def print_summary(results: list[CleanupResult], executed: bool = False,
                  delete_mode: bool = False) -> None:
    """打印汇总信息。"""
    total_to_clean = sum(r.total_to_clean for r in results)
    total_archived = sum(r.archived_count for r in results)
    total_deleted = sum(r.deleted_count for r in results)
    dirs_with_work = sum(1 for r in results if r.has_work)
    total_errors = sum(len(r.errors) for r in results)

    print(f"\n{'='*60}")
    print(f"📊 汇总")
    print(f"{'='*60}")
    print(f"  扫描spec目录: {len(results)}个")
    print(f"  需清理的目录: {dirs_with_work}个")
    print(f"  待清理文件数: {total_to_clean}个")

    if executed:
        action = "删除" if delete_mode else "归档"
        print(f"  已{action}文件: {total_archived + total_deleted}个", end="")
        if not delete_mode:
            print(f"（归档{total_archived}个）", end="")
        print()
        if total_errors:
            print(f"  错误: {total_errors}个")
    else:
        print(f"\n  💡 这是DRY-RUN预览，未执行任何操作。")
        print(f"     加 --execute 执行归档，加 --execute --delete 直接删除。")

    if not delete_mode and executed and total_archived > 0:
        print(f"\n  📁 归档位置: {ARCHIVE_ROOT.relative_to(PROJECT_ROOT)}/")
        print(f"     归档文件可随时恢复，确认无误后可手动清理_archive目录。")


def find_all_spec_dirs() -> list[Path]:
    """扫描所有spec目录。"""
    specs = []
    if not SPECS_DIR.exists():
        return specs

    def _scan(d: Path):
        if (d / "spec.md").exists():
            specs.append(d)
        for child in sorted(d.iterdir()):
            if child.is_dir() and not child.name.startswith("_"):
                _scan(child)

    _scan(SPECS_DIR)
    return specs


def main():
    parser = argparse.ArgumentParser(
        description="Spec工作目录清理脚本——归档中间产物，保持目录精简",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "-d", "--dir",
        help="要清理的spec目录路径（相对项目根或绝对路径），默认使用当前工作目录",
    )
    parser.add_argument(
        "--scan-all",
        action="store_true",
        help="扫描所有spec目录，列出可清理项",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="执行清理（默认dry-run预览）",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="直接删除文件而非归档（不可逆！）",
    )
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="跳过确认提示（与--execute配合使用）",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="静默模式，只输出汇总",
    )

    args = parser.parse_args()

    if args.delete and not args.execute:
        print("❌ --delete 必须与 --execute 配合使用")
        sys.exit(1)

    spec_dirs: list[Path] = []

    if args.scan_all:
        spec_dirs = find_all_spec_dirs()
        if not spec_dirs:
            print("未找到任何spec目录。")
            sys.exit(0)
    elif args.dir:
        d = Path(args.dir)
        if not d.is_absolute():
            d = PROJECT_ROOT / d
        spec_dirs = [d.resolve()]
    else:
        cwd = Path.cwd().resolve()
        if (cwd / "spec.md").exists():
            spec_dirs = [cwd]
        else:
            for parent in [cwd] + list(cwd.parents):
                if (parent / "spec.md").exists():
                    spec_dirs = [parent]
                    break
            if not spec_dirs:
                spec_dirs = [cwd]

    results = []
    for sd in spec_dirs:
        result = analyze_spec_dir(sd)
        results.append(result)
        if not args.quiet:
            print_preview(result)

    has_work = any(r.has_work for r in results)

    if args.execute and has_work:
        if not args.yes:
            action = "删除" if args.delete else "归档"
            total = sum(r.total_to_clean for r in results)
            print(f"\n⚠️  即将{action} {total} 个文件", end="")
            if args.delete:
                print("（不可恢复！）", end="")
            else:
                print(f"到 {ARCHIVE_ROOT.relative_to(PROJECT_ROOT)}/", end="")
            print()
            try:
                resp = input("确认执行？(y/N): ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                resp = "n"
            if resp != "y":
                print("已取消。")
                print_summary(results, executed=False)
                sys.exit(0)

        for result in results:
            if not args.quiet:
                print(f"\n🔧 处理: {result.spec_dir.relative_to(PROJECT_ROOT)}")
            execute_cleanup(result, delete_mode=args.delete, verbose=not args.quiet)

    print_summary(results, executed=args.execute, delete_mode=args.delete)

    if args.execute and has_work:
        errors = sum(len(r.errors) for r in results)
        sys.exit(1 if errors else 0)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
