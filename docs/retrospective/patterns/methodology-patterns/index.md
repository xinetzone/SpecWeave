# 方法论模式库索引

> 本目录存放经过七概念方法论编排（R→I→E→V）萃取的可复用方法论模式。每个模式均通过G1-G4质量门与V对抗审查。

## 模式清单

| 模式ID | 模式名称 | 成熟度 | 验证次数 | 复用次数 | 触发场景 |
|--------|---------|--------|---------|---------|---------|
| bp-dual-layer | [双层分析报告结构](concepts/dual-layer-analysis-report.md) | L2-validated | 3 | 15 | 需要对网页/文章/技术内容进行"既理解内容又提炼洞察"的双目标分析时 |
| bp-subagent-std | [子代理分析任务标准化指令](concepts/subagent-standardized-instruction.md) | L2-validated | 3 | 3 | 需要委派子代理执行复杂多步骤分析任务时 |
| bp-content-funnel | [内容漏斗分析模式](concepts/content-funnel-analysis.md) | L1-draft | 1 | 1 | 需要对技术文章/行业报告进行递进式深度分析时 |
| bp-integration-over-invention | [整合优于发明模式](concepts/integration-over-invention.md) | L1-draft | 1 | 1 | 存在多个互补开源工具但组合使用门槛高时 |
| bp-offline-first-architecture | [离线优先架构模式](concepts/offline-first-architecture.md) | L1-draft | 1 | 1 | 系统需要在离线状态下保证完整功能可用时 |
| bp-lowering-barriers-creates-markets | [降低门槛即创造市场模式](concepts/lowering-barriers-creates-markets.md) | L1-draft | 1 | 1 | 技术方案成熟但安装配置复杂度阻碍大规模采用时 |
| bp-knowledge-compilation | [知识编译模式](concepts/knowledge-compilation.md) | L1-draft | 2 | 1 | 高频深度使用的结构化知识源（技术书籍/手册/规范）需要比RAG更高的token效率时。[案例：七概念方法论编译](../../../../.agents/skills/seven-concepts-cmd/references/compiled-methodology.md)（10个源文件→365行~4800token自包含Skill） |
| bp-dual-engine-uncertainty-certainty | [不确定性探索+确定性校验双引擎架构](concepts/dual-engine-uncertainty-certainty.md) | L2-validated | 2 | 1 | 高风险AI应用场景（改错即故障）中，AI正确率不足但存在确定性程序校验通道时 |
| bp-evaluation-driven-self-evolution | [评测驱动的自进化闭环](concepts/evaluation-driven-self-evolution.md) | L2-validated | 2 | 1 | AI系统需要持续优化而非一次性交付，且输出可明确判定对错时 |
| bp-responsibility-transfer-governance | [责任转移治理模式](concepts/responsibility-transfer-governance.md) | L2-validated | 2 | 1 | 业务方因风险收益不对等缺乏治理动力，平台方能构建可靠自动化系统兜底时 |
| bp-error-blacklist-monotonic-evolution | [错误黑名单单调进化模式](concepts/error-blacklist-monotonic-evolution.md) | L2-validated | 2 | 1 | 系统需持续提升可靠性，且"重犯已知错误"是主要故障来源时 |
| bp-cross-framework-atomic-analysis | [跨框架原子化设计分析模式](concepts/cross-framework-atomic-analysis.md) | L1-draft | 1 | 0 | AI Agent 库需引入跨框架设计方法论（如原子化设计）并回写到具体 Agent 时 |
| bp-layered-chained-spec | [分层链式规格模式](concepts/layered-chained-spec.md) | L1.5 | 1 | 0 | AI编程/多代理协作中需将vibe coding转化为"按图施工"工程流程时。案例：GitHub Spec Kit六命令+SpecWeave三件套双案例萃取 |
| bp-plugin-bridge-standard-integration | [插件桥接规范集成法](../../../../.agents/docs/retrospective/patterns/methodology-patterns/governance-strategy/plugin-bridge-standard-integration.md) | L1-draft | 1 | 1 | 需要把一套工作区规范（AGENTS协议/路由/Skill）接入已运行的Agent平台，且目录感知地自动生效时。案例：Hermes接入SpecWeave规范 |
| bp-automation-idempotent-four-elements | [自动化幂等四要素](../../../../.agents/docs/retrospective/patterns/methodology-patterns/tools-automation/automation-idempotent-four-elements.md) | L1-draft | 1 | 1 | 编写部署/启用/验证类操作脚本（安装器/环境引导/CI初始化）需保证幂等可重跑时。案例：specweave-bridge install.py |
| bp-three-layer-repair-closure | [三层修复闭环](concepts/three-layer-repair-closure.md) | L1-draft | 1 | 1 | 反复复发型故障需根治而非治标时。案例：Windows截图工具10天3次复发双源头根因（治标→断源→兜底→沉淀） |
| bp-preflight-integrity-gate | [前置完整性门禁](preflight-integrity-gate.md) | L1-draft | 1 | 0 | 本地容错工具（编辑器/浏览器）掩盖的数据损坏（编码截断/非法字节/格式错误）需在 CI 依赖安装与构建之前主动曝光（shift-left）时。案例：awesome-okf-xs 12个UTF-8损坏文档于Sphinx构建阶段暴露 |
| bp-destructive-probe-gate | [破坏性探针双向验证门禁](destructive-probe-gate.md) | L1-draft | 1 | 0 | 为 CI 新增校验性 gate 脚本（格式/编码/lint/门禁）时，需双向验证"异常输入拦得住、正常输入放得行"，防止 gate 逻辑缺陷形同虚设。案例：check-utf8.py 截断中文字节探针双向闭环 |
| bp-history-based-doc-repair | [历史基线文档修复法](history-based-doc-repair.md) | L1-draft | 1 | 0 | Markdown/YAML 等文本文件出现编码损坏（UTF-8 截断/U+FFFD/非法字节）且损坏前存在完好 git 历史版本时。案例：awesome-okf-xs 12个损坏文档以历史提交基线无损重建 |
| bp-nav-co-registration | [生成-登记同步法](concepts/nav-co-registration.md) | L1.5 | 2 | 0 | 批量生成结构化内容（知识包/Wiki/报告）需通过导航层（toctree/索引表/注册表）被消费时。案例：docs全量审计2,245处导航债务+OKF v0.2转换双案例（同谱系，待跨项目正向验证升级L2） |
| bp-tech-article-to-wiki-batch | [技术文章Wiki化批量生成模式](concepts/tech-article-to-wiki-batch-generation.md) | L2-validated | 6 | 6 | 将长技术文章/教程（800行以上、多章节需独立引用）转化为原子化Wiki结构时：Spec约束下子代理批量生成原子文件、自动化工具链修复元数据/索引、链接检查为必经门禁（8步标准化流程；短篇<500行用单文件轻量变体）。案例：Harness Engineering Wiki 2小时10原子文件 |
| batch-docs-to-okf-bundle-conversion | [批量Markdown文档到OKF Bundle转换模式](concepts/batch-docs-to-okf-bundle-conversion.md) | stable | — | — | 大量散乱Markdown文档（20+）需批量转换为结构化OKF v0.2 Bundle时：R→I→E→V→C五阶段分批工作流，覆盖frontmatter统一补全、index导航建立、跨文档链接修复与正文保真验证 |

## 成熟度等级说明

| 等级 | 名称 | 标准 |
|------|------|------|
| L1-draft | 假设性模式 | 单案例,待验证 |
| L1.5 | 同谱系双案例 | 同一方法论谱系的两个独立实现互为验证,待第三方独立案例升级L2 |
| L2-validated | 已验证模式 | ≥2独立案例,已在本项目验证 |
| L3-mature | 成熟模式 | 跨项目验证,有明确边界条件 |
| L4-optimized | 优化模式 | 经过对抗审查,工具化/自动化支持 |

## 模式入库流程

1. **R阶段（复盘）**:采集案例事实,≥2个独立案例
2. **I阶段（洞察）**:提炼跨案例共性,形成四元组洞察（现象+根因+影响+建议）
3. **E阶段（萃取）**:按标准模板结构化模式（触发场景+核心做法+反模式+检验标准+迁移示例）
4. **V阶段（对抗审查）**:多视角攻击验证,≥5条审查意见,采纳≥2条修正
5. **入库**:创建模式文档+更新本索引+创建TOML元数据

详见 [萃取指令集](../../../../.agents/commands/extraction.md) 与 [七概念方法论编排指令集](../../../../.agents/commands/seven-concepts.md)。

## 关联资源

- 七概念方法论体系索引（如存在，待创建）
- [网页内容→结构化学习笔记 模式库](../../reports/concepts/milestone/web-content-learning-notes-patterns-20260801.md)
- [萃取指令集](../../../../.agents/commands/extraction.md)
- [七概念方法论编排指令集](../../../../.agents/commands/seven-concepts.md)

```{toctree}
:maxdepth: 2

concepts/index
destructive-probe-gate
history-based-doc-repair
log
preflight-integrity-gate
```