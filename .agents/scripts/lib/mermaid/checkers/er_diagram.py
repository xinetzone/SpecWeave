import re
from typing import List, Tuple

from ..common import CHINESE_CHARS_RE, SPECIAL_CHARS, text_needs_quotes, strip_inline_comment
from .base import BaseDiagramChecker


class ErDiagramChecker(BaseDiagramChecker):
    def __init__(self):
        self.entity_pat = re.compile(r'^\s*([A-Z][A-Z0-9_]*|"[^"]*"|[^\s{]+)(\s*\{?\s*)$')
        self.er_rel_ops = [
            "||--o{", "||--||", "}o--o{", "}o--||", "|o--o{", "|o--||",
            "||--}|", "|o--o|", "|o--}", "|--o{", "|--||",
            "o--o{", "o--||", "--o{", "--||", "--|o", "--o", "--"
        ]
        self.er_rel_ops_sorted = sorted(self.er_rel_ops, key=len, reverse=True)
        self.attr_pat = re.compile(r'^\s*([A-Za-z_][A-Za-z0-9_]*|[A-Za-z_][A-Za-z0-9_]*\[\])\s+([A-Za-z_][A-Za-z0-9_]*)(\s+"[^"]*")?(\s+[A-Za-z]+)?\s*$')

    def get_diagram_type(self) -> str:
        return "erDiagram"

    def _check_specific_rules(self, block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
        issues = []
        lines = block_text.split("\n")
        in_entity_braces = False
        brace_depth = 0

        for i, line in enumerate(lines):
            code_part = strip_inline_comment(line)
            stripped = code_part.strip()
            if not stripped:
                continue
            lb = i + 1

            if stripped == "erDiagram" or stripped.lower().startswith("erdiagram"):
                continue

            if stripped in ("{", "}"):
                if stripped == "{":
                    brace_depth += 1
                    in_entity_braces = True
                else:
                    brace_depth -= 1
                    if brace_depth <= 0:
                        in_entity_braces = False
                        brace_depth = 0
                continue

            if in_entity_braces:
                if not self.attr_pat.match(stripped):
                    issues.append((start_line + lb - 1, "warning",
                                  f'实体属性行格式可能不正确：{stripped[:40]}'))
                continue

            em = self.entity_pat.match(stripped)
            if em and ":" not in stripped:
                ename = em.group(1)
                rest = em.group(2)
                is_upper_id = ename.isupper() and ename.replace("_", "").isalnum()
                is_quoted = ename.startswith('"') and ename.endswith('"')
                if not is_upper_id and not is_quoted:
                    if CHINESE_CHARS_RE.search(ename) or " " in ename or any(c in ename for c in SPECIAL_CHARS):
                        issues.append((start_line + lb - 1, "error",
                                      f'实体名「{ename[:20]}」含中文/空格/特殊字符但未加双引号，或非全大写英文ID格式'))
                if "{" in rest:
                    brace_depth += 1
                    in_entity_braces = True
                continue

            has_rel = False
            found_op = None
            op_pos = -1
            for op in self.er_rel_ops_sorted:
                pos = stripped.find(op)
                if pos != -1:
                    has_rel = True
                    found_op = op
                    op_pos = pos
                    break

            if has_rel:
                colon_pos = stripped.rfind(":")
                label = None
                rel_part = stripped
                if colon_pos != -1:
                    label = stripped[colon_pos + 1:].strip()
                    rel_part = stripped[:colon_pos]

                left = rel_part[:op_pos].strip()
                right = rel_part[op_pos + len(found_op):].strip()

                for side_name in [left, right]:
                    if not side_name:
                        continue
                    is_quoted = side_name.startswith('"') and side_name.endswith('"')
                    is_upper = side_name.isupper() and side_name.replace("_", "").isalnum()
                    if not is_upper and not is_quoted:
                        if CHINESE_CHARS_RE.search(side_name) or " " in side_name or any(c in side_name for c in SPECIAL_CHARS):
                            issues.append((start_line + lb - 1, "error",
                                          f'实体名「{side_name[:20]}」含中文/空格/特殊字符但未加双引号'))

                if label:
                    is_quoted = label.startswith('"') and label.endswith('"')
                    if not is_quoted and text_needs_quotes(label):
                        issues.append((start_line + lb - 1, "error",
                                      f'关系标签「{label[:20]}」含中文/空格但未加双引号'))
                continue

        return issues
