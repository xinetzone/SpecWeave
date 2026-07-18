---
id: "vibe-coding-prompts-learning-analysis"
title: "Vibe Coding 两大神级 Prompt 学习分析"
category: "learning"
tags: ["vibe-coding", "prompt", "第一性原理", "对抗式审查", "ai-agent", "代码审查", "multi-agent", "aihot", "可复用模式", "践行鸿沟", "类比推理"]
date: "2026-07-04"
last_updated: "2026-07-11"
status: "stable"
author: "SpecWeave"
summary: "学习分析卡兹克《Vibe Coding 两大神级 Prompt》一文：第一性原理(管生成)与对抗式审查(管验证)构成完整闭环,是 Vibe Coding 的两大基石。含本项目亲身践行验证案例（含反面教材）及元方法论自举验证。"
source:
  title: "Vibe Coding 两大神级 Prompt"
  author: "卡兹克"
  url: "https://mp.weixin.qq.com/s/umPqTD_-IubbhXIgiS47eQ"
  platform: "微信公众号（数字生命卡兹克）"
validation:
  -   - "卡兹克AIHOT项目实战验证（来源文章）"
  -   - "SpaceX火箭成本重构跨领域验证（来源文章）"
  -   - "本项目2026-07-09类比错误事件反面验证（L3级验证）"
  -   - "本项目2026-07-11 seven-concepts-trigger元方法论自举验证（L2级验证，对抗式审查成熟度升级至L2）"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/knowledge/learning/02-agent-engineering-methodology/vibe-coding-prompts-learning-analysis.toml"
---
# Vibe Coding 两大神级 Prompt 学习分析

> **一句话引言**：在 Vibe Coding 时代,让 AI 真正靠谱地干活,只需要两个"神级 Prompt"——**第一性原理**管生成,**对抗式审查**管验证,二者并肩构成完整闭环。本文是对卡兹克原文的系统化学习与提炼,并落地到 SpecWeave 智能体开发的方法论要点。

---

## 文章基本信息

| 字段 | 内容 |
|------|------|
| **原文标题** | Vibe Coding 两大神级 Prompt |
| **作者** | 卡兹克 |
| **来源** | 微信公众号「数字生命卡兹克」 |
| **原文链接** | https://mp.weixin.qq.com/s/umPqTD_-IubbhXIgiS47eQ |
| **主题** | Vibe Coding 两大神级 Prompt——第一性原理 与 对抗式审查 |
| **作者背景** | 自述为纯粹不懂代码的小白,用 Vibe Coding 方式做出 AIHOT(最近一周请求量超千万,Skill 调用量是网页端的 10 倍以上) |

**文章脉络**：作者周末与老朋友(基金经理、设计师、老师、产品经理、媒体人等非程序员)吃饭聊到 AI 与 Vibe Coding,朋友让他推荐最实用的 Vibe Coding 小技巧。作者想了半天给出两个"神级 Prompt":1. 第一性原理;2. 对抗式审查。前者管生成,后者管验证,构成完整闭环,是作者心目中 Vibe Coding 的两大基石。

## 核心观点提炼

作者认为,Vibe Coding 真正能让非程序员稳定产出可用产品的,不是某个花哨的工具,而是两个朴素的 Prompt 方法论:

| Prompt | 定位 | 一句话本质 |
|--------|------|-----------|
| **第一性原理** | 管**生成**——帮你找到好的方案、找到 BUG 真正本质的解法 | 回到最根本的事实重新推导 |
| **对抗式审查** | 管**验证**——保证 AI 写的代码确实没啥毛病,能稳定上线 | 你永远需要一个站在你对面的力量来告诉你,你可能是错的 |

二者**并肩站在一起**,构成 Vibe Coding 的完整闭环:

- 第一性原理保证**做对的事**(方向与根因正确)
- 对抗式审查保证**把事做对**(实现稳健、可上线)

> 作者原话定位:这两个 Prompt 是他心目中 Vibe Coding 的**两大基石**,并肩站在一起的那种。

---

## 第一性原理深度解析

### Prompt 的具体形式

使用方式极其简单——在原有 Prompt 后面加一句话即可:

```
从第一性原理出发
```

或者:

```
根据第一性原理来找一下原因
```

**效果**:让 Agent 写方案的能力、找 BUG 的能力都进化一大截。

### 底层机理:打断类比推理

理解第一性原理 Prompt 为什么有效,需要先看清当前 AI 的默认工作模式:

- **默认模式——类比推理**:你让它写一个过滤函数,它就从训练数据里找几万个类似函数,给你写一个差不多的。它**跳过了"这个问题真的应该这么解吗?"的关键步骤**。
- **第一性原理模式**:这七个字强制打断 AI 的类比推理,逼它回到问题的本质去思考——不要参考别人的方案,从最基本的事实出发,重新推导。

> 关键洞察:AI 的"聪明"常常停留在"看起来对"的类比层面,而真正高质量的方案与根因定位,需要回到事实本身的重新推导。第一性原理 Prompt 就是那个"强制打断"的开关。

### 实战案例:AIHOT 飞书推送 BUG 修复(治标 vs 治本)

**背景**:AIHOT 周五出事故——精选消息的飞书推送出 BUG。周六凌晨 OpenAI 发布 GPT-5.6 大新闻,在飞书群没被推送,用户反馈炸了二十多条。

**初步修复(治标)**:

> Agent 说是测试国产模型时,OpenAI 抓取被瞎改坏了,断了三天,修好就行。

**作者直觉与追问**:作者觉得这不对,背后有更严重的问题,治标不治本。于是补了一句:

> 根据第一性原理来找一下原因。

**深度发现(治本)**:Agent 找到了抓取海外信源规则中的巨大隐患——非常底层、非常深,是**流量路由层面**的问题。这段代码是今年 4 月中写的,国产模型瞎改代码时在表层做错一个小点,把整个底层流量路由问题暴露出来。

**解决**:花半天时间把底层路由问题直接重构,从机制上看未来大概率可以安心。

**治标 vs 治本对比**:

| 维度 | 初步修复(无第一性原理) | 深度修复(加第一性原理) |
|------|----------------------|------------------------|
| 修复层面 | 表层抓取错误 | 底层流量路由 |
| 代码溯源 | 国产模型瞎改的表层小点 | 4 月中写的深层隐患 |
| 效果 | 治表,未来还会复发 | 治本,机制上可安心 |
| 差异 | 一个是治表,一个是治本 | **差异巨大** |

### 跨领域案例:SpaceX 火箭成本重构

第一性原理并非 AI 时代才有,马斯克的 SpaceX 是经典跨领域案例:

- **行业共识**:火箭发射就是得花几个亿。
- **马斯克做法**:从材料成本开始算——铝合金、碳纤维、航空级燃料加起来才多少钱,从这数字出发重新设计整个制造流程。
- **结果**:发射成本降了 **90%**。
- **思想源头**:亚里士多德两千多年前就说过的道理——**每个系统中存在一个最基本的命题,它不能被违背或删除**。

> 跨领域启示:第一性原理的核心是"剥掉所有既定假设,从最基本的事实重新推导"。这与具体领域无关,这也是它能在 Vibe Coding 中格外好用的根本原因。

### 社区反响与使用建议

**社区反响**:

- 社区里有人称它为"**神之 Prompt**"之一
- GitHub 上甚至有人做了专门的 skill 叫 `first-principles`

**使用建议**:

- **不需要装 Skill 或写 System Prompt**
- 在解决问题、修 BUG、让 AI 帮你设计架构的时候,在 Prompt 后面加一句"从第一性原理出发"就够了
- **只要任务稍微复杂一点,这个 Prompt 几乎是万能的**

### 践行鸿沟：知道≠做到（本项目亲身验证的反面案例）

> **核心洞察**：方法论最危险的陷阱不是"不知道"，而是"知道了但没做到"。

**事件背景**：2026-07-09，在完成本文学习分析并沉淀第一性原理模式**仅1小时后**，在执行"文档链接格式更新"这个看起来极其简单的任务时，恰恰犯了文章反复强调要避免的**类比推理错误**——机械套用了最近看到的 `file:///` 绝对路径格式，而没有回到开发规范的基本事实去验证。

**错误链路（完美复刻类比推理）**：

| 步骤 | 行为 | 问题本质 |
|------|------|---------|
| 1 | 看到任务是"格式统一" | 大脑自动归类为"简单任务"，启动快思考 |
| 2 | 从记忆中提取"最近看到的格式" | 检索到 `file:///` 绝对路径（类比来源） |
| 3 | 批量套用到13个文件 | 跳过了"查规范"这个关键验证步骤 |
| 4 | 自信提交 | 过度自信效应："这么简单不会错" |

**三层认知差距揭示**：

```
陈述性知识 ──(需要练习)──→ 程序性知识 ──(需要检查点)──→ 自动化执行
   ↑ 已达到                    ↑ 部分达到                     ↑ 未达到
（能背诵定义）            （被提问时能用）          （简单任务中自动用）
```

**简单任务陷阱**：恰恰是"看起来不用想"的任务最容易出错——复杂任务有Spec、测试、Review等流程保护，简单任务因为"简单"而跳过所有验证，错误被批量复制且不易发现。

**第一性原理修正**：被用户用提问式纠错（"这个判断哪里来的？符合第一性原理吗？"）点醒后，回到基本事实——查开发规范、查现有同类文件——发现应该用相对路径而非绝对路径，立即修正。

**关键教训**：
- 第一性原理不是"知道了就行"的知识，而是需要**强制检查点**的实践
- 越是简单任务，越要有意识启动第一性原理验证
- 方法论内化需要刻意练习+检查点机制，仅靠理解远远不够

> 事件完整复盘：[retrospective-first-principles-analogy-error-20260709/](../../../retrospective/reports/incident-reports/retrospective-first-principles-analogy-error-20260709/README.md)

---

## 对抗式审查深度解析

### Prompt 的具体形式

针对不同工具有两种典型说法:

**Claude Code**:

```
开启 Ultracode(动态工作流,会有 N 个 Agent 进行并发)来对之前开发的功能进行对抗式审查
```

**Codex**:

```
开启多 Agent 帮我进行对抗性审查
```

### 定位

第一性原理保证帮你找到好的方案、找到 BUG 真正本质的解法,但**没办法保证开发完了以后能稳定上线**。对抗式审查解决的就是——**怎么保证 AI 写的代码确实没啥毛病**。

### 执行模式:多 Agent 并发与攻击者视角

**多 Agent 并发**:开启多个 Agent 同时跑,从不同角度审查。

**攻击者视角**:核心是让 Agent 站在"恶意用户"立场审查系统。典型表述:

> 如果我是一个恶意用户,我会提交一个 50MB 的 HTML 来搞崩你的 worker。

这种视角会逼 Agent 主动构造**异常输入、边界数据、极端场景**,把整条调用路径从入口到崩溃全走一遍,找出缺口。

### 典型 BUG 类型

实战案例来自 6 月初 Claude Opus 4.8 和动态工作流上线后,作者对 AIHOT 做的一次大审查——开启近 40 个 Agent,跑了很久,找出 N 个可能的风险。以下是几类典型 BUG:

**案例 1:OOM 死循环**

- **现象**:后台 worker 处理特别大任务时,内存爆了被系统杀掉;自动重试又爆又被杀,陷入**无限循环**。
- **审查路径**:对抗式审查从"恶意用户提交 50MB HTML 搞崩 worker"角度,把整条路径从入口到崩溃全走了一遍,找出缺口。
- **现实验证**:后来真看到过 **100M 的 HTML**。

**案例 2:未来时间污染 BUG**

- **现象**:某信源文章发布时间因时区错误显示为**未来时间**(如明天),文章会排到精选信息流最前面(时间戳最新)。
- **污染链路**:可能被推送 → 进入飞书群 PUSH → 进入 RSS 订阅 → 日报排最前面。**一篇来自未来的文章会污染整个信息流**。
- **为什么自审想不到**:自己写代码根本想不到;但 AI 站在"用奇怪数据搞崩系统"角度,会主动问——"如果发布时间是未来怎么办?"

**其他隐患**:

| 隐患类型 | 说明 |
|---------|------|
| HTML 清洗模块性能炸弹 | 异常 HTML 触发性能问题 |
| 翻译模块同类隐患 | 与 HTML 清洗类似的边界隐患 |
| 部署探活缓存穿透假阳性 | 探活机制被异常数据干扰,产生假阳性 |

### 进阶实践:反例构造五步法(2026-07-11补充)

基于元方法论自举验证的经验沉淀,对抗式审查的系统化执行可采用**反例构造五步法**,尤其适用于规则系统、匹配系统、分类系统、推荐系统:

1. **识别不通过场景**:主动寻找"应该不通过但实际通过"或"应该通过但实际不通过"的案例
2. **四类标准反例模板**:无关输入(完全不相关内容)、边界输入(刚好在阈值上/下)、混合输入(多特征混杂)、对抗输入(故意构造的欺骗性样本)
3. **定义期望结果**:每个反例必须预先明确"正确的处理结果应该是什么"
4. **按影响分级**:高影响(数据污染/系统崩溃)、中影响(功能异常)、低影响(体验问题)
5. **修复后回归验证**:修复后必须用构造的反例集重新跑一遍,确保问题真正解决

> 详细执行SOP见沉淀模式:[adversarial-review-prompt-pattern.md](../../../retrospective/patterns/methodology-patterns/ai-collaboration/adversarial-review-prompt-pattern.md)(L2级验证,含四大攻击者角色定义)

### 工具实践:Claude Code Ultracode 与 Codex 多 Agent

| 工具 | 触发方式 | 行为 |
|------|---------|------|
| **Claude Code** | 开启 Ultracode(动态工作流,会有 N 个 Agent 进行并发) | 自动启动多个 Agent 并发审查 |
| **Codex** | 直接说"开启多 Agent 帮我进行对抗性审查" | 自动开好几个 Agent |

> 作者形容:这是一场**极致且纯粹的攻防战**——一边是构造攻击的 Agent,一边是被攻击的系统。

**效果**:自从用了对抗式审查,作者对自己代码和项目的**信心变得很强**。

---

## 闭环逻辑分析

### 两大 Prompt 的协同关系

第一性原理与对抗式审查并非二选一,而是**闭环互补**:

```
第一性原理(生成层)          对抗式审查(验证层)
       │                         │
       ▼                         ▼
  找到好的方案               保证方案稳健上线
  找到 BUG 本质解法          发现潜在风险与边界
       │                         │
       └───────── 闭环 ──────────┘
                 ▼
          稳定可上线的产品
```

- **第一性原理**保证**做对的事**——方向正确、根因被真正定位
- **对抗式审查**保证**把事做对**——实现稳健、边界被覆盖、能稳定上线

### 定期审查实践

作者现在每 **2-3 周**定期对整个项目进行一次全局性的:

> 从第一性原理出发的对抗式审查

具体做法:让 Agent 从最底层原理出发,并发审查:

- 架构
- 依赖关系
- 代码质量
- 文档对应

**附加价值**:这种全局审查也可用来**测试新模型能力**——每次都能挑出之前没注意到的**技术债**和**潜在风险**。

---

## 延伸应用

这两个 Prompt 的核心逻辑跟具体领域无关,只是在 Vibe Coding 领域格外好用。它们可以无缝迁移到其他场景:

### 写作审查

让 AI 帮你对抗式审查文章,从以下维度挑毛病:

- 逻辑漏洞
- 事实准确性
- 论证力度

> 比起"帮我看看这篇文章怎么样",对抗式审查有用太多。

### 商业方案审视

让 AI 从第一性原理出发审视方案:

- 剥掉所有假设
- 直接质问核心逻辑是否成立

### 人生决策(如要不要换工作)

两步组合拳:

1. **先从第一性原理想清楚**——自己到底想要什么
2. **再用对抗式审查**——让 AI 专门找思考中的盲点和下意识回避的风险

### 核心逻辑提炼

| Prompt | 核心逻辑(领域无关) |
|--------|---------------------|
| 第一性原理 | 回到最根本的事实重新推导 |
| 对抗式审查 | 你永远需要一个站在你对面的力量来告诉你,你可能是错的 |

---

## 对本项目的启示

以下是可复用到 **SpecWeave 智能体开发**的方法论要点（含2026-07-09亲身践行验证后的更新）:

### 1. 复杂架构设计时使用第一性原理 Prompt

在让 Agent 设计架构、生成方案、定位复杂 BUG 根因时,在 Prompt 后追加"从第一性原理出发"。这能强制打断 Agent 的类比推理,避免它在既有训练数据里"找个差不多的"应付,而是回到问题本质重新推导。

**适用场景**:
- 多智能体协作架构设计
- 复杂 BUG 的根因定位(避免治标不治本)
- 工作流编排方案选型
- vendor 子模块集成方案设计

### 2. 在代码审查工作流中引入对抗式审查

在 SpecWeave 的代码审查工作流中,引入"多 Agent 对抗式审查"环节,让 Agent 站在攻击者/异常输入视角审查代码,主动构造边界数据与极端场景。

**关注点**:
- 异常输入(超大、超长、未来时间、负数、空值)
- 边界场景(OOM、死循环、缓存穿透、假阳性)
- 数据污染链路(一个异常数据如何扩散到整个系统)

### 3. 定期对项目进行全局审查

建立"每 2-3 周一次全局对抗式审查"的治理节奏,让 Agent 从第一性原理出发,并发审查:
- 架构合理性
- 依赖关系健康度
- 代码质量与技术债
- 文档与实现的一致性

**附加用途**:可作为新模型能力的"试金石"——既能挑出技术债,又能评估模型审查能力。

### 4. 闭环思维:生成与验证不可偏废

在 SpecWeave 的标准工作流中,任何"生成"环节(方案设计、代码生成)都应配对应的"验证"环节(对抗式审查、根因复核)。**第一性原理管生成,对抗式审查管验证**,二者缺一不可。

### 5. 建立强制检查点机制（2026-07-09践行新增）

> **来自反面教训**：知道方法论≠自动践行方法论。必须建立**决策前三查**的强制检查点，尤其是在"看起来简单"的任务上。

在做出格式、路径、规范相关决策前，必须执行三查：
1. **查权威文档**：AGENTS.md、对应规范文件实际怎么写的
2. **查现有实例**：项目中同类文件实际用的什么格式（不要只看一个例子）
3. **查本质目标**：这个东西的本质目标是什么？当前选择满足本质目标吗？

**适用范围**：不仅适用于AI Agent，也适用于人类操作者——简单任务恰恰是类比推理最容易自动激活、最需要强制打断的场景。

> 沉淀模式：[pre-decision-three-checks.md](../../../retrospective/patterns/methodology-patterns/ai-collaboration/pre-decision-three-checks.md)

### 6. 简单任务慢做原则（2026-07-09践行新增）

越是"看起来简单、不用想"的任务，越要有意识放慢速度，主动执行验证步骤。简单任务的错误率可能高于复杂任务，因为：
- 复杂任务有Spec、测试、Review等多重流程保护
- 简单任务因为"简单"而跳过所有验证
- 简单任务往往批量执行，错误被快速复制
- 简单任务的错误不影响核心功能，更不容易被发现

> 沉淀模式：[simple-task-high-risk.md](../../../retrospective/patterns/methodology-patterns/governance-strategy/simple-task-high-risk.md)（简单任务高风险定律）

### 7. 提问式纠错优于直接指正（2026-07-09践行新增）

当需要指出他人/Agent的错误时，优先使用苏格拉底式提问而非直接批评：
- 不直接说"你错了"，而是问"这个判断哪里来的？符合第一性原理吗？"
- 不触发防御心理，引导对方自己发现错误
- 这本身就是第一性原理Prompt的正确用法——不是给答案，而是强制启动"回到基本事实"的思考过程
- 自己发现的错误记忆更深刻，同时强化了方法论的应用

> 沉淀模式：[socratic-questioning-correction.md](../../../retrospective/patterns/methodology-patterns/ai-collaboration/socratic-questioning-correction.md)

### 8. 践行鸿沟需要递归练习（2026-07-11补充）

方法论内化不是一次性事件，而是需要递归练习的过程：
- 每次犯错后不仅要修正结果，更要复盘"为什么第一性原理没被触发"
- 建立错误→复盘→更新检查点→再次验证的闭环
- 简单任务是最好的练习场——因为简单任务最容易暴露践行鸿沟

> 沉淀模式：[practice-gap-recursive-practice.md](../../../retrospective/patterns/methodology-patterns/governance-strategy/practice-gap-recursive-practice.md)

### 9. 跨领域复用:Prompt 方法论可迁移到非编码场景

SpecWeave 智能体在协助用户做方案审视、决策推演时,同样可以应用这两个 Prompt:
- 文档/方案审稿:对抗式审查逻辑漏洞与事实准确性
- 决策推演:第一性原理 + 对抗式审查组合,定位真实需求 + 找盲点
- 纠错协作:用提问式引导对方自我发现，而非直接指正

### 10. 产品功能定义的第一性原理延伸（2026-07-11补充）

第一性原理不仅适用于代码BUG定位和架构设计，在产品功能定义领域同样威力巨大——通过"悬置→拆解→质疑→重构"四步法，可以避免竞品类比思维陷阱，从用户本质需求出发重新定义功能。这已沉淀为独立的方法论模式。

> 沉淀模式：[first-principles-feature-analysis.md](../../../retrospective/patterns/methodology-patterns/research-knowledge/first-principles-feature-analysis.md)（第一性原理功能分析法，悬置→拆解→质疑→重构四步SOP）

---

## FAQ

**Q1:这两个 Prompt 适用于哪些场景?**

A:第一性原理适用于**任何需要生成方案或定位根因**的复杂任务——架构设计、BUG 修复、方案选型、根因分析等;对抗式审查适用于**任何需要验证代码/方案稳健性**的场景——上线前审查、定期技术债排查、新模型能力测试等。两个 Prompt 的核心逻辑与具体领域无关,可迁移到写作、商业方案、人生决策等非编码场景。

**Q2:需要安装 Skill 吗?**

A:**不需要**。第一性原理只需在 Prompt 后加一句"从第一性原理出发"即可;对抗式审查在 Claude Code 中开启 Ultracode(动态工作流),或在 Codex 中直接说"开启多 Agent 帮我进行对抗性审查"。虽然 GitHub 上有 `first-principles` 这样的 Skill,但作者明确建议:不需要装 Skill 或写 System Prompt,直接在 Prompt 里加一句话就够了。

**Q3:多久审查一次?**

A:作者实践是每 **2-3 周**对整个项目进行一次全局性的"从第一性原理出发的对抗式审查"。审查范围包括架构、依赖关系、代码质量、文档对应等。这种定期审查也可作为新模型能力的测试手段。

**Q4:第一性原理 Prompt 为什么这么有效?**

A:因为当前 AI 默认做的是**类比推理**——从训练数据找类似案例给你一个"差不多"的答案,跳过了"这个问题真的应该这么解吗?"的关键步骤。"从第一性原理出发"这七个字**强制打断类比推理**,逼 AI 回到问题本质,从最基本的事实重新推导。

**Q5:对抗式审查和普通代码审查有什么区别?**

A:普通代码审查往往是"检查有没有问题",视角是中性的;对抗式审查是**主动攻击**——让 Agent 站在恶意用户立场,主动构造异常输入(50MB HTML、未来时间、负数等)去"搞崩"系统,把整条调用路径从入口到崩溃全走一遍。它能发现自审想不到的边界与污染链路问题。

**Q6:两个 Prompt 必须一起用吗?**

A:不必须,但**组合使用效果最佳**。第一性原理管生成,对抗式审查管验证,二者构成完整闭环。单独用第一性原理能保证方向正确但无法保证稳健上线;单独用对抗式审查能发现风险但可能治标不治本。作者的"定期全局审查"实践就是两者合一:"从第一性原理出发的对抗式审查"。

**Q7:我"知道"第一性原理了，为什么还会犯类比推理错误?**

A:这是**践行鸿沟**问题——认知科学中，知识分为三层：①陈述性知识（能背诵定义）→②程序性知识（被提问时能用）→③自动化执行（无需思考就做）。刚学习的方法论只达到前两层，简单任务时大脑自动走直觉捷径（System 1快思考），完全不会触发第一性原理检查。解决方法不是"更努力地记住"，而是建立**强制检查点机制**——在决策前强制执行三查（查权威、查实例、查本质），即使是简单任务也不跳过。

**Q8:简单任务也需要用第一性原理吗?**

A:**恰恰是简单任务最需要**。卡兹克原文说"只要任务稍微复杂一点，这个Prompt几乎是万能的"，但本项目2026-07-09的反面案例揭示了一个更深刻的真相：复杂任务有流程保护（Spec、测试、Review），简单任务因为"看起来不用想"而跳过所有验证，反而错误率更高。简单任务不需要对AI追加Prompt，但需要人类操作者自己建立检查点，主动打断直觉类比。

**Q9:如何避免"知道方法论但做不到"?**

A:三个关键措施：①**建立强制检查点**——决策前三查（查权威文档、查现有实例、查本质目标），形成肌肉记忆；②**简单任务慢做**——越是觉得"不用想"的任务，越要有意识放慢速度做验证；③**从错误中学习**——每次犯错都复盘"为什么第一性原理没被触发"，而不是只改结果。方法论内化需要刻意练习，不是"理解了"就自动会用。

**Q10:第一性原理模式在本项目有沉淀吗?**

A:有。基于本次学习和后续多次践行验证（含反面案例+元方法论自举验证），已沉淀**9个可复用方法论模式**到模式库：

**核心两大基石（L2/L3级）**：
- [first-principles-prompt-pattern.md](../../../retrospective/patterns/methodology-patterns/ai-collaboration/first-principles-prompt-pattern.md)（第一性原理Prompt模式，L3级验证）
- [adversarial-review-prompt-pattern.md](../../../retrospective/patterns/methodology-patterns/ai-collaboration/adversarial-review-prompt-pattern.md)（对抗式审查Prompt模式，L2级验证，含反例构造五步法）

**践行鸿沟配套治理模式（从2026-07-09反面案例沉淀）**：
- [pre-decision-three-checks.md](../../../retrospective/patterns/methodology-patterns/ai-collaboration/pre-decision-three-checks.md)（决策前三查强制检查点）
- [simple-task-high-risk.md](../../../retrospective/patterns/methodology-patterns/governance-strategy/simple-task-high-risk.md)（简单任务高风险定律）
- [socratic-questioning-correction.md](../../../retrospective/patterns/methodology-patterns/ai-collaboration/socratic-questioning-correction.md)（苏格拉底式提问纠错法）
- [practice-gap-recursive-practice.md](../../../retrospective/patterns/methodology-patterns/governance-strategy/practice-gap-recursive-practice.md)（践行鸿沟递归练习法）

**领域延伸应用模式**：
- [first-principles-feature-analysis.md](../../../retrospective/patterns/methodology-patterns/research-knowledge/first-principles-feature-analysis.md)（第一性原理功能分析法，产品功能定义四步SOP，L1实验性）
- [defuddle-web-extraction-preferred.md](../../../retrospective/patterns/methodology-patterns/tools-automation/defuddle-web-extraction-preferred.md)（defuddle优先提取模式，L3级验证）
- [medium-task-merged-delegation-strategy.md](../../../retrospective/patterns/methodology-patterns/ai-collaboration/medium-task-merged-delegation-strategy.md)（中等任务合并委派策略，L2级验证）

---

## 延伸资源

### 原文与作者

- **原文链接**:https://mp.weixin.qq.com/s/umPqTD_-IubbhXIgiS47eQ
- **公众号**:数字生命卡兹克
- **作者产品**:AIHOT(最近一周请求量超千万,Skill 调用量是网页端 10 倍以上)

### 相关概念

- **亚里士多德第一性原理**:每个系统中存在一个最基本的命题,它不能被违背或删除。这是"第一性原理"思想的哲学源头。
- **马斯克 SpaceX 案例**:从材料成本(铝合金、碳纤维、航空级燃料)重新推导火箭制造成本,发射成本降 90%。
- **类比推理 vs 演绎推理**:AI 默认走类比推理(从训练数据找相似案例),第一性原理强制走演绎推理(从基本事实重新推导)。
- **多 Agent 并发审查**:Claude Code 的 Ultracode 动态工作流、Codex 的多 Agent 模式,均为对抗式审查的执行载体。
- **GitHub `first-principles` Skill**:社区基于该理念封装的 Skill,但作者建议直接在 Prompt 中使用即可,无需安装。

### SpecWeave 内部关联

- 代码审查工作流:[.agents/workflows/](../../../../workflows/README.md)
- 可复用模式库:[patterns/](../../../retrospective/patterns/README.md)
- 复盘体系:[retrospective/](../../../retrospective/README.md)
- 开发规范:[development-standards.md](../../../development-standards.md)
- 关联复盘报告:[retrospective-vibe-coding-prompts-learning-analysis-20260704/](../../../retrospective/reports/insight-extraction/external-learning/retrospective-vibe-coding-prompts-learning-analysis-20260704/README.md)
- 践行反面案例复盘:[retrospective-first-principles-analogy-error-20260709/](../../../retrospective/reports/incident-reports/retrospective-first-principles-analogy-error-20260709/README.md)（学完1小时即犯类比推理错误的教训）
- 核心基石模式1:[first-principles-prompt-pattern.md](../../../retrospective/patterns/methodology-patterns/ai-collaboration/first-principles-prompt-pattern.md)（L3级验证）
- 核心基石模式2:[adversarial-review-prompt-pattern.md](../../../retrospective/patterns/methodology-patterns/ai-collaboration/adversarial-review-prompt-pattern.md)（L2级验证，含反例构造五步法）
- 践行配套模式1:[pre-decision-three-checks.md](../../../retrospective/patterns/methodology-patterns/ai-collaboration/pre-decision-three-checks.md)（决策前三查）
- 践行配套模式2:[simple-task-high-risk.md](../../../retrospective/patterns/methodology-patterns/governance-strategy/simple-task-high-risk.md)（简单任务高风险定律）
- 践行配套模式3:[socratic-questioning-correction.md](../../../retrospective/patterns/methodology-patterns/ai-collaboration/socratic-questioning-correction.md)（苏格拉底式提问纠错）
- 践行配套模式4:[practice-gap-recursive-practice.md](../../../retrospective/patterns/methodology-patterns/governance-strategy/practice-gap-recursive-practice.md)（践行鸿沟递归练习）
- 领域延伸模式1:[first-principles-feature-analysis.md](../../../retrospective/patterns/methodology-patterns/research-knowledge/first-principles-feature-analysis.md)（第一性原理功能分析法，L1实验性）
- 领域延伸模式2:[defuddle-web-extraction-preferred.md](../../../retrospective/patterns/methodology-patterns/tools-automation/defuddle-web-extraction-preferred.md)（defuddle优先提取，L3级验证）
- 领域延伸模式3:[medium-task-merged-delegation-strategy.md](../../../retrospective/patterns/methodology-patterns/ai-collaboration/medium-task-merged-delegation-strategy.md)（中等任务合并委派，L2级验证）

---

## 参考资料

1. 卡兹克. *Vibe Coding 两大神级 Prompt*. 微信公众号「数字生命卡兹克」. https://mp.weixin.qq.com/s/umPqTD_-IubbhXIgiS47eQ
2. AIHOT 产品(作者自述用 Vibe Coding 方式由非程序员构建,周请求量超千万)
3. Claude Code Ultracode 动态工作流(Claude Opus 4.8 上线后的多 Agent 并发能力)
4. 亚里士多德第一性原理(哲学源头)
5. 马斯克 SpaceX 火箭成本重构案例(发射成本降 90%)

---

## Changelog

<!-- changelog -->
- 2026-07-04 | create | 初始创建:学习分析卡兹克《Vibe Coding 两大神级 Prompt》一文,提炼第一性原理与对抗式审查两大方法论,并落地到 SpecWeave 智能体开发的启示要点(v1.0)
- 2026-07-09 | update | 格式标准化:修复frontmatter格式问题、补充关联复盘报告和模式链接、内部链接使用相对路径（遵循开发规范）、更新日期(v1.1)
- 2026-07-10 | update | 践行验证更新（第一性原理深化）:新增"践行鸿沟：知道≠做到"章节，记录2026-07-09本项目类比错误反面案例；新增"决策前三查"强制检查点、"简单任务慢做"、"提问式纠错"三项启示；补充4个已沉淀模式完整链接；新增FAQ Q7-Q10解答践行相关问题；更新验证记录为3次（含L3级本项目反面验证）(v1.2)
- 2026-07-11 | update | 元方法论自举验证更新:新增"进阶实践:反例构造五步法"章节（对抗式审查系统化方法）；启示章节新增第8点"践行鸿沟递归练习"、第10点"产品功能定义的第一性原理延伸"；启示5-7点补充沉淀模式链接；Q10更新为9个沉淀模式分类列表（核心基石/践行配套/领域延伸三类）；内部关联链接更新为9个模式完整清单；验证记录新增第4次（L2级元方法论自举验证）；对抗式审查模式成熟度升级至L2(v1.3)
