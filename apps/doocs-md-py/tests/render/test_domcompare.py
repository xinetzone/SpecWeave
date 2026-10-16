"""归一化 DOM 比较器自身行为。"""

from doocs_md_py.render.domcompare import dom_equal, parse_dom


def test_whitespace_and_newlines_ignored():
    ok, _ = dom_equal("<p>  a\n\nb </p>", "<p>a b</p>")
    assert ok


def test_attribute_order_ignored():
    ok, _ = dom_equal(
        '<a href="x" title="t">q</a>', '<a title="t" href="x">q</a>'
    )
    assert ok


def test_attribute_value_matters():
    ok, message = dom_equal('<a href="x">q</a>', '<a href="y">q</a>')
    assert not ok
    assert "属性不同" in message


def test_tag_difference_reported():
    ok, message = dom_equal("<p>x</p>", "<div>x</div>")
    assert not ok
    assert "标签不同" in message


def test_child_count_difference_reported():
    ok, message = dom_equal("<ul><li>a</li></ul>", "<ul><li>a</li><li>b</li></ul>")
    assert not ok
    assert "子节点数量不同" in message


def test_text_difference_reported():
    ok, message = dom_equal("<p>abc</p>", "<p>abd</p>")
    assert not ok
    assert "文本不同" in message


def test_nested_structure_equal():
    a = "<section><table><thead><tr><th>A</th></tr></thead></table></section>"
    b = """
    <section>
      <table>
        <thead>
          <tr><th>A</th></tr>
        </thead>
      </table>
    </section>
    """
    ok, _ = dom_equal(a, b)
    assert ok


def test_self_closing_void_elements():
    ok, _ = dom_equal('<img src="a" alt="x">', '<img alt="x" src="a"/>')
    assert ok
    root = parse_dom('<br><hr class="hr">')
    tags = [c.tag for c in root.children]
    assert tags == ["br", "hr"]
