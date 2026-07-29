"""mermaid 重构版 checkers 模块单元测试。"""


# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_lib_parent = _Path(__file__).resolve().parent
while not (_lib_parent / "lib").is_dir():
    _lib_parent = _lib_parent.parent
_sys.path.insert(0, str(_lib_parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import pytest

from lib.mermaid.checkers import BaseDiagramChecker, SecurityChecker


class TestBaseDiagramChecker:
    def test_abstract_class_cannot_instantiate(self):
        with pytest.raises(TypeError):
            BaseDiagramChecker()

    def test_concrete_subclass_works(self):
        class TestChecker(BaseDiagramChecker):
            def get_diagram_type(self):
                return "test"

            def _check_specific_rules(self, block_text, start_line):
                return [(start_line, "warning", "specific rule")]

        checker = TestChecker()
        assert checker.get_diagram_type() == "test"

    def test_default_checks_empty_lines(self):
        class TestChecker(BaseDiagramChecker):
            def get_diagram_type(self):
                return "test"

            def _check_specific_rules(self, block_text, start_line):
                return []

        checker = TestChecker()
        block_with_empty_line = "graph TD\n    A --> B\n\n    B --> C\n"
        issues = checker.check(block_with_empty_line, start_line=1)
        assert len(issues) >= 1
        assert any(i[1] == "error" and "空行" in i[2] for i in issues)

    def test_check_flow_order(self):
        call_order = []

        class OrderChecker(BaseDiagramChecker):
            def get_diagram_type(self):
                return "order"

            def _check_specific_rules(self, block_text, start_line):
                call_order.append("specific")
                return []

        checker = OrderChecker()
        original_empty = __import__('lib.mermaid.common', fromlist=['check_empty_lines']).check_empty_lines
        original_backslash = __import__('lib.mermaid.common', fromlist=['check_backslash_n']).check_backslash_n

        def track_empty(b, s):
            call_order.append("empty")
            return original_empty(b, s)

        def track_backslash(b, s):
            call_order.append("backslash")
            return original_backslash(b, s)

        import lib.mermaid.checkers.base as base_mod
        base_mod.check_empty_lines = track_empty
        base_mod.check_backslash_n = track_backslash

        try:
            checker.check("graph TD\nA-->B\n", start_line=1)
            assert call_order[0] == "empty"
            assert call_order[1] == "specific"
            assert call_order[2] == "backslash"
        finally:
            base_mod.check_empty_lines = original_empty
            base_mod.check_backslash_n = original_backslash


class TestSecurityChecker:
    @pytest.fixture
    def checker(self):
        return SecurityChecker()

    def test_clean_block_no_issues(self, checker):
        block = "graph TD\n    A --> B\n    B --> C\n"
        issues = checker.check(block, start_line=1)
        assert len(issues) == 0

    def test_detects_script_tag(self, checker):
        block = "graph TD\n    A[<script>alert(1)</script>] --> B\n"
        issues = checker.check(block, start_line=1)
        assert len(issues) == 1
        assert issues[0][1] == "error"
        assert "script" in issues[0][2]

    def test_detects_click_event(self, checker):
        block = "graph TD\n    click A callback\n    A --> B\n"
        issues = checker.check(block, start_line=1)
        assert len(issues) == 1
        assert "click" in issues[0][2]

    def test_detects_javascript_url(self, checker):
        block = "graph TD\n    A-->B\n    click A href \"javascript:alert(1)\"\n"
        issues = checker.check(block, start_line=1)
        assert any("javascript:" in i[2] for i in issues)

    def test_detects_on_event_handler(self, checker):
        block = "graph TD\n    A[<img src=x onerror=alert(1)>] --> B\n"
        issues = checker.check(block, start_line=1)
        assert any("on*" in i[2] or "事件处理器" in i[2] for i in issues)

    def test_detects_end_as_node(self, checker):
        block = "graph TD\n    start --> end(\n    end --> finish\n"
        issues = checker.check(block, start_line=1)
        assert any('"end"' in i[2] or "保留字" in i[2] for i in issues)

    def test_ignores_comments(self, checker):
        block = "graph TD\n    %% click A callback\n    %% <script>bad</script>\n    A --> B\n"
        issues = checker.check(block, start_line=1)
        assert len(issues) == 0

    def test_detects_dangerous_tags_img(self, checker):
        block = "graph TD\n    A[<img src=x>] --> B\n"
        issues = checker.check(block, start_line=1)
        assert len(issues) >= 1
        assert any("img" in i[2] or "危险 HTML" in i[2] for i in issues)

    def test_detects_iframe(self, checker):
        block = "graph TD\n    A[<iframe src=x>] --> B\n"
        issues = checker.check(block, start_line=1)
        assert any("iframe" in i[2] for i in issues)

