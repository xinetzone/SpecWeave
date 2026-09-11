#!/usr/bin/env python3
"""Wiki / 知识库新鲜度检查脚本。

扫描 Markdown 文件 frontmatter 中的 last_verified 字段，计算距今天数并输出
过期报告；支持把过期条目标注为 status: needs-update（待更新）。

两种目标：
  1. 知识库预设（仓库内 docs/knowledge，递归，自动排除机器生成索引）：
       python .agents/scripts/check-wiki-staleness.py --knowledge
  2. 外部 Wiki 目录（保持原有用法）：
       python .agents/scripts/check-wiki-staleness.py --wiki <wiki-dir-name>
       python .agents/scripts/check-wiki-staleness.py --path <absolute-path-to-wiki>

标注动作（只改写 frontmatter，不改正文；status: deprecated 的条目跳过）：
       python .agents/scripts/check-wiki-staleness.py --knowledge --mark-stale
       python .agents/scripts/check-wiki-staleness.py --knowledge --mark-missing

退出码:
    0 - 所有文件新鲜（无过期、无缺失）
    1 - 存在过期文件或缺失 last_verified 字段
    2 - 参数/路径错误
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

# ---- 常量 ----

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]  # .agents/scripts -> 仓库根
KNOWLEDGE_DIR = REPO_ROOT / "docs" / "knowledge"

# 外部 Wiki 的历史默认根（learning/ 已于 2026-09 迁移至 OKF bundles）
DEFAULT_WIKI_ROOT = REPO_ROOT / "docs" / "knowledge" / "learning"
BUNDLES_ROOT = REPO_ROOT / "projects" / "awesome-okf-xs" / "doc" / "bundles"

DEFAULT_THRESHOLD_DAYS = 90

# 知识库预设的排除规则，与 docs/knowledge/scripts/constants.py 同源语义：
# GENERATED_DIRS（机器生成）+ EXCLUDE_FILES（模板/入口页）
KNOWLEDGE_EXCLUDE_DIRS = {"scripts", "tags", "categories"}
KNOWLEDGE_EXCLUDE_FILES = {"template.md", "readme.md", "category-index.md"}

# 过期条目的机器可读状态值（中文展示名"待更新"，规范文档见
# docs/knowledge/operations/knowledge-review-mechanism.md）
STATUS_NEEDS_UPDATE = "needs-update"
# 显式退役的条目不参与新鲜度标注
SKIP_MARK_STATUSES = {"deprecated"}

# 单次标注动作的安全批量上限：超过须显式 --force。
# 防止误把全量 MISSING（如机制建立日的 249 条无基线条目）一键改写。
MARK_BATCH_LIMIT = 20

YAML_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*$", re.MULTILINE | re.DOTALL)

# ANSI 颜色（Windows 终端兼容）
try:
    import colorama
    colorama.just_fix_windows_console()
    RED = "\033[31m"
    YELLOW = "\033[33m"
    GREEN = "\033[32m"
    CYAN = "\033[36m"
    RESET = "\033[0m"
except ImportError:
    RED = YELLOW = GREEN = CYAN = RESET = ""


@dataclass
class FileStatus:
    path: Path
    last_verified: date | None
    days_since: int | None
    status: str  # "fresh" | "stale" | "missing"
    title: str = ""
    current_status: str = ""
    has_frontmatter: bool = True
    marked: bool = False
    mark_note: str = ""  # "updated" | "already" | "skipped-deprecated" | "no-frontmatter" | ""


def parse_frontmatter(path: Path) -> tuple[dict, str] | None:
    """提取 YAML frontmatter 并解析基础字段。返回 (fields_dict, body) 或 None。"""
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        print(f"{RED}[ERROR]{RESET} Cannot read {path}: {e}", file=sys.stderr)
        return None

    m = YAML_FM_RE.match(content)
    if not m:
        return {}, content

    fm_text = m.group(1)
    body = content[m.end():]

    fields: dict[str, str] = {}
    for line in fm_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if val and not val.startswith("[") and not val.startswith("{"):
                fields[key] = val
    return fields, body


def _is_excluded(md_file: Path, root: Path,
                 exclude_dirs: set[str], exclude_files: set[str]) -> bool:
    """按相对路径部件判定文件是否在排除集合内。"""
    try:
        rel_parts = md_file.relative_to(root).parts
    except ValueError:
        return False
    if any(part in exclude_dirs for part in rel_parts[:-1]):
        return True
    if md_file.name.lower() in exclude_files:
        return True
    return False


def iter_markdown(root: Path, recursive: bool,
                  exclude_dirs: set[str] | None = None,
                  exclude_files: set[str] | None = None):
    """枚举待检查的 Markdown 文件（统一排序，保证报告稳定）。"""
    exclude_dirs = exclude_dirs or set()
    exclude_files = exclude_files or set()
    iterator = root.rglob("*.md") if recursive else root.glob("*.md")
    for md_file in sorted(iterator):
        if _is_excluded(md_file, root, exclude_dirs, exclude_files):
            continue
        yield md_file


def check_wiki(wiki_path: Path, threshold_days: int, *,
               recursive: bool = True,
               exclude_dirs: set[str] | None = None,
               exclude_files: set[str] | None = None) -> list[FileStatus]:
    """扫描目录下所有 .md 文件，返回每个文件的新鲜度状态。"""
    if not wiki_path.is_dir():
        print(f"{RED}[ERROR]{RESET} Wiki directory not found: {wiki_path}", file=sys.stderr)
        sys.exit(2)

    today = date.today()
    results: list[FileStatus] = []

    for md_file in iter_markdown(wiki_path, recursive, exclude_dirs, exclude_files):
        parsed = parse_frontmatter(md_file)
        if parsed is None:
            results.append(FileStatus(md_file, None, None, "missing",
                                      has_frontmatter=False))
            continue
        fields, _ = parsed
        title = fields.get("title", md_file.stem)
        current_status = fields.get("status", "")

        lv_str = fields.get("last_verified")
        if not lv_str:
            results.append(FileStatus(md_file, None, None, "missing", title,
                                      current_status=current_status,
                                      has_frontmatter=bool(fields)))
            continue

        try:
            lv_date = datetime.strptime(lv_str, "%Y-%m-%d").date()
        except ValueError:
            results.append(FileStatus(md_file, None, None, "missing", title,
                                      current_status=current_status,
                                      has_frontmatter=bool(fields)))
            continue

        days = (today - lv_date).days
        state = "stale" if days > threshold_days else "fresh"
        results.append(FileStatus(md_file, lv_date, days, state, title,
                                  current_status=current_status,
                                  has_frontmatter=True))

    return results


def mark_needs_update(path: Path) -> str:
    """把文件 frontmatter 的 status 置为 needs-update。

    返回处置说明：
      updated            - 已写入/新增 status
      already            - 原本就是 needs-update
      skipped-deprecated - status 为 deprecated，显式退役不动
      no-frontmatter     - 无 frontmatter，不自动合成，跳过
    """
    content = path.read_text(encoding="utf-8")
    m = YAML_FM_RE.match(content)
    if not m:
        return "no-frontmatter"

    fm_text = m.group(1)
    lines = fm_text.splitlines()

    status_line_re = re.compile(r"^(\s*status\s*:\s*).*$")
    for i, line in enumerate(lines):
        sm = status_line_re.match(line)
        if sm:
            current = line.split(":", 1)[1].strip().strip('"').strip("'")
            if current == STATUS_NEEDS_UPDATE:
                return "already"
            if current in SKIP_MARK_STATUSES:
                return "skipped-deprecated"
            lines[i] = f"{sm.group(1)}{STATUS_NEEDS_UPDATE}"
            new_fm = "\n".join(lines)
            path.write_text(content[:m.start(1)] + new_fm + content[m.end(1):],
                            encoding="utf-8")
            return "updated"

    # 无 status 行：在 frontmatter 结束符前插入
    lines.append(f"status: {STATUS_NEEDS_UPDATE}")
    new_fm = "\n".join(lines)
    path.write_text(content[:m.start(1)] + new_fm + content[m.end(1):],
                    encoding="utf-8")
    return "updated"


def apply_marks(results: list[FileStatus], mark_stale: bool,
                mark_missing: bool) -> int:
    """按开关对目标文件执行标注，返回实际改写文件数。"""
    targets: list[FileStatus] = []
    if mark_stale:
        targets.extend(r for r in results if r.status == "stale")
    if mark_missing:
        targets.extend(r for r in results if r.status == "missing")

    changed = 0
    for r in targets:
        note = mark_needs_update(r.path)
        r.marked = note == "updated"
        r.mark_note = note
        if note == "updated":
            changed += 1
    return changed


def print_report(results: list[FileStatus], wiki_name: str, threshold_days: int,
                 marks_applied: bool = False) -> int:
    """打印报告表格，返回过期+缺失的总数（用于退出码）。"""
    today = date.today()
    stale = [r for r in results if r.status == "stale"]
    missing = [r for r in results if r.status == "missing"]
    fresh = [r for r in results if r.status == "fresh"]

    print()
    print(f"{CYAN}{'='*70}{RESET}")
    print(f"{CYAN}  Wiki Freshness Report: {wiki_name}{RESET}")
    print(f"{CYAN}  Today: {today.isoformat()}  |  Threshold: {threshold_days} days{RESET}")
    print(f"{CYAN}{'='*70}{RESET}")
    print()

    # 详细表格
    print(f"  {'File':<35} {'Last Verified':<14} {'Days':>5}  Status")
    print(f"  {'-'*35} {'-'*14} {'-'*5}  {'-'*10}")
    for r in results:
        name = r.path.name
        if len(name) > 34:
            name = name[:31] + "..."
        lv = r.last_verified.isoformat() if r.last_verified else "N/A"
        days = f"{r.days_since:>5}" if r.days_since is not None else "  N/A"
        if r.status == "fresh":
            tag = f"{GREEN}✓ fresh{RESET}"
        elif r.status == "stale":
            tag = f"{RED}✗ STALE{RESET}"
        else:
            tag = f"{YELLOW}⚠ MISSING{RESET}"
        print(f"  {name:<35} {lv:<14} {days}  {tag}")

    print()
    print(f"{CYAN}{'='*70}{RESET}")
    print(f"  Summary:  {GREEN}{len(fresh)} fresh{RESET}  "
          f"{RED}{len(stale)} stale{RESET}  "
          f"{YELLOW}{len(missing)} missing last_verified{RESET}  "
          f"/ {len(results)} total files")
    print(f"{CYAN}{'='*70}{RESET}")
    print()

    if stale:
        print(f"{RED}Stale files (last_verified 超过 {threshold_days} 天):{RESET}")
        for r in stale:
            extra = _mark_suffix(r)
            print(f"  - {r.path.name}: last verified {r.last_verified} "
                  f"({r.days_since} days ago){extra}")
        print()

    if missing:
        print(f"{YELLOW}Files missing 'last_verified' frontmatter field:{RESET}")
        for r in missing:
            extra = _mark_suffix(r)
            no_fm = " [无 frontmatter，需人工补建]" if not r.has_frontmatter else ""
            print(f"  - {r.path.name}{no_fm}{extra}")
        print()

    if marks_applied:
        marked = [r for r in results if r.mark_note]
        updated = [r for r in marked if r.mark_note == "updated"]
        skipped_dep = [r for r in marked if r.mark_note == "skipped-deprecated"]
        no_fm = [r for r in marked if r.mark_note == "no-frontmatter"]
        already = [r for r in marked if r.mark_note == "already"]
        print(f"{CYAN}--mark 结果：{RESET}改写 {len(updated)} 个；"
              f"已是 needs-update {len(already)} 个；"
              f"deprecated 跳过 {len(skipped_dep)} 个；"
              f"无 frontmatter 跳过 {len(no_fm)} 个。")
        print("被标注条目须经人工复核：确认后更新 last_verified 并恢复 status，")
        print("同时在 docs/knowledge/operations/knowledge-review-log.md 登记一行。")
        print()

    if not stale and not missing:
        print(f"{GREEN}✓ All files are within freshness threshold. No action needed.{RESET}")
        print()

    return len(stale) + len(missing)


def _mark_suffix(r: FileStatus) -> str:
    if r.mark_note == "updated" or r.mark_note == "already":
        return f" {YELLOW}-> {STATUS_NEEDS_UPDATE}{RESET}"
    if r.mark_note == "skipped-deprecated":
        return " [deprecated，跳过]"
    if r.mark_note == "no-frontmatter":
        return " [无 frontmatter，跳过]"
    return ""


def find_wiki_path(wiki_name: str | None, explicit_path: str | None) -> Path:
    """根据 --wiki 名或 --path 解析 wiki 目录绝对路径。"""
    if explicit_path:
        p = Path(explicit_path)
        if not p.is_absolute():
            p = Path.cwd() / p
        return p

    if wiki_name:
        # 历史默认根 learning/ 已迁移；根不存在时给出可操作的错误信息
        if not DEFAULT_WIKI_ROOT.is_dir():
            print(
                f"{RED}[ERROR]{RESET} 历史 Wiki 根已迁移：{DEFAULT_WIKI_ROOT} 不存在。\n"
                f"        外部学习 Wiki 新位置：{BUNDLES_ROOT}\n"
                f"        请改用 --path <绝对路径>；检查仓库知识库请用 --knowledge。",
                file=sys.stderr,
            )
            sys.exit(2)
        # 在 learning 目录下的各分类中搜索 wiki 子目录
        for category in DEFAULT_WIKI_ROOT.iterdir():
            if not category.is_dir():
                continue
            candidate = category / wiki_name
            if candidate.is_dir():
                return candidate
        # 直接路径尝试
        candidate = DEFAULT_WIKI_ROOT / wiki_name
        if candidate.is_dir():
            return candidate
        print(f"{RED}[ERROR]{RESET} Cannot find wiki '{wiki_name}' under {DEFAULT_WIKI_ROOT}", file=sys.stderr)
        sys.exit(2)

    print(f"{RED}[ERROR]{RESET} Must specify --knowledge, --wiki or --path", file=sys.stderr)
    sys.exit(2)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check documentation freshness by scanning last_verified frontmatter field."
    )
    parser.add_argument("--knowledge", action="store_true",
                        help="知识库预设：递归扫描 docs/knowledge（排除 scripts/tags/categories 与入口页）")
    parser.add_argument("--wiki", help="Wiki directory name (searched under learning/)")
    parser.add_argument("--path", help="Absolute path to a wiki/knowledge directory (recursive)")
    parser.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD_DAYS,
                        help=f"Days before considering a file stale (default: {DEFAULT_THRESHOLD_DAYS})")
    parser.add_argument("--mark-stale", action="store_true",
                        help=f"把过期文件 frontmatter status 置为 {STATUS_NEEDS_UPDATE}（deprecated 跳过）")
    parser.add_argument("--mark-missing", action="store_true",
                        help="把缺失 last_verified 且含 frontmatter 的文件 status 置为 "
                             f"{STATUS_NEEDS_UPDATE}，供存量积压分批待复核")
    parser.add_argument("--force", action="store_true",
                        help=f"允许单次标注超过 {MARK_BATCH_LIMIT} 个目标（默认有批量护栏）")
    args = parser.parse_args()

    if args.knowledge:
        wiki_path = KNOWLEDGE_DIR
        wiki_name = "docs/knowledge"
        results = check_wiki(
            wiki_path, args.threshold,
            recursive=True,
            exclude_dirs=KNOWLEDGE_EXCLUDE_DIRS,
            exclude_files=KNOWLEDGE_EXCLUDE_FILES,
        )
    else:
        wiki_path = find_wiki_path(args.wiki, args.path)
        wiki_name = wiki_path.name
        # 外部 Wiki：递归扫描（OKF 三层结构含子目录）
        results = check_wiki(wiki_path, args.threshold, recursive=True)

    mark_targets = 0
    if args.mark_stale:
        mark_targets += sum(1 for r in results if r.status == "stale")
    if args.mark_missing:
        mark_targets += sum(1 for r in results if r.status == "missing")

    if mark_targets > MARK_BATCH_LIMIT and not args.force:
        print(
            f"{RED}[ERROR]{RESET} 本次标注目标 {mark_targets} 个，超过安全批量上限 "
            f"{MARK_BATCH_LIMIT} 个。\n"
            "        请按分类/目录分批运行（--path 指向子目录），每批 ≤ "
            f"{MARK_BATCH_LIMIT} 并逐个人工复核；\n"
            "        如确需一次性全量改写，显式加 --force。",
            file=sys.stderr,
        )
        sys.exit(2)

    changed = apply_marks(results, args.mark_stale, args.mark_missing)
    problems = print_report(results, wiki_name, args.threshold,
                            marks_applied=bool(changed or args.mark_stale or args.mark_missing))
    return 1 if problems > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
