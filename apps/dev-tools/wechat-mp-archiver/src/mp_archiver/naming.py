"""跨平台安全文件名/目录名工具。

重点兼容 Windows 限制：非法字符 ``<>:"/\\|?*`` 与控制字符、
保留设备名（CON/PRN/AUX/NUL/COMx/LPTx）、首尾空格与点、路径段长度上限。
中文等 Unicode 字符原样保留（NFC 规范化）。
"""

import re
import unicodedata

_INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_WHITESPACE = re.compile(r"\s+")
_WINDOWS_RESERVED = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def safe_filename(
    name: str | None,
    default: str = "untitled",
    max_length: int = 120,
) -> str:
    """将任意标题转换为单文件系统路径段（不含目录分隔符）。

    - 非法字符替换为下划线；
    - 折叠空白、去除首尾空格与点（Windows 资源管理器不允许）；
    - 命中保留设备名时加下划线前缀；
    - 超长时截断主名并保留扩展名；
    - 空结果回退到 ``default``。
    """
    text = unicodedata.normalize("NFC", name or "")
    text = _INVALID_CHARS.sub("_", text)
    text = _WHITESPACE.sub(" ", text)
    # 首尾空格与点可能交替出现（如 "report . "），反复剥离至稳定
    while True:
        cleaned = text.strip().strip(".")
        if cleaned == text:
            break
        text = cleaned
    if not text:
        text = default

    stem, ext = text, ""
    head, dot, tail = text.rpartition(".")
    # 仅当扩展名"看起来像扩展名"（短、无空格）时才保留，否则整段视为主名
    if dot and tail and len(tail) <= 16 and " " not in tail:
        stem, ext = head, tail

    stem = stem.strip().strip(".") or default
    if stem.upper() in _WINDOWS_RESERVED:
        stem = f"_{stem}"

    if ext:
        budget = max_length - len(ext) - 1
        if budget < 1:
            ext = ext[: max(1, max_length - 1)]
            budget = max(1, max_length - len(ext) - 1)
        if len(stem) > budget:
            stem = stem[:budget].rstrip(" .") or default
        return f"{stem}.{ext}"

    if len(stem) > max_length:
        stem = stem[:max_length].rstrip(" .") or default
    return stem


def article_dir_name(publish_date: str | None, title: str | None, max_title: int = 80) -> str:
    """生成文章归档目录名：``YYYY-MM-DD_安全标题``；无日期时退化为 ``unknown-date_...``。"""
    date_part = publish_date[:10] if publish_date else "unknown-date"
    safe_title = safe_filename(title, default="untitled", max_length=max_title)
    return f"{date_part}_{safe_title}"
