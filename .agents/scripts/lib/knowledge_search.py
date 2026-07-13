"""知识库检索增强与查询验证模块。

提供全文检索、完整性感知过滤、查询输入验证、
注入防护、相关性评分等核心检索能力。

设计原则：
- 检索结果自动排除损坏条目，确保结果可信
- 查询输入严格验证，防止注入攻击
- 支持多维标签+全文关键词组合查询
- 返回结果包含完整性状态标记
"""

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
KNOWLEDGE_BASE = PROJECT_ROOT / "docs" / "knowledge"

# ---------------------------------------------------------------------------
# 查询安全
# ---------------------------------------------------------------------------

# 危险模式：SQL 注入、命令注入、路径遍历等
_DANGEROUS_PATTERNS = [
    re.compile(r"(?:;|\|)\s*(?:drop|delete|insert|update|select)\b", re.IGNORECASE),
    re.compile(r"(?:;|\|)\s*(?:rm|cat|curl|wget|nc|bash|sh|cmd|powershell)\b", re.IGNORECASE),
    re.compile(r"\.\./|\.\.\\"),  # 路径遍历
    re.compile(r"<script|<iframe|javascript:", re.IGNORECASE),  # XSS
    re.compile(r"\\x[0-9a-f]{2}", re.IGNORECASE),  # 十六进制编码注入
]

# 查询安全限制
MAX_QUERY_LENGTH = 500
MAX_KEYWORDS = 10


def sanitize_query(query: str) -> tuple[str, bool, str]:
    """清理和验证查询字符串。

    移除危险字符，检查注入模式，确保查询安全。

    Args:
        query: 原始查询字符串。

    Returns:
        (sanitized_query, is_safe, message) 元组。
    """
    if not query or not isinstance(query, str):
        return "", False, "查询不能为空"

    if len(query) > MAX_QUERY_LENGTH:
        return "", False, f"查询长度 {len(query)} 超过限制 {MAX_QUERY_LENGTH}"

    # 检查危险模式
    for pattern in _DANGEROUS_PATTERNS:
        if pattern.search(query):
            return "", False, f"查询包含潜在危险模式"

    # 清理：移除控制字符（保留常见标点）
    sanitized = ''.join(
        ch for ch in query
        if ord(ch) >= 32 or ch in '\n\r\t'
    )

    # 移除多余空白
    sanitized = ' '.join(sanitized.split())

    if not sanitized:
        return "", False, "清理后查询为空"

    return sanitized, True, ""


def extract_keywords(query: str) -> list[str]:
    """从查询字符串提取关键词。

    按空白分割，去除停用词和短词。

    Args:
        query: 清理后的查询字符串。

    Returns:
        关键词列表。
    """
    # 简单分词：按空白和中文标点分割
    raw = re.split(r'[\s,，。；;]+', query)
    keywords = []
    for w in raw:
        w = w.strip().lower()
        if len(w) >= 2:
            keywords.append(w)

    return keywords[:MAX_KEYWORDS]


# ---------------------------------------------------------------------------
# 完整性感知过滤
# ---------------------------------------------------------------------------

def filter_intact_entries(
    entries: list[dict],
    knowledge_base_dir: str | Path | None = None,
) -> tuple[list[dict], list[dict], str]:
    """过滤检索结果，分离完整和损坏条目。

    对每个条目进行完整性校验，自动排除损坏条目，
    确保返回给用户的结果都是可信的。

    Args:
        entries: 待过滤的条目列表（需包含 file 字段）。
        knowledge_base_dir: 知识库目录。

    Returns:
        (intact, damaged, message) 元组。
    """
    if knowledge_base_dir is None:
        knowledge_base_dir = KNOWLEDGE_BASE

    from .frontmatter import split_frontmatter_and_content
    from .knowledge_integrity import verify_integrity

    intact = []
    damaged = []

    for entry in entries:
        file_path = entry.get("absolute_path", "")
        if file_path:
            file_path = Path(file_path)
        else:
            file_path = Path(knowledge_base_dir) / entry.get("file", "")
        if not file_path.exists():
            damaged.append({**entry, "integrity_status": "missing", "integrity_message": "文件不存在"})
            continue

        try:
            raw = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            damaged.append({**entry, "integrity_status": "unreadable", "integrity_message": "无法读取文件"})
            continue

        metadata, content = split_frontmatter_and_content(raw, base_dir=file_path.parent)
        if metadata is None:
            metadata = {}
        content = content.lstrip('\n')

        valid, checksum, msg = verify_integrity(metadata, content)
        if valid:
            entry_copy = dict(entry)
            entry_copy["integrity_status"] = "intact"
            entry_copy["integrity_message"] = msg
            intact.append(entry_copy)
        else:
            damaged.append({**entry, "integrity_status": "damaged", "integrity_message": msg})

    return intact, damaged, (
        f"完整: {len(intact)}, 损坏: {len(damaged)}"
    )


# ---------------------------------------------------------------------------
# 全文检索
# ---------------------------------------------------------------------------

def search_fulltext(
    query: str,
    entries: list[dict],
    knowledge_base_dir: str | Path | None = None,
    *,
    max_results: int = 50,
    min_score: float = 0.0,
) -> list[dict]:
    """在知识条目中进行全文检索。

    对每个条目的正文内容进行关键词匹配，计算相关性评分。

    Args:
        query: 搜索查询字符串。
        entries: 待搜索的条目列表（需包含 file 字段）。
        knowledge_base_dir: 知识库目录。
        max_results: 最大返回结果数。
        min_score: 最低相关性评分阈值。

    Returns:
        按相关性降序排列的搜索结果列表，每个结果包含 score 字段。
    """
    if knowledge_base_dir is None:
        knowledge_base_dir = KNOWLEDGE_BASE

    sanitized, safe, err = sanitize_query(query)
    if not safe:
        return []

    keywords = extract_keywords(sanitized)
    if not keywords:
        return []

    results = []
    base = Path(knowledge_base_dir)

    for entry in entries:
        file_path = entry.get("absolute_path", "")
        if file_path:
            file_path = Path(file_path)
        else:
            file_path = base / entry.get("file", "")
        if not file_path.exists():
            continue

        try:
            raw = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        # 计算相关性评分
        score = _compute_relevance(raw, keywords, entry)

        if score >= min_score:
            results.append({
                **entry,
                "score": score,
                "matched_keywords": [
                    kw for kw in keywords
                    if kw.lower() in raw.lower()
                ],
            })

    # 按相关性降序排列
    results.sort(key=lambda r: r["score"], reverse=True)

    return results[:max_results]


def _compute_relevance(
    content: str,
    keywords: list[str],
    metadata: dict,
) -> float:
    """计算条目的相关性评分。

    评分因素：
    - 标题匹配：权重 3.0
    - 正文匹配：权重 1.0（每次出现）
    - 标签匹配：权重 2.0
    - 摘要匹配：权重 2.5

    Args:
        content: 条目完整内容。
        keywords: 搜索关键词列表。
        metadata: 条目元数据。

    Returns:
        相关性评分（0.0 表示不相关）。
    """
    if not keywords:
        return 0.0

    content_lower = content.lower()
    score = 0.0

    # 标题匹配
    title = str(metadata.get("title", "")).lower()
    for kw in keywords:
        if kw.lower() in title:
            score += 3.0

    # 正文匹配
    for kw in keywords:
        kw_lower = kw.lower()
        count = content_lower.count(kw_lower)
        if count > 0:
            score += 1.0 * min(count, 10)  # 上限防止单一关键词主导

    # 标签匹配
    tags = metadata.get("tags", [])
    if isinstance(tags, list):
        tag_str = ' '.join(str(t).lower() for t in tags)
        for kw in keywords:
            if kw.lower() in tag_str:
                score += 2.0

    # 摘要匹配
    summary = str(metadata.get("summary", "")).lower()
    if summary:
        for kw in keywords:
            if kw.lower() in summary:
                score += 2.5

    return round(score, 2)


# ---------------------------------------------------------------------------
# 综合检索
# ---------------------------------------------------------------------------

def _scan_knowledge_entries(
    base_dir: str | Path | None = None,
) -> list[dict]:
    """扫描知识库目录，提取所有条目的 frontmatter 元数据。

    Args:
        base_dir: 知识库目录，默认为 docs/knowledge/。

    Returns:
        知识条目元数据列表。
    """
    if base_dir is None:
        base_dir = KNOWLEDGE_BASE

    from .frontmatter import parse_frontmatter_unified

    base = Path(base_dir)
    entries = []
    for md_file in base.rglob("*.md"):
        if md_file.name == "README.md":
            continue
        if "templates" in md_file.parts:
            continue

        metadata = parse_frontmatter_unified(md_file)
        if metadata is None:
            metadata = {}

        rel_path = md_file.relative_to(base)
        entry = {
            "file": rel_path.as_posix(),
            "absolute_path": str(md_file),
            "title": metadata.get("title", md_file.stem),
            "category": metadata.get("category", ""),
            "tags": metadata.get("tags", []),
            "knowledge_type": metadata.get("knowledge_type", "factual"),
            "validation_status": metadata.get("validation_status", "draft"),
            "security_level": metadata.get("security_level", "public"),
            "reuse_count": metadata.get("reuse_count", "0"),
            "date": metadata.get("date", ""),
            "status": metadata.get("status", ""),
        }
        entries.append(entry)

    return entries


def search_knowledge(
    query: str = "",
    *,
    knowledge_type: str | None = None,
    validation_status: str | None = None,
    security_level: str | None = None,
    tags: list[str] | None = None,
    entries: list[dict] | None = None,
    knowledge_base_dir: str | Path | None = None,
    max_results: int = 50,
    exclude_damaged: bool = True,
) -> dict:
    """综合知识检索。

    支持多维标签筛选 + 全文关键词搜索 + 完整性过滤。

    Args:
        query: 全文搜索关键词（可选）。
        knowledge_type: 知识类型筛选。
        validation_status: 验证状态筛选。
        security_level: 安全级别筛选。
        tags: 标签筛选。
        entries: 预加载的条目列表，None 时自动扫描。
        knowledge_base_dir: 知识库目录。
        max_results: 最大返回结果数。
        exclude_damaged: 是否排除损坏条目。

    Returns:
        包含完整结果、统计信息、损坏条目的字典。
    """
    from .knowledge_classification import multi_filter, compute_classification_stats

    # 加载条目
    if entries is None:
        entries = _scan_knowledge_entries(knowledge_base_dir)

    if not entries:
        return {
            "total": 0,
            "filtered": 0,
            "results": [],
            "damaged": [],
            "stats": {"by_type": {}, "by_validation": {}, "by_security": {}},
            "query": query,
        }

    # 多维筛选
    filtered = multi_filter(
        entries,
        knowledge_type=knowledge_type,
        validation_status=validation_status,
        security_level=security_level,
        tags=tags,
    )

    # 全文搜索
    if query:
        sanitized, safe, _ = sanitize_query(query)
        if safe:
            filtered = search_fulltext(
                sanitized, filtered, knowledge_base_dir, max_results=max_results,
            )

    # 完整性过滤
    damaged = []
    if exclude_damaged:
        intact, damaged, _ = filter_intact_entries(filtered, knowledge_base_dir)
        filtered = intact

    # 统计
    stats = compute_classification_stats(filtered)

    return {
        "total": len(entries),
        "filtered": len(filtered),
        "results": filtered[:max_results],
        "damaged": damaged,
        "stats": stats,
        "query": query,
    }


# ---------------------------------------------------------------------------
# 快速检索入口
# ---------------------------------------------------------------------------

def search_by_type(
    knowledge_type: str,
    entries: list[dict] | None = None,
) -> list[dict]:
    """按知识类型快速检索。

    Args:
        knowledge_type: 知识类型。
        entries: 预加载的条目列表。

    Returns:
        匹配的条目列表。
    """
    result = search_knowledge(
        knowledge_type=knowledge_type,
        entries=entries,
        exclude_damaged=True,
    )
    return result["results"]


def search_by_tag(
    tags: list[str],
    entries: list[dict] | None = None,
) -> list[dict]:
    """按标签快速检索。

    Args:
        tags: 标签列表。
        entries: 预加载的条目列表。

    Returns:
        匹配的条目列表。
    """
    result = search_knowledge(
        tags=tags,
        entries=entries,
        exclude_damaged=True,
    )
    return result["results"]


def search_verified(
    entries: list[dict] | None = None,
) -> list[dict]:
    """检索已验证的知识条目。

    Args:
        entries: 预加载的条目列表。

    Returns:
        已验证的条目列表。
    """
    result = search_knowledge(
        validation_status="verified",
        entries=entries,
        exclude_damaged=True,
    )
    return result["results"]


def quick_search(
    query: str,
    entries: list[dict] | None = None,
    max_results: int = 20,
) -> list[dict]:
    """快速全文搜索。

    Args:
        query: 搜索关键词。
        entries: 预加载的条目列表。
        max_results: 最大返回结果数。

    Returns:
        搜索结果列表。
    """
    result = search_knowledge(
        query=query,
        entries=entries,
        max_results=max_results,
        exclude_damaged=True,
    )
    return result["results"]