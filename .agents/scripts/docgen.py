#!/usr/bin/env python3
"""文档索引与看板生成统一工具。

聚合以下文档生成功能：
  nav        - 自动生成 README.md / docs/README.md 文档导航表
  dashboard  - 自动生成 .trae/specs/ 执行进度看板
  apps       - 自动生成 apps/README.md 应用清单索引表
  all        - 依次执行 nav + dashboard + apps

用法：
  python docgen.py nav
  python docgen.py dashboard
  python docgen.py apps
  python docgen.py all
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from constants import SCAN_DIRS, ROOT_FILES, TARGETS, MANUAL_DESCRIPTIONS, EXCLUDED_DIRS
from lib.frontmatter import parse_toml_frontmatter, extract_all_fields
from lib.markdown import (
    extract_description as _extract_description,
    extract_title as _extract_title,
    update_marker_region,
)
from lib.project import resolve_project_root


UNCHECKED_LIST_RE = re.compile(r"^- \[ \]", re.MULTILINE)
CHECKED_LIST_RE = re.compile(r"^- \[x\]", re.MULTILINE | re.IGNORECASE)
UNCHECKED_HEADING_RE = re.compile(r"^##+ \[ \]", re.MULTILINE)
CHECKED_HEADING_RE = re.compile(r"^##+ \[x\]", re.MULTILINE | re.IGNORECASE)
YAML_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*$", re.MULTILINE | re.DOTALL)
COMPLETED_STATUSES = {"completed", "done", "finished", "complete"}
THEME_ORDER = [
    "core-foundation",
    "roles-governance",
    "standards-tools",
    "readme-branding",
    "docs-restructure",
    "retrospectives-insights",
    "migration-archival",
]


# ============================================================
# nav 子命令：文档导航表生成
# ============================================================

def _nav_extract_title(file_path: Path) -> str:
    title = _extract_title(file_path)
    return title if title else file_path.stem


def _nav_extract_description(file_path: Path) -> str:
    name = file_path.name
    if name in MANUAL_DESCRIPTIONS:
        return MANUAL_DESCRIPTIONS[name]
    desc = _extract_description(file_path)
    if desc:
        if len(desc) > 60:
            desc = desc[:57] + "..."
        return desc
    return _nav_extract_title(file_path)


def _nav_scan_docs(root: Path) -> list[tuple[str, str, str, bool]]:
    entries = []
    for scan_dir, link_prefix in SCAN_DIRS:
        scan_path = root / scan_dir
        if scan_path.exists():
            for md_file in sorted(scan_path.glob("*.md")):
                if md_file.name == "README.md":
                    continue
                title = _nav_extract_title(md_file)
                desc = _nav_extract_description(md_file)
                entries.append((title, md_file.name, desc, False))
    for rf in ROOT_FILES:
        rf_path = root / rf
        if rf_path.exists():
            title = _nav_extract_title(rf_path)
            desc = _nav_extract_description(rf_path)
            entries.append((title, rf, desc, True))
    return entries


def _nav_generate_table(entries, link_prefix, root_files_prefix) -> str:
    lines = ["| 文档 | 说明 |", "|------|------|"]
    for title, filename, desc, is_root_file in entries:
        link = f"{root_files_prefix}{filename}" if is_root_file else f"{link_prefix}{filename}"
        lines.append(f"| [{title}]({link}) | {desc} |")
    return "\n".join(lines)


def cmd_nav(args) -> int:
    root = args.path or resolve_project_root(__file__)
    if not root.exists():
        print(f"错误: 项目根目录不存在: {root}", file=sys.stderr)
        return 1

    print("扫描文档目录...")
    entries = _nav_scan_docs(root)
    print(f"  找到 {len(entries)} 个文档")

    print("\n更新目标文件...")
    updated = 0
    for target_file, config in TARGETS.items():
        target_path = root / target_file
        if not target_path.exists():
            print(f"  跳过: {target_file} 不存在")
            continue
        table = _nav_generate_table(entries, config["link_prefix"], config["root_files_prefix"])
        try:
            update_marker_region(target_path, config["marker_start"], config["marker_end"], table)
            print(f"  已更新: {target_file}")
            updated += 1
        except ValueError:
            print(f"  警告: {target_path} 中未找到标记 {config['marker_start']} / {config['marker_end']}，跳过")

    if updated == 0:
        print("  未更新任何文件", file=sys.stderr)
        return 1
    print(f"\n完成: 已更新 {updated} 个文件")
    return 0


# ============================================================
# dashboard 子命令：Spec 执行进度看板
# ============================================================

@dataclass
class SpecStatus:
    name: str
    completed: bool
    total_tasks: int
    done_tasks: int


@dataclass
class ThemeStatus:
    name: str
    specs: list[SpecStatus]

    @property
    def total(self) -> int:
        return len(self.specs)

    @property
    def completed_count(self) -> int:
        return sum(1 for s in self.specs if s.completed)

    @property
    def in_progress_count(self) -> int:
        return sum(1 for s in self.specs if not s.completed and s.done_tasks > 0)

    @property
    def pending_count(self) -> int:
        return sum(1 for s in self.specs if not s.completed and s.done_tasks == 0)

    @property
    def progress(self) -> int:
        if self.total == 0:
            return 100
        return int(self.completed_count / self.total * 100)


def _dash_parse_yaml_simple(content: str) -> dict[str, str]:
    match = YAML_FRONTMATTER_RE.match(content)
    if not match:
        return {}
    result = {}
    for line in match.group(1).split("\n"):
        line = line.strip()
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                result[key] = value
    return result


def _dash_scan_spec(spec_dir: Path) -> SpecStatus:
    tasks_file = spec_dir / "tasks.md"
    if not tasks_file.exists():
        return SpecStatus(name=spec_dir.name, completed=False, total_tasks=0, done_tasks=0)

    content = tasks_file.read_text(encoding="utf-8")
    status_from_fm = None

    toml_fm = parse_toml_frontmatter(tasks_file)
    if toml_fm:
        fields = extract_all_fields(toml_fm)
        s = fields.get("status", "").lower().strip()
        if s:
            status_from_fm = s

    if status_from_fm is None:
        yaml_fields = _dash_parse_yaml_simple(content)
        s = yaml_fields.get("status", "").lower().strip()
        if s:
            status_from_fm = s

    in_code_block = False
    filtered_lines = []
    for line in content.split("\n"):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if not in_code_block:
            filtered_lines.append(line)
    filtered = "\n".join(filtered_lines)

    unchecked = len(UNCHECKED_LIST_RE.findall(filtered)) + len(UNCHECKED_HEADING_RE.findall(filtered))
    checked = len(CHECKED_LIST_RE.findall(filtered)) + len(CHECKED_HEADING_RE.findall(filtered))
    total_tasks = unchecked + checked

    if status_from_fm in COMPLETED_STATUSES:
        completed = True
        done_tasks = total_tasks
    else:
        completed = unchecked == 0 and total_tasks > 0
        done_tasks = checked

    return SpecStatus(name=spec_dir.name, completed=completed, total_tasks=total_tasks, done_tasks=done_tasks)


def _dash_scan_themes(specs_root: Path) -> list[ThemeStatus]:
    themes = []
    theme_dirs = sorted([d for d in specs_root.iterdir() if d.is_dir() and d.name not in EXCLUDED_DIRS])

    ordered = []
    for name in THEME_ORDER:
        p = specs_root / name
        if p.exists() and p.is_dir():
            ordered.append(p)
    for td in theme_dirs:
        if td not in ordered:
            ordered.append(td)

    for theme_dir in ordered:
        spec_dirs = sorted([
            d for d in theme_dir.iterdir()
            if d.is_dir() and d.name not in EXCLUDED_DIRS and (d / "tasks.md").exists()
        ])
        specs = [_dash_scan_spec(d) for d in spec_dirs]
        themes.append(ThemeStatus(name=theme_dir.name, specs=specs))
    return themes


def _dash_generate_table(themes: list[ThemeStatus]) -> str:
    total_specs = sum(t.total for t in themes)
    total_completed = sum(t.completed_count for t in themes)
    total_ip = sum(t.in_progress_count for t in themes)
    total_pending = sum(t.pending_count for t in themes)
    pct = int(total_completed / total_specs * 100) if total_specs > 0 else 0

    lines = []
    if total_completed == total_specs:
        lines.append(f"**整体进度：{total_completed}/{total_specs} 完成 · {pct}% · 0 项进行中 · 0 项待启动** 🎉")
    else:
        lines.append(f"**整体进度：{total_completed}/{total_specs} 完成 · {pct}% · {total_ip} 项进行中 · {total_pending} 项待启动**")
    lines.append("")
    lines.append("| 主题 | Spec 数 | 已完成 | 状态 | 看板 |")
    lines.append("|---|---|---|---|---|")
    for theme in themes:
        tlink = f".trae/specs/{theme.name}/"
        rlink = f".trae/specs/{theme.name}/README.md"
        if theme.progress == 100:
            st = f"✅ {theme.progress}%"
        elif theme.progress == 0:
            st = f"📋 {theme.progress}%"
        else:
            st = f"🔧 {theme.progress}%"
        lines.append(f"| [{theme.name}]({tlink}) | {theme.total} | {theme.completed_count} | {st} | [查看]({rlink}) |")
    lines.append("")
    lines.append("> 详细进度、待办事项、里程碑路线图与跨主题依赖关系见 [全局执行看板](.trae/specs/README.md)。")
    return "\n".join(lines)


def cmd_dashboard(args) -> int:
    root = args.path or resolve_project_root(__file__)
    specs_root = root / ".trae" / "specs"
    if not specs_root.exists():
        print(f"错误: Specs 目录不存在: {specs_root}", file=sys.stderr)
        return 1

    print("扫描 Spec 目录...")
    themes = _dash_scan_themes(specs_root)
    total_specs = sum(t.total for t in themes)
    total_completed = sum(t.completed_count for t in themes)
    print(f"  找到 {len(themes)} 个主题，{total_specs} 个 Spec")
    for theme in themes:
        print(f"    - {theme.name}: {theme.completed_count}/{theme.total} 完成")

    print("\n生成根 README.md 看板...")
    root_readme = root / "README.md"
    table = _dash_generate_table(themes)

    if not root_readme.exists():
        print(f"  警告: {root_readme} 不存在，跳过")
        return 1

    ms, me = "<!-- SPEC_DASHBOARD_START -->", "<!-- SPEC_DASHBOARD_END -->"
    try:
        update_marker_region(root_readme, ms, me, table)
    except ValueError:
        print(f"  警告: {root_readme} 中未找到标记 {ms} / {me}，跳过")
        return 1

    print(f"  已更新: {root_readme}")
    print(f"\n完成: 看板数据已从 {total_completed}/{total_specs} Spec 聚合生成")
    return 0


# ============================================================
# apps 子命令：应用清单索引表
# ============================================================

def _apps_extract_title(readme_path: Path, app_dir: str) -> str:
    if not readme_path.exists():
        return app_dir
    t = _extract_title(readme_path)
    return t if t else app_dir


def _apps_extract_desc(readme_path: Path, app_dir: str) -> str:
    if not readme_path.exists():
        return f"{app_dir} 应用"
    d = _extract_description(readme_path)
    if d:
        if len(d) > 80:
            d = d[:77] + "..."
        return d
    return _apps_extract_title(readme_path, app_dir)


def _apps_scan(apps_dir: Path) -> list[tuple[str, str, str]]:
    entries = []
    for item in sorted(apps_dir.iterdir()):
        if not item.is_dir():
            continue
        if item.name.startswith(".") or item.name == "shared":
            continue
        readme = item / "README.md"
        entries.append((item.name, _apps_extract_title(readme, item.name), _apps_extract_desc(readme, item.name)))
    return entries


def _apps_generate_table(entries) -> str:
    lines = ["| 应用 | 说明 | 入口 |", "|---|---|---|"]
    for dir_name, _title, desc in entries:
        lines.append(f"| `{dir_name}/` | {desc} | [README.md]({dir_name}/README.md) |")
    return "\n".join(lines)


def _apps_update_compat(content: str, table: str) -> str | None:
    section = "### 2.3 应用清单"
    idx = content.find(section)
    if idx == -1:
        return None
    after = content[idx + len(section):]
    ts = after.find("| 应用 |")
    if ts == -1:
        ts = after.find("\n\n") + 2
    else:
        ls = after.rfind("\n", 0, ts)
        ts = ls + 1 if ls != -1 else ts
    te = after.find("\n## ", ts)
    if te == -1:
        te = len(after)
    return content[: idx + len(section)] + after[:ts] + table + "\n" + after[te:]


def cmd_apps(args) -> int:
    root = args.path or resolve_project_root(__file__)
    apps_dir = root / "apps"
    target = apps_dir / "README.md"

    if not apps_dir.exists():
        print(f"错误: apps/ 目录不存在: {apps_dir}", file=sys.stderr)
        return 1
    if not target.exists():
        print(f"错误: apps/README.md 不存在: {target}", file=sys.stderr)
        return 1

    print("扫描 apps/ 目录...")
    entries = _apps_scan(apps_dir)
    print(f"  找到 {len(entries)} 个应用")
    for d, title, _desc in entries:
        print(f"    - {d}: {title}")

    print("\n生成应用清单表...")
    table = _apps_generate_table(entries)
    ms, me = "<!-- APPS_TABLE_START -->", "<!-- APPS_TABLE_END -->"

    try:
        update_marker_region(target, ms, me, table)
    except ValueError:
        print(f"  警告: {target} 中未找到标记 {ms} / {me}，回退到兼容模式")
        content = target.read_text(encoding="utf-8")
        new_content = _apps_update_compat(content, table)
        if new_content is None:
            print(f"  错误: 未找到「### 2.3 应用清单」章节", file=sys.stderr)
            return 1
        target.write_text(new_content, encoding="utf-8")

    print(f"  已更新: {target}")
    print(f"\n完成: 已更新 {len(entries)} 个应用条目")
    return 0


# ============================================================
# all 子命令：依次执行全部
# ============================================================

def cmd_all(args) -> int:
    print("=" * 60)
    print("docgen.py all - 执行全部文档生成任务")
    print("=" * 60)

    rc = cmd_nav(args)
    if rc != 0:
        print(f"\n[nav 失败 (exit={rc})，中止后续任务]", file=sys.stderr)
        return rc

    print()
    rc = cmd_dashboard(args)
    if rc != 0:
        print(f"\n[dashboard 失败 (exit={rc})，中止后续任务]", file=sys.stderr)
        return rc

    print()
    rc = cmd_apps(args)
    if rc != 0:
        return rc

    print("\n" + "=" * 60)
    print("全部文档生成任务完成")
    print("=" * 60)
    return 0


# ============================================================
# CLI 入口
# ============================================================

def add_common_args(sp):
    sp.add_argument('--path', type=Path, default=None, help='项目根目录路径（默认自动解析）')


def main():
    parser = argparse.ArgumentParser(description='文档索引与看板生成统一工具')
    subparsers = parser.add_subparsers(dest='command', help='可用子命令')

    p_nav = subparsers.add_parser('nav', help='生成文档导航表（README.md / docs/README.md）')
    add_common_args(p_nav)

    p_dash = subparsers.add_parser('dashboard', help='生成 Spec 执行进度看板（根 README.md）')
    add_common_args(p_dash)

    p_apps = subparsers.add_parser('apps', help='生成 apps/README.md 应用清单索引表')
    add_common_args(p_apps)

    p_all = subparsers.add_parser('all', help='依次执行 nav + dashboard + apps')
    add_common_args(p_all)

    args = parser.parse_args()

    cmd_map = {
        'nav': cmd_nav,
        'dashboard': cmd_dashboard,
        'apps': cmd_apps,
        'all': cmd_all,
    }

    if not args.command:
        parser.print_help()
        return 1

    return cmd_map[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
