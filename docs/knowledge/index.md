# 📚 知识库

本目录汇集 SpecWeave 项目沉淀的**外部知识学习成果与技术研究**，包括对主流 AI Agent 平台/工具的系统学习 Wiki、AI 工程化深度分析、算法艺术探索，以及深度学习原子化设计研究。

与 [复盘与模式库](../retrospective/index.md)（项目自身经验沉淀）和 [技术文档](../tech/index.md)（本项目使用说明）形成互补。

## 📂 内容分类

```{toctree}
:maxdepth: 2
:caption: 知识库
:hidden:

ai-engineering/index
algorithmic-art/index
best-practices/index
cake-cutting-rule/index
categories/index
decisions/index
docs-separation-guide/index
engineering/index
jieban-ai-monetization/index
mdi/index
mdi-research/index
mindfulness-positivity/index
myst-unified-ecosystem/index
operations/index
opensource-contest/index
platform/index
quality-assurance/index
scripts/index
tags/index
tech/index
templates/index
trae-feature-watch/index
troubleshooting/index
anti-crawler-strategy-playbook
caffe-ffi-perf-instrumentation-template
category-index
governance-methodology-architecture
log
mdi-research-report
mdi-spec-v1.0
stage-guardrails-guide
template
three-layer-routing
VENDOR-INTEGRATION
```

| 分类 | 说明 | 入门推荐 |
|------|------|---------|
| **[Agent 平台与工具知识包（bundles）](../../projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/index.md)** | 主流 AI Agent 开发平台与工具的系统学习知识包（DeepSeek Harness、The Agency、Open Code Review 等 10+ 个包） | [DeepSeek Harness 完全指南](../../projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/deepseek-harness/index.md) |
| **[OKF（开放知识格式）主题导航](../../projects/awesome-okf-xs/doc/bundles/meta/okf-ecosystem/index.md)** | OKF 格式规范 + OKF 工具链的统一主题索引（横跨协议接口与工具平台） | [OKF 主题导航](../../projects/awesome-okf-xs/doc/bundles/meta/okf-ecosystem/index.md) |
| **[Python 3.14 标准库知识包](../../projects/awesome-okf-xs/doc/bundles/jishu/python/stdlib/index.md)** | Python 3.14 标准库系统学习（contextlib / contextvars / sys.monitoring / annotationlib / dataclasses / traceback） | [概述](../../projects/awesome-okf-xs/doc/bundles/jishu/python/stdlib/index.md) |
| **[AI Engineering](ai-engineering/index.md)** | AI Agent 工程化领域知识库（Loop Engineering、Karpathy LLM Wiki 分析等） | [Loop Engineering 知识库](ai-engineering/concepts/loop-engineering-knowledge-base.md) |
| **AI 教育** | AI 教育智能体与教育科技学习成果（OpenMAIC 知识包等） | [OpenMAIC 知识包](ai-education/openmaic/index.md) |
| **[开源赛事](opensource-contest/index.md)** | 开源竞赛与政策型开发者大赛的参赛知识包（规则、赛程、评审机制、备赛方法论） | [2026 上海开源软件应用创新大赛知识包](opensource-contest/os2026-shanghai/index.md) |
| **算法艺术** | 生成式艺术与算法创意探索（Atomic Emergence 等） | [Atomic Emergence 哲学](algorithmic-art/atomic-emergence/concepts/philosophy.md) |
| **工程化研究** | 深度学习原子化设计等工程方法论研究 | [AI Agent 原子化设计分析](engineering/deep-learning-atomic-design/concepts/ai-agent-atomic-design-analysis.md) |
| **[正念与正面辨析](mindfulness-positivity/index.md)** | 心智概念知识包：正念（看见）与正面/积极心态（改写）的双教程、联系与区别，及「先接纳后重构」整合模式 | [正念教程](mindfulness-positivity/concepts/01-zheng-nian-mindfulness.md) · [正面教程](mindfulness-positivity/concepts/02-zheng-mian-positivity.md) · [联系与区别](mindfulness-positivity/concepts/03-connection-and-differences.md) |
| **[切蛋糕法则](cake-cutting-rule/index.md)** | 公平分割方法论知识包：数学公平分割理论（你切我选/修剪法/移动刀/无嫉妒）、机制设计解读（切选分离与利益对齐）、职场处世应用（做蛋糕 vs 切蛋糕、动态股权），附实战示例与信源台账 | [01 数学公平分割理论](cake-cutting-rule/concepts/01-fair-division-theory.md) · [02 机制设计解读](cake-cutting-rule/concepts/02-you-cut-i-choose-mechanism.md) · [03 职场与处世应用](cake-cutting-rule/concepts/03-maker-vs-cutter-workplace.md) |
| **[结伴 × AI 变现](jieban-ai-monetization/index.md)** | 行动知识包：高信任社群如何让成员在不消耗信任的前提下获得 AI 变现能力——双主体三元组诊断（真问题/真需求/真目标）、三域飞轮模式（群内零交易、站外赚钱、回站只讲含失败字段的案例）、可直接贴群公告的《愈多案例回流公约》与 90 天核对指标 | [三元组诊断](jieban-ai-monetization/concepts/02-real-problem-need-goal.md) · [案例回流公约](jieban-ai-monetization/concepts/04-case-reflow-covenant.md) |
| **[三元组探究（OKF bundle）](../../projects/awesome-okf-xs/doc/bundles/guoxue/laozi/dao-san-triads/index.md)** | 心智/行动知识包：从「三」之本体论、时间三分到两组行动三元组，收敛为七条可当场判定的行动原则（2026-10-03 起归档于 OKF bundles，单一可信源） | [生存指南](../../projects/awesome-okf-xs/doc/bundles/guoxue/laozi/dao-san-triads/concepts/04-survival-guide.md) · [「三」本体论](../../projects/awesome-okf-xs/doc/bundles/guoxue/laozi/dao-san-triads/concepts/01-san-yi-birth.md) |
| **[TRAE 生态特性监测](trae-feature-watch/index.md)** | 每周例行追踪官方更新日志、文档新特性、TraeWork 设计库与本地插件/skills 清单变化 | [最新一期周报（2026-10-01）](trae-feature-watch/2026-10-01-trae-feature-watch.md) |

## 🎯 如何使用

- **刚接触 AI Agent 开发？** 从 [Agent 平台与工具知识包](../../projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/index.md) 开始，选择一个感兴趣的框架系统学习
- **想了解 AI 工程化方法论？** 阅读 [AI Engineering](ai-engineering/index.md) 下的 Loop Engineering 等知识库
- **想寻找可复用模式？** 前往 [复盘与模式库](../retrospective/index.md) 获取项目自身沉淀的最佳实践与反模式

## 接入约定

> 新增知识库文档时：
>
> 1. 按分类放入对应子目录（ai-engineering/algorithmic-art/engineering 等）；系统化学习 Wiki 一律沉淀至 [projects/awesome-okf-xs/doc/bundles/](../../projects/awesome-okf-xs/doc/bundles/index.md)（原 learning/ 板块已于 2026-09 迁移至此）；
> 2. 新增分类或重要 Wiki 时，在本页表格中追加条目；
> 3. 学习 Wiki 遵循"每个工具一个独立原子目录"的规范，使用 `NN-topic.md` 编号命名。