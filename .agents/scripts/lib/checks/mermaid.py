"""Mermaid 语法安全检查。

支持的图表类型与检测规则：
- flowchart/graph：空行、节点引号、subgraph格式、边标签引号、列表触发
- stateDiagram-v2：空行、迁移标签引号（: 后）、状态描述引号、note文本引号、列表触发
- sequenceDiagram：空行、participant别名引号、消息文本引号
- pie：空行（标签自带引号）
- gantt：空行（title/section/任务名裸文本合法）
- mindmap：空行、节点文本列表触发、形状包裹节点引号
- timeline/xychart-beta/quadrantChart：空行检测
"""

import re
import sys
import difflib
from pathlib import Path

from constants import EXCLUDED_DIRS, ANSI_RED, ANSI_YELLOW, ANSI_GREEN, ANSI_RESET, ANSI_CYAN

_DEBUG = False
_DEBUG_CTX: dict = {}


def _set_debug(enabled: bool) -> None:
    global _DEBUG
    _DEBUG = enabled


def _debug_enter(file_rel: str, start_line: int, dia_type: str) -> None:
    _DEBUG_CTX["file"] = file_rel
    _DEBUG_CTX["line"] = start_line
    _DEBUG_CTX["type"] = dia_type


def _debug_log(stage: str, msg: str) -> None:
    if not _DEBUG:
        return
    f = _DEBUG_CTX.get("file", "?")
    sl = _DEBUG_CTX.get("line", 0)
    dt = _DEBUG_CTX.get("type", "?")
    print(f"  [DEBUG:{dt}] {f}:L{sl} [{stage}] {msg}", file=sys.stderr)

MERMAID_FENCE_RE = re.compile(r"(```mermaid\s*\n)(.*?)(```)", re.DOTALL)
CHINESE_CHARS_RE = re.compile(r"[\u4e00-\u9fff]")
SPECIAL_CHARS = "@#≥≤+"
LIST_TRIGGER_RE = re.compile(r'^[-*+]\s|^\d+[.．、]\s')


def _detect_diagram_type(block_text: str) -> str:
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
    if diagram_type == "pie":
        return "pie"
    if diagram_type == "gantt":
        return "gantt"
    if diagram_type in ("timeline", "mindmap", "xychart-beta", "quadrantchart"):
        return diagram_type
    return "flowchart"


def _text_needs_quotes(ntxt: str) -> bool:
    if ntxt.startswith('"') and ntxt.endswith('"'):
        return False
    if ntxt.startswith("'") and ntxt.endswith("'"):
        return False
    return bool(CHINESE_CHARS_RE.search(ntxt) or any(c in ntxt for c in SPECIAL_CHARS) or " " in ntxt.strip())


def _has_list_trigger(text: str) -> bool:
    stripped = text.strip().strip('"').strip("'")
    return bool(LIST_TRIGGER_RE.match(stripped))


def _state_text_needs_quotes(ntxt: str) -> bool:
    if ntxt.startswith('"') and ntxt.endswith('"'):
        return False
    if ntxt.startswith("'") and ntxt.endswith("'"):
        return False
    if " " in ntxt.strip():
        return True
    dangerous = ":;{}|->"
    return any(c in ntxt for c in dangerous)


def _find_md_files(root_dir: Path, exclude_dirs: set[str]) -> list[Path]:
    files = []
    for md in root_dir.rglob("*.md"):
        parts = set(md.parts)
        if EXCLUDED_DIRS & parts:
            continue
        try:
            rel = md.relative_to(root_dir).as_posix()
        except ValueError:
            rel = str(md)
        if any(rel.startswith(excl.replace("\\", "/")) for excl in exclude_dirs):
            continue
        files.append(md)
    return files


def _line_from_offset(content: str, offset: int) -> int:
    return content[:offset].count("\n") + 1


def _check_empty_lines(block_text: str, start_line: int) -> list[tuple[int, str, str]]:
    issues = []
    if "\n\n" in block_text or "\n \n" in block_text:
        issues.append((start_line, "error", "Mermaid 代码块内存在空行，可能导致解析中断"))
    return issues


def _check_backslash_n(block_text: str, start_line: int) -> list[tuple[int, str, str]]:
    issues = []
    for i, line in enumerate(block_text.split("\n")):
        code_part = _strip_inline_comment(line)
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


def _fix_backslash_n(text: str) -> str:
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


def _strip_inline_comment(line: str) -> str:
    """移除行内 Mermaid 注释（%% 后的内容），返回代码部分。纯注释行返回空字符串。"""
    stripped = line.lstrip()
    if stripped.startswith("%%"):
        return ""
    if "%%" in line:
        return line.split("%%", 1)[0]
    return line


def _check_list_trigger(text: str, line_offset: int, start_line: int,
                        context: str) -> tuple[int, str, str] | None:
    if _has_list_trigger(text):
        return (start_line + line_offset, "warning",
                f'{context}文本「{text.strip()[:20]}」以列表标记开头，可能触发Markdown列表解析')
    return None


def _fix_flowchart(block_text: str) -> tuple[str, list[str]]:
    fixes = []
    text = block_text

    newline_before = text.count("\n")
    text = re.sub(r"\n[ \t]*\n+", "\n", text)
    if text.count("\n") < newline_before:
        fixes.append("空行")

    node_shapes = [
        (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)\(\(([^\)\"]+?)\)\)", re.MULTILINE),
         lambda m: f'{m.group(1)}{m.group(2)}(("{m.group(3)}"))', "圆形"),
        (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)\(\[([^\]\"]+?)\]\)", re.MULTILINE),
         lambda m: f'{m.group(1)}{m.group(2)}(["{m.group(3)}"])', "体育场形"),
        (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)\[\[([^\]\"]+?)\]\]", re.MULTILINE),
         lambda m: f'{m.group(1)}{m.group(2)}[["{m.group(3)}"]]', "子程序形状"),
        (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)>\(([^\)\"]+?)\)", re.MULTILINE),
         lambda m: f'{m.group(1)}{m.group(2)}>("{m.group(3)}")', "标签形状"),
        (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)\[([^\]\"]+?)\]", re.MULTILINE),
         lambda m: f'{m.group(1)}{m.group(2)}["{m.group(3)}"]', "矩形"),
        (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)\{([^\}\"]+?)\}", re.MULTILINE),
         lambda m: f'{m.group(1)}{m.group(2)}{{"{m.group(3)}"}}', "菱形"),
        (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)\(([^\)\"(<]+?)\)", re.MULTILINE),
         lambda m: f'{m.group(1)}{m.group(2)}("{m.group(3)}")', "圆角矩形"),
    ]

    def _wrap_node(pat, rep_fn, shape_name):
        nonlocal text
        def _rep(m):
            ntxt = m.group(3)
            if _text_needs_quotes(ntxt):
                return rep_fn(m)
            return m.group(0)
        text_new = pat.sub(_rep, text)
        return text_new

    for pat, rep_fn, shape_name in node_shapes:
        text_new = _wrap_node(pat, rep_fn, shape_name)
        if text_new != text:
            fixes.append(f"{shape_name}节点引号")
        text = text_new

    arrow_pat = re.compile(
        r"(-\.->|==>|-->|-\.-|===|---|<-->|<==>|<-\.->|<--|<==|<-\.-|==|--|-\.)"
        r"\|([^\"|][^|]*?)\|"
    )

    def _arrow_rep(m):
        arrow, label = m.group(1), m.group(2)
        if _text_needs_quotes(label) or label in ("是", "否"):
            return f'{arrow}|"{label}"|'
        return m.group(0)

    text_before = text
    text = arrow_pat.sub(_arrow_rep, text)
    if text != text_before:
        fixes.append("边标签引号")

    text_before = text
    text = _fix_backslash_n(text)
    if text != text_before:
        fixes.append("换行符(\\n→<br/>)")

    return text, fixes


def _check_flowchart(block_text: str, start_line: int) -> list[tuple[int, str, str]]:
    issues = _check_empty_lines(block_text, start_line)

    sub_pat = re.compile(r"^(\s*subgraph\s+)([^\s\[\"]+)(.*)$", re.MULTILINE)
    for m in sub_pat.finditer(block_text):
        sid = m.group(2).strip()
        rest = m.group(3).strip()
        lb = block_text[:m.start()].count("\n") + 1
        if CHINESE_CHARS_RE.search(sid) or "\uff1a" in sid or " " in sid:
            issues.append((start_line + lb - 1, "error",
                          f'subgraph 使用裸ID「{sid}」，应使用 subgraph EN_ID ["中文标题"] 格式'))
        if rest and not rest.startswith("["):
            if CHINESE_CHARS_RE.search(rest) or any(c in rest for c in "：（()"):
                issues.append((start_line + lb - 1, "error",
                              f'subgraph 标题「{rest[:20]}」缺少方括号，应使用 subgraph EN_ID ["标题"] 格式'))

    node_checks = [
        (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)\(\(([^\)\"]+?)\)\)", re.MULTILINE), "圆形"),
        (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)\(\[([^\]\"]+?)\]\)", re.MULTILINE), "体育场形"),
        (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)\[\[([^\]\"]+?)\]\]", re.MULTILINE), "子程序"),
        (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)>\(([^\)\"]+?)\)", re.MULTILINE), "标签形状"),
        (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)\[([^\]\"]+?)\]", re.MULTILINE), "矩形"),
        (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)\{([^\}\"]+?)\}", re.MULTILINE), "菱形"),
        (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)\(([^\)\"(<]+?)\)", re.MULTILINE), "圆角矩形"),
    ]

    for pat, shape_name in node_checks:
        for m in pat.finditer(block_text):
            ntxt = m.group(3)
            lb = block_text[:m.start()].count("\n") + 1
            if _text_needs_quotes(ntxt):
                issues.append((start_line + lb - 1, "error",
                              f'{shape_name}节点含中文/特殊字符/空格但未加双引号：{ntxt[:20]}'))
            w = _check_list_trigger(ntxt, lb - 1, start_line, f'{shape_name}节点')
            if w:
                issues.append(w)

    arrow_pat = re.compile(
        r"(-\.->|==>|-->|-\.-|===|---|<-->|<==>|<-\.->|<--|<==|<-\.-|==|--|-\.)\|([^|]*?)\|"
    )
    for m in arrow_pat.finditer(block_text):
        label = m.group(2)
        lb = block_text[:m.start()].count("\n") + 1
        if not (label.startswith('"') and label.endswith('"')):
            if _text_needs_quotes(label) or label in ("是", "否"):
                issues.append((start_line + lb - 1, "error",
                              f'边标签「{label[:20]}」含中文/特殊字符但未加双引号'))
        w = _check_list_trigger(label, lb - 1, start_line, '边标签')
        if w:
            issues.append(w)

    style_pat = re.compile(r"^\s*style\s+\w+\s+", re.MULTILINE)
    for m in style_pat.finditer(block_text):
        lb = block_text[:m.start()].count("\n") + 1
        line = block_text[m.start():].split("\n")[0]
        if CHINESE_CHARS_RE.search(line):
            issues.append((start_line + lb - 1, "warning",
                          'style 语句含中文字符，可能导致解析错误'))

    issues.extend(_check_backslash_n(block_text, start_line))

    return issues


def _strip_mindmap_shape(text: str) -> str:
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


def _fix_state_diagram(block_text: str) -> tuple[str, list[str]]:
    fixes = []
    text = block_text

    newline_before = text.count("\n")
    text = re.sub(r"\n[ \t]*\n+", "\n", text)
    if text.count("\n") < newline_before:
        fixes.append("空行")
        _debug_log("fix:空行", f"移除 {newline_before - text.count(chr(10))} 个空行")

    state_label_pat = re.compile(r"^(\s*state\s+)(\S+)\s*:\s*(.+)$", re.MULTILINE)

    def _state_label_rep(m):
        indent, sid, label = m.group(1), m.group(2), m.group(3).strip()
        needs_q = _state_text_needs_quotes(label)
        _debug_log("fix:state-label", f"sid={sid!r} label={label!r} needs_quotes={needs_q}")
        if needs_q:
            return f'{indent}{sid} : "{label}"'
        return m.group(0)

    text_before = text
    text = state_label_pat.sub(_state_label_rep, text)
    if text != text_before:
        fixes.append("状态描述引号")

    note_pat = re.compile(r"^(\s*note\s+(?:right|left|over)\s+of\s+\S+\s*:\s*)(.+)$", re.MULTILINE)

    def _note_rep(m):
        prefix, note_text = m.group(1), m.group(2).strip()
        needs_q = _state_text_needs_quotes(note_text)
        _debug_log("fix:note", f"prefix={prefix.rstrip()!r} note_text={note_text!r} needs_quotes={needs_q}")
        if needs_q:
            return f'{prefix}"{note_text}"'
        return m.group(0)

    text_before = text
    text = note_pat.sub(_note_rep, text)
    if text != text_before:
        fixes.append("note文本引号")

    trans_pat = re.compile(
        r"^(\s*(?:" + r'"[^"]*"' + r"|\[[\*]\]|\S+)\s*-->\s*(?:"
        + r'"[^"]*"' + r"|\[[\*]\]|\S+)\s*:\s*)(.+)$",
        re.MULTILINE,
    )

    def _trans_label_rep(m):
        prefix, label = m.group(1), m.group(2).strip()
        from_match = re.match(r"^\s*(\S+)\s*-->", prefix)
        from_s = from_match.group(1) if from_match else "?"
        to_match = re.search(r"-->\s*(\S+)\s*:", prefix)
        to_s = to_match.group(1) if to_match else "?"
        needs_q = _state_text_needs_quotes(label)
        _debug_log("fix:trans-label", f"{from_s} --> {to_s} : label={label!r} needs_quotes={needs_q}")
        if needs_q:
            return f'{prefix}"{label}"'
        return m.group(0)

    text_before = text
    text = trans_pat.sub(_trans_label_rep, text)
    if text != text_before:
        fixes.append("迁移标签引号")

    text_before = text
    text = _fix_backslash_n(text)
    if text != text_before:
        fixes.append("换行符(\\n→<br/>)")

    return text, fixes


def _check_state_diagram(block_text: str, start_line: int) -> list[tuple[int, str, str]]:
    issues = _check_empty_lines(block_text, start_line)
    if issues:
        _debug_log("check:空行", f"发现 {len(issues)} 个空行问题，起始行L{start_line}")

    state_label_pat = re.compile(r"^(\s*state\s+)(\S+)\s*:\s*(.+)$", re.MULTILINE)
    for m in state_label_pat.finditer(block_text):
        label = m.group(3).strip()
        sid = m.group(2)
        lb = block_text[:m.start()].count("\n") + 1
        needs_q = _state_text_needs_quotes(label)
        has_list = _has_list_trigger(label)
        _debug_log("check:state-label", f"L{lb} sid={sid!r} label={label!r} needs_quotes={needs_q} list_trigger={has_list}")
        if needs_q:
            issues.append((start_line + lb - 1, "error",
                          f'state 描述「{label[:20]}」含空格/特殊字符但未加双引号'))
        if has_list:
            w = _check_list_trigger(label, lb - 1, start_line, 'state描述')
            if w:
                issues.append(w)

    note_pat = re.compile(r"^(\s*note\s+(?:right|left|over)\s+of\s+\S+\s*:\s*)(.+)$", re.MULTILINE)
    for m in note_pat.finditer(block_text):
        note_text = m.group(2).strip()
        prefix = m.group(1).strip()
        lb = block_text[:m.start()].count("\n") + 1
        needs_q = _state_text_needs_quotes(note_text)
        has_list = _has_list_trigger(note_text)
        _debug_log("check:note", f"L{lb} prefix={prefix!r} note={note_text!r} needs_quotes={needs_q} list_trigger={has_list}")
        if needs_q:
            issues.append((start_line + lb - 1, "error",
                          f'note 文本「{note_text[:20]}」含空格/特殊字符但未加双引号'))
        if has_list:
            w = _check_list_trigger(note_text, lb - 1, start_line, 'note文本')
            if w:
                issues.append(w)

    trans_pat = re.compile(
        r"^(\s*(?:" + r'"[^"]*"' + r"|\[[\*]\]|\S+)\s*-->\s*(?:"
        + r'"[^"]*"' + r"|\[[\*]\]|\S+)\s*:\s*)(.+)$",
        re.MULTILINE,
    )
    for m in trans_pat.finditer(block_text):
        label = m.group(2).strip()
        prefix_stripped = m.group(1).strip()
        lb = block_text[:m.start()].count("\n") + 1
        needs_q = _state_text_needs_quotes(label)
        has_list = _has_list_trigger(label)
        from_match_t = re.match(r'^("?[^"\s]+"?|\[[\*]\])\s*-->', prefix_stripped)
        to_match_t = re.search(r'-->\s*("?[^"\s]+"?|\[[\*]\])\s*:', prefix_stripped)
        from_s = from_match_t.group(1) if from_match_t else "?"
        to_s = to_match_t.group(1) if to_match_t else "?"
        _debug_log("check:trans-label", f"L{lb} {from_s} --> {to_s} : label={label!r} needs_quotes={needs_q}(warn) list_trigger={has_list}")
        if needs_q:
            issues.append((start_line + lb - 1, "warning",
                          f'迁移标签「{label[:20]}」含空格/特殊字符，建议加双引号'))
        if has_list:
            w = _check_list_trigger(label, lb - 1, start_line, '迁移标签')
            if w:
                issues.append(w)

    lines = block_text.split("\n")
    _debug_log("check:逐行扫描", f"共 {len(lines)} 行")
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("stateDiagram") or stripped in ("{", "}"):
            _debug_log(f"L{i+1}", f"跳过(空行/图声明/花括号): {stripped[:40]!r}")
            continue
        lb = i + 1
        if re.match(r'^direction\s+\w+$', stripped):
            _debug_log(f"L{lb}", f"跳过(方向指令): {stripped!r}")
            continue

        composite_as = re.match(r'^state\s+"([^"]*)"\s+as\s+(\S+)\s*\{?$', stripped)
        if composite_as:
            cname, cid = composite_as.group(1), composite_as.group(2)
            has_list = _has_list_trigger(cname)
            _debug_log(f"L{lb}", f"复合状态(as格式): name={cname!r} id={cid!r} list_trigger={has_list}")
            if has_list:
                w = _check_list_trigger(cname, i, start_line, '复合状态名')
                if w:
                    issues.append(w)
            continue

        composite_bare = re.match(r'^state\s+(\S+)\s*\{?$', stripped)
        if composite_bare:
            sid = composite_bare.group(1)
            is_quoted = sid.startswith('"') and sid.endswith('"')
            needs_q = _state_text_needs_quotes(sid)
            _debug_log(f"L{lb}", f"复合状态(裸ID): sid={sid!r} quoted={is_quoted} needs_quotes={needs_q}")
            if is_quoted:
                inner = sid[1:-1]
                if _has_list_trigger(inner):
                    w = _check_list_trigger(sid, i, start_line, '复合状态名')
                    if w:
                        issues.append(w)
            elif needs_q:
                issues.append((start_line + lb - 1, "error",
                              f'state ID「{sid[:20]}」含空格/特殊字符，应使用 state "名称" as EN_ID 格式'))
            continue

        if re.match(r'^(?:note\s|end\s*note)', stripped):
            _debug_log(f"L{lb}", f"跳过(note块): {stripped[:40]!r}")
            continue

        if "-->" in stripped:
            trans_line_re = re.compile(
                r'^\s*((?:"[^"]*")|\[[\*]\]|\S+)\s*-->\s*((?:"[^"]*")|\[[\*]\]|\S+)(?:\s*:\s*(.+))?\s*$'
            )
            tm = trans_line_re.match(stripped)
            if tm:
                from_s, to_s, lbl = tm.group(1), tm.group(2), tm.group(3)
                _debug_log(f"L{lb}", f"转换行解析: from={from_s!r} to={to_s!r} label={lbl!r}")
                for stk_pos, stk in [("from", from_s), ("to", to_s)]:
                    if stk == "[*]":
                        _debug_log(f"L{lb}", f"  状态名[{stk_pos}]={stk!r} -> 起始/结束符，跳过")
                        continue
                    is_quoted = stk.startswith('"') and stk.endswith('"')
                    if is_quoted:
                        _debug_log(f"L{lb}", f"  状态名[{stk_pos}]={stk!r} -> 已加引号，跳过引号检查")
                        continue
                    needs_q = _state_text_needs_quotes(stk)
                    has_list = _has_list_trigger(stk)
                    _debug_log(f"L{lb}", f"  状态名[{stk_pos}]={stk!r} needs_quotes={needs_q} list_trigger={has_list}")
                    if needs_q:
                        issues.append((start_line + lb - 1, "error",
                                      f'状态名「{stk[:20]}」含空格/特殊字符但未加双引号'))
                    elif has_list:
                        w = _check_list_trigger(stk, i, start_line, '状态名')
                        if w:
                            issues.append(w)
            else:
                _debug_log(f"L{lb}", f"转换行正则未匹配: {stripped[:60]!r}")
            continue

        _debug_log(f"L{lb}", f"未匹配任何规则: {stripped[:60]!r}")

    _debug_log("check:summary", f"stateDiagram检查完成，累计问题 {len(issues)} 个")
    issues.extend(_check_backslash_n(block_text, start_line))
    return issues


def _fix_sequence_diagram(block_text: str) -> tuple[str, list[str]]:
    fixes = []
    text = block_text

    newline_before = text.count("\n")
    text = re.sub(r"\n[ \t]*\n+", "\n", text)
    if text.count("\n") < newline_before:
        fixes.append("空行")

    participant_pat = re.compile(
        r"^(\s*participant\s+)(\S+)\s+as\s+(.+)$", re.MULTILINE
    )

    def _part_rep(m):
        indent, pid, alias = m.group(1), m.group(2), m.group(3).strip()
        if _text_needs_quotes(alias) and not (alias.startswith('"') and alias.endswith('"')):
            return f'{indent}{pid} as "{alias}"'
        return m.group(0)

    text_before = text
    text = participant_pat.sub(_part_rep, text)
    if text != text_before:
        fixes.append("participant别名引号")

    return text, fixes


def _check_sequence_diagram(block_text: str, start_line: int) -> list[tuple[int, str, str]]:
    issues = _check_empty_lines(block_text, start_line)

    participant_pat = re.compile(
        r"^\s*participant\s+(\S+)\s+as\s+(.+)$", re.MULTILINE
    )
    for m in participant_pat.finditer(block_text):
        alias = m.group(2).strip()
        lb = block_text[:m.start()].count("\n") + 1
        if _text_needs_quotes(alias) and not (alias.startswith('"') and alias.endswith('"')):
            issues.append((start_line + lb - 1, "error",
                          f'participant 别名「{alias[:20]}」含中文/空格但未加双引号'))

    return issues


def _fix_mindmap(block_text: str) -> tuple[str, list[str]]:
    fixes = []
    text = block_text
    newline_before = text.count("\n")
    text = re.sub(r"\n[ \t]*\n+", "\n", text)
    if text.count("\n") < newline_before:
        fixes.append("空行")
    return text, fixes


def _check_mindmap(block_text: str, start_line: int) -> list[tuple[int, str, str]]:
    issues = _check_empty_lines(block_text, start_line)
    lines = block_text.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped == "mindmap" or stripped.startswith("mindmap"):
            if i == 0 or (i == 0 and stripped.lower().startswith("mindmap")):
                continue
        if stripped.startswith("mindmap"):
            continue
        node_text = _strip_mindmap_shape(stripped)
        if not node_text:
            continue
        lb = i + 1
        w = _check_list_trigger(node_text, i, start_line, 'mindmap节点')
        if w:
            issues.append(w)
        if ":" in node_text and not node_text.startswith('"'):
            issues.append((start_line + lb - 1, "warning",
                          f'mindmap节点「{node_text[:20]}」含冒号，可能导致解析错误，建议避免'))
    return issues


def _fix_generic(block_text: str) -> tuple[str, list[str]]:
    fixes = []
    text = block_text
    newline_before = text.count("\n")
    text = re.sub(r"\n[ \t]*\n+", "\n", text)
    if text.count("\n") < newline_before:
        fixes.append("空行")
    return text, fixes


def _check_generic(block_text: str, start_line: int, dia_type: str) -> list[tuple[int, str, str]]:
    issues = _check_empty_lines(block_text, start_line)

    if dia_type == "pie":
        pass
    elif dia_type == "gantt":
        title_pat = re.compile(r"^\s*title\s+(.+)$", re.MULTILINE)
        for m in title_pat.finditer(block_text):
            title_text = m.group(1).strip()
            if title_text.startswith('"') or title_text.startswith("'"):
                lb = block_text[:m.start()].count("\n") + 1
                issues.append((start_line + lb - 1, "warning",
                              'gantt title 不需要引号包裹，Mermaid会自动解析'))

    return issues


DIAGRAM_FIXERS = {
    "flowchart": _fix_flowchart,
    "stateDiagram": _fix_state_diagram,
    "sequenceDiagram": _fix_sequence_diagram,
    "pie": _fix_generic,
    "gantt": _fix_generic,
    "timeline": _fix_generic,
    "mindmap": _fix_mindmap,
    "xychart-beta": _fix_generic,
    "quadrantchart": _fix_generic,
}

DIAGRAM_CHECKERS = {
    "flowchart": _check_flowchart,
    "stateDiagram": _check_state_diagram,
    "sequenceDiagram": _check_sequence_diagram,
    "pie": lambda b, sl: _check_generic(b, sl, "pie"),
    "gantt": lambda b, sl: _check_generic(b, sl, "gantt"),
    "timeline": lambda b, sl: _check_generic(b, sl, "timeline"),
    "mindmap": _check_mindmap,
    "xychart-beta": lambda b, sl: _check_generic(b, sl, "xychart-beta"),
    "quadrantchart": lambda b, sl: _check_generic(b, sl, "quadrantChart"),
}


def _process_file(file_path: Path, root_dir: Path, fix: bool, dry_run: bool
                  ) -> tuple[list[tuple[int, str, str]], int, list[tuple[str, str]]]:
    content = file_path.read_text(encoding="utf-8")
    all_issues: list[tuple[int, str, str]] = []
    total_fixes = 0
    diffs: list[tuple[str, str]] = []

    def _rep_block(m):
        nonlocal total_fixes
        fence_start, block_text, fence_end = m.group(1), m.group(2), m.group(3)
        start_off = m.start(2)
        start_line = _line_from_offset(content, start_off)

        dia_type = _detect_diagram_type(block_text)
        fixer = DIAGRAM_FIXERS.get(dia_type, _fix_generic)
        checker = DIAGRAM_CHECKERS.get(dia_type, lambda b, sl: _check_generic(b, sl, dia_type))

        rel_path = file_path.relative_to(root_dir).as_posix()
        _debug_enter(rel_path, start_line, dia_type)
        _debug_log("block", f"发现 {dia_type} 代码块，文本长度 {len(block_text)} 字符")

        if fix or dry_run:
            fixed_text, fixes = fixer(block_text)
            if fixes:
                _debug_log("block", f"fixer返回修复项: {fixes}")
        else:
            fixed_text, fixes = block_text, []

        issues = checker(fixed_text if fix else block_text, start_line)
        all_issues.extend(issues)
        _debug_log("block", f"checker返回问题 {len(issues)} 个")

        if fixes and fixed_text != block_text:
            total_fixes += 1
            if dry_run:
                old_lines = block_text.split("\n")
                new_lines = fixed_text.split("\n")
                diff = difflib.unified_diff(
                    old_lines, new_lines,
                    fromfile=f"{file_path.relative_to(root_dir).as_posix()} (before)",
                    tofile=f"{file_path.relative_to(root_dir).as_posix()} (after)",
                    lineterm="", n=2
                )
                diffs.append(("\n".join(diff), ", ".join(fixes)))
            return fence_start + fixed_text + fence_end
        return m.group(0)

    new_content = MERMAID_FENCE_RE.sub(_rep_block, content)
    if fix and not dry_run and new_content != content:
        file_path.write_text(new_content, encoding="utf-8")
    return all_issues, total_fixes, diffs


def run(project_root: Path, args) -> int:
    check_root = Path(args.path).resolve() if getattr(args, "path", None) else project_root
    exclude = set(getattr(args, "exclude", []) or [])
    fix = getattr(args, "fix", False)
    dry_run = getattr(args, "dry_run", False)
    debug = getattr(args, "debug", False)
    _set_debug(debug)

    md_files = _find_md_files(check_root, exclude)
    total = len(md_files)
    files_with_issues = 0
    total_errors = 0
    total_warnings = 0
    total_fixes = 0
    all_diffs: list[tuple[str, str]] = []

    fix_mode = fix or dry_run
    fix_label = " (dry-run)" if dry_run else ""

    print(f"[检查] Mermaid 语法安全检查{fix_label}")
    print(f"   扫描目录: {check_root}")
    print(f"   文件总数: {total}")
    if fix_mode:
        print(f"   修复模式: {'预览(dry-run)' if dry_run else '自动修复'}")
    print()

    for md in sorted(md_files):
        issues, fixes, diffs = _process_file(md, project_root, fix=fix, dry_run=dry_run)
        total_fixes += fixes
        all_diffs.extend(diffs)
        if issues:
            files_with_issues += 1
            errs = [i for i in issues if i[1] == "error"]
            warns = [i for i in issues if i[1] == "warning"]
            total_errors += len(errs)
            total_warnings += len(warns)
            rel = md.relative_to(project_root).as_posix()
            print(f"[文件] {rel}")
            for ln, lvl, msg in sorted(issues, key=lambda x: x[0]):
                color = ANSI_RED if lvl == "error" else ANSI_YELLOW
                icon = "[错误]" if lvl == "error" else "[警告]"
                print(f"   {color}{icon} L{ln}: {msg}{ANSI_RESET}")
            if fixes > 0 and not dry_run:
                print(f"   {ANSI_CYAN}[修复] 已修复 {fixes} 个代码块{ANSI_RESET}")
            print()

    if dry_run and all_diffs:
        print("=" * 60)
        print(f"[预览] 修复预览（{len(all_diffs)} 个代码块变更）:")
        print()
        for diff_text, fix_desc in all_diffs:
            print(f"   [修复] {fix_desc}:")
            for line in diff_text.split("\n"):
                if line.startswith("+") and not line.startswith("+++"):
                    print(f"   {ANSI_GREEN}{line}{ANSI_RESET}")
                elif line.startswith("-") and not line.startswith("---"):
                    print(f"   {ANSI_RED}{line}{ANSI_RESET}")
                elif line.startswith("@@"):
                    print(f"   {ANSI_CYAN}{line}{ANSI_RESET}")
                else:
                    print(f"   {line}")
            print()

    print("=" * 60)
    print(f"[结果] 检查结果:")
    print(f"   扫描文件: {total}")
    print(f"   问题文件: {files_with_issues}")
    print(f"   {ANSI_RED}错误: {total_errors}{ANSI_RESET}")
    print(f"   {ANSI_YELLOW}警告: {total_warnings}{ANSI_RESET}")
    if fix_mode:
        print(f"   {ANSI_GREEN}自动修复: {total_fixes} 个文件块{ANSI_RESET}")

    if total_errors > 0 and not fix:
        print(f"\n{ANSI_RED}[错误] 发现 {total_errors} 个错误，请修复后再提交。可使用 --fix 参数自动修复部分问题，或使用 --dry-run 预览修复效果。{ANSI_RESET}")
        return 1
    if fix and total_errors > 0:
        print(f"\n{ANSI_YELLOW}[警告] 已自动修复可修复问题，仍有 {total_errors} 个错误需手动修复。{ANSI_RESET}")
        return 1
    if total_warnings > 0:
        print(f"\n{ANSI_YELLOW}[警告] 发现 {total_warnings} 个警告，建议检查。{ANSI_RESET}")
        return 0
    print(f"\n{ANSI_GREEN}[通过] 所有 Mermaid 代码块检查通过！{ANSI_RESET}")
    return 0
