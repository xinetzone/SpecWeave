---
id: "longcat-agent-learning-wiki-07"
title: "常见问题（FAQ）"
source: "https://mp.weixin.qq.com/s/ymt9W64FD5IwCDNeQFuheA"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/02-agent-engineering-methodology/longcat-agent-learning-wiki/07-faq.toml"
---
## 八、常见问题（FAQ）

### Q1: LongCat-2.0是免费的吗？
**A**: 原文中未明确说明定价策略。LongCat-2.0通过OpenRouter和自有API平台提供服务，具体费用请参考LongCat官方平台的定价页面。值得注意的是，其缓存命中不计费，且token消耗比GPT-5.5少约三分之一，在成本方面具有优势。

### Q2: LongCat-2.0只能用于Claude Code吗？
**A**: 不是。LongCat-2.0已适配多种主流编程工具，包括Claude Code、OpenClaw、Hermes等。只要工具支持通过API Key和Base URL配置自定义模型，理论上都可以接入LongCat-2.0。

### Q3: MoE架构和普通模型有什么区别？
**A**: 普通稠密模型每个token都会激活所有参数，计算成本固定。MoE（混合专家）模型包含多个专家子网络，每次推理只激活与当前任务最相关的少数专家。LongCat-2.0总参数1.6T，但每次只激活约480亿参数，在保持强大能力的同时大幅降低推理成本。

### Q4: 1M上下文在实际编程中够用吗？
**A**: 对于大多数编程项目来说，1M上下文已经足够覆盖整个项目目录的代码、配置文件、终端输出和错误日志。在本次实测中，BI数据看板项目（包含前端、后端、数据库的完整SaaS MVP系统）在1M上下文内运行良好。

### Q5: LongCat-2.0的缓存机制如何工作？
**A**: 在Agent编程的多轮对话中，大量上下文是重复的（项目文件、配置信息等）。LongCat-2.0会缓存这些重复内容，后续轮次中如果命中缓存，这部分内容不消耗token。这解释了为什么在同类任务中，LongCat-2.0的token消耗比GPT-5.5少约三分之一。

### Q6: LongCat-2.0的开发体验和Claude原生模型相比如何？
**A**: 根据原文作者的实测，使用Claude Code + LongCat-2.0的组合开发完整前后端网站"还是比较丝滑的"。整个开发过程约10多分钟，过程中Agent能够拆解任务、搭建项目结构、持续修改代码、遇到报错后自动修复。不过原文也提到"中间也不是一次就完美"，需要Agent持续迭代。

### Q7: 如何判断一个模型是否适合Agent编程？
**A**: 关键指标包括：长上下文能力（能否处理整个项目代码）、工具调用能力（能否执行命令、读写文件）、错误分析能力（能否理解报错并定位问题）、持续迭代能力（能否形成Loop Engineering闭环）。此外，token效率也是重要考量因素。

### Q8: LongCat-2.0的国产算力训练有什么意义？
**A**: 在国际芯片供应链受限的背景下，LongCat-2.0证明了使用国产算力集群完全可以训练出具有国际竞争力的大模型。5万余国产算力芯片、35万亿tokens的训练规模，展示了国产算力在大模型训练中的可行性和规模化能力。