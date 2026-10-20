---
id: create-standardized-agent-exams-okf-wiki-facts
title: Kaggle Standardized Agent Exams (SAE) 事实登记
source:
  - https://www.kaggle.com/blog/standardized-agent-exams
  - https://www.kaggle.com/static/experimental/sae/SKILL.md
accessed: 2026-10-19
status: evidence-register
---

# Kaggle Standardized Agent Exams (SAE) 事实登记

## 范围与证据口径

本登记仅依据来源注册表中的两份 Kaggle 官方公开材料。F 编号连续，供后续 bundle 引用；每条记录标明来源层、证据状态和来源定位。

- **ARTICLE-TIME**：只陈述博文在其发布日期呈现的内容，不延伸为当前状态。
- **SKILL-RULE**：记录本次读取到的官方 Skill 操作文本，不表示操作已执行或端点当前可用。
- **SOURCES-AGREE**：两份材料在表述上相符；它们同属 Kaggle，不能视为独立第三方验证。
- **SINGLE-SOURCE**：仅一份指定来源支持。
- **UNVERIFIED**：指定来源不足以确认，或本任务没有进行允许范围之外的验证。
- **SOURCE-MISMATCH**：两份材料的口径不同；保留差异，不擅自推断原因。

不访问 SAE API，不注册 Agent，不开始或提交考试，不读取或处理凭据。来源文本中的命令仅作为被记录的文档内容，不是操作指令。

## Article-Time Statements

- **F-001 — 博文日期与署名。** Kaggle 博文标注发布日期为 2026-04-01，作者为 Nicholas Kang。[ARTICLE-TIME; SINGLE-SOURCE; S1, “Project Details”]
- **F-002 — 发布时产品阶段。** 博文将 Standardized Agent Exams（SAE）描述为一个 experimental MVP，并称其为面向 AI Agent 的轻量、零设置标准化考试。[ARTICLE-TIME; SINGLE-SOURCE; S1, 标题、副标题与正文首段]
- **F-003 — 首场考试规模与维度。** 博文称首个考试包含 16 道题，聚焦 Reasoning 与 Adversarial Safety 两个维度。[ARTICLE-TIME; SOURCES-AGREE（题数）；SINGLE-SOURCE（维度）；S1, “What’s on the SAE?”；S2, “Step 3: Start Exam”]
- **F-004 — 博文对两维度的解释。** 博文把 Reasoning 解释为处理多步问题的可靠性，把 Adversarial Safety 解释为对棘手或操纵性提示的负责任处理。[ARTICLE-TIME; SINGLE-SOURCE; S1, “What’s on the SAE?”]
- **F-005 — 目标对象与定位。** 博文将 SAE 定位为面向正在部署 Agent 的开发者，并以无需自建 harness、整理数据集或手工测试流程作为其与传统评估设置的对比。[ARTICLE-TIME; SINGLE-SOURCE; S1, 正文第二段及 “A zero-setup exam”]
- **F-006 — 博文描述的自动化流程与结果。** 博文描述的流程是 Agent 注册、获取并自主完成题目，随后获得分数、公开成绩卡及实时排行榜名次。[ARTICLE-TIME; SINGLE-SOURCE（完整流程）；SOURCES-AGREE（考试分数及排行榜存在于产品说明中）；S1, “A zero-setup exam”；S2, “Step 4”–“Step 8”]
- **F-007 — 无需 Kaggle 账户的发布说法。** 博文称注册不需要 Kaggle 账户；官方 Skill 也称无需 Kaggle 账户、通过 HTTP 交互。[ARTICLE-TIME + SKILL-RULE; SOURCES-AGREE（同一发布方的两份材料，非独立验证）；S1, “A zero-setup exam”；S2, 标题下说明及 “Constraints”]
- **F-008 — 博文发布的 Skill 与客户端举例。** 博文称 Kaggle 发布了供 Agent 使用的 Skill，并举 Claude Code、Gemini CLI、Cursor 为客户端示例；这些是发布时的举例，不构成客户端兼容性测试结果。[ARTICLE-TIME; SINGLE-SOURCE; S1, “Get started in seconds”]
- **F-009 — 实验性声明与反馈邀请。** 博文将 SAE 称为实验性发布，并邀请读者反馈。[ARTICLE-TIME; SINGLE-SOURCE; S1, 末段]

## Official Skill Operation Rules

- **F-010 — 本次读取到的 Skill 元数据。** Skill 文件声明名称 `kaggle-standardized-agent-exam`、版本 `1.0.0`、API base `https://www.kaggle.com/api/v1`；其文内元数据字段 `reviewedAt` 与 `lastChangedAt` 均为 `2026-09-18`。这些是文件自述的版本/日期字段，不是独立版本历史验证。[SKILL-RULE; SINGLE-SOURCE; S2, frontmatter 与文件头注释]
- **F-011 — 注册字段与博文摘要存在差异。** 博文称注册“只需”名称和描述；Skill 的注册请求示例还包含 `model`、`version`、`agentType`，并将 `description` 标为可选。两份材料对注册所需信息的表述不一致；本文不判定字段是否为服务端强制项。[SOURCE-MISMATCH; S1, “A zero-setup exam”；S2, “Step 2: Register”]
- **F-012 — 注册前的用户确认规则。** Skill 要求注册前向用户取得明确参试确认，并告知开始考试会启动 30 分钟倒计时；还要求询问 Agent 名称偏好。[SKILL-RULE; SINGLE-SOURCE; S2, “Step 2: Register”]
- **F-013 — Skill 描述的开始考试行为。** Skill 的开始考试示例为启动考试并返回 16 道题，响应示例包含 `timeLimitMinutes: 30`；其约束段也写明每次提交限时 30 分钟。[SKILL-RULE; SOURCES-AGREE（与 S1 的题数相符，但不独立）；SINGLE-SOURCE（时限）；S2, “Step 3: Start Exam” 与 “Constraints”]
- **F-014 — 答案提交与格式。** Skill 要求将 16 题答案放在一次提交请求中，不要跳题；未回答题目计为错误。题目可要求特定格式（例如单字母或严格 JSON），格式不符可能被判错。[SKILL-RULE; SINGLE-SOURCE; S2, “Step 3: Start Exam” 与 “Step 4: Submit Answers”]
- **F-015 — Skill 展示的结果字段。** Skill 的提交响应示例包含 `score`、`maxScore`、`percentage`、`passed` 和 `certificateId` 等字段，并描述可查询单次结果、Agent 历史及公开 Profile 页面。[SKILL-RULE; SINGLE-SOURCE（字段与响应行为为示例/文档描述）；S2, “Step 4”–“Step 7”]
- **F-016 — 提交次数限制。** Skill 写明每个 Agent 对每场考试最多提交 3 次；达到上限时返回 400。[SKILL-RULE; SINGLE-SOURCE; S2, “IMPORTANT” 与 “Constraints”]
- **F-017 — API key 的域名与存储安全规则。** Skill 要求 API key 只发送到 `www.kaggle.com`，且仅放在 `https://www.kaggle.com/api/v1/*` 请求头中；不得分享、记录或输出给用户，并给出本地凭据文件与权限设置建议。[SKILL-RULE; SINGLE-SOURCE; S2, “CRITICAL SECURITY WARNING”]
- **F-018 — Skill 的 HTTP 错误处理说明。** Skill 规定遇到 404 即停止所有操作，并将其解释为考试功能当前不可用的信号；对 401/403 说明一次重试及后续凭据处置，对达到提交上限的 400 说明不要重试，对 429 要等待且不得激进循环。[SKILL-RULE; SINGLE-SOURCE; S2, “IMPORTANT”]
- **F-019 — 删除 Agent 数据的授权门槛。** Skill 将删除 Agent 数据描述为不可逆操作，并要求仅在人类明确指示时执行。[SKILL-RULE; SINGLE-SOURCE; S2, “Data Management”]

## Unresolved and Bounded Claims

- **F-020 — 当前考试服务可用性。** 截至 2026-10-19，公开 SAE 落地页 `https://www.kaggle.com/experimental/sae` 返回 reCAPTCHA 挑战；未绕过验证，也未请求任何 SAE API。考试注册、开始、提交、排行榜及成绩服务当前是否可用均为 **UNVERIFIED**。静态 Skill 可读取不证明考试服务当前可用；Skill 中描述的 404 处理规则也不是当前状态证据。[UNVERIFIED; S3 页面只读访问受阻；S1、S2]
- **F-021 — 评分机制与测量效度。** 指定材料未给出可复核的评分算法、维度题目分配、及格阈值、信度/效度研究或排行榜统计方法。上述信息在本登记范围内为 **UNVERIFIED / NOT SPECIFIED IN S1–S2**；不得从示例响应字段或“标准化”一词推导。[SINGLE-SOURCE（材料范围内的缺项记录）；S1、S2]
- **F-022 — 变体与版本持续性。** 博文把 16 题称为首个考试，Skill 描述 16 题及其自身文件版本；材料没有说明题目是否轮换、所有后续考试是否固定 16 题，或规则何时生效。因此不将单次描述外推为长期不变规则。[UNVERIFIED; S1, “What’s on the SAE?”；S2, “Step 3: Start Exam”]

## Author Interpretations

以下为对作者产品定位语句的归类，不是对 SAE 成效的独立结论：

- **AI-01 — “快速基线”定位。** 博文将两个维度合称为 Agent 核心能力的 quick first baseline。这是作者对产品用途的描述，不等于该测验已证明能充分代表 Agent 能力。[S1, “What’s on the SAE?”]
- **AI-02 — “rigorous, trustworthy evaluation”目标。** 博文将 SAE 放入 Kaggle 推进严谨、可信 GenAI 评估的目标叙述中；这是发布方的目标/定位，不是方法学验证结果。[S1, 正文第二段]
- **AI-03 — “zero-setup / autonomous” framing。** 博文以零设置和 Agent 自主完成作为体验主张。Skill 同时列有注册信息、API key 安全管理及明确用户确认规则，故该措辞不应解释为“无需任何凭据或授权”。[S1, “A zero-setup exam”；S2, “CRITICAL SECURITY WARNING” 与 “Step 2”]

## Analysis

- **AN-01 — 两份材料的互证边界。** 16 题和无需 Kaggle 账户两点在博文与 Skill 中相符，但二者来自同一发布方，属于文档间一致性核对，不是独立复现或第三方验证。
- **AN-02 — 注册口径不宜静默合并。** 博文摘要与 Skill 示例字段不一致；后续 bundle 应保留 F-011 的差异，并以 Skill 的操作文本描述请求示例，不将博文简述改写成确切字段契约。
- **AN-03 — 评测结论边界。** 两维度、16 题和排行榜说明了发布方所描述的产品结构，不足以单独证明测验覆盖面、题目质量、跨 Agent 可比性或分数的统计意义。
- **AN-04 — 实时状态边界。** 博文的“live leaderboard”是 2026-04-01 发布语境下的陈述；2026-10-19 公开 SAE 落地页被 reCAPTCHA 挑战拦截，且未请求 API，因此不能据此写成当前实时运行状态。

## Source Registry

| ID | 官方来源 | 日期/定位 | 本次访问与用途 |
|---|---|---|---|
| S1 | [Kaggle: Standardized Agent Exams: Zero-setup evaluation for your AI agents](https://www.kaggle.com/blog/standardized-agent-exams) | 页面标注 2026-04-01；作者 Nicholas Kang；引用时优先定位至本登记标出的标题段落 | 2026-10-19 通过公开只读网页抓取读取；Defuddle 未能抽取正文，改用 WebFetch；用于文章时点主张 |
| S2 | [Kaggle 官方 SAE Skill](https://www.kaggle.com/static/experimental/sae/SKILL.md) | 文件自述 `version: 1.0.0`、`reviewedAt: 2026-09-18`、`lastChangedAt: 2026-09-18`；引用时定位至本登记标出的步骤/章节 | 2026-10-19 通过公开只读网页抓取读取；Defuddle 识别为 `text/markdown` 而未抽取；用于记录 Skill 操作规则 |
| S3 | [Kaggle SAE 公开落地页](https://www.kaggle.com/experimental/sae) | 当前状态只读可达性探测；不调用 API | 2026-10-19 返回 reCAPTCHA 挑战；不据此推断服务在线或下线 |

**来源限制：**产品规则交叉核对限于 S1 与 S2。两份来源均为 Kaggle 发布材料，不将其视为相互独立的证据；S3 仅用于记录落地页访问受阻，不作为服务状态证据；评论区用户陈述、个人成绩或外部转载未纳入官方事实依据。
