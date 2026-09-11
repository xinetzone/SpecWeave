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
    CATEGORY_INDEX_FILE, CATEGORY_INDEX_DIR, TAG_INDEX_DIR, EXCLUDE_FILES, GENERATED_DIRS,
    DEFAULT_META, DESC_TRUNCATE_LENGTH, REQUIRED_FIELDS,
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


TAG_BUCKETS = [
    ("01-0-9.md", "0-9"),
    ("02-a.md", "A"),
    ("03-b-c.md", "B-C"),
    ("04-d-f.md", "D-F"),
    ("05-g-l.md", "G-L"),
    ("06-m-n.md", "M-N"),
    ("07-o-p.md", "O-P"),
    ("08-q-r.md", "Q-R"),
    ("09-s-t.md", "S-T"),
    ("10-u-z.md", "U-Z"),
    ("11-other-symbols.md", "符号与其他"),
    ("12-cjk-1.md", "中文一"),
    ("13-cjk-2.md", "中文二"),
    ("14-cjk-3.md", "中文三（含未分类）"),
    ("15-cjk-4.md", "中文四"),
    ("16-cjk-5.md", "中文五"),
]

# 大分类子分片定义：顶层分类 -> [(分片文件名后缀, 包含的子目录前缀列表), ...]
# 用于将超过阈值的大分类分片，按文件路径的二级目录前缀分发
CATEGORY_SUBSHARDS = {
    "learning": [
        ("00-02", ("00-", "01-", "02-")),
        ("03-04", ("03-", "04-")),
        ("05-08", ("05-", "06-", "07-", "08-")),
    ],
}


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
        # 忽略脚本目录与生成产物目录，避免索引文件递归纳入自身
        dirs[:] = [d for d in dirs if d not in GENERATED_DIRS]
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


def _build_md_link_from(base_dir: Path, target: Path, title: str) -> str:
    """从任意基准目录生成相对 Markdown 链接。"""
    return _build_md_link(Path(_get_relative_path(base_dir, target)), title)


def _top_level_category(category: str) -> str:
    """提取分类的顶层分组名称。"""
    if not category:
        return "unknown"
    return category.split("/", 1)[0]


def _get_top_level_hub_link(top_level: str) -> str:
    """返回顶层分类的入口链接（优先子目录README，其次分类分片，最后锚点）。"""
    hub_readme = KNOWLEDGE_DIR / top_level / "README.md"
    if hub_readme.exists():
        return _build_md_link(Path(top_level) / "README.md", top_level)
    # 链接到分类分片文件
    return _build_md_link(Path("categories") / f"{top_level}.md", top_level)


def _bucket_file_for_tag(tag: str) -> str:
    """按标签首字符将标签分发到细粒度分片，控制单文件大小。"""
    first = tag[:1].casefold()
    cp = ord(tag[0])
    if first.isdigit():
        return "01-0-9.md"
    if first == 'a':
        return "02-a.md"
    if first in ('b', 'c'):
        return "03-b-c.md"
    if 'd' <= first <= 'f':
        return "04-d-f.md"
    if 'g' <= first <= 'l':
        return "05-g-l.md"
    if first in ('m', 'n'):
        return "06-m-n.md"
    if first in ('o', 'p'):
        return "07-o-p.md"
    if first in ('q', 'r'):
        return "08-q-r.md"
    if first in ('s', 't'):
        return "09-s-t.md"
    if 'u' <= first <= 'z':
        return "10-u-z.md"
    # 非拉丁字母、非数字
    if cp < 0x3400:
        # 符号、标点、拉丁文扩展、希腊文、西里尔文、日文假名等
        return "11-other-symbols.md"
    # CJK字符按码点5路分片，确保每片<80KB
    if cp < 0x5B00:
        # CJK Ext A + 早期CJK统一汉字 U+3400~U+5AFF
        return "12-cjk-1.md"
    if cp < 0x672A:
        # U+5B00~U+6729（不含"未"U+672A）
        return "13-cjk-2.md"
    if cp < 0x6800:
        # U+672A(未)~U+67FF，包含"未分类"标签（538条目）
        return "14-cjk-3.md"
    if cp < 0x7E00:
        # U+6800~U+7DFF
        return "15-cjk-4.md"
    # U+7E00+：剩余CJK统一汉字、兼容汉字等
    return "16-cjk-5.md"


def _bucket_tag_index(tag_index: dict) -> dict:
    """将标签索引切分为多个固定分片。"""
    buckets = {filename: [] for filename, _ in TAG_BUCKETS}
    for tag, tag_entries in tag_index.items():
        bucket_file = _bucket_file_for_tag(tag)
        buckets[bucket_file].append((tag, tag_entries))
    return buckets


def _write_markdown(file_path: Path, lines: list[str]) -> None:
    """以 UTF-8 写入 Markdown 文件。"""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def _generated_frontmatter(title: str) -> list[str]:
    """机器生成索引文件统一使用的最小 YAML frontmatter（type/title）。

    约定：生成文件只携带定位类元数据；category/date/tags 等条目元数据
    属于知识条目本身，禁止出现在生成文件中。
    """
    safe_title = title.replace('"', "'")
    return [
        "---",
        "type: Reference",
        f'title: "{safe_title}"',
        "---",
        "",
    ]


def _append_related_resources(lines: list[str]) -> None:
    """追加知识库的相关资源区块。"""
    lines.append("## 相关资源")
    lines.append("")

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
        else:
            lines.append("*暂无回溯报告*")
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
        else:
            lines.append("*暂无任务总结*")
        lines.append("")


def _append_footer(lines: list[str]) -> None:
    """追加自动生成时间戳脚注。"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append("---")
    lines.append("")
    lines.append(f"*索引自动生成于 {now}*")
    lines.append("")


# ──────────────────────────────────────────────────────────────────────
# README.md 生成
# ──────────────────────────────────────────────────────────────────────

def _generate_root_readme(entries: list, groups: dict, tag_index: dict, sorted_by_date: list) -> None:
    """生成轻量级知识库入口页。"""
    total = len(entries)
    top_level_counts = defaultdict(int)
    for category, items in groups.items():
        top_level_counts[_top_level_category(category)] += len(items)

    lines = [
        *_generated_frontmatter("项目知识库"),
        "# 项目知识库",
        "",
        "项目知识库的统一入口页。详细分类条目与标签检索已拆分到独立索引，避免根 README 持续膨胀。",
        "",
        f"- **总条目数**：{total}",
        f"- **分类数**：{len(groups)}",
        f"- **标签数**：{len(tag_index)}",
        "",
        "## 快速导航",
        "",
        "| 顶层分类 | 条目数 | 入口 |",
        "|----------|--------|------|",
    ]

    for top_level in sorted(top_level_counts):
        lines.append(
            f"| {_escape_md(top_level)} | {top_level_counts[top_level]} | {_get_top_level_hub_link(top_level)} |"
        )

    lines.extend([
        "",
        "## 辅助索引",
        "",
        f"- {_build_md_link(Path('category-index.md'), '分类总索引')}：查看全部分类及条目摘要",
        f"- {_build_md_link(Path('tags/README.md'), '标签索引')}：按关键词标签分片检索",
        "",
        "## 最近更新",
        "",
        "| 标题 | 日期 | 分类 |",
        "|------|------|------|",
    ])

    for path, meta in sorted_by_date[:10]:
        title = meta.get("title", path.stem)
        date = meta.get("date", "")
        category = meta.get("category", "unknown")
        link = _build_md_link(path, title)
        lines.append(f"| {link} | {_escape_md(date)} | {_escape_md(category)} |")

    lines.append("")
    _append_related_resources(lines)

    lines.extend([
        "## 使用指南",
        "",
        "### 如何添加知识条目",
        "",
        "1. 在 `docs/knowledge/` 下选择对应的分类目录（如 `operations/`、`learning/` 等）",
        "2. 复制 `template.md` 作为模板，创建新的 `.md` 文件",
        "3. 填写 YAML frontmatter 元数据（标题、分类、标签、日期、摘要等）",
        "4. 在正文中按照模板结构编写内容",
        "5. 运行 `python scripts/generate_index.py` 重新生成入口页、分类索引与标签分片",
        "",
        "### 如何检索",
        "",
        "- **按分类入口**：优先使用上方「快速导航」进入各主题 README",
        "- **按全部分类**：打开 [分类总索引](category-index.md) 查看所有分类及摘要",
        "- **按标签检索**：打开 [标签索引](tags/README.md) 后进入对应分片页面",
        "- **按时间排序**：查看本页「最近更新」章节，了解最新添加的知识条目",
        '- **全文搜索**：在项目根目录使用 `rg "关键词" docs/knowledge/` 进行全文搜索',
        "",
        "### 如何维护",
        "",
        "- **定期整理**：每月检查一次知识条目，更新过时内容，补充遗漏信息",
        "- **标签规范化**：使用统一的标签命名，避免同义词分散（如 `powershell` 和 `ps`）",
        "- **及时归档**：完成任务或解决问题后，及时将经验沉淀为知识条目",
        "- **索引更新**：每次添加、修改或删除知识条目后，运行本脚本重新生成全部索引",
        "",
    ])

    _append_footer(lines)
    _write_markdown(OUTPUT_FILE, lines)


def _get_subshard_for_entry(top_level: str, path: Path) -> str | None:
    """根据文件路径判断条目属于哪个子分片，返回子分片后缀；无匹配返回第一个分片。"""
    subshards = CATEGORY_SUBSHARDS.get(top_level)
    if not subshards:
        return None
    rel = str(path).replace("\\", "/")
    parts = rel.split("/", 2)
    if len(parts) < 2 or parts[0] != top_level:
        return subshards[0][0]
    sub_part = parts[1] if len(parts) > 1 else ""
    for suffix, prefixes in subshards:
        if any(sub_part.startswith(p) for p in prefixes):
            return suffix
    return subshards[0][0]  # 不匹配任何前缀时默认第一分片


def _generate_category_shard_file(
    file_path: Path,
    title: str,
    cat_entries: list,
    link_prefix: str = "..",
    extra_nav: list[str] | None = None,
) -> None:
    """生成单个分类分片文件内容（通用）。

    Args:
        link_prefix: 条目前缀路径。单文件分片用 ".."（categories/ → knowledge/），
                     子分片（categories/top/）用 "../.."。
    """
    prefix = Path(link_prefix)
    lines = [
        *_generated_frontmatter(title),
        f"# {title}",
        "",
        f"- [返回分类总索引]({link_prefix}/category-index.md)",
        f"- [返回知识库首页]({link_prefix}/README.md)",
        f"- [按标签检索]({link_prefix}/tags/README.md)",
    ]
    if extra_nav:
        lines.extend(extra_nav)
    lines.append("")

    total = sum(len(items) for _, items in cat_entries)
    lines.append(f"> 本分片收录 **{len(cat_entries)}** 个子分类，共 **{total}** 条条目。")
    lines.append("")

    prev_level = 1
    for cat, items in cat_entries:
        depth = cat.count("/")
        # 分类元数据可能深度跳跃（如 "docs" 与 "docs/a/b/c/d" 并存且中间层并非
        # 真实分类）；标题最多比上一条深一级，杜绝 MyST 标题跳级警告。
        level = min(2 + depth, prev_level + 1)
        heading = "#" * level
        prev_level = level
        lines.append(f"{heading} {cat}")
        lines.append("")
        lines.append("| 标题 | 摘要 | 日期 | 标签 |")
        lines.append("|------|------|------|------|")
        for path, meta in items:
            title_txt = meta.get("title", path.stem)
            summary = meta.get("summary", "")
            date = meta.get("date", "")
            tags = meta.get("tags", [])
            link = _build_md_link(prefix / path, title_txt)
            lines.append(
                f"| {link} | {_escape_md(summary)} | {_escape_md(date)} | {_escape_md(_format_tags(tags))} |"
            )
        lines.append("")

    _append_footer(lines)
    _write_markdown(file_path, lines)


def _generate_category_shard(top_level: str, categories: dict) -> None:
    """生成单个顶层分类的分片文件（支持子分片）。"""
    # 收集属于该顶层分类的所有子分类条目
    cat_entries_all = []
    for cat, items in sorted(categories.items()):
        cat_top = cat.split("/", 1)[0]
        if cat_top == top_level:
            cat_entries_all.append((cat, items))

    subshards = CATEGORY_SUBSHARDS.get(top_level)
    if not subshards:
        # 无子分片定义：单文件模式
        _generate_category_shard_file(
            CATEGORY_INDEX_DIR / f"{top_level}.md",
            f"分类索引：{top_level}",
            cat_entries_all,
            link_prefix="..",
        )
        return

    # ── 子分片模式 ──
    subdir = CATEGORY_INDEX_DIR / top_level
    subdir.mkdir(parents=True, exist_ok=True)

    # 按文件路径将单个条目分发到子分片（不按category组，因为很多条目category只有顶层名）
    subshard_entries: dict[str, list] = {suffix: [] for suffix, _ in subshards}
    for cat, items in cat_entries_all:
        for path, meta in items:
            suffix = _get_subshard_for_entry(top_level, path)
            subshard_entries[suffix].append((cat, path, meta))

    # 生成子分片Hub页 (README.md) — Hub在子目录中，link_prefix="../.."
    hub_lines = [
        *_generated_frontmatter(f"分类索引：{top_level}"),
        f"# 分类索引：{top_level}",
        "",
        "- [返回分类总索引](../category-index.md)",
        "- [返回知识库首页](../../README.md)",
        "- [按标签检索](../../tags/README.md)",
        "",
        f"本分类条目较多，已按主题拆分为 **{len(subshards)}** 个子分片：",
        "",
        "| 分片 | 范围 | 条目数 | 链接 |",
        "|------|------|--------|------|",
    ]
    shard_descriptions = {
        "00-02": "本质与思维 · 协议与接口 · 工程方法论",
        "03-04": "平台与工具 · 文档与标记",
        "05-08": "AI多模态 · 商业趋势 · 厂商产品 · 系统基础设施",
    }
    for suffix, _label in subshards:
        entries = subshard_entries[suffix]
        desc = shard_descriptions.get(suffix, suffix)
        link = _build_md_link(Path(f"{suffix}.md"), f"{top_level}-{suffix}")
        hub_lines.append(f"| {suffix} | {desc} | {len(entries)} | {link} |")

    hub_lines.append("")
    _append_footer(hub_lines)
    _write_markdown(subdir / "README.md", hub_lines)

    # 生成各子分片文件 — 子分片在子目录中，link_prefix="../.."
    shard_labels = {
        "00-02": "本质与思维 · 协议与接口 · 工程方法论",
        "03-04": "平台与工具 · 文档与标记",
        "05-08": "AI多模态 · 商业趋势 · 厂商产品 · 系统基础设施",
    }
    for suffix, _prefixes in subshards:
        raw_entries = subshard_entries[suffix]
        # 在子分片内按category分组
        cat_map: dict[str, list] = defaultdict(list)
        for cat, path, meta in raw_entries:
            cat_map[cat].append((path, meta))
        sub_cat_entries = sorted(cat_map.items())
        label_text = shard_labels.get(suffix, suffix)
        nav_back = [f"- [返回{top_level}分片索引](README.md)"]
        _generate_category_shard_file(
            subdir / f"{suffix}.md",
            f"分类索引：{top_level} · {label_text}",
            sub_cat_entries,
            link_prefix="../..",
            extra_nav=nav_back,
        )


def _generate_category_index(entries: list, groups: dict) -> None:
    """生成分类索引Hub页及各分片文件。"""
    top_level_counts = defaultdict(int)
    top_level_subcats = defaultdict(int)
    for category, items in groups.items():
        top = category.split("/", 1)[0]
        top_level_counts[top] += len(items)
        top_level_subcats[top] += 1

    # ── Hub页 ──
    lines = [
        *_generated_frontmatter("分类总索引"),
        "# 分类总索引",
        "",
        "- [返回知识库首页](README.md)",
        "- [按标签检索](tags/README.md)",
        "",
        "分类索引已按顶层分类拆分为独立分片，避免单文件过大；条目较多的分类进一步拆分为子分片。先在下表选择分类，再进入对应分片查看详细条目。",
        "",
        "## 统计摘要",
        "",
        f"- **总条目数**：{len(entries)}",
        f"- **分类路径数**：{len(groups)}",
        f"- **顶层分类数**：{len(top_level_counts)}",
        "",
        "| 顶层分类 | 子分类数 | 条目数 | 入口 |",
        "|----------|----------|--------|------|",
    ]

    for top_level in sorted(top_level_counts, key=lambda x: -top_level_counts[x]):
        count = top_level_counts[top_level]
        subcats = top_level_subcats[top_level]
        if top_level in CATEGORY_SUBSHARDS:
            # 子分片模式：链接到子目录Hub
            shard_link = _build_md_link(Path("categories") / top_level / "README.md", top_level)
        else:
            shard_link = _build_md_link(Path("categories") / f"{top_level}.md", top_level)
        lines.append(f"| {_escape_md(top_level)} | {subcats} | {count} | {shard_link} |")

    lines.append("")
    _append_footer(lines)
    _write_markdown(CATEGORY_INDEX_FILE, lines)

    # ── 分片文件 ──
    CATEGORY_INDEX_DIR.mkdir(parents=True, exist_ok=True)

    # 清理旧的分片文件（单文件模式）
    new_shard_files = {f"{tl}.md" for tl in top_level_counts if tl not in CATEGORY_SUBSHARDS}
    new_shard_dirs = {tl for tl in top_level_counts if tl in CATEGORY_SUBSHARDS}
    for f in CATEGORY_INDEX_DIR.glob("*.md"):
        if f.name not in new_shard_files:
            f.unlink()
    # 清理不再需要的子分片目录
    for d in CATEGORY_INDEX_DIR.iterdir():
        if d.is_dir() and d.name not in new_shard_dirs:
            import shutil
            shutil.rmtree(d)

    # 生成各分片
    for top_level in top_level_counts:
        _generate_category_shard(top_level, groups)

    # ── Sphinx toctree Hub（categories/index.md）──
    # 与上面写出的分片集合同源派生：条目为空的分类不产生分片，也不进入 toctree，
    # 从契约上消除"toctree 引用已被清理的空分片"问题。
    toctree_entries = []
    for top_level in sorted(top_level_counts):
        if top_level in CATEGORY_SUBSHARDS:
            toctree_entries.append(f"{top_level}/README")
        else:
            toctree_entries.append(top_level)
    _write_markdown(
        CATEGORY_INDEX_DIR / "index.md",
        [
            *_generated_frontmatter("Categories"),
            "<!-- 本文件由 scripts/generate_index.py 自动生成，请勿手工编辑；",
            "     分类集合变化后重新运行脚本，本 toctree 与分片集合同源派生。 -->",
            "# Categories",
            "",
            "```{toctree}",
            ":maxdepth: 2",
            ":hidden:",
            "",
            *toctree_entries,
            "```",
        ],
    )


def _generate_tag_indexes(tag_index: dict) -> None:
    """生成标签索引总览及分片页面。"""
    buckets = _bucket_tag_index(tag_index)
    TAG_INDEX_DIR.mkdir(parents=True, exist_ok=True)

    for existing in TAG_INDEX_DIR.glob("*.md"):
        if existing.name != "README.md" and existing.name not in buckets:
            existing.unlink()

    readme_lines = [
        *_generated_frontmatter("标签索引"),
        "# 标签索引",
        "",
        "- [返回知识库首页](../README.md)",
        "- [查看分类总索引](../category-index.md)",
        "",
        "标签索引已按首字符拆分，避免单文件过大；先在本页选择分片，再进入具体标签。",
        "",
        "| 分片 | 标签数 | 条目数 | 链接 |",
        "|------|--------|--------|------|",
    ]

    for filename, label in TAG_BUCKETS:
        bucket_items = buckets[filename]
        tag_count = len(bucket_items)
        entry_count = sum(len(items) for _, items in bucket_items)
        readme_lines.append(
            f"| {_escape_md(label)} | {tag_count} | {entry_count} | {_build_md_link(Path(filename), label)} |"
        )

    readme_lines.append("")
    _append_footer(readme_lines)
    _write_markdown(TAG_INDEX_DIR / "README.md", readme_lines)

    for filename, label in TAG_BUCKETS:
        bucket_items = buckets[filename]
        lines = [
            *_generated_frontmatter(f"标签索引：{label}"),
            f"# 标签索引：{label}",
            "",
            "- [返回标签索引总览](README.md)",
            "- [返回知识库首页](../README.md)",
            "",
            f"> 本页收录 **{len(bucket_items)}** 个标签。",
            "",
        ]

        for tag, tag_entries in bucket_items:
            lines.append(f"## {tag}")
            lines.append("")
            for path, meta in tag_entries:
                title = meta.get("title", path.stem)
                target = KNOWLEDGE_DIR / path
                lines.append(f"- {_build_md_link_from(TAG_INDEX_DIR, target, title)}")
            lines.append("")

        _append_footer(lines)
        _write_markdown(TAG_INDEX_DIR / filename, lines)

    # ── Sphinx toctree Hub（tags/index.md）──
    # 16 个分片文件名由 TAG_BUCKETS 固定声明，toctree 与之同源，杜绝手工漂移。
    _write_markdown(
        TAG_INDEX_DIR / "index.md",
        [
            *_generated_frontmatter("Tags"),
            "<!-- 本文件由 scripts/generate_index.py 自动生成，请勿手工编辑；",
            "     16 个分片由脚本中的 TAG_BUCKETS 固定声明，toctree 与之同源。 -->",
            "# Tags",
            "",
            "```{toctree}",
            ":maxdepth: 2",
            ":hidden:",
            "",
            *[filename.removesuffix(".md") for filename, _ in TAG_BUCKETS],
            "```",
        ],
    )


def generate_readme(entries: list):
    """
    生成知识库入口页及其拆分索引。

    产出物：
      1. docs/knowledge/README.md：轻量入口页
      2. docs/knowledge/category-index.md：完整分类索引（人类入口）
      3. docs/knowledge/categories/index.md：Sphinx toctree Hub（与分片集合同源派生）
      4. docs/knowledge/categories/*.md：分类分片
      5. docs/knowledge/tags/README.md：标签索引总览（人类入口）
      6. docs/knowledge/tags/index.md：Sphinx toctree Hub（与 16 个固定分片同源）
      7. docs/knowledge/tags/*.md：标签索引分片
    """
    if not entries:
        _generate_empty_readme()
        return

    groups = group_by_category(entries)
    tag_index = build_tag_index(entries)
    sorted_by_date = sorted(
        entries,
        key=lambda x: x[1].get("date", ""),
        reverse=True,
    )

    _generate_root_readme(entries, groups, tag_index, sorted_by_date)
    _generate_category_index(entries, groups)
    _generate_tag_indexes(tag_index)

    # 统计顶层分类数
    _top_levels = set(cat.split("/", 1)[0] for cat in groups.keys())

    print(f"[完成] 入口页已生成：{OUTPUT_FILE}")
    print(f"[完成] 分类索引Hub已生成：{CATEGORY_INDEX_FILE}")
    print(f"[完成] 分类分片目录已生成：{CATEGORY_INDEX_DIR}（{len(_top_levels)} 个分片）")
    print(f"[完成] 标签索引目录已生成：{TAG_INDEX_DIR}（{len(TAG_BUCKETS)} 个分片）")
    print(f"  - 总条目数：{len(entries)}")
    print(f"  - 分类数：{len(groups)}")
    print(f"  - 标签数：{len(tag_index)}")


def _generate_empty_readme():
    """生成空知识库的占位 README 与最小索引页。"""
    lines = [
        *_generated_frontmatter("项目知识库"),
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

    _append_related_resources(lines)
    _append_footer(lines)
    _write_markdown(OUTPUT_FILE, lines)

    _write_markdown(
        CATEGORY_INDEX_FILE,
        [
            *_generated_frontmatter("分类总索引"),
            "# 分类总索引",
            "",
            "- [返回知识库首页](README.md)",
            "",
            "> 当前暂无可展示的分类条目。",
            "",
        ],
    )
    _write_markdown(
        TAG_INDEX_DIR / "README.md",
        [
            *_generated_frontmatter("标签索引"),
            "# 标签索引",
            "",
            "- [返回知识库首页](../README.md)",
            "",
            "> 当前暂无可展示的标签条目。",
            "",
        ],
    )

    # 空知识库同样落盘空 toctree Hub，保证 knowledge/index.md 的 toctree 引用始终可解析
    _write_markdown(
        CATEGORY_INDEX_DIR / "index.md",
        [
            *_generated_frontmatter("Categories"),
            "# Categories",
            "",
            "```{toctree}",
            ":maxdepth: 2",
            ":hidden:",
            "```",
        ],
    )
    _write_markdown(
        TAG_INDEX_DIR / "index.md",
        [
            *_generated_frontmatter("Tags"),
            "# Tags",
            "",
            "```{toctree}",
            ":maxdepth: 2",
            ":hidden:",
            "```",
        ],
    )

    print(f"[完成] 空知识库入口页已生成：{OUTPUT_FILE}")


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
