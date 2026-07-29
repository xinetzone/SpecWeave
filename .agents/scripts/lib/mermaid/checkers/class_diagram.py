import re
from typing import List, Tuple

from ..common import CHINESE_CHARS_RE, text_needs_quotes, strip_inline_comment
from .base import BaseDiagramChecker


class ClassDiagramChecker(BaseDiagramChecker):
    def __init__(self):
        self.class_def_pat = re.compile(r'^\s*class\s+("?[A-Za-z][A-Za-z0-9_]*"?|[^\s{]+)(\s*\{?\s*)$')
        self.member_pat = re.compile(r'^\s*([+\-#~])?\s*(?:([A-Za-z_][A-Za-z0-9_<>]*)\s+)?([A-Za-z_][A-Za-z0-9_]*)(\([^)]*\))?(\s*[A-Za-z_][A-Za-z0-9_<>]*)?\s*("[^"]*")?\s*$')
        self.rel_operators = ["<|--", "*--", "o--", "-->", "<--", "--*", "--o", "<.-", ".->", "--"]

    def get_diagram_type(self) -> str:
        return "classDiagram"

    def _check_specific_rules(self, block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
        issues = []
        lines = block_text.split("\n")
        in_class_braces = False
        brace_depth = 0

        for i, line in enumerate(lines):
            code_part = strip_inline_comment(line)
            stripped = code_part.strip()
            if not stripped:
                continue
            lb = i + 1

            if stripped == "classDiagram" or stripped.lower().startswith("classdiagram"):
                continue

            if stripped in ("{", "}"):
                if stripped == "{":
                    brace_depth += 1
                    in_class_braces = True
                else:
                    brace_depth -= 1
                    if brace_depth <= 0:
                        in_class_braces = False
                        brace_depth = 0
                continue

            if in_class_braces:
                if not self.member_pat.match(stripped):
                    is_annotation = stripped.startswith("<<") and stripped.endswith(">>")
                    if not is_annotation:
                        issues.append((start_line + lb - 1, "warning",
                                      f'类成员行格式可能不正确：{stripped[:40]}'))
                continue

            cm = self.class_def_pat.match(stripped)
            if cm:
                cname = cm.group(1)
                rest = cm.group(2)
                is_quoted = cname.startswith('"') and cname.endswith('"')
                if not is_quoted and text_needs_quotes(cname):
                    issues.append((start_line + lb - 1, "error",
                                  f'类名「{cname[:20]}」含中文/空格/特殊字符但未加双引号'))
                if "{" in rest:
                    brace_depth += 1
                    in_class_braces = True
                continue

            has_rel_op = any(op in stripped for op in self.rel_operators)
            if has_rel_op:
                colon_pos = stripped.rfind(":")
                label = None
                rel_part = stripped
                if colon_pos != -1:
                    label = stripped[colon_pos + 1:].strip()
                    rel_part = stripped[:colon_pos]

                found_op = None
                op_pos = -1
                for op in self.rel_operators:
                    pos = rel_part.find(op)
                    if pos != -1:
                        found_op = op
                        op_pos = pos
                        break

                if found_op:
                    left = rel_part[:op_pos].strip()
                    right = rel_part[op_pos + len(found_op):].strip()

                    for side_name in [left, right]:
                        if not side_name:
                            continue
                        is_quoted = side_name.startswith('"') and side_name.endswith('"')
                        if not is_quoted and text_needs_quotes(side_name):
                            issues.append((start_line + lb - 1, "error",
                                          f'类名「{side_name[:20]}」含中文/空格/特殊字符但未加双引号'))

                if label:
                    is_quoted = label.startswith('"') and label.endswith('"')
                    if not is_quoted and text_needs_quotes(label):
                        issues.append((start_line + lb - 1, "error",
                                      f'关系标签「{label[:20]}」含中文/空格但未加双引号'))
                continue

        return issues
