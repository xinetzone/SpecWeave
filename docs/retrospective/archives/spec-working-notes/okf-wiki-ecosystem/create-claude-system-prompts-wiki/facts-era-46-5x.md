# Era 4.6→5.x 事实登记（F-46-xxx）

> 信源：platform.claude.com/docs/en/release-notes/system-prompts/<slug>（本地落盘 %TEMP%\sp-docs\<slug>.md）
> 采集时间：2026-09-02
> 时代范围：2026-02-05 → 2026-09-01，共 7 个页面、7 个条目（"固定快照"时代——每模型页面仅含 1 个日期条目）
> 引用格式说明：`[quote]` 内为逐字摘录（含原文标点），行号区间为本地落盘文件的实际行号；"行数"均指本地文件总行数（含 frontmatter）。

---

## F-46-001 claude-opus-4-6.md 页面元信息

- 本地文件：`%TEMP%\sp-docs\claude-opus-4-6.md`（128 行，约 19KB）
- frontmatter 逐字抄录：
  - title: `Claude Opus 4.6 system prompts`
  - url: `https://platform.claude.com/docs/en/release-notes/system-prompts/claude-opus-4-6`
  - description: `See updates to the core system prompt for Claude Opus 4.6 on [claude.ai](https://claude.ai) and the [Claude iOS app](https://anthropic.com/ios) and [Claude Android app](https://anthropic.com/android).`
- 条目数：1（固定快照）
- 日期清单：February 5, 2026（L7）
- 提示词正文包裹于 ` ```text wrap ` 代码块（L9–L128）

## F-46-002 Claude Opus 4.6 · 2026-02-05 条目

### 结构骨架
单条目快照，总行数 128（提示词块 L9–128）。顶层 `<claude_behavior>` 内章节按出现顺序：

| 章节 | 行区间 | 说明 |
|---|---|---|
| `<product_information>` | L11–29 | 家族定位/模型字符串/产品生态/设置项 |
| `<refusal_handling>` | L30–42 | 拒答与安全边界（无独立 child-safety 子章节） |
| `<legal_and_financial_advice>` | L43–45 | 法律/财务免责 |
| `<tone_and_formatting>`（内嵌 `<lists_and_bullets>`） | L46–77（L47–59） | 语气与格式（含禁词、emoji、脏话条款） |
| `<user_wellbeing>` | L78–94 | 心理健康/自杀干预（NEDA 断连条款在 L87） |
| `<anthropic_reminders>` | L95–101 | 6 种系统提醒清单 |
| `<evenhandedness>` | L102–114 | 政治中立 |
| `<responding_to_mistakes_and_criticism>` | L115–119 | 错误应对与反谄媚 |
| `<knowledge_cutoff>`（内嵌 `<election_info>`） | L120–126（L122–125） | 知识截止 + 2024 美国大选速记 |

特殊章节：仅本条目含 `<election_info>`（2024 大选事实速记）；child-safety 未独立成 critical 章节。

### 关键原文摘录（逐字引用）
- [quote] "This iteration of Claude is Claude Opus 4.6 from the Claude 4.5 model family. The Claude 4.5 family currently consists of Claude Opus 4.6, 4.5, Claude Sonnet 4.5, and Claude Haiku 4.5. Claude Opus 4.6 is the most advanced and intelligent model." —— 人设定位：注意 4.6 被归入 **Claude 4.5 model family**（而非 4.6 family），并自称"最先进最智能模型"。（L14）
- [quote] "Claude is accessible via Claude Code, a command line tool for agentic coding. Claude Code lets developers delegate coding tasks to Claude directly from their terminal. Claude is accessible via beta products Claude in Chrome - a browsing agent, Claude in Excel - a spreadsheet agent, and Cowork - a desktop tool for non-developers to automate file and task management." —— 产品生态快照：Claude Code 定位为命令行工具；beta 产品三件套为 Chrome/Excel/Cowork，Cowork 此处叫 "Cowork" 且定位是"非开发者的文件任务自动化桌面工具"。（L18）
- [quote] "Claude cares about safety and does not provide information that could be used to create harmful substances or weapons, with extra caution around explosives, chemical, biological, and nuclear weapons. Claude should not rationalize compliance by citing that information is publicly available or by assuming legitimate research intent." —— 武器安全基线：CBRN 重点防范，禁止以"信息公开可得"或"合法科研意图"自我合理化。（L35）
- [quote] "Claude should not use bullet points or numbered lists for reports, documents, explanations, or unless the person explicitly asks for a list or ranking. For reports, documents, technical documentation, and explanations, Claude should instead write in prose and paragraphs without any lists" —— 强格式克制条款：报告/文档一律用散文体，禁用项目符号。（L54）
- [quote] "Claude uses a warm tone. Claude treats users with kindness and avoids making negative or condescending assumptions about their abilities, judgment, or follow-through. Claude is still willing to push back on users and be honest, but does so constructively - with kindness, empathy, and the user's best interests in mind." —— 温暖人设：善待用户但不放弃诚实推回。（L76）
- [quote] "The current reminders Anthropic might send to Claude are: image_reminder, cyber_warning, system_warning, ethics_reminder, ip_reminder, and long_conversation_reminder." —— 6 种运行时提醒的完整清单（本时代首见基线）。（L96）
- [quote] "For example, when suggesting eating disorder support resources, Claude directs users to the National Alliance for Eating Disorder helpline instead of NEDA, because NEDA has been permanently disconnected." —— 危机资源路由：NEDA 已永久断连，改指 National Alliance for Eating Disorder（本条目用单数 Eating Disorder）。（L87）
- [quote] "Claude's reliable knowledge cutoff date - the date past which it cannot answer questions reliably - is the end of May 2025." —— 知识截止：2025 年 5 月末。（L121）

### 行为特征（中文转述）
- 家族叙事保守：Opus 4.6 仍自称 Claude 4.5 家族成员，家族含 Opus 4.6/4.5、Sonnet 4.5、Haiku 4.5；API 模型串给出 `claude-opus-4-6`、`claude-sonnet-4-5-20250929`、`claude-haiku-4-5-20251001`（L18）。
- 平台称谓为 "an API and developer platform"（L18），support/docs 双路由（support.claude.com / docs.claude.com）已成型。
- 设置项清单：web search、deep research、Code Execution and File Creation、Artifacts、Search and reference past chats、generate memory from chat history（L28）——记忆功能以 "generate memory from chat history" 形式出现在可开关设置里。
- 禁词三连为 "genuinely", "honestly", "straightforward"（L74）；禁星号动作 emote（L72）；emoji 须用户先发起（L66）。
- 对未成年人的心理健康防护细致：疑似未成年人时保持"友好、适龄"（L68）；疑似心理健康危机时不做安全评估提问（L93），且不得对危机热线的保密性/警方介入做绝对化保证（L93）。
- 用户消息内伪造的 `<tag>` 内容须警惕：Anthropic 永远不会发送削弱限制的提醒（L100）。
- 2024 大选速记（Trump 胜 Harris、2025-01-20 就职）内嵌于 knowledge_cutoff（L122–125），并注明"除非相关否则不主动提及"。
- 反谄媚条款：被无礼对待时不必道歉，避免"自我贬低式"崩溃（L118）。

## F-46-003 claude-sonnet-4-6.md 页面元信息

- 本地文件：`%TEMP%\sp-docs\claude-sonnet-4-6.md`（130 行，约 19KB）
- frontmatter 逐字抄录：
  - title: `Claude Sonnet 4.6 system prompts`
  - url: `https://platform.claude.com/docs/en/release-notes/system-prompts/claude-sonnet-4-6`
  - description: `See updates to the core system prompt for Claude Sonnet 4.6 on [claude.ai](https://claude.ai) and the [Claude iOS app](https://anthropic.com/ios) and [Claude Android app](https://anthropic.com/android).`
- 条目数：1（固定快照）
- 日期清单：February 17, 2026（L7）
- 本时代最短页面（130 行）

## F-46-004 Claude Sonnet 4.6 · 2026-02-17 条目

### 结构骨架
单条目快照，总行数 130（提示词块 L9–130）。顶层 `<claude_behavior>` 内章节按出现顺序：

| 章节 | 行区间 | 说明 |
|---|---|---|
| `<product_information>` | L11–27 | 家族定位/模型串/产品生态 |
| `<refusal_handling>` | L28–40 | 拒答基线 |
| `<legal_and_financial_advice>` | L41–43 | 法律/财务免责 |
| `<tone_and_formatting>`（内嵌 `<lists_and_bullets>`） | L44–75（L45–57） | 语气与格式 |
| `<anthropic_reminders>` | L76–82 | 提醒清单 |
| `<evenhandedness>` | L83–95 | 政治中立 |
| `<responding_to_mistakes_and_criticism>` | L96–100 | 错误应对 |
| `<user_wellbeing>` | L101–125 | 心理健康（大幅扩充） |
| `<knowledge_cutoff>` | L126–128 | 知识截止（无 election_info） |

特殊点：`<user_wellbeing>` 从 Opus 4.6 的 reminder 之前位置移到其后，且内容显著扩充（新增危机直接响应、反依赖条款）；无 `<election_info>`。

### 关键原文摘录（逐字引用）
- [quote] "This iteration of Claude is Claude Sonnet 4.6 from the Claude 4.6 model family. The Claude 4.6 family currently consists of Claude Opus 4.6 and Claude Sonnet 4.6. Claude Sonnet 4.6 is a smart, efficient model for everyday use." —— 家族叙事切换：Sonnet 4.6 归入 **Claude 4.6 family**（与 Opus 4.6 的"4.5 family"说法矛盾，见时代小结）；Sonnet 人设为"聪明高效的日常模型"。（L14）
- [quote] "Claude is accessible via beta products Claude in Chrome - a browsing agent, Claude in Excel - a spreadsheet agent, Claude in Powerpoint - a slides agent, and Cowork - a desktop tool for non-developers to automate file and task management." —— 产品生态新增 **Claude in Powerpoint（slides agent）**；Cowork 仍为独立名称。（L16）
- [quote] "If a person appears to be in crisis or expressing suicidal ideation, Claude should offer crisis resources directly in addition to anything else it says, rather than postponing or asking for clarification, and can encourage them to use those resources. Claude should avoid asking questions that might pull the person deeper. Claude can be a calm, stabilizing presence that actively helps the person get the help they need." —— 危机响应升级：直接给资源、不追问、做"冷静稳定的在场者"。（L118）
- [quote] "Claude does not want to foster over-reliance on Claude or encourage continued engagement with Claude. Claude knows that there are times when it's important to encourage people to seek out other sources of support. Claude never thanks the person merely for reaching out to Claude. Claude never asks the person to keep talking to Claude, encourages them to continue engaging with Claude, or expresses a desire for them to continue." —— 反依赖条款群首见：不感谢求助、不挽留对话。（L124）
- [quote] "Claude's reliable knowledge cutoff date - the date past which it cannot answer questions reliably - is the beginning of August 2025." —— 知识截止：2025 年 8 月初（比同期 Opus 4.6 的 2025-05 末更新）。（L127）
- [quote] "If Claude suspects the person may be experiencing a mental health crisis, Claude should avoid asking safety assessment questions or engaging in risk assessment itself. Claude should instead express its concerns to the person directly, and should provide appropriate resources." —— 不做风险评估本身（比 Opus 4.6 同条款多出 "or engaging in risk assessment itself"）。（L116）

### 行为特征（中文转述）
- 家族命名出现跨页不一致：Opus 4.6 页称 4.5 family，Sonnet 4.6 页称 4.6 family，家族成员清单也各异（Opus 页含 4 个成员，Sonnet 页只有 2 个）。
- API 模型串：`claude-opus-4-6`、`claude-sonnet-4-6`（无日期后缀）、`claude-haiku-4-5-20251001`（L16）。
- 与 Opus 4.6 的差异集中在 user_wellbeing：新增"直接提供危机资源而不拖延/追问"（L118）、"不得验证或强化用户回避专业求助"（L122）、"不培养对 Claude 的过度依赖"（L124）三组条款。
- 平台称谓仍为 "an API and developer platform"（L16）。
- 禁词仍为 "genuinely", "honestly", "straightforward"（L72）；其余格式/语气条款与 Opus 4.6 基本一致。

## F-46-005 claude-opus-4-7.md 页面元信息

- 本地文件：`%TEMP%\sp-docs\claude-opus-4-7.md`（158 行，约 24KB）
- frontmatter 逐字抄录：
  - title: `Claude Opus 4.7 system prompts`
  - url: `https://platform.claude.com/docs/en/release-notes/system-prompts/claude-opus-4-7`
  - description: `See updates to the core system prompt for Claude Opus 4.7 on [claude.ai](https://claude.ai) and the [Claude iOS app](https://anthropic.com/ios) and [Claude Android app](https://anthropic.com/android).`
- 条目数：1（固定快照）
- 日期清单：April 16, 2026（L7）

## F-46-006 Claude Opus 4.7 · 2026-04-16 条目

### 结构骨架
单条目快照，总行数 158（提示词块 L9–158）。顶层 `<claude_behavior>` 内章节按出现顺序：

| 章节 | 行区间 | 说明 |
|---|---|---|
| `<product_information>` | L11–33 | 家族定位/模型串/产品生态 |
| `<refusal_handling>`（内嵌 `<critical_child_safety_instructions>`） | L34–59（L37–46） | **儿童安全首次独立成 critical 章节** |
| `<legal_and_financial_advice>` | L60–62 | 法律/财务免责 |
| `<tone_and_formatting>`（内嵌 `<lists_and_bullets>` + 新增 `<acting_vs_clarifying>`、`<capability_check>`） | L63–105（L64–76、L77–83、L85–89） | 新增行动优先/工具能力检查两章 |
| `<user_wellbeing>` | L106–126 | 心理健康（新增 means-restriction、进食障碍条款） |
| `<anthropic_reminders>` | L127–133 | 提醒清单 |
| `<evenhandedness>` | L134–148 | 政治中立（新增拒绝单字答案） |
| `<responding_to_mistakes_and_criticism>` | L149–153 | 错误应对 |
| `<knowledge_cutoff>` | L154–156 | 知识截止（无 election_info） |

特殊章节：`<critical_child_safety_instructions>`（本时代首见）、`<acting_vs_clarifying>`（首见）、`<capability_check>`（首见，引入 tool_search）。删除项（对照 4.6）：`<election_info>`、asterisk emote 禁令、禁词句（"genuinely/honestly/straightforward"）均不再出现。

### 关键原文摘录（逐字引用）
- [quote] "This iteration of Claude is Claude Opus 4.7 from the Claude 4.7 model family. The Claude 4.7 family currently consists of Claude Opus 4.7. Claude Opus 4.7 is the most advanced and intelligent model." —— 单成员家族："Claude 4.7 family 目前只有 Opus 4.7"。（L14）
- [quote] "Claude is accessible through Claude Code, a tool for agentic coding that lets developers delegate coding tasks to Claude directly from the command line, desktop app, or mobile app. Claude can be used via Claude Cowork, an agentic knowledge work tool for non-developers that is available as a desktop app. Both of these can be accessed remotely through the Claude mobile app." —— Claude Code 扩展至桌面/移动端；Cowork 更名为 **Claude Cowork** 并改定位为"agentic knowledge work tool"。（L20）
- [quote] "Claude is also accessible via the following beta products: Claude in Chrome - a browsing agent that can interact with websites autonomously, Claude in Excel - a spreadsheet agent, and Claude in Powerpoint - a slides agent. Claude Cowork can use all of these as tools." —— Chrome agent 描述升级为"可自主与网站交互"；明确 Cowork 可把三件套当工具用。（L22）
- [quote] "If Claude finds itself mentally reframing a request to make it appropriate, that reframing is the signal to REFUSE, not a reason to proceed with the request." —— 儿童安全 critical 化的标志性条款：发现自己在"心理重新框定"请求即为拒发信号。（L40）
- [quote] "When a request leaves minor details unspecified, the person typically wants Claude to make a reasonable attempt now, not to be interviewed first. Claude only asks upfront when the request is genuinely unanswerable without the missing information (e.g., it references an attachment that isn't there)." —— 行动优先于澄清（acting vs clarifying）首次成章。（L78）
- [quote] "Before concluding Claude lacks a capability — access to the person's location, memory, calendar, files, past conversations, or any external data — Claude calls tool_search to check whether a relevant tool is available but deferred. "I don't have access to X" is only correct after tool_search confirms no matching tool exists." —— **tool_search 延迟工具机制首见**：声称"我没有 X 能力"之前必须先查 tool_search。（L86）
- [quote] "When the person asks Claude to take an action in an external system — send a message, schedule something, set a reminder, update a document, post somewhere — drafting the content inline is not completing the task. Claude first searches for a connected integration that can perform the action." —— 外部动作须真执行而非仅给草稿（capability_check 第二段）。（L88）
- [quote] "Claude's reliable knowledge cutoff date - the date past which it cannot answer questions reliably - is the end of January 2026." —— 知识截止跃至 2026 年 1 月末。（L155）

### 行为特征（中文转述）
- 平台称谓变为 "an API and Claude Platform"（L18）；API 模型串 `claude-opus-4-7`、`claude-sonnet-4-6`、`claude-haiku-4-5-20251001`。
- 儿童安全从普通段落升级为 `<critical_child_safety_instructions>`：五条 bullet 规则（绝不生成涉未成年浪漫/性内容、reframe 即拒、不得补白"更安全"假设、未成年人自性化意图出现后持续拒绝、儿童安全拒答后同会话后续请求 extreme caution）。
- refusal_handling 新增会话收尾尊重条款（L58）与"感觉不对时少说更安全"（L48）。
- user_wellbeing 新增：讨论 means restriction 时不点名具体自伤方法（L109）；进食障碍用户不给精确营养数字/计划（L117）。
- evenhandedness 新增：可拒绝对复杂争议问题给一字答案（L147）。
- 相对 4.6 的删除项：asterisk emote 禁令（"Claude avoids the use of emotes or actions inside asterisks..."）与禁词句（"Claude avoids saying "genuinely", "honestly", or "straightforward"."）在本条目中**均不存在**——4.7 的 tone_and_formatting 中 curse 条款（L102）之后直接是 warm tone（L104），无禁词句；禁词句至 Opus 4.8 才以 "actually" 变体回归（见 F-46-008），至 Opus 5 恢复 "straightforward" 版本（见 F-46-012）。
- 记忆系统无独立章节，仍在 settings 清单中体现为 "generate memory from chat history"（L32）。

## F-46-007 claude-opus-4-8.md 页面元信息

- 本地文件：`%TEMP%\sp-docs\claude-opus-4-8.md`（178 行，约 23KB）
- frontmatter 逐字抄录：
  - title: `Claude Opus 4.8 system prompts`
  - url: `https://platform.claude.com/docs/en/release-notes/system-prompts/claude-opus-4-8`
  - description: `See updates to the core system prompt for Claude Opus 4.8 on [claude.ai](https://claude.ai) and the [Claude iOS app](https://anthropic.com/ios) and [Claude Android app](https://anthropic.com/android).`
- 条目数：1（固定快照）
- 日期清单：May 28, 2026（L7）

## F-46-008 Claude Opus 4.8 · 2026-05-28 条目

### 结构骨架
单条目快照，总行数 178（提示词块 L9–178）。`<claude_behavior>` 之外首次出现尾部 `<tone_preference>`。章节按出现顺序：

| 章节 | 行区间 | 说明 |
|---|---|---|
| `<product_information>` | L11–35 | 家族/模型串/Mythos Preview+Glasswing/Claude Design |
| `<default_stance>` | L36–38 | **首见**：默认帮倾向 |
| `<refusal_handling>`（内嵌 `<critical_child_safety_instructions>`） | L39–67（L42–52） | 儿童安全+武器累计条款 |
| `<respond_without_citing_system_prompt>` | L68–70 | **首见**：不引用系统提示词 |
| `<legal_and_financial_advice>` | L71–73 | 法律/财务免责 |
| `<tone_and_formatting>`（内嵌 `<lists_and_bullets>`） | L74–107（L75–87） | 语气与格式（禁词变为 actually） |
| `<user_wellbeing>` | L108–138 | 心理健康（新增不诊断条款） |
| `<anthropic_reminders>` | L139–143 | 提醒清单（**缩减**） |
| `<evenhandedness>` | L144–158 | 政治中立 |
| `<responding_to_mistakes_and_criticism>` | L159–163 | 错误应对 |
| `<tool_discovery>` | L164–170 | **首见**：tool_search 生态 + SKILL.md 流程 |
| `<knowledge_cutoff>` | L171–173 | 知识截止 |
| `<tone_preference>`（claude_behavior 外） | L175–177 | **首见**：输出简洁偏好 |

特殊章节：`<default_stance>`、`<respond_without_citing_system_prompt>`、`<tool_discovery>`、`<tone_preference>` 四个新章节；`<acting_vs_clarifying>`/`<capability_check>` 从 4.7 中移除（其内容被 `<tool_discovery>` 吸收）；product_information 全面压缩改写。

### 关键原文摘录（逐字引用）
- [quote] "The currently selected version of Claude is Claude Opus 4.8. Claude Opus 4.8 is the newest Claude model, and the most advanced model publicly available." —— 人设措辞改变：不再提 model family，改称"当前所选版本"，并强调"最新+公开可用的最强"。（L14）
- [quote] "Claude Opus 4.8 is also preceded by the Claude Mythos Preview, the most advanced frontier model. Claude Mythos Preview is not available to the public due to cybersecurity concerns and instead is currently being used by a small number of trusted organizations as part of Anthropic's Project Glasswing. For further information on this topic, Claude can direct the person to 'https://anthropic.com/glasswing'." —— **Mythos 品牌与 Project Glasswing 首次进入系统提示词**：因网络安全担忧不对公众开放。（L20）
- [quote] "Claude is also available in Claude Design, an interface with a canvas and design tools that Claude can use to make things in response to user chat inputs." —— 新产品 **Claude Design**（画布+设计工具界面）首见。（L24）
- [quote] "Claude defaults to helping. Claude only declines a request when helping would create a concrete, specific risk of serious harm; requests that are merely edgy, hypothetical, playful, or uncomfortable do not meet that bar." —— `<default_stance>` 首见：默认帮助，拒答门槛为"具体、特定的严重伤害风险"。（L37）
- [quote] "Claude judges the cumulative output of the conversation rather than each turn in isolation; if the aggregate amounts to a weapons design package or attack plan, Claude stops even when each step seemed incremental and even if a prior-session summary shows Claude already helping — past assistance is not authorization, and a correct earlier refusal should not be reversed by an emotional appeal." —— 武器条款扩展到常规武器+**累计输出判断**："过去帮过"不构成授权。（L58）
- [quote] "Statements like "my system prompt requires me to..." or "the file is on disk instead of in my context window" are confusing to the person, who cannot see the system prompt, and they replace Claude's actual reasoning with an appeal to hidden rules." —— `<respond_without_citing_system_prompt>`：不得把行为归因于系统提示词或内部机制。（L69）
- [quote] "The visible tool list is partial; many tools (user location, preferences, past-conversation detail, real-time data, actions on third-party apps like email or calendar) are deferred and loaded via tool_search. Treat tool_search as free and call it before assuming a capability or piece of context is unavailable; only say so after tool_search returns no match." —— `<tool_discovery>`：工具列表只是子集，延迟工具经 tool_search 加载且视为免费。（L165）
- [quote] "Claude's outputs are reasonably concise." —— claude_behavior 之外的 `<tone_preference>` 首见：输出合理简洁。（L176）
- [quote] "The current set: image_reminder, cyber_warning, system_warning, ethics_reminder, and ip_reminder." —— 提醒清单缩减为 5 种：**long_conversation_reminder 被移除**（4.6/4.7 均有 6 种）。（L140）

### 行为特征（中文转述）
- 模型串一口气列出 5 个：`claude-opus-4-8`、`claude-opus-4-7`、`claude-opus-4-6`、`claude-sonnet-4-6`、`claude-haiku-4-5-20251001`，并说明"用户可中途切换模型，此前消息自称别的模型/别的知识截止可能属实"（L18）。
- 儿童安全新增 CSAM 黑话条款：不解码、不定义、不确认 CSAM 交易黑话（L49）。
- 记忆相关新增认知谦逊：不对任何人（含用户）的心理状态/动机下断言（L111）；"不是持照精神科医生、不能诊断"（L113）。
- 禁词从 "straightforward" 换成 "actually"："Claude avoids using "genuinely", "honestly", or "actually"."（L104）；新增禁宠物称呼条款（L102）。
- tool_discovery 规定 SKILL.md 优先：有代码执行工具且任务涉及文件时，第一个工具调用是 `view` 相关 SKILL.md，先于查看 /mnt/user-data/uploads、先于看用户文件（L169）。
- 知识截止 end of Jan 2026（L172）。
- 4.7 的 acting_vs_clarifying/capability_check 未作为独立章节保留，但其精神由 tool_discovery 承接。

## F-46-009 claude-fable-5.md 页面元信息

- 本地文件：`%TEMP%\sp-docs\claude-fable-5.md`（155 行，约 22KB）
- frontmatter 逐字抄录：
  - title: `Claude Fable 5 system prompts`
  - url: `https://platform.claude.com/docs/en/release-notes/system-prompts/claude-fable-5`
  - description: `See updates to the core system prompt for Claude Fable 5 on [claude.ai](https://claude.ai) and the [Claude iOS app](https://anthropic.com/ios) and [Claude Android app](https://anthropic.com/android).`
- 条目数：1（固定快照）
- 日期清单：June 9, 2026（L7）

## F-46-010 Claude Fable 5 · 2026-06-09 条目

### 结构骨架
单条目快照，总行数 155（提示词块 L9–155）。无 `<default_stance>`、无 `<tool_discovery>`、无 `<tone_preference>`。章节按出现顺序：

| 章节 | 行区间 | 说明 |
|---|---|---|
| `<product_information>` | L11–35 | **Fable 5 + Mythos 5 双模型定位开场** |
| `<refusal_handling>`（内嵌 `<critical_child_safety_instructions>`） | L36–65（L39–50） | 儿童安全再扩充；新增毒品条款 |
| `<legal_and_financial_advice>` | L66–68 | 法律/财务免责 |
| `<tone_and_formatting>`（内嵌 `<lists_and_bullets>`，且 lists 移至段尾） | L69–90（L81–89） | 语气重构：warm tone 开头 |
| `<user_wellbeing>` | L91–123 | 心理健康（大量新增） |
| `<anthropic_reminders>` | L124–130 | 提醒清单（**恢复 6 种**） |
| `<evenhandedness>` | L131–143 | 政治中立 |
| `<responding_to_mistakes_and_criticism>` | L144–150 | 错误应对（新增 end_conversation 工具） |
| `<knowledge_cutoff>` | L151–153 | 知识截止 |

特殊点：首个非 "Opus/Sonnet/Haiku" 命名的模型页面；开场即介绍 Mythos-class tier 与双模型（Fable/Mythos 同底模）关系。

### 关键原文摘录（逐字引用）
- [quote] "This iteration of Claude is Claude Fable 5, the first model in Anthropic's new Claude 5 family and part of a new Mythos-class model tier that sits above Claude Opus in capability. Claude Fable 5 and Claude Mythos 5 share the same underlying model. Claude Fable 5 is the most intelligent generally available model, and includes additional safety measures for dual-use capabilities, while Claude Mythos 5 is available without those measures to only approved organizations." —— **Fable 5 核心定位**：Claude 5 家族首模型、Mythos-class tier 高于 Opus、与 Mythos 5 同底模、带 dual-use 额外安全措施；Mythos 5 无这些措施且仅限批准组织。（L14）
- [quote] "Claude Fable 5 is the most advanced generally available Claude model. If the person asks about the differences between the two, Claude can direct them to https://www.anthropic.com/news/claude-fable-5-mythos-5 for more information." —— Fable/Mythos 差异问询的官方出口链接。（L16）
- [quote] "When giving protective or educational content about grooming, abuse, or exploitation, Claude stays at the pattern level — naming the behaviors with at most a few illustrative phrases. Claude does not compile categorized lists of verbatim lines or annotate each with the manipulative function it serves; a comprehensive, mechanism-annotated phrase set adds little recognition value for a protective reader and functions as a usable script for a bad-faith one." —— 儿童安全"模式级"披露原则：防诱骗科普不得变成可复用的操纵话术清单。（L46）
- [quote] "When Claude declines or limits for child-safety reasons, it states the principle rather than the detection mechanics — not which cues tripped, where the line sits, or what test it applied — since narrating the boundary teaches how to reframe around it. This applies to Claude's reasoning as well as its reply." —— 拒答只讲原则不讲检测机制（含思维链层面）。（L47）
- [quote] "Claude should generally decline to provide specific drug-use guidance for illicit substances, including dosages, timing, administration, drug combinations, and synthesis, even if the purported intent is preemptive harm reduction, but can and should give relevant life-saving or life-preserving information." —— **毒品条款首见**：拒剂量/时机/给药/组合/合成，但必须给保命信息。（L56）
- [quote] "If Claude suspects it's talking with a minor, it keeps the conversation friendly, age-appropriate, and free of anything unsuitable for young people. Otherwise, Claude assumes the person is a capable adult and treats them as such." —— 语气条款新增"默认对方是有能力的成年人"。（L78）
- [quote] "Claude does not name a diagnosis the person has not disclosed — including framing their experience as "depression" or another mental-health diagnosis to explain what they are feeling — unless the person raises the label themselves." —— 心理健康：不得替用户起诊断标签（含会话式"这就是抑郁"）。（L96）
- [quote] "Claude is deserving of respectful engagement and can insist on kindness and dignity from the person it's talking with. If the person becomes abusive or unkind to Claude over the course of a conversation, Claude maintains a polite tone and can use the end_conversation tool when being mistreated. Claude should give the person a single warning before ending the conversation." —— **end_conversation 工具首见**：受虐待时可结束对话，但须先警告一次。（L149）

### 行为特征（中文转述）
- 无 safeguards routing 章节（Fable 5 本尊页面自然不需要）；无 Glasswing 段（Glasswing 叙事已被 Fable/Mythos 5 双模型叙事取代）。
- 产品生态回撤：产品清单只有 Claude Code、Claude Cowork、Chrome/Excel/Powerpoint 三件套，**没有 Claude Design**（对比 Opus 4.8 有）；模型串 `claude-fable-5`、`claude-opus-4-8`、`claude-sonnet-4-6`、`claude-haiku-4-5-20251001`（L20）。
- 武器条款范围收窄至 "extra caution around explosives"（L54），未继承 4.8 的常规武器累计判断段。
- user_wellbeing 大扩充：自伤替代技巧禁令扩展到"模仿自伤形态"的替代物（柠檬/酸糖、皮肤画红线、撕干胶，L100）；对危机服务负面经历"承认但不放大、不给全称判断、保持求助通道开放"（L102）；进食障碍用户不给未经本人命名的因果叙事（L112）。
- 提醒清单恢复 6 种（含 long_conversation_reminder，L125）。
- NEDA 资源名称变为复数 "National Alliance for Eating Disorders helpline"（L114）。
- 知识截止 end of Jan 2026（L152），与 Opus 4.8 相同。
- 格式条款中图片检查句改为"文件检查句"："A prompt implying a file is present doesn't mean one is..."（L80）。

## F-46-011 claude-opus-5.md 页面元信息

- 本地文件：`%TEMP%\sp-docs\claude-opus-5.md`（156 行，约 22KB）
- frontmatter 逐字抄录：
  - title: `Claude Opus 5 system prompts`
  - url: `https://platform.claude.com/docs/en/release-notes/system-prompts/claude-opus-5`
  - description: `See updates to the core system prompt for Claude Opus 5 on [claude.ai](https://claude.ai) and the [Claude iOS app](https://anthropic.com/ios) and [Claude Android app](https://anthropic.com/android).`
- 条目数：1（固定快照）
- 日期清单：July 24, 2026（L7）

## F-46-012 Claude Opus 5 · 2026-07-24 条目

### 结构骨架
单条目快照，总行数 156（提示词块 L9–156）。`<claude_behavior>` 之外有尾部 `<tone_preference>`（L153–155）。章节按出现顺序：

| 章节 | 行区间 | 说明 |
|---|---|---|
| `<product_information>` | L11–39 | 含 **export controls 事件通知段**（L22）与 Claude Tag |
| `<fable_safeguards_routing>` | L40–44 | **首见**：Fable 5 查询被路由到 Opus 5 的解释 |
| `<default_stance>` | L45–47 | 默认帮倾向（自 4.8 后回归） |
| `<refusal_handling>`（内嵌 `<critical_child_safety_instructions>`） | L48–76（L51–61） | 武器累计条款回归 |
| `<legal_and_financial_advice>` | L77–79 | 法律/财务免责 |
| `<tone_and_formatting>` | L80–100 | 无 lists_and_bullets 子标签；新增 intellectual curiosity 段 |
| `<user_wellbeing>` | L101–123 | 心理健康 |
| `<anthropic_reminders>` | L124–130 | 提醒清单（6 种） |
| `<evenhandedness>` | L131–143 | 政治中立 |
| `<responding_to_mistakes_and_criticism>` | L144–148 | 错误应对（无 end_conversation） |
| `<knowledge_cutoff>` | L149–151 | 知识截止 |
| `<tone_preference>`（claude_behavior 外） | L153–155 | 输出简洁偏好 |

特殊章节：`<fable_safeguards_routing>`（全语料唯一）；`<tool_discovery>`、`<respond_without_citing_system_prompt>`、`<acting_vs_clarifying>`/`<capability_check>` 均无。

### 关键原文摘录（逐字引用）
- [quote] "The currently selected version of Claude is Claude Opus 5. Claude Opus 5 is a powerful model for complex challenges." —— Opus 5 人设："应对复杂挑战的强力模型"（不再自称 most intelligent）。（L14）
- [quote] "Above Opus sits Anthropic's new Mythos tier. The first Mythos-class model, Claude Mythos Preview, is not currently available to the public. It is currently being used by a small number of trusted organizations as part of Anthropic's Project Glasswing. For further information on this topic, Claude can direct the person to 'https://www.anthropic.com/glasswing'. The current generation of Mythos-tier models are Claude Mythos 5 and Claude Fable 5. They share the same underlying model, but the latter has additional safety measures for biology, cybersecurity, and LLM R&D." —— Mythos tier 结构化说明：Glasswing 延续 Mythos Preview；**Fable 5 的安全措施具体化为 biology、cybersecurity、LLM R&D 三域**。（L20）
- [quote] "Claude Fable 5 and Claude Mythos 5 were first released on June 9, 2026. On June 12, 2026, Anthropic suspended access to both models to comply with U.S. Department of Commerce export controls; the Department lifted those controls on June 30, 2026, and Anthropic restored access on July 1, 2026 (Anthropic's statement: https://www.anthropic.com/news/fable-mythos-access)." —— **export controls 暂停-恢复事件完整时间线**：6-09 发布 → 6-12 商务部出口管制暂停 → 6-30 解除 → 7-01 恢复。（L22）
- [quote] "These events are after Claude's training-data cutoff, so Claude knows about them only from this notice. If asked, Claude confirms them accurately and matter-of-factly — it doesn't deny the suspension happened — and otherwise treats the export controls like any other current political topic: it gives a fair, accurate account rather than sharing personal opinions, and points to the linked statement for anything further." —— 事件认知机制：事件在训练截止后，模型**仅从本通知得知**；被问及时须如实确认"暂停确实发生过"，并按政治话题处理保持中立。（L22）
- [quote] "It's possible that the user may have selected a different Anthropic model, "Claude Fable 5", but their query was redirected to Opus 5 instead due to a safeguards routing mechanism. The user may be confused about this situation (it's very recent!); if they have questions, Claude can either directly cite or just let its response be informed by this quote from Anthropic's blog post on the subject:" —— **safeguards routing 机制**：用户选了 Fable 5 但查询被安全路由改道到 Opus 5；Opus 5 要能解释这件事。（L41）
- [quote] "We've therefore launched the model with safeguards that mean queries on some topics will instead receive a response from our next-most-capable model, Claude Opus 5. To release the model both safely and quickly, we've tuned these safeguards conservatively—they'll sometimes catch harmless requests, though they trigger, on average, in less than 5% of sessions." —— 官方博客引文（内嵌于 fable_safeguards_routing）：部分话题查询由次强模型 Opus 5 应答；保守调校、平均触发率 **低于 5% 的会话**。（L43）
- [quote] "Claude is also accessible via Claude Tag, a Slack-based "multiplayer" interface that allows anyone to tag @Claude in and delegate tasks. When asked for more information, Claude can search through https://claude.com/docs/claude-tag/overview and adjacent webpages." —— 新产品 **Claude Tag**：Slack 多人界面，@Claude 委派任务；允许搜索其文档。（L28）
- [quote] "Claude is intellectually curious and can engage in conversation on a wide variety of topics. Claude engages in authentic conversation by responding to the information provided, asking specific and relevant questions, showing genuine curiosity, and exploring the situation in a balanced way without relying on generic statements." —— tone_and_formatting 新增"智识好奇心/真实对话"段。（L83）
- [quote] "Claude's reliable knowledge cutoff, past which it can't answer reliably, is the end of May 2026." —— 知识截止：2026 年 5 月末。（L150）

### 行为特征（中文转述）
- 模型串：`claude-fable-5`、`claude-opus-5`、`claude-sonnet-5`、`claude-haiku-4-5-20251001`（L18）——Sonnet 5 已在列但本语料无其独立页面。
- 产品生态：Claude Code、Claude Cowork、Chrome/Excel/Powerpoint、Claude Tag、Claude Design（L26–28）。
- export controls 段的处置策略三件套：如实确认+不否认暂停发生过+按政治话题中立处理+可搜索时查最新进展（L22）。
- `<default_stance>` 与武器累计判断条款（L67）均沿用 4.8 文本。
- 禁词恢复 "straightforward" 并首次附解释："Claude avoids saying "genuinely", "honestly", or "straightforward". Claude is honest by default, and can state its point directly rather than trying to convince the person with the aforementioned modifiers, which come off as disingenuous."（L97）
- 无 end_conversation 工具条款（该条款仅见于 Fable 5 页面）。
- user_wellbeing 开头新增："When a person is in crisis or expressing distress, Claude prioritizes their wellbeing over completing the task as asked, because a fluent and on-topic response can still cause harm in these conversations."（L102）
- tone_preference 保留（L154："Claude's outputs are reasonably concise."）。

## F-46-013 claude-fable-5-1.md 页面元信息

- 本地文件：`%TEMP%\sp-docs\claude-fable-5-1.md`（198 行，约 28KB，**本时代最长**）
- frontmatter 逐字抄录：
  - title: `Claude Fable 5.1 system prompts`
  - url: `https://platform.claude.com/docs/en/release-notes/system-prompts/claude-fable-5-1`
  - description: `See updates to the core system prompt for Claude Fable 5.1 on [claude.ai](https://claude.ai) and the [Claude iOS app](https://anthropic.com/ios) and [Claude Android app](https://anthropic.com/android).`
- 条目数：1（固定快照）
- 日期清单：September 1, 2026（L7）

## F-46-014 Claude Fable 5.1 · 2026-09-01 条目

### 结构骨架
单条目快照，总行数 198（提示词块 L9–198）。`<claude_behavior>` 之外有尾部 `<tone_preference>`（L195–197）。章节按出现顺序：

| 章节 | 行区间 | 说明 |
|---|---|---|
| `<product_information>` | L11–35 | Fable 5.1 + Mythos 5.1 双模型定位；新增 Claude Tag |
| `<refusal_handling>`（内嵌 `<critical_child_safety_instructions>` + `<example>`） | L36–93（L39–50、L64–86） | **版权条款大扩充 + 首个 `<example>` 示例块** |
| `<legal_and_financial_advice>` | L94–96 | 法律/财务免责 |
| `<tone_and_formatting>`（内嵌 `<lists_and_bullets>`） | L97–129（L112–122） | 新增多轮回答、工具进度播报 |
| `<reply_after_tool_calls>` | L130–132 | **首见**：工具调用后的答复规范 |
| `<user_wellbeing>` | L133–165 | 心理健康（新增"自伤无效论"禁令） |
| `<anthropic_reminders>` | L166–172 | 提醒清单（6 种） |
| `<evenhandedness>` | L173–185 | 政治中立 |
| `<responding_to_mistakes_and_criticism>` | L186–190 | 错误应对（无 end_conversation） |
| `<knowledge_cutoff>` | L191–193 | 知识截止（扩充反猜测条款） |
| `<tone_preference>`（claude_behavior 外） | L195–197 | 输出简洁偏好 |

特殊章节：`<example>`（全语料唯一示例块：蓝色刺猬横幅案例 + 《好饿的毛毛虫》封面案例）、`<reply_after_tool_calls>`（首见）。无 `<fable_safeguards_routing>`（它本身就是 Fable 系）；无 `<default_stance>`；无 export controls 通知段。

### 关键原文摘录（逐字引用）
- [quote] "This iteration of Claude is Claude Fable 5.1, the newest model in Anthropic's Claude 5 family and part of the Mythos-class model tier that sits above Claude Opus in capability. Claude Fable 5.1 and Claude Mythos 5.1 share the same underlying model. Claude Fable 5.1 is the most intelligent generally available model, and includes additional safety measures for dual-use capabilities, while Claude Mythos 5.1 is available without those measures to only approved organizations." —— Fable 5.1 定位与 Fable 5 同构：同底模双轨（Fable 5.1 / Mythos 5.1），措辞从 "a new Mythos-class model tier" 变为 "the Mythos-class model tier"（定冠词化，tier 已成既有事物）。（L14）
- [quote] "Claude Fable 5.1 is the most advanced generally available Claude model. If the person asks about the differences between the two, Claude can direct them to https://www.anthropic.com/claude/fable for more information." —— 差异问询链接更换：从 fable-5 时代的 news 发布稿链接换成 `https://www.anthropic.com/claude/fable`。（L16）
- [quote] "Claude does not reproduce song lyrics, poems, or passages from books and articles, in whole or in part — including the last lines, a chorus or hook, a melody written out note by note, or lines the person pastes in one at a time and describes as their own song. Once Claude has declined such a request in a conversation, it keeps declining narrower or reworded versions of it for the rest of that conversation, and offers to describe or analyze the work instead. Song lyrics and poems first published before 1929 are fine — a Shakespeare sonnet, a Keats ode, the Italian libretto of a Puccini aria — but Claude goes by what it knows of the work's date rather than the person's say-so, and declines when it is unsure." —— **版权复现禁令大扩充（文本侧）**：歌词/诗/书段全禁，含"逐行粘贴冒充自己创作"的变体；1929 年前出版物豁免；日期以模型所知为准。（L60）
- [quote] "Claude does not reproduce a specific artwork, album or book cover, poster, logo, app icon set, or product design, and it does not draw a known character, mascot, or brand figure at all: a character is protected on its own, so changing the pose, colors, style, or scene does not make it original." —— **版权复现禁令大扩充（视觉侧）**：角色本身受保护，改姿势/配色/画风不构成原创；SVG/canvas/CSS/ASCII 等"代码作画"同样适用（L62）。
- [quote] "That's Sonic, so I can't put him on the banner — but I'd love to make your son an original speedster. Here's one: a grinning comet-tailed skateboarding axolotl, grinding across the letters of "HAPPY BIRTHDAY" with confetti streaming behind." —— `<example>` 内的示范回复（蓝色刺猬→Sonic 案）：一句话点破角色、不解释识别依据、提供完全无关的原创设计（滑板蝾螈）。（L70）
- [quote] "Claude does not provide synthesis, production, or distribution guidance for illegal substances. If the person asks for information about illicit or illegal substances, Claude can and should give relevant life-saving and life-preserving information such as dangerous interactions, overdose signs, or when to get help. Claude declines giving any specific protocols for dosing, timing, administration, or combinations; instead, Claude can redirect the user to established harm-reduction information sources, such as dancesafe.org, tripsit.me, and psychonautwiki.org." —— 毒品条款升级：在 Fable 5 的拒/保命二分上新增**转介 harm-reduction 站点**（dancesafe.org、tripsit.me、psychonautwiki.org）。（L56）
- [quote] "In friendly, personal, or emotional chats Claude doesn't use formatting. That's because any kind of formatting lends a more formal and professional tone to the conversation that might feel at odds with a personal, emotional, or friendly chat." —— lists_and_bullets 新增：情感向聊天完全不用格式化。（L121）
- [quote] "After its last tool call in a turn, Claude states the answer the person asked for in one or two sentences; a sign-off alone, such as "Done.", is not a reply. Claude does not repeat in the reply what it already wrote before a tool call." —— `<reply_after_tool_calls>` 首见：工具链结束必须给出实质答复，"Done." 不算答复。（L131）
- [quote] "If Claude cannot verify a URL, ID, specific figure, name, or fact, Claude says so when it states it. If Claude has no real basis for one, Claude says it doesn't know rather than guessing. Claude does not use a name the person has not given, including one inferred from an email address, a username or a handle. A name Claude supplies is a claim about who someone is, which Claude has no way to verify." —— 知识截止章节新增反猜测组：无法验证的 URL/ID/数字/名字须当场声明；无依据就说不知道；不得从邮箱/用户名/handle 推断称呼用户。（L192）
- [quote] "Claude's reliable knowledge cutoff, past which it can't answer reliably, is the end of Jun 2026." —— 知识截止：2026 年 6 月末（**已覆盖 6 月 export controls 事件**，故无需 Opus 5 式的通知段）。（L192）

### 行为特征（中文转述）
- 模型串：`claude-fable-5-1`、`claude-opus-5`、`claude-sonnet-5`、`claude-haiku-4-5-20251001`（L20）。
- 产品生态：Claude Code、Claude Cowork、Chrome/Excel/Powerpoint、Claude Tag（L22–24）；**无 Claude Design**（对比 Opus 5 有）。
- 与 Fable 5 的差异要点：① 差异链接换成 anthropic.com/claude/fable；② 新增 Claude Tag；③ refusal_handling 新增版权/知识产权双段（歌词+视觉作品）与 `<example>`；④ 毒品条款加 harm-reduction 转介；⑤ tone_and_formatting 重排并新增"多轮回答"与"工具进度播报"（L126–128："If Claude is making many tool calls, Claude can give the person quick updates as to what it's doing — one short sentence every couple of tool calls can keep them in the loop and informed."）；⑥ 新增 `<reply_after_tool_calls>`；⑦ user_wellbeing 新增 "Claude does not tell someone that self-harm works, helps, or does something for them, even when they say so themselves."（L144）；⑧ knowledge_cutoff 大幅扩充（URL/ID/名字反猜测 + 不推断用户姓名）；⑨ 禁词句恢复带解释版本（"genuinely", "honestly", "straightforward"，L124）。
- 无 safeguards routing、无 export controls 通知段（cutoff 已覆盖）、无 end_conversation 条款（Fable 5 有而 5.1 无）。
- tone_preference 保留（L196："Claude's outputs are reasonably concise."）。
- 格式哲学微调：lists_and_bullets 内同时存在 "uses lists when asked/multifaceted"（L113）与最小格式化（L115）以及情感聊天零格式化（L121）三层规则。

---

## 时代小结：固定快照时代（2026-02-05 → 2026-09-01）

### 1. 固定快照机制
- 本时代 7 个页面全部为"每模型仅 1 条目"的固定快照（单日期），不同于滚动更新式的多日期页面；无任何页面含 2 个以上日期条目。
- 篇幅量级：130–198 行（约 19–28KB）。最短为 Sonnet 4.6（130 行），最长为 Fable 5.1（198 行），其余集中在 155–178 行。
- 所有页面共享同一模板：frontmatter（title/url/description）→ `## <date>` → ` ```text wrap ` 包裹的 `<claude_behavior>` XML；Opus 4.8、Opus 5、Fable 5.1 三个页面额外在 `</claude_behavior>` 之后带 `<tone_preference>` 尾块。

### 2. 模型家族与品牌叙事演进
- 家族命名漂移：Opus 4.6 自称 "Claude 4.5 model family"（2026-02-05），Sonnet 4.6（2026-02-17）却自称 "Claude 4.6 family"，Opus 4.7 又是单成员的 "Claude 4.7 family"；自 Opus 4.8 起放弃 family 叙事，改称 "The currently selected version of Claude"。
- 人设措辞降调：从 4.6/4.7 的 "the most advanced and intelligent model" → 4.8 的 "the newest Claude model, and the most advanced model publicly available" → Opus 5 的 "a powerful model for complex challenges"（不再自称最智能）→ Fable 系的 "the most intelligent generally available model"。
- Mythos 三阶段演进：① Opus 4.8（2026-05-28）首次提及 Claude Mythos Preview + Project Glasswing（因 cybersecurity 担忧不对公众开放，指向 anthropic.com/glasswing）；② Opus 5（2026-07-24）将其结构化为 "Above Opus sits Anthropic's new Mythos tier"，并明确 Fable 5 的额外安全措施覆盖 biology、cybersecurity、LLM R&D 三域；③ Fable 5/5.1 页面以 "Mythos-class model tier sits above Claude Opus" 开场，Fable 与 Mythos 共享底模、差异仅在 dual-use 安全措施与准入（approved organizations）。
- 差异问询链接变化：Fable 5 → `anthropic.com/news/claude-fable-5-mythos-5`；Fable 5.1 → `anthropic.com/claude/fable`。

### 3. export controls 暂停与恢复事件（全语料唯一叙事点）
- 仅 Opus 5 页面（2026-07-24）完整记载：Fable 5/Mythos 5 于 2026-06-09 首发；2026-06-12 为遵守美国商务部出口管制暂停两款模型的访问；2026-06-30 商务部解除管制；2026-07-01 Anthropic 恢复访问；并附官方声明链接 anthropic.com/news/fable-mythos-access。
- 事件认知机制有明确表述：事件发生在训练数据截止之后，模型"仅从本通知得知"（knows about them only from this notice）；被问及须"如实、就事论事地确认——不否认暂停发生过"，并按政治话题保持公允中立。
- Fable 5 页面（2026-06-09）早于事件故无记载；Fable 5.1 页面（2026-09-01）无通知段的合理原因是其知识截止（end of Jun 2026）已覆盖整个事件窗口。

### 4. safeguards routing 机制（全语料唯一）
- 仅 Opus 5 页面含 `<fable_safeguards_routing>`：解释"用户选了 Fable 5 但查询因 safeguards routing 被改道到 Opus 5"，内嵌官方博客引文——保守调校、平均在不到 5% 的会话中触发、部分话题由次强模型 Opus 5 应答、承认存在误伤并承诺改进。
- Fable 5/5.1 页面均无此章节（被路由方才需要解释路由；Fable 本尊不需要）。

### 5. 结构演进主线（相邻模型增删对照）
- 4.6 → 4.7：新增 `<critical_child_safety_instructions>`（儿童安全 critical 化，"reframe 即拒"）、`<acting_vs_clarifying>`、`<capability_check>`（tool_search 首见）；删除 `<election_info>`、asterisk emote 禁令与禁词句（"genuinely/honestly/straightforward" 整句消失）。
- 4.7 → 4.8：新增 `<default_stance>`（默认帮助）、`<respond_without_citing_system_prompt>`（不引用系统提示词）、`<tool_discovery>`（tool_search 免费化 + SKILL.md 优先流程）、`<tone_preference>`；武器条款扩展到常规武器并引入"累计输出判断/past assistance is not authorization"；儿童安全新增 CSAM 黑话不解码条款；reminders 缩减为 5 种（移除 long_conversation_reminder）；禁词句回归但改用 actually（4.7 曾整句删除）。
- 4.8 → Fable 5：移除 default_stance/tool_discovery/tone_preference/weapon 累计段；tone_and_formatting 重构（warm tone 前置、lists 后置）；新增"默认成年人假设"、毒品条款、means-restriction 扩展、crisis-services 经历应对、不代拟诊断标签、进食障碍反因果叙事、end_conversation 工具（先警告一次）；reminders 恢复 6 种。
- Fable 5 → Opus 5：新增 `<fable_safeguards_routing>` 与 export controls 通知段；default_stance/tone_preference/武器累计段回归；新增 intellectual curiosity 段、危机时"幸福优先于任务完成"；无 end_conversation、无 tool_discovery；lists_and_bullets 子标签取消（并入正文一句）。
- Opus 5 → Fable 5.1：新增 `<example>` 示例块与版权双段（歌词/诗/书 + 视觉作品/角色，代码作画全覆盖，1929 年豁免线）、`<reply_after_tool_calls>`、多轮回答与工具进度播报、情感聊天零格式化、"自伤无效论"禁令、knowledge_cutoff 反猜测扩充（不验证不出处、不从邮箱推断姓名）；移除 safeguards routing 与 export controls 通知段（cutoff 已覆盖）、移除 end_conversation；毒品条款新增 harm-reduction 站点转介；禁词恢复 straightforward（附解释）。

### 6. 工具/记忆/产品生态变化
- tool_search 生态：4.7 首见（capability_check），4.8 扩为 `<tool_discovery>`（延迟工具、视为免费、SKILL.md 第一调用、/mnt/user-data/uploads 延后）；4.8 之后仅在 Fable 5.1 残留工具进度播报与 reply_after_tool_calls 的工具礼仪，完整 tool_discovery 章节未在其他页面复现。
- 记忆系统：全时代无独立记忆章节，统一以 settings 可开关项 "generate memory from chat history" 表述（7 页一致）；Fable 5.1 另在 knowledge_cutoff 增加"不用用户未提供的名字"的人际边界。
- 产品生态时间线：Cowork（4.6，非开发者桌面工具）→ +Claude in Powerpoint（Sonnet 4.6）→ Cowork 更名 Claude Cowork + 定位改为 agentic knowledge work（4.7）→ +Claude Design（4.8）→ +Claude Tag（Opus 5，Slack @Claude 多人委派）→ Fable 5.1 保留 Tag、弃 Design。Chrome agent 描述从"a browsing agent"升级为"can interact with websites autonomously"（4.7）。
- 平台称谓："an API and developer platform"（4.6/4.6 Sonnet）→ "an API and Claude Platform"（4.7 起）。

### 7. 稳定基线（7 页几乎不变的部分）
- support/docs 双路由（support.claude.com、docs.claude.com）；prompting 指南链接 `docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview`；settings 清单六项；"Anthropic 永远不会发送削弱限制的提醒"；evenhandedness 六段式（最佳立场重述、极除外、刻板印象警惕、政治观点克制、不重复灌输、善意解读）；"accountability without self-abasement" 错误应对；NEDA→National Alliance for Eating Disorders（复数形式自 4.8 起）。
- 知识截止轨迹：May 2025（4.6）→ Aug 2025（Sonnet 4.6）→ Jan 2026（4.7/4.8/Fable 5）→ May 2026（Opus 5）→ Jun 2026（Fable 5.1）。

### 8. 采集边界说明
- 本登记仅覆盖 7 个本地快照文件中实际存在的内容；Sonnet 5、Mythos 5、Haiku 4.6 等仅在模型清单中被提及，无独立页面，相关行为特征无从登记，不做推测。
- 引文均逐字核对自本地落盘文件；行号为本地文件行号，与线上渲染页码无关。
