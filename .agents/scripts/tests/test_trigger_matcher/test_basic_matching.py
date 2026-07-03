from trigger_matcher import match_tier, match_input


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
