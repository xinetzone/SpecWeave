---
id: "finding-fp-three-categories"
title: "发现5：静态分析工具的\"误报三分类\"规律"
source: "../insight-extraction.md#发现-5静态分析工具的误报三分类规律"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/tools-and-automation/retrospective-scripts-shared-lib-extraction-20260626/insights/finding-05-fp-three-categories.toml"
---
# 发现5：静态分析工具的"误报三分类"规律

→ 落地产物：[false-positive-rules.toml](../../../../../../../.agents/scripts/config/false-positive-rules.toml)（通用误报过滤规则）
→ 关联模块：[lib/rules.py](../../../../../../../.agents/scripts/lib/rules.py)（规则加载引擎）

## 事件发现

check-duplication.py 首次运行报告7处重复，经人工分类后发现：
- 2处真实逻辑重复（29%）→ 提取到共享库
- 3处向后兼容薄包装器（43%）→ 自动识别并排除
- 2处纯import/docstring样板（28%）→ 结构性过滤

## 规律

代码重复检测工具的误报可分为三类：

1. **有意转发层**（向后兼容包装器、adapter模式、stub文件）
   - 特征：docstring中有明确标记、仅做转发调用、文件短小
   - 对策：通过代码标记（docstring关键词）自动识别

2. **语言结构样板**（import块、docstring标记、shebang、编码声明、dataclass字段）
   - 特征：纯结构性代码，不含业务逻辑
   - 对策：通过正则模式自动过滤

3. **真实逻辑重复**
   - 特征：包含实际业务逻辑
   - 对策：需要提取或告警

## 四层过滤体系

基于此规律设计了通用误报过滤规则文件（false-positive-rules.toml），按四个层级递进过滤：

| 层级 | 过滤对象 | 判断方式 |
|------|---------|---------|
| 路径排除 | vendor/generated/fixtures等 | 目录名+文件名+路径正则 |
| 文件标记 | 兼容包装器/自动生成/第三方 | 文件前N行docstring关键词 |
| 块过滤 | import样板/类样板/dataclass | 块内行正则匹配（match_all/match_all=false） |
| 行过滤 | pass/return/三引号/控制流 | 单行正则匹配 |

## 对策

检测工具应**内置前两类误报的自动过滤逻辑**，而非将分类成本转嫁给使用者。信噪比 ≥ 30% 是工具可用性的底线（见 tool-self-validation 检查清单第4项）。

## 关联洞察

- [finding-07-tool-self-validation.md](finding-07-tool-self-validation.md) — 自生验证中首次运行即暴露误报
- [finding-01-duplication-threshold.md](finding-01-duplication-threshold.md) — 真实重复的阈值规律

---
*来源：[脚本共享库提取复盘](../README.md)*
