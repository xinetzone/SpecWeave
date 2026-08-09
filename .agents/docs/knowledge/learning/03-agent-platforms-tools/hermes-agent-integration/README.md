---
id: "docs-knowledge-learning-03-agent-platforms-tools-hermes-agent-integration-index"
title: "SpecWeave 接入 Hermes Agent 集成指南"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/hermes-agent-integration/README.toml"
---
# SpecWeave 接入 Hermes Agent 集成指南

> **版本提示**
> - 本文基于 Hermes Agent 插件体系（NousResearch/hermes-agent，插件文档 v2.5.0）与 hermes-okf（EliaszDev/hermes-okf v0.5.9）公开信息整理
> - Hermes 生态仍在快速演进，接口/命令可能发生不兼容变更；**所有命令与代码示例标注"示例/需验证"**
> - 与 [hermes-okf-wiki](../../01-agent-protocols-interfaces/okf-wiki/README.md) 互补：彼为基础概念教程，本文为"如何把 SpecWeave 自身接入 Hermes"的实战指导

## 本指南是什么

本指南系统说明如何将 **SpecWeave 整个工作区**（AGENTS.md 契约、`.agents/` 规范体系、skills/commands/scripts/roles、知识库 knowledge/、vendor 子模块）作为能力来源集成到 **Hermes Agent** 中，使 Hermes 能够正确识别、调用和执行 SpecWeave 的功能。

集成涉及**两条并行路径**：

1. **Hermes Agent 框架本体** — 将 SpecWeave 能力注册为 Hermes 插件（通用插件 tools/skills/hooks、内存插件 Memory Provider、上下文插件 Context Engine）
2. **Hermes OKF 记忆层** — 将 SpecWeave 知识库作为可持久化、可检索的 OKF memory bundle 挂接到 Hermes 会话

## 适合人群

- **Hermes Agent 使用者**：想让 Hermes 调用自己项目/工作区能力的开发者
- **SpecWeave 维护者**：理解如何把成熟的 AGENTS.md + .agents 能力体系暴露给外部 Agent 宿主
- **知识工程师**：需要把知识库作为 Agent 可检索记忆层挂接
- **架构师/技术决策者**：评估 Agent 能力接入与知识层方案

## 📄 文档索引

| 文档 | 说明 | 标签 |
|------|------|------|
| [集成总览与两条路径](00-overview.md) | 集成目标、两条路径总览、章节导航、前置知识 | `hermes` `integration` `overview` |
| [Hermes Agent 插件接口规范](01-hermes-plugin-interface.md) | 插件三类、发现路径、启用机制、plugin.yaml、register(ctx)、tool schema | `hermes` `plugin` `interface` |
| [SpecWeave 能力盘点与映射矩阵](02-capability-mapping.md) | SpecWeave 能力清单 → Hermes tool/skill/hook/memory provider 映射 | `specweave` `mapping` |
| [配置文件设置](03-configuration.md) | config.yaml、HERMES_HOME、project 级插件、hermes-okf 自动配置 | `hermes` `config` |
| [数据格式转换方法](04-data-conversion.md) | AGENTS.md→plugin、知识库 md→OKF concept/bundle、tool schema | `conversion` `okf` |
| [权限认证流程](05-auth-permission.md) | 插件 name 消毒、路径安全、manifest_version、API key、project 权限 | `security` `auth` |
| [调用方式示例](06-usage-examples.md) | plugins install、hermes okf、会话内工具调用、with_context 召回 | `hermes` `usage` |
| [常见问题及解决方案](07-troubleshooting.md) | 未发现/未启用/schema/provider 单实例/Windows 路径/name 冲突/restart | `faq` `troubleshooting` |
| [AGENTS.md 与 .agents/ 的自动加载机制](08-agents-md-autoload.md) | Hermes 原生加载 AGENTS.md 但不加载 .agents/ 目录；路由地图/插件/OKF 三法让规范库被识别调用 | `hermes` `context-files` `agents-md` `autoload` |

## 📖 阅读建议

根据目标选择路径：

### 快速接入路径（想尽快跑通）
```
00-overview.md → 03-configuration.md → 06-usage-examples.md → 07-troubleshooting.md
```

### 深度集成路径（想把 SpecWeave 能力完整暴露）
```
00-overview.md → 01-hermes-plugin-interface.md → 02-capability-mapping.md → 04-data-conversion.md → 05-auth-permission.md
```

### 记忆层挂接路径（专注知识库持久化）
```
00-overview.md → 04-data-conversion.md（OKF 部分）→ 03-configuration.md → 06-usage-examples.md
```

## 🔗 相关资源

- [Hermes Agent 仓库](https://github.com/NousResearch/hermes-agent)（示例来源，需验证）
- [hermes-okf 仓库](https://github.com/EliaszDev/hermes-okf)（EliaszDev/hermes-okf v0.5.9）
- [hermes-okf Wiki](https://github.com/EliaszDev/hermes-okf/wiki)（Quick-Start / CLI-Reference / Troubleshooting）
- [hermes-okf Wiki 教程](../../01-agent-protocols-interfaces/okf-wiki/README.md)（项目内，基础概念）
- [OKF 开放知识格式指南](../../01-agent-protocols-interfaces/okf-wiki/README.md)（项目内）
- [SpecWeave 能力注册中心](../../../../../capability-registry.md)（SpecWeave 能力全量索引）
- [SpecWeave skills 索引](../../../../../skills/README.md)
- [SpecWeave commands 指令集目录](../../../../../commands/README.md)
