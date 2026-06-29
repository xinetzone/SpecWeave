+++
id = "three-layer-rule-enforcement"
domain = "methodology"
layer = "methodology"
maturity = "L2"
validation_count = 1
reuse_count = 0
documentation_level = "basic"
source = "docs/retrospective/reports/governance/retrospective-stage-guardrails-logging-20260629/insight-extraction.md"

[bindings]
rules = [".agents/rules/stage-guardrails.md"]
references = [".agents/protocols/pre-document-reading.md", ".agents/scripts/check-stage-guardrails.py"]
skills = []
+++

# 规则落地三层模型：定义+痕迹+验证

## 模型概述

治理规则的完整落地需要三层协同，缺一不可。纯文档规范靠智能体"自觉遵守"不可靠，必须同时具备标准定义、执行痕迹和事后验证能力。

## 第一层：定义层（规范文档）
- 目标：明确规定"应该怎么做"
- 方法：Markdown规则/协议文档，包含操作边界、正反例、流程图
- 输出：可被智能体读取和理解的规范
- 验证标准：规则清晰无歧义，包含可执行的检查标准而非模糊要求

## 第二层：痕迹层（结构化日志）
- 目标：规定"怎么记录做了什么"，留下可审计的执行痕迹
- 方法：统一前缀的键值对日志格式（如`[SG-LOG] | level=... | event=... | ctx={json}`）
- 关键：关键事件节点全覆盖（进入/检查/拦截/审批/退出/异常），即时输出不延迟
- 验证标准：每条日志单行输出，必填字段完整，ctx为压缩JSON

## 第三层：验证层（检查工具）
- 目标：事后可验证"是否真的遵守了规则"
- 方法：离线分析脚本，解析日志检测异常（未进入即退出、拦截后继续执行、跳转无审批等）
- 关键：支持`--demo`自检模式和`--json`机器输出，误报率可控
- 验证标准：零漏报（关键异常必检出），低误报（WARN级别可容忍，ERROR级别必须精准）

## 依赖关系
```
定义层（前提）→ 痕迹层（证据）→ 验证层（保障）
     ↓              ↓              ↓
 有标准可依    有痕迹可查    有违规可纠
```

## 适用场景

- 开发流程阶段守卫（本次验证场景）
- 代码审查准入规则
- 测试覆盖率门禁
- 文档更新强制检查
- 任何需要AI智能体"自觉遵守"的治理规则

## 反模式警示

- ❌ 只有定义层没有痕迹层：规则写了但没人知道是否执行了
- ❌ 只有痕迹层没有验证层：日志打了但没人分析，异常无人发现
- ❌ 事后补防护：先写规则，出问题后再补日志和脚本（本次迭代即犯了此反模式）
- ❌ 三层不同步：规则更新了但日志格式和检查脚本没更新

## 实施检查清单
- [ ] Layer 1：规则文档包含明确的操作边界、正反例、拦截/审批流程
- [ ] Layer 2：关键事件节点定义了结构化日志格式（前缀+键值对+ctx JSON）
- [ ] Layer 3：检查脚本可解析日志，能检测核心违规场景
- [ ] Layer 3：检查脚本有--demo模式，内置正常/异常场景可自检
- [ ] 三层同步设计：规则设计阶段就同步规划日志格式和检查逻辑

> 来源：来自 retrospective-stage-guardrails-logging-20260629 洞察1
> 关联模式：[three-tier-governance.md](three-tier-governance.md)（三层治理模型）、[structured-lightweight-logging.md](../../code-patterns/structured-lightweight-logging.md)
