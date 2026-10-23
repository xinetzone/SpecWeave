# Concepts

本目录包含经过七概念方法论编排（R→I→E→V）萃取的可复用方法论模式，共 19 个。

## 模式清单

| 模式 | 成熟度 | 说明 |
|------|--------|------|
| [批量Markdown文档到OKF Bundle转换模式](batch-docs-to-okf-bundle-conversion.md) | stable | 将大量散乱的Markdown文档批量转换为结构化OKF v0.2 Bundle的可复用方法论，涵盖R→I→E→V→C五阶段工作流、分批策略、frontmatter补全规则、链接修复和验证清单。 |
| [古典文本-现代阐释双层Bundle构建模式](classical-commentary-dual-layer-bundle.md) | L1-draft | 为'古典原文+现代阐释'双层文本结构批量构建OKF v0.2 Bundle：两Bundle共享同一分组，古典层Bundle负责原文事实采集（F-001起），阐释层Bundle独立编号（从F-N+1起），通过fact编号隔离避免交叉冲突。 |
| [内容漏斗分析模式](content-funnel-analysis.md) | L1-draft | 五层递进式内容深度分析模式，从原始提取到行业洞察逐层深入，确保分析有依据、洞察超越原文。 |
| [跨框架原子化设计分析模式](cross-framework-atomic-analysis.md) | L1-draft | 跨多框架对比提炼原子化设计指南并回写到Agent文件的四阶段链路，将隐含设计哲学转化为显性知识。 |
| [文档自动化生成与验证流水线模式](doc-automation-pipeline.md) | L1-draft | 文档规模扩大后（经验阈值约 500 条目，非测量值），以统一元数据规范 + 自动化脚本（模板生成/链接验证/索引生成）+ 质量门禁构成的生成-验证流水线，将文档维护从人工操作转换为机器驱动，突破人工维护索引的规模瓶颈。 |
| [不确定性探索+确定性校验双引擎架构模式](dual-engine-uncertainty-certainty.md) | L2-validated | AI不确定性引擎与程序确定性引擎双轨校验架构，用互补性对冲AI不确定性，高风险场景实现可信输出。 |
| [双层分析报告结构](dual-layer-analysis-report.md) | L2-validated | 学习笔记层（事实）与洞察总结层（判断）分离的双目标分析报告结构，确保客观性与深度洞察并存。 |
| [错误黑名单单调进化模式](error-blacklist-monotonic-evolution.md) | L2-validated | 将人工拒绝的错误Case持久化为回归测试黑名单，设置100%回归门槛，以下界单调抬升保证系统可靠性持续进化。 |
| [评测驱动的自进化闭环模式](evaluation-driven-self-evolution.md) | L2-validated | 四层评测体系加双Agent自进化飞轮，将人工标注反馈转化为系统持续优化动力，突破AI系统人力维护瓶颈。 |
| [整合优于发明模式](integration-over-invention.md) | L1-draft | 将互补开源工具通过Docker Compose等标准范式整合为一键部署方案，以连接价值替代重复造轮子。 |
| [知识编译模式](knowledge-compilation.md) | L1-draft | 对高频深度使用的结构化知识源一次性深度编译为Agent可推理Skill，运行时高效调用，相比RAG获得数量级token效率提升。 |
| [分层链式规格模式](layered-chained-spec.md) | L1.5 | 分层约束与链式Markdown产物传递将vibe coding转化为按图施工工程流程，规格先行、阶段硬隔离、链式可校验。 |
| [降低门槛即创造市场模式](lowering-barriers-creates-markets.md) | L1-draft | 将成熟技术方案简化为一键部署，通过降低采用门槛跨越技术鸿沟，从技术专家扩展到普通用户创造增量市场。 |
| [生成-登记同步法](nav-co-registration.md) | L1.5 | 批量生成结构化内容时，导航登记（toctree/索引表/注册表）必须与内容产物同步产出、幂等登记、门禁伴随、原子交付，消除'文件存在但不可达'的元数据债务。 |
| [离线优先架构模式](offline-first-architecture.md) | L1-draft | 从离线场景开始系统设计，本地数据与计算优先，在线连接仅作增强能力，确保网络不可靠时核心功能完整可用。 |
| [责任转移治理模式](responsibility-transfer-governance.md) | L2-validated | 将治理执行权与出错责任从业务侧转移到平台侧，以责任压力驱动平台构建可靠自动化系统，打破治理死循环。 |
| [子代理分析任务标准化指令](subagent-standardized-instruction.md) | L2-validated | 标准化子代理指令结构（目标到步骤到质量到输出格式），内嵌验收标准与上下文完整性，保障委派任务质量可控。 |
| [技术文章Wiki化批量生成模式](tech-article-to-wiki-batch-generation.md) | L2-validated | 长文转原子化Wiki的8步标准化流程，Spec约束下子代理批量生成，自动化工具链修复元数据，链接检查为必经质量门禁。 |
| [三层修复闭环](three-layer-repair-closure.md) | L1-draft | 针对反复复发型故障的治标到断源到兜底三层闭环处置，识别周期性破坏源并建立自动化自愈与知识沉淀。 |

```{toctree}
:maxdepth: 2

batch-docs-to-okf-bundle-conversion
classical-commentary-dual-layer-bundle
content-funnel-analysis
cross-framework-atomic-analysis
doc-automation-pipeline
dual-engine-uncertainty-certainty
dual-layer-analysis-report
error-blacklist-monotonic-evolution
evaluation-driven-self-evolution
integration-over-invention
knowledge-compilation
layered-chained-spec
lowering-barriers-creates-markets
nav-co-registration
offline-first-architecture
responsibility-transfer-governance
subagent-standardized-instruction
tech-article-to-wiki-batch-generation
three-layer-repair-closure
```
