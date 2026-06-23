"""文件解析器：支持 CSV、JSON、TXT、Markdown 格式的提示词文件解析。"""

import csv
import json
import os
import re
import uuid
from typing import Any


def detect_format(file_path: str) -> str:
    """根据文件扩展名检测文件格式。

    Args:
        file_path: 文件路径。

    Returns:
        格式标识字符串："csv"、"json"、"txt" 或 "markdown"。

    Raises:
        ValueError: 文件扩展名不在支持列表中时抛出。
    """
    ext = os.path.splitext(file_path)[1].lower()
    format_map = {
        ".csv": "csv",
        ".json": "json",
        ".txt": "txt",
        ".md": "markdown",
        ".markdown": "markdown",
    }
    if ext not in format_map:
        raise ValueError(f"不支持的文件格式：{ext}，支持的格式：{', '.join(format_map.keys())}")
    return format_map[ext]


def _detect_prompt_column(headers: list[str]) -> str:
    """从 CSV 表头中自动检测提示词列名。

    Args:
        headers: CSV 表头列表。

    Returns:
        匹配到的列名。若未找到匹配列，返回第一列。
    """
    keywords = ["prompt", "title", "content", "text", "提示词", "标题", "内容", "文本"]
    for header in headers:
        header_lower = header.strip().lower()
        for kw in keywords:
            if kw in header_lower:
                return header
    return headers[0]


def _detect_prompt_key(records: list[dict[str, Any]]) -> str:
    """从 JSON 对象数组中自动检测提示词字段名。

    Args:
        records: JSON 对象数组。

    Returns:
        匹配到的字段名。若未找到匹配字段，返回第一个字符串类型字段。
    """
    if not records:
        return "text"
    keywords = ["prompt", "title", "content", "text", "提示词", "标题", "内容", "文本"]
    sample = records[0]
    for key in sample:
        key_lower = key.lower()
        for kw in keywords:
            if kw in key_lower:
                return key
    # 回退：取第一个值为字符串类型的键
    for key, value in sample.items():
        if isinstance(value, str):
            return key
    return "text"


def _generate_id() -> str:
    """生成唯一标识符。"""
    return uuid.uuid4().hex[:12]


def parse_csv(file_path: str) -> list[dict]:
    """解析 CSV 文件，自动检测提示词列，返回结构化列表。

    Args:
        file_path: CSV 文件路径。

    Returns:
        [{"text": ..., "id": ...}, ...] 格式的列表。

    Raises:
        ValueError: 文件不存在、格式错误或内容为空时抛出。
    """
    if not os.path.isfile(file_path):
        raise ValueError(f"文件不存在：{file_path}")

    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ValueError("CSV 文件为空或格式无效")
            prompt_col = _detect_prompt_column(reader.fieldnames)
            results: list[dict] = []
            for row in reader:
                text = row.get(prompt_col, "").strip()
                if text:
                    row_id = row.get("id", "").strip() or _generate_id()
                    results.append({"text": text, "id": row_id})
    except UnicodeDecodeError:
        # 尝试其他编码
        with open(file_path, "r", encoding="gbk") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ValueError("CSV 文件为空或格式无效")
            prompt_col = _detect_prompt_column(reader.fieldnames)
            results = []
            for row in reader:
                text = row.get(prompt_col, "").strip()
                if text:
                    row_id = row.get("id", "").strip() or _generate_id()
                    results.append({"text": text, "id": row_id})

    if not results:
        raise ValueError("CSV 文件中未找到有效的提示词内容")
    return results


def parse_json(file_path: str) -> list[dict]:
    """解析 JSON 文件（对象数组格式），自动检测提示词字段。

    Args:
        file_path: JSON 文件路径。

    Returns:
        [{"text": ..., "id": ...}, ...] 格式的列表。

    Raises:
        ValueError: 文件不存在、格式错误或内容为空时抛出。
    """
    if not os.path.isfile(file_path):
        raise ValueError(f"文件不存在：{file_path}")

    with open(file_path, "r", encoding="utf-8-sig") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 解析失败：{e}")

    if not isinstance(data, list):
        raise ValueError("JSON 文件顶层必须是数组格式")

    if not data:
        raise ValueError("JSON 文件中未找到有效的提示词内容")

    prompt_key = _detect_prompt_key(data)
    results: list[dict] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        text = str(item.get(prompt_key, "")).strip()
        if text:
            item_id = str(item.get("id", "")).strip() or _generate_id()
            results.append({"text": text, "id": item_id})

    if not results:
        raise ValueError("JSON 文件中未找到有效的提示词内容")
    return results


def parse_txt(file_path: str) -> list[dict]:
    """按行解析 TXT 文件，每行一条提示词，跳过空行。

    Args:
        file_path: TXT 文件路径。

    Returns:
        [{"text": ..., "id": ...}, ...] 格式的列表。

    Raises:
        ValueError: 文件不存在或内容为空时抛出。
    """
    if not os.path.isfile(file_path):
        raise ValueError(f"文件不存在：{file_path}")

    results: list[dict] = []
    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            for line in f:
                text = line.strip()
                if text:
                    results.append({"text": text, "id": _generate_id()})
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="gbk") as f:
            for line in f:
                text = line.strip()
                if text:
                    results.append({"text": text, "id": _generate_id()})

    if not results:
        raise ValueError("TXT 文件中未找到有效的提示词内容")
    return results


def parse_markdown(file_path: str) -> list[dict]:
    """按 Markdown 标题层级拆分，每个一级/二级标题及其后续内容作为一个独立区块。

    解析逻辑：
    - 遇到一级标题（#）或二级标题（##）时，将之前累积的内容作为一个区块保存。
    - 标题行本身作为区块标题，后续内容作为区块正文。
    - 若无任何标题，整个文件内容作为一个区块返回。

    Args:
        file_path: Markdown 文件路径。

    Returns:
        [{"text": "标题 + 内容", "id": ...}, ...] 格式的列表。

    Raises:
        ValueError: 文件不存在或内容为空时抛出。
    """
    if not os.path.isfile(file_path):
        raise ValueError(f"文件不存在：{file_path}")

    try:
        with open(file_path, "r", encoding="utf-8-sig") as f:
            raw_content = f.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="gbk") as f:
            raw_content = f.read()

    content = raw_content.strip()
    if not content:
        raise ValueError("Markdown 文件中未找到有效的提示词内容")

    # 使用正则拆分区块：以一级或二级标题为分隔
    # 匹配行首的 # 或 ## 标题（不匹配 ### 及更深层级）
    pattern = r"^(#{1,2})\s+(.+)$"
    lines = content.split("\n")
    blocks: list[dict] = []
    current_title = ""
    current_body: list[str] = []

    for line in lines:
        match = re.match(pattern, line.strip())
        if match:
            level = len(match.group(1))  # 1 或 2
            title = match.group(2).strip()
            # 保存上一个区块
            if current_title or current_body:
                block_text = _build_block_text(current_title, current_body)
                if block_text.strip():
                    blocks.append({"text": block_text, "id": _generate_id()})
            current_title = title
            current_body = []
        else:
            current_body.append(line)

    # 保存最后一个区块
    if current_title or current_body:
        block_text = _build_block_text(current_title, current_body)
        if block_text.strip():
            blocks.append({"text": block_text, "id": _generate_id()})

    if not blocks:
        raise ValueError("Markdown 文件中未找到有效的提示词内容")
    return blocks


def _build_block_text(title: str, body_lines: list[str]) -> str:
    """将区块标题与正文拼接为完整文本。

    Args:
        title: 区块标题。
        body_lines: 正文行列表。

    Returns:
        拼接后的完整文本。
    """
    body = "\n".join(body_lines).strip()
    if title and body:
        return f"{title}\n{body}"
    elif title:
        return title
    else:
        return body


def parse_file(file_path: str) -> list[dict]:
    """统一解析入口，根据文件格式自动调用对应的解析器。

    Args:
        file_path: 文件路径。

    Returns:
        [{"text": ..., "id": ...}, ...] 格式的列表。

    Raises:
        ValueError: 文件不存在、格式不支持或内容为空时抛出。
    """
    fmt = detect_format(file_path)
    parsers = {
        "csv": parse_csv,
        "json": parse_json,
        "txt": parse_txt,
        "markdown": parse_markdown,
    }
    return parsers[fmt](file_path)