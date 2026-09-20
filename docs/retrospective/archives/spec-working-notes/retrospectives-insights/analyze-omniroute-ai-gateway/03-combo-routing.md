---
id: "analyze-omniroute-ai-gateway-03"
title: "Combo自动故障转移与路由策略"
theme: "retrospectives-insights"
source: "article-content.md"
chapter: 3
created: "2026-07-09"
---

# Combo自动故障转移与路由策略

## Combo核心机制

Combo是OmniRoute的核心路由机制，将多个模型串成链，按优先级自动路由。当第一层模型的额度烧完或出现故障时，系统会在毫秒级自动切换到下一层模型，用户几乎无感知。

## 内置路由策略

OmniRoute内置17种路由策略，覆盖不同使用场景的需求。

## auto策略

auto策略是默认的智能路由策略，根据实时健康度、额度、成本、延迟、成功率五个维度综合打分，自动选择当前最优的模型进行调用。

## auto策略变体

| 策略变体 | 优化目标 |
|---|---|
| auto/coding | 优化代码质量 |
| auto/fast | 优化响应速度 |
| auto/cheap | 省钱优先 |
| auto/offline | 离线模式 |
| auto/smart | 探索新模型 |
