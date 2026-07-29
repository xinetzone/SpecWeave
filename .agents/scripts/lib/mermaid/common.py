"""Mermaid 检查公共工具模块。

包含所有检查器/修复器共享的正则表达式、工具函数和常量。
"""

import re
from typing import List, Tuple, Optional

MERMAID_FENCE_RE = re.compile(r"(```mermaid\s*\n)(.*?)(```)", re.DOTALL)
CHINESE_CHARS_RE = re.compile(r"[\u4e00-\u9fff]")
SPECIAL_CHARS = "@#≥≤+"
LIST_TRIGGER_RE = re.compile(r'^[-*+]\s|^\d+[.．、]\s')


def detect_diagram_type(block_text: str) -> str:
    """检测 Mermaid 代码块的图表类型。"""
    first_line = block_text.strip().split("\n")[0].strip()
    if not first_line:
        return "unknown"
    diagram_type = first_line.split()[0].lower()
    if diagram_type in ("flowchart", "graph"):
        return "flowchart"
    if diagram_type.startswith("statediagram"):
        return "stateDiagram"
    if diagram_type == "sequencediagram":
        return "sequenceDiagram"
    if diagram_type == "classdiagram":
        return "classDiagram"
    if diagram_type == "erdiagram":
        return "erDiagram"
    if diagram_type == "pie":
        return "pie"
    if diagram_type == "gantt":
        return "gantt"
    if diagram_type in ("timeline", "mindmap", "xychart-beta", "quadrantchart"):
        return diagram_type
    return "flowchart"


def text_needs_quotes(ntxt: str) -> bool:
    """判断文本是否需要引号包裹。"""
    if ntxt.startswith('"') and ntxt.endswith('"'):
        return False
    if ntxt.startswith("'") and ntxt.endswith("'"):
        return False
    return bool(CHINESE_CHARS_RE.search(ntxt) or any(c in ntxt for c in SPECIAL_CHARS) or " " in ntxt.strip())


def state_text_needs_quotes(ntxt: str) -> bool:
    """判断状态图文本是否需要引号包裹。"""
    if ntxt.startswith('"') and ntxt.endswith('"'):
        return False
    if ntxt.startswith("'") and ntxt.endswith("'"):
        return False
    if " " in ntxt.strip():
        return True
    dangerous = ":;{}|->"
    return any(c in ntxt for c in dangerous)


def has_list_trigger(text: str) -> bool:
    """检查文本是否以列表标记开头。"""
    stripped = text.strip().strip('"').strip("'")
    return bool(LIST_TRIGGER_RE.match(stripped))


def line_from_offset(content: str, offset: int) -> int:
    """根据偏移量计算行号。"""
    return content[:offset].count("\n") + 1


def strip_inline_comment(line: str) -> str:
    """移除行内 Mermaid 注释（%% 后的内容），返回代码部分。"""
    stripped = line.lstrip()
    if stripped.startswith("%%"):
        return ""
    if "%%" in line:
        return line.split("%%", 1)[0]
    return line


def check_empty_lines(block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
    """检查代码块中的空行问题。"""
    issues = []
    if "\n\n" in block_text or "\n \n" in block_text:
        issues.append((start_line, "error", "Mermaid 代码块内存在空行，可能导致解析中断"))
    return issues


def check_backslash_n(block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
    """检查代码块中的 \\n 换行符问题。"""
    issues = []
    for i, line in enumerate(block_text.split("\n")):
        code_part = strip_inline_comment(line)
        if not code_part.strip():
            continue
        j = 0
        while True:
            idx = code_part.find("\\n", j)
            if idx == -1:
                break
            issues.append((start_line + i, "error",
                          f'节点/标签文本中使用了 \\n 换行符，应使用 <br/> 而非 \\n'))
            j = idx + 2
    return issues


def fix_backslash_n(text: str) -> str:
    """修复代码块中的 \\n 换行符为 <br/>。"""
    lines = text.split("\n")
    result = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("%%"):
            result.append(line)
            continue
        if "%%" in line:
            code, comment = line.split("%%", 1)
            result.append(code.replace("\\n", "<br/>") + "%%" + comment)
        else:
            result.append(line.replace("\\n", "<br/>"))
    return "\n".join(result)


def fix_empty_lines(text: str) -> str:
    """修复代码块中的空行问题。"""
    return re.sub(r"\n[ \t]*\n+", "\n", text)


def check_list_trigger(text: str, line_offset: int, start_line: int,
                       context: str) -> Optional[Tuple[int, str, str]]:
    """检查文本是否触发列表解析警告。"""
    if has_list_trigger(text):
        return (start_line + line_offset, "warning",
                f'{context}文本「{text.strip()[:20]}」以列表标记开头，可能触发Markdown列表解析')
    return None


def strip_mindmap_shape(text: str) -> str:
    """剥离思维导图节点的形状包裹，返回纯文本。"""
    t = text.strip()
    if t.startswith("<!--") and t.endswith("-->"):
        return ""
    dual_delims = [
        (r'^\(\((.+)\)\)$', 1),
        (r'^\(\[(.+)\]\)$', 1),
        (r'^\[\[(.+)\]\]$', 1),
        (r'^>\((.+)\)$', 1),
    ]
    for pat, grp in dual_delims:
        m = re.match(pat, t)
        if m:
            return m.group(grp)
    single_delims = [
        (r'^\((.+)\)$', 1),
        (r'^\[(.+)\]$', 1),
        (r'^\{(.+)\}$', 1),
    ]
    id_dual = re.match(r'^([A-Za-z][A-Za-z0-9_]*)(\(\(|\(\[|\[\[|>\()(.+?)(\)\)|\)\]|\]\]|\))$', t)
    if id_dual:
        return id_dual.group(3)
    id_single = re.match(r'^([A-Za-z][A-Za-z0-9_]*)(\(|\[|\{)(.+?)(\)|\]|\})$', t)
    if id_single:
        return id_single.group(3)
    for pat, grp in single_delims:
        m = re.match(pat, t)
        if m:
            return m.group(grp)
    return t
