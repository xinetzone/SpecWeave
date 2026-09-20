---
id: "analyze-omniroute-ai-gateway-04"
title: "Quota-Share团队额度共享"
theme: "retrospectives-insights"
source: "article-content.md"
chapter: 4
created: "2026-07-09"
---

# Quota-Share团队额度共享

## 功能概述

Quota-Share功能支持同一订阅账号下多把key按权重分配额度，实现团队成员共享AI订阅资源。

## 适用场景

特别适用于小团队共用Codex Pro或Kimi Coding Plan等付费订阅的场景，避免单人独占额度。

## 解决的核心问题

防止一个人烧光5小时额度导致其他人被锁死，通过权重分配确保团队成员公平共享订阅资源。

## 故障隔离

Quota-Share还提供故障隔离能力，一个模型挂了不会拖累整个连接，系统会自动切换到其他可用模型，保证团队工作流的连续性。
