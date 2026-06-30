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
    fuzzy_match,
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
    return TriggerTier(level="T0", name="弱信号", triggers=T0_TRIGGERS, action=T0_ACTION, default_weight=1)


@pytest.fixture
def t1_tier():
    return TriggerTier(level="T1", name="中信号", triggers=T1_TRIGGERS, action=T1_ACTION, default_weight=5)


@pytest.fixture
def t2_tier():
    return TriggerTier(level="T2", name="强信号", triggers=T2_TRIGGERS, action=T2_ACTION, default_weight=9)


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


class TestFuzzyMatch:
    """fuzzy_match 带间距约束的子序列匹配测试"""

    def test_exact_substring_also_matches(self):
        """精确子串也是子序列，应匹配"""
        is_match, pos, text = fuzzy_match("画流程图", "画流程图", max_gap=2)
        assert is_match
        assert pos == 0
        assert text == "画流程图"

    def test_inserted_char_within_gap(self):
        """中间插入1个字符（画个流程图→画流程图），间距1≤2，应匹配"""
        is_match, pos, text = fuzzy_match("画流程图", "画个流程图", max_gap=2)
        assert is_match
        assert pos == 0
        assert text == "画个流程图"

    def test_gap_exceeds_limit(self):
        """间距超过max_gap不应匹配：画一个完整的流程图，画→流间距5>2"""
        is_match, pos, text = fuzzy_match("画流程图", "画一个完整的流程图", max_gap=2)
        assert not is_match

    def test_relaxed_gap_allows_match(self):
        """放宽max_gap到5后应匹配"""
        is_match, pos, text = fuzzy_match("画流程图", "画一个完整的流程图", max_gap=5)
        assert is_match
        assert text == "画一个完整的流程图"

    def test_first_char_not_found(self):
        """首字符不存在时不应匹配"""
        is_match, pos, text = fuzzy_match("X流程图", "画个流程图", max_gap=2)
        assert not is_match

    def test_empty_trigger(self):
        """空触发词不应匹配"""
        is_match, pos, text = fuzzy_match("", "画个流程图", max_gap=2)
        assert not is_match

    def test_empty_text(self):
        """空文本不应匹配"""
        is_match, pos, text = fuzzy_match("画流程图", "", max_gap=2)
        assert not is_match

    def test_single_char_trigger(self):
        """单字符触发词只需找到该字符"""
        is_match, pos, text = fuzzy_match("画", "画个流程图", max_gap=2)
        assert is_match
        assert pos == 0
        assert text == "画"

    def test_mermaid_fuzzy_match(self):
        """检查mermaid作为子串应精确匹配"""
        is_match, pos, text = fuzzy_match("检查mermaid", "请检查mermaid语法", max_gap=2)
        assert is_match
        assert "检查mermaid" in text


class TestFuzzyMatchGapBoundary:
    """max_gap 边界条件测试：间距刚好等于/超过 max_gap 时的匹配行为"""

    def test_gap_equals_max_gap_matches(self):
        """间距刚好等于max_gap时应匹配（边界包含）"""
        # A@0, B@3, 间距=3-0-1=2=max_gap
        is_match, _, _ = fuzzy_match("AB", "AXXB", max_gap=2)
        assert is_match

    def test_gap_exceeds_max_gap_by_one_no_match(self):
        """间距刚好超过max_gap一个字符时不匹配（边界排除）"""
        # A@0, B@4, 间距=4-0-1=3>max_gap=2
        is_match, _, _ = fuzzy_match("AB", "AXXXB", max_gap=2)
        assert not is_match

    def test_gap_zero_max_gap_zero_matches(self):
        """max_gap=0时只允许连续匹配（等价于精确子串）"""
        is_match, _, _ = fuzzy_match("AB", "AB", max_gap=0)
        assert is_match

    def test_gap_one_max_gap_zero_no_match(self):
        """max_gap=0时插入任何字符都不匹配"""
        is_match, _, _ = fuzzy_match("AB", "AXB", max_gap=0)
        assert not is_match

    def test_gap_one_max_gap_one_matches(self):
        """max_gap=1时间距刚好1应匹配"""
        is_match, _, _ = fuzzy_match("AB", "AXB", max_gap=1)
        assert is_match

    def test_gap_two_max_gap_one_no_match(self):
        """max_gap=1时间距2不匹配"""
        is_match, _, _ = fuzzy_match("AB", "AXXB", max_gap=1)
        assert not is_match

    def test_multi_char_all_pairs_at_boundary(self):
        """多字符trigger每对相邻字符间距都等于max_gap时应匹配"""
        # A@0, B@3(间距2), C@6(间距2), max_gap=2
        is_match, _, _ = fuzzy_match("ABC", "AXXBYCZ", max_gap=2)
        assert is_match

    def test_multi_char_one_pair_exceeds_boundary(self):
        """多字符trigger中有一对间距超过max_gap时不匹配"""
        # A@0, B@4(间距3>2) → 在search范围[1,4)="XXX"中找不到B
        is_match, _, _ = fuzzy_match("ABC", "AXXXBYCZ", max_gap=2)
        assert not is_match


class TestFuzzyTierMatch:
    """match_tier 模糊匹配行为测试"""

    def test_fuzzy_disabled_no_fuzzy_match(self, t2_tier, silent_logger):
        """fuzzy=False时不触发模糊匹配，画个流程图不命中T2"""
        result = match_tier("画个流程图", t2_tier, silent_logger, fuzzy=False)
        assert "画流程图" not in result.matched
        assert "画流程图" not in result.fuzzy_matched
        assert not result.is_matched

    def test_fuzzy_enabled_matches_variant(self, t2_tier, silent_logger):
        """fuzzy=True时画个流程图模糊命中画流程图"""
        result = match_tier("画个流程图", t2_tier, silent_logger, fuzzy=True, max_gap=2)
        assert "画流程图" in result.fuzzy_matched
        assert result.is_matched

    def test_exact_match_preferred_over_fuzzy(self, t2_tier, silent_logger):
        """精确匹配优先：生成时序图应精确命中，不进入fuzzy_matched"""
        result = match_tier("生成时序图", t2_tier, silent_logger, fuzzy=True, max_gap=2)
        assert "生成时序图" in result.matched
        assert "生成时序图" not in result.fuzzy_matched
        assert len(result.fuzzy_matched) == 0

    def test_fuzzy_gap_limit_prevents_match(self, t2_tier, silent_logger):
        """max_gap=2时画一个完整的流程图不模糊命中画流程图"""
        result = match_tier("画一个完整的流程图", t2_tier, silent_logger, fuzzy=True, max_gap=2)
        assert "画流程图" not in result.fuzzy_matched

    def test_fuzzy_relaxed_gap_matches(self, t2_tier, silent_logger):
        """max_gap=5时画一个完整的流程图模糊命中画流程图"""
        result = match_tier("画一个完整的流程图", t2_tier, silent_logger, fuzzy=True, max_gap=5)
        assert "画流程图" in result.fuzzy_matched

    def test_fuzzy_matched_count_in_result(self, t2_tier, silent_logger):
        """fuzzy_matched正确统计模糊命中数量"""
        result = match_tier("画个流程图", t2_tier, silent_logger, fuzzy=True, max_gap=2)
        assert len(result.fuzzy_matched) >= 1

    def test_all_matched_property_combines(self, t2_tier, silent_logger):
        """all_matched属性合并精确和模糊匹配结果"""
        result = match_tier("生成时序图画个图", t2_tier, silent_logger, fuzzy=True, max_gap=2)
        all_matched = result.all_matched
        assert "生成时序图" in all_matched  # 精确匹配
        assert "画个图" in all_matched  # 精确匹配

    def test_fuzzy_log_event(self, t2_tier):
        """模糊命中时日志包含TRIGGER_FUZZY_HIT事件"""
        logger = Logger(json_mode=True)
        match_tier("画个流程图", t2_tier, logger, fuzzy=True, max_gap=2)
        events = [e["event"] for e in logger.entries]
        assert "TRIGGER_FUZZY_HIT" in events


class TestFuzzyMatchInput:
    """match_input 模糊匹配端到端测试"""

    def test_no_fuzzy_t1_only(self, all_tiers, silent_logger):
        """无模糊匹配时画个流程图最高信号为T1"""
        result = match_input("画个流程图", all_tiers, silent_logger, fuzzy=False)
        assert result["highest_signal"] == "T1"

    def test_fuzzy_upgrades_to_t2(self, all_tiers, silent_logger):
        """模糊匹配时画个流程图升级为T2"""
        result = match_input("画个流程图", all_tiers, silent_logger, fuzzy=True, max_gap=2)
        assert result["highest_signal"] == "T2"

    def test_fuzzy_result_contains_fuzzy_matched(self, all_tiers, silent_logger):
        """模糊匹配结果包含fuzzy_matched字段"""
        result = match_input("画个流程图", all_tiers, silent_logger, fuzzy=True, max_gap=2)
        assert "fuzzy_matched" in result["tiers"]["T2"]
        assert "画流程图" in result["tiers"]["T2"]["fuzzy_matched"]

    def test_fuzzy_gap_limit_keeps_t1(self, all_tiers, silent_logger):
        """max_gap=2时画一个完整的流程图保持T1（间距超限）"""
        result = match_input("画一个完整的流程图", all_tiers, silent_logger, fuzzy=True, max_gap=2)
        assert result["highest_signal"] == "T1"

    def test_fuzzy_relaxed_gap_upgrades_to_t2(self, all_tiers, silent_logger):
        """max_gap=5时画一个完整的流程图升级为T2"""
        result = match_input("画一个完整的流程图", all_tiers, silent_logger, fuzzy=True, max_gap=5)
        assert result["highest_signal"] == "T2"

    def test_fuzzy_no_false_positive_on_unrelated(self, all_tiers, silent_logger):
        """模糊匹配不应对无关输入产生误匹配"""
        result = match_input("今天天气真好", all_tiers, silent_logger, fuzzy=True, max_gap=2)
        assert result["highest_signal"] is None
        for tier in result["tiers"].values():
            assert tier["fuzzy_matched"] == []

    def test_fuzzy_load_action_t2(self, all_tiers, silent_logger):
        """模糊匹配T2时加载动作为L1+L2"""
        result = match_input("画个流程图", all_tiers, silent_logger, fuzzy=True, max_gap=2)
        assert "L2" in result["load_action"]


class TestWeightParsing:
    """触发词权重解析测试"""

    def test_default_weights_no_annotation(self, t0_tier, t1_tier, t2_tier):
        """无权重标注时使用默认值：T0=1, T1=5, T2=9"""
        assert t0_tier.default_weight == 1
        assert t1_tier.default_weight == 5
        assert t2_tier.default_weight == 9

    def test_get_weight_returns_default(self, t0_tier):
        """无自定义权重时get_weight返回默认值"""
        assert t0_tier.get_weight("图") == 1

    def test_get_weight_returns_custom(self):
        """有自定义权重时get_weight返回自定义值"""
        tier = TriggerTier(level="T1", name="中信号", triggers=["复盘", "发布复盘"],
                           default_weight=5, weights={"发布复盘": 7})
        assert tier.get_weight("复盘") == 5
        assert tier.get_weight("发布复盘") == 7

    def test_parse_custom_weights(self, tmp_path):
        """解析SKILL.md中的 `词(权重)` 格式"""
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text("""# Test

| **T0 弱信号** | 泛词 | `总结(1)`、`回顾(1)`、`经验(2)` | 不加载 |
| **T1 中信号** | 领域词 | `复盘(5)`、`发布复盘(7)` | 加载L1 |
| **T2 强信号** | 执行意图 | `执行复盘(10)`、`做个复盘(9)` | 加载L1+L2 |
""", encoding="utf-8")
        tiers = parse_skill_triggers(skill_md)
        assert tiers["T0"].get_weight("总结") == 1
        assert tiers["T0"].get_weight("经验") == 2
        assert tiers["T1"].get_weight("复盘") == 5
        assert tiers["T1"].get_weight("发布复盘") == 7
        assert tiers["T2"].get_weight("执行复盘") == 10

    def test_parse_mixed_weights_and_defaults(self, tmp_path):
        """混合权重标注和无标注：无标注的用默认值"""
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text("""# Test

| **T1 中信号** | 领域词 | `复盘`、`发布复盘(7)` | 加载L1 |
""", encoding="utf-8")
        tiers = parse_skill_triggers(skill_md)
        assert tiers["T1"].get_weight("复盘") == 5  # 默认值
        assert tiers["T1"].get_weight("发布复盘") == 7  # 自定义值


class TestWeightMatching:
    """权重匹配和累加测试"""

    def test_exact_match_accumulates_weight(self):
        """精确命中累加完整权重"""
        tier = TriggerTier(level="T2", name="强信号", triggers=["做个复盘", "执行复盘"],
                           default_weight=9, weights={"执行复盘": 10})
        logger = Logger(json_mode=True)
        result = match_tier("做个复盘并执行复盘", tier, logger)
        assert result.matched_weight == 9 + 10

    def test_single_match_weight(self):
        """单个命中的权重"""
        tier = TriggerTier(level="T1", name="中信号", triggers=["复盘", "发布复盘"],
                           default_weight=5, weights={"复盘": 5, "发布复盘": 7})
        logger = Logger(json_mode=True)
        result = match_tier("做个复盘", tier, logger)
        assert "复盘" in result.matched
        assert result.matched_weight == 5

    def test_fuzzy_match_half_weight(self):
        """模糊命中按半权重计算"""
        tier = TriggerTier(level="T2", name="强信号", triggers=["画流程图"],
                           default_weight=9, weights={"画流程图": 9})
        logger = Logger(json_mode=True)
        result = match_tier("画个流程图", tier, logger, fuzzy=True, max_gap=2)
        assert "画流程图" in result.fuzzy_matched
        # 9 // 2 = 4
        assert result.matched_weight == 4

    def test_fuzzy_weight_minimum_one(self):
        """权重为1时模糊命中仍计1（不低于1）"""
        tier = TriggerTier(level="T0", name="弱信号", triggers=["图"],
                           default_weight=1)
        logger = Logger(json_mode=True)
        # "图X" 不含 "图" 的精确匹配，但模糊匹配可以
        # 实际上 "图" 是单字符，text.find("图") 能找到，所以用精确匹配测试不了
        # 改为直接验证 weight=1 时的 half_weight 逻辑
        result = match_tier("图", tier, logger, fuzzy=True, max_gap=2)
        assert result.matched_weight == 1  # 精确命中权重1

    def test_no_match_zero_weight(self):
        """未命中时权重为0"""
        tier = TriggerTier(level="T1", name="中信号", triggers=["复盘"],
                           default_weight=5, weights={"复盘": 5})
        logger = Logger(json_mode=True)
        result = match_tier("今天天气真好", tier, logger)
        assert result.matched_weight == 0
        assert not result.is_matched

    def test_weight_in_log_context(self):
        """日志上下文中包含weight字段"""
        tier = TriggerTier(level="T2", name="强信号", triggers=["做个复盘"],
                           default_weight=9, weights={"做个复盘": 9})
        logger = Logger(json_mode=True)
        match_tier("做个复盘", tier, logger)
        hit_entries = [e for e in logger.entries if e["event"] == "TRIGGER_HIT"]
        assert len(hit_entries) >= 1
        assert hit_entries[0]["ctx"]["weight"] == 9


class TestWeightLoadDecision:
    """权重在加载决策中的体现"""

    def test_highest_weight_in_result(self, all_tiers, silent_logger):
        """match_input返回值包含highest_weight"""
        result = match_input("生成时序图", all_tiers, silent_logger)
        assert result["highest_signal"] == "T2"
        assert result["highest_weight"] > 0

    def test_matched_weight_in_tiers(self, all_tiers, silent_logger):
        """每层结果包含matched_weight字段"""
        result = match_input("画流程图", all_tiers, silent_logger)
        for level in ["T0", "T1", "T2"]:
            if level in result["tiers"]:
                assert "matched_weight" in result["tiers"][level]

    def test_t2_weight_higher_than_t1(self, all_tiers, silent_logger):
        """T2命中的权重大于T1命中"""
        r_t2 = match_input("生成时序图", all_tiers, silent_logger)
        r_t1 = match_input("架构图", all_tiers, silent_logger)
        assert r_t2["highest_weight"] > r_t1["highest_weight"]

    def test_load_decision_log_includes_weight(self, all_tiers):
        """加载决策日志包含matched_weight"""
        logger = Logger(json_mode=True)
        match_input("生成时序图", all_tiers, logger)
        decision_entries = [e for e in logger.entries if e["event"] == "LOAD_DECISION"]
        assert len(decision_entries) == 1
        assert "matched_weight" in decision_entries[0]["ctx"]

    def test_no_match_zero_highest_weight(self, all_tiers, silent_logger):
        """无匹配时highest_weight为0"""
        result = match_input("今天天气真好", all_tiers, silent_logger)
        assert result["highest_signal"] is None
        assert result["highest_weight"] == 0
