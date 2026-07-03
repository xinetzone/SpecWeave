import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = SCRIPTS_DIR.parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from trigger_matcher import (
    TriggerTier,
    TierMatchResult,
    Logger,
    parse_skill_triggers,
    match_tier,
    match_input,
    fuzzy_match,
)


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
    return Logger(json_mode=True)
