"""模式文档创新类归类（_is_innovation_pattern）单元测试。

对应缺陷：无「## 模式类型」章节时的兜底分类用裸「迁移」匹配开头 1000 字符，
导致标题/开头带「迁移」二字的 SOP、速查、操作手册被误判为创新类模式，
进而被 V2 检查要求「失败案例」「反目标用户/场景」两章并阻断提交。

覆盖场景：
    1. 无章节 + 标题含「迁移」的 runbook → 非创新（兜底不再收裸「迁移」）
    2. 无章节 + 正文含「跨域迁移」→ 创新（短语级迁移语义仍收）
    3. 有「## 模式类型」+ 写「迁移类模式」→ 创新（章节口径未被改坏）
    4. 有「## 模式类型」+ 只写业务名（执行类模式）→ 非创新
    5. 有「## 模式类型」+ 裸「迁移」→ 创新（章节内宽口径保持不变）

运行：pytest .agents/scripts/tests/test_pattern_innovation_classify.py -v
"""

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
