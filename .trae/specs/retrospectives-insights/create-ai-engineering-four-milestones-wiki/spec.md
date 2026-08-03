# AI工程四个路标 Wiki教程 Spec

## 1. 资源来源
- 原始URL：https://mp.weixin.qq.com/s/eeB14yOtDU6akQUp0Mkauw
- 资源类型：微信公众号文章（行业洞察/技术趋势分析）
- 作者/来源：AllenTang
- 提取时间：2026-07-04
- 分析报告：已完成（见对话中的双层结构分析报告 + spec目录 retrospective.md）

## 2. 核心主题与目标
- **一句话总结**：AI工程领域接连涌现的四个概念（Prompt、Context、Harness、Loop Engineering）沿"模型变强→系统瓶颈被迫向外移动一层"主线串联，其中Harness是将工程重心从"调教模型"转向"设计模型外部世界"的关键一跃。
- **学习目标**：读者学完后能够：
  1. 理解"瓶颈外移"这一AI工程演进的底层规律
  2. 区分Prompt/Context/Harness/Loop四个概念各自解决的瓶颈
  3. 掌握Harness工程化的复利式方法论（错误即资产、修补必沉淀）
  4. 理解"层层包含"关系，避免"新概念取代旧概念"的误区
  5. 应用4个可复用认知模型诊断自己的AI Agent项目
- **目标读者**：AI工程师、Agent开发者、技术决策者、产品经理
- **前置知识**：了解大模型基本概念（GPT/Claude）、有过使用提示词的经验

## 3. 信息架构设计

### 章节划分
| 文件 | 章节标题 | 核心内容 |
|------|---------|---------|
| 00-overview.md | 概述与学习目标 | 背景、核心主题、学习目标、前置知识、文档导航 |
| 01-bottleneck-migration.md | 瓶颈外移：AI工程演进的主线规律 | 瓶颈外移模型、四站递进关系、层层包含结构 |
| 02-prompt-engineering.md | 第一站：Prompt Engineering | 模型预测本质、提示词配方、瓶颈：怎么说 |
| 03-context-engineering.md | 第二站：Context Engineering | 上下文窗口、context rot、渐进式披露、瓶颈：给什么 |
| 04-harness-engineering.md | 第三站：Harness Engineering（关键一跃） | Hashimoto定义、复利效应、Agent=模型+Harness、瓶颈：干活环境 |
| 05-loop-engineering.md | 第四站：Loop Engineering | 回合制→循环制、三人同期点响、瓶颈：你自己 |
| 06-insights-patterns.md | 深度洞察与可复用方法论 | 行业趋势、市场动态、4个认知模型、Harness工程化方法论 |
| 07-summary-faq-resources.md | 总结、FAQ与资源链接 | 核心要点回顾、FAQ、原始资源、相关学习资源 |

### 逻辑组织方式
- [x] 线性递进（适合概念演进类文章，按四站路标顺序展开）

### 原子化决策

**判断标准**：
| 判断维度 | 拆分阈值 | 本wiki预估 |
|---------|---------|-----------|
| 内容长度 | >300行建议拆分 | 预计约500-600行 |
| 章节独立性 | 各章节是否可单独阅读/引用？ | ✅是（每站可独立阅读） |
| 未来扩展 | 是否预期会持续新增章节/内容？ | ✅是（新概念可能涌现） |
| 复用需求 | 单个章节是否会被其他文档引用？ | ✅是（Harness/Loop概念可被引用） |

**决策结果**：
- [x] **需要原子化拆分**：采用"索引页(xxx-wiki.md) + 目录(xxx-wiki/) + 数字前缀原子文件"结构

## 4. 影响范围
- **新增文件**：`docs/knowledge/learning/ai-engineering-four-milestones-wiki.md`（索引页）+ `docs/knowledge/learning/ai-engineering-four-milestones-wiki/`目录下8个原子文件
- **TOML元数据**：`.meta/toml/docs/knowledge/learning/ai-engineering-four-milestones-wiki/`下8个TOML文件
- **更新文件**：`docs/knowledge/README.md`（知识库索引追加条目）
- **依赖**：已完成的分析报告（对话中双层结构报告）作为内容素材

## 5. Open Questions
- 指令集评估：本wiki为概念理解类知识，非自动化工具，暂不需要配套指令集/Skill。后续如出现Harness工程化的具体工具实践，可考虑转化为Skill。
