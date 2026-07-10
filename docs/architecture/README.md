---
id: "architecture-index"
title: "架构设计文档库"
x-toml-ref: "../../.meta/toml/docs/architecture/README.toml"
category: "architecture"
date: "2026-07-09"
---
# 架构设计文档库

> **本目录**存放 SpecWeave 项目的核心架构设计文档，涵盖多智能体协作流程、系统分层设计、关键机制时序图等架构层面的正式规范。

## 🎯 主题概述

架构文档是 SpecWeave 规范体系的"蓝图层"，定义了系统从启动到交付的完整协作流程与冲突解决机制。所有架构文档均包含可执行的 Mermaid 流程图/时序图，并与 `.agents/protocols/` 下的具体协议文件一一对应。

### 核心设计原则

| 原则 | 说明 |
|------|------|
| 📊 **可视化优先** | 所有流程均以 Mermaid 图表呈现，避免纯文字描述 |
| 🔗 **可追溯性** | 每个架构层级都链接到对应的协议规范文件 |
| 🛡️ **冲突前置** | 冲突解决机制在架构层面定义，而非执行时临时处理 |
| 📋 **分级仲裁** | 职责冲突→Orchestrator、技术分歧→Architect、资源竞争→Orchestrator，无法解决则升级人工 |

---

## 📚 文档索引

| 文档 | 一句话摘要 | 核心内容 | 适用场景标签 |
|------|-----------|---------|-------------|
| [multi-agent-collab.md](multi-agent-collab.md) | 多智能体协作流程架构（7层流程图+冲突解决时序图） | ①启动协议→②任务路由→③中心化模式→④去中心化模式→⑤任务交接→⑥冲突解决→⑦交付验收 | `multi-agent` `collaboration` `architecture` `conflict-resolution` `mermaid` |

---

## 🗺️ 架构层级速览

`multi-agent-collab.md` 中定义的7个核心层级：

| 层级 | 颜色 | 核心内容 | 对应规范文件 |
|------|------|---------|-------------|
| ① 启动协议层 | 🔵 蓝色 | AGENTS.md启动四步协议 + vendor嵌套路由 | [onboarding-protocol.md](../../.agents/protocols/onboarding-protocol.md) |
| ② 任务路由层 | 🟣 紫色 | 复杂度判断 + 协作模式选择 | [collaboration-scenarios.md](../../.agents/roles/collaboration-scenarios.md) |
| ③ 中心化模式 | 🟠 橙色 | Orchestrator主导的六阶段标准流程 | [roles/](../../.agents/roles/README.md) |
| ④ 去中心化模式 | 🟢 绿色 | 角色引用直连 + messaging协议 | [messaging.md](../../.agents/protocols/messaging.md) |
| ⑤ 任务交接层 | 🔴 浅粉 | YAML格式交接 + 确认/退回机制 | [handoff.md](../../.agents/protocols/handoff.md) |
| ⑥ 冲突解决层 | 🔴 红色 | 三类冲突 + 分级仲裁 + 人工升级 | [conflict-resolution.md](../../.agents/protocols/conflict-resolution.md) |
| ⑦ 交付验收层 | 🟦 青色 | 质量门禁 + 产出物归档 + 记录留存 | [development-standards.md](../development-standards.md) |

---

## 🧭 阅读路径建议

| 读者类型 | 推荐阅读路径 |
|---------|-------------|
| 🆕 新智能体/新成员 | [multi-agent-collab.md](multi-agent-collab.md) → 按①→⑦顺序通读，理解完整协作流程 |
| 🏗️ Architect角色 | 重点阅读③中心化模式 + ⑥冲突解决机制 + 技术分歧仲裁规则 |
| 🎼 Orchestrator角色 | 重点阅读②任务路由 + ⑤任务交接 + ⑥冲突解决（职责/资源冲突） |
| 👨‍💻 Developer/Tester | 重点阅读③中心化模式执行阶段 + ⑦交付验收质量门禁 |
| 🔍 Reviewer角色 | 重点阅读④去中心化模式（代码审查请求流程） + ⑦质量门禁 |

---

## 🔗 相关资源

- [📁 .agents/protocols/](../../.agents/protocols/README.md) - 具体协议实现文件（启动/交接/消息/冲突解决）
- [📁 .agents/roles/](../../.agents/roles/README.md) - 7个角色定义与职责矩阵
- [🏠 文档首页](../README.md) - 返回文档总入口
- [📜 AGENTS.md](../../AGENTS.md) - 全局入口与启动协议
