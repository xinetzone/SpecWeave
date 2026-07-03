"""MCP Domain 围栏块解析器 - 支持冒号围栏和反引号围栏。"""

from __future__ import annotations

from typing import Any

from .constants import (
    _DIRECTIVE_RE,
    _COLON_OPEN_RE,
    _COLON_CLOSE_RE,
    _BACKTICK_OPEN_RE,
    _BACKTICK_CLOSE_RE,
)
from .parser_helpers import _parse_options


def parse_fence_blocks(text: str) -> list[dict[str, Any]]:
    """递归解析文本中的 ::: 和 ``` 围栏块，返回 directive 列表。

    使用栈跟踪嵌套围栏：
    - 冒号围栏：内层必须使用更多冒号（MyST 规范），长度匹配开闭
    - 反引号围栏：通过深度计数嵌套（同 markdown-it 行为）
    """
    lines = text.split("\n")

    def parse_colon(start: int, min_fence_len: int) -> tuple[list[dict[str, Any]], int]:
        """解析冒号围栏块。"""
        results: list[dict[str, Any]] = []
        i = start
        while i < len(lines):
            line = lines[i]
            cm = _COLON_OPEN_RE.match(line)
            ccm = _COLON_CLOSE_RE.match(line)

            if cm and not ccm:
                fence_len = len(cm.group(1))
                if fence_len < min_fence_len:
                    i += 1
                    continue
                info = (cm.group(2) + " " + cm.group(3)).strip()
                dm = _DIRECTIVE_RE.match(info)
                if dm:
                    directive_name = dm.group(1).lower()
                    directive_args = dm.group(2).strip()
                    i += 1
                    inner_start = i
                    children, i = parse_colon(i, fence_len + 1)
                    inner_lines = lines[inner_start:i - 1] if i - 1 >= inner_start else []
                    options, content_lines = _parse_options(inner_lines)
                    content = "\n".join(content_lines).strip()
                    results.append({
                        "name": directive_name,
                        "args": directive_args,
                        "options": options,
                        "content": content,
                        "children": children,
                        "fence_type": "colon",
                    })
                    continue
            elif ccm:
                fence_len = len(ccm.group(1))
                if fence_len >= min_fence_len - 1 and min_fence_len > 3:
                    return results, i + 1
            i += 1
        return results, i

    def parse_backtick(start: int) -> tuple[list[dict[str, Any]], int]:
        """解析反引号围栏块，通过深度计数处理嵌套。

        与冒号围栏不同：反引号开闭都用 ``` ，通过深度计数器嵌套。
        遇到 ```{directive} 开标签时递归解析（递归调用会消费其对应的闭标签），
        遇到纯 ``` 闭标签时递减深度，depth==0 时返回。
        """
        children: list[dict[str, Any]] = []
        i = start
        depth = 1
        while i < len(lines):
            line = lines[i]
            is_close = bool(_BACKTICK_CLOSE_RE.match(line)) and not bool(_BACKTICK_OPEN_RE.match(line))
            is_directive_open = bool(_BACKTICK_OPEN_RE.match(line)) and bool(
                _DIRECTIVE_RE.match(
                    (_BACKTICK_OPEN_RE.match(line).group(2) + " " +
                     _BACKTICK_OPEN_RE.match(line).group(3)).strip()
                )
            ) if _BACKTICK_OPEN_RE.match(line) else False

            if is_close:
                depth -= 1
                if depth == 0:
                    return children, i + 1
                i += 1
            elif is_directive_open:
                bm = _BACKTICK_OPEN_RE.match(line)
                info = (bm.group(2) + " " + bm.group(3)).strip()
                dm = _DIRECTIVE_RE.match(info)
                directive_name = dm.group(1).lower()
                directive_args = dm.group(2).strip()
                i += 1
                inner_start = i
                grandkids, i = parse_backtick(i)
                inner_lines = lines[inner_start:i - 1] if i - 1 >= inner_start else []
                opts, clines = _parse_options(inner_lines)
                c = "\n".join(clines).strip()
                children.append({
                    "name": directive_name,
                    "args": directive_args,
                    "options": opts,
                    "content": c,
                    "children": grandkids,
                    "fence_type": "backtick",
                })
            else:
                i += 1
        return children, i

    def parse_mixed(start: int, min_colon_len: int) -> tuple[list[dict[str, Any]], int]:
        """顶层混合解析：同时识别冒号围栏和反引号围栏。"""
        results: list[dict[str, Any]] = []
        i = start
        while i < len(lines):
            line = lines[i]
            cm = _COLON_OPEN_RE.match(line)
            bm = _BACKTICK_OPEN_RE.match(line)
            ccm = _COLON_CLOSE_RE.match(line)

            if cm and not ccm:
                fence_len = len(cm.group(1))
                if fence_len >= min_colon_len:
                    info = (cm.group(2) + " " + cm.group(3)).strip()
                    dm = _DIRECTIVE_RE.match(info)
                    if dm:
                        directive_name = dm.group(1).lower()
                        directive_args = dm.group(2).strip()
                        i += 1
                        inner_start = i
                        children, i = parse_colon(i, fence_len + 1)
                        inner_lines = lines[inner_start:i - 1] if i - 1 >= inner_start else []
                        options, content_lines = _parse_options(inner_lines)
                        content = "\n".join(content_lines).strip()
                        results.append({
                            "name": directive_name,
                            "args": directive_args,
                            "options": options,
                            "content": content,
                            "children": children,
                            "fence_type": "colon",
                        })
                        continue
            elif bm:
                info = (bm.group(2) + " " + bm.group(3)).strip()
                dm = _DIRECTIVE_RE.match(info)
                if dm:
                    directive_name = dm.group(1).lower()
                    directive_args = dm.group(2).strip()
                    i += 1
                    inner_start = i
                    children, i = parse_backtick(i)
                    inner_lines = lines[inner_start:i - 1] if i - 1 >= inner_start else []
                    options, content_lines = _parse_options(inner_lines)
                    content = "\n".join(content_lines).strip()
                    results.append({
                        "name": directive_name,
                        "args": directive_args,
                        "options": options,
                        "content": content,
                        "children": children,
                        "fence_type": "backtick",
                    })
                    continue
            elif ccm and min_colon_len > 3:
                fence_len = len(ccm.group(1))
                if fence_len >= min_colon_len - 1:
                    return results, i + 1
            i += 1
        return results, i

    parsed, _ = parse_mixed(0, 3)
    return parsed
