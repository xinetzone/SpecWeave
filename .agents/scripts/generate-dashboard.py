#!/usr/bin/env python3
"""自动生成并更新 README.md 中的 Spec 执行进度看板。

扫描 `.trae/specs/*/tasks.md` 聚合各 Spec 完成状态，
自动更新根 README.md 中 `<!-- SPEC_DASHBOARD_START -->` /
`<!-- SPEC_DASHBOARD_END -->` 标记之间的看板区域。

判定规则：
- 顶级 Task（无缩进的 `- [ ] Task N:` / `- [x] Task N:`）全部勾选视为该 Spec 完成
- SubTask（缩进的）不单独计数，由顶级 Task 完成状态决定
"""

import re
import sys
from pathlib import Path
from dataclasses import dataclass

from constants import EXCLUDED_DIRS
from lib.frontmatter import parse_toml_frontmatter, extract_frontmatter_field, extract_all_fields

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


def parse_yaml_frontmatter_simple(content: str) -> dict[str, str]:
    """简单解析 YAML frontmatter 的 key: value 字段。"""
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


def scan_spec(spec_dir: Path) -> SpecStatus:
    """扫描单个 Spec 目录，统计任务完成状态。

    判定优先级：
    1. 若 frontmatter 中 status 为 completed/done/finished，视为已完成
    2. 否则，若 tasks.md 中无任何未勾选的复选框，视为已完成
    """
    tasks_file = spec_dir / "tasks.md"
    if not tasks_file.exists():
        return SpecStatus(name=spec_dir.name, completed=False, total_tasks=0, done_tasks=0)

    content = tasks_file.read_text(encoding="utf-8")

    status_from_frontmatter = None

    toml_fm = parse_toml_frontmatter(tasks_file)
    if toml_fm:
        fields = extract_all_fields(toml_fm)
        status = fields.get("status", "").lower().strip()
        if status:
            status_from_frontmatter = status

    if status_from_frontmatter is None:
        yaml_fields = parse_yaml_frontmatter_simple(content)
        status = yaml_fields.get("status", "").lower().strip()
        if status:
            status_from_frontmatter = status

    in_code_block = False
    filtered_lines = []
    for line in content.split("\n"):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            continue
        if not in_code_block:
            filtered_lines.append(line)
    filtered_content = "\n".join(filtered_lines)

    unchecked_list = len(UNCHECKED_LIST_RE.findall(filtered_content))
    checked_list = len(CHECKED_LIST_RE.findall(filtered_content))
    unchecked_heading = len(UNCHECKED_HEADING_RE.findall(filtered_content))
    checked_heading = len(CHECKED_HEADING_RE.findall(filtered_content))
    unchecked = unchecked_list + unchecked_heading
    checked = checked_list + checked_heading
    total_tasks = unchecked + checked

    if status_from_frontmatter in COMPLETED_STATUSES:
        completed = True
        done_tasks = total_tasks
    else:
        completed = unchecked == 0 and total_tasks > 0
        done_tasks = checked

    return SpecStatus(
        name=spec_dir.name,
        completed=completed,
        total_tasks=total_tasks,
        done_tasks=done_tasks,
    )


def scan_themes(specs_root: Path) -> list[ThemeStatus]:
    """扫描所有主题目录，聚合 Spec 状态。"""
    themes = []

    theme_dirs = sorted(
        [d for d in specs_root.iterdir() if d.is_dir() and d.name not in EXCLUDED_DIRS]
    )

    ordered_themes = []
    for theme_name in THEME_ORDER:
        theme_path = specs_root / theme_name
        if theme_path.exists() and theme_path.is_dir():
            ordered_themes.append(theme_path)
    for theme_dir in theme_dirs:
        if theme_dir not in ordered_themes:
            ordered_themes.append(theme_dir)

    for theme_dir in ordered_themes:
        spec_dirs = sorted(
            [
                d
                for d in theme_dir.iterdir()
                if d.is_dir() and d.name not in EXCLUDED_DIRS and (d / "tasks.md").exists()
            ]
        )
        specs = [scan_spec(d) for d in spec_dirs]
        themes.append(ThemeStatus(name=theme_dir.name, specs=specs))

    return themes


def generate_root_dashboard(themes: list[ThemeStatus]) -> str:
    """生成根 README.md 的 SPEC_DASHBOARD 表格。"""
    total_specs = sum(t.total for t in themes)
    total_completed = sum(t.completed_count for t in themes)
    total_in_progress = sum(t.in_progress_count for t in themes)
    total_pending = sum(t.pending_count for t in themes)
    overall_progress = int(total_completed / total_specs * 100) if total_specs > 0 else 0

    lines = []

    if total_completed == total_specs:
        lines.append(
            f"**整体进度：{total_completed}/{total_specs} 完成 · {overall_progress}% · 0 项进行中 · 0 项待启动** 🎉"
        )
    else:
        lines.append(
            f"**整体进度：{total_completed}/{total_specs} 完成 · {overall_progress}% · {total_in_progress} 项进行中 · {total_pending} 项待启动**"
        )

    lines.append("")
    lines.append("| 主题 | Spec 数 | 已完成 | 状态 | 看板 |")
    lines.append("|---|---|---|---|---|")

    for theme in themes:
        theme_link = f".trae/specs/{theme.name}/"
        readme_link = f".trae/specs/{theme.name}/README.md"
        if theme.progress == 100:
            status = f"✅ {theme.progress}%"
        elif theme.progress == 0:
            status = f"📋 {theme.progress}%"
        else:
            status = f"🔧 {theme.progress}%"
        lines.append(
            f"| [{theme.name}]({theme_link}) | {theme.total} | {theme.completed_count} | {status} | [查看]({readme_link}) |"
        )

    lines.append("")
    lines.append("> 详细进度、待办事项、里程碑路线图与跨主题依赖关系见 [全局执行看板](.trae/specs/README.md)。")

    return "\n".join(lines)


def update_file(file_path: Path, marker_start: str, marker_end: str, content: str) -> bool:
    """更新文件中标记区域的内容。"""
    if not file_path.exists():
        print(f"  警告: {file_path} 不存在，跳过")
        return False

    file_content = file_path.read_text(encoding="utf-8")

    start_idx = file_content.find(marker_start)
    end_idx = file_content.find(marker_end)

    if start_idx == -1 or end_idx == -1:
        print(f"  警告: {file_path} 中未找到标记 {marker_start} / {marker_end}，跳过")
        return False

    new_content = (
        file_content[: start_idx + len(marker_start)]
        + "\n\n"
        + content
        + "\n\n"
        + file_content[end_idx:]
    )
    file_path.write_text(new_content, encoding="utf-8")
    return True


def main() -> int:
    root = Path(__file__).parent.parent.parent
    specs_root = root / ".trae" / "specs"

    if not specs_root.exists():
        print(f"错误: Specs 目录不存在: {specs_root}", file=sys.stderr)
        return 1

    print("扫描 Spec 目录...")
    themes = scan_themes(specs_root)

    total_specs = sum(t.total for t in themes)
    total_completed = sum(t.completed_count for t in themes)
    print(f"  找到 {len(themes)} 个主题，{total_specs} 个 Spec")
    for theme in themes:
        print(f"    - {theme.name}: {theme.completed_count}/{theme.total} 完成")

    print("\n生成根 README.md 看板...")
    root_readme = root / "README.md"
    root_dashboard = generate_root_dashboard(themes)
    if update_file(
        root_readme,
        "<!-- SPEC_DASHBOARD_START -->",
        "<!-- SPEC_DASHBOARD_END -->",
        root_dashboard,
    ):
        print(f"  已更新: {root_readme}")
        print(f"\n完成: 看板数据已从 {total_completed}/{total_specs} Spec 聚合生成")
    else:
        print("  未更新任何文件", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
