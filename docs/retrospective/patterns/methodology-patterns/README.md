---
id: "methodology-patterns-index"
title: "方法论模式库索引"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/README.toml"
date: "2026-07-04"
---
# 方法论模式库索引

> 本目录存放经过七概念方法论编排（R→I→E→V）萃取的可复用方法论模式。每个模式均通过G1-G4质量门与V对抗审查。

## 模式清单

| 模式ID | 模式名称 | 成熟度 | 验证次数 | 复用次数 | 触发场景 |
|--------|---------|--------|---------|---------|---------|
| bp-dual-layer | [双层分析报告结构](dual-layer-analysis-report.md) | L2-validated | 3 | 15 | 需要对网页/文章/技术内容进行"既理解内容又提炼洞察"的双目标分析时 |
| bp-subagent-std | [子代理分析任务标准化指令](subagent-standardized-instruction.md) | L2-validated | 3 | 3 | 需要委派子代理执行复杂多步骤分析任务时 |
| bp-content-funnel | [内容漏斗分析模式](content-funnel-analysis.md) | L1-draft | 1 | 1 | 需要对技术文章/行业报告进行递进式深度分析时 |
| bp-integration-over-invention | [整合优于发明模式](integration-over-invention.md) | L1-draft | 1 | 1 | 存在多个互补开源工具但组合使用门槛高时 |
| bp-offline-first-architecture | [离线优先架构模式](offline-first-architecture.md) | L1-draft | 1 | 1 | 系统需要在离线状态下保证完整功能可用时 |
| bp-lowering-barriers-creates-markets | [降低门槛即创造市场模式](lowering-barriers-creates-markets.md) | L1-draft | 1 | 1 | 技术方案成熟但安装配置复杂度阻碍大规模采用时 |
| bp-knowledge-compilation | [知识编译模式](knowledge-compilation.md) | L1-draft | 2 | 1 | 高频深度使用的结构化知识源（技术书籍/手册/规范）需要比RAG更高的token效率时。[案例：七概念方法论编译](../../../../.agents/skills/seven-concepts-cmd/references/compiled-methodology.md)（10个源文件→365行~4800token自包含Skill） |
| bp-knowledge-compilation | [知识编译模式](knowledge-compilation.md) | L1-draft | 2 | 1 | 高频深度使用的结构化知识源（技术书籍/手册/规范）需要比RAG更高的token效率时。[案例：七概念方法论编译](../../../../.agents/skills/seven-concepts-cmd/references/compiled-methodology.md)（10个源文件→365行~4800token自包含Skill） |
| bp-dual-engine-uncertainty-certainty | [不确定性探索+确定性校验双引擎架构](dual-engine-uncertainty-certainty.md) | L2-validated | 2 | 1 | 高风险AI应用场景（改错即故障）中，AI正确率不足但存在确定性程序校验通道时 |
| bp-evaluation-driven-self-evolution | [评测驱动的自进化闭环](evaluation-driven-self-evolution.md) | L2-validated | 2 | 1 | AI系统需要持续优化而非一次性交付，且输出可明确判定对错时 |
| bp-responsibility-transfer-governance | [责任转移治理模式](responsibility-transfer-governance.md) | L2-validated | 2 | 1 | 业务方因风险收益不对等缺乏治理动力，平台方能构建可靠自动化系统兜底时 |
| bp-error-blacklist-monotonic-evolution | [错误黑名单单调进化模式](error-blacklist-monotonic-evolution.md) | L2-validated | 2 | 1 | 系统需持续提升可靠性，且"重犯已知错误"是主要故障来源时 |
| bp-cross-framework-atomic-analysis | [跨框架原子化设计分析模式](cross-framework-atomic-analysis.md) | L1-draft | 1 | 0 | AI Agent 库需引入跨框架设计方法论（如原子化设计）并回写到具体 Agent 时 |
| bp-layered-chained-spec | [分层链式规格模式](layered-chained-spec.md) | L1.5 | 1 | 0 | AI编程/多代理协作中需将vibe coding转化为"按图施工"工程流程时。案例：GitHub Spec Kit六命令+SpecWeave三件套双案例萃取 |
| bp-plugin-bridge-standard-integration | [插件桥接规范集成法](plugin-bridge-standard-integration.md) | L1-draft | 1 | 1 | 需要把一套工作区规范（AGENTS协议/路由/Skill）接入已运行的Agent平台，且目录感知地自动生效时。案例：Hermes接入SpecWeave规范 |
| bp-automation-idempotent-four-elements | [自动化幂等四要素](automation-idempotent-four-elements.md) | L1-draft | 1 | 1 | 编写部署/启用/验证类操作脚本（安装器/环境引导/CI初始化）需保证幂等可重跑时。案例：specweave-bridge install.py |
| bp-three-layer-repair-closure | [三层修复闭环](three-layer-repair-closure.md) | L1-draft | 1 | 1 | 反复复发型故障需根治而非治标时。案例：Windows截图工具10天3次复发双源头根因（治标→断源→兜底→沉淀） |
| bp-preflight-integrity-gate | [前置完整性门禁](preflight-integrity-gate.md) | L1-draft | 1 | 0 | 本地工具对内容损坏容错、引入CI严格解析后首曝损坏时，应把格式/编码完整性检查前置为构建前首道gate。案例：awesome-okf-xs 12个UTF-8损坏文档在Sphinx构建阶段暴露，新增check-utf8.py前置扫描 |
| bp-history-based-doc-repair | [历史基线文档修复法](history-based-doc-repair.md) | L1-draft | 1 | 0 | 文本型数据编码损坏且损坏提交前存在完好历史版本时，用git历史作权威信源：定位基线提交+分离合法编辑+三层字节校验重建。案例：awesome-okf-xs 12个UTF-8文档以6fe904e基线+保留f78d5c4合法frontmatter重建 |
| bp-destructive-probe-gate | [破坏性探针双向验证门禁](destructive-probe-gate.md) | L1-draft | 1 | 0 | 为CI新增校验性gate脚本时，需构造破坏性探针断言非零退出（拦得住）+移除后断言零退出（放得行），否则gate形同虚设。案例：awesome-okf-xs check-utf8.py探针坏文件exit 1+移除exit 0双向闭环 |

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
- [网页内容→结构化学习笔记 模式库](../../reports/milestone/web-content-learning-notes-patterns-20260801.md)
- [萃取指令集](../../../../.agents/commands/extraction.md)
- [七概念方法论编排指令集](../../../../.agents/commands/seven-concepts.md)
