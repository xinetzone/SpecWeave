"""文本标准化模块

提供文本标准化功能，包括全角字符转半角、标点符号规范化等。
"""

import re


def normalize_fullwidth(text: str) -> str:
    """全角字符转半角。

    将全角字母、数字、标点符号转换为对应的半角字符。

    Args:
        text: 原始文本

    Returns:
        全角转半角后的文本
    """
    if not text:
        return ""

    result = []
    for char in text:
        code = ord(char)
        # 全角空格（U+3000）→ 半角空格（U+0020）
        if code == 0x3000:
            result.append(" ")
        # 全角 ASCII 字符范围（U+FF01 至 U+FF5E）→ 半角（U+0021 至 U+007E）
        elif 0xFF01 <= code <= 0xFF5E:
            result.append(chr(code - 0xFEE0))
        # 全角数字 ０-９（U+FF10-U+FF19）已在上述范围内，此处保留作为补充
        else:
            result.append(char)

    return "".join(result)


def normalize_punctuation(text: str) -> str:
    """标点符号规范化。

    将中文标点符号统一为英文标点符号，统一引号格式。

    Args:
        text: 原始文本

    Returns:
        标点规范化后的文本
    """
    if not text:
        return ""

    # 标点符号映射表
    punctuation_map = {
        # 中文标点 → 英文标点
        "，": ",",
        "。": ".",
        "！": "!",
        "？": "?",
        "：": ":",
        "；": ";",
        # 中文引号 → 英文引号
        "\u201c": "\"",  # 左双引号 "
        "\u201d": "\"",  # 右双引号 "
        "\u2018": "'",   # 左单引号 '
        "\u2019": "'",   # 右单引号 '
        "\u300c": "\"",  # 左直角引号 「
        "\u300d": "\"",  # 右直角引号 」
        # 中文括号 → 英文括号
        "（": "(",
        "）": ")",
        "【": "[",
        "】": "]",
        "《": "<",
        "》": ">",
        # 省略号与破折号
        "……": "...",
        "——": "--",
        "–": "-",
        "—": "-",
        # 间隔号
        "·": ".",
        "‧": ".",
    }

    result = text
    for chinese_punct, english_punct in punctuation_map.items():
        result = result.replace(chinese_punct, english_punct)

    return result


def normalize_text(text: str) -> str:
    """文本标准化统一入口。

    依次执行全角字符转换和标点符号规范化。

    Args:
        text: 原始文本

    Returns:
        标准化后的文本
    """
    if not text:
        return ""

    result = normalize_fullwidth(text)
    result = normalize_punctuation(result)
    return result