"""ER图修复器。"""


# 版本校验：相对导入共享库（depth=2）
from ...python310_version_check import enforce_python310

enforce_python310()

import re
from typing import List, Tuple

from ..common import text_needs_quotes, strip_inline_comment, fix_backslash_n
from .base import BaseDiagramFixer


class ErDiagramFixer(BaseDiagramFixer):
    def get_diagram_type(self) -> str:
        return "erDiagram"

    def fix(self, block_text: str) -> Tuple[str, List[str]]:
        fixes = []
        lines = block_text.split("\n")
        result_lines = []
        er_rel_ops = [
            "||--o{", "||--||", "}o--o{", "}o--||", "|o--o{", "|o--||",
            "||--}|", "|o--o|", "|o--}", "|--o{", "|--||",
            "o--o{", "o--||", "--o{", "--||", "--|o", "--o", "--"
        ]
        er_rel_ops_sorted = sorted(er_rel_ops, key=len, reverse=True)

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            code_part = strip_inline_comment(line)
            indent = line[:len(line) - len(line.lstrip())]
            comment = ""
            if "%%" in line and not line.lstrip().startswith("%%"):
                code_part, comment = line.split("%%", 1)
                comment = "%%" + comment

            code_stripped = code_part.strip()
            if not code_stripped or code_stripped == "erDiagram" or code_stripped.lower().startswith("erdiagram"):
                result_lines.append(line)
                continue

            if code_stripped in ("{", "}"):
                result_lines.append(indent + code_stripped + comment)
                continue

            entity_def = re.match(r'^(\s*)([A-Z][A-Z0-9_]*|"[^"]*"|[^\s{]+)(\s*\{?\s*)$', code_part)
            if entity_def and ":" not in code_stripped:
                prefix, ename, rest = entity_def.group(1), entity_def.group(2), entity_def.group(3)
                is_upper_id = ename.isupper() and ename.replace("_", "").isalnum()
                is_quoted = ename.startswith('"') and ename.endswith('"')
                if not is_upper_id and not is_quoted and text_needs_quotes(ename):
                    ename = f'"{ename}"'
                    if "实体名引号" not in fixes:
                        fixes.append("实体名引号")
                result_lines.append(prefix + ename + rest.rstrip() + comment)
                continue

            has_rel = False
            found_op = None
            op_pos = -1
            for op in er_rel_ops_sorted:
                pos = code_part.find(op)
                if pos != -1:
                    has_rel = True
                    found_op = op
                    op_pos = pos
                    break

            if has_rel:
                colon_pos = code_part.rfind(":")
                label_part = ""
                rel_part = code_part
                if colon_pos != -1:
                    label_part = code_part[colon_pos + 1:]
                    rel_part = code_part[:colon_pos]
                    label_text = label_part.strip()
                    if label_text and not (label_text.startswith('"') and label_text.endswith('"')):
                        if text_needs_quotes(label_text):
                            label_part = f' "{label_text}"'
                            if "关系标签引号" not in fixes:
                                fixes.append("关系标签引号")

                left = rel_part[:op_pos].strip()
                right = rel_part[op_pos + len(found_op):].strip()

                def _quote_entity(name):
                    if not name:
                        return name
                    if name.startswith('"') and name.endswith('"'):
                        return name
                    is_upper = name.isupper() and name.replace("_", "").isalnum()
                    if not is_upper and text_needs_quotes(name):
                        if "实体名引号" not in fixes:
                            fixes.append("实体名引号")
                        return f'"{name}"'
                    return name

                left = _quote_entity(left)
                right = _quote_entity(right)
                new_line = f"{indent}{left} {found_op} {right}"
                if colon_pos != -1:
                    new_line += f" :{label_part}"
                result_lines.append(new_line.rstrip() + comment)
                continue

            result_lines.append(line)

        text = "\n".join(result_lines)

        newline_before = block_text.count("\n")
        if text.count("\n") < newline_before:
            if "空行" not in fixes:
                fixes.insert(0, "空行")

        text_before = text
        text = fix_backslash_n(text)
        if text != text_before:
            fixes.append("换行符(\\n→<br/>)")

        return text, fixes

