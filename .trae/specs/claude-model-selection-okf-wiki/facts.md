# F 编号事实登记 —— Claude 模型选型（官方博文 + 官方模型页）

> **本表不含推断。** 每条为源文（claude.dev 2026-11-09 博文）明示内容，或经 anthropic.com 模型页 / Fable 5.2 发布文 / Claude Code 文档核验的事实。
> 口径类型枚举：`博文元信息` / `博文声明` / `作者观点` / `方法论建议` / `厂商自述` / `独立核验`。
> 本表与 bundle `references/article-source.md` **双份登记**，编号集合必须逐字一致、连续无跳号。

- **主源文 URL**：https://claude.dev/blog/which-claude-model-should-you-build-with/
- **主源文标题**：Which Claude model should you build with? Fable, Opus, Sonnet, or Haiku
- **发布方**：claude.dev（Anthropic 开发者博客），作者 Addy Osmani
- **发布时间**：2026-11-09
- **采集时间**：2026-11-10
- **采集通道**：web_fetch 抓取官方 Markdown 版（28,987 字符）+ HTML 版交叉比对

---

## 一、元信息与阵容

| 编号 | 声明 | 信源定位 | 口径类型 | 核验 |
|---|---|---|---|---|
| F-001 | 文章标题为《Which Claude model should you build with? Fable, Opus, Sonnet, or Haiku》。 | 博文标题 | 博文元信息 | 单源 |
| F-002 | 作者 Addy Osmani（Member of Technical Staff），发布于 2026-11-09，栏目 Playbooks，阅读时长 15 分钟。 | 博文页眉 | 博文元信息 | 单源 |
| F-003 | 当前通用可用模型有四个：Claude Haiku 5.5、Sonnet 5.5、Opus 5.5、Fable 5.2。 | 导语 | 博文声明 | 通过（四个模型页） |
| F-004 | Claude Mythos 5.2 是网络安全与生命科学研究方向最强的模型，通过验证计划提供。 | 导语 | 博文声明 | 通过（Fable 5.2 发布文） |

## 二、选型总则

| 编号 | 声明 | 信源定位 | 口径类型 | 核验 |
|---|---|---|---|---|
| F-005 | 多数工作应从 Opus 5.5 的默认 effort（`medium`）开始。 | TL;DR | 方法论建议 | 方法论观点 |
| F-006 | Opus 5.5 是 Claude Code 的默认模型，单位 token 价格为 Fable 5.2 的一半。 | TL;DR | 博文声明 | 价格通过；默认模型部分通过 |
| F-007 | 范围明确的日常工作（修 bug、按规格做功能）可下移到 Sonnet 5.5。 | TL;DR | 方法论建议 | 方法论观点 |
| F-008 | 规格清晰不等于应选 Sonnet：迁移或性能优化即使规格清晰也可能需要 Opus 5.5，重大项目需要 Fable 5.2。 | TL;DR | 作者观点 | 方法论观点 |
| F-009 | 最简单的高频工作（分类、路由、抽取）用 Haiku 5.5；Haiku 也适合给大模型打下手做子代理。 | TL;DR | 方法论建议 | 通过（Haiku 页） |
| F-010 | 最难的技术项目（编码、金融、科学）用 Fable 5.2；Opus 5.5 在 `high` 仍不足、或长时间无人值守运行时也上移。 | TL;DR | 方法论建议 | 方法论观点 |
| F-011 | 换模型前先调 effort；超过 `high` 后，再升一档的成本可能等于换更大的模型。 | TL;DR | 作者观点 | 方法论观点 |
| F-012 | 更高 effort 让模型思考更久、调用更多工具、更多自检，但增加延迟；effort 不会带来模型不具备的知识或技能。 | TL;DR | 作者观点 | 方法论观点 |

## 三、按任务选型矩阵

| 编号 | 声明 | 信源定位 | 口径类型 | 核验 |
|---|---|---|---|---|
| F-013 | 日常工程与调试、多 PR 功能开发：Opus 5.5，`medium`（默认）→ `high`。 | 选型表 | 方法论建议 | 方法论观点 |
| F-014 | 分类、路由、打标、高频抽取：Haiku 5.5，`medium`。 | 选型表 | 方法论建议 | 方法论观点 |
| F-015 | 搜索文件、读日志、做摘要的子代理：Haiku 5.5 或 Sonnet 5.5，模型默认 effort。 | 选型表 | 方法论建议 | 方法论观点 |
| F-016 | 聊天与交互式会话：Sonnet 5.5，`low` 或 `medium`；高频简单聊天可用 Haiku 5.5。 | 选型表 | 方法论建议 | 方法论观点 |
| F-017 | 范围明确的编码（修 bug、功能迭代、规格驱动）：Sonnet 5.5，`medium` → 更难时 `high`。 | 选型表 | 方法论建议 | 方法论观点 |
| F-018 | 日常文档、幻灯片、表格：Sonnet 5.5，`high`（Claude Code 中为 `medium`）；复杂财务模型或大量素材文档从 Opus 5.5 开始。 | 选型表 | 方法论建议 | 方法论观点 |
| F-019 | 重复运行的 Agent 任务（调查、评审、起草）：Sonnet 5.5，`medium`。 | 选型表 | 方法论建议 | 方法论观点 |
| F-020 | 计算机使用与重视觉工作流：Opus 5.5，`medium`。 | 选型表 | 方法论建议 | 方法论观点 |
| F-021 | 大型重构与迁移、架构规划、带大量子代理：Fable 5.2，`medium` → `high`（API 默认 `high`）。 | 选型表 | 方法论建议 | Claude Code 默认 medium 通过；API 默认 high 单源 |
| F-022 | 深度研究、科学或定量分析：Fable 5.2，`medium` → `high`（API 默认 `high`）。 | 选型表 | 方法论建议 | 同上 |
| F-023 | 不确定时：Opus 5.5，`medium`；Claude Code 在 Pro/Max/Ultra/Team/Enterprise 与 Anthropic API 上默认用它。 | 选型表 | 博文声明 | 部分通过（Fable 非任何计划默认已确认） |

## 四、四模型对照

| 编号 | 声明 | 信源定位 | 口径类型 | 核验 |
|---|---|---|---|---|
| F-024 | 定位：Haiku 面向高频低成本；Sonnet 面向范围明确任务的快速胜任；Opus 是复杂编码与知识工作的日常主力；Fable 面向最有野心的开放式技术工作。 | 对照表 | 博文声明 | 通过（四个模型页） |
| F-025 | 相对延迟：Haiku 最快、Sonnet 快、Opus 与 Fable 中等。 | 对照表 | 博文声明 | 单源 |
| F-026 | Haiku 5.5 价格：≤100K token 为 `$0.10/$0.50`，>100K token 为 `$0.50/$2.50`（输入/输出，每百万 token）。 | 对照表 | 博文声明 | 通过（Haiku 页） |
| F-027 | Sonnet 5.5 价格：`$2/$10` 每百万 token。 | 对照表 | 博文声明 | 通过（Sonnet 页） |
| F-028 | Opus 5.5 价格：`$4/$20` 每百万 token。 | 对照表 | 博文声明 | 通过（Opus 页） |
| F-029 | Fable 5.2 价格：`$8/$40` 每百万 token。 | 对照表 | 博文声明 | 通过（Fable 页、发布文） |
| F-030 | 缓存读取价：Haiku `$0.01`（≤100K）/`$0.05`（>100K）；Sonnet `$0.10`；Opus `$0.20`；Fable `$0.20`。 | 对照表 | 博文声明 | Opus/Fable 通过；Sonnet 与官方“最多 90% 节省”口径冲突 |
| F-031 | 四个模型均为 1M token 上下文窗口。 | 对照表 | 博文声明 | 通过（模型页） |
| F-032 | 四个模型最大输出均为 128K token。 | 对照表 | 博文声明 | 单源 |
| F-033 | Thinking（API）：Haiku 自适应、默认开启、可关闭；Sonnet 自适应、默认开启、`between_tools` 跳过前置思考；Opus 与 Fable 自适应、始终开启。 | 对照表 | 博文声明 | 单源（platform 文档区域受限） |
| F-034 | API 默认 effort：Haiku `medium`；Sonnet `high`（Claude Code 为 `medium`）；Opus `medium`；Fable `high`（Claude Code 为 `medium`）。 | 对照表 | 博文声明 | Claude Code 全为 medium 已通过；API 档位单源 |
| F-035 | Fast mode：Opus 5.5 与 Fable 5.2 支持，Haiku 与 Sonnet 不支持。 | 对照表 | 博文声明 | 通过（Opus/Fable 页） |

## 五、成本与性能权衡

| 编号 | 声明 | 信源定位 | 口径类型 | 核验 |
|---|---|---|---|---|
| F-036 | Terminal-Bench 3.0：Fable 5.1 在 `max` 得 58.0%，Opus 5.5 在 `high` 得 58.9% 且 token 用量减半。 | 成本与能力段 | 厂商自述（转述同站文章） | 未独立复算 |
| F-037 | FrontierCode 2.0：Fable 5.2 在 `high` 与 Opus 5.5 在 `max` 基本持平（45.3% vs 45.5%），每任务成本约一半。 | 成本与能力段 | 厂商自述 | 通过（Fable 5.2 发布文） |
| F-038 | 小型模型适合输出可校验的高频工作，不适合长时间 agentic 循环。 | 成本与能力段 | 博文转述平台文档 | 方向一致，未逐字核验 |
| F-039 | 比较模型时要给最难的任务定价：某 20 题搜索基准中 2 题占 43% 开销。 | 成本与能力段 | 厂商自述 | 单源 |
| F-040 | Fable 5.2 输出速度最高比 Fable 5.1 快 30%；Sonnet 5.5 比 Sonnet 5 快 30%。 | 延迟段 | 博文声明 | 通过（两个发布页） |
| F-041 | SWE-bench Pro：Opus 5.5 在 `medium` 比 `high` 低约 2.5 分、成本约为 70%；`low` 低约 8 分、成本约三分之一；`xhigh` 高约 1.4 分、成本为 `high` 的 2.5 倍。 | 延迟段 | 厂商自述 | 未独立复算 |
| F-042 | 模型不够好时的升级顺序：先让模型能自验 → effort 升一档 → 换上一级模型并从更低 effort 起步。 | 延迟段 | 方法论建议 | 方法论观点 |
| F-043 | 可自动校验时，全部用低 effort 跑、只对失败项用高 effort 重跑：同一 SWE-bench Pro 子集通过率约 97%、`$0.17`/题，对比全 `high` 的 95.3%、`$0.29`/题。 | 延迟段 | 厂商自述 | 未独立复算 |
| F-044 | Opus 5.5 与 Fable 5.2 提供 fast mode，以溢价换取更高输出速度。 | 延迟段 | 博文声明 | 通过（Opus 页 `$8/$40`、Fable 页 `$16/$80`，均最高 2.5x） |
| F-045 | 每代模型均为 1M 上下文；每轮都会重发上下文，长任务中大部分输入按缓存读取计费。 | 上下文段 | 博文声明 | 机制通过；比例单源 |
| F-046 | 一轮缓存读取成本：150K 上下文约 `$0.03`，20K 约 `$0.004`。 | 上下文段 | 博文引用同站文章 | 未独立复算 |
| F-047 | 主模型越大，精简主上下文越重要：把昂贵模型的上下文留给决策，让便宜子代理做冗长阅读。 | 上下文段 | 作者观点 | 方法论观点 |
| F-048 | Haiku 5.5 是唯一按提示长度分档计价的模型；>100K 档为低价档的 5 倍，仍是 Sonnet 单位价的四分之一；短提示下输入价为 Sonnet 的二十分之一。 | 上下文段 | 博文声明 | 价格通过；倍数关系为算术推导 |

## 六、混合模型

| 编号 | 声明 | 信源定位 | 口径类型 | 核验 |
|---|---|---|---|---|
| F-049 | 提示缓存属于写入它的模型；在新模型上的第一轮要为整段对话支付缓存写入价。 | 混合模型段 | 机制说明 | 通过（缓存机制） |
| F-050 | 降低切换成本：Claude Code 先 `/compact`，或带简短计划开新会话；API 用工作摘要开启新模型对话，而非全量历史。 | 混合模型段 | 操作建议 | 操作建议 |
| F-051 | Thinking block 兼容矩阵：Opus 5.5 读 Sonnet 5.5/Haiku 5.5；Sonnet 5.5 读 Haiku 5.5；Fable 5.2 读 Opus 5.5/Sonnet 5.5/Haiku 5.5；Fable 5.1 读 Opus 5.5。 | 混合模型段 | 博文声明 | 单源 |
| F-052 | 下移一档会丢失先前推理（模型不读更高级模型的 block）；无法读取时 API 丢弃 block 但请求仍成功。 | 混合模型段 | 博文声明 | 单源 |
| F-053 | 从 Fable 5.2 切换到任何其他通用模型都会丢弃其推理。 | 混合模型段 | 博文引用 preserved thinking 文档 | 单源 |
| F-054 | 子代理在独立上下文窗口运行并回传摘要，按其运行模型的费率计费；Claude Code 用 `model: haiku`/`sonnet` 指定；`CLAUDE_CODE_SUBAGENT_MODEL` 设默认。 | 子代理段 | 博文声明 | 部分通过（别名文档） |
| F-055 | 示例子代理文件 `.claude/agents/log-reader.md` 含 name、description、`tools: Read, Grep, Glob, Bash`、`model: haiku`。 | 子代理段代码块 | 博文声明 | 格式与官方子代理文档一致 |
| F-056 | 小模型只做错误易发现的工作（找文件、跑测试、读日志）；改代码与判断留给主模型。 | 子代理段 | 作者观点 | 方法论观点 |
| F-057 | Claude Code 内置 Explore 子代理使用会话模型（API 上上限为 Opus）；可自建同名 Explore 并设 `model: haiku`；`ANTHROPIC_DEFAULT_HAIKU_MODEL` 可固定 `haiku` 别名指向。 | 子代理段 | 博文声明 | 单源 |
| F-058 | Anthropic API 上 `haiku` 别名解析为 Haiku 5.5，需 Claude Code v2.1.293+；Bedrock、Google Cloud、Microsoft Foundry、Claude Platform on AWS 仍解析为 Haiku 4.5。 | 子代理段 | 博文声明 | 通过（model-config 文档） |
| F-059 | `opusplan` 别名在 plan 模式用 Opus、执行用 Sonnet；博文建议相反（改代码留在主模型），采用前需自测。 | 子代理段 | 博文声明 | 通过（别名存在） |
| F-060 | Advisor 工具（beta）把快速便宜的 executor 与更强的 advisor 配对；多数 token 按 executor 费率计费。 | Advisor 段 | 博文声明 | 单源（platform 文档区域受限） |
| F-061 | 平台成本指南中顾问表四组配对没有一组明显优于单用 executor；只有 executor 主动咨询时 advisor 才有帮助。 | Advisor 段 | 博文转述平台文档 | 单源 |
| F-062 | Sonnet 5.5 executor 接受 Fable 5.2/Opus 5.5/Opus 5/Sonnet 5.5 作为 advisor；Fable 5.2 executor 只接受 Fable 5.2 或 Mythos 5.2。 | Advisor 段 | 博文声明 | 单源 |
| F-063 | Opus 5.5 `high` + Fable 5.1 advisor 在内部编码基准得 90.1%、`$2.92`/次，比单用 Opus 5.5 `high` 高 1.7 分、花费约 2.1 倍。 | Advisor 段 | 厂商内部测试 | 单源 |
| F-064 | 批量委派：Opus 5.5 带队 + 最多 25 个 Sonnet 5.5 worker，在约 2200 万 token 源码的缺陷搜索基准上成本低约三分之一、得分接近。 | 批量委派段 | 厂商内部测试 | 单源 |
| F-065 | Claude Managed Agents 的 multiagent orchestration 提供 coordinator + worker 名单；单链依赖或单上下文可完成的工作不适用。 | 批量委派段 | 博文声明 | 单源 |

## 七、迁移兼容

| 编号 | 声明 | 信源定位 | 口径类型 | 核验 |
|---|---|---|---|---|
| F-066 | 当前所有模型都支持工具调用与图像输入。 | 迁移段 | 博文声明 | 单源 |
| F-067 | Fable 5.2 对所有 API 账号启用 preserved thinking；若 thinking block 之前的系统提示、工具或历史消息发生变化，API 返回 400，除非选择丢弃受影响 thinking。 | 迁移段 | 博文声明 | 单源（platform 文档区域受限） |
| F-068 | 通过 Claude Code、Claude Agent SDK 或 Claude Managed Agents 构建时无需改动；自建请求应保持历史只追加。 | 迁移段 | 操作建议 | 操作建议 |
| F-069 | Opus 5.5 与 Fable 5.2 始终思考，关闭 thinking 会报错；Sonnet 5.5 默认思考，`between_tools` 只在工具间隙思考；Haiku 5.5 默认思考，`high` 及以下可关闭；响应可能以 thinking block 开头，应按 type 读取内容块。 | 迁移段 | 博文声明 | 单源 |
| F-070 | `tool_choice` 为 `any` 或指定 `tool` 时，Sonnet 5.5/Opus 5.5/Fable 5.2 返回 400；应使用 `auto` + 工具 `strict: true` + 提示词说明何时调用。 | 迁移段 | 博文声明 | 单源 |
| F-071 | 计算机使用仅在 Claude API 与 Google Cloud（Google managed）通过 `computer_toolset_20260801` 工具集支持。 | 迁移段 | 博文声明 | 单源 |
| F-072 | Haiku 4.5→5.5 迁移：用 effort 取代 `budget_tokens`；移除非默认 `temperature`/`top_p`/`top_k`（否则 400）；消息须以 user turn 结尾。 | 迁移段 | 博文声明 | 单源 |
| F-073 | 安全分类器最常标记网络安全与生物内容；Claude Code 可将被标记请求改由旧模型重跑并在转录中提示；Fable 5.2 沿用 Fable 5.1 的回退：网络安全→Opus 4.8，生物→Opus 5。 | 迁移段 | 博文声明 | 部分通过（Fable 页确认回退机制） |
| F-074 | 多模型系统应按最严格模型构建请求：历史只追加、`tool_choice` auto + strict 工具、按 type 读内容块、提示词与工具描述足够精确；简单路由规则交给代码而非模型。 | 迁移段 | 作者观点 | 方法论观点 |

## 八、自测与延伸

| 编号 | 声明 | 信源定位 | 口径类型 | 核验 |
|---|---|---|---|---|
| F-075 | 自测方法四步：抽真实任务并写结果校验 → 每个候选模型跑 2–3 个 effort、各自独立会话并记录每任务成本 → 画得分-花费图 → 上线前在真实流量切片上影子运行。 | 自测段 | 方法论建议 | 方法论观点 |
| F-076 | Claude Code 快速对比：用 `/model` 在两个模型上跑同一个待办任务，比较 `/usage`。 | 自测段 | 操作建议 | 操作建议 |
| F-077 | 延伸阅读：Sonnet 5.5 构建指南、Opus 5.5 使用指南、Opus 5.5 任务成本、模型选择与 effort 文档。 | Learn more | 博文元信息 | 单源 |
