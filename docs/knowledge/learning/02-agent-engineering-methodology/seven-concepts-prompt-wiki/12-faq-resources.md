---
id: "seven-concepts-faq"
title: "12、常见问题与资源索引"
category: "reference"
date: "2026-07-13"
version: "1.0"
status: "completed"
source: "实践问题汇总"
---

# 常见问题与资源索引

---

## 1. 章节引言

理论学习和模板参考之外，实践中你一定会遇到很多具体问题。本章收集了社区反馈中最常见的12个问题，每个给出简洁实用的回答；同时整理了官方资源、延伸阅读和工具推荐，方便你深入学习和日常使用。

> 🟢 **来源标注**：FAQ来自大量实践问题汇总，资源链接均为公开可访问的官方资料。

---

## 2. ❓ FAQ常见问题（12个）

---

### Q1：新写法是不是完全不需要角色设定了？

**A**：不是完全不需要，而是"不滥用"。角色设定只在影响**判断视角**时才有用——比如"站在新用户角度Review这个功能""从CFO视角评估预算"。上来就写"20年资深专家"这种标签完全没用，模型能力来自训练数据，不来自你贴的头衔。简单任务不需要角色，需要特定视角时再用。相关章节→[10-anti-patterns.md](10-anti-patterns.md)

---

### Q2：为什么我的Prompt按新写法写了还是效果不好？

**A**：大概率是四个地方出了问题：1.目标还是不够具体（检查有没有形容词、有没有完成标准）；2.关键上下文没给（你知道但模型不可能知道的信息）；3.事实核验没要求（模型自己脑补了数据）；4.任务太复杂没分步（复杂任务要拆，要设Checkpoint）。先用09章的五问清单逐条过一遍，通常能找到问题。相关章节→[09-checklists-templates.md](09-checklists-templates.md)

---

### Q3：GPT-4/Claude/Gemini这些旧模型也适用新写法吗？

**A**：核心原则适用，但细节有差异。GPT-4/Claude 3等模型零样本能力已经不错，GCOB框架完全适用；但特别老的模型（GPT-3.5及更早）推理能力弱，可能还是需要少量示例（Few-shot）和更明确的步骤指引。模型越新，越不需要教它怎么思考，越应该聚焦在"说清你要什么"。

---

### Q4：简单任务真的不需要五段结构吗？

**A**：真的不需要。"翻译一下这句话""2+2等于几"这种简单任务，1-2句话说清楚就行，硬套五段式是过度工程化，浪费Token还稀释重点。判断标准：你给一个同事说这件事，如果10秒能说清，就1-2句话写；如果需要解释背景、说清楚交付要求，再用结构。相关章节→[06-chat-scenarios.md](06-chat-scenarios.md)

---

### Q5：如何判断任务复杂度该用多长的Prompt？

**A**：四级判断法：1.简单（1-2句话）：翻译、润色、简单问答；2.普通（Context+Request+Format三段）：写文案、解释概念、简单总结；3.复杂（完整五段+Checkpoint）：研究报告、长文档、专业内容；4.Agent（六段+白名单+停止条件）：Codex写代码、多工具调用任务。拿不准时先从短的开始，不够再加。相关章节→[13-quick-reference.md](13-quick-reference.md)

---

### Q6：Checkpoint具体该怎么设置？有通用模板吗？

**A**：Checkpoint就是列一个"遇到这些情况停下来问我"的清单，通用三类：1.信息不足/不确定时（缺数据、多个方案选不出、需要你内部才能知道的信息）；2.越界风险时（需要改白名单外的文件、需要装包、需要改核心配置）；3.出错/冲突时（工具调用连续失败、数据冲突、结果和预期差很多）。把你担心的"它可能会自己瞎搞"的情况列出来就行。相关章节→[04-new-paradigm-rules.md](04-new-paradigm-rules.md)

---

### Q7：Codex里按Enter(Steer)和Tab(Queue)怎么选？

**A**：简单判断：方向对按Tab（Queue，让它继续），方向错按Enter（Steer，打断纠正）。具体：模型正在写的内容你认可、希望继续往下做→Tab；模型写偏了、你发现它理解错了、需要补充新要求→Enter打断，说清楚哪里不对、要怎么改。不要等它全部写完一大段再纠正，发现不对立刻打断效率更高。相关章节→[08-codex-scenarios.md](08-codex-scenarios.md)

---

### Q8：模型总是幻觉事实怎么办？

**A**：不要说"不要编"，这没用。要做三件事：1.明确数据来源要求："只用附件里的数据""数据标注来源年份"；2.明确信息不足时的处理方式："不确定标[待确认]""需要更多信息就停下来问我"；3.只问你能验证的问题，不要问太偏门、网上信息少的内容然后指望模型全对。幻觉是模型固有特性，你要做的是建立核验机制，不是要求模型"不犯错"。相关章节→[04-new-paradigm-rules.md](04-new-paradigm-rules.md)

---

### Q9：多轮对话中上下文越来越长怎么处理？

**A**：三个技巧：1.不要每轮重发完整Prompt，第一轮发全，后续只说补充/修改；2.对话太长（超过10轮或内容很多）时，主动总结一下当前进展和关键决策，再继续，防止早期内容被截断；3.开新对话时，先花100字把之前的关键背景、已经确定的内容列一下，不要当模型还记得。模型不是无限记忆，主动管理上下文是你的责任。相关章节→[10-anti-patterns.md](10-anti-patterns.md)

---

### Q10：中文Prompt和英文Prompt效果有差异吗？

**A**：目前多数模型训练数据英文占比更高，英文Prompt在复杂推理上可能略好，但差距已经很小，日常使用完全感知不到。如果你和输出受众都是中文，直接写中文Prompt即可，不用硬写英文。真正影响效果的不是语言，而是你有没有说清楚目标、上下文、输出要求——中文写清楚了一样效果好。

---

### Q11：我需要专门学Prompt Engineering吗？还是直接写就行？

**A**：不需要专门"学"很久，但核心原则要掌握。本Wiki讲的内容就够了——GCOB四要素、五问检查、三场景区别、Codex安全原则，这些是底层逻辑，掌握了不需要记几百条技巧。不用去背各种"神级Prompt""魔法咒语"，那些大多是旧时代遗留，模型越新越没用。把核心原则理解透，多实践多复盘，比记100个模板有用。相关章节→[01-paradigm-shift.md](01-paradigm-shift.md)

---

### Q12：七概念方法论和其他Prompt框架是什么关系？

**A**：七概念（R-I-E-C-A-F-V）是**治理层**方法论，解决"怎么持续写对Prompt、怎么沉淀经验"的问题；GCOB是**写作层**框架，解决"单次Prompt具体怎么写"的问题。两者是互补关系，不是竞争关系。你可以把CRISPE、ICE等其他框架当模板参考，但核心记住GCOB+五问检查就够了，框架太多反而容易乱。本方法论的核心是"少即是多"——用最少的原则覆盖最多场景。相关章节→[02-seven-concepts-mapping.md](02-seven-concepts-mapping.md)

---

## 3. 📚 官方资源与延伸阅读

---

### 3.1 原始参考资料

> 🔵 **B级来源**：以下为方法论原始参考文章

- 微信公众号文章：《GPT-5.6时代的Prompt新写法》（待补充链接）
- 微信公众号文章：《我写了3000条Prompt后总结的反模式》（待补充链接）

---

### 3.2 OpenAI官方Prompting指南

- OpenAI Prompt Engineering Guide：https://platform.openai.com/docs/guides/prompt-engineering
- OpenAI Best Practices for Prompt Engineering：https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-openai-api

> 🟢 **A级来源**：官方指南是最权威的参考，建议通读一遍。

---

### 3.3 SpecWeave七概念方法论相关文档

- [00-overview.md](00-overview.md) - 方法论总览
- [03-gcob-framework.md](03-gcob-framework.md) - GCOB四要素框架详解
- [04-new-paradigm-rules.md](04-new-paradigm-rules.md) - 新范式10条核心规则
- [09-checklists-templates.md](09-checklists-templates.md) - 检查清单与模板库
- [10-anti-patterns.md](10-anti-patterns.md) - 25个反模式避坑指南

---

### 3.4 各场景快速入口

| 场景 | 对应章节 | 核心要点 |
|------|---------|---------|
| 日常聊天/简单问答 | [06-chat-scenarios.md](06-chat-scenarios.md) | 越简单越好，不要过度设计 |
| 写报告/文档/专业内容 | [07-work-scenarios.md](07-work-scenarios.md) | 五段结构，注意事实核验 |
| Codex写代码/Agent任务 | [08-codex-scenarios.md](08-codex-scenarios.md) | 白名单边界，Checkpoint，先计划后动手 |

---

## 4. 🛠️ 工具推荐

---

### 4.1 Prompt调试/测试工具

- **OpenAI Playground**（https://platform.openai.com/playground）：官方调试工具，可调整参数、对比不同模型输出
- **Anthropic Console**（https://console.anthropic.com）：Claude官方调试界面
- **PromptLayer**（https://promptlayer.com）：Prompt版本管理和A/B测试工具

---

### 4.2 Token计数工具

- **OpenAI Tokenizer**（https://platform.openai.com/tokenizer）：官方Token计数器，可视化展示Token拆分
- **tiktoken**（Python库）：本地Token计数，可集成到脚本中：`pip install tiktoken`
- 简单估算：1个Token ≈ 0.75英文单词 ≈ 0.5汉字

---

### 4.3 相关CLI工具

- **Trae IDE**：内置AI编程助手，原生支持Steer/Queue交互模式（本方法论Codex场景最佳实践环境）
- **Cursor**：AI-first代码编辑器，支持类似的Agent交互模式
- **jq**：命令行JSON处理工具，处理API返回结果很方便

---

## 5. 本章小结

### 5.1 核心要点回顾

1. **角色不滥用**：只有影响判断视角时才用角色设定
2. **效果不好查五问**：目标、完成标准、上下文、边界、停止条件
3. **不强行套结构**：简单任务1-2句话说清就行
4. **幻觉靠机制不靠要求**：明确数据来源和信息不足处理方式，不是说"不要编"
5. **主动管理上下文**：多轮对话注意总结，开新对话补背景

### 5.2 学习建议

- FAQ里的问题都是实践中高频踩的坑，遇到问题先回来查
- 官方指南是最权威的，建议抽时间通读一遍OpenAI官方Prompt指南
- 工具只是辅助，核心还是把GCOB四要素理解透

### 5.3 下一步

学完前面所有内容，最后一章是整份Wiki的精华浓缩——一页纸速查表，打印出来贴在显示器旁边，写Prompt时快速查阅。

👉 继续阅读：[13-quick-reference.md](13-quick-reference.md)（快速参考速查表·一页纸）
👉 返回上一章：[11-glossary.md](11-glossary.md)（术语表）

---

*本文件版本：v1.0 | 创建日期：2026-07-13 | 状态：🚧 建设中 | 来源：实践问题汇总*
