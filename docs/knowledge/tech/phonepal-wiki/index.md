---
okf_version: "0.2"
type: Reference
id: "phonepal-wiki"
title: "PhonePal（xiaoman）：Android 手机 AI 助手源码学习 Wiki"
description: "系统学习开源 Android 助手 PhonePal 的源码：双模型分工、模型外安全闸门、纯 JVM 内核、可读文件式技能与记忆、无障碍手眼；82 条编号事实、4 条架构洞察、11 篇概念、3 个示例与 3 份信源/核验文档"
category: "tech"
tags: [phonepal, xiaoman, android, agent, accessibility, llm, kotlin, okf]
date: "2026-11-12"
last_verified: "2026-11-12"
next_review: "2027-05-12"
status: "stable"
author: "SpecWeave Agent（方法论编排 session sc-20261112-phonepal-wiki）"
summary: "PhonePal 把「会思考的部分」和「会碰 Android 的部分」彻底分开：聊天模型只理解与调工具，操作模型每步只决定一个动作，安全判定放在模型之外的 PolicySentinel，技能与记忆都是人类可读文件。本包基于 commit 580fdf7 的 59 个 main Kotlin 文件、8 个模块与 3400+ 行测试（2669 行 Kotlin + 739 行 Python），给出 82 条可溯源事实、4 条架构洞察与 11 篇概念教程；核心结论是：可测试性来自接口收敛，安全性来自规则层而非提示词，鲁棒性来自宽容解析加显式反馈。"
security_level: "public"
knowledge_type: "procedural+conceptual"
validation_status: "verified"
source: "references/00-source-inventory.md（commit 580fdf750f946a6e411c3f54a86443c66aa46652）"
---

# PhonePal（xiaoman）：Android 手机 AI 助手源码学习 Wiki

> 一句话摘要：**PhonePal 是一个「框架 + 技能」的手机助手**——框架负责眼睛（截屏 + 无障碍节点）、手（手势与输入）、记忆、安全闸门和模型调用；具体场景（打车、外卖、改设置）由用户以 Markdown/YAML 技能添加，不用重新打包 APK。它最值得学的不是「怎么调模型」，而是**怎么把不可让渡的安全判断放在模型之外，并把手机操作变成可单元测试的接口**。

- **编排 session**：`sc-20261112-phonepal-wiki`
- **场景与链路**：场景 4 知识沉淀，`R→I→E→V→C`，depth=standard
- **信源快照**：`git@github.com:aduoge/xiaoman.git`，commit `580fdf750f946a6e411c3f54a86443c66aa46652`（2026-11-01），MIT
- **事实规模**：F-001 ~ F-082（82 条，路径 + 行号可回溯）
- **文档规模**：11 篇概念 + 3 个示例 + 3 份信源/核验文档

---

## 导航

```{toctree}
:maxdepth: 2
:hidden:

concepts/index
examples/index
references/index
log
```

| 类别 | 文档 | 说明 |
|---|---|---|
| **入门** | [PhonePal 全景](concepts/00-overview.md) | 一分钟心智模型、关键数字、它不是什么 |
| **入门** | [分层与依赖](concepts/01-architecture.md) | 8 个模块、依赖方向、AppGraph 装配、数据目录 |
| **主链路** | [一轮聊天](concepts/02-chat-and-tools.md) | 系统提示词三段、6 个工具、8 轮工具循环 |
| **主链路** | [操作循环](concepts/03-operator-loop.md) | 观察 → 一步动作 → 反馈、卡死检测、受保护屏幕 |
| **主链路** | [安全闸门](concepts/04-sentinel.md) | deny/ask/allow、17 个确认词、任务级授权与审计 |
| **数据** | [记忆](concepts/05-memory.md) | Basic Memory 格式、原子写、中文 BM25、howto 沉淀 |
| **扩展** | [技能与 flow](concepts/06-skills-and-flows.md) | 7 个 frontmatter 键、8 种 flow 步骤、校验与坑 |
| **扩展** | [无障碍手眼](concepts/07-hands-accessibility.md) | 截屏节流、黑帧识别、节点压缩、手势执行 |
| **扩展** | [模型客户端](concepts/08-llm-client.md) | 重试、JSON 模式降级、图片编码、密钥脱敏 |
| **工具** | [CLI 与轨迹](concepts/09-cli-and-traces.md) | 6 个命令、调试桥、三层证据 |
| **迁移** | [工程模式与边界](concepts/10-engineering-patterns.md) | 五条可迁移模式、反模式、它不解决的问题 |
| **示例** | [技能解剖](examples/01-skill-anatomy.md) | taxi-home 逐字段拆解 + 两个对照样本 |
| **示例** | [CLI 剧本](examples/02-cli-workflow.md) | lint → push → run → traces 全流程 |
| **示例** | [测试替身](examples/03-test-doubles.md) | Harness 夹具与循环测试模板 |
| **信源** | [信源登记](references/00-source-inventory.md) | commit、计数、复现命令、持久性说明 |
| **核验** | [API 索引](references/01-api-map.md) | 类型/签名/常量位置，可 Grep 核对 |
| **核验** | [对抗审查](references/02-adversarial-review.md) | 四视角审查与修复记录 |

---

## 1. R 阶段：事实速览

完整 82 条见 [信源登记](references/00-source-inventory.md) 与包外的事实清单；这里只给最影响理解的一组。

| 主题 | 关键事实 |
|---|---|
| 模块 | 8 个 Gradle 模块；5 个 `core-*` 不引用任何 Android API，第三方运行时依赖只有 OkHttp 与 snakeyaml [F-001/F-077/F-078] |
| 双模型 | `ModelRole.CHAT` 与 `ModelRole.OPERATOR` 两个独立客户端 [F-014] |
| 聊天 | 系统提示词 = 人设 + 技能索引 + 记忆命中；最多 8 轮工具；历史窗口 20 条 [F-021/F-022] |
| 工具 | 6 个：5 个记忆/技能工具 + `phone_task`；工具错误统一转 JSON [F-030/F-031] |
| 操作 | 每步一个 `Action`；11 种动作；坐标 0..1000；解析失败 3 次才终止 [F-012/F-010/F-026] |
| 安全 | 先 deny（受保护屏/密码框/apps 越界）、再 ask（17 个内置确认词 + 技能追加）、最后 allow [F-039/F-042] |
| 记忆 | Basic Memory Markdown；原子写；mtime/size 增量索引；BM25 + 双字主词/单字弱词 [F-045/F-051/F-048] |
| 技能 | 7 个 frontmatter 键；8 种 flow 步骤；坏技能隔离；用户技能覆盖内置 [F-054/F-056/F-053] |
| 手眼 | 截屏 1050 ms 节流；黑帧判受保护；节点压缩到 200；节点优先、坐标兜底 [F-063/F-064/F-065] |
| 证据 | 三层：logcat 事件行、trace.jsonl、audit.jsonl + 每步截图 [F-071] |
| 测试 | 162 个 Kotlin `@Test` + 68 个 Python 测试函数；CI 不依赖真机 [F-075/F-076] |

## 2. I 阶段：四条洞察

| # | 洞察 | 一句话 |
|---|---|---|
| 1 | 双模型 + 模型外闸门 | 安全边界不写在模型能读的提示词里，而写在模型看不见的规则层；技能只能加确认词 [F-039/F-042] |
| 2 | 纯 JVM 内核 | 把平台能力收敛成 `Device`/`LlmClient`/`MemoryStore`/`Sentinel`，手机自动化因此可单测 [F-013/F-077] |
| 3 | 宽容解析 + 显式反馈 | 模型失败是常态；解析器负责把失败变成下一轮可纠正的反馈 [F-036/F-026] |
| 4 | 文件即契约 | 技能与记忆都是人类可读文件；可读性本身是可扩展性与可审计性 [F-019/F-045/F-053] |

详细四元组（陈述/证据/反常识/行动）见包外 `insights.md`，正文展开见 [工程模式与边界](concepts/10-engineering-patterns.md)。

## 3. V 与 C 记录

- **V 阶段**：Grep 级 API 核验（逐项对照 [API 索引](references/01-api-map.md)）、计数断言复核（模块/枚举/确认词/启动器/工具/命令/测试方法）、链接与 frontmatter 检查；发现与修复见 [对抗审查记录](references/02-adversarial-review.md)。
- **C 阶段**：包内沉淀五条可迁移模式（[10 工程模式与边界](concepts/10-engineering-patterns.md)）；本包不向 `docs/retrospective/patterns/` 另建独立模式文档，模式正文与证据保留在知识包内，避免同一结论两处维护。

## 4. 怎么读这个包

| 你的身份 | 建议 |
|---|---|
| 产品/技术负责人 | 00 → 04 → 10：先看边界与安全，再判断能不能复用 |
| Android 工程师 | 01 → 03 → 07：看接口分层与无障碍实现 |
| Agent 工程师 | 02 → 03 → 08 → 10：看提示词、循环、模型客户端与模式 |
| 想写技能的人 | 06 → 05 → [示例 01](examples/01-skill-anatomy.md) → [示例 02](examples/02-cli-workflow.md) |
| 只想快速了解 | 00 的前两节 + 04 的规则表 |

## 5. 维护提示

- 信源无 tag，只有两个提交；任何上游更新都需按 [信源登记](references/00-source-inventory.md) 重新固定 commit 并重采事实。
- 最易过期的事实：CLI 命令与参数、模型默认 Base URL、Sentinel 规则与确认词列表、无障碍截图限制（随 Android 版本变化）。
- 复核时点：`2027-05-12`（发布后 6 个月）。
