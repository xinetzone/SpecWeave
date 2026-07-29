"""mermaid.common 模块单元测试。"""

import pytest

from lib.mermaid import common


class TestConstants:
    """常量和正则表达式测试。"""

    def test_mermaid_fence_re_matches(self):
        text = "```mermaid\ngraph TD\n    A --> B\n```"
        match = common.MERMAID_FENCE_RE.search(text)
        assert match is not None
        assert match.group(2).strip() == "graph TD\n    A --> B"

    def test_chinese_chars_re_detects_chinese(self):
        assert common.CHINESE_CHARS_RE.search("中文") is not None
        assert common.CHINESE_CHARS_RE.search("english") is None

    def test_list_trigger_re_matches(self):
        assert common.LIST_TRIGGER_RE.match("- item") is not None
        assert common.LIST_TRIGGER_RE.match("* item") is not None
        assert common.LIST_TRIGGER_RE.match("+ item") is not None
        assert common.LIST_TRIGGER_RE.match("1. item") is not None
        assert common.LIST_TRIGGER_RE.match("1． item") is not None
        assert common.LIST_TRIGGER_RE.match("1、 item") is not None
        assert common.LIST_TRIGGER_RE.match("normal text") is None

    def test_special_chars_contains_expected_chars(self):
        assert "@" in common.SPECIAL_CHARS
        assert "#" in common.SPECIAL_CHARS
        assert "≥" in common.SPECIAL_CHARS
        assert "≤" in common.SPECIAL_CHARS
        assert "+" in common.SPECIAL_CHARS


class TestDetectDiagramType:
    """diagram 类型检测测试。"""

    def test_flowchart(self):
        assert common.detect_diagram_type("graph TD\n    A --> B") == "flowchart"
        assert common.detect_diagram_type("flowchart TD\n    A --> B") == "flowchart"

    def test_statediagram(self):
        assert common.detect_diagram_type("stateDiagram-v2\n    [*] --> A") == "stateDiagram"
        assert common.detect_diagram_type("stateDiagram\n    [*] --> A") == "stateDiagram"

    def test_sequencediagram(self):
        assert common.detect_diagram_type("sequenceDiagram\n    A->>B: Hello") == "sequenceDiagram"

    def test_classdiagram(self):
        assert common.detect_diagram_type("classDiagram\n    class A") == "classDiagram"

    def test_erdiagram(self):
        assert common.detect_diagram_type("erDiagram\n    CUSTOMER ||--o{ ORDER") == "erDiagram"

    def test_pie(self):
        assert common.detect_diagram_type("pie title Pets\n    \"Dogs\": 386") == "pie"

    def test_gantt(self):
        assert common.detect_diagram_type("gantt\n    title A Gantt Diagram") == "gantt"

    def test_mindmap(self):
        assert common.detect_diagram_type("mindmap\n    root((Root))") == "mindmap"

    def test_timeline(self):
        assert common.detect_diagram_type("timeline\n    title History") == "timeline"

    def test_xychart_beta(self):
        assert common.detect_diagram_type("xychart-beta\n    title Test") == "xychart-beta"

    def test_quadrantchart(self):
        assert common.detect_diagram_type("quadrantChart\n    title Test") == "quadrantchart"

    def test_empty_returns_unknown(self):
        assert common.detect_diagram_type("") == "unknown"
        assert common.detect_diagram_type("   \n  \n  ") == "unknown"

    def test_unknown_defaults_to_flowchart(self):
        assert common.detect_diagram_type("someUnknownDiagram\n    stuff") == "flowchart"


class TestTextNeedsQuotes:
    """引号需求判断测试（通用文本）。"""

    def test_already_double_quoted(self):
        assert common.text_needs_quotes('"Hello"') is False

    def test_already_single_quoted(self):
        assert common.text_needs_quotes("'Hello'") is False

    def test_chinese_needs_quotes(self):
        assert common.text_needs_quotes("开始") is True
        assert common.text_needs_quotes("Hello 世界") is True

    def test_space_needs_quotes(self):
        assert common.text_needs_quotes("Hello World") is True
        assert common.text_needs_quotes("start end") is True

    def test_special_chars_needs_quotes(self):
        assert common.text_needs_quotes("a@b") is True
        assert common.text_needs_quotes("a#b") is True
        assert common.text_needs_quotes("a≥b") is True
        assert common.text_needs_quotes("a≤b") is True
        assert common.text_needs_quotes("a+b") is True

    def test_ascii_no_quotes(self):
        assert common.text_needs_quotes("StartNode") is False
        assert common.text_needs_quotes("node123") is False
        assert common.text_needs_quotes("A_B-C") is False

    def test_empty_stripped_space(self):
        assert common.text_needs_quotes("   ") is False


class TestStateTextNeedsQuotes:
    """状态图文本引号需求判断测试。"""

    def test_already_double_quoted(self):
        assert common.state_text_needs_quotes('"Hello"') is False

    def test_already_single_quoted(self):
        assert common.state_text_needs_quotes("'Hello'") is False

    def test_space_needs_quotes(self):
        assert common.state_text_needs_quotes("Hello World") is True

    def test_colon_needs_quotes(self):
        assert common.state_text_needs_quotes("state:name") is True

    def test_semicolon_needs_quotes(self):
        assert common.state_text_needs_quotes("state;name") is True

    def test_braces_needs_quotes(self):
        assert common.state_text_needs_quotes("{name}") is True

    def test_pipe_needs_quotes(self):
        assert common.state_text_needs_quotes("a|b") is True

    def test_arrow_needs_quotes(self):
        assert common.state_text_needs_quotes("a->b") is True

    def test_plain_ascii_no_quotes(self):
        assert common.state_text_needs_quotes("Idle") is False
        assert common.state_text_needs_quotes("State1") is False


class TestHasListTrigger:
    """列表触发检测测试。"""

    def test_dash_trigger(self):
        assert common.has_list_trigger("- item") is True

    def test_asterisk_trigger(self):
        assert common.has_list_trigger("* item") is True

    def test_plus_trigger(self):
        assert common.has_list_trigger("+ item") is True

    def test_numbered_trigger(self):
        assert common.has_list_trigger("1. item") is True
        assert common.has_list_trigger("2． item") is True
        assert common.has_list_trigger("3、 item") is True

    def test_no_trigger(self):
        assert common.has_list_trigger("normal text") is False
        assert common.has_list_trigger("nodeA") is False

    def test_strips_quotes_before_check(self):
        assert common.has_list_trigger('"- item"') is True
        assert common.has_list_trigger("'- item'") is True

    def test_strips_whitespace(self):
        assert common.has_list_trigger("  - item  ") is True


class TestLineFromOffset:
    """行号计算测试。"""

    def test_start_of_file(self):
        assert common.line_from_offset("hello", 0) == 1

    def test_after_newlines(self):
        text = "line1\nline2\nline3\n"
        assert common.line_from_offset(text, text.index("line1")) == 1
        assert common.line_from_offset(text, text.index("line2")) == 2
        assert common.line_from_offset(text, text.index("line3")) == 3

    def test_after_multiple_newlines(self):
        text = "a\nb\nc\nd"
        assert common.line_from_offset(text, 6) == 4

    def test_empty_content(self):
        assert common.line_from_offset("", 0) == 1


class TestStripInlineComment:
    """注释剥离测试。"""

    def test_comment_line_returns_empty(self):
        assert common.strip_inline_comment("%% this is a comment") == ""
        assert common.strip_inline_comment("  %% indented comment") == ""

    def test_inline_comment_stripped(self):
        assert common.strip_inline_comment("A --> B %% comment") == "A --> B "

    def test_no_comment_unchanged(self):
        assert common.strip_inline_comment("A --> B") == "A --> B"

    def test_indented_code_with_comment(self):
        assert common.strip_inline_comment("    A[Node] %% node comment") == "    A[Node] "

    def test_double_percent_in_text(self):
        assert common.strip_inline_comment("not a %% comment %% but split") == "not a "


class TestCheckEmptyLines:
    """空行检查测试。"""

    def test_no_empty_lines(self):
        issues = common.check_empty_lines("A\nB\nC", 1)
        assert issues == []

    def test_double_newline_error(self):
        issues = common.check_empty_lines("A\n\nB", 1)
        assert len(issues) == 1
        assert issues[0][0] == 1
        assert issues[0][1] == "error"
        assert "空行" in issues[0][2]

    def test_space_between_newlines_error(self):
        issues = common.check_empty_lines("A\n \nB", 5)
        assert len(issues) == 1
        assert issues[0][0] == 5
        assert issues[0][1] == "error"

    def test_start_line_respected(self):
        issues = common.check_empty_lines("A\n\nB", 10)
        assert issues[0][0] == 10

    def test_multiple_empty_lines_still_one_issue(self):
        issues = common.check_empty_lines("A\n\nB\n\nC", 1)
        assert len(issues) == 1


class TestCheckBackslashN:
    """\\n 检查测试。"""

    def test_no_backslash_n(self):
        issues = common.check_backslash_n("A --> B", 1)
        assert issues == []

    def test_finds_backslash_n(self):
        issues = common.check_backslash_n("A[Hello\\nWorld]", 1)
        assert len(issues) == 1
        assert issues[0][1] == "error"
        assert "\\n" in issues[0][2]
        assert "<br/>" in issues[0][2]

    def test_finds_multiple_backslash_n(self):
        issues = common.check_backslash_n("A[Hello\\nWorld\\nTest]", 1)
        assert len(issues) == 2

    def test_ignores_comments(self):
        issues = common.check_backslash_n("A --> B %% note with \\n", 1)
        assert issues == []

    def test_ignores_comment_lines(self):
        issues = common.check_backslash_n("%% this has \\n inside\nA --> B", 1)
        assert issues == []

    def test_line_numbers_correct(self):
        text = "A[One\\nTwo]\nB[Three\\nFour]"
        issues = common.check_backslash_n(text, 10)
        assert issues[0][0] == 10
        assert issues[1][0] == 11


class TestFixBackslashN:
    """\\n 修复测试。"""

    def test_replaces_backslash_n(self):
        text = "A[Hello\\nWorld]"
        fixed = common.fix_backslash_n(text)
        assert fixed == "A[Hello<br/>World]"

    def test_replaces_multiple(self):
        text = "A[Hello\\nWorld\\nTest]"
        fixed = common.fix_backslash_n(text)
        assert fixed == "A[Hello<br/>World<br/>Test]"

    def test_preserves_comments(self):
        text = "A --> B %% note with \\n"
        fixed = common.fix_backslash_n(text)
        assert "%% note with \\n" in fixed
        assert "<br/>" not in fixed.split("%%", 1)[1]

    def test_comment_lines_unchanged(self):
        text = "%% this is a comment with \\n"
        fixed = common.fix_backslash_n(text)
        assert fixed == text

    def test_indented_comment_line_unchanged(self):
        text = "    %% indented comment with \\n"
        fixed = common.fix_backslash_n(text)
        assert fixed == text

    def test_replaces_in_code_before_comment(self):
        text = "A[Hello\\nWorld] %% with comment"
        fixed = common.fix_backslash_n(text)
        assert fixed == "A[Hello<br/>World] %% with comment"


class TestFixEmptyLines:
    """空行修复测试。"""

    def test_removes_empty_lines(self):
        text = "A\n\nB"
        fixed = common.fix_empty_lines(text)
        assert fixed == "A\nB"

    def test_removes_spaced_empty_lines(self):
        text = "A\n \nB"
        fixed = common.fix_empty_lines(text)
        assert fixed == "A\nB"

    def test_removes_multiple_empty_lines(self):
        text = "A\n\n\nB\n\nC"
        fixed = common.fix_empty_lines(text)
        assert fixed == "A\nB\nC"

    def test_preserves_single_newlines(self):
        text = "A\nB\nC"
        fixed = common.fix_empty_lines(text)
        assert fixed == text

    def test_removes_tab_indented_empty_lines(self):
        text = "A\n\t\nB"
        fixed = common.fix_empty_lines(text)
        assert fixed == "A\nB"


class TestCheckListTrigger:
    """列表触发警告测试。"""

    def test_returns_warning_when_triggered(self):
        result = common.check_list_trigger("- item", 0, 1, "节点")
        assert result is not None
        assert result[1] == "warning"
        assert result[0] == 1
        assert "列表" in result[2]

    def test_returns_none_when_no_trigger(self):
        result = common.check_list_trigger("normal", 0, 1, "节点")
        assert result is None

    def test_line_offset_applied(self):
        result = common.check_list_trigger("- item", 5, 10, "标签")
        assert result[0] == 15

    def test_context_included_in_message(self):
        result = common.check_list_trigger("- item", 0, 1, "边标签")
        assert "边标签" in result[2]

    def test_text_truncated_in_message(self):
        long_text = "- " + "x" * 50
        result = common.check_list_trigger(long_text, 0, 1, "节点")
        assert len(result[2]) < 100


class TestStripMindmapShape:
    """思维导图形状剥离测试。"""

    def test_circle_shape(self):
        assert common.strip_mindmap_shape("((Root))") == "Root"

    def test_rounded_stadium_shape(self):
        assert common.strip_mindmap_shape("([Node])") == "Node"

    def test_subroutine_shape(self):
        assert common.strip_mindmap_shape("[[Node]]") == "Node"

    def test_bang_shape(self):
        assert common.strip_mindmap_shape(">(Node)") == "Node"

    def test_round_shape(self):
        assert common.strip_mindmap_shape("(Node)") == "Node"

    def test_square_shape(self):
        assert common.strip_mindmap_shape("[Node]") == "Node"

    def test_diamond_shape(self):
        assert common.strip_mindmap_shape("{Node}") == "Node"

    def test_plain_text(self):
        assert common.strip_mindmap_shape("plain") == "plain"

    def test_html_comment_returns_empty(self):
        assert common.strip_mindmap_shape("<!-- comment -->") == ""

    def test_node_with_id_dual_delims(self):
        assert common.strip_mindmap_shape("root((Center))") == "Center"
        assert common.strip_mindmap_shape("id((Center))") == "Center"
        assert common.strip_mindmap_shape("id[[Text]]") == "Text"
        assert common.strip_mindmap_shape("id>(Text)") == "Text"
        assert common.strip_mindmap_shape("([Standalone])") == "Standalone"

    def test_node_with_id_single_delims(self):
        assert common.strip_mindmap_shape("root(Center)") == "Center"
        assert common.strip_mindmap_shape("id[Text]") == "Text"
        assert common.strip_mindmap_shape("id{Text}") == "Text"

    def test_whitespace_stripped(self):
        assert common.strip_mindmap_shape("  ((Root))  ") == "Root"
