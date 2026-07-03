from trigger_matcher import fuzzy_match, match_tier, match_input, Logger


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
