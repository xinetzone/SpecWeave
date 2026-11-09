"""模式文档创新类归类（_is_innovation_pattern）单元测试。

对应缺陷（两类同源误判）：
    1. 兜底分支用裸「迁移」匹配开头 1000 字符，导致标题/开头带「迁移」二字的
       SOP、速查、操作手册被误判为创新类模式；
    2. 兜底分支用裸「反向」匹配，而「反向」在工程语境里多为计算方向
       （前向/反向计算、反向传播、反向依赖）或动词性表达
       （不反向影响、反向控制范围），并非创新语义。
    两者都会让非创新类模式被 V2 检查要求「失败案例」「反目标用户/场景」两章
    并阻断提交。

覆盖场景（迁移类）：
    1. 无章节 + 标题含「迁移」的 runbook → 非创新（兜底不再收裸「迁移」）
    2. 无章节 + 正文含「跨域迁移」→ 创新（短语级迁移语义仍收）
    3. 有「## 模式类型」+ 写「迁移类模式」→ 创新（章节口径未被改坏）
    4. 有「## 模式类型」+ 只写业务名（执行类模式）→ 非创新
    5. 有「## 模式类型」+ 裸「迁移」→ 创新（章节内宽口径保持不变）

覆盖场景（反向类）：
    6. 无章节 + 正文含「反向传播」→ 非创新（计算方向）
    7. 无章节 + 正文含「前向/反向计算」→ 非创新（计算方向，真实样本形态）
    8. 无章节 + 正文含「反向推理」→ 创新（短语级反向思维语义仍收）
    9. 无章节 + 正文含「反直觉设计」→ 创新（裸「反直觉」仍在兜底词表内）
    10. 有「## 模式类型」+ 裸「反向」→ 创新（章节口径未被改坏）
    11. 真实仓库样本 reverse-leverage-rule-constraints.md（「反向借势」）→ 创新

运行：pytest .agents/scripts/tests/test_pattern_innovation_classify.py -v
"""

from pathlib import Path

from lib.check_pattern_quality.check_content import _is_innovation_pattern

RUNBOOK_WITH_MIGRATION_TITLE = """# WSL 发行版安装与迁移速查手册

> 适用：已在 Windows 11 上使用 WSL2，需要迁移发行版到新磁盘。

## 操作流程

1. `wsl --export` 导出当前发行版
2. `wsl --unregister` 注销旧实例
3. `wsl --import` 导入到新位置

## 检查清单

- [ ] 导出文件大小与磁盘占用相符
- [ ] 迁移后默认发行版指向正确
- [ ] systemd 与网络配置复测通过
"""

FALLBACK_WITH_CROSS_DOMAIN_MIGRATION = """# 把供应链的库存缓冲策略移植到需求排期

本文属于跨域迁移：把制造业的缓冲库存模型搬到软件需求排期上。

## 问题背景

需求排期长期靠拍脑袋，缺少可观测的缓冲量。
"""


def test_fallback_title_migration_runbook_is_not_innovation():
    """无章节 + 标题含「迁移」的 runbook 不应被判为创新类。"""
    assert _is_innovation_pattern(RUNBOOK_WITH_MIGRATION_TITLE) is False


def test_fallback_cross_domain_migration_is_innovation():
    """无章节但正文出现「跨域迁移」短语时，仍判为创新类。"""
    assert _is_innovation_pattern(FALLBACK_WITH_CROSS_DOMAIN_MIGRATION) is True


def test_section_migration_pattern_type_is_innovation():
    """有「## 模式类型」且写「迁移类模式」时判为创新类（章节口径不变）。"""
    content = """# 某迁移模式

## 模式类型

迁移类模式

## 适用场景

存量系统替换。
"""
    assert _is_innovation_pattern(content) is True


def test_section_business_name_only_is_not_innovation():
    """有「## 模式类型」但只写业务名时不是创新类。"""
    content = """# 某执行模式

## 模式类型

执行类模式

## 适用场景

日常任务编排。
"""
    assert _is_innovation_pattern(content) is False


def test_section_bare_migration_keyword_is_innovation():
    """章节内裸「迁移」仍判创新类——收紧只作用于兜底分支。"""
    content = """# 某迁移模式

## 模式类型

迁移
"""
    assert _is_innovation_pattern(content) is True


FALLBACK_WITH_BACKPROPAGATION = """# 梯度校验的一种实现思路

训练时需要校验梯度，用反向传播逐层求导并与数值差分对比。

## 问题背景

手工推导容易漏项。
"""

FALLBACK_WITH_FORWARD_BACKWARD_COMPUTE = """# 推理框架数值对齐检查

需要验证深度学习框架前向/反向计算正确性时，先固定随机种子再逐层比对。

## 问题背景

框架间默认值差异会导致结果不可比。
"""

FALLBACK_WITH_REVERSE_REASONING = """# 从结论倒推需求边界

先从最终交付形态反向推理出必要前提，再决定哪些前提必须先验证。

## 问题背景

正向罗列需求容易把非必要项也纳入范围。
"""

FALLBACK_WITH_COUNTERINTUITIVE_DESIGN = """# 用反直觉设计替代默认路径

默认路径追求最少步骤，反直觉设计要求先制造摩擦以暴露隐藏假设。

## 问题背景

顺滑流程会掩盖用户真实意图。
"""

REAL_REVERSE_LEVERAGE = (
    Path(__file__).resolve().parents[3]
    / "docs/retrospective/patterns/methodology-patterns/product-growth/"
    "reverse-leverage-rule-constraints.md"
)


def test_fallback_backpropagation_is_not_innovation():
    """无章节 + 正文含「反向传播」时不是创新类（计算方向噪声）。"""
    assert _is_innovation_pattern(FALLBACK_WITH_BACKPROPAGATION) is False


def test_fallback_forward_backward_compute_is_not_innovation():
    """无章节 + 正文含「前向/反向计算」时不是创新类（真实样本形态）。"""
    assert _is_innovation_pattern(FALLBACK_WITH_FORWARD_BACKWARD_COMPUTE) is False


def test_fallback_reverse_reasoning_is_innovation():
    """无章节但正文出现「反向推理」短语时，仍判为创新类。"""
    assert _is_innovation_pattern(FALLBACK_WITH_REVERSE_REASONING) is True


def test_fallback_counterintuitive_design_is_innovation():
    """无章节但正文出现「反直觉设计」时，仍判为创新类。"""
    assert _is_innovation_pattern(FALLBACK_WITH_COUNTERINTUITIVE_DESIGN) is True


def test_section_bare_reverse_keyword_is_innovation():
    """章节内裸「反向」仍判创新类——收紧只作用于兜底分支。"""
    content = """# 某反向模式

## 模式类型

反向
"""
    assert _is_innovation_pattern(content) is True


def test_real_reverse_leverage_pattern_still_innovation():
    """真实仓库样本「反向借势」仍判创新类（防回归）。"""
    assert REAL_REVERSE_LEVERAGE.is_file(), f"样本缺失: {REAL_REVERSE_LEVERAGE}"
    content = REAL_REVERSE_LEVERAGE.read_text(encoding="utf-8")
    assert _is_innovation_pattern(content) is True
