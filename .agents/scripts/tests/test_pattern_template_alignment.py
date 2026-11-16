"""模式模板口径统一（A1）单元测试：新模板为权威、检查器兼容旧写法。

背景（三方冲突）：
    - 库索引 2026-08-23 起定义等级表 L1-draft / L1.5 / L2-validated /
      L3-mature / L4-optimized；
    - `pattern-to-methodology-library` 模板（2026-09-30）使用
      模式概述 / 触发场景 / 核心做法 / 沉淀与校验记录；
    - 检查器常量（2026-09-01）仍只认 模式类型 / 成熟度 / 适用场景 / 问题背景
      与 L1~L4 四值枚举，导致新模板文档被判 5 项 error。

契约（本次统一后）：
    1. 成熟度接受等级阶梯与全部历史别名，并归一为基础等级 L1~L4（L1.5 保留）；
       无等级前缀的描述性词（draft/stable 等）只告警不报错。
    2. 章节名做别名归一：触发场景≡适用场景、核心做法≡核心规则类、
       模式概述≡问题背景；模式类型/成熟度章节改为可选。
    3. 创新类分类器的兜底扫描剔除 frontmatter——元数据里的「跨域迁移」
       不得把执行类模式判为创新类；正文中的同类表述仍判创新类。

运行：pytest .agents/scripts/tests/test_pattern_template_alignment.py -v
"""

import pytest

from lib.check_pattern_quality.check_content import (
    check_sections,
    check_why_explanations,
    _is_innovation_pattern,
)
from lib.check_pattern_quality.maturity import normalize_maturity


# ---------------------------------------------------------------- 成熟度归一

@pytest.mark.parametrize(
    "raw,base",
    [
        ("L1-draft", "L1"),
        ("L1", "L1"),
        ("L1-实验性", "L1"),
        ("L1 实验性", "L1"),
        ("L1-experimental", "L1"),
        ("L1-single-case", "L1"),
        ("L1.5", "L1.5"),
        ("L1.5-extracted-from-practice", "L1.5"),
        ("L2", "L2"),
        ("L2-validated", "L2"),
        ("L2-verified", "L2"),
        ("L2 已验证", "L2"),
        ("L2（双案例验证）", "L2"),
        ("L2 验证中", "L2"),
        ("L3", "L3"),
        ("L3-mature", "L3"),
        ("L3 方法论（已完成闭环验证）", "L3"),
        ("L4", "L4"),
        ("L4-optimized", "L4"),
    ],
)
def test_normalize_maturity_level_prefixed(raw, base):
    """等级前缀形态（含全角空格/括号/中文后缀）一律归一到 L1~L4 或 L1.5。"""
    assert normalize_maturity(raw).base == base
    assert normalize_maturity(raw).status == "level"


@pytest.mark.parametrize("raw", ["draft", "stable", "validated", "established"])
def test_normalize_maturity_descriptive_word_is_alias(raw):
    """无等级前缀的描述性词不报错，但标记为 alias 以便提示改用规范形态。"""
    result = normalize_maturity(raw)
    assert result.base is None
    assert result.status == "alias"


def test_normalize_maturity_empty():
    """缺失成熟度返回 empty，不抛异常。"""
    result = normalize_maturity(None)
    assert result.base is None
    assert result.status == "empty"


# ---------------------------------------------------------------- 章节别名

NEW_TEMPLATE_DOC = """# 某执行类模式

## 模式类型

执行类。作用于任务下发之前。

## 模式概述

目标式写法在含外部副作用的场景会失效。

## 触发场景

**适用于**：

- 任务会改变外部状态。

**不适用于**：

- 纯问答。

## 核心做法（5 步）

### 步骤 1：先定义

写清楚做什么。

## 反模式

1. 只有目标没有停点。

## 检验标准

1. 第三人能复述停点。

## 与现有模式的关系

| 关联 | 说明 |
|---|---|
| [a](a.md) | 边界 |
"""


def _fields(maturity="L1-draft"):
    return {"id": "x", "maturity": maturity}


def _failed(report):
    return {r.name for r in report if not r.passed}


def test_new_template_sections_pass():
    """新模板章节（触发场景/核心做法/模式概述）不应被判缺 适用场景/问题背景/核心内容。"""
    failed = _failed(check_sections(NEW_TEMPLATE_DOC, _fields()))
    assert "sections.required.applicable_scenarios" not in failed
    assert "sections.required.problem_background" not in failed
    assert "sections.core_content" not in failed


def test_optional_sections_not_required():
    """模式类型 / 成熟度 章节改为可选；成熟度由 frontmatter 承担。"""
    failed = _failed(check_sections(NEW_TEMPLATE_DOC, _fields()))
    assert "sections.required.pattern_type" not in failed
    assert "sections.required.maturity" not in failed


OLD_TEMPLATE_DOC = """# 某旧模板模式

## 模式类型

方法论模式

## 成熟度

L2 已验证

## 适用场景

- 需要做 X 时。

## 问题背景

现状描述。

## 核心规则

1. 规则一。

## 与现有模式的关系

| 关联 | 说明 |
|---|---|
| [b](b.md) | 边界 |
"""


def test_old_template_still_passes():
    """旧模板四章节齐备时行为不变（不得因兼容新模板而放宽旧模板）。"""
    failed = _failed(check_sections(OLD_TEMPLATE_DOC, _fields("L2")))
    assert "sections.required.applicable_scenarios" not in failed
    assert "sections.required.problem_background" not in failed
    assert "sections.core_content" not in failed


EMPTY_DOC = """# 只有标题和一段话

这里没有任何结构化章节。
"""


def test_empty_doc_still_fails():
    """两套章节都没有时仍然报错——兼容不等于取消检查。"""
    failed = _failed(check_sections(EMPTY_DOC, _fields()))
    assert "sections.required.applicable_scenarios" in failed
    assert "sections.required.problem_background" in failed
    assert "sections.core_content" in failed


# ---------------------------------------------------------------- 分类器扫描范围

DOC_WITH_FRONTMATTER_MIGRATION = """---
type: Pattern
id: "demo"
title: "某执行类模式"
maturity: "L1-draft"
maturity_note: "跨域迁移为同构推演、未实测；升级条件见正文。"
---

# 某执行类模式

## 模式类型

执行类。作用于排期阶段。

## 模式概述

按顺序推进即可。
"""


def test_frontmatter_keywords_do_not_trigger_innovation():
    """frontmatter（元数据）中的「跨域迁移」不得把执行类模式判为创新类。"""
    assert _is_innovation_pattern(DOC_WITH_FRONTMATTER_MIGRATION) is False


DOC_WITH_BODY_MIGRATION = """---
type: Pattern
id: "demo2"
title: "某模式"
maturity: "L2"
---

# 把库存缓冲策略移植到需求排期

## 模式概述

本文属于跨域迁移：把制造业的缓冲库存模型搬到软件需求排期上。
"""


def test_body_keywords_still_trigger_innovation():
    """正文中的「跨域迁移」仍判创新类——剔除 frontmatter 不等于放宽正文判断。"""
    assert _is_innovation_pattern(DOC_WITH_BODY_MIGRATION) is True


def test_frontmatter_mask_does_not_shift_scan_window():
    """掩码不得移动 1000 字符扫描窗口。

    构造：frontmatter 约 400 字符（无关键词），正文先填 650 字符空白区，
    关键词落在原文偏移约 1050 处——在窗口外。若实现改为「切除 frontmatter」，
    正文前移 400 字符会让关键词落进窗口而被误判（全库实测会多判 15 篇）。
    """
    fm = "---\ntype: Pattern\nid: \"demo3\"\n" + ("x" * 330) + "\n---\n"
    body = ("填" * 650) + "本文属于跨域迁移：把库存模型搬到排期上。"
    content = fm + "\n# 某执行类模式\n\n" + body
    assert content.index("跨域迁移") > 1000
    assert _is_innovation_pattern(content) is False


# ---------------------------------------------------------------- 重要章节与 Why

def test_anti_pattern_section_satisfies_legacy_name():
    """新模板的「反模式」章节等价于旧模板的「反例警示」。"""
    content = NEW_TEMPLATE_DOC + "\n## 反模式\n\n1. 只有目标没有停点。\n"
    failed = _failed(check_sections(content, _fields()))
    assert "sections.important.anti_patterns" not in failed


def test_why_explanation_without_bold_still_counts():
    """「> 为什么…」不加粗也应计入设计意图解释（新模板常见写法）。"""
    content = NEW_TEMPLATE_DOC + "\n> 为什么把停点单列？因为条件与停点失效方式不同。\n"
    results = check_why_explanations(content)
    assert results[0].passed is True


# ---------------------------------------------------------------- 通用标签不当创新信号

def test_generic_type_label_is_not_innovation():
    """「方法论模式」是全库通用类型标签，不得据此判为创新类。

    2026-11-16 实测：263 篇命中宽口径的文档中 249 篇仅因该标签命中，
    真正的创新/迁移/反向信号只有 14 篇。
    """
    content = """# 工具故障三级降级策略

## 模式类型

方法论模式（工具自动化/故障处理）

## 适用场景

工具调用失败时按预案降级。
"""
    assert _is_innovation_pattern(content) is False


def test_cross_domain_label_with_generic_word_is_innovation():
    """「跨领域迁移型方法论模式」仍判创新类——去掉通用标签不削弱真实信号。"""
    content = """# 证据链工程化

## 模式类型

跨领域迁移型方法论模式——把合规审计的过程可举证要求迁移到交付场景。
"""
    assert _is_innovation_pattern(content) is True


# ---------------------------------------------------------------- 章节标题容忍修饰前缀

def test_failure_section_with_modifier_prefix_is_recognized():
    """「已记录的失败案例（V2补充）」等带修饰前缀的标题应被识别为失败案例章节。"""
    from lib.check_pattern_quality.check_content import check_innovation_pattern_v2

    content = """# 反向适配创新

## 模式类型

方法论模式 / 创新设计模式

## 已记录的失败案例（V2补充）

某次按五步法执行时跳过了步骤 3，导致方案与用户真实场景不符，返工两次。
"""
    results = {r.name: r.passed for r in check_innovation_pattern_v2(content)}
    assert results["innovation.failure_cases"] is True


def test_navigation_index_page_skips_v2(tmp_path):
    """`*-index.md` 导航页不承载模式主张，应跳过创新类 V2 检查。"""
    from lib.check_pattern_quality.checker import check_pattern

    p = tmp_path / "demo-index.md"
    p.write_text(
        "---\ntype: Pattern\nid: \"demo-index\"\ndomain: methodology\nlayer: governance-strategy\n"
        "maturity: \"L1-draft\"\nsource: \"x\"\n---\n\n"
        "# 某方法论索引\n\n创新突破用 F→V→I→C，知识沉淀用 R→I→E。\n",
        encoding="utf-8",
    )
    rep = check_pattern(p, tmp_path)
    names = {r.name for r in rep.results}
    assert "innovation.v2_gate" not in names
