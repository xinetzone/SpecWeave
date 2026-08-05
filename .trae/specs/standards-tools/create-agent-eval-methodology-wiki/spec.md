# Agent评测体系化建设方法论 Wiki教程与知乎文章 - Product Requirement Document

## Overview
- **Summary**: 基于R-I-E-C-A-F-V七概念方法论编排，对AI Agent评测体系化建设进行全面深入的专题调研，创作一份结构清晰、内容详实的wiki教程文档（含方法论概述、核心框架、关键指标、实施步骤、案例分析、FAQ六大模块），同时完整记录创作全流程（资料收集→框架搭建→内容撰写→审核修订）的思考过程与决策依据，最终基于调研成果和创作经验撰写一篇适合知乎平台的高质量科普文章。
- **Purpose**: 解决当前Agent评测领域"知识碎片化、缺乏体系化方法论指导、落地路径不清晰"的痛点，为AI开发者、技术管理者和研究者提供一份可直接参考、可操作的体系化建设指南，同时沉淀wiki创作方法论为可复用模式。
- **Target Users**: 
  - AI/LLM应用开发者（需要落地Agent评测的工程师）
  - 技术管理者/架构师（需要搭建团队评测体系的负责人）
  - AI研究者/学生（需要了解Agent评测前沿进展）
  - 技术内容创作者（可参考创作流程）

## Goals
- 产出一份专业、系统、可操作的Agent评测体系化建设wiki教程（≥15000字）
- 完整记录创作全流程的思考过程、决策依据、挑战与解决方案（作为创作方法论沉淀）
- 产出一篇兼顾专业性与可读性的知乎平台文章（5000-8000字）
- 遵循七概念方法论（R-I-E-C-A-F-V）质量门标准，确保产出质量可预测
- wiki教程包含六大模块：方法论概述、核心框架对比、关键指标体系、八阶段实施步骤、8个行业案例分析、常见问题解答

## Non-Goals (Out of Scope)
- 不开发实际的Agent评测工具或代码库
- 不进行具体模型的评测跑分
- 不做学术论文级别的原创研究
- 不覆盖机器人/具身智能等非软件Agent领域
- 知乎文章不追求流量噱头，坚持专业严谨

## Background & Context
- AI Agent已成为LLM应用的主流形态，但评测体系严重滞后于开发进度
- 现有评测框架（HELM/MT-Bench/AgentBench等）各有侧重，缺乏统一的选型指导
- 行业普遍存在"LLM-as-Judge偏差"、"奖励黑客"、"可复现性差"等痛点
- 项目遵循SpecWeave规范体系，使用七概念方法论编排指导创作全流程
- 已有前置深度调研覆盖：6大主流框架对比、4维80+指标体系、8阶段实施流程、8个头部企业案例、6大挑战解决方案、12个公开基准数据集

## Functional Requirements
- **FR-1**: wiki教程必须包含方法论概述模块（定义、价值、成熟度模型、常见误区）
- **FR-2**: wiki教程必须包含核心框架对比模块（HELM/MT-Bench/AgentBench/AutoEval/τ-bench/AgentBoard六框架深度对比）
- **FR-3**: wiki教程必须包含关键指标体系模块（能力/效率/安全/人本四维80+指标详解）
- **FR-4**: wiki教程必须包含八阶段实施步骤模块（0-8周落地路线图，每阶段输入/输出/工具/验收标准）
- **FR-5**: wiki教程必须包含8个行业案例分析模块（OpenAI/LangChain/Similarweb/Nubank/AWS/JPMorgan/Harvey/IBM）
- **FR-6**: wiki教程必须包含常见问题解答模块（FAQ≥20条，覆盖选型/实施/踩坑）
- **FR-7**: 必须完整记录创作全流程：资料收集阶段、框架搭建阶段、内容撰写阶段、审核修订阶段的思考过程、决策依据、挑战与解决方案
- **FR-8**: 知乎文章必须采用生动案例+通俗语言，系统介绍Agent评测方法论，分享wiki创作经验
- **FR-9**: 所有产出必须遵循项目规范：YAML frontmatter、kebab-case文件名、相对路径引用、术语表（≥15个核心术语）
- **FR-10**: 必须执行V阶段四视角对抗审查（魔鬼代言人/新人/老板/未来），根据审查意见修正产出

## Non-Functional Requirements
- **NFR-1**: 专业性：引用来源≥20个，覆盖学术论文、官方文档、企业技术博客（2022-2026）
- **NFR-2**: 系统性：内容逻辑自洽，模块间衔接自然，形成完整知识体系
- **NFR-3**: 可操作性：实施步骤可直接落地，有具体工具、检查清单、验收标准
- **NFR-4**: 可读性：知乎文章适合非专业读者理解，专业术语有通俗解释
- **NFR-5**: 可追溯性：创作过程记录真实完整，关键决策有依据说明
- **NFR-6**: 格式规范：符合项目markdown规范、frontmatter规范、链接规范

## Constraints
- **Technical**: 遵循SpecWeave项目现有文档规范和目录结构，使用markdown格式
- **Business**: 内容基于公开可获取资料，不涉及商业秘密或未公开信息
- **Dependencies**: 前置深度调研已完成，依赖七概念方法论编排流程、docgen/link-check等项目工具

## Assumptions
- 用户认可使用七概念方法论（R-I-E-C-A-F-V）指导创作流程
- 用户接受wiki教程存放在 `.agents/docs/knowledge/` 目录下
- 用户接受创作过程记录作为wiki的一部分或附录存在
- 知乎文章风格定位为"专业科普"而非"营销软文"
- 允许在wiki中引用项目内已有的方法论模式作为参考

## Acceptance Criteria

### AC-1: Wiki教程结构完整性
- **Given**: wiki教程创作完成
- **When**: 检查文档结构
- **Then**: 必须包含六大模块：方法论概述、核心框架、关键指标、实施步骤、案例分析、FAQ，且术语表≥15条核心术语
- **Verification**: `programmatic`
- **Notes**: 使用目录结构检查脚本验证

### AC-2: 核心框架对比覆盖度
- **Given**: wiki教程核心框架模块
- **When**: 检查内容覆盖
- **Then**: 必须覆盖HELM、MT-Bench、AgentBench、AutoEval、τ-bench、AgentBoard六个框架的设计理念、指标体系、适用场景、优缺点对比
- **Verification**: `programmatic`

### AC-3: 指标体系完整性
- **Given**: wiki教程关键指标模块
- **When**: 检查指标覆盖
- **Then**: 必须覆盖能力/效率/安全/人本四个维度，关键指标≥50个，每个指标有定义、测量方法、参考阈值
- **Verification**: `programmatic`

### AC-4: 实施步骤可操作性
- **Given**: wiki教程实施步骤模块
- **When**: 检查步骤内容
- **Then**: 八阶段流程每阶段必须有明确输入、输出、工具推荐、验收标准、常见坑，提供0-8周落地清单
- **Verification**: `human-judgment` + `programmatic`
- **Notes**: 评审人按"看完能否直接照着做" rubric打分

### AC-5: 案例分析真实性
- **Given**: wiki教程案例分析模块
- **When**: 检查案例内容
- **Then**: 8个企业案例每个必须有具体做法、经验教训、可复用要点，信息来源可追溯
- **Verification**: `programmatic` + 引用检查

### AC-6: 创作过程记录完整性
- **Given**: 创作过程记录文档
- **When**: 检查记录内容
- **Then**: 必须覆盖资料收集、框架搭建、内容撰写、审核修订四个阶段，每个阶段包含思考过程、决策依据、遇到的挑战与解决方案
- **Verification**: `human-judgment`
- **Notes**: 按"是否真实还原创作心路" rubric评审

### AC-7: 知乎文章质量
- **Given**: 知乎文章完成
- **When**: 阅读并评估
- **Then**: 5000-8000字，语言通俗生动，有具体案例，兼顾专业性与可读性，包含wiki创作经验分享章节
- **Verification**: `human-judgment`
- **Notes**: 按"非AI专业读者能否看懂"、"是否愿意转发"两个维度评审

### AC-8: 对抗审查执行
- **Given**: V阶段对抗审查完成
- **When**: 检查审查记录
- **Then**: 四视角（魔鬼/新人/老板/未来）审查意见≥10条，至少采纳3条修正产出，有审查记录和修正对比
- **Verification**: `programmatic`

### AC-9: 格式规范合规
- **Given**: 所有产出文件
- **When**: 运行项目格式检查工具
- **Then**: 文件名kebab-case无中文、frontmatter YAML格式正确、无断链、markdown表格格式合规、通过ci-check基础检查
- **Verification**: `programmatic`

### AC-10: 七概念质量门通过
- **Given**: 全流程执行完成
- **When**: 检查各阶段质量门
- **Then**: G1（事实无因果词）、G2（洞察四元组完整）、G3（模式可迁移）、G4（行动项原子化）全部通过
- **Verification**: `programmatic`

## Open Questions

> 以下问题在创作执行阶段已全部解决，记录决策结果供追溯。

- [x] **wiki教程最终存放目录**：`.agents/docs/knowledge/learning/02-agent-engineering-methodology/agent-eval-methodology-wiki/`（归属于「Agent工程方法论」专题，与工程手册 `agent-evaluation-wiki/` 互为参阅）
- [x] **知乎文章是否模拟知乎平台格式**：是。产出 `zhihu-article-seven-concepts-wiki-creation-publish.md` 为发布版，去除YAML frontmatter与内部链接，可直接粘贴知乎编辑器
- [x] **创作过程记录的形式**：独立文档，存放于 `appendices/creation-process-record.md`，完整覆盖资料收集/框架搭建/内容撰写/审核修订四阶段
