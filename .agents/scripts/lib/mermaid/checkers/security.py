import re
from typing import List, Tuple

from ..common import strip_inline_comment


class SecurityChecker:
    def __init__(self):
        self.dangerous_tags = re.compile(r'<\s*(script|img|iframe|svg|object|embed)\b', re.IGNORECASE)
        self.event_handler = re.compile(r'\son\w+\s*=', re.IGNORECASE)
        self.click_pat = re.compile(r'^\s*click\s+\S+', re.IGNORECASE)
        self.js_url_pat = re.compile(r'javascript\s*:', re.IGNORECASE)
        self.end_as_node = re.compile(r'(^|[^a-zA-Z0-9_])end\s*[\(\[\{<]', re.IGNORECASE)

    def check(self, block_text: str, start_line: int) -> List[Tuple[int, str, str]]:
        issues = []
        for i, line in enumerate(block_text.split("\n")):
            code_part = strip_inline_comment(line)
            if not code_part.strip():
                continue
            lb = start_line + i

            if self.click_pat.match(code_part):
                issues.append((lb, "error",
                              "禁止使用 click 事件绑定，存在 JavaScript 回调注入风险"))

            tag_m = self.dangerous_tags.search(code_part)
            if tag_m:
                issues.append((lb, "error",
                              f"禁止使用危险 HTML 标签 <{tag_m.group(1)}>，存在安全风险"))

            if self.event_handler.search(code_part):
                issues.append((lb, "error",
                              "禁止使用 HTML 事件处理器属性（on*），存在 XSS 风险"))

            if self.js_url_pat.search(code_part):
                issues.append((lb, "error",
                              '禁止使用 javascript: 协议 URL，存在 XSS 风险'))

            if self.end_as_node.search(code_part):
                issues.append((lb, "error",
                              '禁止使用 "end" 作为节点 ID，与 Mermaid 保留字冲突'))

        return issues
