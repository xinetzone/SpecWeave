#!/usr/bin/env python3
"""
知识库索引自动生成脚本。

功能：
  1. 递归扫描 docs/knowledge/ 下所有 .md 文件（排除 template.md 和 README.md）
  2. 解析每个文件的 YAML frontmatter 元数据
  3. 生成 docs/knowledge/README.md 索引文件

用法：
  cd docs/knowledge/scripts/
  python generate_index.py
"""

import os
import re
import sys
import json
import importlib.util
from datetime import datetime
from pathlib import Path
from collections import defaultdict

_SCRIPT_DIR = Path(__file__).resolve().parent

from constants import (
    SCRIPT_DIR, KNOWLEDGE_DIR, DOCS_DIR, OUTPUT_FILE,
    EXCLUDE_FILES, DEFAULT_META, DESC_TRUNCATE_LENGTH, REQUIRED_FIELDS,
)

_AGENTS_SCRIPTS_DIR = _SCRIPT_DIR.parents[2] / ".agents" / "scripts"
_frontmatter_spec = importlib.util.spec_from_file_location(
    "lib_frontmatter",
    _AGENTS_SCRIPTS_DIR / "lib" / "frontmatter.py",
    submodule_search_locations=[str(_AGENTS_SCRIPTS_DIR / "lib")],
)
_lib_frontmatter = importlib.util.module_from_spec(_frontmatter_spec)
sys.modules["lib_frontmatter"] = _lib_frontmatter
_frontmatter_spec.loader.exec_module(_lib_frontmatter)
parse_frontmatter_unified = _lib_frontmatter.parse_frontmatter_unified


# ──────────────────────────────────────────────────────────────────────
# Frontmatter 解析
# ──────────────────────────────────────────────────────────────────────

# 模块级告警统计：收集 frontmatter 不合规的文件信息
_frontmatter_warnings = []


def _check_required_fields(file_path: Path, fields: dict) -> list:
    """
    检测 frontmatter 中缺失的必填字段。

    参数:
        file_path: 文件路径（用于告警输出）
        fields: 已解析的 frontmatter 字段字典

    返回:
        list: 缺失字段名列表（空列表表示全部齐全）
    """
    missing = []
    for field in REQUIRED_FIELDS:
        val = fields.get(field)
        if val is None:
            missing.append(field)
        elif isinstance(val, str) and not val.strip():
            missing.append(field)
        elif isinstance(val, list) and len(val) == 0:
            missing.append(field)
    return missing


def parse_frontmatter(file_path: Path) -> dict:
    """
    解析 Markdown 文件的 frontmatter（支持 YAML 和 TOML 格式）。

    使用统一解析入口自动识别 TOML(+++)、YAML(---) 和 x-toml-ref 格式。
    缺少 frontmatter 或必填字段缺失时输出明确 warning 日志。

    参数:
        file_path: Markdown 文件的 Path 对象

    返回:
        dict: 解析后的元数据字典，字段见 DEFAULT_META
    """
    meta = dict(DEFAULT_META)
    meta["title"] = file_path.stem

    fields = parse_frontmatter_unified(file_path)

    if fields is None:
        # 情况一：完全无 frontmatter
        required_list = "/".join(REQUIRED_FIELDS)
        msg = f"[警告] 文件缺少 frontmatter：{file_path}，必填字段：{required_list}，将使用默认值（unknown 分类、无标签、无最近更新记录）"
        print(msg, file=sys.stderr)
        _frontmatter_warnings.append({
            "file": str(file_path),
            "type": "missing_frontmatter",
            "missing_fields": REQUIRED_FIELDS[:],
        })
        return meta

    if fields:
        title_val = fields.get("title")
        if title_val:
            meta["title"] = _coerce_to_str(title_val)
        category_val = fields.get("category")
        if category_val:
            meta["category"] = _coerce_to_str(category_val)
        date_val = fields.get("date")
        if date_val:
            meta["date"] = _coerce_to_str(date_val)
        status_val = fields.get("status")
        if status_val:
            meta["status"] = _coerce_to_str(status_val)
        author_val = fields.get("author")
        if author_val:
            meta["author"] = _coerce_to_str(author_val)
        summary_val = fields.get("summary")
        if summary_val:
            meta["summary"] = _coerce_to_str(summary_val)
        tags_val = fields.get("tags")
        if isinstance(tags_val, list):
            meta["tags"] = [str(t).strip() for t in tags_val if str(t).strip()]
        elif isinstance(tags_val, str):
            meta["tags"] = _parse_tags(tags_val)

    # 情况二：有 frontmatter 但缺必填字段
    missing_fields = _check_required_fields(file_path, fields)
    if missing_fields:
        missing_str = "/".join(missing_fields)
        msg = f"[警告] 文件 frontmatter 缺失字段：{file_path}，缺失：{missing_str}，将使用默认值（可能导致分类降级或索引缺失）"
        print(msg, file=sys.stderr)
        _frontmatter_warnings.append({
            "file": str(file_path),
            "type": "missing_fields",
            "missing_fields": missing_fields,
        })

    if not meta["title"]:
        meta["title"] = file_path.stem

    return meta


def _coerce_to_str(value) -> str:
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value).strip() if value is not None else ""


def _parse_string_value(raw: str) -> str:
    """去除字符串值两端的引号和空白。"""
    val = raw.strip()
    if not val:
        return ""
    # 去除首尾的引号（支持单引号和双引号）
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        val = val[1:-1]
    return val.strip()


def _parse_tags(raw: str) -> list:
    """解析标签列表字符串，返回标签列表。"""
    # 尝试 JSON 解析
    try:
        tags = json.loads(raw)
        if isinstance(tags, list):
            return [str(t).strip() for t in tags if str(t).strip()]
    except (json.JSONDecodeError, TypeError):
        pass

    # 回退：手动按逗号分割
    # 先去除首尾方括号
    raw = raw.strip()
    if raw.startswith("["):
        raw = raw[1:]
    if raw.endswith("]"):
        raw = raw[:-1]

    tags = []
    for item in raw.split(","):
        item = item.strip()
        if item:
            # 去除引号
            if (item.startswith('"') and item.endswith('"')) or (item.startswith("'") and item.endswith("'")):
                item = item[1:-1]
            item = item.strip()
            if item:
                tags.append(item)
    return tags


# ──────────────────────────────────────────────────────────────────────
# 文件扫描
# ──────────────────────────────────────────────────────────────────────

def scan_knowledge_files() -> list:
    """
    递归扫描知识库目录下所有 .md 文件，排除 template.md 和 README.md。

    返回:
        list[tuple]: 每个元素为 (文件相对路径, 元数据字典)
    """
    entries = []

    for root, dirs, files in os.walk(KNOWLEDGE_DIR):
        # 忽略 scripts 目录自身
        dirs[:] = [d for d in dirs if d != "scripts"]
        for filename in files:
            if not filename.endswith(".md"):
                continue
            if filename.lower() in EXCLUDE_FILES:
                continue

            file_path = Path(root) / filename
            # 计算相对于知识库根目录的路径
            relative_path = file_path.relative_to(KNOWLEDGE_DIR)

            meta = parse_frontmatter(file_path)

            entries.append((relative_path, meta))

    return entries


# ──────────────────────────────────────────────────────────────────────
# 分类与标签聚合
# ──────────────────────────────────────────────────────────────────────

def group_by_category(entries: list) -> dict:
    """
    按 category 字段分组。
    返回 {category_name: [(relative_path, meta), ...]}
    """
    groups = defaultdict(list)
    for path, meta in entries:
        cat = meta.get("category", "unknown") or "unknown"
        groups[cat].append((path, meta))
    return dict(groups)


def build_tag_index(entries: list) -> dict:
    """
    构建标签→条目列表的索引，按标签字母序排序。
    返回 {tag_name: [(relative_path, meta), ...]}
    """
    tag_map = defaultdict(list)
    for path, meta in entries:
        tags = meta.get("tags", [])
        if not tags:
            # 无标签的条目归入"未分类"标签
            tag_map["未分类"].append((path, meta))
            continue
        for tag in tags:
            tag_map[tag].append((path, meta))
    # 按标签字母序排序后返回
    return dict(sorted(tag_map.items(), key=lambda x: x[0].lower()))


# ──────────────────────────────────────────────────────────────────────
# 辅助函数
# ──────────────────────────────────────────────────────────────────────

def _escape_md(text: str) -> str:
    """转义 Markdown 表格中的管道符。"""
    if text:
        return text.replace("|", "\\|").replace("\n", " ")
    return ""


def _format_tags(tags: list) -> str:
    """将标签列表格式化为逗号分隔的字符串。"""
    if not tags:
        return "-"
    return "、".join(tags)


def _build_md_link(path: Path, title: str) -> str:
    """生成 Markdown 相对链接，确保路径使用正斜杠。"""
    path_str = str(path).replace("\\", "/")
    return f"[{_escape_md(title)}]({path_str})"


def _get_relative_path(base: Path, target: Path) -> str:
    """计算从 base 到 target 的相对路径，使用正斜杠。"""
    # 使用 os.path.relpath 处理兄弟目录等非父子关系的情况
    rel = os.path.relpath(target, base)
    return rel.replace("\\", "/")


# ──────────────────────────────────────────────────────────────────────
# README.md 生成
# ──────────────────────────────────────────────────────────────────────

def generate_readme(entries: list):
    """
    生成完整的 README.md 索引文件。

    章节结构：
      1. 标题
      2. 统计摘要
      3. 按类别分组的条目列表
      4. 按标签聚合的关键词索引
      5. 最近更新 TOP 10
      6. 相关资源
      7. 使用指南
      8. 自动生成时间戳脚注
    """
    if not entries:
        _generate_empty_readme()
        return

    groups = group_by_category(entries)
    tag_index = build_tag_index(entries)

    # 按日期排序（降序），用于最近更新
    sorted_by_date = sorted(
        entries,
        key=lambda x: x[1].get("date", ""),
        reverse=True,
    )

    lines = []

    # ── 标题 ──
    lines.append("# 项目知识库")
    lines.append("")

    # ── 统计摘要 ──
    lines.append("## 统计摘要")
    lines.append("")
    total = len(entries)
    lines.append(f"- **总条目数**：{total}")
    lines.append("")
    lines.append("| 分类 | 数量 |")
    lines.append("|------|------|")
    for cat in sorted(groups.keys()):
        lines.append(f"| {_escape_md(cat)} | {len(groups[cat])} |")
    lines.append("")

    # ── 按类别分组 ──
    lines.append("## 按类别浏览")
    lines.append("")
    for cat in sorted(groups.keys()):
        cat_entries = groups[cat]
        lines.append(f"### {cat}")
        lines.append("")
        lines.append("| 标题 | 摘要 | 日期 | 标签 |")
        lines.append("|------|------|------|------|")
        for path, meta in cat_entries:
            title = meta.get("title", path.stem)
            summary = meta.get("summary", "")
            date = meta.get("date", "")
            tags = meta.get("tags", [])
            link = _build_md_link(path, title)
            lines.append(
                f"| {link} | {_escape_md(summary)} | {_escape_md(date)} | {_escape_md(_format_tags(tags))} |"
            )
        lines.append("")

    # ── 标签索引 ──
    lines.append("## 标签索引")
    lines.append("")
    for tag, tag_entries in tag_index.items():
        lines.append(f"### {tag}")
        lines.append("")
        for path, meta in tag_entries:
            title = meta.get("title", path.stem)
            link = _build_md_link(path, title)
            lines.append(f"- {link}")
        lines.append("")

    # ── 最近更新 TOP 10 ──
    lines.append("## 最近更新")
    lines.append("")
    lines.append("| 标题 | 日期 | 分类 |")
    lines.append("|------|------|------|")
    recent = sorted_by_date[:10]
    for path, meta in recent:
        title = meta.get("title", path.stem)
        date = meta.get("date", "")
        category = meta.get("category", "unknown")
        link = _build_md_link(path, title)
        lines.append(f"| {link} | {_escape_md(date)} | {_escape_md(category)} |")
    lines.append("")

    # ── 相关资源 ──
    lines.append("## 相关资源")
    lines.append("")

    # 回溯报告目录
    retrospective_dir = DOCS_DIR / "retrospective"
    if retrospective_dir.exists():
        lines.append("### 回溯报告")
        lines.append("")
        retro_files = sorted(retrospective_dir.glob("*.md"))
        if retro_files:
            for f in retro_files:
                rel = _get_relative_path(KNOWLEDGE_DIR, f)
                # 尝试读取标题
                title = _read_md_title(f)
                lines.append(f"- [{title}]({rel})")
        else:
            lines.append("*暂无回溯报告*")
        lines.append("")

    # 任务总结目录
    summaries_dir = DOCS_DIR / "task-summaries"
    if summaries_dir.exists():
        lines.append("### 任务总结")
        lines.append("")
        summary_files = sorted(summaries_dir.glob("*.md"))
        if summary_files:
            for f in summary_files:
                rel = _get_relative_path(KNOWLEDGE_DIR, f)
                title = _read_md_title(f)
                lines.append(f"- [{title}]({rel})")
        else:
            lines.append("*暂无任务总结*")
        lines.append("")

    # ── 使用指南 ──
    lines.append("## 使用指南")
    lines.append("")
    lines.append("### 如何添加知识条目")
    lines.append("")
    lines.append("1. 在 `docs/knowledge/` 下选择对应的分类目录（如 `operations/`、`platform/` 等）")
    lines.append("2. 复制 `template.md` 作为模板，创建新的 `.md` 文件")
    lines.append("3. 填写 YAML frontmatter 元数据（标题、分类、标签、日期、摘要等）")
    lines.append("4. 在正文中按照模板结构编写内容")
    lines.append("5. 运行 `python scripts/generate_index.py` 重新生成索引")
    lines.append("")
    lines.append("### 如何检索")
    lines.append("")
    lines.append("- **按类别浏览**：使用上方的「按类别浏览」章节，按操作、平台、排错等分类查找")
    lines.append("- **按标签检索**：使用上方的「标签索引」章节，按关键词标签快速定位")
    lines.append("- **按时间排序**：查看「最近更新」章节，了解最新添加的知识条目")
    lines.append('- **全文搜索**：在项目根目录使用 `grep -r "关键词" docs/knowledge/` 进行全文搜索')
    lines.append("")
    lines.append("### 如何维护")
    lines.append("")
    lines.append("- **定期整理**：每月检查一次知识条目，更新过时内容，补充遗漏信息")
    lines.append("- **标签规范化**：使用统一的标签命名，避免同义词分散（如 `powershell` 和 `ps`）")
    lines.append("- **及时归档**：完成任务或解决问题后，及时将经验沉淀为知识条目")
    lines.append("- **索引更新**：每次添加、修改或删除知识条目后，运行本脚本重新生成索引")
    lines.append("")

    # ── 时间戳脚注 ──
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"---")
    lines.append("")
    lines.append(f"*索引自动生成于 {now}*")
    lines.append("")

    # 写入文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[完成] 索引文件已生成：{OUTPUT_FILE}")
    print(f"  - 总条目数：{total}")
    print(f"  - 分类数：{len(groups)}")
    print(f"  - 标签数：{len(tag_index)}")


def _generate_empty_readme():
    """生成空知识库的占位 README。"""
    lines = [
        "# 项目知识库",
        "",
        "> 当前知识库中暂无条目。",
        "",
        "## 快速开始",
        "",
        "1. 复制 `template.md` 到对应分类目录（如 `operations/`）",
        "2. 填写 frontmatter 元数据和正文内容",
        "3. 运行 `python scripts/generate_index.py` 生成索引",
        "",
        "## 相关资源",
        "",
    ]

    # 依然列出相关资源
    retrospective_dir = DOCS_DIR / "retrospective"
    if retrospective_dir.exists():
        lines.append("### 回溯报告")
        lines.append("")
        retro_files = sorted(retrospective_dir.glob("*.md"))
        if retro_files:
            for f in retro_files:
                rel = _get_relative_path(KNOWLEDGE_DIR, f)
                title = _read_md_title(f)
                lines.append(f"- [{title}]({rel})")
        lines.append("")

    summaries_dir = DOCS_DIR / "task-summaries"
    if summaries_dir.exists():
        lines.append("### 任务总结")
        lines.append("")
        summary_files = sorted(summaries_dir.glob("*.md"))
        if summary_files:
            for f in summary_files:
                rel = _get_relative_path(KNOWLEDGE_DIR, f)
                title = _read_md_title(f)
                lines.append(f"- [{title}]({rel})")
        lines.append("")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append("---")
    lines.append("")
    lines.append(f"*索引自动生成于 {now}*")
    lines.append("")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[完成] 空知识库索引已生成：{OUTPUT_FILE}")


def _read_md_title(file_path: Path) -> str:
    """
    读取 Markdown 文件的一级标题作为显示名称。
    如果读取失败或没有标题，返回文件名（不含扩展名）。
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("# ") and not line.startswith("## "):
                    return line[2:].strip()
    except Exception:
        pass
    return file_path.stem


# ──────────────────────────────────────────────────────────────────────
# 主入口
# ──────────────────────────────────────────────────────────────────────

def main():
    """脚本主入口。"""
    # 验证工作目录：确保 KNOWLEDGE_DIR 存在
    if not KNOWLEDGE_DIR.exists():
        print(f"[错误] 知识库目录不存在：{KNOWLEDGE_DIR}", file=sys.stderr)
        sys.exit(1)

    print(f"[信息] 扫描知识库目录：{KNOWLEDGE_DIR}")
    entries = scan_knowledge_files()
    print(f"[信息] 发现 {len(entries)} 个知识条目")
    generate_readme(entries)

    # 输出 frontmatter 告警统计
    if _frontmatter_warnings:
        warning_count = len(_frontmatter_warnings)
        missing_fm_count = sum(1 for w in _frontmatter_warnings if w["type"] == "missing_frontmatter")
        missing_fields_count = sum(1 for w in _frontmatter_warnings if w["type"] == "missing_fields")
        print("", file=sys.stderr)
        print(f"[告警统计] 共 {warning_count} 个文件 frontmatter 不合规：", file=sys.stderr)
        print(f"  - 缺少 frontmatter：{missing_fm_count} 个", file=sys.stderr)
        print(f"  - frontmatter 字段缺失：{missing_fields_count} 个", file=sys.stderr)
        print(f"  必填字段清单：{'/'.join(REQUIRED_FIELDS)}", file=sys.stderr)
        print(f"  请参考 docs/knowledge/template.md 补充 frontmatter 字段", file=sys.stderr)
    else:
        print("[信息] 所有知识条目 frontmatter 合规")


if __name__ == "__main__":
    main()