"""docs/knowledge/scripts/ 知识库脚本常量"""

import os
from pathlib import Path

# ── 路径常量 ──────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
KNOWLEDGE_DIR = SCRIPT_DIR.parent
DOCS_DIR = KNOWLEDGE_DIR.parent
OUTPUT_FILE = KNOWLEDGE_DIR / "README.md"

# ── 排除文件 ──────────────────────────────────────────────────
EXCLUDE_FILES = {"template.md", "readme.md"}

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

# ── 描述截断长度 ──────────────────────────────────────────────
DESC_TRUNCATE_LENGTH = 60
