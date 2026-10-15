"""TR-7.2 综合黄金对拍：5000 字 complex_doc 与上游 doocs/md v2.1.0 Node 输出逐节点等价。

夹具：
- complex_doc.md：综合文档（frontmatter 场景外的 T6/T7 全部扩展交互）。
- complex_doc.expected.html：上游 `initRenderer({}).renderMarkdownToHtml()` 经
  stripBreakBeforeInlineKatex 后的输出（Node 22 + marked 18.1.0，SSR 占位路径），
  由 .temp-node-comp 对拍 harness 生成并锁定。

重生成方式见 scripts/golden_regenerate.py（需 WSL podman node:22-alpine）。
"""

from doocs_md_py.render import init_renderer
from doocs_md_py.render.domcompare import assert_dom_equal
from doocs_md_py.render.extensions.katex import strip_break_before_inline_katex

from pathlib import Path

FIXTURE_DIR = Path(__file__).resolve().parent


def test_complex_doc_matches_upstream_dom() -> None:
    md = (FIXTURE_DIR / "complex_doc.md").read_text(encoding="utf-8")
    expected = (FIXTURE_DIR / "complex_doc.expected.html").read_text(encoding="utf-8")
    actual = strip_break_before_inline_katex(
        init_renderer().render_markdown_to_html(md)
    )
    assert_dom_equal(expected, actual)
