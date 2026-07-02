---
id: "tuyaopen-insight-1-spec-frontloading"
title: "洞察1：规范前置化是预防违规的根本手段"
source: "docs/knowledge/learning/tuya-open-learning-report.md"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/competitive-analysis/retrospective-tuyaopen-learning-report-optimization-20260630/insights/insight-1-spec-frontloading.toml"
---
# 洞察1：规范前置化是预防违规的根本手段

**来源**：TuyaOpen 学习报告优化任务

## 发现

本次问题的根本原因是 AGENTS.md 缺少文件创建前的强制检查规则，导致智能体在创建文档时跳过了规范查阅环节。

## 深层含义

- 规范文档存在但未被智能体在执行任务时自动加载，等于不存在
- 需要将规范检查嵌入到智能体的启动协议和任务路由中，而非依赖智能体的自觉行为
- 「全局核心规则」是规范前置化的最佳载体，所有智能体启动时都会读取

## 验证证据

- 修复前：文件命名规范存在于 `.agents/rules/file-naming-convention.md`，但路由表中无对应条目
- 修复后：在 AGENTS.md 全局核心规则中新增强制性检查规则，在路由表中新增条目
- 效果：下次创建文件时将自动触发规范检查流程

## 关联资源

- [文件命名规范](../../../../../../.agents/rules/file-naming-convention.md)
- [文件创建前置检查模式](../../../../patterns/methodology-patterns/governance-strategy/file-creation-precheck-pattern.md)
- [规范可发现性保障模式](../../../../patterns/methodology-patterns/governance-strategy/spec-discoverability-guarantee.md)