---
source: "agent-skills-open-standard-wiki.md#二核心机制渐进式披露progressive-disclosure"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/agent-skills-wiki/01-progressive-disclosure.toml"
id: "agent-skills-wiki-progressive-disclosure"
title: "二、核心机制：渐进式披露（Progressive Disclosure）"
---
# 二、核心机制：渐进式披露（Progressive Disclosure）

智能体通过三阶段加载 Skills，保持上下文窗口高效使用：

| 阶段 | 加载内容 | Token 预算 | 触发时机 |
|------|---------|-----------|---------|
| **1. 发现（Discovery）** | 仅 `name` + `description` | ~100 tokens | 智能体启动时 |
| **2. 激活（Activation）** | 完整 `SKILL.md` 正文 | &lt; 5000 tokens（推荐） | 用户任务匹配描述时 |
| **3. 执行（Execution）** | 按需加载脚本/参考/资源 | 按需 | 执行过程中需要时 |

**关键优势**：完整指令仅在任务需要时加载，因此智能体可以保留许多 Skills 在手边，而上下文占用很小。
