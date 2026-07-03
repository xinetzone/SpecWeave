"""MCP Domain 解析辅助函数。"""

from __future__ import annotations

from .constants import _OPTION_RE


def _parse_options(lines: list[str]) -> tuple[dict[str, str], list[str]]:
    """从行列表中解析 :key: value 选项，返回 (选项dict, 剩余内容行)。"""
    options: dict[str, str] = {}
    remaining: list[str] = []
    for line in lines:
        m = _OPTION_RE.match(line.strip())
        if m:
            key = m.group(1).strip().lower().replace(" ", "-")
            optional = bool(m.group(2))
            val = m.group(3).strip()
            if optional:
                options["required"] = "false"
            options[key] = val
        else:
            remaining.append(line)
    return options, remaining


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """提取 YAML frontmatter（简易实现，不依赖 PyYAML）。

    返回 (metadata_dict, remaining_text)。仅支持简单的 key: value 标量。
    """
    meta: dict[str, str] = {}
    if not text.startswith("---\n"):
        return meta, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return meta, text
    fm_text = text[4:end]
    for line in fm_text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip().lower()
            val = val.strip().strip('"').strip("'")
            if val:
                meta[key] = val
    return meta, text[end + 5:]
