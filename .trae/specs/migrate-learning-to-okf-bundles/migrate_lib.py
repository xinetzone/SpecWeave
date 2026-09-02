# -*- coding: utf-8 -*-
"""learning → OKF bundles 迁移共享库（00/01/02 分类批次）。

职责：
- 解析源 md 的 YAML frontmatter
- 重写为 OKF v0.2 合规 frontmatter（type/title/description/tags/sources/generated/status/stale_after）
- 隐私清洗（个人路径 → 占位符）
- 生成目录 index.md（toctree）与束根 index.md/log.md 骨架
不执行 git 操作。
"""
from __future__ import annotations
import re
from pathlib import Path

REPO = Path(r"d:\spaces\SpecWeave")
LEARNING = REPO / "docs" / "knowledge" / "learning"
BUNDLES = REPO / "projects" / "awesome-okf-xs" / "doc" / "bundles"

MIGRATION_DATE = "2026-09-02"
GENERATED_BY = "process:learning-bundles-migration"
STALE_AFTER = "2027-09-02"

# 不迁入的文件名（隐私元数据 / 导航元数据）
SKIP_NAMES = {
    "readme.md", "log.md", "seven-concepts-report.md",
    "02-seven-concepts-report.md", "03-seven-concepts-report.md",
}
SKIP_PREFIXES = ("retrospective", "verification-report")
SKIP_SUFFIXES = (".gitkeep", ".pyc")


def should_skip(p: Path) -> bool:
    name = p.name.lower()
    if name in SKIP_NAMES:
        return True
    if any(name.startswith(pre) for pre in SKIP_PREFIXES):
        return True
    if p.suffix.lower() in SKIP_SUFFIXES:
        return True
    return False


def split_frontmatter(text: str) -> tuple[str, str]:
    """返回 (frontmatter_yaml, body)。无 frontmatter 时返回 ("", text)。"""
    if not text.startswith("---"):
        return "", text
    lines = text.splitlines(keepends=True)
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "".join(lines[1:i]), "".join(lines[i + 1:])
    return "", text


def parse_fm(fm_text: str) -> dict:
    """宽松解析 YAML frontmatter 为 dict（仅取顶层 key: value 与简单列表）。"""
    import yaml
    try:
        data = yaml.safe_load(fm_text)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def clean_body(body: str) -> str:
    """隐私清洗：个人路径 → 占位符。"""
    # 个人工作区路径
    body = re.sub(r"[dD]:\\AI\\?", "<local-workspace>", body)
    body = re.sub(r"[dD]:/AI/?", "<local-workspace>", body)
    # 用户主目录
    body = re.sub(r"C:\\Users\\xinzo", "<user-home>", body)
    return body


def yaml_str(v) -> str:
    """把值渲染为 YAML 安全字符串（含冒号/引号时加引号）。"""
    if v is None:
        return '""'
    s = str(v)
    if any(c in s for c in [":", "#", "{", "}", "[", "]", ",", "&", "*", "!", "|", ">", "'", '"', "%", "@", "`"]) or s.startswith(" ") or s.endswith(" "):
        s = s.replace('"', '\\"')
        return f'"{s}"'
    return s


def build_frontmatter(src_fm: dict, rel_source: str, doc_type: str = "Concept") -> str:
    """由源 frontmatter 构造 OKF v0.2 frontmatter 文本。"""
    title = src_fm.get("title") or ""
    desc = src_fm.get("summary") or src_fm.get("description") or title
    tags = src_fm.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    origin = src_fm.get("source") or ""

    lines = ["---"]
    lines.append(f"type: {doc_type}")
    if title:
        lines.append(f"title: {yaml_str(title)}")
    if desc:
        lines.append(f"description: {yaml_str(desc)}")
    if tags:
        tag_items = ", ".join(yaml_str(t) for t in tags[:12])
        lines.append(f"tags: [{tag_items}]")
    lines.append(f"generated: {{ by: {GENERATED_BY}, at: {MIGRATION_DATE}T00:00:00Z }}")
    lines.append("status: draft")
    lines.append(f"stale_after: {STALE_AFTER}")
    lines.append("sources:")
    lines.append("  - id: learning-source")
    lines.append(f"    resource: {yaml_str('SpecWeave docs/knowledge/learning/' + rel_source)}")
    if origin:
        lines.append(f"    title: {yaml_str(origin)}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def transform_md(src: Path, rel_source: str, doc_type: str = "Concept") -> str:
    """读取源 md，重写 frontmatter + 清洗正文，返回新内容。"""
    text = src.read_text(encoding="utf-8")
    fm_text, body = split_frontmatter(text)
    src_fm = parse_fm(fm_text)
    body = clean_body(body)
    new_fm = build_frontmatter(src_fm, rel_source, doc_type)
    return new_fm + body


def write_doc(dst: Path, content: str):
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(content, encoding="utf-8")


def list_content_files(d: Path) -> list[Path]:
    """目录内直接的内容 md（排除 index/README/隐私文件），按名排序。"""
    out = []
    for f in sorted(d.iterdir()):
        if f.is_file() and f.suffix == ".md" and f.name != "index.md" and not should_skip(f):
            out.append(f)
    return out


def list_subdirs_with_index(d: Path) -> list[Path]:
    out = []
    for f in sorted(d.iterdir()):
        if f.is_dir() and not f.name.startswith(".") and (f / "index.md").exists():
            out.append(f)
    return out


def gen_dir_index(d: Path, title: str, intro: str = "") -> str:
    """为目录生成 index.md（列表 + toctree），无 okf_version。"""
    files = list_content_files(d)
    subs = list_subdirs_with_index(d)
    lines = [f"# {title}", ""]
    if intro:
        lines += [intro, ""]
    entries = []
    if subs:
        lines.append("## 子目录")
        lines.append("")
        for s in subs:
            lines.append(f"* [{s.name}/]({s.name}/index.md)")
            entries.append(f"{s.name}/index")
        lines.append("")
    if files:
        lines.append("## 文档")
        lines.append("")
        for f in files:
            lines.append(f"* [{f.stem}]({f.name})")
            entries.append(f.stem)
        lines.append("")
    lines.append("```{toctree}")
    lines.append(":maxdepth: 2")
    lines.append("")
    lines.extend(entries)
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def gen_bundle_root_index(title: str, description: str, overview: str,
                          nav_sections: list[tuple[str, str, str]],
                          toctree_entries: list[str]) -> str:
    """生成束根 index.md（okf_version + 导航 + hidden toctree）。

    nav_sections: [(label, relpath, desc)]
    """
    lines = [
        "---",
        'okf_version: "0.2"',
        "---",
        "",
        f"# {title}",
        "",
        description,
        "",
    ]
    if overview:
        lines += [overview, ""]
    for label, relpath, desc in nav_sections:
        lines.append(f"* [{label}]({relpath}) — {desc}")
    lines.append("")
    lines.append("```{toctree}")
    lines.append(":hidden:")
    lines.append(":maxdepth: 7")
    lines.append("")
    lines.extend(toctree_entries)
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def gen_log_md(merge_lines: list[str] | None = None) -> str:
    lines = [
        "# 更新日志",
        "",
        f"## {MIGRATION_DATE}",
        "",
        "**Migration**: 从 SpecWeave docs/knowledge/learning/ 迁入 awesome-okf-xs（00/01/02 分类批次）",
        "",
        "* 全部章节文档重写 frontmatter 为 OKF v0.2（type/title/description/tags/sources/generated/status/stale_after）",
        "* 隐私清洗：个人工作区路径替换为占位符",
        "* 舍弃：源侧 README.md/index.md（导航元数据）、log.md（工作流元数据）、.gitkeep",
    ]
    if merge_lines:
        lines.append("")
        lines.extend(merge_lines)
    lines.append("")
    return "\n".join(lines)
