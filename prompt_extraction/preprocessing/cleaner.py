"""文本清洗模块

提供文本清洗功能，包括空白规范化、格式标记去除、
Markdown 结构提取、元数据识别等。
"""

import re
from typing import Any


def normalize_whitespace(text: str) -> str:
    """将连续空白（空格、制表符、换行）规范化为单个空格，去除首尾空白。

    Args:
        text: 原始文本

    Returns:
        规范化空白后的文本
    """
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def strip_markup(text: str) -> str:
    """去除 Markdown 和 HTML 格式标记，保留纯文本内容。

    去除以下标记，但保留其文本内容：
    - **bold**、*italic*、~~strikethrough~~
    - `code`、```code blocks```
    - <html tags>
    - [link](url)、![image](url)
    - 标题标记 #、列表标记 -/*/+、引用标记 >

    Args:
        text: 原始文本

    Returns:
        去除格式标记后的纯文本
    """
    if not text:
        return ""

    result = text

    # 去除 HTML 标签，保留内部文本
    result = re.sub(r"<[^>]+>", "", result)

    # 去除图片语法 ![alt](url)
    result = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", result)

    # 去除链接语法 [text](url)，保留文本
    result = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", result)

    # 去除粗体 **text** 或 __text__
    result = re.sub(r"\*\*([^*]+)\*\*", r"\1", result)
    result = re.sub(r"__([^_]+)__", r"\1", result)

    # 去除斜体 *text* 或 _text_（需注意不匹配粗体残余）
    result = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", result)
    result = re.sub(r"(?<!_)_([^_]+)_(?!_)", r"\1", result)

    # 去除删除线 ~~text~~
    result = re.sub(r"~~([^~]+)~~", r"\1", result)

    # 去除代码块 ```text```（必须在行内代码之前处理，避免行内代码正则误匹配）
    result = re.sub(r"```[\s\S]*?```", "", result)

    # 去除行内代码 `text`
    result = re.sub(r"`([^`]+)`", r"\1", result)

    # 去除标题标记 #，保留标题文本
    result = re.sub(r"^#{1,6}\s+", "", result, flags=re.MULTILINE)

    # 去除引用标记 >
    result = re.sub(r"^>\s?", "", result, flags=re.MULTILINE)

    # 去除无序列表标记 -、*、+
    result = re.sub(r"^[\s]*[-*+]\s+", "", result, flags=re.MULTILINE)

    # 去除有序列表标记 1. 2. 等
    result = re.sub(r"^\s*\d+\.\s+", "", result, flags=re.MULTILINE)

    # 去除水平分割线 ---、***、___
    result = re.sub(r"^[-*_]{3,}\s*$", "", result, flags=re.MULTILINE)

    return result.strip()


def extract_markdown_structure(text: str) -> dict[str, list[Any]]:
    """保留 Markdown 语义结构信息。

    提取标题、列表项和代码块的结构化信息。

    Args:
        text: 原始 Markdown 文本

    Returns:
        包含 headings、list_items、code_blocks 的字典
    """
    if not text:
        return {"headings": [], "list_items": [], "code_blocks": []}

    structure: dict[str, list[Any]] = {
        "headings": [],
        "list_items": [],
        "code_blocks": [],
    }

    # 提取标题（# 至 ######）
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    for match in heading_pattern.finditer(text):
        level = len(match.group(1))
        heading_text = match.group(2).strip()
        structure["headings"].append({"level": level, "text": heading_text})

    # 提取无序列表项（-、*、+）
    list_pattern = re.compile(r"^\s*[-*+]\s+(.+)$", re.MULTILINE)
    for match in list_pattern.finditer(text):
        structure["list_items"].append(match.group(1).strip())

    # 提取有序列表项（1.、2. 等）
    ordered_list_pattern = re.compile(r"^\s*\d+\.\s+(.+)$", re.MULTILINE)
    for match in ordered_list_pattern.finditer(text):
        structure["list_items"].append(match.group(1).strip())

    # 提取代码块（```...```）
    code_block_pattern = re.compile(r"```(\w*)\n([\s\S]*?)```")
    for match in code_block_pattern.finditer(text):
        code_content = match.group(2).strip()
        structure["code_blocks"].append(code_content)

    return structure


def identify_metadata(text: str) -> dict[str, Any]:
    """识别并标记 URL、email、代码块等非核心内容。

    Args:
        text: 原始文本

    Returns:
        包含 urls、emails、code_blocks、core_text 的字典
    """
    if not text:
        return {"urls": [], "emails": [], "code_blocks": [], "core_text": ""}

    # 识别 URL
    url_pattern = re.compile(r"https?://[^\s<>\"']+")
    urls = url_pattern.findall(text)

    # 识别 email 地址
    email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    emails = email_pattern.findall(text)

    # 识别代码块
    code_block_pattern = re.compile(r"```[\s\S]*?```")
    code_blocks = [cb.strip("`").strip() for cb in code_block_pattern.findall(text)]

    # 生成 core_text：去除 URL、email、代码块后的文本
    core_text = text
    # 按长度降序替换，避免短 URL 在长 URL 中先被替换导致问题
    for url in sorted(urls, key=len, reverse=True):
        core_text = core_text.replace(url, "")
    for email in sorted(emails, key=len, reverse=True):
        core_text = core_text.replace(email, "")
    for cb in code_block_pattern.findall(text):
        core_text = core_text.replace(cb, "")

    # 规范化 core_text 的空白
    core_text = normalize_whitespace(core_text)

    return {
        "urls": urls,
        "emails": emails,
        "code_blocks": code_blocks,
        "core_text": core_text,
    }


def clean_text(text: str) -> tuple[str, dict[str, list[Any]], dict[str, Any]]:
    """文本清洗统一入口。

    对输入文本依次执行空白规范化、Markdown 结构提取、
    元数据识别，返回清洗后的文本和结构化信息。

    Args:
        text: 原始文本

    Returns:
        (清洗后的文本, Markdown 结构信息, 元数据信息)
    """
    if not text:
        return ("", {"headings": [], "list_items": [], "code_blocks": []}, {"urls": [], "emails": [], "code_blocks": [], "core_text": ""})

    # 提取 Markdown 结构信息（在清洗前提取，保证结构完整）
    markdown_structure = extract_markdown_structure(text)

    # 识别元数据（在清洗前提取，保证 URL/email 完整）
    metadata = identify_metadata(text)

    # 清洗文本：去除格式标记并规范化空白
    cleaned = strip_markup(text)
    cleaned = normalize_whitespace(cleaned)

    return (cleaned, markdown_structure, metadata)