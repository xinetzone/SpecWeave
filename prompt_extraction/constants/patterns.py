"""提示词萃取系统 —— 正则模式常量

集中管理所有正则表达式模式，消除跨模块重复定义，
便于统一维护与测试。
"""

import re

# ============================================================================
# 评估器正则模式（evaluator.py）
# ============================================================================

# Markdown 标题检测（行首 1-6 个 # 后跟空白）
RE_HEADING = re.compile(r"^#{1,6}\s", re.MULTILINE)

# 段落分隔检测（空行分隔）
RE_PARAGRAPH_SPLIT = re.compile(r"\n\s*\n")

# 列表标记检测（无序列表 -、*、+ 或有序列表 1.）
RE_LIST_MARKER = re.compile(r"^[\-\*\+]\s|^\d+\.\s", re.MULTILINE)

# 数字检测（用于约束可验证性判断）
RE_DIGIT = re.compile(r"\d+")

# ============================================================================
# 提取器正则模式（extractor.py）
# ============================================================================

# 句子拆分（按中文和英文句末标点）
RE_SENTENCE_SPLIT = re.compile(r"(?<=[。！？.!?\n])")

# ============================================================================
# 解析器正则模式（parser.py）
# ============================================================================

# Markdown 区块标题（一级或二级标题）
RE_MARKDOWN_BLOCK = re.compile(r"^(#{1,2})\s+(.+)$")

# ============================================================================
# 清洗器正则模式（cleaner.py）
# ============================================================================

# 连续空白（用于规范化）
RE_WHITESPACE = re.compile(r"\s+")

# HTML 标签
RE_HTML_TAG = re.compile(r"<[^>]+>")

# 图片语法 ![alt](url)
RE_IMAGE = re.compile(r"!\[([^\]]*)\]\([^)]*\)")

# 链接语法 [text](url)
RE_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")

# 粗体 **text** 或 __text__
RE_BOLD_ASTERISK = re.compile(r"\*\*([^*]+)\*\*")
RE_BOLD_UNDERSCORE = re.compile(r"__([^_]+)__")

# 斜体 *text* 或 _text_（需避免匹配粗体）
RE_ITALIC_ASTERISK = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")
RE_ITALIC_UNDERSCORE = re.compile(r"(?<!_)_([^_]+)_(?!_)")

# 删除线 ~~text~~
RE_STRIKETHROUGH = re.compile(r"~~([^~]+)~~")

# 代码块 ```text```
RE_CODE_BLOCK = re.compile(r"```[\s\S]*?```")

# 行内代码 `text`
RE_INLINE_CODE = re.compile(r"`([^`]+)`")

# 标题标记（行首 #）
RE_HEADING_MARKER = re.compile(r"^#{1,6}\s+", re.MULTILINE)

# 引用标记（行首 >）
RE_BLOCKQUOTE = re.compile(r"^>\s?", re.MULTILINE)

# 无序列表标记（行首 -、*、+）
RE_UNORDERED_LIST = re.compile(r"^[\s]*[-*+]\s+", re.MULTILINE)

# 有序列表标记（行首 1. 2. 等）
RE_ORDERED_LIST = re.compile(r"^\s*\d+\.\s+", re.MULTILINE)

# 水平分割线（---、***、___）
RE_HR = re.compile(r"^[-*_]{3,}\s*$", re.MULTILINE)

# Markdown 结构提取
RE_MD_HEADING_EXTRACT = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
RE_MD_UNORDERED_ITEM = re.compile(r"^\s*[-*+]\s+(.+)$", re.MULTILINE)
RE_MD_ORDERED_ITEM = re.compile(r"^\s*\d+\.\s+(.+)$", re.MULTILINE)
RE_MD_CODE_BLOCK_EXTRACT = re.compile(r"```(\w*)\n([\s\S]*?)```")

# 元数据识别
RE_URL = re.compile(r"https?://[^\s<>\"']+")
RE_EMAIL = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
