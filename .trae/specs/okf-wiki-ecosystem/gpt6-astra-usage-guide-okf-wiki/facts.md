---
type: facts
title: GPT-6 Astra 博文转化事实集（F-001～F-043）
date: 2026-09-16
source: https://mp.weixin.qq.com/s/QECM-lf5XuH1szeszv3AFw
verification: 10 项 P0（✅ 8 / ⚠️ 2 / ❌ 0），权威信源为 OpenAI 开发者文档
---

# 事实集：《Skill 又要被干掉了？OpenAI 祭出了 Astra 的使用焚诀》

> 信源：微信公众号 **cxuanAI**（作者 cxuan，原创），2026-09-07 11:07 发布，正文约 6555 字
> 采集方式：browser_use 提取 `#js_content` innerText 全文（WebFetch 被微信反爬拦截）
> 标注约定：P0 = 必核验（数字/日期/官方表态/功能时间线）；P1 = 选核验；P2 = 可单源；**[作者观点]** / **[个人经历]** 条不得转述为事实

## A. 元信息

| F 编号 | 事实 | P 级 | 核验 |
|--------|------|------|------|
| F-001 | 博文标题《Skill 又要被干掉了？OpenAI 祭出了 Astra 的使用焚诀》，公众号 cxuanAI，署名 cxuan，标注原创，2026-09-07 11:07 发布，IP 属地河北 | — | ✅ |
| F-002 | 文末标注"文章来源：OpenAI 官方指南：Using GPT-6 Astra"；功能说明参考：异步工具调用、中途引导、切换思考强度、提示词缓存、偏离检测 | P0 | ✅ 官方指南真实存在且五主题对应 |
| F-003 | 博文形态为官方指南中文转译 + 作者评点（含"卧槽，这个 Prompt 绝了"等主观句），全文无作者实测过程与结果 | P1 | ✅ 通读判定 |
| F-004 | **[个人经历]** 作者称此前使用的某工具侵入式改写模型列表，导致 Codex 更新后仍使用三方模型列表、GPT-6 Astra 未获推送 | P2 | 仅博文单源，不入 bundle 正文事实 |

## B. 模型发布与规格

| F 编号 | 事实 | P 级 | 核验 |
|--------|------|------|------|
| F-005 | 官方定位：GPT-6 Astra 是 OpenAI 迄今最智能模型，在 computer use、browsing、软件工程、科学与专业工作上 SOTA，擅长跨代码/浏览器/专业软件的多步工作流；官方同时称其为最 aligned 模型（注意边界、透明沟通） | P0 | ✅ 官方指南 Introduction |
| F-006 | 博文行文（2026-09-07）称"GPT-6 Astra 还没发布两天"；核验：The Verge 于 2026-09-03 报道发布，公司总裁 Greg Brockman 称进入"AGI era"（属公司高管声称，非独立技术阈值） | P0 | ⚠️ 口语措辞，发文时为发布后第 4 天，非硬错误 |
| F-007 | API 模型 ID 为 `gpt-6-astra`；在 Responses API 请求中设置 `model` 字段调用 | P0 | ✅ 官方指南 + 模型页 |
| F-008 | 模型页规格（核验补充，博文未含）：上下文窗口 1,050,000 tokens，最大输出 128,000 tokens，知识截止 2026-04-30；输入文本+图像、输出文本；不支持音频/视频输入 | P0 | ✅ 官方模型页 |
| F-009 | 模型页定价（核验补充，博文未含）：输入 $10.00/百万 tokens、缓存输入 $1.00、缓存写入 $12.50、输出 $50.00；输入超 272K tokens 的请求整单按输入/缓存 2x、输出 1.5x 计价；Batch/Flex 为标准价 50%；Fast 模式 2x；Free 档不可用 | P0 | ✅ 官方模型页 |
| F-010 | 2026-09-08 起 GPT-6 Astra 在 Amazon Bedrock GA，可经 Bedrock API 直调或配置 ChatGPT Work/Codex 走 Bedrock（核验补充） | P1 | ✅ AWS 官方博客 |

## C. 五项新特性与限制

| F 编号 | 事实 | P 级 | 核验 |
|--------|------|------|------|
| F-011 | **异步工具调用**：以往标准 tool use 在模型层为同步阻塞式，需等应用返回结果才能继续（开发者程序本身可并行/异步执行工具，但模型做不到）；Astra 在应用执行工具期间，模型可继续推理、调用其他工具或回答请求的独立部分 | P0 | ✅ 与官方一致 |
| F-012 | 异步工具用法（核验补充机制）：在 function 或 custom tool 上设置 `async: true`，结果就绪后用**原始 `call_id`** 返回；应用仍负责执行工具与管理 pending 工作；官方另提供开发者自定义 wait-tool 模式 | P0 | ✅ 官方指南 What's new |
| F-013 | **中途引导（Mid-turn steering）**：任务执行中用户可直接插话修改要求/纠正方向，无需等模型做完；博文区分：Codex 产品既有的 steer（插队）/queue（排队）在**应用编排层**实现，Astra 将该能力下沉到 Responses API | P0 | ✅ 能力与分层表述准确（分层为作者解读，合理） |
| F-014 | steering 机制（核验）：仅 GPT-6 Astra 支持、仅 WebSocket 连接，GPT-5.6 及更早不支持；收到 `response.created` 后发 `response.steer`（只接受 `type`/`previous_response_id`/`input`），API 回 `response.steer.accepted`（仅表示排队，不表示已执行），随后自动创建承接响应（创建前先完成当前输出项与已在运行的托管工具）；不改写已发送输出、不撤销已执行动作、不取消已启动工具；原响应以 `response.incomplete`（reason=steered）结束，另有 `response.steer.failed` 事件 | P0 | ✅ 博文 `response.steer` 事件名准确；遗漏边界已补全 |
| F-015 | **对话中切换推理强度并保留缓存**：同一长对话可按任务难度随时切换思考强度；博文示例：low 梳理项目结构 → high 分析复杂并发问题 → low 整理修改说明，无需全程高档位 | P0 | ✅ 与官方配置更新语义一致 |
| F-016 | 机制（核验）：向输入添加 `configuration_update` input item 调整 reasoning effort，新档位持续到下一次 configuration_update 覆盖；在标准单代理请求中使用，请求级 `reasoning.effort` 保持不变，以保留 prompt 前缀缓存 | P0 | ✅ 官方指南 |
| F-017 | **偏离检测（Misalignment monitoring）**：审查模型是否正确理解用户指令，聚焦敏感场景（传输敏感数据、访问敏感数据、破坏性变更）；博文三个场景例——让删临时构建文件却删整个项目目录；只授权读某客户数据却访问其他客户数据；让发公开报告却把含密钥配置一并发出 | P0 | ✅ 三类场景与官方三类别一一对应（例子为官方类别的具体化） |
| F-018 | 检测在**后台异步**审查模型推理过程与操作行为；博文：等发现问题时前面的操作可能已经执行完，停止后续执行也不会撤销已做操作 | P0 | ✅ 与官方原文一致（"an action may already have completed… does not undo earlier actions"） |
| F-019 | 覆盖面与工程细节（核验补充）：使用 persisted reasoning / WebSocket / OpenAI compaction 的 Responses 请求受监控且可自动阻断；不用这些机制的 Responses 请求受监控、webhook 可收告警但**不自动停**；Chat Completions 请求不在该监控覆盖内；流式开始前阻断返回 HTTP 403（type=`invalid_request_error`，code=`misalignment_policy_violation`，按 code 不按文案匹配）；项目经 `safety.alert.created` webhook 订阅告警，凭 `api.safety.alerts.read` 权限 `GET /v1/safety/alerts/{id}` 取回详情；无通用恢复入口，被阻工作流不得自动重试；监控会漏报也会误报，不替代应用侧防护（最小权限、工具输入校验、敏感动作人工批准） | P0 | ✅ 官方 misalignment monitoring 指南 |
| F-020 | **限制一**：Astra 不支持 `none` reasoning effort（最低档位为 low）；模型页列出支持档位 `low`/`medium`/`high`/`xhigh`/`max` 五档；迁移建议：现用 none/minimal 者从 low 起步对比效果 | P0 | ✅ 官方指南 + 模型页 |
| F-021 | **限制二**：开启欧盟数据驻留（EU data residency）的 API 项目调用 Astra 不能用 Fast 模式（博文）；核验补充：`service_tier: "fast"` 与 `"priority"` 均不支持，须用 Standard 处理；Fast 模式不提供延迟 SLA | P0 | ✅ 博文准确但不完整，已补 priority 与 SLA |
| F-022 | 迁移 quickstart（核验补充）：工具调用必须用 Responses API（Chat Completions 可调用模型但不支持工具调用）；不支持参数 `temperature`/`top_p`/`top_logprobs`（Chat Completions 另移除 `logprobs`；Responses 从 `include` 移除 `message.output_text.logprobs`）；从 GPT-5.5 及更早迁移时 `prompt_cache_retention` 替换为 `prompt_cache_options.ttl: "30m"`；Codex 可安装 OpenAI Docs skill，执行 `$openai-docs migrate this project to GPT-6 Astra` | P0 | ✅ 官方指南 Migration quickstart |

## D. 五大行为模式与官方 Prompt 配方

| F 编号 | 事实 | P 级 | 核验 |
|--------|------|------|------|
| F-023 | 官方指南设"Prompting best practices"：GPT-6 Astra 比 GPT-5.6 Sol 等早期模型更智能，同时存在可通过 prompt 针对用例优化的行为模式，共列五方面 | P0 | ✅ |
| F-024 | 行为1 **主动性与贯彻执行力**：模型被设计为更有效协作者，当额外输入可能实质改变结果时更倾向向用户提问，可能在用户期望它合理假设并继续时停下；长任务中比 GPT-5.6 Sol 及更早模型更能保持前后一致，早期模型倾向自行假设 | P0 | ✅ |
| F-025 | 官方 Prompt（主动性-A，官方原文）：从指令与既有对话上下文推断用户意图与任务范围；偏向行动并把用户任务贯彻完成；用户表达开展新工作或修问题意图时持续工作直至目标完成；自主推进（必要时建隔离 worktree/检出、解决合并冲突、只读操作、建草稿 PR 等），除非操作明显具破坏性或不可逆 | P0 | ✅ 逐字对照 |
| F-026 | 官方 Prompt（主动性-B）："can you..."/"I want to..."/"help me..."等表达视为动手执行指令；不停留在确认能力（如只答"Yes"）、不只给计划、不询问是否继续；不为省时间/精力/token 交付不完整或"差不多够用"的结果；需要持续投入的任务完成全部必要工作直至目标达成 | P0 | ✅ |
| F-027 | 官方 Prompt（主动性-C）：提澄清问题前，先完成上下文已授权、且让拟议动作具体可审查所必需的工作，用户批准的应是具体可审查结果；部署变更、写外部应用、合并 PR、发布站点前先做完准备，批准作为最后一步；可逆任务、只读操作、审查/修复、会话早前已授权或任务指令强暗示授权的事项无需再请许可；不要因假设性风险引入未被要求的警告、免责声明、审批流或安全/合规检查清单 | P0 | ✅ |
| F-028 | 模型默认还会在工作过程中提出**非阻塞式问题**；应按应用所需自主程度调节这些提示词 | P1 | ✅ |
| F-029 | 行为2 **指令遵循**：比以往模型更能遵循长指令，同时对上下文中的信息更敏感；skill 文件中不清晰或相互冲突的指引可能导致模型停顿、提前阻塞工作；应显式说明用户指令与 skill 的优先级；官方**强烈建议**审计模型可访问的 skills 及其他文件（点名 `AGENTS.md`）中可能影响行为的指令 | P0 | ✅ |
| F-030 | 官方 Prompt（指令-A）：用户指令优先于 skill 提供的指引；明确的用户指令与 skill 指令冲突时，以用户指令为准 | P0 | ✅ |
| F-031 | 官方 Prompt（指令-B）：若某 skill 导致请求许可/确认、暂停、留下用户要求的工作未完成或偏离用户意图，须点名并链接到所读的具体 SKILL.md 文件、引用导致该行为的相关指令原文、简述该指令如何适用于当前任务；区分 skill 中明文要求与自己对指引的解读/推断 | P0 | ✅ |
| F-032 | 博文解读：应用同时加载很多 Skill、AGENTS.md 等指令文件时，可用上述 Prompt 找出在后台悄悄影响模型行为以及彼此冲突的规则；博文举例——Astra 因 `publishing/SKILL.md` 中"发布前必须获得用户确认"暂停发布（该步骤会向外部平台写入，规则适用） | P1 | ✅ 例子为博文对官方 Prompt 的合理演绎 |
| F-033 | 行为3 **个性与写作风格**：模型倾向提供详细、格式化回复（小标题、项目符号、编号列表、表格、粗体、引用块、Markdown 代码块），并可能跨会话重复某些短语；需显式指定应用所需写作风格与结构，不能假设模型会自选散文风格 | P0 | ✅ |
| F-034 | 官方 Prompt（写作-A 散文风格）：默认使用清晰简洁的自然段，每段展开一个主旨；仅当信息确为并列、有序或便于比较时才用列表，层级无法用散文清晰表达时才嵌套列表；使用朴素简单的语言（熟词、具体例子、精确动词），优先主动语态与直陈；要点清晰前置，句子之间承接推进 | P0 | ✅ |
| F-035 | 官方 Prompt（写作-B 技术沟通）：朴素语言优先于行话，技术细节仅在有助于说明想法或工作时引用；清晰连贯地传达复杂概念；把写作校准到用户提示与上下文所假定的背景知识水平 | P0 | ✅ |
| F-036 | 官方 Prompt（写作-C 去套话/AI Slop）：避免 slop 词与短语——结论中的"Bottom Line:"、"delve"、"foster"、"leverage"、"it's worth noting"、"importantly"、"Question? Answer."、"This isn't about X. It's about Y."、"genuinely"，以及连字符生造的复合描述词/形容词；禁用"In short:.."、"The simplest mental model is:.."类总结句；直接陈述拟执行动作；不补充"不做什么/什么保持不变/如何分类结果"；禁用"X, not Y"/"X—not Y"对比句式（会引入用户没问的替代说法）；避免生造复合标签（如"exact-head checks"、"editorial-row layouts"）、模糊限定词与套路过渡，用朴素动词和介词直接陈述真实关系 | P0 | ✅ 词表逐字对照 |
| F-037 | **[作者观点]** 作者评点"这意思是不是说 Astra 更智能，然后会导致 AI 味儿更小"；总结处表示想亲自验证官方去味儿配方"到底能去掉多少味儿"；并称笼统说"主动一点""去掉 AI 味儿"太笼统 | P2 | 作者观点，正文分层标注 |
| F-038 | 行为4 **子代理委托**：Astra 受过将任务拆分并委托给并行 subagent 的训练；但实际委托频率可能低于工作流预期；需在 prompt 中指定模型应在何时、多大程度上用 subagent 做并行工作 | P0 | ✅ |
| F-039 | 官方 Prompt（委托-A）：无论作为根代理还是 subagent，只要能通过委托其他代理并行化工作、从而节省时间或提升质量，就应使用协作工具这么做；（可读性-B）发给其他代理的消息与最终答复可能由人阅读，确保清晰易读，单词与/或数字之间保留恰当空格 | P0 | ✅ |
| F-040 | 行为5 **测试与验证**：编码任务中模型倾向在认定任务完成前做详尽测试，小任务可能导致测试范围超出实际所需；官方 Prompt——可逆、低影响的变更不编写照搬实现的测试；若用测试验证，测试须有实际意义且为验证实现所必需；运行与变更相匹配的测试并完成规定检查，通过后仅在有新改动、测试失败或仍有未决问题时扩大/重跑测试，否则继续推进任务 | P0 | ✅ |
| F-041 | 博文列举官方延伸资料 4 份：Building games with Astra、Architectural visualization with Astra（实操案例）、Prompt engineering、Codex Best practices（通用指南）；博文页面未挂这些资料的超链接 | P2 | 未逐项核验链接，bundle 中标注"博文列举" |

## E. 标题与总结（观点层）

| F 编号 | 事实 | P 级 | 核验 |
|--------|------|------|------|
| F-042 | **[作者观点/引流标题]** 标题命题"Skill 又要被干掉了"：正文与官方指南均显示模型对 skills 和 AGENTS.md 中指令"更敏感"、官方强烈建议审计 skills，全文不支持"Skill 被干掉"命题；"使用焚诀"为比喻官方 Prompt 配方的网络用语 | P0 | ⚠️ 观点与事实分层，bundle 正文显式辨析 |
| F-043 | **[作者观点]** 作者总结：新特性主要方便长任务（工具执行时可做别的、用户可中途补充、思考强度按难度调整）；作者更在意 Prompt 配方部分 | P2 | 作者观点 |

---

## 核验统计

- P0 项：**10 项集群（覆盖 F-002/F-005～F-009/F-011～F-022/F-023～F-036/F-038～F-040/F-042）**，结论 **✅ 8 集群 / ⚠️ 2 集群（F-006 措辞、F-042 标题）/ ❌ 0**
- 核验补充事实（博文遗漏但官方明确）：F-008、F-009、F-010、F-012、F-014 边界、F-019、F-021 补全、F-022
- 权威信源：
  1. https://developers.openai.com/api/docs/guides/latest-model （Using GPT-6 Astra）
  2. https://developers.openai.com/api/docs/guides/steering （Mid-turn steering）
  3. https://developers.openai.com/api/docs/guides/safety-checks/misalignment-monitoring
  4. https://developers.openai.com/api/docs/models/gpt-6-astra
  5. https://www.theverge.com/ai-artificial-intelligence/989601/openai-gpt-6-astra-release （发布日期二手源）
  6. https://aws.amazon.com/blogs/machine-learning/take-on-your-most-ambitious-work-with-gpt-6-astra-on-amazon-bedrock/ （Bedrock GA 二手源）
