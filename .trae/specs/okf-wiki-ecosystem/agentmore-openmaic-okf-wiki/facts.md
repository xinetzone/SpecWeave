---
okf_version: "0.2"
type: facts
title: "智谱清言 AgentMore × 清华 OpenMAIC 公告事实采集清单"
source: "https://agentmore.chatglm.cn/shareFile/m/6ad704d27f8c85cf468aac82"
blog: { channel: "智谱清言 AgentMore 官方分享页", author: "智谱清言（AgentMore）官方", published: "2026-10（采集时点 2026-10-28，分享页未显示具体日期）", words: "约 700（正文实测，含标题与分节小标题）" }
verify: { repo: "https://github.com/THU-MAIC/OpenMAIC", demo: "https://open.maic.chat", readme: "README.md（含 OpenClaw/Quick Start/News）", license: "LICENSE 原文", skills_openmaic: "skills/openmaic/SKILL.md", skills_runtime: "skills/agent-runtime/（24 目录）", third_party: "36氪 AI 测评 / App Store", at: "2026-10-28" }
generated: { by: "seven-concepts-cmd+blog-article-to-okf-wiki:R", at: "2026-10-28T14:00:00+08:00" }
---

# 事实采集清单（F 编号）

> R 阶段唯一合法事实集。类型：`O`=客观事实，`V`=作者观点/体验，`S`=厂商自述（公告转述）。
> 信源距离：公告一手（厂商自述）/ 第三方综述 / 官方核验 / 官方仓库一手。
> 核验结论：✅ 与官方一致 ｜ ⚠️ 口径/时效/单源差异（见 verification.md 勘误）｜ ➖ 无需外部核验。
> F-001~F-024 来自公告；F-025+ 为 2026-10-28 官方仓库（README/API/目录树/LICENSE）+ Live Demo + 第三方核验补充事实。
> 本文为**厂商产品能力上新公告**，厂商自述（S）/ 作者观点（V）与可核验事实（O）分层登记；被点名项目 OpenMAIC 的事实以官方仓库为准。

## A. 公告元信息

| F编号 | 类型 | 声明 | 信源距离 | 核验级 | 结论 |
|-------|------|------|---------|--------|------|
| F-001 | O | 公告标题《清言 × 清华 OpenMAIC，打造你的专属AI老师》，副标题「你的学习搭子，又升级了！」，发布页位于 `agentmore.chatglm.cn`（智谱清言 AgentMore 域） | 公告一手 | P2 | ➖ |
| F-002 | S | 公告称：智谱清言携手清华「Github万星项目」OpenMAIC，为 **AgentMore 学习搭子**带来两项新技能——**费曼学习、习题带练** | 厂商自述 | P0 | ⚠️ 公告单源（见 F-044） |
| F-003 | O | 公告未给出 OpenMAIC 的具体 Star 数，"Github万星项目"为模糊表述 | 公告一手 | P1 | ⚠️ 见 F-030 |

## B. 费曼学习（技能一）

| F编号 | 类型 | 声明 | 信源距离 | 核验级 | 结论 |
|-------|------|------|---------|--------|------|
| F-004 | O | 公告称费曼学习通过**主动讲解、反馈修正、换情境检验**，帮用户发现"以为懂了"的地方；面向学生复习与职场人自学 | 厂商自述 | P2 | ➖ |
| F-005 | O | 第一轮「先讲理解」示例 prompt：「用费曼学习法检查我对机会成本的理解，我先讲一遍。每次只帮我找一个理解缺口。」 | 公告一手 | P2 | ➖ |
| F-006 | O | 第二轮「再讲一遍」：根据搭子的追问，用自己的话修正解释，让它检查误区是否消除 | 公告一手 | P2 | ➖ |
| F-007 | O | 第三轮「换情境检验」示例：「换个新情境，先别给答案，让我自己判断机会成本。」 | 公告一手 | P2 | ➖ |

## C. 习题带练（技能二）

| F编号 | 类型 | 声明 | 信源距离 | 核验级 | 结论 |
|-------|------|------|---------|--------|------|
| F-008 | O | 公告称习题带练通过**逐步提示、自主推理、总结方法**，帮用户彻底搞定一类题；面向备考人群 | 厂商自述 | P2 | ➖ |
| F-009 | O | 第一轮「找到卡点」示例 prompt：「这道题我选 B，但其实是蒙的。先别公布答案，先问我为什么排除一个选项。」 | 公告一手 | P2 | ➖ |
| F-010 | O | 第二轮「说出依据」：解释自己的排除理由，让搭子检查逻辑，再引导比较其他选项 | 公告一手 | P2 | ➖ |
| F-011 | O | 第三轮「总结方法」：说出最终答案与理由，请搭子核对，并一起总结同类题的判断步骤 | 公告一手 | P2 | ➖ |

## D. 八个 OpenMAIC Skill（上新清单）

| F编号 | 类型 | 声明 | 信源距离 | 核验级 | 结论 |
|-------|------|------|---------|--------|------|
| F-012 | S | 公告称教师、培训者也能用 Skill 辅助备课、设计课程；**8 个 OpenMAIC Skill 已同步上新**，前往「Skill 广场」搜索名称即可安装 | 厂商自述 | P0 | ⚠️ 公告单源（见 F-045） |
| F-013 | O | Skill「费曼学习」：概念自查或知识理解 | 厂商自述 | P1 | ✅ F-034（`feynman-learning`） |
| F-014 | O | Skill「习题带练」：题型练习或解题思路梳理 | 厂商自述 | P1 | ⚠️ F-036（仓库未见逐字同义目录名） |
| F-015 | O | Skill「学会学习」：调整学习方法或优化复习策略 | 厂商自述 | P1 | ✅ F-034（`learning-to-learn`） |
| F-016 | O | Skill「互动工作坊」：互动教学培训或实践活动设计 | 厂商自述 | P1 | ✅ F-034（`workshop-style`） |
| F-017 | O | Skill「系列课规划」：系列课程规划或多课时教学安排 | 厂商自述 | P1 | ✅ F-034（`curriculum-planner`） |
| F-018 | O | Skill「逆向教学设计」：围绕学习目标设计评价与教学活动 | 厂商自述 | P1 | ⚠️ F-035（疑对应 `understanding-by-design`，未逐字确认） |
| F-019 | O | Skill「核心素养备课」：将素养目标转化为具体教学任务 | 厂商自述 | P1 | ✅ F-034（`k12-core-literacy-planning`） |
| F-020 | O | Skill「螺旋式课程设计」：同一概念的多轮学习与逐步深化 | 厂商自述 | P1 | ✅ F-034（`spiral-curriculum`） |
| F-021 | O | 公告称 Skill 面向教师/培训者，用于辅助备课与设计课程，让"学习者主动思考、教学者因材施教" | 厂商自述 | P2 | ➖ |

## E. 结语与边界

| F编号 | 类型 | 声明 | 信源距离 | 核验级 | 结论 |
|-------|------|------|---------|--------|------|
| F-022 | V | 公告结语：让学习者主动思考，让教学者因材施教，一起探索 AI 时代教育的新可能 | 作者观点（厂商宣传语） | P2 | ➖ |
| F-023 | S | 公告称后续学习搭子还将持续升级**课程生成与修改能力** | 厂商自述 | P1 | ✅ F-043（官方 two-stage 生成能力一致，规划中能力未核） |
| F-024 | O | 公告为产品能力上新说明，给出对话示例 prompt 与 Skill 名称清单，但**无可复现的安装/配置/代码/调用流程** | 公告一手 | P2 | ➖ |

## F. 官方核验补充事实（2026-10-28：GitHub 仓库 + Live Demo + 第三方）

| F编号 | 类型 | 声明 | 信源距离 | 核验级 | 结论 |
|-------|------|------|---------|--------|------|
| F-025 | O | OpenMAIC 官方仓库真实存在：`https://github.com/THU-MAIC/OpenMAIC`（2026-10-28 抓取可访问） | 官方核验 | P0 | ✅ |
| F-026 | O | OpenMAIC 全称 **Open Multi-Agent Interactive Classroom**，清华大学 **THU-MAIC** 团队开源的多智能体互动课堂平台 | 官方核验 | P0 | ✅ |
| F-027 | O | 官方 Live Demo `https://open.maic.chat` 可访问；README 确认可在该站获取访问码（access code）以使用托管模式 | 官方核验 | P0 | ✅ |
| F-028 | O | README News 显示最新版本 **v0.2.1（2026-04-26）**；更早 v0.2.0（2026-04-20）、v0.1.1（2026-04-14）、**v0.1.0（2026-03-26）**——与"2026-03 开源"口径一致 | 官方核验 | P0 | ✅ |
| F-029 | O | 技术栈（README 徽章）：Next.js 16 / React 19 / TypeScript 5 / LangGraph 1.1 / Tailwind CSS 4 | 官方核验 | P1 | ✅ |
| F-030 | O | Star 数**多口径互斥**：GitHub API 抓取 **18,538**（2026-10-28）；GitHubDaily 报道 **33,000+**（2026-08-28）；某第三方站点自宣 **41.5k**；过期 HTML 缓存 **16.3k**——本束按"带时点观测"分层登记，不单一断言 | 官方核验 | P0 | ⚠️ 多口径 |
| F-031 | O | License **三源互斥**：`LICENSE` 文件正文为 **MIT License**（Copyright (c) 2026 THU-MAIC）；README 徽章与 GitHub API license 字段均为 **AGPL-3.0**——本束并列登记，不采信单一结论 | 官方核验 | P0 | ⚠️ 三源互斥 |
| F-032 | O | 官方 `skills/` 下有两个目录：`openmaic`（引导式 SOP Skill）与 `agent-runtime`（教学类 Skill 集） | 官方核验 | P0 | ✅ |
| F-033 | O | `skills/agent-runtime/` 共 **24 个** Skill 子目录（目录树 `truncated: false`，清单见 verification.md） | 官方核验 | P0 | ✅ |
| F-034 | O | 8 个上新 Skill 中 **6 个**可与官方目录名一一对应：费曼学习→`feynman-learning`、学会学习→`learning-to-learn`、互动工作坊→`workshop-style`、系列课规划→`curriculum-planner`、核心素养备课→`k12-core-literacy-planning`、螺旋式课程设计→`spiral-curriculum` | 官方核验 | P0 | ✅ |
| F-035 | O | 「逆向教学设计」高度疑似对应官方 `understanding-by-design`（UbD 理解本位/逆向设计），但公告与仓库均未逐字绑定，不推断为定论 | 官方核验 | P1 | ⚠️ 未逐字确认 |
| F-036 | O | 「习题带练」在官方 `skills/agent-runtime/` 24 个目录名中**未见逐字同义项**（候选 `zone-of-proximal-development` 最近发展区，未确认） | 官方核验 | P1 | ⚠️ 未命中 |
| F-037 | O | `skills/openmaic/SKILL.md` 为引导式 SOP：0 选择模式（Live Demo / 本地运行 / 二次开发）→ 克隆或复用 → 选择启动方式 → 配置 Provider Key（可选 web search/image/video/TTS）→ 启劢校验（`GET {url}/api/health`）→ 生成课堂（请求字段 `requirement`、`materialIds`） | 官方核验 | P0 | ✅ |
| F-038 | O | 官方支持 `ACCESS_CODE` 站点级访问口令（v0.1.1 起），设置后访客需先输入口令，API 路由同样受保护 | 官方核验 | P1 | ✅ |
| F-039 | O | 官方支持多 Provider：OpenAI / Anthropic / Google Gemini / DeepSeek / Qwen / Kimi / MiniMax / Grok(xAI) / OpenRouter / Doubao / 腾讯混元·TokenHub / Xiaomi MiMo / GLM(智谱) / Ollama / Lemonade 及任意 OpenAI 兼容 API | 官方核验 | P1 | ✅ |
| F-040 | O | 官方 README 确认 **OpenClaw 集成**：可从飞书/Slack/Telegram 等 20+ 消息应用直接生成课堂（`clawhub install openmaic`） | 官方核验 | P1 | ✅ |
| F-041 | O | 第三方测评（36氪）证实智谱清言存在「学习搭子」功能与「Agentmore 模式」（多 AI 智能体群组协作），作为公告可采信的旁证 | 第三方综述 | P1 | ✅ |
| F-042 | O | 智谱清言由智谱（Beijing Knowledge Atlas Technology）开发（App Store 开发者信息） | 第三方综述 | P2 | ✅ |
| F-043 | O | 官方 README 确认课程生成能力：two-stage pipeline（Outline 大纲 → Scenes 场景，含 slides/quizzes/交互模块/PBL） | 官方核验 | P0 | ✅ |
| F-044 | O | 本次"费曼学习/习题带练作为 AgentMore 学习搭子技能"的官方侧具体实现与命名，未在 OpenMAIC 仓库或智谱公开文档中逐字找到 | 官方核验 | P1 | ⚠️ 公告单源 |
| F-045 | O | AgentMore「Skill 广场」的安装机制在公开资料中未见官方文档说明 | 官方核验 | P1 | ⚠️ 公告单源 |
| F-046 | O | 本次核对未发现公告存在硬性事实错误；争议集中于 Star 数、License 口径与厂商自述的 Skill 上新范围 | 官方核验 | P1 | ✅ |

## G1 自检

- 事实总数：46（公告 24 + 核验补充 22），编号 F-001~F-046 连续无跳号
- 因果/判断词：事实栏纯客观陈述；评价与宣传语（F-022）标 V、厂商自述标 S
- 数字/术语：8 个 Skill、24 个 agent-runtime 目录、v0.2.1、Star 18,538、License 三源等均带 F 出处与时点
- 核验记录：✅ 行级 14、⚠️ 6 个 F 编号（F-002/F-014/F-018/F-030/F-031/F-035/F-036/F-044/F-045 中行级 ⚠️ 计 6——以 verification.md 核验总览为准）、➖ 其余、❌ 0
