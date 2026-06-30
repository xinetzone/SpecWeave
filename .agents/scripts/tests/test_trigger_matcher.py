"""trigger_matcher 单元测试：覆盖 T0/T1/T2 三级信号匹配与嵌套场景。

测试重点：
1. 11个命中词的逐词匹配验证（T0:3 + T1:4 + T2:4）
2. T2动宾组合嵌套包含T1名词和T0泛词的场景
3. 加载决策链路（T2>T1>T0）
"""

import pytest

from trigger_matcher import (
    TriggerTier,
    TierMatchResult,
    Logger,
    parse_skill_triggers,
    match_tier,
    match_input,
)


# mermaid-cmd 真实触发词配置（与 SKILL.md 保持一致）
T0_TRIGGERS = ["图", "可视化", "画", "图表"]
T1_TRIGGERS = ["mermaid", "流程图", "时序图", "状态图", "架构图", "ER图", "类图", "甘特图", "饼图", "UML图", "思维导图"]
T2_TRIGGERS = ["画个图", "画流程图", "检查mermaid", "修复图表", "生成时序图", "流程可视化", "mermaid图"]

T0_ACTION = '不主动加载L1；响应时提示"可用 mermaid-cmd"'
T1_ACTION = "加载本SKILL.md（L1），按§4决策树执行"
T2_ACTION = "加载L1 + 预加载L2（commands/mermaid.md）"


@pytest.fixture
def t0_tier():
    return TriggerTier(level="T0", name="弱信号", triggers=T0_TRIGGERS, action=T0_ACTION)


@pytest.fixture
def t1_tier():
    return TriggerTier(level="T1", name="中信号", triggers=T1_TRIGGERS, action=T1_ACTION)


@pytest.fixture
def t2_tier():
    return TriggerTier(level="T2", name="强信号", triggers=T2_TRIGGERS, action=T2_ACTION)


@pytest.fixture
def all_tiers(t0_tier, t1_tier, t2_tier):
    return {"T0": t0_tier, "T1": t1_tier, "T2": t2_tier}


@pytest.fixture
def silent_logger():
    """静默日志器，不输出到stdout，仅记录entries"""
    return Logger(json_mode=True)


class TestParseSkillTriggers:
    """parse_skill_triggers 解析测试"""

    def test_parses_all_three_tiers(self, tmp_path):
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text(
            "| **T0 弱信号** | 领域泛词 | `图`、`画` | 不加载 |\n"
            "| **T1 中信号** | 领域名词 | `流程图`、`时序图` | 加载L1 |\n"
            "| **T2 强信号** | 动宾组合 | `画流程图` | 加载L1+L2 |\n",
            encoding="utf-8",
        )
        tiers = parse_skill_triggers(skill_md)
        assert set(tiers.keys()) == {"T0", "T1", "T2"}

    def test_parses_t0_triggers(self, tmp_path):
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text(
            "| **T0 弱信号** | 泛词 | `图`、`可视化`、`画`、`图表` | 不加载 |\n",
            encoding="utf-8",
        )
        tiers = parse_skill_triggers(skill_md)
        assert tiers["T0"].triggers == ["图", "可视化", "画", "图表"]

    def test_parses_t2_action(self, tmp_path):
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text(
            "| **T2 强信号** | 动宾 | `画流程图` | 加载L1 + 预加载L2 |\n",
            encoding="utf-8",
        )
        tiers = parse_skill_triggers(skill_md)
        assert "加载L1" in tiers["T2"].action

    def test_returns_empty_for_no_tiers(self, tmp_path):
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text("# 普通文档\n无三级信号表格", encoding="utf-8")
        tiers = parse_skill_triggers(skill_md)
        assert tiers == {}


class TestTierMatchSingle:
    """单信号级匹配测试"""

    def test_t0_match_single_图(self, t0_tier, silent_logger):
        result = match_tier("这个图不错", t0_tier, silent_logger)
        assert result.is_matched
        assert "图" in result.matched

    def test_t0_match_single_可视化(self, t0_tier, silent_logger):
        result = match_tier("数据可视化", t0_tier, silent_logger)
        assert "可视化" in result.matched

    def test_t1_match_single_架构图(self, t1_tier, silent_logger):
        result = match_tier("画个架构图", t1_tier, silent_logger)
        assert "架构图" in result.matched

    def test_t1_match_single_mermaid(self, t1_tier, silent_logger):
        result = match_tier("用mermaid画", t1_tier, silent_logger)
        assert "mermaid" in result.matched

    def test_t2_match_single_生成时序图(self, t2_tier, silent_logger):
        result = match_tier("生成时序图", t2_tier, silent_logger)
        assert "生成时序图" in result.matched

    def test_t2_match_single_检查mermaid(self, t2_tier, silent_logger):
        result = match_tier("请检查mermaid语法", t2_tier, silent_logger)
        assert "检查mermaid" in result.matched

    def test_t0_no_match(self, t0_tier, silent_logger):
        result = match_tier("今天天气真好", t0_tier, silent_logger)
        assert not result.is_matched
        assert result.matched == []

    def test_t1_no_match(self, t1_tier, silent_logger):
        result = match_tier("今天天气真好", t1_tier, silent_logger)
        assert not result.is_matched

    def test_t2_no_match(self, t2_tier, silent_logger):
        result = match_tier("今天天气真好", t2_tier, silent_logger)
        assert not result.is_matched

    def test_unmatched_list_populated(self, t0_tier, silent_logger):
        result = match_tier("图", t0_tier, silent_logger)
        assert "图" in result.matched
        assert "可视化" in result.unmatched
        assert "画" in result.unmatched
        assert "图表" in result.unmatched
        assert len(result.unmatched) == 3


class TestNestedMatching:
    """T0/T1/T2 嵌套场景测试：T2动宾组合天然包含T1名词和T0泛词"""

    def test_nested_画流程图_contains_t1_流程图_and_t0_画(self, t0_tier, t1_tier, t2_tier, silent_logger):
        """画流程图(T2) → 内含 流程图(T1) + 画(T0)"""
        text = "画流程图"
        r0 = match_tier(text, t0_tier, silent_logger)
        r1 = match_tier(text, t1_tier, silent_logger)
        r2 = match_tier(text, t2_tier, silent_logger)

        assert "画流程图" in r2.matched
        assert "流程图" in r1.matched
        assert "画" in r0.matched

    def test_nested_生成时序图_contains_t1_时序图_and_t0_图(self, t0_tier, t1_tier, t2_tier, silent_logger):
        """生成时序图(T2) → 内含 时序图(T1) + 图(T0)"""
        text = "生成时序图"
        r0 = match_tier(text, t0_tier, silent_logger)
        r1 = match_tier(text, t1_tier, silent_logger)
        r2 = match_tier(text, t2_tier, silent_logger)

        assert "生成时序图" in r2.matched
        assert "时序图" in r1.matched
        assert "图" in r0.matched

    def test_nested_检查mermaid_contains_t1_mermaid(self, t1_tier, t2_tier, silent_logger):
        """检查mermaid(T2) → 内含 mermaid(T1)"""
        text = "检查mermaid"
        r1 = match_tier(text, t1_tier, silent_logger)
        r2 = match_tier(text, t2_tier, silent_logger)

        assert "检查mermaid" in r2.matched
        assert "mermaid" in r1.matched

    def test_nested_流程可视化_contains_t0_可视化(self, t0_tier, t2_tier, silent_logger):
        """流程可视化(T2) → 内含 可视化(T0)"""
        text = "流程可视化"
        r0 = match_tier(text, t0_tier, silent_logger)
        r2 = match_tier(text, t2_tier, silent_logger)

        assert "流程可视化" in r2.matched
        assert "可视化" in r0.matched

    def test_nested_position_ordering(self, t0_tier, t1_tier, t2_tier, silent_logger):
        """嵌套场景中T2词的position应 <= T1词position <= T0词position"""
        text = "画流程图"
        r0 = match_tier(text, t0_tier, silent_logger)
        r1 = match_tier(text, t1_tier, silent_logger)
        r2 = match_tier(text, t2_tier, silent_logger)

        pos_t2 = text.find("画流程图")
        pos_t1 = text.find("流程图")
        pos_t0 = text.find("画")

        assert pos_t2 <= pos_t1
        assert pos_t2 <= pos_t0
        assert pos_t0 <= pos_t1

    def test_nested_all_three_levels_match_simultaneously(self, all_tiers, silent_logger):
        """单个T2词同时命中三级信号"""
        text = "画流程图"
        result = match_input(text, all_tiers, silent_logger)
        assert result["tiers"]["T0"]["is_matched"]
        assert result["tiers"]["T1"]["is_matched"]
        assert result["tiers"]["T2"]["is_matched"]
        assert result["highest_signal"] == "T2"


class TestMixedSignalInput:
    """复杂混合输入测试：覆盖11个命中词的完整场景"""

    COMPLEX_INPUT = "帮我把这个架构图用mermaid画流程图，并检查mermaid语法，最后生成时序图做流程可视化"

    def test_t0_matches_3_words(self, all_tiers, silent_logger):
        """T0弱信号命中3个词：图、画、可视化"""
        result = match_input(self.COMPLEX_INPUT, all_tiers, silent_logger)
        t0_matched = result["tiers"]["T0"]["matched"]
        assert set(t0_matched) == {"图", "画", "可视化"}
        assert len(t0_matched) == 3

    def test_t1_matches_4_words(self, all_tiers, silent_logger):
        """T1中信号命中4个词：架构图、mermaid、流程图、时序图"""
        result = match_input(self.COMPLEX_INPUT, all_tiers, silent_logger)
        t1_matched = result["tiers"]["T1"]["matched"]
        assert set(t1_matched) == {"架构图", "mermaid", "流程图", "时序图"}
        assert len(t1_matched) == 4

    def test_t2_matches_4_words(self, all_tiers, silent_logger):
        """T2强信号命中4个词：画流程图、检查mermaid、生成时序图、流程可视化"""
        result = match_input(self.COMPLEX_INPUT, all_tiers, silent_logger)
        t2_matched = result["tiers"]["T2"]["matched"]
        assert set(t2_matched) == {"画流程图", "检查mermaid", "生成时序图", "流程可视化"}
        assert len(t2_matched) == 4

    def test_total_11_hits(self, all_tiers, silent_logger):
        """三级总计命中11个词（T0:3 + T1:4 + T2:4）"""
        result = match_input(self.COMPLEX_INPUT, all_tiers, silent_logger)
        total = (
            len(result["tiers"]["T0"]["matched"])
            + len(result["tiers"]["T1"]["matched"])
            + len(result["tiers"]["T2"]["matched"])
        )
        assert total == 11

    def test_highest_signal_is_t2(self, all_tiers, silent_logger):
        """最高信号为T2（强信号优先于T1和T0）"""
        result = match_input(self.COMPLEX_INPUT, all_tiers, silent_logger)
        assert result["highest_signal"] == "T2"

    def test_load_action_is_l1_plus_l2(self, all_tiers, silent_logger):
        """T2命中时加载动作为L1+L2"""
        result = match_input(self.COMPLEX_INPUT, all_tiers, silent_logger)
        assert "L1" in result["load_action"]
        assert "L2" in result["load_action"]

    def test_t0_图表_not_matched(self, all_tiers, silent_logger):
        """T0的'图表'未命中（输入中无此词）"""
        result = match_input(self.COMPLEX_INPUT, all_tiers, silent_logger)
        assert "图表" not in result["tiers"]["T0"]["matched"]

    def test_t1_unmatched_7_words(self, all_tiers, silent_logger):
        """T1未命中7个词：状态图、ER图、类图、甘特图、饼图、UML图、思维导图"""
        result = match_input(self.COMPLEX_INPUT, all_tiers, silent_logger)
        assert result["tiers"]["T1"]["unmatched_count"] == 7

    def test_t2_unmatched_3_words(self, all_tiers, silent_logger):
        """T2未命中3个词：画个图、修复图表、mermaid图"""
        result = match_input(self.COMPLEX_INPUT, all_tiers, silent_logger)
        assert result["tiers"]["T2"]["unmatched_count"] == 3


class TestLoadDecision:
    """加载决策链路测试：T2 > T1 > T0"""

    def test_t2_overrides_t1_and_t0(self, all_tiers, silent_logger):
        """T2命中时，即使T0/T1也命中，最高信号仍为T2"""
        result = match_input("画流程图", all_tiers, silent_logger)
        assert result["highest_signal"] == "T2"

    def test_t1_overrides_t0(self, all_tiers, silent_logger):
        """T1命中但T2未命中时，最高信号为T1"""
        result = match_input("这个架构图", all_tiers, silent_logger)
        assert result["highest_signal"] == "T1"

    def test_t0_only_no_load(self, all_tiers, silent_logger):
        """仅T0命中时，最高信号为T0，不加载L1"""
        result = match_input("这个图不错", all_tiers, silent_logger)
        assert result["highest_signal"] == "T0"
        assert "不主动加载" in result["load_action"]

    def test_no_match_returns_none(self, all_tiers, silent_logger):
        """无匹配时highest_signal为None"""
        result = match_input("今天天气真好", all_tiers, silent_logger)
        assert result["highest_signal"] is None
        assert result["load_action"] == "不加载"

    def test_t2_action_preloads_l2(self, all_tiers, silent_logger):
        """T2加载动作包含预加载L2"""
        result = match_input("生成时序图", all_tiers, silent_logger)
        assert "预加载L2" in result["load_action"]

    def test_t1_action_loads_l1_only(self, all_tiers, silent_logger):
        """T1加载动作仅加载L1，不含L2"""
        result = match_input("看这个时序图", all_tiers, silent_logger)
        assert result["highest_signal"] == "T1"
        assert "L1" in result["load_action"]
        assert "L2" not in result["load_action"]


class TestLogger:
    """日志记录测试"""

    def test_logger_records_all_entries(self, all_tiers):
        """日志器记录所有条目（含DEBUG级）"""
        logger = Logger(json_mode=True, verbose=True)
        match_input("画流程图", all_tiers, logger)
        # 至少包含：TRIGGER_START + 3×TIER_SCAN + 若干HIT/MISS + 3×TIER_MATCH + LOAD_DECISION
        assert len(logger.entries) >= 10

    def test_logger_json_mode_silent(self, all_tiers, capsys):
        """JSON模式下不输出到stdout"""
        logger = Logger(json_mode=True)
        match_input("画流程图", all_tiers, logger)
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_logger_contains_load_decision_event(self, all_tiers):
        """日志包含LOAD_DECISION事件"""
        logger = Logger(json_mode=True)
        match_input("画流程图", all_tiers, logger)
        events = [e["event"] for e in logger.entries]
        assert "LOAD_DECISION" in events

    def test_logger_contains_tier_match_events(self, all_tiers):
        """日志包含各级TIER_MATCH事件"""
        logger = Logger(json_mode=True)
        match_input("画流程图", all_tiers, logger)
        events = [e["event"] for e in logger.entries]
        assert "TRIGGER_T0_MATCH" in events
        assert "TRIGGER_T1_MATCH" in events
        assert "TRIGGER_T2_MATCH" in events

    def test_logger_no_match_warn(self, all_tiers):
        """无匹配时日志包含WARN级TRIGGER_NO_MATCH"""
        logger = Logger(json_mode=True)
        match_input("今天天气真好", all_tiers, logger)
        warn_entries = [e for e in logger.entries if e["level"] == "WARN"]
        assert len(warn_entries) >= 1
        assert warn_entries[0]["event"] == "TRIGGER_NO_MATCH"
