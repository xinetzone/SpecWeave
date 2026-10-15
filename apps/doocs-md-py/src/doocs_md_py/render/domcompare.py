"""归一化 DOM 结构比较器（黄金样例框架，标准库 html.parser 实现）。

用途：渲染等价性按 NG6「归一化 DOM 结构」裁决——忽略标签间换行/缩进与属性书写
顺序，比较标签树、属性键值与文本节点（文本空白折叠为单空格）。
"""

import re
from dataclasses import dataclass, field
from html.parser import HTMLParser

_WS_RE = re.compile(r"\s+")


@dataclass(slots=True)
class Node:
    tag: str
    attrs: tuple[tuple[str, str], ...]
    children: list = field(default_factory=list)


# HTML void elements：解析为不可有子节点的自闭合标签
_VOID_TAGS = frozenset(
    {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
     "meta", "param", "source", "track", "wbr"}
)


class _DOMBuilder(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", (), [])
        self._stack = [self.root]

    def _make_node(self, tag: str, attrs: list[tuple[str, str | None]]) -> Node:
        return Node(tag, tuple(sorted((k, v or "") for k, v in attrs)), [])

    def handle_starttag(self, tag, attrs):
        node = self._make_node(tag, attrs)
        self._stack[-1].children.append(node)
        if tag not in _VOID_TAGS:
            self._stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self._stack[-1].children.append(self._make_node(tag, attrs))

    def handle_endtag(self, tag):
        for i in range(len(self._stack) - 1, 0, -1):
            if self._stack[i].tag == tag:
                del self._stack[i:]
                return

    def handle_data(self, data):
        text = _WS_RE.sub(" ", data).strip()
        if text:
            self._stack[-1].children.append(text)


def parse_dom(html: str) -> Node:
    builder = _DOMBuilder()
    builder.feed(html)
    builder.close()
    return builder.root


def _diff(expected: Node | str, actual: Node | str, path: str) -> str | None:
    if type(expected) is not type(actual):
        return f"{path}: 节点类型不同 expected={expected!r} actual={actual!r}"
    if isinstance(expected, str):
        if expected != actual:
            return f"{path}: 文本不同 expected={expected!r} actual={actual!r}"
        return None
    assert isinstance(actual, Node)
    if expected.tag != actual.tag:
        return f"{path}: 标签不同 <{expected.tag}> vs <{actual.tag}>"
    if expected.attrs != actual.attrs:
        return f"{path}/{expected.tag}: 属性不同 expected={expected.attrs} actual={actual.attrs}"
    if len(expected.children) != len(actual.children):
        return (
            f"{path}/{expected.tag}: 子节点数量不同 "
            f"expected={len(expected.children)} actual={len(actual.children)}"
        )
    for i, (child_e, child_a) in enumerate(zip(expected.children, actual.children, strict=True)):
        found = _diff(child_e, child_a, f"{path}/{expected.tag}[{i}]")
        if found:
            return found
    return None


def dom_equal(expected_html: str, actual_html: str) -> tuple[bool, str]:
    """返回 (是否等价, 差异描述)。"""
    message = _diff(parse_dom(expected_html), parse_dom(actual_html), "#root")
    return message is None, message or ""


def assert_dom_equal(expected_html: str, actual_html: str) -> None:
    """断言失败时附带首个差异路径。"""
    ok, message = dom_equal(expected_html, actual_html)
    assert ok, message
