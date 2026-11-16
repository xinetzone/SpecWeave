# 版本校验：相对导入共享库（depth=1）
from ..python310_version_check import enforce_python310

enforce_python310()

# docs-as-product 发现层：
# 扫描 docs/ 目录，解析 frontmatter、head 元数据、:orphan、toctree 引用、
# 标题层级与首段，构建 DocsTree。

import logging
import re
from contextlib import contextmanager
from pathlib import Path

from lib.frontmatter import split_frontmatter_and_content

from .constants import (
    DIATAXIS_DIR_ALIASES,
    DIATAXIS_TYPES,
    DIATAXIS_TYPE_FIELDS,
    DOC_SUFFIXES,
    EXCLUDED_DIRS,
    INDEX_FILE_STEMS,
    TYPE_UNCLASSIFIED,
)
from .models import DocNode, DocsTree

# MyST fenced toctree：```{toctree} ... ```
_MYST_TOCTREE_RE = re.compile(
    r"^[`~]{3,}\{toctree\}[^\n]*\n(.*?)^[`~]{3,}",
    re.MULTILINE | re.DOTALL,
)

# RST toctree：.. toctree:: 后随缩进块
_RST_TOCTREE_RE = re.compile(
    r"^\.\. toctree::[^\n]*\n((?:[ \t]+[^\n]*\n?|\n)*)",
    re.MULTILINE,
)

# `Title <entry>` 形式
_TITLE_ENTRY_RE = re.compile(r"^[^<>]+<([^<>]+)>$")

# ATX 标题
_ATX_HEADING_RE = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t#]*$")

# HTML meta 标签
_HTML_META_RE = re.compile(
    r"""<meta[^>]*\bname=["']([^"']+)["'][^>]*\bcontent=["']([^"']*)["']""",
    re.IGNORECASE,
)

# RST .. meta:: 指令内字段
_RST_META_RE = re.compile(
    r"^\.\. meta::\s*\n((?:[ \t]+:[^\n]*\n?)+)", re.MULTILINE
)

_ORPHAN_RE = re.compile(r"(?:^|\n)[ \t]*:orphan:[ \t]*(?:\n|$)")


def _infer_type_from_path(rel_parts: tuple[str, ...]) -> str:
    """按路径组件（目录名）推断 Diátaxis 类型。"""
    for part in rel_parts[:-1]:
        key = part.lower()
        if key in DIATAXIS_DIR_ALIASES:
            return DIATAXIS_DIR_ALIASES[key]
    return TYPE_UNCLASSIFIED


def _infer_type_from_metadata(metadata: dict[str, object]) -> str | None:
    """从 frontmatter 显式字段读取类型。"""
    for field_name in DIATAXIS_TYPE_FIELDS:
        value = metadata.get(field_name)
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in DIATAXIS_TYPES:
                return normalized
    return None


def _parse_toctree_entries(body: str) -> list[str]:
    """提取正文全部 toctree 块中的条目（已去除选项行与标题包裹）。"""
    entries: list[str] = []
    blocks: list[str] = [m.group(1) for m in _MYST_TOCTREE_RE.finditer(body)]
    blocks += [m.group(1) for m in _RST_TOCTREE_RE.finditer(body)]

    for block in blocks:
        for raw_line in block.splitlines():
            line = raw_line.strip()
            if not line or line.startswith(":") or line.startswith("#"):
                continue
            match = _TITLE_ENTRY_RE.match(line)
            if match:
                line = match.group(1).strip()
            entries.append(line)
    return entries


def _extract_head_meta(
    metadata: dict[str, object], body: str
) -> dict[str, str]:
    """汇总将进入页面 head 的元数据：frontmatter 标量字段 + HTML/RST meta。"""
    head: dict[str, str] = {}
    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool)):
            head[str(key)] = str(value)
    for match in _HTML_META_RE.finditer(body):
        head[match.group(1)] = match.group(2)
    for block in _RST_META_RE.finditer(body):
        for line in block.group(1).splitlines():
            line = line.strip()
            if line.startswith(":") and ":" in line[1:]:
                name, _, content = line[1:].partition(":")
                head[name.strip()] = content.strip()
    return head


def _first_heading(lines: list[str]) -> tuple[int, str] | None:
    """返回首个 ATX 标题的 (层级, 标题)。"""
    for line in lines:
        match = _ATX_HEADING_RE.match(line)
        if match:
            return len(match.group(1)), match.group(2)
    return None


def _analyze_headings(body: str) -> tuple[bool, str, int]:
    """分析 Markdown 标题：返回 (层级是否合规, 首个标题文本, H2 数量)。

    合规条件：首个标题为 H1；层级递进不跳跃（相邻标题差 ≤ 1）；无多个 H1。
    """
    lines = body.splitlines()
    first = _first_heading(lines)
    title = first[1] if first else ""
    levels = [
        len(m.group(1))
        for line in lines
        if (m := _ATX_HEADING_RE.match(line))
    ]
    h2_count = sum(1 for lv in levels if lv == 2)
    if not levels:
        return True, title, 0
    ok = levels[0] == 1 and levels.count(1) <= 1
    for prev, cur in zip(levels, levels[1:]):
        if cur > prev + 1:
            ok = False
    return ok, title, h2_count


def _has_lead_paragraph(body: str) -> bool:
    """判断首个标题之后是否紧接普通段落（首段摘要）。"""
    lines = body.splitlines()
    seen_title = False
    for line in lines:
        stripped = line.strip()
        if not seen_title:
            if _ATX_HEADING_RE.match(line):
                seen_title = True
            elif stripped:
                # 标题前即出现正文，按有首段处理
                return True
            continue
        if not stripped:
            continue
        if stripped.startswith(
            ("#", "```", "~~~", ":", "{", "..", "-", "*", ">", "|")
        ):
            return False
        return True
    return False


def _parse_node(path: Path, root: Path) -> DocNode:
    """读取并解析单个文档文件。"""
    rel_path = path.relative_to(root).as_posix()
    content = path.read_text(encoding="utf-8", errors="replace")
    metadata, body = split_frontmatter_and_content(content, base_dir=path.parent)
    metadata = metadata or {}

    orphan = bool(_ORPHAN_RE.search(body))
    entries = _parse_toctree_entries(body)
    heading_ok, heading_title, h2_count = _analyze_headings(body)
    has_lead = _has_lead_paragraph(body)

    title = heading_title
    if not title and isinstance(metadata.get("title"), str):
        title = str(metadata["title"])

    explicit = _infer_type_from_metadata(metadata)
    doc_type = explicit or _infer_type_from_path(
        tuple(Path(rel_path).parts)
    )

    head_meta = _extract_head_meta(metadata, body)

    return DocNode(
        path=path,
        rel_path=rel_path,
        title=title,
        doc_type=doc_type,
        metadata=metadata,
        head_meta=head_meta,
        orphan=bool(orphan),
        toctree_refs=entries,
        has_lead=has_lead,
        heading_ok=heading_ok,
        units=max(1, h2_count),
        is_index=path.stem in INDEX_FILE_STEMS,
    )


def _resolve_entry(entry: str, source: DocNode, tree: DocsTree) -> bool:
    """将 toctree 条目解析为树中节点并标记 in_toctree。"""
    candidates: list[str] = []
    source_dir = Path(source.rel_path).parent
    if str(source_dir) == ".":
        base = entry
    else:
        base = f"{source_dir.as_posix()}/{entry}"
    candidates.append(base)
    # 目录式条目：directory → directory/index
    candidates.append(f"{entry}/index")

    for cand in candidates:
        cand = cand.lstrip("./")
        for suffix in ("", ".md", ".rst", "/index.md", "/index.rst"):
            node = tree.get(cand + suffix)
            if node is not None:
                node.in_toctree = True
                return True
    return False


@contextmanager
def _quiet_frontmatter_warnings():
    """扫描期压低 lib.frontmatter 的逐条 warning，退出时恢复原级别。

    docs-as-product 只读检查不关心外部 TOML 缺失，但该告警对同进程的其它
    消费者（如 Skill 质量门对同一 logger 的断言）仍有意义——因此只能在
    扫描动作内临时抑制，不能在导入时改全局日志级。
    """
    logger = logging.getLogger("lib.frontmatter")
    previous_level = logger.level
    logger.setLevel(logging.ERROR)
    try:
        yield
    finally:
        logger.setLevel(previous_level)


def scan_docs(root: str | Path, config=None) -> DocsTree:
    """扫描文档目录并构建 DocsTree。

    Args:
        root: docs 目录路径（绝对或相对路径）。
        config: 可选 DocsProductConfig；当前仅 root 参与解析，保留以备扩展。

    Returns:
        构建完成（含 toctree 挂载标记）的 DocsTree。
    """
    root_path = Path(root).resolve()
    tree = DocsTree(root=root_path)

    if not root_path.exists():
        return tree

    with _quiet_frontmatter_warnings():
        for path in sorted(root_path.rglob("*")):
            if not path.is_file() or path.suffix not in DOC_SUFFIXES:
                continue
            if any(part in EXCLUDED_DIRS for part in path.relative_to(root_path).parts):
                continue
            tree.add(_parse_node(path, root_path))

    # 依据 toctree 条目标记挂载状态
    for node in tree.nodes:
        for entry in node.toctree_refs:
            _resolve_entry(entry, node, tree)

    return tree
