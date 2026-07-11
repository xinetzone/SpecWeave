"""check-links.py 反例修复测试。

覆盖CE-01到CE-04四个问题：
- CE-01/02: 图片语法(![alt](img))不应被误判为链接
- CE-03: 行内代码中的链接示例应被忽略
- CE-04: 带标题的链接[text](url "title")URL应正确解析
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


def _import_check_links():
    """导入check-links.py中的函数"""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "check_links", Path(__file__).parent.parent / "check-links.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cl = _import_check_links()


def _write_and_parse(content: str, tmp_path: Path, filename: str = "test.md"):
    """Helper: 写临时文件并解析链接"""
    f = tmp_path / filename
    f.write_text(content, encoding="utf-8")
    return cl.parse_links(f), f


class TestImageSyntaxIgnored:
    """CE-01/02: 图片语法![alt](img)应被忽略，不是链接。"""

    def test_basic_image_not_treated_as_link(self, tmp_path):
        """![alt](img.png) 不应被识别为链接"""
        links, _ = _write_and_parse("![图片描述](image.png)", tmp_path)
        assert len(links) == 0, f"图片不应被识别为链接，但找到了{len(links)}个链接"

    def test_empty_alt_image_not_treated_as_link(self, tmp_path):
        """![](img.png) 空alt图片也不应被识别"""
        links, _ = _write_and_parse("![](empty-alt.png)", tmp_path)
        assert len(links) == 0, "空alt图片不应被识别为链接"

    def test_image_with_title_not_treated_as_link(self, tmp_path):
        """![alt](img.png "title") 带标题的图片不应被识别"""
        links, _ = _write_and_parse('![图片](image.png "图片标题")', tmp_path)
        assert len(links) == 0, "带标题的图片不应被识别为链接"

    def test_normal_link_still_works(self, tmp_path):
        """正常的链接[text](file.md)应继续正常工作（正向回归）"""
        links, f = _write_and_parse("[正常链接](file.md)", tmp_path)
        assert len(links) == 1
        assert links[0][0] == "正常链接"
        assert links[0][1] == "file.md"

    def test_image_and_link_mixed(self, tmp_path):
        """同一行同时有图片和链接，只应识别链接"""
        links, _ = _write_and_parse("![图片](img.png) 和 [链接](file.md)", tmp_path)
        assert len(links) == 1
        assert links[0][1] == "file.md"
        assert links[0][0] == "链接"


class TestInlineCodeLinksIgnored:
    """CE-03: 行内代码`...`中的链接示例应被忽略。"""

    def test_inline_code_example_ignored(self, tmp_path):
        """行内代码中的链接示例`[text](fake.md)`不应被检查"""
        links, _ = _write_and_parse("使用 `[text](fake-example.md)` 作为示例", tmp_path)
        assert len(links) == 0, "行内代码中的链接示例应被忽略"

    def test_double_backtick_inline_code_ignored(self, tmp_path):
        """双反引号行内代码``[`code`](url)``也应被忽略"""
        links, _ = _write_and_parse("``[`code`](fake-code.md)`` 是代码", tmp_path)
        assert len(links) == 0, "双反引号行内代码中的链接应被忽略"

    def test_link_outside_inline_code_still_works(self, tmp_path):
        """行内代码外的正常链接应继续工作"""
        links, f = _write_and_parse("[真实链接](real.md) 和 `[代码示例](fake.md)`", tmp_path)
        assert len(links) == 1
        assert links[0][1] == "real.md"

    def test_multiple_inline_code_sections(self, tmp_path):
        """多个行内代码块中的链接都应被忽略"""
        content = "`[a](1.md)` 文字 `[b](2.md)` 文字 `[c](3.md)`"
        links, _ = _write_and_parse(content, tmp_path)
        assert len(links) == 0, "所有行内代码块中的链接都应被忽略"

    def test_real_link_after_inline_code(self, tmp_path):
        """行内代码后面的真实链接应被识别"""
        content = "用 `[code](fake.md)` 语法写[真实链接](real.md)"
        links, _ = _write_and_parse(content, tmp_path)
        assert len(links) == 1
        assert links[0][1] == "real.md"


class TestLinkWithTitle:
    """CE-04: 带标题的链接[text](url "title")URL应正确解析（去掉标题部分）。"""

    def test_double_quoted_title_stripped(self, tmp_path):
        """[text](file.md "title") URL应为file.md，不含标题"""
        links, _ = _write_and_parse('[链接](file.md "这是标题")', tmp_path)
        assert len(links) == 1
        assert links[0][1] == "file.md", f"URL应去掉标题部分，实际是'{links[0][1]}'"

    def test_single_quoted_title_stripped(self, tmp_path):
        """[text](file.md 'title') URL应为file.md"""
        links, _ = _write_and_parse("[链接](file.md '这是标题')", tmp_path)
        assert len(links) == 1
        assert links[0][1] == "file.md"

    def test_link_without_title_unchanged(self, tmp_path):
        """不带标题的普通链接URL应保持不变"""
        links, _ = _write_and_parse("[链接](file.md)", tmp_path)
        assert len(links) == 1
        assert links[0][1] == "file.md"

    def test_external_url_with_title(self, tmp_path):
        """外部URL带标题也应正确解析"""
        links, _ = _write_and_parse('[外部](https://example.com "Example Site")', tmp_path)
        assert len(links) == 1
        assert links[0][1] == "https://example.com"

    def test_url_with_anchor_and_title(self, tmp_path):
        """带锚点和标题的链接应正确处理"""
        links, _ = _write_and_parse('[链接](file.md#section "标题")', tmp_path)
        assert len(links) == 1
        assert links[0][1] == "file.md#section"

    def test_local_link_check_with_title_passes(self, tmp_path):
        """带标题的本地链接存在时应检查通过（不是误报断链）"""
        target_file = tmp_path / "exists.md"
        target_file.write_text("# exists", encoding="utf-8")
        test_file = tmp_path / "test.md"
        test_file.write_text('[链接](exists.md "标题")', encoding="utf-8")

        links = cl.parse_links(test_file)
        assert len(links) == 1
        url = links[0][1]
        assert url == "exists.md", f"URL应为exists.md，实际是'{url}'"

        checked_url, status, msg = cl.check_local_link(test_file, url)
        assert status == "ok", f"带标题的存在文件应通过检查，status='{status}', msg='{msg}'"
