"""lib.seven_concepts 模块单元测试。

直接 import 测试，无子进程调用。
覆盖：核心场景匹配、置信度排序、MatchResult字段、边界情况、格式化函数、反模式、公开API。
"""

import sys
from pathlib import Path

import pytest

# conftest.py 已将 scripts 目录加入 sys.path，此处冗余保险
SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.seven_concepts import (
    ANTI_PATTERN_WARNINGS,
    CONCEPTS,
    QUALITY_GATES,
    WORKFLOWS,
    MatchResult,
    format_match_result,
    format_match_result_dict,
    format_scenario_list,
    get_all_scenarios,
    match_task,
)


class TestCoreScenarios:
    """核心场景匹配：每个工作流场景被正确匹配。"""

    def test_w1_milestone(self):
        results = match_task("Sprint结束做复盘")
        assert len(results) >= 1
        r = results[0]
        assert "里程碑" in r.scenario
        assert r.confidence == 95
        assert r.workflow == "W1"
        assert r.concepts == ["R", "I", "E", "C"]

    def test_p0_emergency(self):
        results = match_task("线上支付挂了P0")
        assert len(results) >= 1
        r = results[0]
        assert "P0" in r.scenario
        assert r.confidence == 98
        assert r.workflow is None

    def test_w2_bug_fix(self):
        results = match_task("修复线上空指针异常Bug")
        assert len(results) >= 1
        r = results[0]
        assert ("问题解决" in r.scenario) or ("故障" in r.scenario)
        assert r.workflow == "W2"
        for c in ["F", "V", "C"]:
            assert c in r.concepts

    def test_w3_refactor(self):
        results = match_task("重构超长文档做原子化拆分")
        assert len(results) >= 1
        r = results[0]
        assert "重构" in r.scenario
        assert r.workflow == "W3"

    def test_w4_knowledge(self):
        results = match_task("把踩坑经验沉淀成模式")
        assert len(results) >= 1
        r = results[0]
        assert "知识沉淀" in r.scenario
        assert r.workflow == "W4"

    def test_w5_architecture(self):
        results = match_task("选Redis还是MongoDB做技术选型")
        assert len(results) >= 1
        r = results[0]
        assert "架构" in r.scenario
        assert r.workflow == "W5"

    def test_simple_modification(self):
        results = match_task("fix typo改个错别字")
        assert len(results) >= 1
        r = results[0]
        assert "简单" in r.scenario
        assert r.confidence == 95
        assert r.concepts == ["C"]

    def test_no_match(self):
        results = match_task("做个蛋糕")
        assert len(results) >= 1
        r = results[0]
        assert "无匹配" in r.scenario
        assert r.confidence == 20


class TestConfidenceOrdering:
    """置信度排序：多结果按 confidence 降序排列。"""

    def test_multiple_results_descending(self):
        results = match_task("重构 知识沉淀 技术选型")
        assert len(results) >= 3
        assert results[0].confidence >= results[1].confidence
        assert results[1].confidence >= results[2].confidence


class TestMatchResultFields:
    """MatchResult 字段完整性。"""

    def test_all_fields_accessible(self):
        r = MatchResult(
            scenario="测试场景",
            confidence=80,
            concepts=["R", "I"],
            workflow="W1",
            notes="备注",
            quality_gates=["G1"],
            anti_patterns=["AP9"],
        )
        assert r.scenario == "测试场景"
        assert r.confidence == 80
        assert r.concepts == ["R", "I"]
        assert r.workflow == "W1"
        assert r.notes == "备注"
        assert r.quality_gates == ["G1"]
        assert r.anti_patterns == ["AP9"]

    def test_default_values(self):
        r = MatchResult(scenario="测试", confidence=50, concepts=[], workflow=None)
        assert r.notes == ""
        assert r.quality_gates == []
        assert r.anti_patterns == []

    def test_quality_gates_nonempty_when_workflow(self):
        results = match_task("Sprint结束做复盘")
        r = results[0]
        assert r.workflow == "W1"
        assert len(r.quality_gates) == 3


class TestEdgeCases:
    """边界情况。"""

    def test_empty_string(self):
        results = match_task("")
        assert isinstance(results, list)
        # 不崩溃即可，可能匹配"无匹配"
        assert len(results) >= 1

    def test_pure_english(self):
        results = match_task("fix bug")
        assert isinstance(results, list)
        assert len(results) >= 1

    def test_mixed_chinese_english(self):
        results = match_task("做个PR Code Review")
        assert len(results) >= 1
        matched = any("代码审查" in r.scenario for r in results)
        assert matched

    def test_super_long_text(self):
        results = match_task("Sprint结束做复盘" * 100)
        assert len(results) >= 1
        r = results[0]
        assert "里程碑" in r.scenario


class TestFormatters:
    """格式化函数。"""

    def test_format_match_result_basic(self):
        results = match_task("Sprint结束做复盘")
        s = format_match_result(results[0])
        assert isinstance(s, str)
        assert len(s) > 0
        assert "🎯 场景" in s
        assert "置信度" in s

    def test_format_match_result_with_index(self):
        results = match_task("Sprint结束做复盘")
        s = format_match_result(results[0], index=1)
        assert "[Top2]" in s

    def test_format_scenario_list(self):
        s = format_scenario_list()
        assert isinstance(s, str)
        assert len(s) > 0
        assert "支持的场景列表" in s
        assert "18" in s

    def test_format_match_result_dict(self):
        results = match_task("Sprint结束做复盘")
        d = format_match_result_dict(results[0])
        assert isinstance(d, dict)
        assert len(d) == 7
        for key in ["scenario", "confidence", "concepts", "workflow", "notes", "quality_gates", "anti_patterns"]:
            assert key in d


class TestAntiPatterns:
    """反模式检测。"""

    def test_rule_engine_has_ap9(self):
        results = match_task("写一个关键词匹配规则引擎")
        assert len(results) >= 1
        has_ap9 = any("AP9" in r.anti_patterns for r in results)
        assert has_ap9

    def test_ci_optimization_no_antipattern(self):
        results = match_task("优化CI构建速度")
        assert len(results) >= 1
        r = results[0]
        assert r.anti_patterns == []


class TestPublicAPI:
    """公开API可用性。"""

    def test_constants_importable(self):
        assert CONCEPTS is not None
        assert WORKFLOWS is not None
        assert QUALITY_GATES is not None
        assert ANTI_PATTERN_WARNINGS is not None

    def test_concepts_has_seven_keys(self):
        assert len(CONCEPTS) == 7

    def test_workflows_has_five_keys(self):
        assert len(WORKFLOWS) == 5

    def test_get_all_scenarios_returns_eighteen(self):
        scenarios = get_all_scenarios()
        assert len(scenarios) == 18
