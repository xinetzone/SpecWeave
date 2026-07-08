---
title: "复盘改进行动项执行 Spec"
source: "retrospective-zhihu-637007780-analysis"
x-toml-ref: "../../../../.meta/toml/.trae/specs/retrospectives-insights/improve-retrospective-action-items/spec.toml"
source_type: "改进行动项执行"
scope: "task"
analysis_date: "2026-07-06"
---
# 复盘改进行动项执行 Spec

## Why

知乎 637007780 分析任务复盘产出 5 个改进行动项（A1-A5），其中 2 个高优先级、2 个中优先级、1 个低优先级。本 spec 执行这些行动项，将复盘洞察转化为实际改进，避免"复盘完就结束"的常见反模式。

来源：[export-suggestions.md](../../../docs/retrospective/reports/task-reports/retrospective-zhihu-637007780-analysis-20260706/export-suggestions.md)

## What Changes

- **A1（高）**：创建反爬策略预设清单文档，覆盖知乎/微博/推特等至少 3 类反爬站点
- **A2（高）**：在小样本分析方法论模式中加入 Spec 模板前置检查步骤 + 报告模板"分析受限警告"引用块
- **A3（中）**：创建外部内容分析任务的渐进式 Spec 规划流程文档
- **A4（中）**：增强 `subagent-atomic-task-template` 模式，增加"内容获取类任务扩展模板"章节
- **A5（低）**：在反爬策略决策树中标注沙箱环境不可达服务，优化 fallback 链
- **BREAKING**：无

## Impact

- Affected specs：无
- Affected code：无代码改动
- 新增文件：
  - `docs/knowledge/anti-crawler-strategy-playbook.md`（A1）
  - `docs/retrospective/patterns/methodology-patterns/research-knowledge/progressive-spec-planning-for-external-content.md`（A3）
- 修改文件：
  - `docs/retrospective/patterns/methodology-patterns/research-knowledge/small-sample-analysis-methodology.md`（A2）
  - `docs/retrospective/patterns/methodology-patterns/ai-collaboration/subagent-atomic-task-template.md`（A4）
  - `docs/retrospective/patterns/methodology-patterns/research-knowledge/external-website-analysis-fallback-strategy.md`（A5）
  - 相关索引文件（README.md）

## ADDED Requirements

### Requirement: A1 反爬策略预设清单

系统 SHALL 创建反爬策略预设清单文档，覆盖至少 3 类反爬站点的获取策略。

#### Scenario: 清单内容完整

- **WHEN** 创建反爬策略预设清单
- **THEN** 文档保存至 `docs/knowledge/anti-crawler-strategy-playbook.md`
- **AND** 覆盖知乎、微博、推特等至少 3 类反爬站点
- **AND** 每类站点包含：特征识别（JS challenge / 错误码 / 登录墙）、策略优先级决策树、命令模板、失败信号
- **AND** 显著标注 `--disable-blink-features=AutomationControlled` + 桌面 UA 的关键配置
- **AND** 区分沙箱环境可用/不可用的策略

### Requirement: A2 小样本分析前置检查

系统 SHALL 在小样本分析方法论模式中加入 Spec 模板前置检查步骤和报告模板引用块。

#### Scenario: 前置检查规则

- **WHEN** 修改小样本分析方法论模式
- **THEN** 加入"样本量前置检查"步骤（样本量 ≥ 10 全规格 / 5-9 降级 / 3-4 大幅降级 / < 3 跳过深度层）
- **AND** 提供"分析受限警告"标准引用块模板
- **AND** 标注触发条件（内容获取后立即评估样本量）

### Requirement: A3 Spec 规划时间盒

系统 SHALL 创建外部内容分析任务的渐进式 Spec 规划流程文档。

#### Scenario: 三阶段规划流程

- **WHEN** 创建渐进式 Spec 规划流程
- **THEN** 文档保存至 `docs/retrospective/patterns/methodology-patterns/research-knowledge/progressive-spec-planning-for-external-content.md`
- **AND** 定义三阶段：最小可行 Spec（15 分钟）→ 内容获取试错（30 分钟）→ 基于实际样本调整 Spec（10 分钟）
- **AND** 核心原则："最小启动 + 渐进细化"

### Requirement: A4 子智能体委派模板增强

系统 SHALL 在 `subagent-atomic-task-template` 模式中增加"内容获取类任务扩展模板"章节。

#### Scenario: 扩展模板内容

- **WHEN** 增强 subagent-atomic-task-template 模式
- **THEN** 新增"内容获取类任务扩展模板"章节
- **AND** 包含：已尝试方法清单（策略名称 + 命令 + 失败原因）、已知约束（沙箱限制、可用工具）、成功标准（如"获取至少 N 条回答正文"）
- **AND** 补充内容获取类任务的产出验证流程（样本覆盖率检查）

### Requirement: A5 沙箱环境 fallback 链优化

系统 SHALL 在反爬策略决策树中标注沙箱环境不可达服务，优化 fallback 链。

#### Scenario: 沙箱环境策略标注

- **WHEN** 优化反爬策略决策树
- **THEN** 标注 archive.org / Google Cache 为"沙箱环境不可达"
- **AND** 在 fallback 链中降低其优先级或移除
- **AND** 区分"沙箱环境可用"和"沙箱环境不可用"的策略

## REMOVED Requirements

无
