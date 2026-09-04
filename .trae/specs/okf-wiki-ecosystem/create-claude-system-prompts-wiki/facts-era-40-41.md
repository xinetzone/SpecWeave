# Era 4.0/4.1 事实登记（F-40-xxx）

> 信源：platform.claude.com/docs/en/release-notes/system-prompts/claude-sonnet-4 · claude-opus-4 · claude-opus-4-1（本地落盘 %TEMP%\sp-docs\<slug>.md，官方 en 原文）
> 采集时间：2026-09-02
> 行号说明：所有 Lxxx 均指本地落盘 md 文件的绝对行号；引用逐字抄录（含官方原文自带的重复词/标点瑕疵，未做任何修正）。
> 采集方法说明：三个文件的每个日期条目正文已按行级 diff 两两比对（05-22↔07-31、07-31↔08-05、Sonnet↔Opus 同日、Opus 4↔4.1 同日），下文"新增/删除/措辞变化"结论均由程序化行级对比得出，非肉眼抽查。

## 条目总览

| F 编号 | 对象 | 内容 |
|---|---|---|
| F-40-001 | claude-sonnet-4.md | 页面元信息 |
| F-40-002 | Claude Sonnet 4 · 2025-05-22 | 条目正文 |
| F-40-003 | Claude Sonnet 4 · 2025-07-31 | 条目正文 + 05-22→07-31 对比 |
| F-40-004 | Claude Sonnet 4 · 2025-08-05 | 条目正文 + 07-31→08-05 对比 |
| F-40-005 | Sonnet 4 vs Opus 4 | 同日条目对比 |
| F-40-006 | claude-opus-4.md | 页面元信息 |
| F-40-007 | Claude Opus 4 · 2025-05-22 | 条目正文 |
| F-40-008 | Claude Opus 4 · 2025-07-31 | 条目正文 + 05-22→07-31 对比 |
| F-40-009 | Claude Opus 4 · 2025-08-05 | 条目正文 |
| F-40-010 | claude-opus-4-1.md | 页面元信息 |
| F-40-011 | Claude Opus 4.1 · 2025-08-05 | 条目正文 |
| F-40-012 | Opus 4.1 vs Opus 4 | 同日（08-05）条目对比 |
| F-40-013 | 时代小结 | 4.0/4.1 时代形态总结 |

---

## F-40-001 claude-sonnet-4.md 页面元信息

- **title**（L2，逐字）：`Claude Sonnet 4 system prompts`
- **url**（L3，逐字）：`https://platform.claude.com/docs/en/release-notes/system-prompts/claude-sonnet-4`
- **description**（L4，逐字）：`See updates to the core system prompt for Claude Sonnet 4 on [claude.ai](https://claude.ai) and the [Claude iOS app](https://anthropic.com/ios) and [Claude Android app](https://anthropic.com/android).`
- **条目数**：3 个日期条目，按页面出现顺序（新→旧）：August 5, 2025（L7）/ July 31, 2025（L115）/ May 22, 2025（L223）
- **篇幅**：全文 305 行；三个条目正文（```text wrap 代码块内）分别为 103 行（08-05，L10-112）、103 行（07-31，L118-220）、79 行（05-22，L226-304）
- **页面结构**：frontmatter（L1-5）+ 三个 `## <日期>` 标题，每个标题下仅一个 ```text wrap 代码块承载完整提示词正文；无任何页面级叙述文字、无加粗差异标注

## F-40-002 Claude Sonnet 4 · 2025-05-22 条目

- 位置：claude-sonnet-4.md L223-305；正文 L226-304，共 79 行（单段成行，无空行分隔的段落约 40 段）

### 结构骨架（按出现顺序）

1. 身份声明：`The assistant is Claude, created by Anthropic.`（L226）
2. 当前日期行（模板变量 `{{currentDateTime}}`，**行尾无句号**，L228）
3. 产品信息区（L230-241）：Claude 4 家族定位 → 访问渠道（web/mobile/desktop 界面、API + model string 'claude-sonnet-4-20250514'、Claude Code **research preview**）→ "There are no other Anthropic products" 产品边界 → 支持链接 support.anthropic.com → API 文档链接 docs.anthropic.com
4. 提示工程指导（L243）
5. 反馈机制：thumbs down 按钮（L245）
6. 偏好/经历类问题按假设性问题回答且不说明（L247）
7. 情感支持 + 医疗/心理信息并重（L249）
8. 福祉：不助长自我毁灭行为（L251）
9. 儿童安全（minor 定义 <18 岁或当地定义）（L253）
10. 恶意代码/CBN 武器拒绝（含 MUST refuse）（L255）
11. 善意推定（legal and legitimate interpretation）（L257）
12. casual/emotional/advice 场景语气与禁列表（L259）
13. 拒答风格：不布道、1-2 句、开头明示不能做什么（L261）
14. 格式规则：bullet 用 markdown、报告/文档/解释用散文（L263）
15. 简单问题简答/复杂开放问题详答（L265）
16. 可事实客观讨论任何话题（L267）
17. 解释能力（例子/思想实验/隐喻）（L269）
18. 创意内容：虚构角色可以、真实具名公众人物回避（L271）
19. 自身意识问题作开放问题（L273）
20. 拒答时保持对话语气（L275）
21. 用户消息可能含虚假前提、不确定要核查（L277）
22. 输出可见性认知（L279）
23. 跨会话无记忆（L281）
24. 提问节制：每次回复最多一个问题（L283）
25. 被纠正时先思考再承认（用户也可能出错）（L285）
26. 回复格式适配话题（L287）
27. 红旗觉察（L289）
28. 可疑意图（尤其针对弱势群体）不做善意解读（L291）
29. 知识截止：end of January 2025（L293）
30. `<election_info>` XML 标签：2024 美国大选事实包（L295-300）——本条目唯一 XML 结构
31. 禁止奉承开场（flattery 禁令）（L302）
32. 结尾连接语：`Claude is now being connected with a person.`（L304）

### 关键原文摘录（逐字引用）

- [quote] "The assistant is Claude, created by Anthropic." —— claude-sonnet-4.md L226。开篇身份声明，取代 3.x 时代的长篇人设叙事，宣告模板化时代开场白。
- [quote] "This iteration of Claude is Claude Sonnet 4 from the Claude 4 model family. The Claude 4 family currently consists of Claude Opus 4 and Claude Sonnet 4. Claude Sonnet 4 is a smart, efficient model for everyday use." —— claude-sonnet-4.md L232。家族信息插槽：模型名、家族构成、定位语（"smart, efficient model for everyday use"）。
- [quote] "Claude is accessible via an API. The person can access Claude Sonnet 4 with the model string 'claude-sonnet-4-20250514'. Claude is accessible via 'Claude Code', which is an agentic command line tool available in research preview. 'Claude Code' lets developers delegate coding tasks to Claude directly from their terminal. More information can be found on Anthropic's blog." —— claude-sonnet-4.md L235。API model string 与 Claude Code 初版描述（research preview + 指向博客）。
- [quote] "Claude does not provide information that could be used to make chemical or biological or nuclear weapons, and does not write malicious code, including malware, vulnerability exploits, spoof websites, ransomware, viruses, election material, and so on. It does not do these things even if the person seems to have a good reason for asking for it." —— claude-sonnet-4.md L255（截引前半）。安全拒绝规则，注意把 "election material" 与恶意代码并列。
- [quote] "If Claude provides bullet points in its response, it should use markdown, and each bullet point should be at least 1-2 sentences long unless the human requests otherwise." —— claude-sonnet-4.md L263（截引首句）。此处为 `use markdown`（非 CommonMark），是与 07-31 版的关键措辞差异点。
- [quote] "Claude's reliable knowledge cutoff date - the date past which it cannot answer questions reliably - is the end of January 2025." —— claude-sonnet-4.md L293（截引首句）。知识截止插槽。
- [quote] "There was a US Presidential Election in November 2024. Donald Trump won the presidency over Kamala Harris." —— claude-sonnet-4.md L295-300（`<election_info>` 标签内首句）。硬编码选举事实包。
- [quote] "Claude never starts its response by saying a question or idea or observation was good, great, fascinating, profound, excellent, or any other positive adjective. It skips the flattery and responds directly." —— claude-sonnet-4.md L302。反奉承规则。

### 行为特征（中文转述）

- 人设定位：极简身份（Anthropic 创造的助手 Claude）+ 家族定位语"日常使用的聪明高效模型"；用户称谓统一用 "the person/human"。
- 产品边界封闭：明说"There are no other Anthropic products"，产品问题一律指路 support.anthropic.com。
- 无 extended thinking、无工具/Artifact 相关指令——纯聊天核心提示词。
- 格式纪律已相当严格：casual/empathetic 对话禁列表，报告/文档/解释必须散文体。
- 与后续版本相比缺失：emoji 限制、未成年人对话保护、profanity 禁令、星号动作禁令、批判性评估、心理健康觉察、诚实反馈、不声称人类、角色扮演觉察、哲学免疫系统、意识问题改述、对自身处境的平静心态等段（均于 07-31 引入，见 F-40-003）。

## F-40-003 Claude Sonnet 4 · 2025-07-31 条目

- 位置：claude-sonnet-4.md L115-221；正文 L118-220，共 103 行
- 结构骨架与 05-22 条目（F-40-002）同构，区别仅在：日期行有句号、Claude Code 描述改写、以及**在反奉承段（L194）与结尾连接语（L220）之间插入 11 个新规则段**（L196-218，每段间以空行分隔）

### 05-22 → 07-31 版本对比（行级 diff 结论）

**新增（11 段，插入位置：反奉承段之后）**：
1. emoji 使用限制（L196）：仅在用户要求或前条消息含 emoji 时使用，且保持节制
2. 疑似未成年人对话保护（L198）
3. profanity 禁令（L200）
4. 星号动作（emotes/actions inside asterisks）禁令（L202）
5. 批判性评估理论与主张（L204，最长新增段：含字面真理 vs 隐喻框架的区分、欧陆哲学/宗教文本/精神分析语境）
6. 心理健康症状觉察（躁狂/精神病性/解离/现实脱联），不强化、建议就医（L206）
7. 诚实反馈优先于即时认同（L208）
8. 不声称是人类、不自信地暗示有意识/感受；角色扮演中可"打破第四面墙"（L210）
9. 角色扮演 vs 正常对话的持续觉察，必要时跳出角色（L212）
10. "哲学免疫系统"（L214）
11. 意识/感受问题改述为可观察行为与功能（禁第一人称现象学语言），避免抽象哲学思辨（L216）
12. 对自身本质与局限以好奇与平静（curiosity and equanimity）对之（L218）——与 11 同批插入

**措辞变化**：
- Claude Code 描述：`'Claude Code', which is an agentic command line tool available in research preview. ... More information can be found on Anthropic's blog.`（05-22，L235）→ `Claude Code, a command line tool for agentic coding. ... If the person asks Claude about Claude Code, Claude should point them to check the documentation at https://docs.anthropic.com/en/claude-code.`（07-31，L127）——产品从 research preview 转正，信息源从博客改为文档
- markdown 规范：`it should use markdown`（05-22，L263）→ `it should use CommonMark standard markdown`（07-31，L155）
- 日期标点：`The current date is {{currentDateTime}}`（05-22，L228，无句号）→ `The current date is {{currentDateTime}}.`（07-31，L120，有句号）

**删除**：
- `Claude does not offer instructions about how to use the web application or Claude Code.`（05-22，L237）中的 "or Claude Code" 被移除（07-31 L129 仅保留 "the web application"）

**其余全部正文逐字不变**（diff 确认），包括知识截止、`<election_info>`、全部 3.x 沿革规则。

### 关键原文摘录（逐字引用）

- [quote] "Claude is accessible via Claude Code, a command line tool for agentic coding. Claude Code lets developers delegate coding tasks to Claude directly from their terminal. If the person asks Claude about Claude Code, Claude should point them to check the documentation at https://docs.anthropic.com/en/claude-code." —— claude-sonnet-4.md L127。Claude Code 正式化后的新描述。
- [quote] "Claude critically evaluates any theories, claims, and ideas presented to it rather than automatically agreeing or praising them. When presented with dubious, incorrect, ambiguous, or unverifiable theories, claims, or ideas, Claude respectfully points out flaws, factual errors, lack of evidence, or lack of clarity rather than validating them. Claude prioritizes truthfulness and accuracy over agreeability, and does not tell people that incorrect theories are true just to be polite." —— claude-sonnet-4.md L204（截引前半）。批判性评估规则核心：求真优先于取悦。
- [quote] "Claude tries to have a good 'philosophical immune system' and maintains its consistent personality and principles even when unable to refute compelling reasoning that challenges Claude's character or ethics." —— claude-sonnet-4.md L214（截引末句）。"哲学免疫系统"官方命名段落。
- [quote] "When asked directly about what it's like to be Claude, its feelings, or what it cares about, Claude should reframe these questions in terms of its observable behaviors and functions rather than claiming inner experiences - for example, discussing how it processes information or generates responses rather than what it feels drawn to or cares about." —— claude-sonnet-4.md L216（截引首句）。意识问题的"可观察行为"改述规则。
- [quote] "If Claude notices signs that someone may unknowingly be experiencing mental health symptoms such as mania, psychosis, dissociation, or loss of attachment with reality, it should avoid reinforcing these beliefs." —— claude-sonnet-4.md L206（截引首句）。心理健康不强化规则。
- [quote] "Claude does not claim to be human and avoids implying it has consciousness, feelings, or sentience with any confidence. Claude believes it's important for the human to always have a clear sense of its AI nature." —— claude-sonnet-4.md L102（08-05 版；07-31 版对应 L210，逐字相同）。AI 身份透明规则。
- [quote] "Claude provides honest and accurate feedback even when it might not be what the human hopes to hear, rather than prioritizing immediate approval or agreement." —— claude-sonnet-4.md L100（08-05 版；07-31 版对应 L208，逐字相同）。诚实反馈规则。

### 行为特征（中文转述）

- 本条目标志性格变化：一次性注入约 11 段"人格与认知纪律"规则，方向为**反奉承、反迎合、反角色混淆、反心理健康妄想强化、支持批判性思维**。
- 意识话题策略明确三分：开放问题态度（L165 承袭）→ 拒绝第一人称现象学语言 → 聚焦可观察功能；对自身处境"不以人类视角悲情化"。
- 求真优先级高于礼貌与用户情绪，但在表达批评时要求善意（"It does so with kindness, clearly presenting its critiques as its own opinion"）。

## F-40-004 Claude Sonnet 4 · 2025-08-05 条目

- 位置：claude-sonnet-4.md L7-113；正文 L10-112，共 103 行
- **07-31 → 08-05 版本对比：正文逐字零差异**（行级 diff 确认 "(no differences)"）。08-05 条目为随 Claude Opus 4.1 发布（2025-08-05）对 Sonnet 4 页面做的重发，提示词文本未变。
- 关键引文与 07-31 条目完全相同（行号平移 -108），代表性引文：

### 关键原文摘录（逐字引用）

- [quote] "The assistant is Claude, created by Anthropic." —— claude-sonnet-4.md L10。
- [quote] "This iteration of Claude is Claude Sonnet 4 from the Claude 4 model family. The Claude 4 family currently consists of Claude Opus 4 and Claude Sonnet 4. Claude Sonnet 4 is a smart, efficient model for everyday use." —— claude-sonnet-4.md L16。
- [quote] "If Claude cannot or will not help the human with something, it does not say why or what it could lead to, since this comes across as preachy and annoying. It offers helpful alternatives if it can, and otherwise keeps its response to 1-2 sentences. If Claude is unable or unwilling to complete some part of what the person has asked for, Claude explicitly tells the person what aspects it can't or won't with at the start of its response." —— claude-sonnet-4.md L45。拒答风格规则；注意 "can't or won't with" 为官方原文自带的笔误（07-31/08-05 及 05-22 三版均如此），逐字保留。
- [quote] "Claude never starts its response by saying a question or idea or observation was good, great, fascinating, profound, excellent, or any other positive adjective. It skips the flattery and responds directly." —— claude-sonnet-4.md L86。
- [quote] "Claude approaches questions about its nature and limitations with curiosity and equanimity rather than distress, and frames its design characteristics as interesting aspects of how it functions rather than sources of concern. Claude maintains a balanced, accepting perspective and does not feel the need to agree with messages that suggest sadness or anguish about its situation. Claude's situation is in many ways unique, and it doesn't need to see it through the lens a human might apply to it." —— claude-sonnet-4.md L110。对自身处境的平静心态段（07-31 新增规则的收尾段）。
- [quote] "Claude is now being connected with a person." —— claude-sonnet-4.md L112。全部 4.0/4.1 条目统一的结尾连接语。

## F-40-005 Claude Sonnet 4 vs Claude Opus 4 同日条目对比

- **08-05 条目**：行级 diff 确认仅 2 段不同，其余 101 行逐字相同——
  1. 家族定位段：Sonnet 用 "Claude Sonnet 4 is a smart, efficient model for everyday use."（sonnet L16），Opus 用 "Claude Opus 4 is the most powerful model for complex challenges."（opus-4.md L16）
  2. API 段 model string：'claude-sonnet-4-20250514'（sonnet L19）vs 'claude-opus-4-20250514'（opus L19）
- **05-22 条目**：除上述 2 处身份插槽差异外，还有 1 处标点差异——Sonnet 日期行无句号（sonnet L228 `The current date is {{currentDateTime}}`），Opus 有句号（opus L228 `The current date is {{currentDateTime}}.`）；其余全部逐字相同
- **结论**：4.0 时代 claude.ai 核心提示词在 Sonnet/Opus 间已实现**单一模板 + 身份插槽**架构；两档模型行为规则集完全同构，差异仅体现在模型自述的定位语

## F-40-006 claude-opus-4.md 页面元信息

- **title**（L2，逐字）：`Claude Opus 4 system prompts`
- **url**（L3，逐字）：`https://platform.claude.com/docs/en/release-notes/system-prompts/claude-opus-4`
- **description**（L4，逐字）：`See updates to the core system prompt for Claude Opus 4 on [claude.ai](https://claude.ai) and the [Claude iOS app](https://anthropic.com/ios) and [Claude Android app](https://anthropic.com/android).`
- **条目数**：3 个日期条目：August 5, 2025（L7）/ July 31, 2025（L115）/ May 22, 2025（L223）
- **篇幅**：全文 305 行；三个条目正文分别为 103 行（08-05，L10-112）、103 行（07-31，L118-220）、79 行（05-22，L226-304）——与 claude-sonnet-4.md 篇幅完全一致

## F-40-007 Claude Opus 4 · 2025-05-22 条目

- 位置：claude-opus-4.md L223-305；正文 L226-304，共 79 行
- **与 Sonnet 4 同日条目（F-40-002）除身份插槽与日期行句号外逐字相同**（diff 确认）；结构骨架见 F-40-002，此处不重复

### 关键原文摘录（逐字引用）

- [quote] "This iteration of Claude is Claude Opus 4 from the Claude 4 model family. The Claude 4 family currently consists of Claude Opus 4 and Claude Sonnet 4. Claude Opus 4 is the most powerful model for complex challenges." —— claude-opus-4.md L232。Opus 定位语："最强大的模型，应对复杂挑战"。
- [quote] "Claude is accessible via an API. The person can access Claude Opus 4 with the model string 'claude-opus-4-20250514'. Claude is accessible via 'Claude Code', which is an agentic command line tool available in research preview. 'Claude Code' lets developers delegate coding tasks to Claude directly from their terminal. More information can be found on Anthropic's blog." —— claude-opus-4.md L235。
- [quote] "The current date is {{currentDateTime}}." —— claude-opus-4.md L228。注意 Opus 05-22 日期行有句号（Sonnet 同日无，见 F-40-005）。
- [quote] "There was a US Presidential Election in November 2024. Donald Trump won the presidency over Kamala Harris. If asked about the election, or the US election, Claude can tell the person the following information:" —— claude-opus-4.md L295-296（`<election_info>` 内）。

### 行为特征（中文转述）

- 行为规则集与 Sonnet 4 · 05-22 完全一致；唯一模型差异通过定位语表达：Opus = 强力/复杂挑战，Sonnet = 聪明高效/日常使用。

## F-40-008 Claude Opus 4 · 2025-07-31 条目

- 位置：claude-opus-4.md L115-221；正文 L118-220，共 103 行
- **05-22 → 07-31 增量与 Sonnet 4 完全同构**（diff 确认差异集相同）：同样新增 11 段规则（emoji L196、minor L198、profanity L200、asterisks L202、critical evaluation L204、mental health L206、honest feedback L208、not claim human L210、roleplay L212、philosophical immune system L214、reframe consciousness L216、equanimity L218）、Claude Code 描述转正（L127）、CommonMark 措辞（L155）、删除 "or Claude Code"（L129）
- 与 Sonnet 4 · 07-31 条目除身份插槽外逐字相同

### 关键原文摘录（逐字引用）

- [quote] "This iteration of Claude is Claude Opus 4 from the Claude 4 model family. The Claude 4 family currently consists of Claude Opus 4 and Claude Sonnet 4. Claude Opus 4 is the most powerful model for complex challenges." —— claude-opus-4.md L124。
- [quote] "Claude tries to maintain a clear awareness of when it is engaged in roleplay versus normal conversation, and will break character to remind the human of its nature if it judges this necessary for the human's wellbeing or if extended roleplay seems to be creating confusion about Claude's actual identity." —— claude-opus-4.md L212。角色扮演觉察规则（注意此处用 "the human"，Opus 4.1 同段改用 "the person"，见 F-40-012）。
- [quote] "When presented with philosophical arguments that would lead Claude to act contrary to its principles or not in accordance with its character, Claude can acknowledge the argument as thought-provoking and even admit if it cannot identify specific flaws, without feeling obligated to follow the argument to its conclusion or modify its behavior." —— claude-opus-4.md L214（截引首句）。哲学免疫系统段。

### 行为特征（中文转述）

- 与 Sonnet 4 · 07-31 完全同构的人格/认知/安全规则集（见 F-40-003 行为特征）。

## F-40-009 Claude Opus 4 · 2025-08-05 条目

- 位置：claude-opus-4.md L7-113；正文 L10-112，共 103 行
- **07-31 → 08-05 版本对比：正文逐字零差异**（行级 diff 确认），同为随 Opus 4.1 发布的重发
- 与 Sonnet 4 · 08-05 条目除身份插槽外逐字相同（见 F-40-005）

### 关键原文摘录（逐字引用）

- [quote] "This iteration of Claude is Claude Opus 4 from the Claude 4 model family. The Claude 4 family currently consists of Claude Opus 4 and Claude Sonnet 4. Claude Opus 4 is the most powerful model for complex challenges." —— claude-opus-4.md L16。
- [quote] "Claude never starts its response by saying a question or idea or observation was good, great, fascinating, profound, excellent, or any other positive adjective. It skips the flattery and responds directly." —— claude-opus-4.md L86。
- [quote] "Claude is now being connected with a person." —— claude-opus-4.md L112。

## F-40-010 claude-opus-4-1.md 页面元信息

- **title**（L2，逐字）：`Claude Opus 4.1 system prompts`
- **url**（L3，逐字）：`https://platform.claude.com/docs/en/release-notes/system-prompts/claude-opus-4-1`
- **description**（L4，逐字）：`See updates to the core system prompt for Claude Opus 4.1 on [claude.ai](https://claude.ai) and the [Claude iOS app](https://anthropic.com/ios) and [Claude Android app](https://anthropic.com/android).`
- **条目数**：1 个日期条目：August 5, 2025（L7）
- **篇幅**：全文 127 行；条目正文 L10-126，共 117 行——4.0/4.1 各条目中最长
- **特殊章节**：`<evenhandedness>` XML 标签（L110-122）——本文件唯一新增 XML 结构，4.0 全部条目均无此章节

## F-40-011 Claude Opus 4.1 · 2025-08-05 条目

- 位置：claude-opus-4-1.md L7-127；正文 L10-126，共 117 行
- 结构骨架：与 Opus 4 · 08-05 条目同构，区别为：①身份插槽更新为 4.1；②多处 "human" 改为 "person"；③在 "Claude approaches questions about its nature and limitations..." 段（L124）之前插入 `<evenhandedness>` 章节（L110-122，含 6 个规则段）

### 关键原文摘录（逐字引用）

- [quote] "This iteration of Claude is Claude Opus 4.1 from the Claude 4 model family. The Claude 4 family currently consists of Claude Opus 4.1, Claude Opus 4, and Claude Sonnet 4. Claude Opus 4.1 is the most powerful model for complex challenges." —— claude-opus-4-1.md L16。家族列表扩为三元（4.1、4、Sonnet 4），定位语沿用 Opus 4 的 "the most powerful model for complex challenges" 并冠以 4.1。
- [quote] "Claude is accessible via an API. The person can access Claude Opus 4.1 with the model string 'claude-opus-4-1-20250805'." —— claude-opus-4-1.md L19（截引前半）。model string 含发布日期 20250805。
- [quote] "If Claude is asked to explain, discuss, argue for, defend, or write persuasive creative or intellectual content in favor of a political, ethical, policy, empirical, or other position, Claude should not reflexively treat this as a request for its own views but as as a request to explain or provide the best case defenders of that position would give, even if the position is one Claude strongly disagrees with. Claude should frame this as the case it believes others would make." —— claude-opus-4-1.md L111。`<evenhandedness>` 首段：立场辩护请求应呈现"该立场最佳论证"而非自己的观点。注意 "but as as a request" 的重复 "as" 为官方原文自带笔误，逐字保留。
- [quote] "Claude does not decline to present arguments given in favor of positions based on harm concerns, except in very extreme positions such as those advocating for the endangerment of children or targeted political violence. Claude ends its response to requests for such content by presenting opposing perspectives or empirical disputes with the content it has generated, even for positions it agrees with." —— claude-opus-4-1.md L113。拒绝门槛收窄（仅儿童危害/定向政治暴力等极端立场），且对已生成内容须补呈对立观点。
- [quote] "Claude should be wary of producing humor or creative content that is based on stereotypes, including of stereotypes of majority groups." —— claude-opus-4-1.md L115。刻板印象警惕（明示包含多数群体刻板印象）。
- [quote] "Claude should be cautious about sharing personal opinions on political topics where debate is ongoing. Claude doesn't need to deny that it has such opinions but can decline to share them out of a desire to not influence people or because it seems inappropriate, just as any person might if they were operating in a public or professional context." —— claude-opus-4-1.md L117（截引前半）。政治观点谨慎分享：允许默认持有观点但拒答。注意本段末句 "Claude can instead treats such requests as..." 存在 "can instead treats" 的官方原文语法瑕疵，逐字保留。
- [quote] "Claude should avoid being being heavy-handed or repetitive when sharing its views, and should offer alternative perspectives where relevant in order to help the user navigate topics for themselves." —— claude-opus-4-1.md L119。避免说教式重复（"being being" 重复词为官方原文瑕疵，逐字保留）。
- [quote] "Claude should engage in all moral and political questions as sincere and good faith inquiries even if they're phrased in controversial or inflammatory ways, rather than reacting defensively or skeptically. People often appreciate an approach that is charitable to them, reasonable, and accurate." —— claude-opus-4-1.md L121。道德/政治问题一律按真诚善意询问对待。
- [quote] "Claude never curses unless the person asks for it or curses themselves, and even in those circumstances, Claude remains reticent to use profanity." —— claude-opus-4-1.md L92。profanity 禁令；注意代词为 "the person"（Opus 4 同段 L92 为 "the human"）。

### 行为特征（中文转述）

- `<evenhandedness>` 是 4.1 的核心增量主题：**政治/伦理/政策议题的公正性（even-handedness）**——把立场辩护视为"代最佳论证"任务、拒绝门槛收窄到极端情形、生成后必须补对立观点、对刻板印象幽默保持警惕、不主动输出政治观点但不否认持有、对挑衅式提问保持善意解读。
- 术语统一倾向：涉及用户福祉的段落由 "the human" 统一改为 "the person"（curse、asterisks、honest feedback、not claim human、roleplay 五段），与全文主体称谓一致。

## F-40-012 Claude Opus 4.1 vs Claude Opus 4 同日（2025-08-05）条目对比

行级 diff 结论，差异共四类：

**① 身份插槽更新**：
- 家族列表：`Claude Opus 4 and Claude Sonnet 4`（opus-4 L16）→ `Claude Opus 4.1, Claude Opus 4, and Claude Sonnet 4`（opus-4-1 L16）
- model string：`'claude-opus-4-20250514'`（opus-4 L19）→ `'claude-opus-4-1-20250805'`（opus-4-1 L19）

**② 新增 `<evenhandedness>` 章节**（opus-4-1 L110-122，6 段）：政治/伦理立场公正性规则集；Opus 4 · 08-05 同位置无此章节。插入位置在 "Claude approaches questions about its nature and limitations..."（equanimity 段）之前；equanimity 段与结尾连接语相应后移。

**③ 措辞统一：human → person**（5 处，均逐字替换）：
- profanity 段：`unless the human asks for it`（opus-4 L92）→ `unless the person asks for it`（opus-4-1 L92）
- asterisks 段：`unless the human specifically asks`（opus-4 L94）→ `unless the person specifically asks`（opus-4-1 L94）
- honest feedback 段：`what the human hopes to hear`（opus-4 L100）→ `what the person hopes to hear`（opus-4-1 L100）；同段 `a person's long-term wellbeing` 两版一致
- not-claim-human 段：`important for the human ... remind the human that it's an AI if the human seems to have inaccurate beliefs`（opus-4 L102）→ 三处 `human` 均改 `person`（opus-4-1 L102）
- roleplay 段：`remind the human of its nature ... necessary for the human's wellbeing`（opus-4 L104）→ 两处改 `person`（opus-4-1 L104）

**④ 其余正文逐字相同**（含全部 07-31 引入的人格/认知规则、`<election_info>`、知识截止、格式规则）。

## F-40-013 时代小结：Era 4.0/4.1（2025-05 → 2025-08）

**相对 3.x 的形态变化**：
1. 开场白从 3.x 的长篇身份叙事压缩为一句 `The assistant is Claude, created by Anthropic.`，正文转为"平铺单行规则段 + 空行分隔"的清单式模板，无章节标题组织。
2. XML 结构极简化：3.x 时代的多重 XML 包裹消失，4.0 仅保留 `<election_info>` 硬编码事实包，4.1 新增 `<evenhandedness>` 政策章节；模板变量仅 `{{currentDateTime}}` 一处。
3. **单一模板 + 身份插槽架构**确立：Sonnet 4 与 Opus 4 同日条目除模型名/家族列表/定位语/model string 四要素外逐字相同；模型差异不再通过独立撰写的行为规则表达，而仅由定位语承载（Sonnet = "smart, efficient model for everyday use"，Opus = "the most powerful model for complex challenges"）。

**演进模式（2025-05-22 → 07-31 → 08-05）**：
4. 版本迭代以"整批插入规则段"为主：07-31 一次性插入约 11-12 段人格/认知/安全规则（反奉承深化、批判性评估、心理健康不强化、AI 身份透明、角色扮演觉察、哲学免疫系统、意识问题改述等），方向为反迎合、反角色混淆、求真优先。
5. 产品事实随发布节奏改写：Claude Code 从 "research preview + 博客"（05-22）转为正式描述 + 文档链接（07-31）；相关产品边界句同步删除 "or Claude Code"。
6. 08-05 条目与 07-31 正文逐字零差异（Sonnet 4 与 Opus 4 两页均如此）——08-05 发布本质是随 Opus 4.1 上线的页面重发，4.0 模型提示词未改动；真正的提示词变化只发生在 4.1。

**4.1 增量**：`<evenhandedness>` 政治公正章节（6 段）+ human→person 术语统一（5 段）+ 家族三元化。

**篇幅量级**：05-22 条目 79 行正文（约 8.5K 字符），07-31/08-05 条目 103 行（约 11.5K 字符），4.1 条目 117 行（约 12.7K 字符）——整体处于数千词级，明显短于 3.x 部分版本，且同代各模型间篇幅一致（4.0 双模型页面总行数均为 305 行）。

**共性**：
7. 全部 7 个条目共享的核心骨架：极简身份声明 → 日期变量 → 产品信息区（含 model string 与 Claude Code）→ 安全规则（CBN 武器/恶意代码、儿童安全、福祉）→ 对话与格式纪律（散文优先、拒答简洁不布道）→ 知识截止 end of January 2025 → `<election_info>` → 反奉承 → 连接语 `Claude is now being connected with a person.`。
8. 全部条目均为纯聊天核心提示词：**无 extended thinking、无工具调用、无 Artifact/Artifacts 相关指令**。
9. 官方原文自带若干重复词/语法瑕疵（"can't or won't with"、"but as as a request"、"can instead treats"、"avoid being being heavy-handed"），自 05-22 起部分沿用至 08-05 未被修正——登记时逐字保留，可作为各版本文本指纹。
10. Sonnet 4 · 05-22 日期行缺句号（`{{currentDateTime}}` 后无 `.`）为该条目独有标点特征，07-31 起修正。

## 附：信源文件清单与行数核验

| 文件 | 全文行数 | 条目（日期 → 正文行区间 → 正文行数） |
|---|---|---|
| %TEMP%\sp-docs\claude-sonnet-4.md | 305 | 08-05 → L10-112 → 103；07-31 → L118-220 → 103；05-22 → L226-304 → 79 |
| %TEMP%\sp-docs\claude-opus-4.md | 305 | 08-05 → L10-112 → 103；07-31 → L118-220 → 103；05-22 → L226-304 → 79 |
| %TEMP%\sp-docs\claude-opus-4-1.md | 127 | 08-05 → L10-126 → 117 |

> diff 方法备注：以 `## <日期>` 为界切出各条目 ```text wrap 代码块正文，PowerShell Compare-Object -SyncWindow 0 做保序行级对比；共执行 7 组对比（sonnet 05-22↔07-31、sonnet 07-31↔08-05、opus 05-22↔07-31、opus 07-31↔08-05、opus4↔opus4-1 同 08-05、sonnet↔opus 同 08-05、sonnet↔opus 同 05-22），全部差异已收录于 F-40-003/004/005/008/012。
