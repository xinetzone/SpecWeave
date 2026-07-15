"""docs/knowledge/scripts/ 知识库脚本常量"""

import os
from pathlib import Path

# ── 路径常量 ──────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
KNOWLEDGE_DIR = SCRIPT_DIR.parent
DOCS_DIR = KNOWLEDGE_DIR.parent
OUTPUT_FILE = KNOWLEDGE_DIR / "README.md"
CATEGORY_INDEX_FILE = KNOWLEDGE_DIR / "category-index.md"
TAG_INDEX_DIR = KNOWLEDGE_DIR / "tags"

# ── 排除文件 ──────────────────────────────────────────────────
EXCLUDE_FILES = {"template.md", "readme.md", "category-index.md"}
GENERATED_DIRS = {"scripts", "tags"}

# ── 默认元数据 ────────────────────────────────────────────────
DEFAULT_META = {
    "title": "",
    "category": "unknown",
    "tags": [],
    "date": "",
    "status": "draft",
    "author": "",
    "summary": "",
}

# ── 必填字段清单 ──────────────────────────────────────────────
# 知识条目 frontmatter 必填字段，缺失时 generate_index.py 会输出 warning 日志
# 缺失字段会导致条目降级（unknown 分类、无标签、无最近更新记录）
REQUIRED_FIELDS = ["title", "category", "tags", "date", "status", "author", "summary"]

# ── 描述截断长度 ──────────────────────────────────────────────
DESC_TRUNCATE_LENGTH = 60
