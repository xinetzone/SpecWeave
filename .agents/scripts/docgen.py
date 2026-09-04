#!/usr/bin/env python3
"""文档索引与看板生成统一工具。

聚合以下文档生成功能：
  nav                    - 自动生成 README.md / docs/README.md / docs/index.md 文档导航表
  dashboard              - 自动生成 .trae/specs/ 执行进度看板（根 README.md）
  theme-dashboards       - 为所有主题生成/刷新主题级看板（.trae/specs/<theme>/README.md）
  update-spec-readme     - 将 .trae/specs/README.md 压缩为轻索引（全局总览表 + 主题行数摘要）
  apps                   - 自动生成 apps/README.md 应用清单索引表
  stats                  - 自动统计并更新 README.md / AGENTS.md / .agents/README.md 核心数据指标
  all                    - 依次执行 nav + dashboard + theme-dashboards + update-spec-readme + apps + stats

用法：
  python docgen.py nav
  python docgen.py dashboard
  python docgen.py theme-dashboards
  python docgen.py update-spec-readme
  python docgen.py apps
  python docgen.py stats
  python docgen.py all
"""


# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import argparse
import json
import re
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from constants import ROOT_FILES, TARGETS, MANUAL_DESCRIPTIONS, EXCLUDED_DIRS


class StatsSourceError(Exception):
    pass
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
# 全部 13 个主题，保持既有 7 主题 + 新扩 6 主题的顺序
THEME_ORDER = [
    "core-foundation",
    "roles-governance",
    "standards-tools",
    "readme-branding",
    "docs-restructure",
    "retrospectives-insights",
    "migration-archival",
    "okf-wiki-ecosystem",
    "classics-knowledge",
    "caffe-framework",
    "xmnn-packaging",
    "workspace-governance",
    "infra-env",
]

# 各主题的描述文本（用于主题 README 和全局总览表）
THEME_DESCRIPTIONS: dict[str, str] = {
    "core-foundation": "核心体系基础：项目核心基础设施、系统架构、核心功能模块的创建与配置类 spec",
    "roles-governance": "角色与治理体系：智能体角色定义扩展、权限标记、治理规则体系、索引同步相关 spec",
    "standards-tools": "规范标准与工具链：文档编写标准、命名规范、自动化检查/验证工具、IDE 适配优化相关 spec",
    "readme-branding": "README 与品牌定位：对外展示窗口演进、品牌定位词选型、蓝图与场景展示相关 spec",
    "docs-restructure": "文档体系重组：已有文档原子化拆分、主题分类、目录重构、重复消除、命名统一等结构性整理 spec",
    "retrospectives-insights": "复盘与洞察萃取：已完成任务/项目系统性复盘、问题诊断、经验萃取、方法论分析的 spec",
    "migration-archival": "迁移与归档：外部内容引入、沙箱治理、历史项目迁移、归档体系建立相关 spec",
    "okf-wiki-ecosystem": "OKF/Wiki 知识生态：外部源码、官方文档、博客文章的知识化转译（OKF 知识包/Wiki 教程）spec",
    "classics-knowledge": "典籍与人文知识：中西方典籍、道家/中医/数理经典的知识化工程 spec",
    "caffe-framework": "Caffe/CaffEx 框架：Caffe FFI、pycaffe、算子实现、Docker 镜像与性能优化 spec",
    "xmnn-packaging": "XMNN 打包与量化：wheel 构建、Nuitka 打包、运行时镜像、模型精度验证 spec",
    "workspace-governance": "工作区治理：目录重组、规范整合、子项目管理、工作区模板萃取 spec",
    "infra-env": "基础设施与环境：Docker/devcontainer/conda/Jupyter 环境搭建与运维 spec",
}

# 状态图标映射
_STATUS_ICONS = {
    "done": "✓", "completed": "✓", "完成": "✓",
    "in-progress": "!", "in_progress": "!", "ongoing": "!", "进行中": "!",
    "planned": "?", "pending": "?", "todo": "?", "待启动": "?", "规划": "?",
}


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


def _nav_scan_docs(root: Path, scan_dir: str, root_files: list[str] | None = None) -> list[tuple[str, str, str, bool]]:
    entries = []
    scan_path = root / scan_dir
    if scan_path.exists():
        for md_file in sorted(scan_path.glob("*.md")):
            # 跳过 hub 页自身：README.md（旧惯例）与 index.md（OKF v0.2 文档中心惯例），
            # 避免导航表出现自链接（迁移后 docs/ 入口为 docs/index.md）
            if md_file.name in ("README.md", "index.md"):
                continue
            title = _nav_extract_title(md_file)
            desc = _nav_extract_description(md_file)
            entries.append((title, md_file.name, desc, False))
    effective_root_files = ROOT_FILES if root_files is None else root_files
    for rf in effective_root_files:
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

    print("\n更新目标文件...")
    updated = 0
    scanned_cache: dict[tuple[str, tuple[str, ...]], list[tuple[str, str, str, bool]]] = {}
    for target_file, config in TARGETS.items():
        target_path = root / target_file
        if not target_path.exists():
            print(f"  跳过: {target_file} 不存在")
            continue
        scan_dir = config.get("scan_dir", "docs/")
        root_files = list(config.get("root_files", ROOT_FILES))
        cache_key = (scan_dir, tuple(root_files))
        if cache_key not in scanned_cache:
            print(f"扫描文档目录: {scan_dir}")
            scanned_cache[cache_key] = _nav_scan_docs(root, scan_dir, root_files)
            print(f"  找到 {len(scanned_cache[cache_key])} 个文档")
        entries = scanned_cache[cache_key]
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


def _dash_get_spec_status(spec_md: Path) -> str:
    """从 spec.md 的 YAML frontmatter 中提取 status 字段的图标表示。"""
    if not spec_md.exists():
        return "—"
    try:
        text = spec_md.read_text(encoding="utf-8")
    except Exception:
        return "—"
    match = YAML_FRONTMATTER_RE.match(text)
    if not match:
        return "—"
    fm = match.group(1)
    sm = re.search(r"^status\s*:\s*[\"']?([^\"'\n]+)", fm, re.M)
    if not sm:
        return "—"
    val = sm.group(1).strip().lower()
    return _STATUS_ICONS.get(val, "—")


def _dash_scan_all_specs(specs_root: Path) -> list[ThemeStatus]:
    """扫描全部 13 主题，收集每个主题下所有子目录（不论是否有 tasks.md）。

    用于主题看板生成和全局 README 压缩。返回 ThemeStatus 列表，其中 specs 包含
    name / has_tasks / has_review / status_icon 字段（不依赖 tasks.md 存在）。
    """
    themes = []
    theme_dirs = sorted(
        [d for d in specs_root.iterdir() if d.is_dir() and d.name not in EXCLUDED_DIRS]
    )
    ordered = []
    for name in THEME_ORDER:
        p = specs_root / name
        if p.exists() and p.is_dir():
            ordered.append(p)
    for td in theme_dirs:
        if td not in ordered:
            ordered.append(td)

    for theme_dir in ordered:
        sub_dirs = sorted([
            d for d in theme_dir.iterdir()
            if d.is_dir() and d.name not in EXCLUDED_DIRS
        ])
        specs = []
        for d in sub_dirs:
            spec_md = d / "spec.md"
            fm = parse_frontmatter_unified(spec_md) if spec_md.exists() else None
            status_val = str(fm.get("status", "")).lower().strip() if fm else ""
            if status_val in COMPLETED_STATUSES:
                completed = True
                total_tasks = 0
                done_tasks = 0
            elif (d / "tasks.md").exists():
                tasks_content = (d / "tasks.md").read_text(encoding="utf-8")
                in_code = False
                flt = []
                for line in tasks_content.split("\n"):
                    if line.strip().startswith("```"):
                        in_code = not in_code
                        continue
                    if not in_code:
                        flt.append(line)
                filtered = "\n".join(flt)
                unchecked = len(UNCHECKED_LIST_RE.findall(filtered)) + len(UNCHECKED_HEADING_RE.findall(filtered))
                checked = len(CHECKED_LIST_RE.findall(filtered)) + len(CHECKED_HEADING_RE.findall(filtered))
                total_tasks = unchecked + checked
                done_tasks = checked
                completed = unchecked == 0 and total_tasks > 0
            else:
                completed = False
                total_tasks = 0
                done_tasks = 0
            specs.append(SpecStatus(
                name=d.name,
                completed=completed,
                total_tasks=total_tasks,
                done_tasks=done_tasks,
            ))
        # 如果主题目录本身是 spec（无子目录但有 tasks.md）
        if not specs and (theme_dir / "tasks.md").exists():
            specs = [_dash_scan_spec(theme_dir)]
        themes.append(ThemeStatus(name=theme_dir.name, specs=specs))
    return themes


def _build_theme_dashboard_table(specs: list[SpecStatus]) -> str:
    """生成主题看板表格（4 列：# | Spec 名称 | 状态 | 三件套）。"""
    lines = ["| # | Spec 名称 | 状态 | 三件套 |"]
    lines.append("|---|---|---|---|")
    ck, cx = "✓", "✗"
    for j, s in enumerate(specs, 1):
        has_tasks = s.total_tasks > 0 or (s.done_tasks > 0)
        has_review = False  # 暂不检测，用 ? 占位
        if s.completed:
            status = "✓ 完成"
        elif s.done_tasks > 0:
            status = "! 进行中"
        else:
            status = "? 待启动"
        trio = f"{ck}{'/' if has_tasks else cx}{'/' if has_review else cx}"
        lines.append(f"| {j} | [{s.name}]({s.name}/spec.md) | {status} | {trio} |")
    return "\n".join(lines)


def cmd_theme_dashboards(args) -> int:
    """为所有主题生成/刷新主题级执行看板（.trae/specs/<theme>/README.md）。

    策略：
    - 精简型主题（已有 <!-- THEME_DASHBOARD_START/END --> marker）：marker 区域替换
    - 其他主题：在文档末尾追加 "## 📊 主题执行看板（docgen 自动生成）" 区域
    """
    root = args.path or resolve_project_root(__file__)
    specs_root = root / ".trae" / "specs"
    if not specs_root.exists():
        print(f"错误: Specs 目录不存在: {specs_root}", file=sys.stderr)
        return 1

    print("扫描所有主题 Spec...")
    themes = _dash_scan_all_specs(specs_root)
    total_specs = sum(t.total for t in themes)
    print(f"  共 {len(themes)} 个主题，{total_specs} 个 Spec")

    updated = 0
    skipped = 0
    for theme in themes:
        readme = specs_root / theme.name / "README.md"
        if not readme.exists():
            print(f"  跳过（无 README）: {theme.name}")
            skipped += 1
            continue

        table = _build_theme_dashboard_table(theme.specs)
        content = readme.read_text(encoding="utf-8")

        ms, me = "<!-- THEME_DASHBOARD_START -->", "<!-- THEME_DASHBOARD_END -->"
        try:
            update_marker_region(readme, ms, me, table)
            print(f"  更新（marker 替换）: {theme.name}（{theme.total} spec）")
            updated += 1
        except ValueError:
            # fallback：在文档末尾追加新区域
            append_content = (
                "\n\n"
                "<!-- THEME_DASHBOARD_START -->\n"
                "## 📊 主题执行看板（docgen 自动生成）\n\n"
                f"> 最后刷新：{date.today().isoformat()} ｜ Spec 总数：{theme.total}\n\n"
                + table + "\n\n"
                "<!-- THEME_DASHBOARD_END -->"
            )
            atomic_write_text(readme, content.rstrip() + append_content + "\n", encoding="utf-8")
            print(f"  更新（末尾追加）: {theme.name}（{theme.total} spec）")
            updated += 1

    print(f"\n完成：已更新 {updated} 个主题看板，跳过 {skipped} 个")
    return 0


def cmd_update_spec_readme(args) -> int:
    """将 .trae/specs/README.md 压缩为轻索引：
    保留全局状态总览表 + 每主题一行摘要，移除全量 spec 索引大表。
    目标：< 50KB（C-4 F 类文件瘦身）。
    """
    root = args.path or resolve_project_root(__file__)
    specs_root = root / ".trae" / "specs"
    target = specs_root / "README.md"
    if not target.exists():
        print(f"错误: {target} 不存在", file=sys.stderr)
        return 1

    print("扫描所有主题 Spec...")
    themes = _dash_scan_all_specs(specs_root)
    total_specs = sum(t.total for t in themes)

    # 读取原文，提取全局总览表
    content = target.read_text(encoding="utf-8")

    # 找到 "## 全局状态总览" 到下一个 "---" 或 "## spec 全量索引" 的区域
    overview_start = content.find("## \U0001f4da 全局状态总览")
    if overview_start == -1:
        overview_start = content.find("## 📊 全局状态总览")
    if overview_start == -1:
        # 找不到，从头开始重建
        overview_start = 0

    # 找第一个 "---" 后面的 "## spec 全量索引"
    after_overview = content[overview_start:]
    hr_idx = after_overview.find("\n---\n")
    if hr_idx == -1:
        hr_idx = after_overview.find("\n---\n")
    index_marker = after_overview.find("## \U0001f451; spec 全量索引")
    if index_marker == -1:
        index_marker = after_overview.find("## 📑 spec 全量索引")

    if index_marker == -1:
        # 没有全量索引，直接写入轻版本
        light_content = _build_light_spec_readme(themes, total_specs)
    else:
        # 保留 overview 部分（包括标题、描述、总览表和图例），截断后续内容
        overview_end = overview_start + index_marker + hr_idx
        prefix = content[:overview_end]
        light_content = prefix + "\n\n" + _build_light_spec_readme(themes, total_specs)

    atomic_write_text(target, light_content, encoding="utf-8")

    new_size = len(light_content.encode("utf-8"))
    print(f"完成：已压缩 .trae/specs/README.md（{new_size // 1024} KB，{total_specs} 个 Spec）")
    return 0


def _build_light_spec_readme(themes: list[ThemeStatus], total_specs: int) -> str:
    """生成轻索引版全局看板（仅总览表 + 主题摘要，不含全量 spec 列表）。"""
    today = date.today().isoformat()
    lines = [
        f"# Specs 全局执行看板",
        "",
        f"> 本目录是 SpecWeave 项目所有规格文档（spec）的指挥中心，按 13 大主题分类组织。"
        f"本文档由 docgen（C-6）于 **{today}** 自动生成；详细 spec 列表见各主题 README。",
        "",
        "---",
        "",
        "## \U0001f4ca 全局状态总览",
        "",
        "| 分区 | Spec 数 | 已完成 | 进行中 | 待启动 | 看板 |",
        "|---|---|---|---|---|---|",
    ]
    for theme in themes:
        c = theme.completed_count
        ip = theme.in_progress_count
        p = theme.pending_count
        tlink = f"./{theme.name}/README.md"
        icon = "✅" if theme.progress == 100 else ("🔧" if theme.progress > 0 else "📋")
        lines.append(f"| [{theme.name}]({tlink}) | {theme.total} | {c} | {ip} | {p} | {icon} [查看]({tlink}) |")
    lines += [
        f"| **合计** | **{total_specs}** | **{sum(t.completed_count for t in themes)}** | **{sum(t.in_progress_count for t in themes)}** | **{sum(t.pending_count for t in themes)}** | &mdash; |",
        "",
        "**状态**：✓ 已完成 ｜ ! 进行中 ｜ ? 待启动 ｜ — 无 metadata",
        "",
        "---",
        "",
        "## \U0001f4c1 主题索引",
        "",
        "> 各主题执行看板详见对应 README，按编号进入查看完整 spec 列表。",
        "",
    ]
    for i, theme in enumerate(themes, 1):
        desc = THEME_DESCRIPTIONS.get(theme.name, "")
        short = desc.split("：", 1)[1] if "：" in desc else desc
        lines.append(f"{i}. [{theme.name}](./{theme.name}/README.md) — {theme.total} spec：{short}")
    lines += [
        "",
        "## \U0001f4c6 新增 Spec 指南",
        "",
        "1. **选择主题**：判断归属 13 大主题之一；跨主题的优先归入最相关主题。",
        "2. **查重**：在对应主题目录下检索是否已有相近 spec，避免近名重复（见 C-5 查重脚本）。",
        "3. **命名**：kebab-case，语义化描述，参考现有命名（如 create-*-wiki-tutorial）。",
        "4. **创建三件套**：spec.md（YAML frontmatter 含 status/title）+ tasks.md + review.md（独立审查清单）。"
        "产物命名与结构以 .agents/skills/TRAE-spec-mode/SKILL.md 为唯一权威依据，禁止使用 checklist.md 等非规范命名。",
        "5. **更新看板**：运行 `python .agents/scripts/docgen.py theme-dashboards` 刷新主题看板，"
        "运行 `python .agents/scripts/docgen.py update-spec-readme` 刷新全局总览。",
        "",
        f"*本看板由 docgen（C-6）于 {today} 生成，后续自动维护。*",
    ]
    return "\n".join(lines) + "\n"


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
        if not spec_dirs and (theme_dir / "tasks.md").exists():
            spec_dirs = [theme_dir]
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
        return 0

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


def _apps_scan(apps_dir: Path) -> list[tuple[str, str, str, bool]]:
    entries = []
    for item in sorted(apps_dir.iterdir()):
        if not item.is_dir():
            continue
        if item.name.startswith(".") or item.name == "shared":
            continue
        readme = item / "README.md"
        has_readme = readme.exists()
        entries.append((item.name, _apps_extract_title(readme, item.name), _apps_extract_desc(readme, item.name), has_readme))
    return entries


def _apps_generate_table(entries) -> str:
    lines = ["| 应用 | 说明 | 入口 |", "|---|---|---|"]
    for dir_name, _title, desc, has_readme in entries:
        if has_readme:
            entry = f"[README.md]({dir_name}/README.md)"
        else:
            entry = f"`{dir_name}/`（暂无 README）"
        lines.append(f"| `{dir_name}/` | {desc} | {entry} |")
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
    for d, title, _desc, _has_readme in entries:
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
    # 模式库已随 .agents/docs/ 统一迁移至 docs/ 文档中心（OKF v0.2）
    patterns_root = root / "docs" / "retrospective" / "patterns"

    critical_paths = [
        (agents / "scripts", "自动化脚本目录"),
        (agents / "skills", "Skill 目录"),
        (agents / "rules", "规则目录"),
        (agents / "commands", "指令集目录"),
        (agents / "roles", "角色目录"),
        (patterns_root, "模式库目录"),
    ]
    for path, desc in critical_paths:
        if not path.exists():
            raise StatsSourceError(f"统计源路径不存在: {path} ({desc})")

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


STATS_ANOMALY_FIELDS = ("commit_count", "pattern_count", "script_count", "rule_count", "command_count")
STATS_ANOMALY_THRESHOLD = 0.5


def _stats_load_snapshot(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _stats_save_snapshot(stats: ProjectStats, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    snapshot = {
        "commit_count": stats.commit_count,
        "pattern_count": stats.pattern_count,
        "script_count": stats.script_count,
        "skill_count": stats.skill_count,
        "rule_count": stats.rule_count,
        "command_count": stats.command_count,
        "role_count": stats.role_count,
        "core_entry_count": stats.core_entry_count,
        "last_updated": stats.last_updated,
    }
    path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")


def _stats_validate_with_snapshot(stats: ProjectStats, snapshot_path: Path) -> list:
    prev = _stats_load_snapshot(snapshot_path)
    if prev is None:
        return []
    warnings = []
    for field in STATS_ANOMALY_FIELDS:
        old_val = prev.get(field)
        new_val = getattr(stats, field)
        if old_val is None or old_val == 0:
            continue
        if new_val < old_val * STATS_ANOMALY_THRESHOLD:
            warnings.append(
                f"  ⚠️  {field} 从 {old_val} 降至 {new_val}（降幅 {old_val - new_val}，可能异常，请人工确认）"
            )
    if warnings:
        print("\n[STATS-WARN] 环比异常检测发现以下指标降幅 >50%:", file=sys.stderr)
        for w in warnings:
            print(w, file=sys.stderr)
        print("（如有误报可忽略；如路径迁移/重构导致，请确认计数源路径正确）\n", file=sys.stderr)
    return warnings


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


def _stats_generate_changelog_entry(stats: ProjectStats) -> str:
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
         f"Issues={gc.issues}", gc.fetched),
        (r"(\[!\[Pull Requests\]\(https://img\.shields\.io/badge/PRs-)[^-]+(-[a-z]+\.svg\))",
         lambda m: f"{m.group(1)}{gc.prs}{m.group(2)}" if gc.fetched else m.group(0),
         f"PRs={gc.prs}", gc.fetched),
        (r"(\[!\[Stars\]\(https://img\.shields\.io/badge/stars-)[^-]+(-[a-z]+\.svg\))",
         lambda m: f"{m.group(1)}{gc.stars}{m.group(2)}" if gc.fetched else m.group(0),
         f"Stars={gc.stars}", gc.fetched),
        (r"(\[!\[Forks\]\(https://img\.shields\.io/badge/forks-)[^-]+(-[a-z]+\.svg\))",
         lambda m: f"{m.group(1)}{gc.forks}{m.group(2)}" if gc.fetched else m.group(0),
         f"Forks={gc.forks}", gc.fetched),
        (r"(\[scripts-badge\]: https://img\.shields\.io/badge/脚本-)[^-]+(-blue\?style=flat)",
         lambda m: f"{m.group(1)}{stats.script_count}%2B{m.group(2)}",
         f"脚本={stats.script_count}+", True),
        (r"(\[skills-badge\]: https://img\.shields\.io/badge/Skills-)[^-]+(-success\?style=flat)",
         lambda m: f"{m.group(1)}{stats.skill_count}{m.group(2)}",
         f"Skills={stats.skill_count}", True),
        (r"(\[rules-badge\]: https://img\.shields\.io/badge/规则-)[^-]+(-orange\?style=flat)",
         lambda m: f"{m.group(1)}{stats.rule_count}%2B{m.group(2)}",
         f"规则={stats.rule_count}+", True),
        (r"(\[commands-badge\]: https://img\.shields\.io/badge/指令集-)[^-]+(-purple\?style=flat)",
         lambda m: f"{m.group(1)}{stats.command_count}{m.group(2)}",
         f"指令集={stats.command_count}", True),
    ]

    new_content = content
    for pattern, replacer, desc, should_log in badge_replacements:
        new_content, count = re.subn(pattern, replacer, new_content, count=1)
        if count > 0 and should_log:
            updates.append(desc)

    return new_content, updates


def _stats_update_readme(root: Path, stats: ProjectStats) -> bool:
    readme = root / "README.md"
    if not readme.exists():
        print(f"  跳过: {readme} 不存在")
        return False

    content = readme.read_text(encoding="utf-8")
    snippet = _stats_generate_readme_snippet(stats)

    new_content = content
    snippet_updated = False

    for pattern_str in [
        r"本体系经过 \*\*\d+\+ 次真实提交\*\* 持续迭代验证，.*?详见 \[项目概述\]\(docs/tech/references/project-overview\.md\)。",
        r"本体系经过 \*\*\d+\+ 次真实提交\*\* 持续迭代验证，.*?详见 \[项目概述\]\(docs/project-overview\.md\)。",
    ]:
        pattern = re.compile(pattern_str, re.DOTALL)
        new_content, count = pattern.subn(snippet, new_content, count=1)
        if count > 0:
            snippet_updated = True
            break

    if not snippet_updated:
        print("  提示: README.md 中未找到核心数据描述段落（仅更新徽章）")

    new_content, badge_updates = _stats_update_badges(new_content, stats)

    changed = new_content != content
    if changed:
        atomic_write_text(readme, new_content, encoding="utf-8")
        parts = []
        if snippet_updated:
            parts.append(f"提交{stats.commit_count}+, 模式{stats.pattern_count}+, 脚本{stats.script_count}+")
        if badge_updates:
            parts.append(", ".join(badge_updates))
        msg = f"  已更新: {readme}"
        if parts:
            msg += f" ({'; '.join(parts)})"
        print(msg)
        return True
    else:
        print(f"  无需更新: {readme} 数据已是最新")
        return True


def _stats_update_changelog_archive(root: Path, stats: ProjectStats) -> bool:
    archive = root / "docs" / "retrospective" / "reports" / "project-governance" / "documentation-governance" / "agents-manifest-changelog-archive.md"
    if not archive.exists():
        print(f"  跳过: {archive} 不存在")
        return False

    content = archive.read_text(encoding="utf-8")
    changelog_marker = "<!-- changelog -->"
    idx = content.find(changelog_marker)
    if idx == -1:
        print("  警告: 归档文件中未找到 <!-- changelog --> 标记")
        return False

    entry = _stats_generate_changelog_entry(stats)
    today_prefix = f"- {stats.last_updated} | docs | 核心数据自动更新"

    after_marker = content[idx + len(changelog_marker):]
    lines = after_marker.split("\n")
    today_line_idx = None
    for i, line in enumerate(lines):
        if line.startswith(today_prefix):
            today_line_idx = i
            break

    if today_line_idx is not None:
        lines[today_line_idx] = entry
        new_content = content[:idx + len(changelog_marker)] + "\n".join(lines)
        atomic_write_text(archive, new_content, encoding="utf-8")
        print(f"  已更新今日条目: {archive}")
        return True
    else:
        insert_pos = idx + len(changelog_marker)
        new_content = content[:insert_pos] + "\n" + entry + content[insert_pos:]
        atomic_write_text(archive, new_content, encoding="utf-8")
        print(f"  已新增条目: {archive}")
        return True


def cmd_stats(args) -> int:
    root = args.path or resolve_project_root(__file__)
    if not root.exists():
        print(f"错误: 项目根目录不存在: {root}", file=sys.stderr)
        return 1

    print("收集项目统计数据...")
    try:
        stats = _stats_collect(root)
    except StatsSourceError as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1

    snapshot_path = root / ".agents" / ".stats-cache.json"
    anomaly_warnings = _stats_validate_with_snapshot(stats, snapshot_path)

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
    results.append(("changelog-archive", _stats_update_changelog_archive(root, stats)))

    _stats_save_snapshot(stats, snapshot_path)

    updated = sum(1 for _, ok in results if ok)
    print(f"\n完成: 已更新 {updated} 个文件")

    if getattr(args, 'strict_anomaly', False) and anomaly_warnings:
        print(f"\n[STATS-ERROR] 严格模式：检测到 {len(anomaly_warnings)} 个环比异常，返回退出码 2", file=sys.stderr)
        return 2

    return 0


# ============================================================
# weekly 子命令：周迭代数据快照
# ============================================================

def _weekly_count_test_commits(root: Path, days: int = 7) -> int:
    since = date.today() - timedelta(days=days)
    try:
        result = subprocess.run(
            ["git", "log", f"--since={since.isoformat()}", "--pretty=format:%s"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=30,
            encoding="utf-8",
        )
        if result.returncode != 0:
            return 0
        count = 0
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("test(") or line.startswith("test:") or line.startswith("test "):
                count += 1
        return count
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return 0


def _weekly_collect(root: Path, days: int = 7) -> dict:
    commit_count_total = _stats_count_commits(root)
    since = date.today() - timedelta(days=days)
    until = date.today()

    commits_by_type = {
        "feat": 0,
        "fix": 0,
        "refactor": 0,
        "docs": 0,
        "test": 0,
        "chore": 0,
        "other": 0,
    }
    commit_count_week = 0

    try:
        result = subprocess.run(
            ["git", "log", f"--since={since.isoformat()}", "--pretty=format:%s"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=30,
            encoding="utf-8",
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                line = line.strip()
                if not line:
                    continue
                commit_count_week += 1
                matched = False
                for t in ["feat", "fix", "refactor", "docs", "test", "chore"]:
                    if line.startswith(f"{t}(") or line.startswith(f"{t}:") or line.startswith(f"{t} "):
                        commits_by_type[t] += 1
                        matched = True
                        break
                if not matched:
                    commits_by_type["other"] += 1
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass

    test_commit_count = _weekly_count_test_commits(root, days)
    test_commit_ratio = round(test_commit_count / commit_count_week * 100, 1) if commit_count_week > 0 else 0.0

    return {
        "commit_count_total": commit_count_total,
        "commit_count_week": commit_count_week,
        "commits_by_type": commits_by_type,
        "test_commit_count": test_commit_count,
        "test_commit_ratio": test_commit_ratio,
        "period_days": days,
        "period_start": since.isoformat(),
        "period_end": until.isoformat(),
    }


def cmd_weekly(args) -> int:
    root = args.path or resolve_project_root(__file__)
    days = getattr(args, "days", 7)

    if not root.exists():
        print(f"错误: 项目根目录不存在: {root}", file=sys.stderr)
        return 1

    stats = _weekly_collect(root, days)

    print("=" * 60)
    print("周迭代数据摘要")
    print("=" * 60)
    print(f"统计周期: {stats['period_start']} ~ {stats['period_end']} (最近{stats['period_days']}天)")
    print(f"项目总提交数: {stats['commit_count_total']}")
    print(f"本周提交数:   {stats['commit_count_week']}")
    print()
    print("提交类型分布:")
    max_count = max(stats['commits_by_type'].values()) if stats['commits_by_type'] else 0
    for t, count in stats['commits_by_type'].items():
        bar_len = int(count / max_count * 20) if max_count > 0 else 0
        bar = "█" * bar_len
        print(f"  {t:<8} {count:>3} {bar}")
    print()
    print(f"测试相关提交: {stats['test_commit_count']} ({stats['test_commit_ratio']}%)")
    if stats['test_commit_ratio'] < 20 and stats['commit_count_week'] > 0:
        print("  💡 提示: 测试提交占比较低，建议补充测试覆盖")
    print()
    print("使用模板进行周复盘: python docgen.py weekly --days 7")
    print("=" * 60)

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
    rc = cmd_theme_dashboards(args)
    if rc != 0:
        print(f"\n[theme-dashboards 失败 (exit={rc})，中止后续任务]", file=sys.stderr)
        return rc

    print()
    rc = cmd_update_spec_readme(args)
    if rc != 0:
        print(f"\n[update-spec-readme 失败 (exit={rc})，中止后续任务]", file=sys.stderr)
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

    p_nav = subparsers.add_parser('nav', help='生成文档导航表（README.md / docs/README.md / docs/index.md）')
    add_common_args(p_nav)

    p_dash = subparsers.add_parser('dashboard', help='生成 Spec 执行进度看板（根 README.md）')
    add_common_args(p_dash)

    p_theme = subparsers.add_parser('theme-dashboards', help='为所有 13 个主题生成/刷新主题级执行看板')
    add_common_args(p_theme)

    p_update = subparsers.add_parser('update-spec-readme', help='将 .trae/specs/README.md 压缩为轻索引（< 50KB）')
    add_common_args(p_update)

    p_apps = subparsers.add_parser('apps', help='生成 apps/README.md 应用清单索引表')
    add_common_args(p_apps)

    p_stats = subparsers.add_parser('stats', help='统计并更新 README.md/AGENTS.md 核心数据指标')
    add_common_args(p_stats)
    p_stats.add_argument('--strict-anomaly', action='store_true', dest='strict_anomaly',
                         help='严格模式：环比异常（关键指标降幅>50%%）时返回退出码2，不阻断文件更新')

    p_all = subparsers.add_parser('all', help='依次执行 nav + dashboard + theme-dashboards + update-spec-readme + apps + stats')
    add_common_args(p_all)

    p_weekly = subparsers.add_parser('weekly', help='生成本周数据快照，辅助周复盘')
    add_common_args(p_weekly)
    p_weekly.add_argument('--days', type=int, default=7, help='统计最近N天（默认7天）')

    args = parser.parse_args()

    cmd_map = {
        'nav': cmd_nav,
        'dashboard': cmd_dashboard,
        'theme-dashboards': cmd_theme_dashboards,
        'update-spec-readme': cmd_update_spec_readme,
        'apps': cmd_apps,
        'stats': cmd_stats,
        'all': cmd_all,
        'weekly': cmd_weekly,
    }

    if not args.command:
        parser.print_help()
        return 1

    return cmd_map[args.command](args)


if __name__ == "__main__":
    sys.exit(main())

