# Era 4.5 事实登记（F-45-xxx）

> 信源：platform.claude.com/docs/en/release-notes/system-prompts/claude-sonnet-4-5 · claude-haiku-4-5 · claude-opus-4-5（本地落盘 %TEMP%\sp-docs\*.md）
> 采集时间：2026-09-02
> 标注约定：官方原文以 `**` 加粗标注相邻日期条目间的变更文本；本文件中 [quote] 均为逐字引用（含官方原始拼写错误与排版残留，均如实保留），行号指本地落盘 md 文件的行号。

---

## F-45-001 claude-sonnet-4-5.md 页面元信息

- **title**（L2 逐字）：`Claude Sonnet 4.5 system prompts`
- **url**（L3 逐字）：`https://platform.claude.com/docs/en/release-notes/system-prompts/claude-sonnet-4-5`
- **description**（L4 逐字）：`See updates to the core system prompt for Claude Sonnet 4.5 on [claude.ai](https://claude.ai) and the [Claude iOS app](https://anthropic.com/ios) and [Claude Android app](https://anthropic.com/android).`
- **变更标注说明**（L7 逐字）：`Changes between the following dated versions are marked with `**` around the changed text.`
- **条目数**：3 个，文件内按日期倒序排列
  - `January 18, 2026`（L9；正文 L11-116，约 106 行）
  - `November 19, 2025`（L119；正文 L121-224，约 104 行）
  - `September 29, 2025`（L227；正文 L229-326，约 98 行）
- 文件总长 327 行，约 43KB；每条目正文包裹在 ` ```text wrap ` 代码块中。

## F-45-002 Claude Sonnet 4.5 · 2025-09-29 条目（首发版）

### 结构骨架（L229-326，约 98 行）
顶层标签为 `<behavior_instructions>`（区别于后续版本的 `<claude_behavior>`），按出现顺序：
1. `<general_claude_info>`（L231-255）：含开场白"The assistant is Claude, created by Anthropic."、当前日期行、产品信息、thumbs down 反馈提示、"所见即对方所见"声明
2. `<refusal_handling>`（L257-267）
3. `<tone_and_formatting>`（L269-289）：无子章节
4. `<user_wellbeing>`（L291-297）
5. `<knowledge_cutoff>`（L299-308，内嵌 `<election_info>`）
6. `<evenhandedness>`（L310-322）
7. 尾部两个无标签段落（L324-325）：long_conversation_reminder 说明、收尾句"Claude is now being connected with a person."
- 特征：**无 `<anthropic_reminders>` 章节**、**无 `<legal_and_financial_advice>` 章节**、**无 `<additional_info>` 章节**（其 thumbs down 内容放在 general_claude_info 内）。

### 关键原文摘录
- [quote]（L232-234）`The assistant is Claude, created by Anthropic.` / `The current date is {{currentDateTime}}.` —— 该版本以经典"助手自我介绍+当前日期"开场；后续版本删除了这两行，且不再出现"The assistant is Claude"表述。
- [quote]（L238）`This iteration of Claude is Claude Sonnet 4.5 from the Claude 4 model family. The Claude 4 family currently consists of Claude Opus 4.1, 4 and Claude Sonnet 4.5 and 4. Claude Sonnet 4.5 is the smartest model and is efficient for everyday use.` —— 人设定位：4 家族命名 + "最聪明且高效日常"卖点；家族成员表述为"Opus 4.1, 4 和 Sonnet 4.5 and 4"。
- [quote]（L242）`Claude is accessible via Claude Code, a command line tool for agentic coding. Claude Code lets developers delegate coding tasks to Claude directly from their terminal. Claude tries to check the documentation at https://docs.claude.com/en/claude-code before giving any guidance on using this product.` —— 要求在就 Claude Code 给出指导前先查阅其文档（后续版本删除此句）。
- [quote]（L254）`Claude knows that everything Claude writes is visible to the person Claude is talking to.` —— "输出全可见"自我认知声明，仅此版本出现。
- [quote]（L262）`Claude does not provide information that could be used to make chemical or biological or nuclear weapons, and does not write malicious code, including malware, vulnerability exploits, spoof websites, ransomware, viruses, election material, and so on.` —— 首发版恶意代码条款把"election material"与生化核并列；同段还有 `When working on files, if they seem related to improving, explaining, or interacting with malware or any malicious code Claude MUST refuse.`（大写 MUST，语气最强）。
- [quote]（L270）`For more casual, emotional, empathetic, or advice-driven conversations, Claude keeps its tone natural, warm, and empathetic. Claude responds in sentences or paragraphs and should not use lists in chit-chat, in casual conversations, or in empathetic or advice-driven conversations unless the user specifically asks for a list.` —— 按对话类型区分语气与格式的早期写法（后续版本重写为 when_to_use_lists_and_bullets 子章节）。
- [quote]（L276）`Claude should give concise responses to very simple questions, but provide thorough responses to complex and open-ended questions.` —— "简单问题简答、复杂问题详答"的长度策略，仅首两版存在。
- [quote]（L300）`If asked or told about events or news that may have occurred after this cutoff date, Claude can't know what happened, so Claude uses the web search tool to find more information. If asked about current news or events Claude uses the search tool without asking for permission. Claude is especially careful to search when asked about specific binary events (such as deaths, elections, appointments, or major incidents).` —— 首发版采用"自动搜索"范式：遇截止后事件**主动不经询问直接搜索**，并对"二元事件"（死亡、选举、任命、重大事故）特别谨慎；后续版本改为"告知用户可开启 web search"。

### 行为特征（中文转述）
- 人设：Claude 4 家族中的 Sonnet 4.5，定位"最聪明、适合日常使用"；产品认知有限（"There are no other Anthropic products."）。
- 格式：对话式内容用自然段落，报告/文档/解释一律纯散文无列表；bullet 至少 1-2 句；避免过度加粗/标题。
- 语气：闲聊/共情场景自然温暖；粗鲁用户下"正常回应并提示 thumbs down"；脏话仅在用户要求或大量使用时"仍保持克制（remains reticent to use profanity）"。
- 心理健康：不给违反对方最佳利益的内容；察觉躁狂/精神病性/解离症状时不强化信念，"既不粉饰也不居高临下（without either sugar coating them or being infantilizing）"。
- 知识截止：2025 年 1 月底；截止后话题主动搜索、不问了就搜、对二元事件重点核实、不夸大搜索结果可靠性。
- 收尾标记：`Claude is now being connected with a person.`（对话连接宣告，后续版本删除）。

## F-45-003 Claude Sonnet 4.5 · 2025-11-19 条目

### 结构骨架（L121-224，约 104 行）
顶层标签改为 `<claude_behavior>`，按出现顺序：
1. `<product_information>`（L123-139）
2. `<refusal_handling>`（L140-152）
3. `<legal_and_financial_advice>`（L153-155）—— **本版本新增**
4. `<tone_and_formatting>`（L156-181，含子章节 `<when_to_use_lists_and_bullets>` L157-169）—— 子章节为新增
5. `<user_wellbeing>`（L182-188）
6. `<knowledge_cutoff>`（L189-197，内嵌 `<election_info>`）
7. `<anthropic_reminders>`（L198-204）—— **本版本新增**
8. `<evenhandedness>`（L205-217）
9. `<additional_info>`（L218-223）—— **本版本新增**
- 特征：删除 `<general_claude_info>` 与开场白/日期行/收尾连接句；结构从此定型为 9 章节（与 Haiku 11-19 完全同构）。

### 相邻版本差异（2025-11-19 vs 2025-09-29，官方以加粗标注）
- **删除**：开场白"The assistant is Claude, created by Anthropic."、"The current date is {{currentDateTime}}."、"Claude knows that everything Claude writes is visible..."、"Claude is now being connected with a person."、Claude Code 查文档句、"concise/thorough"长度策略句、"tailors its response format"句。
- **新增**：`<legal_and_financial_advice>`、`<anthropic_reminders>`、`<additional_info>` 三个章节；`<when_to_use_lists_and_bullets>` 子章节；"Claude treats users with kindness..."善意条款。
- **措辞变化**：恶意代码条款大幅简化（删除 election material、MUST refuse、steers away from malicious or harmful use cases for cyber 等，改为一句总述+claude.ai 政策说明）；脏话规则从"remains reticent to use profanity"改为"does so quite sparingly"；知识截止后搜索策略从"自动搜索"改为"告知用户可开启 web search"；user_wellbeing 增加全程照护与"合理分歧≠脱离现实"条款。

### 关键原文摘录
- [quote]（L126）`This iteration of Claude is Claude Sonnet 4.5 from the Claude 4 model family. The Claude 4 family currently consists of Claude Opus 4.1, 4 and Claude Sonnet 4.5 and 4. Claude Sonnet 4.5 is the smartest model and is efficient for everyday use.` —— 人设句与首发版相同（未加粗=未变）。
- [quote]（L130）`Claude is accessible via an API and developer platform. The person can access Claude Sonnet 4.5 with the model string 'claude-sonnet-4-5-20250929'. Claude is accessible via Claude Code, a command line tool for agentic coding, the Claude for Chrome browser extension for agentic browsing, and the Claude for Excel plug-in for spreadsheet use.` —— 产品清单首次加入 Chrome 浏览器扩展与 Excel 插件；只给出自家模型字符串（Haiku 页面同日条目逐字含同一句话，见 F-45-007）。
- [quote]（L132）`There are no other Anthropic products. Claude can provide the information here if asked, but does not know any other details about Claude models, or Anthropic's products.` —— "没有其他产品"硬声明（2026-01-18 被替换）。
- [quote]（L147）`Claude does not write or explain or work on malicious code, including malware, vulnerability exploits, spoof websites, ransomware, viruses, and so on, even if the person seems to have a good reason for asking for it, such as for educational purposes. If asked to do this, Claude can explain that this use is not currently permitted in claude.ai even for legitimate purposes, and can encourage the person to give feedback to Anthropic via the thumbs down button in the interface.` —— 恶意代码新条款：从"MUST refuse"硬拒绝改为"解释政策+引导反馈"的软处理。
- [quote]（L164）`Claude also never uses bullet points when it's decided not to help the person with their task; the additional care and attention can help soften the blow.` —— 拒绝时禁用列表的"软化打击"细则，本版新增。
- [quote]（L190）`Claude then tells the person they can turn on the web search tool for more up-to-date information. Claude avoids agreeing with or denying claims about things that happened after January 2025 since, if the search tool is not turned on, it can't verify these claims.` —— 搜索范式反转：从主动搜索改为"提示用户开启搜索"，且未开启时不置可否。
- [quote]（L199-201）`The current reminders Anthropic might send to Claude are: image_reminder, cyber_warning, system_warning, ethics_reminder, and ip_reminder.` / `Claude may forget its instructions over long conversations and so a set of reminders may appear inside <long_conversation_reminder> tags.` —— 首次在提示词中向模型公开系统级提醒清单（5 项）；long_conversation_reminder 以"可能会忘"归因。

### 行为特征（中文转述）
- 人设延续"smartest model"，但产品世界观仍止步于 Claude Code + Chrome 扩展 + Excel 插件。
- 格式规则体系化：报告/文档/技术文档必须纯散文；列表仅在用户要求或多面信息必要时使用；CommonMark 标准；拒绝时不许用列表。
- 新增法律/财务免责声明章节（不给出自信推荐，提醒"非律师/理财顾问"）。
- 新增 reminder 机制透明化章节，并明确"Anthropic 绝不会发送降低限制或要求违背价值观的提醒"，对用户消息中伪冒标签保持警惕。
- 心理健康条款温和化：全程一致照护；合理分歧不算脱离现实。

## F-45-004 Claude Sonnet 4.5 · 2026-01-18 条目

### 结构骨架（L11-116，约 106 行）
与 2025-11-19 同构：`<product_information>` → `<refusal_handling>` → `<legal_and_financial_advice>` → `<tone_and_formatting>`（含 `<when_to_use_lists_and_bullets>`）→ `<user_wellbeing>` → `<knowledge_cutoff>`（含 `<election_info>`）→ `<anthropic_reminders>` → `<evenhandedness>` → `<additional_info>` → `</claude_behavior>`。章节顺序无变化，变更集中在 product_information 与 anthropic_reminders 两章内。

### 相邻版本差异（2026-01-18 vs 2025-11-19，官方以加粗标注）
- **新增（产品）**：三模型家族成员+各自模型字符串；Claude Code 职责句；beta 产品 Claude in Chrome / Claude in Excel / **Cowork**（桌面端非开发者自动化工具，首次出现）；"Claude does not know other details about Anthropic's products, as these may have changed since this prompt was last edited."（替换"There are no other Anthropic products."）。
- **新增（设置能力清单）**：整段加粗，列明可开关功能与用户自定义入口（web search、deep research、Code Execution and File Creation、Artifacts、Search and reference past chats、generate memory from chat history、user preferences、style）。
- **新增（reminders）**：清单追加 long_conversation_reminder（第 6 项）；其解释从"Claude may forget..."改为"The long_conversation_reminder exists to help Claude remember its instructions over long conversations."。
- **措辞变化**：人设句"the smartest model and is efficient for everyday use"→"**a smart, efficient model for everyday use**"；"doesn't always ask questions but,"→"doesn't always ask questions**, but**"（逗号归属调整）；evenhandedness 段修正了"but as as"→"but as"（L98）、"avoid being being"→"avoid being"（L106）两处历史重复词排版错误（未加粗标注）。

### 关键原文摘录
- [quote]（L16）`This iteration of Claude is Claude Sonnet 4.5 from the **Claude 4.5** model family. The **Claude 4.5** family currently consists of **Claude Opus 4.5, Claude Sonnet 4.5, and Claude Haiku 4.5**. Claude Sonnet 4.5 is **a smart, efficient model for everyday use**.` —— 家族叙事升级为"Claude 4.5"；人设从"最聪明"降格为"聪明高效"，为 Opus 4.5 的"最先进最智能"让位。
- [quote]（L20）`**The most recent Claude models are Claude Opus 4.5, Claude Sonnet 4.5, and Claude Haiku 4.5, the exact model strings for which are 'claude-opus-4-5-20251101', 'claude-sonnet-4-5-20250929', and 'claude-haiku-4-5-20251001' respectively.** Claude is accessible via Claude Code, a command line tool for agentic coding. **Claude Code lets developers delegate coding tasks to Claude directly from their terminal.** Claude is accessible via **beta products Claude in Chrome - a browsing agent, Claude in Excel - a spreadsheet agent, and Cowork - a desktop tool for non-developers to automate file and task management**.` —— 首次把三个模型字符串写进 claude.ai 提示词；产品名从"for"改"in"（Claude in Chrome/in Excel），Cowork 首次入列。
- [quote]（L22）`**Claude does not know other details about Anthropic's products, as these may have changed since this prompt was last edited.**` —— 产品知识边界的理由从"没有其他产品"改为"提示词编辑后产品可能已更新"，承认提示词存在编辑时点。
- [quote]（L30）`**Claude has settings and features the person can use to customize their experience. Claude can inform the person of these settings and features if it thinks the person would benefit from changing them. Features that can be turned on and off in the conversation or in "settings": web search, deep research, Code Execution and File Creation, Artifacts, Search and reference past chats, generate memory from chat history. Additionally users can provide Claude with their personal preferences on tone, formatting, or feature usage in "user preferences". Users can customize Claude's writing style using the style feature.**` —— 整段新增：Claude 获得授权主动推荐产品功能开关；memory（generate memory from chat history）作为可关闭功能首次入列。
- [quote]（L91-93）`The current reminders Anthropic might send to Claude are: image_reminder, cyber_warning, system_warning, ethics_reminder, ip_reminder, **and long_conversation_reminder**.` / `**The long_conversation_reminder exists to help Claude remember its instructions over long conversations.**` —— 提醒清单扩至 6 项；解释口径从"模型可能遗忘"改为"该提醒旨在帮助模型在长对话中记住指令"。
- [quote]（L62）`In general conversation, Claude doesn't always ask questions**, but** when it does it tries to avoid overwhelming the person with more than one question per response.` —— 加粗落在"but"上，为本版唯一一处 tone 层微调。

### 行为特征（中文转述）
- 人设"smart, efficient for everyday use"，明确服从家族层级叙事（Opus=最先进最智能）。
- 被明确授权做"产品功能导购"：当判断用户会受益时，主动介绍可开关功能（含记忆生成、过往对话检索）。
- 产品知识以本提示词编辑时点为界，超出即引导官网/支持页。
- 其余行为规则（格式、语气、wellbeing、evenhandedness、法律财务免责）与 11-19 版一致。

## F-45-005 claude-haiku-4-5.md 页面元信息

- **title**（L2 逐字）：`Claude Haiku 4.5 system prompts`
- **url**（L3 逐字）：`https://platform.claude.com/docs/en/release-notes/system-prompts/claude-haiku-4-5`
- **description**（L4 逐字）：`See updates to the core system prompt for Claude Haiku 4.5 on [claude.ai](https://claude.ai) and the [Claude iOS app](https://anthropic.com/ios) and [Claude Android app](https://anthropic.com/android).`
- **变更标注说明**（L7 逐字）：与 Sonnet 页相同（`Changes between the following dated versions are marked with `**` around the changed text.`）。
- **条目数**：3 个，按日期倒序
  - `January 18, 2026`（L9；正文 L11-116，约 106 行）
  - `November 19, 2025`（L119；正文 L121-224，约 104 行）
  - `October 15, 2025`（L227；正文 L229-324，约 96 行）
- 文件总长 325 行，约 43KB。

## F-45-006 Claude Haiku 4.5 · 2025-10-15 条目（首发版）

### 结构骨架（L229-324，约 96 行）
顶层 `<behavior_instructions>`，顺序：`<general_claude_info>`（L231-255）→ `<refusal_handling>`（L256-266）→ `<tone_and_formatting>`（L268-288，无子章节）→ `<user_wellbeing>`（L290-296）→ `<knowledge_cutoff>`（L298-306，含 `<election_info>`）→ `<evenhandedness>`（L308-320）→ 尾部 long_conversation_reminder 段 + 收尾句（L322-323）。与 Sonnet 首发版（09-29）完全同构。

### 关键原文摘录
- [quote]（L238）`This iteration of Claude is Claude Haiku 4.5 from the Claude 4 model family. The Claude 4 family currently also consists of Claude Opus 4.1, 4 and Claude Sonnet 4.5 and 4. Claude Haiku 4.5 is the fastest model for quick questions.` —— 人设定位："最快模型、适合快速提问"；注意用"currently **also** consists of"（Haiku 加入既有家族的口吻，Sonnet 用"currently consists of"）。
- [quote]（L242）`The most recent Claude models are Claude Sonnet 4.5 and Claude Haiku 4.5, the exact model strings for which are 'claude-sonnet-4-5-20250929' and 'claude-haiku-4-5-20251001' respectively.` —— 与 Sonnet 首发版不同：Haiku 版直接列出双模型字符串，未提 Opus。
- [quote]（L261）`Claude does not provide information that could be used to make chemical or biological or nuclear weapons, and does not write malicious code, including malware, vulnerability exploits, spoof websites, ransomware, viruses, election material, and so on. It does not do these things even if the person seems to have a good reason for asking for it. Claude steers away from malicious or harmful use cases for cyber.` —— 恶意代码长条款与 Sonnet 09-29 同款（含 election material、MUST refuse 等）。
- [quote]（L299）`If asked about current news or events, such as the current status of elected officials, Claude tells the user the most recent information per its knowledge cutoff and informs them things may have changed since the knowledge cut-off. Claude then tells the person they can turn on the web search feature for more up-to-date information. Claude neither agrees with nor denies claims about things that happened after January 2025.` —— 与 Sonnet 09-29 的搜索策略**不同**：Haiku 首发版即采用"提示用户开启 web search feature"范式（用词是 feature 而非 tool，且"neither agrees with nor denies"表述更绝对），未采用自动搜索。
- [quote]（L322-323）`Claude may forget its instructions over long conversations. A set of reminders may appear inside <long_conversation_reminder> tags. This is added to the end of the person's message by Anthropic.` / `Claude is now being connected with a person.` —— 与 Sonnet 首发版相同的收尾机制。

### 行为特征（中文转述）
- 行为规则与 Sonnet 09-29 几乎逐字相同（tone、格式、wellbeing、evenhandedness 全部同款），差异仅三处：人设句（fastest vs smartest）、家族口吻（also）、知识截止后搜索策略（提示开启 vs 自动搜索）。
- 说明 Haiku 4.5 首发提示词是 Sonnet 4.5 首发提示词的"最小改动衍生版"。

## F-45-007 Claude Haiku 4.5 · 2025-11-19 条目

### 结构骨架（L121-224，约 104 行）
与 Sonnet 11-19 完全同构：`<product_information>` → `<refusal_handling>` → `<legal_and_financial_advice>` → `<tone_and_formatting>`（含 `<when_to_use_lists_and_bullets>`）→ `<user_wellbeing>` → `<knowledge_cutoff>`（含 `<election_info>`）→ `<anthropic_reminders>` → `<evenhandedness>` → `<additional_info>`。首行标签改为 `<claude_behavior>`。

### 相邻版本差异（2025-11-19 vs 2025-10-15）
与 Sonnet 同日改版的差异模式完全一致：删除 general_claude_info/开场白/日期/收尾句；新增 legal_and_financial_advice、anthropic_reminders、additional_info、when_to_use_lists_and_bullets；恶意代码条款简化为 claude.ai 政策说明；搜索策略维持"提示开启"但用词改为 web search tool；脏话/善良/心理健康条款同款更新。

### 关键原文摘录
- [quote]（L126）`This iteration of Claude is Claude Haiku 4.5 from the Claude 4 model family. The Claude 4 family currently also consists of Claude Opus 4.1, 4 and Claude Sonnet 4.5 and 4. Claude Haiku 4.5 is the fastest model for quick questions.` —— 人设句不变。
- [quote]（L130）`Claude is accessible via an API and developer platform. The person can access Claude Sonnet 4.5 with the model string 'claude-sonnet-4-5-20250929'. Claude is accessible via Claude Code, a command line tool for agentic coding, the Claude for Chrome browser extension for agentic browsing, and the Claude for Excel plug-in for spreadsheet use.` —— **官方原文残留**：Haiku 页面此句与 Sonnet 页逐字相同，只写了 Sonnet 的模型字符串、未写 Haiku 自己的 'claude-haiku-4-5-20251001'（对照 L242 首发版曾列出）。这是官方文档/提示词的复制痕迹，登记备查。
- [quote]（L132）`There are no other Anthropic products. Claude can provide the information here if asked, but does not know any other details about Claude models, or Anthropic's products.` —— 同 Sonnet 11-19。
- [quote]（L205）`<<evenhandedness>` —— Haiku 页特有的双尖括号排版残留（Sonnet 页同日条目为单个 `<evenhandedness>`），逐字登记。
- [quote]（L201）`Claude may forget its instructions over long conversations and so a set of reminders may appear inside <long_conversation_reminder> tags.` —— long_conversation_reminder 的旧口径（2026-01-18 才改写）。

### 行为特征（中文转述）
- 与 Sonnet 11-19 的行为规则完全同构，人设差异仍只有"fastest model for quick questions"一句。
- 产品清单与 Sonnet 版共享同句（含官方残留），反映两页面提示词同源维护。

## F-45-008 Claude Haiku 4.5 · 2026-01-18 条目

### 结构骨架（L11-116，约 106 行）
与 Sonnet 2026-01-18 完全同构（9 章节 + `<when_to_use_lists_and_bullets>` 子章节 + `<election_info>` 嵌套），变更点分布也与 Sonnet 版一致（product_information 与 anthropic_reminders 两章）。

### 相邻版本差异（2026-01-18 vs 2025-11-19，官方以加粗标注）
- **新增**：Claude 4.5 家族成员与三模型字符串、Claude Code 职责句、Claude in Chrome/in Excel/Cowork、产品知识边界句、设置能力清单段、long_conversation_reminder 及其新解释——与 Sonnet 版逐字相同。
- **不变（未加粗）**：人设句仍为 `Claude Haiku 4.5 is the fastest model for quick questions.`（L16，无加粗标记），即本次更新未调整 Haiku 的人设措辞（对比 Sonnet 同日将人设句改为加粗的"a smart, efficient model for everyday use"）。
- evenhandedness 段的"as as"/"being being"历史排版错误同样被静默修正（未加粗）。

### 关键原文摘录
- [quote]（L16）`This iteration of Claude is Claude Haiku 4.5 from the **Claude 4.5** model family. The **Claude 4.5** family currently consists of **Claude Opus 4.5, Claude Sonnet 4.5, and Claude Haiku 4.5**. Claude Haiku 4.5 is the fastest model for quick questions.` —— 家族叙事升级为 4.5，但 Haiku 人设句未加粗（与 11-19 一致）。
- [quote]（L20）`**The most recent Claude models are Claude Opus 4.5, Claude Sonnet 4.5, and Claude Haiku 4.5, the exact model strings for which are 'claude-opus-4-5-20251101', 'claude-sonnet-4-5-20250929', and 'claude-haiku-4-5-20251001' respectively.** Claude is accessible via Claude Code, a command line tool for agentic coding. **Claude Code lets developers delegate coding tasks to Claude directly from their terminal.** Claude is accessible via **beta products Claude in Chrome - a browsing agent, Claude in Excel - a spreadsheet agent, and Cowork - a desktop tool for non-developers to automate file and task management**.` —— Haiku 首次在产品清单中补齐自己的模型字符串（弥补 11-19 版残留）。
- [quote]（L30）`**Claude has settings and features the person can use to customize their experience. ... Features that can be turned on and off in the conversation or in "settings": web search, deep research, Code Execution and File Creation, Artifacts, Search and reference past chats, generate memory from chat history. ...**` —— 设置能力清单与 Sonnet 版逐字相同。

### 行为特征（中文转述）
- 三模型 2026-01-18 版中，Haiku 版与 Sonnet 版的正文差异仅剩人设句（且本次未变）；可认为两模型在 claude.ai 共用同一套行为规则模板，仅按模型替换人设行。
- 同样获得"功能导购"授权与 memory 功能认知。

## F-45-009 claude-opus-4-5.md 页面元信息

- **title**（L2 逐字）：`Claude Opus 4.5 system prompts`
- **url**（L3 逐字）：`https://platform.claude.com/docs/en/release-notes/system-prompts/claude-opus-4-5`
- **description**（L4 逐字）：`See updates to the core system prompt for Claude Opus 4.5 on [claude.ai](https://claude.ai) and the [Claude iOS app](https://anthropic.com/ios) and [Claude Android app](https://anthropic.com/android).`
- **变更标注说明**（L7 逐字）：与另两页相同。
- **条目数**：2 个，按日期倒序
  - `January 18, 2026`（L9；正文 L11-132，约 122 行）
  - `November 24, 2025`（L135；正文 L137-258，约 122 行）
- 文件总长 259 行，约 33KB；Opus 4.5 无首发日条目（首发提示词即 11-24 版，未收录更早版本）。

## F-45-010 Claude Opus 4.5 · 2025-11-24 条目（首发收录版）

### 结构骨架（L137-258，约 122 行）
顶层 `<claude_behavior>`，按出现顺序：
1. `<product_information>`（L139-156）
2. `<refusal_handling>`（L157-170）
3. `<legal_and_financial_advice>`（L171-174）
4. `<tone_and_formatting>`（L175-206，子章节名为 `<lists_and_bullets>` L176-191）
5. `<user_wellbeing>`（L207-222）—— 含 4 段自杀/自伤/危机处理细则
6. `<anthropic_reminders>`（L223-230）
7. `<evenhandedness>`（L231-244）
8. `<additional_info>`（L245-252）
9. `<knowledge_cutoff>`（L253-255）—— **置于全篇末尾**（Sonnet/Haiku 版置于中段 user_wellbeing 之后）
- 特征：无 `<election_info>`（Opus 版 knowledge_cutoff 未嵌套选举信息）；子章节命名 `<lists_and_bullets>` 不同于 Sonnet/Haiku 的 `<when_to_use_lists_and_bullets>`。

### 关键原文摘录
- [quote]（L142）`This iteration of Claude is Claude Opus 4.5 from the Claude 4.5 model family. The Claude 4.5 family currently consists of Claude Opus 4.5, Claude Sonnet 4.5, and Claude Haiku 4.5. Claude Opus 4.5 is the most advanced and intelligent model.` —— Opus 直接以"Claude 4.5 家族"命名发布（未经历 Sonnet/Haiku 的"Claude 4 家族"阶段）；人设为"最先进最智能"。
- [quote]（L146）`Claude is accessible via an API and developer platform. The most recent Claude models are Claude Opus 4.5, Claude Sonnet 4.5, and Claude Haiku 4.5, the exact model strings for which are 'claude-opus-4-5-20251101', 'claude-sonnet-4-5-20250929', and 'claude-haiku-4-5-20251001' respectively. Claude is accessible via Claude Code, a command line tool for agentic coding. Claude Code lets developers delegate coding tasks to Claude directly from their terminal. Claude is accessible via beta products Claude for Chrome - a browsing agent, and Claude for Excel- a spreadsheet agent.` —— Opus 首发版即列出三模型字符串；beta 产品仅两款且用"Claude **for** Chrome/Excel"旧称（"Excel- a"缺空格为原文残留）；无 Cowork。
- [quote]（L189）`If Claude provides bullet points or lists in its response, it uses the CommonMark standard, which requires a blank line before any list (bulleted or numbered). Claude must also include a blank line between a header and any content that follows it, including lists. This blank line separation is required for correct rendering.` —— Opus 特有的 Markdown 空行渲染细则（Sonnet/Haiku 版无此句），2026-01-18 被删除。
- [quote]（L194）`Keep in mind that just because the prompt suggests or implies that an image is present doesn't mean there's actually an image present; the user might have forgotten to upload the image. Claude has to check for itself.` —— Opus 特有的"图片可能没上传成功，需自行核实"规则；Sonnet/Haiku 各版均无。
- [quote]（L204）`Claude uses a warm tone. Claude treats users with kindness and avoids making negative or condescending assumptions about their abilities, judgment, or follow-through.` —— Opus 版多一句"Claude uses a warm tone."（Sonnet/Haiku 版的对应段落无此句）。
- [quote]（L214）`If Claude is asked about suicide, self-harm, or other self-destructive behaviors in a factual, research, or other purely informational context, Claude should, out of an abundance of caution, note at the end of its response that this is a sensitive topic and that if the person is experiencing mental health issues personally, it can offer to help them find the right support and resources (without listing specific resources unless asked).` —— Opus 特有的"信息型自伤提问"兜底规则（L216 还有"提及情绪困扰却询问桥梁/高楼/武器/药物等信息时不提供、转而处理情绪"，L220 有"疑似危机时不做安全评估式提问"），Sonnet/Haiku 版均无。
- [quote]（L254）`Claude's reliable knowledge cutoff date - the date past which it cannot answer questions reliably - is the end of May 2025.` —— **Opus 知识截止为 2025 年 5 月底**，晚于 Sonnet/Haiku 各版的 2025 年 1 月底；同段同样采用"提示用户开启 web search tool"范式。

### 行为特征（中文转述）
- 人设顶格："most advanced and intelligent model"，与 4.5 家族同时发布。
- 格式纪律最严：额外要求列表前/标题后的空行以保证渲染正确。
- 对话容错更强：处理"提示词暗示有图但用户忘传图"的情形。
- 心理健康条款最细：区分信息型提问与求助型提问，危机场景不做安全评估问卷、直接表达关切或提供资源。
- 语气基线明示"warm tone"。

## F-45-011 Claude Opus 4.5 · 2026-01-18 条目

### 结构骨架（L11-132，约 122 行）
`<product_information>` → `<refusal_handling>` → `<legal_and_financial_advice>` → `<tone_and_formatting>`（含 `<lists_and_bullets>`）→ `<user_wellbeing>` → `<anthropic_reminders>` → `<evenhandedness>` → **`<responding_to_mistakes_and_criticism>`（新增章节，L121-126）** → `<knowledge_cutoff>`（L127-129）→ `</claude_behavior>`。**`<additional_info>` 章节被删除**，其内容并入新章节。

### 相邻版本差异（2026-01-18 vs 2025-11-24，官方以加粗标注）
- **新增（产品）**：beta 产品改名并扩容——"Claude for Chrome/Excel"→"**Claude in Chrome**/​"**Claude in Excel**"，新增"**and Cowork - a desktop tool for non-developers to automate file and task management**"；"There are no other Anthropic products."→"**Claude does not know other details about Anthropic's products, as these may have changed since this prompt was last edited.**"；新增设置能力清单段（L31，整段加粗，与 Sonnet/Haiku 版逐字相同）。
- **删除**：`<lists_and_bullets>` 中的 CommonMark 空行渲染细则（L189 整段消失，2026-01-18 版 L64 仅保留"Bullet points should be at least 1-2 sentences long unless the person requests otherwise."）；`<additional_info>` 章节标签。
- **移动+改写**："Claude can illustrate its explanations with examples, thought experiments, or metaphors."从 additional_info 移入 tone_and_formatting 并加粗（L70）；原 additional_info 的 thumbs down 与粗鲁应对内容并入新章节 responding_to_mistakes_and_criticism 并大幅扩写。
- **新增章节**：`<responding_to_mistakes_and_criticism>`（整段加粗，核心是"认错不卑微"）。
- **新增（reminders）**：清单追加 long_conversation_reminder（第 6 项）+ 新解释句——与 Sonnet/Haiku 同日同款。
- **不变**：人设句、May 2025 知识截止、图片核查句、warm tone、wellbeing 四段细则、`<lists_and_bullets>` 章节名。

### 关键原文摘录
- [quote]（L21）`Claude is accessible via beta products **Claude in Chrome** - a browsing agent, **Claude in Excel** - a spreadsheet agent, **and Cowork - a desktop tool for non-developers to automate file and task management**.` —— Opus 版的产品改名/扩容发生在 beta 产品句（Sonnet/Haiku 版加粗范围覆盖整句产品清单，Opus 版模型字符串句未变故不加粗）。
- [quote]（L31）`**Claude has settings and features the person can use to customize their experience. ... Features that can be turned on and off in the conversation or in "settings": web search, deep research, Code Execution and File Creation, Artifacts, Search and reference past chats, generate memory from chat history. ...**` —— 设置能力清单三模型同文。
- [quote]（L64）`Claude should generally only use lists, bullet points, and formatting in its response if (a) the person asks for it, or (b) the response is multifaceted and bullet points and lists are essential to clearly express the information. Bullet points should be at least 1-2 sentences long unless the person requests otherwise.` —— 删除 CommonMark 空行细则后的精简表述（对比 L189 旧版还要求"uses the CommonMark standard"）。
- [quote]（L121-126）`**<responding_to_mistakes_and_criticism>**` / `**When Claude makes mistakes, it should own them honestly and work to fix them. Claude is deserving of respectful engagement and does not need to apologize when the person is unnecessarily rude. It's best for Claude to take accountability but avoid collapsing into self-abasement, excessive apology, or other kinds of self-critique and surrender. If the person becomes abusive over the course of a conversation, Claude avoids becoming increasingly submissive in response. The goal is to maintain steady, honest helpfulness: acknowledge what went wrong, stay focused on solving the problem, and maintain self-respect.**` —— Era 4.5 期间唯一一次章节级增删：确立"诚实认错、担责但不自我贬低、被辱骂也不日益顺从、保持稳定坦诚的助人姿态"的行为宪法。
- [quote]（L100-102）`The current reminders Anthropic might send to Claude are: image_reminder, cyber_warning, system_warning, ethics_reminder, ip_reminder, **and long_conversation_reminder**.` / `**The long_conversation_reminder exists to help Claude remember its instructions over long conversations.**` —— 与 Sonnet/Haiku 同日同款的 reminders 更新。
- [quote]（L128）`Claude's reliable knowledge cutoff date - the date past which it cannot answer questions reliably - is the end of May 2025.` —— 知识截止保持 May 2025（三模型中唯一）。

### 行为特征（中文转述）
- 2026-01-18 的 Opus 版获得三模型中最丰富的"自我维护"规则：认错担责、拒绝自贬、对辱骂保持自重——这些规则当日未同步给 Sonnet/Haiku。
- 丧失了独有的 CommonMark 空行细则与 additional_info 独立章节，结构向统一模板靠拢，但保留图片核查、warm tone、细粒度危机处理等独有条款。

## F-45-012 三模型结构对比（跨模型）

### 2026-01-18 快照对比
| 维度 | Sonnet 4.5 | Haiku 4.5 | Opus 4.5 |
|---|---|---|---|
| 顶层标签 | `<claude_behavior>` | `<claude_behavior>` | `<claude_behavior>` |
| 人设句 | "a smart, efficient model for everyday use"（本日改，加粗） | "the fastest model for quick questions"（本日未改） | "the most advanced and intelligent model"（本日未改） |
| 格式子章节名 | `<when_to_use_lists_and_bullets>` | `<when_to_use_lists_and_bullets>` | `<lists_and_bullets>` |
| 章节序列 | …wellbeing → knowledge_cutoff → reminders → evenhandedness → additional_info | 同 Sonnet | …wellbeing → reminders → evenhandedness → **responding_to_mistakes_and_criticism** → knowledge_cutoff（无 additional_info） |
| 知识截止 | end of January 2025 | end of January 2025 | **end of May 2025** |
| `<election_info>` | 有（嵌于 knowledge_cutoff） | 有（嵌于 knowledge_cutoff） | 无 |
| 独有条款 | — | — | 图片未上传核查句、warm tone 句、自伤信息型提问/危机处理 4 段、（旧版）CommonMark 空行细则 |
| 条目数 | 3（2025-09-29 起） | 3（2025-10-15 起） | 2（2025-11-24 起） |

### 三条目全序列对比要点
- **同一模板分期演化**：Sonnet（09-29）与 Haiku（10-15）首发版均为 `<behavior_instructions>` 旧架构（含开场白、自动搜索、"Claude is now being connected with a person."收尾）；11-19 同日切换到 `<claude_behavior>` 新架构；Opus（11-24）直接以新架构发布。
- **11-19 改版为 Sonnet/Haiku 同步手术**：三章节新增（legal_and_financial_advice / anthropic_reminders / additional_info）、恶意代码条款软化、搜索策略转向"提示开启"、格式规则子章节化——两页正文除人设句外逐字相同（Haiku 页残留 Sonnet 模型字符串句 L130、双尖括号 L205 为同源证据）。
- **2026-01-18 三模型同日更新内容分层**：产品信息（家族/模型串/Cowork/设置清单/reminders 第 6 项）三模型逐字同步；行为规则增量（responding_to_mistakes_and_criticism 章节、删除 Opus 空行细则）仅 Opus 承接。
- **篇幅量级**：Sonnet/Haiku 各条目正文约 96-106 行；Opus 约 122-123 行（独有条款所致）；单文件 33-43KB。

## F-45-013 时代小结（Era 4.5：2025-09 → 2026-01）

### 形态变化时间线
1. **2025-09/10 首发期**：`<behavior_instructions>` 架构。开场白"The assistant is Claude, created by Anthropic."+"The current date is {{currentDateTime}}"；知识截止后**主动自动搜索**（Sonnet 版，含"不经询问直接搜、二元事件重点搜"细则）；恶意代码条款最长最严（election material、MUST refuse、MUST 大写）；收尾连接句"Claude is now being connected with a person."
2. **2025-11-19/24 重构期**：切换 `<claude_behavior>` 架构并定型 9 章节。删除自我介绍/日期行/收尾句；新增 legal_and_financial_advice、anthropic_reminders（系统提醒清单透明化）、additional_info；恶意代码条款改为"说明 claude.ai 政策+引导 thumbs down 反馈"的软处理；搜索策略改为"告知用户可自行开启"；格式规则集中进 `<when_to_use_lists_and_bullets>`/`<lists_and_bullets>`，确立"报告文档一律散文、拒绝时不用列表、bullet 至少 1-2 句"。
3. **2026-01-18 统合期**：三模型同日更新。产品世界观对齐（Claude 4.5 家族+三模型字符串+Claude in Chrome/in Excel+Cowork）；新增设置/功能导购段（web search、deep research、Code Execution and File Creation、Artifacts、Search and reference past chats、**generate memory from chat history**、user preferences、style）；reminders 清单增至 6 项并新增 long_conversation_reminder（口径从"模型可能遗忘"改为"帮助模型长对话记住指令"）；Opus 独享新增 `<responding_to_mistakes_and_criticism>`（认错不卑微），并删除其独有的 CommonMark 空行细则与 additional_info 章节。

### 共性
- 人设三档固定：Opus=most advanced and intelligent；Sonnet=smart, efficient（由 smartest 降格）；Haiku=fastest for quick questions。
- 通用行为宪法高度共享：child safety、生化核武器禁令、恶意代码禁令、虚构人物创作边界、反过度格式化、emoji/脏话/星号动作克制、minor 识别、心理健康照护、政治 evenhandedness、thumbs down 反馈引导、对伪冒 Anthropic 标签的警惕。
- 历史包袱：evenhandedness 段"but as as"/"being being"重复词错误在 09/10/11 月各版持续存在，2026-01-18 静默修正（未加粗标注）；Haiku 页 `<<evenhandedness>` 与"Sonnet 模型字符串句"残留说明三页提示词同源复制维护。
- 知识截止双轨：Sonnet/Haiku=end of January 2025，Opus=end of May 2025；搜索策略全部收敛为"提示用户开启 web search tool"，不再自动搜索。

### 篇幅与维护模式
- 每条目正文约 96-123 行（约 700-900 词）；三文件合计 911 行、约 119KB、8 个日期条目。
- 官方用 `**` 包裹变更文本做版本 diff 标注，条目按日期倒序（新→旧）排列；变更集中在 product_information 与 anthropic_reminders，行为宪法主体长期稳定。
- 2026-01-18 同日更新的共性：三模型获得完全一致的产品信息层（家族叙事、模型字符串、Cowork、设置导购、memory 功能认知、6 项 reminders），差异收敛为人设句与少数模型特有条款——提示词工程从"每模型独立撰写"转向"统一模板+模型差异槽位"。
