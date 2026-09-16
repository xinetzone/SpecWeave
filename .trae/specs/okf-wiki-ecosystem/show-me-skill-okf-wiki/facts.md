---
type: Facts
id: facts-show-me-skill-okf-wiki
title: show-me Skill 博文转化事实集（F-001 ~ F-039）
date: 2026-09-16
source:
  - https://mp.weixin.qq.com/s/dG6w9Dd_vqb_qcEqaQRPsQ
  - https://www.humanlayer.dev/blog/show-me-skill
tags: [事实登记, P0核验, Agent-Skill, HumanLayer, show-me]
---

# 事实集：show-me Skill 博文转化

> 编号规则：F-001~F-030 来自博文（2026-09-06"阿胖 AI 手记"体验文），F-031~F-039 为权威核验补充。
> 标注约定：**[作者观点]** = 主观判断/类比/建议，转述为观点而非事实；**[博文转述官方]** = 博文对 HumanLayer 官方口径的转述；无标注 = 博文陈述的客观内容。
> G1 自检：本集只登记"博文说了什么/官方源说了什么"，因果分析入 concepts 层。

## A. 信源元信息

| 编号 | 事实 | 原文位置/备注 |
|------|------|--------------|
| F-001 | 博文标题《我发现一个神仙 Skill，就几行规则，没教AI任何新本事，却让我的WorkBuddy像换了个脑子！》 | #activity-name |
| F-002 | 公众号"阿胖 AI 手记"，作者署名"胖啊"，标注原创，作者 IP 属地湖南 | #js_name / #js_author_name |
| F-003 | 发布时间 2026-09-06 17:27 | #publish_time；页面单源 |
| F-004 | 体裁为个人公众号体验文，正文约 3000 字（#js_content innerText 3477 字符），配图全部为 WorkBuddy 对话与生成页截图，正文无外链、无表格 | browser_use 提取 |

## B. 问题背景（作者的剪视频工作流）

| 编号 | 事实 | 备注 |
|------|------|------|
| F-005 | 作者在构思 AI 自动剪视频工作流：输入一段 20 分钟口播，AI 自动找高光、删废话、加字幕、插 B-roll，最终输出 3 条短视频 | 博文开篇 |
| F-006 | 作者就"转写、高光提取、删废话、字幕、B-roll、配乐、渲染谁先谁后"询问 WorkBuddy，得到大量专业内容的长回答，表示看不懂整体如何运转 | 博文叙述 |
| F-007 | **[作者观点]** AI"想的很多，给的也很多"；用户只想知道"这玩意从哪儿进、经过哪儿、最后去哪儿"，而不是技术白皮书 | 观点 |

## C. show-me 基本事实（博文口径）

| 编号 | 事实 | 备注 |
|------|------|------|
| F-008 | 作者刷到名为 show-me 的 Skill，装入 WorkBuddy 后对同一问题调用，得到图形化回答（博文配图为流程图），称通俗易懂 | 博文叙述+截图 |
| F-009 | **[博文陈述]** show-me 是 HumanLayer 开源的 Skill | 核验见 F-031 ✅ |
| F-010 | 作者查看其 SKILL.md 后称：文件本身不大、就几行规则；做的事情是"别一上来给用户写小作文，能画出来，就尽量画出来" | 作者对 SKILL.md 的概括转述 |
| F-011 | **[作者观点]** 该 Skill 没教 AI 任何新能力（WorkBuddy 本来就会画 Mermaid、写 HTML），但让 AI 换了一种与人说话的方式；"没让 AI 变聪明，但让 AI 换了个脑子" | 观点 |

## D. 官方设计论据（博文转述）

| 编号 | 事实 | 备注 |
|------|------|------|
| F-012 | **[博文转述官方]** HumanLayer 发布 show-me 时吐槽：现在的 coding agent 在纸面上越来越聪明，但在"能不能让人快速读懂"这件事上体验反而变差；其做法不是让模型多说一点，而是让模型少说一点、用视觉结构说 | 核验见 F-032 ✅，转述与官方原文一致 |
| F-013 | **[作者观点/类比]** 人靠结构理解复杂事物：地铁线路图不会写成八千字文章、公司组织架构用一张图搞定；但却容忍 AI 一天写几十篇小作文 | 类比观点 |

## E. 作者实测二：方案取舍可视化

| 编号 | 事实 | 备注 |
|------|------|------|
| F-014 | 剪视频工作流两条候选路线：方案 A 先让 AI 看懂整个 20 分钟视频、挑完高光删完废话再统一剪；方案 B 先把视频切成多段分别处理最后拼接；作者疑问：字幕/B-roll 怎么办、哪个方案上下文更完整 | 博文叙述 |
| F-015 | 作者要求 WorkBuddy 不调用 skill 回答该问题，得到方案 A/B 优缺点与上下文保留的长篇文字分析；随后调用 /show-me，得到结构化图示对比 | 博文叙述+截图 |
| F-016 | **[作者观点]** show-me 不只画流程，还能把复杂方案之间的取舍结构搭出来；AI 列 10 条优缺点信息一个没少，但人真正缺的是"这两个东西到底差在哪" | 观点 |

## F. 作者实测三：HTML explainer

| 编号 | 事实 | 备注 |
|------|------|------|
| F-017 | **[博文陈述]** show-me 规则中，普通图讲不清楚时可以直接做 HTML；命令为 `/show-me as an html explainer` | 核验见 F-031/F-036 ✅ |
| F-018 | 作者将整个 AI 自动剪视频工作流需求再次发给 WorkBuddy，WorkBuddy 生成多段 HTML 讲解页，作者形容为"课件" | 作者实测+截图 |
| F-019 | 实测生成的 HTML 内容：最顶部把整个系统压成一条线；其后拆成五步"听、懂、剪、配、出"——先转写，再让大模型通读全文挑高光，根据保留内容重建新的 60 秒时间轴，字幕、B-roll、配乐挂到新时间轴上，最后统一渲染 | 作者实测输出描述 |
| F-020 | 实测生成的 HTML 专门图示了字幕时间戳问题：原视频中一句话出现在 9 分 12 秒，前面废话被剪掉 5 分多钟、成片约 60 秒，字幕不能仍在第 9 分 12 秒出现 | 作者实测输出描述 |

## G. 模式判断与使用建议（作者观点）

| 编号 | 事实 | 备注 |
|------|------|------|
| F-021 | **[作者观点]** Agent 越来越能干、知道得太多，而人脑没有随之进化；接下来真正好用的 Skill 未必全在给 AI 增加新能力，有一部分是在教 AI 做减法 | 观点（全文核心论点） |
| F-022 | **[作者观点/对比]** 作者此前分享过的 Grill Me 是"在 AI 和执行之间塞进一轮质询"（管"别急着干"）；show-me 更像"在 AI 和人类之间塞进一块白板"（管"别急着写"） | Grill Me 身份核验见 F-037 |
| F-023 | **[作者观点]** 适用场景：信息一多光靠文字脑子里很难搭出结构的任务——接手陌生项目、接触陌生复杂领域、AI 刚改完一大堆东西想知道它动了哪、AI 甩三屏文字不想读时直接调用，无需重想 Prompt | 观点 |
| F-024 | **[作者观点]** 不适用场景：改标题、写小函数、问命令这类小事没必要什么都画（"为了吃碗泡面，先画一张泡面系统架构图"） | 观点 |
| F-025 | **[作者观点]** Agent 干的活越复杂，这个 skill 的作用体现越明显 | 观点 |

## H. 安装与调用（博文口径）

| 编号 | 事实 | 备注 |
|------|------|------|
| F-026 | HumanLayer 官方仓库给出的安装命令：`npx skills add humanlayer/skills --skill show-me` | 核验见 F-031，逐字一致 ✅ |
| F-027 | 装好后可直接调用 `/show-me`，也可直接跟 Agent 说让它使用 show-me Skill | 核验见 F-031 ✅ |
| F-028 | 内容特别复杂时可试 `/show-me as an html explainer` | 核验见 F-031 ✅ |
| F-029 | WorkBuddy 内的极简安装法：直接让 WorkBuddy 搜索"show me"这个 skill 并安装；效率更高的方式是开启 WorkBuddy 的 GitHub 连接器，通过连接器搜索安装 | WorkBuddy 能力核验见 F-038 ✅ |
| F-030 | **[作者个人选择]** 作者准备把该 Skill 长期保留在 WorkBuddy 中，以后遇到"看完还得自己在脑子里重画一遍"的内容直接 /show-me | 个人选择 |

## I. 权威核验补充（R 阶段 WebSearch / 官方源）

| 编号 | 核验事实 | 权威信源 |
|------|----------|----------|
| F-031 | HumanLayer 官方博客 2026-08-12 发布《show-me: a coding agent skill for compact visual representations》，作者 Dex（Dex Horthy，@dexhorthy）；同日以 "Show HN: /show-me" 登上 Hacker News；博客正文两处给出同一安装命令 `npx skills add humanlayer/skills --skill show-me`，结尾明确"invoke `/show-me` or ask the agent to use the `show-me` skill"，并给出 `/show-me as an html explainer` 示例 | https://www.humanlayer.dev/blog/show-me-skill ；HN 镜像 https://www.libhunt.com/posts/1530852 |
| F-032 | 官方问题口径原文："tl;dr make your agent converse visually instead of in walls of prose"；"agents got more intelligent on paper, but the experience of using them got noticeably worse along this dimension"；`/show-me` prompts the agent to use concise visuals... instead of walls of prose。博文 F-012 的转述与官方口径一致 | 同 F-031 |
| F-033 | 官方设计灵感：Coda Hale 演讲《Intuition vs. Attention in Infrastructure Systems》——分析信息困难且耗神；视觉皮层经数百万年进化可毫不费力地处理丰富视觉信息；"Just as an axe must fit the human hand to be useful, software must fit the human mind to be useful" | 同 F-031 |
| F-034 | 官方列出的可视化词汇共 9 类：component trees（组件树）、call stacks（调用栈）、diagrams（图，聊天界面支持内联 Mermaid 时使用，偏好状态图与序列图）、file layouts（浅层文件树+每行一句职责）、pseudocode（伪代码）、types and signatures（类型与签名）、diff syntax（差异语法：组件/调用树/文件布局/状态控制流四种 +/- 形态）、html mockups（HTML 原型）、html diagrams（HTML 图/讲解页） | 同 F-031"What's inside"节 |
| F-035 | 官方推荐两大用法：① program design——写代码前先讨论代码形状（types、signatures、call stacks）；② 事后探索 large diffs，辅助确定 review 重点。官方触发话术示例："this is too much content. show me." | 同 F-031 |
| F-036 | HTML 形态机制：在 HumanLayer 自家产品中 Agent 可在助手回复里直接内嵌 HTML；其他编码 Agent 可将 HTML 在浏览器中打开。官方致谢 Matt Pocock 的 `/teach` skill 生成的 html explainers | 同 F-031 |
| F-037 | **口径精度补充**：Grill Me（`/grill-me`）为 Matt Pocock 发布并走红的 skill，作用是把模型变成对抗式面试官，围绕计划/设计逐决策访谈直到达成共识（正文三句话）；并非 HumanLayer 出品、不在 humanlayer/skills 仓库。博文 F-022 仅以"我之前分享的"提及、未作归属，bundle 呈现时须防止读者误归因 | https://ziyang.io/blog/2026-the-ambiguity-tax ；moderncreator.app Matt Pocock 访谈（2026-06-18） |
| F-038 | WorkBuddy 为腾讯全场景桌面 Agent 工作台（workbuddy.cn，国际文档站 workbuddy.ai），与 CodeBuddy Code 同源兼容：项目级 `.codebuddy/skills/`（每技能一目录含 SKILL.md）、`.codebuddy/commands/` 自定义斜杠命令；支持连接器（含 GitHub、飞书、钉钉等）、微信扫码登录。博文使用环境（装 skill、斜杠命令、GitHub 连接器）与其官方能力一致 | https://www.workbuddy.cn/docs/ （任务栏/项目文档） |
| F-039 | **单源注记**：humanlayer/skills 仓库内 show-me 的 SKILL.md 具体路径本次未直接取得（github.com 页面 WebFetch 失败；jsdelivr 对 `show-me/SKILL.md@main` 返回 404，实际目录结构未确认）。安装命令、调用方式、技能内容以 F-031~F-036 官方博客为权威；"就几行规则"为作者阅读后的主观描述（F-010），标注为博文单源 | 抓取记录 2026-09-16 |

## J. 勘误四张清单过筛记录

| 清单 | 结果 |
|------|------|
| ① 日期/版本表 | ✅ 博文无版本号/GA 日期声明；发布日期 F-003 为页面元数据单源；官方发布日 2026-08-12（F-031）与博文 2026-09-06 相隔 25 天，时序合理 |
| ② 成效数字溯源表 | ✅ 全文无提效倍数/工时节省/成本下降等成效数字（纯体验文，无营销数据） |
| ③ 口径对照表 | ✅ 数字仅"20 分钟口播/3 条短视频/9 分 12 秒/剪掉 5 分多钟/60 秒成片"，均为作者假设场景的叙述性数字，非市场规模口径，无需外部核验 |
| ④ 引文逐字核对表 | ⚠️→✅ F-012 对官方吐槽的转述与官方原文语义一致（非逐字引语、博文未加引号，处理正确）；F-022 Grill Me 未加归属但易被误读，已由 F-037 补充防误读；F-026 安装命令逐字核对完全一致 |

**核验总计**：7 项 P0（发布主体与日期/安装命令/两种调用/HTML 调用/官方问题口径/可视化形态/WorkBuddy 环境）全部 ✅；0 ❌ 硬错误；1 项口径精度补充（F-037）；1 项路径单源注记（F-039）。
