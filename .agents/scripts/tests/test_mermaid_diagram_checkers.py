# 版本校验：导入共享库
import sys as _sys
from pathlib import Path as _Path
_lib_parent = _Path(__file__).resolve().parent
while not (_lib_parent / "lib").is_dir():
    _lib_parent = _lib_parent.parent
_sys.path.insert(0, str(_lib_parent / "lib"))

from python310_version_check import enforce_python310

enforce_python310()

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.mermaid.checkers import (
    FlowchartChecker,
    StateDiagramChecker,
    SequenceDiagramChecker,
    ClassDiagramChecker,
    ErDiagramChecker,
    MindmapChecker,
    PieChecker,
    GanttChecker,
    TimelineChecker,
    XyChartChecker,
    QuadrantChecker,
)


class TestFlowchartChecker:
    def setup_method(self):
        self.checker = FlowchartChecker()

    def test_get_diagram_type(self):
        assert self.checker.get_diagram_type() == "flowchart"

    def test_valid_flowchart_no_errors(self):
        block = """flowchart TD
    A["开始"] --> B["处理"]
    B --> C["结束"]
"""
        issues = self.checker.check(block, 1)
        errors = [i for i in issues if i[1] == "error"]
        assert len(errors) == 0

    def test_subgraph_chinese_id_error(self):
        block = """flowchart TD
    subgraph 中文子图
        A --> B
    end
"""
        issues = self.checker.check(block, 1)
        errors = [i for i in issues if i[1] == "error"]
        assert len(errors) >= 1
        assert any("subgraph" in i[2] for i in errors)

    def test_node_chinese_no_quotes_error(self):
        block = """flowchart TD
    A[中文节点] --> B
"""
        issues = self.checker.check(block, 1)
        errors = [i for i in issues if i[1] == "error"]
        assert len(errors) >= 1
        assert any("节点" in i[2] for i in errors)


class TestStateDiagramChecker:
    def setup_method(self):
        self.checker = StateDiagramChecker()

    def test_get_diagram_type(self):
        assert self.checker.get_diagram_type() == "stateDiagram"

    def test_valid_state_diagram_no_errors(self):
        block = """stateDiagram-v2
    [*] --> "状态A"
    "状态A" --> "状态B" : "转换"
    "状态B" --> [*]
"""
        issues = self.checker.check(block, 1)
        errors = [i for i in issues if i[1] == "error"]
        assert len(errors) == 0

    def test_state_description_no_quotes_error(self):
        block = """stateDiagram-v2
    state S1 : 描述 带空格
"""
        issues = self.checker.check(block, 1)
        errors = [i for i in issues if i[1] == "error"]
        assert len(errors) >= 1
        assert any("state" in i[2] for i in errors)


class TestSequenceDiagramChecker:
    def setup_method(self):
        self.checker = SequenceDiagramChecker()

    def test_get_diagram_type(self):
        assert self.checker.get_diagram_type() == "sequenceDiagram"

    def test_valid_sequence_diagram_no_errors(self):
        block = """sequenceDiagram
    participant A as "用户"
    participant B as "系统"
    A->>B: 请求
    B->>A: 响应
"""
        issues = self.checker.check(block, 1)
        errors = [i for i in issues if i[1] == "error"]
        assert len(errors) == 0

    def test_participant_alias_chinese_no_quotes_error(self):
        block = """sequenceDiagram
    participant A as 用户
"""
        issues = self.checker.check(block, 1)
        errors = [i for i in issues if i[1] == "error"]
        assert len(errors) >= 1
        assert any("participant" in i[2] for i in errors)


class TestClassDiagramChecker:
    def setup_method(self):
        self.checker = ClassDiagramChecker()

    def test_get_diagram_type(self):
        assert self.checker.get_diagram_type() == "classDiagram"

    def test_valid_class_diagram_no_errors(self):
        block = """classDiagram
    class "用户" {
        +String name
        +int age
    }
    "用户" --> "订单" : "拥有"
"""
        issues = self.checker.check(block, 1)
        errors = [i for i in issues if i[1] == "error"]
        assert len(errors) == 0

    def test_class_name_chinese_no_quotes_error(self):
        block = """classDiagram
    class 用户 {
        +String name
    }
"""
        issues = self.checker.check(block, 1)
        errors = [i for i in issues if i[1] == "error"]
        assert len(errors) >= 1
        assert any("类名" in i[2] for i in errors)


class TestErDiagramChecker:
    def setup_method(self):
        self.checker = ErDiagramChecker()

    def test_get_diagram_type(self):
        assert self.checker.get_diagram_type() == "erDiagram"

    def test_valid_er_diagram_no_errors(self):
        block = """erDiagram
    CUSTOMER {
        string name
        string id
    }
    CUSTOMER ||--o{ ORDER : "places"
"""
        issues = self.checker.check(block, 1)
        errors = [i for i in issues if i[1] == "error"]
        assert len(errors) == 0

    def test_entity_name_chinese_no_quotes_error(self):
        block = """erDiagram
    客户 {
        string name
    }
"""
        issues = self.checker.check(block, 1)
        errors = [i for i in issues if i[1] == "error"]
        assert len(errors) >= 1
        assert any("实体名" in i[2] for i in errors)


class TestMindmapChecker:
    def setup_method(self):
        self.checker = MindmapChecker()

    def test_get_diagram_type(self):
        assert self.checker.get_diagram_type() == "mindmap"

    def test_valid_mindmap_no_errors(self):
        block = """mindmap
    root((中心))
        分支1
        分支2
"""
        issues = self.checker.check(block, 1)
        errors = [i for i in issues if i[1] == "error"]
        assert len(errors) == 0


class TestPieChecker:
    def setup_method(self):
        self.checker = PieChecker()

    def test_get_diagram_type(self):
        assert self.checker.get_diagram_type() == "pie"

    def test_valid_pie_no_errors(self):
        block = """pie title 测试数据
    "A" : 40
    "B" : 60
"""
        issues = self.checker.check(block, 1)
        errors = [i for i in issues if i[1] == "error"]
        assert len(errors) == 0


class TestGanttChecker:
    def setup_method(self):
        self.checker = GanttChecker()

    def test_get_diagram_type(self):
        assert self.checker.get_diagram_type() == "gantt"

    def test_valid_gantt_no_errors(self):
        block = """gantt
    title 项目计划
    dateFormat  YYYY-MM-DD
    section 阶段1
    任务1 :a1, 2024-01-01, 7d
"""
        issues = self.checker.check(block, 1)
        errors = [i for i in issues if i[1] == "error"]
        assert len(errors) == 0

    def test_gantt_title_with_quotes_warning(self):
        block = """gantt
    title "带引号的标题"
    dateFormat YYYY-MM-DD
"""
        issues = self.checker.check(block, 1)
        warnings = [i for i in issues if i[1] == "warning"]
        assert len(warnings) >= 1
        assert any("title" in i[2] for i in warnings)


class TestTimelineChecker:
    def setup_method(self):
        self.checker = TimelineChecker()

    def test_get_diagram_type(self):
        assert self.checker.get_diagram_type() == "timeline"

    def test_valid_timeline_no_errors(self):
        block = """timeline
    title 历史时间线
    2020 : 事件1
    2021 : 事件2
"""
        issues = self.checker.check(block, 1)
        errors = [i for i in issues if i[1] == "error"]
        assert len(errors) == 0


class TestXyChartChecker:
    def setup_method(self):
        self.checker = XyChartChecker()

    def test_get_diagram_type(self):
        assert self.checker.get_diagram_type() == "xychart-beta"

    def test_valid_xychart_no_errors(self):
        block = """xychart-beta
    title "销售数据"
    x-axis [jan, feb, mar]
    y-axis "销售额" 0 --> 100
    bar [10, 20, 30]
"""
        issues = self.checker.check(block, 1)
        errors = [i for i in issues if i[1] == "error"]
        assert len(errors) == 0


class TestQuadrantChecker:
    def setup_method(self):
        self.checker = QuadrantChecker()

    def test_get_diagram_type(self):
        assert self.checker.get_diagram_type() == "quadrantchart"

    def test_valid_quadrant_no_errors(self):
        block = """quadrantChart
    title 优先级矩阵
    x-axis 低 --> 高
    y-axis 低 --> 高
    quadrant-1 重要紧急
"""
        issues = self.checker.check(block, 1)
        errors = [i for i in issues if i[1] == "error"]
        assert len(errors) == 0

