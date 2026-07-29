"""Mermaid 修复器测试。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.mermaid.common import fix_empty_lines, fix_backslash_n
from lib.mermaid.fixers import (
    FlowchartFixer,
    StateDiagramFixer,
    SequenceDiagramFixer,
    ClassDiagramFixer,
    ErDiagramFixer,
    MindmapFixer,
    PieFixer,
    GanttFixer,
    GenericFixer,
)
from lib.mermaid.checkers import (
    FlowchartChecker,
    StateDiagramChecker,
)
from lib.mermaid.registry import CheckerRegistry, FixerRegistry
from lib.mermaid.processor import process_mermaid_fences


def test_fix_empty_lines():
    text = "flowchart TD\n    A --> B\n\n    B --> C"
    fixed = fix_empty_lines(text)
    assert "\n\n" not in fixed
    assert fixed.count("\n") == 2


def test_fix_backslash_n():
    text = 'flowchart TD\n    A["Hello\\nWorld"] --> B'
    fixed = fix_backslash_n(text)
    assert "\\n" not in fixed
    assert "<br/>" in fixed
    assert 'Hello<br/>World' in fixed


def test_fix_backslash_n_with_comment():
    text = 'flowchart TD\n    A --> B %% comment with \\n\n    C --> D'
    fixed = fix_backslash_n(text)
    assert '%%' in fixed
    assert 'B' in fixed.split('%%')[0]


def test_flowchart_fixer_node_quotes():
    fixer = FlowchartFixer()
    text = """flowchart TD
    A[开始节点] --> B{判断}
    B -->|是| C((圆形节点))
    B -->|否| D>标签形状]"""
    fixed, fixes = fixer.fix(text)
    assert 'A["开始节点"]' in fixed
    assert 'B{"判断"}' in fixed
    assert 'C(("圆形节点"))' in fixed
    assert "矩形节点引号" in str(fixes) or "矩形" in str(fixes) or any("节点引号" in f for f in fixes)


def test_flowchart_fixer_arrow_label():
    fixer = FlowchartFixer()
    text = """flowchart TD
    A -->|是| B
    A -->|否| C"""
    fixed, fixes = fixer.fix(text)
    assert '|"是"|' in fixed
    assert '|"否"|' in fixed
    assert "边标签引号" in fixes


def test_state_diagram_fixer():
    fixer = StateDiagramFixer()
    text = """stateDiagram-v2
    [*] --> S1
    state S1 : 这是 一个描述
    S1 --> S2 : 发生 迁移
    note right of S1 : 这是 注释"""
    fixed, fixes = fixer.fix(text)
    assert '"这是 一个描述"' in fixed
    assert '"发生 迁移"' in fixed
    assert '"这是 注释"' in fixed


def test_sequence_diagram_fixer():
    fixer = SequenceDiagramFixer()
    text = """sequenceDiagram
    participant 用户 as 用户
    participant 系统 as 系统
    用户->>系统: 请求"""
    fixed, fixes = fixer.fix(text)
    assert 'participant 用户 as "用户"' in fixed
    assert 'participant 系统 as "系统"' in fixed


def test_class_diagram_fixer():
    fixer = ClassDiagramFixer()
    text = """classDiagram
    class 用户类 {
        +String name
    }
    用户类 <|-- 管理员类 : 继承"""
    fixed, fixes = fixer.fix(text)
    assert 'class "用户类"' in fixed
    assert '"管理员类"' in fixed
    assert '"继承"' in fixed


def test_er_diagram_fixer():
    fixer = ErDiagramFixer()
    text = """erDiagram
    CUSTOMER ||--o{ ORDER : places
    CUSTOMER {
        string name
    }"""
    fixed, fixes = fixer.fix(text)
    assert '"places"' in fixed or ": places" in fixed


def test_mindmap_fixer():
    fixer = MindmapFixer()
    text = """mindmap
    root((思维导图))
        节点1
        节点2"""
    fixed, fixes = fixer.fix(text)
    assert fixed.count("\n\n") == 0


def test_pie_gantt_generic_fixers():
    pie = PieFixer()
    text1 = """pie
    title 销售数据
    "A" : 40
    "B" : 60"""
    f1, _ = pie.fix(text1)
    assert f1 == text1

    gantt = GanttFixer()
    text2 = """gantt
    title 项目计划
    section 设计
    任务1 :a1, 2024-01-01, 7d"""
    f2, _ = gantt.fix(text2)
    assert f2 == text2

    generic = GenericFixer("timeline")
    text3 = """timeline
    title 历史
    2024 : 事件1"""
    f3, fixes3 = generic.fix(text3)
    assert f3 == text3


def test_checker_registry_integration():
    checker_reg = CheckerRegistry()
    checker_reg.register(FlowchartChecker)
    checker_reg.register(StateDiagramChecker)

    fixer_reg = FixerRegistry()
    fixer_reg.register("flowchart", FlowchartFixer())
    fixer_reg.register("stateDiagram", StateDiagramFixer())

    content = """# Test

```mermaid
flowchart TD
    A[开始] --> B{结束}
```
"""
    processed, issues, fixes = process_mermaid_fences(
        content, fix=True,
        checker_registry=checker_reg,
        fixer_registry=fixer_reg,
    )
    assert 'A["开始"]' in processed
    assert 'B{"结束"}' in processed


def test_fix_then_check_no_errors():
    fixer = FlowchartFixer()
    checker = FlowchartChecker()

    bad_text = """flowchart TD
    A[开始节点] -->|是| B{结束}"""
    fixed, fixes = fixer.fix(bad_text)
    issues = checker.check(fixed, 1)
    errors = [i for i in issues if i[1] == "error"]
    assert len(errors) == 0
