---
id: "api-interactive-parameter-collection"
title: "AskUserQuestion 分步交互式收集参数模式"
category: "best-practices"
tags: ["API", "AskUserQuestion", "交互", "参数收集", "多选", "自由文本", "会话"]
date: "2026-08-07"
last_updated: "2026-08-07"
status: "stable"
author: "SpecWeave"
summary: "用 AskUserQuestion 分步交互式收集 API 参数的模式：一次一问、等回答、执行前确认、可回退；多选用 AskUserQuestion、自由文本用普通消息、依赖参数串行、独立参数可批量。"
security_level: "public"
knowledge_type: "procedural"
validation_status: "verified"
reuse_count: 0
integrity: "unchecked"
---

# AskUserQuestion 分步交互式收集参数模式

> 所有可枚举参数必须用 **AskUserQuestion 工具**，采用**会话式、逐步**方式收集，在终端渲染一个可用方向键导航的交互选择器。来源为 ListenHub 系列 skill 的共享实现。

**沉淀来源**：`chaos/flexloop/.agents/skills/shared/common-patterns.md`

---

## 一、会话行为（强制）

1. **一次一问。** 每次只问一个问题，然后 STOP 等待用户回答，再进行下一步。除非参数**明确相互独立**（如分辨率 + 宽高比），否则不要一条消息批量问多步。
2. **等待回答。** 绝不假设默认值并跳过。用户未回答就不得继续。
3. **执行前确认。** 所有参数收集完毕后，汇总用户的选择，并在调用任何 API 前请用户确认。这是最后一道闸门。
4. **可回退。** 若用户改变主意或认为某处不对，修改并重新询问，而不是硬推下去。

---

## 二、如何提问

**始终用 AskUserQuestion 工具**——不要把问题当纯文本打印。每个步骤的 `Question` / `Options` 直接映射到 AskUserQuestion 参数：

```
SKILL.md 中的步骤定义:            →  AskUserQuestion 工具调用:

Question: "What language?"        →  question: "What language?"
  - "Chinese (zh)" — Mandarin     →  options: [{label: "Chinese (zh)", description: "Mandarin"}
  - "English (en)" — English      →           {label: "English (en)", description: "English"}]
```

**自由文本**步骤（话题、URL、prompt）则用普通文本消息提问，等待用户输入。

---

## 三、参数类型与收集方式

| 参数类型 | 收集方式 | 示例 |
|----------|----------|------|
| **多选 → AskUserQuestion** | 交互选择器 | language、mode、speaker 数量、生成风格、分辨率、宽高比 |
| **自由文本 → 普通消息** | 文本框输入 | 话题、正文、URL、图像 prompt |
| **依赖参数 → 串行** | 先问前置，再问后续 | speaker 列表依赖 language——先问语言，再拉取并展示 speaker 列表 |
| **独立参数 → 可批量** | 一次 AskUserQuestion 多问题 | 分辨率 + 宽高比可在一次调用中同时问 |

**要点：**

- **Options 需含描述**：不仅 label，还要说明每个选项的含义（description 字段）。
- **依赖关系处理**：当某个参数的可选项取决于前一个参数时，必须先收集前置参数、再动态生成后续选项。
- **批量边界**：仅当参数确实彼此独立时才合并到一次调用；有依赖的必须串行。

---

## 四、变更历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-08-07 | 初始版本：沉淀 AskUserQuestion 分步交互式收集参数模式（会话行为、提问方式、参数类型与收集映射） |
