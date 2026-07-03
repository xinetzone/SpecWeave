from trigger_matcher import parse_skill_triggers


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
