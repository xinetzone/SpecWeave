"""forum-bot 内容处理工具。

提供AI发布声明的幂等插入逻辑。
"""

from __future__ import annotations

import unicodedata

from .constants import AI_NOTICE_KEYWORD, AI_NOTICE_TEXT
from .logger import logger


def ensure_ai_notice(content: str) -> tuple[str, bool]:
    """确保内容包含AI发布声明，幂等处理。

    返回 (处理后的内容, 是否新增了声明)。
    - 如果内容已包含AI_NOTICE_KEYWORD，原样返回，added=False
    - 否则在正确位置插入AI声明：
      - 若开头有emoji问候语行（🎉/👋/📢等emoji开头的短行+空行），在问候语之后插入
      - 否则在最开头插入
    """
    if AI_NOTICE_KEYWORD in content:
        logger.debug("  🤖 AI声明已存在（幂等检测通过），跳过添加")
        return content, False

    lines = content.split('\n', 2)
    is_greeting = False
    if len(lines) >= 3 and lines[0] and len(lines[0]) <= 100 and lines[1] == '':
        first_cp = ord(lines[0][0])
        cat = unicodedata.category(lines[0][0])
        is_emoji = (
            cat.startswith('So')
            or (0x1F300 <= first_cp <= 0x1FAFF)
            or (0x2600 <= first_cp <= 0x27BF)
            or (0x1F000 <= first_cp <= 0x1F2FF)
        )
        if is_emoji:
            is_greeting = True

    if is_greeting:
        first_line = lines[0]
        rest = content[len(first_line) + 2:]
        result = f"{first_line}\n\n{AI_NOTICE_TEXT}{rest}"
        logger.debug("  🤖 AI声明已插入到问候语之后")
    else:
        result = AI_NOTICE_TEXT + content
        logger.debug("  🤖 AI声明已插入到内容开头")

    logger.debug("  📏 添加声明后内容长度: %d 字符（原 %d 字符）", len(result), len(content))
    return result, True
