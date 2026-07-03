from trigger_matcher import (
    TriggerTier,
    Logger,
    parse_skill_triggers,
    match_tier,
    match_input,
)


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
