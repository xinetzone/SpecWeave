---
source: "agent-skills-open-standard-wiki.md#一概述"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/agent-skills-wiki/00-overview.toml"
title: "一、概述"
---
# 一、概述

## 1.1 什么是 Agent Skills？

Agent Skills 是一个**轻量级、开放的格式标准**，最初由 Anthropic 开发，现已成为跨产品的 AI 智能体能力扩展标准。它通过将专业知识和工作流打包成可移植、版本控制的文件夹，让智能体能够按需加载专业能力。

**核心理念**：一个 Skill 就是一个包含 `SKILL.md` 文件的文件夹。该文件包含元数据（至少 `name` 和 `description`）和指导智能体执行特定任务的指令。Skills 还可以捆绑脚本、参考资料、模板和其他资源。

## 1.2 为什么需要 Agent Skills？

智能体虽然能力越来越强，但往往缺乏可靠完成实际工作所需的上下文。Skills 通过以下方式解决这个问题：

- **领域专业知识**：将专业知识（从法律审查流程到数据分析流水线再到演示文稿格式化）捕获为可复用的指令和资源
- **可重复工作流**：将多步任务转化为一致、可审计的流程
- **跨产品复用**：一次构建，可在任何兼容 Skills 的智能体中使用

## 1.3 支持的客户端（40+）

包括但不限于：Claude Code、Cursor、GitHub Copilot、VS Code、**Trae**、Roo Code、Goose、Kiro、OpenHands、Letta、Mistral Vibe、Gemini CLI、Junie、Qodo、Mux、Amp、Tabnine、Databricks、Laravel Boost、Factory、Workshop、Emdash、Piebald、pi、Superconductor、VT Code、Ona、Agentman、Bub、Vita、DeepCode、Snowflake、Spring AI、Firebender、Mistral Vibe、Google AI Edge Gallery、OpenCode 等。

完整列表见：[agentskills.io/clients](https://agentskills.io/clients)
