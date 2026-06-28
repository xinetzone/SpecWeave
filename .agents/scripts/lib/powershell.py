"""PowerShell 脚本文件编码工具。

Windows PowerShell 5.x（Windows 10/11 默认版本）对 .ps1 脚本文件有两个隐含编码要求：
1. 含非ASCII字符的脚本需使用 UTF-8 with BOM 编码
2. 换行符需使用 CRLF（\\r\\n）

违反任一条件可能导致语法解析错误（如"字符串缺少终止符"、"意外的}"）。

本模块提供:
- write_ps1_script(): 以正确编码（UTF-8 BOM + CRLF）写入.ps1文件
- verify_ps1_encoding(): 验证已有.ps1文件编码是否合规
- fix_ps1_encoding(): 修复编码不合规的.ps1文件

用法:
    from lib.powershell import write_ps1_script, verify_ps1_encoding

    # 写入新的.ps1文件（自动BOM+CRLF）
    write_ps1_script(Path("scripts/myscript.ps1"), "$OutputEncoding = [System.Text.Encoding]::UTF8\\nWrite-Host 'Hello'")

    # 验证已有文件
    is_ok, issues = verify_ps1_encoding(Path("scripts/ci-check.ps1"))
    if not is_ok:
        print(f"编码问题: {issues}")
"""

from __future__ import annotations

from pathlib import Path

UTF8_BOM = b"\xef\xbb\xbf"


def write_ps1_script(
    file_path: str | Path,
    content: str,
    *,
    add_bom: bool = True,
    newline: str = "\r\n",
) -> Path:
    """以 Windows PowerShell 兼容编码写入 .ps1 脚本文件。

    将内容统一转换为 CRLF 换行，使用 UTF-8 with BOM 编码写入，
    确保在 PowerShell 5.x 和 7.x 下均能正确解析。

    Args:
        file_path: 目标文件路径。
        content: 脚本内容（换行符可为LF或CRLF，会自动统一）。
        add_bom: 是否写入UTF-8 BOM（默认True，兼容PS 5.x）。
        newline: 目标换行符（默认CRLF）。

    Returns:
        写入的文件路径。
    """
    path = Path(file_path)
    normalized = content.replace("\r\n", "\n").replace("\r", "\n").replace("\n", newline)
    if not normalized.endswith(newline):
        normalized += newline
    data = normalized.encode("utf-8-sig" if add_bom else "utf-8")
    path.write_bytes(data)
    return path


def verify_ps1_encoding(file_path: str | Path) -> tuple[bool, list[str]]:
    """验证 .ps1 文件编码是否符合 Windows PowerShell 5.x 要求。

    Args:
        file_path: .ps1 文件路径。

    Returns:
        (is_compliant, issues列表)
        - is_compliant: True表示编码合规
        - issues: 不合规时的问题描述列表
    """
    path = Path(file_path)
    issues: list[str] = []

    try:
        raw = path.read_bytes()
    except OSError as e:
        return False, [f"无法读取文件: {e}"]

    has_bom = raw.startswith(UTF8_BOM)
    if not has_bom:
        issues.append("缺少UTF-8 BOM（PS 5.x含中文时可能解析错误）")

    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        issues.append("非UTF-8编码（含无法解码的字节）")
        return False, issues

    if "\r\n" not in text and "\n" in text:
        issues.append("使用LF换行（PS 5.x可能导致花括号匹配错误）")

    has_crlf_consistency = True
    lines = text.split("\n")
    for i, line in enumerate(lines[:-1], start=1):
        if not line.endswith("\r"):
            if "\r" in line:
                issues.append(f"第{i}行: 换行符不一致（混合CR）")
                has_crlf_consistency = False
                break

    return len(issues) == 0, issues


def fix_ps1_encoding(file_path: str | Path) -> tuple[bool, list[str]]:
    """修复 .ps1 文件编码问题（添加BOM、统一CRLF换行）。

    Args:
        file_path: .ps1 文件路径。

    Returns:
        (was_fixed, changes列表)
    """
    path = Path(file_path)
    changes: list[str] = []

    try:
        raw = path.read_bytes()
    except OSError as e:
        return False, [f"无法读取文件: {e}"]

    if raw.startswith(UTF8_BOM):
        text = raw[3:].decode("utf-8")
    else:
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = raw.decode("gbk")
                changes.append("从GBK转码为UTF-8")
            except UnicodeDecodeError:
                return False, ["无法识别文件编码（非UTF-8/GBK）"]

    needs_bom = not raw.startswith(UTF8_BOM)
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    needs_crlf = "\r\n" not in text[:100] if text else False
    crlf_lines = normalized.count("\n")
    actual_crlf = text.count("\r\n")
    needs_crlf = actual_crlf < crlf_lines

    if not needs_bom and not needs_crlf:
        return False, ["文件编码已合规，无需修复"]

    content_crlf = normalized.replace("\n", "\r\n")
    if not content_crlf.endswith("\r\n"):
        content_crlf += "\r\n"

    data = content_crlf.encode("utf-8-sig")
    path.write_bytes(data)

    if needs_bom:
        changes.append("添加UTF-8 BOM")
    if needs_crlf:
        changes.append("统一换行符为CRLF")

    return True, changes
