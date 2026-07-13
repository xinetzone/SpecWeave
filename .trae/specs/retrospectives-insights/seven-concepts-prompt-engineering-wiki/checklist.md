# 七概念驱动的GPT-5.6时代Prompt Engineering Wiki教程 - Verification Checklist

## 结构与规范性检查
- [ ] 目标目录 `docs/knowledge/learning/02-agent-engineering-methodology/seven-concepts-prompt-wiki/` 存在
- [ ] 包含15个文件：README.md + 00-overview.md + 01-12章 + 13-quick-reference.md
- [ ] 所有文件名遵循两位数字前缀+英文kebab-case命名规范
- [ ] 每个Markdown文件包含完整YAML frontmatter（id/title/category/date/version/status）
- [ ] 单个文件行数≤500行，符合单一职责原则
- [ ] 无file:///绝对路径引用，所有内部链接使用相对路径

## 内容完整性检查
- [ ] README.md包含完整文档索引表（15个文件条目）
- [ ] README.md包含至少3条分层阅读路径（入门/开发者/研究者）
- [ ] README.md包含主题概述、相关资源链接
- [ ] 00-overview.md包含教程定位、学习目标、适用人群
- [ ] 00-overview.md包含可信度评级说明、文件导航表
- [ ] 01-paradigm-shift.md完整阐述范式转变，包含OpenAI测试数据（Eval+10-15%/Token-41-66%/成本-33-67%）
- [ ] 02-seven-concepts-mapping.md包含R-I-E-C-A-F-V每个概念到Prompt编写环节的明确映射
- [ ] 02-seven-concepts-mapping.md包含七概念五层模型对应关系和Mermaid工作流图
- [ ] 02-seven-concepts-mapping.md明确标注七概念整合为SpecWeave方法论，非OpenAI官方内容
- [ ] 03-gcob-framework.md详细解释Goal/Context/Output/Boundaries四要素（定义+要点+正反示例）
- [ ] 03-gcob-framework.md包含项目状态通报完整Prompt示例（中英对照）
- [ ] 04-new-paradigm-rules.md包含5类应删除内容的详细说明和示例
- [ ] 04-new-paradigm-rules.md包含四级任务复杂度与Prompt长度指南表格
- [ ] 04-new-paradigm-rules.md包含Steer与Queue机制说明
- [ ] 05-before-after-examples.md包含完整6组Before/After对照（内容分析/代码生成/翻译/研究分析/Agent工具调用/日常任务）
- [ ] 每组Before/After包含旧写法问题分析+新写法要点+可复制Prompt
- [ ] 研究分析类和Agent工具调用类示例包含完整五段结构（Context/Request/Output/Constraints/Checkpoint）
- [ ] 06-chat-scenarios.md包含4大Chat场景用法，每个有模板和示例
- [ ] 07-work-scenarios.md包含Work高效使用指南和3大用法示例
- [ ] 08-codex-scenarios.md包含至少8个Codex开发工作流
- [ ] 每个Codex工作流包含适用场景+载体选择+步骤+示例Prompt+上下文说明+验证方式
- [ ] 09-checklists-templates.md包含Prompt五问自检清单（带判定标准）
- [ ] 09-checklists-templates.md包含至少5个可直接复用的Prompt模板（带占位符说明）
- [ ] 10-anti-patterns.md包含至少5类反模式，每类有特征+危害+修正方案+Before/After
- [ ] 11-glossary.md包含至少15个核心术语（中英文对照+定义）
- [ ] 12-faq-resources.md包含至少10个FAQ问答
- [ ] 12-faq-resources.md包含延伸阅读资源索引和相关Wiki交叉引用
- [ ] 13-quick-reference.md内容紧凑，包含GCOB速查、Before/After速览、五问清单、反模式速查

## 七概念映射准确性检查
- [ ] R(复盘)映射正确（如Prompt迭代后的经验总结）
- [ ] I(洞察)映射正确（如识别Prompt问题模式）
- [ ] E(萃取)映射正确（如沉淀可复用Prompt模板）
- [ ] C(原子提交)映射正确（如Prompt小步迭代验证）
- [ ] A(原子化)映射正确（如Prompt结构模块化分解）
- [ ] F(第一性原理)映射正确（如从目标出发而非流程）
- [ ] V(对抗性审查)映射正确（如Prompt五问自检）
- [ ] 五层模型（感知→认知→验证→执行→沉淀）在Prompt编写过程中的解释合理

## 网页内容覆盖检查
- [ ] OpenAI第一篇文章（官方Prompting指南）四要素框架完整覆盖
- [ ] OpenAI第一篇文章Chat/Work/Codex三大场景内容完整覆盖
- [ ] OpenAI第一篇文章Steer与Queue机制完整覆盖
- [ ] 第二篇文章（GPT-5.6新写法）"明确目标而非规定过程"核心理念完整阐述
- [ ] 第二篇文章6组Before/After完整覆盖
- [ ] 第二篇文章5类应删除内容完整覆盖
- [ ] 第二篇文章五问自检清单完整覆盖
- [ ] 第二篇文章四级任务复杂度表格完整覆盖
- [ ] 关键数据（Eval/Token/成本提升数据）准确无误

## 示例可操作性检查
- [ ] 所有"新写法"Prompt示例可直接复制使用
- [ ] 示例中的占位符（如[公司名]）有明确标注
- [ ] Codex场景示例贴近真实开发场景
- [ ] 模板包含填写说明，非纯骨架
- [ ] 反模式的Before/After对比清晰，修正方案具体可执行

## 上级目录索引更新检查
- [ ] 02-agent-engineering-methodology/README.md子Wiki索引表已添加本教程条目
- [ ] 本教程条目描述准确（文件数、核心主题）
- [ ] 快速导航表已添加Prompt Engineering场景分组
- [ ] 至少1条推荐学习路径中包含本教程
- [ ] 更新未破坏现有其他条目的格式和内容

## 链接有效性验证
- [ ] 运行 `python .agents/scripts/check-links.py --path docs/knowledge/learning/02-agent-engineering-methodology/seven-concepts-prompt-wiki/` 无断链
- [ ] 所有跨章节相对路径正确
- [ ] 对上级目录的相对路径（如../README.md）正确
- [ ] 对七概念方法论文档的交叉引用路径正确
- [ ] 对其他Wiki（如karpathy、adversarial-review）的交叉引用路径正确

## 来源标注检查
- [ ] OpenAI官方内容有明确标注来源
- [ ] 微信文章作者解读内容有明确区分
- [ ] SpecWeave七概念整合内容有明确标注
- [ ] 关键数据点有来源说明
- [ ] 无编造的未经验证的"最佳实践"
