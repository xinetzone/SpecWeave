---
id: "bp-plugin-bridge-standard-integration"
title: "插件桥接规范集成法"
type: "methodology"
date: "2026-08-12"
maturity: "L1-draft"
source: "Hermes-SpecWeave 集成里程碑（七概念方法论编排·场景1里程碑复盘）"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/plugin-bridge-standard-integration.toml"
related_patterns: ["bp-integration-over-invention", "bp-layered-chained-spec"]
tags: ["agent-platform", "workspace-governance", "plugin", "context-routing", "integration"]
validation_count: 1
reuse_count: 1
documentation_level: "complete"
---
# 插件桥接规范集成法

## 触发场景

- 当需要把一套既有的工作区规范（AGENTS 启动协议 / 任务路由 / Skill 门面 / 验证脚本）接入一个已运行的 Agent 平台（Hermes、Claude Code、Codex 等）时，使用这个模式
- 适用于：规范治理与 Agent 平台集成、目录感知的上下文注入、组织级 AGENTS 协议的自动化落地
- 不适用于：规范平台本身即 Agent 平台（无需桥接）、接入需求只需一次性手工操作（无需做成可复用插件）、平台禁止第三方扩展（无法以插件/技能叠加）

## 核心做法

以插件 + 技能叠加的方式接入，不改动平台核心，遵循 Footprint Ladder 原则：

| 步骤 | 名称 | 输入 | 输出 | 关键标准 |
|:---:|------|------|------|---------|
| S1 | 能力盘点 | 规范资产清单 + 平台扩展点 | 桥接组件映射表 | 每个规范能力至少对应一个平台扩展点 |
| S2 | 目录感知检测 | 工作区路径约定 + 签名关键词 | detector 模块 | 用路径 + 签名关键词判定工作区，跨平台 pathlib |
| S3 | 上下文注入 | 规范核心内容 | pre_llm_call hook | 注入放用户消息层，不改 system prompt，保 prompt cache |
| S4 | 能力桥接 | 任务→规范路径映射 | route/check 工具 + slash/CLI | 能力按工作区目录服务门控，无匹配回退默认路由 |
| S5 | 校验复用 | 插件自身逻辑 | verify 复用插件模块 | 校验调用插件真实函数，避免双份逻辑漂移 |

**执行要点**：

1. **不改核心（Footprint Ladder）**：接入通过插件与技能叠加，绝不修改平台核心源码，保证平台可独立升级。
2. **用户消息层注入**：把规范上下文注入用户消息层而非 system prompt，保持系统提示词字节级稳定，不破坏三层 prompt cache。
3. **目录感知服务门控**：工具是否可见取决于 cwd 是否在工作区内，跨项目切换即自动切换规范上下文。
4. **复用自身逻辑校验**：自动化脚本通过 importlib 加载插件真实模块做校验，避免双份实现漂移。
5. **三入口覆盖**：同时提供斜杠命令（人）、CLI（脚本/CI）、工具（Agent）三入口。

## 为什么需要这个模式

**解决"规范有人读没人用"的困境**：工作区规范写好了，但 AI 代理每次会话都要人工记忆路由与流程，规范难以真正落地。桥接模式让规范在正确目录下自动生效，把"人记"变成"机器自动路由"。

**保留平台演进能力**：直接改平台核心的接入方式会让平台无法升级，桥接方式（插件叠加）保持了接入方与被接入方的解耦，双方可独立演进。

**让治理可感知、可验证**：桥接不只是注入上下文，还要提供 `verify` 通道，让"规范是否生效"成为可判定的结果，而非黑盒。

## 反模式（不要这么做）

- ❌ **直接改平台核心**：修改 Agent 平台源码接入——后续平台升级会冲突，维护成本急剧上升
- ❌ **注入 system prompt 破坏缓存**：把规范塞进 system prompt——破坏三层 prompt cache，token 成本上升
- ❌ **手动记忆规范路径**：让人工逐个记忆任务→规范映射——路径漂移后无人可维护
- ❌ **校验逻辑双份实现**：自动化脚本重写一套工作区判定——逻辑漂移，修复一处漏一处
- ❌ **无 verify 判据**：接入后没有"是否生效"的判定标准——无法确认接入成功，也难以排障

## 检验标准

做完之后怎么知道做对了？

- **标准1（自动生效）**：在规范工作区内开会话，无需任何用户操作即注入规范上下文
- **标准2（目录感知）**：同一用户离开工作区后能力自动消失/恢复，切换即生效
- **标准3（缓存保留）**：系统提示词字节级不变，prompt cache 命中率不下降
- **标准4（可验证）**：存在 CLI/命令能确认工作区识别与路由结果
- **标准5（可复用校验）**：自动化脚本复用插件自身逻辑，无双份实现

## 迁移示例

这个模式还能用在什么其他场景？

- **场景1（Claude Code 接入组织 AGENTS）**：把组织级 AGENTS.md 启动协议接入 Claude Code，通过 hook + slash command 实现目录感知的规范自动生效
- **场景2（Codex 接入 MCP 规范）**：把 MCP 服务规范接入 Codex 环境，路由工具自动返回规范路径
- **场景3（多项目规范矩阵）**：一个 Agent 平台服务多个项目，每个项目有自己的 AGENTS，通过 cwd 探测切换规范上下文

## 验证案例

| 案例编号 | 任务 | 验证日期 | 结果 |
|---------|------|---------|------|
| hermes-specweave-integration | Hermes 接入 SpecWeave 工作区规范 | 2026-08-12 | ✅ 模式验证通过 |

## 关联资源

- 配套模式：[整合优于发明模式](integration-over-invention.md)（本模式是其"Agent 平台扩展"领域的细化）
- 分层链式规格模式：[分层链式规格模式](layered-chained-spec.md)
- 里程碑复盘报告：[retrospective-hermes-specweave-integration-20260812](../../reports/milestone/retrospective-hermes-specweave-integration-20260812.md)
