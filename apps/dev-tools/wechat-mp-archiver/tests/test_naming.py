"""跨平台安全文件名工具测试。"""

from mp_archiver.naming import article_dir_name, safe_filename


def test_strips_windows_illegal_chars():
    result = safe_filename('a<b>c:d"e/f\\g|h?i*j')
    assert "/" not in result and "\\" not in result
    assert ":" not in result and "?" not in result and "*" not in result
    assert "<" not in result and ">" not in result and '"' not in result and "|" not in result
    assert result.count("_") >= 9


def test_preserves_unicode_and_collapses_whitespace():
    result = safe_filename("  微信  公众号\t归档  指南 \n ")
    assert "微信" in result and "公众号" in result and "指南" in result
    assert "  " not in result
    assert not result.startswith(" ") and not result.endswith(" ")


def test_empty_and_none_fallback():
    assert safe_filename(None) == "untitled"
    assert safe_filename("") == "untitled"
    assert safe_filename("   ") == "untitled"
    assert safe_filename("", default="空") == "空"


def test_windows_reserved_names():
    assert safe_filename("CON") == "_CON"
    assert safe_filename("con.txt") == "_con.txt"  # 仅加前缀，不改变原大小写
    assert safe_filename("com1") == "_com1"
    assert safe_filename("NUL.log") == "_NUL.log"
    # 普通内容不受影响
    assert safe_filename("CONference") == "CONference"


def test_strips_trailing_dots_and_spaces():
    assert not safe_filename("report...").endswith(".")
    assert not safe_filename("report . . ").endswith((" ", "."))


def test_truncation_keeps_extension():
    name = "长" * 200 + ".pdf"
    result = safe_filename(name, max_length=120)
    assert len(result) == 120
    assert result.endswith(".pdf")


def test_long_name_without_extension_truncated():
    result = safe_filename("字" * 300, max_length=100)
    assert len(result) == 100


def test_article_dir_name():
    # 半角斜杠替换；全角冒号为 Windows 合法字符，予以保留
    assert article_dir_name("2026-09-24T10:00:00", "深度/长文：第一讲") == "2026-09-24_深度_长文：第一讲"
    assert article_dir_name(None, None).startswith("unknown-date_untitled")
