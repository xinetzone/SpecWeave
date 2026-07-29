# 版本校验：相对导入共享库（depth=2）
from ...python310_version_check import enforce_python310

enforce_python310()

import re
from typing import List, Tuple

from ..common import CHINESE_CHARS_RE, state_text_needs_quotes, check_list_trigger, strip_inline_comment, has_list_trigger
from .base import BaseDiagramChecker


class StateDiagramChecker(BaseDiagramChecker):
    def __init__(self):
        self.state_label_pat = re.compile(r"^(\s*state\s+)(\S+)\s*:\s*(.+)$", re.MULTILINE)
        self.note_pat = re.compile(r"^(\s*note\s+(?:right|left|over)\s+of\s+\S+\s*:\s*)(.+)$", re.MULTILINE)
        self.trans_pat = re.compile(
            r"^(\s*(?:" + r'"[^"]*"' + r"|\[[\*]\]|\S+)\s*-->\s*(?:"
            + r'"[^"]*"' + r"|\[[\*]\]|\S+)\s*:\s*)(.+)$",
            re.MULTILINE,
        )
        self.direction_pat = re.compile(r'^direction\s+\w+$')
        self.composite_as_pat = re.compile(r'^state\s+"([^"]*)"\s+as\s+(\S+)\s*\{?$')
        self.composite_bare_pat = re.compile(r'^state\s+(\S+)\s*\{?$')
        self.note_block_pat = re.compile(r'^(?:note\s|end\s*note)')
        self.trans_line_pat = re.compile(
            r'^\s*((?:"[^"]*")|\[[\*]\]|\S+)\s*-->\s*((?:"[^"]*")|\[[\*]\]|\S+)(?:\s*:\s*(.+))?\s*$'
        )

    def get_diagram_type(self) -> str:
        return "stateDiagram"

    def _check_specific_rules(self, block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
        issues = []

        for m in self.state_label_pat.finditer(block_text):
            label = m.group(3).strip()
            lb = block_text[:m.start()].count("\n") + 1
            needs_q = state_text_needs_quotes(label)
            if needs_q:
                issues.append((start_line + lb - 1, "error",
                              f'state 描述「{label[:20]}」含空格/特殊字符但未加双引号'))
            w = check_list_trigger(label, lb - 1, start_line, 'state描述')
            if w:
                issues.append(w)

        for m in self.note_pat.finditer(block_text):
            note_text = m.group(2).strip()
            lb = block_text[:m.start()].count("\n") + 1
            needs_q = state_text_needs_quotes(note_text)
            if needs_q:
                issues.append((start_line + lb - 1, "error",
                              f'note 文本「{note_text[:20]}」含空格/特殊字符但未加双引号'))
            w = check_list_trigger(note_text, lb - 1, start_line, 'note文本')
            if w:
                issues.append(w)

        for m in self.trans_pat.finditer(block_text):
            label = m.group(2).strip()
            lb = block_text[:m.start()].count("\n") + 1
            needs_q = state_text_needs_quotes(label)
            if needs_q:
                issues.append((start_line + lb - 1, "warning",
                              f'迁移标签「{label[:20]}」含空格/特殊字符，建议加双引号'))
            w = check_list_trigger(label, lb - 1, start_line, '迁移标签')
            if w:
                issues.append(w)

        lines = block_text.split("\n")
        for i, line in enumerate(lines):
            code_part = strip_inline_comment(line)
            stripped = code_part.strip()
            if not stripped or stripped.startswith("stateDiagram") or stripped in ("{", "}"):
                continue
            lb = i + 1
            if self.direction_pat.match(stripped):
                continue

            composite_as = self.composite_as_pat.match(stripped)
            if composite_as:
                cname = composite_as.group(1)
                w = check_list_trigger(cname, i, start_line, '复合状态名')
                if w:
                    issues.append(w)
                continue

            composite_bare = self.composite_bare_pat.match(stripped)
            if composite_bare:
                sid = composite_bare.group(1)
                is_quoted = sid.startswith('"') and sid.endswith('"')
                needs_q = state_text_needs_quotes(sid)
                if is_quoted:
                    inner = sid[1:-1]
                    if has_list_trigger(inner):
                        w = check_list_trigger(sid, i, start_line, '复合状态名')
                        if w:
                            issues.append(w)
                elif needs_q:
                    issues.append((start_line + lb - 1, "error",
                                  f'state ID「{sid[:20]}」含空格/特殊字符，应使用 state "名称" as EN_ID 格式'))
                continue

            if self.note_block_pat.match(stripped):
                continue

            if "-->" in stripped:
                tm = self.trans_line_pat.match(stripped)
                if tm:
                    from_s, to_s = tm.group(1), tm.group(2)
                    for stk in [from_s, to_s]:
                        if stk == "[*]":
                            continue
                        is_quoted = stk.startswith('"') and stk.endswith('"')
                        if is_quoted:
                            continue
                        needs_q = state_text_needs_quotes(stk)
                        if needs_q:
                            issues.append((start_line + lb - 1, "error",
                                          f'状态名「{stk[:20]}」含空格/特殊字符但未加双引号'))
                        elif has_list_trigger(stk):
                            w = check_list_trigger(stk, i, start_line, '状态名')
                            if w:
                                issues.append(w)
                continue

        return issues

