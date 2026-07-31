"""lib.saas_doc_extractor 单元测试。

覆盖：
1. text_cleaner：零宽字符清理、行拆分、URL提取
2. platforms：平台检测、配置获取
3. models：数据模型字段、属性方法、meta字典
4. anti_patterns：提取前/后反模式检查
5. extractor：mock浏览器驱动的完整提取流程
"""

import sys as _sys
from pathlib import Path as _Path

_lib_parent = _Path(__file__).resolve().parent
while not (_lib_parent / "lib").is_dir():
    _lib_parent = _lib_parent.parent
_sys.path.insert(0, str(_lib_parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import pytest

from lib.saas_doc_extractor import (
    CONTENT_MIN_CHARS,
    CONTENT_MIN_LINES,
    EMPTY_LINE_RATIO_THRESHOLD,
    AntiPatternReport,
    ExtractionConfig,
    ExtractionResult,
    PlatformConfig,
    SaasDocExtractor,
    ZERO_WIDTH_CHARS,
    clean_text,
    detect_platform,
    extract_urls,
    get_platform_config,
    has_zero_width_chars,
    list_supported_platforms,
    split_lines,
)


# ============================================================
# Mock Page for testing extractor
# ============================================================

class MockPage:
    """Mock Playwright Page，实现evaluate/wait_for_timeout，模拟虚拟滚动容器。

    使用字符串特征检测来分派不同的JS调用，比正则更稳定。
    """

    def __init__(self, all_lines: list[str], container_sel: str = '.bear-web-x-container',
                 line_sel: str = '.ace-line', total_height: int = 4000,
                 viewport_height: int = 800, body_scrollable: bool = False,
                 zero_width_chance: float = 0.0):
        import random
        self.all_lines = list(all_lines)
        self.container_sel = container_sel
        self.line_sel = line_sel
        self.total_height = total_height
        self.viewport_height = viewport_height
        self.body_scrollable = body_scrollable
        self.zero_width_chance = zero_width_chance
        self.scroll_top = 0
        self.timeout_calls: list[int] = []
        self.evaluate_calls: list[str] = []
        self._random = random.Random(42)
        self._doc_title = "测试文档 - 飞书云文档"
        self._link_count = 2

    def wait_for_timeout(self, timeout: int) -> None:
        self.timeout_calls.append(timeout)

    def _get_visible_lines(self) -> list[str]:
        """模拟虚拟滚动：只有scrollTop附近的行在DOM中。"""
        line_height = 40
        buffer_lines = 5
        visible_lines_count = self.viewport_height // line_height  # 20
        first_visible = max(0, int(self.scroll_top / line_height) - buffer_lines)
        last_visible = min(len(self.all_lines),
                           first_visible + visible_lines_count + 2 * buffer_lines)
        visible = list(self.all_lines[first_visible:last_visible])
        if self.zero_width_chance > 0:
            visible = [self._inject_zwc(line) for line in visible]
        return visible

    def _inject_zwc(self, text: str) -> str:
        if self._random.random() < self.zero_width_chance and len(text) > 2:
            pos = self._random.randint(1, len(text) - 1)
            return text[:pos] + '\u200b' + text[pos:]
        return text

    def evaluate(self, expression: str, arg=None):
        self.evaluate_calls.append(expression[:100])

        # ---- 分派逻辑（按特征字符串精确匹配）----

        # 1. Body scrollable check
        if "document.body.scrollHeight > window.innerHeight" in expression:
            return self.body_scrollable

        # 2. Container info detection (returns dict with scrollHeight/clientHeight)
        if "scrollHeight" in expression and "clientHeight" in expression and "return {" in expression:
            # Check if selecting the right container - if querySelector returns null,
            # we should return null. But in base MockPage, container always exists.
            return {
                "tag": "DIV",
                "scrollHeight": self.total_height,
                "clientHeight": self.viewport_height,
                "scrollTop": self.scroll_top,
                "className": "bear-web-x-container catalogue-opened",
            }

        # 3. Line count detection (only the simple "return c.querySelectorAll('...').length" pattern)
        #    Must NOT contain forEach, a[href], innerText, or > (to distinguish from title check)
        if ("querySelectorAll" in expression and ".length" in expression
                and "forEach" not in expression and "a[href]" not in expression
                and "innerText" not in expression and ".length >" not in expression
                and "return {" not in expression):
            visible = self._get_visible_lines()
            return len(visible)

        # 4. Title extraction: lines[0].innerText (may have parentheses around it)
        if "lines[0].innerText" in expression:
            visible = self._get_visible_lines()
            return visible[0] if visible else ""

        # 5. document.title
        if "document.title" in expression:
            return self._doc_title

        # 6. Scroll to top
        if "scrollTo" in expression and "top: 0" in expression:
            self.scroll_top = 0
            return None

        # 7. Boundary check: bottom
        if "scrollTop + c.clientHeight >= c.scrollHeight - 10" in expression:
            return self.scroll_top + self.viewport_height >= self.total_height - 10

        # 8. Boundary check: top (the else branch with scrollTop <= 10)
        if "scrollTop <= 10" in expression and "'up'" in expression:
            return self.scroll_top <= 10

        # 9. scrollBy with positive step (down)
        if "scrollBy" in expression and "top:" in expression and "top: -" not in expression:
            import re
            m = re.search(r'top:\s*(\d+)', expression)
            if m:
                step = int(m.group(1))
                self.scroll_top = min(self.scroll_top + step,
                                      self.total_height - self.viewport_height)
            return None

        # 10. scrollBy with negative step (up)
        if "scrollBy" in expression and "top: -" in expression:
            import re
            m = re.search(r'top:\s*-(\d+)', expression)
            if m:
                step = int(m.group(1))
                self.scroll_top = max(0, self.scroll_top - step)
            return None

        # 11. Collect visible lines (has forEach + split)
        if "forEach" in expression and "split" in expression:
            visible = self._get_visible_lines()
            result = []
            for line in visible:
                result.extend(line.split('\n'))
            return result

        # 12. Link count (a[href])
        if "a[href]" in expression and ".length" in expression:
            return self._link_count

        # 13. scrollHeight getter
        if "return c ? c.scrollHeight : 0" in expression or "c.scrollHeight" in expression and "return" in expression and "clientHeight" not in expression:
            return self.total_height

        return None


class MockPageNoContainer(MockPage):
    """模拟容器不存在的页面（反模式：选择器失效）。"""

    def evaluate(self, expression, arg=None):
        self.evaluate_calls.append(expression[:100])

        if "document.body.scrollHeight > window.innerHeight" in expression:
            return False

        # Container info returns null
        if "scrollHeight" in expression and "clientHeight" in expression and "return {" in expression:
            return None

        # Line count returns 0
        if "querySelectorAll" in expression and ".length" in expression and "forEach" not in expression:
            return 0

        # Title returns empty
        if "lines.length > 0 ? lines[0].innerText" in expression:
            return ""

        if "document.title" in expression:
            return "无标题"

        # All scroll ops silently fail
        return None


class MockPageBodyScroll(MockPage):
    """模拟body可滚动而容器短的反模式页面。"""

    def evaluate(self, expression, arg=None):
        if "document.body.scrollHeight > window.innerHeight" in expression:
            return True  # body scrollable (anti-pattern)
        if "scrollHeight" in expression and "clientHeight" in expression and "return {" in expression:
            return {
                "tag": "DIV",
                "scrollHeight": 500,   # container too short
                "clientHeight": 800,
                "scrollTop": 0,
                "className": "bear-web-x-container",
            }
        return super().evaluate(expression, arg)


# ============================================================
# 1. text_cleaner 测试
# ============================================================

class TestTextCleaner:
    """文本清理工具函数测试。"""

    def test_clean_text_removes_zero_width_space(self):
        assert clean_text("Hello\u200bWorld") == "HelloWorld"

    def test_clean_text_removes_all_zero_width_variants(self):
        zwc_chars = ['\u200b', '\u200c', '\u200d', '\u200e', '\u200f',
                     '\u2028', '\u2029', '\u202a', '\u202b', '\u202c',
                     '\u202d', '\u202e', '\u202f', '\ufeff']
        for zwc in zwc_chars:
            assert clean_text(f"a{zwc}b") == "ab", f"Failed for U+{ord(zwc):04X}"

    def test_clean_text_strips_whitespace(self):
        assert clean_text("  hello  ") == "hello"
        assert clean_text("\thello\n") == "hello"

    def test_clean_text_empty_input(self):
        assert clean_text("") == ""
        assert clean_text(None) == ""

    def test_clean_text_preserves_normal_content(self):
        assert clean_text("Hello World 123!") == "Hello World 123!"
        assert clean_text("中文内容正常保留") == "中文内容正常保留"
        assert clean_text("含URL https://example.com/path?q=1 测试") == "含URL https://example.com/path?q=1 测试"

    def test_has_zero_width_chars_detection(self):
        assert has_zero_width_chars("hello\u200bworld") is True
        assert has_zero_width_chars("hello world") is False
        assert has_zero_width_chars("") is False

    def test_split_lines_normal(self):
        assert split_lines("line1\nline2\nline3") == ["line1", "line2", "line3"]

    def test_split_lines_with_empty_lines(self):
        assert split_lines("a\n\nb") == ["a", "b"]
        assert split_lines("\n\nhello\n\n") == ["hello"]

    def test_split_lines_with_zwc(self):
        result = split_lines("hello\u200b\nworld\u200c")
        assert result == ["hello", "world"]

    def test_split_lines_single_line(self):
        assert split_lines("no newline here") == ["no newline here"]

    def test_split_lines_empty(self):
        assert split_lines("") == []
        assert split_lines("\n\n\n") == []

    def test_extract_urls_basic(self):
        urls = extract_urls("visit https://example.com and http://test.org")
        assert "https://example.com" in urls
        assert "http://test.org" in urls

    def test_extract_urls_with_paths(self):
        urls = extract_urls("link: https://example.com/path/to/page?query=1&foo=bar")
        assert "https://example.com/path/to/page?query=1&foo=bar" in urls

    def test_extract_urls_deduplicates(self):
        urls = extract_urls("https://a.com and https://a.com again")
        assert urls.count("https://a.com") == 1

    def test_extract_urls_no_urls(self):
        assert extract_urls("no urls here, just text") == []

    def test_extract_urls_with_chinese_punctuation(self):
        urls = extract_urls("链接（https://example.com）和【https://test.org】")
        assert "https://example.com" in urls
        assert "https://test.org" in urls
        assert not any("）" in u for u in urls)
        assert not any("】" in u for u in urls)

    def test_extract_urls_empty(self):
        assert extract_urls("") == []
        assert extract_urls(None) == []


# ============================================================
# 2. platforms 测试
# ============================================================

class TestPlatforms:
    """平台检测与配置测试。"""

    def test_list_supported_platforms_nonempty(self):
        platforms = list_supported_platforms()
        assert len(platforms) >= 8
        names = [p[0] for p in platforms]
        assert "feishu" in names
        assert "dingtalk" in names
        assert "wecom" in names

    def test_list_platforms_returns_3tuple(self):
        for item in list_supported_platforms():
            assert len(item) == 3
            name, display, verified = item
            assert isinstance(name, str)
            assert isinstance(display, str)
            assert isinstance(verified, bool)

    def test_feishu_platform_verified(self):
        feishu = get_platform_config("feishu")
        assert feishu is not None
        assert feishu.verified is True
        assert feishu.container_selector == ".bear-web-x-container"
        assert feishu.line_selector == ".ace-line"
        assert feishu.scroll_step == 400
        assert feishu.wait_ms == 1500
        assert feishu.initial_wait_ms == 2000
        assert feishu.uses_virtual_scroll is True

    def test_other_platforms_unverified(self):
        for pname in ["dingtalk", "wecom", "yuque", "notion"]:
            p = get_platform_config(pname)
            if p:
                assert p.verified is False, f"{pname} should not be marked verified"

    def test_detect_platform_feishu_urls(self):
        assert detect_platform("https://bytedance.larkoffice.com/wiki/xxx") == "feishu"
        assert detect_platform("https://feishu.cn/docx/abc") == "feishu"
        assert detect_platform("https://xxx.larksuite.com/docx/def") == "feishu"
        assert detect_platform("https://xxx.larkoffice.com/docx/def") == "feishu"

    def test_detect_platform_dingtalk(self):
        assert detect_platform("https://alidocs.dingtalk.com/xxx") == "dingtalk"

    def test_detect_platform_wecom(self):
        assert detect_platform("https://doc.weixin.qq.com/xxx") == "wecom"
        assert detect_platform("https://work.weixin.qq.com/xxx") == "wecom"

    def test_detect_platform_yuque(self):
        assert detect_platform("https://yuque.com/xxx") == "yuque"

    def test_detect_platform_notion(self):
        assert detect_platform("https://notion.site/xxx") == "notion"

    def test_detect_platform_unknown(self):
        assert detect_platform("https://example.com/doc") is None
        assert detect_platform("https://google.com") is None
        assert detect_platform("") is None

    def test_get_platform_config_invalid(self):
        assert get_platform_config("nonexistent") is None
        assert get_platform_config("") is None

    def test_platform_config_selectors_list(self):
        feishu = get_platform_config("feishu")
        containers = feishu.get_container_selectors()
        assert ".bear-web-x-container" in containers
        assert len(containers) >= 2  # 主选+fallback
        lines = feishu.get_line_selectors()
        assert ".ace-line" in lines

    def test_platform_config_notes_not_empty(self):
        feishu = get_platform_config("feishu")
        assert len(feishu.notes) > 0


# ============================================================
# 3. models 测试
# ============================================================

class TestModels:
    """数据模型测试。"""

    def test_platform_config_defaults(self):
        cfg = PlatformConfig(
            name="test",
            display_name="测试平台",
            domains=["test.com"],
            container_selector=".container",
            line_selector=".line",
        )
        assert cfg.scroll_step == 400
        assert cfg.wait_ms == 1500
        assert cfg.initial_wait_ms == 2000
        assert cfg.max_iterations == 30
        assert cfg.uses_virtual_scroll is True
        assert cfg.body_is_scrollable is False
        assert cfg.verified is False
        assert cfg.container_selector_fallbacks == []
        assert cfg.line_selector_fallbacks == []

    def test_extraction_config_defaults(self):
        cfg = ExtractionConfig()
        feishu = get_platform_config("feishu")
        resolved = cfg.resolve(feishu)
        assert resolved.scroll_step == feishu.scroll_step
        assert resolved.wait_ms == feishu.wait_ms
        assert resolved.initial_wait_ms == feishu.initial_wait_ms
        assert resolved.max_no_new == feishu.max_no_new
        assert resolved.bidirectional_scan is True

    def test_extraction_config_override(self):
        cfg = ExtractionConfig(scroll_step=500, wait_ms=2000, verbose=True,
                               bidirectional_scan=False)
        feishu = get_platform_config("feishu")
        resolved = cfg.resolve(feishu)
        assert resolved.scroll_step == 500
        assert resolved.wait_ms == 2000
        assert resolved.initial_wait_ms == feishu.initial_wait_ms
        assert resolved.verbose is True
        assert resolved.bidirectional_scan is False

    def test_extraction_result_empty(self):
        r = ExtractionResult(url="https://test.com/doc", platform="feishu")
        # 空结果所有检查项默认False，success应为False
        assert r.success is False
        assert r.char_count == 0
        assert r.line_count == 0
        assert r.content == ""
        assert r.anti_pattern is not None
        assert r.anti_pattern.all_passed is False  # 默认所有检查未通过
        assert len(r.errors) == 0

    def test_extraction_result_content_is_property(self):
        """content是从lines计算的property，不可直接赋值。"""
        r = ExtractionResult(url="https://test.com", platform="feishu")
        r.lines = ["line1", "line2", "line3"]
        assert r.content == "line1\nline2\nline3"
        assert r.char_count == len("line1\nline2\nline3")

    def test_extraction_result_with_errors_fails(self):
        r = ExtractionResult(url="https://test.com", platform="feishu",
                             errors=["container not found"])
        assert r.success is False

    def test_extraction_result_passing_result(self):
        """构造一个模拟全部通过的结果。"""
        r = ExtractionResult(url="https://test.com", platform="feishu", title="测试文档")
        # 足够长的内容
        long_line = "这是一段足够长的测试内容。" * 20
        r.lines = [long_line] * 20
        r.urls_found = ["https://example.com"]
        # 模拟anti_pattern全通过
        r.anti_pattern = AntiPatternReport(
            container_exists=True,
            container_scrollable=True,
            antipattern_body_scroll=False,
            initial_lines_ok=True,
            content_min_lines=True,
            content_min_chars=True,
            title_exists=True,
            urls_found=1,
            empty_line_ratio=0.0,
            empty_line_ratio_ok=True,
            zerowidth_clean=True,
            has_selectors_effective=True,
        )
        assert r.success is True
        assert r.char_count > CONTENT_MIN_CHARS
        assert r.line_count == 20

    def test_extraction_result_to_meta_dict(self):
        feishu = get_platform_config("feishu")
        cfg = ExtractionConfig().resolve(feishu)
        r = ExtractionResult(url="https://test.com", platform="feishu", title="T",
                             lines=["a", "b"], scroll_iterations=5,
                             container_selector_used=".bear-web-x-container",
                             line_selector_used=".ace-line")
        meta = r.to_meta_dict(cfg)
        assert meta["url"] == "https://test.com"
        assert meta["platform"] == "feishu"
        assert meta["title"] == "T"
        assert meta["line_count"] == 2
        assert meta["scroll_iterations"] == 5
        assert "anti_pattern_checks" in meta
        assert "extraction_params" in meta
        assert meta["extraction_params"]["scroll_step"] == 400
        assert meta["selectors"]["container"] == ".bear-web-x-container"

    def test_anti_pattern_report_pass_count(self):
        report = AntiPatternReport(
            container_exists=True,
            container_scrollable=True,
            antipattern_body_scroll=False,
            initial_lines_ok=True,
        )
        # 4 explicit True, plus zerowidth_clean defaults True = 5
        assert report.pass_count == 5
        assert report.all_passed is False

        report2 = AntiPatternReport(
            container_exists=True, container_scrollable=True,
            antipattern_body_scroll=False, initial_lines_ok=True,
            content_min_lines=True, content_min_chars=True,
            title_exists=True, empty_line_ratio_ok=True,
            zerowidth_clean=True, has_selectors_effective=True,
        )
        assert report2.all_passed is True
        assert report2.pass_count == 10

    def test_anti_pattern_report_to_dict(self):
        report = AntiPatternReport(container_exists=True, title_exists=True)
        d = report.to_dict()
        assert d["container_exists"] is True
        assert d["title_exists"] is True
        assert "all_passed" in d
        assert "pass_count" in d
        assert "warnings" in d


# ============================================================
# 4. anti_patterns 测试
# ============================================================

class TestAntiPatterns:
    """反模式检查测试（纯Python逻辑，无需浏览器）。"""

    def _make_result(self, lines=None, platform_name="feishu"):
        from lib.saas_doc_extractor import run_post_extraction_checks, run_pre_extraction_checks
        platform = get_platform_config(platform_name)
        cfg = ExtractionConfig().resolve(platform)
        result = ExtractionResult(url="https://test.com", platform=platform_name)
        result.lines = lines or []
        return result, platform, cfg, run_pre_extraction_checks, run_post_extraction_checks

    def test_pre_check_container_missing(self):
        _, platform, _, pre, _ = self._make_result()
        result = ExtractionResult(url="https://test.com", platform="feishu")
        pre(None, 0, False, platform, result)
        assert result.anti_pattern.container_exists is False
        assert len(result.errors) > 0
        assert any("容器" in e for e in result.errors)

    def test_pre_check_container_not_scrollable(self):
        _, platform, _, pre, _ = self._make_result()
        result = ExtractionResult(url="https://test.com", platform="feishu")
        container_info = {"tag": "DIV", "scrollHeight": 500, "clientHeight": 800,
                          "className": "test", "scrollTop": 0}
        pre(container_info, 10, False, platform, result)
        assert result.anti_pattern.container_scrollable is False
        assert any("scrollHeight" in w for w in result.warnings)

    def test_pre_check_body_scroll_antipattern(self):
        _, platform, _, pre, _ = self._make_result()
        result = ExtractionResult(url="https://test.com", platform="feishu")
        container_info = {"tag": "DIV", "scrollHeight": 4000, "clientHeight": 800,
                          "className": "bear-web-x-container", "scrollTop": 0}
        pre(container_info, 15, True, platform, result)  # body_scrollable=True
        assert result.anti_pattern.antipattern_body_scroll is True
        assert any("body可滚动" in w or "反模式" in w for w in result.warnings)

    def test_pre_check_all_passed(self):
        _, platform, _, pre, _ = self._make_result()
        result = ExtractionResult(url="https://test.com", platform="feishu")
        container_info = {"tag": "DIV", "scrollHeight": 4000, "clientHeight": 800,
                          "className": "bear-web-x-container", "scrollTop": 0}
        pre(container_info, 20, False, platform, result)
        assert result.anti_pattern.container_exists is True
        assert result.anti_pattern.container_scrollable is True
        assert result.anti_pattern.antipattern_body_scroll is False
        assert result.anti_pattern.initial_lines_ok is True
        assert len(result.errors) == 0

    def test_pre_check_zero_initial_lines_warns(self):
        _, platform, _, pre, _ = self._make_result()
        result = ExtractionResult(url="https://test.com", platform="feishu")
        container_info = {"tag": "DIV", "scrollHeight": 4000, "clientHeight": 800,
                          "className": "bear-web-x-container", "scrollTop": 0}
        pre(container_info, 0, False, platform, result)
        assert result.anti_pattern.initial_lines_ok is False
        assert any("未找到" in w for w in result.warnings)

    def test_post_check_content_too_short(self):
        _, platform, cfg, _, post = self._make_result()
        result = ExtractionResult(url="https://test.com", platform="feishu", title="T")
        result.lines = ["short"]
        post(result, platform, cfg)
        assert result.anti_pattern.content_min_lines is False
        assert result.anti_pattern.content_min_chars is False

    def test_post_check_content_ok(self):
        _, platform, cfg, _, post = self._make_result()
        lines = []
        for i in range(20):
            lines.append(f"这是第{i+1}行内容，包含足够多的文字以通过阈值检查。" * 3)
        lines.append("参考链接：https://example.com/doc/1")
        result = ExtractionResult(url="https://test.com", platform="feishu", title="T")
        result.lines = lines
        post(result, platform, cfg)
        assert result.anti_pattern.content_min_lines is True
        assert result.anti_pattern.content_min_chars is True
        assert result.anti_pattern.title_exists is True
        assert result.anti_pattern.urls_found >= 1

    def test_post_check_high_empty_ratio(self):
        _, platform, cfg, _, post = self._make_result()
        # Very short lines, high empty ratio
        lines = ["a", "", "", "b", "", ""]
        result = ExtractionResult(url="https://test.com", platform="feishu", title="T")
        result.lines = lines
        post(result, platform, cfg)
        assert result.anti_pattern.empty_line_ratio > EMPTY_LINE_RATIO_THRESHOLD
        assert result.anti_pattern.empty_line_ratio_ok is False

    def test_post_check_zero_width_warning(self):
        _, platform, cfg, _, post = self._make_result()
        long_lines = []
        for i in range(20):
            long_lines.append(f"Line {i} with enough text to pass char threshold " * 5)
        long_lines.append("bad\u200bline " * 20)
        result = ExtractionResult(url="https://test.com", platform="feishu", title="T")
        result.lines = long_lines
        post(result, platform, cfg)
        assert result.anti_pattern.zerowidth_clean is False
        assert any("零宽字符" in w for w in result.warnings)

    def test_post_check_no_title_warns(self):
        _, platform, cfg, _, post = self._make_result()
        lines = [f"内容行{i}" for i in range(20)]
        result = ExtractionResult(url="https://test.com", platform="feishu")
        result.lines = lines  # title=""
        post(result, platform, cfg)
        assert result.anti_pattern.title_exists is False

    def test_post_check_urls_extracted(self):
        _, platform, cfg, _, post = self._make_result()
        lines = ["文档内容 " * 30]
        lines.append("链接：https://foo.com/bar 和 http://baz.org")
        result = ExtractionResult(url="https://test.com", platform="feishu", title="T")
        result.lines = lines
        post(result, platform, cfg)
        assert result.anti_pattern.urls_found >= 2
        assert "https://foo.com/bar" in result.urls_found


# ============================================================
# 5. extractor 测试（Mock Page）
# ============================================================

class TestExtractor:
    """核心提取器Mock测试。"""

    def _make_doc_lines(self, n: int = 50, with_url: bool = True) -> list[str]:
        lines = ["文档标题"]
        for i in range(1, n):
            if i == 5 and with_url:
                lines.append(f"参考链接：https://example.com/doc/{i}")
            else:
                lines.append(f"第{i}节内容：这是一段测试文字，用于验证虚拟滚动提取逻辑。段落编号{i}。")
        return lines

    def test_extract_basic_success(self):
        feishu = get_platform_config("feishu")
        lines = self._make_doc_lines(50)
        page = MockPage(all_lines=lines, total_height=4000)
        extractor = SaasDocExtractor(feishu, ExtractionConfig(verbose=False, max_iterations=60))
        result = extractor.extract(page, "https://test.com/doc")

        assert len(result.errors) == 0, f"Errors: {result.errors}"
        assert result.title == "文档标题"
        assert result.line_count >= 40, f"Only got {result.line_count} lines"
        assert result.char_count > CONTENT_MIN_CHARS
        assert result.scroll_iterations > 0
        # anti-pattern checks should pass for a healthy page
        assert result.anti_pattern.container_exists is True

    def test_extract_collects_urls_in_lines(self):
        feishu = get_platform_config("feishu")
        lines = self._make_doc_lines(50, with_url=True)
        page = MockPage(all_lines=lines, total_height=4000)
        extractor = SaasDocExtractor(feishu, ExtractionConfig(verbose=False, max_iterations=60))
        result = extractor.extract(page, "https://test.com/doc")
        # The URL line should be present
        assert any("example.com" in line for line in result.lines)

    def test_extract_cleans_zero_width_chars(self):
        feishu = get_platform_config("feishu")
        lines = self._make_doc_lines(50)
        page = MockPage(all_lines=lines, total_height=4000, zero_width_chance=0.8)
        extractor = SaasDocExtractor(feishu, ExtractionConfig(verbose=False, max_iterations=60))
        result = extractor.extract(page, "https://test.com/doc")

        # 结果内容不应包含零宽字符
        assert '\u200b' not in result.content
        assert all('\u200b' not in l for l in result.lines)
        assert all(not has_zero_width_chars(l) for l in result.lines)

    def test_extract_no_container_errors(self):
        feishu = get_platform_config("feishu")
        page = MockPageNoContainer(all_lines=[], total_height=0)
        extractor = SaasDocExtractor(feishu, ExtractionConfig(verbose=False))
        result = extractor.extract(page, "https://test.com/doc")
        assert result.success is False
        assert len(result.errors) > 0
        assert any("容器" in e for e in result.errors)

    def test_extract_body_scroll_warning(self):
        feishu = get_platform_config("feishu")
        lines = self._make_doc_lines(30)
        page = MockPageBodyScroll(all_lines=lines, total_height=500)
        extractor = SaasDocExtractor(feishu, ExtractionConfig(verbose=False, max_iterations=20))
        result = extractor.extract(page, "https://test.com/doc")
        assert any("body可滚动" in w or "反模式" in w for w in result.warnings)

    def test_extract_dedup_no_duplicates(self):
        """去重：结果中不应有重复行。"""
        feishu = get_platform_config("feishu")
        lines = [f"unique_line_{i:03d}" for i in range(40)]
        page = MockPage(all_lines=lines, total_height=3000)
        extractor = SaasDocExtractor(feishu, ExtractionConfig(verbose=False, max_iterations=40))
        result = extractor.extract(page, "https://test.com/doc")
        assert len(result.lines) == len(set(result.lines)), "Found duplicate lines"

    def test_extract_title_from_document_title_fallback(self):
        """当行选择器无法获取标题时，使用document.title fallback。"""
        feishu = get_platform_config("feishu")
        lines = self._make_doc_lines(30)
        page = MockPage(all_lines=lines, total_height=2500)
        page._doc_title = "Fallback标题 - 飞书云文档"
        extractor = SaasDocExtractor(feishu, ExtractionConfig(verbose=False, max_iterations=30))
        result = extractor.extract(page, "https://test.com/doc")
        assert result.title  # 应有标题

    def test_extract_records_selectors_used(self):
        feishu = get_platform_config("feishu")
        lines = self._make_doc_lines(30)
        page = MockPage(all_lines=lines, total_height=2500)
        extractor = SaasDocExtractor(feishu, ExtractionConfig(verbose=False, max_iterations=30))
        result = extractor.extract(page, "https://test.com/doc")
        assert result.container_selector_used == ".bear-web-x-container"
        assert result.line_selector_used == ".ace-line"
        assert result.used_fallback_container is False
        assert result.used_fallback_line is False

    def test_extract_waits_initial_render(self):
        """验证初始等待时间被调用。"""
        feishu = get_platform_config("feishu")
        lines = self._make_doc_lines(30)
        page = MockPage(all_lines=lines, total_height=2500)
        extractor = SaasDocExtractor(feishu, ExtractionConfig(
            verbose=False, max_iterations=30, initial_wait_ms=3000))
        result = extractor.extract(page, "https://test.com/doc")
        # 应至少有一次wait_for_timeout >= 2000ms（初始等待）
        assert any(t >= 2000 for t in page.timeout_calls)

    def test_extract_bidirectional_produces_more_or_equal(self):
        """双向扫描应不比单向下扫描差。"""
        feishu = get_platform_config("feishu")
        lines = self._make_doc_lines(80)

        page_bi = MockPage(all_lines=list(lines), total_height=5000)
        ext_bi = SaasDocExtractor(feishu, ExtractionConfig(verbose=False, max_iterations=50,
                                                           bidirectional_scan=True))
        r_bi = ext_bi.extract(page_bi, "https://test.com/doc")

        page_uni = MockPage(all_lines=list(lines), total_height=5000)
        ext_uni = SaasDocExtractor(feishu, ExtractionConfig(verbose=False, max_iterations=50,
                                                            bidirectional_scan=False))
        r_uni = ext_uni.extract(page_uni, "https://test.com/doc")

        assert r_bi.line_count >= r_uni.line_count, \
            f"Bi-di ({r_bi.line_count}) should be >= uni ({r_uni.line_count})"


# ============================================================
# 6. 常量和导出一致性测试
# ============================================================

class TestExports:
    """模块导出完整性测试。"""

    def test_zero_width_chars_compiled(self):
        import re
        assert isinstance(ZERO_WIDTH_CHARS, re.Pattern)

    def test_constants_values(self):
        assert CONTENT_MIN_LINES == 10
        assert CONTENT_MIN_CHARS == 200
        assert 0 < EMPTY_LINE_RATIO_THRESHOLD < 1

    def test_saas_doc_extractor_implements_protocol(self):
        """验证MockPage满足PageProtocol。"""
        from lib.saas_doc_extractor import PageProtocol
        page = MockPage(all_lines=["test"], total_height=500)
        assert isinstance(page, PageProtocol)
