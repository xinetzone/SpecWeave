#!/usr/bin/env python3
"""Wiki 新鲜度检查脚本。

扫描指定 Wiki 目录下所有 .md 文件的 frontmatter，检查 last_verified 字段，
计算距今天数，输出过期报告。用于 T2 季度体检触发器。

用法:
    python .agents/scripts/check-wiki-staleness.py --wiki <wiki-dir-name>
    python .agents/scripts/check-wiki-staleness.py --path <absolute-path-to-wiki>
    python .agents/scripts/check-wiki-staleness.py --wiki volcengine-agentkit-wiki --threshold 90

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

DEFAULT_WIKI_ROOT = Path("d:/AI/.agents/docs/knowledge/learning")
DEFAULT_THRESHOLD_DAYS = 90
YAML_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*$", re.MULTILINE | re.DOTALL)
LAST_VERIFIED_RE = re.compile(r"^last_verified\s*:\s*[\"']?(\d{4}-\d{2}-\d{2})[\"']?\s*$", re.MULTILINE)

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


def check_wiki(wiki_path: Path, threshold_days: int) -> list[FileStatus]:
    """扫描目录下所有 .md 文件，返回每个文件的新鲜度状态。"""
    if not wiki_path.is_dir():
        print(f"{RED}[ERROR]{RESET} Wiki directory not found: {wiki_path}", file=sys.stderr)
        sys.exit(2)

    today = date.today()
    results: list[FileStatus] = []

    for md_file in sorted(wiki_path.glob("*.md")):
        # 跳过 MAINTENANCE.md 自身和 README.md（入口文件不强制 last_verified）
        # 但仍检查以便提醒
        parsed = parse_frontmatter(md_file)
        if parsed is None:
            results.append(FileStatus(md_file, None, None, "missing"))
            continue
        fields, _ = parsed
        title = fields.get("title", md_file.stem)

        lv_str = fields.get("last_verified")
        if not lv_str:
            results.append(FileStatus(md_file, None, None, "missing", title))
            continue

        try:
            lv_date = datetime.strptime(lv_str, "%Y-%m-%d").date()
        except ValueError:
            results.append(FileStatus(md_file, None, None, "missing", title))
            continue

        days = (today - lv_date).days
        status = "stale" if days > threshold_days else "fresh"
        results.append(FileStatus(md_file, lv_date, days, status, title))

    return results


def print_report(results: list[FileStatus], wiki_name: str, threshold_days: int) -> int:
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
        print(f"{RED}Stale files (need T2 quarterly verification):{RESET}")
        for r in stale:
            print(f"  - {r.path.name}: last verified {r.last_verified} ({r.days_since} days ago)")
        print()

    if missing:
        print(f"{YELLOW}Files missing 'last_verified' frontmatter field:{RESET}")
        for r in missing:
            print(f"  - {r.path.name}")
        print()

    if not stale and not missing:
        print(f"{GREEN}✓ All files are within freshness threshold. No action needed.{RESET}")
        print()

    return len(stale) + len(missing)


def find_wiki_path(wiki_name: str | None, explicit_path: str | None) -> Path:
    """根据 --wiki 名或 --path 解析 wiki 目录绝对路径。"""
    if explicit_path:
        p = Path(explicit_path)
        if not p.is_absolute():
            p = Path.cwd() / p
        return p

    if wiki_name:
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

    print(f"{RED}[ERROR]{RESET} Must specify --wiki or --path", file=sys.stderr)
    sys.exit(2)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check wiki documentation freshness by scanning last_verified frontmatter field."
    )
    parser.add_argument("--wiki", help="Wiki directory name (searched under learning/)")
    parser.add_argument("--path", help="Absolute path to wiki directory")
    parser.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD_DAYS,
                        help=f"Days before considering a file stale (default: {DEFAULT_THRESHOLD_DAYS})")
    args = parser.parse_args()

    wiki_path = find_wiki_path(args.wiki, args.path)
    wiki_name = wiki_path.name
    results = check_wiki(wiki_path, args.threshold)
    problems = print_report(results, wiki_name, args.threshold)
    return 1 if problems > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
