# 版本校验：相对导入共享库（depth=2）
from ...python310_version_check import enforce_python310

enforce_python310()

import re
from typing import List, Tuple

from ..common import CHINESE_CHARS_RE, text_needs_quotes, check_list_trigger
from .base import BaseDiagramChecker


class FlowchartChecker(BaseDiagramChecker):
    def __init__(self):
        self.sub_pat = re.compile(r"^(\s*subgraph\s+)([^\s\[\"]+)(.*)$", re.MULTILINE)
        self.node_pats = [
            (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)\(\(([^\)\"]+?)\)\)", re.MULTILINE), "圆形"),
            (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)\(\[([^\]\"]+?)\]\)", re.MULTILINE), "体育场形"),
            (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)\[\[([^\]\"]+?)\]\]", re.MULTILINE), "子程序"),
            (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)>\(([^\)\"]+?)\)", re.MULTILINE), "标签形状"),
            (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)\[([^\]\"]+?)\]", re.MULTILINE), "矩形"),
            (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)\{([^\}\"]+?)\}", re.MULTILINE), "菱形"),
            (re.compile(r"(^|[^a-zA-Z0-9_\"])([A-Za-z][A-Za-z0-9_]*)\(([^\)\"(<]+?)\)", re.MULTILINE), "圆角矩形"),
        ]
        self.arrow_pat = re.compile(
            r"(-\.->|==>|-->|-\.-|===|---|<-->|<==>|<-\.->|<--|<==|<-\.-|==|--|-\.)\|([^|]*?)\|"
        )
        self.style_pat = re.compile(r"^\s*style\s+\w+\s+", re.MULTILINE)

    def get_diagram_type(self) -> str:
        return "flowchart"

    def _check_specific_rules(self, block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
        issues = []

        for m in self.sub_pat.finditer(block_text):
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

        for pat, shape_name in self.node_pats:
            for m in pat.finditer(block_text):
                ntxt = m.group(3)
                lb = block_text[:m.start()].count("\n") + 1
                if text_needs_quotes(ntxt):
                    issues.append((start_line + lb - 1, "error",
                                  f'{shape_name}节点含中文/特殊字符/空格但未加双引号：{ntxt[:20]}'))
                w = check_list_trigger(ntxt, lb - 1, start_line, f'{shape_name}节点')
                if w:
                    issues.append(w)

        for m in self.arrow_pat.finditer(block_text):
            label = m.group(2)
            lb = block_text[:m.start()].count("\n") + 1
            if not (label.startswith('"') and label.endswith('"')):
                if text_needs_quotes(label) or label in ("是", "否"):
                    issues.append((start_line + lb - 1, "error",
                                  f'边标签「{label[:20]}」含中文/特殊字符但未加双引号'))
            w = check_list_trigger(label, lb - 1, start_line, '边标签')
            if w:
                issues.append(w)

        for m in self.style_pat.finditer(block_text):
            lb = block_text[:m.start()].count("\n") + 1
            line = block_text[m.start():].split("\n")[0]
            if CHINESE_CHARS_RE.search(line):
                issues.append((start_line + lb - 1, "warning",
                              'style 语句含中文字符，可能导致解析错误'))

        return issues

