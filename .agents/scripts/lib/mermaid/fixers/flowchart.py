"""流程图修复器。"""


# 版本校验：相对导入共享库（depth=2）
from ...python310_version_check import enforce_python310

enforce_python310()

import re
from typing import List, Tuple

from ..common import text_needs_quotes, fix_empty_lines, fix_backslash_n
from .base import BaseDiagramFixer


class FlowchartFixer(BaseDiagramFixer):
    def get_diagram_type(self) -> str:
        return "flowchart"

    def fix(self, block_text: str) -> Tuple[str, List[str]]:
        fixes = []
        text = block_text

        newline_before = text.count("\n")
        text = fix_empty_lines(text)
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
                if text_needs_quotes(ntxt):
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
            if text_needs_quotes(label) or label in ("是", "否"):
                return f'{arrow}|"{label}"|'
            return m.group(0)

        text_before = text
        text = arrow_pat.sub(_arrow_rep, text)
        if text != text_before:
            fixes.append("边标签引号")

        text_before = text
        text = fix_backslash_n(text)
        if text != text_before:
            fixes.append("换行符(\\n→<br/>)")

        return text, fixes

    def _fix_specific(self, block_text: str) -> Tuple[str, List[str]]:
        return block_text, []

