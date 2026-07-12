#!/usr/bin/env python3
"""文档索引与看板生成统一工具。

聚合以下文档生成功能：
  nav        - 自动生成 README.md / docs/README.md 文档导航表
  dashboard  - 自动生成 .trae/specs/ 执行进度看板
  apps       - 自动生成 apps/README.md 应用清单索引表
  stats      - 自动统计并更新 README.md / AGENTS.md / .agents/README.md 核心数据指标
  all        - 依次执行 nav + dashboard + apps + stats

用法：
  python docgen.py nav
  python docgen.py dashboard
  python docgen.py apps
  python docgen.py stats
  python docgen.py all
"""

import argparse
import re
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from constants import SCAN_DIRS, ROOT_FILES, TARGETS, MANUAL_DESCRIPTIONS, EXCLUDED_DIRS
from lib.atomic_write import atomic_write_text
from lib.frontmatter import parse_frontmatter_unified
from lib.markdown import (
    extract_description as _extract_description,
    extract_title as _extract_title,
    update_marker_region,
)
from lib.project import resolve_project_root
from lib.cli import setup_safe_output


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

    fields = parse_frontmatter_unified(tasks_file)
    if fields:
        s = str(fields.get("status", "")).lower().strip()
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
        atomic_write_text(target, new_content, encoding="utf-8")

    print(f"  已更新: {target}")
    print(f"\n完成: 已更新 {len(entries)} 个应用条目")
    return 0


# ============================================================
# stats 子命令：核心数据指标自动统计更新
# ============================================================

GITCODE_REPO_OWNER = "daoCollective"
GITCODE_REPO_NAME = "SpecWeave"
GITCODE_BASE_URL = f"https://gitcode.com/{GITCODE_REPO_OWNER}/{GITCODE_REPO_NAME}"


@dataclass
class GitCodeStats:
    stars: int
    forks: int
    issues: int
    prs: int
    fetched: bool


@dataclass
class ProjectStats:
    commit_count: int
    pattern_count: int
    script_count: int
    skill_count: int
    rule_count: int
    command_count: int
    role_count: int
    core_entry_count: int
    last_updated: str
    gitcode: GitCodeStats


def _stats_fetch_url(url: str, timeout: int = 10) -> str:
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
        return ""


def _stats_extract_int(pattern: str, text: str, default: int = 0) -> int:
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        num_str = match.group(1).replace(",", "").replace(" ", "").strip()
        try:
            return int(num_str)
        except ValueError:
            pass
    return default


def _stats_fetch_gitcode_stats() -> GitCodeStats:
    stars = 0
    forks = 0
    issues = 0
    prs = 0
    fetched = False

    main_html = _stats_fetch_url(GITCODE_BASE_URL)
    if main_html:
        fetched = True
        stars = _stats_extract_int(r"Star\s*(\d+)", main_html)
        forks = _stats_extract_int(r"Fork\s*\[?\s*(\d+)", main_html)
        if stars == 0:
            stars = _stats_extract_int(r"stars?\D+(\d+)", main_html)
        if forks == 0:
            forks = _stats_extract_int(r"forks?\D+(\d+)", main_html)

    issues_html = _stats_fetch_url(f"{GITCODE_BASE_URL}/issues")
    if issues_html:
        fetched = True
        open_issues = _stats_extract_int(r"Open\s*(\d+)", issues_html)
        if open_issues == 0:
            open_issues = _stats_extract_int(r"已开启\s*(\d+)", issues_html)
        issues = open_issues

    prs_html = _stats_fetch_url(f"{GITCODE_BASE_URL}/pulls")
    if prs_html:
        fetched = True
        open_prs = _stats_extract_int(r"Open\s*(\d+)", prs_html)
        if open_prs == 0:
            open_prs = _stats_extract_int(r"已开启\s*(\d+)", prs_html)
        if open_prs == 0:
            open_prs = _stats_extract_int(r"全部\s*(\d+)", prs_html)
        prs = open_prs

    return GitCodeStats(
        stars=stars,
        forks=forks,
        issues=issues,
        prs=prs,
        fetched=fetched,
    )


def _stats_run_git(root: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git"] + list(args),
            cwd=root,
            capture_output=True,
            text=True,
            timeout=30,
            encoding="utf-8",
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ""


def _stats_count_commits(root: Path) -> int:
    output = _stats_run_git(root, "rev-list", "--count", "HEAD")
    try:
        return int(output) if output else 0
    except ValueError:
        return 0


def _stats_count_md_files(path: Path, exclude_readme: bool = True, exclude_dirs: set[str] | None = None) -> int:
    if not path.exists():
        return 0
    excl = exclude_dirs or set()
    count = 0
    for md in path.rglob("*.md"):
        parts = set(md.parts)
        if EXCLUDED_DIRS & parts:
            continue
        rel = md.relative_to(path).as_posix()
        if any(rel.startswith(d) for d in excl):
            continue
        if exclude_readme and md.name == "README.md":
            continue
        if any(part.startswith(".") for part in md.relative_to(path).parts[:-1]):
            continue
        count += 1
    return count


def _stats_count_py_scripts(path: Path) -> int:
    if not path.exists():
        return 0
    count = 0
    for py in path.rglob("*.py"):
        parts = set(py.parts)
        if "__pycache__" in parts:
            continue
        if py.name.startswith("test_") or py.name == "__init__.py":
            continue
        rel_parts = py.relative_to(path).parts
        if rel_parts[0] == "tests":
            continue
        count += 1
    return count


def _stats_count_skill_dirs(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for d in path.iterdir() if d.is_dir() and (d / "SKILL.md").exists())


def _stats_count_command_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for f in path.glob("*.md") if f.name != "README.md")


def _stats_count_role_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for f in path.glob("*.md") if f.name != "README.md" and f.name != "collaboration-scenarios.md")


def _stats_collect(root: Path) -> ProjectStats:
    agents = root / ".agents"
    patterns_root = root / "docs" / "retrospective" / "patterns"

    commit_count = _stats_count_commits(root)
    pattern_count = _stats_count_md_files(patterns_root, exclude_readme=True)
    script_count = _stats_count_py_scripts(agents / "scripts")
    skill_count = _stats_count_skill_dirs(agents / "skills")
    rule_count = _stats_count_md_files(agents / "rules", exclude_readme=True)
    command_count = _stats_count_command_files(agents / "commands")
    role_count = _stats_count_role_files(agents / "roles")
    core_entry_count = 22
    gitcode_stats = _stats_fetch_gitcode_stats()

    return ProjectStats(
        commit_count=commit_count,
        pattern_count=pattern_count,
        script_count=script_count,
        skill_count=skill_count,
        rule_count=rule_count,
        command_count=command_count,
        role_count=role_count,
        core_entry_count=core_entry_count,
        last_updated=date.today().isoformat(),
        gitcode=gitcode_stats,
    )


def _stats_generate_readme_snippet(stats: ProjectStats) -> str:
    return (
        f"本体系经过 **{stats.commit_count}+ 次真实提交** 持续迭代验证，"
        f"包含 {stats.role_count} 个明确定义的智能体角色、"
        f"**{stats.pattern_count}+ 个可复用模式**（方法论/架构/代码/分析卡片）和 "
        f"**{stats.script_count}+ 自动化脚本**，"
        f"通过 AGENTS.md 单一入口路由、渐进式披露（L0/L1/L2）、Core/Tools 双层治理与运行时阶段守卫，"
        f"让多智能体协作具备一致的上下文、可执行的质量门禁与可审计的交付基线。"
        f"只需将本仓库作为 AI 编码工具的工作目录，即可开箱即用。详见 [项目概述](docs/project-overview.md)。"
    )


def _stats_generate_agents_changelog_entry(stats: ProjectStats) -> str:
    base = (
        f"- {stats.last_updated} | docs | 核心数据自动更新：提交数{stats.commit_count}+、"
        f"模式{stats.pattern_count}+、脚本{stats.script_count}+、"
        f"Skill{stats.skill_count}个、规则{stats.rule_count}+、"
        f"指令集{stats.command_count}个、核心规范入口{stats.core_entry_count}项"
    )
    if stats.gitcode.fetched:
        base += (
            f"、GitCode Stars{stats.gitcode.stars}、Forks{stats.gitcode.forks}、"
            f"Issues{stats.gitcode.issues}、PRs{stats.gitcode.prs}"
        )
    base += "。来源：docgen.py stats 自动统计"
    return base


def _stats_generate_dotagents_snippet(stats: ProjectStats) -> str:
    return (
        f"- `AGENTS.md` 是精简入口文件（约100行），定义启动协议（4步骤+自检清单，含内容敏感度预检步骤2.3）、"
        f"{stats.core_entry_count}项核心规范入口导航表、开发规范概要与知识库索引，是智能体启动时首先读取的最高优先级契约。\n"
        f"- `.agents/global-core-rules.md` 承载全局核心规则（启动协议优先、内容敏感度分流、沟通语言、按需读取、"
        f"上下文节省、Mermaid优先、代码修改、歧义澄清、Spec目录规范、禁止临时依赖、三阶段递进、元文档优先、"
        f"修复即闭环、查阅知识库、简单任务验证等，持续演进），从 AGENTS.md 拆分后持续演进。\n"
        f"- `.agents/context-routing.md` 承载从 AGENTS.md 拆分出的完整上下文路由表（vendor方法论资产预检+常规任务路由，90+路由项）。\n"
        f"- `.agents/` 是详细规范容器，承载各角色、提示词、工具规范、协议、工作流、模板与脚本的具体内容"
        f"（{stats.script_count}+脚本、{stats.rule_count}+规则文件、{stats.pattern_count}+可复用模式）。\n"
        f"- 两者关系为\"入口 ↔ 容器\"：`AGENTS.md` 负责路由与全局约束，`.agents/` 负责具体规范与可执行细节。"
        f"智能体应先读 `AGENTS.md`，再按需进入 `.agents/` 加载相关规范。\n"
        f"- 信息架构遵循 L0/L1/L2 渐进式披露：AGENTS.md+ONBOARDING.md(L0) → "
        f"capability-registry.md+context-routing.md+skills/(L1) → 详细规范文档(L2)。"
    )


def _stats_update_badges(content: str, stats: ProjectStats) -> tuple[str, list[str]]:
    updates = []
    gc = stats.gitcode

    badge_replacements = [
        (r"(\[!\[Issues\]\(https://img\.shields\.io/badge/issues-)[^-]+(-[a-z]+\.svg\))",
         lambda m: f"{m.group(1)}{gc.issues}{m.group(2)}" if gc.fetched else m.group(0),
         f"Issues={gc.issues}"),
        (r"(\[!\[Pull Requests\]\(https://img\.shields\.io/badge/PRs-)[^-]+(-[a-z]+\.svg\))",
         lambda m: f"{m.group(1)}{gc.prs}{m.group(2)}" if gc.fetched else m.group(0),
         f"PRs={gc.prs}"),
        (r"(\[!\[Stars\]\(https://img\.shields\.io/badge/stars-)[^-]+(-[a-z]+\.svg\))",
         lambda m: f"{m.group(1)}{gc.stars}{m.group(2)}" if gc.fetched else m.group(0),
         f"Stars={gc.stars}"),
        (r"(\[!\[Forks\]\(https://img\.shields\.io/badge/forks-)[^-]+(-[a-z]+\.svg\))",
         lambda m: f"{m.group(1)}{gc.forks}{m.group(2)}" if gc.fetched else m.group(0),
         f"Forks={gc.forks}"),
    ]

    new_content = content
    for pattern, replacer, desc in badge_replacements:
        new_content, count = re.subn(pattern, replacer, new_content, count=1)
        if count > 0 and gc.fetched:
            updates.append(desc)

    return new_content, updates


def _stats_update_readme(root: Path, stats: ProjectStats) -> bool:
    readme = root / "README.md"
    if not readme.exists():
        print(f"  跳过: {readme} 不存在")
        return False

    content = readme.read_text(encoding="utf-8")
    snippet = _stats_generate_readme_snippet(stats)

    pattern = re.compile(
        r"本体系经过 \*\*\d+\+ 次真实提交\*\* 持续迭代验证，.*?详见 \[项目概述\]\(docs/project-overview\.md\)。",
        re.DOTALL,
    )
    new_content, count = pattern.subn(snippet, content, count=1)
    if count == 0:
        print("  警告: README.md 中未找到核心数据描述段落，跳过")
        return False

    new_content, badge_updates = _stats_update_badges(new_content, stats)

    changed = new_content != content
    if changed:
        atomic_write_text(readme, new_content, encoding="utf-8")
        local_msg = f"提交{stats.commit_count}+, 模式{stats.pattern_count}+, 脚本{stats.script_count}+"
        badge_msg = ", ".join(badge_updates) if badge_updates else ""
        msg = f"  已更新: {readme} ({local_msg}"
        if badge_msg:
            msg += f", {badge_msg}"
        msg += ")"
        print(msg)
        return True
    else:
        print(f"  无需更新: {readme} 数据已是最新")
        return True


def _stats_update_agents_changelog(root: Path, stats: ProjectStats) -> bool:
    agents = root / "AGENTS.md"
    if not agents.exists():
        print(f"  跳过: {agents} 不存在")
        return False

    content = agents.read_text(encoding="utf-8")
    changelog_marker = "<!-- changelog -->"
    idx = content.find(changelog_marker)
    if idx == -1:
        print("  警告: AGENTS.md 中未找到 <!-- changelog --> 标记")
        return False

    entry = _stats_generate_agents_changelog_entry(stats)
    today_prefix = f"- {stats.last_updated} | docs | 核心数据自动更新"

    after_marker = content[idx + len(changelog_marker):]
    if today_prefix in after_marker.split("\n")[1] if "\n" in after_marker else False:
        lines = after_marker.split("\n")
        for i, line in enumerate(lines):
            if line.startswith(today_prefix):
                lines[i] = entry
                break
        new_content = content[:idx + len(changelog_marker)] + "\n".join(lines)
        atomic_write_text(agents, new_content, encoding="utf-8")
        print(f"  已更新今日条目: {agents}")
        return True

    insert_pos = idx + len(changelog_marker)
    new_content = content[:insert_pos] + "\n" + entry + content[insert_pos:]
    atomic_write_text(agents, new_content, encoding="utf-8")
    print(f"  已新增条目: {agents}")
    return True


def cmd_stats(args) -> int:
    root = args.path or resolve_project_root(__file__)
    if not root.exists():
        print(f"错误: 项目根目录不存在: {root}", file=sys.stderr)
        return 1

    print("收集项目统计数据...")
    stats = _stats_collect(root)
    print(f"  Git 提交数:     {stats.commit_count}+")
    print(f"  可复用模式:     {stats.pattern_count}+")
    print(f"  Python 脚本:    {stats.script_count}+")
    print(f"  Skill 数量:     {stats.skill_count}")
    print(f"  规则文件:       {stats.rule_count}+")
    print(f"  指令集:         {stats.command_count}")
    print(f"  角色定义:       {stats.role_count}")
    print(f"  核心规范入口:   {stats.core_entry_count}")
    print(f"  更新日期:       {stats.last_updated}")

    if stats.gitcode.fetched:
        print(f"\nGitCode 仓库统计:")
        print(f"  Stars:          {stats.gitcode.stars}")
        print(f"  Forks:          {stats.gitcode.forks}")
        print(f"  Open Issues:    {stats.gitcode.issues}")
        print(f"  Open PRs:       {stats.gitcode.prs}")
    else:
        print(f"\n  警告: 无法获取 GitCode 远程数据（网络问题或超时），徽章将保持不变")

    print("\n更新核心文档...")
    results = []
    results.append(("README.md", _stats_update_readme(root, stats)))
    results.append(("AGENTS.md", _stats_update_agents_changelog(root, stats)))

    updated = sum(1 for _, ok in results if ok)
    print(f"\n完成: 已更新 {updated} 个文件")
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
        print(f"\n[apps 失败 (exit={rc})，中止后续任务]", file=sys.stderr)
        return rc

    print()
    rc = cmd_stats(args)
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
    setup_safe_output()
    parser = argparse.ArgumentParser(description='文档索引与看板生成统一工具')
    subparsers = parser.add_subparsers(dest='command', help='可用子命令')

    p_nav = subparsers.add_parser('nav', help='生成文档导航表（README.md / docs/README.md）')
    add_common_args(p_nav)

    p_dash = subparsers.add_parser('dashboard', help='生成 Spec 执行进度看板（根 README.md）')
    add_common_args(p_dash)

    p_apps = subparsers.add_parser('apps', help='生成 apps/README.md 应用清单索引表')
    add_common_args(p_apps)

    p_stats = subparsers.add_parser('stats', help='统计并更新 README.md/AGENTS.md 核心数据指标')
    add_common_args(p_stats)

    p_all = subparsers.add_parser('all', help='依次执行 nav + dashboard + apps + stats')
    add_common_args(p_all)

    args = parser.parse_args()

    cmd_map = {
        'nav': cmd_nav,
        'dashboard': cmd_dashboard,
        'apps': cmd_apps,
        'stats': cmd_stats,
        'all': cmd_all,
    }

    if not args.command:
        parser.print_help()
        return 1

    return cmd_map[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
